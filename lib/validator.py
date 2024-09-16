from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage


class OutputModel(BaseModel):
    comment: str = Field(description="comment about the workflow written")
    code: str = Field(description="serverless workflow code in Json")


class ParsedOutputException(Exception):

    def get_mesage(self):
        return HumanMessage(
            "We cannot extract any json from your previous reply")


class JsonSchemaValidationException(Exception):

    def get_mesage(self):
        return HumanMessage(
            "The validation of the previous provided JSON is not valid,"
            " here are the errors {0}\n".format(str(self)))


class OutputValidator():

    def __init__(self, model, validator):
        self.parser = JsonOutputParser(pydantic_object=model)
        self.validator = validator
        return

    def get_format_instructions(self, input, **kwargs):
        return self.parser.get_format_instructions(**kwargs)

    def get_json(self, ai_message):
        parsed_output = self.parser.invoke(ai_message)

        if parsed_output is None or parsed_output == "":
            raise ParsedOutputException(
                    'Cannot get valid json workflow from the AI'
                    f'reponse with id="{ai_message.id}"')
        return parsed_output

    def invoke(self, ai_message):
        try:
            self.validator.validate(parsed_output)
        except Exception as e:
            raise JsonSchemaValidationException(e)

        return parsed_output
