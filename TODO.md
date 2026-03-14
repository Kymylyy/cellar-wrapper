# TODO

- [x] Enrich MCP tool descriptions with semantic context so LLMs know **when** and **why** to call each tool. `_tool_description` now reads human-focused descriptions from `CommandSpec`, so MCP tools expose maintained intent text instead of generic `"mapped to CellarClient.method"` boilerplate.
