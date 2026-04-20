---
feature: statistiche-gioco-storico
agent: Agent-Design
status: DRAFT
version: v0.17.x
date: 2026-04-15
---

# DESIGN 03 — Fase 3: Statistiche di Gioco e Storico

> **Data**: 15 aprile 2026
> **Versione target**: v0.17.x
> **Tipo documento**: Design di fase
> **Fase roadmap**: 3 di 9
> **Dipende da**: Fase 1 (DESIGN_01_FASE1_INFRASTRUCTURE_LAYER_2026-04-15.md) e Fase 2 (DESIGN_02_FASE2_SISTEMA_UTENTE_2026-04-15.md)
> **Sblocca**: Fase 4, Fase 5
> **Documento padre**: DESIGN_COSTITUZIONE_ROADMAP_MULTIPLAYER_2026-04-14.md
> **Stato**: BOZZA
> **Autore analisi**: Agent-Design

---

## 1. Scopo e confini di questa fase

Questa fase introduce il sistema di statistiche di gioco e storico partite nell'applicazione Tombola Stark. Alla versione v0.16.x (prodotta dalla Fase 2) l'applicazione consente a un utente registrato di giocare partite complete contro bot, ma al termine di ciascuna partita nessun dato viene scritto nel database: il risultato viene mostrato a video tramite il renderer, registrato nel log file di sessione e dimenticato alla chiusura della finestra di gioco. Questa fase colma questa lacuna collegando il flusso di fine partita al layer Infrastructure per la persistenza dei risultati.

Lo scopo concreto è quadruplice. Primo: il salvataggio automatico del risultato di ogni partita nella tabella `statistiche` del database, invocato dal Controller dopo che `partita_terminata()` restituisce True. Secondo: la creazione della `FinestraStatistiche` in wxPython con piena accessibilità NVDA, che mostra partite giocate, vinte, perse, premi per tipo (ambo, terno, quaterna, cinquina, tombola) e la miglior partita per numero minimo di turni. Terzo: l'aggiornamento del menu di `FinestraPrincipale` per esporre la voce "Statistiche" con acceleratore Ctrl+T. Quarto: l'esportazione opzionale delle statistiche come file `.txt` leggibile.

Cosa questa fase NON fa. Non modifica il motore di gioco: `Partita`, `Tabellone`, `Cartella`, `GiocatoreBase`, `GiocatoreUmano` e `GiocatoreAutomatico` restano completamente invariati. Non altera il flusso di gioco nella `FinestraGioco`: il ciclo di estrazione e verifica premi non viene toccato. Non introduce statistiche aggregate globali tra utenti: nessuna classifica, nessun leaderboard, nessun confronto tra profili. Le statistiche globali appartengono alla Fase 9 (Multiplayer Online). Non introduce crediti né premi economici legati alle performance: quello appartiene alla Fase 5 (Sistema Crediti Virtuali). Non gestisce la visualizzazione di statistiche per partite non concluse o sospese: il salvataggio dello stato intermedio è compito della Fase 4 (Salvataggio e Ripresa della Partita).

I layer toccati, come indicato dalla Costituzione nella scheda della Fase 3, sono tre. Il Controller (`bingo_game/game_controller.py`) viene aggiornato per invocare il salvataggio delle statistiche al termine della partita, protetto dal flag `_partita_terminata_logged` già esistente. La facade `ComandiSistema` in `bingo_game/comandi_partita.py` viene estesa con un metodo pubblico per la lettura delle statistiche utente. L'Infrastructure viene attivata operativamente: il `SqliteStatisticheRepository` (creato in Fase 1 con operazioni CRUD di base) riceve il completamento delle query aggregate nel metodo `ottieni_statistiche_aggregate()`. La Presentazione riceve la nuova `FinestraStatistiche` e l'aggiornamento del menu in `FinestraPrincipale`.

I layer NON toccati sono i seguenti. Il Dominio di gioco nella sua interezza: `bingo_game/partita.py`, `bingo_game/tabellone.py`, `bingo_game/cartella.py`, `bingo_game/players/giocatore_base.py`, `bingo_game/players/giocatore_umano.py`, `bingo_game/players/giocatore_automatico.py` — nessuna di queste classi importa o conosce `StatisticheRepository`. Il flusso di gioco nella Presentazione: `bingo_game/ui/finestra_gioco.py`, `bingo_game/ui/finestra_aiuto_tasti_rapidi.py`, `bingo_game/ui/finestra_guida_regole.py`, `bingo_game/ui/dialogo_ricerca.py` — il ciclo di estrazione e verifica premi non viene alterato. Le finestre introdotte in Fase 2: `bingo_game/ui/finestra_registrazione.py`, `bingo_game/ui/finestra_login.py` — la logica di autenticazione non viene toccata. Il contratto del renderer: `bingo_game/ui/renderers/base_renderer.py` e `bingo_game/ui/renderers/renderer_wx.py` — il contratto astratto non cambia e il renderer non conosce il concetto di statistiche. Il servizio di autenticazione `bingo_game/auth_service.py` — viene solo consultato in lettura dal Controller per ottenere l'`utente_id` corrente, non modificato. Il gestore del database `bingo_game/infrastructure/database/db_manager.py` — la connessione e lo schema sono già inizializzati in Fase 2 e non richiedono modifiche. Il file `main.py` — la sequenza di avvio è già completa dopo Fase 2 e non viene toccata in questa fase. Il file `requirements.txt` — nessuna nuova dipendenza esterna è introdotta in questa fase.

---

## 2. Analisi del flusso attuale di fine partita

Questa sezione descrive in dettaglio come oggi termina una partita a livello di codice, individuando il punto esatto in cui inserire il salvataggio delle statistiche senza alterare il flusso esistente.

Il metodo `partita_terminata` in `bingo_game/game_controller.py` è un sensore di stato che verifica se la partita è nello stato "terminata". La sua implementazione legge lo stato dalla `Partita` tramite `partita.is_terminata()` e, se il risultato è `True`, controlla il flag di modulo `_partita_terminata_logged`. Se il flag è `False`, il metodo registra nel log il messaggio "Partita terminata." tramite `_log_safe` e imposta il flag a `True` per evitare log duplicati nelle chiamate successive. Il flag `_partita_terminata_logged` viene resettato a `False` da `crea_partita_standard` alla creazione di ogni nuova partita, garantendo che il meccanismo anti-duplicato funzioni correttamente attraverso sessioni multiple di gioco.

