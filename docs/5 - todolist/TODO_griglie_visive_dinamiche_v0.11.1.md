---
type: todo
feature: griglie_visive_dinamiche
status: COMPLETED
version: v0.11.1
plan_ref: docs/3 - coding plans/PLAN_griglie_visive_dinamiche_v0.11.1.md
date: 2026-04-11
---

# TODO — Griglie visive dinamiche v0.11.1

Piano: [PLAN_griglie_visive_dinamiche_v0.11.1.md](../3%20-%20coding%20plans/PLAN_griglie_visive_dinamiche_v0.11.1.md)

## Checklist

- [x] Step 1 — Aggiorna import da `tema` in `finestra_gioco.py`
- [x] Step 2 — Refactor `PannelloTabellone._build_ui` con `self._celle: dict`
- [x] Step 3 — Aggiungi `PannelloTabellone.aggiorna(...)`
- [x] Step 4 — Refactor `PannelloCartella._build_ui` con `self._celle: list[list]`
- [x] Step 5 — Aggiungi `PannelloCartella.aggiorna(...)`
- [x] Step 6 — Aggiungi `FinestraGioco._aggiorna_griglie_visive()`
- [x] Step 7 — 3 punti di chiamata (post-estrazione, post-verifica, avvio)
      Verifica: `python -m py_compile bingo_game/ui/finestra_gioco.py` → exit 0
               `python -m pytest tests/ -m "not gui" -q` → tutti verdi (770 passed)
      Commit: `feat(ui): collega griglie visive allo stato dinamico della partita`
