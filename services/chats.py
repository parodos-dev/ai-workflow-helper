from const import SYSTEM_MESSAGE, EXAMPLES

from langchain.prompts import ChatPromptTemplate
from langchain.prompts import FewShotChatMessagePromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from lib.models import SerVerlessWorkflow


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
            ("human", "{input}"),
        ]
    )

    return prompt


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_response_for_session(ctx, session_id, user_message):
    # retriever = ctx.repo.retriever
    llm = ctx.ollama.llm

    # @TODO check if this clone the thing to a new object.
    history_repo = ctx.history_repo

    prompt = get_prompt_details()

    # @TODO fix retriever for RAG
    chain = (
        {
            # "context": retriever | format_docs,
            "context": lambda x: x,
            "schema": lambda _: SerVerlessWorkflow.schema_json(),
            "input": lambda _: user_message,
        }
        | prompt
        | llm
    )

    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: history_repo.set_session(session_id),
        input_messages_key="input",
        history_messages_key="history",
    )

    config = {"configurable": {"session_id": "<SESSION_ID>"}}
    result = chain_with_history.stream({}, config=config)
    for x in result:
        yield x.content
