"""
CLASSE BASE PER I GIOCATORI
Modulo: bingo_game.players.giocatore_base

Tombola / Bingo – Gestione astratta del giocatore
=================================================

OVERVIEW DEL MODULO
-------------------
Questo modulo definisce la classe GiocatoreBase, che rappresenta la base
comune per tutti i tipi di giocatore (umano o automatico) nel gioco della
tombola/bingo.

La classe gestisce:
- l'identità del giocatore (nome, id opzionale);
- l'elenco delle cartelle assegnate al giocatore;
- le operazioni comuni per aggiornare le cartelle in base ai numeri estratti;
- alcune interrogazioni sullo stato complessivo del giocatore, derivate
  dalle cartelle (ad esempio presenza di una tombola).

Le classi specifiche (GiocatoreUmano, GiocatoreAutomatico) erediteranno
da GiocatoreBase ed eventualmente aggiungeranno comportamenti particolari.

STRUTTURA LOGICA DELLA CLASSE
-----------------------------
La classe è organizzata in quattro gruppi principali di metodi:

1) Identità del giocatore
   - __init__(nome, id_giocatore=None):
     inizializza il giocatore con un nome e un id opzionale.
   - get_nome():
     ritorna il nome del giocatore.
   - get_id_giocatore():
     ritorna l'id del giocatore (se presente).

2) Gestione delle cartelle
   - aggiungi_cartella(cartella):
     assegna una nuova cartella al giocatore.
   - get_cartelle():
     ritorna la lista delle cartelle del giocatore.
   - get_numero_cartelle():
     ritorna il conteggio delle cartelle possedute.

3) Aggiornamento rispetto ai numeri estratti
   - aggiorna_con_numero(numero):
     metodo comune che aggiorna tutte le cartelle del giocatore in base
     a un numero estratto dal tabellone (tipicamente segnando il numero
     su ciascuna cartella).

4) Stato complessivo del giocatore
   - get_stato_cartelle():
     ritorna una lista di dizionari, uno per cartella, contenente le
     informazioni globali di ciascuna cartella (utilizzando i metodi
     di stato della classe Cartella).
   - has_tombola():
     ritorna True se almeno una cartella del giocatore ha la tombola,
     cioè se verifica_cartella_completa() è True per quella cartella.

NOTE DI UTILIZZO
----------------
- GiocatoreBase non gestisce input/output né vocalizzazione: si limita
  a coordinare cartelle e stato di gioco del giocatore.
- Le classi derivate possono sovrascrivere o estendere alcuni metodi
  per aggiungere comportamenti specifici (ad esempio interazione con
  l'interfaccia utente o logiche automatiche).
"""

from __future__ import annotations

from typing import List, Optional
# Importa la classe Cartella per la gestione delle cartelle del giocatore
from bingo_game.cartella import Cartella
# Importa le eccezioni personalizzate per la validazione dei parametri
from bingo_game.exceptions import (
    GiocatoreNomeTypeException,
    GiocatoreNomeValueException,
    GiocatoreIdTypeException,
    GiocatoreCartellaTypeException,
    GiocatoreNumeroTypeException,
    GiocatoreNumeroValueException,
)
#import degli eventi necessari in questo file
from bingo_game.events.eventi_partita import ReclamoVittoria, EventoFineTurno



