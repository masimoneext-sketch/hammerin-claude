# Preventivi — Formato Tabella

Presentato all'utente alla fine della Fase 1 (Sopralluogo), prima di scrivere
il workorder o toccare qualsiasi file.

## Formato tabella comparativa

```
PREVENTIVI — [nome task breve]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────────┬──────────┬───────────┬──────────┬──────────┬──────────┐
│ Preventivo       │ Modalità │ Agenti    │ Token in │ Token out│ Costo €  │
├──────────────────┼──────────┼───────────┼──────────┼──────────┼──────────┤
│ A — ECONOMICO    │ Inline   │ 0         │ ~40K     │ ~7K      │ ~€0.65   │
│ B — BILANCIATO   │ Squadra  │ 1+2       │ ~90K     │ ~18K     │ ~€1.50   │
│ C — COMPLETO     │ Squadra  │ 1+4       │ ~160K    │ ~35K     │ ~€3.20   │
└──────────────────┴──────────┴───────────┴──────────┴──────────┴──────────┘

Tariffe: Opus $15/$75 per 1M | Sonnet $3/$15 per 1M (1€ ≈ $1.08)
```

## Dettaglio per preventivo (obbligatorio sotto la tabella)

Ogni riga della tabella ha un blocco di dettaglio:

```
A — ECONOMICO (inline)
  Agenti inclusi:       nessuno (tutto inline sulla thread principale)
  Agenti esclusi:       — (non applicabile)
  Qualità:              standard — pattern esistenti replicati
  Finiture:             minime — empty states essenziali, no polish
  Verifica:             build + curl endpoint principali
  Strati:               1 Fondamenta, 2 Struttura, 3 Mura, 4 Finiture (light)
  Rischio:              basso per task ≤200 righe, alto oltre

B — BILANCIATO (squadra: 1 Opus plan + 2 Sonnet strati)
  Agenti inclusi:       schema, api, frontend
  Agenti esclusi:       auth (ruoli esistenti), import (non previsto)
  Qualità:              alta — contratti espliciti, gate tra strati
  Finiture:             loading states, empty states, error handling
  Verifica:             build + curl + auth check + regression
  Strati:               1 Fondamenta, 2 Struttura, 3 Mura, 4 Finiture
  Rischio:              basso — gate d'ispezione intercetta deviazioni

C — COMPLETO (squadra: 1 Opus plan + 4 Sonnet + 1 Sonnet test)
  Agenti inclusi:       schema, api, frontend, auth-review, test
  Agenti esclusi:       import (non previsto)
  Qualità:              molto alta — ogni strato ispezionato + test automatici
  Finiture:             polish UX completo, dark mode, accessibilità
  Verifica:             build + curl + auth + regression + test suite
  Strati:               1 Fondamenta, 2 Struttura, 3 Mura, 4 Impianti, 5 Finiture
  Rischio:              minimo — ridondanza di controllo
```

## Regole di presentazione

1. **Minimo 2, massimo 4 preventivi** — più di 4 confonde
2. **Ordine crescente** per costo (A più basso, C/D più alto)
3. **Agenti esclusi sempre dichiarati** — trasparenza sulla regola minima necessità
4. **Costo in € realistico** — converti da $ con tasso attuale, arrotonda a 5 centesimi
5. **Raccomandazione breve** dopo i dettagli: "Consiglio B perché [motivo in 1 riga]"

## Il preventivo scelto diventa tetto duro

Una volta che l'utente sceglie (es. "B"):
- Il campo `budget_cap` nel workorder copia i valori di B
- Se durante la costruzione uno strato sforerebbe → stop, `[SFORO] +€X → chiedo OK`
- Se finisce sotto budget → report lo mostra come risparmio, non gonfiare

## Cosa NON fare

- Non presentare un preventivo senza agenti esclusi (sarebbe il default-NO invertito)
- Non inventare preventivi intermedi durante la costruzione (si torna all'utente)
- Non nascondere il costo stimato dei sub-agenti — anche Opus-plan costa
- Non promettere qualità "massima" in un preventivo economico
