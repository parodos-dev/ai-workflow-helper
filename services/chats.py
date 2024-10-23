import logging
import json

from const import SYSTEM_MESSAGE, EXAMPLES, REACT_EXAMPLES
from lib.models import SerVerlessWorkflow
from lib.json_validator import JsonSchemaValidationException
from lib.validator import ParsedOutputException
from lib.serverless_validation import ServerlessValidation

from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import FewShotChatMessagePromptTemplate
from langchain.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

class WorkflowRepo:
    def __init__(self):
        self._data = {}

    def get(self, session, default=None):
        if session in self._data and self._data[session]:
            return self._data[session][0]
        return default

    def list(self, session):
        if session in self._data and self._data[session]:
            return self._data[session]
        return []

    def put(self, session, data):
        if session not in self._data:
            self._data[session] = []
        self._data[session].insert(0, data)

    def setdefault(self, session, default=None):
        if session not in self._data or not self._data[session]:
            self.put(session, default)
            return default
        return self._data[session][0]

    def __getitem__(self, session):
        return self.get(session)

    def __setitem__(self, session, data):
        self.put(session, data)

WORKFLOWS = WorkflowRepo()

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
    logging.info("The number of docs added to the request are {0}".format(
        len(docs)))
    logging.debug("Files added to the prompt: {}".format(", ".join(
        doc.metadata.get('source') for doc in docs)))
    result = "\n".join("Source: {}\nContent:\n{}".format(
        doc.metadata.get('source'), doc.page_content) for doc in docs)
    return result

def get_all_workflow_for_session(ctx, session_id):
    return WORKFLOWS.list(str(session_id))

def get_workflow_for_session(ctx, session_id):
    return WORKFLOWS.get(str(session_id), {})


def get_history(ctx, session_id):
    ctx.history_repo.set_session(session_id)
    return ctx.history_repo.messages

class ValidatingJsonWorkflow():

    template = """
Please analyze and fix the following JSON workflow definition based on the provided information. Return only the corrected JSON as your response.

--- JSON DATA ---
{json_data}

--- JSON SCHEMA COMPILATION ERRORS ---
{validation_errors}

--- MAVEN COMPILATION LOG ---
{compilation_error}

Instructions:
1. Review all provided information (JSON data, schema compilation errors, and Maven log).
2. Identify and fix all errors in the JSON workflow definition.
3. If there are conflicting fixes, prioritize in this order: schema compilation errors, JSON validation errors, Maven errors.
4. Return only the corrected JSON workflow definition as your response, with no additional explanation.

If the JSON cannot be fully corrected due to missing information or irresolvable conflicts, return the original workflow json.
"""

    def _prompt(self):
        return  PromptTemplate(
            input_variables=["json_data", "validation_errors", "compilation_error"],
            template=self.template
        )

    def _set_workflow(self, doc, valid):
        WORKFLOWS.put(
            str(self.session_id),
            { "document": doc, "valid": valid})

    def __init__(self, chain, session_id, ai_response, validator):
        self.chain = chain
        self.session_id = session_id
        self.ai_response = ai_response
        self.validator = validator
        return

    def _ask_for_fixing(self, workflow, jsonschema, compilation_error):
        formatted_prompt = self._prompt().format(
                json_data=workflow,
                validation_errors=jsonschema,
                compilation_error=compilation_error)
        self.ai_response = self.chain.react(formatted_prompt)

    def validate_compilation(self, workflow):
        return ServerlessValidation(workflow).run()

    def validate(self, tries):
        yield "Validation started\n\n"
        for i in range(tries):
            yield f"<b>Parsing output stage {i} of {tries}:</b>"
            try:
                document = self.validator.invoke(self.ai_response)
                if document is None:
                    logging.error("document is null")
                    return
                self._set_workflow(document, True)
                workflow_json = json.dumps(document, indent=2)
                compilation_error, valid = self.validate_compilation(workflow_json)
                if not valid:
                    logging.error("Workflow json is correct, but cannot compile")
                    self._ask_for_fixing(workflow_json, "", compilation_error)
                    continue
                logging.error("Finally the document is correct")

                return
            except (ParsedOutputException) as e:
                yield "Parsed error\n\n"
                logging.error(
                        f"cannot get valid JSON document from the response: {self.ai_response.content} {e}")
            except (JsonSchemaValidationException) as e:
                self._set_workflow(e.data, False)
                workflow_json = json.dumps(e.data, indent=2)
                compilation_error, valid = self.validate_compilation(workflow_json)
                yield "Jsonschema validation failed with {0} errors\n\n".format(e.get_number_of_errors())
                self._ask_for_fixing(workflow_json, e.get_error(), compilation_error)
            except Exception as e:
                yield "failed with unexpected error\n\n"
                logging.error(f"Latest response: {self.ai_response.content}")
                logging.error(f"Unexected exception on the workflow: {e}")
        return


class ChatChain():
    def get_prompt_details(cls):
        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )

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
                few_shot_prompt,
                MessagesPlaceholder(variable_name="history", optional=True),
                ("human", "{input}"),
            ]
        )

        return prompt

    def get_react_prompt(cls):

        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=REACT_EXAMPLES,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Given the following conversation, relevant context, and a follow up question, reply with an answer to the current question the user is asking. Return only your response to the question given the above information following the users instructions as needed."),
                # ("system", REACT_MESSAGE),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )

        return prompt

    def __init__(self, llm, retriever, history, session_id):
        prompt = self.get_prompt_details()
        self._llm = llm
        self._history_repo = history
        self._config = {"configurable": {
            "session_id": "{0}".format(session_id)}}
        self._chain = (
            {
                "context": retriever | format_docs,
                "schema": lambda _: SerVerlessWorkflow.schema_json(),
                "input": RunnablePassthrough(),
                "history": lambda _: history.messages,
            }
            | prompt
            | llm)
        logging.debug("ChatChain building is finished")

    def react(self, user_message):
        prompt = self.get_react_prompt()
        # import ipdb; ipdb.set_trace()
        #return self._llm.invoke(user_message)
        chain = (
            #{
            #    #"schema": lambda _: SerVerlessWorkflow.schema_json(),
            #    "input": RunnablePassthrough(),
            #}
            { "input": RunnablePassthrough()}
            | prompt
            | self._llm)

        return chain.invoke({"input": user_message})

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
    logging.debug("get_response_for_session started")
    retriever = ctx.repo.retriever
    llm = ctx.llm_runner.llm
    # @TODO check if this clone the thing to a new object.
    history_repo = ctx.history_repo
    history_repo.set_session(f"{session_id}")
    yield "Waiting on AI response\n"
    chain = ChatChain(llm, retriever, history_repo, session_id)
    ai_response = []
    result = chain.stream({"input": user_message})
    logging.debug("Result received")
    for x in result:
        logging.debug("Passing through result")
        ai_response.append(x.content)
        yield str(x.content)

    logging.debug("Validating json")
    yield "\nChecking if json is correct and validation\n\n"
    full_ai_response = "".join(ai_response)
    validator = ValidatingJsonWorkflow(chain, session_id, full_ai_response, ctx.validator)
    for x in validator.validate(10):
        yield str(x)
    # for x in set_json_response(chain, session_id, full_ai_response, ctx.validator):
    #     yield str(x)
