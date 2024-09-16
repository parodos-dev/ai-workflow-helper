from const import SYSTEM_MESSAGE, EXAMPLES
from lib.models import SerVerlessWorkflow
from lib.validator import JsonSchemaValidationException
from lib.validator import ParsedOutputException

from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import FewShotChatMessagePromptTemplate
from langchain.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

WORKFLOWS={}

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
    return "\n\n".join(doc.page_content for doc in docs)

def get_workflow_for_session(ctx, session_id):
    return WORKFLOWS.get(session_id, {})

def get_history(ctx, session_id):
    ctx.history_repo.set_session(session_id)
    return ctx.history_repo.messages


def set_json_response(session_id, ai_response, validator):
    try:
        workflow =validator.get_json(ai_response)
        document = validator.invoke(workflow)
        if document is not None:
            print("No valid document")
        WORKFLOWS[session_id] = {
                "document": document,
                "valid": True
        }
    except (ParsedOutputException) as e:
        print(f"Invalid JSON document: {e}")
    except (JsonSchemaValidationException) as e:
        WORKFLOWS[str(session_id)] = {
                "document": workflow,
                "valid": False
        }
        print("Invalid JSON document for session", session_id)
    except Exception as e:
        print("Invalid Exception document")


def get_response_for_session(ctx, session_id, user_message):
    retriever = ctx.repo.retriever
    llm = ctx.ollama.llm

    # @TODO check if this clone the thing to a new object.
    history_repo = ctx.history_repo
    history_repo.set_session(f"{session_id}")

    prompt = get_prompt_details()
    chain = (
        {
            "context": retriever | format_docs,
            "schema": lambda _: SerVerlessWorkflow.schema_json(),
            "input": RunnablePassthrough(),
            "history": lambda _: history_repo.messages,
        }
        | prompt
        | llm)

    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: history_repo,
        input_messages_key="input",
        history_messages_key="history",
    )
    config = {"configurable": {"session_id": "{0}".format(session_id)}}
    ai_response = []
    result = chain_with_history.stream({"input": user_message}, config=config)

    for x in result:
        ai_response.append(x.content)
        yield x.content

    full_ai_response =  "".join(ai_response)
    set_json_response(session_id, full_ai_response, ctx.validator)
    # history_repo.add_user_message(user_message)
    # history_repo.add_ai_message(full_ai_response)
