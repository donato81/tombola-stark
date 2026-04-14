---
type: design
feature: griglie_visive_statiche
agent: Agent-Design
status: REVIEWED
version: v0.11.0
date: 2026-04-11
---

# DESIGN — Griglie visive statiche in FinestraGioco

## 1. Idea in 3 righe

Aggiungere a `FinestraGioco` due pannelli wx.Panel puramente visivi e non
focalizzabili: `PannelloTabellone` (9 col × 10 righe, numeri 1-90 per decine)
e `PannelloCartella` (9 col × 3 righe, dati placeholder), colorati con le
costanti di `tema.py`. Nessuna logica di aggiornamento in questa fase.

## 2. Attori e Concetti

| Attore / Concetto | Ruolo |
|---|---|
| `FinestraGioco` | Frame ospitante; viene modificato solo in `_build_ui` e nel `__init__` per la dimensione |
| `PannelloTabellone` | Nuova classe wx.Panel non focalizzabile; griglia 9×10 con numeri 1-90 |
| `PannelloCartella` | Nuova classe wx.Panel non focalizzabile; griglia 9×3 con 15 numeri placeholder |
| `PannelloGriglia` | Esistente, NON modificato; resta il centro della navigazione tastiera |
| `tema.py` | Source of truth per colori, font e dimensioni; usato in import |
| `wx.GridSizer` | Sizer per disposizione a griglia delle celle |
| `wx.StaticText` | Widget cella, non focalizzabile, con colori e font da tema |

## 3. Flussi Concettuali

```
FinestraGioco.__init__
  └── size = DIMENSIONE_FINESTRA_GIOCO (da tema.py)
  └── _build_ui()
        ├── [esistenti] btn_principale, btn_pausa, btn_torna_menu
        ├── [esistente] PannelloGriglia (NON modificato)
        ├── [NUOVO] sizer_griglie = wx.BoxSizer(HORIZONTAL)
        │     ├── PannelloTabellone  (sinistra, larghezza fissa ~240px)
        │     └── PannelloCartella  (destra, proporzione 1, si espande)
        └── [esistente] label + _log_ctrl

PannelloTabellone._build_ui:
  GridSizer(rows=10, cols=9)
  for row in 0..9, col in 0..8:
    numero = col * 10 + row + 1   → 1..90
    wx.StaticText con COLORE_CELLA_VUOTA / COLORE_CELLA_TESTO_INATTIVO

PannelloCartella._build_ui:
  GridSizer(rows=3, cols=9)
  for row in 0..2, col in 0..8:
    se _PLACEHOLDER[row][col] > 0 → sfondo COLORE_CELLA_CARTELLA_NUMERO
    se _PLACEHOLDER[row][col] == 0 → sfondo COLORE_CELLA_CARTELLA_VUOTA
```

## 4. Decisioni Architetturali

| Decisione | Motivazione |
|---|---|
| Classi autonome `PannelloTabellone` e `PannelloCartella` | Encapsulation; le fasi future possono aggiungere metodi di aggiornamento senza toccare `FinestraGioco` |
| `wx.GridSizer` (non `wx.FlexGridSizer`) | Griglie a passo uniforme; non serve adattamento colonne/righe in questa fase |
| `style=wx.NO_BORDER` sui pannelli | Aspetto pulito, senza bordi di sistema |
| `wx.TAB_TRAVERSAL` rimosso (`style &= ~wx.TAB_TRAVERSAL`) | I pannelli non devono ricevere focus da Tab; accessibilità NVDA preservata su PannelloGriglia |
| Placeholder hardcoded in `_PLACEHOLDER` | Fase statica; fase 3 introdurrà aggiornamento dai dati di gioco |
| Import da `bingo_game.ui.tema` | Zero magic number nei sorgenti; cambio palette senza toccare la logica |
| Nuovi metodi in questa fase | Nessun nuovo metodo pubblico su FinestraGioco; integrazione solo in `_build_ui` |

## 5. Rischi e Vincoli

| Rischio | Mitigazione |
|---|---|
| Conflitto focus NVDA: nuovi pannelli captano Tab | Rimosso `wx.TAB_TRAVERSAL`; pannelli non fanno `SetFocus()` |
| `DIMENSIONE_CELLA_TABELLONE` / `DIMENSIONE_CELLA_CARTELLA` non presenti in `tema.py` | Aggiungere in commit preparatorio su `tema.py` prima del commit principale |
| Dimensione finestra (1000x700) potrebbe essere troppo grande su schermi piccoli | Vincolo accettato; il target è Windows 11 con display 1920×1080+ |
| Static text senza sizing esplicito potrebbe collassare | `SetMinSize(DIMENSIONE_CELLA)` garantisce dimensione minima; sizer espande |
| Backward compat: `size=(700, 500)` in `__init__` | Sostituito da `size=DIMENSIONE_FINESTRA_GIOCO`; nessun test UI dipende dalla size |
