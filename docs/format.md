# Apertus Chat Format Specification

The Apertus format is a structured conversational format designed for agentic AI models that need to think, use tools, and provide comprehensive responses. This document explains how the format works and its key features.

## Table of Contents

- [Basic Message Structure](#basic-message-structure)
- [Content Formats](#content-formats)
- [Assistant Message Structure](#assistant-message-structure)
- [Tool Integration](#tool-integration)
- [Format Consistency Rules](#format-consistency-rules)
- [Chat Template and Tokens](#chat-template-and-tokens)
- [Complete Examples](#complete-examples)

## Basic Message Structure

Every message in the Apertus format has two core components:

```python
{
    "role": "system" | "user" | "assistant" | "tool",
    "content": <varies by role and format>
}
```

### Message Roles

- **`system`**: System instructions and configuration
- **`user`**: User input and queries  
- **`assistant`**: AI model responses (can be structured)
- **`tool`**: Tool execution results (always simple strings)

## Content Formats

The Apertus format supports two content formats that can be mixed within conversations:

### String Format (Simple)

Traditional chat format where content is a simple string:

```python
{
    "role": "user",
    "content": "What is machine learning?"
}
```

### Mapping Format (Structured)

Advanced format with structured content objects:

**System Message:**
```python
{
    "role": "system", 
    "content": {
        "text": "You are a helpful assistant."
    }
}
```

**User Message:**
```python
{
    "role": "user",
    "content": {
        "parts": [
            {"type": "text", "text": "Please explain "},
            {"type": "text", "text": "machine learning"}
        ]
    }
}
```

**Assistant Message:**
```python
{
    "role": "assistant",
    "content": {
        "blocks": [
            {"type": "thoughts", "text": "I need to explain ML clearly..."},
            {"type": "response", "text": "Machine learning is..."}
        ]
    }
}
```

## Assistant Message Structure

The key innovation of the Apertus format is the structured assistant message with multiple block types:

### Block Types

| Block Type | Purpose | Location | Required Fields |
|------------|---------|----------|-----------------|
| `thoughts` | Reasoning and planning | Inner | `text` |
| `tool_calls` | Parallel tool invocations | Inner/Outer | `calls` |
| `tool_outputs` | Results from tool calls | Inner/Outer | `outputs` |
| `response` | Final response to user | Outer | `text` |

### Inner vs Outer Sections

The assistant message is divided into two conceptual sections:

- **Inner Section**: Private reasoning, thinking, internal tool calls
- **Outer Section**: Public responses, external tool calls, final answers

```python
{
    "role": "assistant",
    "content": {
        "blocks": [
            # Inner section
            {"type": "thoughts", "text": "Let me think about this..."},
            {"type": "tool_calls", "calls": [...]},  # Internal tool use
            {"type": "tool_outputs", "outputs": [...]},
            
            # Outer section  
            {"type": "response", "text": "Based on my analysis..."}
        ]
    }
}
```

### Block Structure Examples

**Thoughts Block:**
```python
{
    "type": "thoughts",
    "text": "I need to calculate this step by step. Let me break it down..."
}
```

**Tool Calls Block:**
```python
{
    "type": "tool_calls", 
    "calls": [
        {
            "name": "calculator",
            "arguments": "{\"expression\": \"25 * 4\"}"
        }
    ]
}
```

**Tool Outputs Block:**
```python
{
    "type": "tool_outputs",
    "outputs": [
        {"output": "{\"result\": 100}"}
    ]
}
```

**Response Block:**
```python
{
    "type": "response",
    "text": "The calculation shows that 25 × 4 = 100."
}
```

## Tool Integration

The Apertus format supports two ways to handle tool interactions:

### 1. Tools Within Assistant Blocks

Tools calls and outputs are embedded within the assistant message:

```python
{
    "role": "assistant",
    "content": {
        "blocks": [
            {"type": "thoughts", "text": "I need to search for this."},
            {"type": "tool_calls", "calls": [{"name": "search", "arguments": "..."}]},
            {"type": "tool_outputs", "outputs": [{"output": "search results..."}]},
            {"type": "response", "text": "Based on my search..."}
        ]
    }
}
```

### 2. Tool Messages Outside Blocks

Tool outputs can be separate messages in the conversation:

```python
[
    {"role": "user", "content": "Search for Python info"},
    {
        "role": "assistant", 
        "content": {
            "blocks": [
                {"type": "thoughts", "text": "I'll search for Python information."},
                {"type": "tool_calls", "calls": [{"name": "search", "arguments": "..."}]}
                # Note: No tool_outputs block here
            ]
        }
    },
    {"role": "tool", "content": "Python is a programming language..."}, # Separate message
    {
        "role": "assistant",
        "content": {
            "blocks": [
                {"type": "response", "text": "Based on the search results..."}
            ]
        }
    }
]
```

### Legacy Tool Call Format

The format also supports the standard OpenAI-style tool calls:

```python
{
    "role": "assistant",
    "content": "I'll help you with that.",
    "tool_calls": [
        {
            "type": "function",
            "function": {
                "name": "search",
                "arguments": "{\"query\": \"python\"}"
            }
        }
    ]
}
```

## Format Consistency Rules

The Apertus format has relaxed consistency rules that provide maximum flexibility:

### What is allowed

1. **Mixed System/User Formats**: System and user messages can use any combination of string and mapping formats
2. **Consistent Assistant Formats**: All assistant messages must use the same format (all string OR all structured)  
3. **Tool Message Exception**: Tool messages are always strings and don't affect validation

### What is not allowed

1. **Mixed Assistant Formats**: Cannot mix string and structured assistant messages in the same conversation

### Examples

**Valid: Mixed system/user, consistent assistants**
```python
[
    {"role": "system", "content": "String format system"},           # String
    {"role": "user", "content": {"parts": [...]}},                   # Mapping
    {"role": "assistant", "content": "String assistant 1"},          # String
    {"role": "assistant", "content": "String assistant 2"}           # String
]
```

**Valid: Any mix with structured assistants**
```python
[
    {"role": "system", "content": {"text": "Mapping system"}},        # Mapping
    {"role": "user", "content": "String user"},                      # String
    {"role": "assistant", "content": {"blocks": [...]}},             # Structured
    {"role": "assistant", "content": {"blocks": [...]}}              # Structured
]
```

**Invalid: Inconsistent assistant formats**
```python
[
    {"role": "system", "content": "Any format"},
    {"role": "user", "content": "Any format"},
    {"role": "assistant", "content": "String assistant"},           # String
    {"role": "assistant", "content": {"blocks": [...]}}             # Structured
]
```

## Chat Template and Tokens

The Apertus format uses special tokens to structure the conversation when rendered:

### Core Tokens

- `<|system_start|>` / `<|system_end|>` - System message boundaries
- `<|user_start|>` / `<|user_end|>` - User message boundaries
- `<|assistant_start|>` / `<|assistant_end|>` - Assistant message boundaries
- `<|developer_start|>` / `<|developer_end|>` - Developer/configuration section

### Assistant-Specific Tokens

- `<|inner_prefix|>` / `<|inner_suffix|>` - Inner/outer section boundaries
- `<|tools_prefix|>` / `<|tools_suffix|>` - Tool call boundaries

### Example Rendered Output

```
<s><|system_start|>You are helpful.<|system_end|>
<|developer_start|>Deliberation: enabled
Tool Capabilities: disabled<|developer_end|>
<|user_start|>What is 2+2?<|user_end|>
<|assistant_start|><|inner_prefix|>I need to calculate this.<|inner_suffix|>
<|tools_prefix|>[{"calculator": {"expr": "2+2"}}]<|tools_suffix|>
[4]
The answer is 4.<|assistant_end|>
```

## Complete Examples

### Example 1: Simple String Format

```python
[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI stands for Artificial Intelligence."}
]
```

### Example 2: Structured Format with Tools

```python
[
    {
        "role": "system",
        "content": {"text": "You are a research assistant."}
    },
    {
        "role": "user", 
        "content": {
            "parts": [
                {"type": "text", "text": "Research machine learning for me"}
            ]
        }
    },
    {
        "role": "assistant",
        "content": {
            "blocks": [
                {
                    "type": "thoughts",
                    "text": "I need to search for comprehensive information about machine learning."
                },
                {
                    "type": "tool_calls",
                    "calls": [
                        {
                            "name": "web_search",
                            "arguments": "{\"query\": \"machine learning overview\"}"
                        }
                    ]
                },
                {
                    "type": "tool_outputs", 
                    "outputs": [
                        {"output": "Machine learning is a subset of AI..."}
                    ]
                },
                {
                    "type": "response",
                    "text": "Based on my research, machine learning is a powerful subset of artificial intelligence..."
                }
            ]
        }
    }
]
```

### Example 3: Mixed Format with Tool Messages

```python
[
    {"role": "system", "content": "You are helpful."},                    # String
    {"role": "user", "content": {"parts": [{"type": "text", "text": "Hi"}]}}, # Mapping
    {
        "role": "assistant", 
        "content": {
            "blocks": [
                {"type": "thoughts", "text": "User said hi, I should search for greeting info."},
                {"type": "tool_calls", "calls": [{"name": "search", "arguments": "..."}]}
            ]
        }
    },
    {"role": "tool", "content": "Greeting information found..."},        # Always string
    {
        "role": "assistant",
        "content": {
            "blocks": [
                {"type": "response", "text": "Hello! Nice to meet you."}
            ]
        }
    }
]
```
