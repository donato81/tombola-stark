---
feature: sistema-utente-registrazione-login
agent: Agent-Design
status: DRAFT
version: v0.16.x
date: 2026-04-15
---

# DESIGN 02 — Fase 2: Sistema Utente, Profilo, Registrazione e Login

> **Data**: 15 aprile 2026
> **Versione target**: v0.16.x
> **Tipo documento**: Design di fase
> **Fase roadmap**: 2 di 9
> **Dipende da**: Fase 1 (DESIGN_01_FASE1_INFRASTRUCTURE_LAYER)
> **Sblocca**: Fase 3, Fase 5, Fase 7
> **Documento padre**: DESIGN_COSTITUZIONE_ROADMAP_MULTIPLAYER_2026-04-14.md
> **Stato**: BOZZA
> **Autore analisi**: Agent-Analyze

---

## 1. Scopo e confini di questa fase

Questa fase costruisce il sistema utente locale dell'applicazione Tombola Stark. Alla versione v0.14.0-alpha non esiste alcun concetto di identità persistente: il giocatore umano è rappresentato da una stringa nome passata a `crea_partita_standard` e dimenticata alla chiusura dell'applicazione. Questa fase introduce un modello `Utente` nel Dominio, un servizio di autenticazione locale (`AuthService`), le finestre di registrazione e login in wxPython con pieno supporto NVDA, e l'aggiornamento di `main.py` per inizializzare e chiudere il database.

Questa fase viene costruita immediatamente dopo la Fase 1 per una ragione strutturale precisa: l'identità utente persistente è il prerequisito di tutte le fasi successive che tracciano dati per-utente. La Fase 3 (statistiche) ha bisogno di un `Utente.id` stabile a cui agganciare i record statistici. La Fase 5 (crediti) ha bisogno dello stesso identificativo per il registro delle transazioni. La Fase 7 (multiplayer locale) ha bisogno del sistema di profili per gestire più giocatori umani. Senza il sistema utente di questa fase, nessuna di queste fasi può associare i dati al giocatore corretto.

Cosa questa fase fa. Introduce il modello `Utente` nel Dominio con i campi necessari all'identificazione e all'autenticazione locale. Implementa l'`AuthService` con le operazioni di registrazione, login, logout e gestione della sessione corrente. Popola la tabella `utenti` del database (creata vuota in Fase 1) con i dati di registrazione e l'hash della password. Crea due nuove finestre wxPython (`FinestraRegistrazione` e `FinestraLogin`) con accessibilità NVDA completa. Modifica la `FinestraPrincipale` per esporre le voci Registrazione e Login e per mostrare il nome dell'utente loggato. Modifica la `FinestraConfigurazione` per verificare la presenza di un utente in sessione prima di procedere. Aggiorna `main.py` per inizializzare il database all'avvio e chiuderlo nel blocco `finally`.

Cosa questa fase NON fa. Non modifica le classi di Dominio del gioco: `Partita`, `Tabellone`, `Cartella`, `GiocatoreBase`, `GiocatoreUmano` e `GiocatoreAutomatico` restano invariate. Non altera il flusso di gioco esistente: `FinestraGioco` non viene toccata. Non introduce comunicazione di rete: tutto avviene in locale, sul file database SQLite. Non introduce JWT per le sessioni: il token di sessione è un concetto della Fase 8 per l'autenticazione distribuita. Non implementa il recupero password: in assenza di un server email, il recupero password non ha senso in locale. Non gestisce più utenti loggati contemporaneamente: questa fase mantiene il vincolo di un solo giocatore umano per partita.

I layer toccati, come indicato dalla Costituzione nella scheda della Fase 2, sono quattro. Il Dominio riceve il nuovo modello `Utente`. L'Infrastructure riceve l'aggiornamento dell'implementazione `UtenteRepository` per gestire l'hash della password tramite argon2. La Presentazione riceve due nuove finestre wx e le modifiche a `FinestraPrincipale` e `FinestraConfigurazione`. Il Controller riceve il nuovo `AuthService`.

I layer NON toccati sono il Dominio di gioco (`Partita`, `Tabellone`, `Cartella`, `GiocatoreBase`, `GiocatoreUmano`, `GiocatoreAutomatico`) e il flusso di gioco nella Presentazione (`FinestraGioco`, `FinestraAiutoTastiRapidi`, `FinestraGuidaRegole`, `DialogoRicercaNumero`).

La distinzione fondamentale tra "utente locale" e "utente online" è la seguente. In questa fase, l'utente è un profilo locale memorizzato nel file database SQLite sulla macchina dell'utente. La registrazione e il login avvengono senza alcuna comunicazione di rete. L'hash della password viene calcolato e verificato localmente. Non esiste un server remoto, non esiste una sincronizzazione, non esiste un concetto di sessione distribuita. L'utente online, introdotto in Fase 8, avrà un profilo sul server PostgreSQL, si autenticherà tramite API REST con JWT, e il client wxPython manterrà una copia locale nella cache SQLite. Le due identità (locale e online) convergeranno in Fase 8: fino a quel momento, l'utente esiste solo nel database locale.

---

## 2. Analisi del flusso attuale di identificazione utente

Dalla lettura diretta di `finestra_configurazione.py`, il nome del giocatore umano nasce nel campo `wx.TextCtrl` con valore predefinito "Giocatore". L'utente digita (o accetta il default) e conferma premendo il pulsante "Avvia partita" o il tasto Invio. Il metodo `_on_conferma` legge il valore dal campo con `self._nome_ctrl.GetValue().strip()`, verifica che non sia vuoto, e lo passa a `self._comandi_sistema.crea_nuova_partita(nome_umano=nome, ...)`. Da quel momento, il nome viene inoltrato a `crea_partita_standard` in `game_controller.py`, che lo passa a `crea_giocatore_umano(nome=nome_giocatore_umano, id_giocatore=1)`, che a sua volta crea un'istanza di `GiocatoreUmano(nome=nome, id_giocatore=1)`. L'attributo `nome` viene assegnato in `GiocatoreBase.__init__` e vi resta per tutta la durata della partita. Il nome viene usato fino alla fine nella reportistica dei premi (ogni record in `storico_premi` contiene il campo `giocatore` con il nome stringa) e nel log di gioco.

Non esiste oggi alcun concetto di "sessione utente" o di "utente corrente" che persista tra una partita e l'altra. Quando la `FinestraGioco` si chiude (per completamento partita, per tombola o per chiusura volontaria), il controllo torna alla `FinestraPrincipale`. Il nome del giocatore non viene conservato in nessun componente persistente: l'informazione muore con l'istanza di `Partita` e di `GiocatoreUmano` che vengono abbandonate dal garbage collector. Se l'utente avvia una nuova partita, la `FinestraConfigurazione` si riapre e chiede nuovamente il nome. Non c'è memoria di chi ha giocato l'ultima partita.

La schermata di configurazione oggi chiede il nome del giocatore ad ogni nuova partita perché il flusso attuale non prevede alcuna forma di identificazione persistente. Quando esisterà un sistema di login, questo flusso cambierà nel modo seguente. Se un utente è già loggato (sessione attiva), la `FinestraConfigurazione` mostrerà il nome dell'utente corrente come valore precompilato e non modificabile nel campo nome, evitando la richiesta manuale ad ogni partita. Se nessun utente è loggato, la `FinestraConfigurazione` non si aprirà affatto: l'applicazione reindirizzerà l'utente alla `FinestraLogin` (o alla `FinestraRegistrazione` se non ha un account) prima di consentire l'accesso alla configurazione partita.

I componenti della Presentazione che dovranno essere modificati per accogliere il login sono i seguenti. `FinestraPrincipale` (`bingo_game/ui/finestra_principale.py`) dovrà aggiungere le voci "Registrazione" e "Login" al menu e mostrare il nome dell'utente loggato quando una sessione è attiva. `FinestraConfigurazione` (`bingo_game/ui/finestra_configurazione.py`) dovrà verificare la presenza di una sessione utente attiva e precompilare il campo nome con il nome dell'utente corrente. Le nuove finestre `FinestraRegistrazione` e `FinestraLogin` verranno create ex novo come file separati nella cartella `bingo_game/ui/`.

---

## 3. Il modello Utente nel Dominio

Il modello `Utente` da introdurre nel Dominio rappresenta l'identità persistente di un giocatore registrato nell'applicazione. I campi sono i seguenti.

- `id`: numero intero. Identificativo univoco dell'utente, assegnato dal database al momento della registrazione. Corrisponde a `utenti.id` nella tabella del database. Scopo: collegare in modo stabile tutte le operazioni dell'utente (partite, statistiche, crediti) al profilo corretto.
- `nome`: testo, non nullo. Nome scelto dall'utente durante la registrazione. Deve essere unico nel database. Scopo: identificazione visiva e vocale dell'utente nell'applicazione e nei log.
- `email`: testo, opzionale. Indirizzo email dell'utente. In questa fase può essere nullo perché la registrazione locale non richiede obbligatoriamente un'email. Scopo: predisposto per la Fase 8 quando l'autenticazione online richiederà un'email come credenziale.
- `password_hash`: testo, non nullo. Hash della password calcolato con argon2. Non è la password in chiaro: è il risultato dell'algoritmo di hashing che permette la verifica senza mai memorizzare il testo originale. Scopo: autenticazione dell'utente al momento del login.
- `data_creazione`: data e ora, non nullo. Timestamp del momento in cui il profilo è stato creato. Scopo: tracciabilità e ordinamento cronologico dei profili.
- `crediti`: numero intero, default zero. Saldo crediti virtuali dell'utente. In questa fase resta a zero perché il sistema crediti è compito della Fase 5. Scopo: predisposto per il sistema crediti senza richiedere migrazione di schema.

Il modello `Utente` appartiene al Dominio e non all'Infrastructure per la seguente ragione. Il Dominio contiene le entità che rappresentano i concetti fondamentali dell'applicazione, indipendentemente da come vengono salvati o recuperati. L'utente è un concetto fondamentale: è chi gioca, è chi possiede le statistiche, è chi accumula crediti. Il modo in cui l'utente viene scritto e letto dal database (SQLite oggi, PostgreSQL domani in Fase 8) è un dettaglio tecnico che appartiene all'Infrastructure. Se il modello `Utente` vivesse nell'Infrastructure, tutte le fasi successive che hanno bisogno dell'identità utente (Fase 3, 5, 7) dovrebbero importare dall'Infrastructure, violando il Vincolo 4 della Costituzione ("Infrastructure mai nel Dominio"). Posizionando il modello nel Dominio, il Controller e l'Application possono usarlo liberamente, e l'Infrastructure lo conosce solo perché le sue implementazioni concrete (i repository SQLite) lo ricevono e lo restituiscono.

La relazione tra il modello `Utente` del Dominio e la tabella `utenti` del database è la seguente. Non sono la stessa cosa. La tabella `utenti` è una struttura di persistenza definita nello schema SQLite, gestita dal `db_manager` e accessibile solo tramite `UtenteRepository`. Il modello `Utente` è un oggetto Python che vive in memoria durante l'esecuzione dell'applicazione. Il repository funge da traduttore tra i due mondi: legge una riga dalla tabella `utenti` e costruisce un'istanza del modello `Utente` con i campi corrispondenti; oppure riceve un'istanza del modello `Utente` e scrive i suoi campi in una riga della tabella. Questa separazione è il Repository Pattern: il Dominio non sa che esiste una tabella, e il database non sa che esiste un modello Python. Il repository è l'unico componente che conosce entrambi.

La classe `GiocatoreUmano` esistente nel Dominio non viene modificata per conoscere il modello `Utente`. Le due entità rimangono separate per la seguente ragione. `GiocatoreUmano` rappresenta un partecipante attivo dentro una partita in corso: gestisce cartelle, focus di navigazione, reclami di vittoria. `Utente` rappresenta un profilo persistente registrato nel sistema: ha un id stabile, una password, una data di creazione. Un `GiocatoreUmano` nasce quando si crea una partita e muore quando la partita termina. Un `Utente` nasce quando si registra e persiste indefinitamente. La Costituzione stabilisce che `GiocatoreBase` e `GiocatoreUmano` non vengono modificati in Fase 2 (sono elencati tra i layer NON toccati). Il collegamento tra i due avviene nel Controller: quando il Controller crea una partita, usa il nome dell'utente corrente (dalla sessione) per istanziare il `GiocatoreUmano`, e usa l'id dell'utente per associare la partita nel database. Ma il `GiocatoreUmano` non ha un riferimento diretto al modello `Utente`.

La relazione tra `Utente.id` (persistente nel database) e l'id del giocatore usato internamente da `GiocatoreBase` (temporaneo di sessione) è la seguente. `Utente.id` è un identificativo autoincrementale assegnato dal database al momento della registrazione. È stabile e permanente: lo stesso utente avrà sempre lo stesso `Utente.id` in tutte le partite, in tutte le sessioni, attraverso tutti i riavvii dell'applicazione. L'`id_giocatore` di `GiocatoreBase` è un indice di sessione assegnato dal Controller al momento della creazione della partita: il giocatore umano riceve `id_giocatore=1`, i bot ricevono `id_giocatore=2, 3, 4, ...`. Questo indice non ha relazione con il database: è un numero locale alla partita corrente, usato per distinguere i giocatori all'interno del roster. Alla prossima partita, il giocatore umano riceverà nuovamente `id_giocatore=1` indipendentemente da chi sia l'utente loggato. Il DESIGN_01 nella sezione 3 conferma esplicitamente questa distinzione: "l'id del giocatore nel Dominio è un indice di sessione, mentre utenti.id è un identificativo persistente".

---

## 4. L'AuthService: registrazione e login locale

L'`AuthService` è il componente che gestisce tutte le operazioni di autenticazione locale. Espone cinque operazioni.

### Registrazione nuovo utente

