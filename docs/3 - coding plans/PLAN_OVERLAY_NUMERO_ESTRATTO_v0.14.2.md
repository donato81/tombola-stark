---
type: plan
feature: overlay_numero_estratto
status: DRAFT
agent: Agent-Plan
target_version: 0.14.2
design_ref: docs/2 - projects/DESIGN_OVERLAY_NUMERO_ESTRATTO.md
---

## Executive Summary

- **Tipo:** Feature additiva — nessuna logica esistente modificata
- **Priorità:** Media — miglioria UX per utenti vedenti senza screen reader
- **Branch suggerito:** `feature/overlay-numero-estratto`
- **Versione target:** 0.14.2
- **Design di riferimento:** `docs/2 - projects/DESIGN_OVERLAY_NUMERO_ESTRATTO.md`
- **Report analisi:** `docs/4 - reports/REPORT_ANALISI_OVERLAY_NUMERO_ESTRATTO_2026-04-20.md`

## Problema da risolvere

La `HeaderBar` esistente mostra il numero estratto in font 12 pt su sfondo scuro.
Utenti vedenti che non usano screen reader non percepiscono il numero a colpo
d'occhio durante il gioco. Nelle sale bingo fisiche un monitor dedicato mostra
il numero estratto in grande per alcuni secondi; l'app non offre un'esperienza
equivalente.

**Vincoli stringenti:**
- La HeaderBar rimane invariata.
- Il flusso NVDA (testo vocalizzato, momento della vocalizzazione) rimane invariato.
- L'overlay non riceve mai il focus della tastiera.
- L'overlay scompare automaticamente dopo 10 secondi.

## File coinvolti

| File | Operazione | Fase |
|------|-----------|------|
| `bingo_game/ui/tema.py` | MODIFY | 1 |
| `bingo_game/ui/overlay_numero.py` | CREATE | 2 |
| `bingo_game/ui/finestra_gioco.py` | MODIFY | 3 |
| `bingo_game/ui/renderers/renderer_wx.py` | MODIFY | 4 |

## Fasi sequenziali

---

### Fase 1 — Costanti tema

**File:** `bingo_game/ui/tema.py`

**Modifica:** Aggiungere, nella sezione `FONT — Dimensioni in punti tipografici`
e nella sezione `DIMENSIONI — Pannelli e componenti`, le tre nuove costanti:

```python
# Overlay numero estratto
FONT_OVERLAY_PT = 72            # Dimensione font numero nell'overlay estratto
FONT_OVERLAY_LABEL_PT = 16      # Dimensione etichetta secondaria overlay

DIMENSIONE_OVERLAY = (260, 180) # Larghezza × Altezza dell'overlay in pixel
```

**Pre-commit:**
```
python -m py_compile bingo_game/ui/tema.py
```

**Commit atomico:**
```
feat(ui): aggiunge costanti tema per overlay numero estratto
```

---

### Fase 2 — Classe OverlayNumeroEstratto

**File:** `bingo_game/ui/overlay_numero.py` (NUOVO)

**Struttura:**

```python
"""
overlay_numero.py — Finestra overlay non modale per numero estratto.

Mostra il numero estratto in grande per N secondi ai giocatori
vedenti che non usano screen reader. Non riceve mai il focus.
Non produce annunci NVDA.

path: bingo_game/ui/overlay_numero.py
"""
from __future__ import annotations
import wx
from bingo_game.ui.tema import (
    FONT_OVERLAY_PT, FONT_OVERLAY_LABEL_PT, DIMENSIONE_OVERLAY,
    COLORE_HEADER_BG, COLORE_HEADER_ACCENT, COLORE_TESTO_MUTED,
)

_DURATA_DEFAULT_MS: int = 10_000  # 10 secondi


class OverlayNumeroEstratto(wx.Frame):
    """
    Finestra overlay non modale che mostra il numero estratto per N secondi.

    - Nessun focus: non interferisce con navigazione tastiera o NVDA.
    - Autodistruzione: si nasconde automaticamente allo scadere del timer.
    - Ciclo di vita: istanziata una volta, mostrata/nascosta a ogni estrazione.
    """

    def __init__(
        self,
        parent: wx.Frame,
        durata_ms: int = _DURATA_DEFAULT_MS,
    ) -> None:
        style = (
            wx.STAY_ON_TOP
            | wx.FRAME_NO_TASKBAR
            | wx.FRAME_TOOL_WINDOW
            | wx.BORDER_NONE
        )
        super().__init__(parent, style=style)
        self._parent = parent
        self._durata_ms = durata_ms
        self._timer: wx.Timer = wx.Timer(self)
        self._build_ui()
        self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)

    def _build_ui(self) -> None:
        w, h = DIMENSIONE_OVERLAY
        self.SetSize(w, h)
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(COLORE_HEADER_BG))

        sizer = wx.BoxSizer(wx.VERTICAL)

        self._lbl_titolo = wx.StaticText(panel, label="Numero estratto")
        self._lbl_titolo.SetFont(
            wx.Font(FONT_OVERLAY_LABEL_PT, wx.FONTFAMILY_DEFAULT,
                    wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        self._lbl_titolo.SetForegroundColour(wx.Colour(COLORE_TESTO_MUTED))
        sizer.Add(self._lbl_titolo, 0, wx.ALIGN_CENTER | wx.TOP, 12)

        self._lbl_numero = wx.StaticText(panel, label="", style=wx.ALIGN_CENTER)
        self._lbl_numero.SetFont(
            wx.Font(FONT_OVERLAY_PT, wx.FONTFAMILY_DEFAULT,
                    wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        self._lbl_numero.SetForegroundColour(wx.Colour(COLORE_HEADER_ACCENT))
        sizer.Add(self._lbl_numero, 1, wx.ALIGN_CENTER | wx.ALL, 8)

        panel.SetSizer(sizer)
        panel.Layout()

    def mostra_numero(self, numero: int) -> None:
        """Mostra l'overlay con il numero e avvia il timer di chiusura automatica."""
        self._lbl_numero.SetLabel(str(numero))
        self._posiziona()
        if self._timer.IsRunning():
            self._timer.Stop()
        self.Show()
        self._timer.Start(self._durata_ms, wx.TIMER_ONE_SHOT)

    def _posiziona(self) -> None:
        """Posiziona l'overlay all'angolo inferiore-destro del parent."""
        if self._parent is None or not self._parent.IsShown():
            return
        px, py = self._parent.GetScreenPosition()
        pw, ph = self._parent.GetSize()
        ow, oh = DIMENSIONE_OVERLAY
        margin = 16
        x = px + pw - ow - margin
        y = py + ph - oh - margin
        self.SetPosition(wx.Point(x, y))

    def _on_timer(self, event: wx.TimerEvent) -> None:
        """Nasconde l'overlay allo scadere del timer."""
        self.Hide()
```

