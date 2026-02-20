"""
Modulo: bingo_game.events.codici_loop

Costanti per i codici di evento del Game Loop (v0.9.0).

Queste costanti sono chiavi del catalogo MESSAGGI_OUTPUT_UI_UMANI definito in
bingo_game/ui/locales/it.py.  Seguono lo stesso pattern di
bingo_game/events/codici_eventi.py: Final + Literal per la type-safety.

Version:
    v0.9.0: Prima implementazione.
"""
from __future__ import annotations

from typing import Final, Literal

# ---------------------------------------------------------------------------
# Costanti di codice evento per il Game Loop
# ---------------------------------------------------------------------------

LOOP_NUMERO_ESTRATTO: Final = "LOOP_NUMERO_ESTRATTO"
LOOP_PROMPT_COMANDO: Final = "LOOP_PROMPT_COMANDO"
LOOP_HELP_COMANDI: Final = "LOOP_HELP_COMANDI"
LOOP_HELP_FOCUS: Final = "LOOP_HELP_FOCUS"
LOOP_QUIT_CONFERMA: Final = "LOOP_QUIT_CONFERMA"
LOOP_QUIT_ANNULLATO: Final = "LOOP_QUIT_ANNULLATO"
LOOP_REPORT_FINALE_INTESTAZIONE: Final = "LOOP_REPORT_FINALE_INTESTAZIONE"
LOOP_REPORT_FINALE_TURNI: Final = "LOOP_REPORT_FINALE_TURNI"
LOOP_REPORT_FINALE_ESTRATTI: Final = "LOOP_REPORT_FINALE_ESTRATTI"
LOOP_REPORT_FINALE_VINCITORE: Final = "LOOP_REPORT_FINALE_VINCITORE"
LOOP_REPORT_FINALE_NESSUN_VINCITORE: Final = "LOOP_REPORT_FINALE_NESSUN_VINCITORE"
LOOP_REPORT_FINALE_PREMI: Final = "LOOP_REPORT_FINALE_PREMI"
LOOP_COMANDO_NON_RICONOSCIUTO: Final = "LOOP_COMANDO_NON_RICONOSCIUTO"

# ---------------------------------------------------------------------------
# Tipo Literal per type-checking (stesso pattern di Codici_Output_Ui_Umani)
# ---------------------------------------------------------------------------

Codici_Loop = Literal[
    "LOOP_NUMERO_ESTRATTO",
    "LOOP_PROMPT_COMANDO",
    "LOOP_HELP_COMANDI",
    "LOOP_HELP_FOCUS",
    "LOOP_QUIT_CONFERMA",
    "LOOP_QUIT_ANNULLATO",
    "LOOP_REPORT_FINALE_INTESTAZIONE",
    "LOOP_REPORT_FINALE_TURNI",
    "LOOP_REPORT_FINALE_ESTRATTI",
    "LOOP_REPORT_FINALE_VINCITORE",
    "LOOP_REPORT_FINALE_NESSUN_VINCITORE",
    "LOOP_REPORT_FINALE_PREMI",
    "LOOP_COMANDO_NON_RICONOSCIUTO",
]