- **Nome operazione**: registra
- **Cosa riceve in ingresso**: nome (testo), password (testo), email (testo, opzionale)
- **Cosa restituisce in caso di successo**: il modello `Utente` appena creato, con tutti i campi valorizzati (incluso l'id assegnato dal database)
- **Cosa restituisce in caso di errore**: un risultato di fallimento con codice errore specifico. I casi di errore sono: nome vuoto o troppo corto, nome già esistente nel database, password troppo corta o non conforme ai requisiti minimi
- **Cosa fa internamente**: verifica che il nome non sia vuoto e rispetti una lunghezza minima. Chiede a `UtenteRepository.esiste_utente` se il nome è già registrato. Se il nome esiste già, restituisce un errore senza rivelare alcun dettaglio aggiuntivo. Se il nome è disponibile, calcola l'hash della password usando argon2. Costruisce un'istanza del modello `Utente` con il nome, l'email (se fornita), il password_hash e la data di creazione corrente. Chiede a `UtenteRepository.crea_utente` di persistere il profilo. Restituisce il modello `Utente` con l'id assegnato dal database.
- **Quale componente la chiama**: la `FinestraRegistrazione` attraverso il Controller, mai direttamente dall'Infrastructure

### Login con nome e password

- **Nome operazione**: login
- **Cosa riceve in ingresso**: nome (testo), password (testo)
- **Cosa restituisce in caso di successo**: il modello `Utente` corrispondente, estratto dal database. La sessione corrente viene aggiornata per riflettere l'utente loggato.
- **Cosa restituisce in caso di errore**: un risultato di fallimento con un messaggio generico di credenziali non valide. Il messaggio deve essere identico sia che il nome non esista sia che la password sia sbagliata, per non rivelare informazioni sull'esistenza degli account.
- **Cosa fa internamente**: chiede a `UtenteRepository.ottieni_utente_per_nome` di recuperare il profilo con il nome fornito. Se il profilo non esiste, restituisce un errore generico. Se il profilo esiste, verifica la password fornita contro il `password_hash` memorizzato usando la funzione di verifica di argon2. Se la verifica fallisce, restituisce lo stesso errore generico (identico a quando il nome non esiste). Se la verifica ha successo, aggiorna la sessione corrente con il modello `Utente` recuperato e restituisce il modello.
- **Quale componente la chiama**: la `FinestraLogin` attraverso il Controller

### Verifica se esiste già un utente con quel nome

- **Nome operazione**: esiste_utente
- **Cosa riceve in ingresso**: nome (testo)
- **Cosa restituisce**: vero o falso
- **Cosa fa internamente**: delega direttamente a `UtenteRepository.esiste_utente`. Questa operazione è una comodità per la `FinestraRegistrazione` per fornire feedback immediato all'utente durante la compilazione del form, senza attendere il tentativo di registrazione completo.
- **Quale componente la chiama**: la `FinestraRegistrazione` attraverso il Controller, per validazione preventiva

### Logout

- **Nome operazione**: logout
- **Cosa riceve in ingresso**: nulla
- **Cosa restituisce in caso di successo**: conferma che la sessione è stata chiusa
- **Cosa restituisce in caso di errore**: un risultato di fallimento se nessun utente era in sessione
- **Cosa fa internamente**: cancella il riferimento all'utente corrente dalla sessione. Non modifica il database: il profilo utente resta intatto. L'utente può fare login nuovamente in qualsiasi momento.
- **Quale componente la chiama**: la `FinestraPrincipale` (voce di menu o pulsante logout) attraverso il Controller

### Recupero dell'utente attualmente in sessione

- **Nome operazione**: ottieni_utente_corrente
- **Cosa riceve in ingresso**: nulla
- **Cosa restituisce**: il modello `Utente` attualmente in sessione, oppure nulla se nessun utente è loggato
- **Cosa fa internamente**: legge il riferimento all'utente corrente dalla sessione e lo restituisce. Non accede al database: il modello `Utente` è già in memoria dalla fase di login.
- **Quale componente la chiama**: qualsiasi componente del Controller o della Presentazione che abbia bisogno di sapere chi è l'utente attuale. In questa fase, viene chiamato dalla `FinestraPrincipale` (per mostrare il nome), dalla `FinestraConfigurazione` (per precompilare il campo nome e per verificare che esista un utente in sessione) e dalla logica di creazione partita nel Controller (per associare `Utente.id` alla partita nel database).

L'`AuthService` vive nel layer Controller (o Application), non nell'Infrastructure. La motivazione è la seguente. L'`AuthService` contiene logica applicativa: decide la politica di validazione del nome, la politica della password (lunghezza minima, complessità), la logica di verifica delle credenziali, la gestione della sessione. Non è una mera operazione di lettura/scrittura su database (quello è il ruolo del repository). Non è logica di business pura del Dominio (l'autenticazione non è una regola del gioco della tombola). È orchestrazione applicativa: coordina il repository, l'algoritmo di hashing e la sessione. La Costituzione nella scheda della Fase 2 indica "AuthService nel layer Application (o Controller, da decidere in DESIGN dedicato)": la scelta cade sul Controller perché il Controller è il layer che già orchestra le operazioni tra Dominio e Infrastructure, e l'`AuthService` segue esattamente questo pattern. L'`AuthService` riceve il `UtenteRepository` tramite dependency injection, come i repository vengono iniettati nel Controller.

La password dell'utente viene protetta con il seguente meccanismo. La password in chiaro digitata dall'utente non viene mai memorizzata: non viene scritta nel database, non viene salvata in una variabile di stato, non viene registrata nei log. Al momento della registrazione, la password viene passata alla funzione di hashing di argon2-cffi, che produce un hash unidirezionale. Questo hash è l'unico dato che viene scritto nel campo `password_hash` della tabella `utenti`. Al momento del login, la password digitata viene nuovamente passata alla funzione di verifica di argon2-cffi, che la confronta con l'hash memorizzato. Se corrispondono, il login ha successo; se non corrispondono, il login fallisce. L'hash unidirezionale garantisce che anche se il file database venisse letto da un soggetto non autorizzato, le password non sarebbero recuperabili. Questo meccanismo è necessario anche per l'uso locale (non solo online) perché il file database è un file sul disco dell'utente, accessibile a qualsiasi programma che giri sullo stesso sistema. In un contesto di accessibilità dove l'utente potrebbe condividere il PC o usare strumenti assistivi che catturano il testo sullo schermo, la protezione della password è una precauzione essenziale.

Il token di sessione JWT citato nella Costituzione nello stack tecnologico (PyJWT) non viene usato per il login locale in questa fase. La motivazione è triplice. Primo: JWT è progettato per l'autenticazione distribuita, dove un server deve verificare l'identità di un client senza mantenere stato. In un'applicazione locale single-process, la sessione è intrinsecamente "con stato" (il processo Python mantiene il modello `Utente` in memoria). Secondo: la Costituzione indica PyJWT come tecnologia della Fase 2 con posizione architetturale "Infrastructure — AuthService per token sessione", ma specifica anche "In Fase 8 lo stesso meccanismo JWT viene usato lato server", suggerendo che il caso d'uso primario è la comunicazione client-server. Terzo: introdurre JWT in questa fase aggiungerebbe complessità (gestione della chiave segreta, scadenza del token, refresh) senza risolvere un problema reale — il processo locale non ha bisogno di verificare un token crittografico per fidarsi della propria memoria. La decisione è quindi di rimandare JWT alla Fase 8, quando le sessioni distribuite lo renderanno necessario. In questa fase, la sessione corrente è gestita come riferimento in memoria al modello `Utente`, senza token.

---

## 5. Il concetto di sessione corrente

Durante il ciclo di vita dell'applicazione, il riferimento all'utente attualmente loggato viene conservato all'interno dell'`AuthService`. L'`AuthService` è il componente responsabile sia dell'autenticazione sia della gestione della sessione: quando un login ha successo, l'`AuthService` memorizza internamente il modello `Utente` restituito dal repository. Quando qualsiasi altro componente ha bisogno di sapere chi è l'utente corrente, chiede all'`AuthService` tramite l'operazione `ottieni_utente_corrente`. L'`AuthService` è istanziato una sola volta durante il ciclo di vita dell'applicazione (in `main.py`) e il suo riferimento viene passato ai componenti che ne hanno bisogno tramite dependency injection.

Se l'utente chiude l'applicazione senza fare logout esplicito, alla prossima apertura non viene considerato ancora loggato. La sessione non persiste tra riavvii dell'applicazione. La ragione è la seguente: la sessione è un riferimento in memoria al modello `Utente`, non un token persistente su disco. Quando il processo Python termina, quel riferimento viene distrutto. Al prossimo avvio, l'`AuthService` viene ricreato con sessione vuota e l'utente deve fare nuovamente login. Questa scelta è deliberata: in assenza di JWT (rimandato alla Fase 8), non esiste un meccanismo sicuro per persistere la sessione su disco senza esporre le credenziali. Un file di sessione in chiaro sarebbe un rischio di sicurezza; cifrarlo richiederebbe una chiave che a sua volta dovrebbe essere protetta. La soluzione più semplice e sicura è richiedere il login ad ogni avvio.

In questa fase non può esistere più di un utente loggato contemporaneamente. La ragione è duplice. Primo: la Costituzione stabilisce nella Sezione 1 (assunzioni implicite del Dominio) che esiste "un solo giocatore umano per partita". La struttura di `ottieni_giocatore_umano()` restituisce un singolo oggetto, non una lista. Fino alla Fase 7 (multiplayer locale), l'applicazione è progettata per un solo utente umano attivo. Secondo: l'`AuthService` mantiene un singolo riferimento all'utente corrente. Un secondo login sovrascrive il primo. Questa limitazione è coerente con il vincolo del singolo giocatore umano e verrà rimossa in Fase 7 quando la struttura di sessione supporterà profili multipli.

Il flusso di avvio dell'applicazione rispetto alla versione v0.14.0-alpha cambia nel modo seguente. In v0.14.0-alpha la sequenza è: avvio, `GameLogger.initialize()`, creazione `wx.App`, creazione `Vocalizzatore`, creazione `WxRenderer`, creazione `FinestraPrincipale` con quattro voci (Nuova partita, Impostazioni, Guida, Esci), il focus iniziale è sul pulsante "Nuova partita". Selezionando "Nuova partita" si apre direttamente la `FinestraConfigurazione` che chiede il nome del giocatore.

In v0.16.x la nuova sequenza è: avvio, `GameLogger.initialize()`, inizializzazione del database tramite `db_manager` (apertura connessione, creazione schema se necessario), creazione dell'`AuthService` con il `UtenteRepository`, creazione `wx.App`, creazione `Vocalizzatore`, creazione `WxRenderer`, creazione `FinestraPrincipale` con sei voci (Nuova partita, Registrazione, Login, Impostazioni, Guida, Esci). Se nessun utente è loggato, la `FinestraPrincipale` mostra un messaggio che invita a registrarsi o fare login. Selezionando "Nuova partita" senza un utente in sessione, l'applicazione non apre la `FinestraConfigurazione` ma mostra un messaggio che chiede di fare login prima. Dopo il login, selezionando "Nuova partita" si apre la `FinestraConfigurazione` con il campo nome precompilato e non modificabile. Al termine della partita, il ritorno alla `FinestraPrincipale` mostra il nome dell'utente ancora attivo nella sessione. L'utente può fare logout dalla `FinestraPrincipale` e poi login con un altro account, oppure registrare un nuovo account.

L'associazione effettiva tra `Utente.id` e il record della partita nel database non avviene in Fase 2. In Fase 2 il Controller sa chi è l'utente corrente (tramite `AuthService.ottieni_utente_corrente()`) ma `game_controller.py` non viene modificato in questa fase. L'aggancio operativo tra l'id utente e la tabella `partite` è responsabilità della Fase 4, quando `PartitaRepository` viene attivato nel Controller e `game_controller.py` riceve i repository come dipendenze iniettate.

---

## 6. Le nuove finestre wx e i cambiamenti alle esistenti

### FinestraRegistrazione (nuova)

- **Nome finestra**: `FinestraRegistrazione`
- **Tipo**: nuova
- **Scopo**: consente all'utente di creare un nuovo profilo locale fornendo nome, password e (opzionalmente) email
- **Campi e controlli principali**:
  - Titolo visivo "Registrazione nuovo utente" (StaticText)
  - Campo "Nome utente" (TextCtrl): campo di testo per il nome scelto dall'utente
  - Campo "Password" (TextCtrl con stile password): campo di testo mascherato per la password
  - Campo "Conferma password" (TextCtrl con stile password): secondo campo mascherato per la verifica della corrispondenza
  - Campo "Email" (TextCtrl): campo opzionale per l'indirizzo email
  - Pulsante "Registrati" (Button): conferma la registrazione
  - Pulsante "Annulla" (Button): torna alla FinestraPrincipale senza registrare
  - Area messaggi errori (StaticText): mostra eventuali errori di validazione
- **Accessibilità NVDA obbligatoria**:
  - Il campo "Nome utente" ha una label `wx.StaticText` "Nome utente:" immediatamente prima di esso nell'ordine di tabulazione, associata al controllo
  - Il campo "Password" ha una label `wx.StaticText` "Password:" immediatamente prima
  - Il campo "Conferma password" ha una label `wx.StaticText` "Conferma password:" immediatamente prima
  - Il campo "Email" ha una label `wx.StaticText` "Email (opzionale):" immediatamente prima
  - L'ordine di navigazione con Tab è: Nome utente, Password, Conferma password, Email, Registrati, Annulla
  - Il focus iniziale quando la finestra si apre è sul campo "Nome utente"
- **Come si apre**: dalla `FinestraPrincipale`, selezionando la voce "Registrazione"
- **Come si chiude**:
  - Premendo "Registrati" con dati validi: la registrazione viene completata, la finestra si chiude e il controllo torna alla `FinestraPrincipale`. L'utente appena registrato viene automaticamente loggato.
  - Premendo "Annulla": la finestra si chiude senza effetti e il controllo torna alla `FinestraPrincipale`
  - Premendo Escape: equivalente ad "Annulla"
  - Chiusura della finestra (X): equivalente ad "Annulla"

### FinestraLogin (nuova)

- **Nome finestra**: `FinestraLogin`
- **Tipo**: nuova
- **Scopo**: consente all'utente di autenticarsi con il proprio nome e password per accedere all'applicazione con il proprio profilo
- **Campi e controlli principali**:
  - Titolo visivo "Accedi al tuo profilo" (StaticText)
  - Campo "Nome utente" (TextCtrl): campo di testo per il nome
  - Campo "Password" (TextCtrl con stile password): campo di testo mascherato
  - Pulsante "Accedi" (Button): conferma il login
  - Pulsante "Annulla" (Button): torna alla FinestraPrincipale senza fare login
  - Area messaggi errori (StaticText): mostra eventuali errori di autenticazione
- **Accessibilità NVDA obbligatoria**:
  - Il campo "Nome utente" ha una label `wx.StaticText` "Nome utente:" immediatamente prima nell'ordine di tabulazione
  - Il campo "Password" ha una label `wx.StaticText` "Password:" immediatamente prima
  - L'ordine di navigazione con Tab è: Nome utente, Password, Accedi, Annulla
  - Il focus iniziale quando la finestra si apre è sul campo "Nome utente"
- **Come si apre**: dalla `FinestraPrincipale`, selezionando la voce "Login"
- **Come si chiude**:
  - Premendo "Accedi" con credenziali valide: il login viene completato, la finestra si chiude e il controllo torna alla `FinestraPrincipale` che mostra il nome dell'utente loggato. NVDA vocalizza un messaggio di benvenuto dopo che il widget del nome nella FinestraPrincipale è stato aggiornato.
  - Premendo "Accedi" con credenziali non valide: la finestra resta aperta, l'area messaggi mostra "Nome utente o password non validi." (messaggio identico sia che il nome non esista sia che la password sia sbagliata), NVDA vocalizza lo stesso messaggio
  - Premendo "Annulla": la finestra si chiude senza effetti e il controllo torna alla `FinestraPrincipale`
  - Premendo Escape: equivalente ad "Annulla"
  - Chiusura della finestra (X): equivalente ad "Annulla"

### FinestraPrincipale (modificata)

- **Tipo**: modificata
- **Cambiamenti rispetto alla versione attuale**:
  - Aggiunta della voce "Registrazione" (pulsante) tra "Nuova partita" e "Impostazioni", con acceleratore Ctrl+R
  - Aggiunta della voce "Login" (pulsante) tra "Registrazione" e "Impostazioni", con acceleratore Ctrl+L
  - Aggiunta di un'area di stato (StaticText) nella parte superiore della finestra che mostra "Utente: [nome]" quando un utente è loggato, oppure "Nessun utente loggato" quando la sessione è vuota. L'area di stato ha una label accessibile a NVDA
  - Quando un utente è loggato, i pulsanti "Registrazione" e "Login" vengono sostituiti visivamente e funzionalmente da un pulsante "Logout" con acceleratore Ctrl+L. In alternativa, i due pulsanti restano visibili ma vengono disabilitati e il pulsante "Logout" appare accanto all'area di stato
  - Selezionando "Nuova partita" quando nessun utente è loggato, il renderer vocalizza un messaggio di invito a fare login e non apre la FinestraConfigurazione
  - Il messaggio iniziale di benvenuto NVDA ("Tombola Stark. Scegli un'opzione.") viene esteso per indicare se un utente è loggato o meno

### FinestraConfigurazione (modificata)

- **Tipo**: modificata
- **Cambiamenti rispetto alla versione attuale**:
  - Prima di aprirsi, verifica tramite `AuthService.ottieni_utente_corrente()` che esista un utente in sessione. Se non esiste, non si apre (il controllo è gestito dalla FinestraPrincipale nel metodo `_on_nuova_partita`)
  - Il campo "Nome giocatore" (TextCtrl) viene precompilato con il nome dell'utente corrente e reso non modificabile (stile read-only). L'utente non deve più digitare il nome ad ogni partita: il nome proviene dalla sessione
  - La label del campo nome viene aggiornata da "Nome giocatore:" a "Giocatore:" per indicare che il valore è assegnato automaticamente
  - L'istanziazione di `ComandiSistema` resta invariata. L'`AuthService` non è una dipendenza diretta della FinestraConfigurazione: è il Controller (attraverso il flusso di creazione partita) che usa l'utente corrente dalla sessione

---

## 7. Aggiornamento di main.py

La Costituzione stabilisce esplicitamente che `main.py` viene aggiornato in Fase 2 per inizializzare il database all'avvio dell'applicazione e chiuderlo esplicitamente nel blocco `finally` accanto a `GameLogger.shutdown()`.

La nuova sequenza completa di inizializzazione in `main.py` dalla versione v0.16.x è la seguente, descritta passo per passo.

1. Parsing degli argomenti da linea di comando (invariato rispetto a v0.14.0-alpha).
2. Inizializzazione del `GameLogger` con la modalità debug se richiesta (invariato).
3. Inizializzazione del database tramite `db_manager`. Si crea l'istanza del `db_manager` passandogli il percorso del file database. Il `db_manager` apre la connessione e crea lo schema (le quattro tabelle) se il file non esiste o è vuoto. Se il file esiste già, il `db_manager` non ricrea le tabelle (idempotenza, come progettato in Fase 1).
4. Creazione del `UtenteRepository` concreto (implementazione SQLite) passandogli la connessione dal `db_manager`.
5. Creazione dell'`AuthService` passandogli il `UtenteRepository`. A questo punto l'`AuthService` è pronto per essere usato ma la sessione è vuota (nessun utente loggato).
6. Creazione dell'istanza `wx.App` (invariato).
7. Creazione del `Vocalizzatore` (invariato).
8. Creazione del `WxRenderer` con la finestra e il vocalizzatore (invariato nella struttura, ma il renderer potrebbe ricevere un riferimento all'`AuthService` o al componente di sessione per comunicare lo stato alla Presentazione).
9. Creazione della `FinestraPrincipale` con il renderer e un riferimento all'`AuthService` (o a un componente contenitore che lo espone). La `FinestraPrincipale` usa questo riferimento per verificare la sessione, per invocare registrazione/login/logout e per leggere il nome dell'utente corrente.
10. Show della finestra e avvio del `MainLoop` (invariato).
11. Nel blocco `finally`, dopo il `MainLoop`, chiusura esplicita del `db_manager` accanto a `GameLogger.shutdown()`. La chiusura del database viene invocata prima della chiusura del logger, in modo che eventuali errori di chiusura del database possano essere ancora registrati nel log.

L'inizializzazione del database in questa fase sostituisce l'inizializzazione differita progettata in Fase 1 nel senso seguente. In Fase 1, poiché `main.py` non veniva modificato, il `db_manager` era progettato per aprire la connessione in modo differito (alla prima richiesta di un repository). In Fase 2, poiché `main.py` viene aggiornato, il `db_manager` viene istanziato esplicitamente all'avvio. La compatibilità è garantita dal fatto che il `db_manager` è progettato per essere idempotente: se la connessione è già aperta, una seconda chiamata di apertura non ne crea una nuova. Il percorso di inizializzazione differita resta disponibile come fallback nel caso in cui un componente tenti di usare un repository prima che `main.py` abbia inizializzato il database, ma in condizioni normali il database è già pronto al passo 3.

La linea di confine tra ciò che viene costruito in `main.py` e ciò che viene costruito nelle finestre wx è la seguente. In `main.py` vengono costruiti: il `db_manager`, il `UtenteRepository`, l'`AuthService`, il `wx.App`, il `Vocalizzatore`, il `WxRenderer` e la `FinestraPrincipale`. Sono i componenti infrastrutturali e di bootstrap che devono esistere prima che qualsiasi finestra venga mostrata. Nelle finestre wx vengono costruiti: il `ComandiSistema` e il `ComandiGiocatoreUmano` (dentro `FinestraConfigurazione` e `FinestraGioco`, come avviene già in v0.14.0-alpha), le istanze di `Partita` e giocatori (creati dal Controller quando l'utente conferma la configurazione). Le finestre wx continuano a non conoscere il `db_manager` né i repository: interagiscono con l'`AuthService` solo per le operazioni di autenticazione e sessione, e con `ComandiSistema` per le operazioni di gioco.

---

## 8. Strategia di test

### Test dell'AuthService (`tests/application/test_auth_service.py`)

Si testa che l'`AuthService`, quando configurato con un `UtenteRepository` SQLite su database in memoria, esegua correttamente tutte le operazioni di autenticazione.

