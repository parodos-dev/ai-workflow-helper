from jsonschema import validate
import requests
import yaml
import json


class JsonSchemaValidatorTool():
    json_schema_validator: object = None

    def __init__(self, url):
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception("Invalid URL status-code={resp.status_code}")
        try:
            schema = self._transform(resp.text)
        except Exception as e:
            raise Exception(f"Invalid yaml definition: {e}")

        self.json_schema_validator = schema

    def validate(self, data):
        if isinstance(data, dict):
            return validate(instance=data, schema=self.json_schema_validator)

        if isinstance(data, str):
            return validate(
                instance=json.loads(data),
                schema=self.json_schema_validator)

        raise Exception(
                "Type of data '{}' cannot be parsed".format(type(data)))

    def _transform(self, data):
        doc = yaml.safe_load(data)
        return doc
