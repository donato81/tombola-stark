# Report Analisi: messaggio di benvenuto ancora non letto dopo le fix precedenti

- Data: 2026-04-14
- Agente: Agent-Analyze
- Ambito: FinestraGioco, WxRenderer, Vocalizzatore, catena AO2/NVDA
- Stato: post-fix G2 (flag `_avvio_silenzioso` + rimozione CallAfter annidato)

---

## Sintomo

Nonostante le fix documentate in CHANGELOG (G2), il messaggio di benvenuto
("Sei nella finestra di gioco. Premi Inizia partita o Ctrl+Invio...") continua
a non essere letto da NVDA all'avvio della partita.

---

## Fix precedenti implementate (riepilogo)

Il report del 2026-04-14 (REPORT_ANALISI_benvenuto_non_letto_avvio_partita)
proponeva tre interventi combinati:

- Fix A: sopprimere la vocalizzazione dei 3 dispatch iniziali
- Fix B: emettere il benvenuto con `interrompi=True`
- Fix C: eliminare il `wx.CallAfter` annidato

Stato attuale nel codice:

- Fix A: IMPLEMENTATA — flag `_avvio_silenzioso` in `finestra_gioco.py:618`
- Fix B: NON IMPLEMENTATA — il benvenuto passa da `mostra_messaggio_sistema`
  che non usa `interrompi=True`
- Fix C: IMPLEMENTATA — il benvenuto e emesso direttamente a fine
  `_imposta_focus_iniziale`, senza CallAfter annidato

---

## Diagnosi dettagliata

### Causa 1 — Fix B mancante: `interrompi=True` mai applicato (bloccante)

Il messaggio di benvenuto percorre questa catena:

```
_imposta_focus_iniziale                     (finestra_gioco.py:1482)
  -> renderer.mostra_messaggio_sistema(testo)   (renderer_wx.py:173)
    -> _ao2_vocalizza(testo)                    (renderer_wx.py:846)
      -> vocalizzatore.vocalizza_testo(testo)   (vocalizzatore.py:89)
        -> backend.speak(testo, interrupt=False)
```

`_ao2_vocalizza` chiama `vocalizza_testo(testo)` senza passare `interrompi=True`.
Il parametro `interrompi` ha valore predefinito `False`.
Il risultato e che `backend.speak(testo, interrupt=False)` accoda il messaggio
in fondo alla coda NVDA invece di svuotarla e parlare subito.

