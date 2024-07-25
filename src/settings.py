import streamlit as st

DIRECTORIES = {
    "job": "data/jobs/",
    "candidate": "data/candidates/",
    "instruction": "data/model_instructions/",
}

APPLICATIONS = {
    "aie-nmv": {
        "job": {"id": "aie", "filename": "aie.md"},
        "candidate": {"id": "nmv", "filename": "nmv.md"},
    }
}

APIKEY = st.secrets["GEMINI_API_KEY"]
MODEL_NAME = "gemini-1.5-flash"
MODEL_INSTRUCTIONS = {
    "system": "system.md",
    "read_jd": "read_jd.md",
    "start": "start.md",
}

DEBUGGING = bool(st.secrets["DEBUGGING"])
print("Debugging:", DEBUGGING)
