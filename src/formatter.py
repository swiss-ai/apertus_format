"""Formatter for the Apertus chat format based on the chat template."""

from __future__ import annotations

from datetime import datetime
import json
import re
import os
from typing import List, Optional, Dict, Any
from jinja2 import Template, TemplateError
from .models import (
    Message,
    Conversation,
    AssistantContent,
    SystemContent,
    UserContent,
)
from .enums import Role, ContentFormat


class ApertusFormatter:
    """Formatter for converting conversations to/from the Apertus chat template format."""

    # Special tokens
    BOS_TOKEN = "<s>"
    SYSTEM_START = "<|system_start|>"
    SYSTEM_END = "<|system_end|>"
    DEVELOPER_START = "<|developer_start|>"
    DEVELOPER_END = "<|developer_end|>"
    USER_START = "<|user_start|>"
    USER_END = "<|user_end|>"
    ASSISTANT_START = "<|assistant_start|>"
    ASSISTANT_END = "<|assistant_end|>"
    INNER_PREFIX = "<|inner_prefix|>"
    INNER_SUFFIX = "<|inner_suffix|>"
    TOOLS_PREFIX = "<|tools_prefix|>"
    TOOLS_SUFFIX = "<|tools_suffix|>"

    def __init__(
        self,
        enable_thinking: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize the formatter.

        Args:
            enable_thinking: Whether thinking/deliberation is enabled
            tools: List of available tools for the conversation
        """
        self.enable_thinking = enable_thinking
        self.tools = tools or []

        template_path = os.path.join(
            os.path.dirname(__file__), "templates", "chat_template.jinja"
        )
        with open(template_path, "r", encoding="utf-8") as f:
            self.template = Template(f.read())

    def _detect_content_format(self, messages: List[Message]) -> ContentFormat:
        """Detect the content format used in the conversation."""
        for message in messages:
            # Skip tool messages as they don't participate in format detection
            if message.role == Role.TOOL:
                continue

            if isinstance(
                message.content, (SystemContent, UserContent, AssistantContent)
            ):
                return ContentFormat.MAPPING
            elif isinstance(message.content, str):
                return ContentFormat.STRING
        return ContentFormat.STRING

    def _validate_format_consistency(self, messages: List[Message]) -> None:
        """Validate that assistant messages use consistent content format."""
        if not messages:
            return

        # Find all assistant messages and check their format consistency
        assistant_messages = [
            (i, msg) for i, msg in enumerate(messages) if msg.role == Role.ASSISTANT
        ]

        if not assistant_messages:
            return

        # Detect format from first assistant message
        first_idx, first_assistant = assistant_messages[0]
        if isinstance(first_assistant.content, AssistantContent):
            expected_format = ContentFormat.MAPPING
        elif isinstance(first_assistant.content, str):
            expected_format = ContentFormat.STRING
        else:
            raise ValueError(
                f"Message {first_idx}: Assistant message has invalid content type: "
                f"{type(first_assistant.content).__name__}"
            )

        # Validate all assistant messages use the same format
        for i, message in assistant_messages[
            1:
        ]:
            if expected_format == ContentFormat.STRING:
                if not isinstance(message.content, str):
                    raise ValueError(
                        f"Format inconsistency: Assistant message {i} uses structured content "
                        f"but other assistant messages use string content. All assistant messages "
                        f"must use the same content format."
                    )
            elif expected_format == ContentFormat.MAPPING:
                if not isinstance(message.content, AssistantContent):
                    raise ValueError(
                        f"Format inconsistency: Assistant message {i} uses string content "
                        f"but other assistant messages use structured content. All assistant messages "
                        f"must use the same content format."
                    )

    def _prepare_messages_for_template(
        self, messages: List[Message]
    ) -> List[Dict[str, Any]]:
        """Convert Message objects to dictionaries for template rendering."""
        template_messages = []

        for message in messages:
            msg_dict = {"role": message.role.value}

            if isinstance(message.content, str):
                msg_dict["content"] = message.content
            elif isinstance(message.content, SystemContent):
                msg_dict["content"] = {"text": message.content.text}
            elif isinstance(message.content, UserContent):
                msg_dict["content"] = {
                    "parts": [
                        {"type": part.type, "text": part.text}
                        for part in message.content.parts
                    ]
                }
            elif isinstance(message.content, AssistantContent):
                blocks = []
                for block in message.content.blocks:
                    block_dict = {"type": block.type.value}
                    if block.text:
                        block_dict["text"] = block.text
                    if block.calls:
                        block_dict["calls"] = [
                            {"name": call.name, "arguments": call.arguments}
                            for call in block.calls
                        ]
                    if block.outputs:
                        block_dict["outputs"] = [
                            {"output": output.output} for output in block.outputs
                        ]
                    blocks.append(block_dict)
                msg_dict["content"] = {"blocks": blocks}
            else:
                msg_dict["content"] = message.content

            if message.tool_calls:
                msg_dict["tool_calls"] = []
                for tool_call in message.tool_calls:
                    msg_dict["tool_calls"].append(
                        {
                            "type": "function",
                            "function": {
                                "name": tool_call.name,
                                "arguments": tool_call.arguments,
                            },
                        }
                    )

            template_messages.append(msg_dict)

        return template_messages

    def format_conversation(
        self, conversation: Conversation, add_generation_prompt: bool = False
    ) -> str:
        """
        Format a conversation using the Apertus chat template.

        Args:
            conversation: The conversation to format
            add_generation_prompt: Whether to add assistant start token at the end

        Returns:
            Formatted conversation string

        Raises:
            ValueError: If assistant messages have inconsistent content formats
        """
        self._validate_format_consistency(conversation.messages)

        def raise_exception(message):
            raise TemplateError(message)
        
        def tojson(x, ensure_ascii=False, indent=None, separators=None, sort_keys=False):
            return json.dumps(x, ensure_ascii=ensure_ascii, indent=indent, separators=separators, sort_keys=sort_keys)
        
        def strftime_now(format):
            return datetime.now().strftime(format)

        template_vars = {
            "bos_token": self.BOS_TOKEN,
            "messages": self._prepare_messages_for_template(conversation.messages),
            "enable_thinking": self.enable_thinking,
            "tools": self.tools,
            "add_generation_prompt": add_generation_prompt,
            "raise_exception": raise_exception,
            "tojson": tojson,
            "strftime_now": strftime_now,
        }

        return self.template.render(**template_vars)

    def format_assistant_content(self, assistant_content: AssistantContent) -> str:
        """
        Format assistant content with blocks as a string for standard chat formats.

        This method allows you to render structured assistant content into a string
        that can be used in standard chat formats where content must be a string.

        Args:
            assistant_content: AssistantContent with structured blocks

        Returns:
            Formatted string representation of the assistant content
        """
        temp_message = Message(role=Role.ASSISTANT, content=assistant_content)

        def raise_exception(message):
            raise TemplateError(message)
        
        def tojson(x, ensure_ascii=False, indent=None, separators=None, sort_keys=False):
            return json.dumps(x, ensure_ascii=ensure_ascii, indent=indent, separators=separators, sort_keys=sort_keys)
        
        def strftime_now(format):
            return datetime.now().strftime(format)

        template_vars = {
            "bos_token": "",  # No BOS token for content-only formatting
            "messages": self._prepare_messages_for_template([temp_message]),
            "enable_thinking": self.enable_thinking,
            "tools": self.tools,
            "add_generation_prompt": False,
            "raise_exception": raise_exception,
            "tojson": tojson,
            "strftime_now": strftime_now,
        }

        full_rendered = self.template.render(**template_vars)

        start_pattern = self.ASSISTANT_START
        end_pattern = self.ASSISTANT_END

        start_idx = full_rendered.find(start_pattern)
        if start_idx != -1:
            start_idx += len(start_pattern)
            end_idx = full_rendered.find(end_pattern, start_idx)
            if end_idx != -1:
                return full_rendered[start_idx:end_idx].strip()
            else:
                return full_rendered[start_idx:].strip()

        return full_rendered.strip()

    def format_assistant_message_as_string(self, message: Message) -> str:
        """
        Format an assistant message with structured content as a simple string.

        This is useful for converting structured assistant messages to standard
        chat format where content must be a string.

        Args:
            message: Assistant message with structured or string content

        Returns:
            String representation of the assistant message content
        """
        if isinstance(message.content, str):
            return message.content
        elif isinstance(message.content, AssistantContent):
            return self.format_assistant_content(message.content)
        else:
            return str(message.content)

    def parse_conversation(self, formatted_text: str) -> Conversation:
        """
        Parse a formatted conversation back into a Conversation object.

        Args:
            formatted_text: The formatted conversation text

        Returns:
            Parsed Conversation object
        """
        text = formatted_text
        if text.startswith(self.BOS_TOKEN):
            text = text[len(self.BOS_TOKEN) :]

        messages = []

        # Parse system message
        system_match = re.search(
            f"{re.escape(self.SYSTEM_START)}(.*?){re.escape(self.SYSTEM_END)}",
            text,
            re.DOTALL,
        )
        if system_match:
            system_content = system_match.group(1).strip()
            if system_content:
                messages.append(Message.system(system_content))

        # Parse user messages
        user_matches = re.finditer(
            f"{re.escape(self.USER_START)}(.*?){re.escape(self.USER_END)}",
            text,
            re.DOTALL,
        )
        for match in user_matches:
            user_content = match.group(1).strip()
            messages.append(Message.user(user_content))

        # Parse assistant messages (simplified)
        assistant_matches = re.finditer(
            f"{re.escape(self.ASSISTANT_START)}(.*?)(?={re.escape(self.ASSISTANT_END)}|$)",
            text,
            re.DOTALL,
        )
        for match in assistant_matches:
            assistant_content = match.group(1).strip()
            messages.append(Message.assistant(assistant_content))

        return Conversation(messages)
