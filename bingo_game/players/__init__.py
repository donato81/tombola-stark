"""
Docstring per bingo_game.players.init

qui sono definiti gli import riguardanti la cartella players.
"""

from .giocatore_base import GiocatoreBase
from .giocatore_umano import GiocatoreUmano
from .giocatore_automatico import GiocatoreAutomatico

__all__ = [
    "GiocatoreBase",
    "GiocatoreUmano",
    "GiocatoreAutomatico",
]
