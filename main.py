import click
import logging
import sys
import yaml

from config import Config
from const import SYSTEM_MESSAGE, SAMPLE_QUERY

from lib.history import HistoryRepository
from lib.click_tooling import MultiLinePromt
from lib.json_validator import JsonSchemaValidatorTool
from lib.models import SerVerlessWorkflow
from lib.ollama import Ollama
from lib.repository import VectorRepository
from lib.retriever import Retriever
from lib.validator import JsonSchemaValidationException
from lib.validator import OutputValidator
from lib.validator import ParsedOutputException
from api.urls import urls
from services.chats import get_prompt_details


from flask import Flask, g
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnablePassthrough
# from langchain_core.runnables.history import RunnableWithMessageHistory

logging.basicConfig(stream=sys.stderr, level=logging.INFO)


class Context:
    def __init__(self, config):
        self.config = config
        self.ollama = Ollama(self.config.base_url, self.config.model)
        self.repo = VectorRepository(self.config.db, self.ollama.embeddings)

        self.validator = OutputValidator(
            SerVerlessWorkflow,
            JsonSchemaValidatorTool.load_schema(SerVerlessWorkflow.schema()))

        self.history_repo = HistoryRepository(
            session_id="empty",
            connection="sqlite:///{0}".format(self.config.chat_db))


app = Flask(__name__)


@app.before_request
def before_request():
    g.ctx = Context(Config())


# @TODO delete this method
@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = Context(Config())
    pass


# @TODO Move this method to the servives
@click.command()
@click.argument('file-path')
@click.pass_obj
def load_data(obj, file_path):
    repo = obj.repo
    try:
        content = Retriever.fetch(file_path)
    except Exception as e:
        click.echo(f"cannot read file-path {e}")
        sys.exit(1)

    documents = obj.ollama.parse_document(content)

    if len(documents) == 0:
        click.echo("The len of the documents is 0")
        sys.exit(1)
    try:
        res = repo.add_documents(documents)
    except Exception as e:
        click.echo(f"cannot create or storing the embeddings: {e}")
        sys.exit(1)
    repo.save()
    click.echo("{0} documents added with ids {1}".format(len(documents), res))


# @TODO move this method to the services.
@click.command()
@click.argument('message')
@click.pass_obj
def chat(obj, message):

    retriever = obj.repo.retriever
    llm = obj.ollama.llm
    validator = obj.validator

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_MESSAGE),
            ("human", "{input}"),
        ]
    )

    merda = PydanticOutputParser(pydantic_object=SerVerlessWorkflow)
    # import ipdb; ipdb.set_trace()
    rag_chain = (
        {
            "context": retriever | format_docs,
            # "workflow_schema": lambda _: Model.schema_json(),
            "input": RunnablePassthrough(),
            "format_instructions": validator.get_format_instructions,
        }
        | prompt
        | llm
        | merda
        # We can use parser here, but TBH I want to have the AI response, so
        # token usage can be tracked and chain of messages can be added.
        # | validator
    )
    click.echo(f"The input query is: {SAMPLE_QUERY}")
    messages = [[{"input": SAMPLE_QUERY}]]

    def generate_reply():
        document = ""
        for _ in range(5):
            AI_response = rag_chain.invoke(messages)
            messages.append(AI_response)
            logging.debug("Got AI response {}".format(AI_response.content))
            try:
                document = validator.invoke(AI_response)

                if document is not None:
                    click.echo("The AI response is:\n{}".format(
                        yaml.dump(document, indent=4)))
                    break
            except (ParsedOutputException, JsonSchemaValidationException) as e:
                messages.append(e.get_mesage())
            except Exception as e:
                click.echo(f"There was an uncaught execption: {e}")

            click.confirm("Do you want to continue asking?")

    generate_reply()
    while True:
        if not click.confirm("Do you want to continue asking?"):
            break

        next_prompt = MultiLinePromt.get_and_wait_prompt()
        messages.append(HumanMessage(f"{next_prompt}"))
        generate_reply()


# @TODO delete this method
@click.command()
@click.argument('message')
@click.pass_obj
def extended_chat(obj, message):
    # This function is only for testing new things and do manual tests.
    retriever = obj.repo.retriever
    llm = obj.ollama.llm
    validator = obj.validator

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    prompt = get_prompt_details()

    rag_chain = (
        {
            "context": retriever | format_docs,
            "input": RunnablePassthrough(),
            "schema": lambda _: SerVerlessWorkflow.schema_json(),
        }
        | prompt
        | llm
    )

    click.echo(f"The input query is: {SAMPLE_QUERY}")
    messages = [[{"input": SAMPLE_QUERY}]]

    def generate_reply():
        document = ""
        for _ in range(5):
            AI_response = rag_chain.invoke(messages)
            logging.debug("Got AI response {}".format(AI_response.content))
            messages.append(AI_response)
            try:
                document = validator.invoke(AI_response)
                if document is not None:
                    click.echo("The AI response is:\n{}".format(
                        yaml.dump(document, indent=4)))
                    break
            except (ParsedOutputException, JsonSchemaValidationException) as e:
                click.echo("Failed to validate input json: {}".format(
                    e.get_mesage()))
                messages.append(e.get_mesage())
            except Exception as e:
                click.echo(f"There was an uncaught execption: {e}")
            click.confirm("Do you want to continue asking?")

    generate_reply()
    while True:
        if not click.confirm("Do you want to continue asking?"):
            break

        next_prompt = MultiLinePromt.get_and_wait_prompt()
        messages.append(HumanMessage(f"{next_prompt}"))
        generate_reply()


cli.add_command(load_data)
cli.add_command(chat)
cli.add_command(extended_chat)

if __name__ == '__main__':
    for x in urls:
        app.add_url_rule(x[0], view_func=x[1], methods=x[2])
    app.run(debug=True)
