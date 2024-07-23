import streamlit as st

import utils
from settings import CODES

if "code" not in st.session_state:
    st.session_state.code = None

if "step" not in st.session_state:
    st.session_state.step = None

STEPS = [None, "Home", "Interview", "End"]


def login():
    code = st.text_input(
        "Interview code", placeholder="aie_nmv", autocomplete="aie_nmv"
    )
    if not code:
        st.warning(
            "Please enter the interview code provided in the email",
            icon=":material/person_alert:",
        )
    elif code not in CODES:
        st.warning(
            f"Interview code '{code}' not found",
            icon=":material/person_alert:",
        )
    else:
        application = CODES[code]
        st.session_state.code = code

        container = st.container(border=1)
        container.caption("Details")

        jd_filename = application["job"]["filename"]
        jd_filepath = utils.get_filepath("job", jd_filename)
        if not jd_filepath:
            container.warning(
                f"Job Description not found. Please contact HR.",
                icon=":material/data_alert:",
            )
        else:
            expander = container.expander(
                f"**Job Description found at: `{jd_filename}`.** Click to view"
            )
            displayer = expander.write
            if jd_filename.lower().endswith(".md"):
                displayer = expander.markdown

            displayer(utils.read_file(jd_filepath))

        profile_filename = application["candidate"]["filename"]
        profile_filepath = utils.get_filepath("candidate", profile_filename)
        if not profile_filepath:
            container.warning(
                f"Candidate Profile not found. Please contact HR.",
                icon=":material/data_alert:",
            )
        else:
            expander = container.expander(
                f"**Candidate Profile found at: `{profile_filename}`.** Click to view"
            )
            displayer = expander.write
            if profile_filename.lower().endswith(".md"):
                displayer = expander.markdown

            displayer(utils.read_file(profile_filepath))

        if st.button("Start Interview", type="primary", use_container_width=True):
            # pages = [st.Page("pages/Interview.py")]

            st.session_state.code = code
            st.session_state.step = "Interview"
            st.rerun()


# def logout():
#     st.session_state.role = None
#     st.rerun()


step = st.session_state.step
code = st.session_state.code

interview = st.Page(
    "interview/interview.py",
    title="Interview",
    icon=":material/settings:",
    default=(step == "Interview"),
)
interview_pages = [interview]


st.set_page_config(
    page_title="Interview Agent",
    page_icon="📄",
)

st.title("📄 Interview Agent")
st.write("## Welcome! 👋")

page_dict = {}
if st.session_state.step in ["Interview"]:
    page_dict["Interview"] = interview_pages

if len(page_dict) > 0:
    pg = st.navigation({"Interview": interview_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()
