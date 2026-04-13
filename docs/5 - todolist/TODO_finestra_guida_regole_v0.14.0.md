---
type: todo
feature: finestra_guida_regole
agent: Agent-Plan
status: NOT_STARTED
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

## Fase A — Creazione `bingo_game/ui/locales/it_guida.py`

**File**: `bingo_game/ui/locales/it_guida.py` (CREATE)

- [ ] File creato con docstring e `from __future__ import annotations`
- [ ] Import `MappingProxyType` da `types`
- [ ] Import `Sequence` da `collections.abc`
- [ ] `GUIDA_CAPITOLI` definito come `Sequence[tuple[str, tuple[str, ...]]]`
- [ ] Capitolo 1 "Introduzione alla Tombola" con testo definitivo
- [ ] Capitolo 2 "La cartella" con testo definitivo
- [ ] Capitolo 3 "I premi in ordine" con testo definitivo
- [ ] Capitolo 4 "Come si svolge un turno" con testo definitivo
- [ ] Capitolo 5 "I bot avversari" con testo definitivo
- [ ] `GUIDA_UI` definito come `MappingProxyType[str, str]`
- [ ] Chiave "TITOLO_FINESTRA": "Guida alle regole del gioco"
- [ ] Chiave "BTN_PRECEDENTE": "Precedente"
- [ ] Chiave "BTN_SUCCESSIVO": "Successivo"
- [ ] Chiave "BTN_CHIUDI": "Chiudi"
- [ ] Chiave "ANNUNCIO_PAGINA": "Pagina {corrente} di {totale}"
- [ ] `py_compile` senza errori
- [ ] `mypy` senza errori

---

## Fase B — Creazione `bingo_game/ui/finestra_guida_regole.py` e test

**File**: `bingo_game/ui/finestra_guida_regole.py` (CREATE)

- [ ] Docstring con path, scopo, apertura, chiusura e focus
- [ ] `from __future__ import annotations`
- [ ] Import `wx`, import `logging`, import `GUIDA_CAPITOLI` e `GUIDA_UI` da `it_guida`
- [ ] Classe `FinestraGuidaRegole(wx.Dialog)` definita
- [ ] `__init__(self, parent: wx.Window) -> None` con super().__init__ corretto
- [ ] `self._indice_corrente: int = 0` inizializzato
- [ ] `_build_ui()` chiamato in `__init__`
- [ ] `_aggiorna_visualizzazione()` chiamato in `__init__`
- [ ] `self.Centre()` chiamato in `__init__`
- [ ] Bind `EVT_SHOW` a `_on_show` in `__init__`
- [ ] `_build_ui`: `self._lbl_titolo` (wx.StaticText) creato
- [ ] `_build_ui`: `self._testo` (wx.TextCtrl multilinea read-only) creato con size (520, 300)
- [ ] `_build_ui`: `self._btn_precedente` (wx.Button) creato
- [ ] `_build_ui`: `self._lbl_pagina` (wx.StaticText) creato
- [ ] `_build_ui`: `self._btn_successivo` (wx.Button) creato
- [ ] `_build_ui`: `self._btn_chiudi` (wx.Button, id=wx.ID_CANCEL) creato
- [ ] `_build_ui`: layout BoxSizer(VERTICAL) con sizer navigazione HORIZONTAL
- [ ] `_build_ui`: StdDialogButtonSizer per _btn_chiudi
- [ ] `_build_ui`: SetSizerAndFit chiamato
- [ ] `_build_ui`: binding EVT_BUTTON per i tre pulsanti
- [ ] `_aggiorna_visualizzazione`: aggiorna _lbl_titolo, _testo, _lbl_pagina
- [ ] `_aggiorna_visualizzazione`: abilita/disabilita _btn_precedente correttamente
- [ ] `_aggiorna_visualizzazione`: abilita/disabilita _btn_successivo correttamente
- [ ] `_vai_pagina_precedente`: decrementa indice, aggiorna, wx.CallAfter(_lbl_titolo.SetFocus)
- [ ] `_vai_pagina_successiva`: incrementa indice, aggiorna, wx.CallAfter(_lbl_titolo.SetFocus)
- [ ] `_on_chiudi`: EndModal(wx.ID_CANCEL)
- [ ] `_on_show`: SetFocus su _testo se IsShown(); event.Skip()
- [ ] `py_compile` senza errori
- [ ] `mypy --strict` senza errori

**File**: `tests/ui/test_finestra_guida_regole.py` (CREATE)

