from __future__ import annotations

from typing import Final, Literal

# Chiavi "stabili" per i cataloghi UI (locales).
# Usare costanti evita refusi nel renderer e rende più facile fare refactor.
EVENTO_FOCUS_AUTO_IMPOSTATO: Final = "EVENTO_FOCUS_AUTO_IMPOSTATO"

# Tipo per tipizzare le chiavi evento (in modo simile a Codici_Errori).
Codici_Eventi = Literal[
    "EVENTO_FOCUS_AUTO_IMPOSTATO",
]
