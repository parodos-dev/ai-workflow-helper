import click
import logging
import sys
import requests
import os

from api.urls import urls
from config import Config
from const import  SAMPLE_QUERY
from lib.history import HistoryRepository
from lib.json_validator import JsonSchemaValidatorTool
from lib.models import SerVerlessWorkflow
from lib.ollama import Ollama
from lib.repository import VectorRepository
from lib.retriever import Retriever
from lib.validator import OutputValidator


from flask import Flask, g

logging.basicConfig(stream=sys.stderr, level=os.environ.get('LOG_LEVEL', 'INFO').upper())


class Context:
    def __init__(self, config):
        self.config = config
        self.ollama = Ollama(self.config.base_url, self.config.model)
        self.repo = VectorRepository(self.config.db, self.ollama.embeddings)

        self.validator = OutputValidator(
            SerVerlessWorkflow,
            JsonSchemaValidatorTool.load_from_file("lib/schema/serverless_workflow.json"))

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
    documents = obj.ollama.parse_document(splitter, content)

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

cli.add_command(load_data)
cli.add_command(run)
cli.add_command(sample_request)

if __name__ == '__main__':
    cli()
