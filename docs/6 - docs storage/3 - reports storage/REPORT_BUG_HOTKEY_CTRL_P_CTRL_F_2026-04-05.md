# REPORT — Bug Hotkey Ctrl+P (sono pronto) e Ctrl+F (ricerca numeri)

**Data**: 2026-04-05  
**Agente**: Agent-Analyze (read-only)  
**Segnalazione**: sessione di gioco reale — feedback utente non vedente con NVDA  
**Scope**: `bingo_game/ui/finestra_gioco.py`, `bingo_game/ui/dialogo_ricerca.py`, `bingo_game/ui/renderers/renderer_wx.py`

---

## Sintesi Problemi Segnalati

L'utente ha identificato due malfunzionamenti durante una partita reale:

1. `Ctrl+P` funziona correttamente per avviare la partita (fase `attesa_estrazione`), ma non fornisce riscontro all'utente nella fase "sono pronto" (fase `attesa_reclami`).
2. `Ctrl+F` apre correttamente il dialog di ricerca numero, ma l'esito della ricerca (trovato / non trovato) non viene mai vocalizzato.

---

## Bug 1 — Ctrl+P in fase `attesa_reclami`: azione eseguita, feedback assente

### File coinvolto
`bingo_game/ui/finestra_gioco.py` — metodo `_on_pulsante_principale`

### Analisi del codice

Il binding in `_on_char_hook` è corretto e completo:
```python
# Ctrl+P — passa turno
if ctrl and key == ord("P"):
    self._on_pulsante_principale(None)
    return
```

`_on_pulsante_principale` gestisce entrambe le fasi:
```python
elif self._fase_turno_ui == "attesa_reclami":
    umano = self._comandi_sistema.ottieni_giocatore_umano(self._partita)
    if umano is not None and not umano.turno_dichiarato_concluso:
        umano.dichiara_fine_turno()
    self._controlla_tutti_pronti()
```

### Difetto identificato

Il ramo `attesa_reclami` **esegue correttamente l'azione** (`dichiara_fine_turno()` imposta `turno_dichiarato_concluso = True` su `GiocatoreBase`), ma **non emette alcun feedback audio o visivo all'utente** che confermi la registrazione.

Al contrario, il ramo `attesa_estrazione` chiama:
- `self._renderer.annuncia_numero_estratto(...)` 
- `self._aggiorna_stato_pulsante()` → che chiama `_renderer.annuncia_fase_turno(label)`

Il ramo `attesa_reclami` non invoca nemmeno `_aggiorna_stato_pulsante()` dopo aver richiamato `dichiara_fine_turno()`.

### Conseguenze per l'utente

- Dopo aver premuto Ctrl+P nella fase "sono pronto", NVDA non legge nulla.
- L'utente crede che il tasto non abbia funzionato.
- Se preme Ctrl+P una seconda volta, la guardia `not umano.turno_dichiarato_concluso` impedisce la doppia dichiarazione, ma il silenzio persiste.
- Se altri giocatori (bot) non hanno ancora dichiarato la fine via `wx.CallLater`, `_controlla_tutti_pronti()` ritorna False silenziosamente: nessun annuncio.

### Violazione accessibilità

Ogni azione dell'utente deve produrre feedback immediato (voce + testo). L'assenza di risposta vocale è una violazione diretta del contratto NVDA descritto in `ui.instructions.md`.

### Violazione Clean Architecture (secondaria)

Il codice accede direttamente all'oggetto `GiocatoreUmano` tramite `ottieni_giocatore_umano()` e chiama `umano.dichiara_fine_turno()` bypassando la facade `ComandiGiocatoreUmano`. Il percorso corretto è `self._comandi.dichiara_fine_turno(self._partita)`.

### Fix suggerito

Aggiungere nel ramo `attesa_reclami` di `_on_pulsante_principale`, dopo aver dichiarato fine turno, una chiamata al renderer:

```python
elif self._fase_turno_ui == "attesa_reclami":
    umano = self._comandi_sistema.ottieni_giocatore_umano(self._partita)
    if umano is not None and not umano.turno_dichiarato_concluso:
        umano.dichiara_fine_turno()
        self._renderer.mostra_messaggio_sistema("Turno dichiarato concluso. Attendo gli altri giocatori.")
    elif umano is not None and umano.turno_dichiarato_concluso:
        self._renderer.mostra_messaggio_sistema("Hai già dichiarato fine turno. Attendo gli altri giocatori.")
    self._controlla_tutti_pronti()
```

Opzionalmente, allineare anche la chiamata alla facade:
```python
self._comandi.dichiara_fine_turno(self._partita)  # via ComandiGiocatoreUmano
```

---

## Bug 2 — Ctrl+F ricerca numeri: vocalizazione interrotta dalla chiusura del dialog

### File coinvolti
- `bingo_game/ui/dialogo_ricerca.py` — metodo `_on_cerca`
- `bingo_game/ui/finestra_gioco.py` — metodo `_apri_ricerca_numero`
- `bingo_game/ui/renderers/renderer_wx.py` — metodo `_handle_ricerca_numero_in_cartelle` e `_wx_aggiorna_output`

### Analisi del codice

`_on_cerca` in `dialogo_ricerca.py`:
```python
esito = self._comandi.cerca_numero(numero)
self._renderer.render_esito(esito)

# Chiusura automatica dopo l'esito
self.EndModal(wx.ID_OK)
```

`_apri_ricerca_numero` in `finestra_gioco.py`:
```python
dlg.ShowModal()
dlg.Destroy()
# Ripristina focus sulla griglia
self._pannello_griglia.SetFocus()
```

