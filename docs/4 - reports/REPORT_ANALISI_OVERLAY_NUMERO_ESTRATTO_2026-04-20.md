# REPORT — Analisi per Overlay Visivo Numero Estratto

**Data:** 2026-04-20
**Feature richiesta:** Elemento visivo temporaneo (≈10 s) che mostra il numero estratto
in grande, visibile ai giocatori vedenti senza screen reader. Non deve alterare
le funzionalità già implementate per NVDA.

---

## 1. Stato attuale — come viene comunicato il numero estratto

### 1.1 Flusso di estrazione (entry point)

Il punto di origine è `FinestraGioco._on_pulsante_principale()` (linea ~961
in `bingo_game/ui/finestra_gioco.py`). Quando la fase è `"attesa_estrazione"`:

```
FinestraGioco._on_pulsante_principale()
  └─► ComandiSistema.esegui_fase_estrazione(partita) → risultato_est
  └─► self._renderer.annuncia_numero_estratto(numero, turno)
  └─► self._aggiorna_griglie_visive()
  └─► self._avvia_timer_azione(durata_finestra_ms)
  └─► self._pianifica_risposta_bot()
```

Esiste un secondo punto di chiamata a `annuncia_numero_estratto` (linea ~1457),
usato nel loop automatico.

### 1.2 Flusso nel renderer

`WxRenderer.annuncia_numero_estratto()` (riga 195, `renderer_wx.py`) esegue in ordine:

1. Costruisce `testo = "Turno N. Numero estratto: X."`
2. `_wx_aggiorna_output(testo)` → aggiorna il pannello griglia (widget di testo leggibile da NVDA)
3. `_wx_avvia_lampeggio(numero)` → avvia il lampeggio sulla cella corrispondente nella cartella
4. `_wx_aggiorna_header(turno=..., ultimo_numero=...)` → aggiorna la `HeaderBar` in cima alla finestra
5. `_ao2_vocalizza(testo)` → passa il testo al `Vocalizzatore` (screen reader)

### 1.3 HeaderBar attuale

La classe `HeaderBar` (riga ~558, `finestra_gioco.py`) è una striscia orizzontale fissa
in cima alla `FinestraGioco`. Mostra tre campi in una riga:

- `Turno: N` — testo chiaro (`COLORE_TESTO_CHIARO = "#ECEFF1"`)
- `Estratto: X` — testo accent (`COLORE_HEADER_ACCENT = "#FFB300"`, giallo-ambra)
- `Premi: ...` — testo chiaro

`FONT_HEADER_PT = 12` (12 punti). Sfondo `COLORE_HEADER_BG = "#2C3E50"` (blu-ardesia).
Altezza fissa `ALTEZZA_HEADER = 36 px`. **Non focalizzabile, nessun binding tastiera.**

### 1.4 Meccanismo lampeggio cartella

`PannelloCartella.avvia_lampeggio(numero)` usa un `wx.Timer` con tick da 300 ms
per un totale di `_N_TICK_LAMPEGGIO = 7` cicli (≈ 2,1 s). Colori alternati:
`COLORE_CELLA_EVIDENZIATA` e `COLORE_CELLA_ESTRATTA_NON_SEGNATA`.

---

## 2. Analisi del problema

La `HeaderBar` usa font 12 pt e altezza 36 px. Per utenti vedenti che non usano NVDA,
il numero estratto non risalta a colpo d'occhio: si confonde con le altre informazioni
nella stessa barra. Nelle sale bingo fisiche, il numero viene mostrato su un monitor
dedicato in formato grande per alcuni secondi.

**Vincoli:**
- La `HeaderBar` deve rimanere invariata (richiesta esplicita).
- La nuova funzionalità è **solo visiva**: non deve produrre annunci NVDA aggiuntivi.
- Non deve spostare il focus della tastiera.
- Deve scomparire automaticamente dopo ≈ 10 secondi.

---

## 3. Opzioni di implementazione

### Opzione A — Mini-frame non modale `STAY_ON_TOP` (RACCOMANDATA)

Un `wx.Frame` separato, senza bordi, senza barra del titolo, senza voce nel
taskbar, posizionato sopra la `FinestraGioco` (es. in basso a destra o al centro).

```
style = wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR | wx.BORDER_NONE | wx.FRAME_TOOL_WINDOW
```

**Ciclo di vita:**
- Istanziato una volta in `FinestraGioco.__init__()` ma tenuto nascosto (`Hide()`).
- Al momento dell'estrazione, viene popolato con il numero, posizionato e mostrato con `Show()`.
- Un `wx.Timer` ONE_SHOT da 10 000 ms lo nasconde di nuovo (`Hide()`).
- La finestra non riceve mai il focus (`SetFocus()` non viene mai chiamato su di essa).

