import streamlit as st
from PIL import Image
from streamlit_chat import message
import base64
from io import BytesIO
import json
import os
import time
import yaml
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import urllib.parse
from tools.mongodb_tools import analyze_mongodb_schema
from tools.python_executor import execute_python_code
from tools.items_finder import filter_items
from tools.schema_analysis import analyze_local_schema
from dotenv import load_dotenv
import streamlit.components.v1 as components
from config import agents_config, tasks_config




# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")


# Custom JSON Encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Agent, Task, Crew, Process)):
            return str(obj)
        return super().default(obj)


# Initialize LLM
llm = ChatOpenAI(model='gpt-4o-mini', api_key=openai_key, temperature=0, max_tokens=16384)

mongodb_uri = os.getenv("mongodb_uri")
database_name = os.getenv("database_name")
collection_names = [
    "categories", "delivery_fees", "locations", "merchant_logs",
    "merchant_settings", "orders", "product_categories", "products",
    "stores", "store_tables", "users"
]

# Set up agents
schema_analyzer = Agent(
    goal=agents_config['schema_analyzer']['goal'],
    role=agents_config['schema_analyzer']['role'],
    backstory=agents_config['schema_analyzer']['backstory'],
    verbose=True,
    allow_code_execution=True,
    tools=[analyze_local_schema, filter_items],
    llm=llm,
    cache=False
)

query_builder = Agent(
    goal=agents_config['query_builder']['goal'],
    role=agents_config['query_builder']['role'],
    backstory=agents_config['query_builder']['backstory'],
    llm=llm,
    cache=False,
    verbose=True,
)

data_analyst = Agent(
    goal=agents_config['data_analyst']['goal'],
    role=agents_config['data_analyst']['role'],
    backstory=agents_config['data_analyst']['backstory'],
    verbose=True,
    cache=False,
    # allow_delegation=True,
    llm=llm,
    tools=[execute_python_code]
)

# Set up tasks
schema_analysis_task = Task(
    description=tasks_config['schema_analysis_task']['description'],
    expected_output=tasks_config['schema_analysis_task']['expected_output'],
    agent=schema_analyzer
)

query_building_task = Task(
    description=tasks_config['query_building_task']['description'],
    expected_output=tasks_config['query_building_task']['expected_output'],
    agent=query_builder,
    context=[schema_analysis_task]
)

data_analysis_task = Task(
    description=tasks_config['data_analysis_task']['description'],
    expected_output=tasks_config['data_analysis_task']['expected_output'],
    agent=data_analyst,
    context=[schema_analysis_task, query_building_task]
)

# Set up crew
crew = Crew(
    agents=[schema_analyzer, query_builder, data_analyst],
    tasks=[schema_analysis_task, query_building_task, data_analysis_task],
    verbose=True,
)


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


# Streamlit app
st.set_page_config(page_title="AppetiQ", layout="centered", initial_sidebar_state="collapsed")


