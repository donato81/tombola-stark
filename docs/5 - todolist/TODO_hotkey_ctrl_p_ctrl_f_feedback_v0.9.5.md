---
type: todo
feature: hotkey_ctrl_p_ctrl_f_feedback
agent: Agent-Plan
status: DONE
version: v0.9.5
plan_ref: docs/3 - coding plans/PLAN_hotkey_ctrl_p_ctrl_f_feedback_v0.9.5.md
date: 2026-04-05
---

# TODO — hotkey_ctrl_p_ctrl_f_feedback v0.9.5

Piano di riferimento: [PLAN_hotkey_ctrl_p_ctrl_f_feedback_v0.9.5.md](../3%20-%20coding%20plans/PLAN_hotkey_ctrl_p_ctrl_f_feedback_v0.9.5.md)

Istruzioni per Agent-Code: esegui le fasi in ordine sequenziale.
Ogni fase è atomica e committable separatamente.
Aggiorna questa checklist marcando `[x]` dopo ogni commit verificato.
Non procedere alla fase successiva prima che i criteri di completamento
della fase corrente siano soddisfatti (py_compile + test di fase).

---

## Fase 1 — Aggiungere `turno_gia_dichiarato` nel boundary applicativo

File: `bingo_game/comandi_partita.py`

- [x] Aggiungere metodo `turno_gia_dichiarato(self) -> bool` in `ComandiGiocatoreUmano`
      (None-safe: ritorna `False` se `self._giocatore is None`)
- [x] Verificare `python -m py_compile bingo_game/comandi_partita.py` senza errori
- [ ] Commit atomico: `fix(comandi): aggiungere turno_gia_dichiarato in ComandiGiocatoreUmano`

---

## Fase 2 — Correggere `_on_pulsante_principale` per Ctrl+P

File: `bingo_game/ui/finestra_gioco.py`

- [x] Sostituire il blocco accesso diretto a `umano` nel branch `attesa_reclami`
      con le chiamate a `self._comandi.turno_gia_dichiarato()` e
      `self._comandi.dichiara_fine_turno(self._partita)`
- [x] Aggiungere `mostra_messaggio_sistema("Turno dichiarato concluso. Attendo gli altri giocatori.")`
      nel percorso di prima dichiarazione
- [x] Aggiungere `mostra_messaggio_sistema("Hai già dichiarato la fine del tuo turno. Attendo gli altri giocatori.")`
      nel percorso idempotente
- [x] Verificare che `_controlla_tutti_pronti()` sia chiamato in entrambi i rami
- [x] Verificare `python -m py_compile bingo_game/ui/finestra_gioco.py` senza errori
- [ ] Commit atomico: `fix(ui): Ctrl+P usa boundary e emette feedback immediato in attesa_reclami`

---

## Fase 3 — Correggere `DialogoRicercaNumero` per Ctrl+F

File: `bingo_game/ui/dialogo_ricerca.py`

- [x] Aggiungere `self._lbl_risultato: wx.StaticText` in `_build_ui`
      (label iniziale vuota, posizionato sotto il pulsante Cerca)
- [x] Aggiungere pulsante "Chiudi" che esegue `self.EndModal(wx.ID_CANCEL)`
- [x] Aumentare dimensioni dialog da `(300, 160)` a `(300, 230)` circa
- [x] In `_on_cerca`, rimuovere `self.EndModal(wx.ID_OK)` dalla fine del metodo
- [x] In `_on_cerca`, dopo `render_esito(esito)`, chiamare
      `self._lbl_risultato.SetLabel(testo_esito)` con testo appropriato
- [x] Aggiornare il docstring della classe rimuovendo il riferimento alla
      "chiusura automatica" e descrivendo il nuovo comportamento persistente
- [x] Verificare `python -m py_compile bingo_game/ui/dialogo_ricerca.py` senza errori
- [ ] Commit atomico: `fix(ui): DialogoRicercaNumero persistente con area risultato accessibile`

---

## Fase 4 — Test unitari sui comportamenti accessibili

### Fase 4a — test_umano_dichiara_fine_turno.py (MODIFY)

- [x] Aggiungere classe `TestComandiGiocatoreUmanoDichiarazioneTurno`
- [x] Test `test_turno_gia_dichiarato_false_prima_di_dichiarare`
- [x] Test `test_turno_gia_dichiarato_true_dopo_dichiarare`
- [x] Test `test_turno_gia_dichiarato_senza_giocatore_ritorna_false`
- [x] Verificare `python -m unittest tests/unit/test_umano_dichiara_fine_turno -v`

### Fase 4b — test_finestra_gioco_shortcuts.py (MODIFY)

- [x] Test `test_ctrl_p_attesa_reclami_emette_conferma_prima_dichiarazione`
- [x] Test `test_ctrl_p_attesa_reclami_emette_messaggio_idempotente`
- [x] Verifica `_controlla_tutti_pronti` chiamato in entrambi i test
- [x] Verificare `python -m unittest tests/unit/test_finestra_gioco_shortcuts -v`

### Fase 4c — test_dialogo_ricerca_persistente.py (CREATE)

- [x] Creare file con pattern `__new__` + `@unittest.skipIf(wx is None, ...)`
- [x] Test `test_on_cerca_non_chiama_end_modal`
- [x] Test `test_on_cerca_aggiorna_lbl_risultato`
- [x] Verificare `python -m unittest tests/unit/test_dialogo_ricerca_persistente -v`
- [ ] Commit atomico: `test(ui): copertura comportamenti accessibili hotkey Ctrl+P e Ctrl+F`

---

## Validazione finale

- [x] `python -m unittest tests/unit/test_ciclo_turno_v2_bot_declaration -v` (regressione)
- [x] `python -m unittest tests/unit/test_ciclo_turno_v2_tutti_pronti -v` (regressione)
- [x] `python -m unittest tests/unit/test_ciclo_turno_v2_timeout_umano -v` (regressione)
- [x] Nessun test esistente regredisce
- [x] CHANGELOG.md aggiornato con voce `Fixed` in `[Unreleased]`
