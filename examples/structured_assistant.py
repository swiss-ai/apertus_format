#!/usr/bin/env python3
"""Examples demonstrating structured assistant messages with blocks."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import (
    Message,
    Conversation,
    ApertusFormatter,
    BlockType,
    AssistantBlock,
    ToolCall,
    ToolOutput,
)


def structured_assistant_example():
    """Example with structured assistant message containing multiple blocks."""
    print("=== Structured Assistant Message Example ===")

    # Create system and user messages
    system_msg = Message.system("You are a helpful assistant with access to tools.")
    user_msg = Message.user("What is the square root of 144?")

    # Create structured assistant message with multiple blocks
    blocks = [
        # Reasoning block (inner)
        AssistantBlock(
            type=BlockType.THOUGHTS,
            text="I need to calculate the square root of 144. I can use my calculator tool for this.",
        ),
        # Tool call block
        AssistantBlock(
            type=BlockType.TOOL_CALLS,
            calls=[
                ToolCall(
                    name="calculator", arguments='{"operation": "sqrt", "value": 144}'
                )
            ],
        ),
        # Tool output block
        AssistantBlock(
            type=BlockType.TOOL_OUTPUTS, outputs=[ToolOutput(output='{"output": 12}')]
        ),
        # Final response block (outer)
        AssistantBlock(type=BlockType.RESPONSE, text="The square root of 144 is 12."),
    ]

    assistant_msg = Message.assistant_with_blocks(blocks)

    # Create conversation
    conversation = Conversation([system_msg, user_msg, assistant_msg])

    # Format with tools
    tools = [
        {
            "name": "calculator",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide", "sqrt"],
                        "description": "The mathematical operation to perform",
                    },
                    "value": {
                        "type": "number",
                        "description": "The value to operate on",
                    },
                },
                "required": ["operation", "value"],
            },
        }
    ]

    formatter = ApertusFormatter(enable_thinking=True, tools=tools)
    formatted = formatter.format_conversation(conversation)

    print("Formatted conversation:")
    print(formatted)
    print()

    print("JSON representation:")
    print(conversation.to_json(indent=2))
    print()


def multiple_tool_calls_example():
    """Example with multiple parallel tool calls."""
    print("=== Multiple Tool Calls Example ===")

    system_msg = Message.system("You are a research assistant.")
    user_msg = Message.user("Find information about Python and JavaScript.")

    blocks = [
        AssistantBlock(
            type=BlockType.THOUGHTS,
            text="I need to search for information about both Python and JavaScript. I'll make parallel searches.",
        ),
        AssistantBlock(
            type=BlockType.TOOL_CALLS,
            calls=[
                ToolCall(
                    name="web_search",
                    arguments='{"query": "Python programming language"}',
                ),
                ToolCall(
                    name="web_search",
                    arguments='{"query": "JavaScript programming language"}',
                ),
            ],
        ),
        AssistantBlock(
            type=BlockType.TOOL_OUTPUTS,
            outputs=[
                ToolOutput(
                    output='{"output": "Python is a high-level programming language..."}'
                ),
                ToolOutput(
                    output='{"output": "JavaScript is a programming language for web development..."}'
                ),
            ],
        ),
        AssistantBlock(
            type=BlockType.RESPONSE,
            text="I found information about both languages. Python is excellent for data science and backend development, while JavaScript is essential for web development.",
        ),
    ]

    assistant_msg = Message.assistant_with_blocks(blocks)
    conversation = Conversation([system_msg, user_msg, assistant_msg])

    tools = [
        {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
            },
        }
    ]

    formatter = ApertusFormatter(enable_thinking=True, tools=tools)
    formatted = formatter.format_conversation(conversation)

    print("Formatted conversation:")
    print(formatted)
    print()


if __name__ == "__main__":
    structured_assistant_example()
    multiple_tool_calls_example()
