---
name: hammerin-claude
description: >
  Orchestratore intelligente multi-agente per sviluppo software — metodo Costruttore.
  Usa questa skill SEMPRE quando l'utente chiede di sviluppare una nuova funzionalità,
  aggiungere una sezione, fare un refactor, implementare una feature, o qualsiasi task
  di sviluppo che richiede pianificazione.
  Attiva anche quando l'utente dice "aggiungi una feature", "crea la sezione X", "implementa",
  "sviluppa", "refactor", "nuova pagina con API", "aggiungi endpoint e frontend",
  "multi-agent", "usa opus e sonnet", "lancia gli agenti", "costruisci".
  NON attivare per: fix singoli bug in 1 file, domande, spiegazioni di codice, modifiche CSS/UI pure
  (usa frontend-design), deploy (usa deploy skill).
---

# Hammerin'Claude — Metodo Costruttore

Costruisci software come un palazzo: fondamenta verificate prima di salire.
Opus ragiona, Sonnet scrive. Mai invertire.

---

## Output — Formato Unico

Un solo formato per tutta la comunicazione. Compatto, leggibile, zero spreco.

**Banner di fase:**
```
━━━ FASE N NOME ━━━
→ progetto | stack
```

**Lancio agente:**
```
→ Sonnet "nome task": file1.js, file2.js [background]
```

Lancio parallelo:
```
→ Parallelo (N):
  [A] "nome": file1.js
  [B] "nome": file2.js
```

**Risultato agente:**
```
← "nome" OK: file1.js +85, file2.js +12 | dettaglio
← "nome" FAIL: motivo → azione correttiva
```

**Verifica:** `[OK] Strato N — dettaglio` oppure `[FAIL] Strato N — errore`

**Riepilogo:** `[N/M] X file, ~Y righe. Next: Strato Z`

**Decisione:** `[SCALA] motivo → azione`

### Cosa NON comprimere MAI

Questi elementi restano verbatim, completi, senza riduzione:
1. **Contratti** — nomi funzioni, endpoint, colonne DB, shape JSON, tipi
2. **Prompt ai sub-agenti** — istruzioni complete, comprimere causa errori
3. **Preventivi e tabelle budget** — l'utente decide come spendere
4. **Comandi di verifica** — curl, npm run build, docker compose: copia-incolla esatti
5. **Messaggi di errore** — chiarezza critica quando qualcosa va storto
6. **Report di consegna finale** — documento completo, mai ridotto

### Task Tracking

Crea TaskCreate per ogni fase all'avvio. Aggiorna con TaskUpdate (in_progress/completed).
Se l'utente non vede output per piu' di 30 secondi, stai sbagliando.

---

## Fase 0 — Ripresa Cantiere

Tutti i checkpoint sono in **`/home/webportal/.hammerin-state/{nome-progetto}.json`** (chmod 700).
Convenzione nome: ultimo segmento del path, lowercase, trattini.

All'avvio: cerca il checkpoint. Se esiste e corrisponde al task, verifica file completati e riprendi.
Se task diverso, chiedi all'utente prima di sovrascrivere.

Per il formato del checkpoint → leggi `references/checkpoint-schema.md` quando devi scriverne uno.

---

## Fase 1 — Sopralluogo

Sempre inline, mai delegato. Leggi il minimo per decidere la strategia:

1. Memoria progetto: `/root/.claude/projects/-root/memory/MEMORY.md`
2. Entrypoint del progetto (server.js, app.ts, ecc.)
3. 1 file pattern — il piu' simile a cio' che devi creare/modificare

**Check di confidenza** dopo il file pattern:
- Pattern copre il dominio? Convenzioni chiare? Volume stimabile?
- Se no → leggi 1 file aggiuntivo. Tetto: 3 file totali nel sopralluogo.

### Valutazione peso

| Fattore | Domanda |
|---------|---------|
| Volume | Quante righe nuove/modificate? |
| Complessita' | Logica nuova o replica di pattern? |
| Domini | Quanti strati indipendenti? (DB, API, auth, frontend) |
| Rischio | Puo' rompere funzionalita' esistenti? |

### Preventivi

Dopo la valutazione, presenta **2-3 preventivi** come tabella comparativa con:
- Modalita', fasi, qualita', finiture, verifica
- Token input/output stimati per fase
- Costo in euro (Opus: $15/$75 per 1M; Sonnet: $3/$15 per 1M)
- Dettaglio per fase sotto la tabella

**Non procedere senza OK dell'utente.** Il budget scelto diventa il guardrail.
Se una fase costa meno del previsto, meglio — non gonfiare per riempire la quota.

### Decisione scala

Inizia sempre inline, scala se serve:

