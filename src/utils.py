import json
import os
from typing import Dict, List

import src.settings as settings


def read_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filepath: str, content: str):
    with open(filepath, "w+", encoding="utf-8") as f:
        f.write(content)


def write_json(filepath: str, content: Dict | List):
    with open(filepath, "w+", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)


def get_filepath(dirname: str, filename: str) -> str:
    return os.path.join(settings.DIRECTORIES[dirname], filename)


def add_debug(*args):
    if settings.DEBUGGING:
        print(*args, sep="\n")


# def get_instruction(name: str, **kwargs):
#     filename = f"{name}.md"
#     filepath = get_filepath("instruction", filename)
#     template = read_file(filepath)
#     instruction = template.format(**kwargs)
#     return instruction
