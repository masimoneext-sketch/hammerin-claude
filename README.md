# Hammerin'Claude

**Orchestratore multi-agente per sviluppo software — metodo Capocantiere.**

Opus progetta, comanda e ispeziona. Sonnet esegue blocchi chiusi con contratto firmato.
Mai invertire. Ogni operaio viene chiamato solo quando serve, solo per ciò che serve.

---

## L'idea

Quando un agente AI deve sviluppare una feature complessa — database, API, auth,
frontend — di solito sceglie tra due strade: fare tutto inline o lanciare tanti
sub-agenti in parallelo. Entrambe hanno un costo: l'inline produce codice confuso
su task grandi, i sub-agenti sprecano token su task piccoli.

Hammerin'Claude risolve il problema con un'idea presa dal cantiere edile:
**non decidi in anticipo quanti operai servono. Parti leggero, scala solo se la
realtà te lo chiede.** E soprattutto: **il capocantiere (Opus) sa chi chiamare
e chi non chiamare.** Se il piano richiede l'idraulico ma non il pittore,
il pittore non entra in cantiere.

> Nome ispirato a *Hammerin' Harry* (Irem, 1990) — un operaio armato di mazza che
> costruisce e combatte. Hammerin'Claude fa lo stesso: costruisce software a strati,
> con la tenacia dell'operaio e l'intelligenza dell'architetto.

---

## Cosa è cambiato nella v4

La v4 introduce il **pattern Capocantiere**. Rispetto alla v3:

| Concetto v3 | Concetto v4 (Capocantiere) |
|-------------|-----------------------------|
| Piano Opus passato via prompt | **Workorder** scritto su file JSON |
| Sonnet riceve istruzioni nel prompt | Sonnet legge il proprio blocco dal file |
| Verifica solo in Fase 4 | **Gate d'ispezione** tra ogni strato |
| Agenti decisi a spanne | **Regola minima necessità**: default NO, ogni esclusione giustificata |
| Nessun confronto preventivo/consumo | Sforamento preventivo chiede OK utente |

SKILL.md è passato da 245 a **265 righe** (sotto il tetto di 300). La logica
nuova è compensata dall'estrazione di 3 reference files caricati on-demand.

---

## Metodo Capocantiere — gli strati

| Strato | Cantiere edile | Software |
|--------|----------------|----------|
| 1 Fondamenta | Scavo + cemento | Schema DB, tipi, interfacce, contratti |
| 2 Struttura | Pilastri portanti | API routes, controller, business logic |
| 3 Mura | Tamponamenti + divisori | Frontend, componenti UI |
| 4 Impianti | Elettrico + idraulico | Auth, logging, validazione |
| 5 Finiture | Intonaco + pittura | Empty states, loading, polish UX |

**Principio:** Opus progetta e ispeziona, Sonnet costruisce. Mai invertire.

---

## Le 5 fasi

### Fase 0 — Ripresa Cantiere
Checkpoint in `/home/webportal/.hammerin-state/{progetto}.json`.
Se esiste, riprendi dallo strato successivo. Schema in `references/checkpoint-schema.md`.

### Fase 1 — Sopralluogo + Preventivi
Legge memoria progetto, entrypoint, 1 file pattern (max 3 file totali).
Presenta **2-4 preventivi** come tabella comparativa con costo in €,
agenti inclusi, **agenti esclusi con motivazione**.
Formato in `references/preventivi-format.md`. Non procede senza OK utente.

### Fase 2 — Ordine di Lavoro (Workorder)
Opus scrive il workorder in `{progetto}-workorder.json` con:
- `agenti_necessari` (lista minima)
- `agenti_esclusi_e_perche` (ogni esclusione giustificata)
- per ogni agente: `files_allowlist`, `files_denylist`, `contratto`,
  `accettazione` (comando eseguibile), `token_cap_output`

Schema completo in `references/workorder-schema.md`.

### Fase 3 — Costruzione + Gate d'Ispezione
Strati sequenziali. Dentro uno strato: agenti paralleli (`run_in_background: true`).
Tra strati: **gate obbligatorio** con 3 check sul diff:
1. File toccati ⊆ allowlist?
2. Contratto rispettato (grep dei nomi esatti)?
3. Righe ≤ cap?

Se un gate fallisce, nessuno strato successivo parte. Opus può riadattare il
workorder (split, aggiunta agente escluso, escalation) — sempre su evidenza,
mai "per sicurezza". Sforo del preventivo chiede OK utente.

### Fase 4 — Collaudo
Verifica appropriata allo stack (build, curl, auth, regression).
Comandi precisi per Node/React/Laravel/Docker/Python/Expo in `references/verifiche-per-stack.md`.

### Fase 5 — Consegna
Elimina checkpoint + workorder. Report con preventivato vs consumato, scostamento,
file toccati, strati completati, gate falliti/risolti.

---

## Cosa è verificato vs cosa è istruito

**Principio di onestà:** la skill è un set di istruzioni che Claude legge e
prova a seguire. Non c'è un runtime esterno che forza il rispetto delle regole.
Qui sotto cosa significa in pratica:

### ✅ Reale — la skill può fare questo

