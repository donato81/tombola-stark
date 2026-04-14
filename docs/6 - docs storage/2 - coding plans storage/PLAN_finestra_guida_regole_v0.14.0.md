---
type: plan
feature: finestra_guida_regole
agent: Agent-Plan
status: READY
version: v0.14.0
design_ref: docs/2 - projects/DESIGN_finestra_guida_regole.md
date: 2026-04-13
---

# PLAN — Finestra guida regole del gioco v0.14.0

## 1. Executive Summary

- **Tipo**: Nuova feature UI (presentazione) — accessibilita e contenuto guida
- **Priorita**: Media — migliora l'autonomia dell'utente non vedente
- **Branch**: main
- **Versione target**: v0.14.0
- **Commit attesi**: 3 (fase A+B, fase C, fase D)
- **Design di riferimento**: [DESIGN_finestra_guida_regole.md](../2%20-%20projects/DESIGN_finestra_guida_regole.md) — REVIEWED

---

## 2. Problema e Obiettivo

Il progetto dispone gia di una finestra tasti rapidi (FinestraAiutoTastiRapidi),
ma non ha alcuna guida alle regole del gioco accessibile dall'interno
dell'applicazione. Un utente non vedente alle prime armi con la tombola non ha
un modo per capire cosa sono ambo, terno, quaterna, cinquina, tombola, come
funziona il turno o come gestire i bot, senza consultare documentazione esterna.

**Obiettivo**: introdurre FinestraGuidaRegole, un wx.Dialog modale navigabile
a pagine con i testi definitivi dei cinque capitoli. Il dialog e apribile con
Ctrl+Shift+H da FinestraGioco e con Ctrl+G dal menu principale. I testi risiedono
in it_guida.py, estensibile senza modificare il codice UI.

---

## 3. File coinvolti

| File | Operazione | Note |
|------|-----------|------|
| `bingo_game/ui/locales/it_guida.py` | CREATE | Dizionari GUIDA_CAPITOLI e GUIDA_UI |
| `bingo_game/ui/finestra_guida_regole.py` | CREATE | Dialog modale navigabile a pagine |
| `bingo_game/ui/finestra_gioco.py` | MODIFY | Hook Ctrl+Shift+H in _on_char_hook + import |
| `bingo_game/ui/finestra_principale.py` | MODIFY | Aggiorna _on_guida() + import |
| `bingo_game/ui/finestra_aiuto_tasti_rapidi.py` | MODIFY | Aggiunge riga Ctrl+Shift+H nel contenuto |
| `tests/ui/test_finestra_guida_regole.py` | CREATE | Suite unittest UI del dialog |
| `docs/API.md` | MODIFY | Voce FinestraGuidaRegole nel layer Presentazione |
| `CHANGELOG.md` | MODIFY | Entry Added in [Unreleased] |

File invariati: tutti i file del dominio, del layer applicativo, dei renderer,
degli eventi, delle eccezioni, di tema.py e del file it.py esistente.

---

## 4. Fasi implementative

### Fase A — Creazione `bingo_game/ui/locales/it_guida.py`

**File coinvolto**: `bingo_game/ui/locales/it_guida.py` (CREATE)

Operazioni:

1. Creare il file con intestazione docstring e import from __future__.
2. Definire GUIDA_CAPITOLI come sequenza di tuple (titolo, righe_testo).
   Usare esattamente i cinque capitoli con i testi definitivi trascritti
   dal DESIGN (sezione 7.3). Ogni riga del testo e un elemento della tupla.
3. Definire GUIDA_UI come MappingProxyType con le chiavi:
   - "TITOLO_FINESTRA": "Guida alle regole del gioco"
   - "BTN_PRECEDENTE": "Precedente"
   - "BTN_SUCCESSIVO": "Successivo"
   - "BTN_CHIUDI": "Chiudi"
   - "ANNUNCIO_PAGINA": "Pagina {corrente} di {totale}"
4. Verificare che il file sia importabile senza errori.

Criteri di completamento Fase A:
- Il file esiste in bingo_game/ui/locales/
- GUIDA_CAPITOLI ha esattamente 5 elementi
- I titoli dei cinque capitoli sono esatti come indicati nel DESIGN
- GUIDA_UI ha tutte e cinque le chiavi
- py_compile non segnala errori
- mypy non segnala errori (tipizzazione corretta)

---

### Fase B — Creazione `bingo_game/ui/finestra_guida_regole.py`

**File coinvolto**: `bingo_game/ui/finestra_guida_regole.py` (CREATE)

