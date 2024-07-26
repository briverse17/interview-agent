import streamlit as st

SUPPORTED_FILETYPES = ["md", "txt"]

DIRECTORIES = {
    "job": "data/jobs/",
    "candidate": "data/candidates/",
    "instruction": "data/model_instructions/",
    "cache": "data/caches",
    "report": "data/reports",
    "conversation": "data/conversations",
}

APPLICATIONS = {
    "aie-nmv": {
        "job": {"id": "aie", "filename": "aie.md"},
        "candidate": {"id": "nmv", "filename": "nmv.md"},
    },
    "de-nmv": {
        "job": {"id": "de", "filename": "de.txt"},
        "candidate": {"id": "nmv", "filename": "nmv.md"},
    },
}

APIKEY = st.secrets["GEMINI_API_KEY"]
MODEL_NAME = "gemini-1.5-flash"

DEBUGGING = bool(st.secrets.get("DEBUGGING"))
print("Debugging:", DEBUGGING)
