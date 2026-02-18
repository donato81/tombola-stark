"""Unit tests for bingo_game.logging.GameLogger (Phase 1).

Tests the GameLogger singleton initialization, file creation,
session markers, and debug/info level configuration.
"""
import logging
from pathlib import Path
import pytest

from bingo_game.logging.game_logger import GameLogger, _LOG_DIR, _LOG_FILE, _LOGGER_NAME


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset GameLogger state before each test."""
    GameLogger._initialized = False
    GameLogger._instance = None
    yield
    # Cleanup after test
    if GameLogger._initialized:
        GameLogger.shutdown()
    GameLogger._initialized = False
    GameLogger._instance = None


@pytest.fixture
def temp_log_dir(tmp_path, monkeypatch):
    """Redirect log directory to temporary path for testing."""
    test_log_dir = tmp_path / "test_logs"
    test_log_file = test_log_dir / "tombola_stark.log"
    
    # Monkeypatch the module-level constants
    monkeypatch.setattr("bingo_game.logging.game_logger._LOG_DIR", test_log_dir)
    monkeypatch.setattr("bingo_game.logging.game_logger._LOG_FILE", test_log_file)
    
    return test_log_dir, test_log_file


def test_initialize_crea_cartella_log(temp_log_dir):
    """Test that initialize() creates the log directory if it doesn't exist."""
    log_dir, log_file = temp_log_dir
    
    assert not log_dir.exists(), "Log directory should not exist before initialization"
    
    GameLogger.initialize(debug_mode=False)
    
    assert log_dir.exists(), "Log directory should be created by initialize()"
    assert log_dir.is_dir(), "Log path should be a directory"


def test_initialize_crea_file_log(temp_log_dir):
    """Test that initialize() creates the log file."""
    log_dir, log_file = temp_log_dir
    
    assert not log_file.exists(), "Log file should not exist before initialization"
    
    GameLogger.initialize(debug_mode=False)
    
    assert log_file.exists(), "Log file should be created by initialize()"
    assert log_file.is_file(), "Log path should be a file"


def test_get_instance_senza_initialize_lancia_errore():
    """Test that get_instance() raises RuntimeError if not initialized."""
    with pytest.raises(RuntimeError, match="GameLogger non inizializzato"):
        GameLogger.get_instance()


def test_initialize_doppio_non_duplica_handler(temp_log_dir):
    """Test that calling initialize() twice doesn't duplicate handlers."""
    log_dir, log_file = temp_log_dir
    
    GameLogger.initialize(debug_mode=False)
    logger1 = GameLogger.get_instance()
    handler_count_1 = len(logger1.handlers)
    
    # Initialize again - should not add duplicate handlers
    GameLogger.initialize(debug_mode=False)
    logger2 = GameLogger.get_instance()
    handler_count_2 = len(logger2.handlers)
    
    assert handler_count_2 == handler_count_1, "Handler count should not increase on second initialize()"
    assert logger1 is logger2, "Should return the same logger instance"


def test_modalita_normale_livello_info(temp_log_dir):
    """Test that normal mode (debug_mode=False) sets INFO level."""
    log_dir, log_file = temp_log_dir
    
    GameLogger.initialize(debug_mode=False)
    logger = GameLogger.get_instance()
    
    assert logger.level == logging.INFO, "Logger level should be INFO in normal mode"


def test_modalita_debug_livello_debug(temp_log_dir):
    """Test that debug mode (debug_mode=True) sets DEBUG level."""
    log_dir, log_file = temp_log_dir
    
    GameLogger.initialize(debug_mode=True)
    logger = GameLogger.get_instance()
    
    assert logger.level == logging.DEBUG, "Logger level should be DEBUG in debug mode"


def test_marcatori_sessione_nel_file(temp_log_dir):
    """Test that session markers (AVVIATA/CHIUSA) are written to the log file."""
    log_dir, log_file = temp_log_dir
    
    GameLogger.initialize(debug_mode=False)
    GameLogger.shutdown()
    
    log_content = log_file.read_text(encoding="utf-8")
    
    assert "SESSIONE AVVIATA:" in log_content, "Session start marker should be in log"
    assert "SESSIONE CHIUSA:" in log_content, "Session close marker should be in log"
    assert "----" in log_content, "Separator should be in log"


def test_shutdown_scrive_marcatore_chiusura(temp_log_dir):
    """Test that shutdown() writes the closing session marker."""
    log_dir, log_file = temp_log_dir
    
    GameLogger.initialize(debug_mode=False)
    logger = GameLogger.get_instance()
    logger.info("Test message")
    
    GameLogger.shutdown()
    
    log_content = log_file.read_text(encoding="utf-8")
    
    assert "SESSIONE CHIUSA:" in log_content, "Closing marker should be written by shutdown()"
    assert "Sistema di logging in chiusura." in log_content, "Shutdown message should be in log"
