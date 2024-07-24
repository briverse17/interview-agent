import google.generativeai as genai
import streamlit as st

# Show title and description.
st.title("📄 Interview Agent")

gemini_api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=gemini_api_key)

# Set a default model
if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-1.5-flash"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages from history on app rerun
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Let the user upload a file via `st.file_uploader`.
jd_file = st.sidebar.file_uploader(
    "Upload the Job Description (.txt or .md)", type=("txt", "md")
)
cv_file = st.sidebar.file_uploader(
    "Upload the Candidate Profile (.txt or .md)", type=("txt", "md")
)

if jd_file and cv_file:
    jd_document = jd_file.read().decode()
    cv_document = cv_file.read().decode()

    model_instruction = (
        "You will be responsible for automatically conducting interviews with candidates in English. Your tasks include:"
        "\n\n"
        "1. Screening candidates and asking basic technical questions.\n"
        "2. Customizing questions based on Job Description and Candidate Profile.\n"
        "3. Conducting the interview.\n"
        "4. Generating an evaluation report after each interview.\n\n---\n\n"
        f"Here's a Markdown document of the Job Description: {jd_document} \n\n---\n\n"
        f"Here's a Markdown document of the Candidate Profile: {cv_document}"
    )

    model = genai.GenerativeModel(
        st.session_state["gemini_model"], system_instruction=model_instruction
    )
    chat = model.start_chat(history=[])

    initial_prompt = f"First, ask the candidate how they are feeling and ask them to briefly introduce themself."

    if len(st.session_state["messages"]) == 0:
        with st.chat_message("assistant"):
            response = chat.send_message(
                initial_prompt,
                stream=True,
            )
            response.resolve()
            st.markdown(response.text)
            st.session_state.messages.append(
                {"role": "assistant", "content": response.text}
            )
    elif prompt := st.chat_input("Hi there!"):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = chat.send_message(
                prompt,
                stream=True,
            )
            response.resolve()
            st.markdown(response.text)
            st.session_state.messages.append(
                {"role": "assistant", "content": response.text}
            )
