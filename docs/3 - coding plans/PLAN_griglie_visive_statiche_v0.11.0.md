---
type: plan
feature: griglie_visive_statiche
agent: Agent-Plan
status: READY
version: v0.11.0
design_ref: docs/2 - projects/DESIGN_griglie_visive_statiche_v0.11.0.md
date: 2026-04-11
---

# PLAN — Griglie visive statiche in FinestraGioco

## 1. Executive Summary

- **Tipo**: Feature UI (presentazione)
- **Priorità**: Alta — fondamenta visive per le fasi successive
- **Branch**: main
- **Versione target**: v0.11.0
- **Commit attesi**: 2 (preparatorio + main)

## 2. Problema e Obiettivo

La `FinestraGioco` attuale è puramente funzionale per screen reader ma priva di
qualsiasi elemento visivo per un giocatore vedente. Questa fase aggiunge due
griglie statiche colorate (`PannelloTabellone` e `PannelloCartella`) usando
le costanti visive di `tema.py`. Nessuna logica di aggiornamento: solo rendering
iniziale con dati placeholder.

## 3. File coinvolti

| File | Operazione | Note |
|---|---|---|
| `bingo_game/ui/tema.py` | MODIFY | Aggiunta di `DIMENSIONE_CELLA_TABELLONE` e `DIMENSIONE_CELLA_CARTELLA` |
| `bingo_game/ui/finestra_gioco.py` | MODIFY | Nuove classi + integrazione `_build_ui` + resize finestra |

## 4. Fasi sequenziali

### Fase A — Costanti celle in tema.py (commit preparatorio)

Aggiungere alla sezione `DIMENSIONI` di `bingo_game/ui/tema.py`:

```python
DIMENSIONE_CELLA_TABELLONE = (24, 26)  # Cella griglia tabellone (w, h) in pixel
DIMENSIONE_CELLA_CARTELLA = (60, 34)   # Cella griglia cartella (w, h) in pixel
```

Commit: `feat(ui): aggiungi costanti dimensione celle in tema.py`
File toccati: solo `bingo_game/ui/tema.py`

Verifica:
- `python -m py_compile bingo_game/ui/tema.py` → exit 0

---

### Fase B — PannelloTabellone e PannelloCartella (commit principale)

Modifiche a `bingo_game/ui/finestra_gioco.py`:

**B.1 — Import da tema**

Aggiungere all'import block esistente:
```python
from bingo_game.ui.tema import (
    COLORE_CELLA_VUOTA, COLORE_CELLA_TESTO_INATTIVO,
    COLORE_CELLA_CARTELLA_VUOTA, COLORE_CELLA_CARTELLA_NUMERO,
    COLORE_TESTO_SCURO,
    FONT_CARTELLA_NUMERO_PT,
    DIMENSIONE_FINESTRA_GIOCO,
    DIMENSIONE_CELLA_TABELLONE, DIMENSIONE_CELLA_CARTELLA,
)
```

**B.2 — Classe PannelloTabellone**

Nuova classe prima di `PannelloGriglia`:
- `wx.Panel` non focalizzabile (`~wx.TAB_TRAVERSAL`)
- `wx.GridSizer(rows=10, cols=9, vgap=1, hgap=1)`
- Per `row` in 0..9, `col` in 0..8: `numero = col * 10 + row + 1`
- Ogni cella: `wx.StaticText`, `SetBackgroundColour(COLORE_CELLA_VUOTA)`,
  `SetForegroundColour(COLORE_CELLA_TESTO_INATTIVO)`, `SetMinSize(DIMENSIONE_CELLA_TABELLONE)`

**B.3 — Classe PannelloCartella**

Nuova classe prima di `PannelloGriglia`:
- `wx.Panel` non focalizzabile (`~wx.TAB_TRAVERSAL`)
- `_PLACEHOLDER` (classvar): lista 3×9 con 0 per celle vuote
- `wx.GridSizer(rows=3, cols=9, vgap=2, hgap=2)`
- Celle con numero: sfondo `COLORE_CELLA_CARTELLA_NUMERO`, testo `COLORE_TESTO_SCURO`
- Celle vuote: sfondo `COLORE_CELLA_CARTELLA_VUOTA`

**B.4 — Modifica FinestraGioco.__init__**

Sostituire `size=(700, 500)` con `size=DIMENSIONE_FINESTRA_GIOCO`.

**B.5 — Modifica FinestraGioco._build_ui**

Dopo l'aggiunta di `PannelloGriglia` al sizer, e prima della label del log:
```python
sizer_griglie = wx.BoxSizer(wx.HORIZONTAL)
self._pannello_tabellone = PannelloTabellone(panel)
sizer_griglie.Add(self._pannello_tabellone, 0, wx.ALL, 5)
self._pannello_cartella = PannelloCartella(panel)
sizer_griglie.Add(self._pannello_cartella, 1, wx.ALL | wx.EXPAND, 5)
sizer.Add(sizer_griglie, 0, wx.ALL | wx.EXPAND, 0)
```

Commit: `feat(ui): aggiungi PannelloTabellone e PannelloCartella statici in finestra_gioco`
File toccati: solo `bingo_game/ui/finestra_gioco.py`

Verifica:
- `python -m py_compile bingo_game/ui/finestra_gioco.py` → exit 0
- `python -m pytest tests/ -m "not gui" -q` → tutti verdi
- `git diff --name-only HEAD` → solo `bingo_game/ui/finestra_gioco.py`

## 5. Test Plan

- **Unit**: nessun test nuovo richiesto — i pannelli sono puramente visivi e statici
- **Smoke test manuale**: `py main.py` → finestra avvia, griglie visibili, PannelloGriglia
  mantiene il focus, NVDA vocalizza correttamente gli annunci
- **Regression**: tutta la suite esistente (`pytest -m "not gui"`) deve continuare a passare
  senza modifiche — nessuna logica di dominio è stata toccata
