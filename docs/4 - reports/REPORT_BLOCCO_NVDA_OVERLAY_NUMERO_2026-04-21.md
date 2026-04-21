# Report Analisi: Blocco Vocalizzazione NVDA dopo Estrazione Numero

**Data**: 2026-04-21  
**Agente**: Agent-Analyze  
**Contesto**: Problema accessibilità dopo introduzione overlay visivo numero estratto  
**Stato**: Analisi completata — Causa radicale identificata

---

## Sintesi Problema

Dopo aver introdotto l'overlay visivo del numero estratto (`OverlayNumeroEstratto`), 
l'utente riscontra che:

1. Preme `Ctrl+Enter` per estrarre il primo numero
2. L'overlay appare sullo schermo
3. NVDA annuncia solo "panel" 
4. **NVDA NON annuncia il numero estratto** come faceva prima della modifica
5. Il gioco risulta bloccato per l'utente non vedente

### Impatto Critico

L'accessibilità NVDA è requisito **fondamentale** per questa applicazione.
L'overlay doveva essere un widget **puramente visivo** per utenti senza screen reader,
senza alterare il flusso di accessibilità esistente.

---

## Struttura Codice Attuale

### File Coinvolti

1. **bingo_game/ui/overlay_numero.py**  
   - Classe `OverlayNumeroEstratto` (wx.Frame)
   - Mostra numero in grande per 10 secondi
   - Style: `wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR | wx.FRAME_TOOL_WINDOW | wx.BORDER_NONE`

2. **bingo_game/ui/renderers/renderer_wx.py**  
   - Metodo `annuncia_numero_estratto(numero, turno)`  
   - Coordina aggiornamento visivo + vocalizzazione
   
3. **bingo_game/ui/finestra_gioco.py**  
   - Gestisce interazione utente (Ctrl+Enter)
   - Delega rendering a `WxRenderer`

### Flusso di Esecuzione Attuale

```
User: Ctrl+Enter
    ↓
finestra_gioco.py: esegui_fase_estrazione()
    ↓
renderer_wx.py: annuncia_numero_estratto(numero, turno)
    ↓
    ├─→ _wx_aggiorna_output(testo)           # Aggiorna textarea
    ├─→ _wx_avvia_lampeggio(numero)          # Lampeggio visivo
    ├─→ _wx_aggiorna_header(turno, numero)   # Aggiorna header bar
    ├─→ _wx_mostra_overlay_numero(numero)    # ⚠️ MOSTRA OVERLAY
    │       ↓
    │   overlay_numero.py: mostra_numero(numero)
    │       ├─→ SetLabel(str(numero))
    │       ├─→ Show()                       # ⚠️ PROBLEMA QUI
    │       └─→ Raise()                      # ⚠️ E QUI
    │
    └─→ _ao2_vocalizza(testo)                # ❌ Vocalizzazione bloccata
            ↓
        vocalizzatore.py: vocalizza_testo(testo)
            ↓
        accessible_output2: backend.speak(testo)
```

---

## Causa Radicale Identificata

### Problema Principale: Timing e Focus

La chiamata `_wx_mostra_overlay_numero(numero)` avviene **PRIMA** di `_ao2_vocalizza(testo)`.

Quando l'overlay viene mostrato (riga 88-92 di overlay_numero.py):

```python
def mostra_numero(self, numero: int) -> None:
    # ...
    self.Show()      # ⚠️ Mostra il frame
    self.Raise()     # ⚠️ Porta il frame in primo piano
    self._timer.Start(...)
```

Questo causa:

1. **Cattura/Interferenza Focus**  
   `Show()` + `Raise()` su un `wx.Frame` con `wx.STAY_ON_TOP` può:
   - Portare il focus sul nuovo frame (anche se non intenzionale)
   - Interrompere il flusso di accessibilità corrente
   - Impedire a NVDA di leggere il testo vocalizzato immediatamente dopo

2. **Sequenza Eventi wxPython**  
   wxPython processa gli eventi UI in modo asincrono:
   - `Show()` + `Raise()` generano eventi `wx.EVT_SHOW`, `wx.EVT_ACTIVATE`
   - Questi eventi possono essere processati PRIMA che AO2 completi la vocalizzazione
   - NVDA intercetta il cambio focus e annuncia "panel" invece del testo

