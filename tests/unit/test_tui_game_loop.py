"""
Test unitari per bingo_game/ui/tui_game_loop.py — v0.9.0

Verifica:
1. _cmd_quit con conferma 's': imposta _quit_richiesto = True.
2. _cmd_quit con risposta 'n': NON imposta _quit_richiesto.
3. _cmd_quit con risposta vuota/invalida: NON imposta _quit_richiesto.
4. _cmd_segna con argomento non-intero: stampa errore NUMERO_TIPO_NON_VALIDO.
5. _stampa_numero_estratto: chiamabile senza eccezioni.
"""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def loop_con_partita_mock():
    """TuiGameLoop con partita mock (non richiede partita reale)."""
    from bingo_game.ui.tui_game_loop import TuiGameLoop
    partita_mock = MagicMock()
    # Configura get_stato_partita per evitare eccezioni nel __init__
    partita_mock.get_stato_partita.return_value = "in_corso"
    # Fa credere al controller che sia una Partita (isinstance check)
    from bingo_game.partita import Partita
    partita_mock.__class__ = Partita
    loop = TuiGameLoop(partita_mock)
    return loop


# ---------------------------------------------------------------------------
# Test 1 — quit confermato con 's'
# ---------------------------------------------------------------------------

def test_cmd_quit_conferma_si(loop_con_partita_mock):
    """_cmd_quit con risposta 's' deve impostare _quit_richiesto = True."""
    with patch("builtins.input", return_value="s"):
        loop_con_partita_mock._cmd_quit()
    assert loop_con_partita_mock._quit_richiesto is True


# ---------------------------------------------------------------------------
# Test 2 — quit annullato con 'n'
# ---------------------------------------------------------------------------

def test_cmd_quit_annullato_n(loop_con_partita_mock):
    """_cmd_quit con risposta 'n' NON deve impostare _quit_richiesto."""
    with patch("builtins.input", return_value="n"):
        loop_con_partita_mock._cmd_quit()
    assert loop_con_partita_mock._quit_richiesto is False


# ---------------------------------------------------------------------------
# Test 3 — quit annullato con input invalido
# ---------------------------------------------------------------------------

def test_cmd_quit_annullato_input_invalido(loop_con_partita_mock):
    """_cmd_quit con risposta vuota/casuale NON deve impostare _quit_richiesto."""
    for risposta in ["", "x", "no", "nope", "siù"]:
        loop_con_partita_mock._quit_richiesto = False  # reset
        with patch("builtins.input", return_value=risposta):
            loop_con_partita_mock._cmd_quit()
        assert loop_con_partita_mock._quit_richiesto is False, (
            f"_quit_richiesto doveva rimanere False per risposta '{risposta}'"
        )


# ---------------------------------------------------------------------------
# Test 4 — _cmd_segna con argomento non-intero stampa errore
# ---------------------------------------------------------------------------

def test_cmd_segna_argomento_non_intero_stampa_errore(loop_con_partita_mock, capsys):
    """_cmd_segna con argomento non intero deve stampare il messaggio di errore."""
    loop_con_partita_mock._cmd_segna("abc")
    out = capsys.readouterr().out
    # Deve contenere la prima riga del messaggio NUMERO_TIPO_NON_VALIDO
    assert "Tipo non valido" in out or "Errore" in out


# ---------------------------------------------------------------------------
# Test 5 — _stampa_numero_estratto non solleva eccezioni
# ---------------------------------------------------------------------------

def test_stampa_numero_estratto_non_solleva(loop_con_partita_mock, capsys):
    """_stampa_numero_estratto deve stampare senza eccezioni per qualsiasi int 1..90."""
    for numero in [1, 45, 90]:
        loop_con_partita_mock._stampa_numero_estratto(numero)
    out = capsys.readouterr().out
    assert "45" in out  # Il numero 45 deve apparire nell'output