Il metodo `esegui_turno_sicuro` in `bingo_game/game_controller.py` esegue un turno completo e, quando rileva una tombola o l'esaurimento dei numeri, registra nel log il riepilogo finale tramite `_log_game_summary`. Similmente, il metodo `esegui_fase_verifica_sicura` è la versione bifasica dello stesso scenario: al termine della fase di verifica, se si rileva tombola o fine numeri, viene chiamato `_log_game_summary`. Questi due metodi sono i punti in cui il Controller rileva attivamente la terminazione della partita. Tuttavia, il flusso di Presentazione (`FinestraGioco`) utilizza `partita_terminata` come sensore per decidere quando uscire dal ciclo di gioco e mostrare il report finale tramite il renderer.

Il metodo `ottieni_stato_sintetico` in `bingo_game/game_controller.py` restituisce un dizionario con le seguenti chiavi verificate nella versione v0.14.0-alpha: `stato_partita` (stringa, uno tra "non_iniziata", "in_corso", "terminata"), `ultimo_numero_estratto` (intero o None), `numeri_estratti` (lista di interi), `giocatori` (lista di dizionari con lo stato per ciascun giocatore), `premi_gia_assegnati` (lista ordinata di chiavi stringa). Da questo dizionario si derivano i turni giocati (lunghezza della lista `numeri_estratti`) e l'elenco dei giocatori con il loro stato.

L'attributo `storico_premi` di `Partita` è una lista di dizionari, ciascuno con le chiavi: `giocatore` (nome stringa del vincitore), `id_giocatore` (intero, indice di sessione), `cartella` (indice intero della cartella vincente), `premio` (stringa del tipo di premio: "ambo", "terno", "quaterna", "cinquina", "tombola"), `riga` (indice intero della riga vincente o None), `turno` (intero, numero del turno in cui il premio è stato assegnato). Filtrando questa lista per il nome del giocatore umano si ottengono tutti i premi vinti dall'utente corrente nella partita, con il dettaglio per tipo.

La ragione per cui oggi nessuno di questi dati viene scritto su disco è l'assenza totale del collegamento operativo tra il Controller e il layer Infrastructure per le statistiche. La Fase 1 ha creato la tabella `statistiche` nel database e l'implementazione `SqliteStatisticheRepository`, ma il Controller non invoca mai il repository. La Fase 2 ha introdotto l'utente persistente e l'inizializzazione del database in `main.py`, ma non ha collegato il flusso di fine partita al repository. Questa fase completa il collegamento.

