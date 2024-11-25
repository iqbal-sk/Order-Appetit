import streamlit as st
from langchain_openai import ChatOpenAI

from dashboard.src.dashboard.ui.css import apply_css
from tools.mongodb_tools import analyze_mongodb_schema
from tools.python_executor import execute_python_code
from tools.items_finder import filter_items
from tools.schema_analysis import analyze_local_schema
from dotenv import load_dotenv

from config import agents_config, tasks_config

from utils.chat_utils import *

from ui.sidebar import render_sidebar
from ui.chat_interface import create_chat_interface, render_chat_messages

# Load environment variables
load_dotenv()
serper_key = os.getenv("SERPER_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")


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
    render_sidebar()


render_chat_messages()
apply_css()
create_chat_interface(crew, mongodb_uri, database_name, collection_names)