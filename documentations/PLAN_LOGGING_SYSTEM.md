# 📋 Piano di Implementazione — Sistema di Logging Centralizzato

> **Basato su**: `DESIGN_LOGGING_SYSTEM.md` (stato: DESIGN FREEZE ✅)  
> Tutte le decisioni di design sono chiuse. Questo documento traduce quelle decisioni in codice.

---

## 📊 Executive Summary

**Tipo**: FEATURE  
**Priorità**: 🟠 ALTA  
**Stato**: READY  
**Branch**: `feat/logging-system`  
**Versione Target**: `v0.4.0` (Fase 1) → `v0.5.0` (Fase 2)  
**Data Creazione**: 2026-02-18  
**Autore**: AI Assistant + donato81  
**Effort Stimato Fase 1**: 4–5 ore totali (3 ore implementazione + 1–2 ore review/testing)  
**Effort Stimato Fase 2**: 3–4 ore totali (2 ore implementazione + 1–2 ore review/testing)  
**Commits Previsti**: 5 (Fase 1) + 4 (Fase 2) = 9 commit atomici totali

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
| **Scope** | 6–8 file modificati o nuovi (Fase 1) + 5–7 file (Fase 2) | Vedi File Structure |
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

## 📝 Piano di Implementazione — FASE 1 (v0.4.0)

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
```

#### Codice Nuovo — `bingo_game/logging/__init__.py`

```python
"""Modulo di logging centralizzato per Tombola Stark."""
from bingo_game.logging.game_logger import GameLogger

__all__ = ["GameLogger"]
```

#### Commit Message

```
feat(logging): add GameLogger singleton with cumulative file and real-time flush

- New module bingo_game/logging/ with GameLogger class
- Single cumulative file logs/tombola_stark.log (append mode)
- FlushingFileHandler: every log line is flushed to disk immediately
- Session markers (start/end) with timestamps separate sessions in log
- initialize(debug_mode) / get_instance() / shutdown() API
```

---

### COMMIT 2: Aggiornamento `.gitignore`

**Priorità**: 🔴 CRITICA  
**File**: `.gitignore`

```gitignore
# File di log generati a runtime — artefatti locali, non nel repository
logs/
*.log
```

#### Commit Message

```
chore(gitignore): exclude logs/ directory from version control
```

---

### COMMIT 3: Aggancio al Controller

**Priorità**: 🔴 CRITICA  
**File**: `bingo_game/game_controller.py`

#### Pattern di Aggancio Sicuro

```python
def _log_safe(message: str, level: str = "info", *args) -> None:
    """Scrive nel log senza mai propagare eccezioni al chiamante.

    Version:
        v0.4.0: Helper interno per logging sicuro nel controller
    """
    try:
        logger = GameLogger.get_instance()
        getattr(logger, level)(message, *args)
    except Exception:  # noqa: BLE001
        pass
```

#### Punti di Aggancio

```python
# crea_partita_standard() — dopo la creazione riuscita
_log_safe("Partita creata: nome=%s, giocatori_umani=%d, bot=%d", "info", nome, n_umani, n_bot)

# avvia_partita_sicura() — avvio OK
_log_safe("Partita avviata con successo.", "info")

# avvia_partita_sicura() — eccezione
_log_safe("Avvio partita fallito: %s", "warning", str(exc))

# esegui_turno_sicuro() — turno OK (solo DEBUG)
_log_safe("Turno eseguito: numero=%s, premi=%d", "debug",
          risultato.get("numero_estratto"), len(risultato.get("premi_nuovi", [])))

# esegui_turno_sicuro() — anomalia intercettata
_log_safe("Anomalia nel turno intercettata: %s", "warning", str(exc))

# partita_terminata() — fine partita
_log_safe("Partita terminata.", "info")
```

#### Commit Message

```
feat(logging): hook GameLogger into game_controller at all key points
```

---

### COMMIT 4: Aggancio a `main.py`

**Priorità**: 🔴 CRITICA  
**File**: `main.py`

```python
import argparse
from bingo_game.logging import GameLogger

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tombola Stark")
    parser.add_argument("--debug", action="store_true", default=False)
    return parser.parse_args()

def main() -> None:
    args = _parse_args()
    GameLogger.initialize(debug_mode=args.debug)
    try:
        pass  # codice esistente del gioco
    finally:
        GameLogger.shutdown()

if __name__ == "__main__":
    main()
