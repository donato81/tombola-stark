# REPORT — Analisi sostituzione hotkey Ctrl+P → Ctrl+Enter

**Data**: 2026-04-11  
**Autore**: Agent-Analyze  
**Stato**: DRAFT — solo analisi, nessuna modifica al codice  
**Obiettivo**: Mappare tutti i riferimenti a `Ctrl+P` nel codebase e definire
le modifiche necessarie per trasferirne la funzionalità a `Ctrl+Enter`.

---

## Sommario esecutivo

`Ctrl+P` è il tasto rapido che attiva il pulsante principale a due stati
in `FinestraGioco` (estrai numero / dichiara fine turno). L'hotkey è definita
in **un solo punto di esecuzione** (`finestra_gioco.py`, metodo `_on_char_hook`).
I restanti riferimenti sono commenti, docstring, documentazione e nomi di test.

`Ctrl+Enter` è **libero** in `finestra_gioco.py`: nessun binding esistente
intercetta quella combinazione a livello di frame. La sostituzione è
tecnicamente pulita e a basso rischio.

---

## 1. Inventario completo dei riferimenti a Ctrl+P

### 1.1 Codice di produzione

| File | Riga | Tipo | Contenuto |
|------|------|------|-----------|
| `bingo_game/ui/finestra_gioco.py` | 28 | Commento docstring | `Ctrl+P -> passa turno` |
| `bingo_game/ui/finestra_gioco.py` | 299 | Commento inline | `# Ctrl+P — passa turno` |
| `bingo_game/ui/finestra_gioco.py` | 300 | **Binding attivo** | `if ctrl and key == ord("P"):` |
| `bingo_game/partita.py` | 814 | Docstring metodo | `(tramite il pulsante "Ho finito"/Ctrl+P)` |

Il binding effettivo è **una sola condizione** all'interno di `_on_char_hook`
(riga 300), sotto il blocco `EVT_CHAR_HOOK` del frame.

```python
# estratto da finestra_gioco.py — metodo _on_char_hook
# Ctrl+P — passa turno
if ctrl and key == ord("P"):
    self._on_pulsante_principale(None)
    return
```

L'azione associata è `self._on_pulsante_principale(None)`, che gestisce tre
stati distinti in base a `self._fase_turno_ui`:

- `"attesa_estrazione"` → estrae il numero, avvia il timer finestra d'azione
  e pianifica la risposta dei bot.
- `"attesa_reclami"` → dichiara la fine del turno dell'utente umano
  (o emette messaggio idempotente se già dichiarato).
- `"pausa_turno"` → ignorato (nessuna azione).

### 1.2 Test di unità

| File | Riga | Tipo | Contenuto |
|------|------|------|-----------|
| `tests/unit/test_finestra_gioco_shortcuts.py` | 83 | Nome classe | `TestFinestraGiocoCtrlPAttesaReclami` |
| `tests/unit/test_finestra_gioco_shortcuts.py` | 95 | Nome metodo | `test_ctrl_p_attesa_reclami_emette_conferma_prima_dichiarazione` |
| `tests/unit/test_finestra_gioco_shortcuts.py` | 106 | Nome metodo | `test_ctrl_p_attesa_reclami_emette_messaggio_idempotente` |

**Nota**: i due test chiamano `FinestraGioco._on_pulsante_principale` direttamente,
non tramite `_on_char_hook`. Non testano il binding della tastiera ma la logica
della fase `attesa_reclami`. Funzionalmente continuerebbero a passare anche
dopo la sostituzione senza alcun aggiornamento. I nomi contengono `ctrl_p`
solo come etichetta semantica, non come dipendenza tecnica.

### 1.3 Documentazione (docs storage — read-only, non bloccante)

File nella cartella `docs/6 - docs storage/` che citano `Ctrl+P` in contesti
storici o descrittivi. Non richiedono aggiornamento per rendere il codice
funzionante, ma possono essere aggiornati per coerenza editoriale:

| File | Riga | Contesto |
|------|------|----------|
| `docs/6 - docs storage/3 - reports storage/idea_sviluppo_intefaccia.md` | 78, 130, 220 | Tabella mapping hotkey / note di design early-stage |
| `docs/6 - docs storage/1 - projects storage/DESIGN_CICLO_TURNO_V2.md` | 71, 127 | Descrizione flusso ciclo turno V2 |
| `docs/6 - docs storage/2 - coding plans storage/PLAN_ciclo_turno_fasi_reclami_collettivi_v0.9.5.md` | 229 | Nota implementativa |
| `docs/6 - docs storage/4 - todolist storage/TODO_ciclo_turno_fasi_reclami_collettivi_v0.9.5.md` | 101 | Checklist riga completata (`[x]`) |
| `docs/6 - docs storage/3 - reports storage/REPORT_BUG_HOTKEY_CTRL_P_CTRL_F_2026-04-05.md` | 1, 14 | Report bug storico — titolo e descrizione |
| `docs/6 - docs storage/3 - reports storage/REPORT_BUG_ACCESSIBILITA_FOCUS_TIMER_BOT_2026-04-05.md` | 164 | Report bug storico — riferimento descrittivo |

### 1.4 CHANGELOG

| File | Riga | Contesto |
|------|------|----------|
| `CHANGELOG.md` | 19 | Descrizione fix v1.1.0 — riferimento storico alla hotkey |

---

## 2. Analisi conflitti per Ctrl+Enter

### 2.1 In FinestraGioco (target principale)

Il metodo `_on_char_hook` di `FinestraGioco` non contiene alcun riferimento a
`wx.WXK_RETURN`. La combinazione `ctrl + WXK_RETURN` è completamente libera.

Mappa attuale delle combinazioni con `ctrl` in `_on_char_hook`:

| Combinazione | Tasto wx | Azione |
|---|---|---|
| Ctrl+P | `ord("P")` | passa turno — **da spostare** |
| Ctrl+F | `ord("F")` | apre dialog ricerca |
| Ctrl+1..6 | `ord("1")..ord("6")` | salta a cartella N |
| Ctrl+T | `ord("T")` | ultimo numero estratto |
| Ctrl+L | `ord("L")` | lista numeri estratti |
| Ctrl+U | `ord("U")` | ultimi 5 estratti |
| Ctrl+R | `ord("R")` | riepilogo tabellone |
| Ctrl+E | `ord("E")` | consulta log annunci |

Nessun elemento intercetta `wx.WXK_RETURN` con o senza `ctrl`.

### 2.2 In PannelloGriglia (_on_key_down)

Il metodo `_on_key_down` di `PannelloGriglia` non gestisce `WXK_RETURN`.
Ctrl+Enter sul pannello griglia ricadrebbe nella clausola finale `event.Skip()`,
senza azione. Con il nuovo binding a livello frame (EVT_CHAR_HOOK), l'evento
verrebbe intercettato dal frame prima che raggiunga `_on_key_down`, quindi
non c'è conflitto.

### 2.3 In DialogoRicerca (rischio parziale — da verificare)

Il `_on_char_hook` di `DialogoRicerca` gestisce `WXK_RETURN` **senza**
controllare il modificatore `ctrl`:

```python
def _on_char_hook(self, event: wx.KeyEvent) -> None:
    key = event.GetKeyCode()
    if key == wx.WXK_RETURN:   # ← intercetta anche Ctrl+Enter
        ...
```

Quando il dialog è aperto, il suo `EVT_CHAR_HOOK` si attiva prima di quello
del frame padre. Premendo `Ctrl+Enter` mentre il dialog ha il focus, il dialog
consumerebbe l'evento e farebbe una ricerca o conferma — **non** il passa-turno.
Questo è un comportamento coerente e desiderato: il dialog mantiene il controllo
del tasto Enter in tutti i suoi stati.

**Nessuna azione correttiva richiesta**: il comportamento del dialog non cambia.

### 2.4 In FinestraConfigurazione

Il `_on_char_hook` di `FinestraConfigurazione` gestisce `WXK_RETURN` senza
controllare `ctrl` (riga 117). Stesso ragionamento: la configurazione è una
finestra separata, non c'è sovrapposizione con il binding di `FinestraGioco`.

### 2.5 Compatibilità NVDA

La combinazione `Ctrl+Enter` non è assegnata a comandi standard di NVDA
in modalità focus (la modalità attiva su finestre wxPython). In modalità
navigazione/virtual buffer NVDA usa `Enter` da solo, non `Ctrl+Enter`.
Il framework usa già la tecnica EVT_CHAR_HOOK (che consuma l'evento prima
di NVDA quando `Skip()` non viene chiamato), usata con successo per tutti
gli altri shortcut. La nuova combinazione si integra nello stesso pattern.

