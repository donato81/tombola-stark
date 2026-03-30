"""
Eccezioni di dominio per la classe Tabellone.
Modulo: bingo_game.exceptions.tabellone_exceptions
"""


class TabelloneNumeriEsauritiException(Exception):
    """
    Eccezione sollevata quando si tenta di estrarre un numero dal tabellone
    ma tutti i 90 numeri sono già stati estratti.

    Indica un tentativo di estrazione illegale in una partita dove il
    tabellone è completamente esaurito.
    """
