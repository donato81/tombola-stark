---
type: plan
feature: ricerca_auto_chiusura_dialog
agent: Agent-Plan
status: DRAFT
version: v1.1.0
design_ref: docs/2 - projects/DESIGN_ricerca_auto_chiusura_dialog_v1.1.0.md
date: 2026-04-09
report_ref: docs/4 - reports/REPORT_ANALISI_ricerca_auto_chiusura_dialog_2026-04-09.md
---

# PLAN — Auto-chiusura dialog ricerca numero (Ctrl+F) v1.1.0

## 1. Executive Summary

| Campo | Valore |
|---|---|
| Tipo | Fix UX / Accessibilità |
| Feature | ricerca_auto_chiusura_dialog |
| Priorità | Alta |
| Branch | feat/ricerca-auto-chiusura-dialog |
| Versione target | v1.1.0 |
| Status | DRAFT |
| Commit attesi | 2 (+1 test) |
| Design di riferimento | docs/2 - projects/DESIGN_ricerca_auto_chiusura_dialog_v1.1.0.md |

---

## 2. Problema / Obiettivo

### Problema

Dopo una ricerca con esito positivo (Ctrl+F), l'utente deve premere ESC per
chiudere il dialog e tornare al gioco. Questo passaggio non necessario rallenta
il flusso di gioco per un utente non vedente con NVDA che deve eseguire una
navigazione rapida.

### Obiettivo misurabile

Al termine dell'implementazione:

- Una ricerca con numero trovato chiude automaticamente il dialog dopo un ritardo
  dinamico calcolato come `400 + max(0, len(risultati) - 1) * 200` ms.
- Il focus ritorna alla griglia, posizionato su cartella/riga/colonna del
  primo risultato trovato.
- Una ricerca con numero non trovato lascia il dialog aperto come oggi.
- I test unitari riflettono e verificano il nuovo comportamento.

### Riferimento DESIGN

Documento REVIEWED: `docs/2 - projects/DESIGN_ricerca_auto_chiusura_dialog_v1.1.0.md`  
Sezioni chiave: §5 Formula ritardo, §6 Modifiche specifiche ai file, §7 Test, §8 Rischi.

---

## 3. File coinvolti

| File | Azione | Note |
|---|---|---|
| `bingo_game/ui/dialogo_ricerca.py` | MODIFY | Auto-chiusura con `wx.CallLater` e `_primo_risultato` |
| `bingo_game/ui/finestra_gioco.py` | MODIFY | Navigazione al primo risultato + nuovo metodo helper |
| `tests/unit/test_dialogo_ricerca_persistente.py` | MODIFY | Aggiornamento test esistente + aggiunta 5 test |

**File invariati (vincolo assoluto):**
- `bingo_game/events/` — nessuna modifica
- `bingo_game/players/` — nessuna modifica
- `bingo_game/comandi_partita.py` — nessuna modifica
- `bingo_game/ui/renderers/` — nessuna modifica
- Domain layer — nessuna modifica

---

## 4. Fasi sequenziali

### FASE 1 — Modifica `bingo_game/ui/dialogo_ricerca.py`

**File coinvolto:** `bingo_game/ui/dialogo_ricerca.py`

**Operazioni:**

1. Nel metodo `__init__`, dopo `self._comandi = comandi`, aggiungere:
   ```python
   self._primo_risultato: Optional[Any] = None
   ```
   Aggiungere `Any` agli import da `typing` se non già presente
   (è già usato `TYPE_CHECKING`; verificare che `Any` sia importato).

2. Nel metodo `_on_cerca()`, sostituire la riga finale:
   ```python
   self._input_ctrl.SetFocus()
   ```
   con il blocco:
   ```python
   from bingo_game.events.eventi_output_ui_umani import EventoRicercaNumeroInCartelle
   evento_ricerca = esito.evento if hasattr(esito, "evento") else None
   if isinstance(evento_ricerca, EventoRicercaNumeroInCartelle) and evento_ricerca.esito == "trovato":
       self._primo_risultato = evento_ricerca.risultati[0]
       ritardo_ms = 400 + max(0, len(evento_ricerca.risultati) - 1) * 200
       wx.CallLater(ritardo_ms, self.EndModal, wx.ID_OK)
   else:
       self._input_ctrl.SetFocus()
   ```

3. Eseguire: `python -m py_compile bingo_game/ui/dialogo_ricerca.py` — deve returnare exit code 0.

**Commit:** `fix(ui): dialogo ricerca si chiude automaticamente dopo annuncio risultato`

**Dipendenza:** nessuna (questa fase è indipendente).

---

### FASE 2 — Modifica `bingo_game/ui/finestra_gioco.py`

**File coinvolto:** `bingo_game/ui/finestra_gioco.py`

**Operazioni:**

1. Verificare che `Any` sia importato da `typing`. Se non presente, aggiungerlo:
   ```python
   from typing import Optional, Any
   ```
   (Nota: `Optional` è già importato; solo `Any` potrebbe mancare.)

2. Sostituire il metodo `_apri_ricerca_numero()` attuale:
   ```python
   def _apri_ricerca_numero(self) -> None:
       """Apre il dialog modale di ricerca numero."""
       from bingo_game.ui.dialogo_ricerca import DialogoRicercaNumero
       dlg = DialogoRicercaNumero(
           parent=self,
           renderer=self._renderer,
           comandi=self._comandi,
       )
       dlg.ShowModal()
       dlg.Destroy()
       # Ripristina focus sulla griglia
       self._pannello_griglia.SetFocus()
   ```
   con:
   ```python
   def _apri_ricerca_numero(self) -> None:
       """Apre il dialog modale di ricerca numero."""
       from bingo_game.ui.dialogo_ricerca import DialogoRicercaNumero
       dlg = DialogoRicercaNumero(
           parent=self,
           renderer=self._renderer,
           comandi=self._comandi,
       )
       dlg.ShowModal()
       primo_risultato = getattr(dlg, "_primo_risultato", None)
       dlg.Destroy()
       if primo_risultato is not None:
           self._naviga_a_risultato_ricerca(primo_risultato)
       else:
           self._pannello_griglia.SetFocus()
   ```

