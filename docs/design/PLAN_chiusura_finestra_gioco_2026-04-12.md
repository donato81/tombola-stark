# PLAN — Chiusura visiva FinestraGioco
**Data:** 2026-04-12
**Autore:** Agent-Design (via Agent-Orchestrator)
**Riferimento analisi:** `docs/design/REPORT_ANALISI_chiusura_finestra_gioco_2026-04-12.md`
**Stato:** REVIEWED

---

## Sezione B — Colori semantici sui pulsanti azione

### Obiettivo

I tre pulsanti principali (`_btn_principale`, `_btn_pausa`, `_btn_torna_menu`) ricevono
`SetBackgroundColour()` e `SetForegroundColour()` sincronizzati con l'etichetta assegnata
in `_aggiorna_stato_pulsante()`.

### Costanti da aggiungere in tema.py

Aggiungere nella sezione `# COLORI — Pulsanti`:

```python
COLORE_BTN_INIZIA = "#2E7D32"        # "Inizia partita" (verde scuro)
COLORE_BTN_PASSA_TURNO = "#1565C0"   # "Passa turno" (blu istituzionale)
COLORE_BTN_HO_FINITO = "#E65100"     # "Ho finito — avvia verifica" (arancione)
COLORE_BTN_RIPRENDI = "#388E3C"      # "Riprendi" (verde medio)
```

`COLORE_BTN_PAUSA = "#424242"`, `COLORE_BTN_GRIGIO = "#757575"` e
`COLORE_BTN_DISABILITATO = "#BDBDBD"` sono già presenti in `tema.py`.

### Aggiornamento import in finestra_gioco.py

Aggiungere al blocco `from bingo_game.ui.tema import (...)`:

```python
COLORE_BTN_INIZIA, COLORE_BTN_PASSA_TURNO, COLORE_BTN_HO_FINITO, COLORE_BTN_RIPRENDI,
COLORE_BTN_PAUSA, COLORE_BTN_GRIGIO, COLORE_BTN_DISABILITATO,
```

### Modifica a `_aggiorna_stato_pulsante()` — ramo "in_pausa"

Posizione: riga ~875 — all'inizio del metodo, ramo `if fase == "in_pausa":`.

Aggiungere dopo `self._btn_principale.Disable()`:

```python
self._btn_principale.SetBackgroundColour(wx.Colour(COLORE_BTN_DISABILITATO))
self._btn_principale.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
self._btn_principale.Refresh()
```

Aggiungere dopo `self._btn_pausa.Enable()` (nel ramo in_pausa):

```python
self._btn_pausa.SetBackgroundColour(wx.Colour(COLORE_BTN_RIPRENDI))
self._btn_pausa.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
self._btn_pausa.Refresh()
```

### Modifica a `_aggiorna_stato_pulsante()` — ramo generico

Dopo l'assegnazione di `label` (quattro sotto-rami) e dopo `self._btn_principale.SetLabel(label)`:

```python
# Ramo: fase == "attesa_reclami"
self._btn_principale.SetBackgroundColour(wx.Colour(COLORE_BTN_HO_FINITO))
self._btn_principale.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))

# Ramo: fase == "pausa_turno"
self._btn_principale.SetBackgroundColour(wx.Colour(COLORE_BTN_GRIGIO))
self._btn_principale.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))

# Ramo: primo_turno_eseguito = True  (label = "Passa turno")
self._btn_principale.SetBackgroundColour(wx.Colour(COLORE_BTN_PASSA_TURNO))
self._btn_principale.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))

# Ramo: else  (label = "Inizia partita")
self._btn_principale.SetBackgroundColour(wx.Colour(COLORE_BTN_INIZIA))
self._btn_principale.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
```

Dopo la sezione `if hasattr(self, "_btn_pausa"):` nel ramo generico, a valle di
`self._btn_pausa.SetLabel("Metti in pausa")`:

```python
self._btn_pausa.SetBackgroundColour(wx.Colour(COLORE_BTN_PAUSA))
self._btn_pausa.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
self._btn_pausa.Refresh()
```

Aggiungere `self._btn_principale.Refresh()` alla fine di entrambi i rami del metodo.

