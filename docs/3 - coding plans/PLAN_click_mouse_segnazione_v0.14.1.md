---
type: plan
feature: click_mouse_segnazione
status: READY
agent: Agent-Plan
target_version: 0.14.1
design_ref: docs/2 - projects/DESIGN_click_mouse_segnazione.md
---

## Problema da risolvere
Aggiungere supporto click sinistro del mouse per segnare i numeri sulla cartella visiva. Il click attualmente viene ignorato perché le celle wx.StaticText di PannelloCartella non ha nessun binding EVT_LEFT_DOWN.

## Approccio tecnico
Modifica chirurgica e additiva in un unico file: bingo_game/ui/finestra_gioco.py
- Classe PannelloCartella: aggiungere parametro opzionale `on_click_numero` nel costruttore; nel metodo `_build_ui()` aggiungere `cell.Bind(wx.EVT_LEFT_DOWN, self._on_cella_click)` su ogni cella; aggiungere metodo `_on_cella_click(self, event)`.
- Classe FinestraGioco: passare il callback nella creazione di `self._pannello_cartella`; aggiungere metodo `_on_click_numero_cartella(self, numero: int)` con guard sulla fase turno.
Nessuna modifica ad altri file.

## File da modificare
- bingo_game/ui/finestra_gioco.py (unico file modificato)

## Dipendenze
- ComandiGiocatoreUmano.segna_numero(numero: int) — già esistente, nessuna modifica
- WxRenderer._handle_segnazione_numero — già esistente, nessuna modifica

## Rischi
Nessun rischio rilevante. La modifica è additiva. Test di regressione tastiera e NVDA raccomandati.

## Fasi di implementazione
Fase 1 — Modifica PannelloCartella (aggiunta binding + handler + parametro callback)
Fase 2 — Modifica FinestraGioco (passaggio callback + handler _on_click_numero_cartella)

## Project padre
docs/2 - projects/DESIGN_click_mouse_segnazione.md