**Vantaggi:**
- NVDA/JAWS non leggono un `wx.Frame` che non riceve il focus e non ha `SetName()` utile.
- Posizionabile liberamente sullo schermo, indipendentemente dal layout dei sizer.
- Compatibile con Windows 10/11: `STAY_ON_TOP` funziona correttamente.
- Nessuna modifica al layout interno di `FinestraGioco` (nessun sizer da ricalcolare).

**Svantaggi:**
- Due oggetti `wx.Frame` attivi contemporaneamente. Gestione ciclo di vita da curare.
- Al `Close()` di `FinestraGioco`, il mini-frame deve essere distrutto esplicitamente.

### Opzione B — Pannello sovrapposto inside la FinestraGioco

Un `wx.Panel` posizionato con `SetPosition()` assoluto sopra gli altri widget.

**Problemi:**
- wxPython usa sizer per il layout; il posizionamento assoluto si sovrascrive
  al prossimo `Layout()` o ridimensionamento.
- Richiede una finestra senza sizer per quella regione, o un `wx.lib.floatcanvas`.
- Complessità notevolmente superiore rispetto a Opzione A.
- **Non raccomandata.**

### Opzione C — Finestra figlia `wx.PopupWindow`

`wx.PopupWindow` è progettata esattamente per popup visivi senza focus.

```python
overlay = wx.PopupWindow(parent=finestra_gioco)
```

**Vantaggi:**
- By design non riceve il focus (semantica popup).
- Distrutta automaticamente quando il parent viene chiuso.
- Nessun rischio di essere letta da NVDA.

**Svantaggi:**
- Su Windows, `wx.PopupWindow` non supporta `STAY_ON_TOP` in modo affidabile
  nelle versioni più vecchie di wxPython. Da verificare con la versione in uso.
- Meno usata e documentata del semplice `wx.Frame`.

---

## 4. Soluzione raccomandata — dettaglio tecnico

### 4.1 Nuovo file: `bingo_game/ui/overlay_numero.py`

Classe `OverlayNumeroEstratto(wx.Frame)`:

```python
class OverlayNumeroEstratto(wx.Frame):
    """
    Finestra overlay non modale che mostra il numero estratto per N secondi.

    - Nessun focus: non interferisce mai con la navigazione tastiera.
    - Nessun annuncio NVDA: non ha SetName() utile, non riceve SetFocus().
    - Scomparsa automatica: wx.Timer ONE_SHOT da durata_ms.
    - Ciclo di vita: istanziata una volta, mostrata/nascosta a ogni estrazione.
    """
```

**Layout interno:**
- `wx.Panel` anomino (no `SetName`)
- `wx.StaticText` con:
  - Font: `FONT_OVERLAY_PT = 72` (nuova costante in `tema.py`)
  - Colore testo: `COLORE_HEADER_ACCENT = "#FFB300"` (giallo bingo)
  - Sfondo: `COLORE_HEADER_BG = "#2C3E50"` (blu-ardesia, coerente con HeaderBar)
- Etichetta secondaria opzionale: font 18 pt, testo "Numero estratto" (senza `SetName`)

**Posizionamento:**
- Centrato nella `FinestraGioco` al momento di `mostra_numero()`.
- Oppure angolo in basso a destra (preferito per non coprire il tabellone centrale).
- Dimensione fissa: es. 240 × 160 px (nuova costante `DIMENSIONE_OVERLAY`).

**Timer:**
- Un singolo `wx.Timer` ONE_SHOT riusato a ogni chiamata.
- Alla scadenza: `self.Hide()`.
- Se `mostra_numero()` viene chiamato mentre l'overlay è già visibile
  (estrazione rapida), il timer viene resettato.

### 4.2 Modifiche a `bingo_game/ui/finestra_gioco.py`

Nel metodo `__init__()`:

```python
from bingo_game.ui.overlay_numero import OverlayNumeroEstratto
self._overlay_numero = OverlayNumeroEstratto(parent=self)
```

Aggiunto metodo pubblico per il renderer:

```python
def mostra_overlay_numero(self, numero: int) -> None:
    """Mostra l'overlay visivo del numero estratto (solo per vedenti, non-NVDA)."""
    self._overlay_numero.mostra_numero(numero)
```

Nel metodo `_on_close()`: aggiungere `self._overlay_numero.Destroy()`.

### 4.3 Modifiche a `bingo_game/ui/renderers/renderer_wx.py`

Aggiunto metodo privato `_wx_mostra_overlay_numero()`:

```python
def _wx_mostra_overlay_numero(self, numero: int) -> None:
    """Mostra l'overlay visivo del numero estratto (solo se disponibile)."""
    if self._finestra is None:
        return
    if hasattr(self._finestra, "mostra_overlay_numero"):
        self._finestra.mostra_overlay_numero(numero)
```

Modifica a `annuncia_numero_estratto()` — aggiunta di una sola riga, DOPO
le chiamate esistenti e PRIMA di `_ao2_vocalizza`:

```python
def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
    testo = f"Turno {numero_turno}. Numero estratto: {numero}."
    self._wx_aggiorna_output(testo)
    self._wx_avvia_lampeggio(numero)
    self._wx_aggiorna_header(turno=numero_turno, ultimo_numero=numero)
    self._wx_mostra_overlay_numero(numero)   # ← NUOVA RIGA
    self._ao2_vocalizza(testo)               # NVDA: invariato
```

### 4.4 Modifiche a `bingo_game/ui/tema.py`

Nuove costanti (sezione FONT e sezione DIMENSIONI):

```python
FONT_OVERLAY_PT = 72          # Dimensione font numero nell'overlay estratto
FONT_OVERLAY_LABEL_PT = 16    # Dimensione etichetta secondaria overlay

DIMENSIONE_OVERLAY = (260, 180)  # Larghezza × Altezza dell'overlay in pixel
```

---

## 5. Garanzie di non-regressione per NVDA

| Proprietà | Comportamento atteso |
|---|---|
| Focus tastiera | L'overlay non riceve mai `SetFocus()`. Tab e frecce ignorano il frame. |
| Annunci NVDA | Nessun `SetName()`, nessun `wx.accessible`, nessun `SetAccessible()` sull'overlay. |
| `_ao2_vocalizza(testo)` | Invariato: chiamato con lo stesso testo, nello stesso momento. |
| `HeaderBar` | Invariata: `_wx_aggiorna_header()` chiamata prima dell'overlay, nessun conflitto. |
| Lampeggio cartella | Invariato: `_wx_avvia_lampeggio()` è indipendente dall'overlay. |
| Layout FinestraGioco | Invariato: l'overlay è un frame separato, non inserito in nessun sizer. |
| Alt+Tab Windows | `FRAME_NO_TASKBAR` impedisce la comparsa nell'Alt+Tab switcher. |
| Chiusura finestra | `_on_close()` distrugge esplicitamente l'overlay prima di procedere. |

---

## 6. File coinvolti — riepilogo

| File | Modifica |
|---|---|
| `bingo_game/ui/overlay_numero.py` | **NUOVO** — classe `OverlayNumeroEstratto` |
| `bingo_game/ui/tema.py` | Aggiunte 3 costanti (`FONT_OVERLAY_PT`, `FONT_OVERLAY_LABEL_PT`, `DIMENSIONE_OVERLAY`) |
| `bingo_game/ui/finestra_gioco.py` | Istanziazione overlay in `__init__`, metodo `mostra_overlay_numero()`, `_on_close()` |
| `bingo_game/ui/renderers/renderer_wx.py` | Metodo `_wx_mostra_overlay_numero()`, una riga in `annuncia_numero_estratto()` |
| `docs/API.md` | Aggiunta firma pubblica `mostra_overlay_numero()` |
| `CHANGELOG.md` | Voce `Added` |

---

## 7. Rischi residui e punti da verificare

1. **`wx.PopupWindow` vs `wx.Frame`**: se `wx.PopupWindow` si comporta bene con
   la versione di wxPython installata (`requirements.txt`), potrebbe essere preferito
   a `wx.Frame` per la semantica più esplicita di "popup non focalizzabile".
   Da testare empiricamente prima dell'implementazione.

2. **Posizionamento relativo**: su schermi multi-monitor o con DPI elevato, il
   calcolo della posizione dell'overlay rispetto alla `FinestraGioco` richiede
   `GetScreenPosition()` + offset, non `GetPosition()`.

3. **Ridimensionamento finestra**: se l'utente ridimensiona la `FinestraGioco`
   mentre l'overlay è visibile, la posizione non si aggiorna automaticamente.
   Mitigazione: bind a `EVT_MOVE` e `EVT_SIZE` della `FinestraGioco` per
   riposizionare l'overlay se visibile.

4. **Animazione fade**: opzionale. Può essere implementata come fase 2, usando
   `wx.CallLater` in cascata per ridurre l'alpha progressivamente (`SetTransparent()`).
   Non prevista nella fase 1.

---

## 8. Conclusione e prossimi passi

L'implementazione è fattibile con modifiche chirurgiche e ben localizzate.
Il flusso NVDA non viene toccato in nessun punto: `_ao2_vocalizza(testo)` rimane
l'ultima istruzione in `annuncia_numero_estratto()`, il testo vocalizzato è identico.

**Prossimi passi suggeriti:**

1. Agent-Design crea `DESIGN_OVERLAY_NUMERO_ESTRATTO.md` con la decisione
   su `wx.Frame` vs `wx.PopupWindow` (test empirico).
2. Agent-Plan crea `PLAN_OVERLAY_NUMERO_ESTRATTO.md` con i commit atomici.
3. Agent-Code implementa i 4 file elencati nella sezione 6.
4. Agent-Validate esegue la checklist accessibilità NVDA e i test di regressione.
