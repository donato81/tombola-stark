# DESIGN 01 — Fase 1: Infrastructure Layer e Persistenza Locale

> **Data**: 15 aprile 2026
> **Versione target**: v0.15.x
> **Tipo documento**: Design di fase
> **Fase roadmap**: 1 di 9
> **Dipende da**: nessuna fase precedente
> **Sblocca**: Fase 2, Fase 4, Fase 6
> **Documento padre**: DESIGN_COSTITUZIONE_ROADMAP_MULTIPLAYER_2026-04-14.md
> **Stato**: BOZZA
> **Autore analisi**: Agent-Analyze

---

## 1. Scopo e confini di questa fase

Questa fase costruisce il layer Infrastructure del progetto, che alla versione v0.14.0-alpha non esiste. Alla data odierna nessun file nel repository esegue persistenza su disco, autenticazione, comunicazione di rete né gestione audio strutturata come servizio. La cartella `bingo_game/infrastructure/` è assente. Questa fase la crea da zero.

Lo scopo concreto è triplice. Primo: introdurre un database SQLite locale tramite il modulo standard `sqlite3`, con uno schema iniziale composto da quattro tabelle (`utenti`, `partite`, `statistiche`, `crediti_log`). Secondo: definire quattro interfacce astratte ABC (`PartitaRepository`, `UtenteRepository`, `StatisticheRepository`, `CreditiRepository`) che fungono da contratto stabile tra il layer Application/Controller e il layer Infrastructure. Terzo: fornire le implementazioni concrete SQLite di ciascuna interfaccia, coperte da test unitari.

Questa fase viene costruita prima di tutte le altre per una ragione strutturale precisa: è la fondazione su cui poggiano la Fase 2 (sistema utente, che consuma `UtenteRepository`), la Fase 4 (salvataggio partite, che consuma `PartitaRepository`), la Fase 5 (crediti virtuali, che consuma `CreditiRepository`) e la Fase 6 (sound effects, che ha bisogno della persistenza per l'opzione ON/OFF). Senza le interfacce ABC e le implementazioni SQLite di questa fase, nessuna delle fasi successive può iniziare. La mappa delle dipendenze nella Costituzione conferma che la Fase 1 non dipende da nessuna fase precedente e sblocca Fase 2, Fase 4 e Fase 6.

Cosa questa fase NON fa. Non introduce il modello `Utente` nel Dominio: quello è compito della Fase 2. Non implementa il salvataggio dello stato di una partita in corso: quello è compito della Fase 4. Non implementa la logica dei crediti virtuali: quello è compito della Fase 5. Non tocca il layer Presentazione: nessuna finestra wxPython viene creata né modificata. Non modifica il file `main.py`. Non introduce librerie esterne: `sqlite3` è parte della standard library Python 3.11.

I layer toccati, come indicato dalla Costituzione, sono due. Il layer Infrastructure viene creato ex novo con la cartella `bingo_game/infrastructure/`, le interfacce ABC e le implementazioni SQLite. Il layer Controller (`bingo_game/game_controller.py`) viene aggiornato per accettare i repository come dipendenze iniettate, senza modificare la logica di orchestrazione esistente.

I layer NON toccati sono il Dominio (nessun file in `bingo_game/` fuori da `infrastructure/` può essere modificato per dipendere dall'Infrastructure, come impone il Vincolo 2 della Costituzione) e la Presentazione (nessuna finestra wx viene toccata, come impone il contratto in uscita della Fase 1).

---

## 2. Analisi del punto di innesto nel codice esistente

### Metodi del Controller che terminano o modificano lo stato del gioco

Partendo dalla lettura diretta di `game_controller.py`, i metodi che oggi terminano una partita o modificano lo stato del gioco in modo rilevante per la futura persistenza sono i seguenti.

Il metodo `esegui_turno_sicuro` esegue un turno completo e, quando rileva una tombola o l'esaurimento dei numeri, registra nel log il riepilogo finale tramite `_log_game_summary`. Questo è il punto in cui domani si dovrà invocare il salvataggio delle statistiche di partita e l'aggiornamento dei crediti. Lo si riconosce dai blocchi condizionali che verificano `risultato_turno.get("tombola_rilevata")` e `risultato_turno.get("partita_terminata")`.

Il metodo `esegui_fase_verifica_sicura` è la versione bifasica dello stesso scenario: al termine della fase di verifica, se `risultato.get("tombola_rilevata")` o `risultato.get("partita_terminata")` sono veri, viene chiamato `_log_game_summary`. Anche questo metodo è un punto di innesto naturale per la persistenza.

Il metodo `partita_terminata` è un sensore di stato che verifica se la partita è nello stato "terminata". Il suo flag `_partita_terminata_logged` evita log duplicati. Domani questo punto sarà il luogo naturale per invocare il salvataggio finale (una volta sola, coerentemente con il pattern esistente del flag).

Il metodo `crea_partita_standard` resetta lo stato di sessione (`_turno_corrente`, `_partita_terminata_logged`). Domani questo sarà il punto in cui creare il record iniziale nella tabella `partite`, registrando la configurazione della nuova partita.

Nel file `comandi_partita.py`, il metodo `ComandiSistema.termina_partita` chiama `partita.termina_partita()` e restituisce un booleano. Questo metodo è il punto in cui la Presentazione richiede la terminazione forzata: è un ulteriore innesto per il salvataggio.

### Momento naturale per inizializzare la connessione al database

Il ciclo di vita dell'applicazione parte da `main.py`. La sequenza osservata è: parsing argomenti, inizializzazione `GameLogger`, creazione dell'istanza `wx.App`, creazione del `Vocalizzatore`, costruzione manuale del `WxRenderer`, creazione della `FinestraPrincipale` con il renderer iniettato, `Show` e `MainLoop`. Alla chiusura, il blocco `finally` chiama `GameLogger.shutdown()`.

Il momento naturale per inizializzare la connessione al database è dopo l'inizializzazione del `GameLogger` e prima della creazione della `FinestraPrincipale`. Tuttavia, la Costituzione stabilisce che `main.py` non viene modificato in Fase 1. Questo significa che l'inizializzazione del database dovrà avvenire al momento della prima richiesta effettiva — ovvero quando il Controller viene istanziato o quando viene creata la prima partita. Il componente `db_manager` sarà progettato per supportare l'inizializzazione differita: la connessione viene aperta la prima volta che un repository la richiede, non al momento dell'import del modulo.

### Dependency injection nel Controller attuale

Il Controller attuale, `game_controller.py`, non usa dependency injection per nulla. Tutte le funzioni sono a livello di modulo (non metodi di una classe). La funzione `crea_partita_standard` istanzia direttamente `Tabellone`, `GiocatoreUmano`, `GiocatoreAutomatico` e `Partita`. Non riceve alcuna factory, alcun repository, alcun servizio dall'esterno.

L'unico punto in cui esiste dependency injection nel progetto è nella Presentazione: il `WxRenderer` riceve la finestra e il vocalizzatore come argomenti, e la `FinestraPrincipale` riceve il renderer. Ma nel Controller questo pattern non esiste.

Il `ComandiSistema` in `comandi_partita.py` è una classe, ma non riceve dipendenze nel costruttore: è stateless e delega tutto a funzioni di modulo di `game_controller.py`. Il `ComandiGiocatoreUmano` riceve la `Partita` nel costruttore, ma non riceve repository né servizi.

La dependency injection per i repository dovrà essere introdotta. La sezione 6 descrive come.

### Dati sufficienti e dati mancanti per la persistenza

Il metodo `get_stato_completo` di `Partita` restituisce un dizionario con le seguenti chiavi: `stato_partita` (stringa), `ultimo_numero_estratto` (intero o None), `numeri_estratti` (lista di interi), `numeri_mancanti` (lista di interi), `giocatori` (lista di dizionari con stato per giocatore), `premi_gia_assegnati` (lista ordinata di chiavi stringa), `conteggio_giocatori` (intero).

L'attributo `storico_premi` di `Partita` è una lista di dizionari, ciascuno con chiavi: `giocatore` (nome stringa), `id_giocatore` (intero), `cartella` (indice intero), `premio` (tipo stringa), `riga` (indice intero o None), `turno` (intero).

I dati sufficienti per la persistenza in Fase 1 sono: il nome del giocatore umano (già presente in `GiocatoreBase.nome`), il numero di bot (derivabile da `conteggio_giocatori` meno uno), il numero di cartelle (derivabile da `GiocatoreBase.get_numero_cartelle()`), lo storico dei premi, lo stato finale della partita, il conteggio dei turni giocati (derivabile dalla lunghezza di `numeri_estratti`), e l'informazione sulla tombola (derivabile da `has_tombola`).

I dati che mancano ancora sono: l'identità persistente dell'utente (non esiste un modello `Utente` con id, email, password_hash — questo arriverà in Fase 2), il timestamp di inizio e fine partita (nessun attributo della classe `Partita` registra data e ora), un identificativo univoco della partita (la classe `Partita` non ha un campo `id` né un campo UUID), il saldo crediti (concetto assente nel Dominio attuale — arriverà in Fase 5), e lo stato serializzato completo per il ripristino (il dizionario di `get_stato_completo` è pensato per la visualizzazione, non per la ricostruzione fedele — questo arriverà in Fase 4).

---

## 3. Struttura del database

### Tabella `utenti`

- **Scopo**: rappresenta un profilo utente locale persistente. Nella Fase 1 viene creata con i campi di base. In Fase 2 viene popolata con i dati di registrazione e autenticazione.
- **Campi principali**:
  - `id`: numero intero, autoincrementale. Identificativo univoco dell'utente.
  - `nome`: testo, non nullo. Nome scelto dall'utente. Corrisponde al parametro `nome_giocatore_umano` passato a `crea_partita_standard`.
  - `email`: testo, nullable. Non popolato in Fase 1 (introdotto in Fase 2 per la registrazione).
  - `password_hash`: testo, nullable. Non popolato in Fase 1 (introdotto in Fase 2 per l'autenticazione con argon2).
  - `data_creazione`: data-ora, non nullo. Timestamp di creazione del profilo.
  - `crediti`: numero intero, default zero. Non popolato in Fase 1 (introdotto in Fase 5 per il sistema crediti).
- **Chiave primaria**: `id`.
- **Relazioni**: nessuna relazione in ingresso in Fase 1. In fasi successive, `utenti.id` sarà referenziato da `partite.utente_id`, `statistiche.utente_id` e `crediti_log.utente_id`.
- **Note su questa fase**: in Fase 1 la tabella viene creata ma non viene popolata in modo significativo. L'unico campo scritto sarà `nome` e `data_creazione`, per consentire un profilo locale minimale da agganciare alle partite. I campi `email`, `password_hash` e `crediti` esistono nello schema ma restano nulli fino alle rispettive fasi di competenza. Questo approccio evita migrazioni di schema in Fase 2 e Fase 5.

Il collegamento con il codice esistente è il seguente: il nome del giocatore umano, oggi passato come stringa a `crea_partita_standard`, diventa il campo `nome` nella tabella `utenti`. L'id del giocatore, oggi assegnato come intero locale temporaneo in `crea_giocatore_umano` (parametro `id_giocatore=1`), non ha relazione con `utenti.id`: l'id del giocatore nel Dominio è un indice di sessione, mentre `utenti.id` è un identificativo persistente. Questa distinzione è fondamentale e deve essere mantenuta.

### Tabella `partite`

- **Scopo**: rappresenta una singola partita giocata o in corso. Registra la configurazione, lo stato e il risultato.
- **Campi principali**:
  - `id`: numero intero, autoincrementale. Identificativo univoco della partita.
  - `utente_id`: numero intero, non nullo. Riferimento all'utente che ha giocato la partita.
  - `data_inizio`: data-ora, non nullo. Timestamp di avvio della partita.
  - `data_fine`: data-ora, nullable. Timestamp di terminazione. Nullo se la partita è stata interrotta senza completarsi.
  - `stato`: testo, non nullo. Valore tra "in_corso", "completata", "interrotta". Corrisponde allo stato restituito da `Partita.get_stato_partita()`, mappato ai valori persistenti.
  - `num_bot`: numero intero, non nullo. Numero di bot nella configurazione. Derivato dal parametro `num_bot` di `crea_partita_standard`.
  - `num_cartelle_umano`: numero intero, non nullo. Cartelle assegnate al giocatore umano. Derivato dal parametro `num_cartelle_umano` di `crea_partita_standard`.
  - `turni_giocati`: numero intero, default zero. Conteggio dei turni completati. Derivabile dalla lunghezza della lista `numeri_estratti` restituita da `get_stato_completo`.
  - `ha_tombola`: vero/falso, default falso. Indica se la partita è terminata per tombola. Derivato da `Partita.has_tombola()`.
  - `checkpoint_stato`: testo, nullable. Campo riservato per il JSON serializzato dello stato completo. Non popolato in Fase 1 (introdotto in Fase 4 per il salvataggio e ripresa partita).
- **Chiave primaria**: `id`.
- **Relazioni**: `utente_id` referenzia `utenti.id`. Questa relazione vincola ogni partita a un utente.
- **Note su questa fase**: in Fase 1 i campi `data_inizio`, `data_fine`, `stato`, `num_bot`, `num_cartelle_umano`, `turni_giocati` e `ha_tombola` vengono tutti popolati. Il campo `checkpoint_stato` viene creato nello schema ma resta nullo fino alla Fase 4.

Il collegamento con il codice esistente è il seguente: i parametri di configurazione (`num_bot`, `num_cartelle_umano`) corrispondono direttamente ai parametri di `crea_partita_standard`. Lo stato finale corrisponde al valore restituito da `Partita.get_stato_partita()` al momento della terminazione. Il conteggio dei turni corrisponde alla variabile di modulo `_turno_corrente` in `game_controller.py`. L'informazione tombola corrisponde al risultato di `Partita.has_tombola()`.

### Tabella `statistiche`

- **Scopo**: rappresenta le statistiche aggregate per utente. Ogni record corrisponde a una singola statistica calcolata al termine di una partita.
- **Campi principali**:
  - `id`: numero intero, autoincrementale. Identificativo univoco del record statistico.
  - `utente_id`: numero intero, non nullo. Riferimento all'utente proprietario delle statistiche.
  - `partita_id`: numero intero, non nullo. Riferimento alla partita da cui è stato calcolato il record.
  - `data`: data-ora, non nullo. Timestamp di registrazione.
  - `turni`: numero intero, non nullo. Turni giocati nella partita. Derivato dal conteggio dei numeri estratti.
  - `premi_vinti`: numero intero, non nullo. Numero totale di premi vinti dal giocatore umano in quella partita. Derivato contando i record in `storico_premi` il cui campo `giocatore` corrisponde al nome dell'utente umano.
  - `ha_tombola`: vero/falso, non nullo. Se il giocatore umano ha ottenuto la tombola. Derivato verificando se in `storico_premi` esiste un record con `premio` uguale a "tombola" e `giocatore` uguale al nome dell'utente umano.
  - `dettaglio_premi`: testo, nullable. Rappresentazione testuale dei premi vinti (tipo e cartella), per consultazione futura. Derivato da `storico_premi`.
- **Chiave primaria**: `id`.
- **Relazioni**: `utente_id` referenzia `utenti.id`. `partita_id` referenzia `partite.id`.
- **Note su questa fase**: in Fase 1 la tabella viene creata e i repository espongono le operazioni di scrittura e lettura. Tuttavia, la scrittura effettiva al termine della partita non viene attivata nel Controller in Fase 1: il collegamento tra il Controller e `StatisticheRepository` per il salvataggio automatico al termine della partita è compito della Fase 3. In Fase 1 si garantisce che la tabella esista, che l'implementazione SQLite funzioni e che i test la verifichino.

Il collegamento con il codice esistente è il seguente: i dati per popolare la tabella `statistiche` sono tutti derivabili dallo `storico_premi` di `Partita` e dallo stato restituito da `get_stato_completo`. Il campo `turni` corrisponde alla lunghezza di `numeri_estratti`. I campi `premi_vinti`, `ha_tombola` e `dettaglio_premi` sono tutti derivabili filtrando `storico_premi` per il nome del giocatore umano.

### Tabella `crediti_log`

- **Scopo**: rappresenta il registro cronologico di tutte le transazioni di crediti virtuali per utente.
- **Campi principali**:
  - `id`: numero intero, autoincrementale. Identificativo univoco della transazione.
  - `utente_id`: numero intero, non nullo. Riferimento all'utente coinvolto.
  - `tipo`: testo, non nullo. Valore tra "addebito" e "accredito".
  - `importo`: numero intero, non nullo. Quantità di crediti coinvolti nella transazione.
  - `motivo`: testo, non nullo. Descrizione della ragione della transazione (esempio: "costo_partita", "premio_tombola", "daily_reward").
  - `saldo_risultante`: numero intero, non nullo. Saldo dell'utente dopo l'applicazione della transazione.
  - `timestamp`: data-ora, non nullo. Momento della transazione.
- **Chiave primaria**: `id`.
- **Relazioni**: `utente_id` referenzia `utenti.id`.
- **Note su questa fase**: in Fase 1 la tabella viene creata nello schema e il repository espone le operazioni di base (registra transazione, leggi storico per utente). Tuttavia, nessun componente del Controller o dell'applicazione scrive in questa tabella in Fase 1. La logica dei crediti virtuali, incluso il `CreditiService`, viene implementata in Fase 5. Il campo `saldo_risultante` garantisce che il registro sia autoconsistente: anche senza leggere la tabella `utenti`, è possibile ricostruire la sequenza completa dei saldi.

Il collegamento con il codice esistente è il seguente: alla versione v0.14.0-alpha non esiste alcun concetto di crediti nel Dominio. La tabella `crediti_log` è interamente prospettica. Non esiste nessun attributo nelle classi `Partita`, `GiocatoreBase` o `GiocatoreUmano` che corrisponda ai campi di questa tabella. La struttura viene creata in Fase 1 solo per evitare una migrazione di schema in Fase 5.

---

## 4. Le interfacce astratte dei repository

### Perché interfacce ABC e non classi concrete

Le interfacce sono definite come classi astratte ABC e non come classi concrete per una ragione specifica a questo progetto. La Costituzione stabilisce nella Fase 8 che il server online sostituirà SQLite con PostgreSQL lato backend, ma il client wxPython continuerà a usare SQLite per la cache locale. Per rendere questa sostituzione possibile senza modificare il Controller, è necessario che il Controller dipenda da un contratto stabile (l'interfaccia ABC) e non dall'implementazione concreta (il repository SQLite). Quando in Fase 8 verrà creato il `NetworkAdapter`, questo implementerà le stesse interfacce ABC senza che il Controller debba cambiare una riga. Questo è il Repository Pattern applicato: il Dominio e il Controller conoscono le interfacce, l'Infrastructure fornisce le implementazioni.

Inoltre, il Vincolo 4 della Costituzione ("Infrastructure mai nel Dominio") impone che le classi di Dominio non importino da Infrastructure. Le interfacce ABC vengono posizionate in una cartella visibile sia al Controller che all'Infrastructure, ma non nel Dominio puro. Il Dominio non conosce l'esistenza dei repository: è il Controller che li usa per orchestrare la persistenza dopo aver coordinato le operazioni di Dominio.

### PartitaRepository

- **Nome interfaccia**: `PartitaRepository`
- **Responsabilità**: definisce le operazioni di persistenza per i dati di una partita di gioco.
- **Operazioni esposte**:
  - `salva_partita`: registra una nuova partita nel database con la sua configurazione iniziale (utente, numero bot, numero cartelle, data inizio). Restituisce l'identificativo assegnato.
  - `aggiorna_partita`: aggiorna lo stato di una partita esistente (stato finale, data fine, turni giocati, esito tombola).
  - `ottieni_partita_per_id`: recupera i dati di una singola partita dato il suo identificativo.
  - `ottieni_partite_per_utente`: recupera la lista delle partite di un utente specifico, in ordine cronologico inverso.
  - `salva_checkpoint`: salva lo stato serializzato di una partita per il ripristino futuro. Non implementato in Fase 1 (il metodo esiste nell'interfaccia ma l'implementazione SQLite solleva un'eccezione di non-implementazione fino alla Fase 4).
  - `carica_checkpoint`: recupera lo stato serializzato di una partita precedentemente salvata. Stessa regola del salva_checkpoint.
- **Cosa NON fa**: non contiene logica di business. Non decide quando salvare: è il Controller che decide. Non valida la coerenza dei dati di Dominio (se i turni giocati sono corretti, se la tombola è effettiva): queste verifiche restano nel Dominio. Non gestisce la connessione al database: la riceve dal `db_manager`.
- **Chi la usa**: il layer Controller (in futuro tramite `game_controller.py` o un servizio applicativo dedicato).
- **Chi la implementa**: `SqlitePartitaRepository` nella cartella `bingo_game/infrastructure/repositories/`.

### UtenteRepository

- **Nome interfaccia**: `UtenteRepository`
- **Responsabilità**: definisce le operazioni di persistenza per i profili utente.
- **Operazioni esposte**:
  - `crea_utente`: registra un nuovo profilo utente con il nome fornito. Restituisce l'identificativo assegnato.
  - `ottieni_utente_per_id`: recupera i dati di un utente dato il suo identificativo.
  - `ottieni_utente_per_nome`: recupera i dati di un utente dato il suo nome. Utile in Fase 1 per associare il nome digitato nella configurazione a un profilo persistente.
  - `aggiorna_utente`: aggiorna i campi di un profilo utente esistente.
  - `esiste_utente`: verifica se esiste un utente con un dato nome. Restituisce vero o falso.
- **Cosa NON fa**: non gestisce autenticazione (niente hash password, niente JWT — quello è compito della Fase 2 e dell'`AuthService`). Non gestisce la sessione corrente. Non decide la validazione del nome utente (lunghezza minima, caratteri ammessi): quella logica va nel Controller o nel layer Application.
- **Chi la usa**: il layer Controller.
- **Chi la implementa**: `SqliteUtenteRepository` nella cartella `bingo_game/infrastructure/repositories/`.

### StatisticheRepository

- **Nome interfaccia**: `StatisticheRepository`
- **Responsabilità**: definisce le operazioni di persistenza per le statistiche di gioco aggregate per utente.
- **Operazioni esposte**:
  - `registra_statistiche_partita`: salva un record statistico al termine di una partita (utente, partita, turni, premi vinti, tombola, dettaglio).
  - `ottieni_statistiche_utente`: recupera tutte le statistiche di un utente specifico.
  - `ottieni_statistiche_aggregate`: recupera una sintesi aggregata per un utente (partite giocate totali, partite vinte, premi totali, miglior partita).
- **Cosa NON fa**: non calcola le statistiche partendo dai dati grezzi della partita: riceve dati già calcolati dal Controller. Non gestisce la visualizzazione (quella è della `FinestraStatistiche` in Fase 3). Non decide quando registrare: è il Controller che invoca la registrazione al termine della partita.
- **Chi la usa**: il layer Controller.
- **Chi la implementa**: `SqliteStatisticheRepository` nella cartella `bingo_game/infrastructure/repositories/`.

### CreditiRepository

- **Nome interfaccia**: `CreditiRepository`
- **Responsabilità**: definisce le operazioni di persistenza per il registro delle transazioni di crediti virtuali.
- **Operazioni esposte**:
  - `registra_transazione`: salva una transazione di crediti (utente, tipo, importo, motivo, saldo risultante).
  - `ottieni_storico_utente`: recupera lo storico cronologico delle transazioni di un utente.
  - `ottieni_saldo_corrente`: recupera il saldo più recente di un utente leggendo l'ultima transazione registrata.
- **Cosa NON fa**: non implementa la logica di business dei crediti (non decide se l'utente può permettersi una partita, non applica i bonus giornalieri — quello è compito del `CreditiService` in Fase 5). Non modifica la tabella `utenti`: il campo `crediti` in `utenti` è gestito dal `CreditiService`, non dal repository.
- **Chi la usa**: il `CreditiService` (introdotto in Fase 5).
- **Chi la implementa**: `SqliteCreditiRepository` nella cartella `bingo_game/infrastructure/repositories/`.

---

## 5. Il componente di gestione del database

Il componente `db_manager` è il punto unico di accesso al database SQLite. Nessun repository apre o chiude la connessione autonomamente: tutti ricevono la connessione dal `db_manager`.

### Apertura e chiusura della connessione

Il `db_manager` apre la connessione al file database SQLite quando viene invocato per la prima volta, non al momento dell'import del modulo. Questo approccio (inizializzazione differita) è scelto perché la Costituzione stabilisce che `main.py` non viene modificato in Fase 1: il database non può essere costruito all'avvio dell'applicazione. La connessione viene aperta quando il Controller (o un componente che opera per conto del Controller) richiede per la prima volta un repository.

La chiusura della connessione avviene quando l'applicazione rilascia esplicitamente le risorse, o quando il `db_manager` viene distrutto. Il `db_manager` espone un metodo di chiusura esplicita che i componenti di livello superiore possono chiamare. Se la chiusura esplicita non viene chiamata, SQLite chiude la connessione quando l'oggetto Python viene rimosso dal garbage collector, ma il design non si affida a questo: il metodo di chiusura esplicita è il percorso primario.

### Creazione dello schema

Alla prima apertura della connessione, se il file database non esiste ancora o se è vuoto, il `db_manager` crea lo schema completo (le quattro tabelle descritte nella Sezione 3). Lo schema viene creato in modo idempotente: se le tabelle esistono già, il `db_manager` non tenta di ricrearle. Questo garantisce che avviare l'applicazione più volte sullo stesso file database non produca errori.

Il file database viene posizionato in una cartella dati locale dell'utente (non nella cartella del codice sorgente). La scelta esatta del percorso dipende dalla piattaforma, ma su Windows 11 (la piattaforma di riferimento dichiarata nel profilo utente) il percorso sarà nella cartella AppData dell'utente corrente, o in alternativa nella cartella del progetto sotto una sottocartella dedicata `data/`. Questa decisione di path viene incapsulata nel `db_manager` e non è nota ai repository.

### Gestione delle transazioni

Atomicità, in questo contesto, significa che un gruppo di operazioni sul database o vengono eseguite tutte con successo o non ne viene eseguita nessuna. Se durante il salvataggio di una partita qualcosa va storto (un campo mancante, un vincolo violato, un errore di I/O), il database torna allo stato precedente al tentativo di salvataggio. Non rimane un record parzialmente scritto.

Il `db_manager` fornisce un meccanismo di transazione a cui i repository accedono. Ogni operazione di scrittura del repository viene eseguita all'interno di una transazione. Se l'operazione ha successo, il `db_manager` conferma la transazione. Se l'operazione fallisce, il `db_manager` annulla la transazione. I repository non gestiscono direttamente il commit o il rollback: delegano al `db_manager`.

### Ciclo di vita nel contesto dell'applicazione

Il `db_manager` viene creato una sola volta durante il ciclo di vita dell'applicazione. In Fase 1, dato che `main.py` non viene modificato, il `db_manager` viene istanziato al momento della prima richiesta di accesso al database — tipicamente quando il Controller riceve i repository iniettati. Il riferimento al `db_manager` è detenuto dal componente che assembla i repository (la factory o il modulo di cablaggio delle dipendenze).

Alla chiusura dell'applicazione, il `db_manager` deve essere chiuso esplicitamente. In una futura integrazione con `main.py` (post Fase 1), la chiusura verrà aggiunta nel blocco `finally` accanto a `GameLogger.shutdown()`. In Fase 1, la chiusura avviene implicitamente alla terminazione del processo Python.

### Comportamento nei casi anomali

**Il file database è corrotto**: se `sqlite3` non riesce ad aprire il file perché è corrotto, il `db_manager` intercetta l'errore e solleva un'eccezione specifica di Infrastructure (non un'eccezione generica Python). Il repository non tenta di riparare il file. L'applicazione può decidere (in una fase successiva) di mostrare un messaggio all'utente e di offrire la possibilità di ricreare un database vuoto. In Fase 1, il comportamento minimo è: l'eccezione viene registrata nel log e la persistenza non è disponibile per quella sessione. L'applicazione continua a funzionare senza database, come avviene oggi in v0.14.0-alpha.

**Il file database non è accessibile in scrittura**: se il file esiste ma il sistema operativo nega la scrittura (permessi insufficienti, file bloccato da un altro processo), il `db_manager` intercetta l'errore, lo registra nel log e solleva un'eccezione specifica. Come nel caso precedente, l'applicazione continua senza persistenza.

**L'applicazione viene chiusa mentre una transazione è aperta**: SQLite gestisce questo caso nativamente: se la connessione viene chiusa con una transazione in corso, la transazione viene annullata automaticamente (rollback implicito). Il `db_manager` non deve aggiungere logica per questo caso. Il dato non confermato viene perso, ma il database rimane in uno stato consistente.

---

## 6. Integrazione con il Controller esistente

### Meccanismo di iniezione dei repository

I repository vengono passati al Controller tramite un oggetto contenitore di dipendenze. La scelta è un oggetto semplice (una classe o una dataclass) che raggruppa i quattro repository e li rende disponibili con nomi espliciti. Non si usa un framework di dependency injection esterno: non è giustificato per quattro dipendenze.

L'alternativa scartata è passare i repository come parametri individuali alle funzioni di `game_controller.py`. Questa alternativa è stata scartata perché le funzioni di `game_controller.py` sono a livello di modulo e un aumento del numero di parametri su ogni funzione renderebbe il codice fragile e verboso. L'oggetto contenitore mantiene la firma delle funzioni stabile: ogni funzione riceve il contenitore (o lo accede tramite un riferimento di modulo) anziché quattro parametri aggiuntivi.

L'altra alternativa scartata è usare variabili globali di modulo per i repository. Questa scelta renderebbe impossibile testare il Controller con repository substitutivi (mock, in-memory) senza usare monkey-patching, e violerebbe il principio di dependency injection che la Costituzione richiede implicitamente nel contratto in uscita della Fase 1 ("il Controller accetta i repository come dipendenze iniettate").

### Impatto sui metodi pubblici del Controller

I metodi pubblici esistenti del Controller non cambiano la loro firma verso le finestre wx. La Presentazione chiama i metodi di `ComandiSistema` e `ComandiGiocatoreUmano`, i quali delegano alle funzioni di `game_controller.py`. Queste funzioni continueranno a ricevere la `Partita` come primo argomento e a restituire gli stessi tipi di dato (dizionari, booleani, `EsitoAzione`). L'accesso ai repository avviene internamente alle funzioni del Controller, non attraverso i parametri visibili alla Presentazione.

Il cambiamento rimane invisibile alla Presentazione perché la classe `ComandiSistema` non espone i repository. La `FinestraConfigurazione` chiama `ComandiSistema.crea_nuova_partita(nome, cartelle, bot)` e riceve una `Partita`. La `FinestraGioco` chiama `ComandiSistema.esegui_turno(partita)` e riceve un dizionario. Nessuno di questi contratti cambia. La persistenza avviene come effetto collaterale interno, non come cambiamento di interfaccia.

### Visibilità del database dalla Presentazione

La `FinestraGioco` e le altre finestre wx non devono sapere che ora esiste un database. Il Vincolo 5 della Costituzione ("Renderer come unico ponte") stabilisce che la Presentazione comunica con il Dominio esclusivamente tramite il sistema eventi (`EsitoAzione`, `EventoAzione`) e il contratto `BaseRenderer`. Nessuna finestra wx importa direttamente classi di Dominio o di Infrastructure per invocare metodi su di esse. Le finestre usano `ComandiSistema` e `ComandiGiocatoreUmano` come facade.

Questo vincolo viene rispettato senza eccezioni. I repository sono componenti dell'Infrastructure. Le finestre wx non li importano, non li ricevono, non sanno che esistono. Se in futuro una finestra avrà bisogno di leggere dati dal database (per esempio la `FinestraStatistiche` in Fase 3), lo farà tramite un metodo aggiunto a `ComandiSistema` che internamente usa il repository, restituendo dati neutri (dizionari, stringhe) alla finestra.

---

## 7. Strategia di test

### Test del db_manager

Si testa che il `db_manager` crei correttamente il file database e le quattro tabelle alla prima inizializzazione. Si verifica che una seconda inizializzazione sullo stesso file non produca errori (idempotenza). Si verifica che la chiusura della connessione non sollevi eccezioni. Si verifica che, in caso di file database corrotto (simulato fornendo un file non-SQLite), il `db_manager` sollevi l'eccezione specifica e non un'eccezione generica.

I test non dipendono dalla UI perché il `db_manager` non ha nessuna relazione con wxPython. Viene istanziato direttamente nel test passandogli un percorso di file temporaneo.

I test non lasciano dati residui perché ogni test crea il database in una cartella temporanea dedicata, e la cartella viene eliminata al termine del test.

Un test si considera superato quando: il file database esiste dopo l'inizializzazione, le quattro tabelle sono presenti nello schema, la connessione si chiude senza errori, e i casi anomali producono le eccezioni attese.

### Test dei quattro repository

Per ciascun repository (SqliteUtenteRepository, SqlitePartitaRepository, SqliteStatisticheRepository, SqliteCreditiRepository) si testa ogni operazione esposta dall'interfaccia ABC. Si verifica che l'inserimento di un record restituisca un identificativo valido. Si verifica che la lettura di un record inserito restituisca i dati corretti. Si verifica che l'aggiornamento di un record modifichi effettivamente i campi. Si verifica che la lettura di un record inesistente restituisca il valore atteso (None o lista vuota, secondo l'operazione).

I test non dipendono dalla UI perché ogni repository riceve la connessione dal `db_manager`, il quale non ha nessuna relazione con wxPython. I test istanziano direttamente il `db_manager` con un file temporaneo e poi istanziano il repository passandogli la connessione.

I test non lasciano dati residui perché ogni test usa un file database temporaneo creato nella cartella temporanea del sistema operativo, eliminato al termine del test. In alternativa, si usa un database SQLite in memoria (senza file su disco), che viene distrutto automaticamente alla chiusura della connessione.

Un test del repository si considera superato quando: l'inserimento non solleva eccezioni, la lettura restituisce esattamente i dati inseriti, l'aggiornamento modifica i dati verificabili con una successiva lettura, e le operazioni su record inesistenti restituiscono i valori attesi senza sollevare eccezioni.

### Test di integrazione con il Controller

Si testa che il Controller, quando configurato con i repository SQLite (o con repository in memoria per velocità), possa creare una partita e che i repository registrino i dati attesi. Si verifica che l'esecuzione di un turno non produca errori di persistenza. Si verifica che al termine di una partita (tombola o numeri esauriti) i dati finali siano coerenti nel database.

I test non dipendono dalla UI perché l'integrazione viene testata al livello Controller: si chiama `crea_partita_standard`, `avvia_partita_sicura`, `esegui_turno_sicuro` e si verificano i dati nei repository. Nessuna finestra wx viene istanziata.

I test non lasciano dati residui per la stessa ragione dei test dei repository: database temporaneo o in memoria.

Un test di integrazione si considera superato quando: la creazione di una partita produce un record nella tabella `partite`, l'esecuzione di turni non solleva eccezioni di persistenza, e al termine della partita il record nella tabella `partite` contiene lo stato finale corretto (`ha_tombola`, `turni_giocati`, `stato`).

---

## 8. Struttura delle cartelle e dei file

La struttura seguente descrive i file e le cartelle introdotti dalla Fase 1 nel repository. Tutti i nuovi file si trovano sotto `bingo_game/infrastructure/`, che è una cartella nuova.

```
bingo_game/
  infrastructure/
    __init__.py                       — Package marker per il layer Infrastructure
    database/
      __init__.py                     — Package marker per il modulo database
      db_manager.py                   — Componente di gestione connessione, schema e transazioni SQLite
    repositories/
      __init__.py                     — Package marker e raccolta export dei repository
      interfaces/
        __init__.py                   — Package marker per le interfacce astratte
        partita_repository.py         — Interfaccia ABC PartitaRepository
        utente_repository.py          — Interfaccia ABC UtenteRepository
        statistiche_repository.py     — Interfaccia ABC StatisticheRepository
        crediti_repository.py         — Interfaccia ABC CreditiRepository
      sqlite_partita_repository.py    — Implementazione SQLite di PartitaRepository
      sqlite_utente_repository.py     — Implementazione SQLite di UtenteRepository
      sqlite_statistiche_repository.py — Implementazione SQLite di StatisticheRepository
      sqlite_crediti_repository.py    — Implementazione SQLite di CreditiRepository
tests/
  infrastructure/
    __init__.py                       — Package marker per i test del layer Infrastructure
    test_db_manager.py                — Test unitari per db_manager
    test_sqlite_partita_repository.py — Test unitari per SqlitePartitaRepository
    test_sqlite_utente_repository.py  — Test unitari per SqliteUtenteRepository
    test_sqlite_statistiche_repository.py — Test unitari per SqliteStatisticheRepository
    test_sqlite_crediti_repository.py — Test unitari per SqliteCreditiRepository
    test_controller_integration.py    — Test di integrazione Controller + repository
```

Questa struttura non crea conflitti con i file esistenti. La cartella `bingo_game/infrastructure/` non esiste in v0.14.0-alpha. La cartella `tests/infrastructure/` non esiste e si aggiunge accanto alle cartelle `tests/unit/`, `tests/ui/` e `tests/integration/` già presenti.

---

## 9. Decisioni deliberatamente rinviate

### Scelta del driver e dell'ORM per il server online

- **Cosa non si decide ora**: quale driver Python asincrono (asyncpg, aiopg, altro) e quale ORM (SQLAlchemy, Tortoise ORM, nessun ORM) verranno usati per il database PostgreSQL del server online.
- **Perché non si decide ora**: il server online è un progetto separato che verrà costruito in Fase 8. La Costituzione stabilisce esplicitamente nella scheda SQLite dello stack tecnologico che "la scelta dell'ORM o del driver asincrono per il database del server online viene presa durante il DESIGN dedicato alla Fase 8, non prima". Introdurre uno strumento come SQLAlchemy prima che il problema che risolve sia presente aggiungerebbe complessità non necessaria.
- **In quale fase verrà decisa**: Fase 8.

### Formato di sincronizzazione dei dati tra locale e cloud

- **Cosa non si decide ora**: in che formato i dati di partita, statistiche e crediti vengono sincronizzati tra il database SQLite locale del client e il database PostgreSQL del server.
- **Perché non si decide ora**: la sincronizzazione richiede un protocollo di comunicazione (REST, WebSocket) e una strategia di risoluzione dei conflitti che dipendono dalla struttura del server, non ancora definita.
- **In quale fase verrà decisa**: Fase 8 per il meccanismo base, Fase 9 per la sincronizzazione real-time.

### Struttura della tabella crediti_log per uso multiplayer

- **Cosa non si decide ora**: se la tabella `crediti_log` avrà bisogno di campi aggiuntivi per il multiplayer online (ad esempio un identificativo di sessione server, un timestamp di sincronizzazione, un flag di conferma server).
- **Perché non si decide ora**: i campi dipendono dalla logica di crediti condivisi tra client e server, che non è definita fino alla Fase 8. In Fase 1 la tabella viene creata con i campi necessari al funzionamento locale.
- **In quale fase verrà decisa**: Fase 8, nel contesto del design delle API server.

### Gestione dei conflitti di dati tra sessioni diverse

- **Cosa non si decide ora**: cosa succede se lo stesso utente gioca su due dispositivi diversi e i database locali divergono (partite diverse, statistiche diverse, saldi crediti diversi).
- **Perché non si decide ora**: questo scenario non esiste fino a quando non viene introdotto il server online. In Fase 1 (e fino alla Fase 7 inclusa) il database è strettamente locale e un solo processo alla volta vi accede.
- **In quale fase verrà decisa**: Fase 8, nel contesto della strategia di sincronizzazione e reconciliation.

### Migrazione dello schema tra versioni

- **Cosa non si decide ora**: quale strumento o meccanismo viene usato per migrare lo schema del database quando una nuova versione dell'applicazione introduce modifiche alle tabelle.
- **Perché non si decide ora**: in Fase 1 lo schema viene creato da zero. Le fasi successive che aggiungono campi (Fase 2 per `email` e `password_hash`, Fase 5 per la logica crediti) possono gestire le modifiche con logiche semplici (verifica della versione dello schema e aggiunta dei campi mancanti). Un sistema di migrazione formale diventa necessario solo quando il numero di migrazioni rende impraticabile la gestione manuale.
- **In quale fase verrà decisa**: da valutare tra Fase 4 e Fase 7, quando il numero di modifiche allo schema sarà sufficiente per giustificare l'investimento.

---

## 10. Assunzioni e incertezze

### Assunzione 1 — get_stato_completo restituisce un dizionario stabile

- **Cosa si assume**: il dizionario restituito da `Partita.get_stato_completo()` mantiene la sua struttura attuale (chiavi `stato_partita`, `ultimo_numero_estratto`, `numeri_estratti`, `numeri_mancanti`, `giocatori`, `premi_gia_assegnati`, `conteggio_giocatori`) e non cambia in modo incompatibile nelle fasi successive.
- **Cosa succederebbe se l'assunzione fosse sbagliata**: il codice dei repository che deriva i dati da `get_stato_completo` si romperebbe. In particolare, il calcolo dei turni giocati (basato sulla lunghezza di `numeri_estratti`) e la mappatura dei giocatori potrebbero produrre errori.
- **Quando si scoprirà se l'assunzione è corretta**: in Fase 4, quando `serializza_stato()` verrà introdotto su `Partita` e potrebbe modificare o estendere il dizionario di `get_stato_completo`.

### Assunzione 2 — storico_premi ha struttura stabile

- **Cosa si assume**: la lista `Partita.storico_premi` continua ad avere record con le chiavi `giocatore`, `id_giocatore`, `cartella`, `premio`, `riga`, `turno`, come osservato nella versione v0.14.0-alpha.
- **Cosa succederebbe se l'assunzione fosse sbagliata**: il calcolo delle statistiche per utente (conteggio premi, verifica tombola, dettaglio premi) nel `StatisticheRepository` produrrebbe risultati errati o eccezioni.
- **Quando si scoprirà se l'assunzione è corretta**: in Fase 3, quando il Controller inizierà a invocare `StatisticheRepository.registra_statistiche_partita` con dati reali derivati dallo `storico_premi`.

### Assunzione 3 — Un solo giocatore umano per partita

- **Cosa si assume**: in Fase 1 (e fino alla Fase 6 inclusa), ogni partita ha esattamente un giocatore umano. Questa assunzione è già identificata nella Sezione 1 della Costituzione come assunzione implicita del Dominio, confermata dal metodo `ottieni_giocatore_umano` in `game_controller.py` che restituisce un singolo oggetto.
- **Cosa succederebbe se l'assunzione fosse sbagliata**: la tabella `partite` ha un singolo campo `utente_id` che referenzia un solo utente. Se in Fase 7 (multiplayer locale) più utenti umani giocano la stessa partita, la tabella `partite` dovrà essere estesa con una tabella di associazione (ad esempio `partita_giocatori`).
- **Quando si scoprirà se l'assunzione è corretta**: in Fase 7, durante il DESIGN del multiplayer locale.

### Assunzione 4 — SQLite in accesso singolo è sufficiente

- **Cosa si assume**: il database SQLite viene acceduto in scrittura da un solo processo alla volta (l'applicazione wxPython). Non ci sono accessi concorrenti da altri processi.
- **Cosa succederebbe se l'assunzione fosse sbagliata**: SQLite ha un singolo writer alla volta. Se due istanze dell'applicazione accedessero allo stesso file database, una delle due riceverebbe errori di blocco. La Costituzione identifica questa limitazione nell'Assunzione 3 delle incertezze, indicando che potrebbe emergere in Fase 7 con profili utente multipli sullo stesso PC.
- **Quando si scoprirà se l'assunzione è corretta**: in Fase 7, durante la valutazione dei pattern di accesso multiutente locale.

### Assunzione 5 — Il percorso del file database è accessibile in scrittura

- **Cosa si assume**: la cartella scelta per il file database (nella directory AppData dell'utente o una sottocartella del progetto) è sempre accessibile in scrittura su Windows 11 con le configurazioni standard.
- **Cosa succederebbe se l'assunzione fosse sbagliata**: il `db_manager` non riuscirebbe a creare il file database e l'applicazione funzionerebbe senza persistenza, come in v0.14.0-alpha. Non ci sarebbe perdita di funzionalità rispetto alla versione corrente, ma le funzionalità di persistenza non sarebbero disponibili.
- **Quando si scoprirà se l'assunzione è corretta**: durante il primo test di integrazione su una macchina Windows 11 reale.

### Assunzione 6 — Il contatore turni _turno_corrente è affidabile

- **Cosa si assume**: la variabile di modulo `_turno_corrente` in `game_controller.py` riflette accuratamente il numero di turni giocati, e viene resettata correttamente da `crea_partita_standard`.
- **Cosa succederebbe se l'assunzione fosse sbagliata**: il campo `turni_giocati` nella tabella `partite` potrebbe contenere un valore errato. Tuttavia, il design mitiga questo rischio permettendo anche di derivare i turni dalla lunghezza di `numeri_estratti` in `get_stato_completo`, che è un dato di Dominio non dipendente dalla variabile di modulo.
- **Quando si scoprirà se l'assunzione è corretta**: durante i test di integrazione della Fase 1, verificando la coerenza tra `_turno_corrente` e la lunghezza di `numeri_estratti`.

---

## 11. Istruzioni specifiche per l'agente implementatore

- Non creare la cartella `bingo_game/infrastructure/` prima di aver definito tutte e quattro le interfacce ABC. Le interfacce devono esistere prima delle implementazioni, come specificato nel Vincolo 7 della Costituzione.

- Non importare `sqlite3` in nessun file sotto `bingo_game/` che non sia dentro la cartella `infrastructure/`. Questa regola deriva dal Vincolo 2 della Costituzione (Dominio puro) e va verificata con grep al termine dell'implementazione.

- Non importare da `bingo_game.infrastructure` in nessun file sotto `bingo_game/` che non sia dentro `infrastructure/` stessa o non sia il Controller. Verificare con grep al termine dell'implementazione che nessun file di Dominio importi da Infrastructure, come richiesto dal Vincolo 4.

- Non aggiungere parametri ai metodi pubblici di `ComandiSistema` che siano visibili dalla Presentazione. L'integrazione dei repository nel Controller deve restare invisibile alle finestre wx.

- Creare il database in una cartella dati dedicata, non nella cartella del codice sorgente. Non usare percorsi assoluti hardcoded: usare un meccanismo portatile basato su `pathlib` per determinare il percorso.

- Non scrivere `print()` in nessun file della cartella `infrastructure/`. Usare il sub-logger `tombola_stark.infrastructure` per tutti i messaggi di log.

- Non catturare eccezioni generiche (`except Exception`) nei repository SQLite senza loggarle. Ogni eccezione SQL deve essere intercettata, registrata nel log e convertita in un'eccezione specifica di Infrastructure.

- Ogni test del `db_manager` e dei repository deve usare un database temporaneo o in memoria. Nessun test deve scrivere nel file database dell'applicazione. Nessun test deve lasciare file residui su disco.

- Non popolare la tabella `utenti` con dati di autenticazione (email, password_hash) nei test di Fase 1. Questi campi esistono nello schema ma devono restare nulli.

- Non implementare la logica di business dei crediti nel `SqliteCreditiRepository`. Il repository esegue solo operazioni CRUD. La logica (saldo minimo, bonus giornaliero, addebito partita) è compito del `CreditiService` in Fase 5.

- Non implementare il corpo dei metodi `salva_checkpoint` e `carica_checkpoint` in `SqlitePartitaRepository`. Questi metodi devono esistere nell'interfaccia ABC e nell'implementazione, ma l'implementazione deve sollevare un'eccezione esplicita (`NotImplementedError` con messaggio chiaro) fino alla Fase 4.

- Dopo l'implementazione, eseguire le tre verifiche grep indicate nei Vincoli 2, 4 e 7 della Costituzione per confermare che nessun import proibito è stato introdotto.

- Non modificare `main.py`. Il `db_manager` viene istanziato con inizializzazione differita, non nel punto di avvio dell'applicazione.

- Non modificare nessun file del layer Presentazione (`bingo_game/ui/`). Nessuna finestra wx deve sapere che il database esiste.

- Assicurarsi che ogni implementazione concreta di repository riceva la connessione dal `db_manager` e non la crei autonomamente. Il `db_manager` è il punto unico di gestione della connessione.

- Verificare che i test di tutti e quattro i repository passino in isolamento, senza dipendere dall'ordine di esecuzione e senza dipendere dalla presenza di uno specifico file database su disco.
