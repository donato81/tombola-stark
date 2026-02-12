from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

__all__ = [
    "Tipo_Focus",
    "EventoFocusAutoImpostato",
    "EventoFocusCartellaImpostato",
]

# Tipi di dominio (fonte unica per i valori ammessi del focus)
Tipo_Focus = Literal["cartella", "riga", "colonna"]


@dataclass(frozen=True)
class EventoFocusAutoImpostato:
    """
    Evento generato quando un helper imposta automaticamente un focus mancante
    (es. focus cartella a 0, focus riga a 0, focus colonna a 0).

    Note di stabilità:
    - Non contiene testo: la UI può decidere se notificare o restare silenziosa.
    - "indice" è l'indice interno 0-based.
    """
    tipo_focus: Tipo_Focus
    indice: int


@dataclass(frozen=True)
class EventoFocusCartellaImpostato:
    """
    Evento generato quando il giocatore imposta esplicitamente il focus su una cartella specifica
    (ad esempio tramite comando da tastiera).

    Scopo:
    - Permettere alla UI/screen reader di sapere quale cartella è diventata attiva,
      senza stringhe “pronte” dentro la logica di gioco.

    Campi importanti:
    - numero_cartella: numero "umano" (1..N), utile per annunci e comandi.
    - indice_cartella: indice interno 0-based, utile per la logica e per riferimenti coerenti.
    - reset_riga_colonna: True se, cambiando cartella, sono stati resettati i focus di riga e colonna
      per evitare di trascinare selezioni della cartella precedente.
    """
    id_giocatore: Optional[int]
    nome_giocatore: str
    numero_cartella: int
    indice_cartella: int
    reset_riga_colonna: bool = False
