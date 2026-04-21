# Report di diagnosi: NVDA legge "panel" all'estrazione del numero

**Data**: 21 aprile 2026
**Agente**: Agent-Analyze
**Stato**: DIAGNOSI COMPLETA — pronto per Agent-Code

---

## 1. Sintomo osservato

Quando l'utente preme il tasto di estrazione, NVDA annuncia "panel" invece di
leggere "Turno N. Numero estratto: X.". Il gioco è funzionante (nessun errore
visibile), ma l'annuncio del numero è completamente perso.

---

## 2. Cronologia dei tentativi precedenti e perché hanno fallito

### Tentativo 1 — Inversione dell'ordine `_ao2_vocalizza` / `_wx_mostra_overlay`

**Ipotesi**: l'overlay appariva prima della vocalizzazione, rubando l'annuncio.
**Risultato**: NVDA continua a leggere "panel" invece del numero.
**Perché ha fallito**: l'ordine non è il problema. La chiamata
`speak(testo, interrupt=False)` di AO2 è **asincrona**: accoda il testo nella
coda di sintesi di NVDA e ritorna immediatamente. Le righe successive vengono
eseguite prima che NVDA elabori il testo accodato. Quando subito dopo
`Raise()` genera un evento di focus, NVDA lo gestisce con `interrupt=True`
implicito (le transizioni di focus interrompono sempre la coda), cancellando
il testo appena accodato.

### Tentativo 2 — Aggiunta di `wx.FRAME_NO_ACTIVATE` agli stili del frame

**Ipotesi**: il flag avrebbe prevenuto l'attivazione della finestra overlay.
**Risultato**: `AttributeError` silenzioso → la partita non si avviava.
**Perché ha fallito**: `wx.FRAME_NO_ACTIVATE` non esiste in wxPython 4.2.1
(`hasattr(wx, 'FRAME_NO_ACTIVATE') = False`). Era un approccio nella
direzione giusta ma con l'attributo sbagliato.

---

## 3. Analisi della causa radice

### 3.1 La catena di chiamate in `annuncia_numero_estratto`

```python
# renderer_wx.py, linea 195
def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
    testo = f"Turno {numero_turno}. Numero estratto: {numero}."
    self._wx_aggiorna_output(testo)           # [A]
    self._wx_avvia_lampeggio(numero)           # [B]
    self._wx_aggiorna_header(turno=..., ...)   # [C]
    self._ao2_vocalizza(testo)                 # [D] — accoda in NVDA, ritorna subito
    self._wx_mostra_overlay_numero(numero)     # [E] — PROBLEMA
```

### 3.2 Cosa fa `_wx_mostra_overlay_numero` (passo E)

```
renderer._wx_mostra_overlay_numero(numero)
  → finestra_gioco.mostra_overlay_numero(numero)
    → overlay_numero.mostra_numero(numero)
      → self.Show()          # [E1] mostra il frame overlay
      → self.Raise()         # [E2] ← CAUSA PRIMARIA
      → self._timer.Start()
```

### 3.3 Perché `Raise()` rompe NVDA

`wx.Frame.Raise()` su Windows chiama `::SetForegroundWindow(hwnd)`.
`SetForegroundWindow()` genera l'evento di accessibilità Win32
**`EVENT_SYSTEM_FOREGROUND`** tramite `NotifyWinEvent`.

NVDA intercetta `EVENT_SYSTEM_FOREGROUND` attraverso i suoi hook WinEvent.
Quando lo riceve, NVDA:

1. Sposta il cursore di accessibilità sulla nuova finestra foreground.
2. Naviga nell'albero accessibile della finestra fino al primo elemento.
3. In `OverlayNumeroEstratto` trova `wx.Panel` (senza `SetName`).
4. Annuncia la **role** dell'elemento: **"panel"**.
5. Questa operazione usa `interrupt=True` internamente → cancella il testo
   "Turno N. Numero estratto: X." che era stato accodato al passo [D].

### 3.4 Perché anche `Show()` da solo è problematico

`wx.TopLevelWindow.Show(True)` in wxMSW chiama internamente
`ShowWindow(hwnd, SW_SHOW)`, che attiva la finestra
(equivalente a `SW_SHOWNORMAL`). Questo può generare `WM_ACTIVATE` e, in
alcuni casi, `EVENT_SYSTEM_FOREGROUND` anche senza `Raise()`.

La conferma: `ShowWithoutActivating` esiste in wxPython 4.2.1
(`hasattr(frm, 'ShowWithoutActivating') = True`). Questo metodo chiama
internamente `ShowWindow(hwnd, SW_SHOWNOACTIVATE)`, che mostra la finestra
senza renderla foreground e senza inviare `WM_ACTIVATE`.

### 3.5 Perché l'approccio `wx.Frame` è sbagliato per questo caso

Un `wx.Frame` è una finestra di primo livello a tutti gli effetti:
- Compare nell'albero di accessibilità di NVDA come oggetto navigabile.
- `Show()` standard attiva la finestra.
- Qualsiasi `Raise()` genera eventi di focus che NVDA traccia.
- Non esiste un modo nativo e semplice per renderlo "invisibile ad NVDA"
  senza usare hook Win32 di basso livello.

L'overlay visivo per utenti vedenti **non deve essere un `wx.Frame`**.

---

## 4. Soluzione proposta

La soluzione è chirurgica: agisce solo su `overlay_numero.py` e
`renderer_wx.py`, senza toccare la logica di gioco o il renderer per il
resto.

### 4.1 Modifica 1 — `overlay_numero.py`: sostituire `Show()` e rimuovere `Raise()`

