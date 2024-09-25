import os
# import requests

# from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownTextSplitter


class Retriever:

    @classmethod
    def fetch(cls, source):
        if cls.is_url(source):
            return cls.fetch_from_url(source)
        elif cls.is_file(source):
            return cls.fetch_from_file(source)
        else:
            raise ValueError(f"Source file '{source}' is not valid")

    @classmethod
    def get_splitters(cls, source):
        if cls.is_url(source):
            return RecursiveCharacterTextSplitter
        elif cls.is_file(source):
            if Retriever.is_markdown_file(source):
                return MarkdownTextSplitter
            return RecursiveCharacterTextSplitter
        else:
            raise ValueError(f"Source file '{source}' is not valid")

    @staticmethod
    def is_url(source):
        return source.startswith('http://') or source.startswith('https://')

    @staticmethod
    def is_file(source):
        return os.path.isfile(source)

    @staticmethod
    def is_markdown_file(file_path):
        markdown_extensions = ['.md', '.markdown', '.mdown', '.mkdn']
        return any(
                file_path.lower().endswith(ext) for ext in markdown_extensions)

    @staticmethod
    def fetch_from_url(url):
        loader = RecursiveUrlLoader(
            url,
            max_depth=3,
        )
        # loader = WebBaseLoader(url)
        return loader.load()

    @staticmethod
    def fetch_from_file(file_path):
        loader = TextLoader(file_path)
        if Retriever.is_markdown_file(file_path):
            loader = UnstructuredMarkdownLoader(
                file_path,
                mode="single",
                strategy="fast",
            )
        return loader.load()
