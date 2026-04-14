---
type: plan
feature: finestra_aiuto_tasti_rapidi
agent: Agent-Plan
status: READY
version: v0.13.0
design_ref: docs/2 - projects/DESIGN_finestra_aiuto_tasti_rapidi.md
date: 2026-04-13
---

# PLAN — Finestra aiuto tasti rapidi v0.13.0

## 1. Executive Summary

- **Tipo**: Nuova feature UI (presentazione) — accessibilità tastiera
- **Priorità**: Alta — consultazione immediata scorciatoie per utente non vedente
- **Branch**: main
- **Versione target**: v0.13.0
- **Commit attesi**: 2 (implementazione UI + test; poi sync docs + changelog)
- **Design di riferimento**: [DESIGN_finestra_aiuto_tasti_rapidi.md](../2%20-%20projects/DESIGN_finestra_aiuto_tasti_rapidi.md) — REVIEWED

---

## 2. Problema e Obiettivo

`FinestraGioco` espone un ricco set di hotkey (Categorie A, B, C) ma non
offre alcun accesso diretto all'elenco delle scorciatoie dall'interno della
partita. Un utente non vedente che dimentica un tasto deve interrompere la
sessione o consultare documentazione esterna.

**Obiettivo**: introdurre `FinestraAiutoTastiRapidi`, un `wx.Dialog` modale
apribile con `Ctrl+H` da `FinestraGioco`. Il dialog espone contenuto statico
read-only, riceve il focus iniziale sul `wx.TextCtrl` e alla chiusura ripristina
deterministicamente il focus su `PannelloGriglia`. Zero modifiche al dominio,
ai renderer o al sistema di eventi.

---

## 3. File coinvolti

| File | Operazione | Note |
|------|-----------|------|
| `bingo_game/ui/finestra_aiuto_tasti_rapidi.py` | CREATE | Nuovo dialog wx |
| `bingo_game/ui/finestra_gioco.py` | MODIFY | Hook `Ctrl+H` in `_on_char_hook` + focus restore |
| `tests/ui/test_finestra_aiuto_tasti_rapidi.py` | CREATE | Suite unittest UI del dialog |
| `docs/API.md` | MODIFY | Voce `FinestraAiutoTastiRapidi` nel layer Presentazione |
| `CHANGELOG.md` | MODIFY | Entry `### Added` in `[Unreleased]` |

File invariati: `bingo_game/ui/tema.py`, tutti i file del dominio, del layer
applicativo, dei renderer, degli eventi e delle eccezioni.

---

## 4. Fasi implementative

### Fase 1 — Creazione `FinestraAiutoTastiRapidi`

**File coinvolto**: `bingo_game/ui/finestra_aiuto_tasti_rapidi.py` (CREATE)

Operazioni:

1. Definire `class FinestraAiutoTastiRapidi(wx.Dialog)` con:
   - `__init__(self, parent: wx.Window) -> None`:
     - Chiama `super().__init__(parent, title="Tasti rapidi", style=wx.DEFAULT_DIALOG_STYLE)`.
     - Costruisce `self._testo: wx.TextCtrl` multilinea read-only con stile
       `wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL`.
     - Imposta il contenuto statico delle scorciatoie (stringa multi-sezione,
       derivata dal censimento in REPORT_ANALISI_finestra_aiuto_tasti_rapidi_2026-04-12).
     - Costruisce pulsante Chiudi: `wx.Button(self, id=wx.ID_CANCEL, label="Chiudi")`.
     - Assembla layout con `wx.BoxSizer(wx.VERTICAL)` +
       `wx.StdDialogButtonSizer` per il pulsante.
     - Chiama `self.SetSizerAndFit(sizer)`.
     - Bind `wx.EVT_BUTTON` su Chiudi → `_on_chiudi`.
     - Bind `wx.EVT_SHOW` → `_on_show` per assegnare il focus al TextCtrl.
   - `_on_show(self, event: wx.ShowEvent) -> None`:
     - Se `event.IsShown()`: `self._testo.SetFocus()`.
     - Chiama `event.Skip()`.
   - `_on_chiudi(self, event: wx.CommandEvent) -> None`:
     - `self.EndModal(wx.ID_CANCEL)`.
