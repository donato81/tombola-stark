# DESIGN — Costituzione Architetturale: Roadmap v0.15.x → v2.0.x

> **Data**: 14 aprile 2026
> **Versione baseline**: v0.14.0-alpha
> **Tipo documento**: Costituzione / Visione d'insieme
> **Stato**: BOZZA
> **Autore analisi**: Agent-Analyze

---

## 1. Fotografia dell'architettura esistente

Questa sezione descrive lo stato reale del codice alla versione v0.14.0-alpha,
derivato dalla lettura diretta dei file sorgente. Non descrive stato futuro
né aspirazioni: è la fotografia del punto di partenza.

---

### Layer Dominio (`bingo_game/` — escluse le sottocartelle `ui/` e `logging/`)

Il layer Dominio contiene tutta la logica di business. Non importa wxPython,
sqlite3, librerie di rete né alcuna dipendenza esterna. Dipende esclusivamente
dalla standard library Python.

**Classi pubbliche esistenti e contratti esposti:**

- `Tabellone` (`bingo_game/tabellone.py`): gestisce il sacchetto dei numeri
  da 1 a 90, l'estrazione sequenziale e lo storico degli estratti. Espone
  estrazioni via eccezione `TabelloneNumeriEsauritiException` quando i numeri
  sono esauriti.

- `Cartella` (`bingo_game/cartella.py`): rappresenta una singola cartella di
  gioco (3 righe × 9 colonne con 5 numeri per riga). Espone metodi di
  segnatura, verifica premi per riga e stato completo della cartella.

- `Partita` (`bingo_game/partita.py`): coordinatore centrale. Gestisce il roster
  di giocatori, il ciclo di estrazioni e la verifica premi. Espone
  `get_stato_completo()`, `esegui_fase_estrazione()`, `esegui_fase_verifica()`,
  `tutti_hanno_dichiarato_fine()`, `storico_premi` (lista in tempo reale di
  tutti i premi assegnati con giocatore, cartella, premio, riga, turno),
  `termina_partita()`.

- `GiocatoreBase` (`bingo_game/players/giocatore_base.py`): classe base comune.
  Gestisce identità (nome, id opzionale), lista cartelle, aggiornamento con
  numero estratto, stato complessivo. Espone `reset_reclamo_turno()`.

- `GiocatoreUmano` (`bingo_game/players/giocatore_umano.py`): specializzazione
  con supporto reclami vittoria e interazione con il sistema eventi UI.

- `GiocatoreAutomatico` (`bingo_game/players/giocatore_automatico.py`):
  bot automatico. Non ha dipendenze UI.

- `GestioneFocusMixin` / `helper_focus.py` (`bingo_game/players/helper_focus.py`):
  helper per la gestione del focus navigazionale sulla griglia della cartella.
  Auto-seleziona la prima cartella disponibile quando il focus non è ancora
  impostato.

**Sistema eventi strutturati (`bingo_game/events/`):**

- `EsitoAzione` (`eventi.py`): dataclass frozen che trasporta l'esito di ogni
  comando. Regola: se `ok=False` allora `errore` è valorizzato e `evento` è
  None; se `ok=True` allora `errore` è None e `evento` può essere un
  `EventoAzione` o None (successo silenzioso).

- `EventoAzione` (`eventi.py`): tipo Union chiuso degli eventi che possono
  viaggiare dentro `EsitoAzione.evento` — comprende `EventoFocusAutoImpostato`,
  `EventoFocusCartellaImpostato`, `EventoReclamoVittoria`,
  `EventoEsitoReclamoVittoria`, `EventoFineTurno`.

- Moduli codici: `codici_eventi.py`, `codici_controller.py`,
  `codici_configurazione.py`, `codici_errori.py`, `codici_loop.py`,
  `codici_messaggi_sistema.py`, `codici_output_ui_umani.py` — ciascuno
  contiene solo costanti stringa. Nessun import da moduli del progetto.

- Moduli eventi tipizzati: `eventi_output_ui_umani.py`, `eventi_partita.py`,
  `eventi_ui.py` — dataclass che incapsulano payload strutturati per il
  renderer.

**Gerarchia eccezioni (`bingo_game/exceptions/`):**

Ogni modulo di dominio ha le proprie eccezioni personalizzate:
`cartella_exceptions.py`, `game_controller_exceptions.py`,
`giocatore_exceptions.py`, `partita_exceptions.py`,
`tabellone_exceptions.py`. Il Controller intercetta queste eccezioni e
non le propaga al layer di presentazione.

**Validazioni (`bingo_game/validations/`):**

`validazione_oggetti.py` e `validazioni_input.py`: logica di validazione
riutilizzabile, senza dipendenze esterne.

**Assunzioni implicite presenti nel Dominio:**

- Un solo giocatore umano per partita (struttura di `GiocatoreUmano` e
  `ottieni_giocatore_umano()` restituisce un singolo oggetto).
- Partita sempre locale: nessun concetto di sessione, rete o persistenza.
- Numero massimo giocatori: 8 (1 umano + 7 bot) come costante nel controller.
- I numeri estratti vanno da 1 a 90: invariante del `Tabellone`.

---

### Layer Controller (`bingo_game/game_controller.py`, `bingo_game/comandi_partita.py`)

**Funzioni pubbliche in `game_controller.py`:**

- `crea_partita_standard(nome_giocatore_umano, num_cartelle_umano, num_bot)`:
  factory completa. Crea tabellone, giocatori, cartelle e l'istanza `Partita`
  configurata. Valida i parametri e solleva eccezioni controller se invalidi.
- `avvia_partita_sicura(partita)`: avvia la partita con gestione sicura delle
  eccezioni di dominio. Restituisce `bool`.
- `esegui_turno_sicuro(partita)`: esegue un turno completo con intercettazione
  di tutte le eccezioni di dominio. Restituisce `EsitoAzione`.
- `esegui_fase_estrazione_sicura(partita)` / `esegui_fase_verifica_sicura(partita)`:
  versioni bifasiche del turno per il ciclo V2.
- `ottieni_stato_sintetico(partita)`: restituisce un dizionario con turni,
  numeri estratti, premi, giocatori. Non contiene logica di business.
- `ha_partita_tombola(partita)` / `partita_terminata(partita)`: sensori di stato.
- `ottieni_giocatore_umano(partita)`: restituisce l'unico `GiocatoreUmano`
  dalla partita. Assunzione: esiste sempre esattamente un giocatore umano.

**Cosa il Controller non fa:**

