#!/usr/bin/env bash
# shellcheck disable=SC2034 # VK_* settings are read by the sourced verify-lib.sh
set -euo pipefail

VK_SCRIPT="$0"
VK_APP="mcp-course"
VK_DESCRIPTION="Verify the pinned MCP SDK's real stdio tool registration and calls offline."
VK_DEFAULT_BASE_DIR="${TMPDIR:-/tmp}/verify-kit/mcp-course"
VK_DEFAULT_EVIDENCE_ROOT="${TMPDIR:-/tmp}/verify-evidence/mcp-course"
# shellcheck source=verify-lib.sh disable=SC1091
. "$(cd "$(dirname "$0")" && pwd)/verify-lib.sh"

vk_commands_help() {
  cat <<'HELP'
  launch                 create isolated run directories
  doctor                 check the locked SDK runtime is available
  sdk-offline            run the documented real stdio SDK acceptance suite
  cleanup                remove this run's state; evidence is kept
HELP
}
vk_sample_commands() { printf '%s\n' verify launch doctor sdk-offline cleanup; }
vk_paths() {
  STATE="$VK_BASE_DIR/$VK_RUN_ID/state"
  EVIDENCE="$VK_EVIDENCE_ROOT/$VK_RUN_ID/evidence"
}
vk_plan() {
  case "$1" in
    verify) vk_plan_line "run make test-sdk-offline against the existing locked .venv with sync disabled; assert two real SDK stdio acceptance tests pass; remove run state and keep evidence at $EVIDENCE" ;;
    launch) vk_plan_line "create isolated HOME and uv cache under $STATE; prepare $EVIDENCE" ;;
    doctor) vk_plan_line "check the documented locked SDK test and its existing .venv Python runtime" ;;
    sdk-offline) vk_plan_line "run make test-sdk-offline with HTTP/model credentials unavailable; capture output in $EVIDENCE/sdk-offline.log" ;;
    cleanup) vk_plan_line "remove only $STATE and keep $EVIDENCE" ;;
    *) vk_unknown_command ;;
  esac
}
cmd_launch() {
  mkdir -p "$STATE/home" "$STATE/uv-cache" "$EVIDENCE"
  vk_mark_current
  printf '%s\n' "$VK_RUN_ID" > "$STATE/run-id"
  vk_record_revision "$EVIDENCE/revision.txt"
  vk_say "ready run=$VK_RUN_ID state=$STATE evidence=$EVIDENCE"
}
cmd_doctor() {
  if [ ! -d "$STATE" ] || [ ! -f "$STATE/run-id" ] || [ "$(cat "$STATE/run-id")" != "$VK_RUN_ID" ]; then
    vk_fail "no isolated state for run $VK_RUN_ID; launch first"
    return 1
  fi
  if [ ! -x "$VK_ROOT/.venv/bin/python" ] || [ ! -f "$VK_ROOT/uv.lock" ] || [ ! -f "$VK_ROOT/tests/test_sdk_stdio.py" ]; then
    vk_fail "locked SDK test prerequisites are missing (run 'uv sync --locked' from the repository root)"
    return 1
  fi
  vk_say "OK locked SDK test prerequisites exist"
}
cmd_sdk_offline() {
  local log="$EVIDENCE/sdk-offline.log"
  local uv_path
  if command -v mise >/dev/null 2>&1; then
    uv_path="$(mise which uv 2>/dev/null || true)"
  else
    uv_path="$(command -v uv 2>/dev/null || true)"
  fi
  if [ -z "$uv_path" ] || [ ! -x "$uv_path" ]; then
    vk_fail "could not resolve an executable uv (install uv or make it available through mise)"
    return 1
  fi
  (
    cd "$VK_ROOT"
    unset ANTHROPIC_API_KEY OPENAI_API_KEY
    PATH="$(dirname "$uv_path"):$PATH" HOME="$STATE/home" UV_CACHE_DIR="$STATE/uv-cache" \
      UV_PROJECT_ENVIRONMENT="$VK_ROOT/.venv" UV_NO_SYNC=1 \
      PYTHONDONTWRITEBYTECODE=1 make test-sdk-offline
  ) > "$log" 2>&1 || {
    tail -n 20 "$log"
    return 1
  }
  cat "$log"
}
cmd_cleanup() {
  rm -rf "${STATE:?}"
  rmdir "$VK_BASE_DIR/$VK_RUN_ID" 2>/dev/null || true
  vk_clear_current
  vk_say "removed state for run=$VK_RUN_ID; evidence kept at $EVIDENCE"
}
vk_verify_recipes() {
  cmd_sdk_offline
  vk_expect_contains "$EVIDENCE/sdk-offline.log" "Ran 2 tests"
  vk_expect_contains "$EVIDENCE/sdk-offline.log" "OK"
  vk_expect_contains "$EVIDENCE/sdk-offline.log" "test_registered_tools_in_local_child"
  vk_expect_contains "$EVIDENCE/sdk-offline.log" "test_published_calculator_registered_with_sdk"
}
vk_dispatch() {
  local cmd="$1"; shift
  case "$cmd" in
    launch) cmd_launch ;;
    doctor) cmd_doctor ;;
    sdk-offline) cmd_sdk_offline ;;
    cleanup) cmd_cleanup ;;
    *) vk_unknown_command ;;
  esac
}
vk_main "$@"
