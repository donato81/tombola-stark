---
type: todo
feature: overlay_numero_estratto
status: DRAFT
agent: Agent-Plan
plan_ref: docs/3 - coding plans/PLAN_OVERLAY_NUMERO_ESTRATTO_v0.14.2.md
---

## Descrizione task

Implementazione overlay visivo numero estratto per utenti vedenti.
4 fasi di implementazione atomiche. Nessuna modifica al flusso NVDA.

## Checklist implementazione

### Fase 1 — Costanti tema (`bingo_game/ui/tema.py`)

- [ ] Aggiungere `FONT_OVERLAY_PT = 72` nella sezione FONT
- [ ] Aggiungere `FONT_OVERLAY_LABEL_PT = 16` nella sezione FONT
- [ ] Aggiungere `DIMENSIONE_OVERLAY = (260, 180)` nella sezione DIMENSIONI
- [ ] Pre-commit: `python -m py_compile bingo_game/ui/tema.py` → exit 0
- [ ] Commit: `feat(ui): aggiunge costanti tema per overlay numero estratto`

### Fase 2 — Classe OverlayNumeroEstratto (`bingo_game/ui/overlay_numero.py`)

- [ ] Creare file `bingo_game/ui/overlay_numero.py` con classe `OverlayNumeroEstratto(wx.Frame)`
- [ ] Stile frame: `STAY_ON_TOP | FRAME_NO_TASKBAR | FRAME_TOOL_WINDOW | BORDER_NONE`
- [ ] Metodo `mostra_numero(numero: int)`: aggiorna label, posiziona, Show(), timer ONE_SHOT 10 s
- [ ] Metodo `_posiziona()`: calcola posizione angolo basso-destra con `GetScreenPosition()`
- [ ] Metodo `_on_timer()`: Handler EVT_TIMER → `Hide()`
- [ ] Reset timer se overlay già visibile (Stop→Start prima di Show)
- [ ] Pre-commit: `python -m py_compile bingo_game/ui/overlay_numero.py` → exit 0
- [ ] Commit: `feat(ui): aggiunge OverlayNumeroEstratto — finestra overlay non modale`

### Fase 3 — Integrazione FinestraGioco (`bingo_game/ui/finestra_gioco.py`)

- [ ] Aggiungere import `from bingo_game.ui.overlay_numero import OverlayNumeroEstratto`
- [ ] Aggiungere `self._overlay_numero = OverlayNumeroEstratto(parent=self)` in `__init__()` dopo `self._build_ui()`
- [ ] Aggiungere metodo pubblico `mostra_overlay_numero(self, numero: int) -> None`
- [ ] Aggiornare `_on_close()`: aggiungere `self._overlay_numero.Destroy()` prima di `event.Skip()`
- [ ] Pre-commit: `python -m py_compile bingo_game/ui/finestra_gioco.py` → exit 0
- [ ] Commit: `feat(ui): integra OverlayNumeroEstratto in FinestraGioco`

### Fase 4 — Integrazione renderer (`bingo_game/ui/renderers/renderer_wx.py`)

- [ ] Aggiungere metodo `_wx_mostra_overlay_numero(self, numero: int) -> None` dopo `_wx_avvia_lampeggio()`
- [ ] Aggiungere `self._wx_mostra_overlay_numero(numero)` in `annuncia_numero_estratto()` tra `_wx_aggiorna_header(...)` e `_ao2_vocalizza(testo)`
- [ ] Verificare che `_ao2_vocalizza(testo)` rimanga l'ultima istruzione del metodo
- [ ] Pre-commit: `python -m py_compile bingo_game/ui/renderers/renderer_wx.py` → exit 0
- [ ] Commit: `feat(ui): renderer chiama overlay numero estratto in annuncia_numero_estratto`

### Verifica finale

- [ ] `python -m pytest tests/ -q --tb=short` → 0 regressioni
- [ ] Verifica manuale: overlay appare e scompare dopo 10 s
- [ ] Verifica manuale NVDA: nessun annuncio aggiuntivo dell'overlay
- [ ] Verifica manuale: focus tastiera non si sposta durante la visualizzazione overlay

## Priorità

Media — feature UX per utenti vedenti, non blocca il rilascio

## Riferimento PLAN

docs/3 - coding plans/PLAN_OVERLAY_NUMERO_ESTRATTO_v0.14.2.md