Il punto di aggancio naturale per il salvataggio delle statistiche è all'interno del metodo `partita_terminata` in `bingo_game/game_controller.py`, immediatamente prima della riga `_partita_terminata_logged = True`. Questo punto è l'unico corretto per tre ragioni. Prima: il flag `_partita_terminata_logged` garantisce che il salvataggio avvenga esattamente una volta per partita, senza duplicati. Seconda: a questo punto la partita è certamente terminata (`partita.is_terminata()` ha già restituito `True`), quindi tutti i dati sono definitivi. Terza: il salvataggio avviene nel Controller, non nella Presentazione, rispettando il Vincolo 5 della Costituzione (il renderer non accede direttamente all'Infrastructure).

---

## 3. Il modello di dati per le statistiche

Lo schema logico del record statistiche descrive la struttura di ogni riga che viene scritta nella tabella `statistiche` del database al termine di una partita conclusa. I campi minimi richiesti dalla Costituzione (Sezione 2, scheda Fase 3) sono cinque: `utente_id`, `data`, `turni`, `premi_vinti`, `ha_tombola`. Questa sezione espande la lista a quattordici campi, motivando ogni aggiunta.

Il campo `id` è un numero intero autoincrementale, obbligatorio, che serve come chiave primaria del record. È un requisito strutturale del database, presente in tutte le tabelle dello schema (coerentemente con la convenzione stabilita nel DESIGN_01).

Il campo `utente_id` è un numero intero, obbligatorio, che referenzia `utenti.id`. Identifica l'utente proprietario del record statistico. È uno dei cinque campi minimi della Costituzione. Il valore viene ottenuto dal Controller tramite `AuthService.ottieni_utente_corrente().id` al momento del salvataggio.

Il campo `partita_id` è un numero intero, obbligatorio, che referenzia `partite.id`. Identifica la partita specifica da cui il record è stato generato. Questo campo non è nei cinque minimi della Costituzione ma è necessario per due ragioni: consente di correlare le statistiche con i dati completi della partita nella tabella `partite` (utile per la Fase 4 quando i checkpoint saranno disponibili) e permette di verificare l'unicità del record (una sola riga in `statistiche` per ogni partita conclusa).

Il campo `data` è una data e ora, obbligatorio. Registra il timestamp del momento in cui il record statistico è stato scritto nel database. È uno dei cinque campi minimi. Il valore viene calcolato al momento della chiamata a `registra_statistiche_partita`, non derivato dalla Partita (che non gestisce timestamp).

Il campo `turni` è un numero intero, obbligatorio. Registra il numero di turni giocati prima della terminazione. È uno dei cinque campi minimi. Il valore si deriva dalla lunghezza della lista `numeri_estratti` restituita da `ottieni_stato_sintetico`, oppure dalla variabile di modulo `_turno_corrente` in `game_controller.py`. La prima derivazione è preferita perché è un dato di Dominio, non una variabile di stato del Controller.

Il campo `premi_vinti` è un numero intero, obbligatorio. Registra il numero totale di premi vinti dal giocatore umano nella partita. È uno dei cinque campi minimi. Il valore si deriva contando i record in `storico_premi` il cui campo `giocatore` corrisponde al nome dell'utente umano.

Il campo `ha_tombola` è un valore booleano (intero 0 o 1 in SQLite), obbligatorio. Indica se il giocatore umano ha ottenuto la tombola nella partita. È l'ultimo dei cinque campi minimi. Il valore si deriva verificando se in `storico_premi` esiste almeno un record con `premio` uguale a "tombola" e `giocatore` uguale al nome dell'utente umano.

Il campo `ambo` è un numero intero, obbligatorio, default zero. Registra il conteggio dei premi di tipo ambo vinti dal giocatore umano nella partita. Non è nei cinque minimi ma è necessario perché la `FinestraStatistiche` (Sezione 5) deve mostrare il dettaglio premi per tipo in una sezione dedicata. Senza questo campo, il calcolo richierebbe di parsare il campo `dettaglio_premi` testuale ad ogni apertura della finestra.

Il campo `terno` è un numero intero, obbligatorio, default zero. Stessa motivazione del campo `ambo`, per i premi di tipo terno.

Il campo `quaterna` è un numero intero, obbligatorio, default zero. Stessa motivazione, per i premi di tipo quaterna.

Il campo `cinquina` è un numero intero, obbligatorio, default zero. Stessa motivazione, per i premi di tipo cinquina.

Il campo `num_bot` è un numero intero, obbligatorio. Registra il numero di bot presenti nella partita. Non è nei cinque minimi ma è necessario per contestualizzare le statistiche: una tombola ottenuta contro 7 bot ha un significato diverso da una contro 1 bot. La `FinestraStatistiche` mostra questo dato nello storico delle ultime partite. Il valore si deriva dal parametro `num_bot` usato in `crea_partita_standard`, preservato nella tabella `partite` dal meccanismo di persistenza della Fase 1.

Il campo `num_cartelle_umano` è un numero intero, obbligatorio. Registra il numero di cartelle assegnate al giocatore umano. Stessa motivazione del campo `num_bot`: contestualizza la prestazione. Il valore si deriva dal parametro `num_cartelle_umano` di `crea_partita_standard`.

Il campo `dettaglio_premi` è un testo, opzionale. Contiene una rappresentazione testuale leggibile dei premi vinti, con tipo, cartella e turno per ciascuno. Questo campo serve esclusivamente per l'esportazione in file `.txt`: quando l'utente esporta le statistiche, il dettaglio testuale viene incluso nel file senza richiedere il ricalcolo dai dati grezzi. Il valore si deriva serializzando i record filtrati di `storico_premi`.

Il record statistiche non appartiene al Dominio ma all'Infrastructure per la seguente ragione, coerente con la logica applicata al modello `Utente` nel DESIGN_02. Il Dominio contiene le entità che descrivono le regole del gioco: la `Partita` sa come si svolge un turno, il `Tabellone` sa come estrarre un numero, la `Cartella` sa come verificare un premio. Nessuna di queste entità ha bisogno di sapere che le statistiche vengono salvate su disco. Il record statistiche è un artefatto di persistenza: esiste solo perché qualcuno vuole leggere i risultati dopo la chiusura dell'applicazione. Se il record vivesse nel Dominio, le classi di gioco dovrebbero importare da — o almeno conoscere — il concetto di database, violando il Vincolo 2 della Costituzione (Dominio puro) e il Vincolo 4 (Infrastructure mai nel Dominio). Il record vive nell'Infrastructure come struttura dati gestita dal repository, e il Controller è l'unico componente che traduce i dati di Dominio (lo `storico_premi`, lo stato sintetico) nei campi del record statistiche.

---

## 4. Lo StatisticheService e il punto di aggancio nel Controller

Il servizio applicativo per le statistiche gestisce la scrittura e la lettura dei dati statistici. A differenza dell'`AuthService` (che nel DESIGN_02 è stato implementato come classe autonoma in `bingo_game/auth_service.py`), il servizio statistiche viene realizzato come insieme di funzioni nel Controller esistente, coerentemente con l'architettura attuale di `bingo_game/game_controller.py` dove tutte le operazioni di orchestrazione sono funzioni a livello di modulo. La motivazione è la seguente: l'`AuthService` gestisce un concetto trasversale (la sessione utente, usata da molteplici componenti), mentre il servizio statistiche è strettamente legato al ciclo di vita della partita e opera esclusivamente all'interno del Controller. Separarlo in un modulo dedicato aggiungerebbe un file senza risolvere un problema di accoppiamento.

Le quattro operazioni del servizio statistiche sono le seguenti.

### Operazione 1: registra_fine_partita

Il nome dell'operazione è `registra_fine_partita`. Riceve in ingresso tre parametri: `utente_id` (intero, identificativo dell'utente corrente), `stato_sintetico` (dizionario restituito da `ottieni_stato_sintetico`), `storico_premi` (lista di dizionari dall'attributo `Partita.storico_premi`). In caso di successo restituisce `True`. In caso di errore restituisce `False` e registra l'errore nel sub-logger `tombola_stark.errors` senza propagare eccezioni alla Presentazione. Internamente, questa operazione filtra lo `storico_premi` per estrarre solo i premi del giocatore umano, conta i premi per tipo (ambo, terno, quaterna, cinquina), verifica la presenza della tombola, compone il campo `dettaglio_premi` come stringa leggibile, e invoca `StatisticheRepository.registra_statistiche_partita` con tutti i campi descritti nella Sezione 3. Questa operazione viene chiamata esclusivamente dal punto di aggancio nel metodo `partita_terminata` di `bingo_game/game_controller.py`.

### Operazione 2: ottieni_statistiche_utente

Il nome dell'operazione è `ottieni_statistiche_utente`. Riceve in ingresso `utente_id` (intero). In caso di successo restituisce un dizionario con le statistiche aggregate dell'utente, contenente le chiavi: `partite_giocate` (intero), `partite_vinte` (intero, conteggio partite con `ha_tombola` vero), `partite_perse` (intero, differenza tra giocate e vinte), `percentuale_vittorie` (decimale), `ambo_totali` (intero), `terno_totali` (intero), `quaterna_totali` (intero), `cinquina_totali` (intero), `tombola_totali` (intero), `miglior_partita_turni` (intero o None), `miglior_partita_data` (stringa data o None). In caso di errore restituisce un dizionario con valori zero per tutti i campi numerici e None per i campi opzionali. Internamente, l'operazione delega a `StatisticheRepository.ottieni_statistiche_aggregate`, che esegue le query SQL aggregate (COUNT, SUM, MIN). Questa operazione viene chiamata dalla `FinestraStatistiche` attraverso il nuovo metodo pubblico `ottieni_statistiche_utente()` aggiunto a `ComandiSistema` in `bingo_game/comandi_partita.py`.

### Operazione 3: ottieni_partite_recenti

Il nome dell'operazione è `ottieni_partite_recenti`. Riceve in ingresso `utente_id` (intero) e `limite` (intero, default 10). In caso di successo restituisce una lista di dizionari, ciascuno con le chiavi: `data` (stringa data), `turni` (intero), `premi_vinti` (intero), `ha_tombola` (booleano), `num_bot` (intero), `num_cartelle_umano` (intero). La lista è ordinata per data in ordine cronologico inverso (la partita più recente è la prima). In caso di errore restituisce una lista vuota. Internamente, l'operazione delega a `StatisticheRepository.ottieni_statistiche_utente` per ottenere tutti i record dell'utente, li ordina per data decrescente e applica il limite. Questa operazione viene chiamata dalla `FinestraStatistiche` attraverso `ComandiSistema`.

### Operazione 4: esporta_statistiche_txt

Il nome dell'operazione è `esporta_statistiche_txt`. Riceve in ingresso `utente_id` (intero) e `percorso_file` (stringa, percorso completo del file `.txt` scelto dall'utente tramite `wx.FileDialog`). In caso di successo restituisce `True`. In caso di errore (permessi negati, disco pieno, percorso non valido) restituisce `False` e registra l'errore nel log. Internamente, l'operazione legge le statistiche aggregate e le partite recenti, compone un testo leggibile con sezioni intestate (riepilogo, premi per tipo, miglior partita, storico), e scrive il file con encoding UTF-8. L'operazione di scrittura su file è protetta da un blocco try/except che intercetta le eccezioni di I/O senza propagarle. Questa operazione viene chiamata dalla `FinestraStatistiche` attraverso `ComandiSistema`.

