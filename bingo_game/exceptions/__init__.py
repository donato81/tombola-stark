"""
Docstring per bingo_game.exceptions.init
questo file contiene le eccezioni personalizzate per il gioco del bingo.

Raccoglie le eccezioni specifiche per:
- Cartella
- Giocatore
(altri moduli potranno essere aggiunti in futuro)
"""

#import delle classi di eccezioni personalizzate

# Eccezioni per la Cartella
from .cartella_exceptions import (
    CartellaException,
    CartellaNumeroTypeException,
    CartellaNumeroValueException,
    CartellaRigaTypeException,
    CartellaRigaValueException,
    CartellaColonnaTypeException,
    CartellaColonnaValueException,
)

# Eccezioni per il Giocatore
from .giocatore_exceptions import (
    GiocatoreException,
    GiocatoreNomeTypeException,
    GiocatoreNomeValueException,
    GiocatoreIdTypeException,
    GiocatoreCartellaTypeException,
    GiocatoreNumeroTypeException,
    GiocatoreNumeroValueException,
)
# Import delle eccezioni relative alla Partita
from .partita_exceptions import (
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

from .game_controller_exceptions import (
    ControllerNomeGiocatoreException,
    ControllerCartelleNegativeException,
    ControllerBotNegativeException,
    ControllerBotExcessException,
)

#definizione dell'export delle eccezioni
__all__ = [
    #cartella exceptions
    "CartellaException",
    "CartellaNumeroTypeException",
    "CartellaNumeroValueException",
    "CartellaRigaTypeException",
    "CartellaRigaValueException",
    "CartellaColonnaTypeException",
    "CartellaColonnaValueException",
    # Giocatore
    "GiocatoreException",
    "GiocatoreNomeTypeException",
    "GiocatoreNomeValueException",
    "GiocatoreIdTypeException",
    "GiocatoreCartellaTypeException",
    "GiocatoreNumeroTypeException",
    "GiocatoreNumeroValueException",
    #partita
    "PartitaException",
    "PartitaStatoException",
    "PartitaGiaIniziataException",
    "PartitaNonInCorsoException",
    "PartitaGiaTerminataException",
    "PartitaRosterException",
    "PartitaRosterPienoException",
    "PartitaGiocatoriInsufficientiException",
    "PartitaGiocatoreTypeException",
    "PartitaGiocatoreGiaPresenteException",
    "PartitaGiocoException",
    "PartitaNumeriEsauritiException",
    #game_controller
    "ControllerNomeGiocatoreException",
    "ControllerCartelleNegativeException",
"ControllerBotNegativeException",
"ControllerBotExcessException",
]