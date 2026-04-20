---
type: plan
feature: lampeggio_btn_pronto
agent: Agent-Plan
status: READY
version: v0.15.0
design_ref: docs/2 - projects/DESIGN_lampeggio_btn_pronto_v0.15.0.md
date: 2026-04-20
---

# PLAN — Lampeggio pulsante "Sono pronto / Ho finito" (v0.15.0)

## 1. Executive Summary

- **Tipo**: Feature presentazionale (UI-only)
- **Priorità**: Media — migliora usabilità per utenti vedenti
- **Branch**: main
- **Versione target**: v0.15.0
- **Design approvato**: DESIGN_lampeggio_btn_pronto_v0.15.0.md (status: REVIEWED)

## 2. Problema e Obiettivo

**Problema**: durante la fase `attesa_reclami`, il pulsante "Ho finito — avvia verifica"
cambia colore (arancione) ma resta statico. Un utente vedente che vuole segnare
un numero può perdere il riferimento su quale azione compiere per concludere il turno.

**Obiettivo**: il pulsante deve lampeggiare (alternanza cromatica arancione ↔ giallo-oro)
per tutta la durata della fase, fermandosi automaticamente all'uscita. NVDA non è impattato.

## 3. File coinvolti

| File | Tipo modifica |
|---|---|
| `bingo_game/ui/tema.py` | MODIFY — aggiunge costante `COLORE_BTN_LAMPEGGIO_A` |
| `bingo_game/ui/finestra_gioco.py` | MODIFY — aggiunge timer lampeggio e si aggancia ad aggiorna_stato_pulsante |

## 4. Fasi sequenziali

### Fase 1 — Costante colore in tema.py
- Aggiungere `COLORE_BTN_LAMPEGGIO_A = "#FFD54F"` nella sezione "Pulsanti" di `tema.py`
- Aggiornare import in `finestra_gioco.py` (riga import tema)

### Fase 2 — Attributi di stato in `FinestraGioco.__init__`
- Aggiungere `self._timer_lampeggio_btn: Optional[wx.Timer] = None`
- Aggiungere `self._lampeggio_btn_attivo: bool = False`
- Aggiungere `self._tick_lampeggio_btn: int = 0`

### Fase 3 — Tre nuovi metodi privati in FinestraGioco
- `_avvia_lampeggio_btn()`: crea e avvia timer 500ms
- `_ferma_lampeggio_btn()`: ferma timer e ripristina colore base arancione
- `_on_tick_lampeggio_btn()`: handler tick, alterna colori su `_btn_principale`

### Fase 4 — Agganci in aggiorna_stato_pulsante e _on_close
- In `aggiorna_stato_pulsante()`: chiamare `_avvia_lampeggio_btn()` quando fase == "attesa_reclami",
  `_ferma_lampeggio_btn()` in tutti gli altri rami
- In `_on_close()`: aggiungere stop guard per `_timer_lampeggio_btn`

## 5. Test Plan

- **Unit test GUI**: non applicabili (componente wx puro, marcato `@pytest.mark.gui`)
- **Smoke test manuale**: avviare partita, premere "Inizia partita", verificare che
  il pulsante "Ho finito" lampeggi; premere il pulsante e verificare che si fermi;
  attendere timeout e verificare stop automatico
- **Test NVDA**: avvio partita con NVDA attivo, verificare che non si sentano
  annunci aggiuntivi durante il lampeggio
- **Test pausa**: entrare in pausa durante attesa_reclami, verificare stop lampeggio;
  riprendere, verificare no-restart (la fase è cambiata)

## 6. Note implementative

- Usare `Bind(wx.EVT_TIMER, self._on_tick_lampeggio_btn, self._timer_lampeggio_btn)`
  (bind all'istanza specifica, non a tutti i timer del frame)
- In `_ferma_lampeggio_btn()` ripristinare il colore prima di impostare `_lampeggio_btn_attivo = False`
- Importare `COLORE_BTN_LAMPEGGIO_A` nell'import di tema già esistente in `finestra_gioco.py`
