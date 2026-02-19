"""
Modulo: bingo_game.players.giocatore_automatico

Definisce la classe GiocatoreAutomatico, che rappresenta un giocatore
controllato dal programma (bot) nel gioco della tombola/bingo.

Al momento questa classe si appoggia completamente alla logica di
GiocatoreBase per la gestione di nome, id, cartelle e aggiornamento
rispetto ai numeri estratti, ma espone un punto di ingresso comodo
per la futura integrazione con la logica della Partita.
"""

from __future__ import annotations

from typing import Optional

from bingo_game.players.giocatore_base import GiocatoreBase


class GiocatoreAutomatico(GiocatoreBase):
    """
    Classe concreta che rappresenta un giocatore automatico (bot).

    Eredita tutta la logica di base da GiocatoreBase:
    - identità del giocatore (nome, id_giocatore);
    - gestione delle cartelle (aggiunta, conteggio, stato);
    - aggiornamento delle cartelle rispetto ai numeri estratti;
    - interrogazioni sullo stato complessivo (es. has_tombola()).

    In futuro potrà essere estesa con logiche specifiche per il bot,
    ad esempio gestione di eventi di partita o strategie particolari.
    """

    def __init__(self, nome: str = "Giocatore automatico", id_giocatore: Optional[int] = None) -> None:
        """
        Inizializza un giocatore automatico.

        Parametri:
        - nome: str
          Nome descrittivo del giocatore automatico. Ha un valore di
          default per creare rapidamente bot senza specificare ogni
          volta il nome.
        - id_giocatore: Optional[int]
          Identificativo numerico opzionale del giocatore (es. indice
          interno alla partita).

        La validazione di nome e id_giocatore è delegata a GiocatoreBase.
        """
        super().__init__(nome=nome, id_giocatore=id_giocatore)


    """metodi relativi alla classe giocatoreAutomatico"""

    def is_automatico(self) -> bool:
        """
        Override di GiocatoreBase: indica che questo giocatore è un bot.

        Ritorna:
        - bool: sempre True per GiocatoreAutomatico.
        """
        return True

    #metodo per aggiornare il giocatore automatico in seguito all'estrazione di un numero
    def aggiorna_da_tabellone(self, numero: int) -> None:
        """
        Punto di ingresso per aggiornare il giocatore automatico
        in seguito all'estrazione di un numero dal tabellone.

        Questo metodo è pensato per essere chiamato dalla logica
        di Partita: internamente delega ad aggiorna_con_numero()
        di GiocatoreBase, che valida il numero e lo applica a tutte
        le cartelle del giocatore.

        Parametri:
        - numero: int
          Numero estratto dal tabellone da applicare alle cartelle
          del giocatore automatico.
        """
        # Delegazione alla logica già presente in GiocatoreBase:
        # verifica tipo e range del numero, poi chiama segna_numero()
        # su tutte le cartelle assegnate al giocatore.
        self.aggiorna_con_numero(numero)
