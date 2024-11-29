import os

import streamlit as st
from crewai import Crew
from crewai.flow.flow import Flow, start, listen, router, or_
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from utils.crew_utils import *
from callbacks.agent_callbacks import AgentProgressCallback
from callbacks.task_callbacks import TaskProgressCallback
from memory.conversation import ConversationBufferWindow
load_dotenv()

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
from utils.utils import extract_last_meaningful_query

# Environment variables
mongodb_uri = os.getenv("mongodb_uri")
database_name = os.getenv("database_name")
collection_names = [
    "categories", "delivery_fees", "locations", "merchant_logs",
    "merchant_settings", "orders", "product_categories", "products",
    "stores", "store_tables", "users"
]



class ChatState(BaseModel):
    conversation_history: ConversationBufferWindow = Field(default_factory=ConversationBufferWindow)
    current_query: str = ""
    response: str = ""
    is_task_specific: bool = False

    class Config:
        arbitrary_types_allowed = True



class ChatbotFlow(Flow[ChatState]):
    def __init__(self):
        super().__init__()
        self.task_crew = self.create_task_crew()
        self.conversation_crew = self.create_conversation_crew()
        self.chat_llm = OpenAI()


    def create_task_crew(self):
        agents = create_agents(AgentProgressCallback, st.empty())
        tasks = create_tasks(agents, st.empty(), self.state.conversation_history)
        return Crew(agents=agents, tasks=tasks, verbose=True, memory=True)

    def create_conversation_crew(self):
        conversational_agent = create_conversational_agent(AgentProgressCallback, st.empty())
        conversational_task = create_conversational_task(conversational_agent, self.state.conversation_history)
        return Crew(agents=[conversational_agent], tasks=[conversational_task], verbose=True, memory=True)

    @start()
    def process_input(self):
        print(f"Processing input: {self.state.current_query}")


        last_query = extract_last_meaningful_query(self.state.conversation_history.get_conversation_string(), self.state.current_query)

        print(last_query)

        if last_query:
            self.state.current_query = last_query

        self.state.conversation_history.add_message("User", self.state.current_query)

        # print('current query will be', self.state.current_query)

        self.state.is_task_specific = determine_if_task_specific_llm(self.state.current_query)

        # print(self.state.is_task_specific)

    @router(process_input)
    def route_query(self):
        if self.state.is_task_specific:
            return "task_specific"
        else:
            return "general_conversation"

    @listen("task_specific")
    def handle_task_query(self):
        result = self.task_crew.kickoff(inputs={
            "user_query": self.state.current_query,
            "conversation_history": self.state.conversation_history.get_conversation_string(),
            'mongodb_uri': mongodb_uri,
            'database_name': database_name,
            'collection_names': collection_names,
        })
        self.state.response = result.raw

    @listen("general_conversation")
    def handle_general_query(self):
        result = self.conversation_crew.kickoff(inputs={
            "user_query": self.state.current_query,
            "conversation_history": self.state.conversation_history.get_conversation_string()
        })
        self.state.response = result.raw

    @listen(or_(handle_task_query, handle_general_query))
    def update_conversation(self):
        self.state.conversation_history.add_message("AI", self.state.response)
        print(f"AI response: {self.state.response}")



def handle_interaction(flow, prompt, memory):
    flow.state.conversation_history = memory
    flow.state.current_query = prompt
    flow.kickoff()
    return flow.state.response



def main():

    st.set_page_config(page_title="AppetiQ", layout="wide", initial_sidebar_state="collapsed")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = load_chat_history()
    if 'current_thread' not in st.session_state:
        st.session_state.current_thread = None
    if 'show_placeholder' not in st.session_state:
        st.session_state.show_placeholder = True

    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationBufferWindow(window_size=10)

    if 'messages_container' not in st.session_state:
        st.session_state.messages_container = None

    with st.sidebar:
        render_sidebar()

    render_chat_messages()
    apply_css()

    # if prompt := st.chat_input("What would you like to know?"):
    #     st.session_state.messages.append({"role": "user", "content": prompt})
    #     with st.chat_message("user"):
    #         st.markdown(prompt)
    #
    #     flow = ChatbotFlow()
    #     response = handle_interaction(flow, prompt, st.session_state.memory)
    #
    #     with st.chat_message("assistant"):
    #         st.markdown(response)
    #
    #     st.session_state.messages.append({
    #         "role": "assistant",
    #         "content": response
    #     })
    #
    #     # Update the conversation memory
    #     st.session_state.memory.add_message("User", prompt)
    #     st.session_state.memory.add_message("Assistant", response)

    create_chat_interface(ChatbotFlow, mongodb_uri, database_name, collection_names)

if __name__ == "__main__":
    main()