- Non contiene logica di business (delega sempre al Dominio).
- Non scrive su stdout (verificabile: `grep -n "print(" bingo_game/game_controller.py` → zero risultati).
- Non conosce wxPython né librerie audio.
- Non gestisce persistenza, rete o autenticazione.

**Facade in `bingo_game/comandi_partita.py`:**

- `ComandiSistema`: incapsula le operazioni globali di partita. Metodi:
  `crea_nuova_partita()`, `avvia_partita()`, `esegui_turno()`,
  `ottieni_stato_gioco()`, `ha_tombola()`, `e_terminata()`,
  `ottieni_giocatore_umano()`.
- `ComandiGiocatoreUmano`: facade per i comandi personali del giocatore umano.
  Metodi: `segna_numero()`, `dichiara_vittoria()`, `dichiara_fine_turno()`,
  `turno_gia_dichiarato()`, `stato_focus()`, navigazione cartella/riga/colonna.
- Entrambe le classi importano esclusivamente da `game_controller` e dal
  layer Dominio. Non importano wxPython.

---

### Layer Presentazione (`bingo_game/ui/`)

**Contratto BaseRenderer (`bingo_game/ui/renderers/base_renderer.py`):**

Classe astratta ABC che definisce l'interfaccia obbligatoria per ogni renderer.
Metodi astratti: `render_esito()`, `mostra_schermata_configurazione()`,
`mostra_report_finale()`, `mostra_messaggio_sistema()`,
`annuncia_numero_estratto()`, `annuncia_premi_turno()`,
`annuncia_fase_turno()`, `annuncia_avviso_timeout()`,
`annuncia_avvio_pausa_turno()`, `annuncia_tutti_pronti()`,
`annuncia_pausa()`. Metodo concreto: `_formatta_testo_da_catalogo()`.
Regola esplicitata nel docstring: "Ordine fisso handler: testo → widget → voce".

`StatoConfigurazione`: dataclass frozen per lo stato della schermata di
configurazione iniziale. Contiene: `fase_corrente`, `codice_messaggio`,
`codice_errore`, `nome_giocatore`, `numero_bot`, `numero_cartelle`.

**Implementazione concreta (`bingo_game/ui/renderers/renderer_wx.py`):**

`WxRenderer(BaseRenderer)`: riceve `wx.Frame` e `IVocalizzatore` tramite
dependency injection. Non crea la finestra né il backend AO2. Struttura
interna: per ogni famiglia di eventi esiste un handler `_handle_*` dedicato
che chiama prima `_wx_*` (aggiornamento widget) poi `_ao2_*` (vocalizzazione).

**Componenti wx esistenti:**

- `FinestraPrincipale` (`ui/finestra_principale.py`): menu di avvio con
  quattro voci (Nuova partita, Impostazioni placeholder, Guida, Esci).
  Nessuna logica di dominio. Apre `FinestraConfigurazione` tramite pulsante.
- `FinestraConfigurazione` (`ui/finestra_configurazione.py`): raccoglie nome
  giocatore, numero bot, numero cartelle. Crea la partita e apre `FinestraGioco`.
- `FinestraGioco` (`ui/finestra_gioco.py`): frame principale di gioco. Gestisce
  pannello griglia (PannelloGriglia), pulsante principale bifasico (Inizia
  partita / Passa turno), area log annunci (Ctrl+E), HeaderBar visiva con
  turno/ultimo estratto/premi. Binding tastiera in tre categorie (A: EVT_KEY_DOWN
  sul pannello griglia; B e C: EVT_CHAR_HOOK sul frame). Pausa con Ctrl+P.
- `DialogoRicercaNumero` (`ui/dialogo_ricerca.py`): dialog persistente per la
  ricerca numeri sulla cartella. Non si chiude automaticamente.
- `FinestraAiutoTastiRapidi` (`ui/finestra_aiuto_tasti_rapidi.py`): dialog
  modale con elenco 35 binding, aperto con Ctrl+H.
- `FinestraGuidaRegole` (`ui/finestra_guida_regole.py`): dialog modale con
  5 capitoli di regole navigabili, aperto con Ctrl+Shift+H.
- `bingo_game/ui/tema.py`: costanti colore e dimensione per la UI.
- `bingo_game/ui/locales/it.py` (e `it_guida.py`): dizionari di testi
  localizzati. Nessun import da moduli di business.

**Infrastruttura trasversale di logging (`bingo_game/logging/game_logger.py`):**

`GameLogger`: singleton registrato su `tombola_stark`. Sub-logger per
categoria: `tombola_stark.game`, `tombola_stark.prizes`, `tombola_stark.system`,
`tombola_stark.errors`, `tombola_stark.ui`. Il Dominio non usa il logger:
solo il Controller e la Presentazione lo usano.

---

### Assente — Layer Infrastructure

Alla versione v0.14.0-alpha il layer Infrastructure **non esiste**. Nessun file
nel repository esegue le seguenti operazioni:

- Persistenza su disco (nessun accesso a SQLite, file JSON o database).
- Autenticazione o gestione sessioni utente.
- Comunicazione di rete (nessun socket, nessuna HTTP request da logica di gioco).
- Gestione audio strutturata persistente (pygame e playsound sono nelle
  dipendenze di `requirements.txt` ma nessun modulo di gioco li usa in modo
  organizzato come servizio).
- Modello Utente. Non esiste classe `Utente`, `Profilo`, `Sessione` né alcun
  concetto di identità persistente al di là del nome stringa passato alla
  `crea_partita_standard()`.

La cartella `bingo_game/infrastructure/` **non esiste**.

---

## 2. I 9 contratti inter-fase

---

#### Fase 1 — Infrastructure Layer e Persistenza Locale

- **Versione target**: v0.15.x
- **Cosa produce**: la cartella `bingo_game/infrastructure/` con il modulo
  `database/db_manager.py` (connessione SQLite, creazione schema, migrazioni
  via Alembic), le interfacce ABC `PartitaRepository`, `UtenteRepository`,
  `StatisticheRepository` e `CreditiRepository`, e le implementazioni SQLite
  di ognuna. Lo schema iniziale comprende le tabelle `utenti`, `partite`,
  `statistiche` e `crediti_log`. Il layer Infrastructure è coperto da test
  unitari con coverage minima richiesta dal progetto.
- **Cosa consuma**: nessun output di fasi precedenti. Dipende esclusivamente
  dal Dominio esistente (struttura `Partita`, `GiocatoreBase`, contratti
  di dati già esposti da `get_stato_completo()` e `storico_premi`).
