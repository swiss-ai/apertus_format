#!/usr/bin/env python3
"""Examples demonstrating assistant content formatting as strings for standard chat formats."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (
    Message,
    Conversation,
    ApertusFormatter,
    Role,
    BlockType,
    AssistantBlock,
    ToolCall,
    ToolOutput,
    AssistantContent,
)


def format_structured_assistant_as_string():
    """Convert structured assistant content to string for standard chat formats."""
    print("=== Converting Structured Assistant Content to String ===")

    # Create structured assistant content with multiple blocks
    blocks = [
        AssistantBlock(
            type=BlockType.THOUGHTS,
            text="I need to think about this problem step by step. Let me break it down.",
        ),
        AssistantBlock(
            type=BlockType.TOOL_CALLS,
            calls=[ToolCall(name="calculator", arguments='{"expression": "25 * 4"}')],
        ),
        AssistantBlock(
            type=BlockType.TOOL_OUTPUTS, outputs=[ToolOutput(output='{"output": 100}')]
        ),
        AssistantBlock(
            type=BlockType.RESPONSE, text="The calculation shows that 25 * 4 = 100."
        ),
    ]

    assistant_message = Message(role=Role.ASSISTANT, content=AssistantContent(blocks))

    # Initialize formatter
    formatter = ApertusFormatter(
        enable_thinking=True,
        tools=[
            {
                "name": "calculator",
                "description": "A calculator tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The expression to calculate",
                        }
                    },
                },
            }
        ],
    )

    # Format the entire assistant message as string
    formatted_message = formatter.format_assistant_message_as_string(assistant_message)
    print("Formatted message:")
    print(formatted_message)
    print()

    system_message = Message.system("You are a research assistant.")
    user_message = Message.user("Find information about Python and JavaScript.")

    # Format the entire assistant message as string
    conversation = Conversation([system_message, user_message, assistant_message])
    formatted = formatter.format_conversation(conversation)
    print("Formatted conversation:")
    print(formatted)
    print()


def mixed_assistant_blocks_tool_messsage():
    """Demonstrate how we can use assistant blocks with separate messages for tool outputs"""
    print("=== Mixed Assistant Blocks with Tool Messages Example ===")

    formatter = ApertusFormatter(
        enable_thinking=True,
        tools=[
            {
                "name": "calculator",
                "description": "A calculator tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The expression to calculate",
                        }
                    },
                },
            }
        ],
    )

    assistant_message1 = Message.assistant_with_blocks(
        [
            AssistantBlock(
                type=BlockType.THOUGHTS,
                text="I need to think about this problem step by step. Let me break it down.",
            ),
            AssistantBlock(
                type=BlockType.TOOL_CALLS,
                calls=[
                    ToolCall(name="calculator", arguments='{"expression": "25 * 4"}')
                ],
            ),
        ]
    )

    tool_message = Message.tool('{"output": 100}')

    assistant_message2 = Message.assistant_with_blocks(
        [
            AssistantBlock(
                type=BlockType.RESPONSE, text="The calculation shows that 25 * 4 = 100."
            ),
        ]
    )

    system_message = Message.system("You are a research assistant.")
    user_message = Message.user("Find information about Python and JavaScript.")

    conversation = Conversation(
        [
            system_message,
            user_message,
            assistant_message1,
            tool_message,
            assistant_message2,
        ]
    )

    formatted = formatter.format_conversation(conversation)
    print("Formatted conversation:")
    print(formatted)
    print()


if __name__ == "__main__":
    format_structured_assistant_as_string()
    mixed_assistant_blocks_tool_messsage()
