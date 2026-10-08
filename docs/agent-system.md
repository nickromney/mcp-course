# mcp-course: agent operating model

Adopted 6 October 2026 from local source and command inspection.
Independent teaching demos of MCP servers, clients and agent applications.

## Read by intent

Start with the local agent guide and build manifest. For domain or behavior
changes, follow the owners below, then the relevant contract/test. These
documents retain product detail and historical evidence:

- [README.md](../README.md)
- [demos/02-study-case-anthropic-tools-resources-prompts-chat-app/README.md](../demos/02-study-case-anthropic-tools-resources-prompts-chat-app/README.md)
- [demos/03-claude-agents-sdk-filesystem-agent/README.md](../demos/03-claude-agents-sdk-filesystem-agent/README.md)
- [demos/04-query-tabular-data/README.md](../demos/04-query-tabular-data/README.md)
- [demos/05-automations-agent/reports/link_audit_2026-04-22.md](../demos/05-automations-agent/reports/link_audit_2026-04-22.md)

## System ownership

| Owner | Responsibility |
| --- | --- |
| [demos/01-introduction-to-mcp](../demos/01-introduction-to-mcp) | Progressive protocol and model-backed examples. |
| [demos/02-study-case-anthropic-tools-resources-prompts-chat-app](../demos/02-study-case-anthropic-tools-resources-prompts-chat-app) | Progressive protocol and model-backed examples. |
| [requirements](../requirements) | Shared/inline dependency declarations. |
| [demos](../demos) | Shared/inline dependency declarations. |
| [tests/test_offline_demos.py](../tests/test_offline_demos.py) | Credential-free behavior with stubbed mcp modules; not SDK proof. |
| [tests/test_sdk_stdio.py](../tests/test_sdk_stdio.py) | Actual SDK stdio protocol proof (`make test-sdk-offline`). |

Intent selects the owning policy; that policy produces decisions or artifacts;
adapters perform effects; verification establishes the result. Change the
owner once and keep alternate surfaces on that same contract.

## Invariants

- A server module import is weaker evidence than SDK handshake/tool call.
- Model-backed demos spend tokens and require credentials.

## Existing action interfaces

These are inspected command surfaces, not a report that they ran. Read current
help and recipes for arguments, dependencies and lifecycle hooks before use.
Examples containing placeholder paths or bracketed options are grammar.

| Command | Effects and evidence |
| --- | --- |
| `make test-offline` | Python unittest offline demos. |
| `make test-sdk-offline` | SDK stdio unittest under `uv run --locked` (pyproject.toml, uv.lock). |
| `cd demos/01-introduction-to-mcp && uv run mcp_server.py` | Runs selected demo; uv may resolve dependencies. |

## Observe, verify and retain

Establish source revision, dirty state and relevant input identity before
choosing an action. Keep intended settings, cached artifacts and observed
runtime state distinct. An existing artifact is not a freshness or readiness
claim. Use the smallest deterministic fixture at the changed seam first;
expand to process, browser, device or deployment checks only when that
claim needs them. Record unavailable evidence explicitly.

Retain the command/configuration, source and input identity, result, limitation
and next discriminating check. Reuse evidence only while its relevant inputs
remain applicable. Promote a reproducible failure to a regression fixture,
a design decision to its owning document, and a repeated operator correction
to one concise guide rule. Keep private observations in private artifacts.

## Implemented plan for this pass

- [x] Map current source ownership and existing interfaces.
- [x] Make command effects and evidence limits discoverable.
- [x] Route agent work here and retain detailed product plans at their owners.

Acceptance: owner paths and document links resolve; current instructions
match inspected source; catalog hashes bind this context to the reviewed
bytes. This is documentation/control navigation acceptance. Product runtime
checks retain their own scope and are not certified by this pass.

## Project decisions

Choose a demo before setting up tooling. make test-offline checks the credential-free examples; make test-sdk-offline checks actual SDK stdio behavior under `uv run --locked` (pyproject.toml, uv.lock). These are separate from paid model-backed chat, deployment and Inspector acceptance. Trace lesson to demo script to dependency declaration to protocol test. Record demo path, environment/dependency identity and handshake/tool-call outcome with a working-demo claim. Prefer the two offline gates when changing deterministic examples, and run only the relevant model-backed scenario when attended credentials and spend are part of the task. Promote repeated protocol mistakes into a demo fixture rather than adding more setup prose.
