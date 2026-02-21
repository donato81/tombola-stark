"""
Test unitari per game_controller — ottieni_giocatore_umano() v0.9.0

Copertura:
1.  ottieni_giocatore_umano() ritorna il primo GiocatoreUmano.
2.  Nome corretto del GiocatoreUmano ritornato.
3.  Ritorna None se la partita ha solo bot.
4.  Ritorna None per input non-Partita (None).
5.  Ritorna None per input non-Partita (intero).
6.  Ritorna None per input non-Partita (stringa).
7.  Non modifica lo stato della partita (nessun side effect).
8.  Smoke: crea_partita_standard non è regredita.
9.  Smoke: esegui_turno_sicuro non è regredita.
10. Smoke: ottieni_stato_sintetico non è regredita.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Fixture condivise
# ---------------------------------------------------------------------------

@pytest.fixture
def partita_avviata():
    """Partita standard (1 umano + 1 bot) già avviata."""
    from bingo_game.game_controller import (
        crea_partita_standard,
        avvia_partita_sicura,
    )
    partita = crea_partita_standard(
        nome_giocatore_umano="TestPlayer",
        num_cartelle_umano=1,
        num_bot=1,
    )
    avvia_partita_sicura(partita)
    return partita


@pytest.fixture
def partita_solo_bot():
    """Partita creata manualmente con solo bot (nessun GiocatoreUmano)."""
    from bingo_game.tabellone import Tabellone
    from bingo_game.partita import Partita
    from bingo_game.game_controller import crea_giocatori_automatici

    tabellone = Tabellone()
    bot_list = crea_giocatori_automatici(num_bot=2)
    return Partita(tabellone, bot_list)


# ---------------------------------------------------------------------------
# Test 1 — Ritorna un oggetto non-None su partita valida
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_ritorna_non_none(partita_avviata):
    """ottieni_giocatore_umano deve ritornare un oggetto non-None su partita valida."""
    from bingo_game.game_controller import ottieni_giocatore_umano
    risultato = ottieni_giocatore_umano(partita_avviata)
    assert risultato is not None, "ottieni_giocatore_umano ha ritornato None su partita valida"


# ---------------------------------------------------------------------------
# Test 2 — Il GiocatoreUmano ha il nome corretto
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_nome_corretto(partita_avviata):
    """ottieni_giocatore_umano deve ritornare il GiocatoreUmano con il nome giusto."""
    from bingo_game.game_controller import ottieni_giocatore_umano
    giocatore = ottieni_giocatore_umano(partita_avviata)
    assert giocatore is not None
    assert giocatore.nome == "TestPlayer", (
        f"Nome atteso 'TestPlayer', ottenuto '{giocatore.nome}'"
    )


# ---------------------------------------------------------------------------
# Test 3 — Partita con solo bot → None
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_solo_bot_ritorna_none(partita_solo_bot):
    """Con partita senza GiocatoreUmano deve ritornare None."""
    from bingo_game.game_controller import ottieni_giocatore_umano
    risultato = ottieni_giocatore_umano(partita_solo_bot)
    assert risultato is None, "Atteso None con partita di soli bot"


# ---------------------------------------------------------------------------
# Test 4 — Input None → None
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_none_ritorna_none():
    """Con None come argomento deve ritornare None senza eccezioni."""
    from bingo_game.game_controller import ottieni_giocatore_umano
    assert ottieni_giocatore_umano(None) is None


# ---------------------------------------------------------------------------
# Test 5 — Input intero → None
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_intero_ritorna_none():
    """Con intero come argomento deve ritornare None senza eccezioni."""
    from bingo_game.game_controller import ottieni_giocatore_umano
    assert ottieni_giocatore_umano(42) is None


# ---------------------------------------------------------------------------
# Test 6 — Input stringa → None
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_stringa_ritorna_none():
    """Con stringa come argomento deve ritornare None senza eccezioni."""
    from bingo_game.game_controller import ottieni_giocatore_umano
    assert ottieni_giocatore_umano("non-partita") is None


# ---------------------------------------------------------------------------
# Test 7 — Nessun side effect sulla partita
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_nessun_side_effect(partita_avviata):
    """ottieni_giocatore_umano non deve modificare lo stato della partita."""
    from bingo_game.game_controller import ottieni_giocatore_umano, ottieni_stato_sintetico

    stato_prima = ottieni_stato_sintetico(partita_avviata)
    ottieni_giocatore_umano(partita_avviata)
    stato_dopo = ottieni_stato_sintetico(partita_avviata)

    assert stato_prima["stato_partita"] == stato_dopo["stato_partita"]
    assert stato_prima["numeri_estratti"] == stato_dopo["numeri_estratti"]


# ---------------------------------------------------------------------------
# Test 8 — Smoke: crea_partita_standard non è regredita
# ---------------------------------------------------------------------------

def test_smoke_crea_partita_standard():
    """crea_partita_standard deve ancora funzionare dopo le modifiche del controller."""
    from bingo_game.game_controller import crea_partita_standard
    partita = crea_partita_standard(
        nome_giocatore_umano="SmokeTest",
        num_cartelle_umano=1,
        num_bot=1,
    )
    assert partita is not None
    assert partita.get_numero_giocatori() == 2


# ---------------------------------------------------------------------------
# Test 9 — Smoke: esegui_turno_sicuro non è regredita
# ---------------------------------------------------------------------------

def test_smoke_esegui_turno_sicuro(partita_avviata):
    """esegui_turno_sicuro deve ancora funzionare dopo le modifiche del controller."""
    from bingo_game.game_controller import esegui_turno_sicuro
    risultato = esegui_turno_sicuro(partita_avviata)
    assert risultato is not None
    assert "numero_estratto" in risultato
    assert "tombola_rilevata" in risultato


# ---------------------------------------------------------------------------
# Test 10 — Smoke: ottieni_stato_sintetico non è regredita
# ---------------------------------------------------------------------------

def test_smoke_ottieni_stato_sintetico(partita_avviata):
    """ottieni_stato_sintetico deve ancora funzionare dopo le modifiche del controller."""
    from bingo_game.game_controller import ottieni_stato_sintetico
    stato = ottieni_stato_sintetico(partita_avviata)
    assert isinstance(stato, dict)
    assert "stato_partita" in stato
    assert "numeri_estratti" in stato
    assert "giocatori" in stato