```

#### Commit Message

```
feat(logging): integrate GameLogger init/shutdown in main.py with --debug flag
```

---

### COMMIT 5: Test Suite Fase 1

**Priorità**: 🟠 ALTA  
**File Nuovi**: `tests/unit/test_game_logger.py`, `tests/integration/test_logging_integration.py`

8 unit test + 3 integration test (vedi dettaglio nella sezione Testing Strategy).

#### Commit Message

```
test(logging): add unit and integration tests for GameLogger (Phase 1)
```

---

## 🧪 Testing Strategy — Fase 1

### Unit Tests (8 test) — `tests/unit/test_game_logger.py`

- [ ] `test_initialize_crea_cartella_log`
- [ ] `test_initialize_crea_file_log`
- [ ] `test_get_instance_senza_initialize_lancia_errore`
- [ ] `test_initialize_doppio_non_duplica_handler`
- [ ] `test_modalita_normale_livello_info`
- [ ] `test_modalita_debug_livello_debug`
- [ ] `test_marcatori_sessione_nel_file`
- [ ] `test_shutdown_scrive_marcatore_chiusura`

### Integration Tests (3 test) — `tests/integration/test_logging_integration.py`

- [ ] `test_creazione_partita_loggata`
- [ ] `test_avvio_partita_loggato`
- [ ] `test_turni_loggati_in_debug`

### Manual Testing Checklist

- [ ] `python main.py` → `logs/tombola_stark.log` creato automaticamente
- [ ] Due sessioni consecutive → file si accumula, non sovrascritto
- [ ] `python main.py --debug` → righe DEBUG presenti
- [ ] `python main.py` (senza --debug) → nessuna riga DEBUG
- [ ] `git status` → `logs/` mai tracciato

---

## ✅ Validation & Acceptance — Fase 1

- [ ] `logs/tombola_stark.log` creato automaticamente al primo avvio
- [ ] Sessioni multiple si accumulano nello stesso file
- [ ] Log leggibile in tempo reale (`tail -f logs/tombola_stark.log`)
- [ ] Zero breaking changes — tutti i test esistenti passano
- [ ] Test coverage ≥ 80% per `bingo_game/logging/`
- [ ] Il dominio non importa mai `GameLogger`
- [ ] PEP8 compliant, type hints e docstring Google style completi
- [ ] `CHANGELOG.md` aggiornato con sezione v0.4.0

---

## 📊 Progress Tracking — Fase 1

| Commit | Descrizione | Status | Data |
|--------|-------------|--------|------|
| 1 | GameLogger singleton + FlushingHandler | [ ] | - |
| 2 | .gitignore aggiornato | [ ] | - |
| 3 | Aggancio game_controller.py | [ ] | - |
| 4 | Aggancio main.py + argparse | [ ] | - |
| 5 | Test suite (unit + integration) | [ ] | - |
| — | CHANGELOG.md aggiornato con v0.4.0 | [ ] | - |

---

---

# 🔖 FASE 2 — Copertura Completa degli Eventi (v0.5.0)

> **Prerequisito**: Fase 1 completata e tutti i commit della Fase 1 su `main`.  
> **Obiettivo**: Usare il `GameLogger` già esistente per tracciare **tutti** gli eventi di gioco e di sistema, organizzati per categoria e livello di severità.

---

## 📊 Executive Summary — Fase 2

**Tipo**: ENHANCEMENT  
**Priorità**: 🟠 ALTA  
**Stato**: PLANNED  
**Branch**: `feat/logging-event-coverage`  
**Versione Target**: `v0.5.0`  
**Data Creazione**: 2026-02-18  
**Effort Stimato**: 3–4 ore totali  
**Commits Previsti**: 4 commit atomici

---

### Problema/Obiettivo Fase 2

La Fase 1 aggancia il logger ai punti di ingresso/uscita principali del controller. È un diario di primo livello: sappiamo che la partita è iniziata e finita, ma non sappiamo **nulla di ciò che è accaduto nel mezzo**. Un premio assegnato? Un'eccezione di dominio inghiottita dal controller sicuro? Un bot che ha vinto con il turno 42? Tutto questo è invisibile.

L'obiettivo della Fase 2 è portare la copertura degli eventi al **100% degli eventi osservabili dal Controller**, senza mai toccare il Dominio.

---

### Cosa Cambia rispetto alla Fase 1

| Aspetto | Fase 1 | Fase 2 |
|---|---|---|
| **Scope** | Punti di ingresso/uscita del Controller | Tutti gli eventi interni alla partita |
| **Granularità** | 5 eventi loggati | 18+ eventi distinti |
| **Categorie** | Unico logger `tombola_stark` | Sub-logger per categoria (game, prizes, system, errors) |
| **Dati per evento** | Messaggio testuale semplice | Dati strutturati dal dizionario di ritorno delle API |
| **Nuovi file** | Nessuno | Nessuno (si estende `game_controller.py`) |

---

## 🗺️ Mappa Completa degli Eventi

Ogni evento è classificato per **categoria**, **livello** e **fonte API** da `API.md`.

### Categoria: `game` — Ciclo di vita della partita

| ID Evento | Livello | Fonte API | Trigger | Messaggio Log |
|---|---|---|---|---|
| `GAME_CREATED` | INFO | `crea_partita_standard()` | Creazione riuscita | `"[GAME] Partita creata: giocatore='%s', cartelle=%d, bot=%d"` |
| `GAME_STARTED` | INFO | `avvia_partita_sicura()` → `True` | Avvio riuscito | `"[GAME] Partita avviata — stato: in_corso"` |
| `GAME_START_FAILED` | WARNING | `avvia_partita_sicura()` → `False` | Avvio fallito | `"[GAME] Avvio fallito: %s"` |
| `GAME_TURN` | DEBUG | `esegui_turno_sicuro()` | Ogni turno (solo `--debug`) | `"[GAME] Turno #%d — estratto: %d, avanzamento: %.1f%%"` |
| `GAME_ENDED_TOMBOLA` | INFO | `esegui_turno_sicuro()` → `tombola_rilevata=True` | Fine per tombola | `"[GAME] Partita terminata per TOMBOLA al turno #%d"` |
| `GAME_ENDED_NUMBERS` | INFO | `esegui_turno_sicuro()` → `partita_terminata=True, tombola=False` | Fine per numeri esauriti | `"[GAME] Partita terminata per NUMERI ESAURITI al turno #%d"` |
| `GAME_STATE_SNAPSHOT` | DEBUG | `ottieni_stato_sintetico()` | Ogni turno (solo `--debug`) | `"[GAME] Stato: estratti=%d/90, giocatori=%d"` |

### Categoria: `prizes` — Premi assegnati

| ID Evento | Livello | Fonte API | Trigger | Messaggio Log |
|---|---|---|---|---|
| `PRIZE_AMBO` | INFO | `verifica_premi()` → `premio="ambo"` | Ambo conseguito | `"[PRIZE] AMBO — giocatore='%s', cartella=%d, riga=%d"` |
| `PRIZE_TERNO` | INFO | `verifica_premi()` → `premio="terno"` | Terno conseguito | `"[PRIZE] TERNO — giocatore='%s', cartella=%d, riga=%d"` |
| `PRIZE_QUATERNA` | INFO | `verifica_premi()` → `premio="quaterna"` | Quaterna conseguita | `"[PRIZE] QUATERNA — giocatore='%s', cartella=%d, riga=%d"` |
| `PRIZE_CINQUINA` | INFO | `verifica_premi()` → `premio="cinquina"` | Cinquina conseguita | `"[PRIZE] CINQUINA — giocatore='%s', cartella=%d, riga=%d"` |
| `PRIZE_TOMBOLA` | INFO | `verifica_premi()` → `premio="tombola"` | Tombola conseguita | `"[PRIZE] TOMBOLA! — giocatore='%s', cartella=%d"` |
| `PRIZE_SUMMARY` | INFO | Fine partita | Riepilogo premi | `"[PRIZE] Riepilogo: %d premi totali assegnati"` |

### Categoria: `system` — Infrastruttura e configurazione

| ID Evento | Livello | Fonte API | Trigger | Messaggio Log |
|---|---|---|---|---|
| `SYS_LOGGER_INIT` | INFO | `GameLogger.initialize()` | Avvio logger | `"[SYS] Logger inizializzato — livello: %s, file: %s"` |
| `SYS_SESSION_START` | INFO | `main()` | Avvio applicazione | `"[SYS] Sessione avviata — versione: %s"` |
| `SYS_SESSION_END` | INFO | `GameLogger.shutdown()` | Chiusura applicazione | `"[SYS] Sessione chiusa — durata: %s"` |
| `SYS_DEBUG_MODE` | INFO | `--debug` flag | Solo se `--debug` attivo | `"[SYS] Modalità DEBUG attiva — tutti gli eventi saranno tracciati"` |
| `SYS_TABELLONE_RESET` | DEBUG | `reset_tabellone()` se chiamato | Reset tabellone | `"[SYS] Tabellone resettato"` |

### Categoria: `errors` — Eccezioni e anomalie

| ID Evento | Livello | Fonte API | Trigger | Messaggio Log |
|---|---|---|---|---|
| `ERR_TURN_EXCEPTION` | WARNING | `esegui_turno_sicuro()` → `None` | Eccezione nel turno | `"[ERR] Eccezione turno #%d: %s — tipo: %s"` |
| `ERR_GAME_START` | WARNING | `avvia_partita_sicura()` → `False` | Eccezione avvio | `"[ERR] Eccezione avvio partita: %s — tipo: %s"` |
| `ERR_INVALID_STATE` | ERROR | `partita_terminata()` su stato incoerente | Stato inatteso | `"[ERR] Stato partita inatteso: %s"` |
| `ERR_NUMBERS_EXHAUSTED` | WARNING | `PartitaNumeriEsauritiException` | Numeri esauriti | `"[ERR] Numeri esauriti al turno #%d — partita terminata forzatamente"` |

---

## 🏗️ Architettura Fase 2

### Sub-Logger per Categoria

Il modulo `logging` di Python supporta nativamente una gerarchia di logger tramite la notazione a punto. Invece di un unico logger `tombola_stark`, la Fase 2 introduce **sub-logger per categoria**, tutti figli dello stesso logger radice. Questo permette di filtrare le righe nel file per categoria semplicemente cercando `[GAME]`, `[PRIZE]`, `[SYS]`, `[ERR]`.

```
tombola_stark                    ← logger radice (Fase 1, handler su file)
├── tombola_stark.game           ← eventi ciclo partita
├── tombola_stark.prizes         ← eventi premi
├── tombola_stark.system         ← eventi infrastruttura
└── tombola_stark.errors         ← eccezioni e anomalie
```

Tutti i sub-logger ereditano automaticamente l'handler del logger radice (propagate=True di default nei figli). **Nessuna modifica a `game_logger.py`** — i sub-logger vengono ottenuti con `logging.getLogger("tombola_stark.game")` direttamente nel controller.

```python
# In game_controller.py — ottenere i sub-logger (pattern da seguire)
import logging

