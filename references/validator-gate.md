# Validator Gate — enforcement livello 2

Script Python standalone che esegue i 3 check del Gate d'Ispezione in modo
deterministico, senza fare affidamento sulla disciplina di Opus.

**Path:** `/root/.claude/skills/hammerin-claude/hooks/hammerin_gate.py`

**Relazione con il livello 1:**
- Livello 1 (PreToolUse hook bash): blocca *in tempo reale* scritture fuori allowlist
- Livello 2 (questo validator): verifica *a strato completato* allowlist + contratto + righe

I due livelli sono complementari: il livello 1 previene; il livello 2 convalida.

---

## Invocazione

```bash
python3 /root/.claude/skills/hammerin-claude/hooks/hammerin_gate.py \
    --cwd /home/webportal/www/progetto-x
```

**Argomenti:**

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--workorder` | autodiscover | path esplicito al workorder JSON |
| `--cwd` | cwd corrente | repo git del progetto (deve contenere `.git`) |
| `--base-ref` | `HEAD` | base git per `git diff` |
| `--agent` | `active_agent` dal workorder | override manuale del blocco da validare |
| `--skip` | `""` | csv di check da saltare: `allowlist,contract,lines` |

**Exit code:**
- `0` → pass (o nessun workorder attivo → allow)
- `1` → fail di un check bloccante (allowlist o contratto)
- `2` → errore di configurazione (workorder malformato, cwd non git)

---

## I 3 check

### Check 1 — Allowlist (BLOCCANTE)

Per ogni file modificato (`git diff --name-only HEAD` + untracked tramite
`git ls-files --others --exclude-standard`):

1. Deve matchare almeno un pattern di `files_allowlist` (glob tramite `fnmatch`)
2. Se matcha anche un pattern di `files_denylist` diverso da `*`, fail

Stessa logica del hook bash livello 1, così i due enforcement sono coerenti.

### Check 2 — Contratto (BLOCCANTE)

Estrae gli **identificatori tecnici** dal testo del campo `contratto` del blocco
tramite 4 pattern regex:

| Pattern | Esempio matchato |
|---------|------------------|
| `/[A-Za-z_][\w/{}-]*` | `/api/assets/{id}/log` |
| `\b[a-z_][a-z0-9_]*_[a-z0-9_]+\b` | `assets_log`, `user_id` |
| `\b[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]+)+\b` | `AssetsLogController` |
| `\b[a-z][a-z0-9]+(?:[A-Z][A-Za-z0-9]+)+\b` | `createAssetLog` |

**Perché solo questi pattern:** evitano falsi positivi su parole italiane
comuni nel contratto (Tabella, Risposta, Endpoint…) che non sono nomi di
codice. Una singola parola PascalCase come `Tabella` non viene catturata.

Ogni token estratto deve apparire almeno una volta nel `git diff HEAD`
(ricerca case-sensitive su stringa). Se manca anche solo un token, fail con
stderr che lista i mancanti.

### Check 3 — Righe (WARNING, non blocca)

Conta le righe aggiunte (`^+` nel diff, escluso header `+++`) e confronta con
`token_cap_output × 0.5`. Se supera, emette warning su stderr ma ritorna 0.

Ratio 0.5 è un'approssimazione: in codice strutturato servono ~2 token per
riga. Non è critico avere precisione esatta — il check serve a catturare
blow-up evidenti (10x il cap), non fluttuazioni del 20%.

---

## Integrazione nella skill

La skill chiama il gate dopo ogni strato, in Fase 3:

```bash
set -e
python3 /root/.claude/skills/hammerin-claude/hooks/hammerin_gate.py \
    --cwd "$PROJECT_PATH"
```

Con `set -e`, l'exit 1 blocca naturalmente la fase successiva. Opus legge
l'output, decide se rollback / agente correttivo / escalation, poi riprova.

Se si vuole silenziare il check righe (es: rewrite ampi previsti):
```bash
python3 ... --skip lines
```

---

## Differenze chiave rispetto al livello 1

| Aspetto | Livello 1 (hook bash) | Livello 2 (gate Python) |
|---------|----------------------|-------------------------|
| Quando scatta | Prima di ogni tool Edit/Write | Dopo strato completato |
| Granularità | Per singolo file | Per intero diff |
| Check | Solo allowlist/denylist | Allowlist + contratto + righe |
| Contratti | Non controllati | Verificati con grep regex |
| Trigger | Automatico (runtime Claude Code) | Esplicito (skill invoca) |

---

## Casi d'uso tipici

**Scenario A — pass pulito:**
```
━━━ GATE agent='schema' files=1 workorder=asset-portal-workorder.json ━━━
[OK] Check 1 allowlist — 1 file in allowlist
[OK] Check 2 contratto — tutti i 4 identificatori presenti
[OK] Check 3 righe — +32 / cap 750
```

**Scenario B — allowlist violata:**
```
[FAIL] Check 1 allowlist:
  - file fuori allowlist: app/Models/Asset.php
  allowlist consentita: ['database/migrations/2026_04_17_assets_log.php']
```
Exit 1 → Opus decide: rollback + riassegnazione blocco.

**Scenario C — contratto incompleto:**
```
[FAIL] Check 2 contratto — 2/5 identificatori mancanti nel diff:
  - assets_log
  - asset_id
```
Exit 1 → Opus lancia agente correttivo con cap 500 token.

**Scenario D — righe oltre cap (non blocca):**
```
[OK] Check 1 allowlist — 3 file in allowlist
[OK] Check 2 contratto — tutti i 7 identificatori presenti
[WARN] Check 3 righe — +2140 aggiunte > cap 1250 (token_cap=2500)
```
Exit 0 → procedi ma segnala lo scostamento nel riepilogo finale.

---

## Limiti noti

- Nessun parsing AST — il check contratto è grep testuale. Un identificatore
  dentro un commento conta come "presente". Accettabile: il gate certifica
  *sintassi*, non *semantica*. La verifica funzionale sta in Fase 4.
- Ratio token→righe è approssimativo. Per stime precise servirebbe tokenizer
  Anthropic, overkill per un warning.
- Non verifica l'ordine degli strati — la skill è responsabile di invocare
  il gate dopo ogni strato, non salta.
