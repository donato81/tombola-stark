"""Unit test per la copertura eventi di Fase 2.

Verifica che le funzioni helper di logging (sub-logger, _log_prize_event,
_log_game_summary) scrivano le righe attese con il prefisso di categoria corretto.
"""
import logging
import pytest
from bingo_game.logging.game_logger import GameLogger


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


def test_sublogger_game_scrive_su_file(tmp_log):
    """Il sub-logger tombola_stark.game propaga sul file del logger radice."""
    GameLogger.initialize()
    logging.getLogger("tombola_stark.game").info("[GAME] Test game event")
    assert "[GAME] Test game event" in _read(tmp_log)


def test_sublogger_prizes_scrive_su_file(tmp_log):
    """Il sub-logger tombola_stark.prizes propaga sul file del logger radice."""
    GameLogger.initialize()
    logging.getLogger("tombola_stark.prizes").info("[PRIZE] Test prize event")
    assert "[PRIZE] Test prize event" in _read(tmp_log)


def test_sublogger_errors_scrive_su_file(tmp_log):
    """Il sub-logger tombola_stark.errors propaga sul file del logger radice."""
    GameLogger.initialize()
    logging.getLogger("tombola_stark.errors").warning("[ERR] Test error event")
    assert "[ERR] Test error event" in _read(tmp_log)


def test_sublogger_system_scrive_su_file(tmp_log):
    """Il sub-logger tombola_stark.system propaga sul file del logger radice."""
    GameLogger.initialize()
    logging.getLogger("tombola_stark.system").info("[SYS] Test system event")
    assert "[SYS] Test system event" in _read(tmp_log)


def test_debug_non_scrive_in_modalita_normale(tmp_log):
    """In modalità normale (INFO), gli eventi DEBUG non compaiono nel file."""
    GameLogger.initialize(debug_mode=False)
    logging.getLogger("tombola_stark.game").debug("[GAME] Turno #1 — estratto: 42")
    assert "Turno #1" not in _read(tmp_log)


def test_debug_scrive_in_modalita_debug(tmp_log):
    """In modalità debug, gli eventi DEBUG compaiono nel file."""
    GameLogger.initialize(debug_mode=True)
    logging.getLogger("tombola_stark.game").debug("[GAME] Turno #1 — estratto: 42")
    assert "Turno #1" in _read(tmp_log)


def test_prefissi_categoria_distinti_nel_file(tmp_log):
    """Più categorie di eventi sono distinguibili nel file tramite prefisso."""
    GameLogger.initialize()
    logging.getLogger("tombola_stark.game").info("[GAME] evento gioco")
    logging.getLogger("tombola_stark.prizes").info("[PRIZE] evento premio")
    logging.getLogger("tombola_stark.errors").warning("[ERR] evento errore")
    content = _read(tmp_log)
    assert "[GAME]" in content
    assert "[PRIZE]" in content
    assert "[ERR]" in content
