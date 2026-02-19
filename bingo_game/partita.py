"""
CLASSE PER LA GESTIONE DELLA PARTITA
Modulo: bingo_game.partita

Tombola / Bingo – Coordinamento di tabellone, giocatori e cartelle
==================================================================

OVERVIEW DEL MODULO
-------------------

Questo modulo definisce la classe Partita, responsabile del
coordinamento di una partita di tombola/bingo.

La classe Partita mette in relazione:

- il tabellone delle estrazioni (numeri da 1 a 90);
- l'elenco dei giocatori (umani e automatici);
- le cartelle assegnate ai giocatori;
- lo stato di avanzamento della partita (non iniziata, in corso, terminata);
- l'assegnazione dei premi (ambo, terno, quaterna, cinquina, tombola).

La creazione concreta dei giocatori e delle cartelle è delegata a un
livello superiore (interfaccia/controller), che fornisce a Partita
giocatori già configurati.

STRUTTURA LOGICA DELLA CLASSE
-----------------------------

La classe Partita è organizzata in più gruppi principali di metodi:

1) Costruzione e stato base della partita

- __init__(tabellone, giocatori=None):
  inizializza la partita con un tabellone e una lista opzionale di
  giocatori già registrati. La partita parte nello stato "non_iniziata".

- get_giocatori():
  ritorna la lista dei giocatori registrati alla partita.

- get_numero_giocatori():
  ritorna il numero totale di giocatori registrati.

- get_stato_partita() [previsto]:
  ritorna lo stato corrente della partita ("non_iniziata",
  "in_corso", "terminata").

- is_pronta_per_iniziare():
  verifica se la partita soddisfa i requisiti minimi per essere
  avviata (es. almeno due giocatore registrati e stato "non_iniziata").

2) Gestione del roster di giocatori

- aggiungi_giocatore(giocatore):
  aggiunge un giocatore alla partita, verificando che la partita
  non sia ancora iniziata e che non sia stato superato il limite
  massimo di giocatori ammessi.

(Altri eventuali metodi in futuro potranno gestire la rimozione di
giocatori o controlli più specifici sul tipo di giocatore.)

3) Avvio e terminazione della partita [da implementare]

- avvia_partita():
  porta la partita dallo stato "non_iniziata" allo stato "in_corso",
  dopo aver verificato che i requisiti minimi siano soddisfatti.
  Può occuparsi anche di eventuali reset del tabellone.

- termina_partita():
  porta la partita nello stato "terminata". Può in futuro registrare
  vincitori, statistiche o log di fine partita.

4) Gestione delle estrazioni [da implementare]

- estrai_prossimo_numero():
  chiede al tabellone il prossimo numero da estrarre, aggiorna lo
  stato interno (es. ultimo numero estratto) e coordina
  l'aggiornamento dei giocatori.

- aggiorna_giocatori_con_numero(numero):
  notifica a tutti i giocatori il numero estratto, delegando a ciascun
  giocatore l'aggiornamento delle proprie cartelle (ad esempio tramite
  aggiorna_con_numero()).

- get_ultimo_numero_estratto():
  ritorna l'ultimo numero estratto dal tabellone, oppure None se
  non è ancora stato estratto alcun numero.

5) Verifica dei premi [da implementare]

- verifica_premi_per_cartella(cartella):
  calcola i premi presenti su una singola cartella (ambo, terno,
  quaterna, cinquina, tombola), utilizzando i metodi di stato
  già definiti nella classe Cartella.

- verifica_premi():
  scorre tutte le cartelle di tutti i giocatori e individua i premi
  ottenuti, aggiornando lo stato interno dei premi già assegnati e
  restituendo le informazioni utili per l'interfaccia (quale giocatore,
  quale cartella, quale premio).

- has_tombola() a livello di partita [previsto]:
  ritorna True se almeno una cartella di qualsiasi giocatore ha
  completato la tombola.

6) Ciclo di gioco ad alto livello [da implementare]

- esegui_turno():
  esegue un "passo" della partita: estrae un numero dal tabellone,
  aggiorna i giocatori e verifica se sono stati assegnati nuovi premi.
  Se viene rilevata una tombola, termina la partita.

- is_terminata():
  helper che ritorna True se la partita è nello stato "terminata".

7) Metodi di stato per l'interfaccia [da implementare]

- get_stato_giocatori():
  ritorna una rappresentazione sintetica dello stato dei giocatori
  (es. nome, id, numero di cartelle, presenza di tombola).

- get_stato_completo():
  ritorna un riepilogo complessivo della partita (stato, ultimo numero
  estratto, premi assegnati, elenco sintetico dei giocatori).

NOTE DI UTILIZZO
----------------

- La classe Partita non gestisce direttamente input/output verso
  l'utente. La responsabilità di leggere comandi, confermare azioni
  e presentare le informazioni (via terminale o interfaccia accessibile)
  è delegata a uno strato superiore.

- La creazione dei giocatori (umani e automatici) e delle loro cartelle
  avviene al di fuori della Partita: il "controller" si occupa di
  configurare il numero di giocatori, di bot e di cartelle, e poi
  registra questi oggetti nella Partita prima dell'avvio.
"""

