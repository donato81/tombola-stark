---
type: plan
feature: fix-pannello-riepilogo-finale
status: READY
agent: Agent-Plan
date: 2026-04-20
design: docs/2 - projects/DESIGN_fix_pannello_riepilogo_finale_2026-04-20.md
---

# PLAN — Fix Pannello Riepilogo Finale v0.1.0

## Riferimento DESIGN

`docs/2 - projects/DESIGN_fix_pannello_riepilogo_finale_2026-04-20.md`

## Obiettivo

Correggere i 4 difetti che causano la finestra grigia a fine partita,
modificando esclusivamente `bingo_game/ui/finestra_gioco.py`.

## Fasi di implementazione

### Fase 1 — D1: self._panel.Layout() al posto di self.Layout()

File: `bingo_game/ui/finestra_gioco.py`  
Punti: `mostra_riepilogo_finale()` e `_on_verifica()` (blocco post-terminazione)  
Azione:
- In `mostra_riepilogo_finale`: `self.Layout()` → `self._panel.Layout()`
- In `_on_verifica` (blocco `if risultato_ver.get("partita_terminata")...`):
  rimuovere `self.Layout()` ridondante (il layout è già gestito in `mostra_riepilogo_finale`)

### Fase 2 — D2: Hide() per elementi non nascosti in mostra_riepilogo_finale()

File: `bingo_game/ui/finestra_gioco.py`  
Punto: inizio di `mostra_riepilogo_finale()`, dopo gli Hide già presenti  
Azione: aggiungere Hide() per:
- `self._header_bar`
- `self._btn_principale`
- `self._btn_pausa`
- `self._lbl_cartella_titolo`
- ogni bottone in `self._btn_premi.values()`
- `self._lbl_log`
- `self._log_ctrl`

### Fase 3 — D3: Refresh() dopo Layout()

File: `bingo_game/ui/finestra_gioco.py`  
Punto: in `mostra_riepilogo_finale()`, dopo `self._panel.Layout()`  
Azione: aggiungere `self._panel.Refresh()`

### Fase 4 — D4: rimozione SetFocus duplicato

File: `bingo_game/ui/finestra_gioco.py`  
Punto: in `mostra_riepilogo_finale()`, riga con `wx.CallAfter(self._btn_torna_menu.SetFocus)`  
Azione: rimuovere il `wx.CallAfter` — il SetFocus sincrono nel chiamante è sufficiente

## Pre-commit checklist

- `python -m py_compile bingo_game/ui/finestra_gioco.py`
- Lancio visivo manuale: avviare partita con 1 bot, attendere tombola, verificare riepilogo
