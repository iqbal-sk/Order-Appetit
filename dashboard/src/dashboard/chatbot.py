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
from dotenv import load_dotenv

from config import agents_config, tasks_config


# Load environment variables
load_dotenv()
serper_key = os.getenv("SERPER_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")
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
    tools=[analyze_mongodb_schema, filter_items],
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
def generate_unique_thread_id():
    return str(int(time.time() * 1000000))

# Streamlit app
st.set_page_config(page_title="AppetiQ", layout="wide", initial_sidebar_state="expanded")

# Load images
logo_path = "/Users/vikkyfury/Desktop/appetit/Order-Appetit/dashboard/src/dashboard/images/logo.png"
logo = Image.open(logo_path)
logo = logo.resize((1200, 300))

placeholder_image_path = "/Users/vikkyfury/Desktop/appetit/Order-Appetit/dashboard/src/dashboard/images/background.png"
placeholder_image = Image.open(placeholder_image_path)
placeholder_image_base64 = convert_image_to_base64(placeholder_image)

# Custom CSS
st.markdown(f"""
<style>
    .main {{ 
        background-image: url('data:image/png;base64,{placeholder_image_base64}'); 
        background-size: cover; 
        background-position: center; 
    }}
    .sidebar {{ background-color: #f7f7f7; padding: 20px; }}
    .stButton button {{ 
        background-color: #636160; 
        color: white; 
        border: 1px solid #636160; 
        text-align: left; 
        width: 100%; 
        padding: 10px; 
        font-size: 16px; 
        border-radius: 5px; 
    }}
    .stButton button:hover {{ 
        background-color: #7a7877; 
    }}
    .chat-message {{ padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex; align-items: flex-start; }}
    .chat-message.user {{ background-color: #f7f7f7; }}
    .chat-message.bot {{ background-color: #ffffff; }}
    .stTextInput {{ position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); width: 60%; background-color: transparent !important; padding: 10px; border-radius: 20px; border: 1px solid #4B4B4B; }}
    .stTextInput > div > div > input {{ color: #333333; background-color: #262730; color: white; border-radius: 5px; padding: 8px 12px; border: 1px solid #4B4B4B; }}
    .stTextInput > div > div > input::placeholder {{ color: #9E9E9E; }}
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

# Sidebar
with st.sidebar:
    st.markdown(
        """
        <style>
            .css-1d391kg { background-color: #ffffff !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.image(logo, use_container_width=True)
    if st.button("New Thread"):
        new_thread_id = generate_unique_thread_id()
        st.session_state.current_thread = new_thread_id
        st.session_state.messages = []
        st.session_state.chat_history[new_thread_id] = []
        st.session_state.show_placeholder = True
        save_chat_history()

# Functions for thread management
def switch_thread(thread_id):
    st.session_state.current_thread = thread_id
    st.session_state.messages = st.session_state.chat_history[thread_id]
    st.session_state.show_placeholder = False

def delete_thread(thread_id):
    if thread_id in st.session_state.chat_history:
        del st.session_state.chat_history[thread_id]
        save_chat_history()

# Display previous threads
with st.sidebar:
    st.markdown("<h3 style='font-size: 20px;'>Previous Threads:</h3>", unsafe_allow_html=True)
    sorted_threads = sorted(st.session_state.chat_history.items(), key=lambda x: float(x[0]), reverse=True)
    for thread_id, thread in sorted_threads:
        first_message = thread[0]["content"] if thread else "No messages yet"
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"{first_message}", key=f"switch_thread_{thread_id}"):
                switch_thread(thread_id)
        with col2:
            if st.button("del", key=f"delete_thread_{thread_id}"):
                delete_thread(thread_id)

# Main chat container
chat_container = st.container()

# Display messages or placeholder
with chat_container:
    if st.session_state.show_placeholder:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center;">
                <img src="data:image/png;base64,{placeholder_image_base64}" alt="Placeholder" style="width: 600px;">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for i, msg in enumerate(st.session_state.messages):
            message(msg['content'], is_user=msg['is_user'], key=f"msg_{i}")



# Chat input handling
def handle_input():
    if st.session_state.user_input and st.session_state.user_input.strip():
        if st.session_state.current_thread is None:
            st.session_state.current_thread = generate_unique_thread_id()
            st.session_state.chat_history[st.session_state.current_thread] = []

        user_message = {
            "content": st.session_state.user_input,
            "is_user": True
        }

        # Process user query using the crew
        result = crew.kickoff(inputs={
            'user_query': st.session_state.user_input,
            'mongodb_uri': mongodb_uri,
            'database_name': database_name,
            'collection_names': collection_names,
        })

        # print(result)

        bot_message = {
            "content": str(result),  # Convert result to string
            "is_user": False
        }

        st.session_state.messages.extend([user_message, bot_message])
        st.session_state.chat_history[st.session_state.current_thread].extend([user_message, bot_message])
        st.session_state.show_placeholder = False
        save_chat_history()
        st.session_state.user_input = ""

# Input box
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.text_input(
        "Are you Ready!!",
        key="user_input",
        on_change=handle_input,
        placeholder="Ask anything..."
    )