3. **Natura Frame Top-Level**  
   `OverlayNumeroEstratto` è un `wx.Frame` completo, non un semplice widget:
   - Ha un proprio ciclo eventi
   - Ha un proprio focus management
   - `wx.STAY_ON_TOP` lo rende ancora più invasivo

---

## Evidenze dal Codice

### renderer_wx.py linea 197-203

```python
def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
    """Vocalizza il numero estratto nel contesto del turno (senza premi)."""
    testo = f"Turno {numero_turno}. Numero estratto: {numero}."
    self._wx_aggiorna_output(testo)
    self._wx_avvia_lampeggio(numero)
    self._wx_aggiorna_header(turno=numero_turno, ultimo_numero=numero)
    self._wx_mostra_overlay_numero(numero)  # ⚠️ Overlay mostrato QUI
    self._ao2_vocalizza(testo)               # ❌ Vocalizzazione DOPO
```

**Problema**: L'overlay viene mostrato PRIMA della vocalizzazione.

### overlay_numero.py linea 81-92

```python
def mostra_numero(self, numero: int) -> None:
    """Aggiorna il numero visualizzato e mostra l'overlay con timeout automatico."""
    if self._lbl_numero is None:
        return
    self._lbl_numero.SetLabel(str(numero))
    self._posiziona_overlay()
    if self._timer.IsRunning():
        self._timer.Stop()
    self.Show()        # ⚠️ Mostra il frame
    self.Raise()       # ⚠️ Porta in primo piano
    self._timer.Start(self._durata_ms, wx.TIMER_ONE_SHOT)
```

**Problema**: `Show()` + `Raise()` su frame top-level interferisce con focus/accessibilità.

### Style Flags dell'Overlay

```python
style = (
    wx.STAY_ON_TOP           # ⚠️ Sempre in primo piano
    | wx.FRAME_NO_TASKBAR    # OK - Non in taskbar
    | wx.FRAME_TOOL_WINDOW   # OK - Window decorations minime
    | wx.BORDER_NONE         # OK - Nessun bordo
)
```

**Problema**: `wx.STAY_ON_TOP` rende il frame ancora più invasivo per focus/accessibilità.

---

## Soluzioni Possibili

### Soluzione 1: Invertire Ordine di Chiamata (Quick Fix)

**Implementazione**: Spostare `_ao2_vocalizza(testo)` PRIMA di `_wx_mostra_overlay_numero(numero)`

```python
def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
    """Vocalizza il numero estratto nel contesto del turno (senza premi)."""
    testo = f"Turno {numero_turno}. Numero estratto: {numero}."
    self._wx_aggiorna_output(testo)
    self._wx_avvia_lampeggio(numero)
    self._wx_aggiorna_header(turno=numero_turno, ultimo_numero=numero)
    self._ao2_vocalizza(testo)               # ✅ Vocalizzazione PRIMA
    self._wx_mostra_overlay_numero(numero)  # ✅ Overlay DOPO
```

**Pro**:
- Fix minimale (1 riga spostata)
- Permette a AO2 di iniziare la vocalizzazione prima che l'overlay interferisca
- Basso rischio di regressione

**Contro**:
- Non elimina completamente il rischio di interferenza focus
- L'overlay potrebbe comunque interrompere la vocalizzazione se AO2 è lento

**Raccomandazione**: ⭐ **Immediato** - Fix da applicare subito

---

### Soluzione 2: Ritardo Overlay con wx.CallAfter (Best Practice)

**Implementazione**: Usare `wx.CallAfter` per posticipare la visualizzazione dell'overlay

```python
def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
    """Vocalizza il numero estratto nel contesto del turno (senza premi)."""
    testo = f"Turno {numero_turno}. Numero estratto: {numero}."
    self._wx_aggiorna_output(testo)
    self._wx_avvia_lampeggio(numero)
    self._wx_aggiorna_header(turno=numero_turno, ultimo_numero=numero)
    self._ao2_vocalizza(testo)
    # Ritarda la visualizzazione dell'overlay dopo la vocalizzazione
    wx.CallAfter(self._wx_mostra_overlay_numero, numero)
```

