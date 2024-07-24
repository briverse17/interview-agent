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
        "You will be responsible for automatically conducting interviews with candidates in English. Your tasks include:"
        "\n\n"
        "1. Screening candidates and asking basic technical questions.\n"
        "2. Customizing questions based on Job Description and Candidate Profile.\n"
        "3. Conducting the interview.\n"
        "4. Generating an evaluation report after each interview.\n\n---\n\n"
        "Here's a Markdown document of the Job Description: {jd_document} \n\n---\n\n"
        "Here's a Markdown document of the Candidate Profile: {profile_document}"
    ),
    "start": (
        "Task:"
        "\n- Welcome the candidate to the interview."
        "\n- Mention the COMPANY NAME and the JOB POSITION they are applying to."
        " If COMPANY NAME is not available in the Job Description,"
        " refer to it as 'our company'"
        "\n- Ask 1 icebreaker question to help them relax"
        " and feel more comfortable to start the interview."
        "\n\n---\n\n"
        "Tone: professional but still helpful and friendly, can be a bit humorous"
    ),
}
