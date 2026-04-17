# Enforcement Hook — Livello 1

Hook `PreToolUse` che blocca **fisicamente** le scritture Edit/Write/MultiEdit/NotebookEdit
quando il file target non è nella `files_allowlist` dell'agente attivo del workorder.

Non dipende dalla disciplina di Claude: è il runtime di Claude Code che esegue
lo script e rifiuta il tool call se lo script esce con exit code 1.

## Componenti

1. **Script:** `/root/.claude/hooks/hammerin-allowlist-check.sh` (eseguibile, ~140 righe)
2. **Settings:** voce `hooks.PreToolUse` in `/root/.claude/settings.json` con
   matcher `Edit|Write|MultiEdit|NotebookEdit`
3. **State:** `/home/webportal/.hammerin-state/` (chmod 700) contiene:
   - `{progetto}-workorder.json` — il workorder con campo `active_agent`
   - `{progetto}.json` — checkpoint (dalla v4 base)
   - `enforcement.log` — log eventi del hook

## Protocollo active_agent

Il hook legge `active_agent` dal workorder per sapere quale blocco sta scrivendo.

**La skill deve aggiornare `active_agent` prima e dopo ogni sub-agente:**

```bash
# Prima di lanciare Sonnet "schema"
jq '.active_agent = "schema"' workorder.json > tmp && mv tmp workorder.json

# Lancio del sub-agente
# ... Sonnet scrive file in allowlist di "schema" ...

# Al termine
jq '.active_agent = ""' workorder.json > tmp && mv tmp workorder.json
```

Se `active_agent` è vuoto o assente → il hook **permette tutto** con warning
nel log. Questo rende il hook retrocompatibile con workorder senza `active_agent`.

## Comportamento del hook

Ordine di valutazione:

1. `HAMMERIN_ENFORCE=0` → allow + log
2. Nessun `file_path` nel payload → allow
3. File in **ALWAYS_ALLOW** (whitelist infrastruttura) → allow
4. Nessun `*-workorder.json` nel state dir → allow
5. Workorder JSON invalido → allow + WARN
6. `active_agent` vuoto/assente → allow + WARN
7. Nessun allowlist per l'agente → allow + WARN
8. File in denylist del blocco → **BLOCK** (salvo override in allowlist)
9. File in allowlist del blocco → allow
10. File non in allowlist → **BLOCK**

## Whitelist infrastruttura (ALWAYS_ALLOW)

Path sempre permessi indipendentemente dal workorder:

- `/root/.claude/projects/*/memory/*` — memoria Claude
- `/root/.claude/CLAUDE.md` — istruzioni globali
- `/root/.claude/settings.json`, `settings.local.json`, `keybindings.json`
- `/home/webportal/.hammerin-state/*` — stato Hammerin'Claude stesso
- `/root/.claude/skills/hammerin-claude/*` — skill stessa
- `/root/.claude/hooks/*` — hook stessi
- `/tmp/*`
- `*.lock`
- `*/node_modules/*`

Modifica l'array `ALWAYS_ALLOW` nello script se servono altri path sempre permessi.

## Toggle

Per disabilitare temporaneamente (es. durante onboarding di un nuovo progetto):

```bash
export HAMMERIN_ENFORCE=0
# ... lavoro senza enforcement ...
unset HAMMERIN_ENFORCE  # riattiva
```

L'env var viene letta a ogni invocazione del hook, quindi il toggle è live.

## Log

File: `/home/webportal/.hammerin-state/enforcement.log`

Esempio di riga:
```
[2026-04-17T14:32:15+00:00] ALLOW agent=schema (database/migrations/*.php): database/migrations/2026_04_17_log.php
[2026-04-17T14:33:02+00:00] BLOCK agent=schema not-in-allowlist: app/frontend/src/App.tsx
```

Rotazione: manuale. Se cresce troppo:
```bash
mv /home/webportal/.hammerin-state/enforcement.log{,.old}
```

## Pattern matching

Lo script usa `case` bash con pattern **glob shell** (non regex):
- `*` matcha qualsiasi sequenza
- `?` matcha un carattere
- `[abc]` matcha un set

**Nel workorder usa glob bash nei path:**
```json
"files_allowlist": [
  "database/migrations/2026_04_17_*.php",
  "app/Http/Controllers/AssetsLogController.php"
]
```

## Errori comuni

**"BLOCK not-in-allowlist" su un file che dovrebbe passare**
→ Pattern nel workorder non matcha il file reale. Verifica con:
```bash
case "/path/reale/file.php" in database/migrations/*.php) echo OK ;; esac
```

**Tutto viene bloccato dopo attivazione**
→ Verifica che `active_agent` sia `""` quando non stai eseguendo un blocco.
Oppure `export HAMMERIN_ENFORCE=0` per uscita d'emergenza.

**Hook non si attiva**
→ Verifica `jq '.hooks.PreToolUse' /root/.claude/settings.json` e che lo
script sia eseguibile (`chmod +x`).

## Limiti noti (livello 1)

- Non controlla il contratto (nomi funzioni/endpoint) — solo allowlist file
- Non controlla il token cap — solo allowlist
- Non forza l'aggiornamento di `active_agent` — dipende dalla skill
- Non gestisce workorder multipli simultanei — prende il primo `*-workorder.json`

Per check contratto + token cap → livelli 2 e 3 (vedi memoria progetto).

## Disinstallazione

```bash
# Rimuovi PreToolUse da settings.json
# (manualmente via skill update-config o edit del JSON)

# Opzionale: rimuovi script
rm /root/.claude/hooks/hammerin-allowlist-check.sh

# Opzionale: pulizia stato
rm /home/webportal/.hammerin-state/enforcement.log
```
