---
type: report
titolo: Diagnostica progetto post-rimozione TUI — Tombola Stark
data: 2026-03-28
agente: Agent-Analyze
versione_progetto: 0.9.0 (branch main)
commit_analizzati: 093fe23, 01fc7e3, 3fca45b
---

# Diagnostica progetto post-rimozione TUI — 2026-03-28

## Sommario esecutivo

Il repository ha subito due commit significativi che non erano ancora
riflessi nella documentazione ufficiale. Questo report fotografa lo
stato attuale del progetto (codice, test, docs) e classifica le
incongruenze riscontrate per priorità di intervento.

- Commit `01fc7e3` — rimozione di 11 file TUI e relativi test (3 301 righe)
- Commit `3fca45b` — migrazione test a unittest, riorganizzazione docs

### Stato badge suite test (post-rimozione TUI)

| Metrica | Valore |
|---------|--------|
| Test totali eseguiti | 351 |
| OK | 319 |
| Skipped | 1 |
| ERROR | 32 |
| FAIL | 0 |

---

## 1 — Moduli sorgente rimasti

### Nucleo dominio (invariato, stabile)

| Modulo | Stato |
|--------|-------|
| `bingo_game/tabellone.py` | OK |
| `bingo_game/cartella.py` | OK |
| `bingo_game/partita.py` | OK |
| `bingo_game/game_controller.py` | OK |
| `bingo_game/comandi_partita.py` | **PROBLEMA** — vedi sezione 3 |
| `bingo_game/utils.py` | OK |
| `bingo_game/players/giocatore_base.py` | OK |
| `bingo_game/players/giocatore_umano.py` | OK |
| `bingo_game/players/giocatore_automatico.py` | OK |
| `bingo_game/players/helper_focus.py` | OK |
| `bingo_game/players/helper_reclami_focus.py` | OK |
| `bingo_game/logging/game_logger.py` | OK |
| `bingo_game/events/` (tutti i moduli) | OK |
| `bingo_game/exceptions/` (tutti i moduli) | OK |
| `bingo_game/validations/` (tutti i moduli) | OK |

### Layer UI (parzialmente rimosso)

| Modulo | Stato |
|--------|-------|
| `bingo_game/ui/__init__.py` | OK (vuoto) |
| `bingo_game/ui/locales/it.py` | **ORFANO** — nessun consumer attivo post-TUI |
| `bingo_game/ui/locales/__init__.py` | **ORFANO** — nessun consumer attivo post-TUI |
| `bingo_game/ui/renderers/renderer_terminal.py` | **ORFANO** — importa locali TUI rimosse |
| `bingo_game/ui/tui/__init__.py` | **SVUOTATO** — directory rimasta vuota |
| `main.py` | **ROTTO** — importa `ui_terminale.TerminalUI` rimossa |

---

## 2 — Inventario file test: presenti vs rimossi

### File test rimossi nel commit 01fc7e3

| File rimosso | Copertura persa |
|---|---|
| `tests/unit/test_tui_commander.py` | 13 test — `tui_commander` |
| `tests/unit/test_tui_partita.py` | 27 test — `tui_partita` funzioni dispatch |
| `tests/unit/test_ui_terminale.py` | 8 test — `TerminalUI` |
| `tests/unit/test_codici_loop.py` | ~16 test — costanti `codici_loop` |
| `tests/integration/test_game_loop_tasti.py` | 6 test — game loop integration |
| `tests/flow/test_flusso_game_loop.py` | 12 test — scenari E2E |
| (la cartella `tests/flow/` è scomparsa) | — |

### File test rimasti (attivi)

```
tests/test_cartella.py
tests/test_comandi_partita.py         ← 30 ERROR UnicodeEncodeError
tests/test_game_controller.py         ← 2 ERROR UnicodeEncodeError
tests/test_giocatore_base.py
tests/test_giocatore_umano.py
tests/test_partita.py
tests/test_silent_controller.py
tests/test_tabellone.py
tests/integration/test_event_coverage.py
tests/integration/test_logging_integration.py
tests/integration/test_partita_bot_attivo.py
tests/unit/test_event_logging.py
tests/unit/test_game_controller_loop.py
tests/unit/test_game_logger.py
tests/unit/test_giocatore_automatico_bot_attivo.py
tests/unit/test_imposta_focus_cartella_regression.py
tests/unit/test_ottieni_giocatore_umano.py
tests/unit/test_renderer_report_finale.py
```

