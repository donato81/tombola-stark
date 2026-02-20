"""
Test unitari per game_controller.ottieni_giocatore_umano() — v0.9.0

Verifica:
1. Con partita standard: ritorna GiocatoreUmano non-None.
2. Con partita standard: il nome corrisponde a quello inserito.
3. Con parametro non-Partita: ritorna None senza eccezioni.
4. Smoke test regressione: esegui_turno_sicuro non è rotto dopo le modifiche.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def partita_configurata():
    """Partita standard creata e avviata (stato in_corso)."""
    from bingo_game.game_controller import (
        crea_partita_standard,
        avvia_partita_sicura,
    )
    partita = crea_partita_standard(
        nome_giocatore_umano="TestUmano",
        num_cartelle_umano=1,
        num_bot=1,
    )
    avvia_partita_sicura(partita)
    return partita


# ---------------------------------------------------------------------------
# Test 1 — Ritorna GiocatoreUmano non-None
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_ritorna_non_none(partita_configurata):
    """Con partita valida deve ritornare un oggetto non-None."""
    from bingo_game.game_controller import ottieni_giocatore_umano
    risultato = ottieni_giocatore_umano(partita_configurata)
    assert risultato is not None, "ottieni_giocatore_umano ha ritornato None su partita valida"


# ---------------------------------------------------------------------------
# Test 2 — Il nome corrisponde
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_nome_corretto(partita_configurata):
    """Il GiocatoreUmano restituito deve avere il nome usato in crea_partita_standard."""
    from bingo_game.game_controller import ottieni_giocatore_umano
    giocatore = ottieni_giocatore_umano(partita_configurata)
    assert giocatore is not None
    assert giocatore.nome == "TestUmano", (
        f"Nome atteso 'TestUmano', ottenuto '{giocatore.nome}'"
    )


# ---------------------------------------------------------------------------
# Test 3 — Con parametro non-Partita ritorna None
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_parametro_invalido_ritorna_none():
    """Con parametro non-Partita deve ritornare None senza sollevare eccezioni."""
    from bingo_game.game_controller import ottieni_giocatore_umano
    assert ottieni_giocatore_umano(None) is None
    assert ottieni_giocatore_umano("non-partita") is None
    assert ottieni_giocatore_umano(42) is None


# ---------------------------------------------------------------------------
# Test 4 — Smoke test: esegui_turno_sicuro non è rotto
# ---------------------------------------------------------------------------

def test_esegui_turno_sicuro_smoke(partita_configurata):
    """Dopo le modifiche del controller, esegui_turno_sicuro deve ancora funzionare."""
    from bingo_game.game_controller import esegui_turno_sicuro
    risultato = esegui_turno_sicuro(partita_configurata)
    assert risultato is not None, "esegui_turno_sicuro ha ritornato None su partita valida"
    assert "numero_estratto" in risultato
    assert "tombola_rilevata" in risultato
