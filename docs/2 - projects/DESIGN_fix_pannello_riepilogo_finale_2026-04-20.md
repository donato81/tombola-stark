---
type: design
feature: fix-pannello-riepilogo-finale
status: REVIEWED
agent: Agent-Design
date: 2026-04-20
---

# DESIGN — Fix Pannello Riepilogo Finale (finestra grigia a fine partita)

## Contesto

A fine partita, `PannelloRiepilogoFinale` esiste nel sizer e viene popolato
correttamente via `mostra()`, ma la finestra appare grigia senza contenuto
visivo. NVDA legge i dati corretti perché il layer voce è indipendente dal
layer visivo.

## Causa Radice

`FinestraGioco.mostra_riepilogo_finale()` chiama `self.Layout()` sul frame.
Il sizer dell'interfaccia è assegnato a `self._panel` (figlio del frame),
non al frame stesso. `wx.Frame.Layout()` senza sizer proprio è un no-op:
i widget non vengono ridimensionati dopo le chiamate a `Hide()` / `Show()`.

## Difetti da correggere (da REPORT analisi 2026-04-20)

| ID | Priorità | Descrizione |
|----|----------|-------------|
| D1 | CRITICO | `self.Layout()` → `self._panel.Layout()` (no-op, sizer è sul panel) |
| D2 | ALTO | Hide() mancanti per 7+ widget che occupano spazio nel sizer |
| D3 | MEDIO | Manca `self._panel.Refresh()` dopo il ricalcolo layout |
| D4 | BASSO | Doppio `SetFocus` su `_btn_torna_menu` (sincrono + CallAfter) |

## Strategia

Modifiche chirurgiche a due soli punti in `finestra_gioco.py`:

### Punto A — `mostra_riepilogo_finale()` (linea ~1338)

Aggiungere Hide() per tutti gli elementi non ancora nascosti:
- `self._header_bar`
- `self._btn_principale`
- `self._btn_pausa`
- `self._lbl_cartella_titolo`
- tutti i valori di `self._btn_premi`
- `self._lbl_log`
- `self._log_ctrl`

Sostituire `self.Layout()` con `self._panel.Layout()`.
Aggiungere `self._panel.Refresh()`.
Rimuovere il `wx.CallAfter(self._btn_torna_menu.SetFocus)` da questo
metodo (il SetFocus sincrono nel chiamante è sufficiente).

### Punto B — blocco `_on_verifica()` post-terminazione (linea ~1104)

La chiamata `self.Layout()` ridondante va rimossa: il layout è già stato
rieseguito correttamente dentro `mostra_riepilogo_finale()`.

## Vincoli

- Non modificare `PannelloRiepilogoFinale`, `WxRenderer`, `BaseRenderer`.
- Non alterare la logica di gioco, i flag di stato o i dati passati.
- Non aggiungere nuove dipendenze.
- Mantenere invariato il comportamento NVDA (layer voce non toccato).

## File coinvolti

- `bingo_game/ui/finestra_gioco.py` — unico file da modificare

## Test di accettazione

1. Avviare partita con 1 bot.
2. Attendere tombola automatica.
3. Verificare: la finestra mostra titolo "Partita terminata", nome vincitore,
   turni giocati, numeri estratti, lista premi.
4. Verificare che il pulsante "Torna al menu principale" riceva il focus.
5. NVDA deve leggere il bottone senza annunci spurii duplicati.
