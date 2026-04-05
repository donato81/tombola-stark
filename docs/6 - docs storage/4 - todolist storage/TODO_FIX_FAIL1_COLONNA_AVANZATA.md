---
type: todo
feature: fix_fail1_colonna_avanzata
agent: Agent-Plan
status: DRAFT
version: v0.9.3
plan_ref: docs/3 - coding plans/PLAN_FIX_FAIL1_COLONNA_AVANZATA.md
design_ref: docs/2 - projects/DESIGN_FIX_FAIL1_COLONNA_AVANZATA.md
date: 2026-03-29
---

## Metadati

tipo: todo_task
titolo: TODO fix FAIL-1 colonna avanzata
data_creazione: 2026-03-29
agente: Agent-Plan
stato: bozza
feature: fix_fail1_colonna_avanzata
versione_progetto: v0.9.3
plan: docs/3 - coding plans/PLAN_FIX_FAIL1_COLONNA_AVANZATA.md
design: docs/2 - projects/DESIGN_FIX_FAIL1_COLONNA_AVANZATA.md
report: docs/4 - reports/REPORT_FIX_FAIL1_COLONNA_AVANZATA_2026-03-29.md

## Contenuto

### Descrizione task

Correggere il solo test `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`
nel file `tests/test_giocatore_umano.py`, sostituendo assertion su testo con
assertion strutturate sull'oggetto `EsitoAzione` e sul relativo evento.

### Priorita

Alta

### Agente assegnato

Agent-Code

### Scadenza (opzionale)

Non definita

### Riferimento project/plan padre

- Project: [DESIGN_FIX_FAIL1_COLONNA_AVANZATA.md](../2%20-%20projects/DESIGN_FIX_FAIL1_COLONNA_AVANZATA.md)
- Plan: [PLAN_FIX_FAIL1_COLONNA_AVANZATA.md](../3%20-%20coding%20plans/PLAN_FIX_FAIL1_COLONNA_AVANZATA.md)
- Report: [REPORT_FIX_FAIL1_COLONNA_AVANZATA_2026-03-29.md](../4%20-%20reports/REPORT_FIX_FAIL1_COLONNA_AVANZATA_2026-03-29.md)

## Checklist operativa

- [x] Confermare la struttura reale di `EsitoAzione` restituita dal metodo
  in `tests/test_giocatore_umano.py`
- [x] Importare o riusare `EventoNavigazioneColonnaAvanzata` nel test, se necessario,
  in `tests/test_giocatore_umano.py`
- [x] Sostituire le assertion testuali obsolete con assertion strutturate
  in `tests/test_giocatore_umano.py`
- [x] Verificare in modo esplicito il caso colonna vuota tramite campo evento
  in `tests/test_giocatore_umano.py`
- [x] Eseguire `py -3.10 -m unittest discover -s tests -q` e confermare zero failure

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato
