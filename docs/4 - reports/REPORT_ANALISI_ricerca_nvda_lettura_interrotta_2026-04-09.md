---
title: Analisi - NVDA non riesce a leggere il risultato della ricerca
status: FINAL
data: 2026-04-09
agente: Agent-Analyze
scope: bingo_game/ui/dialogo_ricerca.py, bingo_game/ui/finestra_gioco.py
---

# Analisi: NVDA non legge il risultato della ricerca prima della chiusura del dialog

## Problema segnalato

Dopo aver cercato un numero con Ctrl+F, il dialog si chiude prima che NVDA
abbia il tempo di leggere il messaggio con i risultati della ricerca.
L'utente torna alla griglia senza aver sentito dove si trova il numero.

## File coinvolti

- `bingo_game/ui/dialogo_ricerca.py` - metodo `_on_cerca()`, righe 108-137
- `bingo_game/ui/finestra_gioco.py` - metodo `_apri_ricerca_numero()`, righe 610-625
- `bingo_game/ui/finestra_gioco.py` - metodo `_naviga_a_risultato_ricerca()`, righe 626-632
- `bingo_game/ui/renderers/renderer_wx.py` - metodo `_handle_ricerca_numero_in_cartelle()`, righe 569-588
- `bingo_game/ui/renderers/renderer_wx.py` - metodo `_ao2_vocalizza()`, riga 721
- `my_lib/vocalizzatore.py` - metodo `vocalizza_testo()`, righe 87-99

## Flusso attuale (sequenza temporale)

1. L'utente preme Ctrl+F: si apre `DialogoRicercaNumero` come dialog modale
2. L'utente digita un numero e preme Invio
3. `_on_cerca()` chiama `self._comandi.cerca_numero(numero)` e ottiene un `EsitoAzione`
4. `self._renderer.render_esito(esito)` viene chiamato, che dispatcha a
   `_handle_ricerca_numero_in_cartelle(evento)`
5. Il handler costruisce un testo multi-riga, es:
   "Numero 42 trovato in: Cartella 1, riga 2, colonna 3 (non segnato)."
6. Chiama `_ao2_vocalizza(testo)` che invoca `self._backend.speak(testo, interrupt=False)`
7. NVDA inizia a leggere il messaggio
8. Il testo viene anche scritto nella label `_lbl_risultato` del dialog
9. `wx.CallLater(ritardo_ms, self.EndModal, wx.ID_OK)` viene schedulato con:
   `ritardo_ms = 400 + max(0, len(risultati) - 1) * 200`
   - 1 risultato: 400ms
   - 2 risultati: 600ms
   - 3 risultati: 800ms
10. Dopo il delay: `EndModal(wx.ID_OK)` chiude il dialog modale
11. Il focus ritorna a `FinestraGioco`
12. `_naviga_a_risultato_ricerca()` invia 3 comandi di navigazione sincroni,
    ognuno dei quali vocalizza tramite `_ao2_vocalizza`:
    - "Cartella N selezionata."
    - Riga avanzata (celle della riga)
    - Colonna avanzata (celle della colonna)

## Causa radice: due problemi concatenati

### Problema 1 - Il delay e' troppo breve

Il delay attuale (400ms per un singolo risultato) e' basato sul numero
di risultati, non sulla lunghezza del testo da leggere.

Un messaggio tipico come:
"Numero 42 trovato in: Cartella 1, riga 2, colonna 3 (non segnato)."
contiene circa 12-15 parole.

NVDA a velocita' standard legge circa 150-200 parole al minuto
(2.5-3.3 parole/secondo). Per 15 parole servono circa 4.5-6 secondi.

400ms copre meno di una parola.

Con piu' risultati il messaggio si allunga, ma l'incremento di 200ms per
risultato aggiuntivo resta insufficiente per il testo aggiuntivo di
ciascuna riga di dettaglio.

### Problema 2 - La chiusura del dialog modale interrompe NVDA

Quando `EndModal()` viene chiamato:
- wxPython chiude il loop modale del dialog
- Il focus si sposta dal dialog al frame padre (`FinestraGioco`)
- NVDA rileva il cambio di focus e interrompe la speech corrente per
  annunciare l'elemento che riceve il focus
- Immediatamente dopo, `_naviga_a_risultato_ricerca()` invia 3 comandi
  che producono altrettante vocalizzazioni

Risultato: anche con un delay piu' lungo, se non e' sufficiente a
coprire l'intero tempo di lettura NVDA, la speech verra' comunque
interrotta dalla chiusura del dialog. I comandi di navigazione
successivi sovrascrivono qualsiasi residuo del messaggio originale.

## Dettaglio tecnico: la vocalizzazione non usa interrupt

`_ao2_vocalizza()` chiama `vocalizza_testo(testo)` senza `interrompi=True`,
quindi usa `interrupt=False` di default. Questo significa che le chiamate
successive al backend TTS si accodano nel buffer NVDA.