#classe per la gestione dei metodi comuni a tutti i giocatori della partita
class GiocatoreBase:
    """
    Classe base astratta per rappresentare un giocatore della tombola/bingo.

    Gestisce l'identità del giocatore (nome, id opzionale) e l'elenco delle
    cartelle assegnate. Fornisce metodi comuni per aggiornare le cartelle
    in base ai numeri estratti e per interrogare lo stato complessivo.
    """

    def __init__(self, nome: str, id_giocatore: Optional[int] = None):
        """
        Inizializza un nuovo giocatore base.
        Parametri:
        - nome: str
        Nome descrittivo del giocatore (es. "Mario", "Giocatore 1").
        - id_giocatore: Optional[int]
        Identificativo numerico opzionale del giocatore (es. indice
        interno alla partita).
        """
        # Verifica tipo del nome
        if not isinstance(nome, str):
            # nome deve essere una stringa
            raise GiocatoreNomeTypeException(nome)
        # Verifica valore del nome (non vuoto, non solo spazi)
        if nome.strip() == "":
            raise GiocatoreNomeValueException(nome)
        # Verifica tipo di id_giocatore (deve essere int o None)
        if id_giocatore is not None and not isinstance(id_giocatore, int):
            raise GiocatoreIdTypeException(id_giocatore)
        # Se tutti i controlli sono passati, assegna gli attributi
        self.nome = nome
        self.id_giocatore = id_giocatore
        self.cartelle: List[Cartella] = []
        self._prossimo_indice_cartella: int = 1
        # Reclamo del turno corrente (None = nessun reclamo inviato).
        # Il reclamo viene consumato e resettato dalla Partita quando processa il turno.
        self.reclamo_turno: Optional[ReclamoVittoria] = None

    """metodi di classe per la gestione del giocatore base"""

    """Sezione: Metodi di identità"""

    #metodo di identità che ritorna il nome del giocatore
    def get_nome(self) -> str:
        """Ritorna il nome del giocatore."""
        return self.nome

    #metodo di identità che ritorna l'id del giocatore
    def get_id_giocatore(self) -> Optional[int]:
        """Ritorna l'id del giocatore (può essere None se non impostato)."""
        return self.id_giocatore


    """Sezione: Gestione delle cartelle"""

    #metodo per aggiungere una cartella al giocatore
    def aggiungi_cartella(self, cartella: Cartella) -> None:
        """
        Aggiunge una cartella alla lista delle cartelle del giocatore.
        assegna un nome alla cartella ed un indice se non sono già presenti.
        incrementa l'indice per la prossima cartella.

        Parametri:
        - cartella: Cartella
          Istanza di Cartella da assegnare al giocatore.
        """
        # Verifica che l'oggetto passato sia effettivamente una Cartella
        # Se il tipo è errato, solleva un'eccezione specifica del giocatore
        if not isinstance(cartella, Cartella):
            raise GiocatoreCartellaTypeException(cartella)
        #verifica se la cartella ha un nome, altrimenti lo assegna
        if cartella.nome is None:
            #assegna un nome basato sull'indice della cartella
            cartella.nome = f"Cartella {self._prossimo_indice_cartella}"
        #verifica se la cartella ha un id, altrimenti lo assegna
        if cartella.indice is None:
            #assegna un id basato sull'indice della cartella
            cartella.indice = self._prossimo_indice_cartella
        #incrementa l'indice per la prossima cartella
        self._prossimo_indice_cartella += 1
        #aggiunge la cartella alla lista
        self.cartelle.append(cartella)


    #metodo per ottenere la lista delle cartelle del giocatore
    def get_cartelle(self) -> List[Cartella]:
        """
        Ritorna la lista delle cartelle assegnate al giocatore.

        Nota:
        - La lista ritornata è quella interna; si raccomanda di non
          modificarla direttamente dall'esterno.
        """
        return self.cartelle

    #metodo per ottenere il numero di cartelle del giocatore
    def get_numero_cartelle(self) -> int:
        """
        Ritorna il numero totale di cartelle possedute dal giocatore.
        """
        return len(self.cartelle)

    
    """Sezione: Aggiornamento rispetto ai numeri estratti"""

    #metodo per aggiornare le cartelle con un numero estratto
    def aggiorna_con_numero(self, numero: int) -> None:
        """
        Aggiorna tutte le cartelle del giocatore in base a un numero estratto.

        Per ogni cartella assegnata, prova a segnare il numero utilizzando
        il metodo segna_numero(). Il metodo non ritorna nulla: lo stato
        aggiornato è contenuto all'interno delle cartelle.

        Parametri:
        - numero: int
          Numero estratto dal tabellone da applicare alle cartelle.
        """
        # Verifica che il numero estratto sia di tipo intero
        # Se il tipo è errato, solleva un'eccezione specifica del giocatore
        if not isinstance(numero, int):
            raise GiocatoreNumeroTypeException(numero)
        # Verifica che il numero estratto sia nel range valido 1-90
        # Se il valore è fuori intervallo, solleva un'eccezione dedicata
        if numero < 1 or numero > 90:
            raise GiocatoreNumeroValueException(numero)
        # Per ogni cartella del giocatore, chiama segna_numero(numero)
        for cartella in self.cartelle:
            cartella.segna_numero(numero)


    """Sezione: Stato complessivo del giocatore"""

    #metodo per ottenere lo stato di tutte le cartelle del giocatore
    def get_stato_cartelle(self) -> List[dict]:
        """
        Ritorna una lista di dizionari con lo stato di ciascuna cartella.

        Per ogni cartella del giocatore, chiama get_stato_cartella() e
        raccoglie i risultati in una lista.

        Ritorna:
        - list[dict]: lista di dizionari, uno per cartella.
        """
        stati = []
        for cartella in self.cartelle:
            stato = cartella.get_stato_cartella()
            stati.append(stato)
        return stati


    #metodo per verificare se il giocatore ha fatto tombola
    def has_tombola(self) -> bool:
        """
        Verifica se almeno una cartella del giocatore ha fatto TOMBOLA.

        Ritorna:
        - True se almeno una cartella ha verifica_cartella_completa() == True.
        - False altrimenti.
        """
        for cartella in self.cartelle:
            if cartella.verifica_cartella_completa():
                return True
        return False


    def reset_reclamo_turno(self) -> None:
        """
        Resetta il reclamo del turno corrente.

        Quando chiamarlo:
        - Tipicamente alla fine del turno, dopo che la classe Partita
          ha processato/validato il reclamo.

        Effetti:
        - Imposta self.reclamo_turno a None.
        """
        self.reclamo_turno = None


    def is_automatico(self) -> bool:
        """
        Indica se il giocatore è un bot automatico.

        Ritorna:
        - bool: True se il giocatore è automatico, False altrimenti.

        Nota:
        - Il default è False (giocatore umano).
        - Questo metodo è pensato per essere sovrascritto nelle sottoclassi
          (es. GiocatoreAutomatico) che rappresentano bot.
        - Evita l'uso di isinstance() diretto in Partita, mantenendo il
          pattern "programma verso l'interfaccia".
        """
        return False



    #Sezione: eventi passa turno

    def _passa_turno_core(self, *, numero_turno: int) -> "EventoFineTurno":
        """
        Logica comune di fine turno (condivisa da umano e automatico).

        Responsabilità:
        - Impacchettare lo stato "di turno" del giocatore in un EventoFineTurno.
        - Allegare l'eventuale reclamo di vittoria (se presente).
        - Resettare lo stato di turno (reclamo_turno) dopo la creazione dell'evento,
          così il turno successivo parte pulito e non si rischiano reinvii/blocchi.

        Nota:
        - Non valida la correttezza del reclamo (ambo vero, tombola vera, ecc.):
          sarà la Partita a validarlo quando processa l'EventoFineTurno.
        """

        # 1) Costruzione evento usando il factory method (standardizzazione e stabilità futura).
        evento = EventoFineTurno.crea(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            numero_turno=numero_turno,
            reclamo_turno=self.reclamo_turno,
        )

        # 2) Reset stato turno: il reclamo (se c'era) è stato "consumato" e inviato alla Partita.
        self.reclamo_turno = None

        return evento
