"""Integration tests for GameLogger with game_controller (Phase 1).

Tests the logging system integrated with game_controller functions
to verify that key game events are logged correctly.
"""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bingo_game.logging.game_logger import GameLogger
from bingo_game.game_controller import (
    crea_partita_standard,
    avvia_partita_sicura,
    esegui_turno_sicuro,
)


class TestLoggingIntegration(unittest.TestCase):
    """Integration tests unittest per GameLogger e game_controller."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.log_dir = Path(self._tmpdir.name) / "test_logs"
        self.log_file = self.log_dir / "tombola_stark.log"

        GameLogger._initialized = False
        GameLogger._instance = None
        patch_log_dir = patch("bingo_game.logging.game_logger._LOG_DIR", self.log_dir)
        patch_log_file = patch("bingo_game.logging.game_logger._LOG_FILE", self.log_file)
        patch_log_dir.start()
        patch_log_file.start()
        self.addCleanup(patch_log_dir.stop)
        self.addCleanup(patch_log_file.stop)
        self.addCleanup(self._cleanup_logger)

    def _cleanup_logger(self) -> None:
        if GameLogger._initialized:
            GameLogger.shutdown()
        GameLogger._initialized = False
        GameLogger._instance = None

    def test_creazione_partita_loggata(self) -> None:
        """Test that creating a game logs the creation event."""
        GameLogger.initialize(debug_mode=False)

        crea_partita_standard(
            nome_giocatore_umano="TestPlayer",
            num_cartelle_umano=2,
            num_bot=2,
        )

        GameLogger.shutdown()

        log_content = self.log_file.read_text(encoding="utf-8")

        self.assertIn("Partita creata", log_content, "Game creation should be logged")
        self.assertIn("TestPlayer", log_content, "Player name should be in log")
        self.assertTrue(
            "cartelle_umano=2" in log_content or "cartelle" in log_content,
            "Card count should be logged",
        )
        self.assertIn("bot=2", log_content, "Bot count should be logged")


    def test_avvio_partita_loggato(self) -> None:
        """Test that starting a game logs the start event."""
        GameLogger.initialize(debug_mode=False)

        partita = crea_partita_standard(
            nome_giocatore_umano="TestPlayer",
            num_cartelle_umano=1,
            num_bot=1,
        )

        success = avvia_partita_sicura(partita)

        GameLogger.shutdown()

        self.assertTrue(success, "Game should start successfully")

        log_content = self.log_file.read_text(encoding="utf-8")
        self.assertTrue(
            "Partita avviata" in log_content or "avviata con successo" in log_content,
            "Game start should be logged",
        )


    def test_turni_loggati_in_debug(self) -> None:
        """Test that turns are logged in DEBUG mode but not in INFO mode."""
        GameLogger.initialize(debug_mode=False)

        partita = crea_partita_standard(
            nome_giocatore_umano="TestPlayer",
            num_cartelle_umano=1,
            num_bot=1,
        )
        avvia_partita_sicura(partita)

        for _ in range(3):
            result = esegui_turno_sicuro(partita)
            if not result:
                break

        GameLogger.shutdown()

        log_content_info = self.log_file.read_text(encoding="utf-8")
        self.assertNotIn("[GAME] Turno", log_content_info, "Turn execution should NOT be logged in INFO mode")

        GameLogger._initialized = False
        self.log_file.unlink()

        GameLogger.initialize(debug_mode=True)

        partita_debug = crea_partita_standard(
            nome_giocatore_umano="TestPlayer",
            num_cartelle_umano=1,
            num_bot=1,
        )
        avvia_partita_sicura(partita_debug)

        for _ in range(3):
            result = esegui_turno_sicuro(partita_debug)
            if not result:
                break

        GameLogger.shutdown()

        log_content_debug = self.log_file.read_text(encoding="utf-8")
        self.assertIn("[GAME] Turno #", log_content_debug, "Turn execution SHOULD be logged in DEBUG mode")


if __name__ == "__main__":
    unittest.main()
