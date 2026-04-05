---
type: design
feature: hotkey_ctrl_p_ctrl_f_feedback
agent: Agent-Design
status: REVIEWED
version: v0.9.5
date: 2026-04-05
report_ref: docs/4 - reports/REPORT_BUG_HOTKEY_CTRL_P_CTRL_F_2026-04-05.md
---

### Idea in 3 righe

Il design corregge due rotture di feedback da tastiera nella UI wx: Ctrl+P
deve confermare subito la registrazione del giocatore nella fase attesa_reclami,
mentre Ctrl+F deve mostrare l'esito della ricerca nel dialog senza chiuderlo.
La priorita' architetturale e' preservare un feedback immediato, lineare e
stabile per NVDA e JAWS dopo ogni azione da tastiera, senza affidarsi a
vocalizzazioni asincrone che possono essere interrotte dal cambio di focus.
Per la ricerca numeri viene adottata la soluzione strutturale scelta
dall'utente: dialog persistente, feedback visivo interno al dialog e chiusura
solo esplicita da parte dell'utente.

### Attori e Concetti

#### Attori

- FinestraGioco, che intercetta le hotkey Ctrl+P e Ctrl+F e governa il focus
  della sessione di gioco.
- DialogoRicercaNumero, che raccoglie l'input del numero, presenta l'esito
  della ricerca e rimane il contenitore attivo finche' l'utente non decide di
  chiuderlo.
- WxRenderer, che continua a essere il punto di emissione del testo verso log,
  widget e vocalizzazione AO2.
- ComandiGiocatoreUmano e comandi di ricerca, che eseguono l'azione applicativa
  senza inglobare logica di presentazione.
- NVDA, JAWS e AO2, che costituiscono il canale di feedback accessibile e
  impongono sincronizzazione corretta tra testo mostrato, focus e annuncio.

#### Concetti

- Feedback immediato: ogni scorciatoia da tastiera deve produrre un riscontro
  percepibile subito dopo l'azione, anche quando il turno non puo' ancora
  avanzare o il dialog rimane aperto.
- Conferma di stato locale: il messaggio di conferma deve descrivere cosa e'
  successo all'azione appena richiesta, non solo lo stato globale della partita.
- Dialog persistente: il risultato della ricerca resta nel contesto del dialog,
  cosi' il focus non rientra prematuramente nella finestra principale.
- Race condition TTS-focus: una vocalizzazione asincrona perde affidabilita' se
  il focus cambia subito dopo l'avvio della sintesi o se il contenitore UI viene
  distrutto.
- Separazione dei ruoli: la logica applicativa conferma l'esito dell'azione,
  mentre la presentazione decide come renderlo in forma testuale e accessibile.

### Flussi Concettuali

#### Flusso 1 - Ctrl+P durante attesa_reclami

1. L'utente preme Ctrl+P mentre la UI e' nella fase attesa_reclami.
2. FinestraGioco delega la dichiarazione di fine turno al percorso applicativo
   corretto, evitando accessi diretti non necessari all'oggetto giocatore.
3. Subito dopo l'azione, la UI emette un messaggio locale e accessibile del tipo
   "Turno dichiarato concluso. Attendo gli altri giocatori.".
4. Se il giocatore aveva gia' dichiarato la fine turno, la UI emette un feedback
   esplicito idempotente, senza restare silenziosa.
5. Solo dopo la conferma locale viene rieseguito il controllo tutti_pronti,
   cosi' il feedback non dipende dalla tempistica dei bot o da esiti silenziosi.

#### Flusso 2 - Ctrl+F con dialog di ricerca persistente

1. L'utente preme Ctrl+F e il dialog di ricerca si apre nel contesto modale
   corrente.
2. L'utente inserisce il numero e conferma la ricerca.
3. Il comando restituisce l'esito applicativo e il dialog aggiorna un'area di
   feedback interna con il testo trovato o non trovato.
4. Il renderer puo' ancora vocalizzare l'esito, ma il dialog resta aperto e il
   focus non torna subito alla griglia di gioco.
5. L'utente legge o riascolta l'esito restando nel dialog, poi decide quando
   chiudere con un'azione esplicita come Escape o pulsante dedicato.