**Pre-commit:**
```
python -m py_compile bingo_game/ui/overlay_numero.py
```

**Commit atomico:**
```
feat(ui): aggiunge OverlayNumeroEstratto — finestra overlay non modale
```

---

### Fase 3 — Integrazione in FinestraGioco

**File:** `bingo_game/ui/finestra_gioco.py`

**Modifica 3a — Import in testa al file** (dopo gli import esistenti di `bingo_game.ui`):
```python
from bingo_game.ui.overlay_numero import OverlayNumeroEstratto
```

**Modifica 3b — `FinestraGioco.__init__()`**, dopo `self._build_ui()`:
```python
self._overlay_numero: OverlayNumeroEstratto = OverlayNumeroEstratto(parent=self)
```

**Modifica 3c — Nuovo metodo pubblico** (aggiunto dopo `aggiungi_a_log()`):
```python
def mostra_overlay_numero(self, numero: int) -> None:
    """Mostra l'overlay visivo del numero estratto (solo per vedenti, non-NVDA)."""
    self._overlay_numero.mostra_numero(numero)
```

**Modifica 3d — `FinestraGioco._on_close()`**, prima di `event.Skip()`:
```python
if hasattr(self, "_overlay_numero"):
    self._overlay_numero.Destroy()
```

**Pre-commit:**
```
python -m py_compile bingo_game/ui/finestra_gioco.py
```

**Commit atomico:**
```
feat(ui): integra OverlayNumeroEstratto in FinestraGioco
```

---

### Fase 4 — Integrazione nel renderer

**File:** `bingo_game/ui/renderers/renderer_wx.py`

**Modifica 4a — Nuovo metodo privato `_wx_mostra_overlay_numero()`**
(aggiunto dopo `_wx_avvia_lampeggio()`):
```python
def _wx_mostra_overlay_numero(self, numero: int) -> None:
    """Mostra l'overlay visivo del numero estratto (solo se disponibile nel frame)."""
    if self._finestra is None:
        return
    if hasattr(self._finestra, "mostra_overlay_numero"):
        self._finestra.mostra_overlay_numero(numero)
```

**Modifica 4b — `WxRenderer.annuncia_numero_estratto()`**:
Aggiungere `self._wx_mostra_overlay_numero(numero)` dopo `self._wx_aggiorna_header(...)`
e prima di `self._ao2_vocalizza(testo)`.

Risultato finale del metodo:
```python
def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
    testo = f"Turno {numero_turno}. Numero estratto: {numero}."
    self._wx_aggiorna_output(testo)
    self._wx_avvia_lampeggio(numero)
    self._wx_aggiorna_header(turno=numero_turno, ultimo_numero=numero)
    self._wx_mostra_overlay_numero(numero)   # ← FASE 4
    self._ao2_vocalizza(testo)
```

**Pre-commit:**
```
python -m py_compile bingo_game/ui/renderers/renderer_wx.py
```

**Commit atomico:**
```
feat(ui): renderer chiama overlay numero estratto in annuncia_numero_estratto
```

---

## Test Plan

### Unit — nessun test aggiuntivo richiesto in fase 1

La classe `OverlayNumeroEstratto` crea widget wxPython e non è testabile
in ambiente headless. Non è richiesta coverage unit per questo componente
(analogamente a `HeaderBar`, `PannelloTabellone`, ecc.).

### Verifica manuale obbligatoria prima del merge

- [ ] Avviare l'applicazione con `py main.py`
- [ ] Avviare una partita e premere "Inizia partita"
- [ ] Verificare che l'overlay appaia in basso a destra con il numero in grande (font giallo su sfondo blu)
- [ ] Verificare che l'overlay scompaia dopo circa 10 secondi senza interazione
- [ ] Verificare che una seconda estrazione mentre l'overlay è visibile aggiorna il numero e resetta il timer
- [ ] Verificare con NVDA attivo che nessun annuncio aggiuntivo viene emesso dall'overlay
- [ ] Verificare che il focus da tastiera rimanga sul pannello griglia durante tutta la durata dell'overlay
- [ ] Verificare che la chiusura della finestra di gioco non lasci frame orfani

### Regressione automatica

```
python -m pytest tests/ -q --tb=short
```

I test esistenti non devono regredire.
