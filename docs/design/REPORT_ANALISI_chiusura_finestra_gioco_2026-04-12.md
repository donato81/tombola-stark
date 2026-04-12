# REPORT ANALISI — Chiusura visiva FinestraGioco
**Data:** 2026-04-12
**Autore:** Agent-Analyze (via Agent-Orchestrator)
**Scope:** Quattro elementi grafici mancanti in `FinestraGioco` (A, B, C, D)
**Stato:** REVIEWED

---

## Premessa metodologica

Questa analisi è basata sulla lettura diretta di:

- `bingo_game/ui/finestra_gioco.py` (intero file, ~1160 righe)
- `bingo_game/ui/tema.py` (intero file, ~115 righe)
- `bingo_game/ui/renderers/renderer_wx.py` (metodi pubblici + layer `_wx_*`)

La regola interna invariante del progetto — **testo → widget visivo → voce** — è rispettata
da tutti e quattro gli elementi: nessuno produce voce né testo accessibile.

---

## Elemento A — Header Bar

### Dove si interviene

| File | Metodo / Sezione | Riga appross. | Tipo modifica |
|------|-----------------|---------------|---------------|
| `finestra_gioco.py` | Nuova classe `HeaderBar(wx.Panel)` | Dopo `PannelloGriglia` (~335) | Aggiunta classe |
| `finestra_gioco.py` | `FinestraGioco._build_ui()` | Prima riga del sizer (~386) | Inserimento widget |
| `renderer_wx.py` | `annuncia_numero_estratto()` | ~157 | Aggiunta chiamata |
| `renderer_wx.py` | `annuncia_premi_turno()` | ~172 | Aggiunta chiamata |
| `renderer_wx.py` | Nuovo metodo `_wx_aggiorna_header()` | ~765 (dopo `_wx_aggiorna_tabellone`) | Aggiunta metodo |

### Dipendenze tema.py

**Già presenti (nessuna aggiunta obbligatoria):**

| Costante | Valore | Uso |
|----------|--------|-----|
| `COLORE_HEADER_BG` | `#2C3E50` | Sfondo del pannello |
| `COLORE_TESTO_CHIARO` | `#ECEFF1` | Testo etichette |
| `FONT_HEADER_PT` | `12` | Dimensione font |
| `ALTEZZA_HEADER` | `36` | Altezza minima pannello |
| `COLORE_ACCENT_DORATO` | `#FFB300` | Colore del numero estratto |

**Da aggiungere (1 costante semantica):**

| Costante | Valore | Motivazione |
|----------|--------|-------------|
| `COLORE_HEADER_ACCENT` | `"#FFB300"` | Alias semantico per il numero estratto nell'header; evita dipendere dal nome `COLORE_ACCENT_DORATO` che ha semantiche più generali |

### Rischio NVDA

**Rischio: Nullo.**

- `HeaderBar` usa esclusivamente `wx.StaticText`, che non riceve focus di default.
- Il pannello avrà `TAB_TRAVERSAL` rimosso esplicitamente (stessa tecnica di `PannelloTabellone`
  e `PannelloCartella`, già presenti).
- NVDA non vocalizza elementi privi di focus né intercetta `SetLabel()` su StaticText se
  non sono widget interattivi. Il pannello non ha ARIA-equivalent in wxPython.
- Nessun evento di accessibilità viene emesso dal pannello.

### Rischio focus

**Rischio: Nullo.**

- `wx.StaticText` non può ricevere il focus del keyboard input.
- La rimozione di `wx.TAB_TRAVERSAL` tramite
  `self.SetWindowStyleFlag(self.GetWindowStyleFlag() & ~wx.TAB_TRAVERSAL)`
  esclude il pannello dal ciclo Tab in modo identico ai pannelli già esistenti.
- Il sizer principale di `_build_ui()` riceve il pannello come elemento `flag=wx.EXPAND`
  senza `wx.WANTS_CHARS` né `wx.TAB_TRAVERSAL`.

