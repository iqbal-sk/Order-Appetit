import os
import streamlit as st
import streamlit.components.v1 as components

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
        for msg in st.session_state.chat_history[st.session_state.current_thread]:
            role = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(msg["content"])

# Chat input handling
def handle_input(prompt):
    if prompt:  # Using the prompt from the text_input
        st.session_state.show_placeholder = False
        if st.session_state.current_thread is None:
            st.session_state.current_thread = generate_unique_thread_id()
            st.session_state.chat_history[st.session_state.current_thread] = []
            st.session_state.messages = []  # Reset messages for the new thread

        # Append user message
        user_message = {"role": "user", "content": prompt}
        st.session_state.chat_history[st.session_state.current_thread].append(user_message)

        with st.chat_message("user"):
            st.markdown(prompt)

        # Process input
        result = crew.kickoff(inputs={
            'user_query': prompt,
            'mongodb_uri': mongodb_uri,
            'database_name': database_name,
            'collection_names': collection_names,
        })

        # Append assistant response
        response = str(result)
        assistant_message = {"role": "assistant", "content": response}
        st.session_state.chat_history[st.session_state.current_thread].append(assistant_message)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages = st.session_state.chat_history[st.session_state.current_thread]
        st.session_state.show_placeholder = False
        save_chat_history()
        st.session_state.text_input = ""


def create_chat_interface(crew, mongodb_uri, database_name, collection_names):
    # Inject custom CSS to make input and button scale equally
    chat_container = st.container()
    col1, col2, col3 = st.columns([1,4,1])
    with col2:
        prompt = st.chat_input("What is up?")
        if prompt:
            handle_input(prompt)  # Pass prompt as argument

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
                    top: 180px;
                    left: 50%;
                    transform: translateX(-50%);
                    text-align: center;
                    z-index: 10;
                }

                /* Feature container */
                .feature-container {
                    position: fixed; /* Fix relative to viewport */
                    bottom: 100px; /* Space from the bottom of the viewport */
                    left: 50%; /* Center horizontally */
                    transform: translateX(-50%); /* Ensure exact centering */
                    display: flex; /* Flex layout for child elements */
                    justify-content: space-between; /* Space between child elements */
                    gap: 10px; /* Add space between feature boxes */
                    width: 90%; /* Adjust width for responsiveness */
                    max-width: 700px; /* Optional: prevent too wide a container */
                    background-color: transparent; /* Light background for visibility */
                    padding: 20px; /* Padding inside the container */
                    border-radius: 12px; /* Rounded corners */
                    z-index: 9999; /* Ensure it's above other elements */
                }

                /* Feature box */
                .feature-box {
                    background-color: rgba(255, 255, 255, 0.05); /* Background for each feature box */
                    border-radius: 15px; /* Rounded corners */
                    padding: 20px;
                    flex: 2; /* Equal width for all boxes */
                    text-align: center; /* Center text inside each box */
                    color: white; /* Ensure text color contrasts with the background */
                    height: auto; /* Allows box to grow with content */
                    max-height: 50%; /* Takes full height of container */
                }
                .feature-box h3 {
                    color: white;
                    font-size: 1rem;
                    margin-bottom: 0.5rem;
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
                    padding: 8px 12px;
                    margin: 4px 0;
                    border-radius: 8px;
                    color: #B8B9BC;
                    font-size: 0.8rem;
                }
                </style>
                """, unsafe_allow_html=True)

            # Main header and subheader
            # Main header and subheader
            st.markdown("<h3 class='main-header'>AppetiQ</h3>", unsafe_allow_html=True)
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
                        <div class="feature-item">which month has the highest sales of pasta</div>
                        <div class="feature-item">Give the top 10 restaurants in sales for last 12months</div>
                    </div>
                    <div class="feature-box">
                        <h3>Capabilities</h3>
                        <div class="feature-item">Provide information and answer questions</div>
                        <div class="feature-item">Handle both database-related and general queries efficiently.</div>
                        <div class="feature-item">Retains previous user inputs during ongoing conversations</div>
                        <div class="feature-item">Displays sales data in tables.</div>
                    </div>
                    <div class="feature-box">
                        <h3>Limitations</h3>
                        <div class="feature-item">Does not support graphs or visualizations.</div>
                        <div class="feature-item">Requires enhancement in handling follow-up queries.</div>
                        <div class="feature-item">Needs performance improvement to handle diverse queries effectively.</div>

                </div>
            """, unsafe_allow_html=True)
        else:
            pass
