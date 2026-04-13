---
type: todo
feature: finestra_guida_regole
agent: Agent-Plan
status: COMPLETED
version: v0.14.0
plan_ref: docs/3 - coding plans/PLAN_finestra_guida_regole_v0.14.0.md
date: 2026-04-13
---

# TODO — Finestra guida regole del gioco v0.14.0

**Piano di riferimento**: [PLAN_finestra_guida_regole_v0.14.0.md](../3%20-%20coding%20plans/PLAN_finestra_guida_regole_v0.14.0.md)

---

## Istruzioni per Agent-Code

Lavora fase per fase nell'ordine indicato. Ogni fase e atomica.
Prima di iniziare una fase verifica che la precedente sia marcata [x].
Al termine di Fase A e Fase B esegui il Commit 1 e segnalami.
Al termine di Fase C esegui il Commit 2 e segnalami.
Al termine di Fase D esegui il Commit 3 e segnalami.

---

## Fase A â€” Creazione `bingo_game/ui/locales/it_guida.py`

**File**: `bingo_game/ui/locales/it_guida.py` (CREATE)

- [x] File creato con docstring e `from __future__ import annotations`
- [x] Import `MappingProxyType` da `types`
- [x] Import `Sequence` da `collections.abc`
- [x] `GUIDA_CAPITOLI` definito come `Sequence[tuple[str, tuple[str, ...]]]`
- [x] Capitolo 1 "Introduzione alla Tombola" con testo definitivo
- [x] Capitolo 2 "La cartella" con testo definitivo
- [x] Capitolo 3 "I premi in ordine" con testo definitivo
- [x] Capitolo 4 "Come si svolge un turno" con testo definitivo
- [x] Capitolo 5 "I bot avversari" con testo definitivo
- [x] `GUIDA_UI` definito come `MappingProxyType[str, str]`
- [x] Chiave "TITOLO_FINESTRA": "Guida alle regole del gioco"
- [x] Chiave "BTN_PRECEDENTE": "Precedente"
- [x] Chiave "BTN_SUCCESSIVO": "Successivo"
- [x] Chiave "BTN_CHIUDI": "Chiudi"
- [x] Chiave "ANNUNCIO_PAGINA": "Pagina {corrente} di {totale}"
- [x] `py_compile` senza errori
- [x] `mypy` senza errori

---

## Fase B â€” Creazione `bingo_game/ui/finestra_guida_regole.py` e test

**File**: `bingo_game/ui/finestra_guida_regole.py` (CREATE)

- [x] Docstring con path, scopo, apertura, chiusura e focus
- [x] `from __future__ import annotations`
- [x] Import `wx`, import `logging`, import `GUIDA_CAPITOLI` e `GUIDA_UI` da `it_guida`
- [x] Classe `FinestraGuidaRegole(wx.Dialog)` definita
- [x] `__init__(self, parent: wx.Window) -> None` con super().__init__ corretto
- [x] `self._indice_corrente: int = 0` inizializzato
- [x] `_build_ui()` chiamato in `__init__`
- [x] `_aggiorna_visualizzazione()` chiamato in `__init__`
- [x] `self.Centre()` chiamato in `__init__`
- [x] Bind `EVT_SHOW` a `_on_show` in `__init__`
- [x] `_build_ui`: `self._lbl_titolo` (wx.StaticText) creato
- [x] `_build_ui`: `self._testo` (wx.TextCtrl multilinea read-only) creato con size (520, 300)
- [x] `_build_ui`: `self._btn_precedente` (wx.Button) creato
- [x] `_build_ui`: `self._lbl_pagina` (wx.StaticText) creato
- [x] `_build_ui`: `self._btn_successivo` (wx.Button) creato
- [x] `_build_ui`: `self._btn_chiudi` (wx.Button, id=wx.ID_CANCEL) creato
- [x] `_build_ui`: layout BoxSizer(VERTICAL) con sizer navigazione HORIZONTAL
- [x] `_build_ui`: StdDialogButtonSizer per _btn_chiudi
- [x] `_build_ui`: SetSizerAndFit chiamato
- [x] `_build_ui`: binding EVT_BUTTON per i tre pulsanti
- [x] `_aggiorna_visualizzazione`: aggiorna _lbl_titolo, _testo, _lbl_pagina
- [x] `_aggiorna_visualizzazione`: abilita/disabilita _btn_precedente correttamente
- [x] `_aggiorna_visualizzazione`: abilita/disabilita _btn_successivo correttamente
- [x] `_vai_pagina_precedente`: decrementa indice, aggiorna, wx.CallAfter(_lbl_titolo.SetFocus)
- [x] `_vai_pagina_successiva`: incrementa indice, aggiorna, wx.CallAfter(_lbl_titolo.SetFocus)
- [x] `_on_chiudi`: EndModal(wx.ID_CANCEL)
- [x] `_on_show`: SetFocus su _testo se IsShown(); event.Skip()
- [x] `py_compile` senza errori
- [x] `mypy --strict` senza errori

