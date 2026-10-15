#!/usr/bin/env bats

setup() {
  SKILL_DIR="$(cd "$BATS_TEST_DIRNAME/.." && pwd)"
  SCRIPT="$SKILL_DIR/scripts/control.sh"
  export VERIFY_BASE_DIR="$BATS_TEST_TMPDIR/base"
  export VERIFY_EVIDENCE_ROOT="$BATS_TEST_TMPDIR/evidence"
  export VERIFY_RUN_ID="doctor-prereq-run"
}

@test "doctor names the locked dependency setup when the venv is missing" {
  if [ -x "$(git -C "$SKILL_DIR" rev-parse --show-toplevel)/.venv/bin/python" ]; then
    skip "a prepared .venv exists, so the missing-venv diagnostic cannot be exercised here"
  fi
  run /bin/bash "$SCRIPT" --execute launch
  [ "$status" -eq 0 ]
  run /bin/bash "$SCRIPT" --execute doctor
  [ "$status" -ne 0 ]
  [[ "$output" == *"uv sync --locked"* ]]
  run /bin/bash "$SCRIPT" --execute cleanup
  [ "$status" -eq 0 ]
}

@test "sdk-offline uses the uv binary resolved from mise under isolated HOME" {
  local fake_bin="$BATS_TEST_TMPDIR/fake-bin"
  local uv_bin="$BATS_TEST_TMPDIR/real-uv"
  mkdir -p "$fake_bin" "$uv_bin"
  cat > "$fake_bin/mise" <<'SH'
#!/bin/sh
[ "$1" = "which" ] && [ "$2" = "uv" ] || exit 1
printf '%s\n' "$FAKE_UV_PATH"
SH
  cat > "$uv_bin/uv" <<'SH'
#!/bin/sh
printf '%s\n' "$HOME" > "$UV_CALL_RECORD"
printf '%s\n' "$*" >> "$UV_CALL_RECORD"
SH
  chmod +x "$fake_bin/mise" "$uv_bin/uv"
  export FAKE_UV_PATH="$uv_bin/uv"
  export UV_CALL_RECORD="$BATS_TEST_TMPDIR/uv-call"
  export PATH="$fake_bin:$PATH"

  run /bin/bash "$SCRIPT" --execute launch
  [ "$status" -eq 0 ]
  run /bin/bash "$SCRIPT" --execute sdk-offline
  [ "$status" -eq 0 ]
  [ "$(sed -n '1p' "$UV_CALL_RECORD")" = "$VERIFY_BASE_DIR/$VERIFY_RUN_ID/state/home" ]
  [[ "$(sed -n '2p' "$UV_CALL_RECORD")" == "run --locked python -m unittest discover -s tests -p test_sdk_stdio.py -v" ]]
  run /bin/bash "$SCRIPT" --execute cleanup
  [ "$status" -eq 0 ]
}
