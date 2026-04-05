---
type: plan
feature: fix_accessibilita_focus_timer_bot
agent: Agent-Plan
status: READY
version: v0.9.5
design_ref: docs/2 - projects/DESIGN_fix_accessibilita_focus_timer_bot.md
date: 2026-04-05
---

# PLAN — Fix accessibilità: focus iniziale, soppressione avvisi timer, annuncio turno bot

## Executive Summary

Tipo intervento: fix accessibilità layer Presentation  
Priorità: P1 (Bug 1: blocca navigazione), P2 (Bug 2, Bug 3: rumore NVDA e mancanza contesto)  
Branch: fix/accessibilita-focus-timer-bot  
Versione di riferimento: v0.9.5  
Scope: tre correzioni atomiche in `bingo_game/ui/finestra_gioco.py`, nessuna modifica al domain layer.  
Vincoli: i metodi riutilizzati esistono già; nessuna nuova regola di dominio; i test esistenti non devono rompersi.

---

## Problema e Obiettivo

### Bug 1 — Focus non inizializzato su cartella 1/riga 1/colonna 1 all'avvio

`FinestraGioco.__init__` chiama `self._pannello_griglia.SetFocus()` ma non
inizializza `GiocatoreUmano._indice_cartella_focus`. Qualsiasi pressione
di tasto freccia produce "Nessuna cartella selezionata." senza che il
giocatore abbia ancora interagito.

### Bug 2 — Avvisi timer emessi dopo dichiarazione turno umano

`_on_tick_azione` non controlla se l'umano ha già dichiarato fine turno.
Anche dopo la pressione di Ctrl+P, il timer continua a emettere avvisi
vocali alle soglie 60%/80%/95%.

### Bug 3 — Passaggio turno bot non annunciato

`_dichiara_fine_bot` registra la dichiarazione del bot senza emettere
nessun annuncio. Il giocatore non sa quanti bot abbiano già dichiarato
mentre aspetta il turno successivo.

---

## Approccio tecnico

### Fix 1 — `FinestraGioco.__init__`: inizializzazione focus

Aggiungere in fondo a `__init__`, dopo `self._pannello_griglia.SetFocus()`:

```python
wx.CallAfter(self._imposta_focus_iniziale)
```

Aggiungere il metodo privato:

```python
def _imposta_focus_iniziale(self) -> None:
    """Imposta il focus di gioco su cartella 1, riga 1, colonna 1 all'avvio."""
    self._dispatch(self._comandi.imposta_focus_cartella(1))
    self._dispatch(self._comandi.vai_a_riga(1))
    self._dispatch(self._comandi.vai_a_colonna(1))
```

`wx.CallAfter` garantisce che il renderer sia già collegato alla finestra
quando vengono emessi gli annunci, evitando race condition tra costruzione
del frame e loop degli eventi.

### Fix 2 — `FinestraGioco._on_tick_azione`: soppressione avvisi post-dichiarazione

Inserire all'inizio del corpo del metodo, subito dopo l'incremento di
`self._ms_trascorsi_azione` e prima del blocco delle percentuali:

```python
# Se l'umano ha già dichiarato fine turno, non emettere avvisi timeout.
if self._comandi.turno_gia_dichiarato():
    if self._ms_trascorsi_azione >= self._durata_finestra_corrente_ms:
        self._on_timeout_azione()
    return
```

Il timer continua a girare (necessario per il timeout dei bot); gli avvisi
vocali percentuali vengono soppressi solo per il giocatore umano che ha
già agito.

### Fix 3 — `FinestraGioco._dichiara_fine_bot`: annuncio passaggio turno

Aggiungere dopo `bot.dichiara_fine_fase_azione(premi_gia_assegnati, premi_tipo_chiusi)`:

```python
nome_bot: str = getattr(bot, "nome", "Bot")
self._renderer.mostra_messaggio_sistema(f"{nome_bot} ha passato il turno.")
```

`getattr` con fallback è coerente con il pattern già usato in
`_ottieni_numero_in_focus` e gestisce correttamente il type hint loose
`bot: object`.

---

## File da modificare

- `bingo_game/ui/finestra_gioco.py` — MODIFY (unico file di produzione)
  - Fix 1: `__init__` (aggiunta `wx.CallAfter`) + nuovo metodo `_imposta_focus_iniziale`
  - Fix 2: `_on_tick_azione` (inserimento guard `turno_gia_dichiarato`)
  - Fix 3: `_dichiara_fine_bot` (aggiunta annuncio renderer dopo dichiarazione bot)

---

## Fasi di implementazione

### Fase 1 — Fix focus iniziale cartella 1/riga 1/colonna 1

