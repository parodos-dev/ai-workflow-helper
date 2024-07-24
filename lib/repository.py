import os

from langchain_community.vectorstores import FAISS
from faiss import IndexFlatL2
from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_community.docstore.in_memory import Docstore


class VectorRepository:

    def __init__(self, path, embeddings, index_name="faissIndex"):
        self._index_name = index_name
        self.path = path
        self.embeddings = embeddings

        self._initialize()

    def _initialize(self):
        # Same initialization as here:
        # https://github.com/langchain-ai/langchain/blob/379803751e5ae40a2aadcb4072dbb2525187dd1f/libs/community/langchain_community/vectorstores/faiss.py#L871 # noqa E501
        # @TODO The 4096 is the shape size of the embeddings, currently
        # hardcoded, but maybe we can get from OllamaEmbeddings class?
        self.faiss = FAISS(
            embedding_function=self.embeddings,
            index=IndexFlatL2(4096),
            docstore=InMemoryDocstore(),
            normalize_L2=False,
            index_to_docstore_id={},
        )

        if not os.path.isfile(os.path.join(self.path, "index.faiss")):
            self.faiss.save_local(folder_path=self.path)

        # @TODO check if pickle serialization can be changed
        self._vector_store = self.faiss.load_local(
                folder_path=self.path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True)

    def save(self):
        # This get the current InMemoryDocstore and save into the disk
        # self.faiss.save_local(
        # folder_path=self.path,
        # index_name = self._index_name
        # )
        self._vector_store.save_local(folder_path=self.path)

    def add_documents(self, docs: [str]):
        return self._vector_store.add_documents(docs)

    @property
    def vectordb(self):
        return self._vector_store

    @property
    def retriever(self):
        return self._vector_store.as_retriever()
