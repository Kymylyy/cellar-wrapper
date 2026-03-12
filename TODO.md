# TODO

- [ ] Enrich MCP tool descriptions with semantic context so LLMs know **when** and **why** to call each tool. Currently `_tool_description` in `mcp_server.py` produces generic text like `"CELLAR command 'lookup get-act' mapped to CellarClient.get_act."`. Add a `description` field to `CommandSpec` with human-readable explanations of what each tool does, what it returns, and when to prefer it over alternatives.