2. Le sezioni del contenuto testuale devono seguire la struttura lineare:
   intestazione, sezione Categoria A, sezione Categoria B, sezione Categoria C,
   nota finale — senza markup, tabelle o simboli non vocalizabili da NVDA.

---

### Fase 2 — Hook `Ctrl+H` in `FinestraGioco`

**File coinvolto**: `bingo_game/ui/finestra_gioco.py` (MODIFY)

Operazioni:

1. Aggiungere in testa agli import UI:
   ```python
   from bingo_game.ui.finestra_aiuto_tasti_rapidi import FinestraAiutoTastiRapidi
   ```
2. Nel metodo che gestisce gli input di tastiera globali (tipicamente
   `_on_char_hook` o il dispatcher delle hotkey di Categoria A),
   aggiungere il ramo per `Ctrl+H` prima del fallthrough a `event.Skip()`:
   ```python
   if key_code == ord("H") and event.ControlDown():
       dlg = FinestraAiutoTastiRapidi(self)
       dlg.ShowModal()
       dlg.Destroy()
       self._pannello_griglia.SetFocus()
       return
   ```
3. Verificare il nome esatto dell'attributo del pannello griglia in `_build_ui`
   e sostituire `self._pannello_griglia` con l'attributo corretto se necessario.

Nota: `ShowModal()` è bloccante; tutti i binding di `FinestraGioco` rimangono
inattivi mentre il dialog è aperto, coerentemente con la decisione D1 del DESIGN.

---

### Fase 3 — Suite test unitari UI

**File coinvolto**: `tests/ui/test_finestra_aiuto_tasti_rapidi.py` (CREATE)

Seguire il pattern esistente in `tests/ui/test_finestra_gioco.py`.

Struttura:

```python
import unittest
import wx

from bingo_game.ui.finestra_aiuto_tasti_rapidi import FinestraAiutoTastiRapidi

class TestFinestraAiutoTastiRapidi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = wx.App(False)

    @classmethod
    def tearDownClass(cls):
        cls.app.Destroy()

    def setUp(self):
        self.parent = wx.Frame(None)
        self.dlg = FinestraAiutoTastiRapidi(self.parent)

    def tearDown(self):
        self.dlg.Destroy()
        self.parent.Destroy()
```

Test da implementare:

1. `test_dialog_istanziazione_senza_eccezioni`: crea il dialog senza errori.
2. `test_dialog_titolo_corretto`: `self.dlg.GetTitle() == "Tasti rapidi"`.
3. `test_dialog_contiene_text_ctrl_readonly`: scansiona i figli del dialog;
   verifica presenza di almeno un `wx.TextCtrl` con stile `wx.TE_READONLY`.
4. `test_dialog_contiene_pulsante_chiudi`: verifica presenza del
   `wx.Button` con `GetId() == wx.ID_CANCEL`.
5. `test_dialog_contenuto_testo_non_vuoto`: il `wx.TextCtrl` ha
   `GetValue()` non vuoto e la stringa contiene le parole chiave
   attese (es. `"Ctrl"`, `"Escape"`, `"Categoria"`).
6. `test_dialog_stile_default_dialog`: verifica che lo stile del dialog
   includa `wx.DEFAULT_DIALOG_STYLE`.

Tutti i test devono essere CI-safe: usare `wx.App(False)` (no display reale),
distruggere frame e dialog in `tearDown` per evitare memory leak nei test.

---

### Fase 4 — Sync documentazione e changelog

**File coinvolto**: `docs/API.md` (MODIFY)

Nella sezione del layer Presentazione (`bingo_game/ui/`), aggiungere:

```
### FinestraAiutoTastiRapidi

- **Percorso**: `bingo_game/ui/finestra_aiuto_tasti_rapidi.py`
- **Tipo**: `wx.Dialog` (modale)
- **Scopo**: espone l'elenco statico delle scorciatoie di gioco in un dialog modale read-only.
- **Apertura**: `Ctrl+H` da `FinestraGioco` (hotkey globale Categoria A).
- **Chiusura**: `Escape` o pulsante Chiudi — entrambi chiamano `EndModal(wx.ID_CANCEL)`.
- **Focus iniziale**: `wx.TextCtrl` multilinea read-only (leggibile riga per riga con NVDA).
- **Focus finale**: `PannelloGriglia` di `FinestraGioco` (ripristino deterministico).
- **Dipendenze**: nessuna dipendenza da dominio, renderer o eventi.
```

**File coinvolto**: `CHANGELOG.md` (MODIFY)

Nella sezione `## [Unreleased]`, sotto `### Added` (crearla se assente):

```
- `FinestraAiutoTastiRapidi`: nuovo `wx.Dialog` modale con elenco statico
  tasti rapidi, apribile con `Ctrl+H` da `FinestraGioco`. Chiusura con
  `Escape` o pulsante Chiudi, focus iniziale sul testo, ripristino focus
  su `PannelloGriglia` alla chiusura.
```

**Commit 2 atteso**: `docs: aggiorna API.md e CHANGELOG per FinestraAiutoTastiRapidi v0.13.0`

---

## 5. Test Plan

### 5.1 Test unitari automatici — `tests/ui/test_finestra_aiuto_tasti_rapidi.py`

| ID | Nome test | Tipo | Verifica |
|----|-----------|------|---------|
| T1 | `test_dialog_istanziazione_senza_eccezioni` | Unit | Nessuna eccezione alla creazione |
| T2 | `test_dialog_titolo_corretto` | Unit | `GetTitle() == "Tasti rapidi"` |
| T3 | `test_dialog_contiene_text_ctrl_readonly` | Unit | TextCtrl con stile `TE_READONLY` |
| T4 | `test_dialog_contiene_pulsante_chiudi` | Unit | Pulsante con `id == wx.ID_CANCEL` |
| T5 | `test_dialog_contenuto_testo_non_vuoto` | Unit | `GetValue()` non vuoto, contiene parole chiave |
| T6 | `test_dialog_stile_default_dialog` | Unit | Stile include `DEFAULT_DIALOG_STYLE` |

### 5.2 Smoke test manuale (non automatizzabile in CI)

- Avviare partita, premere `Ctrl+H` → dialog si apre, NVDA annuncia il titolo
  e legge il `wx.TextCtrl` in focus.
- Usare frecce su/giù e PagSu/PagGiù → navigazione del testo funziona.
- Premere `Tab` → focus si sposta al pulsante Chiudi.
- Premere `Escape` → dialog si chiude, focus torna alla griglia.
- Premere pulsante Chiudi → medesimo comportamento di Escape.
- Aprire il dialog durante una partita in pausa → verificare che le hotkey
  di gioco restino inattive mentre il dialog è aperto.

### 5.3 Test di non-regressione

- Eseguire `pytest tests/` (o `python -m unittest discover tests/`): suite
  esistente deve restare completamente verde.
- Verificare che il ramo `Ctrl+H` in `_on_char_hook` non interferisca con
  le hotkey di Categoria A, B, C già definite.

---

## 6. Gate di completamento

- [ ] `FinestraAiutoTastiRapidi` istanziabile e modale
- [ ] `Ctrl+H` apre il dialog da `FinestraGioco`
- [ ] `Escape` chiude il dialog
- [ ] Pulsante Chiudi chiude il dialog
- [ ] Focus iniziale sul `wx.TextCtrl` read-only
- [ ] Focus ripristinato su `PannelloGriglia` alla chiusura
- [ ] Contenuto statico completo e vocalizabile da NVDA
- [ ] 6 test UI verdi
- [ ] Suite esistente non degradata
- [ ] `docs/API.md` aggiornato
- [ ] `CHANGELOG.md` aggiornato (sezione `[Unreleased]`)
- [ ] Smoke test manuale NVDA superato
