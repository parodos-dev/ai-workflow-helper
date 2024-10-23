from langchain_community.chat_models import ChatOllama
# from langchain_experimental.llms.ollama_functions import OllamaFunctions
# from langchain_openai import OpenAIEmbeddings

from langchain_community.embeddings import OllamaEmbeddings, FakeEmbeddings, HuggingFaceEmbeddings
# from langchain_openai import ChatOpenAI

#from langchain.chains import LLMChain
from langchain_community.llms import Replicate
#from langchain_core.prompts import PromptTemplate

class LlmRunner():
    def __init__(self, runner, base_url, model):
        self._runner = runner
        self.base_url = base_url
        self.model = model
        self._embeddings = None
        self._ollama = None
        self._replicate = None

    @property
    def llm(self):
        if self._runner == "replicate":
            if not self._replicate:
                self._replicate = Replicate(model=self.model, 
                                            # model_kwargs={"temperature": 0.75, "max_length": 500, "top_p": 1}
                                            )
            return self._replicate    
        else:
            if not self._ollama:
                # Normally we should use ChatOllama, but does not support
                # OllamaFunctions.
                # On the other hand, the OpenAI has better support for multiple actions
                # in langchain, let's take advantage of it
                self._ollama = ChatOllama(
                    base_url=self.base_url,
                    model=self.model,
                    temperature=0,
                    num_ctx=20000,
                )
                # self._ollama = ChatOpenAI(
                #     base_url=self.base_url + "/v1",
                #     api_key="no-need",
                #     model=self.model,
                #     temperature=0
                # )
                # self._ollama = OllamaFunctions(
                #     base_url=self.base_url,
                #     model=self.model,
                #     format="json")
            return self._ollama

    @property
    def embeddings(self):
        if not self._embeddings:
            if self._runner == "replicate":
                self._embeddings = FakeEmbeddings(size=4096)
            else:
                self._embeddings = OllamaEmbeddings(
                    base_url=self.base_url,
                    model=self.model)
                # self._embeddings = OpenAIEmbeddings(
                #     base_url=self.base_url + "/api",
                #     api_key="no-need",
                #     model=self.model
                # )
        return self._embeddings

    @classmethod
    def parse_document(cls, splitter, content):
        # @TODO here the splitter can be different, and we should check the
        # content[].metadata.source filename type, so:
        # - Markdown: https://api.python.langchain.com/en/latest/text_splitters_api_reference.html#module-langchain_text_splitters.markdown # noqa: E501
        # - HTML: https://api.python.langchain.com/en/latest/text_splitters_api_reference.html#module-langchain_text_splitters.html # noqa: E501

        text_splitter = splitter()
        documents = text_splitter.split_documents(content)
        return documents
