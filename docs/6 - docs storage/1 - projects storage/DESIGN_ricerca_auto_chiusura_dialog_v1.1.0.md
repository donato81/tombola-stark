---
type: design
feature: ricerca_auto_chiusura_dialog
agent: Agent-Design
status: REVIEWED
version: v1.1.0
date: 2026-04-09
report_ref: docs/4 - reports/REPORT_ANALISI_ricerca_auto_chiusura_dialog_2026-04-09.md
---

# DESIGN — Auto-chiusura dialog ricerca numero (Ctrl+F) v1.1.0

## 1. Idea in 3 righe

Dopo che il dialog di ricerca (Ctrl+F) ha annunciato un risultato positivo,
il dialog si chiude automaticamente tramite `wx.CallLater` con ritardo dinamico,
e il focus ritorna alla griglia posizionato sulla cartella/riga/colonna del
primo risultato trovato.

---

## 2. Obiettivo misurabile

Al termine dell'implementazione:

- Premendo Ctrl+F, inserendo un numero trovato e premendo Invio, il dialog si
  chiude automaticamente dopo un ritardo calcolato in base al numero di risultati
  (400ms per 1 risultato, +200ms per ogni risultato aggiuntivo).
- Il focus ritorna al pannello griglia, posizionato esattamente sulla cartella,
  riga e colonna del primo risultato della ricerca.
- Se il numero non è trovato, il dialog rimane aperto come nel comportamento attuale,
  permettendo una nuova ricerca senza che l'utente debba fare nulla.
- L'utente non deve mai premere ESC per tornare al gioco dopo una ricerca con esito positivo.

---

## 3. Attori e Componenti coinvolti

| Attore / Componente | Ruolo | Modifica |
|---|---|---|
| `DialogoRicercaNumero` | Dialog modale di ricerca | MODIFY — aggiunta auto-chiusura con `wx.CallLater` |
| `FinestraGioco` | Frame di gioco principale | MODIFY — navigazione al primo risultato dopo `ShowModal()` |
| `EsitoAzione` | Contenitore esito ricerca | Invariato |
| `EventoRicercaNumeroInCartelle` | Evento con dati risultati | Invariato |
| `RisultatoRicercaNumeroInCartella` | Dati posizione singolo risultato | Invariato |
| `ComandiGiocatoreUmano` | Comandi navigazione (già esistenti) | Invariato |
| `WxRenderer` | Vocalizzazione / output | Invariato |
| `tests/unit/test_dialogo_ricerca_persistente.py` | Test esistente dialog | MODIFY — adeguamento al nuovo comportamento |

**Vincolo assoluto:** nessuna modifica al domain layer, a `comandi_partita.py`,
ai file in `bingo_game/events/`, ai file in `bingo_game/players/` o al renderer.

---

## 4. Flusso attuale vs flusso target

### 4.1 Flusso attuale

```
Ctrl+F
  └─ FinestraGioco._apri_ricerca_numero()
       ├─ DialogoRicercaNumero.ShowModal()   ← BLOCCA
       │     [utente digita numero, preme Invio]
       │     └─ _on_cerca()
       │           ├─ cerca_numero(numero)
       │           ├─ renderer.render_esito(esito)  ← NVDA vocalizza
       │           ├─ _lbl_risultato.SetLabel(testo)
       │           └─ _input_ctrl.SetFocus()  ← ATTENDE ESC
       │
       [utente preme ESC]
       ├─ dlg.Destroy()
       └─ _pannello_griglia.SetFocus()       ← focus generico, senza navigazione
```

### 4.2 Flusso target (Opzione B scelta)

```
Ctrl+F
  └─ FinestraGioco._apri_ricerca_numero()
       ├─ DialogoRicercaNumero.ShowModal()   ← BLOCCA
       │     [utente digita numero, preme Invio]
       │     └─ _on_cerca()
       │           ├─ cerca_numero(numero)   → EsitoAzione
       │           ├─ renderer.render_esito(esito)  ← NVDA vocalizza
       │           ├─ _lbl_risultato.SetLabel(testo)
       │           │
       │           ├─ [SE trovato]
       │           │     self._primo_risultato = esito.evento.risultati[0]
       │           │     ritardo_ms = 400 + max(0, len(risultati) - 1) * 200
       │           │     wx.CallLater(ritardo_ms, self.EndModal, wx.ID_OK)
       │           │                                ← nessuna azione utente richiesta
       │           └─ [SE non trovato]
       │                 _input_ctrl.SetFocus()  ← ATTENDE input (comportamento invariato)
       │
       [dialog si chiude automaticamente dopo ritardo_ms]
       ├─ dlg._primo_risultato letto da FinestraGioco
       ├─ dlg.Destroy()
       └─ FinestraGioco._naviga_a_risultato_ricerca(dlg._primo_risultato)
             ├─ _dispatch(comandi.imposta_focus_cartella(r.numero_cartella))
             ├─ _dispatch(comandi.vai_a_riga(r.indice_riga + 1))
             └─ _dispatch(comandi.vai_a_colonna(r.indice_colonna + 1))
```

