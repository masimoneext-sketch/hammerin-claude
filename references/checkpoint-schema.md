# Checkpoint Schema v2

Salva in `/home/webportal/.hammerin-state/{nome-progetto}.json` dopo ogni strato verificato.
Convenzione nome: ultimo segmento del path del progetto, lowercase, trattini.
Esempio: `/home/webportal/www/sudo-support-it/` → `sudo-support-it.json`

```json
{
  "version": 2,
  "project_path": "/path/to/project/",
  "project_name": "nome-progetto",
  "task_description": "Breve descrizione del task",
  "started_at": "2026-04-16T10:00:00Z",
  "updated_at": "2026-04-16T11:00:00Z",
  "mode": "inline|squadra",
  "budget": {
    "preventivo_scelto": "B — BILANCIATO",
    "fasi": [
      { "nome": "Backend", "input_max": 80000, "output_max": 30000 },
      { "nome": "Frontend + Collaudo", "input_max": 70000, "output_max": 30000 }
    ],
    "totale_input_max": 150000,
    "totale_output_max": 60000
  },
  "current_layer": 2,
  "layers": {
    "1": {
      "name": "FONDAMENTA",
      "status": "completato",
      "files_modified": ["src/database.js"],
      "contracts_summary": "Sintesi contratti esposti — nomi esatti, shape, colonne",
      "verification": "OK"
    },
    "2": {
      "name": "STRUTTURA PORTANTE",
      "status": "da_fare",
      "files_to_modify": ["src/routes/foo.js"],
      "contracts_summary": "",
      "verification": null
    }
  },
  "plan_summary": "Sintesi piano — strati, modalita', decisioni chiave",
  "decisions": ["Decisione 1", "Decisione 2"],
  "next_action": "Azione specifica per il prossimo strato"
}
```

## Regole

- Scrivi solo dopo strato completato con verifica OK
- Aggiorna `updated_at` ad ogni scrittura
- Un solo checkpoint per progetto — sovrascrivilo per lo stesso task
- Alla consegna elimina il file
- NON salvare: contenuto file, output verifiche completo, contesto conversazione
- SALVA: stato avanzamento, file modificati per strato, sintesi contratti, piano, prossima azione