Tuttavia, quando un dialog modale si chiude, e' NVDA stesso (non il codice)
che interrompe la speech in corso per annunciare il cambio di focus.
Il `interrupt=False` nel codice e' quindi irrilevante rispetto a questo evento.

## Soluzioni proposte

### Opzione A - Delay calcolato sulla lunghezza del testo

Sostituire la formula del delay con una basata sul numero di parole:

```python
parole = len(testo_risultato.split())
ritardo_ms = max(3000, int(parole / 2.5 * 1000)) + 1000
```

- Pro: semplice da implementare, nessun cambio UX
- Con: la velocita' NVDA varia per utente (chi usa velocita' alta
  aspettera' troppo, chi usa velocita' bassa potrebbe non bastare).
  Non elimina il problema 2 se il delay e' sottostimato.

### Opzione B - Conferma esplicita tramite Invio per navigare al risultato

Quando il risultato e' "trovato":
- NVDA vocalizza il risultato normalmente
- Il dialog rimane aperto (nessun timer di auto-chiusura)
- Il focus va sul pulsante "Cerca" oppure su un nuovo pulsante "Vai al risultato"
- L'utente preme Invio per chiudere il dialog e navigare alla cella trovata
- Se l'utente preme Escape, torna alla griglia senza navigazione

- Pro: NVDA legge tutto senza interruzione, l'utente decide quando procedere
- Con: richiede un tasto in piu' (Invio) rispetto alla chiusura automatica.
  Pero' e' un solo tasto, piu' naturale di ESC+navigazione manuale.

### Opzione C - Chiusura silenziosa del dialog + ri-vocalizzazione post-navigazione

Il dialog si chiude immediatamente (nessun delay o delay minimo), la
navigazione avviene, e dopo la navigazione il messaggio di ricerca viene
ri-vocalizzato integralmente.

Sequenza percepita dall'utente:
1. "Cartella 1 selezionata."
2. "Avanzata riga 2, ..."
3. "Avanzata colonna 3, ..."
4. "Numero 42 trovato in: Cartella 1, riga 2, colonna 3 (non segnato)."

- Pro: navigazione immediata, il messaggio completo viene sempre letto
- Con: ordine invertito (prima la posizione, poi il risultato).
  L'utente potrebbe trovare confusa la sequenza.

### Opzione D - Delay lungo + skip su tasto utente

Usare un delay conservativo (es. 8-10 secondi), ma permettere all'utente
di premere Invio o Escape per saltare l'attesa e procedere subito.

- Invio: chiude il dialog e naviga al risultato (come auto-chiusura)
- Escape: chiude il dialog senza navigare
- Se nessun tasto viene premuto: il dialog si chiude automaticamente dopo il delay

- Pro: garantisce tempo sufficiente per la lettura, l'utente non e' bloccato
- Con: complessita' implementativa media (serve gestire l'interazione
  durante il countdown).

### Opzione E - Pulsante "Vai al risultato" con focus automatico

Variante della Opzione B. Dopo un risultato trovato:
- Il testo dell'attuale pulsante "Cerca" cambia in "Vai al risultato"
  oppure viene aggiunto un pulsante dedicato
- Il focus si sposta su questo pulsante dopo la vocalizzazione
- Invio sul pulsante chiude il dialog e naviga
- Il pulsante "Cerca" torna disponibile se l'utente vuole cercare un altro numero

- Pro: flusso naturale (ascolta risultato, premi Invio per andare),
  compatibile con qualsiasi velocita' NVDA
- Con: modifica alla UI del dialog (aggiunta/modifica pulsante).

## Confronto sintetico

- Opzione A: rischio residuo (delay potrebbe non bastare), nessun cambio UX
- Opzione B: soluzione piu' sicura, un solo tasto extra (Invio)
- Opzione C: navigazione rapida, ordine lettura invertito
- Opzione D: buon compromesso automatismo/controllo, complessita' media
- Opzione E: UX piu' pulita, complessita' implementativa leggermente superiore

## Raccomandazione

**Opzione B** oppure **Opzione E**, entrambe eliminano il problema alla
radice: non c'e' timer da stimare, e' l'utente a decidere quando ha finito
di ascoltare.

La differenza tra B e E e' solo cosmetica:
- B riusa il pulsante "Cerca" come target per Invio
- E aggiunge un pulsante "Vai" dedicato

In entrambi i casi il flusso percepito e':
1. Ctrl+F, digita numero, Invio
2. NVDA legge il risultato
3. L'utente preme Invio per andare al risultato

In alternativa, **Opzione D** e' un buon compromesso se si preferisce
mantenere la chiusura automatica: il delay lungo garantisce la lettura,
e lo skip su tasto elimina l'attesa per chi ha gia' sentito.
