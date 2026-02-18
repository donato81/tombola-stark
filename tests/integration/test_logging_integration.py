"""Integration tests for GameLogger with game_controller (Phase 1).

Tests the logging system integrated with game_controller functions
to verify that key game events are logged correctly.
"""
from pathlib import Path
import pytest

from bingo_game.logging.game_logger import GameLogger
from bingo_game.game_controller import (
    crea_partita_standard,
    avvia_partita_sicura,
    esegui_turno_sicuro,
)


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


def test_creazione_partita_loggata(temp_log_dir):
    """Test that creating a game logs the creation event."""
    log_dir, log_file = temp_log_dir
    
    GameLogger.initialize(debug_mode=False)
    
    # Create a standard game
    partita = crea_partita_standard(
        nome_giocatore_umano="TestPlayer",
        num_cartelle_umano=2,
        num_bot=2
    )
    
    GameLogger.shutdown()
    
    log_content = log_file.read_text(encoding="utf-8")
    
    # Verify game creation is logged
    assert "Partita creata" in log_content, "Game creation should be logged"
    assert "TestPlayer" in log_content, "Player name should be in log"
    assert "cartelle_umano=2" in log_content or "cartelle" in log_content, "Card count should be logged"
    assert "bot=2" in log_content, "Bot count should be logged"


def test_avvio_partita_loggato(temp_log_dir):
    """Test that starting a game logs the start event."""
    log_dir, log_file = temp_log_dir
    
    GameLogger.initialize(debug_mode=False)
    
    # Create and start a game
    partita = crea_partita_standard(
        nome_giocatore_umano="TestPlayer",
        num_cartelle_umano=1,
        num_bot=1
    )
    
    success = avvia_partita_sicura(partita)
    
    GameLogger.shutdown()
    
    assert success, "Game should start successfully"
    
    log_content = log_file.read_text(encoding="utf-8")
    
    # Verify game start is logged
    assert "Partita avviata" in log_content or "avviata con successo" in log_content, \
        "Game start should be logged"


def test_turni_loggati_in_debug(temp_log_dir):
    """Test that turns are logged in DEBUG mode but not in INFO mode."""
    log_dir, log_file = temp_log_dir
    
    # First test: INFO mode (turns should not be logged)
    GameLogger.initialize(debug_mode=False)
    
    partita = crea_partita_standard(
        nome_giocatore_umano="TestPlayer",
        num_cartelle_umano=1,
        num_bot=1
    )
    avvia_partita_sicura(partita)
    
    # Execute a few turns
    for _ in range(3):
        result = esegui_turno_sicuro(partita)
        if not result:
            break
    
    GameLogger.shutdown()
    
    log_content_info = log_file.read_text(encoding="utf-8")
    
    # In INFO mode, turn details should NOT be logged
    # The "Turno eseguito" is logged at DEBUG level
    assert "Turno eseguito" not in log_content_info, \
        "Turn execution should NOT be logged in INFO mode"
    
    # Reset for DEBUG mode test
    GameLogger._initialized = False
    log_file.unlink()  # Remove old log file
    
    # Second test: DEBUG mode (turns SHOULD be logged)
    GameLogger.initialize(debug_mode=True)
    
    partita2 = crea_partita_standard(
        nome_giocatore_umano="TestPlayer",
        num_cartelle_umano=1,
        num_bot=1
    )
    avvia_partita_sicura(partita2)
    
    # Execute a few turns
    for _ in range(3):
        result = esegui_turno_sicuro(partita2)
        if not result:
            break
    
    GameLogger.shutdown()
    
    log_content_debug = log_file.read_text(encoding="utf-8")
    
    # In DEBUG mode, turn details SHOULD be logged
    assert "Turno eseguito" in log_content_debug, \
        "Turn execution SHOULD be logged in DEBUG mode"
