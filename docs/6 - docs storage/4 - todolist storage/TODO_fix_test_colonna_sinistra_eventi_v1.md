---
type: todo
feature: fix_test_colonna_sinistra_eventi
agent: Agent-Plan
status: COMPLETED
version: v1.0
plan_ref: docs/3 - coding plans/PLAN_fix_test_colonna_sinistra_eventi_v1.md
design_ref: docs/2 - projects/DESIGN_fix_test_colonna_sinistra_eventi.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md
---

## Metadati

tipo: todo_task
titolo: TODO tranche 2 modernizzazione test colonna sinistra
data_creazione: 2026-03-29
agente: Agent-Plan
stato: completato
feature: fix_test_colonna_sinistra_eventi
versione_progetto: v1.0
plan: docs/3 - coding plans/PLAN_fix_test_colonna_sinistra_eventi_v1.md
design: docs/2 - projects/DESIGN_fix_test_colonna_sinistra_eventi.md
report: docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md

## Contenuto

### Descrizione task

Modernizzare i test legacy del gruppo colonna sinistra in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py),
sostituendo assertion su testo renderizzato con assertion strutturate su
`EsitoAzione`, `EventoNavigazioneColonna` ed `EventoNavigazioneColonnaAvanzata`.

### Priorita

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: [DESIGN_fix_test_colonna_sinistra_eventi.md](../2%20-%20projects/DESIGN_fix_test_colonna_sinistra_eventi.md)
- Plan: [PLAN_fix_test_colonna_sinistra_eventi_v1.md](../3%20-%20coding%20plans/PLAN_fix_test_colonna_sinistra_eventi_v1.md)
- Report: [REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md](../4%20-%20reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md)

## Checklist operativa

### Micro-fase 1 — versione base

- [x] Aggiornare `test_sposta_focus_colonna_sinistra_semplice_cartella_mancante`
- [x] Aggiornare `test_sposta_focus_colonna_sinistra_semplice_prima_colonna`
- [x] Aggiornare `test_sposta_focus_colonna_sinistra_semplice_movimento_normale`
- [x] Aggiornare `test_sposta_focus_colonna_sinistra_semplice_auto_inizializzazione`
- [x] Aggiornare `test_sposta_focus_colonna_sinistra_semplice_colonna_vuota`
- [x] Verificare il gruppo base

### Micro-fase 2 — versione avanzata

- [x] Aggiornare `test_sposta_focus_colonna_sinistra_avanzata_cartella_mancante`
- [x] Aggiornare `test_sposta_focus_colonna_sinistra_avanzata_prima_colonna`
- [x] Aggiornare `test_sposta_focus_colonna_sinistra_avanzata_auto_inizializzazione`
- [x] Verificare se `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni` richiede ancora intervento oppure e' gia' verde strutturato
- [x] Verificare il gruppo avanzata senza toccare `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`

### Chiusura tranche

- [x] Eseguire verifica finale del file [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- [x] Confermare che i test legacy del gruppo colonna sinistra sono allineati al contratto eventi
- [x] Aggiornare questo TODO marcando le fasi completate

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato
