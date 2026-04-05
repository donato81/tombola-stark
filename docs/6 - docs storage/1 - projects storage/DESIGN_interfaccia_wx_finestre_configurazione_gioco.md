---
feature: interfaccia_wx_finestre_configurazione_gioco
type: design
agent: Agent-Design
status: REVIEWED
version: v0.9.5
date: 2026-03-31
---

### Idea in 3 righe

La feature introduce un primo perimetro wxPython accessibile limitato a due
finestre: configurazione partita e gioco principale. L'obiettivo non e' ancora
coprire l'intera esperienza grafica, ma fissare il bordo architetturale tra
motore di gioco, renderer wx e navigazione da tastiera NVDA-first.
Le decisioni qui definite derivano dal report di analisi esistente e bloccano
solo cio' che serve per avviare la progettazione successiva senza includere
impostazioni avanzate o modalita' cartelle affiancate.

### Attori e Concetti

#### Attori

- Giocatore umano, che usa tastiera e screen reader come canale primario.
- GameController e ComandiSistema, che governano creazione partita e turni.
- GiocatoreUmano, che espone le azioni gia' coperte dal dominio durante il gioco.
- WxRenderer, che applica gli eventi del motore ai widget e alla vocalizzazione.
- Vocalizzatore/AO2, che annuncia stato e aggiornamenti senza sottrarre focus.

#### Concetti

- Finestra di configurazione: raccoglie nome giocatore, numero bot,
  numero cartelle e conferma avvio partita.
- Finestra di gioco principale: ospita area partita, pulsante di azione
  principale, log consultabile e superficie di navigazione cartella.
- Focus preservation: ogni transizione o dialogo deve restituire il focus al
  punto logico precedente, in modo coerente con NVDA.
- Tastiera come interfaccia primaria: nessuna azione critica dipende dal mouse.
- Scope esplicito: fuori perimetro in questa fase sono finestra iniziale
  separata, impostazioni avanzate, cartelle affiancate e rifiniture visive.

### Flussi Concettuali

#### Flusso 1 - configurazione partita

1. L'utente apre la finestra di configurazione e il focus atterra sul primo
   controllo utile all'inserimento.
2. La finestra presenta in sequenza guidata i campi minimi: nome giocatore,
   numero bot, numero cartelle, conferma.
3. Ogni variazione valida o errore di input viene resa in testo e voce tramite
   il renderer, senza introdurre logiche di dominio nella finestra.
4. Alla conferma, la UI delega a ComandiSistema la creazione della partita e,
   in caso di esito valido, apre la finestra di gioco principale.

#### Flusso 2 - ingresso nella finestra di gioco

1. La finestra di gioco viene aperta con titolo semantico e focus iniziale
   posizionato sull'area griglia/cartella.
2. NVDA annuncia il cambio finestra tramite il titolo del frame e il renderer
   completa l'ingresso con il primo messaggio contestuale di stato partita.
3. Il pulsante principale espone stato dinamico: prima "Inizia partita",
   poi "Passa turno" dopo la prima estrazione.

#### Flusso 3 - ciclo di gioco principale

1. L'utente usa i tasti gia' mappati nel dominio per navigazione cartella,
   righe, colonne, segnazione, consultazione e reclami.
2. Il controller produce esiti/eventi; WxRenderer li smista ai widget e alla
   voce mantenendo ordine coerente degli annunci.
3. Gli eventi automatici dei bot vengono vocalizzati e registrati nel log
   consultabile senza spostare il focus dell'utente.

#### Flusso 4 - ricerca e consultazione contestuale

1. Dalla finestra di gioco l'utente puo' invocare i comandi di consultazione
   previsti dal report, inclusa la ricerca numero con dialogo modale.
2. Il dialogo si apre focalizzato sul controllo corretto, restituisce l'esito,
   si chiude e ripristina il focus logico nella finestra chiamante.
3. Nessun dialogo di questa fase introduce preferenze avanzate permanenti.

### Decisioni Architetturali

1. Il perimetro documentale iniziale copre soltanto due frame wx dedicati:
   finestra di configurazione e finestra di gioco principale.
2. La finestra di configurazione resta un bordo di presentazione: valida il
   minimo necessario lato UI ma delega creazione partita e stato al layer
   applicativo gia' esistente.
3. La finestra di gioco usa un pannello griglia focalizzabile come centro di
   input tastiera, con Escape per uscire dalla griglia e Tab per rientrare.
4. Il pulsante principale adotta un modello a due stati derivato dallo stato
   della partita, senza introdurre un nuovo flag di dominio dedicato.
5. Il renderer wx mantiene la separazione tra aggiornamento widget e
   vocalizzazione AO2, cosi' gli annunci dei bot non sottraggono mai il focus.
6. I binding tastiera si basano sulla matrice del report: binding normali per
   la griglia, binding forti di finestra per i comandi globali, e verifica
   empirica successiva per i tasti a rischio intercettazione NVDA.
7. Il log annunci e' parte della finestra di gioco principale come supporto
   consultabile, non come canale di input primario.
8. Restano esplicitamente fuori scope impostazioni avanzate, gestione grafica
   delle cartelle affiancate, styling visuale definitivo e eventuale finestra
   iniziale autonoma di bootstrap.

### Rischi e Vincoli

- Vincolo accessibilita': ogni flusso deve essere completabile solo da tastiera,
  con output lineare e compatibile con NVDA/JAWS su Windows.
- Vincolo architetturale: la UI non deve spostare logica di gioco nel layer wx;
  il dominio resta invariato e la presentazione reagisce agli esiti.
- Rischio binding: alcuni shortcut globali indicati dal report possono essere
  intercettati da NVDA o wx e richiedono validazione empirica prima del freeze.
- Rischio stato renderer: funzionalita' come ripetizione ultimo annuncio e log
  consultabile richiedono stato locale controllato nel renderer.
- Vincolo di scope: nessuna estensione a impostazioni avanzate, cartelle
  affiancate o altri frame deve entrare in questa prima fase documentale.
- Vincolo temporale di progetto: il design deve restare coerente con la
  versione v0.9.5 e con il report sorgente del 2026-03-31.