File: `bingo_game/ui/finestra_gioco.py`

Modifiche:
1. In `FinestraGioco.__init__`, dopo `self._pannello_griglia.SetFocus()`,
   aggiungere: `wx.CallAfter(self._imposta_focus_iniziale)`
2. Aggiungere il metodo privato `_imposta_focus_iniziale` nella sezione
   Helper interni (vicino a `_ottieni_numero_in_focus`).

Criteri di completamento:
- `python -m py_compile bingo_game/ui/finestra_gioco.py` senza errori
- Commit atomico: `fix(ui): imposta focus iniziale su cartella 1 riga 1 colonna 1 all'avvio`

---

### Fase 2 — Soppressione avvisi timer dopo dichiarazione turno umano

File: `bingo_game/ui/finestra_gioco.py`

Modifiche:
1. In `_on_tick_azione`, dopo `self._ms_trascorsi_azione += self._tick_ms`
   e prima del blocco `if self._durata_finestra_corrente_ms <= 0: return`,
   inserire il guard `if self._comandi.turno_gia_dichiarato(): ...`

Criteri di completamento:
- `python -m py_compile bingo_game/ui/finestra_gioco.py` senza errori
- Commit atomico: `fix(ui): sopprimi avvisi timer turno se umano ha già dichiarato`

---

### Fase 3 — Annuncio passaggio turno bot

File: `bingo_game/ui/finestra_gioco.py`

Modifiche:
1. In `_dichiara_fine_bot`, aggiungere due righe dopo
   `bot.dichiara_fine_fase_azione(premi_gia_assegnati, premi_tipo_chiusi)`.

Criteri di completamento:
- `python -m py_compile bingo_game/ui/finestra_gioco.py` senza errori
- Commit atomico: `fix(ui): annuncia passaggio turno bot durante attesa_reclami`

---

### Fase 4 — Test unitari

File: da creare → `tests/unit/test_finestra_gioco_accessibilita_avvio.py`

Test da implementare:
- `TestFinestraGiocoFocusIniziale`:
  - `test_imposta_focus_iniziale_dispatcha_cartella_1`: verifica che `_dispatch`
    sia chiamato con esito di `imposta_focus_cartella(1)`
  - `test_imposta_focus_iniziale_dispatcha_riga_1`: verifica che `_dispatch`
    sia chiamato con esito di `vai_a_riga(1)`
  - `test_imposta_focus_iniziale_dispatcha_colonna_1`: verifica che `_dispatch`
    sia chiamato con esito di `vai_a_colonna(1)`

- `TestOnTickAzionePostDichiarazione`:
  - `test_nessun_avviso_se_umano_ha_dichiarato`: verifica che `annuncia_avviso_timeout`
    NON venga chiamato quando `turno_gia_dichiarato()` ritorna `True`
  - `test_avviso_emesso_se_umano_non_ha_dichiarato`: verifica che `annuncia_avviso_timeout`
    venga chiamato normalmente quando `turno_gia_dichiarato()` ritorna `False`

- `TestDichiaraFineBotAnnuncio`:
  - `test_annuncio_passaggio_turno_bot`: verifica che `mostra_messaggio_sistema`
    sia chiamato con testo contenente il nome del bot dopo `dichiara_fine_fase_azione`

Criteri di completamento:
- Tutti i test passano con `python -m unittest tests/unit/test_finestra_gioco_accessibilita_avvio -v`
- Commit atomico: `test(ui): copertura fix accessibilità focus iniziale, timer e annuncio bot`

---

## Dipendenze

- `ComandiGiocatoreUmano.turno_gia_dichiarato()` — già presente (v0.9.5)
- `ComandiGiocatoreUmano.imposta_focus_cartella`, `vai_a_riga`, `vai_a_colonna` — già presenti
- `WxRenderer.mostra_messaggio_sistema` — già presente
- Nessuna nuova dipendenza esterna

---

## Rischi

- **Race condition focus NVDA**: se `wx.CallAfter` è troppo rapido, l'annuncio
  della finestra potrebbe essere sovrapposto all'annuncio del focus iniziale.
  Mitigazione: accettabile; NVDA gestisce la coda degli annunci. Se segnalato
  empiricamente, sostituire con `wx.CallLater(100, ...)`.
- **Type hint loose `bot: object`**: l'uso di `getattr` con fallback è il
  pattern sicuro già adottato nel codebase.

---

## Project padre

- Design: `docs/2 - projects/DESIGN_fix_accessibilita_focus_timer_bot.md`
- Report origine: `docs/4 - reports/REPORT_BUG_ACCESSIBILITA_FOCUS_TIMER_BOT_2026-04-05.md`