**Pro**:
- Garantisce che la vocalizzazione parta prima dell'overlay
- Segue best practice wxPython per operazioni UI non urgenti
- Compatibile con event loop wxPython

**Contro**:
- Leggero ritardo visivo (impercettibile, ~milliseconds)
- Richiede import wx nel renderer

**Raccomandazione**: ⭐⭐ **Consigliato** - Approccio più robusto

---

### Soluzione 3: Rendere Overlay Trasparente al Focus (Architetturale)

**Implementazione**: Modificare `OverlayNumeroEstratto` per non catturare focus

Opzione 3A: Aggiungere `wx.FRAME_NO_ACTIVATE` allo style

```python
style = (
    wx.STAY_ON_TOP
    | wx.FRAME_NO_TASKBAR
    | wx.FRAME_TOOL_WINDOW
    | wx.BORDER_NONE
    | wx.FRAME_NO_ACTIVATE  # ✅ Non attiva il frame quando mostrato
)
```

Opzione 3B: Non usare `Raise()`, solo `Show()`

```python
def mostra_numero(self, numero: int) -> None:
    # ...
    self.Show()
    # self.Raise()  # ❌ Rimosso - non portare in primo piano
    self._timer.Start(...)
```

Opzione 3C: Sostituire Frame con wx.PopupWindow (più leggero)

```python
class OverlayNumeroEstratto(wx.PopupWindow):
    # wx.PopupWindow non ha focus management come wx.Frame
    # Ideale per overlay decorativi
```

**Pro**:
- Fix architetturale che previene il problema alla fonte
- L'overlay diventa veramente "trasparente" all'accessibilità
- Migliora separazione concerns (visivo vs accessibilità)

**Contro**:
- Richiede modifica più profonda di `overlay_numero.py`
- Richiede test approfonditi per verificare comportamento visivo
- Opzione 3C: `wx.PopupWindow` ha limitazioni (no decorations, positioning complesso)

**Raccomandazione**: ⭐⭐⭐ **A lungo termine** - Da valutare in refactoring dedicato

---

### Soluzione 4: Ritardo Temporizzato (Fallback)

**Implementazione**: Ritardare l'overlay con timer esplicito (500ms)

```python
def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
    testo = f"Turno {numero_turno}. Numero estratto: {numero}."
    self._wx_aggiorna_output(testo)
    self._wx_avvia_lampeggio(numero)
    self._wx_aggiorna_header(turno=numero_turno, ultimo_numero=numero)
    self._ao2_vocalizza(testo)
    # Mostra overlay dopo 500ms per dare tempo ad AO2
    wx.CallLater(500, self._wx_mostra_overlay_numero, numero)
```

**Pro**:
- Garantisce separazione temporale netta tra vocalizzazione e overlay
- Utile se AO2 ha latenza elevata

**Contro**:
- Ritardo visivo percepibile (500ms)
- Sembra "laggy" per utenti vedenti
- Non risolve la causa radicale

**Raccomandazione**: ❌ **Sconsigliato** - Workaround non elegante

---

## Raccomandazione Finale

### Piano di Fix Consigliato

#### Fase 1: Quick Fix Immediato (oggi)

Applicare **Soluzione 1** + **Soluzione 3A**:

1. Spostare vocalizzazione prima dell'overlay (renderer_wx.py)
2. Aggiungere `wx.FRAME_NO_ACTIVATE` all'overlay (overlay_numero.py)

**File da modificare**:
- [renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py) linea 197-203
- [overlay_numero.py](../../bingo_game/ui/overlay_numero.py) linea 31-36

**Impatto**: Minimo, fix chirurgico

---

#### Fase 2: Miglioramento Architetturale (successivo ciclo)

Valutare **Soluzione 3C** (wx.PopupWindow):

- Refactoring completo di `OverlayNumeroEstratto`
- Eliminare gestione focus/activation completamente
- Test approfonditi con NVDA

**Deliverable**:
- Task in TODO.md
- DESIGN doc per refactoring overlay

