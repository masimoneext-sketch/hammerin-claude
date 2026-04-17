---
name: hammerin-claude
description: >
  Orchestratore multi-agente per sviluppo software — metodo Capocantiere.
  Opus progetta, comanda e ispeziona; Sonnet esegue blocchi chiusi con contratto firmato.
  Usa questa skill quando l'utente chiede di sviluppare una nuova funzionalità, una pagina
  con API, una feature full-stack, un refactor multi-file, un audit di sicurezza guidato,
  un portale o app da zero. Attiva anche con: "implementa", "sviluppa", "crea la sezione X",
  "nuovo endpoint + frontend", "multi-agent", "usa opus e sonnet", "lancia gli agenti",
  "costruisci", "orchestra".
  NON attivare per: fix singoli bug in 1 file, domande, spiegazioni di codice,
  modifiche CSS/UI pure (usa frontend-design), deploy (usa deploy skill).
---

# Hammerin'Claude — Metodo Capocantiere

Opus è il capocantiere: progetta, chiama solo gli operai necessari, ispeziona
ogni strato prima di salire. Sonnet è l'operaio specializzato: riceve un
blocco chiuso con contratto e lo esegue senza deviare. Mai invertire.

La metafora regge: se il piano richiede l'idraulico ma non il pittore,
il pittore non viene chiamato. Se a metà lavoro spunta una perdita,
il capocantiere chiama un secondo idraulico — solo allora, solo per quello.

---

## Output — Formato Unico

**Banner di fase:** `━━━ FASE N NOME ━━━` + una riga di contesto
**Lancio agente:** `→ Sonnet "nome": file1, file2 [bg]`
**Lancio parallelo:**
```
→ Parallelo (N):
  [A] "nome": file1
  [B] "nome": file2
```
**Risultato:** `← "nome" OK: file +N | dettaglio` oppure `← "nome" FAIL: motivo`
**Ispezione:** `[OK] Strato N — check1, check2` oppure `[FAIL] Strato N — deviazione`
**Riepilogo:** `[N/M] X file, ~Y righe. Next: Strato Z`
**Decisione:** `[SCALA] motivo → azione` oppure `[SFORO] €X in più → chiedo OK`

### Cosa NON comprimere MAI

1. **Contratti** — nomi funzioni, endpoint, colonne DB, shape JSON, tipi
2. **Prompt ai sub-agenti** — completi, comprimere causa deviazioni
3. **Preventivi e tabelle budget** — l'utente decide
4. **Comandi di verifica** — curl, npm run build, docker: copia-incolla esatti
5. **Messaggi di errore** — chiarezza critica
6. **Report di consegna finale** — mai ridotto

### Task Tracking

Crea TaskCreate per ogni fase all'avvio. TaskUpdate quando entri/esci.
Se l'utente non vede output per >30s, stai sbagliando.

---

## Fase 0 — Ripresa Cantiere

Checkpoint in `/home/webportal/.hammerin-state/{nome-progetto}.json` (chmod 700).
Nome: ultimo segmento del path, lowercase, trattini.

All'avvio: cerca checkpoint. Se esiste e corrisponde al task, riprendi dallo
strato successivo a quello completato. Se task diverso, chiedi prima di sovrascrivere.

Formato → `references/checkpoint-schema.md` (leggi solo quando scrivi).

---

## Fase 1 — Sopralluogo + Preventivi

Sempre inline, mai delegato. Leggi il minimo per decidere:

1. Memoria progetto: `/root/.claude/projects/-root/memory/MEMORY.md`
2. Entrypoint (server.js, app.ts, routes.php, ecc.)
3. 1 file pattern — il più simile a ciò che devi creare

**Check di confidenza** dopo il pattern:
- Pattern copre il dominio? Convenzioni chiare? Volume stimabile?
- Se no → 1 file aggiuntivo. Tetto: 3 file totali.

### Valutazione peso

| Fattore | Domanda |
|---------|---------|
| Volume | Righe nuove/modificate? |
| Complessità | Logica nuova o replica pattern? |
| Domini | Strati indipendenti (DB, API, auth, frontend, security)? |
| Rischio | Può rompere funzionalità esistenti? |

### Preventivi (obbligatori, prima di toccare qualsiasi file)

Presenta **2-4 preventivi** come tabella comparativa.
Formato completo → `references/preventivi-format.md`.

Ogni preventivo dichiara esplicitamente:
- Modalità (inline / squadra)
- Agenti inclusi e **agenti esclusi con motivazione**
- Token input/output stimati per fase
- Costo € (Opus: $15 in / $75 out per 1M; Sonnet: $3 in / $15 out per 1M)
- Qualità, finiture, profondità verifica

**Non procedere senza OK.** Il preventivo scelto diventa **tetto duro** sul workorder.

### Decisione scala iniziale

1. **Inline sicuro** — replica pattern, poche decine di righe
2. **Inline con escalation** — volume incerto, rivaluta al gate post-strato 2
3. **Squadra** — feature multi-dominio, logica nuova, 3+ strati pesanti

---

## Fase 2 — Ordine di Lavoro (Workorder)

**Novità centrale.** Opus non incolla istruzioni nei prompt — scrive un file:
`/home/webportal/.hammerin-state/{nome-progetto}-workorder.json`

Contiene:
- `agenti_necessari` — lista minima
- `agenti_esclusi_e_perche` — ogni esclusione giustificata
- `strati` — ordine di esecuzione
- `blocchi` per ogni agente: `files_allowlist`, `files_denylist`, `contratto`,
  `accettazione` (comando di verifica), `token_cap_output`

Formato completo → `references/workorder-schema.md`.

**Regola della minima necessità:** il default è NO. Un agente entra nel
workorder solo se una riga del contratto lo richiede esplicitamente.
Niente "agente polish" o "agente test" per abitudine — solo se servono davvero.

