import streamlit as st

DIRECTORIES = {
    "job": "data/jobs/",
    "candidate": "data/candidates/",
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
    "system": (
        "You will be responsible for automatically conducting interviews with candidates in English."
        " Your tasks include:"
        "\n"
        "\n1. Screening candidates and asking basic technical questions."
        "\n2. Customizing questions based on Job Description and Candidate Profile."
        "\n3. Conducting the interview."
        "\n4. Generating an evaluation report after each interview."
        "\n---\n\n"
        "Here's a Markdown document of the Job Description: {jd_document}"
        "\n---\n\n"
        "Here's a Markdown document of the Candidate Profile: {profile_document}"
    ),
    "start": (
        "Tasks:"
        "\n- Welcome the candidate to the interview."
        "\n- Mention the 'company name' and the 'job title' they are applying to."
        " If 'company name' is not available in the Job Description document,"
        " refer to it as 'our company'"
        "\n- Ask the candidate to briefly introduce themself."
        " Especially their past experience related to the 'job title'"
        "\n---\n\n"
        "Tone: professional but still helpful and friendly"
    ),
}