_logger_game    = logging.getLogger("tombola_stark.game")
_logger_prizes  = logging.getLogger("tombola_stark.prizes")
_logger_system  = logging.getLogger("tombola_stark.system")
_logger_errors  = logging.getLogger("tombola_stark.errors")
```

### Contatore di Turno

La Fase 2 introduce un **contatore di turno di sessione** a livello di controller per arricchire i messaggi di log senza modificare le firme delle funzioni.

```python
# In game_controller.py — variabile di modulo (stato di sessione)
_turno_corrente: int = 0  # resettato a ogni nuova partita in crea_partita_standard()
_premi_totali: int = 0    # contatore cumulativo premi per la sessione
_tempo_inizio_sessione: datetime | None = None  # per calcolare la durata in SYS_SESSION_END
```

### Timer di Sessione

Per `SYS_SESSION_END`, il controller registra il timestamp di inizio partita e calcola la durata in `GameLogger.shutdown()` tramite `main.py`.

```python
# In main.py — calcolo durata sessione
import time
_t0 = time.monotonic()
GameLogger.initialize(debug_mode=args.debug)
try:
    ...
finally:
    durata = time.monotonic() - _t0
    _log_safe(f"[SYS] Sessione chiusa — durata: {durata:.1f}s", "info")
    GameLogger.shutdown()
