---
type: todo
feature: griglie_visive_statiche
status: COMPLETED
version: v0.11.0
plan_ref: docs/3 - coding plans/PLAN_griglie_visive_statiche_v0.11.0.md
date: 2026-04-11
---

# TODO — Griglie visive statiche v0.11.0

Piano di riferimento: [PLAN_griglie_visive_statiche_v0.11.0.md](../3%20-%20coding%20plans/PLAN_griglie_visive_statiche_v0.11.0.md)

## Istruzioni per Agent-Code

Implementa una fase alla volta. Dopo ogni commit spunta la fase. Non
proseguire alla fase successiva senza aver eseguito la verifica indicata.

## Checklist fasi

- [x] Fase A — Aggiungi `DIMENSIONE_CELLA_TABELLONE` e `DIMENSIONE_CELLA_CARTELLA` a `tema.py`
      Verifica: `python -m py_compile bingo_game/ui/tema.py` → exit 0
      Commit: `feat(ui): aggiungi costanti dimensione celle in tema.py`

- [x] Fase B — Aggiungi `PannelloTabellone`, `PannelloCartella` e integra in `_build_ui`
      e `__init__` di `FinestraGioco`
      Verifica: `python -m py_compile bingo_game/ui/finestra_gioco.py` → exit 0
               `python -m pytest tests/ -m "not gui" -q` → tutti verdi
      Commit: `feat(ui): aggiungi PannelloTabellone e PannelloCartella statici in finestra_gioco`
