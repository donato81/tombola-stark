from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

# Import codici errore
from bingo_game.events.codici_errori import Codici_Errori

# Import eventi ammessi (ombrello)
from bingo_game.events.eventi_ui import (
    EventoFocusAutoImpostato,
    EventoFocusCartellaImpostato,
)
from bingo_game.events.eventi_partita import (
    EventoReclamoVittoria,
    EventoEsitoReclamoVittoria,
    EventoFineTurno,
)


# Ombrello: elenco chiuso degli eventi che possono viaggiare dentro EsitoAzione.evento
EventoAzione = Union[
    EventoFocusAutoImpostato,
    EventoFocusCartellaImpostato,
    EventoReclamoVittoria,
    EventoEsitoReclamoVittoria,
    EventoFineTurno,
]


@dataclass(frozen=True)
class EsitoAzione:
    """
    Esito generico per metodi "command" (es. navigazione focus, annuncia_ambo, annuncia_tombola, ecc.).

    Regole (semplici e stabili):
    - Se ok=False  -> errore DEVE essere valorizzato, evento DEVE essere None.
    - Se ok=True   -> errore DEVE essere None, evento può essere un EventoAzione oppure None
                     (successo "silenzioso", utile per non essere troppo verbosi in UI/voce).
    """

    ok: bool
    errore: Optional[Codici_Errori] = None
    evento: Optional[EventoAzione] = None

    @classmethod
    def successo(cls, evento: Optional[EventoAzione] = None) -> "EsitoAzione":
        """
        Crea un esito di successo.
        - errore sempre None
        - evento opzionale (può essere None per successi silenziosi)
        """
        return cls(ok=True, errore=None, evento=evento)

    @classmethod
    def fallimento(cls, errore: Codici_Errori) -> "EsitoAzione":
        """
        Crea un esito di fallimento.
        - ok sempre False
        - errore obbligatorio
        - evento sempre None
        """
        return cls(ok=False, errore=errore, evento=None)
