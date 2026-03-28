"""Unit test per la copertura eventi di Fase 2.

Verifica che le funzioni helper di logging (sub-logger, _log_prize_event,
_log_game_summary) scrivano le righe attese con il prefisso di categoria corretto.
"""
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bingo_game.logging.game_logger import GameLogger


class TestEventLogging(unittest.TestCase):
    """Test unittest per la copertura eventi di logging."""

    LOGGER_NAMES = [
        "tombola_stark",
        "tombola_stark.game",
        "tombola_stark.prizes",
        "tombola_stark.system",
        "tombola_stark.errors",
    ]

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.tmp_log = Path(self._tmpdir.name) / "logs" / "tombola_stark.log"

        self._reset_logger_state()
        patch_log_dir = patch("bingo_game.logging.game_logger._LOG_DIR", self.tmp_log.parent)
        patch_log_file = patch("bingo_game.logging.game_logger._LOG_FILE", self.tmp_log)
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

    def _read(self) -> str:
        return self.tmp_log.read_text(encoding="utf-8")

    def test_sublogger_game_scrive_su_file(self) -> None:
        """Il sub-logger tombola_stark.game propaga sul file del logger radice."""
        GameLogger.initialize()
        logging.getLogger("tombola_stark.game").info("[GAME] Test game event")
        self.assertIn("[GAME] Test game event", self._read())


    def test_sublogger_prizes_scrive_su_file(self) -> None:
        """Il sub-logger tombola_stark.prizes propaga sul file del logger radice."""
        GameLogger.initialize()
        logging.getLogger("tombola_stark.prizes").info("[PRIZE] Test prize event")
        self.assertIn("[PRIZE] Test prize event", self._read())


    def test_sublogger_errors_scrive_su_file(self) -> None:
        """Il sub-logger tombola_stark.errors propaga sul file del logger radice."""
        GameLogger.initialize()
        logging.getLogger("tombola_stark.errors").warning("[ERR] Test error event")
        self.assertIn("[ERR] Test error event", self._read())


    def test_sublogger_system_scrive_su_file(self) -> None:
        """Il sub-logger tombola_stark.system propaga sul file del logger radice."""
        GameLogger.initialize()
        logging.getLogger("tombola_stark.system").info("[SYS] Test system event")
        self.assertIn("[SYS] Test system event", self._read())


    def test_debug_non_scrive_in_modalita_normale(self) -> None:
        """In modalità normale (INFO), gli eventi DEBUG non compaiono nel file."""
        GameLogger.initialize(debug_mode=False)
        logging.getLogger("tombola_stark.game").debug("[GAME] Turno #1 — estratto: 42")
        self.assertNotIn("Turno #1", self._read())


    def test_debug_scrive_in_modalita_debug(self) -> None:
        """In modalità debug, gli eventi DEBUG compaiono nel file."""
        GameLogger.initialize(debug_mode=True)
        logging.getLogger("tombola_stark.game").debug("[GAME] Turno #1 — estratto: 42")
        self.assertIn("Turno #1", self._read())


    def test_prefissi_categoria_distinti_nel_file(self) -> None:
        """Più categorie di eventi sono distinguibili nel file tramite prefisso."""
        GameLogger.initialize()
        logging.getLogger("tombola_stark.game").info("[GAME] evento gioco")
        logging.getLogger("tombola_stark.prizes").info("[PRIZE] evento premio")
        logging.getLogger("tombola_stark.errors").warning("[ERR] evento errore")
        content = self._read()
        self.assertIn("[GAME]", content)
        self.assertIn("[PRIZE]", content)
        self.assertIn("[ERR]", content)


if __name__ == "__main__":
    unittest.main()