- Registrazione con nome valido e password valida: si verifica che il metodo `registra` restituisca un modello `Utente` con id non nullo, nome corretto, e password_hash non uguale alla password in chiaro
- Registrazione con nome già esistente: si verifica che un secondo tentativo di registrazione con lo stesso nome restituisca un errore specifico e non crei un secondo record nel database
- Login con credenziali corrette: si registra un utente, poi si invoca `login` con lo stesso nome e la stessa password. Si verifica che il risultato sia il modello `Utente` con i dati corretti e che `ottieni_utente_corrente` restituisca lo stesso modello
- Login con password sbagliata: si registra un utente, poi si invoca `login` con il nome corretto e una password diversa. Si verifica che il risultato sia un errore e che il messaggio di errore sia identico a quello del caso "nome inesistente" (senza rivelare se il nome esiste)
- Login con nome inesistente: si invoca `login` con un nome mai registrato. Si verifica che il risultato sia un errore e che il messaggio di errore sia identico a quello del caso "password sbagliata"
- Logout: si registra un utente, si fa login, poi si invoca `logout`. Si verifica che `ottieni_utente_corrente` restituisca nulla dopo il logout
- Login corretto seguito da logout e nuovo login: si verifica la sequenza completa di login, logout e secondo login con o senza lo stesso utente, verificando che la sessione rifletta correttamente l'utente loggato ad ogni passo

I test non dipendono dalla UI wx perché l'`AuthService` non importa wxPython. Viene istanziato nel test passandogli un `UtenteRepository` costruito su un `db_manager` con database in memoria.

L'isolamento tra test è garantito dal fatto che ogni test crea un database SQLite in memoria dedicato (che viene distrutto alla fine del test) o una cartella temporanea con file database che viene rimossa al teardown.

Un test si considera superato quando: l'operazione produce il risultato atteso (modello `Utente` o errore), il database contiene esattamente i record attesi (nessun record duplicato, nessun campo nullo non previsto), e la sessione riflette correttamente lo stato (utente loggato o nessun utente).

### Test del UtenteRepository (già progettato in Fase 1)

I test del `UtenteRepository` sono stati progettati nel DESIGN_01. In Fase 2 questi test vengono estesi per verificare le operazioni specifiche dell'autenticazione.

- Si verifica che `crea_utente` accetti un utente con `password_hash` valorizzato e lo persista correttamente
- Si verifica che `ottieni_utente_per_nome` restituisca il modello con il `password_hash` corretto per la verifica
- Si verifica che `aggiorna_utente` possa aggiornare i campi `email` e `password_hash`
- Si verifica che `esiste_utente` restituisca vero dopo una registrazione e falso per un nome mai registrato

I test non dipendono dalla UI per la stessa ragione della Fase 1: il repository riceve la connessione dal `db_manager` che non ha relazione con wxPython.

### Test della sessione corrente (`tests/application/test_sessione.py`)

Si testa che la gestione della sessione corrente all'interno dell'`AuthService` funzioni correttamente in isolamento.

- Si verifica che all'avvio (prima di qualsiasi login) `ottieni_utente_corrente` restituisca nulla
- Si verifica che dopo un login valido `ottieni_utente_corrente` restituisca il modello dell'utente loggato
- Si verifica che dopo un logout `ottieni_utente_corrente` restituisca nulla
- Si verifica che un secondo login sovrascriva il primo (sessione singola)
- La sessione non persiste tra due avvii consecutivi dell'applicazione: in Fase 2 la sessione è esclusivamente in memoria. Non esiste un test di persistenza della sessione tra riavvii perché il design lo esclude esplicitamente. Ogni nuovo `AuthService` parte con sessione vuota.

### Test di integrazione Controller (`tests/application/test_controller_utente_integration.py`)

Si testa che il flusso completo (login, creazione partita, associazione utente) funzioni senza avviare wxPython.

- Si registra un utente tramite `AuthService`, si fa login, si invoca `crea_partita_standard` con il nome dell'utente corrente (letto dalla sessione). Si verifica che la partita venga creata con il nome corretto.
- Si esegue un turno e si verifica che non si producano errori di persistenza (quando il Controller è configurato con i repository).

I test non dipendono dalla UI perché il test istanzia direttamente l'`AuthService`, il `UtenteRepository`, il `ComandiSistema` e il `game_controller` senza creare finestre wx.

### Scenari di test obbligatori

- **Registrazione con nome già esistente**: si registra un utente con nome "Mario", poi si tenta di registrare un secondo utente con lo stesso nome "Mario". Il secondo tentativo deve fallire con un messaggio specifico indicante che il nome è già in uso.
- **Login con password sbagliata**: si registra un utente con nome "Mario" e password "segreta123", poi si tenta il login con nome "Mario" e password "sbagliata456". Il login deve fallire con un messaggio generico ("Nome utente o password non validi") senza rivelare che il nome "Mario" esiste nel database.
- **Login corretto seguito da logout e nuovo login**: si registra un utente, si fa login, si verifica la sessione, si fa logout, si verifica che la sessione sia vuota, si fa nuovamente login, si verifica che la sessione sia nuovamente attiva con i dati corretti.
- **Sessione persistente tra due avvii consecutivi dell'applicazione**: questo scenario non è applicabile in Fase 2 perché la sessione non persiste (come documentato nella Sezione 5). Un test verifica esplicitamente che creando un nuovo `AuthService` (simulando un riavvio) la sessione sia vuota anche se l'utente non ha fatto logout nella sessione precedente.

---

## 9. Struttura delle cartelle e dei file

La struttura seguente mostra i file introdotti o modificati da questa fase.

### File nuovi introdotti da questa fase

- `bingo_game/utente.py` — Modello `Utente` del Dominio, con i campi `id`, `nome`, `email`, `password_hash`, `data_creazione`, `crediti`. La cartella `bingo_game/domain/` non viene creata in questa fase. Il modello `Utente` viene posizionato direttamente in `bingo_game/utente.py`, coerentemente con la posizione degli altri file di Dominio esistenti (`partita.py`, `tabellone.py`, ecc.). Una eventuale ristrutturazione in sottocartelle è una decisione separata che richiede un documento di refactoring dedicato.
- `bingo_game/auth_service.py` — `AuthService` nel layer Controller, con le operazioni `registra`, `login`, `esiste_utente`, `logout`, `ottieni_utente_corrente`
- `bingo_game/ui/finestra_registrazione.py` — Finestra wxPython per la registrazione di un nuovo utente
- `bingo_game/ui/finestra_login.py` — Finestra wxPython per il login di un utente esistente
- `tests/application/__init__.py` — Package marker per i test del layer Application/Controller
- `tests/application/test_auth_service.py` — Test unitari per l'`AuthService`
- `tests/application/test_sessione.py` — Test per la gestione della sessione corrente
- `tests/application/test_controller_utente_integration.py` — Test di integrazione Controller + AuthService + UtenteRepository
- `tests/test_utente.py` — Test unitari per il modello `Utente` del Dominio

La convenzione adottata è: `tests/infrastructure/` per i test dei repository SQLite (stabilita nel DESIGN_01), `tests/application/` per i test dei servizi applicativi come `AuthService`. I test del `UtenteRepository` (già progettati nel DESIGN_01 in `tests/infrastructure/`) restano dove sono: non si spostano e non si duplicano.

### File esistenti modificati da questa fase