### Gestione `_btn_torna_menu`

Il pulsante `_btn_torna_menu` è visibile solo a fine partita (`Show()` in
`_esegui_verifica_premi()`). Il design originale specifica: "sfondo neutro, visibile solo
a fine partita — comportamento già implementato". Non richiede colore semantico specifico;
rimane con lo stile di default di sistema. Nessuna modifica necessaria.

### Nessuna modifica al renderer

I colori seguono la logica di stato già gestita dal pulsante. Il renderer non conosce
i dettagli visivi dei pulsanti.

---

## Sezione D — Stile visivo del log annunci

### Obiettivo

Il `wx.TextCtrl` del log riceve sfondo scuro + testo chiaro + font monospace.
La `wx.StaticText` sopra di esso riceve una label più chiara e font bold.

### Costanti necessarie

Tutte già presenti in `tema.py`. Aggiungere agli import di `finestra_gioco.py`:

```python
COLORE_LOG_BG, COLORE_TESTO_MUTED,
FONT_LOG_PT, FONT_LOG_FAMIGLIA,
FONT_LABEL_PT,
```

### Modifica a `_build_ui()` — etichetta log

Sostituire la riga attuale (~487):

```python
# Prima (riga ~487):
sizer.Add(wx.StaticText(panel, label="Log annunci (Ctrl+E per consultare):"), 0, wx.LEFT | wx.TOP, 5)
```

Con:

```python
# Dopo:
_lbl_log = wx.StaticText(panel, label="Cronologia annunci (Ctrl+E)")
_lbl_log.SetFont(wx.Font(
    FONT_LABEL_PT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
))
sizer.Add(_lbl_log, 0, wx.LEFT | wx.TOP, 5)
```

### Modifica a `_build_ui()` — stile _log_ctrl

Dopo la creazione di `self._log_ctrl` (~492) e prima di `self._log_ctrl.SetName(...)`:

```python
self._log_ctrl.SetBackgroundColour(wx.Colour(COLORE_LOG_BG))
self._log_ctrl.SetForegroundColour(wx.Colour(COLORE_TESTO_MUTED))
self._log_ctrl.SetFont(wx.Font(
    FONT_LOG_PT, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
))
```

Nota: `wx.FONTFAMILY_TELETYPE` garantisce una famiglia monospaziata indipendente
dalla disponibilità di "Courier New" sul sistema. Come fallback aggiuntivo si può
usare `wx.Font(FONT_LOG_PT, wx.FONTFAMILY_TELETYPE, ...)` con face name:

```python
font_log = wx.Font(FONT_LOG_PT, wx.FONTFAMILY_TELETYPE,
                   wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
font_log.SetFaceName(FONT_LOG_FAMIGLIA)  # "Courier New" — fallback implicito se non disponibile
self._log_ctrl.SetFont(font_log)
```

### Nessuna modifica al renderer o al binding Ctrl+E

`_consulta_log()` usa solo `self._log_ctrl.SetFocus()` e `GetValue()` —
entrambi invariati rispetto ai cambiamenti di stile.

---

## Sezione C — Animazione lampeggio post-estrazione

### Obiettivo

