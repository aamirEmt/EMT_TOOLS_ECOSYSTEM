# Tool Factory – Usage Guide

This document explains how a parent project can consume and interact with tools exposed via the centralized **ToolFactory**.

---

## Importing the Tool Factory

```python
from tools_factory.factory import get_tool_factory

factory = get_tool_factory()
```

The `get_tool_factory()` function returns a singleton instance that automatically registers all available tools.

---

## List All Available Tools

Use this when you want to discover all registered tools at runtime.

```python
all_tools = factory.list_all_tools()

for tool in all_tools:
    print(tool.metadata.name)
```

Example output:

```
flight_search
```

---

## Get Tool by Name

Use this when you know the exact tool you want to execute.

```python
flight_search_tool = factory.get_tool("flight_search")

if flight_search_tool:
    result = flight_search_tool.execute(
        origin="DEL",
        destination="BOM",
        date="2025-01-10"
    )
```

---

## Get Tools by Category

Categories help group tools by domain (for example: `flights`, `hotels`, `auth`).

```python
flight_tools = factory.get_tools_by_category("flights")

for tool in flight_tools:
    print(tool.metadata.name)
```

Typical categories:

* `flights`
* `hotels`
* `weather`
* `auth`

---

## Get Tools by Tags

Tags allow flexible discovery based on capabilities such as `search`, `booking`, or `public`.

```python
search_tools = factory.get_tools_by_tags(["search"])

for tool in search_tools:
    print(tool.metadata.name)
```

> A tool is returned if **any** of the provided tags match its metadata.

---

## Get Multiple Tools by Names

Fetch a predefined list of tools in one call.

```python
tools = factory.get_tools_by_names([
    "flight_search",
    "hotel_search"
])

for tool in tools:
    print(tool.metadata.name)
```

---

## Typical Usage in a Parent Application

```python
factory = get_tool_factory()

# Dynamically discover all flight-related tools
tools = factory.get_tools_by_category("flights")

# Execute the first matching tool
tool = tools[0]
response = tool.execute(**payload)
```

---

## Why Use ToolFactory

* Centralized tool registration and discovery
* Clean separation between tool logic and orchestration
* Easy integration with LLM agents, MCP servers, and LangGraph
* Scales naturally as the number of tools grows

---

This approach enables reusable, discoverable, and agent-friendly tooling across multiple projects.



