import time
from typing import List

import streamlit as st

import src.utils as utils
from src.service.service import Service
from src.settings import MODEL_INSTRUCTIONS, MODEL_NAME

code: str = st.session_state["code"]
application = utils.get_application(code)

jd_filename = application["job"]["filename"]
jd_filepath = utils.get_filepath("job", jd_filename)

profile_filename = application["candidate"]["filename"]
profile_filepath = utils.get_filepath("candidate", profile_filename)

jd_document = utils.read_file(jd_filepath)
profile_document = utils.read_file(profile_filepath)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Initialize service
if "service" not in st.session_state:
    st.session_state["service"] = Service(
        MODEL_NAME,
        MODEL_INSTRUCTIONS["system"].format(
            jd_document=jd_document,
            profile_document=profile_document,
        ),
    )

@st.experimental_dialog("Tips")
def tips():
    st.info(
        ":blue[Click the **>** button to open the sidebar]",
        icon=":material/chevron_right:",
    )
    st.info(
        ":blue[Move the cursor to the right edge of the sidebar to resize it]",
        icon=":material/width:",
    )
    if st.button("Thanks"):
        st.rerun()


with st.sidebar.expander("Job Description") as ex:
    st.markdown(jd_document)

with st.sidebar.expander("Candidate Profile"):
    st.markdown(profile_document)


messages: List = st.session_state["messages"]
service: Service = st.session_state["service"]


# Display chat messages from history on app rerun
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not service.started:
    tips()
    with st.chat_message("assistant"):
        chunks = service.start(MODEL_INSTRUCTIONS["start"])
        response = st.write_stream(chunks)
        messages.append({"role": "assistant", "content": response})

if prompt := st.chat_input("Your message..."):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chunks = service.chat(prompt)
        response = st.write_stream(chunks)
        messages.append({"role": "assistant", "content": response})
