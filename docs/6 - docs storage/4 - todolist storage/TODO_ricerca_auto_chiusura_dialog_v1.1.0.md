---
type: todo
feature: ricerca_auto_chiusura_dialog
agent: Agent-Plan
status: DRAFT
version: v1.1.0
plan_ref: docs/3 - coding plans/PLAN_ricerca_auto_chiusura_dialog_v1.1.0.md
design_ref: docs/2 - projects/DESIGN_ricerca_auto_chiusura_dialog_v1.1.0.md
date: 2026-04-09
---

# TODO — Auto-chiusura dialog ricerca numero (Ctrl+F) v1.1.0

Piano di riferimento (fonte di verità):
[PLAN_ricerca_auto_chiusura_dialog_v1.1.0.md](../3%20-%20coding%20plans/PLAN_ricerca_auto_chiusura_dialog_v1.1.0.md)

---

## Istruzioni per Agent-Code

Esegui le fasi nell'ordine indicato. Ogni fase corrisponde a un commit atomico.
Prima di ogni commit esegui `python -m py_compile` sul file modificato.
Non procedere alla fase successiva se il compile fallisce.
Riferiti al PLAN per le specifiche tecniche dettagliate di ogni operazione.

---

## Checklist operativa

- [x] **FASE 1** — Modifica `bingo_game/ui/dialogo_ricerca.py`
  - [x] Verificare che `Any` sia importato da `typing` (aggiungere se assente)
  - [x] In `__init__`, dopo `self._comandi = comandi`, aggiungere: `self._primo_risultato: Optional[Any] = None`
  - [x] In `_on_cerca()`, rimuovere la riga finale `self._input_ctrl.SetFocus()`
  - [x] In `_on_cerca()`, aggiungere import lazy: `from bingo_game.events.eventi_output_ui_umani import EventoRicercaNumeroInCartelle`
  - [x] In `_on_cerca()`, aggiungere: `evento_ricerca = esito.evento if hasattr(esito, "evento") else None`
  - [x] In `_on_cerca()`, aggiungere blocco `if isinstance(evento_ricerca, EventoRicercaNumeroInCartelle) and evento_ricerca.esito == "trovato":`
  - [x] Dentro il ramo `if trovato`: `self._primo_risultato = evento_ricerca.risultati[0]`
  - [x] Dentro il ramo `if trovato`: `ritardo_ms = 400 + max(0, len(evento_ricerca.risultati) - 1) * 200`
  - [x] Dentro il ramo `if trovato`: `wx.CallLater(ritardo_ms, self.EndModal, wx.ID_OK)`
  - [x] Dentro il ramo `else`: `self._input_ctrl.SetFocus()` (comportamento invariato per non trovato)
  - [x] `python -m py_compile bingo_game/ui/dialogo_ricerca.py` → exit code 0
  - [x] Nessun `print()` nel file
  - [x] Type hints presenti su tutti i metodi modificati
  - [ ] Commit: `fix(ui): dialogo ricerca si chiude automaticamente dopo annuncio risultato`

- [x] **FASE 2** — Modifica `bingo_game/ui/finestra_gioco.py`
  - [x] Verificare che `Any` sia importato da `typing` (aggiungere se assente)
  - [x] In `_apri_ricerca_numero()`, dopo `dlg.ShowModal()`, aggiungere: `primo_risultato = getattr(dlg, "_primo_risultato", None)`
  - [x] In `_apri_ricerca_numero()`, spostare `dlg.Destroy()` dopo la riga `primo_risultato = ...`
  - [x] In `_apri_ricerca_numero()`, sostituire `self._pannello_griglia.SetFocus()` con blocco `if/else`:
    - se `primo_risultato is not None`: chiama `self._naviga_a_risultato_ricerca(primo_risultato)`
    - altrimenti: `self._pannello_griglia.SetFocus()`
  - [x] Aggiungere nuovo metodo `_naviga_a_risultato_ricerca(self, risultato: Any) -> None` subito dopo `_apri_ricerca_numero`
  - [x] Dentro `_naviga_a_risultato_ricerca`: `self._dispatch(self._comandi.imposta_focus_cartella(risultato.numero_cartella))`
  - [x] Dentro `_naviga_a_risultato_ricerca`: `self._dispatch(self._comandi.vai_a_riga(risultato.indice_riga + 1))`
  - [x] Dentro `_naviga_a_risultato_ricerca`: `self._dispatch(self._comandi.vai_a_colonna(risultato.indice_colonna + 1))`
  - [x] `python -m py_compile bingo_game/ui/finestra_gioco.py` → exit code 0
  - [x] Nessun `print()` nel file
  - [x] Type hints presenti su tutti i metodi modificati
  - [ ] Commit: `fix(ui): FinestraGioco naviga al primo risultato dopo chiusura dialog ricerca`