### Rischio alto contrasto (Windows)

Su temi ad alto contrasto (Modalità Contrasto elevato di Windows), `SetBackgroundColour()`
su un `wx.Panel` può essere ignorato dal sistema operativo o ridipinto dal tema.

**Rilevamento:** al momento dell'aggiornamento, confrontare il colore effettivo con quello
atteso tramite `wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)`. Se differisce
marcatamente da `#F0F0F0` (grigio sistema standard), il tema personalizzato è soppresso.
In quel caso l'header degrada silenziosamente a testo su sfondo di sistema, senza errori.

### Complessità stimata

**Media.** Motivazione:

- Richiede la creazione di una nuova classe (`HeaderBar`) con `_build_ui()` dedicato.
- Richiede due punti di aggiornamento nel renderer (`annuncia_numero_estratto`,
  `annuncia_premi_turno`) e un nuovo metodo `_wx_aggiorna_header()`.
- Il posizionamento nel sizer va testato visivamente per verificare che l'altezza fissa
  `ALTEZZA_HEADER = 36` non comprima gli altri widget a risoluzioni ridotte.

---

## Elemento B — Colori semantici sui pulsanti azione

### Dove si interviene

| File | Metodo | Riga appross. | Tipo modifica |
|------|--------|---------------|---------------|
| `tema.py` | — (nuove costanti) | Fine sezione pulsanti (~53) | Aggiunta costanti |
| `finestra_gioco.py` | Import da `tema` | ~52–68 | Aggiornamento import |
| `finestra_gioco.py` | `aggiorna_stato_pulsante()` (pubblico) | ~875–945 | Aggiunta `SetBackgroundColour` + `SetForegroundColour` |

### Dipendenze tema.py

**Già presenti — riutilizzabili direttamente:**

| Costante | Valore | Stato pulsante |
|----------|--------|----------------|
| `COLORE_VERDE_SCURO` | `#2E7D32` | "Inizia partita" |
| `COLORE_ACCENT_BLU` | `#1565C0` | "Passa turno" |
| `COLORE_ACCENT_ARANCIONE` | `#E65100` | "Ho finito — avvia verifica" |
| `COLORE_BTN_GRIGIO` | `#757575` | "Pausa in corso…" (disabilitato) |
| `COLORE_BTN_PAUSA` | `#424242` | "Metti in pausa" |
| `COLORE_VERDE_RIPRENDI` | `#388E3C` | "Riprendi" |
| `COLORE_BTN_DISABILITATO` | `#BDBDBD` | "Gioco in pausa" (fase in_pausa) |
| `COLORE_TESTO_CHIARO` | `#ECEFF1` | Testo bianco su tutti i pulsanti colorati |

**Da aggiungere (4 alias semantici):**

| Costante | Valore | Alias di |
|----------|--------|----------|
| `COLORE_BTN_INIZIA` | `#2E7D32` | `COLORE_VERDE_SCURO` |
| `COLORE_BTN_PASSA_TURNO` | `#1565C0` | `COLORE_ACCENT_BLU` |
| `COLORE_BTN_HO_FINITO` | `#E65100` | `COLORE_ACCENT_ARANCIONE` |
| `COLORE_BTN_RIPRENDI` | `#388E3C` | `COLORE_VERDE_RIPRENDI` |

Gli alias sono giustificati dalla semantica: il codice di `aggiorna_stato_pulsante()` deve
referenziare costanti con nomi di dominio UI coerenti, non colori generici.

### Rischio NVDA

**Rischio: Nullo.**

`SetBackgroundColour()` e `SetForegroundColour()` su `wx.Button` sono puramente visivi.
Non producono eventi accessibilità wx (`wx.AccessibleEvent`), non modificano il testo
vocalizzato da NVDA (che legge `GetLabel()`), non alterano la struttura dell'albero AT.

### Rischio focus

**Rischio: Nullo.**

