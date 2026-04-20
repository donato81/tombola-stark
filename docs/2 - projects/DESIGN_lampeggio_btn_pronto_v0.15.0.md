---
type: design
feature: lampeggio_btn_pronto
agent: Agent-Design
status: REVIEWED
version: v0.15.0
date: 2026-04-20
---

# DESIGN — Lampeggio pulsante "Sono pronto / Ho finito"

## 1. Idea in 3 righe

Durante la fase `attesa_reclami`, il pulsante principale "Ho finito — avvia verifica"
deve lampeggiare (alternanza colore sfondo) per segnalare visivamente all'utente vedente
che deve premerlo per concludere il proprio turno, prima che scada il timer automatico.

## 2. Attori e Concetti

- `FinestraGioco` — frame principale di gioco; ospita `_btn_principale`
- `_btn_principale` — `wx.Button` a etichetta variabile; già supporta `SetBackgroundColour`
- `_fase_turno_ui` — flag di stato che governa il ciclo del turno (str)
- `wx.Timer` — meccanismo event-driven già in uso per PannelloCartella e timer_azione
- `aggiorna_stato_pulsante()` — metodo di FinestraGioco che aggiorna etichetta e colori
- `COLORE_BTN_HO_FINITO` / `COLORE_BTN_LAMPEGGIO_A` — coppia cromatica del lampeggio

## 3. Flussi Concettuali

### 3.1 Avvio lampeggio

```
_aggiorna_stato_pulsante()  ← chiamata da _on_pulsante_principale() dopo estrazione
  fase == "attesa_reclami"
    └─► SetBackgroundColour(COLORE_BTN_HO_FINITO)   # colore base
    └─► _avvia_lampeggio_btn()
          └─► wx.Timer(self) ogni 500 ms → _on_tick_lampeggio_btn()
                └─► alterna sfondo  COLORE_BTN_HO_FINITO ↔ COLORE_BTN_LAMPEGGIO_A
```

### 3.2 Stop lampeggio

Stop garantito in quattro punti di uscita dalla fase attesa_reclami:
1. Click utente: `_on_pulsante_principale()` → `_controlla_tutti_pronti()`
2. Timeout: `_on_timeout_azione()`
3. Tutti pronti: `_on_all_ready()`
4. Pausa utente: `_metti_in_pausa()` (tramite `aggiorna_stato_pulsante` con fase `in_pausa`)

In tutti i casi il flusso passa per `_aggiorna_stato_pulsante()` con fase diversa
da `attesa_reclami`, che chiama `_ferma_lampeggio_btn()`.
Protezione aggiuntiva in `_on_close()` per la chiusura della finestra.

### 3.3 Colori alternati

```
tick dispari  →  sfondo COLORE_BTN_LAMPEGGIO_A (#FFD54F, giallo-oro)
                 testo  COLORE_TESTO_SCURO      (#212121, scuro)
tick pari     →  sfondo COLORE_BTN_HO_FINITO   (#E65100, arancione)
                 testo  COLORE_TESTO_CHIARO     (#ECEFF1, chiaro)
```

Frequenza: 2 tick/secondo = 1 lampeggio completo/secondo (sotto soglia WCAG 2.3.1).

## 4. Decisioni Architetturali

- **Pattern scelto**: stesso pattern di `PannelloCartella.avvia_lampeggio()` già presente
  nel codebase — wx.Timer owner-bound + Bind esplicito all'istanza.
- **Non usare `Bind(wx.EVT_TIMER, handler)` senza istanza**: legherebbero tutti i timer
  del frame allo stesso handler. Usare `Bind(..., timer_instance)`.
- **Durata illimitata vs N-tick fissi**: a differenza del lampeggio cella (7 tick fissi),
  il lampeggio pulsante deve durare tutta la fase. Il timer viene fermato dall'uscita di fase.
- **Stato isolato**: `_timer_lampeggio_btn` e `_lampeggio_btn_attivo` sono attributi
  di `FinestraGioco`, ben separati da `_timer_azione` e `_timer_pausa`.
- **Nessuna modifica al renderer**: la logica è puramente presentazionale e appartiene
  alla view. Il renderer non conosce il dettaglio del lampeggio.

## 5. Rischi e Vincoli

- **Timer non fermato in pausa**: mitigato — la pausa chiama `aggiorna_stato_pulsante`
  con fase `in_pausa` che chiama `_ferma_lampeggio_btn()`.
- **Timer non fermato a chiusura finestra**: mitigato — aggiunto guard in `_on_close()`.
- **NVDA**: nessun impatto. Il lampeggio non modifica Label né sposta focus.
  `annuncia_fase_turno()` già vocalizza la transizione.
- **Windows High Contrast**: il lampeggio non sarà visibile, comportamento accettabile.
- **Fotosensibilità**: 1 Hz < soglia critica 3 Hz (WCAG 2.3.1 SC).
- **Backward compat**: nessuna API pubblica cambiata.
