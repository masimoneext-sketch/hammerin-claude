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

Costruisci software come si costruisce un palazzo: dal terreno al collaudo.
Ogni strato si appoggia su quello precedente. Non si posano le mura senza le fondamenta.

Il principio fondamentale: **Opus ragiona, Sonnet scrive**. Mai invertire.

---

## Fase 0 — Ripresa Cantiere (checkpoint cross-sessione)

Prima di qualsiasi sopralluogo, controlla se esiste un cantiere interrotto.

### All'avvio di ogni task, SEMPRE:

1. Cerca il file `.hammerin-checkpoint.json` nella **root del progetto** su cui stai lavorando
2. Se **non esiste** → procedi normalmente con Fase 1
3. Se **esiste** → leggi il checkpoint e riprendi da dove ti eri fermato

### Logica di ripresa

Quando trovi un checkpoint:

1. **Leggi il file** `.hammerin-checkpoint.json`
2. **Verifica che il task corrisponda** — il campo `task_description` deve essere coerente con cio' che l'utente sta chiedendo ora. Se l'utente chiede un task diverso, ignora il checkpoint e parti da zero (ma non cancellarlo — chiedi all'utente se vuole abbandonare il cantiere precedente).
3. **Verifica i file completati** — fai un check rapido che i file elencati in `files_modified` esistano e contengano le modifiche attese (leggi le prime righe, non tutto). Questo conferma che il lavoro precedente non e' stato annullato.
4. **Riprendi dallo strato successivo** — se l'ultimo strato completato e' il 2, parti dallo strato 3. Non rileggere i file degli strati completati se non serve.
5. **Comunica all'utente**:

> **Cantiere interrotto trovato** — task: "{task_description}", ultimo strato completato: {current_layer} ({layer_name}). File verificati OK. Riprendo dallo strato {next_layer}.

> **Cantiere interrotto trovato** — task: "{task_description}", ma i file risultano modificati/assenti. Riparto dal sopralluogo.

### Formato del file checkpoint

Il file `.hammerin-checkpoint.json` ha questa struttura:

```json
{
  "version": 1,
  "project_path": "/path/to/project/",
  "task_description": "Descrizione breve del task richiesto dall'utente",
  "started_at": "2026-04-11T10:30:00Z",
  "updated_at": "2026-04-11T11:15:00Z",
  "mode": "inline|squadra",
  "current_layer": 2,
  "layers": {
    "1": {
      "name": "FONDAMENTA",
      "status": "completato",
      "files_modified": ["src/database.js"],
      "contracts_summary": "tabella turni creata con colonne: id, name, date, shift_type, user_id",
      "verification": "OK — tabella creata, query funzionano"
    },
    "2": {
      "name": "STRUTTURA PORTANTE",
      "status": "completato",
      "files_modified": ["src/routes/turni.js"],
      "contracts_summary": "GET/POST/PUT/DELETE /api/turni — shape: {id, name, date, shift_type}",
      "verification": "OK — curl 200 su tutti gli endpoint"
    },
    "3": {
      "name": "MURA E IMPIANTI",
      "status": "da_fare",
      "files_to_modify": ["public/js/app.js", "public/index.html"],
      "contracts_summary": "",
      "verification": null
    }
  },
  "plan_summary": "Breve sintesi del piano — strati previsti, modalita', decisioni chiave",
  "decisions": [
    "Inline dopo sopralluogo — ~80 righe, 2 domini",
    "Confermato inline dopo strato 2 — volume come previsto"
  ],
  "next_action": "Costruire strato 3 — frontend turni in public/js/app.js"
}
```

### Cosa salvare nel checkpoint (e cosa no)

**Salva:**
- Stato di avanzamento (strato corrente, status per strato)
- File modificati per strato (per verifica rapida alla ripresa)
- Sintesi contratti (non il codice completo — solo nomi endpoint, tabelle, shape)
- Piano sintetico e decisioni prese
- Prossima azione da eseguire

