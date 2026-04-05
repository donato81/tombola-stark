---
type: todo
feature: fix_accessibilita_focus_timer_bot
agent: Agent-Plan
status: DONE
version: v0.9.5
plan_ref: docs/3 - coding plans/PLAN_fix_accessibilita_focus_timer_bot_v0.9.5.md
date: 2026-04-05
---

# TODO — fix_accessibilita_focus_timer_bot v0.9.5

Piano di riferimento: [PLAN_fix_accessibilita_focus_timer_bot_v0.9.5.md](../3%20-%20coding%20plans/PLAN_fix_accessibilita_focus_timer_bot_v0.9.5.md)

Istruzioni per Agent-Code: esegui le fasi in ordine sequenziale.
Ogni fase è atomica e committable separatamente.
Aggiorna questa checklist marcando `[x]` dopo ogni commit verificato.
Non procedere alla fase successiva prima che i criteri di completamento
della fase corrente siano soddisfatti (`py_compile` + test di fase).

---

## Fase 1 — Fix focus iniziale cartella 1/riga 1/colonna 1

File: `bingo_game/ui/finestra_gioco.py`

- [x] In `FinestraGioco.__init__`, aggiungere `wx.CallAfter(self._imposta_focus_iniziale)`
      dopo `self._pannello_griglia.SetFocus()`
- [x] Aggiungere il metodo privato `_imposta_focus_iniziale(self) -> None`
      nella sezione Helper interni (dopo `_ottieni_numero_in_focus`)
- [x] Verificare `python -m py_compile bingo_game/ui/finestra_gioco.py` senza errori
- [x] Commit atomico: `fix(ui): imposta focus iniziale su cartella 1 riga 1 colonna 1 all'avvio`

---

## Fase 2 — Soppressione avvisi timer dopo dichiarazione turno umano

File: `bingo_game/ui/finestra_gioco.py`

- [x] In `_on_tick_azione`, aggiungere il guard `if self._comandi.turno_gia_dichiarato():`
      dopo `self._ms_trascorsi_azione += self._tick_ms`
      e prima del blocco `if self._durata_finestra_corrente_ms <= 0: return`
- [x] Verificare che il guard chiami `_on_timeout_azione()` se il timer è scaduto
      e poi faccia `return` senza emettere avvisi
- [x] Verificare `python -m py_compile bingo_game/ui/finestra_gioco.py` senza errori
- [x] Commit atomico: `fix(ui): sopprimi avvisi timer turno se umano ha già dichiarato`

---

## Fase 3 — Annuncio passaggio turno bot

File: `bingo_game/ui/finestra_gioco.py`

- [x] In `_dichiara_fine_bot`, aggiungere dopo `bot.dichiara_fine_fase_azione(...)`:
      `nome_bot: str = getattr(bot, "nome", "Bot")`
      `self._renderer.mostra_messaggio_sistema(f"{nome_bot} ha passato il turno.")`
- [x] Verificare `python -m py_compile bingo_game/ui/finestra_gioco.py` senza errori
- [x] Commit atomico: `fix(ui): annuncia passaggio turno bot durante attesa_reclami`

---

## Fase 4 — Test unitari

File: `tests/unit/test_finestra_gioco_accessibilita_avvio.py` (CREA)

### Fase 4a — Focus iniziale

- [x] Classe `TestFinestraGiocoFocusIniziale`
- [x] `test_imposta_focus_iniziale_dispatcha_cartella_1`
- [x] `test_imposta_focus_iniziale_dispatcha_riga_1`
- [x] `test_imposta_focus_iniziale_dispatcha_colonna_1`

### Fase 4b — Soppressione avvisi timer

- [x] Classe `TestOnTickAzionePostDichiarazione`
- [x] `test_nessun_avviso_se_umano_ha_dichiarato`
- [x] `test_avviso_emesso_se_umano_non_ha_dichiarato`

### Fase 4c — Annuncio bot

- [x] Classe `TestDichiaraFineBotAnnuncio`
- [x] `test_annuncio_passaggio_turno_bot`
- [x] Verificare `python -m unittest tests/unit/test_finestra_gioco_accessibilita_avvio -v`
- [x] Commit atomico: `test(ui): copertura fix accessibilità focus iniziale, timer e annuncio bot`
