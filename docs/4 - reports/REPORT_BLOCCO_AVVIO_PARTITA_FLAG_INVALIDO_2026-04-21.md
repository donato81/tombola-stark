# Report: Blocco Avvio Partita — Flag wxPython Non Valido

**Data**: 2026-04-21  
**Agente**: Agent-Analyze  
**Priorità**: CRITICA — il gioco non si avvia  
**Stato**: Causa radicale identificata — fix proposto

---

## Sintomo Osservato

Dopo l'avvio dell'applicazione:
1. La finestra principale si apre correttamente
2. La finestra di configurazione partita si apre correttamente
3. L'utente pressa "Avvia Partita"
4. **Nulla accade** — la finestra di configurazione rimane aperta
5. La finestra di gioco non viene mai aperta

---

## Causa Radicale

Il commit `dddfbe328799c2b4a650c207d734dc2f73967113` (`fix(ui): ripristina vocalizzazione NVDA durante estrazione numero`) ha introdotto il flag `wx.FRAME_NO_ACTIVATE` in `bingo_game/ui/overlay_numero.py`.

**Questo attributo non esiste in wxPython 4.2.1:**

```
>>> import wx
>>> hasattr(wx, 'FRAME_NO_ACTIVATE')
False
>>> wx.version()
'4.2.1 msw (phoenix) wxWidgets 3.2.2.1'
```

L'unico attributo wx simile disponibile è `wx.FRAME_NO_TASKBAR`.  
Non esiste nessun attributo `NO_ACTIVATE` o `NOACTIVATE` nel modulo wx.

---

## Flusso di Errore

```
FinestraConfigurazione._on_avvia_partita()
    ↓
finestra_gioco = FinestraGioco(...)   ← costruzione del frame
    ↓
FinestraGioco.__init__()
    ↓
self._overlay_numero = OverlayNumeroEstratto(parent=self)
    ↓
OverlayNumeroEstratto.__init__()
    ↓
style = (
    wx.STAY_ON_TOP
    | wx.FRAME_NO_TASKBAR
    | wx.FRAME_TOOL_WINDOW
    | wx.FRAME_NO_ACTIVATE      ← ❌ AttributeError QUI
    | wx.BORDER_NONE
)
    ↓
AttributeError: module 'wx' has no attribute 'FRAME_NO_ACTIVATE'
    ↓
wxPython App.OnExceptionInMainLoop() consuma l'eccezione
    ↓
L'handler del pulsante termina silenziosamente
    ↓
FinestraGioco non viene mai creata né mostrata
    ↓
Utente: "non succede nulla"
```

### Perché wxPython Consuma l'Errore

wxPython intercetta tutte le eccezioni non gestite che si propagano fuori dagli handler degli eventi wx tramite `App.OnExceptionInMainLoop()`. Il comportamento default è stampare il traceback su stderr e continuare l'esecuzione. Poiché la costruzione di `FinestraGioco` avviene dentro l'handler dell'evento click del pulsante, l'eccezione viene silenziata e l'utente non riceve alcun feedback visivo dell'errore.

---

## Analisi del Commit Responsabile

### Modifica introdotta in overlay_numero.py

**Prima** (funzionante):
```python
style = (
    wx.STAY_ON_TOP
    | wx.FRAME_NO_TASKBAR
    | wx.FRAME_TOOL_WINDOW
    | wx.BORDER_NONE
)
```

**Dopo** (rotto):
```python
style = (
    wx.STAY_ON_TOP
    | wx.FRAME_NO_TASKBAR
    | wx.FRAME_TOOL_WINDOW
    | wx.FRAME_NO_ACTIVATE   # ← non esiste in wxPython 4.2.1
    | wx.BORDER_NONE
)
```

### Responsabilità

Il flag è stato aggiunto in buona fede per impedire che l'overlay catturasse il focus. Il problema è che:

1. `wx.FRAME_NO_ACTIVATE` non è una costante wxPython documentata
2. Il subagent non ha verificato l'esistenza del flag prima di scriverlo
3. Non è stato eseguito un test di importazione runtime sul file modificato