### Il punto di aggancio nel Controller

Il punto di aggancio per il salvataggio delle statistiche si trova nel metodo `partita_terminata` in `bingo_game/game_controller.py`, nella sezione condizionale `if is_terminata: if not _partita_terminata_logged:`. La chiamata a `registra_fine_partita` viene inserita immediatamente prima della riga `_partita_terminata_logged = True`, dopo la riga di log "Partita terminata.":

```
if is_terminata:
    if not _partita_terminata_logged:
        _log_safe("Partita terminata.", "info")
        # --- Fase 3: salvataggio statistiche ---
        registra_fine_partita(utente_id, stato_sintetico, storico_premi)
        _partita_terminata_logged = True
```

L'`utente_id` viene ottenuto dal Controller consultando `AuthService.ottieni_utente_corrente()`. Il metodo `partita_terminata` dovrà ricevere il riferimento all'`AuthService` (o al suo risultato) per poter effettuare questa lettura. La modalità di passaggio del riferimento è coerente con il meccanismo di dependency injection stabilito nel DESIGN_01 (Sezione 6): il Controller accede all'`AuthService` tramite l'oggetto contenitore di dipendenze, non tramite import diretto.

Il servizio statistiche vive nel layer Controller/Application e non nell'Infrastructure per la stessa ragione documentata nel DESIGN_02 per l'`AuthService`. Il servizio contiene logica applicativa: decide quali dati estrarre dallo `storico_premi`, come filtrarli per il giocatore umano, come contare i premi per tipo, come comporre il testo di esportazione. Queste operazioni non sono mere letture e scritture CRUD (quelle sono del repository): sono orchestrazione applicativa. Il repository implementa l'accesso al database; il servizio nel Controller decide quando e cosa scrivere. Questa separazione è il pattern Repository applicato: il Controller coordina, l'Infrastructure persiste.

---

## 5. La FinestraStatistiche: struttura e accessibilità NVDA

La `FinestraStatistiche` è una nuova finestra wxPython che mostra le statistiche dell'utente corrente. Il file viene creato in `bingo_game/ui/finestra_statistiche.py`. La finestra è un `wx.Frame` non modale che si apre dalla `FinestraPrincipale` e restituisce il focus alla stessa alla chiusura. Il titolo della finestra è letto dalla chiave di localizzazione `STAT_TITOLO_FINESTRA`. La finestra non contiene logica di business: legge i dati tramite `ComandiSistema` e li visualizza, rispettando il Vincolo 5 della Costituzione (Renderer come unico ponte).

### Sezione 1: Riepilogo generale

Il titolo della sezione è un `wx.StaticText` con testo dalla chiave `STAT_RIEPILOGO_TITOLO`. Sotto il titolo, quattro etichette `wx.StaticText` mostrano: partite giocate (`STAT_PARTITE_GIOCATE`), partite vinte (`STAT_PARTITE_VINTE`), partite perse (`STAT_PARTITE_PERSE`), percentuale vittorie (`STAT_PERCENTUALE_VITTORIE`). I valori vengono formattati con il placeholder `{0}` sostituito dal dato numerico. Ogni etichetta è un elemento discreto nel sizer verticale, leggibile individualmente da NVDA con le frecce verticali.

### Sezione 2: Premi per tipo

Il titolo della sezione è un `wx.StaticText` con testo dalla chiave `STAT_PREMI_TIPO_TITOLO`. Sotto il titolo, cinque etichette `wx.StaticText` mostrano i conteggi cumulativi: ambo (`STAT_AMBO_CONTEGGIO`), terno (`STAT_TERNO_CONTEGGIO`), quaterna (`STAT_QUATERNA_CONTEGGIO`), cinquina (`STAT_CINQUINA_CONTEGGIO`), tombola (`STAT_TOMBOLA_CONTEGGIO`). Ogni etichetta ha il formato "Tipo: N" dove N è il totale cumulativo su tutte le partite dell'utente.

### Sezione 3: Miglior partita

Il titolo della sezione è un `wx.StaticText` con testo dalla chiave `STAT_MIGLIOR_PARTITA_TITOLO`. Se l'utente ha almeno una partita con tombola, un'etichetta `wx.StaticText` mostra il dettaglio dalla chiave `STAT_MIGLIOR_PARTITA_DETTAGLIO` con il numero minimo di turni e la data della partita. Se l'utente non ha mai ottenuto una tombola, l'etichetta mostra il testo dalla chiave `STAT_NESSUNA_TOMBOLA`.

### Sezione 4: Storico ultime partite

Il titolo della sezione è un `wx.StaticText` con testo dalla chiave `STAT_STORICO_TITOLO`. Sotto il titolo, un `wx.ListBox` contiene le ultime 10 partite dell'utente. Ogni elemento del ListBox è una stringa composta dalla chiave `STAT_STORICO_ELEMENTO` con data, turni e premi vinti. Il `wx.ListBox` è il widget appropriato perché è navigabile con le frecce dalla tastiera e NVDA annuncia ogni elemento quando è selezionato. Se l'utente non ha partite registrate, il ListBox contiene un singolo elemento con il testo dalla chiave `STAT_STORICO_VUOTO`. Il `wx.ListBox` ha una `wx.StaticText` label ("Storico ultime partite:") immediatamente precedente nell'ordine di tabulazione, associata al controllo per la lettura NVDA.

### Sezione 5: Pulsante Esporta

Un `wx.Button` con etichetta dalla chiave `STAT_BTN_ESPORTA`. Alla pressione, apre un `wx.FileDialog` in modalità salvataggio con titolo dalla chiave `STAT_ESPORTA_TITOLO_DIALOG`, filtro `*.txt` e nome file predefinito `statistiche_tombola.txt`. Se l'utente conferma il salvataggio, viene invocata l'operazione `esporta_statistiche_txt` tramite `ComandiSistema`. In caso di successo, NVDA vocalizza il messaggio dalla chiave `STAT_ESPORTA_SUCCESSO` seguito dal percorso del file dalla chiave `STAT_ESPORTA_PERCORSO`. In caso di errore, NVDA vocalizza il messaggio dalla chiave `STAT_ESPORTA_ERRORE`. L'ordine delle operazioni rispetta il Vincolo 1 della Costituzione: prima aggiornamento widget (se applicabile), poi vocalizzazione.

### Sezione 6: Pulsante Chiudi

Un `wx.Button` con etichetta dalla chiave `STAT_BTN_CHIUDI`. Alla pressione, chiude la `FinestraStatistiche` e restituisce il focus alla `FinestraPrincipale`. Il tasto Escape produce lo stesso effetto tramite binding `wx.EVT_CHAR_HOOK`.

