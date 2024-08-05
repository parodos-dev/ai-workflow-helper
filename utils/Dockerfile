From docker.io/python:3.12

RUN mkdir /app/
WORKDIR /app/
RUN apt-get update
RUN apt-get install -y yq vim git
RUN pip install datamodel-code-generator pydantic==2.7.4
RUN git clone https://github.com/serverlessworkflow/specification.git -b 0.8.x

# RUN curl https://raw.githubusercontent.com/serverlessworkflow/specification/main/schema/workflow.yaml -o  /app/workflow.yaml
#RUN cat /app/workflow.yaml | yq . > /app/workflow.json

#ENTRYPOINT datamodel-codegen --input /app/workflow.json --input-file-type jsonschema --output-model-type pydantic.BaseModel  --use-union-operator
