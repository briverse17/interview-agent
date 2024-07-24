# from openai import OpenAI
import google.generativeai as genai
import streamlit as st

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "To use this app, you need to provide an Gemini API key, which you can get [here](https://makersuite.google.com/app/apikey). "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
# openai_api_key = st.text_input("OpenAI API Key", type="password")
gemini_api_key = st.text_input("Gemini API Key", type="password")

if not gemini_api_key:
    # st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    # client = OpenAI(api_key=openai_api_key)
    genai.configure(api_key=gemini_api_key)
    client = genai.GenerativeModel("gemini-1.5-flash")
    chat = client.start_chat(history=[])

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:

        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        messages = [
            {
                "role": "user",
                # "content": f"Here's a document: {document} \n\n---\n\n {question}",
                "parts": [
                    f"Here's Markdown a document: {document} \n\n---\n\n {question}"
                ],
            }
        ]

        # Generate an answer using the OpenAI API.
        # stream = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=messages,
        #     stream=True,
        # )
        response = chat.send_message(
            messages[0]["parts"][0],
            stream=True,
        )
        response.resolve()
        # Stream the response to the app using `st.write_stream`.
        # st.write_stream(stream._result.candidates)
        st.write(response.text)

        # for chunk in stream:
        #     st.write(chunk.text)
        #     # st.write("_"*80)
