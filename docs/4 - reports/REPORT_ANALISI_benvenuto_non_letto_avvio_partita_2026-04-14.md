# Report Analisi: messaggio di benvenuto non letto all'avvio partita

- Data: 2026-04-14
- Agente: Agent-Analyze
- Ambito: FinestraGioco.__init__ / _imposta_focus_iniziale / WxRenderer
- File coinvolti: finestra_gioco.py, renderer_wx.py, finestra_configurazione.py

---

## Sintomo

Dopo la configurazione, quando si entra nella finestra di gioco, il messaggio
di benvenuto ("Sei nella finestra di gioco. Premi Inizia partita o
Ctrl+Invio...") non viene letto da NVDA. L'utente non riceve alcuna
indicazione vocale su come procedere.

---

## Flusso attuale (sequenza temporale)

### Fase 1 — Costruttore FinestraGioco.__init__ (finestra_gioco.py:565-631)

1. `_build_ui()` costruisce tutti i widget
2. `_bind_finestra()` registra gli handler
3. `Centre()`
4. `renderer.aggiorna_finestra(self)` — aggiorna il riferimento al frame
5. `renderer.imposta_widget_log(self._log_ctrl)` — collega il log testuale
6. `self._pannello_griglia.SetFocus()` — primo focus
7. `wx.CallAfter(self._imposta_focus_iniziale)` — **schedula nel mainloop**

### Fase 2 — Chiamante finestra_configurazione.py:219-230

8. `finestra_gioco.Show()` — finestra diventa visibile
9. `self.Hide()` — finestra configurazione si nasconde

NVDA reagisce immediatamente a:
- Show() del frame: legge titolo "Tombola Stark — In gioco"
- SetFocus() su _pannello_griglia: legge nome accessibile "Griglia cartella"
- Hide() della finestra precedente: possibile re-focus automatico

### Fase 3 — Esecuzione CallAfter: _imposta_focus_iniziale (finestra_gioco.py:1452-1465)

Eseguito nel primo idle dell'event loop **dopo** Show()/Hide():

10. `_dispatch(comandi.imposta_focus_cartella(1))`
    - handler: _handle_focus_cartella_impostato
    - vocalizza: "Cartella 1 selezionata." (AO2 speak, interrupt=False → accoda)
11. `_dispatch(comandi.vai_a_riga(1))`
    - handler: _handle_vai_a_riga_avanzata
    - vocalizza: "Avanzata riga 1, 0 segnati su N: ..." (accoda in coda NVDA)
12. `_dispatch(comandi.vai_a_colonna(1))`
    - handler: _handle_vai_a_colonna_avanzata
    - vocalizza: "Avanzata colonna 1, 0 segnati su N: ..." (accoda in coda NVDA)
13. `_aggiorna_griglie_visive()` — aggiorna pannelli visivi, nessun output vocale diretto
14. `_aggiorna_titolo_cartella()` — SetLabel su StaticText, nessun speak diretto
15. `wx.CallAfter(renderer.mostra_messaggio_sistema, "Sei nella finestra di gioco...")` — **secondo CallAfter annidato**

### Fase 4 — Esecuzione CallAfter annidato

16. `mostra_messaggio_sistema("Sei nella finestra di gioco...")`
    - chiama `_wx_aggiorna_output(testo)` — aggiorna griglia testuale + log
    - chiama `_ao2_vocalizza(testo)` — AO2 speak con interrupt=False → accoda

---

## Causa radice

Il messaggio di benvenuto non viene letto per una combinazione di fattori:

### Causa 1 — Coda vocale satura (effetto principale)

Prima che il messaggio di benvenuto venga accodato (passo 16), la coda AO2/NVDA
contiene gia 3 annunci di navigazione (passi 10-12). Tutti sono emessi con
`interrupt=False`, cioe si accodano. La coda totale al momento del benvenuto e:

1. "Cartella 1 selezionata."
2. "Avanzata riga 1, 0 segnati su 5: 12 vuoto 34 vuoto 56" (esempio)
3. "Avanzata colonna 1, 0 segnati su 3: 12 vuoto 45" (esempio)
4. **"Sei nella finestra di gioco..."** (il messaggio utile)

L'utente sente una raffica di informazioni tecniche di navigazione prima del
messaggio orientativo. Nella maggior parte dei casi l'utente interrompe la
lettura premendo un tasto o spostando il focus, e il messaggio di benvenuto
non viene mai raggiunto.

### Causa 2 — NVDA interrompe su focus change

Quando NVDA rileva un cambio di focus (Show, SetFocus, eventi wx), interrompe
la lettura corrente per annunciare il nuovo elemento focalizzato.
La sequenza Show() → SetFocus(pannello_griglia) → CallAfter produce almeno
2 interruzioni NVDA prima che i dispatch comincino, e ogni evento che aggiorna
widget visivi puo scatenarne di ulteriori.

### Causa 3 — CallAfter annidato ritarda ulteriormente il benvenuto

Il messaggio di benvenuto e in un `wx.CallAfter` dentro `_imposta_focus_iniziale`,
che a sua volta e gia in un `wx.CallAfter`. Questo significa che il benvenuto
viene schedulato nel **secondo** idle cycle dopo l'init. In ambienti con NVDA
attivo, il primo idle cycle gia produce eventi di focus che resettano la coda
di lettura.

---

## Impatto accessibilita

- L'utente non vedente entra nella finestra di gioco senza alcuna guida
- Non sa che deve premere "Inizia partita" o Ctrl+Invio
- Non sa che Ctrl+H apre la guida ai tasti rapidi
- Sente solo frammenti di navigazione cartella che non ha contesto

---

## Proposta di fix (3 interventi, tutti in finestra_gioco.py)

### Fix A — Sopprimere la vocalizzazione dei dispatch iniziali

I 3 dispatch in `_imposta_focus_iniziale` servono a posizionare il focus logico
interno (cartella 1 / riga 1 / colonna 1), ma la loro vocalizzazione all'avvio
e solo rumore. Possibile approccio:

- Introdurre un flag `_avvio_in_corso: bool = True` nel costruttore
- In `_dispatch`, se `_avvio_in_corso` e True, non delegare al renderer
  (oppure usare un renderer temporaneo muto)
- Al termine di `_imposta_focus_iniziale`, impostare `_avvio_in_corso = False`

Questo elimina i 3 annunci di navigazione e lascia solo il benvenuto.

### Fix B — Usare interrupt=True per il messaggio di benvenuto

Cambiare la chiamata del messaggio di benvenuto da:
```python
self._renderer.mostra_messaggio_sistema(testo)
```
a una nuova variante o chiamata diretta che vocalizza con `interrompi=True`,
in modo che qualsiasi rumore precedente nella coda venga azzerato.

### Fix C — Eliminare il CallAfter annidato

Il messaggio di benvenuto puo essere emesso direttamente alla fine di
`_imposta_focus_iniziale` senza un secondo CallAfter, oppure con un singolo
`wx.CallAfter` al posto di quello annidato, riducendo la latenza e il rischio
che NVDA lo perda.

### Combinazione consigliata

Fix A + Fix C: sopprimere i dispatch vocali all'avvio e vocalizzare il
messaggio di benvenuto direttamente (non annidato) con `interrupt=True`.
Questo garantisce che l'utente senta **un solo messaggio** chiaro e
immediato all'ingresso nella finestra di gioco.

---

## File da modificare

- `bingo_game/ui/finestra_gioco.py` — `_imposta_focus_iniziale`, `_dispatch` e/o `__init__`

## File da NON modificare

- `bingo_game/ui/renderers/renderer_wx.py` — il renderer funziona correttamente
- `bingo_game/ui/finestra_configurazione.py` — il lancio della finestra e corretto
- `my_lib/vocalizzatore.py` — il backend TTS e corretto

---

## Prossimo passo suggerito

- Agent-Design per definire la soluzione dettagliata (flag avvio / interrupt)
- Agent-Code per implementare il fix