Operazioni:

1. Definire `class FinestraGuidaRegole(wx.Dialog)` con:

   a. `__init__(self, parent: wx.Window) -> None`:
      - Chiama super().__init__ con title=GUIDA_UI["TITOLO_FINESTRA"]
        e style=wx.DEFAULT_DIALOG_STYLE.
      - Imposta self._indice_corrente: int = 0.
      - Chiama _build_ui().
      - Chiama _aggiorna_visualizzazione().
      - Chiama self.Centre().
      - Bind EVT_SHOW a _on_show.

   b. `_build_ui(self) -> None`:
      - Crea self._lbl_titolo: wx.StaticText con label vuota inizialmente.
      - Crea self._testo: wx.TextCtrl con stile
        wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL e size wx.Size(520, 300).
      - Crea self._btn_precedente: wx.Button con label GUIDA_UI["BTN_PRECEDENTE"].
      - Crea self._lbl_pagina: wx.StaticText con label vuota inizialmente.
      - Crea self._btn_successivo: wx.Button con label GUIDA_UI["BTN_SUCCESSIVO"].
      - Crea self._btn_chiudi: wx.Button con id=wx.ID_CANCEL
        e label GUIDA_UI["BTN_CHIUDI"].
      - Assembla con BoxSizer(VERTICAL):
        - _lbl_titolo (ALL | EXPAND, border 10)
        - _testo (ALL | EXPAND, proporzione 1)
        - BoxSizer(HORIZONTAL) con _btn_precedente, _lbl_pagina, _btn_successivo
        - StdDialogButtonSizer con _btn_chiudi
      - Chiama SetSizerAndFit(sizer).
      - Bind EVT_BUTTON _btn_precedente -> _vai_pagina_precedente.
      - Bind EVT_BUTTON _btn_successivo -> _vai_pagina_successiva.
      - Bind EVT_BUTTON _btn_chiudi -> _on_chiudi.

   c. `_aggiorna_visualizzazione(self) -> None`:
      - Legge titolo, righe = GUIDA_CAPITOLI[self._indice_corrente].
      - Chiama self._lbl_titolo.SetLabel(titolo).
      - Chiama self._testo.SetValue("\n".join(righe)).
      - Calcola totale = len(GUIDA_CAPITOLI).
      - Aggiorna self._lbl_pagina con template GUIDA_UI["ANNUNCIO_PAGINA"]
        sostituendo {corrente} con _indice_corrente + 1 e {totale} con totale.
      - Abilita/disabilita _btn_precedente: Enable(_indice_corrente > 0).
      - Abilita/disabilita _btn_successivo:
        Enable(_indice_corrente < totale - 1).

   d. `_vai_pagina_precedente(self, event: wx.CommandEvent) -> None`:
      - Se self._indice_corrente > 0:
        - Decrementa self._indice_corrente.
        - Chiama self._aggiorna_visualizzazione().
        - Chiama wx.CallAfter(self._lbl_titolo.SetFocus).

   e. `_vai_pagina_successiva(self, event: wx.CommandEvent) -> None`:
      - Se self._indice_corrente < len(GUIDA_CAPITOLI) - 1:
        - Incrementa self._indice_corrente.
        - Chiama self._aggiorna_visualizzazione().
        - Chiama wx.CallAfter(self._lbl_titolo.SetFocus).

   f. `_on_chiudi(self, event: wx.CommandEvent) -> None`:
      - Chiama self.EndModal(wx.ID_CANCEL).

   g. `_on_show(self, event: wx.ShowEvent) -> None`:
      - Se event.IsShown(): self._testo.SetFocus().
      - Chiama event.Skip().

2. Aggiungere in cima al file il docstring con path, scopo, apertura,
   chiusura e attributo focus, seguendo il pattern di finestra_aiuto_tasti_rapidi.py.

