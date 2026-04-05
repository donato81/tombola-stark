---
type: design
feature: ciclo_turno_fasi_reclami_collettivi
agent: Agent-Design
status: REVIEWED
version: v0.9.5
date: 2026-04-01
report_ref: docs/4 - reports/REPORT_FATTIBILITA_FASI_TURNO_2026-04-01.md
---

### Idea in 3 righe

La feature separa il turno di gioco in due fasi esplicite: estrazione del numero
e finestra di verifica collettiva dei reclami prima della chiusura del turno.
L'obiettivo e' rimettere umano e bot nella stessa finestra temporale, cosi' da
rendere equa la validazione dei premi e compatibile il flusso con NVDA.
Il design blocca il bordo architetturale tra dominio, controller e renderer wx,
inclusa la correzione di verifica_premi per supportare co-vincite nello stesso turno.

### Attori e Concetti

#### Attori

- Partita, che governa stato del turno, raccolta reclami e assegnazione premi.
- GameController e ComandiSistema, che espongono le due fasi come operazioni
  sicure e compatibili con il flusso esistente.
- FinestraGioco, che orchestra l'interazione utente e rende esplicita la fase UI.
- BaseRenderer e WxRenderer, che devono annunciare numero, fase e premi come
  messaggi distinti e coerenti con la presentazione wx.
- GiocatoreUmano e GiocatoreAutomatico, che partecipano alla stessa finestra di
  reclamo dopo l'estrazione del numero.
- NVDA/AO2, che costituiscono il canale primario di feedback accessibile.

#### Concetti

- Fase di estrazione: produce il numero del turno, aggiorna i giocatori e apre
  la finestra temporale in cui i reclami restano ancora modificabili.
- Fase di reclami collettivi: bot e umano convergono nello stesso turno logico,
  prima della validazione definitiva dei premi.
- Fase UI esplicita: la finestra non inferisce piu' il turno solo dal contatore,
  ma espone uno stato dedicato per decidere cosa fa il pulsante principale.
- Verifica a due passate: i candidati vengono prima raccolti per tipo premio e
  poi assegnati insieme, evitando che il primo giocatore nell'ordine di lista
  chiuda il premio a scapito di una co-vincita valida nello stesso turno.
- Annuncio atomico: numero estratto, invito alla dichiarazione, verifica e premi
  sono eventi separati sia per log sia per vocalizzazione.

### Flussi Concettuali

#### Flusso 1 - avvio fase estrazione

1. L'utente attiva il pulsante principale quando la UI e' in attesa di
   estrazione.
2. Il controller esegue la sola fase di estrazione e restituisce il numero
   estratto e lo stato aggiornato del turno.
3. La UI annuncia il numero in modo separato dai premi, aggiorna il log e porta
   il proprio stato in attesa reclami.
4. Il pulsante principale cambia semantica da azione di avanzamento turno a
   conferma di fine valutazione, con annuncio esplicito compatibile con NVDA.

#### Flusso 2 - finestra reclami collettivi

1. Dopo l'estrazione, i bot valutano il numero appena segnato nello stesso turno
   logico in cui anche l'umano puo' ancora dichiarare il proprio reclamo.
2. L'umano dispone di una finestra esplicita per confermare eventuali vincite,
   senza dover anticipare la decisione prima di conoscere il numero estratto.
3. Finche' la UI resta nella fase reclami, il turno non viene chiuso e la
   verifica definitiva non parte.

#### Flusso 3 - verifica e assegnazione premi

1. L'utente attiva di nuovo il pulsante principale per dichiarare conclusa la
   fase reclami.
2. Il controller esegue la fase di verifica, che raccoglie prima tutti i
   candidati validi per tipo premio e poi assegna insieme i premi co-vinti.
3. Il sistema produce esiti distinti per premi nuovi, reclami bot confermati e
   controllo tombola.
4. Solo al termine vengono resettati i reclami del turno e la UI torna in
   attesa di una nuova estrazione.

#### Flusso 4 - annuncio accessibile del turno

