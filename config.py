

import os

FAISS_DB = "/tmp/db_faiss"
# MODEL = "llama3.1:8b"
MODEL = "granite-code:8b"
OLLAMA_URL = "http://localhost:11434"
SPEC_URL = "https://raw.githubusercontent.com/serverlessworkflow/specification/0.8.x/specification.md" # noqa E501
SQLITE_DB = "chats.db"
LLM_RUNNER = "ollama" # or "replicate"

class Config:
    def __init__(self):
        self.llm_runner = self.get_env_variable('LLM_RUNNER', LLM_RUNNER)
        self.model = self.get_env_variable('LLM_MODEL', MODEL)
        self.base_url = self.get_env_variable('LLM_URL', OLLAMA_URL)
        self.db = self.get_env_variable('FAISS_DB', FAISS_DB)
        self.chat_db = self.get_env_variable('SQLITE_DB', SQLITE_DB)

    @staticmethod
    def get_env_variable(var_name, default_value):
        return os.getenv(var_name, default_value)