3. Creare `tests/ui/test_finestra_guida_regole.py` con la suite unittest:
   - Struttura identica a test_finestra_aiuto_tasti_rapidi.py.
   - setUpClass/tearDownClass con wx.App(False).
   - setUp crea wx.Frame(None) come parent e instanzia FinestraGuidaRegole.
   - tearDown distrugge dialog e parent.
   - T1: test_dialog_istanziazione_senza_eccezioni
   - T2: test_dialog_titolo_corretto — GetTitle() == GUIDA_UI["TITOLO_FINESTRA"]
   - T3: test_dialog_contiene_text_ctrl_readonly
   - T4: test_dialog_contiene_pulsante_chiudi — id == wx.ID_CANCEL
   - T5: test_dialog_contiene_pulsante_precedente
   - T6: test_dialog_contiene_pulsante_successivo
   - T7: test_dialog_precedente_disabilitato_prima_pagina — _btn_precedente.IsEnabled() is False
   - T8: test_dialog_successivo_abilitato_prima_pagina — _btn_successivo.IsEnabled() is True
   - T9: test_dialog_capitolo_1_visibile_all_apertura — _testo.GetValue() non vuoto
   - T10: test_dialog_navigazione_successivo — dopo _vai_pagina_successiva,
         _indice_corrente == 1 e _testo aggiornato
   - T11: test_dialog_cinque_capitoli_disponibili — len(GUIDA_CAPITOLI) == 5
   - T12: test_dialog_successivo_disabilitato_ultima_pagina —
          imposta _indice_corrente = 4, chiama _aggiorna_visualizzazione(),
          verifica _btn_successivo.IsEnabled() is False

Criteri di completamento Fase B:
- Il file finestra_guida_regole.py esiste e importa correttamente
- py_compile non segnala errori
- mypy --strict non segnala errori
- Suite test_finestra_guida_regole.py: 12 test verdi
- Suite esistente non degradata (zero regressioni)

---

### Fase C — Integrazione binding e collegamento menu

**File coinvolti**: `finestra_gioco.py` (MODIFY), `finestra_principale.py` (MODIFY),
`finestra_aiuto_tasti_rapidi.py` (MODIFY)

Operazioni su `finestra_gioco.py`:

1. Aggiungere import:
   ```python
   from bingo_game.ui.finestra_guida_regole import FinestraGuidaRegole
   ```
2. In `_on_char_hook`, dopo il ramo `Ctrl+I` (dettaglio premi) e prima
   di `event.Skip()`, aggiungere:
   ```python
   # Ctrl+Shift+H — apri guida regole del gioco  [Categoria C]
   if ctrl and shift and key == ord("H"):
       dlg = FinestraGuidaRegole(self)
       dlg.ShowModal()
       dlg.Destroy()
       self._pannello_griglia.SetFocus()
       return
   ```
3. Verificare che `shift = event.ShiftDown()` sia gia assegnato in cima
   al metodo. Se non fosse presente, aggiungere prima del blocco.

Operazioni su `finestra_principale.py`:

1. Nel metodo `_on_guida`, sostituire il corpo:
   ```python
   # PRIMA:
   self._renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")

   # DOPO:
   from bingo_game.ui.finestra_guida_regole import FinestraGuidaRegole
   dlg = FinestraGuidaRegole(self)
   dlg.ShowModal()
   dlg.Destroy()
   ```
   Import lazy nel corpo del metodo per evitare import circolare
   (pattern gia usato in finestra_principale._on_nuova_partita).

Operazioni su `finestra_aiuto_tasti_rapidi.py`:

1. Nel contenuto testuale _CONTENUTO_TASTI_RAPIDI, nella sezione
   CATEGORIA C, aggiungere una riga dopo la riga relativa a Ctrl+H:
   ```
   Ctrl+Shift+H           — apri la guida alle regole del gioco
   ```

Criteri di completamento Fase C:
- Ctrl+Shift+H apre il dialog durante una partita in corso
- Ctrl+G apre il dialog dal menu principale
- Nessuna hotkey esistente e stata rimossa o spostata
- Il contenuto della finestra tasti rapidi mostra Ctrl+Shift+H
- py_compile e mypy non segnalano errori nei file modificati
- Suite test esistente non degradata (zero regressioni)

---

### Fase D — Aggiornamento documentazione e changelog

**File coinvolti**: `docs/API.md` (MODIFY), `CHANGELOG.md` (MODIFY)

Operazioni su `docs/API.md`:

1. Nella sezione del layer Presentazione (`bingo_game/ui/`), aggiungere
   dopo la voce FinestraAiutoTastiRapidi:

   ```
   ### FinestraGuidaRegole

   - **Percorso**: `bingo_game/ui/finestra_guida_regole.py`
   - **Tipo**: `wx.Dialog` (modale)
   - **Scopo**: guida alle regole del gioco navigabile a pagine.
   - **Apertura**: `Ctrl+Shift+H` da `FinestraGioco`; `Ctrl+G` da `FinestraPrincipale`.
   - **Chiusura**: `Escape` o pulsante Chiudi (EndModal).
   - **Focus iniziale**: `wx.TextCtrl` del capitolo 1.
   - **Annuncio NVDA**: a ogni cambio pagina, il focus si sposta su StaticText titolo.
   - **Testi**: `bingo_game/ui/locales/it_guida.py` — GUIDA_CAPITOLI.
   - **Dipendenze**: nessuna dipendenza da dominio, renderer o eventi.
   ```

