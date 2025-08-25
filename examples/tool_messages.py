#!/usr/bin/env python3
"""Examples demonstrating tool messages outside of assistant blocks."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import Message, Conversation, ApertusFormatter, ToolCall


def tool_messages_example():
    """Example with tool messages outside of assistant blocks."""
    print("=== Tool Messages Outside Assistant Blocks Example ===")

    # Create initial conversation
    system_msg = Message.system("You are a helpful assistant with access to tools.")
    user_msg = Message.user("What's the weather like in Paris?")

    # Assistant makes a tool call (using the legacy format)
    assistant_msg = Message.assistant("I'll check the weather in Paris for you.")
    assistant_msg.tool_calls = [
        ToolCall(name="get_weather", arguments='{"city": "Paris", "country": "France"}')
    ]

    # Tool response as separate message
    tool_msg = Message.tool(
        '{"temperature": "22°C", "condition": "Sunny", "humidity": "65%"}'
    )

    # Assistant final response
    final_response = Message.assistant(
        "The weather in Paris is currently sunny with a temperature of 22°C and 65% humidity."
    )

    # Create conversation
    conversation = Conversation(
        [system_msg, user_msg, assistant_msg, tool_msg, final_response]
    )

    # Format with tools
    tools = [
        {
            "name": "get_weather",
            "description": "Get current weather information for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The city name"},
                    "country": {"type": "string", "description": "The country name"},
                },
                "required": ["city"],
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


if __name__ == "__main__":
    tool_messages_example()
