import streamlit as st
from streamlit_user_device import user_device

import src.utils as utils
from src.service.application import Application, ApplicationNotFoundError
from src.service.document import DocumentNotFoundError, DocumentTypeNotSupportedError

st.set_page_config(
    page_title="Interview Agent",
    page_icon="📄",
    initial_sidebar_state="collapsed",
)

if "interview_id" not in st.session_state:
    st.session_state["interview_id"] = None

if "application" not in st.session_state:
    st.session_state["application"] = None

if "step" not in st.session_state:
    st.session_state["step"] = None

if "device" not in st.session_state:
    st.session_state["device"] = "desktop"


STEPS = [None, "Home", "Interview", "End"]


def login():
    interview_id = st.text_input(
        "Interview ID", placeholder="aie-nmv", autocomplete="aie-nmv"
    )
    container = st.container(border=1)
    container.caption("Details")
    if not interview_id:
        st.session_state["application"] = None
        container.warning(
            "Please enter the Interview ID",
            icon=":material/person_alert:",
        )
        container.info(
            "It can be found in the invitation",
            icon=":material/info:",
        )
    else:
        try:
            application = Application(interview_id)
            container.success(
                f"**{application.job.document.title} found at: `{application.job.document.filename}`**",
                icon=application.job.document.st_icon,
            )
            container.success(
                f"**{application.candidate.document.title} found at: `{application.candidate.document.filename}`**",
                icon=application.candidate.document.st_icon,
            )
            st.session_state["application"] = application
        except ApplicationNotFoundError as e:
            st.session_state["application"] = None
            container.warning(e.args[-1], icon=":material/person_alert:")
            container.info("Please check the invitation", icon=":material/info:")
        except (
            DocumentTypeNotSupportedError,
            DocumentNotFoundError,
        ) as e:
            st.session_state["application"] = None
            container.error(
                f"An error occured: {e.args[-1]}", icon=":material/data_alert:"
            )
            container.warning(
                f"Please contact HR", icon=":material/person_raised_hand:"
            )

    start_button = st.button(
        "Start",
        type="primary",
        disabled=not st.session_state["application"],
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

application = st.session_state["application"]
step = st.session_state["step"]

interview = st.Page(
    "src/pages/interview.py",
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
