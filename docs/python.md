# Apertus Format Python API Reference

## Enumerations

### `Role`
Represents the author of a message. Possible values are `SYSTEM`, `USER`, `ASSISTANT`, `TOOL`.

### `BlockType`
Defines the types of blocks within an assistant message:
- `THOUGHTS` - reasoning content (always in inner section)
- `TOOL_CALLS` - parallel tool calls (can be in inner or outer)
- `TOOL_OUTPUTS` - parallel tool outputs (can be in inner or outer)
- `RESPONSE` - actual response to user (always in outer section)

### `ContentFormat`
Defines the content format being used:
- `STRING` - simple string content
- `MAPPING` - structured mapping content with parts/blocks

### `SectionType`
Defines the section within assistant messages:
- `INNER` - for reasoning content and internal tool calls
- `OUTER` - for final responses and external tool calls

## Dataclasses

### `TextPart`
```python
TextPart(type: str = "text", text: str)
```
Represents a text part within user content parts.

### `UserContent`
```python
UserContent(parts: List[TextPart])
```
Structured user content with multiple parts. Can be serialized to `{"parts": [...]}` format.

### `SystemContent`
```python
SystemContent(text: str)
```
System message content. Can be serialized to `{"text": "..."}` format.

### `AssistantBlock`
```python
AssistantBlock(type: BlockType, text: Optional[str] = None, calls: Optional[List[ToolCall]] = None, outputs: Optional[List[ToolOutput]] = None)
```
Represents a single block within an assistant message. The content depends on the block type:
- For `THOUGHTS` and `RESPONSE`: uses `text` field
- For `TOOL_CALLS`: uses `calls` field
- For `TOOL_OUTPUTS`: uses `outputs` field

### `ToolCall`
```python
ToolCall(name: str, arguments: str)
```
Represents a single tool call with function name and JSON arguments.

### `ToolOutput`
```python
ToolOutput(output: str)
```
Represents the output from a tool execution.

### `AssistantContent`
```python
AssistantContent(blocks: List[AssistantBlock])
```
Structured assistant content with multiple blocks. Can be serialized to `{"blocks": [...]}` format.

### `Message`
```python
Message(role: Role, content: Union[str, SystemContent, UserContent, AssistantContent])
```
A single chat message that can contain different content types based on the role.

Convenience methods:
- `Message.system(text: str)` - create a system message
- `Message.user(text: str)` - create a simple user message
- `Message.user_with_parts(parts: List[TextPart])` - create structured user message
- `Message.assistant(text: str)` - create simple assistant message
- `Message.assistant_with_blocks(blocks: List[AssistantBlock])` - create structured assistant message
- `Message.tool(content: str)` - create tool message

### `Conversation`
```python
Conversation(messages: List[Message])
```
Sequence of messages representing a complete conversation.

Methods:
- `to_dict()` - convert to dictionary format
- `from_dict(data: dict)` - create from dictionary
- `to_json()` - serialize to JSON string
- `from_json(json_str: str)` - deserialize from JSON string

## Formatting and Parsing

### `ApertusFormatter`
Main class for rendering conversations using the Apertus chat template with Jinja2 templating.

```python
ApertusFormatter(enable_thinking: bool = True, tools: Optional[List[dict]] = None)
```

Methods:
- `format_conversation(conversation: Conversation, add_generation_prompt: bool = False)` - render conversation to chat template format
- `format_assistant_content(assistant_content: AssistantContent)` - format structured assistant content as string
- `format_assistant_message_as_string(message: Message)` - format assistant message content as string for standard chat formats
- `parse_conversation(formatted_text: str)` - parse formatted text back to Conversation object

## Usage Examples

### Basic Usage

```python
from apertus_format import Message, Conversation, ApertusFormatter, Role

# Create messages
system_msg = Message.system("You are a helpful assistant.")
user_msg = Message.user("What is 2 + 2?")

# Create conversation
conversation = Conversation([system_msg, user_msg])

# Format using the chat template
formatter = ApertusFormatter(enable_thinking=True)
formatted = formatter.format_conversation(conversation, add_generation_prompt=True)
print(formatted)
```

### Structured Assistant Response

```python
from apertus_format import AssistantBlock, BlockType, ToolCall, ToolOutput

# Create assistant message with structured blocks
blocks = [
    AssistantBlock(type=BlockType.THOUGHTS, text="I need to calculate 2 + 2"),
    AssistantBlock(type=BlockType.TOOL_CALLS, calls=[
        ToolCall(name="calculator", arguments='{"expression": "2 + 2"}')
    ]),
    AssistantBlock(type=BlockType.TOOL_OUTPUTS, outputs=[
        ToolOutput(output="4")
    ]),
    AssistantBlock(type=BlockType.RESPONSE, text="The answer is 4.")
]

assistant_msg = Message.assistant_with_blocks(blocks)
conversation = Conversation([system_msg, user_msg, assistant_msg])

formatted = formatter.format_conversation(conversation)
print(formatted)
```

### Converting Structured Assistant Content to String

For compatibility with standard chat formats where content must be a string:

```python
from apertus_format import AssistantBlock, BlockType, AssistantContent

# Create structured assistant content
blocks = [
    AssistantBlock(type=BlockType.THOUGHTS, text="Let me think about this..."),
    AssistantBlock(type=BlockType.TOOL_CALLS, calls=[
        ToolCall(name="calculator", arguments='{"expr": "2+2"}')
    ]),
    AssistantBlock(type=BlockType.TOOL_OUTPUTS, outputs=[
        ToolOutput(output="4")
    ]),
    AssistantBlock(type=BlockType.RESPONSE, text="The answer is 4.")
]

assistant_content = AssistantContent(blocks)
assistant_message = Message.assistant_with_blocks(blocks)

formatter = ApertusFormatter(enable_thinking=True)

# Method 1: Format just the content
content_string = formatter.format_assistant_content(assistant_content)

# Method 2: Format the entire message content
message_string = formatter.format_assistant_message_as_string(assistant_message)

# Use in standard chat format
standard_message = Message(role=Role.ASSISTANT, content=content_string)
```

### Tool Messages Outside Assistant Blocks

The format also supports tool messages that appear outside of assistant message blocks:

```python
# Assistant makes tool call
assistant_msg = Message.assistant("I'll help you with that.")
assistant_msg.tool_calls = [ToolCall(name="search", arguments='{"query": "python"}')]

# Tool response as separate message
tool_msg = Message.tool("Here are the search results...")

conversation = Conversation([system_msg, user_msg, assistant_msg, tool_msg])
```