- I binding `EVT_BUTTON` non cambiano.
- L'ordine Tab non cambia (nessun `MoveAfterInTabOrder` coinvolto).
- `Enable()` / `Disable()` già presenti — i colori vengono aggiunti negli stessi rami.

### Rischio alto contrasto (Windows)

Su alto contrasto, `SetBackgroundColour()` su `wx.Button` viene ignorato dalla maggior parte
delle implementazioni native. Il pulsante usa i colori di sistema. **Impatto:** nessuna degradazione
funzionale; l'etichetta rimane leggibile con i colori di alto contrasto del sistema.

**Rilevamento:** `wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).GetAsString()` restituisce
il colore di sistema corrente; se distante da `#F0F0F0`, l'applicazione è in alto contrasto.

### Complessità stimata

**Bassa.** Ogni ramo if/elif di `aggiorna_stato_pulsante()` riceve 2 chiamate aggiuntive
(`SetBackgroundColour`, `SetForegroundColour`). Nessuna logica condizionale nuova.

---

## Elemento C — Animazione lampeggio post-estrazione

### Dove si interviene

| File | Metodo / Sezione | Riga appross. | Tipo modifica |
|------|-----------------|---------------|---------------|
| `finestra_gioco.py` | `PannelloCartella.__init__()` | ~143 | Aggiunta attributi |
| `finestra_gioco.py` | `PannelloCartella.aggiorna()` | ~186–207 | Costruzione `_mappa_celle_numero` |
| `finestra_gioco.py` | `PannelloCartella` (nuovi metodi) | ~210 | `avvia_lampeggio()`, `_on_tick_lampeggio()`, `ferma_lampeggio()` |
| `finestra_gioco.py` | `FinestraGioco._bind_finestra()` | ~508 | Binding `wx.EVT_CLOSE` |
| `finestra_gioco.py` | `FinestraGioco` (nuovo metodo) | ~512 | `_on_close()` |
| `renderer_wx.py` | `annuncia_numero_estratto()` | ~157 | Aggiunta chiamata `_wx_avvia_lampeggio()` |
| `renderer_wx.py` | Nuovo metodo `_wx_avvia_lampeggio()` | ~770 | Aggiunta metodo |

### Problema strutturale: mappatura numero→cella

`PannelloCartella._celle` è strutturato come `list[list[wx.StaticText]]` (3×9),
senza reverse mapping numero→cella. Per poter trovare la cella associata a un numero
estratto in O(1), è necessario costruire al termine di ogni `aggiorna()` un dizionario:

```python
self._mappa_celle_numero: dict[int, wx.StaticText] = {
    int(griglia[row][col]): self._celle[row][col]
    for row in range(3)
    for col in range(9)
    if isinstance(griglia[row][col], int)
}
```

La griglia viene passata come `tuple` a `aggiorna()`; la mappatura va ricostruita
a ogni chiamata perché la cartella visualizzata può cambiare (navigazione tra cartelle).

### Dipendenze tema.py

**Già presenti (nessuna aggiunta necessaria):**

| Costante | Valore | Uso |
|----------|--------|-----|
| `COLORE_CELLA_EVIDENZIATA` | `#FFF176` | Colore di lampeggio (tick dispari) |
| `COLORE_CELLA_ESTRATTA_NON_SEGNATA` | `#FFF9C4` | Colore fisso post-lampeggio |
| `COLORE_TESTO_SCURO` | `#212121` | Testo sulla cella durante e dopo il lampeggio |

### Rischio NVDA

**Rischio: Nullo.**

- Il `wx.Timer` alterna esclusivamente `SetBackgroundColour()` su `wx.StaticText`.
- `wx.StaticText` non genera eventi accessibilità quando cambia colore.
- Il timer non sposta mai il focus; NVDA non intercetta variazioni di colore su `StaticText`.
- Nessuna chiamata ad `_ao2_vocalizza()` nel percorso del lampeggio.

### Rischio focus