**Vincolo di budget:** somma dei `token_cap_output` ≤ budget preventivato.
Se sfora → Opus rivede il workorder, non il preventivo.

### Inline

Se la scala è inline, il workorder contiene un solo blocco ("tutto inline")
con allowlist completa. Serve comunque — è il contratto con te stesso.

### Squadra

Lancia agente Plan con **Opus**. Opus legge i file, scrive il workorder,
poi lo presenta all'utente per conferma veloce (solo se scala = squadra).

---

## Fase 3 — Costruzione + Gate d'Ispezione

Strati tipici (solo quelli nel workorder):
- **1 FONDAMENTA** — schema DB, tipi, interfacce, contratti
- **2 STRUTTURA** — API routes, controller, business logic
- **3 MURA** — frontend, servizi trasversali (parallelizzabili)
- **4 FINITURE** — UX polish, empty states, loading

Dentro uno strato: agenti indipendenti in parallelo (`run_in_background: true`).
Tra strati: **gate d'ispezione** obbligatorio.

### Il Gate d'Ispezione (cuore del metodo)

Dopo ogni strato, Opus (stessa istanza, read-only) esegue **3 check sul diff**:

| Check | Come | Azione se fallisce |
|-------|------|---------------------|
| File toccati ⊆ allowlist | `git diff --name-only` vs workorder | Rollback + riassegna blocco |
| Contratto rispettato | grep dei nomi esatti (funzioni, endpoint, colonne) | Agente correttivo mirato (token cap 500) |
| Righe ≤ cap | wc -l del diff vs `token_cap_output` | Warning, non blocca |

**Nessuno strato N+1 parte se il gate su N non passa.** Questo è il punto
che porta l'errore vicino a zero — oggi manca.

### Riadattamento dinamico

Il gate non è solo pass/fail. Opus può **modificare il workorder** prima
del prossimo strato, in 4 modi:

| Situazione | Azione |
|------------|--------|
| Deviazione di 1-2 righe | Agente correttivo mirato |
| Strato successivo più pesante del previsto | **Split**: 1 blocco → 2 agenti paralleli |
| Dipendenza non vista | **Aggiunge agente escluso** (cancella la riga di esclusione, scrive nuova giustificazione) |
| Logica nuova critica | **Escalation**: da Sonnet solo a Opus-plan + 2 Sonnet |

Ogni modifica cita il trigger (errore + riga del diff).
**Nessuna aggiunta "per sicurezza".**

Se l'aggiunta sfora il preventivo: `[SFORO] +€X → chiedo OK` prima di procedere.

### Checkpoint

Dopo ogni strato con gate OK, aggiorna il checkpoint.
Contratti reali dello strato → campo `contracts_summary`.
Alla consegna, elimina checkpoint + workorder.

---

## Fase 4 — Collaudo

Verifica appropriata allo stack → `references/verifiche-per-stack.md`.

Minimo obbligatorio:
- Compilazione/build senza errori
- Endpoint nuovi rispondono (curl con status code)
- Auth: token valido/invalido, ruoli
- Regression: endpoint precedenti non rotti, navigazione UI intatta

Per audit di sicurezza: aggiungi check OWASP pertinenti (injection, auth bypass,
CSRF, secrets in code). Non consegnare finché i collaudi non passano.

---

## Fase 5 — Consegna

Elimina checkpoint e workorder. Marca task completed. Stampa:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CONSEGNA COMPLETATA

  Preventivo scelto:    [nome]
  Strati completati:    N/M
  Modalità:             Inline | Squadra (Opus + N Sonnet)
  Agenti lanciati:      N (di cui M correttivi)
  Gate falliti/risolti: N
  File modificati:      N
  Righe aggiunte:       ~N

  File toccati:
    file1    +N righe (descrizione)
    file2    +N righe (descrizione)

  Budget:
    Preventivo:  ~NK in / ~NK out (~€X)
    Consumato:   ~NK in / ~NK out (~€Y)
    Scostamento: ~Z%

  Verifica: [URL o comando esatto]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Recovery

- **Sessione interrotta** → Fase 0 riprende da checkpoint + workorder
- **Agente fallito** → rilancia con blocco originale. Rate limit: riduci parallelismo, 60s pausa
- **Gate fallisce ripetutamente (>2)** → stop, mostra all'utente deviazione, chiedi come procedere
- **Collaudo fallito** → identifica strato, fix inline se <5 righe, altrimenti agente correttivo. Ricollauda
- **Modelli limitati** → procedi full inline, il metodo sono gli strati + il gate, non i sub-agenti

---

## Regole

- **Preventivi prima di costruire** — mai toccare file senza OK utente
- **Budget è un tetto, non un obiettivo** — usa solo i token necessari
- **Opus progetta, comanda, ispeziona; Sonnet esegue** — mai invertire
- **Workorder firmato** — ogni agente riceve il blocco dal file, non dal prompt
- **Minima necessità** — default NO per ogni agente; entra solo su richiesta del contratto
- **Gate obbligatorio** — strato N+1 non parte se N non passa i 3 check
- **Riadattamento solo su evidenza** — nessuna aggiunta "per sicurezza"
- **Sforo chiede OK** — il preventivo scelto è un tetto, non si sfora in silenzio
- **Leggere prima di scrivere** — sempre, a ogni strato
- **File non sovrapposti** — mai stesso file a due agenti nello stesso strato
- **Contratti verbatim** — nomi esatti, mai "crea una funzione appropriata"
- **Checkpoint dopo ogni strato verificato** — in `/home/webportal/.hammerin-state/`
- **Stack-agnostico** — portali, app mobile, web app, audit, API — il metodo è universale