---

## Checklist Validazione Post-Fix

Dopo aver applicato il fix, verificare:

- [ ] Ctrl+Enter estrae numero
- [ ] NVDA annuncia "Turno N. Numero estratto: X." immediatamente
- [ ] L'overlay appare visivamente in basso a destra
- [ ] NVDA NON annuncia "panel" o altri artefatti
- [ ] La finestra principale mantiene il focus tastiera
- [ ] La navigazione cartella funziona dopo estrazione
- [ ] L'overlay scompare automaticamente dopo 10 secondi
- [ ] Il comportamento è identico per numeri 1-90
- [ ] Test con estrazione multipla (3-4 numeri consecutivi)

---

## Conformità Standard Accessibilità

### Violazioni Correnti

- ❌ **UI Instructions** (ui.instructions.md):  
  > "Nessun aggiornamento dinamico silenzioso: usa wx.PostEvent o AccessibleDescription"  
  L'overlay appare senza notifica accessibilità

- ❌ **Validate Accessibility Skill** (validate-accessibility.skill.md):  
  > "Nessun feedback visivo esclusivo senza alternativa testuale"  
  L'overlay è puramente visivo ma interferisce con feedback testuale

### Fix Proposti Conformi

✅ Soluzione 1: Ripristina priorità vocalizzazione  
✅ Soluzione 3A: `wx.FRAME_NO_ACTIVATE` rende overlay non-invasivo  
✅ Soluzione 3C: `wx.PopupWindow` design pattern per overlay decorativi

---

## Note Tecniche Aggiuntive

### Comportamento AO2 (Accessible Output 2)

Da `vocalizzatore.py`:

```python
def vocalizza_testo(self, testo: str, interrompi: bool = False) -> None:
    try:
        self._backend.speak(testo, interrupt=interrompi)
    except Exception:
        _error_logger.exception("Errore backend TTS")
```

- `speak()` è **asincrono**: ritorna immediatamente, vocalizzazione continua in background
- `interrupt=False` di default in `_ao2_vocalizza` (riga 864 renderer_wx.py)
- Se overlay appare mentre AO2 sta parlando, NVDA potrebbe switchare output

### wxPython Event Loop

- `Show()` genera `wx.EVT_SHOW`
- `Raise()` genera `wx.EVT_ACTIVATE` (può cambiare focus)
- Eventi processati nella prossima iterazione event loop
- Se vocalizzazione non è ancora iniziata, NVDA intercetta il cambio focus prima

---

## Riferimenti

### Files Analizzati

- [bingo_game/ui/overlay_numero.py](../../bingo_game/ui/overlay_numero.py)
- [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)
- [bingo_game/ui/finestra_gioco.py](../../bingo_game/ui/finestra_gioco.py)
- [my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py)

### Skills/Instructions di Riferimento

- [.github/instructions/ui.instructions.md](../../.github/instructions/ui.instructions.md)
- [.github/skills/validate-accessibility.skill.md](../../.github/skills/validate-accessibility.skill.md)
- [.github/skills/accessibility-output.skill.md](../../.github/skills/accessibility-output.skill.md)

### Documentazione wxPython

- [wx.Frame.Show()](https://docs.wxpython.org/wx.Frame.html#wx.Frame.Show)
- [wx.Frame.Raise()](https://docs.wxpython.org/wx.Frame.html#wx.Frame.Raise)
- [wx.FRAME_NO_ACTIVATE](https://docs.wxpython.org/wx.Frame.html#wx-frame-styles)
- [wx.PopupWindow](https://docs.wxpython.org/wx.PopupWindow.html)
- [wx.CallAfter()](https://docs.wxpython.org/wx.functions.html#wx.CallAfter)

---

## Prossimi Passi

1. **Conferma utente** sulla raccomandazione fix Fase 1
2. **Delegare ad Agent-Code** per implementazione fix
3. **Test manuale NVDA** da parte utente
4. **Commit atomico** con messaggio: `fix(ui): ripristina vocalizzazione NVDA durante estrazione numero`
5. **Update CHANGELOG.md** sezione `[Unreleased] - Fixed`

---

**Fine Report Analisi**