**Rischio: Nullo.**

- `PannelloCartella` ha `TAB_TRAVERSAL` rimosso e non è focalizzabile.
- Le celle `wx.StaticText` non ricevono input da tastiera.
- Il binding `wx.EVT_TIMER` viene agganciato al `PannelloCartella` (non al frame), quindi
  non collide con `_timer_azione` e `_timer_pausa` di `FinestraGioco` (anch'essi agganciati
  al frame tramite `self.Bind(wx.EVT_TIMER, ..., self._timer_azione)`).

### Gestione bordi critici

**Caso 1 — Lampeggio già attivo quando arriva un nuovo numero:**
`avvia_lampeggio()` chiama sempre `ferma_lampeggio()` come prima operazione, poi ripristina
il colore fisso sulla cella precedente prima di avviare il nuovo ciclo.

**Caso 2 — Chiusura finestra durante lampeggio:**
`FinestraGioco._bind_finestra()` aggiunge `Bind(wx.EVT_CLOSE, self._on_close)`.
`_on_close()` chiama `self._pannello_cartella.ferma_lampeggio()` prima di `event.Skip()`.

**Caso 3 — Fine partita durante lampeggio:**
`_esegui_verifica_premi()` chiama `_aggiorna_griglie_visive()` alla fine del turno.
Poiché `_aggiorna_griglie_visive()` chiama `PannelloCartella.aggiorna()`, che ridipinge
tutte le celle, il colore del lampeggio viene sovrascritto. Per evitare stati incoerenti
(timer ancora attivo ma cella già ridipinta), `_aggiorna_griglie_visive()` deve chiamare
`self._pannello_cartella.ferma_lampeggio()` prima di `aggiorna()`.

### Rischio alto contrasto (Windows)

Stessa situazione dell'Elemento A: su alto contrasto `SetBackgroundColour()` su `StaticText`
può essere ignorato. Il lampeggio non è visibile, ma l'accessibilità non decade (il lampeggio
è puramente estetico).

### Complessità stimata

**Media.** Motivazione:

- Introduce concorrenza leggera (timer secondario separato da quelli della finestra).
- Richiede gestione esplicita del ciclo di vita (start, stop, reset, close).
- La costruzione della `_mappa_celle_numero` va mantenuta sincronizzata con `aggiorna()`.
- Tre punti di integrazione distinti (PannelloCartella, FinestraGioco, renderer).

---

## Elemento D — Stile visivo del log annunci

### Dove si interviene

| File | Metodo | Riga appross. | Tipo modifica |
|------|--------|---------------|---------------|
| `finestra_gioco.py` | Import da `tema` | ~52–68 | Aggiungere 5 costanti mancanti |
| `finestra_gioco.py` | `FinestraGioco._build_ui()` | ~487 (StaticText) + ~492 (`_log_ctrl`) | Cambio label + 3 chiamate stile |

### Dipendenze tema.py

**Già presenti — nessuna aggiunta necessaria:**

| Costante | Valore | Uso |
|----------|--------|-----|
| `COLORE_LOG_BG` | `#263238` | Sfondo `_log_ctrl` |
| `COLORE_TESTO_MUTED` | `#B0BEC5` | Testo `_log_ctrl` |
| `FONT_LOG_PT` | `10` | Dimensione font monospace |
| `FONT_LOG_FAMIGLIA` | `"Courier New"` | Famiglia font monospace |
| `FONT_LABEL_PT` | `11` | Dimensione font etichetta bold sopra il log |

Nessuna costante va aggiunta a `tema.py` per questo elemento.

### Rischio NVDA

**Rischio: Minimo — monitorare il cambio di label.**

- Il cambio di `SetBackgroundColour()` e `SetForegroundColour()` su `wx.TextCtrl` è
  puramente visivo; non modifica il testo accessibile né il contenuto vocalizzato.
