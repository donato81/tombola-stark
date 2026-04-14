---
type: todo
feature: pulsanti_interattivi
status: COMPLETED
version: v0.12.0
plan_ref: docs/3 - coding plans/PLAN_pulsanti_interattivi_v0.12.0.md
date: 2026-04-12
---

# TODO — Pulsanti interattivi FinestraGioco v0.12.0

Piano: [PLAN_pulsanti_interattivi_v0.12.0.md](../3%20-%20coding%20plans/PLAN_pulsanti_interattivi_v0.12.0.md)

## Checklist

### Fase A — Import e struttura base

- [x] Aggiunto `import functools` in `finestra_gioco.py`
- [x] Aggiornati import da `tema.py` con costanti pulsanti
- [x] `self._panel` salvato in `_build_ui()`

### Fase B — Gruppo 1: frecce navigazione cartella

- [x] `self._btn_freccia_sx` e `self._btn_freccia_dx` creati in `_build_ui()`
- [x] Layout sizer_griglie: `[tabellone][◀][cartella][▶]`
- [x] Handler `_on_cartella_precedente` e `_on_cartella_successiva` aggiunti
- [x] Abilitazione frecce gestita in `aggiorna_stato_pulsante()`
- [x] Disabilitazione nel ramo `in_pausa` (early return)

### Fase C — Gruppo 2: selezione diretta cartella

- [x] `self._sizer_selezione` creato e aggiunto al sizer principale
- [x] `self._pulsanti_selezione: list[wx.Button] = []` inizializzato
- [x] Metodo `_crea_pulsanti_selezione_cartella()` implementato
- [x] Handler `_on_seleziona_cartella(n, event)` implementato
- [x] Metodo `_aggiorna_evidenziazione_selezione(numero_cartella)` implementato
- [x] Metodo pubblico `aggiorna_selezione_cartella(numero)` implementato
- [x] Chiamata `_crea_pulsanti_selezione_cartella()` in `_on_pulsante_principale()`

### Fase D — Gruppo 3: pulsanti premi

- [x] `self._btn_premi: dict[str, wx.Button] = {}` inizializzato
- [x] 5 pulsanti creati con stile e accessibilità corretti
- [x] Handler `_on_premio(tipo, event)` implementato con `functools.partial`
- [x] Logica abilitazione/disabilitazione in `aggiorna_stato_pulsante()`
- [x] Label ` ✓` per premi definitivamente assegnati

### Fase E — Renderer

- [x] `aggiorna_selezione_cartella` chiamata in `_handle_focus_cartella_impostato()`

### Fase F — CHANGELOG

- [x] Entry `### Fase 2 — Pulsanti interattivi` aggiunta in `[Unreleased]`

### Validazione finale

- [x] `python -m py_compile bingo_game/ui/finestra_gioco.py` → OK
- [x] `python -m py_compile bingo_game/ui/renderers/renderer_wx.py` → OK
- [x] `python -m unittest tests/test_game_controller.py -q` → 204 test OK
- [x] `python -m unittest tests/test_partita.py -q` → OK