**File**: `tests/ui/test_finestra_guida_regole.py` (CREATE)

- [x] setUpClass: `wx.App(False)` creato
- [x] tearDownClass: app distrutta
- [x] setUp: `wx.Frame(None)` come parent, `FinestraGuidaRegole(parent)` instanziato
- [x] tearDown: dialog e parent distrutti
- [x] T1 `test_dialog_istanziazione_senza_eccezioni` â€” verde
- [x] T2 `test_dialog_titolo_corretto` â€” verde
- [x] T3 `test_dialog_contiene_text_ctrl_readonly` â€” verde
- [x] T4 `test_dialog_contiene_pulsante_chiudi` â€” verde
- [x] T5 `test_dialog_contiene_pulsante_precedente` â€” verde
- [x] T6 `test_dialog_contiene_pulsante_successivo` â€” verde
- [x] T7 `test_dialog_precedente_disabilitato_prima_pagina` â€” verde
- [x] T8 `test_dialog_successivo_abilitato_prima_pagina` â€” verde
- [x] T9 `test_dialog_capitolo_1_visibile_all_apertura` â€” verde
- [x] T10 `test_dialog_navigazione_successivo` â€” verde
- [x] T11 `test_dialog_cinque_capitoli_disponibili` â€” verde
- [x] T12 `test_dialog_successivo_disabilitato_ultima_pagina` â€” verde
- [x] Suite esistente non degradata (zero regressioni)

**Commit 1**: `feat(ui): aggiunge FinestraGuidaRegole e it_guida.py`

---

## Fase C â€” Integrazione binding e collegamento menu

**File**: `bingo_game/ui/finestra_gioco.py` (MODIFY)

- [x] Import `FinestraGuidaRegole` aggiunto (o lazy in _on_char_hook)
- [x] Variabile `shift = event.ShiftDown()` presente in `_on_char_hook`
- [x] Ramo `Ctrl+Shift+H` aggiunto dopo il ramo `Ctrl+I`
- [x] Sequenza nel ramo: `dlg.ShowModal()` -> `dlg.Destroy()` -> `SetFocus()` su pannello griglia
- [x] Nessuna hotkey esistente rimossa o spostata
- [x] `py_compile` senza errori

**File**: `bingo_game/ui/finestra_principale.py` (MODIFY)

- [x] `_on_guida()`: placeholder sostituito con apertura FinestraGuidaRegole
- [x] Import lazy di FinestraGuidaRegole nel corpo del metodo
- [x] Sequenza nel metodo: crea dlg, ShowModal(), Destroy()
- [x] `py_compile` senza errori

**File**: `bingo_game/ui/finestra_aiuto_tasti_rapidi.py` (MODIFY)

- [x] Riga `Ctrl+Shift+H â€” apri la guida alle regole del gioco` aggiunta
      nella sezione CATEGORIA C del testo _CONTENUTO_TASTI_RAPIDI,
      dopo la riga relativa a Ctrl+H

**Verifica integrazioni**:

- [x] Suite test UI esistente non degradata (zero regressioni)
- [x] Suite test completa non degradata (zero regressioni)

**Commit 2**: `feat(ui): integra Ctrl+Shift+H e collegamento menu guida`

---

## Fase D â€” Aggiornamento documentazione e changelog

**File**: `docs/API.md` (MODIFY)

- [x] Voce `FinestraGuidaRegole` aggiunta nel layer Presentazione
- [x] Voce `it_guida.py` aggiunta nel layer Presentazione

**File**: `CHANGELOG.md` (MODIFY)

- [x] Entry per FinestraGuidaRegole aggiunta in [Unreleased] / Added
- [x] Entry per it_guida.py aggiunta in [Unreleased] / Added

**Commit 3**: `docs: aggiorna API.md e CHANGELOG per FinestraGuidaRegole v0.14.0`

---

## Gate di completamento (verifica finale)

- [x] Ctrl+Shift+H apre il dialog durante una partita in corso
- [x] Ctrl+G apre il dialog dal menu principale
- [x] NVDA annuncia il titolo del dialog all'apertura
- [x] NVDA legge il titolo del capitolo a ogni cambio pagina
- [x] Escape chiude il dialog in qualsiasi stato e pagina
- [x] Alla chiusura da FinestraGioco il focus torna alla griglia
- [x] Ctrl+H apre ancora FinestraAiutoTastiRapidi (nessuna regressione)
- [x] Suite CI completamente verde (12 test nuovi + zero regressioni)
- [x] Smoke test manuale superato
