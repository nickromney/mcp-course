# mcp-course agent guide

## Verify

- Offline gates: `make test-offline` (stdlib unittest with stubbed MCP modules; not SDK proof) and `make test-sdk-offline` (real SDK stdio handshake and tool calls, under `uv run --locked`).
- Pre-push gate: `lefthook run pre-push --force`, which runs `uv run --locked python -m unittest discover -s tests -v`.
- Model-backed demos (02, 03) spend tokens and need credentials; run them only for an attended scenario.
- A module import is not a handshake, a handshake is not a model-backed scenario, and none proves hosting.
