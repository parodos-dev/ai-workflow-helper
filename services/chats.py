import logging

from const import SYSTEM_MESSAGE, EXAMPLES
from lib.models import SerVerlessWorkflow
from lib.json_validator import JsonSchemaValidationException
from lib.validator import ParsedOutputException

from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import FewShotChatMessagePromptTemplate
from langchain.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

WORKFLOWS = {}


def get_prompt_details():
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=EXAMPLES,
    )

    # @TODO add chat message history here
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_MESSAGE),
            few_shot_prompt,
            MessagesPlaceholder(variable_name="history", optional=True),
            ("human", "{input}"),
        ]
    )
    return prompt


def format_docs(docs):
    logging.info("The number of docs added to the request are {0}".format(len(docs)))
    logging.debug("Files added to the prompt: {}".format(", ".join(
        doc.metadata.get('source') for doc in docs)))
    result = "\n".join("Source: {}\nContent:\n{}".format(
        doc.metadata.get('source'), doc.page_content) for doc in docs)
    return result


def get_workflow_for_session(ctx, session_id):
    return WORKFLOWS.get(str(session_id), {})


def get_history(ctx, session_id):
    ctx.history_repo.set_session(session_id)
    return ctx.history_repo.messages

# This function iterates over the json and try to fix it.
def set_json_response(chain, session_id, ai_response, validator):
    initial = True;
    def set_workflow(doc, valid):
        if initial:
            WORKFLOWS[str(session_id)] = {
                "document": doc,
                "valid": valid
            }
    template = """Here's the serverless workflow JSON data I'm working with:
```json
{json_data}
```

I'm getting the following validation errors from the jsonschema:
{validation_errors}

please return the serverless workflow fixed"""

    prompt = PromptTemplate(
        input_variables=["json_data", "validation_errors"],
        template=template
    )

    for i in range(5):
        try:
            document = validator.invoke(ai_response)
            if document is None:
                logging.info("document is null")
                return
            set_workflow(document, True)
            return
        except (ParsedOutputException) as e:
            logging.error(f"cannot get valid JSON document from the response: {e}")
        except (JsonSchemaValidationException) as e:
            set_workflow(e.data, False)
            logging.error("workflow is not correct has some JSON issues")
            formatted_prompt = prompt.format(json_data=e.data, validation_errors=e.get_error())
            ai_response = chain.invoke({ "input": formatted_prompt })
        except Exception as e:
            logging.error(f"Unexected exception on the workflow: {e}")


class ChatChain():
    def get_prompt_details(cls):
        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", "This is additional context from the retriever:\n {context} Use this information if it's relevant, if not discard it."),
        ])

        schema_prompt = ChatPromptTemplate.from_messages([
            ("system", "Ensure that your response compiles with the following schema definition: ```{schema}```"),
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=EXAMPLES,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                schema_prompt,
                ("system", SYSTEM_MESSAGE),
                # rag_prompt,
                few_shot_prompt,
                MessagesPlaceholder(variable_name="history", optional=True),
                ("human", "{input}"),
            ]
        )

        return prompt

    def __init__(self, llm, retriever, history, session_id):
        prompt = self.get_prompt_details()
        self._history_repo = history
        self._config = {"configurable": {"session_id": "{0}".format(session_id)}}
        self._chain = (
            {
                "context": retriever | format_docs,
                "schema": lambda _: SerVerlessWorkflow.schema_json(),
                "input": RunnablePassthrough(),
                "history": lambda _: history.messages,
            }
            | prompt
            | llm)

    @property
    def config(self):
        return self._config

    def chain(self):
        return self._chain

    def chain_with_history(self):
        return RunnableWithMessageHistory(
            self.chain(),
            lambda session_id: self._history_repo,
            input_messages_key="input",
            history_messages_key="history",
        )

    def invoke(self, data):
        return self.chain_with_history().invoke(data, config=self._config)

    def stream(self, data):
        return self.chain_with_history().stream(data, config=self._config)


def get_response_for_session(ctx, session_id, user_message):
    retriever = ctx.repo.retriever
    llm = ctx.ollama.llm

    # @TODO check if this clone the thing to a new object.
    history_repo = ctx.history_repo
    history_repo.set_session(f"{session_id}")

    chain = ChatChain(llm, retriever, history_repo, session_id)
    ai_response = []
    result = chain.stream({"input": user_message})

    for x in result:
        ai_response.append(x.content)
        yield x.content

    full_ai_response = "".join(ai_response)
    set_json_response(chain, session_id, full_ai_response, ctx.validator)