```

---

## 📝 Piano di Implementazione — FASE 2 (v0.5.0)

---

### COMMIT 6: Sub-Logger e Costanti di Categoria

**Priorità**: 🔴 CRITICA (prerequisito di tutti gli altri commit di Fase 2)  
**File**: `bingo_game/game_controller.py`

#### Modifiche da Apportare

Aggiungere in cima a `game_controller.py`, dopo gli import esistenti:

```python
import logging
from datetime import datetime

# Sub-logger per categoria — figli del logger radice tombola_stark
# Nessuna configurazione necessaria: ereditano handler e livello dal padre
_logger_game   = logging.getLogger("tombola_stark.game")
_logger_prizes = logging.getLogger("tombola_stark.prizes")
_logger_system = logging.getLogger("tombola_stark.system")
_logger_errors = logging.getLogger("tombola_stark.errors")

# Stato di sessione — variabili di modulo (reset in crea_partita_standard)
_turno_corrente: int = 0
_premi_totali: int = 0
```

#### Helper Esteso

Estendere `_log_safe()` per supportare il logger specifico per categoria:

```python
def _log_safe(message: str, level: str = "info", *args,
              logger: logging.Logger | None = None) -> None:
    """Scrive nel log senza mai propagare eccezioni al chiamante.

    Args:
        message: Messaggio da registrare.
        level: Livello logging ('info', 'warning', 'debug', 'error').
        *args: Argomenti per il formato stringa del logger.
        logger: Sub-logger specifico. Se None, usa il logger radice.

    Version:
        v0.5.0: Aggiunto parametro logger per supporto sub-logger
    """
    try:
        target = logger or GameLogger.get_instance()
        getattr(target, level)(message, *args)
    except Exception:  # noqa: BLE001
        pass
```

#### Commit Message

```
feat(logging): add category sub-loggers and session state to game_controller

- Sub-loggers: tombola_stark.game / .prizes / .system / .errors
- Module-level session counters: _turno_corrente, _premi_totali
- _log_safe() extended with optional logger parameter
- Zero impact on existing function signatures or return values
```

---

### COMMIT 7: Tracciamento Completo Ciclo di Gioco

**Priorità**: 🔴 CRITICA  
**File**: `bingo_game/game_controller.py`

#### Modifiche per `crea_partita_standard()`

```python
def crea_partita_standard(
    nome_giocatore_umano: str = "Giocatore 1",
    num_cartelle_umano: int = 1,
    num_bot: int = 1
) -> Partita:
    global _turno_corrente, _premi_totali
    _turno_corrente = 0   # reset contatore turni per nuova partita
    _premi_totali = 0     # reset contatore premi per nuova partita

    partita = ...  # logica esistente invariata

    _log_safe(
        "[GAME] Partita creata — giocatore='%s', cartelle=%d, bot=%d, tot_giocatori=%d",
        "info", nome_giocatore_umano, num_cartelle_umano, num_bot,
        partita.get_numero_giocatori(),
        logger=_logger_game
    )
    return partita
```

#### Modifiche per `avvia_partita_sicura()`

```python
def avvia_partita_sicura(partita: Partita) -> bool:
    try:
        partita.avvia_partita()
        _log_safe(
            "[GAME] Partita avviata — stato: %s, giocatori: %d",
            "info", partita.get_stato_partita(), partita.get_numero_giocatori(),
            logger=_logger_game
        )
        return True
    except Exception as exc:
        _log_safe("[GAME] Avvio fallito: %s", "warning", str(exc), logger=_logger_game)
        _log_safe(
            "[ERR] Eccezione avvio partita: %s — tipo: %s",
            "warning", str(exc), type(exc).__name__,
            logger=_logger_errors
        )
        return False
