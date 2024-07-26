from typing import List

import streamlit as st

from src.service.application import Application
from src.service.llm import LLM
from src.service.phase import HistoryEntryItem, Phase
from src.settings import MODEL_NAME

application: Application = st.session_state["application"]
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


with st.sidebar.expander("Job Description") as ex:
    st.write(application.job.document.content)

# Initialize service
if "llm" not in st.session_state:
    with st.spinner("Processing..."):
        st.session_state["llm"] = LLM(MODEL_NAME, application)
    show_tips()


messages: List = st.session_state["messages"]
llm: LLM = st.session_state["llm"]


# Display chat messages from history on app rerun
for item in llm.chat_history:
    with st.chat_message(item.st_role):
        st.markdown(item.content)

if not llm.current_phase:
    with st.chat_message("assistant"):
        chunks = llm.update("start")
        response = st.write_stream(chunks)
        llm.current_phase.update_history("question", response)

if prompt := st.chat_input("Your message..."):
    llm.current_phase.update_history("answer", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        llm.eval()
        with st.spinner("Processing..."):
            chunks = llm.update(*llm.follow())
            response = st.write_stream(chunks)
            llm.current_phase.update_history("question", response)