- Il cambio di label da `"Log annunci (Ctrl+E per consultare):"` a `"Cronologia annunci (Ctrl+E)"`:
  la `wx.StaticText` è un elemento statico non vocalizzato automaticamente da NVDA
  (non è etichetta formale di un campo). L'utente non percepisce differenza vocale.
- `Ctrl+E` (binding in `_on_char_hook()`) non cambia.

### Rischio focus

**Rischio: Nullo.**

- `_consulta_log()` chiama `self._log_ctrl.SetFocus()` — invariato.
- Il widget `_log_ctrl` mantiene la stessa posizione nel ciclo Tab.
- Il campo è `TE_READONLY`: non accetta input da tastiera alfanumerico.

### Rischio alto contrasto (Windows)

Su alto contrasto, `SetBackgroundColour()` e `SetForegroundColour()` su `wx.TextCtrl` vengono
ignorati. Il log torna ai colori di sistema (bianco/nero o contrasto invertito). **Impatto:**
nessuna degradazione funzionale; il testo rimane leggibile con i colori di sistema.

### Complessità stimata

**Bassa.** 3–4 chiamate aggiuntive in `_build_ui()`, più aggiornamento degli import.

---

## Ordine di implementazione consigliato

| Ordine | Elemento | Motivazione |
|--------|----------|-------------|
| 1° | **B — Colori pulsanti** | Nessuna dipendenza esterna. Solo modifiche a codice già esistente in un metodo isolato. Rischio zero. Reversibile in 1 minuto. |
| 2° | **D — Stile log** | Completamente indipendente da B, C, A. Modifica localizzata a `_build_ui()`. Rischio zero. |
| 3° | **C — Lampeggio** | Introduce il timer secondario e la `_mappa_celle_numero`. Va implementato dopo D (che non tocca PannelloCartella) per ridurre la finestra di errori. Richiede test EVT_CLOSE. |
| 4° | **A — Header Bar** | Dipende da `COLORE_HEADER_ACCENT` (aggiunto in B/D o in un preambolo). Introduce una nuova classe e due punti di aggiornamento nel renderer. Va per ultimo perché ha il maggior numero di touch point. |

---

## Riepilogo costanti tema.py da aggiungere

| Costante | Valore | Elemento | Sezione tema.py |
|----------|--------|----------|-----------------|
| `COLORE_HEADER_ACCENT` | `"#FFB300"` | A | Accenti |
| `COLORE_BTN_INIZIA` | `"#2E7D32"` | B | Pulsanti |
| `COLORE_BTN_PASSA_TURNO` | `"#1565C0"` | B | Pulsanti |
| `COLORE_BTN_HO_FINITO` | `"#E65100"` | B | Pulsanti |
| `COLORE_BTN_RIPRENDI` | `"#388E3C"` | B | Pulsanti |

Totale: **5 nuove costanti** (tutte alias semantici di costanti già esistenti, tranne `COLORE_HEADER_ACCENT`).

---

## Riepilogo import da aggiungere in finestra_gioco.py

Costanti già in `tema.py` ma non ancora importate in `finestra_gioco.py`:

```
# Per elemento A
COLORE_HEADER_BG, FONT_HEADER_PT, ALTEZZA_HEADER,

# Per elemento B
COLORE_BTN_PAUSA, COLORE_BTN_GRIGIO, COLORE_BTN_DISABILITATO,

# Per elemento C
COLORE_CELLA_EVIDENZIATA,

# Per elemento D
COLORE_LOG_BG, COLORE_TESTO_MUTED, FONT_LOG_PT, FONT_LABEL_PT, FONT_LOG_FAMIGLIA,
```

Costanti nuove da importare dopo aggiunta a `tema.py`:

```
COLORE_HEADER_ACCENT,
COLORE_BTN_INIZIA, COLORE_BTN_PASSA_TURNO, COLORE_BTN_HO_FINITO, COLORE_BTN_RIPRENDI,
```

Totale: **17 import aggiuntivi** nel blocco `from bingo_game.ui.tema import (...)`.
