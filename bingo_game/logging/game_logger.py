"""Sistema di logging centralizzato per Tombola Stark.

Fornisce un Singleton GameLogger che scrive su un file di testo cumulativo
con flush immediato (leggibile in tempo reale) e marcatori di sessione.

Version:
    v0.4.0: Introduzione del sistema di logging centralizzato
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path


# Formato riga: QUANDO | QUANTO importante | CHI | COSA
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_LOG_DIR = Path("logs")
_LOG_FILE = _LOG_DIR / "tombola_stark.log"
_LOGGER_NAME = "tombola_stark"
_SESSION_SEPARATOR = "-" * 60


class GameLogger:
    """Singleton per il sistema di logging di Tombola Stark.

    Scrive su un file cumulativo in append con flush immediato.
    Supporta modalità normale (INFO+) e dettagliata (DEBUG+).

    Example:
        >>> GameLogger.initialize(debug_mode=False)
        >>> logger = GameLogger.get_instance()
        >>> logger.info("Partita avviata")

    Version:
        v0.4.0: Prima implementazione
    """

    _instance: GameLogger | None = None
    _initialized: bool = False

    def __init__(self) -> None:
        """Non chiamare direttamente — usare initialize() e get_instance()."""
        if GameLogger._initialized:
            raise RuntimeError("Usare GameLogger.get_instance()")

    @classmethod
    def initialize(cls, debug_mode: bool = False) -> None:
        """Inizializza il logger. Chiamare una sola volta all'avvio dell'applicazione.

        Args:
            debug_mode: Se True, imposta il livello a DEBUG (modalità dettagliata).
                        Se False (default), imposta il livello a INFO.

        Version:
            v0.4.0: Prima implementazione
        """
        if cls._initialized:
            return

        _LOG_DIR.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(_LOGGER_NAME)
        level = logging.DEBUG if debug_mode else logging.INFO
        logger.setLevel(level)

        class FlushingFileHandler(logging.FileHandler):
            def emit(self, record: logging.LogRecord) -> None:
                super().emit(record)
                self.flush()

        logger.handlers.clear()
        flushing_handler = FlushingFileHandler(
            _LOG_FILE, mode="a", encoding="utf-8", delay=False
        )
        flushing_handler.setLevel(level)
        formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
        flushing_handler.setFormatter(formatter)
        logger.addHandler(flushing_handler)
        logger.propagate = False

        cls._initialized = True

        cls._write_session_marker(logger, "AVVIATA")
        mode_label = "DEBUG (modalità dettagliata)" if debug_mode else "INFO (modalità normale)"
        logger.info("Sistema di logging inizializzato — livello: %s", mode_label)

    @classmethod
    def get_instance(cls) -> logging.Logger:
        """Restituisce il logger configurato.

        Raises:
            RuntimeError: Se initialize() non è stato ancora chiamato.

        Version:
            v0.4.0: Prima implementazione
        """
        if not cls._initialized:
            raise RuntimeError(
                "GameLogger non inizializzato. Chiamare GameLogger.initialize() in main.py."
            )
        return logging.getLogger(_LOGGER_NAME)

    @classmethod
    def shutdown(cls) -> None:
        """Scrive il marcatore di chiusura sessione e chiude tutti gli handler.

        Version:
            v0.4.0: Prima implementazione
        """
        if not cls._initialized:
            return
        logger = logging.getLogger(_LOGGER_NAME)
        logger.info("Sistema di logging in chiusura.")
        cls._write_session_marker(logger, "CHIUSA")
        logging.shutdown()
        cls._initialized = False

    @staticmethod
    def _write_session_marker(logger: logging.Logger, tipo: str) -> None:
        """Scrive un marcatore visivo di confine sessione nel file di log.

        Args:
            logger: Il logger su cui scrivere.
            tipo: "AVVIATA" o "CHIUSA".

        Version:
            v0.4.0: Prima implementazione
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_sep = logging.LogRecord(
            name=logger.name, level=logging.INFO, pathname="",
            lineno=0, msg=_SESSION_SEPARATOR, args=(), exc_info=None,
        )
        record_marker = logging.LogRecord(
            name=logger.name, level=logging.INFO, pathname="",
            lineno=0, msg=f"SESSIONE {tipo}: {timestamp}", args=(), exc_info=None,
        )
        for handler in logger.handlers:
            handler.emit(record_sep)
            handler.emit(record_marker)
            handler.emit(record_sep)