- [x] **FASE 3** — Aggiorna `tests/unit/test_dialogo_ricerca_persistente.py`
  - [x] Rimuovere il test `test_on_cerca_non_chiama_end_modal` (non più valido)
  - [x] Aggiungere mock di `wx.CallLater` nel metodo `_crea_dialog_stub` (o tramite `unittest.mock.patch`)
  - [x] Aggiungere `test_on_cerca_non_chiama_end_modal_se_non_trovato`:
    - mock `cerca_numero` → `EventoRicercaNumeroInCartelle.non_trovato(...)`
    - verifica: `dialogo.EndModal.assert_not_called()`
  - [x] Aggiungere `test_on_cerca_non_chiama_end_modal_immediatamente_se_trovato`:
    - mock `cerca_numero` → `EventoRicercaNumeroInCartelle.trovato(...)`
    - mock `wx.CallLater` per intercettare senza eseguire
    - verifica: `dialogo.EndModal.assert_not_called()` (EndModal non chiamata direttamente)
  - [x] Aggiungere `test_ritardo_dinamico_1_risultato`:
    - 1 risultato nell'evento → verifica primo argomento di `wx.CallLater` == 400
  - [x] Aggiungere `test_ritardo_dinamico_3_risultati`:
    - 3 risultati nell'evento → verifica primo argomento di `wx.CallLater` == 800
  - [x] Aggiungere `test_primo_risultato_impostato_se_trovato`:
    - verifica che `dialogo._primo_risultato` sia `evento.risultati[0]`
  - [x] Aggiungere `test_primo_risultato_none_se_non_trovato`:
    - verifica che `dialogo._primo_risultato` sia `None` dopo ricerca con esito non trovato
  - [x] `python -m py_compile tests/unit/test_dialogo_ricerca_persistente.py` → exit code 0
  - [x] `py -3.11 -m unittest tests.unit.test_dialogo_ricerca_persistente -v` → tutti i test pass (7 skipped per assenza wx nell'ambiente CI)
  - [ ] Commit: `test(ui): aggiorna e amplia test dialogo ricerca per auto-chiusura`

---

## Verifica manuale finale (post FASE 2)

Prima di considerare il task completato, eseguire questa sequenza manuale in gioco:

**Scenario 1 — 1 risultato trovato:**
1. Avviare la partita con almeno 2 cartelle
2. Premere Ctrl+F, inserire un numero presente in esattamente 1 cartella, premere Invio
3. Ascoltare il risultato vocalizzato da NVDA
4. Verificare: il dialog si chiude da solo entro ~400ms
5. Verificare: il focus è sulla cartella/riga/colonna annunciata

**Scenario 2 — 3 risultati trovati:**
1. Avviare la partita con 6 cartelle (se disponibili)
2. Premere Ctrl+F, inserire un numero presente in più cartelle, premere Invio
3. Ascoltare la lista di risultati vocalizzata
4. Verificare: il dialog si chiude dopo ~800ms (3 risultati) lasciando NVDA finire la lettura
5. Verificare: il focus è sulla cartella del PRIMO risultato (indice cartella più basso)

**Scenario 3 — numero non trovato:**
1. Premere Ctrl+F, inserire il numero 99 (raramente su una cartella), premere Invio
2. Verificare: NVDA annuncia "non trovato"
3. Verificare: il dialog rimane aperto, il focus è sull'input
4. Verificare: ESC chiude il dialog normalmente

*Fine documento TODO*
