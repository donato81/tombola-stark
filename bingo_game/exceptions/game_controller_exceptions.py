"""
Eccezioni personalizzate per il Game Controller
===============================================

Modulo: bingo_game.exceptions.game_controller_exceptions

Questo modulo definisce le eccezioni specifiche per le funzioni del game_controller.py.
Ogni eccezione è progettata per identificare univocamente un tipo di errore nel controller,
mantenendo coerenza con le eccezioni già definite per giocatori e cartelle.

Le eccezioni sostituiscono i ValueError generici con messaggi semantici chiari e
facilitano il debugging e la gestione degli errori specifici del controller.
"""

from __future__ import annotations

class ControllerNomeGiocatoreException(Exception):
    """
    Eccezione sollevata quando il nome del giocatore umano è invalido.

    Sollevata da:
    - crea_giocatore_umano()
    - crea_partita_standard()

    Cause comuni:
    - nome vuoto ("" o None)
    - nome composto solo da spazi ("   ")
    """
    def __init__(self, nome_invalido: str) -> None:
        self.messaggio = f"ControllerNomeGiocatoreException: Nome giocatore umano invalido: '{nome_invalido}'"
        super().__init__(self.messaggio)


class ControllerCartelleNegativeException(Exception):
    """
    Eccezione sollevata quando il numero di cartelle è negativo.

    Sollevata da:
    - assegna_cartelle_a_giocatore()
    - crea_giocatore_umano()
    - crea_partita_standard()

    Parametro:
    - num_cartelle: int < 0
    """
    def __init__(self, num_cartelle: int) -> None:
        self.messaggio = f"ControllerCartelleNegativeException: Numero cartelle negativo: {num_cartelle}"
        super().__init__(self.messaggio)


class ControllerBotNegativeException(Exception):
    """
    Eccezione sollevata quando il numero di bot è negativo.

    Sollevata da:
    - crea_giocatori_automatici()
    - crea_partita_standard()

    Parametro:
    - num_bot: int < 0
    """
    def __init__(self, num_bot: int) -> None:
        self.messaggio = f"ControllerBotNegativeException: Numero bot negativo: {num_bot}"
        super().__init__(self.messaggio)


class ControllerBotExcessException(Exception):
    """
    Eccezione sollevata quando il numero di bot supera il limite massimo (7).

    Sollevata da:
    - crea_giocatori_automatici()
    - crea_partita_standard()

    Motivo: Partita standard limitata a 8 giocatori totali (1 umano + 7 bot).
    """
    def __init__(self) -> None:
        self.messaggio = "ControllerBotExcessException: Massimo 7 bot consentiti (partita da 8 giocatori totali)"
        super().__init__(self.messaggio)
