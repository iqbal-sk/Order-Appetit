import streamlit as st
from openai import OpenAI
from dashboard.src.dashboard.config import agents_config, tasks_config
from dashboard.src.dashboard.tools.items_finder import filter_items
from dashboard.src.dashboard.tools.schema_analysis import analyze_local_schema
from dashboard.src.dashboard.tools.python_executor import execute_python_code
from langchain_openai import ChatOpenAI

from crewai import Agent, Task
from dashboard.src.dashboard.callbacks.task_callbacks import TaskProgressCallback

from dotenv import load_dotenv

load_dotenv()


def create_agents(callback_handler, placeholder):
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, max_tokens=16384)

    schema_analyzer = Agent(
        role=agents_config['schema_analyzer']['role'],
        goal=agents_config['schema_analyzer']['goal'],
        backstory=agents_config['schema_analyzer']['backstory'],
        verbose=True,
        allow_delegation=False,
        tools=[analyze_local_schema, filter_items],
        llm=llm,
        cache=True,
        step_callback=callback_handler('Schema Analyzer', placeholder)
    )

    query_builder = Agent(
        role=agents_config['query_builder']['role'],
        goal=agents_config['query_builder']['goal'],
        backstory=agents_config['query_builder']['backstory'],
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=callback_handler('Query Builder', placeholder)
    )

    data_analyst = Agent(
        role=agents_config['data_analyst']['role'],
        goal=agents_config['data_analyst']['goal'],
        backstory=agents_config['data_analyst']['backstory'],
        verbose=True,
        allow_delegation=False,
        tools=[execute_python_code],
        llm=llm,
        step_callback=callback_handler('Data Analyst', placeholder),
        max_retries=3,
        max_execution_time=20
    )

    return [schema_analyzer, query_builder, data_analyst]


def create_tasks(agents, placeholder, memory):
    callback = TaskProgressCallback(placeholder, memory)

    schema_analysis_task = Task(
        description=tasks_config['schema_analysis_task']['description'],
        expected_output=tasks_config['schema_analysis_task']['expected_output'],
        agent=agents[0],
        callback=callback
    )


    query_building_task = Task(
        description=tasks_config['query_building_task']['description'],
        expected_output=tasks_config['query_building_task']['expected_output'],
        agent=agents[1],
        context=[schema_analysis_task],
        callback=callback
    )

    data_analysis_task = Task(
        description=tasks_config['data_analysis_task']['description'],
        expected_output=tasks_config['data_analysis_task']['expected_output'],
        agent=agents[2],
        context=[schema_analysis_task, query_building_task],
        callback=callback
    )

    return [schema_analysis_task, query_building_task, data_analysis_task]


def create_conversational_agent(callback_handler, placeholder):
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.0)

    conversational_agent = Agent(
        role="Conversational AI Assistant",
        goal="Engage in natural conversations with users.",
        backstory="I am an AI assistant designed to have friendly and informative conversations.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        # step_callback=callback_handler('Conversational Agent', placeholder)
    )

    return conversational_agent


def create_conversational_task(agent, memory):
    return Task(
        description="Engage in a conversation with the user, Consider {conversation_history} and current user query: {user_query}",
        expected_output="A natural response to user input",
        agent=agent,
        # callback=TaskProgressCallback(st.empty(), memory)
    )


llm_classifier = OpenAI()
def determine_if_task_specific_llm(user_input):
    # Use an LLM to classify the input as task-specific or not


    prompt = f"Determine if the following query is related to database tasks or general conversation:\n\nQuery: \"{user_input}\"\n\nResponse with 'Task' or 'General'."

    response = llm_classifier.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt}
        ],
        max_tokens=10,
        temperature=0.0
    )

    classification = response.choices[0].message.content.strip().lower()

    return classification == 'task'