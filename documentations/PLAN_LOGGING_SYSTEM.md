# 📋 Piano di Implementazione — Sistema di Logging Centralizzato

> **Basato su**: `DESIGN_LOGGING_SYSTEM.md` (stato: DESIGN FREEZE ✅)  
> Tutte le decisioni di design sono chiuse. Questo documento traduce quelle decisioni in codice.

---

## 📊 Executive Summary

**Tipo**: FEATURE  
**Priorità**: 🟠 ALTA  
**Stato**: READY  
**Branch**: `feat/logging-system`  
**Versione Target**: `v0.4.0`  
**Data Creazione**: 2026-02-18  
**Autore**: AI Assistant + donato81  
**Effort Stimato**: 4–5 ore totali (3 ore implementazione + 1–2 ore review/testing)  
**Commits Previsti**: 5 commit atomici

---

### Problema/Obiettivo

Tombola Stark non ha nessun meccanismo per tracciare cosa accade durante una sessione di gioco. Se qualcosa va storto, non c'è modo di capire quando, dove e perché. L'obiettivo è introdurre un **sistema di logging centralizzato** che scriva un diario automatico degli eventi rilevanti: silenzioso per l'utente, indispensabile per lo sviluppatore.

---

### Soluzione Proposta

Introdurre un modulo `bingo_game/logging/` con un `GameLogger` singleton che wrappa il modulo standard `logging` di Python. Il logger si aggancia ai punti chiave dell'architettura esistente (controller, dominio, eventi) tramite chiamate esplicite — senza modificare le interfacce pubbliche dei moduli esistenti. Il file di log è cumulativo, con flush immediato dopo ogni scrittura e marcatori di sessione per separare le esecuzioni.

**Scelta tecnica chiave**: si usa `logging.FileHandler` con `delay=False` e `mode='a'` (append), con un `StreamHandler` configurato con `flush=True` per garantire la leggibilità in tempo reale. La modalità `--debug` è gestita via `argparse` in `main.py`.

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---|---|---|
| **Severità** | MEDIA | Nessuna funzionalità di gioco cambia |
| **Scope** | 6–8 file modificati o nuovi | Vedi File Structure |
| **Rischio regressione** | BASSO | Il logger non interferisce mai col flusso di gioco |
| **Breaking changes** | NO | Nessuna API pubblica cambia |
| **Testing** | MEDIO | Unit + integration su logger e agganci |

---

## 🎯 Requisiti Funzionali

### RF-01: Logger Singleton Inizializzato all'Avvio

**Comportamento Atteso**:
1. L'utente avvia l'applicazione (`python main.py` oppure `python main.py --debug`)
2. Il sistema crea automaticamente la cartella `logs/` se non esiste
3. Il `GameLogger` viene inizializzato e scrive il marcatore di avvio sessione nel file `logs/tombola_stark.log`
4. Tutte le parti del gioco possono ora chiamare `GameLogger.get_instance()` per scrivere nel diario

**File Coinvolti**:
- `bingo_game/logging/game_logger.py` — DA CREARE 🆕
- `bingo_game/logging/__init__.py` — DA CREARE 🆕
- `main.py` — DA MODIFICARE ⚙️

---

### RF-02: Aggancio al Controller (Punto Principale)

**Comportamento Atteso**:
1. `crea_partita_standard()` → log INFO: partita creata con N giocatori
2. `avvia_partita_sicura()` → log INFO: partita avviata / log WARNING: fallita per eccezione specifica
3. `esegui_turno_sicuro()` → log DEBUG (solo in modalità dettagliata): numero estratto, premi rilevati
4. `esegui_turno_sicuro()` in caso di eccezione → log WARNING: anomalia intercettata con dettaglio
5. Fine partita → log INFO: partita terminata con riepilogo essenziale

**File Coinvolti**:
- `bingo_game/game_controller.py` — DA MODIFICARE ⚙️

---

### RF-03: Aggancio alla Chiusura dell'Applicazione

**Comportamento Atteso**:
1. L'utente chiude l'applicazione
2. Il sistema scrive il marcatore di chiusura sessione con timestamp
3. Il file handler viene chiuso correttamente (nessun dato perso nel buffer)

**File Coinvolti**:
- `main.py` — DA MODIFICARE ⚙️
- `bingo_game/logging/game_logger.py` — shutdown() method

---

### RF-04: Modalità Dettagliata via Flag `--debug`

**Comportamento Atteso**:
1. Avvio normale (`python main.py`) → solo eventi INFO e WARNING nel log
2. Avvio debug (`python main.py --debug`) → anche tutti i DEBUG nel log (passaggi interni, ogni turno)
3. Il flag non ha nessun effetto sull'interfaccia utente o sul comportamento di gioco

**File Coinvolti**:
- `main.py` — DA MODIFICARE ⚙️

---

### RF-05: Leggibilità in Tempo Reale

**Comportamento Atteso**:
1. Lo sviluppatore apre `logs/tombola_stark.log` con qualsiasi editor mentre il gioco è in esecuzione
2. Ogni nuova riga è visibile immediatamente, senza riavviare il gioco o chiudere l'editor
3. Nessun evento rimane in buffer di sistema in attesa dello shutdown

**Implementazione**: `FileHandler` con `delay=False` + chiamata esplicita a `handler.flush()` dopo ogni `logger.log()`, oppure configurazione `logging` con `stream` dotato di `flush` automatico.

**File Coinvolti**:
- `bingo_game/logging/game_logger.py` — Configurazione handler

---

### RF-06: Il Log Non Entra nel Repository

**Comportamento Atteso**:
1. La cartella `logs/` è elencata in `.gitignore`
2. Nessun file `.log` viene mai committato

**File Coinvolti**:
- `.gitignore` — DA MODIFICARE ⚙️

---

## 🏗️ Architettura

### Posizione nell'Architettura a Livelli

Il logger è un'**infrastruttura trasversale** (cross-cutting concern): non appartiene a nessuno dei tre livelli Dominio → Controller → Interfaccia, ma è accessibile da tutti. Il pattern scelto è **Singleton** per garantire che tutti i moduli scrivano sullo stesso handler senza passarsi l'istanza.

```
┌─────────────────────────────────────────────────────────────┐
│          LIVELLO INTERFACCIA (futuro)                        │
│  bingo_game/ui/  → chiama GameLogger per azioni UI/TTS      │
└─────────────────────────────────────────────────────────────┘
                      ↓ dipende da
┌─────────────────────────────────────────────────────────────┐
│          LIVELLO CONTROLLER                                  │
│  game_controller.py → chiama GameLogger ad ogni operazione  │
└─────────────────────────────────────────────────────────────┘
                      ↓ dipende da
┌─────────────────────────────────────────────────────────────┐
│          LIVELLO DOMINIO                                     │
│  ← Il dominio NON chiama il logger direttamente             │
│    (mantiene zero dipendenze esterne)                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│          INFRASTRUTTURA TRASVERSALE                          │
│  bingo_game/logging/game_logger.py  (Singleton)             │
│  → accessibile da Controller e Interfaccia                   │
│  → scrive su logs/tombola_stark.log (append + flush)        │
│  → NON accessibile dal Dominio (regola architetturale)      │
└─────────────────────────────────────────────────────────────┘
```

### Regola Architetturale Importante

> **Il Dominio (`bingo_game/` root, `players/`, `events/`, `exceptions/`) NON chiama mai il logger.**  
> Il Dominio rimane con zero dipendenze esterne come da ADR-001 e ADR-003.  
> Il Controller è il punto di aggancio principale, perché intercetta già tutti gli eventi rilevanti.

### File Structure

```
bingo_game/
├── logging/                          # NEW — modulo logger
│   ├── __init__.py                   # NEW: espone GameLogger
│   └── game_logger.py                # NEW: Singleton logger + configurazione
├── game_controller.py                # MODIFIED: aggancio logging ai metodi *_sicuro()
└── ...

main.py                               # MODIFIED: init logger, argparse --debug, shutdown
.gitignore                            # MODIFIED: aggiunta logs/

logs/                                 # RUNTIME ONLY — non nel repository
└── tombola_stark.log                 # Diario cumulativo di tutte le sessioni

tests/
├── unit/
│   └── test_game_logger.py           # NEW: 8 unit test
└── integration/
    └── test_logging_integration.py   # NEW: 3 integration test

documentations/
├── DESIGN_LOGGING_SYSTEM.md          # Design freeze (già esistente)
└── PLAN_LOGGING_SYSTEM.md            # QUESTO FILE
```

---

## 📝 Piano di Implementazione

---

### COMMIT 1: Struttura Base del Logger

**Priorità**: 🔴 CRITICA (tutto dipende da questo)  
**File Nuovi**: `bingo_game/logging/__init__.py`, `bingo_game/logging/game_logger.py`

#### Codice Nuovo — `bingo_game/logging/game_logger.py`

```python
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

        Crea la cartella logs/ se non esiste, configura FileHandler con append
        e flush immediato, scrive il marcatore di avvio sessione.

        Args:
            debug_mode: Se True, imposta il livello a DEBUG (modalità dettagliata).
                        Se False (default), imposta il livello a INFO.

        Version:
            v0.4.0: Prima implementazione
        """
        if cls._initialized:
            return

        # Crea cartella logs/ se non esiste
        _LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Configura il logger radice per il progetto
        logger = logging.getLogger(_LOGGER_NAME)
        level = logging.DEBUG if debug_mode else logging.INFO
        logger.setLevel(level)

        # FileHandler: append + flush immediato
        file_handler = logging.FileHandler(
            _LOG_FILE, mode="a", encoding="utf-8", delay=False
        )
        file_handler.setLevel(level)
        formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
        file_handler.setFormatter(formatter)

        # Wrapper per garantire flush dopo ogni scrittura
        class FlushingFileHandler(logging.FileHandler):
            def emit(self, record: logging.LogRecord) -> None:
                super().emit(record)
                self.flush()

        logger.handlers.clear()
        flushing_handler = FlushingFileHandler(
            _LOG_FILE, mode="a", encoding="utf-8", delay=False
        )
        flushing_handler.setLevel(level)
        flushing_handler.setFormatter(formatter)
        logger.addHandler(flushing_handler)
        logger.propagate = False

        cls._initialized = True

        # Marcatore di avvio sessione
        cls._write_session_marker(logger, "AVVIATA")
        mode_label = "DEBUG (modalità dettagliata)" if debug_mode else "INFO (modalità normale)"
        logger.info("Sistema di logging inizializzato — livello: %s", mode_label)

    @classmethod
    def get_instance(cls) -> logging.Logger:
        """Restituisce il logger configurato.

        Returns:
            logging.Logger: Il logger del progetto, pronto per l'uso.

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

        Chiamare prima dell'uscita dell'applicazione per garantire che
        nessun evento resti nel buffer.

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
        # Scriviamo direttamente sugli handler per aggirare il formatter
        record_sep = logging.LogRecord(
            name=logger.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=_SESSION_SEPARATOR,
            args=(),
            exc_info=None,
        )
        record_marker = logging.LogRecord(
            name=logger.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"SESSIONE {tipo}: {timestamp}",
            args=(),
            exc_info=None,
        )
        for handler in logger.handlers:
            handler.emit(record_sep)
            handler.emit(record_marker)
            handler.emit(record_sep)
```

#### Codice Nuovo — `bingo_game/logging/__init__.py`

```python
"""Modulo di logging centralizzato per Tombola Stark.

Espone GameLogger come punto di accesso unico al sistema di logging.
"""
from bingo_game.logging.game_logger import GameLogger

__all__ = ["GameLogger"]
```

#### Rationale

**Perché Singleton e non istanza passata come parametro?**  
Il progetto usa già un pattern di funzioni top-level nel controller (`game_controller.py`) senza dependency injection. Un Singleton è coerente con questo stile e non richiede modifiche alle firme di nessuna funzione esistente.

**Perché `FlushingFileHandler` custom invece di `flush()` esplicito?**  
Sovrascrivere `emit()` garantisce il flush anche in caso di logging da librerie terze future. È la soluzione più robusta e non aggiunge overhead significativo per un'app monoutente.

**Perché il Dominio non chiama mai il logger?**  
Il Dominio ha zero dipendenze esterne (ADR-001, ADR-003 in `ARCHITECTURE.md`). Il logger è infrastruttura: il Controller è già il livello deputato a intercettare tutto ciò che accade nel dominio.

#### Commit Message

```
feat(logging): add GameLogger singleton with cumulative file and real-time flush

- New module bingo_game/logging/ with GameLogger class
- Single cumulative file logs/tombola_stark.log (append mode)
- FlushingFileHandler: every log line is flushed to disk immediately
- Session markers (start/end) with timestamps separate sessions in log
- initialize(debug_mode) / get_instance() / shutdown() API

Impact:
- Zero impact on existing game logic or tests
- logs/ directory created automatically on first run

Testing:
- See tests/unit/test_game_logger.py
```

---

### COMMIT 2: Aggiornamento `.gitignore`

**Priorità**: 🔴 CRITICA (deve precedere il primo avvio reale)  
**File**: `.gitignore`

#### Modifica

Aggiungere alla fine del file:

```gitignore
# File di log generati a runtime — artefatti locali, non nel repository
logs/
*.log
```

#### Commit Message

```
chore(gitignore): exclude logs/ directory from version control

- logs/tombola_stark.log is a runtime artifact local to each installation
- Never committed as per DESIGN_LOGGING_SYSTEM.md decision
```

---

### COMMIT 3: Aggancio al Controller

**Priorità**: 🔴 CRITICA (è il punto di raccolta di tutti gli eventi rilevanti)  
**File**: `bingo_game/game_controller.py`

#### Approccio

Aggiungere chiamate `GameLogger.get_instance()` alle funzioni esistenti del controller, **senza modificarne le firme o il comportamento**. Il logger è chiamato **dopo** ogni operazione significativa, mai prima (per non interferire con la logica).

Importante: le chiamate al logger sono wrappate in `try/except Exception` silenzioso, così un errore di scrittura del log non interrompe mai il gioco.

```python
# Pattern di aggancio sicuro da seguire in tutto il controller
def _log_safe(message: str, level: str = "info", *args) -> None:
    """Scrive nel log senza mai propagare eccezioni al chiamante.
    
    Args:
        message: Messaggio da registrare.
        level: Livello logging ('info', 'warning', 'debug', 'error').
        *args: Argomenti per il formato stringa del logger.
        
    Version:
        v0.4.0: Helper interno per logging sicuro nel controller
    """
    try:
        logger = GameLogger.get_instance()
        getattr(logger, level)(message, *args)
    except Exception:  # noqa: BLE001
        pass  # Il logging non deve mai interrompere il gioco
```

#### Punti di Aggancio nel Controller

```python
# crea_partita_standard() — dopo la creazione riuscita
_log_safe(
    "Partita creata: nome=%s, giocatori_umani=%d, bot=%d",
    "info", nome, n_umani, n_bot
)

# avvia_partita_sicura() — avvio OK
_log_safe("Partita avviata con successo.", "info")

# avvia_partita_sicura() — eccezione specifica
_log_safe("Avvio partita fallito: %s", "warning", str(exc))

# esegui_turno_sicuro() — turno OK (solo in DEBUG)
_log_safe(
    "Turno eseguito: numero=%s, premi=%d",
    "debug",
    risultato.get("numero_estratto"),
    len(risultato.get("premi_nuovi", []))
)

# esegui_turno_sicuro() — anomalia intercettata
_log_safe("Anomalia nel turno intercettata: %s", "warning", str(exc))

# partita_terminata() — prima volta che ritorna True
_log_safe("Partita terminata.", "info")
```

#### Commit Message

```
feat(logging): hook GameLogger into game_controller at all key points

- crea_partita_standard: log INFO on success
- avvia_partita_sicura: log INFO on success, WARNING on failure
- esegui_turno_sicuro: log DEBUG per-turn data, WARNING on exception
- partita_terminata: log INFO on game end
- _log_safe() helper: logging errors never propagate to game loop

Impact:
- No change to function signatures or return values
- No impact on existing tests
```

---

### COMMIT 4: Aggancio a `main.py`

**Priorità**: 🔴 CRITICA (senza questo il logger non viene mai inizializzato)  
**File**: `main.py`

#### Codice da Aggiungere a `main.py`

```python
import argparse
from bingo_game.logging import GameLogger

def _parse_args() -> argparse.Namespace:
    """Analizza gli argomenti da riga di comando.
    
    Returns:
        argparse.Namespace: Namespace con i flag rilevati.
        
    Version:
        v0.4.0: Aggiunto --debug flag per modalità dettagliata
    """
    parser = argparse.ArgumentParser(
        description="Tombola Stark — Simulatore tombola italiana accessibile"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Attiva la modalità di logging dettagliata (solo per sviluppatori)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    
    # Inizializza il logger PRIMA di qualsiasi altra operazione
    GameLogger.initialize(debug_mode=args.debug)
    
    try:
        # ... codice esistente del gioco ...
        pass
    finally:
        # Chiude il logger in modo pulito anche in caso di eccezione
        GameLogger.shutdown()


if __name__ == "__main__":
    main()
```

#### Commit Message

```
feat(logging): integrate GameLogger init/shutdown in main.py with --debug flag

- argparse: --debug flag activates DEBUG log level
- GameLogger.initialize() called before any game operation
- GameLogger.shutdown() in finally block: clean close in all exit paths

Impact:
- python main.py       → INFO level log (normal mode)
- python main.py --debug → DEBUG level log (verbose mode)
```

---

### COMMIT 5: Test Suite

**Priorità**: 🟠 ALTA  
**File Nuovi**: `tests/unit/test_game_logger.py`, `tests/integration/test_logging_integration.py`

#### `tests/unit/test_game_logger.py`

```python
"""Unit test per GameLogger.

Verifica il comportamento del singleton in isolamento,
senza richiedere l'ambiente di gioco completo.
"""
import logging
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from bingo_game.logging.game_logger import GameLogger


@pytest.fixture(autouse=True)
def reset_logger():
    """Resetta lo stato del singleton tra un test e l'altro."""
    yield
    GameLogger.shutdown()
    GameLogger._initialized = False
    # Rimuove il logger radice di test dall'ambiente logging
    logger = logging.getLogger("tombola_stark")
    logger.handlers.clear()


@pytest.fixture
def tmp_log_dir(tmp_path, monkeypatch):
    """Redirige i log su una cartella temporanea."""
    import bingo_game.logging.game_logger as gl_module
    monkeypatch.setattr(gl_module, "_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(gl_module, "_LOG_FILE", tmp_path / "logs" / "tombola_stark.log")
    return tmp_path / "logs"


def test_initialize_crea_cartella_log(tmp_log_dir):
    """La cartella logs/ viene creata automaticamente se non esiste."""
    assert not tmp_log_dir.exists()
    GameLogger.initialize()
    assert tmp_log_dir.exists()


def test_initialize_crea_file_log(tmp_log_dir):
    """Il file tombola_stark.log viene creato all'inizializzazione."""
    GameLogger.initialize()
    assert (tmp_log_dir / "tombola_stark.log").exists()


def test_get_instance_senza_initialize_lancia_errore():
    """get_instance() senza initialize() solleva RuntimeError."""
    with pytest.raises(RuntimeError, match="GameLogger non inizializzato"):
        GameLogger.get_instance()


def test_initialize_doppio_non_duplica_handler(tmp_log_dir):
    """Chiamate multiple a initialize() non aggiungono handler duplicati."""
    GameLogger.initialize()
    GameLogger.initialize()  # seconda chiamata — deve essere no-op
    logger = logging.getLogger("tombola_stark")
    assert len(logger.handlers) == 1


def test_modalita_normale_livello_info(tmp_log_dir):
    """In modalità normale, il livello del logger è INFO."""
    GameLogger.initialize(debug_mode=False)
    logger = GameLogger.get_instance()
    assert logger.level == logging.INFO


def test_modalita_debug_livello_debug(tmp_log_dir):
    """In modalità debug, il livello del logger è DEBUG."""
    GameLogger.initialize(debug_mode=True)
    logger = GameLogger.get_instance()
    assert logger.level == logging.DEBUG


def test_marcatori_sessione_nel_file(tmp_log_dir):
    """Il file di log contiene i marcatori di inizio sessione."""
    GameLogger.initialize()
    log_content = (tmp_log_dir / "tombola_stark.log").read_text(encoding="utf-8")
    assert "SESSIONE AVVIATA" in log_content


def test_shutdown_scrive_marcatore_chiusura(tmp_log_dir):
    """Dopo shutdown(), il file contiene il marcatore di chiusura."""
    GameLogger.initialize()
    GameLogger.shutdown()
    log_content = (tmp_log_dir / "tombola_stark.log").read_text(encoding="utf-8")
    assert "SESSIONE CHIUSA" in log_content
```

#### `tests/integration/test_logging_integration.py`

```python
"""Test di integrazione: logger + controller.

Verifica che le chiamate al controller producano
le righe attese nel file di log.
"""
import logging
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
    yield
    GameLogger.shutdown()
    GameLogger._initialized = False
    logger = logging.getLogger("tombola_stark")
    logger.handlers.clear()


@pytest.fixture
def tmp_log_dir(tmp_path, monkeypatch):
    import bingo_game.logging.game_logger as gl_module
    monkeypatch.setattr(gl_module, "_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(gl_module, "_LOG_FILE", tmp_path / "logs" / "tombola_stark.log")
    return tmp_path / "logs"


def test_creazione_partita_loggata(tmp_log_dir):
    """crea_partita_standard() produce una riga INFO nel log."""
    GameLogger.initialize()
    crea_partita_standard("Test", n_umani=1, n_bot=1)
    content = (tmp_log_dir / "tombola_stark.log").read_text(encoding="utf-8")
    assert "Partita creata" in content


def test_avvio_partita_loggato(tmp_log_dir):
    """avvia_partita_sicura() produce una riga INFO nel log."""
    GameLogger.initialize()
    partita = crea_partita_standard("Test", n_umani=1, n_bot=1)
    avvia_partita_sicura(partita)
    content = (tmp_log_dir / "tombola_stark.log").read_text(encoding="utf-8")
    assert "avviata" in content.lower()


def test_turni_loggati_in_debug(tmp_log_dir):
    """In modalità debug, ogni turno produce una riga DEBUG nel log."""
    GameLogger.initialize(debug_mode=True)
    partita = crea_partita_standard("Test", n_umani=1, n_bot=1)
    avvia_partita_sicura(partita)
    esegui_turno_sicuro(partita)
    content = (tmp_log_dir / "tombola_stark.log").read_text(encoding="utf-8")
    assert "DEBUG" in content
    assert "Turno eseguito" in content
```

#### Commit Message

```
test(logging): add unit and integration tests for GameLogger

- tests/unit/test_game_logger.py: 8 unit tests (init, shutdown, levels, markers)
- tests/integration/test_logging_integration.py: 3 integration tests
  (create game, start game, debug-mode turns)
- All tests use tmp_path fixture: no real logs/ affected

Testing:
- pytest tests/unit/test_game_logger.py
- pytest tests/integration/test_logging_integration.py
```

---

## 🧪 Testing Strategy

### Unit Tests (8 test)

#### `tests/unit/test_game_logger.py` (8 test)
- [ ] `test_initialize_crea_cartella_log` — cartella creata automaticamente
- [ ] `test_initialize_crea_file_log` — file creato all'init
- [ ] `test_get_instance_senza_initialize_lancia_errore` — RuntimeError senza init
- [ ] `test_initialize_doppio_non_duplica_handler` — seconda chiamata è no-op
- [ ] `test_modalita_normale_livello_info` — livello INFO in modalità normale
- [ ] `test_modalita_debug_livello_debug` — livello DEBUG in modalità debug
- [ ] `test_marcatori_sessione_nel_file` — marcatore AVVIATA nel file
- [ ] `test_shutdown_scrive_marcatore_chiusura` — marcatore CHIUSA dopo shutdown

### Integration Tests (3 test)

#### `tests/integration/test_logging_integration.py` (3 test)
- [ ] `test_creazione_partita_loggata` — crea_partita_standard produce INFO
- [ ] `test_avvio_partita_loggato` — avvia_partita_sicura produce INFO
- [ ] `test_turni_loggati_in_debug` — esegui_turno_sicuro produce DEBUG in debug mode

### Manual Testing Checklist

- [ ] Avviare `python main.py` → verificare che `logs/tombola_stark.log` venga creato
- [ ] Aprire il file con un editor mentre il gioco è in esecuzione → le righe appaiono in tempo reale
- [ ] Avviare due sessioni consecutive → il file si accumula, non viene sovrascritto
- [ ] I marcatori `SESSIONE AVVIATA` / `SESSIONE CHIUSA` separano visivamente le sessioni
- [ ] Avviare `python main.py --debug` → le righe DEBUG sono presenti nel log
- [ ] Avviare `python main.py` (senza --debug) → nessuna riga DEBUG nel log
- [ ] Verificare che `git status` non mostri mai `logs/` tra i file tracciati

---

## 🎓 Architectural Patterns Reference

### Pattern: Logger Singleton con FlushingHandler

**Quando Usare**: Applicazioni monoutente dove il log deve essere leggibile in tempo reale e tutti i moduli devono scrivere sullo stesso file senza passarsi istanze.

**Caratteristiche**:
- `initialize()` chiamato una sola volta in `main.py`
- `get_instance()` chiamato da qualsiasi punto del codice
- `shutdown()` in blocco `finally` di `main()`
- `emit()` sovrascritto per flush automatico

**Pro/Contro**:
- ✅ Pro: Zero modifiche alle firme di funzioni esistenti
- ✅ Pro: Flush immediato senza gestione manuale
- ⚠️ Contro: Il Singleton rende i test più delicati (richiede reset tra i test — vedi fixture)

### Pattern: `_log_safe()` Helper

**Quando Usare**: Ovunque il logging non deve mai propagare eccezioni al chiamante.

```python
def _log_safe(message: str, level: str = "info", *args) -> None:
    try:
        GameLogger.get_instance()  # può sollevare se non inizializzato
        getattr(logging.getLogger("tombola_stark"), level)(message, *args)
    except Exception:
        pass  # Il logging non interrompe mai il gioco
```

**Caratteristiche**:
- Protegge da `RuntimeError` se chiamato prima di `initialize()`
- Protegge da errori di I/O (disco pieno, permessi)
- Aggiunge overhead trascurabile (try/except vuoto su percorso felice)

---

## ✅ Validation & Acceptance

### Success Criteria

**Funzionali**:
- [ ] Il file `logs/tombola_stark.log` viene creato automaticamente al primo avvio — *verificabile: avviare il gioco da zero*
- [ ] Sessioni multiple si accumulano nello stesso file — *verificabile: contare i marcatori AVVIATA nel file dopo 3 avvii*
- [ ] Il log è leggibile mentre il gioco è in esecuzione — *verificabile: `tail -f logs/tombola_stark.log` durante una partita*
- [ ] `--debug` aggiunge righe DEBUG, assenza del flag le nasconde — *verificabile: confrontare i due file*
- [ ] Chiusura forzata (Ctrl+C) scrive comunque il marcatore di fine — *verificabile: testare KeyboardInterrupt*

**Tecnici**:
- [ ] Zero breaking changes — tutti i test esistenti passano
- [ ] Test coverage ≥ 80% per `bingo_game/logging/`
- [ ] Il dominio (`bingo_game/` root, `players/`, `events/`) non importa mai `GameLogger`
- [ ] Nessuna riga `print()` di debug lasciata nel codice

**Code Quality**:
- [ ] Tutti i commit compilano senza errori
- [ ] PEP8 compliant (pycodestyle)
- [ ] Type hints completi su tutti i metodi pubblici di `GameLogger`
- [ ] Docstring Google style su tutti i metodi pubblici
- [ ] `CHANGELOG.md` aggiornato con la sezione v0.4.0

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T: Logger nel Dominio

```python
# WRONG — in bingo_game/partita.py
from bingo_game.logging import GameLogger

class Partita:
    def esegui_turno(self):
        GameLogger.get_instance().info("Turno eseguito")  # ❌ Dominio → Infrastruttura
```

**Perché non funziona**: Viola ADR-001 e ADR-003. Il Dominio deve avere zero dipendenze esterne.

### ✅ DO: Logger nel Controller

```python
# CORRECT — in bingo_game/game_controller.py
def esegui_turno_sicuro(partita):
    risultato = partita.esegui_turno()  # Dominio non sa nulla del log
    _log_safe("Turno: numero=%s", "debug", risultato.get("numero_estratto"))  # ✅
    return risultato
```

---

### ❌ DON'T: File Handler senza Flush

```python
# WRONG — il log non è leggibile in tempo reale
handler = logging.FileHandler("logs/tombola_stark.log")
logger.addHandler(handler)
# Nessun flush → le righe restano nel buffer fino alla chiusura
```

### ✅ DO: FlushingFileHandler

```python
# CORRECT — ogni riga è su disco immediatamente
class FlushingFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()  # ✅ Flush immediato dopo ogni scrittura
```

---

### ❌ DON'T: Logging che Interrompe il Gioco

```python
# WRONG — un errore di I/O sul log fa crashare il gioco
def esegui_turno_sicuro(partita):
    risultato = partita.esegui_turno()
    GameLogger.get_instance().info("Turno")  # ❌ Può sollevare IOError
    return risultato
```

### ✅ DO: `_log_safe()` Helper

```python
# CORRECT
def esegui_turno_sicuro(partita):
    risultato = partita.esegui_turno()
    _log_safe("Turno eseguito", "info")  # ✅ Mai propaga eccezioni
    return risultato
```

---

## 📦 Commit Strategy

### Atomic Commits (5 totali)

1. **Commit 1**: Logger base
   - `feat(logging): add GameLogger singleton with cumulative file and real-time flush`
   - Files: `bingo_game/logging/__init__.py`, `bingo_game/logging/game_logger.py`

2. **Commit 2**: Gitignore
   - `chore(gitignore): exclude logs/ directory from version control`
   - Files: `.gitignore`

3. **Commit 3**: Aggancio controller
   - `feat(logging): hook GameLogger into game_controller at all key points`
   - Files: `bingo_game/game_controller.py`

4. **Commit 4**: Aggancio main
   - `feat(logging): integrate GameLogger init/shutdown in main.py with --debug flag`
   - Files: `main.py`

5. **Commit 5**: Test suite
   - `test(logging): add unit and integration tests for GameLogger`
   - Files: `tests/unit/test_game_logger.py`, `tests/integration/test_logging_integration.py`

---

## 📚 References

### Documentazione Python Standard Library
- [logging — HOWTO](https://docs.python.org/3/howto/logging.html)
- [logging.FileHandler](https://docs.python.org/3/library/logging.handlers.html#logging.FileHandler)
- [argparse](https://docs.python.org/3/library/argparse.html)

### Internal Architecture Docs
- `documentations/ARCHITECTURE.md` — Regole di dipendenza tra livelli, ADR-001, ADR-003
- `documentations/API.md` — API pubblica del controller (punti di aggancio)
- `documentations/DESIGN_LOGGING_SYSTEM.md` — Design freeze: tutte le decisioni concettuali

### Related Code Files
- `bingo_game/game_controller.py` — Punto principale di aggancio logging
- `bingo_game/events/` — Sistema eventi esistente (candidati naturali da tracciare)
- `main.py` — Entry point: init e shutdown del logger

---

## 📝 Note Operative per Copilot

### Istruzioni Step-by-Step

1. **Commit 1 — Crea il modulo logger**:
   - Crea directory `bingo_game/logging/`
   - Crea `bingo_game/logging/__init__.py` con il contenuto del Commit 1
   - Crea `bingo_game/logging/game_logger.py` con il contenuto del Commit 1
   - Commit: `feat(logging): add GameLogger singleton...`

2. **Commit 2 — Aggiorna .gitignore**:
   - Apri `.gitignore` nella root del progetto
   - Aggiungi le righe `logs/` e `*.log` in fondo
   - Commit: `chore(gitignore): exclude logs/...`

3. **Commit 3 — Modifica game_controller.py**:
   - Aggiungi `from bingo_game.logging import GameLogger` agli import
   - Aggiungi la funzione helper `_log_safe()` (privata, top-level)
   - Aggiungi le chiamate `_log_safe()` nei punti elencati nella Fase 3
   - NON modificare le firme delle funzioni esistenti
   - Commit: `feat(logging): hook GameLogger into game_controller...`

4. **Commit 4 — Modifica main.py**:
   - Aggiungi import `argparse` e `from bingo_game.logging import GameLogger`
   - Aggiungi funzione `_parse_args()`
   - Wrappa il corpo di `main()` con `try/finally` per garantire `shutdown()`
   - Chiama `GameLogger.initialize(debug_mode=args.debug)` come prima istruzione di `main()`
   - Commit: `feat(logging): integrate GameLogger init/shutdown in main.py...`

5. **Commit 5 — Crea i test**:
   - Crea `tests/unit/test_game_logger.py`
   - Crea `tests/integration/test_logging_integration.py`
   - Esegui: `python -m pytest tests/unit/test_game_logger.py -v`
   - Esegui: `python -m pytest tests/integration/test_logging_integration.py -v`
   - Commit solo se tutti i test passano

### Verifica Rapida Pre-Commit

```bash
# Sintassi Python
python -m py_compile bingo_game/logging/game_logger.py
python -m py_compile bingo_game/game_controller.py
python -m py_compile main.py

# Test unitari logging
python -m pytest tests/unit/test_game_logger.py -v

# Test integrazione logging
python -m pytest tests/integration/test_logging_integration.py -v

# Test suite completa (nessuna regressione)
python -m pytest tests/ -v

# Code style
pycodestyle bingo_game/logging/ --max-line-length=120
```

### Troubleshooting

**Se `GameLogger.get_instance()` solleva RuntimeError**:
- Verifica che `GameLogger.initialize()` sia chiamato prima in `main.py`
- Controlla che il blocco `finally` non esegua `shutdown()` troppo presto

**Se il file di log non viene aggiornato in tempo reale**:
- Verifica che `FlushingFileHandler.emit()` chiami `self.flush()`
- Controlla che non ci sia buffering a livello di sistema operativo (Windows può bufferizzare su rete)

**Se i test falliscono per stato condiviso tra test**:
- Verifica che la fixture `reset_logger` resetti correttamente `GameLogger._initialized = False`
- Assicurati che `logger.handlers.clear()` venga chiamato nella fixture

---

## 🚀 Risultato Finale Atteso

Una volta completati i 5 commit:

✅ **Tracciabilità automatica**: ogni evento rilevante della partita è nel log, senza intervento dell'utente  
✅ **Diario cumulativo**: tutte le sessioni in un unico file, separate da marcatori con timestamp  
✅ **Leggibilità in tempo reale**: il log è consultabile con qualsiasi editor durante l'esecuzione  
✅ **Modalità dettagliata**: `python main.py --debug` attiva il livello DEBUG per sessioni di diagnosi  
✅ **Silenzioso per l'utente**: nessuna finestra, nessun messaggio, nessuna interazione richiesta  
✅ **Architettura rispettata**: il Dominio rimane con zero dipendenze esterne  
✅ **Repository pulito**: `logs/` mai committato grazie al `.gitignore` aggiornato  

**Metriche Successo**:
- Test coverage `bingo_game/logging/`: ≥ 80%
- Tutti i test esistenti: ancora ✅ (zero regressioni)
- Scrittura log per turno: < 1ms overhead (flush su SSD locale)

---

## 📊 Progress Tracking

| Commit | Descrizione | Status | Data |
|--------|-------------|--------|------|
| 1 | GameLogger singleton + FlushingHandler | [ ] | - |
| 2 | .gitignore aggiornato | [ ] | - |
| 3 | Aggancio game_controller.py | [ ] | - |
| 4 | Aggancio main.py + argparse | [ ] | - |
| 5 | Test suite (unit + integration) | [ ] | - |
| — | CHANGELOG.md aggiornato con v0.4.0 | [ ] | - |

---

*Documento creato: 2026-02-18*  
*Autore: AI Assistant + donato81*  
*Basato su*: `DESIGN_LOGGING_SYSTEM.md` (DESIGN FREEZE), `ARCHITECTURE.md` (ADR-001, ADR-003), `API.md`

---

**Fine Piano di Implementazione**
