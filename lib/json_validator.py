from jsonschema import validate
import requests
import yaml


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
        import json
        f = open("/tmp/data.json", "w")
        f.write(json.dumps(data, indent=2))
        f.close()
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
