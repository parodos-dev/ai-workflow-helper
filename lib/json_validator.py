from jsonschema import ValidationError, Draft202012Validator
import requests
import yaml
import json


def format_error(error: ValidationError) -> dict:

    underlaying = []

    state_type = ""
    if isinstance(error.instance, dict):
        state_type = error.instance.get("type")

    definition = f"#/definitions/{state_type}state"
    validator_schema = error.schema

    if state_type and error.validator in ["anyOf"]:
        path = None
        for i,x in enumerate(validator_schema.get(error.validator)):
            if x.get("$ref") == definition:
                path = i
                break
        i = 0
        for x in error.context:
            if x.schema_path[0] != path:
                continue
            subschema_path= ".".join([str(val) for val in x.schema_path])
            underlaying_error = f"\tSuberrror {i} in definition: {definition}\n"
            underlaying_error += f"\t\tFailed validating {x.validator!r} in {subschema_path}\n"
            underlaying_error += f"\t\tValidator value: ```{json.dumps(x.validator_value)}```"
            underlaying.append(underlaying_error.rstrip())
            i += 1
    return {
        "path": ".".join(str(path) for path in error.path),
        "message": error.message,
        "schema_path": ".".join(str(path) for path in error.schema_path),
        "instance": json.dumps(error.instance),
        "underlaying": "\n".join(underlaying)
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
            output += f"Error {i} in path `{x['path']}`:\n"
            output += f"\tSchema_path: {x['schema_path']}\n"
            output += f"\tInstance: ```{x['instance']}```\n"
            output += f"\tUnderlaying errors:\n{x['underlaying']}\n"
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
        errors = list(validator.iter_errors(local_data))
        if len(errors) > 0:
            raise JsonSchemaValidationException(errors, local_data)

        return True

    def _transform(self, data):
        doc = yaml.safe_load(data)
        return doc
