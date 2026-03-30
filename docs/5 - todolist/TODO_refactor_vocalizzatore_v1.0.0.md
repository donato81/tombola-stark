---
type: todo
feature: refactor_vocalizzatore
agent: Agent-Plan
status: COMPLETED
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_refactor_vocalizzatore_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_refactor_vocalizzatore_v1.0.0.md
date: 2026-03-31
report_ref: docs/4 - reports/analisi_refactor_vocalizzatore/REPORT_DIAGNOSI_VOCALIZZATORE_2026-03-30.md
---

## Metadati

tipo: todo_task
titolo: TODO refactor strutturale R2 per my_lib/vocalizzatore.py
data_creazione: 2026-03-31
agente: Agent-Plan
stato: completato
feature: refactor_vocalizzatore
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_refactor_vocalizzatore_v1.0.0.md
design: docs/2 - projects/DESIGN_refactor_vocalizzatore_v1.0.0.md
report: docs/4 - reports/analisi_refactor_vocalizzatore/REPORT_DIAGNOSI_VOCALIZZATORE_2026-03-30.md

## Contenuto

### Descrizione task

Implementare il refactor R2 di [my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py)
introducendo `IVocalizzatore`, `NullVocalizzatore`, il backend iniettabile e la
modifica minima di type hint in `WxRenderer`, con copertura unitaria dedicata.

### Priorita

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: DESIGN_refactor_vocalizzatore_v1.0.0.md
- Plan: PLAN_refactor_vocalizzatore_v1.0.0.md
- Report: REPORT_DIAGNOSI_VOCALIZZATORE_2026-03-30.md

## Checklist operativa

- [x] Definire `IVocalizzatore` come `Protocol` in `my_lib/vocalizzatore.py`
- [x] Esporre `vocalizza_testo(self, testo: str, interrompi: bool = False) -> None` nel contratto
- [x] Definire `NullVocalizzatore` in `my_lib/vocalizzatore.py`
- [x] Implementare `NullVocalizzatore.vocalizza_testo()` come no-op silenziosa
- [x] Rimuovere i 9 metodi dead code da `my_lib/vocalizzatore.py`
- [x] Aggiungere backend opzionale iniettabile al costruttore di `Vocalizzatore`
- [x] Aggiornare type hints e docstring di `Vocalizzatore`
- [x] Proteggere `Vocalizzatore.vocalizza_testo()` con `try/except` best-effort
- [x] Propagare `interrompi` verso `backend.speak(..., interrupt=interrompi)`
- [x] Sostituire il type hint del parametro `vocalizzatore` in `bingo_game/ui/renderers/renderer_wx.py` da `Vocalizzatore` a `IVocalizzatore`
- [x] Sostituire il type hint dell'attributo `_vocalizzatore` in `bingo_game/ui/renderers/renderer_wx.py` da `Vocalizzatore` a `IVocalizzatore`
- [x] Creare `tests/unit/test_vocalizzatore.py`
- [x] Scrivere test `unittest` per `NullVocalizzatore`
- [x] Scrivere test `unittest` per `Vocalizzatore` con backend fake iniettabile
- [x] Verificare che nessun test usi `pytest`
- [x] Verificare che nessun test usi `patch()` su `Auto`
- [x] Eseguire `python -m unittest discover tests/unit`
- [x] Confermare zero failure e zero error sull'intera suite `tests/unit`

## Stato Avanzamento

- [x] TODO redatto
- [x] Validazione umana
- [x] Approvato per implementazione
- [x] Implementazione completata — 2026-03-31
- [x] Suite tests/unit verde: 329 test, 0 failure, 0 error