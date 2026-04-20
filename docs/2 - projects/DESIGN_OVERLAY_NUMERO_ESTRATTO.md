---
type: design
titolo: Overlay visivo numero estratto (monitor bingo sala)
data_creazione: 2026-04-20
agent: Agent-Design
status: REVIEWED
feature: overlay_numero_estratto
---

## Obiettivo

Mostrare agli utenti vedenti (che non usano screen reader) il numero appena
estratto in formato grande e ad alta visibilità per circa 10 secondi, in
analogia con i monitor presenti nelle sale bingo fisiche.
L'elemento visivo deve sparire automaticamente e non alterare in alcun modo
le funzionalità già implementate per NVDA e screen reader.

## Contesto

Segnalazione post-alpha da utenti vedenti: la `HeaderBar` in cima alla
`FinestraGioco` mostra il numero estratto in font 12 pt su sfondo scuro; è
poco visibile a colpo d'occhio durante il gioco. L'attuale meccanismo di
lampeggio è limitato alla cella della cartella del giocatore (piccola, 9 col ×
3 righe) e non è percepibile come annuncio globale.

Versione baseline: `0.14.1` (post fix click-mouse).

### Architettura del flusso di estrazione attuale

```
FinestraGioco._on_pulsante_principale()
  └─► ComandiSistema.esegui_fase_estrazione(partita)
  └─► renderer.annuncia_numero_estratto(numero, turno)
        ├─► _wx_aggiorna_output(testo)    [pannello griglia]
        ├─► _wx_avvia_lampeggio(numero)   [cella cartella]
        ├─► _wx_aggiorna_header(...)      [HeaderBar]
        └─► _ao2_vocalizza(testo)         [screen reader — INVARIATO]
```

Il nuovo metodo `_wx_mostra_overlay_numero(numero)` si inserisce tra
`_wx_aggiorna_header(...)` e `_ao2_vocalizza(testo)`, senza alterare né il
testo vocalizzato né l'ordine delle chiamate esistenti.

## Componenti coinvolti

| File | Tipo modifica | Descrizione |
|------|--------------|-------------|
| `bingo_game/ui/overlay_numero.py` | CREATE | Classe `OverlayNumeroEstratto` — finestra overlay |
| `bingo_game/ui/tema.py` | MODIFY | 3 nuove costanti: `FONT_OVERLAY_PT`, `FONT_OVERLAY_LABEL_PT`, `DIMENSIONE_OVERLAY` |
| `bingo_game/ui/finestra_gioco.py` | MODIFY | Istanziazione overlay, metodo `mostra_overlay_numero()`, aggiornamento `_on_close()` |
| `bingo_game/ui/renderers/renderer_wx.py` | MODIFY | Metodo `_wx_mostra_overlay_numero()`, una riga in `annuncia_numero_estratto()` |

## Decisione architetturale: `wx.Frame` vs `wx.PopupWindow`

### Opzione scelta: `wx.Frame` con `STAY_ON_TOP | FRAME_NO_TASKBAR | BORDER_NONE`

**Motivazione:**
- `wx.PopupWindow` su Windows non gestisce `STAY_ON_TOP` in modo affidabile
  con tutte le versioni di wxPython (comportamento non garantito nello stack
  Windows 10/11 + NVDA).
- `wx.Frame` con `style = wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR | wx.BORDER_NONE`
  è il pattern più testato per overlay non interattivi su Windows.
- `FRAME_NO_TASKBAR` garantisce che il frame non compaia nell'Alt+Tab switcher,
  eliminando il rischio che NVDA lo legga quando il focus switcher è aperto.
- `FRAME_TOOL_WINDOW` aggiuntivo rimuove il frame dall'elenco finestre di Windows,
  prevenendo ulteriori annunci da parte di NVDA.

**Ciclo di vita:**
- Istanziato **una sola volta** in `FinestraGioco.__init__()` e tenuto nascosto.
- `mostra_numero(n)` → popola l'etichetta, posiziona, chiama `Show()`, avvia il timer.
- Timer ONE_SHOT da 10 000 ms → chiama `Hide()`.
- Se `mostra_numero()` viene chiamato mentre l'overlay è già visibile, il timer
  viene resettato (Stop + Start) per evitare scomparse premature.
