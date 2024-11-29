import streamlit as st

from crewai.tasks.task_output import TaskOutput
from dashboard.src.dashboard.utils.utils import summarize_task
from dashboard.src.dashboard.memory.conversation import ConversationBufferWindow


class TaskProgressCallback:
    def __init__(self, container, memory: ConversationBufferWindow):
        self.container = container
        self.memory = memory
        self.message = None
        self.placeholder = container

    def __call__(self, task_output: TaskOutput):
        task_name = task_output.name if task_output.name else ''
        summary = summarize_task(task_name + ': ' + task_output.summary)
        self.message = f"{summary}"
        self.memory.add_task_output(task_output)
        self._update_display()

    def _update_display(self):
        self.placeholder.empty()
        with st.session_state.message_container:
            with self.placeholder:
                st.markdown(
                    f"""
                            <div style="
                                display: flex;
                                padding-left: 10%;
                                padding-right: 10%;
                            ">
                                {self.message}
                            </div>
                            """,
                    unsafe_allow_html=True
                )