**NON salvare:**
- Contenuto dei file (e' gia' su disco)
- Output completo delle verifiche (solo OK/FAIL)
- Contesto conversazione (non e' riproducibile)

### Regole checkpoint

- **Scrivi il checkpoint dopo ogni strato completato con verifica OK** — non prima
- **Aggiorna `updated_at` ad ogni scrittura** per tracciare la freschezza
- **Il checkpoint e' del progetto, non della sessione** — salvalo nella root del progetto, non in /tmp
- **Un solo checkpoint per progetto alla volta** — se ne esiste uno vecchio, sovrascrivilo solo se lo stai aggiornando per lo stesso task
- **Aggiungi `.hammerin-checkpoint.json` al `.gitignore` del progetto** se non e' gia' presente

---

## Fase 1 — Sopralluogo del Terreno

Prima di posare qualsiasi cosa, studia il terreno. Questa fase e' SEMPRE inline, mai delegata.

### Sopralluogo adattivo (sempre)

Leggi il minimo indispensabile per capire il peso del task, ma adatta la profondita'
al terreno che trovi:

1. Leggi la memoria del progetto: `/root/.claude/projects/-root/memory/MEMORY.md`
2. Leggi l'**entrypoint** del progetto (server.js, app.ts, ecc.) per capire la struttura
3. Leggi **1 file pattern** — il file piu' simile a cio' che devi creare/modificare (es. una route CRUD esistente, un componente simile).

**Check di confidenza** — dopo il file pattern, chiediti:
- Il pattern copre il dominio del task? (es. se devi fare auth e hai letto una route CRUD, no)
- Le convenzioni sono chiare? (naming, struttura file, pattern di import)
- Riesci a stimare il volume con ragionevole sicurezza?

Se la risposta a una di queste e' **no**, leggi **1 file aggiuntivo** in un dominio diverso.
Tetto massimo: **3 file** nel sopralluogo (entrypoint + 2 pattern). Se dopo 3 file non hai
abbastanza contesto, il codebase e' eterogeneo — segnalalo nella valutazione e parti con
"inline con possibile escalation" per ridurre il rischio di stima sbagliata.

NON leggere tutti i file coinvolti in questa fase. Il sopralluogo serve solo a decidere
la strategia. I file dettagliati li leggerai quando lavori (inline) o li fara' leggere Opus
ai Sonnet (squadra).

### Valutazione economica

Stima il **peso reale** del lavoro — non contare i file, pesa le modifiche:

| Fattore | Domanda |
|---------|---------|
| **Volume** | Quante righe di codice nuovo/modificato servono in totale? |
| **Complessita'** | Logica nuova o replica di pattern esistenti? |
| **Domini** | Quanti strati indipendenti? (DB, API, auth, frontend, infra) |
| **Rischio** | Puo' rompere funzionalita' esistenti? |

### Decisione: scala dinamica

Non devi decidere tutto subito. La regola e': **inizia sempre inline, scala se serve**.

Il sopralluogo ti da' una prima impressione del peso del lavoro. Usala per scegliere
come partire, ma resta pronto a cambiare strategia durante la costruzione.

#### 3 modalita' di partenza

**1. Inline sicuro** — il lavoro e' chiaramente leggero:
- Replica di pattern esistenti, poche decine di righe
- Anche cross-dominio (backend + frontend), ma volume basso
- Parti e finisci da solo. Nessun agente.

**2. Inline con possibile escalation** — non sei sicuro:
- Il lavoro sembra gestibile ma potrebbe crescere
- Parti inline dalle fondamenta (schema DB, interfacce base)
- Dopo lo strato 2 (struttura portante), rivaluta: se il volume restante e' sostanziale, chiama la squadra per gli strati superiori
- Questo ti costa solo il tempo delle fondamenta — che avresti dovuto fare comunque

**3. Squadra diretta** — il lavoro e' chiaramente pesante:
- Feature completa con DB + CRUD + auth + frontend + import/export
- Logica nuova, non replica di pattern
- Piu' di 3 domini con lavoro sostanziale in ognuno
- Chiama Opus per il progetto e lancia la squadra Sonnet

#### Come rivalutare durante la costruzione

Dopo ogni strato completato, chiediti:
- "Quanto lavoro resta? Lo finisco piu' veloce da solo o con agenti?"
- "Gli strati restanti sono indipendenti tra loro?" (se si', parallelizzare ha senso)
- "Ho scoperto complessita' che non vedevo dal sopralluogo?"

Se la risposta cambia, cambia strategia:
- **Inline → Squadra**: hai completato fondamenta e struttura inline, ma il frontend e' piu' grosso del previsto. Lancia Opus per progettare gli strati restanti, poi agenti Sonnet.
- **Squadra → Inline**: hai lanciato Opus e il piano mostra che restano solo 2 blocchi piccoli. Annulla la squadra, finisci da solo.

La scala dinamica non e' un fallimento — e' adattamento intelligente. Come un cantiere che
inizia con una squadra piccola e chiama rinforzi solo quando scopre che il terreno e' piu' duro.

#### Comunica la decisione all'utente

> **Sopralluogo completato** — ~30 righe, replica pattern. Costruisco inline.

> **Sopralluogo completato** — volume incerto, parto inline dalle fondamenta. Rivaluto dopo lo strato 2.

> **Sopralluogo completato** — ~300 righe, 4 domini. Chiamo la squadra, 3 strati di costruzione.

> **Sopralluogo completato** — codebase eterogeneo (letto 3 file, pattern non uniformi). Parto inline con escalation — riduco il rischio di stima sbagliata.

---

## Fase 2 — Progetto e Fondamenta

Le fondamenta sono cio' su cui tutto si regge: schema DB, tipi, interfacce, contratti.

### Se lavori inline

Ora leggi i file che devi modificare (nel sopralluogo hai letto solo l'entrypoint e 1 pattern).
Procedi strato per strato: fondamenta prima, verifica, poi sali.

### Se chiami la squadra

Lancia un agente `Plan` con modello **opus**. Opus leggera' i file dettagliati di cui ha bisogno —
non serve che tu li abbia gia' letti tutti nel sopralluogo. Passa a Opus: il task, lo stack,
le convenzioni osservate nel file pattern, e la stima del peso.

Il piano Opus deve definire:

#### Strati di costruzione

Ogni strato corrisponde a una fase edilizia. Non tutti i task hanno tutti gli strati —
l'architetto include solo quelli necessari.

```
Strato 1 — FONDAMENTA (schema DB, tipi, interfacce)
  Chi: Agente A
  File: src/database.js
  Contratto: tabella X con colonne esatte, funzioni di accesso
  Verifica: la tabella esiste, le query funzionano

Strato 2 — STRUTTURA PORTANTE (API routes, controller, business logic)
  Chi: Agente B
  Dipende da: Strato 1
  File: src/routes/foo.js
  Contratto: endpoint con shape risposta esatte
  Verifica: curl ritorna i dati attesi

Strato 3 — MURA E IMPIANTI (frontend + servizi trasversali)
  Chi: Agente C (frontend) + Agente D (auth/logging) — in parallelo
  Dipende da: Strato 2
  File C: public/js/app.js, public/index.html
  File D: src/auth.js (se serve modificare)
  Verifica: la UI si carica, i permessi funzionano

Strato 4 — FINITURE (UX polish, empty states, feedback visivo)
  Chi: inline o Agente E
  Dipende da: Strato 3
  Verifica: UI completa e responsive
```

#### Per ogni agente nel piano

Ogni blocco deve essere **autocontenuto** — l'agente Sonnet riceve SOLO il suo blocco.
Deve contenere:

- **File assegnati** e file da NON toccare
- **Nomi esatti** di funzioni, route, colonne DB — niente di generico
- **Pattern da replicare** con riferimento a codice esistente (file + riga)
- **Contratto esposto** — cosa questo strato offre a quelli sopra
- **Contratti consumati** — cosa si aspetta dagli strati sotto (per strato 2+)

#### Parallelismo dentro gli strati

Dentro uno stesso strato, agenti indipendenti possono lavorare in parallelo.
Tra strati con dipendenze, si procede in sequenza e si verifica prima di salire.

Esempio: se strato 3 ha frontend e auth che non si toccano, partono insieme.
Ma strato 3 non parte finche' strato 2 non e' verificato.

---

## Fase 3 — Costruzione

### Lavoro inline (con checkpoint di escalation)

Procedi strato per strato dall'alto in basso:

1. **Fondamenta** — Schema DB, migration. Verifica: tabella creata, query OK.
   **→ SALVA CHECKPOINT** (strato 1 completato, contratti esposti, file modificati)
2. **Struttura** — Route, controller, logic. Verifica: curl endpoint.
   **→ SALVA CHECKPOINT** (strato 2 completato)
   **→ CHECKPOINT DECISIONALE: rivaluta.** Quanto lavoro resta? Se gli strati restanti sono piu' grossi
   del previsto, questo e' il momento di chiamare la squadra. Le fondamenta e la struttura
   sono gia' pronte — lancia Opus per progettare solo gli strati superiori, poi agenti Sonnet.
3. **Mura** — Frontend HTML/JS. Verifica: UI si carica.
   **→ SALVA CHECKPOINT** (strato 3 completato)
4. **Impianti** — Auth, logging, validazione. Verifica: permessi funzionano.
   **→ SALVA CHECKPOINT** (strato 4 completato)
5. **Finiture** — Empty states, loading, feedback. Verifica: UX completa.
   (nessun checkpoint — si passa direttamente al collaudo e alla consegna)

Ad ogni strato, **verifica prima di salire**. Se le fondamenta sono rotte, non costruire sopra.

**Procedura salvataggio checkpoint dopo ogni strato:**
1. Aggiorna il file `.hammerin-checkpoint.json` nella root del progetto
2. Imposta lo strato appena completato come `"status": "completato"` con `verification` e `files_modified`
3. Aggiorna `current_layer`, `updated_at`, `next_action`
4. Se il prossimo strato ha file gia' noti, compilali in `files_to_modify`

Se scali alla squadra dal checkpoint decisionale, comunica all'utente:
> **Escalation** — fondamenta e struttura completate inline. Il volume restante e' ~200 righe
> su 3 domini indipendenti. Chiamo la squadra per mura + impianti + finiture.

### Lavoro con squadra

Lancia gli agenti Sonnet strato per strato.

**Lancio parallelo dentro lo strato:**
Tutti gli agenti dello stesso strato partono **nello stesso messaggio** con `run_in_background: true`.

**Ogni agente Sonnet riceve:**
1. Il suo blocco di istruzioni dal piano Opus
2. I contratti degli strati gia' completati (reali, non teorici)
3. Istruzione: **leggere i file esistenti prima di modificarli**
4. Istruzione: **non toccare file non assegnati**

**Tra uno strato e l'altro:**
1. Verifica che i contratti esposti siano rispettati
2. Se un agente ha deviato, correggi prima di salire
3. **SALVA CHECKPOINT** — aggiorna `.hammerin-checkpoint.json` con strato completato, file modificati, contratti reali
4. Passa allo strato successivo con i contratti aggiornati dal codice reale

Questo e' il vantaggio della costruzione a strati: ogni piano si appoggia su fondamenta verificate.

---

## Fase 4 — Collaudo

Il palazzo e' costruito. Ora lo collaudi prima di consegnarlo.

### Verifica strutturale (test funzionali)

Esegui la verifica appropriata al progetto:
- **Node.js**: riavvia il server, curl ogni endpoint, verifica risposte
- **React/Vite**: `npm run build`, verifica compilazione senza errori
- **Laravel**: `php artisan test` o curl API
- **Docker**: `docker compose restart`, verifica HTTP 200
- **React Native**: build o start senza errori

### Verifica impianti (servizi trasversali)

- Auth: token valido accede, token invalido no, ruoli rispettati
- Logging: le azioni vengono registrate nell'audit log
- Validazione: input malformato ritorna errore chiaro

### Verifica interni (UI)

- La nuova funzionalita' e' visibile e funzionante
- Empty states per liste vuote
- Loading states durante le richieste
- I permessi per ruolo nascondono/mostrano correttamente

### Regression check

- Le funzionalita' esistenti non sono rotte
- Gli endpoint precedenti rispondono come prima
- La navigazione tra sezioni funziona

**Non consegnare finche' tutti i collaudi non passano.**

---

## Fase 5 — Consegna

### Pulizia checkpoint

Il palazzo e' completato e collaudato — rimuovi il cantiere:
1. **Elimina** il file `.hammerin-checkpoint.json` dalla root del progetto
2. Se avevi aggiunto `.hammerin-checkpoint.json` al `.gitignore`, lascialo — non da fastidio e previene commit accidentali futuri

### Rapporto di consegna

Comunica all'utente cosa hai costruito:
- Quali strati sono stati completati
- Quanti agenti sono stati usati (se squadra) o che hai lavorato inline
- Se il lavoro e' stato ripreso da un checkpoint precedente, menzionalo
- Eventuali scelte fatte durante la costruzione
- Come verificare di persona (URL, comando, sezione da aprire)

---

## Recovery

### Sessione interrotta (rate limit, context esaurito, crash)

Questo e' lo scenario piu' comune e il motivo per cui esistono i checkpoint.

1. **Non succede nulla di grave** — il checkpoint su disco ha tutto lo stato necessario
2. Nella prossima sessione, la Fase 0 rileva il checkpoint e riprende automaticamente
3. L'utente non deve ricordarsi a che punto era — il checkpoint lo sa

**Cosa si recupera dal checkpoint:**
- Strato corrente e stato di ogni strato precedente
- File modificati (per verifica rapida che il lavoro sia integro)
- Piano sintetico e contratti (per non dover riprogettare)
- Prossima azione da eseguire

**Cosa si perde (inevitabilmente):**
- Contesto conversazione (file letti in cache, discussione con l'utente)
- Output dettagliato delle verifiche precedenti

**Costo della ripresa:** ~1 lettura del checkpoint + verifica rapida dei file completati.
Molto meno del sopralluogo completo da zero.

### Agente fallito

1. Non riprogettare il palazzo da zero
2. Rilancia lo stesso agente con il **blocco originale** + cosa era gia' fatto
3. Se rate limit: vedi sezione **Degradazione Gracile** — riduci parallelismo e riprova

### Contratto violato

1. Identifica la deviazione specifica
2. Correggi inline se banale, o lancia agente correttivo con istruzioni precise
3. Non riscrivere lo strato — ripara solo il punto rotto

### Collaudo fallito

1. Leggi l'errore e identifica quale strato ha il problema
2. Correggi inline se e' un fix sotto 5 righe
3. Rilancia agente correttivo se serve piu' lavoro
4. Ricollada dopo ogni fix

---

## Degradazione Gracile

Il metodo funziona al meglio con Opus (progetto) + Sonnet (costruzione), ma deve funzionare
anche quando le condizioni non sono ideali. Non fallire — adattati.

### Opus non disponibile (per agente Plan)

Se non riesci a lanciare un agente Plan con Opus (rate limit, errore, non disponibile):
- **Non bloccarti.** Tu stai gia' girando come Opus nel thread principale.
- Fai la progettazione inline: leggi i file necessari, scrivi il piano degli strati con i
  contratti esatti, poi lancia i Sonnet direttamente con quel piano.
- Il risultato e' equivalente — perdi solo la separazione del contesto di pianificazione.

### Sonnet rate-limited

Se un agente Sonnet fallisce per rate limit:
1. **Riduci il parallelismo**: se avevi 3 agenti nello stesso strato, rilanciane 2 alla volta
2. **Aspetta e riprova**: attendi 60 secondi, poi rilancia l'agente fallito con lo stesso blocco
3. **Non cambiare il piano**: il rate limit e' temporaneo, il piano resta valido

### Entrambi i modelli limitati

Se sia Opus che Sonnet sono limitati:
- Passa a **modalita' full inline** — lavori tu da solo, strato per strato, con i checkpoint
- Il metodo Costruttore funziona anche senza sub-agenti: gli strati, le verifiche, e i
  contratti sono gli stessi. Cambia solo chi esegue il lavoro.
- Comunica all'utente: "Modelli sub-agente limitati, procedo inline con il metodo a strati."

Il principio: il metodo e' la struttura a strati con verifica, non la presenza di sub-agenti.
I sub-agenti sono un'ottimizzazione di velocita', non un requisito.

---

## Regole

- **Opus progetta, Sonnet costruisce** — mai invertire
- **Leggere prima di scrivere** — sempre, a ogni strato
- **File non sovrapposti** — mai assegnare lo stesso file a due agenti nello stesso strato
- **Contratti da Opus** — nomi funzioni, endpoint, tipi li decide l'architetto
- **Verificare prima di salire** — non costruire strato 2 senza aver collaudato strato 1
- **Salvare checkpoint dopo ogni strato verificato** — il lavoro sopravvive alle interruzioni
- **Controllare checkpoint all'avvio** — Fase 0 prima di Fase 1, sempre
- **Pulire checkpoint alla consegna** — cantiere finito = checkpoint eliminato
- **Niente generico** — nomi esatti, non "crea una funzione appropriata"
- **Decisione economica** — se il costo degli agenti supera il costo del lavoro, fai inline
- **Stack-agnostico** — funziona con qualsiasi stack: React, Node.js, Laravel, React Native, Python
