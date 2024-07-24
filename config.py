

import os

FAISS_DB = "/tmp/db_faiss"
# MODEL = "llama3.1:8b"
MODEL = "granite-code:8b"
OLLAMA_URL = "http://localhost:11434"
SPEC_URL = "https://raw.githubusercontent.com/serverlessworkflow/specification/0.8.x/specification.md" # noqa E501
WORKFLOW_SCHEMA_URL="https://raw.githubusercontent.com/serverlessworkflow/specification/main/schema/workflow.yaml" # noqa E501


class Config:
    def __init__(self):
        self.model = self.get_env_variable('OLLAMA_MODEL', MODEL)
        self.base_url = self.get_env_variable('OLLAMA_URL', OLLAMA_URL)
        self.db = self.get_env_variable('FAISS_DB', FAISS_DB)
        self.workflow_schema_url = self.get_env_variable(
                'WORKFLOW_SCHEMA_URL', WORKFLOW_SCHEMA_URL)

    @staticmethod
    def get_env_variable(var_name, default_value):
        return os.getenv(var_name, default_value)
