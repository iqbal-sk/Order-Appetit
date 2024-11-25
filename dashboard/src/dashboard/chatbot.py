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
import streamlit.components.v1 as components
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


# Streamlit app
st.set_page_config(page_title="AppetiQ", layout="wide", initial_sidebar_state="collapsed")
# for center screen
# st.markdown("""
#     <style>
#     .main-header {
#         position: fixed; /* Ensure it can be positioned */
#         font-family: 'Radley', serif !important;
#         font-size: 3.5rem !important;
#         top: 150px;
#         left: 50%;
#         transform: translateX(-50%);
#         text-align: center;
#         z-index: 10;
#     }
#
#     .subheader {
#         position: fixed; /* Ensure it can be positioned */
#         top: 250px;
#         left: 50%;
#         transform: translateX(-50%);
#         text-align: center;
#         z-index: 10;
#     }
#
#     /* Feature container */
#     .feature-container {
#         position: fixed; /* Fix relative to viewport */
#         bottom: 140px; /* Space from the bottom of the viewport */
#         left: 50%; /* Center horizontally */
#         transform: translateX(-50%); /* Ensure exact centering */
#         display: flex; /* Flex layout for child elements */
#         justify-content: space-between; /* Space between child elements */
#         gap: 20px; /* Add space between feature boxes */
#         width: 80%; /* Adjust width for responsiveness */
#         max-width: 900px; /* Optional: prevent too wide a container */
#         background-color: transparent; /* Light background for visibility */
#         padding: 20px; /* Padding inside the container */
#         border-radius: 12px; /* Rounded corners */
#         z-index: 9999; /* Ensure it's above other elements */
#     }
#
#     /* Feature box */
#     .feature-box {
#         background-color: rgba(255, 255, 255, 0.05); /* Background for each feature box */
#         border-radius: 10px; /* Rounded corners */
#         padding: 20px;
#         flex: 1; /* Equal width for all boxes */
#         text-align: center; /* Center text inside each box */
#         color: white; /* Ensure text color contrasts with the background */
#         height: auto; /* Allows box to grow with content */
#         max-height: 100%; /* Takes full height of container */
#     }
#     .feature-box h3 {
#         color: white;
#         font-size: 1.25rem;
#         margin-bottom: 1.5rem;
#         font-weight: 500;
#         text-align: center;
#     }
#     .feature-content {
#         display: flex;
#         flex-direction: column;
#         gap: 12px;
#         flex-grow: 1; /* Allows content to expand */
#     }
#
#     .feature-item {
#         background-color: rgba(255, 255, 255, 0.05);
#         padding: 12px 16px;
#         margin: 8px 0;
#         border-radius: 8px;
#         color: #B8B9BC;
#         font-size: 0.8rem;
#     }
#     </style>
#     """, unsafe_allow_html=True)
#
# # Main header and subheader
# # Main header and subheader
# st.markdown("<h1 class='main-header'>AppetiQ</h1>", unsafe_allow_html=True)
# st.markdown(
#     "<p class='subheader'>Explore Trends, Sales and Item performance interactively with insights from Order Appetit data.</p>",
#     unsafe_allow_html=True)
#
# # Feature boxes with styled items
# st.markdown("""
#     <div class="feature-container">
#         <div class="feature-box">
#             <h3>Examples</h3>
#             <div class="feature-item">Tell me about the history of Borobudur</div>
#             <div class="feature-item">Calculate the derivative of the function y=3x² + 2x - 1</div>
#             <div class="feature-item">What news happened in the world today?</div>
#             <div class="feature-item">Explain how to manage money with $3000/month salary</div>
#         </div>
#         <div class="feature-box">
#             <h3>Capabilities</h3>
#             <div class="feature-item">Provide information and answer questions</div>
#             <div class="feature-item">Programmed to reject inappropriate solicitations</div>
#             <div class="feature-item">Retains previous user inputs during ongoing conversations</div>
#             <div class="feature-item">Grammar and language correction</div>
#         </div>
#         <div class="feature-box">
#             <h3>Limitations</h3>
#             <div class="feature-item">May sometimes produce inaccurate or erroneous data</div>
#             <div class="feature-item">Sometimes it can create harmful or biased content</div>
#             <div class="feature-item">Limited awareness of post-2021 world events</div>
#             <div class="feature-item">Potential for biased or inappropriate responses</div>
#         </div>
#     </div>
# """, unsafe_allow_html=True)

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
        min-width: 300px;
    }}

    .stApp {{
    background: linear-gradient(to right, #140a31, #22264e);
    min-height: 100vh;
    }}
    
    
    .main .block-container {{
        background: transparent !important;
        padding: 0;
        margin-left: 0 !important;  /* Adds negative margin to move left */
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
        max-width: 900px;
        width: 90%;  /* Added width constraint */
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
        font-size: 19px !important;
    }}
    

    .stTextInput > div > div > input {{
        background-color: rgba(0, 0, 0, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 15px;
        border-radius: 8px;
        
    }}
    
    /* Chat input */
    .stChatInput {{
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 1000px;
    }}

    .stChatInput > div > div > input {{
        background: #334063 !important; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white !important;  /* Set the text color to white */
        border-radius: 8px;
        margin: 1rem 0;
        padding: 1.2rem;
        
    }}

    .stChatInput > div > div > input::placeholder {{
        color: rgba(255, 255, 255, 0) !important;
       
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

            .css-1d391kg {  /* Sidebar background */
                background: linear-gradient(to down, #311579, #5865c9);
            }

            .sidebar-title {
                font-family: 'Radley', serif !important;
                text-align: center !important;
                padding: 0rem 0 !important;
                font-size: 3rem !important;
                color:  white !important;
                margin-bottom: 0.5rem!important;
            }
            /* Navigation menu */
            .nav-item {
                padding: 6px 12px;
                color: rgba(255, 255, 255, 0.8);
                display: flex;
                font-size: 1.2rem !important;
                align-items: center;
                gap: 1px;
                transition: background 0.3s ease;
            }
            .nav-item:hover {
            background: rgba(255, 255, 255, 0.1);
            }
             /* Chat list section */
            .chat-list-header {
                padding: 1px 100px;
                color: rgba(255, 255, 255, 0.6);
                align-items: center;
                font-size: 1.5rem;
                width: 300px;
                font-weight: 100;
                
            }
            
        
            /* User profile section */
            .user-profile {
                position: fixed;
                bottom: 20px;
                left: 16px;
                width: 250px;
                padding: 16px 24px;
                background: rgba(0, 0, 0, 0.2);
                display: flex;
                align-items: center;
                gap: 12px;
                border-radius: 8px;
                z-index: 100;
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
            <div class="nav-item">
                <div style="display: flex; align-items: center; padding: 8px;">
                    <i class="fa-solid fa-headset" style="width: 30px; height: 30px; margin-right: 8px; display: flex; align-items: center; justify-content: left;"></i>
                    <span style="display: inline-block; vertical-align: left;">Support</span>
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
    if thread_id in st.session_state.chat_history:
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
custom_button_css = """
<style>
.stButton > button {
    margin: 12px 24px;
    padding: 1px 10px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    text-align: center;
    cursor: pointer;
    transition: background 0.3s ease;
    width: calc(100% - 48px);
    border: none;
}

.stButton > button:hover {
    background: rgba(255, 255, 255, 0.2);
}

</style>
"""


def truncate_message(message, length=25):
    """Truncate message to a certain length and add ellipsis."""
    if len(message) <= length:
        return message
    return message[:length] + "..."


# Add this CSS for the bin icon styling
custom_icon_css = """
<style>
.thread-container {
    display: flex;
    align-items: center;
    gap: 0;
    padding: 1px 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    margin: 0 0 1px 0;
}

.thread-button > button {
    width:calc(100% - 48px);
    text-align: left !important;
    background: transparent !important;
    border: none !important;
    color: white !important;
    padding: 0 !important;
    margin: 0 !important;
}

.delete-button > button {
    background: transparent !important;
    border: none !important;
    color: rgba(255, 255, 255, 0.6) !important;
    padding: 0 !important;
    min-width: auto !important;
    margin: 0 !important;
    align: left !important;
}


.delete-button > button:hover {
    color: white !important;
}
/* Remove gaps between threads */
.element-container {
    margin: 0 !important;
    padding: 0 !important;
}
* Modify column layout */
[data-testid="column"] {
    padding: 0 !important;
    gap: 0 !important;
}

/* Remove default Streamlit button styling */
.stButton {
    margin: 0 !important;
}
/* Remove gaps in markdown elements */
.stMarkdown {
    margin: 0 !important;
    padding: 0 !important;
}
</style>
"""

with st.sidebar:
    # Apply custom styling
    st.markdown(custom_button_css, unsafe_allow_html=True)
    st.markdown(custom_icon_css, unsafe_allow_html=True)

    # Create functional button with custom styling
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
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown('<div class="thread-button">', unsafe_allow_html=True)
            if st.button(f"{first_message}", key=f"switch_thread_{thread_id}"):
                switch_thread(thread_id)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="delete-button">', unsafe_allow_html=True)
            if st.button("🗑️", key=f"delete_thread_{thread_id}"):
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

# Custom CSS for just the chat input
st.markdown("""
<style>
    /* Chat input container styling */
    .stTextInput {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 50%;
    }
    /* Target Streamlit's specific input container */
    [data-testid="stTextInput"] > div > div > input {
        outline: none !important;
        box-shadow: none !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Handle the focus state */
    [data-testid="stTextInput"] > div > div > input:focus {
        box-shadow: none !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        outline: none !important;
    }
    
    /* Remove any residual outlines */
    div[data-testid="stTextInput"] {
        outline: none !important;
    }
    
    /* Target the specific container class */
    .stTextInput > div {
        outline: none !important;
        border: none !important;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background:#334063 !important; 
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 15px 20px !important;
        font-size: 18px !important;
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:hover {
        border-color: rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.1) !important;
        transform: scale(1);
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.2) !important;
        background: #334063  !important;
    }
    /* Input placeholder styling */
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    

    /* Button container */
    .button-container {
        position: fixed;
        right: 22%;
        bottom: 0px;
        transform: translateY(-50%);
        
    }

    /* Send button styling */
    .send-button {
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
    }
    
    .send-button:hover {
        background: rgba(75, 59, 138, 0.8) !important;
        border-color: rgba(255, 255, 255, 0.4);
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
    }
    
    /* Paper plane icon */
    .send-icon {
        color: white;
        transform: rotate(45deg);
        font-size: 20px;
        transition: all 0.3s ease;
    }
    
    .send-button:hover .send-icon {
        transform: rotate(45deg) translateX(2px);
        color: rgba(255, 255, 255, 0.9);
    }
</style>


<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">

<!-- HTML Structure -->
<div class="button-container">
    <button class="send-button">
        <span class="send-icon"><i class="fas fa-paper-plane"></i></span> <!-- Send icon -->
    </button>
</div>
""", unsafe_allow_html=True)

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

# Chat input implementation
def create_chat_interface():
    components.html(js_code, height=0)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        prompt = st.text_input("", placeholder="Ask anything...", key="initial_input")
        if prompt:
            st.session_state.show_placeholder = False
            st.text_input("", placeholder="Ask follow-up", key="follow_up_input")
            handle_input(prompt)  # Pass prompt as argument


    #display messages or placeholder

    if not st.markdown(prompt) or st.session_state.show_placeholder:
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
        st.markdown("<p class='subheader'>Explore Trends, Sales and Item performance interactively with insights from Order Appetit data.</p>",unsafe_allow_html=True)

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

create_chat_interface()