```

#### Modifiche per `esegui_turno_sicuro()`

```python
def esegui_turno_sicuro(partita: Partita) -> Optional[Dict[str, Any]]:
    global _turno_corrente, _premi_totali
    try:
        risultato = partita.esegui_turno()
        _turno_corrente += 1

        # Evento turno (solo DEBUG)
        _log_safe(
            "[GAME] Turno #%d — estratto: %d, avanzamento: %.1f%%",
            "debug", _turno_corrente,
            risultato["numero_estratto"],
            ((_turno_corrente / 90) * 100),
            logger=_logger_game
        )

        # Snapshot stato (solo DEBUG)
        stato = ottieni_stato_sintetico(partita)
        _log_safe(
            "[GAME] Stato: estratti=%d/90, premi_sessione=%d",
            "debug", len(stato.get("numeri_estratti", [])), _premi_totali,
            logger=_logger_game
        )

        # Premi nuovi (INFO per tutti i premi)
        for evento in risultato.get("premi_nuovi", []):
            _premi_totali += 1
            _log_prize_event(evento)

        # Fine partita per tombola
        if risultato.get("tombola_rilevata"):
            _log_safe(
                "[GAME] Partita terminata per TOMBOLA al turno #%d",
                "info", _turno_corrente, logger=_logger_game
            )

        # Fine partita per numeri esauriti
        elif risultato.get("partita_terminata"):
            _log_safe(
                "[GAME] Partita terminata per NUMERI ESAURITI al turno #%d",
                "info", _turno_corrente, logger=_logger_game
            )
            _log_safe(
                "[ERR] Numeri esauriti al turno #%d",
                "warning", _turno_corrente, logger=_logger_errors
            )

        return risultato

    except Exception as exc:
        _log_safe(
            "[ERR] Eccezione turno #%d: %s — tipo: %s",
            "warning", _turno_corrente, str(exc), type(exc).__name__,
            logger=_logger_errors
        )
        return None
```

#### Nuova Funzione Helper Privata `_log_prize_event()`

```python
def _log_prize_event(evento: dict) -> None:
    """Logga un singolo evento di vincita dalla lista premi_nuovi.

    Args:
        evento: Dizionario con chiavi 'giocatore', 'cartella', 'premio', 'riga'.
                Formato come da API Partita.verifica_premi().

    Version:
        v0.5.0: Prima implementazione
    """
    premio = evento.get("premio", "sconosciuto")
    giocatore = evento.get("giocatore", "?")
    cartella = evento.get("cartella", "?")
    riga = evento.get("riga")

    if premio == "tombola":
        _log_safe(
            "[PRIZE] TOMBOLA! — giocatore='%s', cartella=%s",
            "info", giocatore, cartella, logger=_logger_prizes
        )
    else:
        _log_safe(
            "[PRIZE] %s — giocatore='%s', cartella=%s, riga=%s",
            "info", premio.upper(), giocatore, cartella, riga,
            logger=_logger_prizes
        )
```

#### Commit Message

```
feat(logging): full game lifecycle event tracing in game_controller

- crea_partita_standard: GAME_CREATED with player/bot counts
- avvia_partita_sicura: GAME_STARTED / GAME_START_FAILED with exception detail
- esegui_turno_sicuro: GAME_TURN (DEBUG), GAME_ENDED_TOMBOLA/NUMBERS (INFO)
- _log_prize_event(): dedicated helper for all prize events
- Session counters _turno_corrente and _premi_totali updated each turn

Impact: zero changes to return values or function signatures
```

---

### COMMIT 8: Tracciamento Premi e Riepilogo Finale

**Priorità**: 🟠 ALTA  
**File**: `bingo_game/game_controller.py`

#### Riepilogo Finale a Fine Partita

Aggiungere una funzione helper chiamata da `esegui_turno_sicuro()` quando `partita_terminata=True`:

```python
def _log_game_summary(partita: Partita) -> None:
    """Logga il riepilogo finale della partita al termine.

    Scrive un blocco INFO con le statistiche essenziali:
    turni giocati, numeri estratti, premi assegnati, vincitore (se tombola).

    Args:
        partita: L'istanza Partita terminata da cui leggere lo stato finale.

    Version:
        v0.5.0: Prima implementazione
    """
    try:
        stato = ottieni_stato_sintetico(partita)
        giocatori = stato.get("giocatori", [])
        vincitore = next(
            (g["nome"] for g in giocatori if g.get("ha_tombola")), None
        )

        _log_safe(
            "[GAME] === RIEPILOGO PARTITA ===",
            "info", logger=_logger_game
        )
        _log_safe(
            "[GAME] Turni giocati: %d | Numeri estratti: %d/90",
            "info", _turno_corrente, len(stato.get("numeri_estratti", [])),
            logger=_logger_game
        )
        _log_safe(
            "[PRIZE] Riepilogo premi: %d premi totali assegnati",
            "info", _premi_totali, logger=_logger_prizes
        )
        if vincitore:
            _log_safe(
                "[PRIZE] Vincitore TOMBOLA: '%s'",
                "info", vincitore, logger=_logger_prizes
            )
        else:
            _log_safe(
                "[GAME] Partita senza vincitore (numeri esauriti)",
                "info", logger=_logger_game
            )
    except Exception:
        pass  # Il riepilogo non deve mai interrompere la chiusura