### 4.3 Sequenza utente finale (esperienza con NVDA)

1. L'utente preme **Ctrl+F** durante la partita.
2. NVDA legge: "Cerca numero. Dialogo. Numero da cercare uno a novanta. Modifica."
3. L'utente digita il numero e preme **Invio**.
4. NVDA legge il risultato, es.: "Numero 42 trovato in: Cartella 2, riga 1, colonna 3 (non segnato)."
5. Dopo **400ms** (1 risultato) il dialog si chiude automaticamente — nessun ESC richiesto.
6. NVDA annuncia il cambio focus: il cursore è già su Cartella 2, Riga 1, Colonna 3.
7. L'utente riprende la navigazione normale senza interruzioni.

Per 3 risultati, il ritardo è 800ms, dando a NVDA tempo sufficiente per leggere
la lista completa prima che il focus si sposti.

---

## 5. Formula del ritardo dinamico

```python
ritardo_ms = 400 + max(0, len(risultati) - 1) * 200
```

| Numero di risultati | Ritardo |
|---|---|
| 1 | 400ms |
| 2 | 600ms |
| 3 | 800ms |
| 4 | 1000ms |
| n | 400 + (n-1) × 200 ms |

Il ritardo è calcolato nel metodo `_on_cerca()` di `DialogoRicercaNumero`
al momento della chiamata a `wx.CallLater`, immediatamente dopo la vocalizzazione.

---

## 6. Modifiche specifiche ai file

### 6.1 bingo_game/ui/dialogo_ricerca.py

**Metodo `__init__`:**
- Aggiungere `self._primo_risultato: Optional[Any] = None` tra gli attributi
  di istanza (inizializzazione nel costruttore, dopo `self._comandi = comandi`).

**Metodo `_on_cerca()`:**
Modificare la parte finale del metodo (attualmente termina con `self._input_ctrl.SetFocus()`).

Dopo `self._lbl_risultato.SetLabel(testo_risultato)`, aggiungere:

```python
from bingo_game.events.eventi_output_ui_umani import EventoRicercaNumeroInCartelle
evento = esito.evento if hasattr(esito, "evento") else None
if isinstance(evento, EventoRicercaNumeroInCartelle) and evento.esito == "trovato":
    self._primo_risultato = evento.risultati[0]
    ritardo_ms = 400 + max(0, len(evento.risultati) - 1) * 200
    wx.CallLater(ritardo_ms, self.EndModal, wx.ID_OK)
else:
    self._input_ctrl.SetFocus()
```