- **Contratto in ingresso**: la cartella `bingo_game/infrastructure/` non esiste.
  `bingo_game/game_controller.py` non importa sqlite3 né librerie di rete.
  Il Dominio non contiene import di dipendenze esterne (verificabile con
  `grep -rn "import sqlite3\|import requests" bingo_game/` escludendo `ui/`
  e `infrastructure/` → zero risultati).
- **Contratto in uscita**: la cartella `bingo_game/infrastructure/` esiste e
  contiene almeno `database/db_manager.py` e `repositories/` con le interfacce
  ABC e le implementazioni SQLite. Nessun file in `bingo_game/domain/` (ovvero
  in `bingo_game/` escluso `ui/`, `logging/`, `infrastructure/`) importa da
  `bingo_game/infrastructure/` (verificabile con grep). I test del layer
  Infrastructure passano in isolamento.
- **Layer toccati**: Infrastructure (creato ex novo). Controller (aggiornato
  per accettare i repository come dipendenze iniettate, senza modificare la
  logica di orchestrazione).
- **Layer NON toccati**: Dominio (nessun file in `bingo_game/` fuori da
  `infrastructure/` può essere modificato per dipendere dall'Infrastructure).
  Presentazione (nessuna finestra wx viene toccata in questa fase). Il file
  `main.py` non viene modificato.

---

#### Fase 2 — Sistema Utente: Profilo, Registrazione, Login

- **Versione target**: v0.16.x
- **Cosa produce**: il modello `Utente` nel Dominio; l'`AuthService` nel
  layer Application (o Controller, da decidere in DESIGN dedicato); hash
  password con `argon2-cffi`; token di sessione con `PyJWT`; la finestra
  `FinestraRegistrazione` e la finestra `FinestraLogin` in wxPython con pieno
  supporto NVDA (label `wx.StaticText` associata, TabOrder, focus iniziale
  esplicito); il menu principale `FinestraPrincipale` aggiornato per
  mostrare le voci Registrazione e Login; il profilo utente accessibile a
  partita terminata.
- **Cosa consuma**: output di Fase 1 (tabella `utenti` nel DB, interfaccia
  `UtenteRepository` implementata in SQLite).
- **Contratto in ingresso**: `UtenteRepository` con implementazione SQLite
  esiste e i test passano. La cartella `bingo_game/infrastructure/` esiste.
  Non esiste ancora nessun file che implementi hashing di password o JWT
  (verificabile cercando `argon2` o `jwt` nei file del progetto → zero risultati).
- **Contratto in uscita**: esiste il modello `Utente` nel Dominio con almeno
  i campi `id`, `nome`, `email`, `password_hash`. L'`AuthService` espone
  almeno `registra(nome, email, password)` e `login(email, password)`.
  Le finestre `FinestraRegistrazione` e `FinestraLogin` esistono e ogni
  campo input ha una label `wx.StaticText` associata (verificabile leggendo
  il codice wx di ogni finestra). I test di autenticazione passano senza
  eseguire l'applicazione.
- **Layer toccati**: Dominio (nuovo modello `Utente`). Infrastructure
  (`UtenteRepository` implementato con persistenza hash). Presentazione
  (due nuove finestre wx, menu aggiornato). Controller (nuovo `AuthService`
  o estensione del controller esistente). `main.py` (aggiornato per
  inizializzare il database all'avvio dell'applicazione e chiuderlo
  esplicitamente nel blocco finally, accanto a `GameLogger.shutdown()`).
- **Layer NON toccati**: `Partita`, `Tabellone`, `Cartella`, `GiocatoreBase`,
  `GiocatoreUmano`, `GiocatoreAutomatico` — nessuna di queste classi viene
  modificata. Il flusso di gioco esistente (FinestraGioco, FinestraConfigurazione)
  non viene alterato in questa fase.

---

#### Fase 3 — Statistiche di Gioco e Storico

- **Versione target**: v0.17.x
- **Cosa produce**: il salvataggio automatico del risultato di ogni partita
  nel `StatisticheRepository` al termine della partita (invocato dal Controller
  dopo `termina_partita()`); la finestra `FinestraStatistiche` in wxPython
  con dati aggregati leggibili da NVDA (partite giocate, vinte, perse, premi
  per tipo, miglior partita); l'esportazione opzionale come file `.txt`.
- **Cosa consuma**: output di Fase 1 (tabella `statistiche` nel DB) e di
  Fase 2 (identità `Utente` per aggancio alle statistiche per-utente).
- **Contratto in ingresso**: `StatisticheRepository` con implementazione SQLite
  esiste. Il modello `Utente` esiste con un `id` stabile. Il `GameController`
  espone `ottieni_stato_sintetico()` e `partita_terminata()` già funzionanti
  (verificabile: questi metodi esistono già in v0.14.0-alpha).
- **Contratto in uscita**: a ogni chiamata a `partita_terminata()` che restituisce
  `True`, un record viene scritto nella tabella `statistiche` con almeno i campi
  `utente_id`, `data`, `turni`, `premi_vinti`, `ha_tombola`. La
  `FinestraStatistiche` legge e visualizza dati reali dal DB (non mock).
  Ogni widget della finestra ha label associata (verificabile nel codice wx).
- **Layer toccati**: Controller (aggiunta chiamata a `StatisticheRepository`
  al termine della partita). Infrastructure (`StatisticheRepository`
  implementato con lettura/scrittura). Presentazione (nuova `FinestraStatistiche`,
  menu aggiornato).
- **Layer NON toccati**: Dominio (nessuna classe di dominio importa o conosce
  `StatisticheRepository`). Il ciclo di gioco (`FinestraGioco`) non viene
  alterato in questa fase.

---

#### Fase 4 — Salvataggio e Ripresa della Partita

- **Versione target**: v0.18.x
- **Cosa produce**: il metodo `serializza_stato()` su `Partita` che restituisce
  un dizionario serializzabile completo (tabellone, cartelle con numeri segnati,
  premi assegnati, giocatori, configurazione); il metodo factory
  `ripristina_da_stato(stato)` nel Controller per ricostruire una `Partita`
  da un dizionario; il `PartitaRepository` con i metodi `salva_checkpoint()`
  e `carica_checkpoint()`; il menu "Pausa e Salva" nella `FinestraGioco`
  (esteso dal pulsante Pausa esistente); la finestra di selezione partite
  sospese accessibile da `FinestraPrincipale`.
- **Cosa consuma**: output di Fase 1 (tabella `partite` nel DB), output di
  Fase 2 (identità `Utente` per vincolare i checkpoint all'utente corrente).
- **Contratto in ingresso**: `PartitaRepository` con implementazione SQLite
  esiste. Il metodo `get_stato_completo()` esiste già su `Partita`
  (verificabile in v0.14.0-alpha). Il pulsante Pausa esiste in `FinestraGioco`
  (verificabile: `COLORE_BTN_PAUSA` è usato nella finestra di gioco).
- **Contratto in uscita**: il checkpoint è atomico (salvato in transazione DB
  — verificabile nel codice di `PartitaRepository.salva_checkpoint()`).
  Il metodo `ripristina_da_stato()` ricostruisce una `Partita` identica allo
  stato al momento del salvataggio (verificabile con un test: salva, ricarica,
  confronta `get_stato_completo()` prima e dopo). La finestra di selezione
  elenca solo le partite dell'utente corrente.
- **Layer toccati**: Dominio (nuovo metodo `serializza_stato()` su `Partita`).
  Controller (nuovo metodo factory `ripristina_da_stato()`). Infrastructure
  (`PartitaRepository` implementato). Presentazione (menu Pausa esteso,
  nuova finestra selezione checkpoint).
- **Layer NON toccati**: `Tabellone`, `Cartella`, `GiocatoreAutomatico` —
  nessuna di queste classi viene modificata. Il flusso di estrazione numeri
  e verifica premi non viene alterato.

---

#### Fase 5 — Sistema Crediti Virtuali

- **Versione target**: v0.19.x
- **Cosa produce**: il campo `crediti` nel modello `Utente`; il
  `CreditiService` nel layer Infrastructure che gestisce addebiti e accrediti
  tramite `CreditiRepository`; il log di ogni transazione in tabella
  `crediti_log`; la visualizzazione del saldo crediti in `FinestraPrincipale`
  e in `FinestraGioco`; l'annuncio NVDA del saldo a ogni variazione; il
  meccanismo di "crediti bonus" all'apertura giornaliera via `daily_reward`.
- **Cosa consuma**: output di Fase 1 (tabella `crediti_log` nel DB), output
  di Fase 2 (identità `Utente`), output di Fase 4 (il `CreditiService` può
  usare i checkpoint per vincolare il costo partita al completamento effettivo).
- **Contratto in ingresso**: il modello `Utente` esiste con un `id` stabile.
  La tabella `crediti_log` esiste nel DB. Il `CreditiRepository` è definito
  come interfaccia ABC in Infrastructure (dalla Fase 1).
- **Contratto in uscita**: ogni scrittura su `crediti_log` è tracciata con
  almeno `utente_id`, `tipo` (addebito/accredito), `importo`, `motivo`,
  `timestamp`. Il saldo non scende mai sotto zero lato codice (verificabile
  nel `CreditiService`: il metodo `addebita()` solleva eccezione se il saldo
  risultante è negativo). L'annuncio NVDA del saldo usa il sistema eventi
  esistente (non `print()`).
- **Layer toccati**: Dominio (campo `crediti` aggiunto a `Utente`).
  Infrastructure (`CreditiService`, `CreditiRepository` implementato).
  Controller (integrazione del `CreditiService` al termine di ogni partita).
  Presentazione (saldo visibile in due finestre, annuncio NVDA).
- **Layer NON toccati**: `Partita`, `Tabellone`, `Cartella`, tutto il flusso
  di estrazione e verifica premi. Il Dominio di gioco non conosce il concetto
  di crediti.

---

#### Fase 6 — Sound Effects e Audio Enhancement

- **Versione target**: v0.20.x
- **Cosa produce**: il `SoundManager` singleton in
  `bingo_game/infrastructure/audio/sound_manager.py` basato su `pygame.mixer`
  (già presente in `requirements.txt`); la cartella `bingo_game/assets/sounds/`
  con i file audio `.wav` o `.ogg` per i seguenti eventi: estrazione numero,
  ambo, terno, quaterna, cinquina, tombola, click navigazione, errore,
  benvenuto; l'opzione "Suoni: ON/OFF" nella `FinestraConfigurazione`;
  il controllo volume (slider wx con label NVDA) nella configurazione.
- **Cosa consuma**: nessun output di fasi precedenti obbligatorio. Questa
  fase è indipendente e può essere inserita dopo la Fase 1 in qualsiasi momento.
- **Contratto in ingresso**: il `WxRenderer` importa `IVocalizzatore` tramite
  dependency injection (verificabile in v0.14.0-alpha in `renderer_wx.py`).
  Non esiste nessun modulo `SoundManager` nel progetto.
- **Contratto in uscita**: il `SoundManager` viene inizializzato in `main.py`
  (o nel Controller) e iniettato nel renderer tramite dependency injection
  (non creato dentro FinestraGioco). I suoni vengono riprodotti su thread
  separato non bloccante rispetto al thread UI wxPython (verificabile nel
  codice di `SoundManager.play()`). L'opzione ON/OFF nella configurazione
  persiste tra sessioni (richiede Fase 1 per la persistenza).
- **Layer toccati**: Infrastructure (nuovo `SoundManager`). Presentazione
  (`WxRenderer` aggiornato per chiamare `SoundManager` dopo la vocalizzazione,
  mai prima; `FinestraConfigurazione` aggiornata con opzione suoni).
- **Layer NON toccati**: Dominio (nessuna classe di dominio conosce l'audio).
  Controller (`game_controller.py` non viene modificato). Il contratto
  `BaseRenderer` può richiedere un nuovo metodo `riproduci_suono()` oppure
  il `SoundManager` viene chiamato direttamente dal `WxRenderer` senza
  passare per il contratto astratto — la scelta va documentata nel DESIGN
  dedicato.

---

#### Fase 7 — Modalità Multiplayer Locale

- **Versione target**: v1.0.x
- **Cosa produce**: il supporto a più oggetti `GiocatoreUmano` all'interno
  della stessa `Partita` (oggi l'architettura supporta un solo umano per
  limitazione in `ottieni_giocatore_umano()`); il sistema "profilo attivo"
  per il login rapido tra profili locali; i turni alternati tra giocatori
  umani con notifica NVDA esplicita del cambio turno; le statistiche
  aggiornate separatamente per ciascun utente al termine della partita.
- **Cosa consuma**: output di Fase 2 (sistema utenti), Fase 3 (statistiche
  per-utente), Fase 4 (salvataggio partite multi-utente), Fase 5 (crediti
  separati per utente).
- **Contratto in ingresso**: il Dominio supporta esattamente un solo
  `GiocatoreUmano` (vincolo verificabile in `ottieni_giocatore_umano()`
  che restituisce un oggetto singolo). Questa limitazione deve essere rimossa
  **prima** di iniziare questa fase, introducendo `ottieni_giocatori_umani()`
  a lista. Non esiste ancora la logica di "turno corrente per utente umano N".
- **Contratto in uscita**: `ottieni_giocatori_umani()` restituisce una lista.
  Il flusso di gioco in `FinestraGioco` gestisce il passaggio del turno tra
  giocatori umani multipli (verificabile: esiste un meccanismo di selezione
  giocatore umano attivo nel ciclo turno). Le statistiche di ogni utente umano
  vengono aggiornate separatamente al termine della partita.
- **Layer toccati**: Dominio (rimozione vincolo singolo umano in `Partita` e
  nel Controller). Controller (`ottieni_giocatori_umani()` a lista).
  Presentazione (logica di cambio turno tra umani, notifica NVDA).
- **Layer NON toccati**: `Tabellone`, `Cartella`, `GiocatoreAutomatico`,
  il sistema eventi esistente. Infrastructure non viene modificata.

---

#### Fase 8 — Pre-Online: API Layer e Auth Distribuita

- **Versione target**: v1.1.x
- **Cosa produce**: le interfacce `NetworkAdapter` astratte in Infrastructure
  (ABC per `UserNetworkAdapter`, `GameNetworkAdapter`) che espongono le stesse
  firme delle repository SQLite; il server FastAPI minimale con endpoint CRUD
  per utenti, partite e statistiche, autenticazione JWT; la migrazione dello
  schema da SQLite locale a PostgreSQL sul server; la sincronizzazione cloud
  dei checkpoint tramite API REST (metodi `push_checkpoint()`,
  `pull_checkpoint()` su `NetworkAdapter`); i test di integrazione
  client-server in ambiente locale con server FastAPI in-process.
- **Cosa consuma**: output di tutte le fasi 1-7. Tutta l'infrastruttura
  locale deve essere stabile prima di introdurre la rete.
- **Contratto in ingresso**: le interfacce ABC dei repository esistono
  (introdotte in Fase 1). Il Controller usa dependency injection per i
  repository (non li istanzia direttamente). Non esiste nessun `NetworkAdapter`
  nel progetto (verificabile cercando `requests` o `websockets` nei file non-UI).
- **Contratto in uscita**: il `NetworkAdapter` implementa le stesse interfacce
  ABC dei repository SQLite. Il Controller non conosce la differenza tra
  esecuzione locale (SQLite) e esecuzione online (NetworkAdapter): la selezione
  avviene in `main.py` o in un modulo di configurazione (verificabile:
  `game_controller.py` non importa né `requests` né `websockets`).
  Il server FastAPI risponde correttamente a tutti gli endpoint CRUD con
  autenticazione JWT attiva.
- **Layer toccati**: Infrastructure (nuovi `NetworkAdapter`). Il server
  FastAPI è un progetto separato fuori dalla cartella `bingo_game/`.
  `main.py` aggiornato per selezionare il backend (locale vs. rete).
- **Layer NON toccati**: Dominio (nessuna modifica). Controller (solo
  aggiornamento del punto di iniezione delle dipendenze). Presentazione
  (nessuna finestra wx viene modificata). Il flusso di gioco è invariato.

---

#### Fase 9 — Multiplayer Online

- **Versione target**: v2.0.x
- **Cosa produce**: il server FastAPI con WebSocket per comunicazione real-time;
  il sistema Lobby (crea stanza, cerca stanza, lista stanze pubbliche, wait room);
  l'autorità del tabellone lato server (il numero estratto è deciso dal server,
  non dal client); la chat testuale in lobby leggibile da NVDA; la classifica
  globale (leaderboard); la sincronizzazione crediti online; il
  `NetworkAdapter` WebSocket implementato nel client wxPython.
- **Cosa consuma**: output di Fase 8 (server FastAPI operativo, interfacce
  `NetworkAdapter` definite).
- **Contratto in ingresso**: il `NetworkAdapter` astratto esiste con interfacce
  stabili. Il server FastAPI risponde ai CRUD endpoint. Il client wxPython
  non istanzia direttamente `Tabellone` in modalità online (il tabellone
  online è gestito dal server).
- **Contratto in uscita**: in modalità online il `Tabellone` locale non viene
  usato per le estrazioni: il numero estratto arriva esclusivamente via
  WebSocket dal server (verificabile: in modalità online
  `Tabellone.estrai_numero()` non viene mai chiamato sul client). La chat
  in lobby annuncia ogni nuovo messaggio tramite il sistema eventi NVDA
  esistente. Il leaderboard legge dati reali dal server (non mock locali).
- **Layer toccati**: Infrastructure (implementazione `NetworkAdapter` WebSocket).
  Il server FastAPI (progetto separato) con WebSocket handler. Presentazione
  (nuove finestre Lobby, Chat, Leaderboard con accessibilità NVDA). Controller
  (selezione modalità locale vs. online).
- **Layer NON toccati**: il Dominio di gioco (Partita, Cartella, Tabellone,
  Giocatori) non viene modificato dalla modalità online (il Dominio descrive
  la regola del gioco, indipendentemente da chi estrae il numero).

---

## 3. Vincoli architetturali non negoziabili

---

**Vincolo 1 — Regola testo-widget-voce**

- **Regola**: dentro ogni metodo handler del renderer, gli aggiornamenti
  visivi ai widget wx precedono sempre la chiamata a ao2/vocalizza.
- **Motivazione**: NVDA intercetta i cambiamenti dei widget wx (SetLabel,
  AppendText) attraverso le API di accessibilità di Windows. Se la voce
  precede il widget, NVDA può leggere il vecchio testo oppure rimanere silente.
  Questo pattern è codificato nel contratto `BaseRenderer` ("Ordine fisso
  handler: testo → widget → voce") ed è la causa originaria di vari bug
  di benvenuto NVDA risolti in v0.12.x-v0.14.x del CHANGELOG.
- **Come verificarlo**: leggere ogni metodo `_handle_*` di `WxRenderer`:
  le chiamate `.SetLabel()`, `.AppendText()` o analoghi devono comparire
  prima di qualsiasi chiamata a `self._vocalizzatore.vocalizza_testo()`.

---

**Vincolo 2 — Dominio puro**

- **Regola**: nessuna classe in `bingo_game/` (escluse le sottocartelle `ui/`,
  `logging/` e il futuro `infrastructure/`) può importare wxPython, sqlite3,
  librerie di rete o qualsiasi dipendenza esterna non presente nella standard
  library Python.
- **Motivazione**: il Dominio deve essere testabile senza UI, senza DB e senza
  rete. Questa proprietà esiste già in v0.14.0-alpha ed è il presupposto che
  rende possibile aggiungere Infrastructure senza riscrivere il motore di gioco.
- **Come verificarlo**: `grep -rn "import wx\|import sqlite3\|import requests\|import websockets" bingo_game/`
  escludendo le cartelle `ui/`, `logging/` e `infrastructure/` → zero risultati.

---

**Vincolo 3 — Accessibilità NVDA non regredisce**

- **Regola**: ogni nuova finestra `wx.Frame` o `wx.Dialog`, ogni nuovo campo
  di input e ogni nuova notifica deve avere: label `wx.StaticText` associata al
  controllo, TabOrder corretto definito esplicitamente, focus iniziale assegnato
  con `SetFocus()` dopo che il widget è visibile.
- **Motivazione**: il progetto ha come utente primario dichiarato un programmatore
  non vedente con NVDA su Windows 11. Ogni regressione di accessibilità blocca
  l'uso dell'applicazione. Il CHANGELOG registra ripetutamente bug di focus e
  benvenuto NVDA tra v0.12.x e v0.14.x come conseguenza della mancanza di
  questi tre elementi.
- **Come verificarlo**: leggere il costruttore di ogni nuova classe `wx.Frame`
  o `wx.Dialog`: deve contenere almeno una chiamata `wx.StaticText` con testo
  descrittivo, una lista di `MoveAfterInTabOrder()` o un `wx.Panel` con
  `SetTabOrder()`, e una chiamata `SetFocus()` esplicita.

---

**Vincolo 4 — Infrastructure mai nel Dominio**

- **Regola**: il layer Infrastructure dipende dal Dominio; il Dominio non
  sa che Infrastructure esiste.
- **Motivazione**: se il Dominio importasse da Infrastructure (anche solo per
  salvare uno stato), si creerebbe una dipendenza ciclica e il motore di gioco
  diventerebbe non testabile senza DB. Il Repository Pattern risolve questo:
  sono i repository a conoscere le entità di Dominio, non il contrario.
- **Come verificarlo**: `grep -rn "from bingo_game.infrastructure\|import infrastructure"` 
  all'interno dei file in `bingo_game/` escludendo la cartella `infrastructure/`
  → zero risultati.

---

**Vincolo 5 — Renderer come unico ponte**

- **Regola**: la Presentazione comunica con il Dominio esclusivamente tramite
  il sistema eventi (`EsitoAzione`, `EventoAzione`) e il contratto `BaseRenderer`.
  Nessuna finestra wx importa direttamente classi di Dominio per invocare metodi
  su di esse.
- **Motivazione**: se `FinestraGioco` importasse `Partita` direttamente,
  qualsiasi refactor del Dominio romperebbe la UI. Il contratto BaseRenderer
  con `EsitoAzione` isola le finestre dai dettagli implementativi del motore.
  Questo pattern è già applicato in v0.14.0-alpha: `FinestraGioco` usa
  `ComandiSistema` e `ComandiGiocatoreUmano` come facade.
- **Come verificarlo**: `grep -n "from bingo_game.partita\|from bingo_game.tabellone\|from bingo_game.cartella" bingo_game/ui/`
  → zero risultati (la UI importa solo da `comandi_partita` e dal sistema eventi).

---

**Vincolo 6 — Nessuna stringa hardcoded nel renderer**

- **Regola**: ogni testo vocalizzato o mostrato in un widget wx deve provenire
  dal catalogo `bingo_game/ui/locales/` tramite `_formatta_testo_da_catalogo()`.
  Nessuna stringa di testo umano può essere scritta inline in un metodo handler.
- **Motivazione**: la centralizzazione dei testi permette localizzazione futura
  e mantiene coerenza tra voce e widget (lo stesso testo viene usato per
  entrambi). Questo vincolo è codificato nel contratto `BaseRenderer`.
- **Come verificarlo**: ogni metodo `_handle_*` o `_ao2_*` di `WxRenderer`
  non contiene stringhe di testo in italiano inline (eccetto costanti locali
  per separatori come spazio e punto).

---

**Vincolo 7 — Il Controller non scrive su stdout**

- **Regola**: nessun metodo in `game_controller.py` e in `comandi_partita.py`
  può chiamare `print()`.
- **Motivazione**: il Controller era originariamente progettato per un'interfaccia
  da terminale. La migrazione al layer wx richiede che tutto l'output passi
  esclusivamente attraverso il sistema di logging categorizzato e il renderer.
  Un `print()` in Controller bypasserebbe sia NVDA sia il log file.
- **Come verificarlo**: `grep -n "print(" bingo_game/game_controller.py bingo_game/comandi_partita.py`
  → zero risultati.

---

## 4. Mappa delle dipendenze tra fasi

| Fase | Dipende da | Sblocca | Rischio di accoppiamento |
|------|-----------|---------|--------------------------|
| 1 — Infrastructure Layer | Nessuna | 2, 4, 6 | Alto — definire interfacce ABC sbagliate qui inquina tutte le fasi successive |
| 2 — Sistema Utente | 1 | 3, 5, 7 | Alto — il modello Utente è condiviso da statistiche, crediti e multiplayer |
| 3 — Statistiche | 1, 2 | 7 | Basso — layer foglia senza dipendenze a valle |
| 4 — Salvataggio partita | 1, 2 | 5, 7 | Medio — il formato di serializzazione dello stato deve sopravvivere alle evoluzioni del Dominio |
| 5 — Crediti virtuali | 1, 2, 4 | 7, 8 | Medio — l'audit trail di crediti deve essere coerente col server in Fase 8 |
| 6 — Sound Effects | 1 (per persistenza ON/OFF) | Nessuna | Basso — layer foglia, nessuna fase dipende dai suoni |
| 7 — Multiplayer locale | 2, 3, 4, 5 | 8 | Medio — richiede rimozione del vincolo singolo-umano nel Dominio |
| 8 — API Layer | 1, 2, 3, 4, 5, 6, 7 | 9 | Alto — le interfacce NetworkAdapter devono essere identiche a quelle dei repository SQLite |
| 9 — Multiplayer online | 8 | Nessuna | Alto — dipende dalla stabilità del server FastAPI e dalla latenza WebSocket |

---

## 5. Stack tecnologico vincolante

---

**SQLite (standard library `sqlite3`)**

- **Tecnologia**: `sqlite3` — modulo standard Python, nessuna
  versione aggiuntiva da installare. Già presente nell'installazione
  base di Python 3.11.
- **Fase di introduzione**: Fase 1. Utilizzato per tutte le fasi
  locali fino alla Fase 7 inclusa.
- **Posizione architetturale**: Infrastructure — `db_manager.py`
  e tutte le implementazioni concrete dei repository fino alla Fase 7.
- **Compatibilità con NVDA**: Nessuno. SQLite non ha interazione
  con il canale vocale.
- **Reversibilità**: Alta per il client. Le interfacce ABC dei
  repository (introdotte in Fase 1) isolano il resto del codice
  dall'implementazione SQLite: in Fase 8 si sostituisce solo
  l'implementazione concreta lato server, non le interfacce.
  Il client wxPython continua a usare SQLite anche dopo la Fase 8.
- **Nota strategica**: la scelta dell'ORM o del driver asincrono
  per il database del server online viene presa durante il DESIGN
  dedicato alla Fase 8, non prima. Introdurre uno strumento come
  SQLAlchemy prima che il problema che risolve sia presente
  aggiungerebbe complessità non necessaria alle Fasi 1-7.

---

**argon2-cffi**

- **Tecnologia**: `argon2-cffi >= 21.x`.
- **Fase di introduzione**: Fase 2.
- **Posizione architetturale**: Infrastructure — `AuthService` per hash password.
- **Compatibilità con NVDA**: Nessuno.
- **Reversibilità**: Bassa. Cambiare algoritmo di hash dopo che gli utenti
  sono registrati richiede una procedura di migrazione password.

---

**PyJWT**

- **Tecnologia**: `PyJWT >= 2.x`.
- **Fase di introduzione**: Fase 2.
- **Posizione architetturale**: Infrastructure — `AuthService` per token sessione.
  In Fase 8 lo stesso meccanismo JWT viene usato lato server.
- **Compatibilità con NVDA**: Nessuno.
- **Reversibilità**: Media. JWT è uno standard; sostituire la libreria richiede
  solo il cambio della chiamata di firma e verifica.

---

**pygame.mixer**

- **Tecnologia**: `pygame >= 2.6.1` (già presente in `requirements.txt`).
- **Fase di introduzione**: Fase 6.
- **Posizione architetturale**: Infrastructure —
  `bingo_game/infrastructure/audio/sound_manager.py`.
- **Compatibilità con NVDA**: Rischio noto. `pygame.mixer` inizializza un
  device audio che potrebbe interferire con il buffer AO2 se usato sullo
  stesso thread UI. Il `SoundManager` deve operare su thread separato.
- **Reversibilità**: Media. `playsound` è alternativa più leggera ma meno
  controllabile. `pygame.mixer` è già dipendenza del progetto.

---

**FastAPI**

- **Tecnologia**: `fastapi >= 0.110`.
- **Fase di introduzione**: Fase 8.
- **Posizione architetturale**: progetto server separato fuori da `bingo_game/`.
  Il client wxPython non importa FastAPI.
- **Compatibilità con NVDA**: Nessuno (lato server).
- **Reversibilità**: Media. FastAPI può essere sostituito con Django Channels
  se i WebSocket richiedono funzionalità avanzate, ma la migrazione implica
  riscrivere gli endpoint.

---

**websockets / FastAPI WebSocket nativo**

- **Tecnologia**: `websockets >= 12.x` oppure WebSocket nativo di FastAPI.
- **Fase di introduzione**: Fase 9.
- **Posizione architetturale**: Infrastructure — `NetworkAdapter` WebSocket
  nel client. Server FastAPI lato server.
- **Compatibilità con NVDA**: Da verificare. Il ricevimento asincrono di
  messaggi WebSocket deve avvenire su thread separato e comunicare al thread
  UI tramite `wx.CallAfter()` per non bloccare il ciclo di eventi wx.
- **Reversibilità**: Bassa. Una volta costruita la logica di gioco real-time
  su WebSocket, passare a un'altra tecnologia di trasporto richiederebbe un
  refactor significativo del multiplayer.

---

**PostgreSQL + asyncpg**

- **Tecnologia**: PostgreSQL (server); `asyncpg >= 0.29` (driver Python async).
- **Fase di introduzione**: Fase 8 (lato server), sostituisce SQLite solo
  nel backend online.
- **Posizione architetturale**: Infrastructure — repository online nel server
  FastAPI. Il client wxPython usa ancora SQLite per la cache locale.
- **Compatibilità con NVDA**: Nessuno.
- **Reversibilità**: Bassa rispetto al server. Il client non è impattato
  perché continua a usare SQLite tramite le stesse interfacce ABC.

---

## 6. Assunzioni e incertezze

---

**Assunzione 1 — Un solo giocatore umano per partita**

- **Cosa non si sa**: l'architettura attuale in `game_controller.py` prevede
  `ottieni_giocatore_umano()` come metodo che restituisce un singolo oggetto.
  Non è definito come il ciclo turno gestirà più umani (alternanza, input
  simultaneo, timer separati).
- **Impatto se l'assunzione è sbagliata**: Fase 7 richiede un refactor del
  Controller e della logica di binding tastiera in `FinestraGioco` per gestire
  il giocatore umano attivo corrente.
- **Quando si saprà**: in Fase 7, durante il DESIGN dedicato al multiplayer locale.

---

**Assunzione 2 — Partita sempre locale, nessuna sessione persistente**

- **Cosa non si sa**: il modello `Partita` è progettato per l'uso in memoria.
  Non è definito quante informazioni siano necessarie in un checkpoint minimo
  per ricostruire fedelmente una partita (es.: il generatore random del
  tabellone, lo stato interno dei timer del ciclo V2).
- **Impatto se l'assunzione è sbagliata**: il metodo `serializza_stato()` (Fase 4)
  potrebbe non essere sufficiente a ricostruire lo stato esatto se il ciclo V2
  usa timer non serializzabili con stato interno.
- **Quando si saprà**: in Fase 4, durante l'implementazione di `serializza_stato()`.

---

**Assunzione 3 — Il database locale è SQLite per tutte le fasi pre-online**

- **Cosa non si sa**: SQLite ha limitazioni di concorrenza (un solo writer alla
  volta). Se in Fase 7 più giocatori umani condividono lo stesso PC con profili
  distinti e si prevede accesso concorrente al DB, SQLite potrebbe non essere
  adeguato.
- **Impatto se l'assunzione è sbagliata**: potrebbe essere necessario passare
  a PostgreSQL già in Fase 7 invece di Fase 8.
- **Quando si saprà**: in Fase 7, valutando il pattern di accesso concorrente.

---

**Assunzione 4 — pygame.mixer non interferisce con AO2 su Windows 11 + NVDA**

- **Cosa non si sa**: `pygame.mixer` inizializza il device audio di sistema.
  Con NVDA attivo su Windows 11, due driver audio che usano lo stesso device
  possono produrre conflitti o ritardi nella vocalizzazione (noto come
  "audio ducking").
- **Impatto se l'assunzione è sbagliata**: il `SoundManager` deve usare un
  device audio dedicato separato da quello usato da NVDA, oppure usare un
  canale virtuale. Questo potrebbe richiedere la sostituzione di `pygame.mixer`
  con la libreria `playsound` o con le API DirectSound di Windows.
- **Quando si saprà**: in Fase 6, durante il primo test di integrazione
  sound + NVDA su macchina reale.

---

**Assunzione 5 — Il formato di serializzazione dello stato di Partita è stabile**

- **Cosa non si sa**: il dizionario restituito da `get_stato_completo()` è usato
  in v0.14.0-alpha solo per la visualizzazione. Non è specificato se cambierà
  forma nelle fasi successive (es. aggiunta di campi per multi-utente in Fase 7).
- **Impatto se l'assunzione è sbagliata**: i checkpoint salvati in Fase 4 con
  un formato precedente potrebbero non essere caricabili dopo un aggiornamento
  che cambia la struttura del dizionario. È necessario un version tag su ogni
  checkpoint.
- **Quando si saprà**: in Fase 4, definendo il formato di serializzazione con
  version tag obbligatorio.

---

**Assunzione 6 — Il canale WebSocket è sufficiente per la latenza di gioco**

- **Cosa non si sa**: la tombola è un gioco a turni, non real-time stretto.
  Tuttavia, in multiplayer online la latenza del WebSocket su connessioni
  instabili potrebbe causare desincronizzazioni (es.: due client vedono
  numeri diversi). La strategia di reconciliation lato server non è ancora
  definita.
- **Impatto se l'assunzione è sbagliata**: la Fase 9 richiede una logica di
  predizione lato client e di reconciliation server più complessa di una
  semplice trasmissione del numero estratto.
- **Quando si saprà**: in Fase 9, durante il DESIGN del protocollo WebSocket.

---

## 7. Istruzioni per gli agenti implementatori

Le seguenti regole si applicano a qualsiasi agente Copilot che lavori su una
qualsiasi fase della roadmap. Sono derivate dai vincoli della Sezione 3 e dai
Fixed ricorrenti nel CHANGELOG tra v0.12.x e v0.14.0-alpha.

- Non modificare alcun file in `bingo_game/` (escluse `ui/`, `logging/`,
  `infrastructure/`) per aggiungere import da librerie esterne. Ogni violazione
  rompe il Vincolo 2.
- Non creare finestre wx o dialog senza assegnare una label `wx.StaticText`
  esplicita a ogni controllo input. Il pattern ricorrente di bug NVDA nel
  CHANGELOG dimostra che questa regola non è opzionale.
- Non assegnare `SetFocus()` prima che il widget sia visibile e prima che
  l'annuncio NVDA sia stato inviato. L'ordine corretto, validato in
  v0.12.x-v0.14.x, è: costruzione widget → `Show()` → `wx.CallAfter(SetFocus)`.
- Non chiamare `self._vocalizzatore.vocalizza_testo()` prima di aver aggiornato
  i widget wx corrispondenti. Rispettare il Vincolo 1 in ogni nuovo metodo
  handler del renderer.
- Non aggiungere stringhe di testo italiano inline nei metodi handler del
  renderer. Aggiungere la chiave nel catalogo `bingo_game/ui/locales/it.py`
  e usare `_formatta_testo_da_catalogo()`.
- Non importare classi di Dominio direttamente nelle finestre wx. Usare
  esclusivamente le facade `ComandiSistema` e `ComandiGiocatoreUmano`. Rispettare
  il Vincolo 5.
- Non definire le implementazioni concrete dei repository senza prima definire
  le interfacce ABC. Le interfacce ABC devono esistere prima delle implementazioni
  per garantire la reversibilità in Fase 8.
- Non usare `print()` in `game_controller.py` o in `comandi_partita.py`.
  Rispettare il Vincolo 7. Usare i sub-logger `tombola_stark.game`,
  `tombola_stark.prizes`, `tombola_stark.system`, `tombola_stark.errors`.
- Non modificare `Tabellone`, `Cartella` o `GiocatoreAutomatico` per fasi che
  non li impattano. Se una fase non dichiara un layer tra quelli "toccati"
  nella Sezione 2, nessun file di quel layer deve essere modificato.
- Prima di ogni fase, verificare i contratti in ingresso elencati nella
  Sezione 2. Se un contratto in ingresso non è soddisfatto, la fase non può
  iniziare.
- Ogni modifica al contratto `BaseRenderer` (aggiunta di un metodo astratto)
  richiede l'aggiornamento di `WxRenderer` nella stessa pull request, altrimenti
  il progetto non si avvia. Il pattern di errore ricorrente "AttributeError" su
  metodi mancanti del renderer è documentato nel CHANGELOG.
- Non inizializzare `pygame.mixer` sul thread UI principale. Il `SoundManager`
  deve usare un thread separato con comunicazione asincrona verso il thread UI.
- Aggiungere un version tag (`schema_version`) a ogni checkpoint serializzato
  in Fase 4. Senza versioning, i checkpoint diventano inutilizzabili dopo
  qualsiasi modifica allo schema.
- Non scrivere direttamente in tabella `crediti_log` dall'esterno del
  `CreditiService`. L'audit trail dei crediti è un dato sensibile per la
  futura monetizzazione e deve passare esclusivamente dal service dedicato.

---

*Documento prodotto da Agent-Analyze — Tombola Stark Framework v1.10.3*
*Baseline di riferimento: v0.14.0-alpha — 14 aprile 2026*
