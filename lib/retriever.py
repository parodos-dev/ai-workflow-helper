import os
# import requests

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import TextLoader


class Retriever:
    @classmethod
    def fetch(cls, source):
        if cls.is_url(source):
            return cls.fetch_from_url(source)
        elif cls.is_file(source):
            return cls.fetch_from_file(source)
        else:
            raise ValueError(f"Source file '{source}' is not valid")

    @staticmethod
    def is_url(source):
        return source.startswith('http://') or source.startswith('https://')

    @staticmethod
    def is_file(source):
        return os.path.isfile(source)

    @staticmethod
    def fetch_from_url(url):
        loader = WebBaseLoader(url)
        return loader.load()

    @staticmethod
    def fetch_from_file(file_path):
        loader = TextLoader(file_path)
        return loader.load()
