import os

from src.utils import read_file


class DocumentNotFoundError(FileNotFoundError):
    pass


class DocumentBlankError(RuntimeError):
    pass


class DocumentTypeNotSupportedError(RuntimeError):
    pass


class Document:
    def __init__(self, path: str, title: str=None):
        self.path = path
        self.title = title
        self.filename: str
        self.filetype: str
        self.st_icon: str
        self.content = read_file(self.path)
        self.parsed_content: str

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def filetype(self):
        if self.path.lower().endswith(".md"):
            return "Markdown"
        elif self.path.lower().endswith(".txt"):
            return "Plain text"
        else:
            raise DocumentTypeNotSupportedError(
                f"Document type not supported: {self.filename}"
            )

    @property
    def st_icon(self):
        if self.filetype == "Markdown":
            return ":material/markdown:"
        return ":material/text_snippet:"

    @property
    def parsed_content(self):
        return self._parsed_content

    @parsed_content.setter
    def parsed_content(self, value):
        self._parsed_content = value

    def read_content(self):
        content = read_file(self.path)
        if content:
            return content
        else:
            raise DocumentBlankError(f"Document is blank: {self.filename}")

