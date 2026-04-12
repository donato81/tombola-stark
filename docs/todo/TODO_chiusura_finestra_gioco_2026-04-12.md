# TODO — Chiusura visiva FinestraGioco
**Data:** 2026-04-12
**Riferimento piano:** `docs/design/PLAN_chiusura_finestra_gioco_2026-04-12.md`
**Riferimento analisi:** `docs/design/REPORT_ANALISI_chiusura_finestra_gioco_2026-04-12.md`
**Stato:** COMPLETATO

Ordine di implementazione: **B → D → C → A**
(colori pulsanti → stile log → lampeggio → header bar)

---

## Gruppo B — Colori semantici pulsanti azione

### B1 — Aggiungere costanti alias in tema.py

**File:** `bingo_game/ui/tema.py`
**Cosa fare:** Aggiungere 4 costanti alias nella sezione `# COLORI — Pulsanti`:
```
COLORE_BTN_INIZIA = "#2E7D32"
COLORE_BTN_PASSA_TURNO = "#1565C0"
COLORE_BTN_HO_FINITO = "#E65100"
COLORE_BTN_RIPRENDI = "#388E3C"
```
**Dipende da:** —
**Test minimo:** Aprire il file, cercare `COLORE_BTN_INIZIA` — deve essere visibile con il valore `#2E7D32`.

---

### B2 — Aggiornare import in finestra_gioco.py (blocco pulsanti)

**File:** `bingo_game/ui/finestra_gioco.py`
**Cosa fare:** Aggiungere al blocco `from bingo_game.ui.tema import (...)`:
```
COLORE_BTN_INIZIA, COLORE_BTN_PASSA_TURNO, COLORE_BTN_HO_FINITO, COLORE_BTN_RIPRENDI,
COLORE_BTN_PAUSA, COLORE_BTN_GRIGIO, COLORE_BTN_DISABILITATO,
```
**Dipende da:** B1
**Test minimo:** `python -m py_compile bingo_game/ui/finestra_gioco.py` — exit code 0, nessun ImportError.

---

### B3 — Colori nel ramo "in_pausa" di `aggiorna_stato_pulsante()`

**File:** `bingo_game/ui/finestra_gioco.py` — metodo `_aggiorna_stato_pulsante()`, ramo `fase == "in_pausa"`
**Cosa fare:**
- Dopo `self._btn_principale.Disable()`: aggiungere `SetBackgroundColour(COLORE_BTN_DISABILITATO)` + `SetForegroundColour(COLORE_TESTO_SCURO)` + `Refresh()`.
- Dopo `self._btn_pausa.Enable()`: aggiungere `SetBackgroundColour(COLORE_BTN_RIPRENDI)` + `SetForegroundColour(COLORE_TESTO_CHIARO)` + `Refresh()`.
**Dipende da:** B2
**Test minimo:** Avviare la partita, premere Ctrl+P (pausa). Il pulsante principale deve diventare grigio chiaro (`#BDBDBD`) e il pulsante "Riprendi" deve diventare verde (`#388E3C`). Verificare a occhio; nessuna variazione all'enunciazione NVDA attesa.

---

### B4 — Colori nel ramo generico di `aggiorna_stato_pulsante()` per `_btn_principale`

**File:** `bingo_game/ui/finestra_gioco.py` — metodo `_aggiorna_stato_pulsante()`, ramo `else` generico
**Cosa fare:** Dopo ciascuna assegnazione di `label`, subito dopo `self._btn_principale.SetLabel(label)`, aggiungere i tre sotto-rami:
- `fase == "attesa_reclami"` → `SetBackgroundColour(COLORE_BTN_HO_FINITO)` + `SetForegroundColour(COLORE_TESTO_CHIARO)`.
- `fase == "pausa_turno"` → `SetBackgroundColour(COLORE_BTN_GRIGIO)` + `SetForegroundColour(COLORE_TESTO_CHIARO)`.
- `primo_turno_eseguito = True` (label "Passa turno") → `SetBackgroundColour(COLORE_BTN_PASSA_TURNO)` + `SetForegroundColour(COLORE_TESTO_CHIARO)`.
- `else` (label "Inizia partita") → `SetBackgroundColour(COLORE_BTN_INIZIA)` + `SetForegroundColour(COLORE_TESTO_CHIARO)`.

