# mcp-course agent guide

For system ownership, action effects, verification scope or a new agent task,
read [the operating model](docs/agent-system.md). Detailed product plans
remain at the linked owners; historical observations retain their dates.

The source-owned `.agent/contract.json` declares existing local verification actions,
their effects and acceptance scope, and lessons bound to exact source/test bytes.
Run the full local gate with `lefthook run pre-push --force`; a plain manual run
can select no files. Remote workflows publish allowed artifacts only. Local
fixture acceptance does not establish a live cloud, device or deployment state.
