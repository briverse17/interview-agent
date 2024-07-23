import os

from settings import DIRECTORIES


def get_filepath(type: str, filename: str):
    filepath = os.path.join(DIRECTORIES[type], filename)
    if os.path.isfile(filepath):
        return os.path.join(DIRECTORIES[type], filename)

def read_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        return content
