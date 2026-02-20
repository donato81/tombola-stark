from __future__ import annotations

from typing import Final, Literal

# =============================================================================
# Costanti per i codici di evento del Game Loop — v0.9.0
# =============================================================================
# Convenzione: ogni costante è una stringa immutabile (Final) che identifica
# un evento/codice del loop di partita.
# Il renderer e la TUI le usano come chiavi per recuperare il testo da it.py.
# Nessun side effect all'import.
# =============================================================================

LOOP_TURNO_AVANZATO:   Final = "LOOP_TURNO_AVANZATO"
LOOP_NUMERO_ESTRATTO:  Final = "LOOP_NUMERO_ESTRATTO"
LOOP_SEGNAZIONE_OK:    Final = "LOOP_SEGNAZIONE_OK"
LOOP_REPORT_FINALE:    Final = "LOOP_REPORT_FINALE"
LOOP_QUIT_CONFERMATO:  Final = "LOOP_QUIT_CONFERMATO"
LOOP_QUIT_ANNULLATO:   Final = "LOOP_QUIT_ANNULLATO"
LOOP_HELP:             Final = "LOOP_HELP"
LOOP_FOCUS_AUTO:       Final = "LOOP_FOCUS_AUTO"

# Tipo Literal per type-checking sulle chiavi del catalogo loop.
Codici_Loop = Literal[
    "LOOP_TURNO_AVANZATO",
    "LOOP_NUMERO_ESTRATTO",
    "LOOP_SEGNAZIONE_OK",
    "LOOP_REPORT_FINALE",
    "LOOP_QUIT_CONFERMATO",
    "LOOP_QUIT_ANNULLATO",
    "LOOP_HELP",
    "LOOP_FOCUS_AUTO",
]
