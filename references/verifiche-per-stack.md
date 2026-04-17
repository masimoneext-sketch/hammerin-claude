# Verifiche per Stack — Fase 4 (Collaudo)

Comandi di verifica appropriati per ciascuno stack supportato.
Usa il set pertinente al progetto in questione.

## Node.js + Express

```bash
# Server riavviato
pm2 restart {nome-app} || node server.js &

# Endpoint rispondono
curl -s -o /dev/null -w "%{http_code}" http://localhost:{porta}/api/health
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:{porta}/api/{endpoint} | jq .

# Database (SQLite)
sqlite3 data.db ".tables"
sqlite3 data.db "SELECT count(*) FROM {tabella_nuova}"

# Log errori
tail -30 logs/error.log
pm2 logs {nome-app} --lines 30
```

## React / Vite

```bash
cd app/frontend
npm run build
# Deve finire senza errori TypeScript
# Verifica: dist/ generato, size ragionevole

# Dev server (per test manuale rapido)
npm run dev
# Apri http://localhost:5173, naviga alla sezione nuova
```

## Laravel 11 / PHP

```bash
# Migration applicata
php artisan migrate:status | grep {nome_migration}

# Test (se il progetto li ha)
php artisan test --filter {NomeTest}

# Endpoint
curl -s -H "Accept: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     http://localhost/api/{endpoint} | jq .

# Route registrata
php artisan route:list --path=api/{endpoint}
```

## Docker / Docker Compose

```bash
# Container up
docker compose ps | grep {servizio}

# Restart con volume montato
docker compose restart {servizio}

# Log
docker compose logs --tail=50 {servizio}

# HTTP dietro Traefik
curl -sI https://{dominio}/ | head -5
# Deve essere 200/301/302, mai 404/502/503
```

## React Native / Expo

```bash
# Build Android tramite GitHub Actions (non EAS)
# Dopo push su main, attendi fine build — non triggerare manualmente

# TypeScript check
cd {progetto}
npx tsc --noEmit

# Lint
npx expo-doctor
```

## Python / FastAPI

```bash
# Server up
curl -s http://localhost:8000/docs | grep -o "title" | head -1

# Endpoint
curl -s -X POST http://localhost:8000/api/{endpoint} \
     -H "Content-Type: application/json" \
     -d '{"key": "value"}' | jq .

# Pytest (se esiste)
pytest tests/test_{modulo}.py -v
```

---

## Check trasversali (sempre, ogni stack)

### Auth
```bash
# Senza token → 401
curl -s -o /dev/null -w "%{http_code}" http://localhost/api/{endpoint}
# Con token valido → 200
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" http://localhost/api/{endpoint}
# Con ruolo insufficiente → 403 (se endpoint protetto da role)
```

### Regression
- Endpoint esistenti pre-modifica: ancora 200
- Navigazione UI: menu, link, pagine precedenti caricano
- Login/logout: ancora funzionante

### Struttura del gate d'ispezione (Fase 3)

Non è collaudo ma è la verifica minima tra strati. Comandi rapidi:

```bash
# Check allowlist: file toccati = quelli nel workorder?
git diff --name-only HEAD~1 HEAD   # o dallo start del lavoro

# Check contratto: i nomi dichiarati esistono nel codice?
grep -rn "{nome_funzione_o_endpoint}" {dir_target}

# Check righe: entro cap?
git diff --stat HEAD~1 HEAD
```

---

## Audit di sicurezza — check OWASP pertinenti

Se il task è audit/review, aggiungi in Fase 4:

```bash
# Secret nel codice
grep -rIn -E "(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]" . \
     --include="*.{js,ts,php,py}" | grep -v node_modules

# SQL injection — concatenazioni sospette
grep -rn -E "(query|execute)\(.*\\\$|\\+.*req\\." --include="*.{js,ts,php}" .

# XSS — innerHTML / dangerouslySetInnerHTML
grep -rn "innerHTML\|dangerouslySetInnerHTML" app/frontend/src/

# CSRF — POST senza token
# (verifica framework-specifico)

# Upload file — estensioni validate?
grep -rn "file.*upload\|multer\|Storage::put" app/
```

---

## Soglia minima per consegnare

Fase 5 (Consegna) parte solo se:
- [ ] Build/compile senza errori
- [ ] Almeno 1 curl OK sugli endpoint nuovi
- [ ] Auth check passato (401 senza token, 200 con token)
- [ ] Regression check passato (endpoint/UI precedenti non rotti)

Se uno fallisce → torna a Fase 3 con agente correttivo. Non barare.