- `FinestraGioco._on_close()` chiama `Destroy()` sull'overlay prima di procedere.

## Flussi Concettuali

### Flusso normale (estrazione)

```
[Estrazione numero N]
  │
  ├─► renderer._wx_aggiorna_header()   → HeaderBar aggiornata (invariata)
  ├─► renderer._wx_mostra_overlay_numero(N)
  │       └─► finestra.mostra_overlay_numero(N)
  │               └─► overlay.mostra_numero(N)
  │                       ├─► SetLabel(str(N))
  │                       ├─► SetPosition(...)   ← angolo basso-destra FinestraGioco
  │                       ├─► Show()
  │                       └─► timer.Start(10000, ONE_SHOT)
  └─► renderer._ao2_vocalizza(testo)   → NVDA invariato
```

### Flusso timer scaduto

```
[Timer ONE_SHOT 10 s scaduto]
  └─► OverlayNumeroEstratto._on_timer()
          └─► Hide()
```

### Flusso chiusura FinestraGioco

```
[EVT_CLOSE su FinestraGioco]
  └─► _on_close()
          ├─► pannello_cartella.ferma_lampeggio()   ← esistente
          ├─► overlay_numero.Destroy()              ← NUOVO
          └─► event.Skip()
```

## Layout dell'overlay

```
┌──────────────────────────┐
│   Numero estratto        │   ← StaticText font 16 pt, colore muted
│                          │
│          42              │   ← StaticText font 72 pt, colore #FFB300 (giallo bingo)
│                          │
└──────────────────────────┘
 Dimensione: 260 × 180 px
 Sfondo: #2C3E50 (blu-ardesia, coerente con HeaderBar)
 Bordo: nessuno
 Posizione: angolo inferiore-destro della FinestraGioco
```

## Vincoli e garanzie di non-regressione NVDA

| Proprietà | Garanzia |
|-----------|----------|
| Focus tastiera | L'overlay NON riceve mai `SetFocus()`. Tab, frecce e screen reader lo ignorano. |
| Accessibilità NVDA | Nessun `SetName()` utile, nessun `wx.accessible`, nessun `SetAccessible()`. |
| `_ao2_vocalizza(testo)` | Invariato: chiamato con lo stesso testo, nello stesso momento. |
| HeaderBar | Invariata: `_wx_aggiorna_header()` non viene toccata. |
| Lampeggio cartella | Invariato: `_wx_avvia_lampeggio()` è indipendente dall'overlay. |
| Layout FinestraGioco | Invariato: l'overlay è un frame separato, fuori da qualsiasi sizer. |
| Alt+Tab Windows | `FRAME_NO_TASKBAR` + `FRAME_TOOL_WINDOW` impediscono la comparsa. |
| Chiusura finestra | `_on_close()` distrugge l'overlay prima di `event.Skip()`. |

## Rischi e punti da monitorare

1. **Posizionamento multi-monitor**: usare `GetScreenPosition()` (coordinate globali)
   e non `GetPosition()` (coordinate client) per calcolare l'offset corretto.

2. **Ridimensionamento finestra**: se l'utente ridimensiona `FinestraGioco` mentre
   l'overlay è visibile, la posizione non si aggiorna automaticamente.
   — Mitigazione fase 1: posizione calcolata solo al momento di `Show()`.
   — Mitigazione opzionale fase 2: bind a `EVT_MOVE` / `EVT_SIZE` sul parent.

3. **Estrazioni rapide consecutive**: se l'utente esegue due estrazioni in meno di
   10 s, il timer viene resettato e il numero aggiornato. Comportamento corretto.

4. **Compatibilità wxPython**: testare empiricamente che `BORDER_NONE` +
   `STAY_ON_TOP` funzionino con la versione installata prima di procedere
   all'implementazione.

## Riferimento al report di analisi

docs/4 - reports/REPORT_ANALISI_OVERLAY_NUMERO_ESTRATTO_2026-04-20.md
