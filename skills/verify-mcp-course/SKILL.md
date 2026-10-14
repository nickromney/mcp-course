---
name: verify-mcp-course
description: Verify the course's pinned MCP SDK through local stdio handshakes and tool calls.
---

# Verify the MCP course SDK path

Run `make verify` from this repository. It invokes the documented `make test-sdk-offline`
acceptance target, which runs `tests/test_sdk_stdio.py` under `uv run --locked`. The suite
starts copied course servers as local stdio child processes, initializes the actual pinned MCP
SDK client, checks registered tool schemas, calls tools, and checks their results and file
effects. One test exercises the link checker with HTTP forbidden; the other exercises the
published calculator implementation. The checks use no model provider or API key.

The run uses the repository's existing `.venv` with uv syncing disabled, plus a run-specific
HOME and uv cache under `$VERIFY_BASE_DIR/$VERIFY_RUN_ID/state`. The SDK test uses its own
temporary fixture directories. Cleanup removes only the run-specific state. Captured test output
and source revision/status remain at `$VERIFY_EVIDENCE_ROOT/$VERIFY_RUN_ID/evidence`; defaults
are under `$TMPDIR/verify-kit/mcp-course` and `$TMPDIR/verify-evidence/mcp-course`.

Use `make verify-dry-run` to preview the cycle and `make verify-test` for Bash 3.2 shellcheck and
the shared contract suite. This proves local SDK registration and stdio tool behavior. It does
not run model-backed demos or prove cloud hosting.
