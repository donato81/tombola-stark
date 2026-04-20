# REPORT — Fattibilità Lampeggio Pulsante "Sono pronto / Ho finito"

**Data:** 2026-04-20
**Feature richiesta:** Rendere visivamente evidente (lampeggio) il pulsante principale
nei momenti in cui il giocatore vedente deve premerlo per chiudere il proprio turno,
senza interferire con l'accessibilità NVDA già implementata.

---

## 1. Stato attuale — il pulsante "Sono pronto"

### 1.1 Identificazione del widget

Il pulsante in questione è `FinestraGioco._btn_principale`, un `wx.Button` creato
in `_build_ui()` (riga ~677, `bingo_game/ui/finestra_gioco.py`).
Non ha un nome fisso: la sua etichetta cambia in base alla fase di gioco.

### 1.2 Ciclo di vita etichette

| Fase UI (`_fase_turno_ui`) | Etichetta pulsante | Colore sfondo |
|---|---|---|
| `attesa_estrazione` (primo avvio) | "Inizia partita" | `COLORE_BTN_INIZIA` (#2E7D32, verde) |
| `attesa_estrazione` (turni successivi) | "Passa turno" | `COLORE_BTN_PASSA_TURNO` (#1565C0, blu) |
| `attesa_reclami` | "Ho finito — avvia verifica" | `COLORE_BTN_HO_FINITO` (#E65100, arancione) |
| `pausa_turno` | "Pausa in corso…" | `COLORE_BTN_GRIGIO` (#757575, grigio, disabilitato) |
| `in_pausa` | "Gioco in pausa" | `COLORE_BTN_DISABILITATO` (#BDBDBD, disabilitato) |

**La fase critica è `attesa_reclami`**: l'utente ha appena visto apparire il numero
estratto (overlay + lampeggio cella cartella) e deve premere questo pulsante—
oppure usare Ctrl+Invio — per chiudere il suo turno prima che scada il timer.

### 1.3 Sequenza di entrata nella fase attesa_reclami

```
_on_pulsante_principale()   [fase == "attesa_estrazione"]
  └─► ComandiSistema.esegui_fase_estrazione(partita)
  └─► _renderer.annuncia_numero_estratto(numero, turno)    # NVDA + overlay + lampeggio cella
  └─► _aggiorna_griglie_visive()
  └─► _fase_turno_ui = "attesa_reclami"
  └─► _aggiorna_stato_pulsante()    ← qui il pulsante diventa "Ho finito"
  └─► _avvia_timer_azione(durata_finestra_ms)
  └─► _pianifica_risposta_bot()
```

### 1.4 Uscita dalla fase attesa_reclami

Il pulsante smette di essere rilevante in tre scenari:
1. **Click manuale** — utente preme il pulsante (o Ctrl+Invio): `_on_pulsante_principale()`
2. **Timeout** — scade il timer azione: `_on_timeout_azione()`
3. **Tutti pronti** — tutti i giocatori dichiarano fine prima del timeout: `_on_all_ready()`

Tutti e tre confluiscono in `_esegui_verifica_premi()` che imposta
`_fase_turno_ui = "pausa_turno"` e richiama `_aggiorna_stato_pulsante()`.

---

## 2. Meccanismo di lampeggio già esistente (PannelloCartella)

Il codebase ha già un precedente diretto: `PannelloCartella.avvia_lampeggio()`
(riga ~247, `finestra_gioco.py`), che fa lampeggiare la cella del numero appena
estratto. Funziona con:

```python
self._timer_lampeggio = wx.Timer(self)
self.Bind(wx.EVT_TIMER, self._on_tick_lampeggio, self._timer_lampeggio)
self._timer_lampeggio.Start(300)   # tick ogni 300 ms
```

Nel tick alterna `SetBackgroundColour()` + `Refresh()` per N cicli
(`_N_TICK_LAMPEGGIO = 7`, circa 2,1 secondi), poi si ferma.

Questa architettura è esattamente riproducibile per il pulsante, con
la differenza che il lampeggio del pulsante deve durare per tutta la
fase `attesa_reclami` (fino a click/timeout/all_ready), non un numero
fisso di cicli.

---

## 3. Analisi tecnica di fattibilità

### 3.1 Supporto SetBackgroundColour su wx.Button in Windows

L'ostacolo classico su wxPython/Windows è che il sistema operativo applica
il tema visuale (UXTHEME) sui `wx.Button` standard, ignorando talvolta
`SetBackgroundColour`. 

**Il codice attuale dimostra che non è un problema in questo codebase:**
`aggiorna_stato_pulsante()` (riga ~1299) già cambia con successo il colore
di sfondo di `_btn_principale` in cinque stati diversi tramite `SetBackgroundColour()`.
Il lampeggio userà la stessa chiamata, quindi non introduce nuovi rischi di compatibilità.

### 3.2 Impatto su NVDA

Il lampeggio è **esclusivamente visivo**: alterna il colore di sfondo del pulsante.
Non modifica la proprietà `Label`, non emette eventi accessibilità, non sposta il focus.
NVDA non annuncia cambio di sfondo sui pulsanti. La label "Ho finito — avvia verifica"
viene già vocalizzata da `annuncia_fase_turno()` all'ingresso nella fase.

**Non c'è interferenza con NVDA.** Il requisito "nessun feedback esclusivamente visivo
senza alternativa testuale" (ui.instructions.md) è soddisfatto perché la voce già
annuncia la transizione di fase.

### 3.3 Colori proposti per il lampeggio

Alternanza tra:
- Stato A: `COLORE_BTN_HO_FINITO` = `#E65100` (arancione, colore corrente della fase)
- Stato B: `#FFFFFF` (bianco) oppure `#FFD54F` (giallo oro, già usato in `COLORE_TITOLO_MENU`)

Si raccomanda `#FFD54F` perché offre contrasto leggibile (testo scuro su giallo)
e coerenza col vocabolario cromatico del tema. In alternativa `#FF8F00` (arancione
chiaro) mantiene la tonalità arancione attenuando il lampeggio.

La coppia `#E65100` ↔ `#FFD54F` garantisce un rapporto di contrasto misurabile
dai test di accessibilità visiva (non necessario per NVDA, ma buona pratica).

### 3.4 Durata e ritmo del lampeggio

Per non essere stancante né invisibile si raccomanda:
- Intervallo: **500 ms** (mezzo secondo per semi-ciclo) → 1 lampeggio completo al secondo
- Durata: **illimitata** — il lampeggio resta attivo per tutta la fase `attesa_reclami`
  e si ferma automaticamente all'uscita (click, timeout, tutti_pronti)

Questo è diverso dal lampeggio cella (7 tick fissi), che serve solo per richiamare
l'attenzione iniziale. Il lampeggio del pulsante deve essere persistente perché
l'utente può impiegare molti secondi a segnare il numero prima di premere il pulsante.

---

## 4. File coinvolti e impatto stimato

### 4.1 File da modificare

| File | Tipo modifica | Stima righe |
|---|---|---|
| `bingo_game/ui/finestra_gioco.py` | MODIFY | +30/40 righe |
| `bingo_game/ui/tema.py` | MODIFY | +2 righe (nuova costante colore) |

### 4.2 Nessuna modifica necessaria a

- Layer dominio (`bingo_game/domain/`) — nessun impatto
- Layer applicazione (`bingo_game/game_controller.py`, `bingo_game/partita.py`) — nessun impatto
- Renderer (`bingo_game/ui/renderers/`) — nessun impatto
- Test esistenti — nessun impatto (test unitari non coprono GUI pura)

### 4.3 Struttura delle modifiche in `finestra_gioco.py`

**In `FinestraGioco.__init__`** — aggiungere due attributi di stato:
```python
self._timer_lampeggio_btn: Optional[wx.Timer] = None
self._lampeggio_btn_attivo: bool = False
```

**Nuovo metodo `_avvia_lampeggio_btn()`:**
```python
def _avvia_lampeggio_btn(self) -> None:
    """Avvia il lampeggio del pulsante principale (fase attesa_reclami)."""
    if self._lampeggio_btn_attivo:
        return
    self._lampeggio_btn_attivo = True
    self._timer_lampeggio_btn = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self._on_tick_lampeggio_btn, self._timer_lampeggio_btn)
    self._timer_lampeggio_btn.Start(500)
```

**Nuovo metodo `_ferma_lampeggio_btn()`:**
```python
def _ferma_lampeggio_btn(self) -> None:
    """Ferma il lampeggio e ripristina il colore standard della fase."""
    if self._timer_lampeggio_btn is not None:
        self._timer_lampeggio_btn.Stop()
        self._timer_lampeggio_btn = None
    self._lampeggio_btn_attivo = False
    # Ripristina colore standard "Ho finito"
    self._btn_principale.SetBackgroundColour(wx.Colour(COLORE_BTN_HO_FINITO))
    self._btn_principale.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
    self._btn_principale.Refresh()
```

**Nuovo metodo `_on_tick_lampeggio_btn()`:**
```python
def _on_tick_lampeggio_btn(self, event: wx.TimerEvent) -> None:
    """Tick lampeggio: alterna sfondo tra arancione e giallo-oro."""
    if not self._lampeggio_btn_attivo:
        return
    # Usa _tick contatore per alternare i colori
    self._tick_lampeggio_btn = getattr(self, "_tick_lampeggio_btn", 0) + 1
    if self._tick_lampeggio_btn % 2 == 1:
        self._btn_principale.SetBackgroundColour(wx.Colour(COLORE_BTN_LAMPEGGIO_A))
        self._btn_principale.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
    else:
        self._btn_principale.SetBackgroundColour(wx.Colour(COLORE_BTN_HO_FINITO))
        self._btn_principale.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
    self._btn_principale.Refresh()
```

**In `aggiorna_stato_pulsante()`** — agganciare start/stop:
- Quando `fase == "attesa_reclami"`: chiamare `_avvia_lampeggio_btn()` dopo aver impostato il colore base
- In tutti gli altri casi: chiamare `_ferma_lampeggio_btn()`

**In `_on_close()`** — fermare il timer alla chiusura:
```python
if hasattr(self, "_timer_lampeggio_btn") and self._timer_lampeggio_btn:
    self._timer_lampeggio_btn.Stop()
```

**In `tema.py`** — aggiungere costante:
```python
COLORE_BTN_LAMPEGGIO_A = "#FFD54F"   # Giallo-oro per lampeggio pulsante "Ho finito"
```

---

## 5. Rischi e vincoli

### 5.1 Rischi tecnici

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| Timer non fermato in pausa utente | Media | Visivo: pulsante continua a lampeggiare in pausa | Impostare `_ferma_lampeggio_btn()` nel branch pausa di `aggiorna_stato_pulsante()` (già gestito dalla logica proposta) |
| Timer non fermato alla chiusura finestra | Bassa | Crash di wx all'On_Close | Aggiungere `ferma_lampeggio_btn()` in `_on_close()` |
| wx.EVT_TIMER con due timer attivi contemporaneamente | Bassa | Interferenza con timer_azione esistente | I due timer (azione e lampeggio_btn) usano istanze wx.Timer distinte; Bind con istanza specifica già usato in PannelloCartella — nessun conflitto |
| Contrasto insufficiente | Bassa | Difficoltà lettura testo sul pulsante alternato | La coppia #E65100/#FFD54F verificata: testo scuro su giallo ha contrasto sufficiente |

### 5.2 Vincoli di accessibilità

- **Windows High Contrast**: in High Contrast Mode, Windows ignora i colori personalizzati sui controlli.
  Il lampeggio non sarà visibile, ma il pulsante manterrà il comportamento corretto.
  Vincolo accettabile: High Contrast è pensato per utenti ipovedenti che già si avvantaggiano
  del contrasto di sistema.
- **NVDA**: nessun impatto, come analizzato in 3.2.
- **Movimento/animazione**: per utenti con fotosensibilità, un lampeggio a 1 Hz è sotto
  la soglia critica (3 Hz) indicata dalle linee guida WCAG 2.1 (Success Criterion 2.3.1).

---

## 6. Conclusioni e raccomandazione

**La feature è tecnicamente fattibile e a basso rischio.**

Il codebase contiene già il pattern di riferimento esatto (`PannelloCartella.avvia_lampeggio`)
e il widget target (`_btn_principale`) già supporta `SetBackgroundColour` dinamico in
cinque stati diversi. L'implementazione richiede:

- Una nuova costante in `tema.py`
- Tre nuovi metodi privati in `FinestraGioco` (~30 righe totali)
- Due agganci in un metodo esistente (`aggiorna_stato_pulsante`)
- Una riga in `_on_close`

Non è richiesta nessuna modifica al dominio, all'application layer, al renderer
né ai test unitari esistenti. La feature è isolabile in un singolo commit atomico.

**Raccomandazione**: procedere con l'implementazione non appena l'utente convalida
il report. Suggerito un DESIGN minimo (non è una decisione architetturale: è una
feature puramente presentazionale su widget esistente) e un TODO operativo per
Agent-Code o implementazione diretta.

---

*Prodotto da: Agent-Analyze — modalità read-only*
*Fonti: `bingo_game/ui/finestra_gioco.py`, `bingo_game/ui/tema.py`,
`bingo_game/ui/renderers/renderer_wx.py`, `.github/instructions/ui.instructions.md`*
