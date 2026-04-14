---
type: plan
feature: sostituzione_hotkey_ctrl_enter
status: READY
agent: Agent-Plan
versione: 0.9.6
data_creazione: 2026-04-11
---

# PLAN: Sostituzione hotkey Ctrl+P → Ctrl+Enter (v0.9.6)

## 1. Obiettivo

Sostituire il binding `Ctrl+P` (passa turno) con `Ctrl+Enter` in
`FinestraGioco._on_char_hook`. Intervento chirurgico: 1 riga di codice
attiva + 2 commenti/docstring nello stesso modulo + 1 docstring in
`partita.py` + 3 rename simboli test + 1 test di regressione nuovo.

Design di riferimento:
`docs/2 - projects/DESIGN_sostituzione_hotkey_ctrl_enter_v0.9.6.md`

Versione target: **0.9.6** (patch su 0.9.5)

---

## 2. File coinvolti

| File | Operazione | Dettaglio |
|------|-----------|-----------|
| `bingo_game/ui/finestra_gioco.py` | MODIFY | riga 28 (docstring), riga 299 (commento), riga 300 (binding attivo) |
| `bingo_game/partita.py` | MODIFY | riga 814 (docstring) |
| `tests/unit/test_finestra_gioco_shortcuts.py` | MODIFY | rename 3 simboli + aggiunta 1 test |

---

## 3. Fasi implementative

### Fase 1 — Modifica binding attivo in `finestra_gioco.py` (riga 300)

**File**: `bingo_game/ui/finestra_gioco.py`
**Operazione**: MODIFY

Stato attuale (riga 300):
```python
if ctrl and key == ord("P"):
```

Stato target:
```python
if ctrl and key == wx.WXK_RETURN:
```

Nota: `wx` è già importato nel modulo; nessuna nuova import necessaria.

---

### Fase 2 — Aggiorna commenti/docstring in `finestra_gioco.py` (righe 28, 299)

**File**: `bingo_game/ui/finestra_gioco.py`
**Operazione**: MODIFY

#### Riga 28 — docstring del metodo/classe (commento hotkey):

Stato attuale:
```
    Ctrl+P                 -> passa turno
```

Stato target:
```
    Ctrl+Enter             -> passa turno
```

#### Riga 299 — commento inline sopra il binding:

Stato attuale:
```python
        # Ctrl+P — passa turno
```

Stato target:
```python
        # Ctrl+Enter — passa turno
```

---

### Fase 3 — Aggiorna docstring in `partita.py` (riga 814)

**File**: `bingo_game/partita.py`
**Operazione**: MODIFY

Stato attuale (riga 814, dentro docstring di `tutti_hanno_dichiarato_fine`):
```
        Nel ciclo V2 sia i giocatori umani (tramite il pulsante "Ho finito"/Ctrl+P)
```

Stato target:
```
        Nel ciclo V2 sia i giocatori umani (tramite il pulsante "Ho finito"/Ctrl+Enter)
```

---

### Fase 4 — Rename simboli test + aggiungi test binding `_on_char_hook`

**File**: `tests/unit/test_finestra_gioco_shortcuts.py`
**Operazione**: MODIFY

#### 4a — Rename classe (riga 83):

- Da: `TestFinestraGiocoCtrlPAttesaReclami`
- A: `TestFinestraGiocoCtrlEnterAttesaReclami`

#### 4b — Rename metodo 1 (riga 95):

- Da: `test_ctrl_p_attesa_reclami_emette_conferma_prima_dichiarazione`
- A: `test_ctrl_enter_attesa_reclami_emette_conferma_prima_dichiarazione`

#### 4c — Rename metodo 2 (riga 106):

- Da: `test_ctrl_p_attesa_reclami_emette_messaggio_idempotente`
- A: `test_ctrl_enter_attesa_reclami_emette_messaggio_idempotente`

#### 4d — Aggiungi test esplicito binding `_on_char_hook` con `WXK_RETURN + ctrl`

Aggiungere nella classe `TestFinestraGiocoShortcuts` (già esistente):

```python
def test_char_hook_ctrl_enter_invoca_pulsante_principale(self) -> None:
    finestra = self._crea_finestra_stub()
    evento = _EventoTastoFittizio(wx.WXK_RETURN, ctrl=True)

    FinestraGioco._on_char_hook(finestra, evento)

    finestra._on_pulsante_principale.assert_called_once_with(None)
    self.assertFalse(evento.skip_chiamato)
```

Verifica che `_on_pulsante_principale` sia stato chiamato e che
`evt.Skip()` NON sia stato chiamato (il binding è consumato).

---

### Fase 5 — Pre-commit check

Comandi da eseguire nel terminale dopo le modifiche:

```bash
# Compilazione sintattica
python -m py_compile bingo_game/ui/finestra_gioco.py
python -m py_compile bingo_game/partita.py
python -m py_compile tests/unit/test_finestra_gioco_shortcuts.py

# Suite test (almeno i file toccati)
pytest tests/unit/test_finestra_gioco_shortcuts.py -v
```

---

## 4. Pre-commit checklist

- [ ] `py_compile` su tutti e 3 i file modificati → exit code 0
- [ ] nessun riferimento a `Ctrl+P` (passa turno) residuo nei file modificati
- [ ] `pytest tests/unit/test_finestra_gioco_shortcuts.py` → tutti verdi
- [ ] nessun simbolo `ctrl_p` / `CtrlP` residuo nel file di test
- [ ] CHANGELOG.md aggiornato (sezione `[Unreleased]`, voce `Changed`)

---

## 5. Test da aggiungere

| Test | Classe | Comportamento verificato |
|------|--------|--------------------------|
| `test_char_hook_ctrl_enter_invoca_pulsante_principale` | `TestFinestraGiocoShortcuts` | `_on_char_hook(WXK_RETURN, ctrl=True)` chiama `_on_pulsante_principale(None)` e non chiama `evt.Skip()` |

---

## 6. Rischi

### Rischio 1 — Conflitto con `DialogoRicerca`

**Probabilità**: Bassa.
`DialogoRicerca._on_char_hook` intercetta `WXK_RETURN` senza guard `ctrl`.
Il dialog è modale: quando è aperto cattura tutti gli eventi prima di
`FinestraGioco`. Il conflitto non si verifica.
**Mitigazione**: Nessuna modifica a `dialogo_ricerca.py`. Test manuale
verifica che apertura ricerca + Invio non scateni passa-turno.

### Rischio 2 — NVDA intercetta `Ctrl+Enter`

**Probabilità**: Molto bassa.
`Ctrl+Enter` non è assegnato a comandi NVDA predefiniti in focus mode
su wxPython. In browse mode NVDA non è attivo durante la partita.
**Mitigazione**: Test manuale con NVDA in modalità focus sulla finestra
di gioco prima del rilascio v0.9.6.

### Rischio 3 — Simboli test referenziati altrove

**Probabilità**: Molto bassa (task di puro unit test isolato).
**Mitigazione**: `grep -r "CtrlP\|ctrl_p" tests/` prima del rename
per escludere import o riferimenti incrociati.