---

## 3 — Bug/problemi attivi nel codice sorgente

### BUG-1 · CRITICO — `comandi_partita.py`: print() con emoji Unicode

**Causa**: `bingo_game/comandi_partita.py` contiene 18 chiamate `print()` con
emoji Unicode (es. `✅ \u2705`, `❌ \u274c`, `🚀 \u1F680`). Su Windows con
encoding di console `cp1252`, queste righe sollevano `UnicodeEncodeError`
ogni volta che vengono eseguite.

**Effetto**: 30 test di `test_comandi_partita.py` falliscono con ERROR.

**File coinvolti**:
- `bingo_game/comandi_partita.py` — righe 72, 76, 91, 96, 111, 117, 119, 121,
  136, 141, 144, 159, 164, 179, 184, 199, 204, 207

**Violazione aggiuntiva**: la codebase vieta `print()` in `src/` (o in
`bingo_game/` per questo progetto). Il modulo `comandi_partita.py` produce
output diretto su stdout invece di loggare o emettere eventi.

**Soluzione indicata**: rimuovere tutte le `print()` da `comandi_partita.py`
e sostituirle con `_log_safe()` sullo stile già usato in `game_controller.py`.

---

### BUG-2 · CRITICO — `test_game_controller.py`: print() con emoji Unicode

**Causa**: due `print()` con emoji Unicode nelle righe 470 e 780.

**Effetto**: 2 test di `test_game_controller.py` falliscono con ERROR.

**File coinvolto**:
- `tests/test_game_controller.py` — righe 470, 780

**Soluzione indicata**: rimuovere i `print()` dai test (non sono asserzioni,
sono solo log informativi).

---

### BUG-3 · ALTO — `main.py`: importa modulo rimosso

**Causa**: `main.py` importa `TerminalUI` da `bingo_game.ui.ui_terminale`,
file eliminato nel commit `01fc7e3`.

**Effetto**: il programma non si avvia (`ImportError` immediato).

**Soluzione indicata**: aggiornare `main.py` con un entry point temporaneo
(placeholder, stub, o startup basato sul solo dominio) finché non viene
definita una nuova interfaccia utente.

---

### WARNING-1 · MEDIO — `renderer_terminal.py`: modulo orfano con import interni validi

**Causa**: `bingo_game/ui/renderers/renderer_terminal.py` importa locales TUI
(`MESSAGGI_ERRORI`, `MESSAGGI_EVENTI` da `bingo_game.ui.locales.it`) che
esistono ancora su disco. Il renderer non è rotto a livello di import, ma non
ha più consumer (la TUI che lo usava è stata rimossa).

**Effetto**: copertura test di `test_unit/test_renderer_report_finale.py` rimane
attiva (8 test, tutti OK). Il modulo è funzionalmente isolato.

**Azione suggerita**: decidere se mantenere il renderer come base per una nuova
UI o rimuoverlo con un'operazione dedicata.

---

### WARNING-2 · MEDIO — `bingo_game/ui/locales/it.py`: orfano parziale

**Causa**: dopo la rimozione della TUI, `it.py` contiene chiavi progettate per
la TUI rimossa (`MESSAGGI_CONFIGURAZIONE`, chiavi `LOOP_*`,
`MESSAGGI_CONTROLLER`). Solo le chiavi usate da `renderer_terminal.py`
(`MESSAGGI_ERRORI`, `MESSAGGI_EVENTI`, `MESSAGGI_OUTPUT_UI_UMANI`,
`MESSAGGI_SISTEMA`) hanno ancora consumer attivi.

**Effetto**: nessun errore runtime, ma il modulo trasporta payload inutilizzato.

---

### WARNING-3 · BASSO — `bingo_game/events/codici_loop.py`: orfano

**Causa**: le costanti `LOOP_*` erano usate esclusivamente dalla TUI rimossa.

**Effetto**: il modulo è importabile ma nessun consumer attivo lo usa.

---

## 4 — Incongruenze documentazione vs stato attuale

### CHANGELOG.md

| Sezione `[Unreleased]` | Incongruenza |
|---|---|
| Voci `Added` per `tui_commander.py`, `codici_tasti_tui.py`, `tui_partita.py`, test TUI | File rimossi — le voci Added dovrebbero essere integrate da una voce `Removed` corrispondente |
| Voci `Changed` che citano `tui_partita.py` (v0.11.0) | File rimosso |
| Nessuna voce `Removed` per i commit `01fc7e3` e `3fca45b` | Mancano le voci di changelog per la rimozione della TUI |

### docs/API.md

| Sezione | Incongruenza |
|---|---|
| `Modulo: bingo_game/ui/ui_terminale.py` (riga 1622) | File rimosso — sezione obsoleta |
| `Modulo: bingo_game/ui/tui/tui_partita.py` (riga 1669) | File rimosso — sezione obsoleta |
| Changelog API v0.9.0: cita `_loop_partita()` in `tui_partita.py` (riga 1707) | File rimosso |
| Changelog API v0.8.0: cita `ui_terminale.py` guardie TUI (riga 1708) | File rimosso |
| Changelog API v0.7.0: cita `TerminalUI` in `ui_terminale.py` (riga 1709) | File rimosso |
| Firma `visualizza_ultimi_numeri_estratti()`: aggiornata sessione precedente | OK |

### docs/ARCHITECTURE.md

| Sezione | Incongruenza |
|---|---|
| Tabella componenti UI (riga 188-191) | Cita `ui_terminale.py`, `tui_partita.py`, `tui_commander.py`, `codici_tasti_tui.py` — tutti rimossi |
| Struttura directory albero (riga 485-490) | Cita `ui_terminale.py`, `tui_partita.py`, `tui_commander.py`, `codici_tasti_tui.py` — tutti rimossi |
| Vincolo architetturale v0.9.0 (riga 214) | Cita `tui_partita.py` — file rimosso |
| Diagramma dipendenze (riga 81) | Cita `ui_terminale.py` — file rimosso |
| Sezione tech stack Testing (riga 55) | Già corretto a `unittest` nella sessione precedente |

### README.md

| Sezione | Incongruenza |
|---|---|
| `## 🕹️ Come si gioca (v0.9.1)` (riga 87) | Descrive comandi TUI (`p s c v q ?`) che dipendono dalla TUI rimossa |
| `## Tasti Rapidi (v0.10.0)` (riga 105+) | Descrive tasti msvcrt/tui_commander — modulo rimosso |
| Struttura albero directory | Già corretta nella sessione precedente (docs/ + unittest) |

---

## 5 — Analisi copertura test post-rimozione

### Test attualmente verdi (senza errori): 319

Copertura effettiva del nucleo dominio:

| Area coperta | File test | Test count stimato |
|---|---|---|
| Cartella | `test_cartella.py` | ~30 |
| Partita | `test_partita.py` | ~25 |
| Tabellone | `test_tabellone.py` | ~15 |
| GiocatoreBase | `test_giocatore_base.py` | ~20 |
| GiocatoreUmano | `test_giocatore_umano.py` | ~40 |
| GameController | `test_game_controller.py` | ~60 (meno i 2 ERROR) |
| GameController loop | `test_game_controller_loop.py` | ~10 |
| GiocatoreAutomatico | `test_giocatore_automatico_bot_attivo.py` | ~10 |
| Bot attivo | `test_partita_bot_attivo.py` | ~10 |
| Logging | `test_game_logger.py`, `test_event_logging.py`, `test_logging_integration.py`, `test_event_coverage.py` | ~23 |
| Focus cartella | `test_imposta_focus_cartella_regression.py` | ~5 |
| Ottieni giocatore | `test_ottieni_giocatore_umano.py` | ~10 |
| Renderer | `test_renderer_report_finale.py` | ~8 |
| Silent controller | `test_silent_controller.py` | ~15 |

