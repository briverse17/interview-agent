import os
from typing import Dict

import src.settings as settings


class DocumentNotFoundError(FileNotFoundError):
    pass


class DocumentBlankError(RuntimeError):
    pass


class DocumentTypeNotSupportedError(RuntimeError):
    pass


def read_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        if content:
            return content
        else:
            filename = os.path.basename(filepath)
            raise DocumentBlankError(f"Document is blank: {filename}")


def write_file(filepath: str, content: str):
    with open(filepath, "w+", encoding="utf-8") as f:
        f.write(content)


def set_filetypes(application: Dict) -> Dict:
    for type in ("job", "candidate"):
        if "filetype" not in application[type]:
            filename: str = application[type]["filename"]
            if filename.lower().endswith(".md"):
                application[type]["filetype"] = "Markdown"
            elif filename.lower().endswith(".txt"):
                application[type]["filetype"] = "Plain text"
            else:
                raise DocumentTypeNotSupportedError(
                    f"Document type not supported: {filename}"
                )

    return application


def get_filepath(dirname: str, filename: str):
    return os.path.join(settings.DIRECTORIES[dirname], filename)


def set_filepaths(application: Dict) -> Dict:
    for type in ("job", "candidate"):
        if "filepath" not in application[type]:
            filename: str = application[type]["filename"]
            filepath = get_filepath(type, filename)
            if os.path.isfile(filepath):
                application[type]["filepath"] = filepath
            else:
                raise DocumentNotFoundError(f"Document not found: {filename}")

    return application


def set_documents(application: Dict) -> Dict:
    application = set_filetypes(application)
    application = set_filepaths(application)
    for type in ("job", "candidate"):
        application[type]["document"] = read_file(application[type]["filepath"])

    return application


def get_application(code: str):
    return settings.APPLICATIONS.get(code)


def set_application(code: str, application: Dict):
    settings.APPLICATIONS[code] = application


def add_debug(*args):
    if settings.DEBUGGING:
        print(*args, sep="\n")


def get_instruction(name: str, **kwargs):
    filename = f"{name}.md"
    filepath = get_filepath("instruction", filename)
    template = read_file(filepath)
    instruction = template.format(**kwargs)
    return instruction
