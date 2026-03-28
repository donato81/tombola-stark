---
type: todo
feature: conversione_test_pytest_unittest
status: DRAFT
version: 0.9.0
date: 2026-03-28
plan: docs/3 - coding plans/PLAN_conversione_test_pytest_unittest_v0.9.0.md
---

# TODO conversione_test_pytest_unittest v0.9.0

Piano padre: [PLAN_conversione_test_pytest_unittest_v0.9.0.md](../3%20-%20coding%20plans/PLAN_conversione_test_pytest_unittest_v0.9.0.md)

Istruzioni per Agent-Code: esegui una fase alla volta. Dopo ogni fase esegui il batch
con `python -m unittest` e verifica il verde prima di proseguire. Non passare alla fase
successiva se il batch corrente non e verde.

---

## Fase 0 — Baseline e pre-condizioni

- [ ] Eseguire `python -m unittest discover -s tests -p "test_*.py"` e annotare il conteggio
      dei test verdi.
- [ ] Verificare che i file pytest target non siano nella baseline verde.
- [ ] Documentare la baseline numerica (es. `XX test OK, YY errori/fallimenti`).

Criteri: baseline numerica annotata, nessun commit richiesto.

---

## Fase 1 — Batch 1: recupero critico ad alto impatto

File target:
- `tests/unit/test_tui_commander.py`
- `tests/flow/test_flusso_game_loop.py`
- `tests/test_silent_controller.py`

- [ ] `test_tui_commander.py`: rimuovere `@pytest.fixture`, convertire in `setUp`/`tearDown`.
- [ ] `test_tui_commander.py`: sostituire `capsys` con patch di `sys.stdout` + `io.StringIO`.
- [ ] `test_tui_commander.py`: sostituire `monkeypatch` con `unittest.mock.patch` + cleanup.
- [ ] `test_tui_commander.py`: isolare mock `msvcrt` in `setUp`, cleanup in `tearDown`.
- [ ] `test_flusso_game_loop.py`: convertire fixture e side effect finiti.
- [ ] `test_flusso_game_loop.py`: rendere il setup dello stato di gioco locale e deterministico.
- [ ] `test_silent_controller.py`: convertire fixture e mock globali in TestCase standard.
- [ ] Eseguire batch 1: `python -m unittest tests.unit.test_tui_commander
      tests.flow.test_flusso_game_loop tests.test_silent_controller`.
- [ ] Verde confermato — nessun `import pytest` residuo nei tre file.
- [ ] Commit: `test(batch1): converti test_tui_commander, test_flusso_game_loop, test_silent_controller`

---

## Fase 2 — Batch 2: consolidamento TUI e input da tastiera

File target:
- `tests/unit/test_tui_partita.py`
- `tests/integration/test_game_loop_tasti.py`

- [ ] `test_tui_partita.py`: convertire fixture pytest in `setUp`/`tearDown`.
- [ ] `test_tui_partita.py`: sostituire cattura output con `io.StringIO` patchato.
- [ ] `test_game_loop_tasti.py`: rendere deterministiche le sequenze di input tastiera
      (`side_effect` con lista + `StopIteration`).
- [ ] `test_game_loop_tasti.py`: verificare assenza di leak di stato tra test consecutivi.
- [ ] Eseguire batch 2: `python -m unittest tests.unit.test_tui_partita
      tests.integration.test_game_loop_tasti`.
- [ ] Verde confermato — nessun dipendenza pytest residua.
- [ ] Commit: `test(batch2): converti test_tui_partita e test_game_loop_tasti in unittest`

---

## Fase 3 — Batch 3: classi a media frizione

File target:
- `tests/unit/test_giocatore_automatico_bot_attivo.py`
- `tests/integration/test_partita_bot_attivo.py`
- `tests/unit/test_ui_terminale.py`

- [ ] `test_giocatore_automatico_bot_attivo.py`: completare conversione a `TestCase`.
- [ ] `test_giocatore_automatico_bot_attivo.py`: convertire `parametrize` in `subTest`
      o casi espansi con naming italiano.