1. **Inline sicuro** — replica pattern, poche decine di righe, volume basso
2. **Inline con escalation** — parti dalle fondamenta, rivaluta dopo strato 2
3. **Squadra** — feature completa multi-dominio, logica nuova, 3+ domini pesanti

---

## Fase 2 — Progetto e Fondamenta

### Inline
Leggi i file da modificare (nel sopralluogo hai letto solo pattern). Procedi strato per strato.

### Squadra
Lancia agente Plan con **Opus**. Opus legge i file e produce il piano strati.

Il piano definisce **strati di costruzione** — solo quelli necessari:

**Strato 1 FONDAMENTA** — schema DB, tipi, interfacce
**Strato 2 STRUTTURA** — API routes, controller, business logic
**Strato 3 MURA** — frontend, servizi trasversali (parallelizzabili)
**Strato 4 FINITURE** — UX polish, empty states, loading

Per ogni agente nel piano: file assegnati, file da NON toccare, nomi esatti (funzioni, route, colonne), pattern da replicare con file+riga, contratto esposto e consumato.

Dentro uno strato: agenti indipendenti in parallelo. Tra strati: sequenza con verifica.

---

## Fase 3 — Costruzione

### Inline (con checkpoint)

Procedi strato per strato:
1. **Fondamenta** → verifica → salva checkpoint
2. **Struttura** → verifica → salva checkpoint → **CHECKPOINT DECISIONALE: rivaluta peso restante**
3. **Mura** → verifica → salva checkpoint
4. **Impianti** → verifica → salva checkpoint
5. **Finiture** → verifica → passa a collaudo

Se al checkpoint decisionale il volume restante e' piu' grosso del previsto, scala a squadra.
Le fondamenta e struttura sono pronte — lancia Opus solo per strati superiori.

### Squadra

Lancia agenti Sonnet strato per strato, tutti nello stesso messaggio con `run_in_background: true`.

Ogni agente Sonnet riceve:
1. Il suo blocco dal piano Opus
2. I contratti reali degli strati completati
3. Istruzione: leggere file prima di modificarli, non toccare file non assegnati

Tra strati: verifica contratti → correggi deviazioni → salva checkpoint → prossimo strato.

### Checkpoint

Salva in `/home/webportal/.hammerin-state/{nome-progetto}.json` dopo ogni strato verificato.
Per il formato → leggi `references/checkpoint-schema.md`.
Alla consegna, elimina il checkpoint.

---

## Fase 4 — Collaudo

Verifica appropriata al progetto:
- **Node.js**: riavvia server, curl ogni endpoint, verifica risposte
- **React/Vite**: `npm run build`, compilazione senza errori
- **Laravel**: `php artisan test` o curl API
- **Docker**: `docker compose restart`, HTTP 200

Poi: auth (token valido/invalido, ruoli), UI (funzionalita' visibile, empty states, permessi), regression (endpoint precedenti, navigazione).

Non consegnare finche' i collaudi non passano.

---

## Fase 5 — Consegna

Elimina il checkpoint. Marca tutti i task completed. Stampa report:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CONSEGNA COMPLETATA

  Preventivo scelto:    [nome]
  Strati completati:    N/M
  Modalita':            Inline | Squadra (Opus + N Sonnet)
  Agenti utilizzati:    N
  File modificati:      N
  Righe aggiunte:       ~N

  File toccati:
    file1.js    +N righe (descrizione)
    file2.js    +N righe (descrizione)

  Budget:
    Preventivo:  ~NK input / ~NK output (~€X)
    Consumato:   ~NK input / ~NK output (~€Y)
    Risparmio:   ~Z% sotto budget

  Verifica: [URL o comando]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Recovery

- **Sessione interrotta**: il checkpoint ha tutto, Fase 0 riprende automaticamente
- **Agente fallito**: rilancia con blocco originale. Se rate limit: riduci parallelismo, attendi 60s
- **Contratto violato**: correggi inline se banale, agente correttivo se serve
- **Collaudo fallito**: identifica strato, fix inline se <5 righe, altrimenti agente. Ricollauda dopo
- **Modelli limitati**: procedi full inline — il metodo e' la struttura a strati, non i sub-agenti

---

## Regole

- Preventivi prima di costruire — mai toccare file senza OK
- Budget e' un tetto, non un obiettivo
- Opus progetta, Sonnet costruisce — mai invertire
- Leggere prima di scrivere — sempre
- File non sovrapposti — mai stesso file a due agenti nello stesso strato
- Verificare prima di salire — strato N OK prima di strato N+1
- Checkpoint dopo ogni strato verificato — in `/home/webportal/.hammerin-state/`
- Niente generico — nomi esatti, non "crea una funzione appropriata"
- Stack-agnostico — funziona con qualsiasi stack