**File**: `bingo_game/ui/overlay_numero.py`
**Metodo**: `mostra_numero()`

```python
# PRIMA (comportamento attuale — ROTTO):
def mostra_numero(self, numero: int) -> None:
    if self._lbl_numero is None:
        return
    self._lbl_numero.SetLabel(str(numero))
    self._posiziona_overlay()
    if self._timer.IsRunning():
        self._timer.Stop()
    self.Show()          # ← attiva la finestra (SW_SHOW)
    self.Raise()         # ← SetForegroundWindow → NVDA dice "panel"
    self._timer.Start(self._durata_ms, wx.TIMER_ONE_SHOT)

# DOPO (fix):
def mostra_numero(self, numero: int) -> None:
    if self._lbl_numero is None:
        return
    self._lbl_numero.SetLabel(str(numero))
    self._posiziona_overlay()
    if self._timer.IsRunning():
        self._timer.Stop()
    self.ShowWithoutActivating()   # ← SW_SHOWNOACTIVATE, nessun WM_ACTIVATE
    # Raise() rimosso: STAY_ON_TOP garantisce la visibilità senza SetForegroundWindow
    self._timer.Start(self._durata_ms, wx.TIMER_ONE_SHOT)
```

**Perché funziona**: `ShowWithoutActivating()` chiama `ShowWindow(hwnd,
SW_SHOWNOACTIVATE)` che rende visibile la finestra senza attivare la finestra,
senza inviare `WM_ACTIVATE`, senza generare `EVENT_SYSTEM_FOREGROUND`.
NVDA non riceve alcun evento di focus e non anuncia "panel".
Il flag `STAY_ON_TOP` garantisce che l'overlay rimanga visibile sopra le
altre finestre senza bisogno di `Raise()`.

### 4.2 Modifica 2 — `renderer_wx.py`: aggiungere `wx.CallLater` come misura difensiva

**File**: `bingo_game/ui/renderers/renderer_wx.py`
**Metodo**: `annuncia_numero_estratto()`

```python
# PRIMA:
    self._ao2_vocalizza(testo)
    self._wx_mostra_overlay_numero(numero)

# DOPO:
    self._ao2_vocalizza(testo)
    wx.CallLater(350, self._wx_mostra_overlay_numero, numero)
```

**Perché è necessaria come misura difensiva**: anche senza Raise(), c'è un
breve intervallo tra il momento in cui AO2 accoda il testo e il momento in cui
NVDA inizia a leggerlo. Differire l'overlay di 350 ms garantisce che NVDA abbia
già iniziato la lettura prima che la finestra overlay diventi visibile.
350 ms è impercettibile per l'utente vedente ma sufficiente per separare i due
eventi nell'elaborazione di NVDA.

**Nota**: `wx.CallLater` richiede l'import di `wx` nel modulo `renderer_wx.py`.
`wx` è già importato tramite `TYPE_CHECKING` ma potrebbe servire un import
runtime; verificare se è già disponibile.

### 4.3 Soluzione ideale futura (fuori scope di questo fix)

Sostituire `wx.Frame` con una delle seguenti alternative:
- **Disegno diretto** sul `PannelloGriglia` usando `wx.ClientDC` +
  `wx.Timer` per la durata. Nessuna finestra separata, nessun evento
  accessibilità.
- **`wx.PopupWindow`** configurato come layered window: meno supporto
  stilistico ma intrinsecamente non-modal e meno tracciato da NVDA.

Queste alternative richiedono una riscrittura del componente e sono
consigliate per un ciclo di sviluppo futuro.

---

## 5. Verifica che il fix non rompe l'accessibilità

- La vocalizzazione del numero avviene tramite `_ao2_vocalizza` (paso D)
  prima che l'overlay appaia: questo percorso non è toccato.
- `PannelloGriglia` mantiene il focus durante tutta l'operazione.
- L'overlay rimane visivamente presente grazie a `STAY_ON_TOP`.
- `Hide()` nel timer non genera eventi di focus (solo nasconde la finestra).

---

## 6. File coinvolti

| File | Modifica | Righe approssimative |
|------|----------|----------------------|
| `bingo_game/ui/overlay_numero.py` | `Show()` → `ShowWithoutActivating()`, rimosso `Raise()` | 87-89 |
| `bingo_game/ui/renderers/renderer_wx.py` | `wx.CallLater(350, ...)` intorno alla chiamata overlay | 201-202 |

---

## 7. Comandi di pre-commit da eseguire dopo l'implementazione

```bash
python -m py_compile bingo_game/ui/overlay_numero.py
python -m py_compile bingo_game/ui/renderers/renderer_wx.py
pytest --tb=short   # baseline: 355 test passing
```

---

## 8. Messaggio di commit proposto

```
fix(ui): sostituisce Show/Raise con ShowWithoutActivating nell'overlay

Causa radice del problema NVDA: Raise() chiama SetForegroundWindow che
genera EVENT_SYSTEM_FOREGROUND; NVDA intercetta l'evento, naviga
nell'overlay, annuncia "panel" con interrupt implicito cancellando
il numero estratto dalla coda di sintesi.

Soluzione:
- overlay_numero.py: Show() -> ShowWithoutActivating() (SW_SHOWNOACTIVATE),
  Raise() rimosso. STAY_ON_TOP garantisce la visibilita visiva.
- renderer_wx.py: CallLater(350ms) separa vocalizzazione da apparizione
  overlay, misura difensiva contro race condition nella coda NVDA.

Refs: REPORT_DIAGNOSI_NVDA_OVERLAY_RADICE_2026-04-21.md
```