- [ ] setUpClass: `wx.App(False)` creato
- [ ] tearDownClass: app distrutta
- [ ] setUp: `wx.Frame(None)` come parent, `FinestraGuidaRegole(parent)` instanziato
- [ ] tearDown: dialog e parent distrutti
- [ ] T1 `test_dialog_istanziazione_senza_eccezioni` — verde
- [ ] T2 `test_dialog_titolo_corretto` — verde
- [ ] T3 `test_dialog_contiene_text_ctrl_readonly` — verde
- [ ] T4 `test_dialog_contiene_pulsante_chiudi` — verde
- [ ] T5 `test_dialog_contiene_pulsante_precedente` — verde
- [ ] T6 `test_dialog_contiene_pulsante_successivo` — verde
- [ ] T7 `test_dialog_precedente_disabilitato_prima_pagina` — verde
- [ ] T8 `test_dialog_successivo_abilitato_prima_pagina` — verde
- [ ] T9 `test_dialog_capitolo_1_visibile_all_apertura` — verde
- [ ] T10 `test_dialog_navigazione_successivo` — verde
- [ ] T11 `test_dialog_cinque_capitoli_disponibili` — verde
- [ ] T12 `test_dialog_successivo_disabilitato_ultima_pagina` — verde
- [ ] Suite esistente non degradata (zero regressioni)

**Commit 1**: `feat(ui): aggiunge FinestraGuidaRegole e it_guida.py`

---

## Fase C — Integrazione binding e collegamento menu

**File**: `bingo_game/ui/finestra_gioco.py` (MODIFY)

- [ ] Import `FinestraGuidaRegole` aggiunto (o lazy in _on_char_hook)
- [ ] Variabile `shift = event.ShiftDown()` presente in `_on_char_hook`
- [ ] Ramo `Ctrl+Shift+H` aggiunto dopo il ramo `Ctrl+I`
- [ ] Sequenza nel ramo: `dlg.ShowModal()` -> `dlg.Destroy()` -> `SetFocus()` su pannello griglia
- [ ] Nessuna hotkey esistente rimossa o spostata
- [ ] `py_compile` senza errori

**File**: `bingo_game/ui/finestra_principale.py` (MODIFY)

- [ ] `_on_guida()`: placeholder sostituito con apertura FinestraGuidaRegole
- [ ] Import lazy di FinestraGuidaRegole nel corpo del metodo
- [ ] Sequenza nel metodo: crea dlg, ShowModal(), Destroy()
- [ ] `py_compile` senza errori

**File**: `bingo_game/ui/finestra_aiuto_tasti_rapidi.py` (MODIFY)

- [ ] Riga `Ctrl+Shift+H — apri la guida alle regole del gioco` aggiunta
      nella sezione CATEGORIA C del testo _CONTENUTO_TASTI_RAPIDI,
      dopo la riga relativa a Ctrl+H

**Verifica integrazioni**:

- [ ] Suite test UI esistente non degradata (zero regressioni)
- [ ] Suite test completa non degradata (zero regressioni)

**Commit 2**: `feat(ui): integra Ctrl+Shift+H e collegamento menu guida`

---

## Fase D — Aggiornamento documentazione e changelog

**File**: `docs/API.md` (MODIFY)

- [ ] Voce `FinestraGuidaRegole` aggiunta nel layer Presentazione
- [ ] Voce `it_guida.py` aggiunta nel layer Presentazione

**File**: `CHANGELOG.md` (MODIFY)

- [ ] Entry per FinestraGuidaRegole aggiunta in [Unreleased] / Added
- [ ] Entry per it_guida.py aggiunta in [Unreleased] / Added

**Commit 3**: `docs: aggiorna API.md e CHANGELOG per FinestraGuidaRegole v0.14.0`

---

## Gate di completamento (verifica finale)

- [ ] Ctrl+Shift+H apre il dialog durante una partita in corso
- [ ] Ctrl+G apre il dialog dal menu principale
- [ ] NVDA annuncia il titolo del dialog all'apertura
- [ ] NVDA legge il titolo del capitolo a ogni cambio pagina
- [ ] Escape chiude il dialog in qualsiasi stato e pagina
- [ ] Alla chiusura da FinestraGioco il focus torna alla griglia
- [ ] Ctrl+H apre ancora FinestraAiutoTastiRapidi (nessuna regressione)
- [ ] Suite CI completamente verde (12 test nuovi + zero regressioni)
- [ ] Smoke test manuale superato