Raccomandazione: verificare empiricamente con NVDA come da prassi del progetto.

---

## 3. Modifiche necessarie per l'implementazione

Le modifiche sono **minimali e localizzate**. Elencate in ordine di priorità.

### 3.1 Modifica obbligatoria — Binding attivo (1 riga)

**File**: `bingo_game/ui/finestra_gioco.py`  
**Metodo**: `_on_char_hook`  
**Linea**: 300  

```python
# PRIMA
if ctrl and key == ord("P"):

# DOPO
if ctrl and key == wx.WXK_RETURN:
```

### 3.2 Modifica obbligatoria — Commento inline (1 riga)

**File**: `bingo_game/ui/finestra_gioco.py`  
**Linea**: 299  

```python
# PRIMA
# Ctrl+P — passa turno

# DOPO
# Ctrl+Enter — passa turno
```

### 3.3 Modifica obbligatoria — Docstring intestazione file (1 riga)

**File**: `bingo_game/ui/finestra_gioco.py`  
**Linea**: 28  

```
# PRIMA
    Ctrl+P                 -> passa turno

# DOPO
    Ctrl+Enter             -> passa turno
```

### 3.4 Modifica consigliata — Docstring partita.py (1 riga)

**File**: `bingo_game/partita.py`  
**Linea**: 814  

```python
# PRIMA
(tramite il pulsante "Ho finito"/Ctrl+P)

# DOPO
(tramite il pulsante "Ho finito"/Ctrl+Enter)
```

### 3.5 Modifica consigliata — Nomi test (refactoring simbolico)

**File**: `tests/unit/test_finestra_gioco_shortcuts.py`

I nomi seguenti contengono `ctrl_p` come etichetta descrittiva:

| Simbolo attuale | Simbolo proposto |
|---|---|
| `TestFinestraGiocoCtrlPAttesaReclami` | `TestFinestraGiocoCtrlEnterAttesaReclami` |
| `test_ctrl_p_attesa_reclami_emette_conferma_prima_dichiarazione` | `test_ctrl_enter_attesa_reclami_emette_conferma_prima_dichiarazione` |
| `test_ctrl_p_attesa_reclami_emette_messaggio_idempotente` | `test_ctrl_enter_attesa_reclami_emette_messaggio_idempotente` |

**Nota**: questi test non testano il binding (`_on_char_hook`) ma la logica
di `_on_pulsante_principale`. Passano senza modifiche. Il rename è puramente
documentativo e non introduce rischi.

Se si vuole aggiungere un test esplicito del binding, occorrerebbe un test
che usa `_on_char_hook` con `_EventoTastoFittizio(wx.WXK_RETURN, ctrl=True)`.

---

## 4. Riepilogo impatto

| Categoria | File coinvolti | Linee | Rischio |
|---|---|---|---|
| Binding attivo | `finestra_gioco.py` | 1 | Basso |
| Commenti/docstring | `finestra_gioco.py`, `partita.py` | 3 | Nessuno |
| Nomi test | `test_finestra_gioco_shortcuts.py` | 3 nomi | Nessuno |
| Docs storage | 6 file archivio | n/a | Nessuno (opzionale) |
| CHANGELOG | 1 riga storica | n/a | Nessuno (non aggiornare) |

**Totale modifiche al codice eseguibile**: 1 riga (la condizione del binding).  
**Rischio regressione**: minimo — nessun altro modulo dipende da `ord("P")`;
la funzione `_on_pulsante_principale` rimane invariata.

---

## 5. Checklist pre-commit raccomandata

- [ ] Modificare `finestra_gioco.py` — binding + commenti (3 righe)
- [ ] Modificare `partita.py` — docstring (1 riga)
- [ ] Rinominare classe e metodi di test in `test_finestra_gioco_shortcuts.py`
- [ ] Aggiungere (opzionale) test esplicito del binding `Ctrl+Enter` via `_on_char_hook`
- [ ] `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [ ] `pytest tests/unit/test_finestra_gioco_shortcuts.py -v`
- [ ] Verifica empirica NVDA: Ctrl+Enter nella fase `attesa_estrazione`
      e nella fase `attesa_reclami`