### Test con ERROR: 32

Tutti riconducibili a BUG-1 e BUG-2 (UnicodeEncodeError da emoji in
`comandi_partita.py` e `test_game_controller.py`).

---

## 6 — Moduli con funzioni senza consumer post-TUI

| Modulo | Funzione/simbolo | Consumer pre-TUI | Consumer post-TUI |
|---|---|---|---|
| `game_controller.py` | `ottieni_giocatore_umano()` | `tui_partita.py` (rimosso) | nessuno diretto |
| `game_controller.py` | `imposta_focus_cartella()`, `esegui_azione_giocatore()`, `riepilogo_cartella_corrente()` (wrappers v0.11.0) | `tui_partita.py` (rimosso) | nessuno diretto |
| `events/codici_loop.py` | tutte le costanti `LOOP_*` | `tui_partita.py` (rimosso) | nessuno |
| `ui/locales/it.py` | chiavi `LOOP_*`, `MESSAGGI_CONFIGURAZIONE` | TUI rimossa | nessuno |

---

## 7 — Priorità interventi

### P1 — Bloccanti (rompono test e/o avvio)

- Rimuovere print() con emoji da `bingo_game/comandi_partita.py` (18 occorrenze)
- Rimuovere print() con emoji da `tests/test_game_controller.py` (2 occorrenze)
- Aggiornare `main.py` con un entry point non rotto

### P2 — Documentazione (incoerenza vs stato attuale)

- Aggiornare `CHANGELOG.md`: aggiungere voce `Removed` per file TUI eliminati
- Aggiornare `docs/API.md`: rimuovere sezioni `ui_terminale.py` e `tui_partita.py`
- Aggiornare `docs/ARCHITECTURE.md`: rimuovere righe che citano file rimossi
- Aggiornare `README.md`: rimuovere sezioni "Come si gioca" e "Tasti Rapidi" legate alla TUI rimossa

### P3 — Pulizia codebase (orfani)

- Valutare se mantenere o rimuovere `bingo_game/ui/renderers/renderer_terminal.py`
- Valutare se mantenere o rimuovere `bingo_game/events/codici_loop.py`
- Valutare se mantenere o ridurre `bingo_game/ui/locales/it.py`
- Decidere il destino dei wrapper v0.11.0 di `game_controller.py` senza consumer

---

## 8 — Commit analizzati

| Commit | Messaggio | Impatto |
|---|---|---|
| `093fe23` | Move tests/flow to bingo_game/ui/tui | Move non andato a buon fine: `tests/flow/` è scomparsa, `bingo_game/ui/tui/` contiene solo `__init__.py` vuoto |
| `01fc7e3` | Remove TUI modules and related tests | Rimossi 11 file, 3 301 righe. Rompe `main.py` |
| `3fca45b` | Switch tests to unittest and reorganize docs | Migrazione test framework + coordinamento doc |

---

## Conclusione

Il nucleo dominio del progetto (Tabellone, Cartella, Partita, GiocatoreBase,
GiocatoreUmano, GiocatoreAutomatico, GameController, GameLogger) è **stabile e
test-coperto**. I 32 errori della suite sono **tutti risolvibili** con la
rimozione di print() con emoji da `comandi_partita.py` e `test_game_controller.py`.

La documentazione (CHANGELOG, API, ARCHITECTURE, README) richiede aggiornamento
sistematico per riflettere l'eliminazione dei file TUI e lo stato del progetto
come **motore di gioco senza interfaccia terminale**.

Il layer UI è attualmente in uno stato di transizione: i sub-moduli
`locales/`, `renderers/` e la directory `tui/` (vuota) sono presenti ma orfani.
Il progetto necessita di una decisione architetturale su quale sarà la nuova
interfaccia utente (GUI wxPython? API REST? SDK?) prima di procedere con la
pulizia definitiva.
