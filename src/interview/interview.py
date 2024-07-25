from typing import List

import streamlit as st

import src.settings as settings
import src.utils as utils
from src.service import service as _service

code: str = st.session_state["code"]
application = utils.get_application(code)
application = utils.set_documents(application)
device: str = st.session_state["device"]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []


@st.experimental_dialog("Tips")
def show_tips():
    st.info(
        ":blue[Click the `>` button to open the sidebar]",
        icon=":material/chevron_right:",
    )

    if st.session_state["device"] == "desktop":
        st.info(
            ":blue[Move the cursor to the right edge of the sidebar to resize it]",
            icon=":material/width:",
        )

    if st.button("Thanks"):
        st.rerun()


jd_type = application["job"]["filetype"]
jd_document = application["job"]["document"]
profile_type = application["candidate"]["filetype"]
profile_document = application["candidate"]["document"]

with st.sidebar.expander("Job Description") as ex:
    st.write(jd_document)

# Initialize service
if "service" not in st.session_state:
    with st.spinner("Processing..."):
        st.session_state["service"] = _service.Service(settings.MODEL_NAME, application)
    show_tips()


messages: List = st.session_state["messages"]
service: _service.Service = st.session_state["service"]


# Display chat messages from history on app rerun
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not service.started:
    with st.chat_message("assistant"):
        instruction = utils.get_instruction("start")
        chunks = service.start(instruction)
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
