import streamlit as st


from dashboard.src.dashboard.utils.utils import summarize_text


class AgentProgressCallback:
    def __init__(self, agent, container):
        self.container = container
        self.messages = []
        self.placeholder = container
        self.agent = agent

    def __call__(self, step_output):
        message = ''
        if hasattr(step_output, 'tool'):
            if hasattr(step_output, 'thought') and len(step_output.thought) > 0:
                message += f'\n{self.agent}💭: {summarize_text(step_output.thought)}'
        else:
            message = f'🤔 Thought: {str(step_output)}'
        self.messages.append(message)
        self._update_display()

    def _update_display(self):
        self.placeholder.empty()
        with self.placeholder:
            st.write(self.messages[-1])