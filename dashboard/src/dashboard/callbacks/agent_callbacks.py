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
                message += f'\n{summarize_text(step_output.thought)}'
        else:
            message = f'🤔 Thought: {str(step_output)}'
        self.messages.append(message)
        self._update_display()

    def _update_display(self):
        self.placeholder.empty()
        with st.session_state.message_container:
            with self.placeholder:
                st.markdown(
                    f"""
                    <div style="
                        display: flex;
                        padding-left: 20%;
                        padding-right: 10%;
                    ">
                        {self.messages[-1]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )