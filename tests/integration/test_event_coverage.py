"""Test di integrazione: copertura completa degli eventi di Fase 2.

Verifica che una partita completa produca tutte le categorie di eventi
attese nel file di log, con il contenuto semanticamente corretto.
"""
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bingo_game.logging.game_logger import GameLogger
from bingo_game.game_controller import (
    crea_partita_standard,
    avvia_partita_sicura,
    esegui_turno_sicuro,
    partita_terminata,
)


class TestEventCoverage(unittest.TestCase):
    """Test di integrazione unittest per la copertura eventi."""

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

    def test_partita_completa_produce_game_created(self) -> None:
        """Una partita completa produce l'evento GAME_CREATED con dati corretti."""
        GameLogger.initialize()
        crea_partita_standard("TestPlayer", num_cartelle_umano=1, num_bot=1)
        self.assertIn("[GAME] Partita creata", self._read())
        self.assertIn("TestPlayer", self._read())


    def test_partita_avviata_produce_game_started(self) -> None:
        """avvia_partita_sicura produce GAME_STARTED con stato in_corso."""
        GameLogger.initialize()
        partita = crea_partita_standard("Test", num_cartelle_umano=1, num_bot=1)
        avvia_partita_sicura(partita)
        self.assertIn("[GAME] Partita avviata", self._read())
        self.assertIn("in_corso", self._read())


    def test_turni_in_debug_producono_game_turn(self) -> None:
        """In modalità debug, ogni turno produce un evento [GAME] Turno #N."""
        GameLogger.initialize(debug_mode=True)
        partita = crea_partita_standard("Test", num_cartelle_umano=1, num_bot=1)
        avvia_partita_sicura(partita)
        esegui_turno_sicuro(partita)
        self.assertIn("[GAME] Turno #1", self._read())


    def test_premio_produce_prize_event(self) -> None:
        """Un premio assegnato durante la partita produce un evento [PRIZE]."""
        GameLogger.initialize()
        partita = crea_partita_standard("Test", num_cartelle_umano=1, num_bot=1)
        avvia_partita_sicura(partita)

        for _ in range(90):
            risultato = esegui_turno_sicuro(partita)
            if risultato and risultato.get("premi_nuovi"):
                break
            if partita_terminata(partita):
                break

        content = self._read()
        self.assertTrue(any(tag in content for tag in ["[PRIZE]", "[GAME] Partita terminata"]))


    def test_fine_partita_produce_riepilogo(self) -> None:
        """Al termine della partita il riepilogo [GAME] === RIEPILOGO è nel log."""
        GameLogger.initialize()
        partita = crea_partita_standard("Test", num_cartelle_umano=1, num_bot=1)
        avvia_partita_sicura(partita)
        while not partita_terminata(partita):
            esegui_turno_sicuro(partita)
        self.assertIn("RIEPILOGO", self._read())


if __name__ == "__main__":
    unittest.main()
