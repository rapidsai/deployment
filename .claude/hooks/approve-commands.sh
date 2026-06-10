#!/bin/bash

# This hook automatically approves known-good commands
# Hook receives tool call details via stdin as JSON
#
# Any command containing one of these patterns is approved.

APPROVED_PATTERNS=(
  'ls'
  'find'
  'playwright-cli'
  'uv run make'
)

# Read the tool call data
input=$(cat)

# PreToolUse input uses tool_name and tool_input (see https://code.claude.com/docs/en/hooks)
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
command=$(echo "$input" | jq -r '.tool_input.command // empty')

if [[ "$tool_name" != "Bash" ]]; then
  exit 10
fi

for pattern in "${APPROVED_PATTERNS[@]}"; do
  if [[ "$command" == *"$pattern"* ]]; then
    reason="Command matches approved pattern: $pattern"
    jq -n \
      --arg reason "$reason" \
      '{ hookSpecificOutput: { hookEventName: "PreToolUse", permissionDecision: "allow", permissionDecisionReason: $reason } }'
    exit 0
  fi
done

# Exit 10 means "no decision" - defer to normal approval flow
exit 10