Quando un numero estratto è presente nella cartella corrente del giocatore umano,
la cella del `PannelloCartella` lampeggia per ~2 secondi alternando tra
`COLORE_CELLA_EVIDENZIATA` (#FFF176) e `COLORE_CELLA_ESTRATTA_NON_SEGNATA` (#FFF9C4),
poi si stabilizza sul colore fisso.

### Costante da importare in finestra_gioco.py (già presente in tema.py)

```python
COLORE_CELLA_EVIDENZIATA,
```

### Nuovi attributi in `PannelloCartella.__init__()`

Aggiungere dopo `self._build_ui()`:

```python
# Stato animazione lampeggio
self._timer_lampeggio: Optional[wx.Timer] = None
self._numero_lampeggio: Optional[int] = None
self._lampeggio_attivo: bool = False
self._tick_lampeggio: int = 0
self._mappa_celle_numero: dict[int, wx.StaticText] = {}
```

### Modifica a `PannelloCartella.aggiorna()`

Aggiungere alla fine del metodo, dopo `self.Refresh()`:

```python
# Aggiorna la mappa numero → cella per l'animazione lampeggio
self._mappa_celle_numero = {
    int(griglia[row][col]): self._celle[row][col]
    for row in range(3)
    for col in range(9)
    if isinstance(griglia[row][col], int)
}
```

Aggiungere anche la chiamata di cleanup prima di ridipingere, per evitare
che un lampeggio in corso interferisca con il repaint:

```python
# All'inizio di aggiorna(), prima del loop righe:
if self._lampeggio_attivo:
    self.ferma_lampeggio()
```

### Nuovo metodo `PannelloCartella.avvia_lampeggio()`

```python
_N_TICK_LAMPEGGIO: int = 7  # 7 tick × 300ms ≈ 2.1 secondi totali

def avvia_lampeggio(self, numero: int) -> None:
    """Avvia l'animazione lampeggio sulla cella del numero indicato.

    Se un lampeggio precedente è attivo, lo ferma e stabilizza la cella
    precedente prima di avviarne uno nuovo.
    Il numero deve essere presente in _mappa_celle_numero (cioè nella
    cartella correntemente visualizzata).
    """
    if numero not in self._mappa_celle_numero:
        return

    # Ferma eventuale lampeggio precedente (cella diversa)
    if self._timer_lampeggio is not None:
        self._timer_lampeggio.Stop()
        self._timer_lampeggio = None
    if self._numero_lampeggio is not None:
        cella_prec = self._mappa_celle_numero.get(self._numero_lampeggio)
        if cella_prec is not None:
            cella_prec.SetBackgroundColour(wx.Colour(COLORE_CELLA_ESTRATTA_NON_SEGNATA))
            cella_prec.Refresh()

    self._numero_lampeggio = numero
    self._lampeggio_attivo = True
    self._tick_lampeggio = 0
    self._timer_lampeggio = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self._on_tick_lampeggio, self._timer_lampeggio)
    self._timer_lampeggio.Start(300)
```

### Nuovo handler `PannelloCartella._on_tick_lampeggio()`

```python
def _on_tick_lampeggio(self, event: wx.TimerEvent) -> None:
    """Tick del timer lampeggio: alterna i colori per N cicli, poi stabilizza."""
    if not self._lampeggio_attivo or self._numero_lampeggio is None:
        return
    cella = self._mappa_celle_numero.get(self._numero_lampeggio)
    if cella is None:
        self.ferma_lampeggio()
        return

    self._tick_lampeggio += 1

    if self._tick_lampeggio >= _N_TICK_LAMPEGGIO:
        # Fine ciclo: stabilizza sul colore fisso e ferma il timer
        self.ferma_lampeggio()
        cella.SetBackgroundColour(wx.Colour(COLORE_CELLA_ESTRATTA_NON_SEGNATA))
        cella.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
        cella.Refresh()
        return

    # Toggle colore al ritmo del tick
    if self._tick_lampeggio % 2 == 1:
        cella.SetBackgroundColour(wx.Colour(COLORE_CELLA_EVIDENZIATA))
    else:
        cella.SetBackgroundColour(wx.Colour(COLORE_CELLA_ESTRATTA_NON_SEGNATA))
    cella.Refresh()
```

### Nuovo metodo pubblico `PannelloCartella.ferma_lampeggio()`

```python
def ferma_lampeggio(self) -> None:
    """Ferma il timer lampeggio e azzera lo stato. Non ripristina il colore della cella."""
    if self._timer_lampeggio is not None:
        self._timer_lampeggio.Stop()
        self._timer_lampeggio = None
    self._lampeggio_attivo = False
```

### Binding EVT_CLOSE in FinestraGioco

In `FinestraGioco._bind_finestra()`, aggiungere dopo `self.Bind(wx.EVT_CHAR_HOOK, ...)`:

```python
self.Bind(wx.EVT_CLOSE, self._on_close)
```

### Nuovo metodo `FinestraGioco._on_close()`

```python
def _on_close(self, event: wx.CloseEvent) -> None:
    """Ferma il timer lampeggio prima della distruzione della finestra."""
    if hasattr(self, "_pannello_cartella"):
        pannello = self._pannello_cartella
        if hasattr(pannello, "ferma_lampeggio"):
            pannello.ferma_lampeggio()
    event.Skip()  # Necessario per procedere con la distruzione standard della finestra
```

### Modifica a `FinestraGioco._aggiorna_griglie_visive()`

Prima della chiamata a `self._pannello_cartella.aggiorna(...)`, aggiungere:

```python
if hasattr(self._pannello_cartella, "ferma_lampeggio"):
    self._pannello_cartella.ferma_lampeggio()
```

Questo garantisce che un lampeggio attivo non sopravviva a un repaint completo della
cartella (es. fine partita, navigazione tra cartelle).

### Nuovo metodo `WxRenderer._wx_avvia_lampeggio()`

In `renderer_wx.py`, nella sezione layer `_wx_*` (dopo `_wx_aggiorna_tabellone`):

```python
def _wx_avvia_lampeggio(self, numero: int) -> None:
    """Avvia l'animazione lampeggio sulla cella del numero estratto (se presente nella cartella)."""
    if self._finestra is None:
        return
    if not hasattr(self._finestra, "_pannello_cartella"):
        return
    pannello = self._finestra._pannello_cartella
    if hasattr(pannello, "avvia_lampeggio"):
        pannello.avvia_lampeggio(numero)
```

### Modifica a `WxRenderer.annuncia_numero_estratto()`

Aggiungere dopo `self._wx_aggiorna_output(testo)` e **prima** di
`self._ao2_vocalizza(testo)`:

```python
self._wx_avvia_lampeggio(numero)
```

Questo rispetta la regola invariante del progetto: testo → widget visivo → voce.
Il lampeggio è un aggiornamento visivo puro e deve precedere la vocalizzazione.

---

## Sezione A — Header Bar

### Obiettivo

Una striscia orizzontale fissa in cima alla finestra che mostra in tempo reale:
"Turno: N" — "Estratto: N" (colore accent) — "Premi: elenco".
Puramente visiva, nessun focus tastiera.

### Costanti da aggiungere in tema.py

Aggiungere nella sezione `# COLORI — Accenti`:

```python
COLORE_HEADER_ACCENT = "#FFB300"  # Numero estratto nell'header (alias semantico di COLORE_ACCENT_DORATO)
```

### Import aggiuntivi in finestra_gioco.py

```python
COLORE_HEADER_BG, FONT_HEADER_PT, ALTEZZA_HEADER, COLORE_HEADER_ACCENT,
```

### Nuova classe `HeaderBar(wx.Panel)` in finestra_gioco.py

Posizionare dopo `class PannelloGriglia` e prima di `class FinestraGioco`.

```python
class HeaderBar(wx.Panel):
    """
    Striscia informativa orizzontale fissa in cima alla FinestraGioco.

    Mostra: turno corrente, ultimo numero estratto (con colore accent), premi assegnati.
    Puramente visiva: non focalizzabile, nessun binding tastiera.
    """

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, style=wx.NO_BORDER)
        self.SetWindowStyleFlag(self.GetWindowStyleFlag() & ~wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(wx.Colour(COLORE_HEADER_BG))
        self.SetMinSize((-1, ALTEZZA_HEADER))
        self._build_ui()

    def _build_ui(self) -> None:
        font_normale = wx.Font(
            FONT_HEADER_PT, wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._lbl_turno = wx.StaticText(self, label="Turno: —")
        self._lbl_turno.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        self._lbl_turno.SetFont(font_normale)
        sizer.Add(self._lbl_turno, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        sizer.Add(10, 0)  # spacer

        self._lbl_estratto = wx.StaticText(self, label="Estratto: —")
        self._lbl_estratto.SetForegroundColour(wx.Colour(COLORE_HEADER_ACCENT))
        self._lbl_estratto.SetFont(font_normale)
        sizer.Add(self._lbl_estratto, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        sizer.Add(10, 0)  # spacer

        self._lbl_premi = wx.StaticText(self, label="Premi: —")
        self._lbl_premi.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        self._lbl_premi.SetFont(font_normale)
        sizer.Add(self._lbl_premi, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        self.SetSizer(sizer)

    def aggiorna(
        self,
        turno: Optional[int] = None,
        ultimo_numero: Optional[int] = None,
        premi_lista: Optional[list] = None,
    ) -> None:
        """Aggiorna le tre etichette dell'header.

        I parametri None significano "non aggiornare quel campo".
        """
        if turno is not None:
            self._lbl_turno.SetLabel(f"Turno: {turno}")
        if ultimo_numero is not None:
            self._lbl_estratto.SetLabel(f"Estratto: {ultimo_numero}")
        if premi_lista is not None:
            if premi_lista:
                testo_premi = "Premi: " + ", ".join(premi_lista)
            else:
                testo_premi = "Premi: —"
            self._lbl_premi.SetLabel(testo_premi)
        self.Layout()
```

### Posizionamento in `FinestraGioco._build_ui()`

Aggiungere come **prima** operazione nel metodo, dopo `self._panel = wx.Panel(self)`:

```python
self._header_bar = HeaderBar(panel)
sizer.Add(self._header_bar, 0, wx.EXPAND, 0)
```

Il pannello successivo (`_btn_principale`) si posiziona subito sotto l'header.

### Nuovo metodo `WxRenderer._wx_aggiorna_header()`

In `renderer_wx.py`, nella sezione layer `_wx_*`:

```python
def _wx_aggiorna_header(
    self,
    turno: Optional[int] = None,
    ultimo_numero: Optional[int] = None,
    premi_lista: Optional[list] = None,
) -> None:
    """Aggiorna la HeaderBar della finestra di gioco (se disponibile)."""
    if self._finestra is None:
        return
    if not hasattr(self._finestra, "_header_bar"):
        return
    self._finestra._header_bar.aggiorna(turno, ultimo_numero, premi_lista)
```

### Modifica a `WxRenderer.annuncia_numero_estratto()`

Aggiungere prima di `self._ao2_vocalizza(testo)`:

```python
self._wx_aggiorna_header(turno=numero_turno, ultimo_numero=numero)
```

Rispetta la regola: testo (`_wx_aggiorna_output`) → widget visivo (header) → voce (`_ao2_vocalizza`).

### Modifica a `WxRenderer.annuncia_premi_turno()`

⚠️ La chiamata va inserita **dopo** `self._wx_aggiorna_output(testo)` e
**prima** di `self._ao2_vocalizza(testo)`, in tutti i rami del metodo
(sia il ramo con premi, sia il ramo senza premi). Stessa regola di A6.

Aggiungere prima di `self._ao2_vocalizza(testo)` (in entrambi i rami premi/nessun_premio):

```python
if premi:
    nomi_premi = [f"{p.get('premio', '?')} — {p.get('giocatore', '?')}" for p in premi]
else:
    nomi_premi = []
self._wx_aggiorna_header(premi_lista=nomi_premi)
```

### Nota sull'ordine nella struttura `aggiorna()`

Il metodo `HeaderBar.aggiorna()` accetta parametri `Optional[...]` per permettere
aggiornamenti parziali: `annuncia_numero_estratto` aggiorna turno + numero,
`annuncia_premi_turno` aggiorna solo i premi. In questo modo l'header non azzera
il numero estratto quando vengono annunciati i premi.

---

## Dipendenze tra sezioni

```
tema.py (B1, A1) ──────────────────────────────────────────────────┐
                                                                    ▼
finestra_gioco.py imports (B2, D1, C0, A3) → aggiorna_stato_pulsante() (B3, B4, B5)
                                          → _build_ui() log (D2, D3)
                                          → PannelloCartella (C1, C2, C3, C4, C5)
                                          → _aggiorna_griglie_visive() (C6a)
                                          → _bind_finestra() + _on_close() (C6)
                                          → HeaderBar class (A2)
                                          → _build_ui() header (A4)
renderer_wx.py (C7, C8, A5, A6, A7) ──────────────────────────────┘
```

Nessuna dipendenza circolare. L'ordine B → D → C → A rispetta il grafo.
