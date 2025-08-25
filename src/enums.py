"""Enumerations for the Apertus chat format."""

from enum import Enum, auto


class Role(Enum):
    """Message role enumeration."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class BlockType(Enum):
    """Assistant message block type enumeration."""

    THOUGHTS = "thoughts"
    TOOL_CALLS = "tool_calls"
    TOOL_OUTPUTS = "tool_outputs"
    RESPONSE = "response"


class ContentFormat(Enum):
    """Content format enumeration."""

    STRING = auto()
    MAPPING = auto()


class SectionType(Enum):
    """Section type for assistant message organization."""

    INNER = auto()
    OUTER = auto()
