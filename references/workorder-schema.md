# Workorder Schema

Salva in `/home/webportal/.hammerin-state/{nome-progetto}-workorder.json`
dopo che Opus ha progettato gli strati e prima di lanciare Sonnet.

Convenzione nome: stesso `{nome-progetto}` del checkpoint.

```json
{
  "version": 1,
  "project_name": "nome-progetto",
  "task_description": "Breve descrizione del task",
  "preventivo_scelto": "B — BILANCIATO",
  "budget_cap": {
    "token_input_max": 150000,
    "token_output_max": 60000,
    "costo_max_eur": 1.50
  },
  "agenti_necessari": ["schema", "api", "frontend"],
  "agenti_esclusi_e_perche": {
    "auth": "ruoli già esistenti, nessun nuovo permesso",
    "import": "feature non prevede import dati",
    "test-unit": "pattern progetto non usa unit test"
  },
  "strati": [
    {
      "numero": 1,
      "nome": "FONDAMENTA",
      "blocchi": ["schema"]
    },
    {
      "numero": 2,
      "nome": "STRUTTURA",
      "blocchi": ["api"]
    },
    {
      "numero": 3,
      "nome": "MURA",
      "blocchi": ["frontend"]
    }
  ],
  "blocchi": {
    "schema": {
      "agente": "Sonnet",
      "files_allowlist": [
        "database/migrations/2026_04_17_assets_log.php"
      ],
      "files_denylist": ["*"],
      "contratto": "Tabella assets_log: id (bigint), asset_id (fk assets.id), action (enum: create,update,delete), user_id (fk users.id), ts (timestamp)",
      "pattern_da_replicare": "database/migrations/2026_03_15_assets.php righe 1-40",
      "accettazione": "php artisan migrate:status | grep 2026_04_17_assets_log",
      "token_cap_output": 1500
    },
    "api": {
      "agente": "Sonnet",
      "files_allowlist": [
        "app/Http/Controllers/AssetsLogController.php",
        "routes/api.php"
      ],
      "files_denylist": ["app/Models/*", "database/*"],
      "contratto": "GET /api/assets/{id}/log → 200 [{id, action, user, ts}]; POST fatto da observer, no endpoint",
      "pattern_da_replicare": "app/Http/Controllers/AssetsController.php metodo index",
      "accettazione": "curl -s -H 'Authorization: Bearer $TOKEN' http://localhost/api/assets/1/log | jq '.[0] | keys' → [action,id,ts,user]",
      "token_cap_output": 2500
    },
    "frontend": {
      "agente": "Sonnet",
      "files_allowlist": [
        "app/frontend/src/pages/AssetDetail.tsx",
        "app/frontend/src/api/assets.ts"
      ],
      "files_denylist": ["app/frontend/src/App.tsx", "app/frontend/src/router.tsx"],
      "contratto": "Tab 'Log' in AssetDetail chiama GET /api/assets/{id}/log, mostra tabella con colonne action/user/ts",
      "pattern_da_replicare": "AssetDetail.tsx tab 'Documenti' righe 120-180",
      "accettazione": "npm run build senza errori + grep 'assets/.*/log' src/api/assets.ts",
      "token_cap_output": 2000
    }
  },
  "gate_ispezione": {
    "check_allowlist": true,
    "check_contratto_grep": true,
    "check_righe_vs_cap": true
  },
  "created_at": "2026-04-17T10:00:00Z",
  "updated_at": "2026-04-17T10:00:00Z"
}
```

## Campi obbligatori

- `agenti_necessari` — lista minima, default vuoto
- `agenti_esclusi_e_perche` — **ogni esclusione con motivazione**, non omettibile
- `blocchi.{nome}.files_allowlist` — lista esatta, niente glob `*` se non per denylist
- `blocchi.{nome}.files_denylist` — almeno `["*"]` + whitelist eccezioni
- `blocchi.{nome}.contratto` — testo verbatim (nomi, endpoint, shape)
- `blocchi.{nome}.accettazione` — comando eseguibile, esatto
- `blocchi.{nome}.token_cap_output` — numero, somma ≤ budget

## Regola minima necessità

Il default per ogni agente è **NO**. Un agente entra in `agenti_necessari`
solo se una riga del contratto lo richiede esplicitamente.

Esempi di agenti NON da lanciare per abitudine:
- "test-unit" se il progetto non ha test esistenti
- "docs" se non c'è cartella docs/
- "migration-seed" se la tabella parte vuota
- "auth" se i ruoli esistenti bastano
- "polish-ux" se le finiture non sono nel preventivo scelto

## Riadattamento dinamico

Se il gate rileva che serve un agente escluso, Opus:
1. Cancella la riga da `agenti_esclusi_e_perche`
2. Aggiunge a `agenti_necessari` con nuova giustificazione
3. Aggiunge il blocco completo con allowlist/contratto/accettazione
4. Aggiorna `updated_at`
5. Se sfora `budget_cap` → chiede OK utente prima di lanciare

## Ciclo di vita

- Scritto in Fase 2 (Ordine di Lavoro)
- Letto da ogni Sonnet per il suo blocco (non dal prompt)
- Aggiornato dopo ogni gate (se riadattamento)
- Eliminato in Fase 5 (Consegna) insieme al checkpoint
