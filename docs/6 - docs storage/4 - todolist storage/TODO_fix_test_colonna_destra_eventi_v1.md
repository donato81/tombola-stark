---
type: todo
feature: fix_test_colonna_destra_eventi
agent: Agent-Plan
status: COMPLETED
version: v1.0
plan_ref: docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md
design_ref: docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md
---

## Metadati

tipo: todo_task
titolo: TODO tranche 3 modernizzazione test colonna destra
data_creazione: 2026-03-29
agente: Agent-Plan
stato: completato
feature: fix_test_colonna_destra_eventi
versione_progetto: v1.0
plan: docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md
design: docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md
report: docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md

## Contenuto

### Descrizione task

Modernizzare i test legacy del gruppo colonna destra in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py),
sostituendo assertion su testo renderizzato con assertion strutturate su
`EsitoAzione`, `EventoNavigazioneColonna` ed `EventoNavigazioneColonnaAvanzata`.

### Priorita

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: [DESIGN_fix_test_colonna_destra_eventi.md](../2%20-%20projects/DESIGN_fix_test_colonna_destra_eventi.md)
- Plan: [PLAN_fix_test_colonna_destra_eventi_v1.md](../3%20-%20coding%20plans/PLAN_fix_test_colonna_destra_eventi_v1.md)
- Report: [REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md](../4%20-%20reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md)

## Checklist operativa

### Micro-fase 1 — versione base

- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_cartella_mancante` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_semplice_cartella_mancante`
- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_ultima_colonna` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_semplice_ultima_colonna`
- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_movimento_normale` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_semplice_movimento_normale`
- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_auto_inizializzazione` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_semplice_auto_inizializzazione`
- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_colonna_vuota` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_semplice_colonna_vuota`
- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_semplice_stato_interno` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_semplice_stato_interno`
- [x] Verificare il gruppo base (6/6 pass)

### Micro-fase 2 — versione avanzata

- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_cartella_mancante` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_avanzata_cartella_mancante`
- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_ultima_colonna` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_avanzata_ultima_colonna`
- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_movimento_normale` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_avanzata_movimento_normale`
- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_auto_inizializzazione` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_avanzata_auto_inizializzazione`
- [x] Leggere il corpo di `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni` prima di modificarlo
- [x] Aggiornare `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni`
- [x] Verificare il gruppo avanzata (5/5 pass)

### Chiusura tranche

- [x] Eseguire verifica finale del file [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- [x] Confermare che i test legacy del gruppo colonna destra sono allineati al contratto eventi
- [x] Registrare eventuali test gia' strutturati trovati durante la rilettura preventiva (nessuno: tutti e 11 erano legacy)
- [x] Aggiornare questo TODO marcando le fasi completate

## Note implementative

### Discrepanza REPORT item 4 (base auto_init)

Il REPORT indicava per `test_sposta_focus_colonna_destra_semplice_auto_inizializzazione`:
  - `numero_colonna_corrente == 5`, `_indice_colonna_focus == 4`

Traccia reale del codice (`_esito_inizializza_focus_colonna_se_manca` → 4, poi move +1 → 5):
  - `numero_colonna_corrente == 6`, `_indice_colonna_focus == 5`

Il REPORT era corretto per l'avanzata (item 10: indice=5, numero=6) ma errato per la base.
Il test e' stato implementato secondo il comportamento reale del codice (task: "fotografare il
comportamento reale"). I test passano: il comportamento e' confermato.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato (2026-03-29 — file target 67/67 OK, suite completa 366/366 OK, 1 skipped)