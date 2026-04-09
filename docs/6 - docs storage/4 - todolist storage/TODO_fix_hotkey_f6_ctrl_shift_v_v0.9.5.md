---
type: todo
feature: fix_hotkey_f6_ctrl_shift_v
agent: Agent-Plan
status: DONE
version: v0.9.5
plan_ref: docs/3 - coding plans/PLAN_fix_hotkey_f6_ctrl_shift_v_v0.9.5.md
date: 2026-04-05
---

# TODO — Fix hotkey F6 e Ctrl+Shift+V — v0.9.5

Piano di riferimento: [PLAN_fix_hotkey_f6_ctrl_shift_v_v0.9.5.md](../3%20-%20coding%20plans/PLAN_fix_hotkey_f6_ctrl_shift_v_v0.9.5.md)

## Istruzioni per Agent-Code

Leggere il PLAN prima di ogni modifica. Procedere una fase per volta.
Ogni fase è atomica e committabile separatamente.
Non modificare file fuori dal perimetro dichiarato nel PLAN.

Nota: i commit non sono stati eseguiti in questa sessione; i messaggi restano
come riferimento operativo.

---

## Checklist fasi

### Fase 1 — Fix Bug 1: F6 AttributeError

- [x] Modificare `bingo_game/ui/finestra_gioco.py` riga 171:
  sostituire `fg._finestra._renderer.ripeti_ultimo_annuncio()`
  con `fg._renderer.ripeti_ultimo_annuncio()`
- [x] Gate: `python -m py_compile bingo_game/ui/finestra_gioco.py` → 0 errori
- [x] Verifica automatizzata: test unitario shortcut F6 verde
- Commit proposto: `fix(ui): corretto riferimento _renderer in handler F6`

### Fase 2 — Fix Bug 2: Ctrl+Shift+V handler incompleto

- [x] Modificare `bingo_game/ui/renderers/renderer_wx.py`:
  riscrivere `_handle_visualizza_tutte_cartelle_avanzata` per iterare
  `evento.cartelle` e costruire il testo completo con segnati evidenziati
- [x] Gate: `python -m py_compile bingo_game/ui/renderers/renderer_wx.py` → 0 errori
- [x] Verifica automatizzata: renderer legge il contenuto completo di tutte le cartelle
- Commit proposto: `fix(renderer): handler visualizza_tutte_avanzata ora itera le cartelle`

### Fase 3 — Verifica test suite

- [x] Eseguire validazione equivalente con `python -m unittest` sui test mirati disponibili
- [x] Aggiornare assertions minime per coprire F6 e output avanzato completo
- Commit proposto solo se necessario: `test: aggiorna assertions handler avanzata`

### Fase 4 — Aggiornamento CHANGELOG

- [x] Aggiungere in `CHANGELOG.md` sezione `[Unreleased] → Fixed`:
  - Fix F6 (`finestra_gioco.py`)
  - Fix Ctrl+Shift+V (`renderer_wx.py`)
- Commit proposto: `docs(changelog): aggiunge fix hotkey F6 e Ctrl+Shift+V`
