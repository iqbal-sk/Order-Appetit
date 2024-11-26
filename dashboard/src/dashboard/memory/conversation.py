from crewai.tasks.task_output import TaskOutput
from collections import deque
import json
from typing import Any
from pydantic_core import CoreSchema, core_schema

class ConversationBufferWindow:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)

    def add_message(self, role: str, content: str):
        self.buffer.append((role, content))

    def add_task_output(self, task_output: TaskOutput):
        self.add_message(task_output.agent, f"{task_output.raw}")

    def get_conversation_string(self) -> str:
        return "\n".join([f"{role}: {content}" for role, content in self.buffer])

    def clear(self):
        self.buffer.clear()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.list_schema(
                core_schema.tuple_schema([
                    core_schema.str_schema(),
                    core_schema.str_schema()
                ])
            )
        )

    def to_json(self):
        return json.dumps({
            "window_size": self.window_size,
            "buffer": list(self.buffer)
        })

    @classmethod
    def from_dict(cls, dictionary: dict) -> "ConversationBufferWindow":
        data = dictionary
        instance = cls(window_size=data["window_size"])
        instance.buffer = deque(data["buffer"], maxlen=instance.window_size)
        return instance