### TabOrder e comportamento NVDA

L'ordine di tabulazione è il seguente: Riepilogo generale (etichette statiche, navigabili con le frecce), Premi per tipo (etichette statiche), Miglior partita (etichetta statica), ListBox storico partite, Pulsante Esporta, Pulsante Chiudi. Il focus iniziale quando la finestra si apre è sulla prima etichetta della sezione Riepilogo, impostato con `wx.CallAfter(self.<widget>.SetFocus)` dopo che la finestra è visibile. NVDA vocalizza il messaggio dalla chiave `STAT_ANNUNCIO_APERTURA` al momento dell'apertura, dopo che tutti i widget sono stati popolati con i dati correnti (rispettando il Vincolo 1: testo → widget → voce). Il tasto Escape chiude la finestra in qualsiasi momento.

La `FinestraStatistiche` legge i dati tramite `ComandiSistema`, che internamente delega alle operazioni del servizio statistiche nel Controller, che a loro volta usano `StatisticheRepository`. La finestra non importa dal layer Infrastructure, non conosce l'esistenza del database e non sa che il repository è SQLite. Se in Fase 8 il repository venisse sostituito da un `NetworkAdapter`, la `FinestraStatistiche` continuerebbe a funzionare senza modifiche. Questo rispetta il Vincolo 5 della Costituzione.

---

## 6. Aggiornamento della FinestraPrincipale

La `FinestraPrincipale` in `bingo_game/ui/finestra_principale.py` viene modificata per esporre la voce "Statistiche" nel menu. Le modifiche sono le seguenti.

Aggiunta di un pulsante "Statistiche" con etichetta dalla chiave di localizzazione `STAT_VOCE_MENU` e acceleratore da tastiera Ctrl+T. L'acceleratore Ctrl+T è stato scelto perché Ctrl+S è convenzionalmente riservato al salvataggio, Ctrl+R è già assegnato alla Registrazione (Fase 2) e Ctrl+L al Login (Fase 2). La lettera T richiama "sTatistiche" ed è mnemonicamente ragionevole.

Il pulsante viene posizionato nel sizer verticale tra le voci esistenti, nella posizione appropriata decisa dall'implementatore (dopo "Nuova partita" e prima di "Impostazioni" è la collocazione naturale, coerente con l'ordine funzionale: prima si gioca, poi si consultano le statistiche, poi si configurano le impostazioni).

