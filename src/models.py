"""Core dataclasses for the Apertus chat format."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any
from .enums import Role, BlockType


@dataclass
class TextPart:
    """A text part within user content."""

    text: str
    type: str = "text"

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"type": self.type, "text": self.text}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> TextPart:
        """Create from dictionary format."""
        return cls(text=data["text"], type=data.get("type", "text"))


@dataclass
class SystemContent:
    """System message content in mapping format."""

    text: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"text": self.text}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> SystemContent:
        """Create from dictionary format."""
        return cls(text=data["text"])


@dataclass
class UserContent:
    """User message content in mapping format."""

    parts: List[TextPart]

    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        """Convert to dictionary format."""
        return {"parts": [part.to_dict() for part in self.parts]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserContent:
        """Create from dictionary format."""
        parts = [TextPart.from_dict(part_data) for part_data in data["parts"]]
        return cls(parts=parts)


@dataclass
class ToolCall:
    """A tool call within an assistant message."""

    name: str
    arguments: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"name": self.name, "arguments": self.arguments}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> ToolCall:
        """Create from dictionary format."""
        return cls(name=data["name"], arguments=data["arguments"])


@dataclass
class ToolOutput:
    """A tool output within an assistant message."""

    output: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"output": self.output}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> ToolOutput:
        """Create from dictionary format."""
        return cls(output=data["output"])


@dataclass
class AssistantBlock:
    """A block within an assistant message."""

    type: BlockType
    text: Optional[str] = None
    calls: Optional[List[ToolCall]] = None
    outputs: Optional[List[ToolOutput]] = None

    def __post_init__(self):
        """Validate block content based on type."""
        if self.type in (BlockType.THOUGHTS, BlockType.RESPONSE):
            if self.text is None:
                raise ValueError(f"{self.type.value} block requires text")
            if self.calls is not None or self.outputs is not None:
                raise ValueError(
                    f"{self.type.value} block cannot have calls or outputs"
                )
        elif self.type == BlockType.TOOL_CALLS:
            if self.calls is None:
                raise ValueError("tool_calls block requires calls")
            if self.text is not None or self.outputs is not None:
                raise ValueError("tool_calls block cannot have text or outputs")
        elif self.type == BlockType.TOOL_OUTPUTS:
            if self.outputs is None:
                raise ValueError("tool_outputs block requires outputs")
            if self.text is not None or self.calls is not None:
                raise ValueError("tool_outputs block cannot have text or calls")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {"type": self.type.value}

        if self.text is not None:
            result["text"] = self.text
        if self.calls is not None:
            result["calls"] = [call.to_dict() for call in self.calls]
        if self.outputs is not None:
            result["outputs"] = [output.to_dict() for output in self.outputs]

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssistantBlock:
        """Create from dictionary format."""
        block_type = BlockType(data["type"])

        text = data.get("text")
        calls = None
        outputs = None

        if "calls" in data:
            calls = [ToolCall.from_dict(call_data) for call_data in data["calls"]]
        if "outputs" in data:
            outputs = [
                ToolOutput.from_dict(output_data) for output_data in data["outputs"]
            ]

        return cls(type=block_type, text=text, calls=calls, outputs=outputs)


@dataclass
class AssistantContent:
    """Assistant message content in mapping format."""

    blocks: List[AssistantBlock]

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert to dictionary format."""
        return {"blocks": [block.to_dict() for block in self.blocks]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssistantContent:
        """Create from dictionary format."""
        blocks = [AssistantBlock.from_dict(block_data) for block_data in data["blocks"]]
        return cls(blocks=blocks)


@dataclass
class Message:
    """A single chat message."""

    role: Role
    content: Union[str, SystemContent, UserContent, AssistantContent]
    tool_calls: Optional[List[ToolCall]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {"role": self.role.value}

        if isinstance(self.content, str):
            result["content"] = self.content
        else:
            result["content"] = self.content.to_dict()

        if self.tool_calls:
            result["tool_calls"] = [
                {
                    "type": "function",
                    "function": {"name": call.name, "arguments": call.arguments},
                }
                for call in self.tool_calls
            ]

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Message:
        """Create from dictionary format."""
        role = Role(data["role"])
        content_data = data["content"]

        # Parse content based on role and format
        if isinstance(content_data, str):
            content = content_data
        elif role == Role.SYSTEM and "text" in content_data:
            content = SystemContent.from_dict(content_data)
        elif role == Role.USER and "parts" in content_data:
            content = UserContent.from_dict(content_data)
        elif role == Role.ASSISTANT and "blocks" in content_data:
            content = AssistantContent.from_dict(content_data)
        else:
            content = content_data  # Fallback to raw content

        # Parse tool calls if present
        tool_calls = None
        if "tool_calls" in data:
            tool_calls = []
            for tc_data in data["tool_calls"]:
                if tc_data.get("type") == "function":
                    func_data = tc_data["function"]
                    tool_calls.append(
                        ToolCall(
                            name=func_data["name"], arguments=func_data["arguments"]
                        )
                    )

        return cls(role=role, content=content, tool_calls=tool_calls)

    @classmethod
    def system(cls, text: str) -> Message:
        """Create a system message with string content."""
        return cls(role=Role.SYSTEM, content=text)

    @classmethod
    def system_with_mapping(cls, text: str) -> Message:
        """Create a system message with mapping content."""
        return cls(role=Role.SYSTEM, content=SystemContent(text))

    @classmethod
    def user(cls, text: str) -> Message:
        """Create a user message with string content."""
        return cls(role=Role.USER, content=text)

    @classmethod
    def user_with_parts(cls, parts: List[TextPart]) -> Message:
        """Create a user message with structured parts."""
        return cls(role=Role.USER, content=UserContent(parts))

    @classmethod
    def assistant(cls, text: str) -> Message:
        """Create an assistant message with string content."""
        return cls(role=Role.ASSISTANT, content=text)

    @classmethod
    def assistant_with_blocks(cls, blocks: List[AssistantBlock]) -> Message:
        """Create an assistant message with structured blocks."""
        return cls(role=Role.ASSISTANT, content=AssistantContent(blocks))

    @classmethod
    def tool(cls, content: str) -> Message:
        """Create a tool message."""
        return cls(role=Role.TOOL, content=content)


@dataclass
class Conversation:
    """A sequence of messages representing a conversation."""

    messages: List[Message]

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert to dictionary format."""
        return {"messages": [msg.to_dict() for msg in self.messages]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Conversation:
        """Create from dictionary format."""
        messages = [Message.from_dict(msg_data) for msg_data in data["messages"]]
        return cls(messages=messages)

    def to_json(self, indent: Optional[int] = None) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> Conversation:
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_messages(cls, messages: List[Message]) -> Conversation:
        """Create a conversation from a list of messages."""
        return cls(messages=messages)
