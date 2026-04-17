#!/usr/bin/env bash
# hammerin-allowlist-check.sh
# PreToolUse hook per Edit/Write/MultiEdit/NotebookEdit.
# Blocca scritture fuori dall'allowlist dell'agente attivo nel workorder
# (Hammerin'Claude v4 Capocantiere — livello 1 enforcement).
#
# Ciclo di vita:
#   - Nessun workorder attivo → allow (comportamento normale)
#   - Workorder attivo senza active_agent → allow + WARN in log
#   - Workorder + active_agent → check allowlist/denylist, blocca se violato
#
# Toggle:
#   HAMMERIN_ENFORCE=0 → disabilita tutto (passa sempre)
#
# Exit code:
#   0 = permetti
#   1 = blocca (stderr mostra motivo)

set -uo pipefail

STATE_DIR="/home/webportal/.hammerin-state"
LOG_FILE="${STATE_DIR}/enforcement.log"
ENFORCE="${HAMMERIN_ENFORCE:-1}"

log() {
  printf '[%s] %s\n' "$(date -Iseconds)" "$1" >> "$LOG_FILE" 2>/dev/null || true
}

# Toggle off esplicito
if [ "$ENFORCE" = "0" ]; then
  log "ENFORCE=0 — skip check"
  exit 0
fi

# Legge payload JSON da stdin (protocollo hook Claude Code)
PAYLOAD=$(cat)

# Estrae file_path (Edit/Write/MultiEdit usano file_path; NotebookEdit notebook_path)
FILE_PATH=$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
  log "no file_path in payload — allow"
  exit 0
fi

# Whitelist — path sempre permessi (infrastruttura, memoria, lock file)
ALWAYS_ALLOW=(
  "/root/.claude/projects/*/memory/*"
  "/root/.claude/CLAUDE.md"
  "/root/.claude/settings.json"
  "/root/.claude/settings.local.json"
  "/root/.claude/keybindings.json"
  "/home/webportal/.hammerin-state/*"
  "/root/.claude/skills/hammerin-claude/*"
  "/root/.claude/hooks/*"
  "/tmp/*"
  "*.lock"
  "*/node_modules/*"
)

for pattern in "${ALWAYS_ALLOW[@]}"; do
  case "$FILE_PATH" in
    $pattern)
      log "WHITELIST ($pattern): $FILE_PATH"
      exit 0
      ;;
  esac
done

# Cerca workorder attivo (unico file -workorder.json nel state dir)
WORKORDER=$(ls "${STATE_DIR}"/*-workorder.json 2>/dev/null | head -1 || true)

if [ -z "$WORKORDER" ]; then
  log "no workorder — allow: $FILE_PATH"
  exit 0
fi

# Validità JSON
if ! jq empty "$WORKORDER" 2>/dev/null; then
  log "WARN: workorder $WORKORDER invalid JSON — allow: $FILE_PATH"
  exit 0
fi

ACTIVE_AGENT=$(jq -r '.active_agent // empty' "$WORKORDER")

if [ -z "$ACTIVE_AGENT" ]; then
  log "WARN: no active_agent in $WORKORDER — allow: $FILE_PATH"
  exit 0
fi

ALLOWLIST=$(jq -r --arg a "$ACTIVE_AGENT" '.blocchi[$a].files_allowlist[]? // empty' "$WORKORDER")
DENYLIST=$(jq -r --arg a "$ACTIVE_AGENT" '.blocchi[$a].files_denylist[]? // empty' "$WORKORDER")

if [ -z "$ALLOWLIST" ]; then
  log "WARN: no allowlist for agent '$ACTIVE_AGENT' — allow: $FILE_PATH"
  exit 0
fi

# Calcola match allowlist (glob)
IN_ALLOW=0
MATCHED_ALLOW=""
while IFS= read -r allowed; do
  [ -z "$allowed" ] && continue
  case "$FILE_PATH" in
    $allowed)
      IN_ALLOW=1
      MATCHED_ALLOW="$allowed"
      break
      ;;
  esac
done <<< "$ALLOWLIST"

# Calcola match denylist (glob) — ma solo pattern diversi da "*" se allowlist matcha
# Logica: la denylist serve come eccezione specifica dentro l'allowlist
IN_DENY=0
MATCHED_DENY=""
while IFS= read -r denied; do
  [ -z "$denied" ] && continue
  # Se il pattern denylist è "*" lo ignoriamo quando allowlist matcha (l'allowlist è
  # già un filtro positivo). Se denylist è specifica, ha precedenza.
  if [ "$denied" = "*" ] && [ $IN_ALLOW -eq 1 ]; then
    continue
  fi
  case "$FILE_PATH" in
    $denied)
      IN_DENY=1
      MATCHED_DENY="$denied"
      break
      ;;
  esac
done <<< "$DENYLIST"

# Decisione finale:
#   in allowlist & in denylist specifica  → BLOCK (denylist più stretta)
#   in allowlist & !in denylist           → ALLOW
#   !in allowlist                         → BLOCK

if [ $IN_ALLOW -eq 1 ] && [ $IN_DENY -eq 0 ]; then
  log "ALLOW agent=$ACTIVE_AGENT ($MATCHED_ALLOW): $FILE_PATH"
  exit 0
fi

if [ $IN_ALLOW -eq 1 ] && [ $IN_DENY -eq 1 ]; then
  log "BLOCK agent=$ACTIVE_AGENT denylist($MATCHED_DENY): $FILE_PATH"
  echo "[Hammerin'Claude] BLOCCO: '$FILE_PATH' è in denylist specifica dell'agente '$ACTIVE_AGENT' (pattern: $MATCHED_DENY)." >&2
  echo "  Per disabilitare: export HAMMERIN_ENFORCE=0" >&2
  exit 1
fi

# !IN_ALLOW
log "BLOCK agent=$ACTIVE_AGENT not-in-allowlist: $FILE_PATH"
echo "[Hammerin'Claude] BLOCCO: '$FILE_PATH' NON è nell'allowlist dell'agente '$ACTIVE_AGENT'." >&2
echo "  Allowlist consentita:" >&2
printf '%s\n' "$ALLOWLIST" | sed 's/^/    - /' >&2
echo "  Workorder: $WORKORDER" >&2
echo "  Per disabilitare: export HAMMERIN_ENFORCE=0" >&2
exit 1