Aggiungere `self._btn_principale.Refresh()` alla fine del ramo generico.
**Dipende da:** B2
**Test minimo:** Avviare la partita; il pulsante "Inizia partita" deve essere verde scuro. Premere Inizia partita; il pulsante "Passa turno" deve diventare blu. Nella finestra reclami, il pulsante "Ho finito" deve essere arancione. Tra i turni, il pulsante "Pausa in corso…" deve essere grigio (`#757575`).

---

### B5 — Colore del `_btn_pausa` nel ramo generico

**File:** `bingo_game/ui/finestra_gioco.py` — metodo `_aggiorna_stato_pulsante()`, sezione `if hasattr(self, "_btn_pausa"):`
**Cosa fare:** Dopo `self._btn_pausa.SetLabel("Metti in pausa")` nel ramo generico: aggiungere `SetBackgroundColour(COLORE_BTN_PAUSA)` + `SetForegroundColour(COLORE_TESTO_CHIARO)` + `Refresh()`.
**Dipende da:** B2, B3
**Test minimo:** All'avvio, il pulsante "Metti in pausa" deve essere grigio scuro (`#424242`). Dopo aver premuto Riprendi, deve tornare grigio scuro.

---

## Gruppo D — Stile visivo del log annunci

### D1 — Aggiornare import in finestra_gioco.py (blocco log)