#### Flusso 3 - chiusura del dialog e ripristino focus

1. La chiusura del dialog non avviene piu' automaticamente dopo la ricerca.
2. Quando l'utente chiude il dialog, la finestra principale ripristina il focus
   sulla griglia solo come ultimo passo del flusso.
3. Il ripristino focus non compete piu' con la lettura dell'esito, perche'
   l'esito e' gia' presente nel dialog e non dipende da una finestra distrutta.
4. Il principio architetturale e' che il focus cambia solo dopo che il contesto
   informativo corrente e' stato reso disponibile all'utente.

### Decisioni Architetturali

1. Ctrl+P in attesa_reclami viene trattato come azione a conferma immediata,
   distinta dal controllo globale del turno. Il feedback locale e' obbligatorio
   anche quando la partita non puo' avanzare perche' altri giocatori non sono
   ancora pronti.
2. La dichiarazione di fine turno deve passare dal boundary applicativo gia'
   previsto, invece di manipolare direttamente il giocatore umano nella UI. Il
   motivo e' ridurre accoppiamento presentation-domain e mantenere la UI centrata
   sul feedback, non sulla mutazione dello stato interno.
3. Il fix di Ctrl+F adotta la soluzione strutturale e non il workaround basato
   sul ritardo del focus. Differire SetFocus o Destroy attenuerebbe il sintomo,
   ma lascerebbe intatto il problema di fondo: l'esito dipende oggi da una
   vocalizzazione asincrona lanciata fuori dal contesto informativo del dialog.
4. DialogoRicercaNumero deve introdurre un elemento di output interno stabile,
   leggibile da screen reader e aggiornabile a ogni ricerca successiva. Il dialog
   diventa quindi una micro-superficie di consultazione, non un contenitore usa
   e chiudi.
5. Il renderer wx mantiene l'ordine semantico testo -> aggiornamento UI ->
   vocalizzazione, ma per la ricerca numeri l'aggiornamento principale avviene nel
   dialog e non solo nel log della finestra madre. Questo evita che il feedback
   sia presente in un punto invisibile al focus corrente.
6. Il principio di accessibilita' vincolante e' uno solo per entrambi i bug:
   nessuna azione da tastiera puo' concludersi nel silenzio. Se l'azione e'
   valida, l'utente deve ricevere una conferma immediata; se l'azione e' gia'
   stata eseguita o non produce avanzamento, l'utente deve ricevere un messaggio
   esplicativo altrettanto immediato.
7. Il design resta confinato al layer di presentation e al suo boundary
   applicativo: non introduce nuove regole di dominio, ma stabilizza il contratto
   di feedback tra hotkey, dialog, renderer e screen reader.

### Rischi e Vincoli

- Vincolo NVDA/JAWS: i messaggi devono essere lineari, brevi e collocati nel
  controllo o contesto che mantiene il focus, altrimenti il lettore di schermo
  puo' annunciare un altro elemento e mascherare l'esito reale.
- Vincolo di feedback immediato: Ctrl+P e Ctrl+F non possono dipendere da
  condizioni asincrone esterne per confermare l'azione. Il riscontro minimo deve
  essere disponibile subito, anche se il flusso complessivo prosegue dopo.
- Rischio di duplicazione annunci: se il dialog mostra il testo e il renderer lo
  vocalizza anche nel log principale, occorre evitare doppie letture confuse o
  messaggi ridondanti non coordinati.
- Rischio di regressione UX: mantenere il dialog aperto richiede comandi di
  chiusura espliciti, etichette chiare e ordine di tab coerente, altrimenti la
  ricerca migliora l'audibilita' ma peggiora la navigazione.
- Vincolo di scope: questo documento definisce la decisione architetturale per
  la correzione hotkey in v0.9.5. Non introduce PLAN, TODO per-feature o cambi
  extra-scope fuori dal design e dall'aggiornamento del coordinatore docs.
- Rischio di coerenza implementativa: il fix di Ctrl+P e quello di Ctrl+F devono
  convergere sullo stesso principio progettuale. Se uno usa feedback locale e
  l'altro continua a dipendere dal log remoto o da focus differito, il contratto
  accessibile delle hotkey restera' incoerente.