"""
Test unitari per bingo_game.events.codici_loop — v0.9.0.

Verifica:
1. Tutte le costanti sono stringhe non vuote.
2. Nessuna costante duplicata.
3. Tutte le 13 chiavi LOOP_* presenti in MESSAGGI_OUTPUT_UI_UMANI.
4. Template con placeholder sono formattabili senza eccezioni.
5. Import senza side effect.
"""
from __future__ import annotations

import importlib

import pytest


# ---------------------------------------------------------------------------
# Test 1: tutte le costanti sono stringhe non vuote
# ---------------------------------------------------------------------------

def test_costanti_loop_sono_stringhe_non_vuote():
    """Ogni costante LOOP_* deve essere una stringa non vuota."""
    import bingo_game.events.codici_loop as m
    costanti = [
        m.LOOP_NUMERO_ESTRATTO,
        m.LOOP_PROMPT_COMANDO,
        m.LOOP_HELP_COMANDI,
        m.LOOP_HELP_FOCUS,
        m.LOOP_QUIT_CONFERMA,
        m.LOOP_QUIT_ANNULLATO,
        m.LOOP_REPORT_FINALE_INTESTAZIONE,
        m.LOOP_REPORT_FINALE_TURNI,
        m.LOOP_REPORT_FINALE_ESTRATTI,
        m.LOOP_REPORT_FINALE_VINCITORE,
        m.LOOP_REPORT_FINALE_NESSUN_VINCITORE,
        m.LOOP_REPORT_FINALE_PREMI,
        m.LOOP_COMANDO_NON_RICONOSCIUTO,
    ]
    for c in costanti:
        assert isinstance(c, str), f"Costante non è stringa: {c!r}"
        assert len(c) > 0, f"Costante è stringa vuota: {c!r}"


# ---------------------------------------------------------------------------
# Test 2: nessuna costante duplicata
# ---------------------------------------------------------------------------

def test_costanti_loop_nessun_duplicato():
    """Nessuna costante LOOP_* deve avere lo stesso valore di un'altra."""
    import bingo_game.events.codici_loop as m
    costanti = [
        m.LOOP_NUMERO_ESTRATTO,
        m.LOOP_PROMPT_COMANDO,
        m.LOOP_HELP_COMANDI,
        m.LOOP_HELP_FOCUS,
        m.LOOP_QUIT_CONFERMA,
        m.LOOP_QUIT_ANNULLATO,
        m.LOOP_REPORT_FINALE_INTESTAZIONE,
        m.LOOP_REPORT_FINALE_TURNI,
        m.LOOP_REPORT_FINALE_ESTRATTI,
        m.LOOP_REPORT_FINALE_VINCITORE,
        m.LOOP_REPORT_FINALE_NESSUN_VINCITORE,
        m.LOOP_REPORT_FINALE_PREMI,
        m.LOOP_COMANDO_NON_RICONOSCIUTO,
    ]
    assert len(costanti) == len(set(costanti)), "Trovati valori duplicati tra le costanti LOOP_*"


# ---------------------------------------------------------------------------
# Test 3: tutte le chiavi LOOP_* presenti in MESSAGGI_OUTPUT_UI_UMANI
# ---------------------------------------------------------------------------

def test_chiavi_loop_presenti_in_messaggi_output_ui_umani():
    """Ogni costante LOOP_* deve essere una chiave di MESSAGGI_OUTPUT_UI_UMANI."""
    import bingo_game.events.codici_loop as m
    from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI

    chiavi_attese = [
        m.LOOP_NUMERO_ESTRATTO,
        m.LOOP_PROMPT_COMANDO,
        m.LOOP_HELP_COMANDI,
        m.LOOP_HELP_FOCUS,
        m.LOOP_QUIT_CONFERMA,
        m.LOOP_QUIT_ANNULLATO,
        m.LOOP_REPORT_FINALE_INTESTAZIONE,
        m.LOOP_REPORT_FINALE_TURNI,
        m.LOOP_REPORT_FINALE_ESTRATTI,
        m.LOOP_REPORT_FINALE_VINCITORE,
        m.LOOP_REPORT_FINALE_NESSUN_VINCITORE,
        m.LOOP_REPORT_FINALE_PREMI,
        m.LOOP_COMANDO_NON_RICONOSCIUTO,
    ]
    for chiave in chiavi_attese:
        assert chiave in MESSAGGI_OUTPUT_UI_UMANI, (
            f"Chiave mancante in MESSAGGI_OUTPUT_UI_UMANI: {chiave!r}"
        )


# ---------------------------------------------------------------------------
# Test 4: template con placeholder sono formattabili
# ---------------------------------------------------------------------------

def test_template_con_placeholder_sono_formattabili():
    """I template con placeholder devono accettare .format() senza eccezioni."""
    from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI
    import bingo_game.events.codici_loop as m

    placeholder_map = {
        m.LOOP_NUMERO_ESTRATTO: {"numero": 42},
        m.LOOP_HELP_FOCUS: {"numero_cartella": 1},
        m.LOOP_REPORT_FINALE_TURNI: {"turni": 45},
        m.LOOP_REPORT_FINALE_ESTRATTI: {"estratti": 45},
        m.LOOP_REPORT_FINALE_VINCITORE: {"nome": "Mario"},
        m.LOOP_REPORT_FINALE_PREMI: {"premi": 3},
    }
    for chiave, kwargs in placeholder_map.items():
        tupla = MESSAGGI_OUTPUT_UI_UMANI[chiave]
        for riga in tupla:
            try:
                riga.format(**kwargs)
            except KeyError as exc:
                pytest.fail(f"Placeholder mancante in {chiave!r}: {exc}")


# ---------------------------------------------------------------------------
# Test 5: import senza side effect
# ---------------------------------------------------------------------------

def test_import_codici_loop_senza_side_effect(capsys):
    """L'import di codici_loop non deve produrre output su stdout/stderr."""
    importlib.reload(__import__("bingo_game.events.codici_loop", fromlist=["codici_loop"]))
    captured = capsys.readouterr()
    assert captured.out == "", "Import codici_loop produce output su stdout"
    assert captured.err == "", "Import codici_loop produce output su stderr"