```

#### Chiamata dal Controller

```python
# In esegui_turno_sicuro(), dopo aver rilevato tombola_rilevata=True o partita_terminata=True:
if risultato.get("tombola_rilevata") or risultato.get("partita_terminata"):
    _log_game_summary(partita)
```

#### Commit Message

```
feat(logging): add end-of-game summary logging with prize recap

- _log_game_summary(): INFO block with turns, numbers, prizes, winner
- Called automatically when tombola_rilevata=True or partita_terminata=True
- PRIZE_SUMMARY event: total prizes assigned in session
- PRIZE_WINNER event: tombola winner name if present
```

---

### COMMIT 9: Test Suite Fase 2

**Priorità**: 🟠 ALTA  
**File Nuovi**: `tests/unit/test_event_logging.py`, `tests/integration/test_event_coverage.py`

#### `tests/unit/test_event_logging.py` (7 test)

```python
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
```

#### `tests/integration/test_event_coverage.py` (5 test)

```python
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
```

#### Commit Message

```
test(logging): add Phase 2 event coverage tests (unit + integration)

- tests/unit/test_event_logging.py: 7 unit tests
  (sub-logger propagation, debug/info filtering, category prefixes)
- tests/integration/test_event_coverage.py: 5 integration tests
  (game created, started, turns, prizes, end summary)
- All tests use tmp_path fixture: no real logs/ affected
- Full game loop test verifies end-of-game summary block

Testing:
  pytest tests/unit/test_event_logging.py -v
  pytest tests/integration/test_event_coverage.py -v
```

---

## 🧪 Testing Strategy — Fase 2

### Unit Tests (7 test) — `tests/unit/test_event_logging.py`

- [ ] `test_sublogger_game_scrive_su_file` — propagazione su logger radice
- [ ] `test_sublogger_prizes_scrive_su_file` — propagazione prizes
- [ ] `test_sublogger_errors_scrive_su_file` — propagazione errors
- [ ] `test_sublogger_system_scrive_su_file` — propagazione system
- [ ] `test_debug_non_scrive_in_modalita_normale` — filtraggio DEBUG in INFO mode
- [ ] `test_debug_scrive_in_modalita_debug` — DEBUG visibile in debug mode
- [ ] `test_prefissi_categoria_distinti_nel_file` — tutti i prefissi distinguibili

### Integration Tests (5 test) — `tests/integration/test_event_coverage.py`

- [ ] `test_partita_completa_produce_game_created` — GAME_CREATED con nome giocatore
- [ ] `test_partita_avviata_produce_game_started` — GAME_STARTED con stato
- [ ] `test_turni_in_debug_producono_game_turn` — GAME_TURN solo in debug
- [ ] `test_premio_produce_prize_event` — PRIZE event durante partita reale
- [ ] `test_fine_partita_produce_riepilogo` — blocco RIEPILOGO a fine partita

### Manual Testing Checklist — Fase 2

- [ ] Eseguire una partita completa → verificare tutte le categorie `[GAME]`, `[PRIZE]`, `[SYS]`, `[ERR]` nel log
- [ ] Verificare che gli ambi/terne/quaterne/cinquine/tombola abbiano righe dedicate
- [ ] Verificare il blocco `=== RIEPILOGO PARTITA ===` a fine sessione
- [ ] In modalità `--debug`: verificare le righe `[GAME] Turno #N` per ogni turno
- [ ] In modalità normale: verificare che i `[GAME] Turno #N` non compaiano
- [ ] Cercare `[ERR]` dopo un run normale → deve essere assente
- [ ] Cercare `[ERR]` in un run con errore simulato → deve essere presente
- [ ] Verificare che i timestamp siano coerenti con l'orario di esecuzione

---

## 🚨 Common Pitfalls to Avoid — Fase 2

### ❌ DON'T: Chiamare sub-logger prima di `GameLogger.initialize()`

```python
# WRONG — all'avvio del modulo, prima di initialize()
_logger_game = logging.getLogger("tombola_stark.game")
_logger_game.info("test")  # ❌ Nessun handler → nessun output, ma nessun errore
```

**Perché non funziona**: I sub-logger cercano l'handler sul padre `tombola_stark`, che non è ancora configurato. Non crashano, ma scrivono nel vuoto.

### ✅ DO: Sub-logger definiti come costanti di modulo, chiamati solo dopo init