- [ ] `test_partita_bot_attivo.py`: oggetti fresh per ogni test method, rimuovere fixture
      di sessione.
- [ ] `test_ui_terminale.py`: sostituire `monkeypatch` con `patch`; `tmp_path` con
      `tempfile.TemporaryDirectory` + cleanup.
- [ ] Eseguire batch 3: `python -m unittest tests.unit.test_giocatore_automatico_bot_attivo
      tests.integration.test_partita_bot_attivo tests.unit.test_ui_terminale`.
- [ ] Verde confermato — nessuna directory temporanea lasciata su disco.
- [ ] Commit: `test(batch3): converti test_giocatore_automatico_bot_attivo, test_partita_bot_attivo, test_ui_terminale`

---

## Fase 4 — Batch 4: funzioni standalone a bassa frizione

File target:
- `tests/unit/test_codici_loop.py`
- `tests/unit/test_imposta_focus_cartella_regression.py`
- `tests/unit/test_ottieni_giocatore_umano.py`
- `tests/unit/test_game_controller_loop.py`
- `tests/unit/test_renderer_report_finale.py`

- [ ] Incapsulare funzioni standalone in classi `TestX(unittest.TestCase)` per ciascuno
      dei cinque file.
- [ ] Estrarre setup condiviso in `setUp` dove presente.
- [ ] Rimuovere decoratori pytest non portabili.
- [ ] Verificare naming italiano descrittivo su tutti i metodi `test_*`.
- [ ] Eseguire `python -m unittest discover -s tests/unit` e verificare i cinque file
      scoperti e verdi.
- [ ] Commit: `test(batch4): converti test standalone in TestCase — codici_loop, focus, ottieni_giocatore, controller_loop, renderer`

---

## Fase 5 — Batch 5: logging e filesystem con cleanup rigoroso

File target:
- `tests/unit/test_game_logger.py`
- `tests/unit/test_event_logging.py`
- `tests/integration/test_event_coverage.py`
- `tests/integration/test_logging_integration.py`

- [ ] `test_game_logger.py`: sostituire `tmp_path` con `tempfile.TemporaryDirectory`;
      registrare cleanup con `addCleanup`.
- [ ] `test_game_logger.py`: isolare singleton logger in `setUp`; `logger.handlers.clear()`
      in `tearDown`.
- [ ] `test_event_logging.py`: sostituire `monkeypatch` su filesystem con `patch` +
      ripristino esplicito.
- [ ] `test_event_coverage.py`: verificare assenza di handler residui dopo ogni test.
- [ ] `test_logging_integration.py`: tutti i file di log sotto `tempfile.gettempdir()`,
      rimossi da `addCleanup`.
- [ ] Eseguire batch 5: `python -m unittest tests.unit.test_game_logger
      tests.unit.test_event_logging tests.integration.test_event_coverage
      tests.integration.test_logging_integration`.
- [ ] Verde confermato — nessun file temporaneo residuo, nessun handler logger residuo.
- [ ] Commit: `test(batch5): converti test_game_logger, test_event_logging, test_event_coverage, test_logging_integration`

---

## Fase 6 — Validazione finale e chiusura

- [ ] Eseguire `python -m unittest discover -s tests -p "test_*.py"` sull'intera suite.
- [ ] Verificare che il conteggio verde sia uguale o superiore a baseline Fase 0 + casi
      recuperati previsti.
- [ ] Eseguire `python -m py_compile` su tutti i file convertiti (nessun errore).
- [ ] Verificare che nessun file convertito contenga `import pytest` (grep).
- [ ] Aggiornare `CHANGELOG.md` sezione `[Unreleased]`.
- [ ] Aggiornare `docs/API.md` se la conversione ha rivelato differenze di contratto.
- [ ] Escalare status PLAN a COMPLETED dopo conferma utente.
- [ ] Commit: `test(validation): suite unittest verde — validazione finale conversione_test_pytest_unittest`
