From docker.io/python:3.12

RUN mkdir /app/
RUN apt-get update
RUN apt-get install -y yq vim
RUN pip install datamodel-code-generator pydantic==2.7.4

RUN curl https://raw.githubusercontent.com/serverlessworkflow/specification/main/schema/workflow.yaml -o  /app/workflow.yaml
RUN cat /app/workflow.yaml | yq . > /app/workflow.json

ENTRYPOINT datamodel-codegen --input /app/workflow.json --input-file-type jsonschema --output-model-type pydantic.BaseModel  --use-union-operator
