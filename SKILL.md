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

## Fase 1 — Sopralluogo del Terreno

Prima di posare qualsiasi cosa, studia il terreno. Questa fase e' SEMPRE inline, mai delegata.

### Sopralluogo leggero (sempre)

Leggi il minimo indispensabile per capire il peso del task:

1. Leggi la memoria del progetto: `/root/.claude/projects/-root/memory/MEMORY.md`
2. Leggi l'**entrypoint** del progetto (server.js, app.ts, ecc.) per capire la struttura
3. Leggi **1 file pattern** — il file piu' simile a cio' che devi creare/modificare (es. una route CRUD esistente, un componente simile). Questo basta per capire le convenzioni.

NON leggere tutti i file coinvolti in questa fase. Il sopralluogo leggero serve solo a decidere
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
2. **Struttura** — Route, controller, logic. Verifica: curl endpoint.
   **→ CHECKPOINT: rivaluta.** Quanto lavoro resta? Se gli strati restanti sono piu' grossi
   del previsto, questo e' il momento di chiamare la squadra. Le fondamenta e la struttura
   sono gia' pronte — lancia Opus per progettare solo gli strati superiori, poi agenti Sonnet.
3. **Mura** — Frontend HTML/JS. Verifica: UI si carica.
4. **Impianti** — Auth, logging, validazione. Verifica: permessi funzionano.
5. **Finiture** — Empty states, loading, feedback. Verifica: UX completa.

Ad ogni strato, **verifica prima di salire**. Se le fondamenta sono rotte, non costruire sopra.

Se scali alla squadra dal checkpoint, comunica all'utente:
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
3. Passa allo strato successivo con i contratti aggiornati dal codice reale

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

Comunica all'utente cosa hai costruito:
- Quali strati sono stati completati
- Quanti agenti sono stati usati (se squadra) o che hai lavorato inline
- Eventuali scelte fatte durante la costruzione
- Come verificare di persona (URL, comando, sezione da aprire)

---

## Recovery

### Agente fallito

1. Non riprogettare il palazzo da zero
2. Rilancia lo stesso agente con il **blocco originale** + cosa era gia' fatto
3. Se rate limit: aspetta il reset e riprova — non bypassare il metodo

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

## Regole

- **Opus progetta, Sonnet costruisce** — mai invertire
- **Leggere prima di scrivere** — sempre, a ogni strato
- **File non sovrapposti** — mai assegnare lo stesso file a due agenti nello stesso strato
- **Contratti da Opus** — nomi funzioni, endpoint, tipi li decide l'architetto
- **Verificare prima di salire** — non costruire strato 2 senza aver collaudato strato 1
- **Niente generico** — nomi esatti, non "crea una funzione appropriata"
- **Decisione economica** — se il costo degli agenti supera il costo del lavoro, fai inline
- **Stack-agnostico** — funziona con qualsiasi stack: React, Node.js, Laravel, React Native, Python
