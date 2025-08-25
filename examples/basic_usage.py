#!/usr/bin/env python3
"""Basic usage examples for the Apertus format library."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import Message, Conversation, ApertusFormatter


def basic_string_format():
    """Example using string format for messages."""
    print("=== Basic String Format Example ===")

    # Create messages using string format
    system_msg = Message.system("You are a helpful assistant.")
    user_msg = Message.user("What is 2 + 2?")
    assistant_msg = Message.assistant("The answer is 4.")

    # Create conversation
    conversation = Conversation([system_msg, user_msg, assistant_msg])

    # Format using the chat template
    formatter = ApertusFormatter(enable_thinking=True)
    formatted = formatter.format_conversation(conversation)

    print("Formatted conversation:")
    print(formatted)
    print()

    # Convert to JSON
    json_output = conversation.to_json(indent=2)
    print("JSON representation:")
    print(json_output)
    print()


def basic_mapping_format():
    """Example using mapping format for messages."""
    print("=== Basic Mapping Format Example ===")

    from src import TextPart, AssistantBlock, BlockType

    # Create messages using mapping format
    system_msg = Message.system_with_mapping("You are a helpful assistant.")
    user_msg = Message.user_with_parts(
        [TextPart(text="What is "), TextPart(text="2 + 2"), TextPart(text="?")]
    )
    # Assistant message must also use mapping format for consistency
    assistant_msg = Message.assistant_with_blocks(
        [AssistantBlock(type=BlockType.RESPONSE, text="The answer is 4.")]
    )

    # Create conversation
    conversation = Conversation([system_msg, user_msg, assistant_msg])

    # Format using the chat template
    formatter = ApertusFormatter(enable_thinking=True)
    formatted = formatter.format_conversation(conversation)

    print("Formatted conversation:")
    print(formatted)
    print()


if __name__ == "__main__":
    basic_string_format()
    basic_mapping_format()
