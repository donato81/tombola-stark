---
type: plan
feature: griglie_visive_dinamiche
agent: Agent-Plan
status: READY
version: v0.11.1
design_ref: docs/2 - projects/DESIGN_griglie_visive_dinamiche_v0.11.1.md
date: 2026-04-11
---

# PLAN — Collegamento dinamico griglie visive ↔ stato di gioco

## 1. Executive Summary

- **Tipo**: Feature UI (presentazione)
- **Priorità**: Alta — griglie diventano strumento visivo reale
- **Branch**: main
- **Versione target**: v0.11.1
- **Commit attesi**: 1 (unico commit su `finestra_gioco.py`)

## 2. Problema e Obiettivo

`PannelloTabellone` e `PannelloCartella` mostrano dati statici placeholder.
Questa fase li rende dinamici: ridipingono le celle con colori semantici
dopo ogni estrazione, dopo la verifica premi e all'avvio della partita.

## 3. File coinvolti

| File | Operazione | Note |
|---|---|---|
| `bingo_game/ui/finestra_gioco.py` | MODIFY | Unico file toccato |

## 4. Fasi sequenziali

### Fase unica — Tutto in `finestra_gioco.py`

**Step 1 — Aggiorna import da `tema`**

Aggiungere al blocco esistente:
```python
COLORE_CELLA_ESTRATTO, COLORE_TESTO_CHIARO,
COLORE_CELLA_SEGNATA, COLORE_CELLA_ESTRATTA_NON_SEGNATA,
```

**Step 2 — Refactor `PannelloTabellone._build_ui`**

Sostituire la costruzione anonima con:
```python
self._celle: dict[int, wx.StaticText] = {}
# ... dopo SetBackgroundColour / SetForegroundColour:
self._celle[numero] = cell
```

**Step 3 — Aggiungere `PannelloTabellone.aggiorna`**

```python
def aggiorna(self, numeri_estratti: set[int]) -> None:
    for numero, cell in self._celle.items():
        if numero in numeri_estratti:
            cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_ESTRATTO))
            cell.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        else:
            cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_VUOTA))
            cell.SetForegroundColour(wx.Colour(COLORE_CELLA_TESTO_INATTIVO))
    self.Refresh()
```

**Step 4 — Refactor `PannelloCartella._build_ui`**

- Rimuovere `_PLACEHOLDER` dalla classe
- Costruire `self._celle: list[list[wx.StaticText]]` con celle inizialmente vuote:
```python
self._celle: list[list[wx.StaticText]] = []
for row in range(3):
    riga: list[wx.StaticText] = []
    for col in range(9):
        cell = wx.StaticText(...)
        cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_CARTELLA_VUOTA))
        # ...
        riga.append(cell)
    self._celle.append(riga)
```

**Step 5 — Aggiungere `PannelloCartella.aggiorna`**

```python
def aggiorna(
    self,
    griglia: tuple,     # format get_griglia_semplice(): "-" o int
    numeri_segnati: set[int],
    numeri_estratti: set[int],
) -> None:
    for row in range(3):
        for col in range(9):
            val = griglia[row][col]
            cell = self._celle[row][col]
            if isinstance(val, str):           # cella vuota ("-")
                cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_CARTELLA_VUOTA))
                cell.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
                cell.SetLabel("")
            elif val in numeri_segnati:        # segnato
                cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_SEGNATA))
                cell.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
                cell.SetLabel(str(val))
            elif val in numeri_estratti:       # estratto non segnato
                cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_ESTRATTA_NON_SEGNATA))
                cell.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
                cell.SetLabel(str(val))
            else:                              # non estratto
                cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_CARTELLA_NUMERO))
                cell.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
                cell.SetLabel(str(val))
    self.Refresh()
```

**Step 6 — Aggiungere `FinestraGioco._aggiorna_griglie_visive`**

```python
def _aggiorna_griglie_visive(self) -> None:
    self._pannello_tabellone.aggiorna(self._partita.tabellone.numeri_estratti)
    giocatore_umano = next(
        (g for g in self._partita.giocatori if not g.is_automatico()), None
    )
    if giocatore_umano is None or not giocatore_umano.cartelle:
        return
    indice = getattr(giocatore_umano, '_indice_cartella_focus', None)
    if indice is None:
        indice = 0
    indice = max(0, min(indice, len(giocatore_umano.cartelle) - 1))
    cartella = giocatore_umano.cartelle[indice]
    self._pannello_cartella.aggiorna(
        griglia=cartella.get_griglia_semplice(),
        numeri_segnati=cartella.numeri_segnati,
        numeri_estratti=self._partita.tabellone.numeri_estratti,
    )
```

**Step 7 — 3 punti di chiamata**

1. `_on_pulsante_principale` → dopo `annuncia_numero_estratto`
2. `_esegui_verifica_premi` → dopo `annuncia_premi_turno`
3. `_imposta_focus_iniziale` → in coda

Commit: `feat(ui): collega griglie visive allo stato dinamico della partita`
File toccati: solo `bingo_game/ui/finestra_gioco.py`

Verifica:
- `python -m py_compile bingo_game/ui/finestra_gioco.py` → exit 0
- `python -m pytest tests/ -m "not gui" -q` → tutti verdi

## 5. Test Plan

- **Unit**: nessun test nuovo richiesto — modifiche puramente UI/presentazione
- **Smoke test manuale**: `py main.py` → avviare partita, estrarre numeri; verificare
  che tabellone colori i numeri estratti in rosso e cartella mostri i segnati in verde
- **Regression**: suite completa (`pytest -m "not gui"`) deve restare verde