from __future__ import annotations
#import dei tipi di dati avanzato 
from typing import List, Optional, Any, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from bingo_game.cartella import Cartella

#import dei file di gioco
from bingo_game.tabellone import Tabellone
from bingo_game.players.giocatore_base import GiocatoreBase
# Import pulito grazie all'init aggiornato
from bingo_game.exceptions import (
    PartitaException,
    PartitaStatoException,
    PartitaGiaIniziataException,
    PartitaNonInCorsoException,
    PartitaGiaTerminataException,
    PartitaRosterException,
    PartitaRosterPienoException,
    PartitaGiocatoriInsufficientiException,
    PartitaGiocatoreTypeException,
    PartitaGiocatoreGiaPresenteException,
    PartitaGiocoException,
    PartitaNumeriEsauritiException
)


class Partita:
    """
    Classe che rappresenta una partita di tombola/bingo.

    Gestisce:
    - il tabellone delle estrazioni;
    - l'elenco dei giocatori partecipanti;
    - lo stato di avanzamento della partita;
    - i limiti logici su numero di giocatori.

    La logica di estrazione numeri e verifica dei premi verrà
    aggiunta progressivamente.
    """

    # Limiti consigliati sul numero di giocatori
    MIN_GIOCATORI: int = 2
    MAX_GIOCATORI: int = 8  # es. 1 umano + fino a 7 bot

    def __init__(self, tabellone: Tabellone, giocatori: Optional[List[GiocatoreBase]] = None) -> None:
        """
        Inizializza una nuova partita.

        Parametri:
        - tabellone: Tabellone
          Istanza del tabellone da usare per le estrazioni.
        - giocatori: Optional[List[GiocatoreBase]]
          Lista opzionale di giocatori già creati e configurati
          (umani e automatici). Se None, la partita parte senza
          giocatori e questi potranno essere aggiunti in seguito.

        La partita inizia nello stato "non iniziata".
        """
        self.tabellone = tabellone
        self.giocatori: List[GiocatoreBase] = giocatori[:] if giocatori else []
        self.stato_partita: str = "non_iniziata"  # possibili valori: non_iniziata, in_corso, terminata
        self.ultimo_numero_estratto: Optional[int] = None
        self.premi_gia_assegnati = set()



    #metodo che ritorna una lista con i giocatori partecipanti
    def get_giocatori(self) -> List[GiocatoreBase]:
        """
        Ritorna la lista dei giocatori registrati alla partita.

        Nota:
        - Ritorna la lista interna; si raccomanda di non modificarla
          direttamente dall'esterno.
        """
        return self.giocatori


    #metodo che ritorna il numero di giocatori partecipanti
    def get_numero_giocatori(self) -> int:
        """
        Ritorna il numero totale di giocatori registrati alla partita.
        """
        return len(self.giocatori)


    #metodo che ritorna lo stato corrente della partita 
    def get_stato_partita(self):
        """
        Ritorna lo stato attuale della partita.

        Lo stato indica a che fase si trova la partita:
        - "non_iniziata": la partita è stata creata ma non ancora avviata;
        - "in_corso": la partita è stata avviata e sono in corso le estrazioni;
        - "terminata": la partita è finita (es. perché è stata fatta una tombola).

        Ritorna:
        - str: il valore dello stato corrente della partita.

        Utilizzo tipico:
        - Controllare se è possibile aggiungere altri giocatori (solo se
          lo stato è "non_iniziata").
        - Decidere se l'interfaccia deve permettere l'estrazione del prossimo
          numero (solo se lo stato è "in_corso").
        - Riconoscere quando la partita è finita (stato == "terminata").
        """
        return self.stato_partita


    #metodo che verifica se la partita soddisfa i requisiti minimi per essere avviata
    def is_pronta_per_iniziare(self) -> bool:
        """
        Verifica se la partita soddisfa i requisiti minimi per essere avviata.

        Requisiti minimi:
        - almeno MIN_GIOCATORI giocatori registrati;
        - stato attuale 'non_iniziata'.

        Ritorna:
        - True se la partita può essere avviata.
        - False altrimenti.
        """
        if self.stato_partita != "non_iniziata":
            return False
        return self.get_numero_giocatori() >= self.MIN_GIOCATORI


    """Sezione 2: Gestione del roster di giocatori"""

    #metodo per aggiungere un giocatore alla partita
    def aggiungi_giocatore(self, giocatore: GiocatoreBase) -> None:
        """
        Aggiunge un giocatore alla partita.

        Parametri:
        - giocatore: GiocatoreBase
          Istanza di GiocatoreBase o di una sua sottoclasse
          (GiocatoreUmano, GiocatoreAutomatico).

        Vincoli:
        - Non è possibile aggiungere giocatori dopo l'inizio della partita.
        - Il numero totale di giocatori non deve superare MAX_GIOCATORI.

                Raises:
        - PartitaGiaIniziataException: se la partita non è nello stato 'non_iniziata'.
        - PartitaGiocatoreTypeException: se l'oggetto passato non è un giocatore valido.
        - PartitaGiocatoreGiaPresenteException: per evitare duplicati di giocatori.
        - PartitaRosterPienoException: se è stato raggiunto il limite MAX_GIOCATORI.
        """
        # Non permettere modifiche al roster a partita in corso o terminata
        if self.stato_partita != "non_iniziata":
            raise PartitaGiaIniziataException(
                f"Impossibile aggiungere giocatori: la partita è nello stato '{self.stato_partita}'."
            )

        # Verifica tipo del giocatore
        if not isinstance(giocatore, GiocatoreBase):
            raise PartitaGiocatoreTypeException(
                f"Il giocatore deve essere un'istanza di GiocatoreBase, ricevuto: {type(giocatore)}"
            )

        # CONTROLLO DUPLICATI
        if giocatore in self.giocatori:
            raise PartitaGiocatoreGiaPresenteException(
                f"Il giocatore '{giocatore.nome}' (ID: {giocatore.id_giocatore}) è già presente nella partita."
            )

        # Verifica limite massimo di giocatori
        if len(self.giocatori) >= self.MAX_GIOCATORI:
            raise PartitaRosterPienoException(
                f"Numero massimo di giocatori raggiunto ({self.MAX_GIOCATORI}). "
                "Impossibile aggiungere altri giocatori."
            )

        self.giocatori.append(giocatore)


    """Sezione 3: Avvio e terminazione della partita"""

    #metodo che porta la partita dallo stato "non_iniziata" allo stato "in_corso", dopo aver verificato che i requisiti minimi siano soddisfatti.
    def avvia_partita(self):
        """
        Avvia la partita, portandola dallo stato "non_iniziata" a "in_corso".

        Prima di avviare, verifica che:
        - la partita non sia già stata avviata o terminata (stato deve essere
          "non_iniziata");
        - i prerequisiti minimi siano soddisfatti (almeno MIN_GIOCATORI
          registrati).

        Se uno di questi controlli fallisce, solleva un'eccezione con un
        messaggio descrittivo.

        Una volta avviata, la partita è pronta per iniziare le estrazioni
        e l'aggiornamento dei giocatori.

        Eccezioni:
        - PartitaGiaIniziataException: se la partita è già avviata o terminata.
        - PartitaGiocatoriInsufficientiException: se numero insufficiente di giocatori.
        """
        # Verifica che la partita non sia già stata avviata
        if self.stato_partita != "non_iniziata":
            raise PartitaGiaIniziataException(
                f"Impossibile avviare la partita: lo stato è '{self.stato_partita}'. "
                "La partita può essere avviata solo dallo stato 'non_iniziata'."
            )

        # Verifica che i prerequisiti minimi siano soddisfatti
        if not self.is_pronta_per_iniziare():
            raise PartitaGiocatoriInsufficientiException(
                f"Impossibile avviare la partita: numero insufficiente di giocatori. "
                f"Richiesti almeno {self.MIN_GIOCATORI}, presenti {self.get_numero_giocatori()}."
            )

        # Se tutti i controlli sono passati, avvia la partita
        self.stato_partita = "in_corso"



    #porta la partita nello stato "terminata". Può in futuro registrare vincitori, statistiche o log di fine partita.
    def termina_partita(self):
        """
        Termina la partita, portandola nello stato "terminata".

        Questo metodo serve a marcare la fine della partita (ad esempio dopo
        una tombola, oppure per una terminazione forzata decisa dal controller).

        Regole:
        - Può essere chiamato quando la partita è "non_iniziata" oppure "in_corso".
        - Se la partita è già "terminata", l'operazione non è consentita.

        Effetti:
        - Imposta l'attributo interno self.stato_partita a "terminata".

        Ritorna:
        - str: lo stato attuale della partita dopo la modifica (cioè "terminata").

        Eccezioni:
        - PartitaGiaTerminataException: se la partita risulta già terminata.
        """
        # Se è già terminata, evitare una seconda terminazione (stato incoerente).
        if self.stato_partita == "terminata":
            raise PartitaGiaTerminataException("Impossibile terminare la partita: la partita è già terminata.")

        # Termina la partita.
        self.stato_partita = "terminata"
        return self.stato_partita



    """sezione 4: Gestione delle estrazioni"""

    #chiede al tabellone il prossimo numero da estrarre, aggiorna lo stato interno (es. ultimo numero estratto) e coordina l'aggiornamento dei giocatori.
    def estrai_prossimo_numero(self) -> int:
        """
        Estrae il prossimo numero dal tabellone e aggiorna lo stato interno della partita.

        Questo è il metodo centrale dell'estrazione durante una partita in corso:
        - valida che la partita sia nello stato corretto per estrarre ("in_corso");
        - delega l'estrazione al tabellone tramite Tabellone.estrai_numero();
        - memorizza il numero estratto nello stato interno della partita (ultimo estratto);
        - aggiorna tutti i giocatori applicando il numero alle loro cartelle
          tramite GiocatoreBase.aggiorna_con_numero(numero).

        Vincoli:
        - È possibile estrarre solo quando la partita è già stata avviata
          (stato == "in_corso").

        Effetti collaterali:
        - Imposta l'attributo self.ultimo_numero_estratto con il numero estratto.
          (Se l'attributo non esiste ancora, viene creato alla prima estrazione.)

        Ritorna:
        - int: il numero estratto dal tabellone.

        Eccezioni:
        - PartitaNonInCorsoException: se la partita non è nello stato "in_corso".
        - PartitaNumeriEsauritiException: se il tabellone non può estrarre altri numeri (numeri terminati).
        """
        # L'estrazione è consentita solo durante una partita avviata.
        if self.stato_partita != "in_corso":
            raise PartitaNonInCorsoException(
                f"Impossibile estrarre un numero: lo stato della partita è '{self.stato_partita}'. "
                "È possibile estrarre solo quando la partita è in_corso."
            )

        # Estrae dal tabellone (può sollevare ValueError se i numeri sono terminati).
        try:
            numero_estratto = self.tabellone.estrai_numero()
        except ValueError as exc:
            # Cattura l'errore del tabellone e lancia l'eccezione specifica di fine gioco
            raise PartitaNumeriEsauritiException(
                "Impossibile estrarre un altro numero: il tabellone non ha più numeri disponibili."
            ) from exc

        # Aggiorna lo stato interno della partita.
        self.ultimo_numero_estratto = numero_estratto

        # Aggiorna tutti i giocatori con il numero estratto.
        self.aggiorna_giocatori_con_numero(numero_estratto)

        return numero_estratto


    #notifica a tutti i giocatori il numero estratto, delegando a ciascun giocatore l'aggiornamento delle proprie cartelle (ad esempio tramite aggiorna_con_numero()).
    def aggiorna_giocatori_con_numero(self, numero: int) -> None:
        """
        Aggiorna tutti i giocatori della partita applicando un numero estratto.

        Questo metodo riceve un numero (tipicamente estratto dal tabellone) e lo
        propaga a tutti i giocatori registrati nella partita.

        La logica concreta di aggiornamento è delegata ai giocatori stessi:
        per ogni giocatore viene chiamato GiocatoreBase.aggiorna_con_numero(numero),
        che si occupa di validare il parametro e di segnare il numero su tutte le
        cartelle possedute dal giocatore.

        Vincoli:
        - In una partita ben strutturata questo metodo viene usato durante lo stato
          "in_corso". Se chiamato quando la partita non è in corso, l'operazione
          non è consentita.

        Parametri:
        - numero: int
          Numero estratto dal tabellone da applicare ai giocatori.

        Ritorna:
        - None. L'aggiornamento modifica lo stato interno delle cartelle dei giocatori.

        Eccezioni:
                - PartitaNonInCorsoException: se la partita non è nello stato "in_corso".
        - Le eccezioni di validazione del giocatore (es. tipo/range del numero)
          possono propagarsi da GiocatoreBase.aggiorna_con_numero(numero).
        """
        # Consentire l'aggiornamento dei giocatori solo durante una partita in corso.
        if self.stato_partita != "in_corso":
            raise PartitaNonInCorsoException(
                f"Impossibile aggiornare i giocatori: lo stato della partita è '{self.stato_partita}'. "
                "È possibile aggiornare i giocatori solo quando la partita è in_corso."
            )

        # Propaga il numero a tutti i giocatori registrati.
        for giocatore in self.giocatori:
            giocatore.aggiorna_con_numero(numero)



    #metodo che ritorna l'ultimo numero estratto dal tabellone, oppure None se   non è ancora stato estratto alcun numero.
    def get_ultimo_numero_estratto(self) -> Optional[int]:
        """
        Ritorna l'ultimo numero estratto durante la partita.

        Questo metodo è un semplice getter che permette all'interfaccia (o ad altri
        metodi della classe Partita) di conoscere l'ultimo numero uscito, senza
        modificare lo stato della partita.

        Valori possibili:
        - None: se non è ancora stata effettuata alcuna estrazione.
        - int: l'ultimo numero estratto dal tabellone (tipicamente tra 1 e 90).

        Ritorna:
        - Optional[int]: l'ultimo numero estratto, oppure None se non disponibile.
        """
        return self.ultimo_numero_estratto


    """sezione 5: Verifica dei premi"""

    #calcola i premi presenti su una singola cartella (ambo, terno, quaterna, cinquina, tombola), utilizzando i metodi di stato già definiti nella classe Cartella.
    def verifica_premi_per_cartella(self, cartella: 'Cartella') -> Dict[str, Any]:
        """
        Analizza una cartella per identificare tutti i premi attualmente conseguiti.
        
        Questo metodo effettua una scansione completa della cartella passata come argomento,
        verificando riga per riga la presenza di ambo, terno, quaterna e cinquina,
        e controllando globalmente se è stata raggiunta la tombola.
        
        La struttura dati restituita è un dizionario dettagliato che mappa ogni riga
        ai premi specifici che ha ottenuto, permettendo al chiamante di avere
        una visione granulare dello stato della cartella senza ambiguità.
        
        Parametri:
        - cartella (Cartella): L'istanza della cartella da verificare.
        
        Ritorna:
        - Dict[str, Any]: Un dizionario strutturato con due chiavi principali:
            - "tombola" (bool): True se l'intera cartella è completa.
            - "righe" (dict): Un dizionario dove le chiavi sono gli indici delle righe (0, 1, 2)
                              e i valori sono dizionari annidati con i boolean dei premi:
                              {
                                0: {'ambo': bool, 'terno': bool, 'quaterna': bool, 'cinquina': bool},
                                ...
                              }
        """
        
        # Inizializzo la struttura del risultato
        risultato = {
            "tombola": False,
            "righe": {}
        }
        
        # 1. Verifica globale della TOMBOLA
        # Chiamo il metodo specifico della cartella che controlla se tutti i 15 numeri sono segnati.
        if cartella.verifica_cartella_completa():
            risultato["tombola"] = True
            
        # 2. Verifica puntuale dei premi per ciascuna riga
        # Itero sulle 3 righe standard della cartella (indici 0, 1, 2)
        for i in range(3):
            # Per ogni riga, costruisco un dizionario con l'esito di ogni singolo premio.
            # Nota: una riga che ha fatto 'cinquina' avrà True anche su 'quaterna', 'terno' e 'ambo'.
            # Questo è voluto: riportiamo lo stato reale e completo.
            dettaglio_riga = {
                "ambo": cartella.verifica_ambo_riga(i),
                "terno": cartella.verifica_terno_riga(i),
                "quaterna": cartella.verifica_quaterna_riga(i),
                "cinquina": cartella.verifica_cinquina_riga(i)
            }
            
            # Salvo il dettaglio della riga corrente nel risultato principale
            risultato["righe"][i] = dettaglio_riga
            
        return risultato


    #metodo che scorre tutte le cartelle di tutti i giocatori e individua i premi ottenuti, aggiornando lo stato interno dei premi già assegnati e restituendo le informazioni utili per l'interfaccia (quale giocatore, quale cartella, quale premio).
    def verifica_premi(self) -> List[Dict[str, Any]]:
        """
        Scansiona tutti i giocatori e le loro cartelle per trovare NUOVI premi.
        
        Questo metodo è il 'regista' delle vittorie:
        1. Chiama 'verifica_premi_per_cartella' per sapere cosa c'è su ogni cartella.
        2. Confronta i risultati con 'self.premi_gia_assegnati' per capire se sono novità.
        3. Se un premio è nuovo, lo registra e lo aggiunge alla lista degli eventi da ritornare.
        
        Ritorna:
        - List[Dict]: Una lista di eventi (dizionari). Ogni evento contiene:
          {
            "giocatore": str (nome del giocatore),
            "cartella": int (indice della cartella),
            "premio": str ("ambo", "terno", "tombola", etc.),
            "riga": int (0, 1, 2, oppure None per la tombola)
          }
        """
        
        # Lista vuota che riempiremo con i nuovi premi trovati in questo turno
        nuovi_eventi = []

        # Ciclo su tutti i giocatori partecipanti (umani e bot)
        for giocatore in self.giocatori:
            
            # Ciclo su tutte le cartelle possedute dal giocatore corrente
            for cartella in giocatore.get_cartelle():
                
                # 1. Scatto la "fotografia" dello stato attuale della cartella
                #    (Uso il metodo che abbiamo creato prima)
                stato_cartella = self.verifica_premi_per_cartella(cartella)
                
                # Recupero l'ID univoco della cartella per creare le chiavi di memoria
                id_cartella = cartella.indice

                # A. CONTROLLO TOMBOLA (Vittoria globale sulla cartella)
                if stato_cartella["tombola"]:
                    # Creo una chiave univoca per questo evento: es. "cartella_5_tombola"
                    chiave_tombola = f"cartella_{id_cartella}_tombola"
                    
                    # Se questa chiave NON è nella memoria, è una novità!
                    if chiave_tombola not in self.premi_gia_assegnati:
                        # 1. Aggiungo alla memoria per non ripeterlo in futuro
                        self.premi_gia_assegnati.add(chiave_tombola)
                        
                        # 2. Creo l'evento dettagliato
                        evento = {
                            "giocatore": giocatore.get_nome(),
                            "cartella": id_cartella,
                            "premio": "tombola",
                            "riga": None  # La tombola non ha riga specifica
                        }
                        
                        # 3. Aggiungo alla lista da ritornare
                        nuovi_eventi.append(evento)

                # B. CONTROLLO PREMI INTERMEDI (Per ogni riga)

                # Scorro il dizionario delle righe: indice_riga (0-2), premi_riga (dict boolean)
                for indice_riga, premi_riga in stato_cartella["righe"].items():
                    
                    # Definisco l'ordine di controllo per importanza (dal basso all'alto)
                    # Anche se li controlliamo tutti, l'ordine qui è solo per pulizia.
                    tipi_premio = ["ambo", "terno", "quaterna", "cinquina"]
                    
                    for tipo in tipi_premio:
                        # Se il premio è True (è presente sulla riga)
                        if premi_riga[tipo]:
                            
                            # Creo la chiave univoca: es. "cartella_5_riga_0_ambo"
                            chiave_premio = f"cartella_{id_cartella}_riga_{indice_riga}_{tipo}"
                            
                            # Verifico se è una novità
                            if chiave_premio not in self.premi_gia_assegnati:
                                # È nuovo! Lo registro e creo l'evento
                                self.premi_gia_assegnati.add(chiave_premio)
                                
                                evento = {
                                    "giocatore": giocatore.get_nome(),
                                    "cartella": id_cartella,
                                    "premio": tipo,
                                    "riga": indice_riga
                                }
                                nuovi_eventi.append(evento)

        # Alla fine dei giri, ritorno la lista con tutte le novità trovate
        return nuovi_eventi


    #metodo che ritorna True se almeno una cartella di qualsiasi giocatore ha completato la tombola.
    def has_tombola(self) -> bool:
        """
        Verifica se è presente almeno una tombola a livello di partita.

        Questo metodo controlla tutti i giocatori registrati e ritorna True se
        almeno uno di essi ha almeno una cartella completa (tombola).

        La verifica concreta è delegata ai giocatori tramite GiocatoreBase.has_tombola(),
        che a sua volta controlla lo stato delle proprie cartelle.

        Ritorna:
        - bool: True se almeno un giocatore ha tombola, False altrimenti.

        Note:
        - Se la partita è "non_iniziata", tipicamente il risultato sarà False,
          perché non sono ancora state fatte estrazioni.
        - Il metodo non modifica lo stato della partita.
        """
        # Scorre i giocatori: basta che uno abbia tombola per terminare il controllo.
        for giocatore in self.giocatori:
            if giocatore.has_tombola():
                return True

        return False


    """Sezione 6: Ciclo di gioco ad alto livello"""

    #esegue un "passo" della partita: estrae un numero dal tabellone, aggiorna i giocatori e verifica se sono stati assegnati nuovi premi. Se viene rilevata una tombola, termina la partita.
    #esegue un "passo" della partita: estrae un numero dal tabellone, aggiorna i giocatori e verifica se sono stati assegnati nuovi premi. Se viene rilevata una tombola, termina la partita.
    def esegui_turno(self) -> dict[str, Any]: 
        """
        Esegue un singolo turno della partita.

        Un "turno" rappresenta un passo del ciclo di gioco e include:
        - estrazione del prossimo numero dal tabellone;
        - aggiornamento dei giocatori (e quindi delle loro cartelle);
        - verifica e raccolta dei nuovi premi conseguiti (ambo, terno, ecc.);
        - verifica di condizioni di fine partita (tombola).

        Ritorna:
        - dict: un dizionario con informazioni utili per l'interfaccia o per il controller.
          Chiavi previste:
          - "numero_estratto": int, il numero estratto dal tabellone.
          - "stato_partita_prima": str, stato della partita prima del turno.
          - "stato_partita_dopo": str, stato della partita dopo il turno.
          - "tombola_rilevata": bool, True se dopo l'estrazione risulta almeno una tombola.
          - "partita_terminata": bool, True se la partita risulta terminata dopo il turno.
          - "premi_nuovi": List[Dict], lista degli eventi di vincita rilevati in questo turno.
          - "reclami_bot": List[Dict], lista degli esiti dei reclami bot (v0.6.0+).
            Ogni elemento contiene:
            - "nome_giocatore": str, nome del bot
            - "id_giocatore": int, id del bot
            - "reclamo": ReclamoVittoria, oggetto reclamo costruito dal bot
            - "successo": bool, True se il reclamo coincide con un premio reale

        Eccezioni:
        - PartitaNonInCorsoException: se si tenta di eseguire un turno quando la partita non è "in_corso".
        - PartitaNumeriEsauritiException: (propagato da estrai_prossimo_numero) se i numeri finiscono.
        """
        # Salva lo stato prima del turno (utile per log e interfaccia).
        stato_prima = self.stato_partita

        # Un turno ha senso solo quando la partita è stata avviata.
        if self.stato_partita != "in_corso":
            raise PartitaNonInCorsoException(
                f"Impossibile eseguire un turno: lo stato della partita è '{self.stato_partita}'. "
                "È possibile eseguire un turno solo quando la partita è in_corso."
            )

        # 1. Estrae il prossimo numero.
        # Questo metodo aggiorna anche self.ultimo_numero_estratto e notifica tutti i giocatori.
        numero_estratto = self.estrai_prossimo_numero()

        # 2. [NUOVO] Fase reclami bot: i bot valutano se hanno premi reclamabili
        # Questa fase avviene DOPO l'estrazione e PRIMA della verifica ufficiale dei premi.
        # I bot analizzano lo stato delle proprie cartelle e costruiscono un reclamo se appropriato.
        #
        # Nota architetturale: Chiamiamo _valuta_potenziale_reclamo() anche se è un metodo
        # interno (prefisso _) perché Partita è il coordinatore naturale del ciclo di gioco
        # e ha la responsabilità di orchestrare le azioni dei giocatori. Questo pattern
        # mantiene l'incapsulamento (il bot decide autonomamente cosa reclamare) pur
        # permettendo a Partita di coordinarle il timing della valutazione.
        for giocatore in self.giocatori:
            # Filtra solo i bot automatici usando il metodo is_automatico()
            if giocatore.is_automatico():
                # Passa lo snapshot dei premi già assegnati (prima di questo turno)
                # Il bot valuterà se ha un premio reclamabile che non è già stato assegnato
                reclamo = giocatore._valuta_potenziale_reclamo(self.premi_gia_assegnati)
                
                # Se il bot ha trovato un reclamo valido, lo memorizza
                if reclamo is not None:
                    giocatore.reclamo_turno = reclamo

        # 3. Verifica i premi (Ambo, Terno, Quaterna, Cinquina, Tombola)
        # Chiama il metodo che scansiona tutti i giocatori e ritorna solo le NOVITÀ rispetto al passato.
        # Questo metodo rimane l'UNICO ARBITRO dei premi reali.
        premi_nuovi = self.verifica_premi()

        # 4. [NUOVO] Confronto reclami bot vs premi reali
        # Per ogni bot che ha fatto un reclamo, verifica se il reclamo corrisponde a un premio reale.
        # Costruisce una lista di esiti per il logging e l'interfaccia.
        reclami_bot = []
        for giocatore in self.giocatori:
            if giocatore.is_automatico() and giocatore.reclamo_turno is not None:
                reclamo = giocatore.reclamo_turno
                
                # Determina se il reclamo è corretto confrontandolo con i premi reali
                successo = False
                for evento in premi_nuovi:
                    # Matching per (nome giocatore, cartella, tipo premio, riga)
                    if (evento["giocatore"] == giocatore.get_nome() and
                        evento["cartella"] == reclamo.indice_cartella and
                        evento["premio"] == reclamo.tipo and
                        evento["riga"] == reclamo.indice_riga):
                        successo = True
                        break
                
                # Aggiungi l'esito del reclamo alla lista
                reclami_bot.append({
                    "nome_giocatore": giocatore.get_nome(),
                    "id_giocatore": giocatore.get_id_giocatore(),
                    "reclamo": reclamo,
                    "successo": successo
                })

        # 5. [NUOVO] Reset reclami bot
        # Dopo aver processato i reclami, resettiamo lo stato per il turno successivo
        for giocatore in self.giocatori:
            if giocatore.is_automatico():
                giocatore.reset_reclamo_turno()

        # 6. Verifica se è stata fatta tombola (condizione di fine partita)
        # Nota: La tombola sarà già presente anche dentro "premi_nuovi", ma qui serve per
        # decidere se chiudere la partita.
        tombola_rilevata = self.has_tombola()

        # Se c'è tombola, termina la partita.
        if tombola_rilevata:
            self.termina_partita()

        # Stato dopo il turno (potrebbe essere rimasto "in_corso" oppure diventare "terminata").
        stato_dopo = self.stato_partita

        # Costruisce l'evento/risultato del turno in un dizionario pronto per il controller.
        risultato_turno = {
            "numero_estratto": numero_estratto,
            "stato_partita_prima": stato_prima,
            "stato_partita_dopo": stato_dopo,
            "tombola_rilevata": tombola_rilevata,
            "partita_terminata": self.is_terminata(),
            "premi_nuovi": premi_nuovi,  # Qui ora passiamo i premi reali!
            "reclami_bot": reclami_bot,  # [NUOVO] Lista degli esiti dei reclami bot (backward-compatible: lista vuota se nessun bot)
        }

        return risultato_turno


    #helper che ritorna True se la partita è nello stato "terminata".
    def is_terminata(self) -> bool:
        """
        Indica se la partita è terminata.

        Questo metodo è un helper di stato: permette di capire rapidamente se la
        partita è arrivata alla fine, senza dover confrontare manualmente
        self.stato_partita in altri punti del codice.

        La partita è considerata terminata quando:
        - self.stato_partita == "terminata"

        Ritorna:
        - bool: True se la partita è nello stato "terminata", False altrimenti.

        Note:
        - Il metodo non modifica lo stato della partita.
        - È pensato per essere usato in metodi di alto livello (esegui_turno,
          loop di gioco, interfaccia) per decidere se continuare o fermarsi.
        """
        # Controlla lo stato corrente senza modificarlo.
        return self.stato_partita == "terminata"



    """Sezione 7: Metodi di stato per l'interfaccia"""

    #ritorna una rappresentazione sintetica dello stato dei giocatori (es. nome, id, numero di cartelle, presenza di tombola).
    #ritorna una rappresentazione sintetica dello stato dei giocatori (es. nome, id, numero di cartelle, presenza di tombola).
    def get_stato_giocatori(self) -> List[Dict[str, Any]]:
        """
        Ritorna una rappresentazione sintetica dello stato di tutti i giocatori.

        Questo metodo è pensato per fornire all'interfaccia utente (o allo screen reader)
        una "radiografia" veloce della situazione, senza dover interrogare ogni singolo
        oggetto giocatore.

        Per ogni giocatore registrato, viene creato un dizionario con i dati essenziali:
        - Chi è (nome, id).
        - Quanto possiede (numero di cartelle).
        - Se ha vinto (presenza di tombola).

        Ritorna:
        - List[Dict]: Una lista di dizionari, dove ogni dizionario ha la forma:
          {
            "nome": str,
            "id": int o None,
            "num_cartelle": int,
            "ha_tombola": bool
          }
        """
        stato_complessivo = []

        for giocatore in self.giocatori:
            # Estrae i dati essenziali usando i metodi pubblici di GiocatoreBase
            info_giocatore = {
                "nome": giocatore.get_nome(),
                "id": giocatore.get_id_giocatore(),
                "num_cartelle": giocatore.get_numero_cartelle(),
                "ha_tombola": giocatore.has_tombola()
            }
            stato_complessivo.append(info_giocatore)

        return stato_complessivo



    #metodo che ritorna un riepilogo complessivo della partita (stato, ultimo numero estratto, premi assegnati, elenco sintetico dei giocatori).
    #metodo che ritorna un riepilogo complessivo della partita (stato, ultimo numero estratto, premi assegnati, elenco sintetico dei giocatori).
    def get_stato_completo(self) -> Dict[str, Any]:
        """
        Ritorna una fotografia completa e dettagliata dello stato attuale della partita.

        Questo metodo è fondamentale per l'interfaccia utente (o per il salvataggio partita),
        perché in una sola chiamata fornisce TUTTE le informazioni necessarie a ricostruire
        la scena di gioco:
        - A che punto siamo (stato partita, ultimo numero).
        - Cosa è successo sul tabellone (numeri estratti, numeri mancanti).
        - Come stanno i giocatori (chi sono, quante cartelle hanno, se hanno vinto).
        - Quali premi sono già stati assegnati (lo storico delle vittorie).

        Ritorna:
        - Dict[str, Any]: Un dizionario contenitore con le seguenti chiavi:
            - "stato_partita": str ("non_iniziata", "in_corso", "terminata")
            - "ultimo_numero_estratto": int o None
            - "numeri_estratti": List[int] (tutti i numeri usciti sul tabellone finora)
            - "giocatori": List[Dict] (la lista sintetica generata da get_stato_giocatori)
            - "premi_gia_assegnati": List[str] (elenco delle chiavi dei premi già vinti, es. "cartella_1_riga_0_ambo")
        """
        
        # 1. Recupero informazioni dal Tabellone
        # Uso i metodi pubblici del tabellone per avere i dati puliti
        numeri_estratti = self.tabellone.get_numeri_estratti()
        
        # 2. Recupero informazioni sui Giocatori
        # Riuso il metodo che abbiamo appena scritto per non duplicare la logica
        stato_giocatori = self.get_stato_giocatori()
        
        # 3. Preparo la lista dei premi
        # Converto il set in lista per renderlo serializzabile (es. in JSON) e leggibile
        lista_premi = list(self.premi_gia_assegnati)
        lista_premi.sort()  # Li ordino per avere un output stabile e prevedibile
        
        # 4. Assemblo il pacchetto finale
        stato_completo = {
            "stato_partita": self.stato_partita,
            "ultimo_numero_estratto": self.ultimo_numero_estratto,
            "numeri_estratti": numeri_estratti,
            "giocatori": stato_giocatori,
            "premi_gia_assegnati": lista_premi
        }
        
        return stato_completo