- `main.py` — Aggiunta inizializzazione `db_manager`, `UtenteRepository`, `AuthService` all'avvio; chiusura del database nel blocco `finally`
- `bingo_game/ui/finestra_principale.py` — Aggiunta voci "Registrazione", "Login" (o "Logout" se loggato); area di stato con nome utente; logica di verifica sessione su "Nuova partita"
- `bingo_game/ui/finestra_configurazione.py` — Campo nome precompilato e read-only con il nome dell'utente corrente dalla sessione
- `bingo_game/ui/locales/it.py` — Aggiunta chiavi di testo per i messaggi delle nuove finestre (errori di registrazione, errori di login, messaggi di benvenuto, messaggio di sessione richiesta)
- `requirements.txt` — Aggiunta dipendenza `argon2-cffi`
- `bingo_game/infrastructure/repositories/sqlite_utente_repository.py` — Aggiornato per gestire la scrittura del campo `password_hash` al momento della registrazione e la lettura dello stesso al momento del login. In Fase 1 questo campo era nullable e mai popolato; in Fase 2 diventa obbligatorio per ogni utente registrato.

### File esistenti non toccati da questa fase

- `bingo_game/game_controller.py` — Non modificato. Il Controller di gioco non cambia in Fase 2. L'associazione tra utente e partita avverrà tramite l'`AuthService` che il Controller consulta, non tramite modifiche alle funzioni di `game_controller.py`
- `bingo_game/comandi_partita.py` — Non modificato. Le facade `ComandiSistema` e `ComandiGiocatoreUmano` mantengono la stessa interfaccia
- `bingo_game/partita.py` — Non modificato (Dominio di gioco non toccato)
- `bingo_game/tabellone.py` — Non modificato
- `bingo_game/cartella.py` — Non modificato
- `bingo_game/players/giocatore_base.py` — Non modificato
- `bingo_game/players/giocatore_umano.py` — Non modificato
- `bingo_game/players/giocatore_automatico.py` — Non modificato
- `bingo_game/ui/finestra_gioco.py` — Non modificato (il flusso di gioco è invariato)
- `bingo_game/ui/finestra_aiuto_tasti_rapidi.py` — Non modificato
- `bingo_game/ui/finestra_guida_regole.py` — Non modificato
- `bingo_game/ui/dialogo_ricerca.py` — Non modificato
- `bingo_game/ui/renderers/base_renderer.py` — Non modificato (il contratto astratto del renderer non cambia in questa fase)
- `bingo_game/ui/renderers/renderer_wx.py` — Non modificato nella struttura degli handler di gioco. L'unico aggiornamento possibile riguarda il metodo `mostra_messaggio_sistema` per i nuovi messaggi, ma il contratto resta invariato

---

## 10. Decisioni deliberatamente rinviate

### Introduzione dei JWT per le sessioni online

- **Cosa non si decide ora**: il formato, la durata, la chiave segreta e il meccanismo di refresh dei token JWT per l'autenticazione distribuita
- **Perché non si decide ora**: JWT è progettato per la comunicazione client-server. In Fase 2 non esiste un server. La sessione è un riferimento in memoria nel processo locale. Introdurre JWT senza un server significherebbe implementare una complessità crittografica senza un problema reale da risolvere.
- **In quale fase verrà decisa**: Fase 8 (Pre-Online: API Layer e Auth Distribuita)

### Recupero password

- **Cosa non si decide ora**: il meccanismo di recupero della password per utenti che l'hanno dimenticata
- **Perché non si decide ora**: il recupero password richiede un canale di comunicazione esterno (email, SMS, domanda segreta). In Fase 2 l'applicazione è interamente locale e non ha un server email. Un meccanismo di "reset password" locale significherebbe permettere a chiunque abbia accesso al PC di resettare la password di qualsiasi profilo, eliminando il senso stesso della protezione con password. L'unica soluzione ragionevole è fornire il recupero quando esiste un canale email verificato, introdotto con il server online.
- **In quale fase verrà decisa**: Fase 8, quando l'infrastruttura email del server lo renderà possibile

### Gestione di più utenti loggati contemporaneamente

- **Cosa non si decide ora**: come più utenti umani possono essere loggati e giocare nella stessa partita sullo stesso PC
- **Perché non si decide ora**: la Fase 2 mantiene il vincolo di un solo giocatore umano per partita, ereditato dal Dominio esistente (il metodo `ottieni_giocatore_umano` restituisce un singolo oggetto). La gestione multi-utente richiede prima la rimozione di questo vincolo nel Dominio, la modifica del Controller per gestire una lista di giocatori umani, e un meccanismo di "profilo attivo" o di "switch rapido" tra sessioni.
- **In quale fase verrà decisa**: Fase 7 (Modalità Multiplayer Locale)

### Sincronizzazione del profilo utente con il server online

- **Cosa non si decide ora**: come il profilo utente locale viene sincronizzato con un profilo sul server PostgreSQL, quali campi hanno priorità in caso di conflitto, e come viene gestito il merge tra dati locali e dati remoti
- **Perché non si decide ora**: la sincronizzazione richiede un server operativo, un protocollo di comunicazione definito e una strategia di risoluzione dei conflitti. Nessuno di questi elementi esiste prima della Fase 8.
- **In quale fase verrà decisa**: Fase 8 (Pre-Online: API Layer e Auth Distribuita)

### Avatar o immagine del profilo utente

- **Cosa non si decide ora**: se il profilo utente avrà un avatar, un'icona o un'immagine associata
- **Perché non si decide ora**: l'utente primario dell'applicazione è non vedente e usa NVDA. Un avatar visivo non ha utilità funzionale per lo use case primario. Tuttavia, in futuro (multiplayer online) potrebbe essere utile per gli altri giocatori vedenti. La decisione viene rimandata a quando il contesto multiplayer la renderà pertinente.
- **In quale fase verrà decisa**: Fase 8 o Fase 9, nel contesto del profilo utente online

---

## 11. Assunzioni e incertezze

### Assunzione 1 — La FinestraPrincipale può ricevere un riferimento all'AuthService

- **Cosa si assume**: la `FinestraPrincipale` può ricevere un riferimento all'`AuthService` (o a un oggetto contenitore che lo espone) nel suo costruttore, senza violare il vincolo che la Presentazione non importa direttamente dall'Infrastructure
- **Cosa succederebbe se l'assunzione fosse sbagliata**: se l'`AuthService` fosse troppo accoppiato all'Infrastructure (perché importa `UtenteRepository` concreto anziché l'interfaccia), passarlo alla `FinestraPrincipale` potrebbe creare una dipendenza transitiva non voluta. In quel caso, sarebbe necessario introdurre una facade aggiuntiva nel Controller che isoli la Presentazione dall'AuthService
- **Quando si scoprirà se l'assunzione è corretta**: durante l'implementazione, al momento di definire la firma del costruttore di `FinestraPrincipale` e di verificare gli import

### Assunzione 2 — Il campo nome nella FinestraConfigurazione può essere reso read-only

- **Cosa si assume**: il campo `wx.TextCtrl` per il nome del giocatore nella `FinestraConfigurazione` può essere reso non modificabile (stile `wx.TE_READONLY`) senza effetti collaterali sulla navigazione NVDA o sull'ordine di tabulazione
- **Cosa succederebbe se l'assunzione fosse sbagliata**: NVDA potrebbe non annunciare il contenuto di un TextCtrl read-only nello stesso modo di un TextCtrl editabile, o il focus potrebbe saltare il campo. In quel caso, il design alternativo è usare un `wx.StaticText` per mostrare il nome (non editabile per definizione) al posto del TextCtrl
- **Quando si scoprirà se l'assunzione è corretta**: durante il primo test di accessibilità con NVDA sulla nuova FinestraConfigurazione