---

## Ricerca Alternative valide

La ricerca di tutti gli attributi wx correlati al focus/activation disponibili in wxPython 4.2.1 ha prodotto solo `['FRAME_NO_TASKBAR']`.

**Non esiste in wxPython 4.2.1 una costante diretta** equivalente a `wxNO_ACTIVATE` di wxWidgets (C++).

Le opzioni disponibili in wxPython per ridurre l'interferenza focus di un overlay sono:

### Opzione A — Rimuovere il flag (soluzione minima)

Rimuovere semplicemente `wx.FRAME_NO_ACTIVATE`. Il problema originale di NVDA era già risolto dalla prima modifica del commit (inversione dell'ordine `_ao2_vocalizza` / `_wx_mostra_overlay_numero`). Il flag era un layer di protezione aggiuntivo non strettamente necessario.

**Rischio**: lieve possibilità che l'overlay catturi focus in edge case, ma con la vocalizzazione già precedente, l'annuncio NVDA è già garantito.

### Opzione B — SetWindowStyle senza attributo mancante

Dopo la costruzione, tentare via Win32 API (non raccomandato, dipendente da OS).

### Opzione C — wx.PopupWindow (refactoring futuro)

Sostituire `wx.Frame` con `wx.PopupWindow` che per design non attiva o cattura focus. Richiede refactoring completo dell'overlay. Soluzione robusta a lungo termine, già documentata nel report precedente come Soluzione 3C.

---

## Fix Raccomandato

### Fix immediato — Opzione A

Rimuovere la sola riga `| wx.FRAME_NO_ACTIVATE` da `bingo_game/ui/overlay_numero.py`.

**Nessun'altra modifica necessaria.** L'inversione dell'ordine in `renderer_wx.py` rimane intatta e continua a garantire che NVDA riceva il testo prima dell'overlay.

**File da modificare**: [bingo_game/ui/overlay_numero.py](../../bingo_game/ui/overlay_numero.py)

**Delta**:
```diff
 style = (
     wx.STAY_ON_TOP
     | wx.FRAME_NO_TASKBAR
     | wx.FRAME_TOOL_WINDOW
-    | wx.FRAME_NO_ACTIVATE
     | wx.BORDER_NONE
 )
```

**Commit message**:
```
fix(ui): rimuove wx.FRAME_NO_ACTIVATE non valido in wxPython 4.2.1

Il flag wx.FRAME_NO_ACTIVATE non esiste in wxPython 4.2.1 e causa
AttributeError all'avvio della partita, impedendo l'apertura della
FinestraGioco. La correzione lo rimuove; la vocalizzazione NVDA
rimane comunque garantita dall'inversione dell'ordine
_ao2_vocalizza / _wx_mostra_overlay_numero già presente nel commit
dddfbe3.
```

---

## Checklist Validazione Post-Fix

- [ ] `python -m py_compile bingo_game/ui/overlay_numero.py` → exit 0
- [ ] `python -c "from bingo_game.ui.overlay_numero import OverlayNumeroEstratto"` → no errori
- [ ] Avvio applicazione con `py main.py`
- [ ] Premere "Avvia Partita" → finestra di gioco si apre
- [ ] `Ctrl+Enter` estrae numero
- [ ] NVDA annuncia "Turno N. Numero estratto: X." immediatamente
- [ ] Suite test: `pytest tests/ -q` → 0 regressioni

---

## Lezione Appresa

Quando si usa un attributo di una libreria esterna (wxPython), occorre sempre verificare che esista prima di scrivere il codice:

```python
# Verifica prima di usare
import wx
print(hasattr(wx, 'FRAME_NO_ACTIVATE'))  # False → non usare
```

Oppure eseguire un import di smoke test nella pre-commit checklist:

```
python -c "from bingo_game.ui.overlay_numero import OverlayNumeroEstratto"
```

Questo avrebbe rilevato l'errore prima del commit.

---

**Fine Report**