# Set background using custom CSS
st.markdown(f"""
<style>
    /* Reset default Streamlit styles */
    #root > div:first-child {{
        background-color: transparent;
    }}
    /* Sidebar container */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #311579,#403699) !important;
        padding: 0;
        width: calc(300px+0%);
    }}

    .stApp {{
    background: linear-gradient(to right, #140a31, #22264e);
    min-height: 100vh;
    }}


    .main .block-container {{
        background: transparent !important;
        padding: 0;
        margin-left: 0% !important;  /* Adds negative margin to move left */
        position: relative;   /* Ensures proper positioning */
        width: 100% !important  /* Maintains container width */
    }}

    /* Message cards */
    [data-testid="stChatMessage"] {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        margin: 2rem 0 !important;  /* Increased margin */
        padding: 1rem;
        max-width: 800px;
        width: 100%;  /* Added width constraint */
        position: relative;
        margin_left: 50px !important;
        text-align: left !important;
        clear: both !important;
    }}


    .chat-card {{
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;

    }}
    
    [data-testid="stChatMessage"] {{
        font-size: 18px !important;
    }}


    /* Chat input */
    .stChatInput {{
        position: fixed;
        bottom: 2vh;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(255, 255, 255, 0.1);
        width:1200px
        max-width: 80px;
        margin: 0;
        padding: 0 0px;
        display: flex;
        font-color:white;
    }}
    div[data-testid="stChatInput"] button {{
        background: #334063 !important;
        border-radius: 12px;
        width: 40px;
        height: 40px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    div[data-testid="stChatInput"] button:hover {{
        background: rgba(75, 59, 138, 0.8) !important;
        border-color: rgba(255, 255, 255, 0.4);
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
    }}


    /* Text colors */
    p, h1, h2, h3, h4, h5, h6 {{
        color: white !important;
    }}

    /* Scrollbar styling */
    ::-webkit-scrollbar {{
        width: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: transparent;
    }}

    ::-webkit-scrollbar-thumb {{
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: rgba(255, 255, 255, 0.3);
    }}
    
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = load_chat_history()
if 'current_thread' not in st.session_state:
    st.session_state.current_thread = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_placeholder' not in st.session_state:
    st.session_state.show_placeholder = True
if 'show_support' not in st.session_state:
    st.session_state.show_support = False

def render_chat_messages():
    if st.session_state.current_thread is not None:
        # Render messages for the current thread
        for msg in st.session_state.chat_history[st.session_state.current_thread]:
            role = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(msg["content"])



# Sidebar
with st.sidebar:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Radley&display=swap');
            .sidebar-title {
                font-family: 'Radley', serif !important;
                text-align: center !important;
                padding: 0rem 0 !important;
                font-size: 3rem !important;
                color:  white !important;
                margin-bottom: 0.5rem!important;
            }
            /* Navigation menu */
            .support-nav-item {
                position: relative;
            }
            .support-nav-item .support-dropdown {
                display: block;
                position: absolute;
                left: 0;
                background-color:#181038!important;
                padding: 10px;
                width: 102%;
                z-index: 1000;
                border-radius: 8px;
                color: white !important;
                text-align: center !important;
                visibility: hidden;
                opacity: 0;
                transition: opacity 0.3s, visibility 0s linear 1s;
            }
            .support-nav-item:hover .support-dropdown {
                visibility: visible;
                opacity: 1;
                transition-delay: 1s;
            }
            .email-item {
                padding: 8px;
                margin: 5px 0;
                border-bottom: 1px solid #eee;
            }
             /* Chat list section */
            .chat-list-header {
                padding: 1px 10px;
                color: rgba(255, 255, 255, 0.6);
                align-items: center;
                font-size: 1.2rem;
                width: 300px;
                font-weight: 100;
            }

            /* User profile section */
            .user-profile {
                position: fixed;
                bottom: 20px;
                left: 10px;
                width: 230px;
                padding: 16px 24px;
                background: rgba(0, 0, 0, 0.2);
                display: flex;
                align-items: left;
                gap: 12px;
                border-radius: 8px;
                z-index: 100;
            }
            .user-profile:hover {
                background: rgba(0, 0, 0, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            .user-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background-image: url('https://pbs.twimg.com/profile_images/1557071011467739136/mBfyJP5B_400x400.jpg');
                background-size: cover;
                background-position: center;
            }

            .user-info {
                flex-grow: 1;
            }

            .user-name {
                color: white;
                font-size: 1rem;
                align-items: center;
            }

            .user-email {
                color: rgba(255, 255, 255, 0.6);
                font-size: 1rem;
                align-items: center;
            }
            .stButton > button {
                margin: 0px;
                padding: 1px 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: white;
                text-align: center;
                cursor: pointer;
                transition: background 0.3s ease;
                width: calc(100% - 10px);
                border: none;
                gap=1px;
            }

            .stButton > button:hover {
                background: rgba(255, 255, 255, 0.2);
            }

            /* Delete button */
            .delete-btn {
                background: transparent;
                border: none;
                padding: 4px;
                cursor: pointer;
                display: flex;
                align-items: center;
            }
            .delete-icon {
                width: 16px;
                height: 16px;
                fill: white;
                opacity: 0.7;
                transition: fill 0.3s ease;
            }
            .delete-btn:hover .delete-icon {
            opacity: 1;
            fill: #ff3b30;
            }

            /* Section header */
            .section-header {
                color: white;
                font-size: 20px;
                margin: 24px 0 16px 0;
                padding: 0 12px;
            }
            /* Optional: Add hover effect */
            .sidebar-title:hover {
                color: rgba(255, 255, 255, 0.8) !important;
            }


        </style>
        <div class="sidebar-title">AppetiQ</div>
        """,
        unsafe_allow_html=True
    )
    # sidebar items
    st.markdown("""
            <div class="nav-item">
                <a href="https://orderappetit.com/" style="text-decoration: none; color: inherit; display: flex; align-items: center;">
                    <img src="https://orderappetit.com/static/media/buffalo.dce0a965.png" style="width: 30px; height: 30px; margin-right: 8px;">
                    Order Appetit
                </a>
            </div>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <div class="nav-item support-nav-item">
                <div style="display: flex; align-items: center; padding: 8px;">
                    <i class="fa-solid fa-headset" style="width: 30px; height: 30px; margin-right: 8px; display: flex; align-items: center; justify-content: left;"></i>
                    <span style="display: inline-block; vertical-align: left;">Support</span>
                </div>
                <div class="support-dropdown">
                    <div class="email-item">Technical: mahammad@buffalo.edu</div>
                    <div class="email-item">General: vduggemp@buffalo.edu</div>
                    <div class="email-item">Urgent:  saishiri@buffalo.edu</div>
                    <div class="email-item">Urgent: vkaturu@buffalo.edu</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    # Chat List Section
    st.markdown('<div class="chat-list-header">Chat List</div>', unsafe_allow_html=True)

    # Functions for thread management
    st.markdown("""
                    <div class="user-profile">
                        <a href="https://www.buffalo.edu" style="text-decoration: none; color: inherit;">
                            <div style="display: flex; align-items: center; padding: 12px;">
                                <div class="user-avatar" style="margin-right: 16px;"></div>
                                <div class="user-info">
                                    <div class="user-name">Created by UB</div>
                                    <div class="user-email">@buffalo.edu</div>
                                </div>
                            </div>
                        </a>
                    </div>
                """, unsafe_allow_html=True)


def switch_thread(thread_id):
    """Switch to a selected thread."""
    if thread_id in st.session_state.chat_history:
        st.session_state.current_thread = thread_id
        st.session_state.messages = st.session_state.chat_history[thread_id]
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

    elif thread_id in st.session_state.chat_history:
        del st.session_state.chat_history[thread_id]
        save_chat_history()


def generate_unique_thread_id():
    return str(int(time.time() * 1000000))


def create_new_thread():
    new_thread_id = generate_unique_thread_id()
    st.session_state.current_thread = new_thread_id
    st.session_state.messages = []
    st.session_state.chat_history[new_thread_id] = []
    st.session_state.show_placeholder = True
    save_chat_history()


# Add custom CSS for the button styling
# custom_button_css = """
# <style>
# .stButton > button {
#     margin: 0px;
#     padding: 1px 10px;
#     background: rgba(255, 255, 255, 0.1);
#     border-radius: 8px;
#     color: white;
#     text-align: center;
#     cursor: pointer;
#     transition: background 0.3s ease;
#     width: calc(100% - 10px);
#     border: none;
#     gap=1px;
# }
#
# .stButton > button:hover {
#     background: rgba(255, 255, 255, 0.2);
# }
#
# </style>
# """

# Custom CSS to style the support container





def truncate_message(message, length=20):
    """Truncate message to a certain length and add ellipsis."""
    if len(message) <= length:
        return message
    return message[:length] + "..."


# Add this CSS for the bin icon styling
custom_icon_css = """
<style>

.thread-container {
    margin: 0px !important;
    padding: 0px !important;
}

.stButton {
    margin: 0px !important;
    padding: 0px !important;
}

.stButton > button {
    margin: 1px !important;
    padding: 8px !important;
    width: 100% !important;
}
.stButton:first-child > button {
    margin-bottom: 2px !important;
}

[data-testid="column"] {
    padding: 0px !important;
    margin: 0px !important;
}

.element-container {
    margin: 0px !important;
    padding: 0px !important;
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0rem !important;
    padding: 0rem !important;
}

div[class*="stVerticalBlock"] {
    margin: 3px !important;
    gap: 0rem !important;
    padding: 0rem !important;
}

.stButton,
.stMarkdown,
div[data-testid="column"] {
    margin: 0px !important;
    padding: 0px !important;
}

.stButton > button {
    margin: 0px !important;
    padding: 8px !important;
}

.element-container,
.stMarkdown > div {
    margin: 0px !important;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
}
/* Target the button text directly */
[data-testid="stButton"] button p {
    font-size: 0.9rem !important;
}
</style>
"""
with st.sidebar:
    # Add custom CSS to remove spacing
    st.markdown(custom_icon_css, unsafe_allow_html=True)

    if st.button("+New Thread", key="new_thread_btn", use_container_width=True):
        create_new_thread()

    sorted_threads = sorted(st.session_state.chat_history.items(), key=lambda x: float(x[0]), reverse=True)
    for thread_id, thread in sorted_threads:
        try:
            first_message = thread[0]["content"] if thread else "No messages yet"
            first_message = truncate_message(first_message)
        except (IndexError, KeyError, TypeError):
            first_message = "No messages yet"

        st.markdown('<div class="thread-container">', unsafe_allow_html=True)
        col1, spacer, col2 = st.columns([5.5,0.5, 1])
        with col1:
            st.markdown('<div class="thread-button">', unsafe_allow_html=True)
            if st.button(f"{first_message}", key=f"switch_thread_{thread_id}"):
                switch_thread(thread_id)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="delete-button">', unsafe_allow_html=True)
            if st.button("⌫", key=f"delete_thread_{thread_id}"):
                delete_thread(thread_id)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
render_chat_messages()


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


# Chat input implementation
chat_container = st.container()


def create_chat_interface():
    # Inject custom CSS to make input and button scale equally

    col1, col2, col3 = st.columns([0.1,20,0.1])
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


create_chat_interface()