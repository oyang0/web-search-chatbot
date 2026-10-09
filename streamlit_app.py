import hmac

import streamlit as st
from openai import OpenAI

st.title("💬 Chatbot")
st.write("Enter the app password to use the chatbot.")

password = st.text_input("App password", type="password")

if not password:
        st.info("Please enter the app password to continue.", icon="🔒")
elif not hmac.compare_digest(password, st.secrets["APP_PASSWORD"]):
        st.error("Incorrect password.")
else:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], timeout=900.0)

        if "messages" not in st.session_state:
                st.session_state.messages = []

        for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                        st.markdown(message["content"])

        if prompt := st.chat_input("What is up?"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                        st.markdown(prompt)

                stream = client.with_options(timeout=900.0).responses.create(
                        model="gpt-6-sol",
                        input=[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages
                        ],
                        stream=True,
                        reasoning={"effort": "none"},
                        text={"verbosity": "high"},
                        temperature=0,
                        max_output_tokens=32768,
                        tool=[{"type": "web_search", search_context_size: "high"}],
                        tool_choice="required",
                        service_tier="flex",
                )

                def write_stream():
                        for event in stream:
                                if event.type == "response.output_text.delta":
                                        yield event.delta

                with st.chat_message("assistant"):
                        response = st.write_stream(write_stream())
                st.session_state.messages.append({"role": "assistant", "content": response})