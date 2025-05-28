import streamlit as st
from openai import OpenAI
import os
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="ChatGPT-like Clone with Threads", layout="wide")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Function to save chat history
def save_chat_history(threads, file_path='my_bot_threads.json'):
    with open(file_path, 'w') as f:
        json.dump(threads, f)


# Function to load chat history
def load_chat_history(file_path='my_bot_threads.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}


# Initialize session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "threads" not in st.session_state:
    st.session_state.threads = load_chat_history()

if "current_thread" not in st.session_state:
    st.session_state.current_thread = None

# Sidebar for thread management
with st.sidebar:
    st.header("Thread Management")

    if st.button("New Thread"):
        new_thread_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.threads[new_thread_id] = {"messages": [], "name": ""}
        st.session_state.current_thread = new_thread_id
        save_chat_history(st.session_state.threads)
        st.rerun()

    st.subheader("Previous Threads")
    for thread_id, thread_data in reversed(list(st.session_state.threads.items())):
        thread_name = thread_data.get('name') or f"Thread {thread_id}"
        if st.button(f"{thread_name}", key=thread_id):
            st.session_state.current_thread = thread_id
            st.rerun()

    if st.button("Clear All Threads"):
        st.session_state.threads = {}
        st.session_state.current_thread = None
        save_chat_history({})
        st.rerun()

# Main chat interface
st.title("ChatGPT-like Clone with Threads")

if st.session_state.current_thread:
    current_thread = st.session_state.threads[st.session_state.current_thread]
    thread_name = current_thread.get('name') or f"Thread {st.session_state.current_thread}"
    # st.subheader(f"Current Thread: {thread_name}")

    # Display chat messages for the current thread
    for message in current_thread['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("What is up?"):
        if not current_thread.get('name'):
            current_thread['name'] = prompt[:25]  # Set thread name to first 50 chars of first message

        current_thread['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI API call
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[{"role": m["role"], "content": m["content"]} for m in current_thread['messages']],
                    stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        current_thread['messages'].append({"role": "assistant", "content": full_response})

        # Save chat history after each interaction
        save_chat_history(st.session_state.threads)
        st.rerun()
else:
    st.info("Create a new thread to start chatting!")