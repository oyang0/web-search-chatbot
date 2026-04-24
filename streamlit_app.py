import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's model to generate responses. "
    "To use this app, you need an OpenAI API key configured in Streamlit secrets."
)

# Read secrets from ./.streamlit/secrets.toml
try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    app_password = st.secrets["APP_PASSWORD"]
except FileNotFoundError:
    st.error(
        "Secrets file not found. Create `./.streamlit/secrets.toml` "
        "and add `OPENAI_API_KEY` and `APP_PASSWORD`."
    )
    st.stop()
except KeyError as e:
    st.error(f"Missing secret: {e}")
    st.stop()

# Ask user for the app password via st.text_input.
entered_password = st.text_input("Password", type="password")

if not entered_password:
    st.info("Please enter the app password to continue.", icon="🔐")
    st.stop()

if entered_password != app_password:
    st.error("Incorrect password.")
    st.stop()

# Create an OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Create a session state variable to store the chat messages.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages via st.chat_message.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field.
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the OpenAI API.
    stream = client.responses.create(
        model="gpt-5.5",
        input=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
        reasoning={"effort": "none"},
        temperature=0,
        max_output_tokens=32768,
        tools=[{"type": "web_search"}],
        include=["web_search_call.action.sources"],
        tool_choice={"type": "required"},
    )

    def write_stream():
        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta

    # Stream the response to the chat, then store it in session state.
    with st.chat_message("assistant"):
        response = st.write_stream(write_stream())

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )