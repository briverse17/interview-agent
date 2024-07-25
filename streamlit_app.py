import streamlit as st
from streamlit_user_device import user_device

import src.utils as utils

st.set_page_config(
    page_title="Interview Agent",
    page_icon="📄",
    initial_sidebar_state="collapsed",
)

if "code" not in st.session_state:
    st.session_state["code"] = None

if "step" not in st.session_state:
    st.session_state["step"] = None

if "device" not in st.session_state:
    st.session_state["device"] = "desktop"


STEPS = [None, "Home", "Interview", "End"]


# @st.experimental_dialog("Interview code")
def login():
    code = st.text_input(
        "Interview code", placeholder="aie-nmv", autocomplete="aie-nmv"
    )
    container = st.container(border=1)
    container.caption("Details")
    if not code:
        st.session_state["code"] = None
        container.warning(
            "Please enter the Interview Code",
            icon=":material/person_alert:",
        )
        container.info(
            "It can be found in the invitation",
            icon=":material/info:",
        )
    else:
        application = utils.get_application(code)
        if not application:
            st.session_state["code"] = None
            container.warning(
                f"Interview code '{code}' not found",
                icon=":material/person_alert:",
            )
            container.info(
                "Please check the invitation",
                icon=":material/info:",
            )
        else:
            st.session_state["code"] = code
            application = utils.get_application(code)

            try:
                application = utils.set_filetypes(application)
                application = utils.set_filepaths(application)
                container.success(
                    f"**Job Description found at: `{application['job']['filename']}`**",
                    icon=(
                        ":material/markdown:"
                        if application["job"]["filetype"] == "Markdown"
                        else ":material/text_snippet:"
                    ),
                )
                container.success(
                    f"**Candidate Profile found at: `{application['candidate']['filename']}`**",
                    icon=(
                        ":material/markdown:"
                        if application["candidate"]["filetype"] == "Markdown"
                        else ":material/text_snippet:"
                    ),
                )
                utils.set_application(code, application)

            except (
                utils.DocumentTypeNotSupportedError,
                utils.DocumentNotFoundError,
            ) as e:
                container.error(
                    f"An error occured:\n{e.args[0]}",
                    icon=":material/data_alert:",
                )
                container.warning(
                    f"Please contact HR",
                    icon=":material/person_raised_hand:",
                )

    start_button = st.button(
        "Start",
        type="primary",
        disabled=not st.session_state["code"],
        use_container_width=True,
    )
    # device info
    device = user_device()
    st.session_state["device"] = device

    if start_button:
        st.session_state["step"] = "Interview"
        st.rerun()


st.title("📄 Interview Agent")
st.write("## Welcome! 👋")

code = st.session_state["code"]
step = st.session_state["step"]

interview = st.Page(
    "src/interview/interview.py",
    title="Interview",
    icon=":material/settings:",
    default=(step == "Interview"),
)
interview_pages = [interview]


page_dict = {}
if st.session_state["step"] in ["Interview"]:
    page_dict["Interview"] = interview_pages

if len(page_dict) > 0:
    pg = st.navigation({"Interview": interview_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()
