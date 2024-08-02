import click
import sys
import yaml

from config import Config
from const import SYSTEM_MESSAGE, SAMPLE_QUERY

from lib.json_validator import JsonSchemaValidatorTool
from lib.models import Model
from lib.ollama import Ollama
from lib.repository import VectorRepository
from lib.retriever import Retriever
from lib.validator import OutputValidator, OutputModel
from lib.validator import ParsedOutputException, JsonSchemaValidationException

from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


class Context:
    def __init__(self, config):
        self.config = config
        self.ollama = Ollama(self.config.base_url, self.config.model)
        self.repo = VectorRepository(self.config.db, self.ollama.embeddings)
        self.validator = OutputValidator(
            OutputModel,
            JsonSchemaValidatorTool(self.config.workflow_schema_url))


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = Context(Config())
    pass


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


@click.command()
@click.argument('message')
@click.pass_obj
def chat(obj, message):

    retriever = obj.repo.retriever
    llm = obj.ollama.llm
    validator = obj.validator

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    system_prompt = (
        "The schema for serverless workflow is the"
        "following: {workflow_schema}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_MESSAGE),
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    rag_chain = (
        {
            "context": retriever | format_docs,
            "workflow_schema": lambda _: Model.schema_json(),
            "input": RunnablePassthrough(),
            "format_instructions": validator.get_format_instructions,
        }
        | prompt
        | llm
        # We can use parser here, but TBH I want to have the AI response, so
        # token usage can be tracked and chain of messages can be added.
        # | parser
    )

    messages = [[{"input": SAMPLE_QUERY}]]
    document = ""
    for _ in range(5):
        AI_response = rag_chain.invoke(messages)
        messages.append(AI_response)

        try:
            document = validator.invoke(AI_response)
            if document is not None:
                break
        except (ParsedOutputException, JsonSchemaValidationException) as e:
            messages.append(e.get_mesage())
        except Exception as e:
            print("Execption: ", e)

    print("Query send was: \n", SAMPLE_QUERY)
    print("The response is:\n", yaml.dump(document, indent=4))

@click.command()
@click.pass_obj
def test(obj):
    from lib.click_tooling import MultiLinePromt
    result = MultiLinePromt.get_and_wait_prompt()

    click.echo(f"Result {result}")

cli.add_command(load_data)
cli.add_command(chat)
cli.add_command(test)

if __name__ == '__main__':
    cli()
