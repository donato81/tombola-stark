from __future__ import annotations

from typing import Final, Literal

# Chiavi "stabili" per i cataloghi UI (locales).
# Usare costanti evita refusi nel renderer e rende più facile fare refactor.
EVENTO_FOCUS_AUTO_IMPOSTATO: Final = "EVENTO_FOCUS_AUTO_IMPOSTATO"

# Chiavi ciclo turno V2.
TURNO_AVVISO_60: Final = "TURNO_AVVISO_60"
TURNO_AVVISO_80: Final = "TURNO_AVVISO_80"
TURNO_AVVISO_95: Final = "TURNO_AVVISO_95"
TURNO_TIMEOUT_SALTATO: Final = "TURNO_TIMEOUT_SALTATO"
TURNO_TUTTI_PRONTI: Final = "TURNO_TUTTI_PRONTI"
TURNO_PAUSA_INIZIO: Final = "TURNO_PAUSA_INIZIO"
TURNO_PAUSA_COUNTDOWN: Final = "TURNO_PAUSA_COUNTDOWN"

# Chiavi pausa gioco (layer UI).
PAUSA_ATTIVATA: Final = "PAUSA_ATTIVATA"
PAUSA_DISATTIVATA: Final = "PAUSA_DISATTIVATA"

# Tipo per tipizzare le chiavi evento (in modo simile a Codici_Errori).
Codici_Eventi = Literal[
    "EVENTO_FOCUS_AUTO_IMPOSTATO",
    "TURNO_AVVISO_60",
    "TURNO_AVVISO_80",
    "TURNO_AVVISO_95",
    "TURNO_TIMEOUT_SALTATO",
    "TURNO_TUTTI_PRONTI",
    "TURNO_PAUSA_INIZIO",
    "TURNO_PAUSA_COUNTDOWN",
    "PAUSA_ATTIVATA",
    "PAUSA_DISATTIVATA",
]
