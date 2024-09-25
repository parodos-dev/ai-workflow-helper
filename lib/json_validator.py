from jsonschema import validate, ValidationError
import requests
import yaml
import json
import logging


class JsonSchemaValidationException(Exception):

    def __init__(self, errors, data={}):
        self.errors = errors
        self._data = data
        super().__init__(str(errors))

    @property
    def data(self):
        return self._data

    def get_number_of_errors(self):
        return len(self.errors.context)

    def get_error(self):
        messages = []
        if len(self.errors.context) == 0:
            logging.error("There are no errors, return the initial message")
            return self.errors.message

        logging.debug("Number the errors in validation '{}'".format(
            len(self.errors.context)))
        errors = sorted(self.errors.context, key=lambda e: e.schema_path)
        for suberror in errors:
            messages.append((
                '.'.join(str(item) for item in suberror.schema_path),
                suberror.message))
        res = '\n'.join("- {}: error {}".format(x, y) for x, y in messages)
        return res

    def get_mesage(self):
        return self.get_error()


class JsonSchemaValidatorTool():
    json_schema_validator: object = None

    @classmethod
    def load_schema(cls, schema):
        return cls(schema)

    @classmethod
    def load_from_url(cls, url):
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception("Invalid URL status-code={resp.status_code}")
        try:
            schema = cls._transform(resp.text)
        except Exception as e:
            raise Exception(f"Invalid yaml definition: {e}")

        return cls(schema)

    def __init__(self, schema):
        self.json_schema_validator = schema

    def validate(self, data):

        try:
            if isinstance(data, dict):
                return validate(
                    instance=data,
                    schema=self.json_schema_validator)

            if isinstance(data, str):
                return validate(
                    instance=json.loads(data),
                    schema=self.json_schema_validator)

        except ValidationError as errors:
            raise JsonSchemaValidationException(errors, data)

        raise Exception(
                "Type of data '{}' cannot be parsed".format(type(data)))

    def _transform(self, data):
        doc = yaml.safe_load(data)
        return doc
