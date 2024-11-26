import json
import base64
from io import BytesIO
import os
from crewai import Agent, Task, Crew, Process
import time
from dashboard.src.dashboard.memory.conversation import ConversationBufferWindow
import streamlit as st


# Custom JSON Encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Agent, Task, Crew, Process)):
            return str(obj)
        elif isinstance(obj, ConversationBufferWindow):
            return {
                "window_size": obj.window_size,
                "buffer": list(obj.buffer)
            }

        return super().default(obj)

# Streamlit UI functions
def convert_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def load_chat_history():
    try:
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r") as file:
                content = file.read()
                if not content.strip():  # Check if file is empty
                    return {}
                return json.loads(content)
        return {}
    except json.JSONDecodeError as e:
        print(f"Error loading chat history: {e}")
        # If there's an error, return empty dict and create new file
        with open("chat_history.json", "w") as file:
            json.dump({}, file)
        return {}


def save_chat_history():
    try:
        with open("chat_history.json", "w") as file:
            json.dump(
                st.session_state.chat_history,
                file,
                cls=CustomJSONEncoder,
                indent=2
            )
    except Exception as e:
        print(f"Error saving chat history: {e}")


def switch_thread(thread_id):
    """Switch to a selected thread."""
    if thread_id in st.session_state.chat_history:
        st.session_state.current_thread = thread_id
        st.session_state.show_placeholder = False
    else:
        st.error("Thread not found.")


def delete_thread(thread_id):
    """Delete a thread."""
    if thread_id == st.session_state.current_thread:
        # Create a container for the warning message
        warning_container = st.empty()

        # Display the warning message
        warning_container.markdown("""
            <div class='main-header' style='text-align: center; position: fixed; top: 0; left: 50%; transform: translateX(-50%); width: 100%; z-index: 999;'>
                <p style='background-color: #7975b8; color: white; padding: 10px; border-radius: 5px; margin: 0;'>
                    Current thread can't be deleted
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Wait for 3 seconds
        time.sleep(2)

        # Clear the warning message
        warning_container.empty()
        return

    if thread_id in st.session_state.chat_history:
        del st.session_state.chat_history[thread_id]
        save_chat_history()

def generate_unique_thread_id():
    return str(int(time.time() * 1000000))

def create_new_thread():
    new_thread_id = generate_unique_thread_id()
    st.session_state.current_thread = new_thread_id
    st.session_state.messages = []
    st.session_state.chat_history[new_thread_id] = {}
    st.session_state.chat_history[new_thread_id]['messages'] = []
    st.session_state.chat_history[new_thread_id]['conversation'] = ConversationBufferWindow(window_size=10)
    st.session_state.show_placeholder = True
    save_chat_history()


def truncate_message(message, length=25):
    """Truncate message to a certain length and add ellipsis."""
    if len(message) <= length:
        return message
    return message[:length] + "..."