1. La UI o il renderer annunciano prima il numero estratto.
2. Viene poi annunciata la fase corrente, per esempio con un messaggio del tipo
   "Numero estratto. Dichiara la tua vittoria.".
3. Alla chiusura della finestra reclami, il renderer annuncia separatamente
   l'avvio della verifica e l'esito finale dei premi del turno.
4. Ogni annuncio viene scritto nel log consultabile e vocalizzato senza
   sottrarre il focus alla superficie di gioco.

### Decisioni Architetturali

1. Il turno viene modellato come flusso bifasico esplicito, con almeno due
   stati stabili: attesa estrazione e attesa reclami. La chiusura del turno e'
   una conseguenza della fase di verifica, non un'azione implicita dell'estrazione.
2. Partita espone due operazioni pubbliche distinte, una per l'estrazione e una
   per la verifica, mentre il wrapper monolitico resta solo come compatibilita'
   transitoria verso codice e test esistenti.
3. verifica_premi deve essere corretta alla radice con una strategia a due
   passate, cosi' da supportare co-vincite nello stesso turno e rimuovere il
   bias dell'ordine di iterazione dei giocatori.
4. FinestraGioco introduce uno stato UI esplicito del turno. Il pulsante
   principale diventa contestuale: prima estrae, poi conferma la fine della
   finestra reclami e avvia la verifica.
5. BaseRenderer estende il contratto oltre il semplice messaggio generico,
   includendo annunci distinti per numero estratto, fase del turno e premi.
   Questo impedisce di comprimere numero e premi in un'unica stringa opaca.
6. WxRenderer mantiene l'ordine testo -> aggiornamento widget/log ->
   vocalizzazione AO2, ma con metodi atomici separati per ciascun momento del
   turno. In questo modo il log conserva una cronologia leggibile anche in caso
   di doppio annuncio nello stesso turno.
7. Il cambio di etichetta del pulsante in finestra_gioco non viene considerato
   sufficiente come notifica accessibile. Dopo ogni SetLabel occorre un annuncio
   esplicito della nuova fase, perche' NVDA non garantisce la rilettura del nome
   del controllo se il focus non si trova gia' sul pulsante.
8. L'impatto di presentazione e' confinato a finestra_gioco, base_renderer e
   renderer_wx: la finestra decide il ramo contestuale, il contratto renderer
   dichiara le nuove primitive e l'implementazione wx realizza gli annunci e gli
   aggiornamenti del log coerenti con la nuova sequenza.

### Rischi e Vincoli

- Vincolo di accessibilita': il flusso deve restare completabile solo da
  tastiera, con annunci lineari, nessun timeout implicito e compatibilita'
  esplicita con NVDA su Windows.
- Vincolo di simmetria di gioco: bot e umano devono reclamare nello stesso
  intervallo logico successivo all'estrazione, altrimenti la separazione in fasi
  non risolve l'asimmetria evidenziata dal report.
- Rischio di regressione contrattuale: il passaggio da un renderer basato su
  messaggio generico a primitive piu' specifiche richiede coerenza stretta tra
  finestra_gioco, base_renderer e renderer_wx per evitare annunci mancanti o
  duplicati.
- Rischio di stato incoerente: senza un flag di fase esplicito nella UI e nel
  dominio, il doppio click o la ripetizione rapida del comando principale puo'
  saltare direttamente alla verifica o chiudere il turno in modo ambiguo.
- Vincolo di backward compatibility: il percorso monolitico esistente deve poter
  sopravvivere durante la transizione, almeno come wrapper compatibile, per non
  rompere subito il comportamento corrente e la base test esistente.
- Rischio di memoria degli annunci: se il renderer conserva solo l'ultimo testo,
  la ripetizione vocale potrebbe restituire solo l'ultimo esito premi e non
  l'intera sequenza del turno. Questo va considerato in fase successiva, pur non
  bloccando il design corrente.
- Vincolo di perimetro: questa fase produce solo il documento DESIGN e l'indice
  coordinatore. Nessun PLAN, TODO per-feature o modifica ai file Python rientra
  nello scope corrente.