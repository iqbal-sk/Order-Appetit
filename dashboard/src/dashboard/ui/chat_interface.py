import os
import streamlit as st

from dashboard.src.dashboard.memory.conversation import ConversationBufferWindow
from dashboard.src.dashboard.utils.chat_utils import generate_unique_thread_id, save_chat_history

# Create the custom JavaScript component
js_code = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const inputField = document.querySelector('[data-testid="stTextInput"] input');
    const sendButton = document.querySelector('.send-button');

    // Handle button click
    sendButton.addEventListener('click', function() {
        if (inputField.value.trim() !== '') {
            submitMessage();
        }
    });

    // Handle Enter key press
    inputField.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && inputField.value.trim() !== '') {
            submitMessage();
        }
    });

    function submitMessage() {
        const submitEvent = new Event('submit', {
            'bubbles': true,
            'cancelable': true
        });
        inputField.form.dispatchEvent(submitEvent);
    }
});
</script>
"""

def render_chat_messages():
    if st.session_state.current_thread is not None:
        # Render messages for the current thread
        for msg in st.session_state.chat_history[st.session_state.current_thread]['messages']:
            role = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(msg["content"])


def handle_flow_interaction(prompt, flow):
    if prompt:  # Using the prompt from the text_input
        st.session_state.show_placeholder = False
        if st.session_state.current_thread is None:
            st.session_state.current_thread = generate_unique_thread_id()
            st.session_state.chat_history[st.session_state.current_thread] = {}
            # st.session_state.memory = ConversationBufferWindow(window_size=10)
            st.session_state.chat_history[st.session_state.current_thread]['messages'] = []
            st.session_state.chat_history[st.session_state.current_thread]['conversation'] = ConversationBufferWindow(window_size=10)

            # st.session_state.messages = []  # Reset messages for the new thread

        # Append user message
        user_message = {"role": "user", "content": prompt}
        st.session_state.chat_history[st.session_state.current_thread]['messages'].append(user_message)

        with st.chat_message("user"):
            st.markdown(prompt)

        flow.state.conversation_history = st.session_state.chat_history[st.session_state.current_thread]['conversation']

        if not isinstance(st.session_state.chat_history[st.session_state.current_thread]['conversation'], ConversationBufferWindow):
            data = st.session_state.chat_history[st.session_state.current_thread]['conversation']
            st.session_state.chat_history[st.session_state.current_thread]['conversation'] = ConversationBufferWindow.from_dict(data)

        flow.state.conversation_history = st.session_state.chat_history[st.session_state.current_thread]['conversation']

        flow.state.current_query = prompt
        flow.kickoff()

        # Append assistant response
        response = flow.state.response
        assistant_message = {"role": "assistant", "content": response}
        st.session_state.chat_history[st.session_state.current_thread]['messages'].append(assistant_message)

        with st.chat_message("assistant"):
            st.markdown(response)

        # st.session_state.messages = st.session_state.chat_history[st.session_state.current_thread]['messages']
        st.session_state.show_placeholder = False
        save_chat_history()
        st.session_state.text_input = ""




def create_chat_interface(flow_class, mongodb_uri, database_name, collection_names):
    chat_container = st.container()

    col1, col2, col3 = st.columns([1, 4, 1])
    st.session_state.message_container = col2

    # print(st.session_state.message_container)

    flow = flow_class()


    with st.session_state.message_container:
        prompt = st.chat_input("What is up?")
        if prompt:
            # handle_input(prompt, crew, mongodb_uri=mongodb_uri,
            #              database_name=database_name,
            #              collection_names=collection_names)  # Pass prompt as argument
            handle_flow_interaction(prompt, flow)

    # display messages or placeholder
    with chat_container:
        if st.session_state.show_placeholder:

            st.markdown("""
                <style>
                .main-header {
                    position: fixed; /* Ensure it can be positioned */
                    font-family: 'Radley', serif !important;
                    font-size: 3.5rem !important;
                    top: 100px;
                    left: 50%;
                    transform: translateX(-50%);
                    text-align: center;
                    z-index: 10;
                }

                .subheader {
                    position: fixed; /* Ensure it can be positioned */
                    top: 200px;
                    left: 50%;
                    transform: translateX(-50%);
                    text-align: center;
                    z-index: 10;
                }

                /* Feature container */
                .feature-container {
                    position: fixed; /* Fix relative to viewport */
                    bottom: 120px; /* Space from the bottom of the viewport */
                    left: 50%; /* Center horizontally */
                    transform: translateX(-50%); /* Ensure exact centering */
                    display: flex; /* Flex layout for child elements */
                    justify-content: space-between; /* Space between child elements */
                    gap: 20px; /* Add space between feature boxes */
                    width: 100%; /* Adjust width for responsiveness */
                    max-width: 800px; /* Optional: prevent too wide a container */
                    background-color: transparent; /* Light background for visibility */
                    padding: 20px; /* Padding inside the container */
                    border-radius: 12px; /* Rounded corners */
                    z-index: 9999; /* Ensure it's above other elements */
                }

                /* Feature box */
                .feature-box {
                    background-color: rgba(255, 255, 255, 0.05); /* Background for each feature box */
                    border-radius: 10px; /* Rounded corners */
                    padding: 20px;
                    flex: 1; /* Equal width for all boxes */
                    text-align: center; /* Center text inside each box */
                    color: white; /* Ensure text color contrasts with the background */
                    height: auto; /* Allows box to grow with content */
                    max-height: 100%; /* Takes full height of container */
                }
                .feature-box h3 {
                    color: white;
                    font-size: 1.25rem;
                    margin-bottom: 1.5rem;
                    font-weight: 500;
                    text-align: center;
                }
                .feature-content {
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                    flex-grow: 1; /* Allows content to expand */
                }

                .feature-item {
                    background-color: rgba(255, 255, 255, 0.05);
                    padding: 12px 16px;
                    margin: 8px 0;
                    border-radius: 8px;
                    color: #B8B9BC;
                    font-size: 0.8rem;
                }
                </style>
                """, unsafe_allow_html=True)

            # Main header and subheader
            # Main header and subheader
            st.markdown("<h1 class='main-header'>AppetiQ</h1>", unsafe_allow_html=True)
            st.markdown(
                "<p class='subheader'>Explore Trends, Sales and Item performance interactively with insights from Order Appetit data.</p>",
                unsafe_allow_html=True)

            # Feature boxes with styled items
            st.markdown("""
                <div class="feature-container">
                    <div class="feature-box">
                        <h3>Examples</h3>
                        <div class="feature-item">What are the sales of mac n cheese for last 7 months?</div>
                        <div class="feature-item">Give sales of biryani till now.</div>
                        <div class="feature-item"></div>
                        <div class="feature-item">Explain how to manage money with $3000/month salary</div>
                    </div>
                    <div class="feature-box">
                        <h3>Capabilities</h3>
                        <div class="feature-item">Provide information and answer questions</div>
                        <div class="feature-item">Programmed to reject inappropriate solicitations</div>
                        <div class="feature-item">Retains previous user inputs during ongoing conversations</div>
                        <div class="feature-item">Grammar and language correction</div>
                    </div>
                    <div class="feature-box">
                        <h3>Limitations</h3>
                        <div class="feature-item">May sometimes produce inaccurate or erroneous data</div>
                        <div class="feature-item">Sometimes it can create harmful or biased content</div>
                        <div class="feature-item">Limited awareness of post-2021 world events</div>
                        <div class="feature-item">Potential for biased or inappropriate responses</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            pass