**File:** `bingo_game/ui/finestra_gioco.py`
**Cosa fare:** Aggiungere al blocco `from bingo_game.ui.tema import (...)`:
```
COLORE_LOG_BG, COLORE_TESTO_MUTED,
FONT_LOG_PT, FONT_LOG_FAMIGLIA,
FONT_LABEL_PT,
```
**Dipende da:** B2 (stesso blocco import — fare in un'unica modifica)
**Test minimo:** `python -m py_compile bingo_game/ui/finestra_gioco.py` — exit code 0.

---

### D2 — Cambiare label e applicare font bold alla StaticText sopra il log

**File:** `bingo_game/ui/finestra_gioco.py` — `FinestraGioco._build_ui()`, blocco StaticText log (~riga 487)
**Cosa fare:** Sostituire la riga con la `wx.StaticText` anonima con:
```python
_lbl_log = wx.StaticText(panel, label="Cronologia annunci (Ctrl+E)")
_lbl_log.SetFont(wx.Font(FONT_LABEL_PT, wx.FONTFAMILY_DEFAULT,
                         wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
sizer.Add(_lbl_log, 0, wx.LEFT | wx.TOP, 5)
```
**Dipende da:** D1
**Test minimo:** Avviare la finestra di gioco; l'etichetta sopra il log deve leggere "Cronologia annunci (Ctrl+E)" in grassetto. Ctrl+E deve ancora portare il focus al log e vocalizzare "Consultazione log annunci." o "Log annunci vuoto.".

---

### D3 — Applicare stile scuro e font monospace al `_log_ctrl`

**File:** `bingo_game/ui/finestra_gioco.py` — `FinestraGioco._build_ui()`, dopo la creazione di `self._log_ctrl` (~riga 492)
**Cosa fare:** Aggiungere prima di `self._log_ctrl.SetName(...)`:
```python
self._log_ctrl.SetBackgroundColour(wx.Colour(COLORE_LOG_BG))
self._log_ctrl.SetForegroundColour(wx.Colour(COLORE_TESTO_MUTED))
font_log = wx.Font(FONT_LOG_PT, wx.FONTFAMILY_TELETYPE,
                   wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
font_log.SetFaceName(FONT_LOG_FAMIGLIA)
self._log_ctrl.SetFont(font_log)
```
**Dipende da:** D1
**Test minimo:** Avviare la finestra di gioco; il pannello log deve avere sfondo scuro (`#263238`) e testo grigio chiaro (`#B0BEC5`) in Courier New. Giocare un turno: il testo del turno deve apparire nel log con il nuovo stile.

---

## Gruppo C — Animazione lampeggio post-estrazione

### C1 — Aggiungere import `COLORE_CELLA_EVIDENZIATA` in finestra_gioco.py

**File:** `bingo_game/ui/finestra_gioco.py`
**Cosa fare:** Aggiungere `COLORE_CELLA_EVIDENZIATA` al blocco import da `tema`.
**Dipende da:** D1 (stesso blocco — fare in un'unica modifica, vedere D1+B2+D1+C1 come un'unica operazione di import)
**Test minimo:** `python -m py_compile bingo_game/ui/finestra_gioco.py` — exit code 0.

---

### C2 — Aggiungere attributi lampeggio in `PannelloCartella.__init__()`

**File:** `bingo_game/ui/finestra_gioco.py` — `PannelloCartella.__init__()`, dopo `self._build_ui()`
**Cosa fare:** Aggiungere:
```python
self._timer_lampeggio: Optional[wx.Timer] = None
self._numero_lampeggio: Optional[int] = None
self._lampeggio_attivo: bool = False
self._tick_lampeggio: int = 0
self._mappa_celle_numero: dict[int, wx.StaticText] = {}
```
**Dipende da:** C1
**Test minimo:** `python -m py_compile bingo_game/ui/finestra_gioco.py` — exit code 0.

---

### C3 — Aggiornare `PannelloCartella.aggiorna()` per costruire `_mappa_celle_numero`

**File:** `bingo_game/ui/finestra_gioco.py` — `PannelloCartella.aggiorna()`, inizio e fine metodo
**Cosa fare:**
- All'inizio del metodo (prima del loop 3×9): `if self._lampeggio_attivo: self.ferma_lampeggio()`
- Alla fine del metodo, dopo `self.Refresh()`: costruire `_mappa_celle_numero` con dict comprehension che itera griglia 3×9 raccogliendo solo le celle dove `griglia[row][col]` è `int`.
**Dipende da:** C2 (usa `ferma_lampeggio` che va definita prima, ma per il compilatore basta che esista nel metodo)
**Test minimo:** Avviare la partita, navigare in una cartella, estrarre un numero. Non deve esserci crash. L'attributo `_mappa_celle_numero` deve essere popolato (verificabile con un breakpoint o print temporaneo in test).

---

### C4 — Aggiungere metodo `PannelloCartella.avvia_lampeggio()`

**File:** `bingo_game/ui/finestra_gioco.py` — `PannelloCartella` (dopo `aggiorna()`)
**Cosa fare:** Implementare `avvia_lampeggio(numero: int) -> None` seguendo la specifica del piano:
- Guard: se numero non in `_mappa_celle_numero`, return.
- Ferma timer precedente e ripristina colore cella precedente.
- Avvia nuovo timer da 300ms con `Start(300)`.
**Dipende da:** C3
**Test minimo:** `python -m py_compile bingo_game/ui/finestra_gioco.py` — exit code 0.

---

### C5 — Aggiungere handler `_on_tick_lampeggio()` e metodo `ferma_lampeggio()` a `PannelloCartella`

**File:** `bingo_game/ui/finestra_gioco.py` — `PannelloCartella` (dopo `avvia_lampeggio()`)
**Cosa fare:**
- Aggiungere costante di modulo `_N_TICK_LAMPEGGIO: int = 7` prima della classe (oppure come attributo di classe).
- Implementare `_on_tick_lampeggio(event: wx.TimerEvent) -> None`: toggle colore, ferma a tick 7, stabilizza su `COLORE_CELLA_ESTRATTA_NON_SEGNATA`.
- Implementare `ferma_lampeggio() -> None`: `Stop()` timer + `None` + `_lampeggio_attivo = False`.
**Dipende da:** C4
**Test minimo:** Avviare la partita e giocare un turno con un numero presente nella cartella. La cella deve lampeggiare circa 2 secondi alternando giallo acceso/giallo chiaro, poi stabilizzarsi sul giallo chiaro fisso. Nessun testo viene vocalizzato durante il lampeggio.

---

### C6 — Aggiungere EVT_CLOSE e `_on_close()` in `FinestraGioco`

**File:** `bingo_game/ui/finestra_gioco.py`
**Cosa fare:**
- In `_bind_finestra()`: aggiungere `self.Bind(wx.EVT_CLOSE, self._on_close)`.
- Aggiungere metodo `_on_close(self, event: wx.CloseEvent) -> None` che chiama `ferma_lampeggio()` sul pannello cartella se disponibile, poi `event.Skip()`.
**Dipende da:** C5
**Test minimo:** Avviare la partita, estrarre un numero (cella lampeggiante attiva), poi chiudere la finestra con Alt+F4 o il pulsante X. L'applicazione non deve crashare. Il timer lampeggio deve fermarsi senza eccezioni.

---

### C7 — Aggiungere `FinestraGioco._aggiorna_griglie_visive()` cleanup lampeggio

**File:** `bingo_game/ui/finestra_gioco.py` — metodo `_aggiorna_griglie_visive()`
**Cosa fare:** Aggiungere prima della chiamata a `self._pannello_cartella.aggiorna(...)`:
```python
if hasattr(self._pannello_cartella, "ferma_lampeggio"):
    self._pannello_cartella.ferma_lampeggio()
```
**Dipende da:** C5
**Test minimo:** 

**Test A:** Avviare la partita, giocare un turno con un numero presente nella
cartella (lampeggio attivo). Attendere la fine del lampeggio naturale: la cella
deve stabilizzarsi sul giallo chiaro senza colori incoerenti.

**Test B (caso bordo critico):** Con il lampeggio attivo, premere immediatamente
Ctrl+1 (o Ctrl+2…6) per cambiare cartella. Il lampeggio deve interrompersi
immediatamente. La cella della vecchia cartella non deve continuare ad alternare
colori dopo il cambio. Nessun timer fantasma attivo dopo la navigazione.

---

### C8 — Aggiungere `_wx_avvia_lampeggio()` in `renderer_wx.py`

**File:** `bingo_game/ui/renderers/renderer_wx.py` — sezione `_wx_*` (dopo `_wx_aggiorna_tabellone`)
**Cosa fare:** Implementare `_wx_avvia_lampeggio(self, numero: int) -> None` che accede a `self._finestra._pannello_cartella.avvia_lampeggio(numero)` tramite duck typing con `hasattr`.
**Dipende da:** C5
**Test minimo:** `python -m py_compile bingo_game/ui/renderers/renderer_wx.py` — exit code 0.

---

### C9 — Chiamare `_wx_avvia_lampeggio()` in `annuncia_numero_estratto()`

**File:** `bingo_game/ui/renderers/renderer_wx.py` — metodo `annuncia_numero_estratto()`
**Cosa fare:** Aggiungere in `annuncia_numero_estratto()`, dopo `self._wx_aggiorna_output(testo)`
e **prima** di `self._ao2_vocalizza(testo)`:
```python
self._wx_avvia_lampeggio(numero)
```
⚠️ NON aggiungere dopo `_ao2_vocalizza` — posizione errata rispetto alla regola
testo → widget visivo → voce.
**Dipende da:** C8
**Test minimo:** Giocare un turno completo con un numero presente nella cartella. La cella lampeggia. Giocare un turno con un numero assente dalla cartella: nessun lampeggio visibile, nessun errore.

---

## Gruppo A — Header Bar

### A1 — Aggiungere `COLORE_HEADER_ACCENT` in tema.py

**File:** `bingo_game/ui/tema.py` — sezione `# COLORI — Accenti`
**Cosa fare:** Aggiungere `COLORE_HEADER_ACCENT = "#FFB300"` (alias semantico per il numero estratto nell'header).
**Dipende da:** —
**Test minimo:** Cercare `COLORE_HEADER_ACCENT` nel file — presente con valore `#FFB300`.

---

### A2 — Aggiornare import in finestra_gioco.py (blocco header)

**File:** `bingo_game/ui/finestra_gioco.py`
**Cosa fare:** Aggiungere al blocco import da `tema`:
```
COLORE_HEADER_BG, FONT_HEADER_PT, ALTEZZA_HEADER, COLORE_HEADER_ACCENT,
```
**Dipende da:** A1
**Test minimo:** `python -m py_compile bingo_game/ui/finestra_gioco.py` — exit code 0.

---

### A3 — Creare classe `HeaderBar(wx.Panel)` in finestra_gioco.py

**File:** `bingo_game/ui/finestra_gioco.py` — dopo `class PannelloGriglia`, prima di `class FinestraGioco`
**Cosa fare:** Implementare la classe seguendo la specifica del piano:
- `__init__()`: rimuove `TAB_TRAVERSAL`, imposta `COLORE_HEADER_BG`, `SetMinSize(-1, ALTEZZA_HEADER)`.
- `_build_ui()`: tre `wx.StaticText` in `BoxSizer(HORIZONTAL)`, font bold 12pt.
- `aggiorna(turno, ultimo_numero, premi_lista)`: aggiorna le label, chiama `Layout()`.
**Dipende da:** A2
**Test minimo:** `python -m py_compile bingo_game/ui/finestra_gioco.py` — exit code 0. Istanziare `HeaderBar` in isolamento (senza avviare la partita) non produce eccezioni.

---

### A4 — Aggiungere `_header_bar` come prima riga del sizer in `_build_ui()`

**File:** `bingo_game/ui/finestra_gioco.py` — `FinestraGioco._build_ui()`, dopo `sizer = wx.BoxSizer(wx.VERTICAL)`
**Cosa fare:** Aggiungere come seconda istruzione:
```python
self._header_bar = HeaderBar(panel)
sizer.Add(self._header_bar, 0, wx.EXPAND, 0)
```
**Dipende da:** A3
**Test minimo:** Avviare la finestra di gioco. In cima deve apparire una striscia scura con "Turno: —", "Estratto: —", "Premi: —". Il ciclo Tab non la attraversa. NVDA non vocalizza contenuti dell'header senza focus esplicito.

---

### A5 — Aggiungere `_wx_aggiorna_header()` in renderer_wx.py

**File:** `bingo_game/ui/renderers/renderer_wx.py` — sezione `_wx_*`
**Cosa fare:** Implementare `_wx_aggiorna_header(self, turno, ultimo_numero, premi_lista)` con duck typing: accede a `self._finestra._header_bar.aggiorna(...)` se l'attributo esiste.
**Dipende da:** A3
**Test minimo:** `python -m py_compile bingo_game/ui/renderers/renderer_wx.py` — exit code 0.

---

### A6 — Chiamare `_wx_aggiorna_header()` in `annuncia_numero_estratto()`

**File:** `bingo_game/ui/renderers/renderer_wx.py` — metodo `annuncia_numero_estratto()`
**Cosa fare:** Aggiungere tra `self._wx_aggiorna_output(testo)` e `self._ao2_vocalizza(testo)`:
```python
self._wx_aggiorna_header(turno=numero_turno, ultimo_numero=numero)
```
**Dipende da:** A5
**Test minimo:** Giocare un turno. L'header deve mostrare "Turno: 1" e "Estratto: [numero]" in colore giallo-arancio.

---

### A7 — Chiamare `_wx_aggiorna_header()` in `annuncia_premi_turno()`

**File:** `bingo_game/ui/renderers/renderer_wx.py` — metodo `annuncia_premi_turno()`
**Cosa fare:** ⚠️ Posizione obbligatoria: dopo `self._wx_aggiorna_output(testo)` e
prima di `self._ao2_vocalizza(testo)` — identico al task A6.

Aggiungere tra `self._wx_aggiorna_output(testo)` e `self._ao2_vocalizza(testo)`:
```python
nomi_premi = [f"{p.get('premio', '?')} — {p.get('giocatore', '?')}" for p in premi] if premi else []
self._wx_aggiorna_header(premi_lista=nomi_premi)
```
**Dipende da:** A5
**Test minimo:** Giocare turni fino a un ambo. L'header deve mostrare "Premi: ambo — [nome giocatore]" nel campo premi.

---

## Aggiornamento TODO generale

Dopo aver completato tutti i task del presente TODO, aggiornare il file `docs/todo.md`:

1. **Nessuna voce esistente** in `docs/todo.md` si riferisce direttamente agli elementi A, B, C, D
   di questa feature visiva — nessuna spunta da apporre su voci precedenti.

2. **Aggiungere in `docs/todo.md` sezione `### Progetti`** un link al documento di analisi:
   ```
   - [REPORT_ANALISI_chiusura_finestra_gioco_2026-04-12.md](design/REPORT_ANALISI_chiusura_finestra_gioco_2026-04-12.md) — COMPLETED
   ```

3. **Aggiungere in `docs/todo.md` sezione `### Piani`** un link al piano:
   ```
   - [PLAN_chiusura_finestra_gioco_2026-04-12.md](design/PLAN_chiusura_finestra_gioco_2026-04-12.md) — COMPLETED
   ```

4. **Aggiornare `CHANGELOG.md`** sezione `[Unreleased]` con:
   ```
   ### Added
   - Header Bar visiva in cima a FinestraGioco (turno, ultimo estratto, premi)
   - Colori semantici sui pulsanti principali (verde/blu/arancione/grigio per ogni fase)
   - Animazione lampeggio post-estrazione sulla cella cartella (2 secondi, wx.Timer)
   - Stile visivo scuro sul log annunci (sfondo #263238, testo #B0BEC5, Courier New 10pt)
   ```