La voce "Statistiche" è abilitata solo se esiste un utente in sessione. Il metodo handler `_on_statistiche` verifica tramite il riferimento all'`AuthService` (già disponibile nella `FinestraPrincipale` dopo la Fase 2) che `ottieni_utente_corrente()` restituisca un utente non nullo. Se la verifica ha successo, apre la `FinestraStatistiche` passandole il necessario per leggere i dati tramite `ComandiSistema`. Se nessun utente è loggato e si tenta di accedere alle statistiche, viene vocalizzato tramite NVDA il messaggio dalla chiave `STAT_SESSIONE_RICHIESTA`, che invita l'utente ad effettuare il login. Il widget del pulsante "Statistiche" può essere disabilitato (`Disable()`) quando nessun utente è in sessione e riabilitato (`Enable()`) dopo il login, oppure il controllo può avvenire esclusivamente nell'handler: la scelta implementativa è lasciata all'agente implementatore purché il comportamento sia lo stesso (l'utente non loggato non raggiunge la `FinestraStatistiche`).

L'annuncio NVDA all'apertura della `FinestraStatistiche` segue il Vincolo 1: prima la finestra viene creata e i widget popolati, poi il focus viene assegnato, poi la vocalizzazione avviene.

---

## 7. Il catalogo testi: nuove chiavi da aggiungere a locale/it.py

Le seguenti chiavi di testo vengono aggiunte al dizionario di localizzazione in `bingo_game/ui/locale/it.py`, rispettando il Vincolo 6 della Costituzione (nessuna stringa italiana inline nei metodi handler del renderer). Per ogni chiave è indicato il nome della costante, il valore stringa italiano e il contesto d'uso.

- `STAT_TITOLO_FINESTRA` — "Statistiche di gioco" — Titolo del `wx.Frame` della `FinestraStatistiche`.
- `STAT_RIEPILOGO_TITOLO` — "Riepilogo generale" — Header `wx.StaticText` della prima sezione.
- `STAT_PARTITE_GIOCATE` — "Partite giocate: {0}" — Etichetta nel riepilogo, `{0}` sostituito dal conteggio.
- `STAT_PARTITE_VINTE` — "Partite vinte: {0}" — Etichetta nel riepilogo.
- `STAT_PARTITE_PERSE` — "Partite perse: {0}" — Etichetta nel riepilogo.
- `STAT_PERCENTUALE_VITTORIE` — "Percentuale vittorie: {0}%" — Etichetta nel riepilogo.
- `STAT_PREMI_TIPO_TITOLO` — "Premi ottenuti per tipo" — Header `wx.StaticText` della sezione premi.
- `STAT_AMBO_CONTEGGIO` — "Ambo: {0}" — Etichetta conteggio ambo nella sezione premi.
- `STAT_TERNO_CONTEGGIO` — "Terno: {0}" — Etichetta conteggio terno.
- `STAT_QUATERNA_CONTEGGIO` — "Quaterna: {0}" — Etichetta conteggio quaterna.
- `STAT_CINQUINA_CONTEGGIO` — "Cinquina: {0}" — Etichetta conteggio cinquina.
- `STAT_TOMBOLA_CONTEGGIO` — "Tombola: {0}" — Etichetta conteggio tombola.
- `STAT_MIGLIOR_PARTITA_TITOLO` — "Miglior partita" — Header `wx.StaticText` della sezione miglior partita.
- `STAT_MIGLIOR_PARTITA_DETTAGLIO` — "Tombola ottenuta in {0} turni il {1}" — Dettaglio della miglior partita, `{0}` turni, `{1}` data.
- `STAT_NESSUNA_TOMBOLA` — "Nessuna tombola ottenuta finora." — Testo mostrato quando l'utente non ha mai fatto tombola.
- `STAT_STORICO_TITOLO` — "Storico ultime partite" — Header `wx.StaticText` e label del `wx.ListBox`.
- `STAT_STORICO_ELEMENTO` — "{0} — Turni: {1}, Premi: {2}" — Formato di ciascun elemento nel ListBox dello storico, `{0}` data, `{1}` turni, `{2}` numero premi.
- `STAT_STORICO_VUOTO` — "Nessuna partita registrata." — Elemento placeholder nel ListBox quando lo storico è vuoto.
- `STAT_BTN_ESPORTA` — "Esporta statistiche" — Etichetta del pulsante Esporta nella `FinestraStatistiche`.
- `STAT_BTN_CHIUDI` — "Chiudi" — Etichetta del pulsante Chiudi nella `FinestraStatistiche`.
- `STAT_ESPORTA_TITOLO_DIALOG` — "Salva statistiche come file di testo" — Titolo del `wx.FileDialog` di esportazione.
- `STAT_ESPORTA_SUCCESSO` — "Statistiche esportate con successo." — Messaggio vocalizzato da NVDA dopo esportazione riuscita.
- `STAT_ESPORTA_PERCORSO` — "File salvato in: {0}" — Messaggio con il percorso del file esportato, `{0}` percorso completo.
- `STAT_ESPORTA_ERRORE` — "Errore durante l'esportazione delle statistiche." — Messaggio vocalizzato in caso di errore di esportazione.
- `STAT_SESSIONE_RICHIESTA` — "Effettua il login per consultare le statistiche." — Messaggio vocalizzato quando l'utente tenta di aprire le statistiche senza sessione attiva.
- `STAT_ANNUNCIO_APERTURA` — "Finestra statistiche. Riepilogo generale." — Annuncio NVDA all'apertura della `FinestraStatistiche`, dopo il popolamento dei widget.
- `STAT_VOCE_MENU` — "Statistiche" — Etichetta della voce nel menu della `FinestraPrincipale`.

Il totale delle nuove chiavi è ventisette. Nessuna di queste chiavi entra in conflitto con le chiavi esistenti nel dizionario di localizzazione. L'implementatore è libero di scegliere il meccanismo tecnico per la definizione delle chiavi (costanti stringa, enum, o integrazione nel sistema codici esistente), purché il dizionario in `bingo_game/ui/locale/it.py` contenga tutti i valori elencati.

---

## 8. Strategia di test

### Test del SqliteStatisticheRepository

Il file `tests/infrastructure/test_sqlite_statistiche_repository.py` esiste già dalla Fase 1 con i test per le operazioni CRUD di base (`registra_statistiche_partita`, `ottieni_statistiche_utente`). In questa fase il file viene completato aggiungendo i test per il metodo `ottieni_statistiche_aggregate(utente_id)`.

I test delle query aggregate verificano che le funzioni SQL (COUNT, SUM, MIN) restituiscano dizionari con i campi attesi: `partite_giocate`, `partite_vinte`, `premi_totali`, `ambo_totali`, `terno_totali`, `quaterna_totali`, `cinquina_totali`, `tombola_totali`, `miglior_partita_turni`. Si inseriscono nel database di test almeno tre record statistici con combinazioni diverse di premi e tombola, poi si invoca `ottieni_statistiche_aggregate` e si verificano i valori calcolati contro i valori attesi. Si verifica anche il caso di utente senza partite registrate: il metodo deve restituire un dizionario con valori zero, non sollevare eccezioni.

Tutti i test usano un database SQLite in memoria (`:memory:`) o una cartella temporanea, mai il file database dell'applicazione — coerentemente con la strategia già stabilita nel DESIGN_01 (Sezione 7). I test non dipendono dalla UI perché il repository riceve la connessione dal `db_manager` che non ha relazione con wxPython.

### Test di integrazione Controller e StatisticheRepository

Il file `tests/integration/test_statistiche_fine_partita.py` è nuovo in questa fase. Testa il flusso completo Controller → StatisticheRepository senza UI wx.

Il test crea un `db_manager` con database in memoria, istanzia `SqliteStatisticheRepository`, configura il Controller con il repository iniettato, registra un utente fittizio, e simula una partita completa: `crea_partita_standard`, `avvia_partita_sicura`, ciclo ripetuto di `esegui_turno_sicuro` e `esegui_fase_verifica_sicura` fino a terminazione. Al termine, verifica che `partita_terminata` abbia restituito `True` e che un record sia stato scritto nella tabella `statistiche` con i campi corretti.

Il test verifica anche il meccanismo anti-duplicato: una seconda chiamata a `partita_terminata` sulla stessa partita non deve produrre un secondo record nel database. Il flag `_partita_terminata_logged` (già esistente in `game_controller.py`, verificato alla riga 73 della versione corrente) è il meccanismo che lo garantisce.

I nomi dei metodi reali del Controller usati nel test sono: `esegui_turno_sicuro` e `esegui_fase_verifica_sicura` come punti di innesto del ciclo turno (nomi verificati in `bingo_game/game_controller.py`), e il flag `_partita_terminata_logged` come meccanismo anti-duplicato. Il test non accede a metodi privati: usa esclusivamente l'interfaccia pubblica del Controller.

### Test della FinestraStatistiche

Il file `tests/ui/test_finestra_statistiche.py` è nuovo in questa fase. Testa l'apertura della finestra, il focus iniziale, le label NVDA e lo stato vuoto.

I test verificano i seguenti aspetti: la finestra si apre senza eccezioni quando viene costruita con dati mock; il focus iniziale è sulla prima etichetta della sezione riepilogo (verificabile interrogando `FindFocus()`); ogni sezione ha un `wx.StaticText` con testo non vuoto; il `wx.ListBox` dello storico è presente e navigabile; i pulsanti Esporta e Chiudi esistono e sono attivi; la pressione di Escape chiude la finestra; in stato vuoto (utente senza partite), il ListBox contiene il messaggio dalla chiave `STAT_STORICO_VUOTO`.

I test usano un database in memoria per il repository o mock objects per i dati, mai il file database dell'applicazione.

### Percorsi e nomi dei file di test

```
tests/
  infrastructure/
    test_sqlite_statistiche_repository.py   ← già esistente dalla Fase 1, completato in questa fase
                                               con i test per ottieni_statistiche_aggregate()
  integration/
    test_statistiche_fine_partita.py        ← nuovo in questa fase: testa il flusso completo
                                               Controller → StatisticheRepository senza UI wx
  ui/
    test_finestra_statistiche.py            ← nuovo in questa fase: testa apertura finestra,
                                               focus iniziale, label NVDA, stato vuoto
```

---

## 9. Struttura delle cartelle e dei file

### File nuovi introdotti da questa fase

```
bingo_game/
  ui/
    finestra_statistiche.py          ← nuova finestra wxPython per la consultazione delle statistiche

tests/
  integration/
    test_statistiche_fine_partita.py ← test di integrazione Controller→StatisticheRepository
  ui/
    test_finestra_statistiche.py     ← test accessibilità e comportamento della FinestraStatistiche
```

### File modificati da questa fase

```
bingo_game/
  game_controller.py                 ← aggiunta chiamata a StatisticheRepository al termine della partita,
                                        protetta dal flag partita_terminata_logged già esistente
  comandi_partita.py                 ← aggiunta del metodo pubblico ottieni_statistiche_utente()
                                        alla classe ComandiSistema
  ui/
    finestra_principale.py           ← aggiunta voce "Statistiche" (acceleratore Ctrl+T) e handler
                                        on_statistiche con verifica sessione utente
    locale/
      it.py                          ← aggiunta di tutte le stringhe per FinestraStatistiche,
                                        messaggi stato vuoto, testo esportazione, messaggio percorso file

tests/
  infrastructure/
    test_sqlite_statistiche_repository.py  ← completamento dei test per le query aggregate
                                              (file già esistente dalla Fase 1, ora completato)
```

Nota sul file `bingo_game/infrastructure/repositories/sqlite_statistiche_repository.py`: questo file esiste già dalla Fase 1 con le operazioni CRUD di base. In questa fase viene attivato operativamente tramite le chiamate dal Controller e riceve il completamento delle query aggregate nel metodo `ottieni_statistiche_aggregate()`. Il file è pertanto da considerarsi modificato, ma la struttura complessiva e l'interfaccia pubblica restano invariate rispetto a quanto definito nel DESIGN_01.

### File non toccati da questa fase

```
main.py
bingo_game/partita.py
bingo_game/tabellone.py
bingo_game/cartella.py
bingo_game/players/giocatore_base.py
bingo_game/players/giocatore_umano.py
bingo_game/players/giocatore_automatico.py
bingo_game/utente.py
bingo_game/auth_service.py
bingo_game/ui/finestra_gioco.py
bingo_game/ui/finestra_configurazione.py
bingo_game/ui/finestra_registrazione.py
bingo_game/ui/finestra_login.py
bingo_game/ui/finestra_aiuto_tasti_rapidi.py
bingo_game/ui/finestra_guida_regole.py
bingo_game/ui/dialogo_ricerca.py
bingo_game/ui/renderers/base_renderer.py
bingo_game/ui/renderers/renderer_wx.py
bingo_game/infrastructure/database/db_manager.py
bingo_game/infrastructure/repositories/interfaces/partita_repository.py
bingo_game/infrastructure/repositories/interfaces/utente_repository.py
bingo_game/infrastructure/repositories/interfaces/statistiche_repository.py
bingo_game/infrastructure/repositories/interfaces/crediti_repository.py
bingo_game/infrastructure/repositories/sqlite_partita_repository.py
bingo_game/infrastructure/repositories/sqlite_utente_repository.py
bingo_game/infrastructure/repositories/sqlite_crediti_repository.py
requirements.txt
```

Questa struttura non crea conflitti con i file esistenti. I due nuovi file di test si collocano nelle cartelle `tests/integration/` e `tests/ui/` già presenti nel repository. Il file `bingo_game/ui/finestra_statistiche.py` si aggiunge accanto alle finestre wx esistenti.

---

## 10. Contratto in ingresso e contratto in uscita

### Contratto in ingresso

Le seguenti condizioni devono essere vere prima che questa fase inizi. Ogni condizione è verificabile.

`StatisticheRepository` con interfaccia ABC esiste in `bingo_game/infrastructure/repositories/interfaces/statistiche_repository.py` e l'implementazione SQLite esiste in `bingo_game/infrastructure/repositories/sqlite_statistiche_repository.py` (verificabile: i file esistono e i test di Fase 1 passano). Creati in Fase 1.

Il modello `Utente` esiste in `bingo_game/utente.py` con un campo `id` stabile (verificabile: il file esiste e il campo `id` è presente nella classe). Creato in Fase 2.

`AuthService.ottieni_utente_corrente()` è funzionante e restituisce il modello `Utente` quando un utente è loggato, oppure `None` quando la sessione è vuota (verificabile: i test di Fase 2 passano). Creato in Fase 2.

`GameController.ottieni_stato_sintetico()` è funzionante e restituisce un dizionario con le chiavi `stato_partita`, `ultimo_numero_estratto`, `numeri_estratti`, `giocatori`, `premi_gia_assegnati` (verificabile: il metodo esiste già in v0.14.0-alpha, come documentato nella Sezione 2).

`partita_terminata()` in `bingo_game/game_controller.py` è funzionante con il flag `_partita_terminata_logged` che garantisce l'esecuzione una volta sola (verificabile: il metodo e il flag esistono già in v0.14.0-alpha, come documentato nella Sezione 2).

`storico_premi` esposto da `Partita` come lista di dizionari con le chiavi `giocatore`, `id_giocatore`, `cartella`, `premio`, `riga`, `turno` è funzionante (verificabile: l'attributo esiste già in v0.14.0-alpha).

Il database è inizializzato in `main.py` con le tabelle `statistiche` e `partite` già create (verificabile: la sequenza di avvio di Fase 2 in `main.py` include l'inizializzazione del `db_manager`).

### Contratto in uscita

Le seguenti condizioni devono essere vere dopo che questa fase è completata. Ogni condizione è verificabile con il metodo indicato.

A ogni chiamata a `partita_terminata()` che restituisce `True`, un record viene scritto nella tabella `statistiche` con almeno i campi `utente_id`, `data`, `turni`, `premi_vinti`, `ha_tombola` più i campi aggiuntivi definiti nella Sezione 3 (verificabile: eseguire una partita fino alla terminazione e interrogare il database con `SELECT * FROM statistiche`).

La `FinestraStatistiche` legge e visualizza dati reali dal database, non mock (verificabile: dopo aver giocato una partita, la finestra statistiche mostra i dati corrispondenti).

Ogni widget della `FinestraStatistiche` ha label `wx.StaticText` associata (verificabile: leggendo il costruttore della classe `FinestraStatistiche` in `bingo_game/ui/finestra_statistiche.py`).

Il file `.txt` esportato contiene dati corretti e leggibili (verificabile: esportare dopo aver giocato almeno una partita e leggere il file con un editor di testo).

I test del servizio statistiche e del repository passano senza eseguire l'applicazione (verificabile: `pytest tests/infrastructure/test_sqlite_statistiche_repository.py tests/integration/test_statistiche_fine_partita.py tests/ui/test_finestra_statistiche.py`).

Nessun file di Dominio (`bingo_game/partita.py`, `bingo_game/tabellone.py`, `bingo_game/cartella.py`, `bingo_game/players/`) importa da `bingo_game.infrastructure` (verificabile: `grep -rn "from bingo_game.infrastructure" bingo_game/` escludendo la cartella `infrastructure/` e il Controller → zero risultati).

---

## 11. Decisioni rinviate

### Classifica globale tra utenti

Non si decide ora se e come implementare una classifica (leaderboard) che confronti le statistiche di utenti diversi. Le statistiche di questa fase sono strettamente per-utente: ogni utente vede solo le proprie. La classifica richiede un server condiviso e un protocollo di sincronizzazione che non esistono fino alla Fase 8. La decisione viene rinviata alla Fase 9 (Multiplayer Online), dove la classifica è elencata tra i deliverable.

### Statistiche comparative tra sessioni di gioco multiplo

Non si decide ora come gestire le statistiche quando nella stessa partita sono presenti più giocatori umani. Questa fase mantiene il vincolo di un solo giocatore umano per partita (assunzione del Dominio confermata nella Costituzione). Quando in Fase 7 (Multiplayer Locale) più umani potranno giocare la stessa partita, il record statistiche dovrà essere scritto separatamente per ciascun utente umano, e la tabella `statistiche` potrebbe richiedere un adattamento. La decisione viene rinviata alla Fase 7.

### Formato di esportazione avanzato

Non si decide ora se introdurre formati di esportazione diversi dal `.txt` leggibile, come PDF o HTML. L'esportazione PDF richiederebbe una libreria esterna (es. `reportlab` o `fpdf2`) non presente nel `requirements.txt` attuale. L'esportazione HTML richiederebbe una decisione su template e stile. In questa fase il formato `.txt` è sufficiente per l'accessibilità (NVDA legge i file di testo senza problemi) e non introduce dipendenze. La decisione viene rinviata a una fase futura, se l'utente ne esprime l'esigenza.

### Sistema di badge o obiettivi

Non si decide ora se introdurre un sistema di badge, trofei o obiettivi basati sulle statistiche (es. "Prima tombola", "100 partite giocate", "5 tombola consecutive"). Questo sistema non è previsto nella roadmap delle 9 fasi della Costituzione. Se l'utente lo richiedesse, sarebbe un'estensione post-v2.0.x che legge dalla tabella `statistiche` senza modificarla. La decisione viene rinviata indefinitamente.

---

## 12. Istruzioni specifiche per l'agente implementatore

- Il punto di aggancio per il salvataggio delle statistiche è nel metodo `partita_terminata` in `bingo_game/game_controller.py`, immediatamente prima della riga `_partita_terminata_logged = True`. Non aggiungere il salvataggio in `esegui_turno_sicuro` o in `esegui_fase_verifica_sicura`: il flag `_partita_terminata_logged` è il meccanismo anti-duplicato e si trova solo in `partita_terminata`.

- L'`utente_id` per il salvataggio viene ottenuto da `AuthService.ottieni_utente_corrente().id`. Se `ottieni_utente_corrente()` restituisce `None` (nessun utente in sessione), il salvataggio non deve avvenire e il metodo deve registrare un warning nel sub-logger `tombola_stark.system`.

- Il nuovo metodo `ottieni_statistiche_utente()` in `ComandiSistema` (`bingo_game/comandi_partita.py`) deve delegare alle funzioni di `bingo_game/game_controller.py`, non accedere direttamente al repository. La `FinestraStatistiche` chiama `ComandiSistema`, non il Controller direttamente.

- Le nuove funzioni di statistiche in `bingo_game/game_controller.py` devono usare il sub-logger `tombola_stark.game` per le operazioni normali e `tombola_stark.errors` per le eccezioni. Non usare `print()` in nessun file modificato (rispettando il Vincolo 7 della Costituzione).

- La `FinestraStatistiche` in `bingo_game/ui/finestra_statistiche.py` deve avere il focus iniziale sulla prima sezione (Riepilogo generale), impostato con `wx.CallAfter` dopo che la finestra è visibile. Il tasto Escape deve chiudere la finestra.

- Ogni sezione della `FinestraStatistiche` deve avere un header `wx.StaticText` che NVDA legge quando l'utente naviga con le frecce. Il `wx.ListBox` dello storico deve avere una `wx.StaticText` label associata immediatamente precedente nell'ordine di tabulazione (rispettando il Vincolo 3 della Costituzione).

- L'acceleratore per la voce "Statistiche" nella `FinestraPrincipale` (`bingo_game/ui/finestra_principale.py`) deve essere Ctrl+T, non Ctrl+S (riservato al salvataggio convenzionale).

- Tutte le stringhe di testo mostrate nella `FinestraStatistiche` e nel menu devono provenire dal catalogo `bingo_game/ui/locale/it.py`. Nessuna stringa italiana può essere scritta inline nei costruttori delle finestre o nei metodi handler (rispettando il Vincolo 6 della Costituzione).

- L'esportazione in file `.txt` deve usare encoding UTF-8 e deve proteggere l'operazione di scrittura con un blocco try/except per le eccezioni di I/O. Il percorso del file viene scelto dall'utente tramite `wx.FileDialog`, non hardcoded.

- Il `SqliteStatisticheRepository` (`bingo_game/infrastructure/repositories/sqlite_statistiche_repository.py`) necessita del completamento del metodo `ottieni_statistiche_aggregate()` con le query SQL aggregate. Le query devono restituire risultati corretti anche per utenti senza partite registrate (COUNT restituisce 0, SUM restituisce 0 o NULL da gestire, MIN restituisce NULL da gestire).

- I test in `tests/integration/test_statistiche_fine_partita.py` devono simulare una partita completa usando i metodi pubblici del Controller (`esegui_turno_sicuro`, `esegui_fase_verifica_sicura`, `partita_terminata`), non chiamando direttamente funzioni interne. Il database di test deve essere SQLite in memoria (`:memory:`) o in una cartella temporanea.

- I test in `tests/ui/test_finestra_statistiche.py` devono verificare la presenza delle label `wx.StaticText`, il focus iniziale, e il comportamento di Escape. I dati possono essere mock o provenire da un repository in memoria.

- Dopo l'implementazione, eseguire le verifiche grep richieste dalla Costituzione per confermare che nessun import proibito è stato introdotto: `grep -rn "from bingo_game.infrastructure" bingo_game/` escludendo `infrastructure/` e il Controller deve restituire zero risultati. `grep -n "print(" bingo_game/game_controller.py bingo_game/comandi_partita.py` deve restituire zero risultati.

- Non modificare `main.py`. La sequenza di avvio è completa dalla Fase 2. Il `StatisticheRepository` è già istanziabile tramite il `db_manager` senza modifiche al bootstrap.

- Non modificare i file del Dominio di gioco (`bingo_game/partita.py`, `bingo_game/tabellone.py`, `bingo_game/cartella.py`, `bingo_game/players/`). Le statistiche sono un aspetto di persistenza, non una regola di gioco.

- Non modificare il contratto del renderer (`bingo_game/ui/renderers/base_renderer.py`). La `FinestraStatistiche` è una finestra separata, non un componente del flusso di gioco gestito dal renderer.

---

*Documento prodotto da Agent-Design — Tombola Stark Framework v1.10.3*
*Baseline di riferimento: v0.14.0-alpha — 15 aprile 2026*
