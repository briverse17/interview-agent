import os

import google.generativeai as genai
import streamlit as st

import utils
from settings import ACCOUNTS

st.set_page_config(
    page_title="Interview Agent",
    page_icon="📄",
)

# Show title and description.
st.title("📄 Interview Agent")
st.write("## Welcome! 👋")

account_name = st.text_input(
    "Account name", placeholder="aie_nmv", autocomplete="aie_nmv"
)
if not account_name:
    st.warning(
        f"Please enter the account name provided in the email",
        icon=":material/person_alert:",
    )
else:
    account = ACCOUNTS[account_name]
    container = st.container(border=1)
    container.caption("Related documents")
    display_container = st.container(border=1)
    col1, col2 = container.columns(2)
    jd_filepath = utils.get_filepath("job", account["job"]["filename"])
    if not jd_filepath:
        col1.warning(
            f"Job Description not found. Please contact HR.",
            icon=":material/data_alert:",
        )
    else:
        icon = ":material/text_snippet:"
        displayer = display_container.write
        if account["job"]["filename"].lower().endswith(".md"):
            icon = ":material/markdown:"
            displayer = display_container.markdown

        col1.success(
            f"Job Description found at: `{account['job']['filename']}`",
            icon=icon,
        )
        if col1.button("Show Job Description"):
            expander = display_container.expander("Displayer")
            expander.markdown(utils.read_file(jd_filepath))

    profile_filepath = utils.get_filepath("candidate", account["candidate"]["filename"])
    if not profile_filepath:
        col2.warning(
            f"Candidate Profile not found. Please contact HR or upload one.",
            icon=":material/data_alert:",
        )
    else:
        icon = ":material/text_snippet:"
        displayer = display_container.write
        if account["candidate"]["filename"].lower().endswith(".md"):
            icon = ":material/markdown:"
            displayer = display_container.markdown

        col2.success(
            f"Candidate Profile found at: `{account['candidate']['filename']}`",
            icon=icon,
        )
        if col2.button("Show Candidate Profile"):
            expander = display_container.expander("Displayer")
            expander.markdown(utils.read_file(profile_filepath))

    help_col1, help_col2, help_col3 = st.columns([1,1,1])
    with help_col1:
        st.write("")

    with help_col2:
        st.button("Start Interview", type="primary", use_container_width=True)

    with help_col3:
        st.write("")
