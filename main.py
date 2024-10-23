import click
import logging
import sys
import requests
import os

from api.urls import urls
from config import Config
from const import  SAMPLE_QUERY
from lib.history import HistoryRepository
from lib.json_validator import JsonSchemaValidatorTool, JsonSchemaValidationException
from lib.models import SerVerlessWorkflow
from lib.llm_runner import LlmRunner
from lib.repository import VectorRepository
from lib.retriever import Retriever
from lib.validator import OutputValidator
from lib.serverless_validation import ServerlessValidation
from langchain.globals import set_debug

from flask import Flask, g

def setup_logging():
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(stream=sys.stderr, level=log_level)
    if log_level == "DEBUG":
        set_debug(True)

MODELS_EMBEDDINGS = {
    "llama3.2:3b": 3072
}

class Context:
    def __init__(self, config):
        self.config = config

        self.llm_runner = LlmRunner(self.config.llm_runner, self.config.base_url, self.config.model)
        self.repo = VectorRepository(self.config.db, self.llm_runner.embeddings, embeddings_len=MODELS_EMBEDDINGS.get(self.config.model, 4096))

        self.validator = OutputValidator(
            SerVerlessWorkflow,
            JsonSchemaValidatorTool.load_from_file("lib/schema/workflow.json"))

        self.history_repo = HistoryRepository(
            session_id="empty",
            connection="sqlite:///{0}".format(self.config.chat_db))


app = Flask(
    __name__,
    static_folder='static',
)


@app.before_request
def before_request():
    g.ctx = Context(Config())


# @TODO delete this method
@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = Context(Config())
    pass


# @TODO Move this method to the servives
@click.command()
@click.argument('file-path')
@click.pass_obj
def load_data(obj, file_path):
    repo = obj.repo
    try:
        content = Retriever.fetch(file_path)
    except Exception as e:
        click.echo(f"cannot read file-path {e}")
        sys.exit(1)

    splitter = Retriever.get_splitters(file_path)
    documents = obj.llm_runner.parse_document(splitter, content)

    if len(documents) == 0:
        click.echo("The len of the documents is 0")
        sys.exit(1)
    try:
        res = repo.add_documents(documents)
    except Exception as e:
        click.echo(f"cannot create or storing the embeddings: {e}")
        sys.exit(1)
    repo.save()
    click.echo("{0} documents added with ids {1}".format(len(documents), res))


@click.command()
@click.pass_obj
def run(obj):
    for x in urls:
        app.add_url_rule(x[0], view_func=x[1], methods=x[2])
    app.run(debug=True)


@click.command()
@click.argument('example', required=False)
@click.pass_obj
def sample_request(obj, example):
    url = "http://localhost:5000/chat"
    headers = {
        'Content-type': 'application/json',
    }
    query = SAMPLE_QUERY
    if example:
        with open(f"examples/prompts/{example}.txt", "r") as fp:
            query = fp.read()
    data = {'input': query}
    response = requests.post(url, json=data, headers=headers, stream=True)
    for line in response.iter_lines():
        print(line.decode('utf-8'))
    session_id = response.headers.get('session_id')
    click.echo(f"The session_id is: {session_id}")

@click.command()
@click.argument('file-path', required=True)
@click.pass_obj
def validate_json(obj, file_path):
    fp = open(file_path, "r")
    workflow = fp.read()
    fp.close()
    click.echo("JSONschema validation:")
    try:
        obj.validator.invoke(workflow)
    except JsonSchemaValidationException as e:
        click.echo(e.get_error())

    click.echo("Maven compilation validation:")
    serverless_validation, valid = ServerlessValidation(workflow).run()
    click.echo(serverless_validation)
    click.echo(f"The workflow can compile, result: {valid}")

setup_logging()
cli.add_command(load_data)
cli.add_command(run)
cli.add_command(sample_request)
cli.add_command(validate_json)


if __name__ == '__main__':
    cli()