### Assunzione 3 — argon2-cffi è installabile senza compilazione C su Windows 11

- **Cosa si assume**: la libreria argon2-cffi fornisce wheel precompilati per Windows 11 su Python 3.11, quindi l'installazione tramite pip avviene senza richiedere un compilatore C
- **Cosa succederebbe se l'assunzione fosse sbagliata**: l'utente o il sistema CI dovrebbe avere Visual C++ Build Tools installato per compilare le estensioni C di argon2-cffi. Questo aggiungerebbe un requisito di sistema non documentato
- **Quando si scoprirà se l'assunzione è corretta**: al primo `pip install argon2-cffi` su una macchina Windows 11 pulita

### Assunzione 4 — Il default "Giocatore" nel campo nome può essere sostituito senza effetti collaterali

- **Cosa si assume**: il valore predefinito "Giocatore" nel campo nome della `FinestraConfigurazione` non è usato come sentinella o valore speciale in nessun altro punto del codice. Sostituirlo con il nome dell'utente dalla sessione non rompe alcun controllo
- **Cosa succederebbe se l'assunzione fosse sbagliata**: se qualche componente verificasse il nome "Giocatore" come caso speciale (fallback, nome bot, test hardcoded), la sostituzione produrrebbe comportamenti imprevisti
- **Quando si scoprirà se l'assunzione è corretta**: durante l'implementazione, cercando nel codice tutti gli usi della stringa "Giocatore" (da verificare con grep)

### Assunzione 5 — Il renderer non ha bisogno di un aggiornamento di contratto per i messaggi di autenticazione

- **Cosa si assume**: i nuovi messaggi dell'AuthService (errori di login, benvenuto dopo login, invito a registrarsi) possono essere gestiti tramite il metodo `mostra_messaggio_sistema` già presente nel contratto `BaseRenderer`, senza aggiungere nuovi metodi astratti
- **Cosa succederebbe se l'assunzione fosse sbagliata**: se i messaggi di autenticazione richiedessero un trattamento diverso (per esempio un handler specifico con aggiornamento widget dedicato), sarebbe necessario estendere `BaseRenderer` con un nuovo metodo astratto e aggiornare `WxRenderer` di conseguenza
- **Quando si scoprirà se l'assunzione è corretta**: durante l'implementazione delle nuove finestre, verificando se `mostra_messaggio_sistema` è sufficiente per tutti i feedback dell'autenticazione

### Assunzione 6 — La FinestraPrincipale attuale consente l'aggiunta di nuovi pulsanti senza ristrutturare il layout

- **Cosa si assume**: il sizer verticale della `FinestraPrincipale` attuale può ospitare due pulsanti aggiuntivi (Registrazione e Login) e un'area di stato senza richiedere un cambio di layout strutturale o un ridimensionamento della finestra
- **Cosa succederebbe se l'assunzione fosse sbagliata**: se lo spazio verticale non fosse sufficiente, sarebbe necessario ridimensionare la finestra o introdurre uno scrollbar, entrambi con implicazioni per l'accessibilità NVDA (lo scrollbar richierebbe navigazione aggiuntiva)
- **Quando si scoprirà se l'assunzione è corretta**: durante l'implementazione, quando i nuovi pulsanti vengono aggiunti al sizer e testati visivamente

---

## 12. Istruzioni specifiche per l'agente implementatore

- Non salvare mai la password in chiaro in nessun campo del database, nessuna variabile di stato dell'applicazione, nessun log (né di sistema né di errore), nessun file temporaneo e nessun output di debug. L'unica forma ammessa della password è l'hash prodotto da argon2-cffi.

- Non registrare nei log del `GameLogger` il valore del campo password nemmeno a livello DEBUG. I sub-logger `tombola_stark.system` e `tombola_stark.errors` possono registrare eventi di autenticazione (login riuscito, login fallito, registrazione completata) ma mai il valore della password o del password_hash.

- Non mostrare mai all'utente se il nome esiste o non esiste in caso di login fallito. Il messaggio di errore deve essere identico sia che il nome sia sbagliato sia che la password sia sbagliata. Il testo standard è "Nome utente o password non validi." — nessuna variante, nessun dettaglio aggiuntivo.

- La `FinestraLogin` deve avere il focus iniziale sul campo nome utente, non sul pulsante Conferma. Il metodo `SetFocus()` deve essere chiamato sul TextCtrl del nome utente dopo che la finestra è visibile, usando `wx.CallAfter`.

- La `FinestraRegistrazione` deve avere il focus iniziale sul campo nome utente, con la stessa regola di SetFocus della FinestraLogin.

- Il messaggio di benvenuto NVDA dopo il login deve essere vocalizzato dopo che il widget dell'area di stato nella `FinestraPrincipale` è stato aggiornato con il nome dell'utente. L'ordine è: aggiornare il SetLabel dell'area di stato, poi chiamare il vocalizzatore. Questo rispetta il Vincolo 1 della Costituzione (regola testo-widget-voce).

- Ogni nuovo campo di input nelle finestre `FinestraRegistrazione` e `FinestraLogin` deve avere una `wx.StaticText` label esplicita immediatamente precedente nell'ordine di tabulazione. Verificare dopo l'implementazione che NVDA legga la label prima del contenuto del campo quando si naviga con Tab.

- I campi password nelle finestre di registrazione e login devono usare lo stile `wx.TE_PASSWORD` per mascherare il testo digitato. Questo è importante non solo visivamente ma anche per impedire che strumenti di cattura schermo o screen reader non autorizzati leggano la password in chiaro dal widget.

- Non usare `print()` nel file `auth_service.py`. Usare il sub-logger `tombola_stark.system` per gli eventi di autenticazione e `tombola_stark.errors` per le eccezioni.

- Aggiungere tutte le nuove stringhe di testo per le finestre di registrazione e login nel catalogo `bingo_game/ui/locales/it.py`. Non scrivere stringhe italiane inline nei costruttori delle finestre o nei metodi handler.

- L'`AuthService` deve ricevere il `UtenteRepository` tramite il suo costruttore (dependency injection). Non deve istanziare autonomamente il repository o il `db_manager`. Il wiring avviene esclusivamente in `main.py`.

- Non modificare la tabella `utenti` nel file di schema del `db_manager`. Lo schema è stato definito in Fase 1 con i campi `email` e `password_hash` già presenti come nullable. In Fase 2 questi campi vengono popolati ma lo schema non cambia.

- Dopo l'implementazione, eseguire una verifica grep per confermare che la stringa "password" non compaia in nessun messaggio di log generato dall'applicazione (escludendo i nomi dei campi nei moduli di test e nell'interfaccia utente dove "password" è un'etichetta visiva).

- Prima di considerare completata l'implementazione, eseguire un test manuale NVDA sulle due nuove finestre verificando: il focus iniziale è sul campo nome, Tab naviga nell'ordine progettato, ogni campo annuncia la propria label, il messaggio di errore viene vocalizzato, il messaggio di benvenuto post-login viene vocalizzato dopo l'aggiornamento del widget.

---

*Documento prodotto da Agent-Design — Tombola Stark Framework v1.10.3*
*Baseline di riferimento: v0.14.0-alpha — 15 aprile 2026*