```python
# CORRECT — definizione come costante di modulo (no side effects)
_logger_game = logging.getLogger("tombola_stark.game")

# Usato solo dentro funzioni, dopo che initialize() è stato chiamato da main()
def crea_partita_standard(...):
    ...
    _log_safe("[GAME] Partita creata", "info", logger=_logger_game)  # ✅
```

---

### ❌ DON'T: Loggare dati strutturati con `str(dict)` completo

```python
# WRONG — produce righe illeggibili e molto lunghe
_log_safe("Stato: %s", "debug", str(ottieni_stato_sintetico(partita)))
# Output: "Stato: {'stato_partita': 'in_corso', 'ultimo_numero_estratto': 42, ...}"
```

### ✅ DO: Loggare solo i campi rilevanti

```python
# CORRECT — conciso e leggibile
stato = ottieni_stato_sintetico(partita)
_log_safe(
    "[GAME] Stato: estratti=%d/90",
    "debug", len(stato.get("numeri_estratti", [])),
    logger=_logger_game
)  # ✅
```

---

### ❌ DON'T: Duplicare gli eventi tra logger radice e sub-logger

```python
# WRONG — l'evento appare due volte nel file
GameLogger.get_instance().info("Partita creata")   # riga 1
_logger_game.info("[GAME] Partita creata")          # riga 2 (duplicato!)
```

### ✅ DO: Usare esclusivamente il sub-logger appropriato dalla Fase 2 in poi

```python
# CORRECT — dalla Fase 2, tutti gli eventi passano per il sub-logger
_log_safe("[GAME] Partita creata", "info", logger=_logger_game)  # ✅ una sola riga
```

---

## ✅ Validation & Acceptance — Fase 2

**Copertura eventi**:
- [ ] Tutti i 18 eventi della mappa sono presenti nel file dopo una partita completa
- [ ] Gli eventi `[GAME]` compaiono in ordine cronologico coerente
- [ ] Gli eventi `[PRIZE]` compaiono immediatamente dopo il turno che li ha generati
- [ ] Gli eventi `[ERR]` compaiono solo in presenza di anomalie reali

**Filtraggio per categoria**:
- [ ] `grep "\[GAME\]" logs/tombola_stark.log` → solo eventi di ciclo partita
- [ ] `grep "\[PRIZE\]" logs/tombola_stark.log` → solo eventi premio
- [ ] `grep "\[ERR\]" logs/tombola_stark.log` → solo anomalie ed eccezioni
- [ ] `grep "\[SYS\]" logs/tombola_stark.log` → solo eventi di sistema

**Tecnici**:
- [ ] Zero breaking changes — tutti i test di Fase 1 ancora passano
- [ ] Test coverage ≥ 80% per le nuove funzioni helper (`_log_prize_event`, `_log_game_summary`)
- [ ] Nessuna riga di log duplicata per lo stesso evento
- [ ] Overhead per turno: < 2ms (misurabile con `time.perf_counter()` nel test di integrazione)

**Code Quality**:
- [ ] Docstring Google style su `_log_prize_event()` e `_log_game_summary()`
- [ ] Type hints completi su tutti i nuovi helper
- [ ] `CHANGELOG.md` aggiornato con sezione v0.5.0

---

## 📊 Progress Tracking — Fase 2

| Commit | Descrizione | Status | Data |
|--------|-------------|--------|------|
| 6 | Sub-logger per categoria + state counters | [ ] | - |
| 7 | Tracciamento completo ciclo di gioco | [ ] | - |
| 8 | Tracciamento premi + riepilogo finale | [ ] | - |
| 9 | Test suite Fase 2 (unit + integration) | [ ] | - |
| — | CHANGELOG.md aggiornato con v0.5.0 | [ ] | - |

---

## 📚 References

