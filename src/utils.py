import os

from src.settings import APPLICATIONS, DIRECTORIES


def get_filepath(type: str, filename: str):
    filepath = os.path.join(DIRECTORIES[type], filename)
    if os.path.isfile(filepath):
        return os.path.join(DIRECTORIES[type], filename)


def read_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        return content


def get_documents(application):
    jd_filename = application["job"]["filename"]
    jd_filepath = get_filepath("job", jd_filename)

    profile_filename = application["candidate"]["filename"]
    profile_filepath = get_filepath("candidate", profile_filename)

    jd_document = read_file(jd_filepath)
    profile_document = read_file(profile_filepath)
    return jd_document, profile_document

def get_application(code: str):
    return APPLICATIONS.get(code)