`_handle_ricerca_numero_in_cartelle` in `renderer_wx.py`:
```python
def _handle_ricerca_numero_in_cartelle(self, evento: EventoRicercaNumeroInCartelle) -> None:
    ...
    self._wx_aggiorna_output(testo)
    self._ao2_vocalizza(testo)
```

`_ao2_vocalizza` chiama `self._vocalizzatore.vocalizza_testo(testo)` → `AO2.speak(testo)`.

### Difetto principale: race condition TTS vs chiusura dialog

`AO2.speak()` è **asincrono**: avvia la sintesi vocale e ritorna immediatamente. Non aspetta che il testo sia stato letto.

La sequenza reale al momento della pressione di Invio nel dialog è:

1. `render_esito(esito)` → avvia la vocalizazione AO2 del risultato (es. "Numero 42 trovato in: Cartella 1...")
2. `self.EndModal(wx.ID_OK)` — chiamata sincrona che **chiude il dialog istantaneamente**
3. Ritorna in `_apri_ricerca_numero`: `dlg.Destroy()` seguito da `self._pannello_griglia.SetFocus()`
4. `SetFocus()` genera un evento EVT_SET_FOCUS su `PannelloGriglia` → **NVDA annuncia il pannello** ("Griglia cartella") **interrompendo la vocalizazione AO2 in corso**

Il risultato percepito dall'utente: il dialog si chiude senza che l'utente senta l'esito della ricerca.

### Difetto secondario: routing del testo verso la finestra principale, non verso il dialog

`_wx_aggiorna_output` aggiorna `self._finestra` (la `FinestraGioco`), non il dialog:
```python
def _wx_aggiorna_output(self, testo: str) -> None:
    if self._finestra is None:
        return
    if hasattr(self._finestra, "mostra_testo"):
        self._finestra.mostra_testo(testo)
    if hasattr(self._finestra, "aggiungi_a_log"):
        self._finestra.aggiungi_a_log(testo)
```

Quindi il testo del risultato della ricerca viene scritto nel log della finestra principale, **non in nessun elemento visivo del dialog**. Il dialog si chiude senza mai mostrare il risultato al suo interno.

Il docstring del `DialogoRicercaNumero` afferma:
> "AO2 vocalizza l'esito nel dialog prima della chiusura automatica."

Questa è una precondizione non rispettata: l'esito non viene vocalizzato "nel dialog" (nel senso di un'etichetta leggibile da NVDA nel contesto del dialog), ma delegato al renderer che punta alla finestra principale.

### Conseguenze per l'utente

- Il dialog si apre, l'utente digita il numero e preme Invio.
- Il dialog si chiude.
- NVDA annuncia "Griglia cartella" (ripristino focus), cancellando il messaggio di esito che AO2 stava per vocalizzare.
- L'utente non sente né "trovato" né "non trovato".

### Fix suggeriti

**Opzione A (minimale, singolo punto di fix)**: Non chiudere il dialog automaticamente; mostrare l'esito in un'etichetta nel dialog (`wx.StaticText`) e lasciare che l'utente chiuda manualmente con Escape o Invio. NVDA leggerà l'etichetta perché il focus è ancora nel dialog.

```python
# dialogo_ricerca.py — _on_cerca: non chiamare EndModal subito dopo
# Aggiungere un wx.StaticText 'self._lbl_risultato' nel _build_ui
esito = self._comandi.cerca_numero(numero)
# vocalizazione tramite renderer
self._renderer.render_esito(esito)
# Mostra il risultato nell'etichetta del dialog (NVDA lo legge con il focus ancora aperto)
self._lbl_risultato.SetLabel(testo_risultato)
self._lbl_risultato.SetFocus()  # oppure lasciare il focus sull'input
# NON chiamare EndModal qui: l'utente chiude con Escape
```

**Opzione B (in `_apri_ricerca_numero`)**: Non chiamare `SetFocus` sul pannello griglia immediatamente dopo `Destroy`; usare `wx.CallAfter` per differire il focus al successivo ciclo di evento, **dopo** che WX ha già processato la chiusura dialog e NVDA ha già annunciato la chiusura.

```python
def _apri_ricerca_numero(self) -> None:
    dlg = DialogoRicercaNumero(...)
    dlg.ShowModal()
    dlg.Destroy()
    # Differisce il SetFocus al prossimo ciclo evento, lasciando che AO2 completi
    wx.CallAfter(self._pannello_griglia.SetFocus)
```

Nota: l'Opzione B è un workaround fragile; l'Opzione A è la soluzione strutturalmente corretta.

---

## Mappa dei file da modificare

| File | Metodo da modificare | Bug |
|------|----------------------|-----|
| `bingo_game/ui/finestra_gioco.py` | `_on_pulsante_principale` ramo `attesa_reclami` | Bug 1 |
| `bingo_game/ui/dialogo_ricerca.py` | `_build_ui`, `_on_cerca` | Bug 2 |
| `bingo_game/ui/finestra_gioco.py` | `_apri_ricerca_numero` | Bug 2 (complementare) |

---

## Priorità di intervento

| Bug | Impatto accessibilità | Complessità fix |
|-----|-----------------------|-----------------|
| Bug 1 — Ctrl+P senza feedback | Alta — blocca l'utente nella fase "sono pronto" | Bassa (aggiungere 1-2 righe di renderer) |
| Bug 2 — Ctrl+F senza feedback ricerca | Alta — rende inutilizzabile la ricerca | Media (modificare struttura dialog o differire focus) |

Entrambi i bug richiedono l'intervento di Agent-Code.  
Il Bug 2 richiede una decisione progettuale (Opzione A vs B) prima dell'implementazione: raccomandato passare da Agent-Design per conferma dell'approccio.