2. Nella stessa sezione, aggiungere voce per il nuovo modulo locales:

   ```
   ### it_guida.py

   - **Percorso**: `bingo_game/ui/locales/it_guida.py`
   - **Tipo**: modulo dati immutabili (MappingProxyType)
   - **Scopo**: testi dei capitoli della guida in italiano.
   - **Estensibile**: aggiungere un elemento a GUIDA_CAPITOLI aggiunge
     automaticamente una pagina nel dialog senza modificare il codice UI.
   ```

Operazioni su `CHANGELOG.md`:

1. Nella sezione `## [Unreleased]`, sotto `### Added` (crearla se assente):
   ```
   - `FinestraGuidaRegole`: wx.Dialog modale navigabile a pagine con le regole
     del gioco. 5 capitoli: Introduzione, La cartella, I premi, Come si svolge
     un turno, I bot avversari. Apribile con Ctrl+Shift+H da FinestraGioco
     e con Ctrl+G dal menu principale. Annuncio NVDA automatico del titolo
     capitolo a ogni cambio pagina.
   - `bingo_game/ui/locales/it_guida.py`: nuovo modulo con dizionari
     GUIDA_CAPITOLI e GUIDA_UI. Estensibile senza modifiche al codice UI.
   ```

Criteri di completamento Fase D:
- docs/API.md contiene le due nuove voci
- CHANGELOG.md contiene la entry in [Unreleased] / Added

---

## 5. Commit attesi

**Commit 1** (al termine di Fase A + Fase B):
```
feat(ui): aggiunge FinestraGuidaRegole e it_guida.py
```
File: it_guida.py, finestra_guida_regole.py, tests/ui/test_finestra_guida_regole.py

**Commit 2** (al termine di Fase C):
```
feat(ui): integra Ctrl+Shift+H e collegamento menu guida
```
File: finestra_gioco.py, finestra_principale.py, finestra_aiuto_tasti_rapidi.py

**Commit 3** (al termine di Fase D):
```
docs: aggiorna API.md e CHANGELOG per FinestraGuidaRegole v0.14.0
```
File: docs/API.md, CHANGELOG.md

---

## 6. Test Plan

### 6.1 Test unitari automatici — `tests/ui/test_finestra_guida_regole.py`

| ID  | Nome test | Verifica |
|-----|-----------|---------|
| T1  | test_dialog_istanziazione_senza_eccezioni | Nessuna eccezione alla creazione |
| T2  | test_dialog_titolo_corretto | GetTitle() == GUIDA_UI["TITOLO_FINESTRA"] |
| T3  | test_dialog_contiene_text_ctrl_readonly | TextCtrl con stile TE_READONLY |
| T4  | test_dialog_contiene_pulsante_chiudi | Button con id == wx.ID_CANCEL |
| T5  | test_dialog_contiene_pulsante_precedente | Button label "Precedente" presente |
| T6  | test_dialog_contiene_pulsante_successivo | Button label "Successivo" presente |
| T7  | test_dialog_precedente_disabilitato_prima_pagina | IsEnabled() is False |
| T8  | test_dialog_successivo_abilitato_prima_pagina | IsEnabled() is True |
| T9  | test_dialog_capitolo_1_visibile_all_apertura | GetValue() non vuoto |
| T10 | test_dialog_navigazione_successivo | _indice_corrente == 1 dopo navigazione |
| T11 | test_dialog_cinque_capitoli_disponibili | len(GUIDA_CAPITOLI) == 5 |
| T12 | test_dialog_successivo_disabilitato_ultima_pagina | IsEnabled() is False a pagina 5 |

### 6.2 Smoke test manuale (non automatizzabile in CI)

- Avviare partita, premere Ctrl+Shift+H — dialog apre senza eccezioni.
- NVDA annuncia "Guida alle regole del gioco, dialogo" poi legge il testo.
- Tab porta al pulsante Successivo. Spazio o Invio cambia pagina.
- NVDA legge il titolo del nuovo capitolo.
- Tab torna al TextCtrl. Frecce leggono il testo riga per riga.
- Escape chiude il dialog. Focus torna alla griglia.
- Ctrl+G dal menu principale apre il dialog. Escape chiude.
- Ctrl+H apre ancora la finestra tasti rapidi (nessuna regressione).
