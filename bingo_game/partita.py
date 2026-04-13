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
from typing import Dict, Any, List, Literal, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from bingo_game.cartella import Cartella

#import dei file di gioco
from bingo_game.tabellone import Tabellone
from bingo_game.exceptions.tabellone_exceptions import TabelloneNumeriEsauritiException
from bingo_game.players.giocatore_base import GiocatoreBase
from bingo_game.players.giocatore_umano import GiocatoreUmano
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
        self.premi_tipo_chiusi: set = set()
        self.ultimo_premio_evento: Optional[Dict[str, Any]] = None
        self.storico_premi: List[Dict[str, Any]] = []
        self.fase_turno_corrente: str = "attesa_estrazione"



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

        # Estrae dal tabellone (può sollevare TabelloneNumeriEsauritiException se i numeri sono terminati).
        try:
            numero_estratto = self.tabellone.estrai_numero()
        except TabelloneNumeriEsauritiException as exc:
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
        per ogni giocatore automatico o base viene chiamato
        GiocatoreBase.aggiorna_con_numero(numero), che si occupa di validare il
        parametro e di segnare il numero su tutte le cartelle possedute dal
        giocatore. Il giocatore umano viene escluso da questo aggiornamento
        automatico: la segnazione resta manuale tramite i comandi UI.

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

        # Propaga il numero a tutti i giocatori registrati, ma lascia al
        # giocatore umano la segnazione manuale tramite Space.
        for giocatore in self.giocatori:
            if isinstance(giocatore, GiocatoreUmano):
                continue
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
        
        # Raccoglie tutti i candidati validi per tipo senza assegnare (prima passata).
        # Struttura: tipo_premio -> lista di candidati {giocatore, cartella, indice_riga, chiave}
        candidati_per_tipo: Dict[str, List[Dict]] = {}

        for giocatore in self.giocatori:
            if giocatore.reclamo_turno is None:
                continue

            reclamo = giocatore.reclamo_turno

            # Trova la cartella indicata nel reclamo.
            cartella = next(
                (c for c in giocatore.get_cartelle() if c.indice == reclamo.indice_cartella),
                None
            )
            if cartella is None:
                continue

            stato_cartella = self.verifica_premi_per_cartella(cartella)
            id_cartella = cartella.indice

            if reclamo.tipo == "tombola":
                chiave = f"cartella_{id_cartella}_tombola"
                if (stato_cartella["tombola"]
                        and "tombola" not in self.premi_tipo_chiusi
                        and chiave not in self.premi_gia_assegnati):
                    tipo = "tombola"
                    if tipo not in candidati_per_tipo:
                        candidati_per_tipo[tipo] = []
                    candidati_per_tipo[tipo].append({
                        "giocatore": giocatore,
                        "cartella": id_cartella,
                        "indice_riga": None,
                        "chiave": chiave,
                    })
            else:
                # Premio di riga: trova il premio più alto realmente presente sulla riga.
                indice_riga = reclamo.indice_riga
                if indice_riga is None:
                    continue
                premi_riga = stato_cartella["righe"].get(indice_riga, {})
                for tipo in ["cinquina", "quaterna", "terno", "ambo"]:
                    if premi_riga.get(tipo, False):
                        chiave = f"cartella_{id_cartella}_riga_{indice_riga}_{tipo}"
                        if tipo not in self.premi_tipo_chiusi and chiave not in self.premi_gia_assegnati:
                            if tipo not in candidati_per_tipo:
                                candidati_per_tipo[tipo] = []
                            candidati_per_tipo[tipo].append({
                                "giocatore": giocatore,
                                "cartella": id_cartella,
                                "indice_riga": indice_riga,
                                "chiave": chiave,
                            })
                        break  # Solo il premio più alto presente sulla riga

        # Seconda passata: assegna il premio a TUTTI i candidati validi per tipo (co-vincita).
        nuovi_eventi = []
        for tipo, candidati in candidati_per_tipo.items():
            for candidato in candidati:
                self.premi_gia_assegnati.add(candidato["chiave"])
                evento: Dict[str, Any] = {
                    "giocatore": candidato["giocatore"].get_nome(),
                    "id_giocatore": candidato["giocatore"].get_id_giocatore(),
                    "cartella": candidato["cartella"],
                    "premio": tipo,
                    "riga": candidato["indice_riga"],
                    "turno": len(self.tabellone.get_numeri_estratti()),
                }
                nuovi_eventi.append(evento)
                self.storico_premi.append(evento)
            self.premi_tipo_chiusi.add(tipo)

        if nuovi_eventi:
            self.ultimo_premio_evento = nuovi_eventi[-1]

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

    #esegue la prima fase del turno: estrazione e reclami bot.
    def esegui_fase_estrazione(self) -> Dict[str, Any]:
        """
        Esegue la prima fase del turno (V2): estrae il numero e porta il dominio
        nello stato "attesa_reclami".

        I bot aggiornano internamente le proprie cartelle tramite
        aggiorna_giocatori_con_numero() (già chiamato da estrai_prossimo_numero()),
        ma NON registrano ancora nessun reclamo. I reclami bot vengono registrati
        esplicitamente durante la fase 2 tramite dichiara_fine_fase_azione().

        La fase è consentita solo quando fase_turno_corrente == "attesa_estrazione".
        Al termine imposta fase_turno_corrente = "attesa_reclami".

        Ritorna:
        - dict: {"numero_estratto": int, "fase": str}

        Eccezioni:
        - PartitaNonInCorsoException: partita non in_corso.
        - PartitaGiocoException: fase_turno_corrente != "attesa_estrazione".
        - PartitaNumeriEsauritiException: propagata dal tabellone.
        """
        if self.stato_partita != "in_corso":
            raise PartitaNonInCorsoException(
                f"Impossibile eseguire fase estrazione: stato '{self.stato_partita}'."
            )
        if self.fase_turno_corrente != "attesa_estrazione":
            raise PartitaGiocoException(
                f"Impossibile eseguire fase estrazione: fase corrente '{self.fase_turno_corrente}', "
                "attesa 'attesa_estrazione'."
            )

        numero_estratto = self.estrai_prossimo_numero()

        self.fase_turno_corrente = "attesa_reclami"

        return {
            "numero_estratto": numero_estratto,
            "fase": self.fase_turno_corrente,
        }


    #esegue la seconda fase del turno: verifica premi, confronto bot, reset, tombola.
    def esegui_fase_verifica(self) -> Dict[str, Any]:
        """
        Esegue la seconda fase del turno: verifica premi, confronto reclami bot,
        reset stati di turno e controllo tombola.

        La fase è consentita solo quando fase_turno_corrente == "attesa_reclami".
        Al termine imposta fase_turno_corrente = "attesa_estrazione".

        Ritorna:
        - dict: {"premi_nuovi": list, "reclami_bot": list,
                 "tombola_rilevata": bool, "partita_terminata": bool}

        Eccezioni:
        - PartitaNonInCorsoException: partita non in_corso.
        - PartitaGiocoException: fase_turno_corrente != "attesa_reclami".
        """
        if self.stato_partita != "in_corso":
            raise PartitaNonInCorsoException(
                f"Impossibile eseguire fase verifica: stato '{self.stato_partita}'."
            )
        if self.fase_turno_corrente != "attesa_reclami":
            raise PartitaGiocoException(
                f"Impossibile eseguire fase verifica: fase corrente '{self.fase_turno_corrente}', "
                "attesa 'attesa_reclami'."
            )

        premi_nuovi = self.verifica_premi()

        # Confronto reclami bot vs premi reali.
        reclami_bot = []
        for giocatore in self.giocatori:
            if giocatore.is_automatico() and giocatore.reclamo_turno is not None:
                reclamo = giocatore.reclamo_turno
                successo = False
                id_bot = giocatore.get_id_giocatore()
                for evento in premi_nuovi:
                    giocatore_match = (
                        (id_bot is not None and evento.get("id_giocatore") == id_bot) or
                        (id_bot is None and evento["giocatore"] == giocatore.get_nome())
                    )
                    if (giocatore_match and
                            evento["cartella"] == reclamo.indice_cartella and
                            evento["premio"] == reclamo.tipo and
                            evento["riga"] == reclamo.indice_riga):
                        successo = True
                        break
                reclami_bot.append({
                    "nome_giocatore": giocatore.get_nome(),
                    "id_giocatore": giocatore.get_id_giocatore(),
                    "reclamo": reclamo,
                    "successo": successo,
                })

        # Reset: reclami e turno_dichiarato_concluso per tutti i giocatori.
        for giocatore in self.giocatori:
            giocatore.reset_reclamo_turno()
            giocatore.turno_dichiarato_concluso = False

        tombola_rilevata = self.has_tombola()
        if tombola_rilevata:
            self.termina_partita()

        self.fase_turno_corrente = "attesa_estrazione"

        return {
            "premi_nuovi": premi_nuovi,
            "reclami_bot": reclami_bot,
            "tombola_rilevata": tombola_rilevata,
            "partita_terminata": self.is_terminata(),
        }


    #verifica che tutti i giocatori (umani e bot) abbiano dichiarato fine turno.
    def tutti_hanno_dichiarato_fine(self) -> bool:
        """
        Verifica che tutti i giocatori (umani e automatici) abbiano dichiarato fine turno.

        Nel ciclo V2 sia i giocatori umani (tramite il pulsante "Ho finito"/Ctrl+Enter)
        che i bot (tramite dichiara_fine_fase_azione()) devono esplicitamente
        segnalare la fine della propria azione prima che la finestra possa chiudersi.

        Ritorna:
        - True: tutti i giocatori hanno turno_dichiarato_concluso == True.
        - False: almeno uno (umano o bot) non ha ancora dichiarato fine.
        """
        for giocatore in self.giocatori:
            if not giocatore.turno_dichiarato_concluso:
                return False
        return True


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
        if self.stato_partita != "in_corso":
            raise PartitaNonInCorsoException(
                f"Impossibile eseguire un turno: lo stato della partita è '{self.stato_partita}'. "
                "È possibile eseguire un turno solo quando la partita è in_corso."
            )

        stato_prima = self.stato_partita

        # Fase 1: estrazione numero e reclami bot.
        risultato_estrazione = self.esegui_fase_estrazione()
        numero_estratto = risultato_estrazione["numero_estratto"]

        # Fase 2: verifica premi, confronto bot, reset, tombola.
        risultato_verifica = self.esegui_fase_verifica()

        stato_dopo = self.stato_partita

        return {
            "numero_estratto": numero_estratto,
            "stato_partita_prima": stato_prima,
            "stato_partita_dopo": stato_dopo,
            "tombola_rilevata": risultato_verifica["tombola_rilevata"],
            "partita_terminata": risultato_verifica["partita_terminata"],
            "premi_nuovi": risultato_verifica["premi_nuovi"],
            "reclami_bot": risultato_verifica["reclami_bot"],
        }


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



    #metodo che ritorna un riepilogo sintetico e stabile dello stato di gioco.
    def get_stato_sintetico(self) -> Dict[str, Any]:
      """
      Ritorna la fotografia sintetica pubblica dello stato attuale della partita.

      È una vista ridotta di get_stato_completo(): include solo i campi minimi
      richiesti dal layer controller/UI secondo il contratto di bordo.

      Ritorna:
      - Dict[str, Any]: Dizionario con chiavi pubbliche e stabili per il bordo
        applicativo:
        - "stato_partita"
        - "ultimo_numero_estratto"
        - "numeri_estratti"
        - "giocatori"
        - "premi_gia_assegnati"
      """
      completo = self.get_stato_completo()

      # Copie difensive per evitare alias sullo stato interno.
      return {
        "stato_partita": completo["stato_partita"],
        "ultimo_numero_estratto": completo["ultimo_numero_estratto"],
        "numeri_estratti": list(completo["numeri_estratti"]),
        "giocatori": list(completo["giocatori"]),
        "premi_gia_assegnati": list(completo["premi_gia_assegnati"]),
      }



    #metodo che ritorna un riepilogo complessivo della partita (stato, ultimo numero estratto, premi assegnati, elenco sintetico dei giocatori).
    #metodo che ritorna un riepilogo complessivo della partita (stato, ultimo numero estratto, premi assegnati, elenco sintetico dei giocatori).
    def get_stato_completo(self) -> Dict[str, Any]:
        """
        Ritorna una fotografia completa e dettagliata dello stato attuale della partita.

        Questo metodo fornisce lo snapshot più esteso e autoritativo del dominio.
        Il controller e l'interfaccia possono usarlo direttamente oppure prendere una
        vista sintetica via get_stato_sintetico().

        Ritorna:
        - Dict[str, Any] con chiavi:
            - "stato_partita": str ("non_iniziata", "in_corso", "terminata" o altro)
            - "ultimo_numero_estratto": int | None
            - "numeri_estratti": List[int]
            - "numeri_mancanti": List[int]
            - "giocatori": List[Dict[str, Any]]
            - "premi_gia_assegnati": List[str]
            - "conteggio_giocatori": int
        """

        numeri_estratti_raw = self.tabellone.get_numeri_estratti()
        numeri_estratti = list(numeri_estratti_raw) if isinstance(numeri_estratti_raw, list) else list(numeri_estratti_raw)

        numeri_mancanti_raw = self.tabellone.get_numeri_disponibili()
        numeri_mancanti = list(numeri_mancanti_raw) if isinstance(numeri_mancanti_raw, list) else list(numeri_mancanti_raw)

        stato_giocatori_raw = self.get_stato_giocatori()
        stato_giocatori = list(stato_giocatori_raw) if isinstance(stato_giocatori_raw, list) else list(stato_giocatori_raw)

        premi_gia_assegnati = sorted(list(self.premi_gia_assegnati))

        stato_partita = self.stato_partita
        if not isinstance(stato_partita, str):
            stato_partita = str(stato_partita)

        return {
            "stato_partita": stato_partita,
            "ultimo_numero_estratto": self.ultimo_numero_estratto,
            "numeri_estratti": numeri_estratti,
            "numeri_mancanti": numeri_mancanti,
            "giocatori": stato_giocatori,
            "premi_gia_assegnati": premi_gia_assegnati,
            "conteggio_giocatori": len(stato_giocatori),
        }


