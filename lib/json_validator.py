from jsonschema import ValidationError, Draft202012Validator
import requests
import yaml
import json
import jsonschema

def format_error(error: ValidationError) -> dict:
    best_match = jsonschema.exceptions.best_match(error.context)
    return {
        "path": " -> ".join(str(path) for path in error.path),
        "message": error.message,
        "schema_path": " -> ".join(str(path) for path in error.schema_path),
        "instance": error.instance,
        "underlaying": best_match.message
    }

class JsonSchemaValidationException(Exception):

    def __init__(self, errors, data={}):
        self.errors = errors
        self._data = data
        super().__init__(str(errors))

    @property
    def data(self):
        return self._data

    def get_number_of_errors(self):
        return len(self.errors)

    def get_error(self):
        error_msg = [format_error(x) for x in self.errors]
        output = ""
        for i,x in enumerate(error_msg):
            output += f"Error {i} in path {x['path']}\n"
            output += f"\tMessage: {x['message']}\n"
            output += f"\tSchema_path: {x['schema_path']}\n"
            output += f"\tInstance: {x['instance']}\n"
            output += f"\tUnderlaying error: {x['underlaying']}\n"
            output += "\n"
        return output

    def get_mesage(self):
        return self.get_error()


class JsonSchemaValidatorTool():
    json_schema_validator: object = None

    @classmethod
    def load_schema(cls, schema):
        return cls(schema)

    @classmethod
    def load_from_file(cls, filename):
        fp = open(filename, "r")
        data = fp.read()
        fp.close()
        return cls.load_schema(json.loads(data))


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
        local_data = data
        if isinstance(data, str):
            local_data = json.loads(data)

        validator = Draft202012Validator(self.json_schema_validator)
        errors = sorted(validator.iter_errors(local_data), key=lambda e: e.path)
        if len(errors) > 0:
            raise JsonSchemaValidationException(errors, local_data)

        return True

    def _transform(self, data):
        doc = yaml.safe_load(data)
        return doc