Poiche NVDA ha gia generato annunci propri (vedi Causa 2), il benvenuto
o viene letto troppo tardi (quando l'utente ha gia premuto un tasto)
o viene troncato da un evento di focus successivo.

### Causa 2 — Annunci NVDA nativi da Show/SetFocus (aggravante)

Il flusso temporale tra finestra_configurazione.py e l'event loop e:

```
1. FinestraGioco.__init__()
     ...
     self._pannello_griglia.SetFocus()          # (riga 636) — focus pre-Show
     wx.CallAfter(self._imposta_focus_iniziale)  # (riga 637) — schedulato

2. finestra_gioco.Show()                         # (configurazione:226)
     -> NVDA legge titolo finestra: "Tombola Stark — In gioco"
     -> NVDA legge controllo focus: "Griglia cartella"

3. self.Hide()                                   # (configurazione:227)
     -> possibile re-focus/re-announce NVDA

4. Event loop idle -> _imposta_focus_iniziale()
     -> 3 dispatch silenziosi (Fix A funziona)
     -> mostra_messaggio_sistema("Sei nella finestra di gioco...")
       -> _ao2_vocalizza(testo)        # interrupt=False
```

Al passo 4, NVDA ha gia nella coda (o sta gia leggendo) almeno:
- "Tombola Stark - In gioco" (titolo finestra)
- "Griglia cartella" (nome accessibile del pannello in focus)

Il benvenuto si accoda dopo questi messaggi nativi. Senza `interrupt=True`,
non li interrompe.

### Causa 3 — SetFocus prima di Show (concorrente)

`self._pannello_griglia.SetFocus()` (riga 636) viene chiamato nel costruttore,
prima che `Show()` venga invocato dal chiamante (finestra_configurazione.py:226).

Su Windows, un `SetFocus()` su una finestra non ancora visibile puo:
- Non produrre alcun effetto reale sul focus di sistema
- Essere ripetuto implicitamente da wxPython/Windows quando `Show()` viene
  chiamato, generando un doppio evento EVT_SET_FOCUS
- Produrre un focus event NVDA aggiuntivo non previsto

Questo aumenta il rumore nella coda NVDA e riduce la probabilita che il
benvenuto venga raggiunto prima di un'interruzione.

### Causa 4 — mostra_messaggio_sistema non distingue contesti

`mostra_messaggio_sistema` (renderer_wx.py:172-174) e un metodo generico:

```python
def mostra_messaggio_sistema(self, testo: str) -> None:
    self._wx_aggiorna_output(testo)
    self._ao2_vocalizza(testo)
```

Non ha alcun parametro per forzare l'interruzione della coda. Il benvenuto
usa lo stesso percorso di un qualsiasi messaggio di sistema, senza priorita.
Nessun helper alternativo e stato introdotto per il caso critico dell'avvio.

---

## Riepilogo priorita blocchi

| ID | Descrizione | Severita | Stato |
|---|---|---|---|
| B1 | `interrompi=True` non usato nel benvenuto | Bloccante | Fix B non implementata |
| B2 | Annunci NVDA nativi da Show/SetFocus in coda | Aggravante | Non mitigato |
| B3 | SetFocus pre-Show produce potenziali focus spurii | Concorrente | Non mitigato |
| B4 | mostra_messaggio_sistema senza parametro interrupt | Strutturale | Non risolto |

---

## Proposta di risoluzione

### Intervento 1 — Applicare Fix B (priorita massima)

Alla fine di `_imposta_focus_iniziale`, sostituire:

```python
self._renderer.mostra_messaggio_sistema(
    "Sei nella finestra di gioco. ..."
)
```

con una chiamata che vocalizzi con interruzione esplicita, ad esempio:

```python
testo_benvenuto = (
    "Sei nella finestra di gioco. "
    "Premi Inizia partita o Ctrl+Invio per estrarre il primo numero. "
    "Premi Ctrl+H per la guida ai tasti rapidi."
)
self._renderer._wx_aggiorna_output(testo_benvenuto)
self._renderer._vocalizzatore.vocalizza_testo(testo_benvenuto, interrompi=True)
self._renderer._ultimo_annuncio = testo_benvenuto
```

Oppure, piu pulito architetturalmente, introdurre un metodo dedicato nel
renderer:

```python
def mostra_messaggio_benvenuto(self, testo: str) -> None:
    self._wx_aggiorna_output(testo)
    self._ultimo_annuncio = testo
    self._vocalizzatore.vocalizza_testo(testo, interrompi=True)
```

Questo garantisce che, qualunque cosa sia in coda NVDA al momento, venga
interrotta e il benvenuto letto immediatamente.

### Intervento 2 — Spostare SetFocus dopo Show (consigliato)

Rimuovere `self._pannello_griglia.SetFocus()` dal costruttore (riga 636) e
spostare il SetFocus alla fine di `_imposta_focus_iniziale`, subito prima del
messaggio di benvenuto. Questo riduce gli eventi NVDA spurii generati tra
Show() e il benvenuto.

### Intervento 3 — Aggiungere wx.CallAfter al benvenuto con delay (opzionale)

Se l'Intervento 1 da solo non basta in pratica (verificabile solo con NVDA),
aggiungere un piccolo `wx.CallLater(200, ...)` per il benvenuto, dando tempo
a NVDA di completare i propri annunci di focus prima di interrompere.
Questo e un fallback empirico, da usare solo se il test manuale conferma
che l'interrupt immediato non e sufficiente.

---

## File da modificare per la fix

- `bingo_game/ui/finestra_gioco.py` — `_imposta_focus_iniziale`, posizione di SetFocus
- `bingo_game/ui/renderers/renderer_wx.py` — nuovo metodo con parametro interrupt (opzionale)

## File da NON modificare

- `my_lib/vocalizzatore.py` — il backend funziona correttamente
- `bingo_game/ui/finestra_configurazione.py` — il lancio e corretto
- Nessun file di dominio o application

---

## Verifica suggerita

1. Avviare l'app con NVDA attivo
2. Completare la configurazione e avviare la partita
3. Verificare che NVDA legga immediatamente e per primo:
   "Sei nella finestra di gioco. Premi Inizia partita o Ctrl+Invio..."
4. Verificare che NON vengano letti prima "Tombola Stark — In gioco"
   ne "Griglia cartella" ne annunci di navigazione cartella/riga/colonna

---

## Prossimo passo suggerito

- Agent-Code per implementare Intervento 1 (Fix B) e Intervento 2
- Test manuale con NVDA per validazione
