---
type: todo
feature: finestra_aiuto_tasti_rapidi
agent: Agent-Plan
status: IN_PROGRESS
version: v0.13.0
plan_ref: docs/3 - coding plans/PLAN_finestra_aiuto_tasti_rapidi_v0.13.0.md
date: 2026-04-13
---

# TODO — Finestra aiuto tasti rapidi v0.13.0

**Piano di riferimento**: [PLAN_finestra_aiuto_tasti_rapidi_v0.13.0.md](../3%20-%20coding%20plans/PLAN_finestra_aiuto_tasti_rapidi_v0.13.0.md)

---

## Istruzioni per Agent-Code

Lavora fase per fase nell'ordine indicato. Ogni fase è atomica.
Prima di iniziare una fase verifica che la precedente sia marcata `[x]`.
Al termine di Fase 3, esegui il Commit 1 e segnalami.
Al termine di Fase 4, esegui il Commit 2 e segnalami.

---

## Fase 1 — Creazione `FinestraAiutoTastiRapidi`

**File**: `bingo_game/ui/finestra_aiuto_tasti_rapidi.py` (CREATE)

- [x] Classe `FinestraAiutoTastiRapidi(wx.Dialog)` creata
- [x] `__init__` con titolo `"Tasti rapidi"` e stile `wx.DEFAULT_DIALOG_STYLE`
- [x] `wx.TextCtrl` multilinea read-only (`wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL`)
- [x] Contenuto statico delle scorciatoie inserito (sezioni Categoria A, B, C)
- [x] Pulsante Chiudi con `id=wx.ID_CANCEL`
- [x] Layout con `wx.BoxSizer(wx.VERTICAL)` + `wx.StdDialogButtonSizer`
- [x] `SetSizerAndFit(sizer)` chiamato
- [x] Bind `EVT_BUTTON` → `_on_chiudi` (chiama `EndModal(wx.ID_CANCEL)`)
- [x] Bind `EVT_SHOW` → `_on_show` (imposta focus su TextCtrl se `IsShown()`)

---

## Fase 2 — Hook `Ctrl+H` in `FinestraGioco`

**File**: `bingo_game/ui/finestra_gioco.py` (MODIFY)

- [x] Import `FinestraAiutoTastiRapidi` aggiunto
- [x] Ramo `Ctrl+H` aggiunto in `_on_char_hook` (o dispatcher equivalente)
- [x] Sequenza: `dlg.ShowModal()` → `dlg.Destroy()` → `SetFocus()` su pannello griglia
- [x] Attributo `_pannello_griglia` verificato nel codice esistente
- [x] Nessuna hotkey esistente toccata o spostata

---

## Fase 3 — Suite test unitari UI

**File**: `tests/ui/test_finestra_aiuto_tasti_rapidi.py` (CREATE)

 - [x] `setUpClass` crea `wx.App(False)`
 - [x] `tearDownClass` distrugge l'app
 - [x] `setUp` crea `wx.Frame(None)` come parent e istanzia il dialog
 - [x] `tearDown` distrugge dialog e parent
 - [x] T1 `test_dialog_istanziazione_senza_eccezioni` — verde
 - [x] T2 `test_dialog_titolo_corretto` — verde
 - [x] T3 `test_dialog_contiene_text_ctrl_readonly` — verde
 - [x] T4 `test_dialog_contiene_pulsante_chiudi` — verde
 - [x] T5 `test_dialog_contenuto_testo_non_vuoto` — verde
 - [x] T6 `test_dialog_stile_default_dialog` — verde
 - [x] Suite esistente non degradata (gli elementi della suite target non sono stati degradati)

### Risultati eseguiti

- **UI tests**: 8 passed
- **shortcut/unit**: 24 passed
- **validate_gates (globali)**: presenti errori storici noti, fuori perimetro di questa feature
- **Validazione manuale NVDA**: non eseguita (manual smoke test non ancora svolto)

**Commit 1**: `feat(ui): aggiunge FinestraAiutoTastiRapidi con hook Ctrl+H`

---

## Fase 4 — Sync documentazione e changelog

**File**: `docs/API.md` (MODIFY)
**File**: `CHANGELOG.md` (MODIFY)

- [x] `docs/API.md`: voce `FinestraAiutoTastiRapidi` aggiunta nel layer Presentazione
- [x] `CHANGELOG.md`: entry `### Added` in `[Unreleased]` aggiunta

**Commit 2**: `docs: aggiorna API.md e CHANGELOG per FinestraAiutoTastiRapidi v0.13.0`

---

## Gate di completamento (verifica finale)

- [ ] Dialog apre con `Ctrl+H` da partita in corso
- [ ] NVDA annuncia titolo e legge il testo senza markup anomali
- [ ] `Escape` chiude il dialog e il focus torna alla griglia
- [ ] Pulsante Chiudi: stessa chiusura di Escape
- [ ] Suite CI completamente verde
- [ ] Smoke test manuale superato
