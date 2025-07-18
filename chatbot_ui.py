import streamlit as st
import requests
import sseclient
import json

st.title("🧠 Chat with Local LLM")

API_URL = "http://localhost:8000/v1/chat/completions"

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.chat_input("Type your message")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_box = st.empty()
        assistant_text = ""

        payload = {
            "model": "gpt2",
            "messages": st.session_state.history,
            "stream": True
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, json=payload, stream=True, headers=headers)
        client = sseclient.SSEClient(response)

        for event in client.events():
            if event.data:
                try:
                    delta = json.loads(event.data)["choices"][0]["delta"]
                    content = delta.get("content", "")
                    assistant_text += content
                    response_box.markdown(assistant_text + "▌")
                except Exception:
                    continue

        st.session_state.history.append({"role": "assistant", "content": assistant_text})