import os

from src.service.document import Document, DocumentNotFoundError
from src.settings import APPLICATIONS, DIRECTORIES
from src.utils import get_path

class ApplicationNotFoundError(RuntimeError):
    pass


class ApplicationData:
    def __init__(self, type, id: str) -> None:
        self.type = type
        self.id = id
        self.document = self.load_document()

    def entitle_document(self):
        if self.type == "job":
            return "Job Title"
        return "Candidate Profile"

    def load_document(self):
        md_path = get_path(self.type, f"{self.id}.md")
        txt_path = get_path(self.type, f"{self.id}.txt")
        if os.path.exists(md_path):
            return Document(md_path, self.entitle_document())
        elif os.path.exists(txt_path):
            return Document(txt_path, self.entitle_document())
        else:
            raise DocumentNotFoundError(
                f"No document not found for {self.type} `{self.id}`"
            )


class Application:
    def __init__(self, id: str) -> None:
        self.id = id
        self.job: ApplicationData = None
        self.candidate: ApplicationData = None
        self.load()

    def load(self):
        data = APPLICATIONS.get(self.id)
        if data:
            for key in data:
                setattr(self, key, ApplicationData(key, data[key]["id"]))
        else:
            raise ApplicationNotFoundError(
                f"No application found for Interview ID `{self.id}`"
            )
