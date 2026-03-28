"""Unit tests for bingo_game.logging.GameLogger (Phase 1).

Tests the GameLogger singleton initialization, file creation,
session markers, and debug/info level configuration.
"""
import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bingo_game.logging.game_logger import GameLogger, _LOG_DIR, _LOG_FILE, _LOGGER_NAME


class TestGameLogger(unittest.TestCase):
    """Test unittest per GameLogger con cleanup esplicito."""

    LOGGER_NAMES = [
        "tombola_stark",
        "tombola_stark.game",
        "tombola_stark.prizes",
        "tombola_stark.system",
        "tombola_stark.errors",
    ]

    def setUp(self) -> None:
        self._reset_logger_state()
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.log_dir = Path(self._tmpdir.name) / "test_logs"
        self.log_file = self.log_dir / "tombola_stark.log"

        patch_log_dir = patch("bingo_game.logging.game_logger._LOG_DIR", self.log_dir)
        patch_log_file = patch("bingo_game.logging.game_logger._LOG_FILE", self.log_file)
        patch_log_dir.start()
        patch_log_file.start()
        self.addCleanup(patch_log_dir.stop)
        self.addCleanup(patch_log_file.stop)
        self.addCleanup(self._cleanup_logger)

    def _reset_logger_state(self) -> None:
        GameLogger._initialized = False
        GameLogger._instance = None
        for name in self.LOGGER_NAMES:
            logging.getLogger(name).handlers.clear()

    def _cleanup_logger(self) -> None:
        if GameLogger._initialized:
            GameLogger.shutdown()
        self._reset_logger_state()

    def test_initialize_crea_cartella_log(self) -> None:
        """Test that initialize() creates the log directory if it doesn't exist."""
        self.assertFalse(self.log_dir.exists(), "Log directory should not exist before initialization")

        GameLogger.initialize(debug_mode=False)

        self.assertTrue(self.log_dir.exists(), "Log directory should be created by initialize()")
        self.assertTrue(self.log_dir.is_dir(), "Log path should be a directory")


    def test_initialize_crea_file_log(self) -> None:
        """Test that initialize() creates the log file."""
        self.assertFalse(self.log_file.exists(), "Log file should not exist before initialization")

        GameLogger.initialize(debug_mode=False)

        self.assertTrue(self.log_file.exists(), "Log file should be created by initialize()")
        self.assertTrue(self.log_file.is_file(), "Log path should be a file")


    def test_get_instance_senza_initialize_lancia_errore(self) -> None:
        """Test that get_instance() raises RuntimeError if not initialized."""
        with self.assertRaisesRegex(RuntimeError, "GameLogger non inizializzato"):
            GameLogger.get_instance()


    def test_initialize_doppio_non_duplica_handler(self) -> None:
        """Test that calling initialize() twice doesn't duplicate handlers."""
        GameLogger.initialize(debug_mode=False)
        logger1 = GameLogger.get_instance()
        handler_count_1 = len(logger1.handlers)

        GameLogger.initialize(debug_mode=False)
        logger2 = GameLogger.get_instance()
        handler_count_2 = len(logger2.handlers)

        self.assertEqual(handler_count_2, handler_count_1, "Handler count should not increase on second initialize()")
        self.assertIs(logger1, logger2, "Should return the same logger instance")


    def test_modalita_normale_livello_info(self) -> None:
        """Test that normal mode (debug_mode=False) sets INFO level."""
        GameLogger.initialize(debug_mode=False)
        logger = GameLogger.get_instance()
        self.assertEqual(logger.level, logging.INFO, "Logger level should be INFO in normal mode")


    def test_modalita_debug_livello_debug(self) -> None:
        """Test that debug mode (debug_mode=True) sets DEBUG level."""
        GameLogger.initialize(debug_mode=True)
        logger = GameLogger.get_instance()
        self.assertEqual(logger.level, logging.DEBUG, "Logger level should be DEBUG in debug mode")


    def test_marcatori_sessione_nel_file(self) -> None:
        """Test that session markers (AVVIATA/CHIUSA) are written to the log file."""
        GameLogger.initialize(debug_mode=False)
        GameLogger.shutdown()

        log_content = self.log_file.read_text(encoding="utf-8")

        self.assertIn("SESSIONE AVVIATA:", log_content, "Session start marker should be in log")
        self.assertIn("SESSIONE CHIUSA:", log_content, "Session close marker should be in log")
        self.assertIn("----", log_content, "Separator should be in log")


    def test_shutdown_scrive_marcatore_chiusura(self) -> None:
        """Test that shutdown() writes the closing session marker."""
        GameLogger.initialize(debug_mode=False)
        logger = GameLogger.get_instance()
        logger.info("Test message")

        GameLogger.shutdown()

        log_content = self.log_file.read_text(encoding="utf-8")

        self.assertIn("SESSIONE CHIUSA:", log_content, "Closing marker should be written by shutdown()")
        self.assertIn("Sistema di logging in chiusura.", log_content, "Shutdown message should be in log")


if __name__ == "__main__":
    unittest.main()
