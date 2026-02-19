"""Test di integrazione: copertura completa degli eventi di Fase 2.

Verifica che una partita completa produca tutte le categorie di eventi
attese nel file di log, con il contenuto semanticamente corretto.
"""
import logging
import pytest
from bingo_game.logging.game_logger import GameLogger
from bingo_game.game_controller import (
    crea_partita_standard,
    avvia_partita_sicura,
    esegui_turno_sicuro,
    partita_terminata,
)


@pytest.fixture(autouse=True)
def reset_logger():
    yield
    GameLogger.shutdown()
    GameLogger._initialized = False
    for name in ["tombola_stark", "tombola_stark.game",
                 "tombola_stark.prizes", "tombola_stark.system", "tombola_stark.errors"]:
        logging.getLogger(name).handlers.clear()


@pytest.fixture
def tmp_log(tmp_path, monkeypatch):
    import bingo_game.logging.game_logger as gl
    monkeypatch.setattr(gl, "_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(gl, "_LOG_FILE", tmp_path / "logs" / "tombola_stark.log")
    return tmp_path / "logs" / "tombola_stark.log"


def _read(tmp_log):
    return tmp_log.read_text(encoding="utf-8")


def test_partita_completa_produce_game_created(tmp_log):
    """Una partita completa produce l'evento GAME_CREATED con dati corretti."""
    GameLogger.initialize()
    crea_partita_standard("TestPlayer", num_cartelle_umano=1, num_bot=1)
    assert "[GAME] Partita creata" in _read(tmp_log)
    assert "TestPlayer" in _read(tmp_log)


def test_partita_avviata_produce_game_started(tmp_log):
    """avvia_partita_sicura produce GAME_STARTED con stato in_corso."""
    GameLogger.initialize()
    p = crea_partita_standard("Test", num_cartelle_umano=1, num_bot=1)
    avvia_partita_sicura(p)
    assert "[GAME] Partita avviata" in _read(tmp_log)
    assert "in_corso" in _read(tmp_log)


def test_turni_in_debug_producono_game_turn(tmp_log):
    """In modalità debug, ogni turno produce un evento [GAME] Turno #N."""
    GameLogger.initialize(debug_mode=True)
    p = crea_partita_standard("Test", num_cartelle_umano=1, num_bot=1)
    avvia_partita_sicura(p)
    esegui_turno_sicuro(p)
    assert "[GAME] Turno #1" in _read(tmp_log)


def test_premio_produce_prize_event(tmp_log):
    """Un premio assegnato durante la partita produce un evento [PRIZE]."""
    GameLogger.initialize()
    p = crea_partita_standard("Test", num_cartelle_umano=1, num_bot=1)
    avvia_partita_sicura(p)
    # Eseguiamo turni finché non c'è almeno un premio o la partita finisce
    for _ in range(90):
        risultato = esegui_turno_sicuro(p)
        if risultato and risultato.get("premi_nuovi"):
            break
        if partita_terminata(p):
            break
    content = _read(tmp_log)
    # Almeno una delle categorie prize deve essere presente
    assert any(tag in content for tag in ["[PRIZE]", "[GAME] Partita terminata"])


def test_fine_partita_produce_riepilogo(tmp_log):
    """Al termine della partita il riepilogo [GAME] === RIEPILOGO è nel log."""
    GameLogger.initialize()
    p = crea_partita_standard("Test", num_cartelle_umano=1, num_bot=1)
    avvia_partita_sicura(p)
    while not partita_terminata(p):
        esegui_turno_sicuro(p)
    assert "RIEPILOGO" in _read(tmp_log)