- Lettura/scrittura file JSON (checkpoint, workorder)
- Lancio sub-agenti Opus/Sonnet tramite il tool Agent
- Esecuzione di `git diff`, `grep`, `wc -l` per il gate d'ispezione
- Presentazione tabella preventivi con attesa OK utente
- Esecuzione curl/npm run build/docker restart in Fase 4
- Task tracking con TaskCreate/TaskUpdate
- Ripresa cross-sessione via checkpoint su disco

### ⚠️ Istruito ma non enforced — dipende dalla disciplina di Claude

- **Token cap per agente** è un'istruzione nel workorder, non un kill switch
- **Gate blocca strato N+1** è una regola procedurale, non un controllo runtime
- **Allowlist/denylist file** è un vincolo testuale, non un filesystem permission
- **Regola minima necessità** è una policy, Claude deve scegliere di rispettarla
- **Riadattamento dinamico** è descritto come flusso, non come macchina a stati

### ❌ Non promesso

- Garanzia matematica di zero errori
- Rollback automatico (Claude deve farlo a mano con git)
- Validatore esterno che rifiuta output di un agente non-conforme
- Kill switch automatico al superamento del budget

Per avere *enforcement* vero servono strumenti fuori dalla skill: hooks Claude Code,
validator esterni, CI gates. Non sono in questa repo.

---

## Benchmark

La v3 aveva benchmark plan-only su 2 eval tasks con 100% pass rate e -19% token
overhead rispetto alla baseline. La v4 introduce il workorder e il gate
d'ispezione — **i benchmark sulla v4 non sono ancora stati eseguiti**.
Prima di dichiarare metriche, vanno scritti eval che testino:
1. Creazione workorder con agenti_esclusi_e_perche popolato
2. Gate d'ispezione che blocca quando l'allowlist è violata
3. Riadattamento dinamico con tracciatura del trigger

Finché non girano, assumere parità con v3 come floor minimo.

---

## Use case previsti

La skill è progettata per:
- **Portali web** (React + backend PHP/Node) — sezioni nuove, CRUD, auth
- **Web app** con database + API + frontend coordinati
- **App mobile** con backend dedicato (Expo + Node/Python)
- **Refactor multi-file** dove i contratti tra moduli contano
- **Audit di sicurezza guidato** (con check OWASP in Fase 4)
- **Migrazioni di stack** strato per strato

NON adatta per:
- Fix singoli bug in 1 file
- Modifiche CSS/UI pure (esiste `frontend-design`)
- Deploy (esiste `deploy`)
- Domande o spiegazioni di codice

---

## Installazione

```
~/.claude/skills/hammerin-claude/
├── SKILL.md                           # Skill core
├── README.md                          # Questo file
├── hooks/
│   └── hammerin-allowlist-check.sh    # Hook enforcement livello 1 (opzionale)
├── references/
│   ├── checkpoint-schema.md           # JSON checkpoint cross-sessione
│   ├── workorder-schema.md            # JSON ordine di lavoro
│   ├── preventivi-format.md           # Formato tabella preventivi
│   ├── verifiche-per-stack.md         # Comandi verifica per stack
│   └── enforcement-hook.md            # Documentazione hook livello 1
└── evals/
    └── evals.json                     # Eval v3 (da aggiornare per v4)
```

Auto-trigger su tutte le sessioni. Nessuna configurazione richiesta per la
skill base. L'enforcement hook è opzionale — vedi sotto.

### Enforcement livello 1 (opzionale)

Hook `PreToolUse` che **blocca fisicamente** scritture fuori dall'allowlist
dell'agente attivo nel workorder. Trasforma una regola della skill
(istruzione) in un vincolo runtime (comando rifiutato).

```bash
# 1. Copia lo script in ~/.claude/hooks/
mkdir -p ~/.claude/hooks
cp hooks/hammerin-allowlist-check.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/hammerin-allowlist-check.sh

# 2. Aggiungi il hook in ~/.claude/settings.json:
#   "hooks": {
#     "PreToolUse": [{
#       "matcher": "Edit|Write|MultiEdit|NotebookEdit",
#       "hooks": [{"type": "command",
#                  "command": "/root/.claude/hooks/hammerin-allowlist-check.sh"}]
#     }]
#   }

# 3. Assicurati che /home/webportal/.hammerin-state/ esista con chmod 700
mkdir -p /home/webportal/.hammerin-state && chmod 700 /home/webportal/.hammerin-state

# 4. Toggle d'emergenza (disabilita tutto):
export HAMMERIN_ENFORCE=0
```

Dettagli in `references/enforcement-hook.md`.

---

## Regole (le 12 del capocantiere)

1. Preventivi prima di costruire — mai toccare file senza OK utente
2. Budget è un tetto, non un obiettivo
3. Opus progetta/ispeziona, Sonnet esegue — mai invertire
4. Workorder firmato — ogni agente riceve il blocco dal file
5. Minima necessità — default NO, ogni esclusione giustificata
6. Gate obbligatorio — strato N+1 non parte se N non passa i 3 check
7. Riadattamento solo su evidenza — nessuna aggiunta per sicurezza
8. Sforo chiede OK — il preventivo scelto è un tetto
9. Leggere prima di scrivere — sempre, a ogni strato
10. File non sovrapposti — mai stesso file a due agenti nello stesso strato
11. Contratti verbatim — nomi esatti, mai "crea una funzione appropriata"
12. Checkpoint dopo ogni strato verificato

---

*Marco Simone — Aprile 2026. v4 Capocantiere.*
