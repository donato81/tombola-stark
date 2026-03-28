# docs/4 - reports

**Scopo:** Report copertura e validazione gate, output CI

## Agenti

| Ruolo | Agente |
|-------|--------|
| Scrittura | Agent-Validate |
| Lettura | Agent-Docs |

## Convenzione naming

`REPORT_<tipo>_AAAA-MM-GG.md`

## Istruzioni specifiche

Documento punto-nel-tempo (es. coverage, validation).
Non viene mai aggiornato: ogni rilevazione produce un nuovo file distinto.
La data nel nome è la chiave di unicità storica.
