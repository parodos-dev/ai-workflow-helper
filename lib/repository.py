import os

from langchain_community.vectorstores import FAISS
from faiss import IndexFlatL2
from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_community.docstore.in_memory import Docstore


class VectorRepository:

    def __init__(self, path, embeddings, index_name="faissIndex", embeddings_len=4096):
        self._index_name = index_name
        self.path = path
        self.embeddings = embeddings
        self.embeddings_len = embeddings_len
        self.initialized = False


    def _initialize(self):
        # Same initialization as here:
        # https://github.com/langchain-ai/langchain/blob/379803751e5ae40a2aadcb4072dbb2525187dd1f/libs/community/langchain_community/vectorstores/faiss.py#L871 # noqa E501

        index = IndexFlatL2(self.embeddings_len)
        self.faiss = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore= InMemoryDocstore(),
            index_to_docstore_id={}
        )

        if not os.path.isfile(os.path.join(self.path, "index.faiss")):
            self.faiss.save_local(folder_path=self.path)

        # @TODO check if pickle serialization can be changed
        self._vector_store = self.faiss.load_local(
                folder_path=self.path,
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True)
        self.initialized = True

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
        if not self.initialized:
            self._initialize()
        return self._vector_store.as_retriever()