3. Aggiungere il nuovo metodo `_naviga_a_risultato_ricerca` immediatamente dopo
   `_apri_ricerca_numero`:
   ```python
   def _naviga_a_risultato_ricerca(self, risultato: Any) -> None:
       """Naviga alla posizione del primo risultato della ricerca."""
       self._dispatch(self._comandi.imposta_focus_cartella(risultato.numero_cartella))
       self._dispatch(self._comandi.vai_a_riga(risultato.indice_riga + 1))
       self._dispatch(self._comandi.vai_a_colonna(risultato.indice_colonna + 1))
   ```

4. Eseguire: `python -m py_compile bingo_game/ui/finestra_gioco.py` — deve returnare exit code 0.

**Commit:** `fix(ui): FinestraGioco naviga al primo risultato dopo chiusura dialog ricerca`

**Dipendenza:** può essere eseguita in parallelo con FASE 1, ma logicamente dopo.

---

### FASE 3 — Aggiornamento test `tests/unit/test_dialogo_ricerca_persistente.py`

**File coinvolto:** `tests/unit/test_dialogo_ricerca_persistente.py`

**Operazioni:**

1. Il test esistente `test_on_cerca_non_chiama_end_modal` non è più corretto
   (verifica che `EndModal` non sia mai chiamata, ma ora viene chiamata nel
   ramo trovato). Sostituirlo con due test separati:

   - `test_on_cerca_non_chiama_end_modal_se_non_trovato`:  
     mock `cerca_numero` → esito con `EventoRicercaNumeroInCartelle.non_trovato(...)`.  
     Verifica: `dialogo.EndModal.assert_not_called()`.

   - `test_on_cerca_non_chiama_end_modal_immediatamente_se_trovato`:  
     mock `cerca_numero` → esito con `EventoRicercaNumeroInCartelle.trovato(...)`.  
     Mock `wx.CallLater` per catturare la chiamata.  
     Verifica: `dialogo.EndModal.assert_not_called()` (non chiamata subito, solo via CallLater).

2. Aggiungere i test di verifica ritardo dinamico:

   - `test_ritardo_dinamico_1_risultato`:  
     1 risultato → verifica che `wx.CallLater` sia chiamato con `400` come primo argomento.

   - `test_ritardo_dinamico_3_risultati`:  
     3 risultati → verifica che `wx.CallLater` sia chiamato con `800` come primo argomento.

3. Aggiungere test di verifica attributo:

   - `test_primo_risultato_impostato_se_trovato`:  
     Verifica che `dialogo._primo_risultato` sia il primo elemento di `evento.risultati`.

   - `test_primo_risultato_none_se_non_trovato`:  
     Verifica che `dialogo._primo_risultato` sia `None` dopo ricerca fallita.

4. Eseguire: `python -m py_compile tests/unit/test_dialogo_ricerca_persistente.py` — exit code 0.

5. Eseguire: `py -3.11 -m unittest tests.unit.test_dialogo_ricerca_persistente -v` — tutti i test devono passare.

**Commit:** `test(ui): aggiorna e amplia test dialogo ricerca per auto-chiusura`

**Dipendenza:** FASE 1 deve essere completata prima di questa fase (i test verificano il codice modificato).

---

## 5. Dipendenze tra fasi

```
FASE 1 (dialogo_ricerca.py)
  ↓
FASE 2 (finestra_gioco.py)   ← può essere sviluppata in parallelo con FASE 1
  ↓
FASE 3 (test)               ← dipende da FASE 1 (verifica il codice modificato)
```

FASE 2 è logicamente indipendente da FASE 1 a livello di compilazione, ma
per coerenza semantica si consiglia l'ordine sequenziale.

---

## 6. Rischi con mitigazione

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| NVDA race condition (lettura interrotta) | Media | Medio | Ritardo dinamico dimensionato per velocità media; ESC rimane sempre disponibile |
| Double EndModal (ESC + CallLater in sequenza) | Bassa | Nullo | wxPython ignora EndModal su dialog già chiuso |
| `_primo_risultato` non inizializzato | Bassa | Basso | `getattr(..., None)` difensivo in FinestraGioco; init esplicito in `__init__` |
| Rottura test esistente `test_on_cerca_non_chiama_end_modal` | Certa | Basso | Test da aggiornare in FASE 3 (previsto nel piano) |

---

## 7. Criteri di completamento

La feature è da considerarsi completa quando:

- `python -m py_compile bingo_game/ui/dialogo_ricerca.py` → exit code 0
- `python -m py_compile bingo_game/ui/finestra_gioco.py` → exit code 0
- `py -3.11 -m unittest tests.unit.test_dialogo_ricerca_persistente -v` → tutti i test pass
- Verifica manuale: 1 risultato → dialog si chiude dopo 400ms, focus su cartella corretta
- Verifica manuale: 3 risultati → dialog si chiude dopo 800ms, focus sul primo risultato
- Verifica manuale: non trovato → dialog rimane aperto, focus sull'input

*Fine documento PLAN*