### Documentazione Python Standard Library
- [logging — HOWTO](https://docs.python.org/3/howto/logging.html)
- [logging.FileHandler](https://docs.python.org/3/library/logging.handlers.html#logging.FileHandler)
- [Logger hierarchy](https://docs.python.org/3/howto/logging.html#logging-flow)
- [argparse](https://docs.python.org/3/library/argparse.html)

### Internal Architecture Docs
- `documentations/ARCHITECTURE.md` — Regole di dipendenza tra livelli, ADR-001, ADR-003
- `documentations/API.md` — API pubblica: `verifica_premi()`, `esegui_turno()`, `get_stato_completo()`
- `documentations/DESIGN_LOGGING_SYSTEM.md` — Design freeze: tutte le decisioni concettuali

### Related Code Files
- `bingo_game/game_controller.py` — Unico file modificato in entrambe le fasi
- `bingo_game/partita.py` — Fonte dei dati: `verifica_premi()`, `esegui_turno()`, `get_stato_completo()`
- `main.py` — Entry point: timer di sessione per `SYS_SESSION_END`

---

## 📝 Note Operative per Copilot — Fase 2

### Istruzioni Step-by-Step

1. **Commit 6 — Sub-logger e contatori**:
   - Apri `bingo_game/game_controller.py`
   - Aggiungi i 4 sub-logger come costanti di modulo dopo gli import esistenti
   - Aggiungi `_turno_corrente: int = 0` e `_premi_totali: int = 0`
   - Estendi `_log_safe()` con il parametro opzionale `logger`
   - Commit: `feat(logging): add category sub-loggers...`

2. **Commit 7 — Ciclo di gioco**:
   - Modifica `crea_partita_standard()`: reset contatori + log `[GAME] Partita creata`
   - Modifica `avvia_partita_sicura()`: log `[GAME] Partita avviata` / `[GAME] Avvio fallito` + `[ERR]`
   - Modifica `esegui_turno_sicuro()`: incremento `_turno_corrente`, log turno DEBUG, loop premi, log fine
   - Aggiungi `_log_prize_event()` come funzione helper privata top-level
   - Commit: `feat(logging): full game lifecycle event tracing...`

3. **Commit 8 — Riepilogo**:
   - Aggiungi `_log_game_summary()` come funzione helper privata top-level
   - Chiamala da `esegui_turno_sicuro()` quando `tombola_rilevata=True` o `partita_terminata=True`
   - Commit: `feat(logging): add end-of-game summary logging...`

4. **Commit 9 — Test**:
   - Crea `tests/unit/test_event_logging.py`
   - Crea `tests/integration/test_event_coverage.py`
   - Esegui: `python -m pytest tests/ -v` (tutta la suite, inclusi test Fase 1)
   - Commit solo se **tutti i test** (Fase 1 + Fase 2) passano

### Verifica Rapida Pre-Commit Fase 2

```bash
# Sintassi
python -m py_compile bingo_game/game_controller.py

# Test Fase 2
python -m pytest tests/unit/test_event_logging.py -v
python -m pytest tests/integration/test_event_coverage.py -v

# Regressione Fase 1 — devono ancora passare tutti
python -m pytest tests/unit/test_game_logger.py -v
python -m pytest tests/integration/test_logging_integration.py -v

# Suite completa
python -m pytest tests/ -v

# Verifica copertura eventi su una partita reale
python main.py  # poi: grep "\[PRIZE\]" logs/tombola_stark.log
```

---

## 🚀 Risultato Finale Atteso — Fase 1 + Fase 2

Una volta completati tutti e 9 i commit:

✅ **Copertura completa**: tutti gli eventi osservabili della partita sono nel log  
✅ **Organizzazione per categoria**: `[GAME]`, `[PRIZE]`, `[SYS]`, `[ERR]` facilmente filtrabili  
✅ **Riepilogo automatico**: blocco riassuntivo a fine sessione con statistiche chiave  
✅ **Diagnosi rapida**: `grep "[ERR]"` mostra immediatamente tutte le anomalie della sessione  
✅ **Architettura rispettata**: il Dominio ha ancora zero dipendenze esterne  
✅ **Test completa**: 15 unit test + 8 integration test totali (Fase 1 + Fase 2)  

**Esempio di output log dopo una partita completa**:

```
------------------------------------------------------------
SESSIONE AVVIATA: 2026-02-18 20:30:00
------------------------------------------------------------
2026-02-18 20:30:00 | INFO     | tombola_stark.system    | [SYS] Logger inizializzato — livello: INFO
2026-02-18 20:30:00 | INFO     | tombola_stark.game      | [GAME] Partita creata — giocatore='Lucia', cartelle=2, bot=3, tot_giocatori=4
2026-02-18 20:30:00 | INFO     | tombola_stark.game      | [GAME] Partita avviata — stato: in_corso, giocatori: 4
2026-02-18 20:30:01 | INFO     | tombola_stark.prizes    | [PRIZE] AMBO — giocatore='Bot 1', cartella=0, riga=1
2026-02-18 20:30:01 | INFO     | tombola_stark.prizes    | [PRIZE] TERNO — giocatore='Lucia', cartella=1, riga=0
2026-02-18 20:30:02 | INFO     | tombola_stark.prizes    | [PRIZE] TOMBOLA! — giocatore='Bot 2', cartella=0
2026-02-18 20:30:02 | INFO     | tombola_stark.game      | [GAME] Partita terminata per TOMBOLA al turno #47
2026-02-18 20:30:02 | INFO     | tombola_stark.game      | [GAME] === RIEPILOGO PARTITA ===
2026-02-18 20:30:02 | INFO     | tombola_stark.game      | [GAME] Turni giocati: 47 | Numeri estratti: 47/90
2026-02-18 20:30:02 | INFO     | tombola_stark.prizes    | [PRIZE] Riepilogo premi: 8 premi totali assegnati
2026-02-18 20:30:02 | INFO     | tombola_stark.prizes    | [PRIZE] Vincitore TOMBOLA: 'Bot 2'
------------------------------------------------------------
SESSIONE CHIUSA: 2026-02-18 20:30:02
------------------------------------------------------------
```

---

*Documento creato: 2026-02-18 | Ultima modifica: 2026-02-18*  
*Autore: AI Assistant + donato81*  
*Basato su*: `DESIGN_LOGGING_SYSTEM.md` (DESIGN FREEZE), `ARCHITECTURE.md` (ADR-001, ADR-003), `API.md`

---

**Fine Piano di Implementazione**
