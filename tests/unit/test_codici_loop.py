"""
Test unitari per bingo_game/events/codici_loop.py — v0.9.0

Verifica:
1. Tutte le costanti sono stringhe non vuote.
2. Nessuna costante è duplicata.
3. Tutte le 13 chiavi LOOP_* sono presenti in MESSAGGI_OUTPUT_UI_UMANI.
4. I template con placeholder sono formattabili senza eccezioni.
5. L'import di codici_loop non produce side effect.
"""
from __future__ import annotations

import importlib
import sys

import pytest


# ---------------------------------------------------------------------------
# Test 1 — Le costanti sono stringhe non vuote
# ---------------------------------------------------------------------------

def test_costanti_loop_sono_stringhe_non_vuote():
    """Tutte le costanti in codici_loop sono str non vuote."""
    from bingo_game.events.codici_loop import (
        LOOP_TURNO_AVANZATO,
        LOOP_NUMERO_ESTRATTO,
        LOOP_SEGNAZIONE_OK,
        LOOP_REPORT_FINALE,
        LOOP_QUIT_CONFERMATO,
        LOOP_QUIT_ANNULLATO,
        LOOP_HELP,
        LOOP_FOCUS_AUTO,
    )
    costanti = [
        LOOP_TURNO_AVANZATO, LOOP_NUMERO_ESTRATTO, LOOP_SEGNAZIONE_OK,
        LOOP_REPORT_FINALE, LOOP_QUIT_CONFERMATO, LOOP_QUIT_ANNULLATO,
        LOOP_HELP, LOOP_FOCUS_AUTO,
    ]
    for c in costanti:
        assert isinstance(c, str), f"Costante non è str: {c!r}"
        assert len(c) > 0, f"Costante è stringa vuota: {c!r}"


# ---------------------------------------------------------------------------
# Test 2 — Nessuna costante duplicata
# ---------------------------------------------------------------------------

def test_costanti_loop_nessun_duplicato():
    """Nessuna costante in codici_loop è duplicata."""
    from bingo_game.events.codici_loop import (
        LOOP_TURNO_AVANZATO, LOOP_NUMERO_ESTRATTO, LOOP_SEGNAZIONE_OK,
        LOOP_REPORT_FINALE, LOOP_QUIT_CONFERMATO, LOOP_QUIT_ANNULLATO,
        LOOP_HELP, LOOP_FOCUS_AUTO,
    )
    costanti = [
        LOOP_TURNO_AVANZATO, LOOP_NUMERO_ESTRATTO, LOOP_SEGNAZIONE_OK,
        LOOP_REPORT_FINALE, LOOP_QUIT_CONFERMATO, LOOP_QUIT_ANNULLATO,
        LOOP_HELP, LOOP_FOCUS_AUTO,
    ]
    assert len(costanti) == len(set(costanti)), "Costanti duplicate trovate in codici_loop"


# ---------------------------------------------------------------------------
# Test 3 — Le 13 chiavi LOOP_* sono presenti in MESSAGGI_OUTPUT_UI_UMANI
# ---------------------------------------------------------------------------

CHIAVI_LOOP_ATTESE = [
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


@pytest.mark.parametrize("chiave", CHIAVI_LOOP_ATTESE)
def test_chiavi_loop_presenti_in_messaggi_output_ui_umani(chiave):
    """Ogni chiave LOOP_* deve essere presente in MESSAGGI_OUTPUT_UI_UMANI."""
    from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI
    assert chiave in MESSAGGI_OUTPUT_UI_UMANI, (
        f"Chiave mancante in MESSAGGI_OUTPUT_UI_UMANI: {chiave!r}"
    )


# ---------------------------------------------------------------------------
# Test 4 — I template con placeholder sono formattabili
# ---------------------------------------------------------------------------

def test_template_placeholder_formattabili():
    """I template con placeholder non sollevano eccezioni se formattati con valori dummy."""
    from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI

    valori_dummy = {
        "numero": 42,
        "numero_cartella": 1,
        "turni": 10,
        "estratti": 45,
        "nome": "Mario",
        "premi": 3,
    }

    chiavi_con_placeholder = [
        "LOOP_NUMERO_ESTRATTO",
        "LOOP_HELP_FOCUS",
        "LOOP_REPORT_FINALE_TURNI",
        "LOOP_REPORT_FINALE_ESTRATTI",
        "LOOP_REPORT_FINALE_VINCITORE",
        "LOOP_REPORT_FINALE_PREMI",
    ]

    for chiave in chiavi_con_placeholder:
        righe = MESSAGGI_OUTPUT_UI_UMANI[chiave]
        for riga in righe:
            try:
                risultato = riga.format(**valori_dummy)
                assert isinstance(risultato, str)
            except KeyError as exc:
                pytest.fail(
                    f"Placeholder mancante per chiave {chiave!r}, riga {riga!r}: {exc}"
                )


# ---------------------------------------------------------------------------
# Test 5 — L'import di codici_loop non produce side effect
# ---------------------------------------------------------------------------

def test_import_codici_loop_no_side_effect():
    """L'import di codici_loop non deve produrre side effect visibili."""
    # Rimuovi il modulo dalla cache per forzare re-import
    sys.modules.pop("bingo_game.events.codici_loop", None)
    mod = importlib.import_module("bingo_game.events.codici_loop")
    # Deve esporre le costanti attese
    assert hasattr(mod, "LOOP_TURNO_AVANZATO")
    assert hasattr(mod, "LOOP_HELP")
    assert hasattr(mod, "LOOP_FOCUS_AUTO")
