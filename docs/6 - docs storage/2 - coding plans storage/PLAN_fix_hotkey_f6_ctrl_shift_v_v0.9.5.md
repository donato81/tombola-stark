---
type: plan
feature: fix_hotkey_f6_ctrl_shift_v
agent: Agent-Plan
status: READY
version: v0.9.5
design_ref: docs/2 - projects/DESIGN_fix_hotkey_f6_ctrl_shift_v.md
date: 2026-04-05
---

# PLAN — Fix hotkey F6 e Ctrl+Shift+V — v0.9.5

## 1. Executive Summary

| Voce | Valore |
|---|---|
| Tipo | Bug fix — presentazione |
| Priorità | Alta (crash a runtime + funzionalità accessibilità non operativa) |
| Branch | main |
| Versione | v0.9.5 |
| Commit attesi | 2 (uno per bug, atomici) |

## 2. Problema e Obiettivo

### Bug 1 — F6 (crash `AttributeError`)

**Sintomo:** premendo F6 nella finestra di gioco appare in console:
```
AttributeError: '_finestra'
```
Nessuna vocalizzazione avviene. NVDA rimane silente.

**Causa radice:** in `PannelloGriglia._on_key_down` la riga
```python
fg._finestra._renderer.ripeti_ultimo_annuncio()
```
usa `fg._finestra` dove `fg` è già `self._finestra` (cioè `FinestraGioco`).
`FinestraGioco` non possiede l'attributo `_finestra` (appartiene a `PannelloGriglia`).
`FinestraGioco` espone `self._renderer` direttamente.

**Correzione:** sostituire con `fg._renderer.ripeti_ultimo_annuncio()`.

### Bug 2 — Ctrl+Shift+V (handler incompleto)

**Sintomo:** il sistema vocalizza "Tutte le N cartelle mostrate in modalità
avanzata." ma non legge il contenuto di nessuna cartella.

**Causa radice:** `WxRenderer._handle_visualizza_tutte_cartelle_avanzata`
non itera `evento.cartelle`. Costruisce e vocalizza solo il conteggio.
I dati completi (griglia, segnati) sono presenti nell'evento ma ignorati.

**Correzione:** implementare l'iterazione completa, analoga agli handler
`_handle_visualizza_tutte_cartelle_semplice` (iterazione) e
`_handle_visualizza_cartella_avanzata` (formattazione con segnati evidenziati).
La vocalizzazione dovrà coprire l'intero testo costruito (comportamento avanzata).

## 3. File coinvolti

| File | Operazione | Bug |
|---|---|---|
| `bingo_game/ui/finestra_gioco.py` | MODIFY — fix riga 171 | Bug 1 |
| `bingo_game/ui/renderers/renderer_wx.py` | MODIFY — handler linee 399-404 | Bug 2 |
| `tests/` (eventuali test esistenti sull'handler) | VERIFY / FIX | Bug 2 |

## 4. Fasi sequenziali

### Fase 1 — Fix Bug 1: F6 AttributeError
**File:** `bingo_game/ui/finestra_gioco.py`
**Modifica singola:**

```python
# PRIMA (riga 171)
fg._finestra._renderer.ripeti_ultimo_annuncio()

# DOPO
fg._renderer.ripeti_ultimo_annuncio()
```

**Verifica:**
- Avviare il gioco, ogni tasto prima di F6 deve generare un annuncio.
- Premere F6: NVDA deve ripetere l'ultimo annuncio.
- Se F6 è il primo tasto premuto: NVDA deve vocalizzare "Nessun annuncio precedente."
- Nessuna eccezione nel log di errore.

**Gate pre-commit:**
```bash
python -m py_compile bingo_game/ui/finestra_gioco.py
```

---

### Fase 2 — Fix Bug 2: Ctrl+Shift+V handler incompleto
**File:** `bingo_game/ui/renderers/renderer_wx.py`
**Funzione da modificare:** `_handle_visualizza_tutte_cartelle_avanzata`

**Logica della nuova implementazione:**

1. Inizializzare lista `parti: list[str] = []`.
2. Per ogni `(numero_c, griglia_semplice, stato_cartella, numeri_segnati_ordinati)`
   in `evento.cartelle`:
   - `segnati_set = set(numeri_segnati_ordinati)`
   - Appendere `f"Cartella {numero_c}:"` a `parti`
   - Per ogni `(i, riga)` in `enumerate(griglia_semplice)`:
     - `celle = "  ".join(_formatta_cella(c, evidenziata=isinstance(c, int) and c in segnati_set) for c in riga)`
     - Appendere `f"  Riga {i+1}: {celle}"` a `parti`
3. `testo = "\n".join(parti)`
4. `self._wx_aggiorna_output(testo)`
5. `self._ao2_vocalizza(testo)`

**Verifica:**
- Avviare il gioco con minimo 1 cartella assegnata al giocatore umano.
- Premere Ctrl+Shift+V sul pannello griglia.
- NVDA deve leggere "Cartella 1: Riga 1: ..." per ogni cartella.
- I numeri segnati devono essere vocdalizzati col token "N segnato" (già
  gestito da `_formatta_cella`).
- L'area di testo (PannelloGriglia) deve mostrare il contenuto completo.
- Nessuna eccezione nel log.

**Gate pre-commit:**
```bash
python -m py_compile bingo_game/ui/renderers/renderer_wx.py
```

---

### Fase 3 — Verifica test esistenti
**Scope:** eseguire la suite test unitari e di integrazione per accertare
che nessun test verificasse il comportamento stub (ormai rimosso).

```bash
py -3.11 -m pytest tests/ -q --tb=short
```

Se test falliscono per cambio comportamento `_handle_visualizza_tutte_cartelle_avanzata`:
aggiornare le assertions per riflettere il comportamento corretto.

---

### Fase 4 — Aggiornamento CHANGELOG
**File:** `CHANGELOG.md`
**Sezione:** `[Unreleased] → Fixed`

Aggiungere:
- Fix Bug 1 (`finestra_gioco.py`: `fg._finestra._renderer` → `fg._renderer`)
- Fix Bug 2 (`renderer_wx.py`: handler avanzata completato)

## 5. Test Plan

### Unit test nuovi (opzionale, da aggiungere se non presenti)

| Test | Descrizione |
|---|---|
| `test_ripeti_ultimo_annuncio_con_annuncio` | `F6` dopo un annuncio → vocalizza l'ultimo testo |
| `test_ripeti_ultimo_annuncio_senza_annuncio` | `F6` senza annunci → vocalizza "Nessun annuncio precedente." |
| `test_handle_visualizza_tutte_avanzata_con_dati` | Verifica che il testo costruito contenga "Cartella 1:" e le celle formattate |
| `test_handle_visualizza_tutte_avanzata_segnati_evidenziati` | Verifica che i numeri segnati abbiano la label "segnato" nel testo |

### Gate complessivo
```bash
py -3.11 -m pytest tests/ -q
python -m py_compile bingo_game/ui/finestra_gioco.py
python -m py_compile bingo_game/ui/renderers/renderer_wx.py
grep -r "print(" bingo_game/ --include="*.py"   # deve restituire 0 occorrenze
```
