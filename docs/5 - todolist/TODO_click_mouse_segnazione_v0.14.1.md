---
type: todo
feature: click_mouse_segnazione
status: COMPLETED
agent: Agent-Plan
plan_ref: docs/3 - coding plans/PLAN_click_mouse_segnazione_v0.14.1.md
---

## Descrizione task
Implementazione click mouse per segnazione numeri cartella. Fix additiva, un solo file modificato.

## Checklist implementazione

- [x] Fase 1 — Aggiungere parametro `on_click_numero` al costruttore di `PannelloCartella`
- [x] Fase 1 — Aggiungere `cell.Bind(wx.EVT_LEFT_DOWN, self._on_cella_click)` nel ciclo `_build_ui()` di `PannelloCartella`
- [x] Fase 1 — Implementare metodo `PannelloCartella._on_cella_click(self, event: wx.MouseEvent) -> None`
- [x] Fase 2 — Passare `on_click_numero=self._on_click_numero_cartella` nella creazione di `self._pannello_cartella` in `FinestraGioco._build_ui()`
- [x] Fase 2 — Implementare metodo `FinestraGioco._on_click_numero_cartella(self, numero: int) -> None`
- [x] Pre-commit — Eseguire `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [x] Pre-commit — Eseguire `pytest tests/ -q --tb=short`

## Priorità
Alta — Fix segnalata da utenti vedenti post-alpha.

## Riferimento PLAN
docs/3 - coding plans/PLAN_click_mouse_segnazione_v0.14.1.md