La riga `self._input_ctrl.SetFocus()` esistente va spostata nel ramo `else`
(attivato solo se il numero non è trovato o l'esito non è valido).

### 6.2 bingo_game/ui/finestra_gioco.py

**Metodo `_apri_ricerca_numero()`:**

Attualmente:
```python
def _apri_ricerca_numero(self) -> None:
    from bingo_game.ui.dialogo_ricerca import DialogoRicercaNumero
    dlg = DialogoRicercaNumero(parent=self, renderer=self._renderer, comandi=self._comandi)
    dlg.ShowModal()
    dlg.Destroy()
    self._pannello_griglia.SetFocus()
```

Modificato:
```python
def _apri_ricerca_numero(self) -> None:
    from bingo_game.ui.dialogo_ricerca import DialogoRicercaNumero
    dlg = DialogoRicercaNumero(parent=self, renderer=self._renderer, comandi=self._comandi)
    dlg.ShowModal()
    primo_risultato = getattr(dlg, "_primo_risultato", None)
    dlg.Destroy()
    if primo_risultato is not None:
        self._naviga_a_risultato_ricerca(primo_risultato)
    else:
        self._pannello_griglia.SetFocus()
```

**Nuovo metodo `_naviga_a_risultato_ricerca()`** (da aggiungere subito dopo `_apri_ricerca_numero`):

```python
def _naviga_a_risultato_ricerca(self, risultato: Any) -> None:
    self._dispatch(self._comandi.imposta_focus_cartella(risultato.numero_cartella))
    self._dispatch(self._comandi.vai_a_riga(risultato.indice_riga + 1))
    self._dispatch(self._comandi.vai_a_colonna(risultato.indice_colonna + 1))
```

Import aggiuntivo necessario in `finestra_gioco.py`: `from typing import Any`
(già presente tramite `Optional`; verificare che `Any` sia già importato).

---

## 7. Impatto sui test

### 7.1 Test da aggiornare

**File:** `tests/unit/test_dialogo_ricerca_persistente.py`  
**Test:** `test_on_cerca_non_chiama_end_modal`

Questo test verifica che `EndModal` NON sia chiamata — il comportamento ora dipende
dall'esito. Il test va rinominato / riscritto in 3 test distinti:

| Nuovo test | Verifica |
|---|---|
| `test_on_cerca_non_chiama_end_modal_se_non_trovato` | `EndModal` NON chiamata se `evento.esito == "non_trovato"` |
| `test_on_cerca_primo_risultato_none_se_non_trovato` | `_primo_risultato` è `None` dopo ricerca fallita |
| `test_on_cerca_chiama_call_later_se_trovato` | `wx.CallLater` chiamata con ritardo corretto e `EndModal` come callback |

### 7.2 Test da aggiungere

| Nuovo test | Verifica |
|---|---|
| `test_ritardo_1_risultato` | `ritardo_ms == 400` con 1 risultato |
| `test_ritardo_3_risultati` | `ritardo_ms == 800` con 3 risultati |
| `test_primo_risultato_impostato_se_trovato` | `_primo_risultato` contiene il primo `RisultatoRicercaNumeroInCartella` |

---

## 8. Rischi

### 8.1 NVDA race condition (principale)

**Descrizione:** NVDA inizia a leggere il risultato (es. lista di 3 cartelle)
mentre `wx.CallLater` conta il tempo. Se il ritardo finisce prima che NVDA
abbia terminato, il cambio di focus interrompe la lettura.

**Mitigazione:** La formula `400 + (n-1) × 200` è dimensionata per un sintetizzatore
a velocità media. Se l'utente usa una velocità più alta, il margine aumenta.  
Non è possibile eliminare completamente questo rischio senza agganciare un evento
"fine lettura" dal sintetizzatore, che non è disponibile pubblicamente in NVDA/SAPI.

**Fallback:** Se l'utente percepisce troncamento, può sempre premere ESC manualmente;
il comportamento ESC rimane invariato.

### 8.2 Double EndModal

**Descrizione:** Se l'utente preme ESC o il pulsante Chiudi prima che scada
il `wx.CallLater`, `EndModal` viene chiamata due volte (ESC la prima volta,
il timer la seconda).

**Mitigazione:** In wxPython, chiamare `EndModal` su un dialog già chiuso è
un no-op sicuro — non genera eccezioni nè comportamenti anomali.

### 8.3 Attributo _primo_risultato non inizializzato

**Descrizione:** `getattr(dlg, "_primo_risultato", None)` in `FinestraGioco`
è una lettura difensiva. Se il dialog non ha eseguito `_on_cerca()` (chiuso
subito con ESC), `_primo_risultato` non esiste e `getattr` restituisce `None`.

**Mitigazione:** Inizializzare esplicitamente `self._primo_risultato = None`
in `__init__` elimina la necessità del `getattr` difensivo, ma il getattr
è comunque una garanzia in più senza costo.

---

## 9. Accessibilità NVDA — sequenza completa post-modifica

**Caso 1: numero trovato in 1 cartella**
1. Ctrl+F → NVDA: "Cerca numero. Dialogo."
2. Invio → NVDA: "Numero 42 trovato in: Cartella 2, riga 1, colonna 3 (non segnato)."
3. Dopo 400ms: dialog sparisce, NVDA segue il focus.
4. Focus su PannelloGriglia, posizione Cartella 2, Riga 1, Colonna 3.
5. Ripresa immediata della navigazione.

**Caso 2: numero trovato in 3 cartelle**
1. Ctrl+F → NVDA: "Cerca numero. Dialogo."
2. Invio → NVDA legge lista di 3 risultati (~600ms di lettura).
3. Dopo 800ms: dialog sparisce.
4. Focus posizionato sulla prima cartella della lista (indice_cartella più basso).

**Caso 3: numero non trovato**
1. Ctrl+F → NVDA: "Cerca numero. Dialogo."
2. Invio → NVDA: "Numero 99 non trovato in nessuna cartella."
3. Il dialog rimane aperto, focus sull'input.
4. L'utente può inserire un altro numero o premere ESC per uscire.

*Fine documento DESIGN*
