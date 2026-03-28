---
type: plan
feature: conversione_test_pytest_unittest
status: READY
agent: Agent-Plan
version: 0.9.0
date: 2026-03-28
design: docs/2 - projects/DESIGN_conversione_test_pytest_unittest.md
branch: feature/conversione-test-pytest-unittest
---

# PLAN conversione_test_pytest_unittest v0.9.0

## Executive Summary

| Campo | Valore |
|---|---|
| Tipo | conversione / migrazione test |
| Feature | conversione_test_pytest_unittest |
| Priorita | critical path — stabilizzazione suite |
| Branch | feature/conversione-test-pytest-unittest |
| Versione target | v0.9.0 |
| Status | DRAFT |
| Design sorgente | [DESIGN_conversione_test_pytest_unittest.md](../2%20-%20projects/DESIGN_conversione_test_pytest_unittest.md) |

## Problema e Obiettivo

I file di test in `tests/unit/`, `tests/integration/` e `tests/flow/` contengono costrutti
strutturali legati a pytest (fixture, capsys, monkeypatch, mark, parametrize) che impediscono
la discovery e l'esecuzione verde con `python -m unittest discover`.

L'obiettivo di questo PLAN e tradurre la strategia di batching definita nel DESIGN in un
programma di lavoro incrementale, committabile per batch, che porti l'intera suite a girare
verde con il solo runner unittest standard.

## Dipendenze Pre-Implementazione

- Design approvato: [DESIGN_conversione_test_pytest_unittest.md](../2%20-%20projects/DESIGN_conversione_test_pytest_unittest.md) — status REVIEWED
- Report di analisi: [REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md](../4%20-%20reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md)
- File unittest di riferimento canonico: tutti i file `tests/*.py` gia verdi
- Runner disponibile: `python -m unittest discover` (venv attivo: `.venv`)
- Nessuna dipendenza funzionale da pytest consentita nei file convertiti

## Fasi di Implementazione

---

### Fase 0 — Baseline e pre-condizioni

**Obiettivo**: fissare il punto di partenza della suite, quantificare test gia verdi e
confermare che i file pytest incompatibili siano fuori dalla baseline verde.

**File coinvolti**: nessuno modificato

**Azioni**:
1. Eseguire `python -m unittest discover -s tests -p "test_*.py"` e registrare il conteggio
   dei test passsanti.
2. Verificare che i file pytest target siano effettivamente non scoperti o non verdi.
3. Annotare il numero di test verdi come baseline di riferimento per la Fase successiva.

**Criteri di completamento**:
- Baseline numerica documentata (test verdi / totale scoperto).
- Confermato che i file pytest non passanti non influenzano la baseline unittest.

**Rischi**: nessuno — operazione read-only.

**Commit**: nessun commit richiesto in questa fase.

---

### Fase 1 — Batch 1: recupero critico ad alto impatto

**Obiettivo**: convertire i file a piu alta densita di errori per sbloccare il maggior numero
di casi verde nel minor tempo.

**File da MODIFICARE**:
- `tests/unit/test_tui_commander.py`
- `tests/flow/test_flusso_game_loop.py`
- `tests/test_silent_controller.py`

**Azioni per ciascun file**:
1. Sostituire `@pytest.fixture` con `setUp` / `tearDown` o helper privati `_build_*`.
2. Sostituire `capsys` con `unittest.mock.patch('sys.stdout', new_callable=io.StringIO)`.
3. Sostituire `monkeypatch` con `unittest.mock.patch` e cleanup esplicito in `tearDown`.
4. Isolare il mock di `msvcrt` prima degli import del modulo sotto test (o nel `setUp`).
5. Avvolgere classi in `unittest.TestCase`; verificare naming `test_*` su tutti i metodi.
6. Eseguire il batch con `python -m unittest tests.unit.test_tui_commander
   tests.flow.test_flusso_game_loop tests.test_silent_controller` e raggiungere verde.

**Dipendenze**: Fase 0 completata.

**Rischi**:
- Mock di `msvcrt` che inquina `sys.modules` tra test — mitigazione: `setUp`/`tearDown` con
  `sys.modules` cleanup esplicito.
- Side effect finiti nei test di game loop — mitigazione: stato simulato locale per ogni test.
- Perdita di copertura semantica sul mock TUI — mitigazione: verificare che ogni asserzione
  su output resti invariata dopo la sostituzione di `capsys`.

**Criteri di completamento**:
- I tre file eseguiti verdi con `python -m unittest`.
- Nessun import di pytest nei file convertiti.
- Cleanup di `sys.modules`, stdout, patcher confermato in review del codice.

**Commit suggerito**:
```
test(batch1): converti test_tui_commander, test_flusso_game_loop, test_silent_controller in unittest
```

---

### Fase 2 — Batch 2: consolidamento TUI e input da tastiera

**Obiettivo**: rimuovere flakiness e incompatibilita strutturali residue nei test TUI e di
loop tastiera.

**File da MODIFICARE**:
- `tests/unit/test_tui_partita.py`
- `tests/integration/test_game_loop_tasti.py`

**Azioni**:
1. Convertire fixture pytest residue in `setUp`/`tearDown`.
2. Sostituire cattura output con `io.StringIO` patchato su `sys.stdout`.
3. Rendere deterministiche le sequenze di input da tastiera usando mock sequenziali.
4. Verificare assenza di leak di stato tra test consecutivi.
5. Eseguire il batch con `python -m unittest` e raggiungere verde.

**Dipendenze**: Fase 1 completata.

**Rischi**:
- Simulazione input da tastiera (`msvcrt.getch`) non deterministica — mitigazione: `side_effect`
  con lista di valori predefiniti e `StopIteration` esplicita.
- Stato TUI condiviso tra test — mitigazione: istanza separata per ogni test.

**Criteri di completamento**:
- I due file eseguiti verdi con `python -m unittest`.
- Nessun dipendenza pytest residua.
- Nessun leak di stato TUI o keyboard tra test.

**Commit suggerito**:
```
test(batch2): converti test_tui_partita e test_game_loop_tasti in unittest
```

---

### Fase 3 — Batch 3: classi a media frizione

**Obiettivo**: promuovere classi di test gia quasi conformi a pieno standard unittest.

**File da MODIFICARE**:
- `tests/unit/test_giocatore_automatico_bot_attivo.py`
- `tests/integration/test_partita_bot_attivo.py`
- `tests/unit/test_ui_terminale.py`

**Azioni**:
1. Completare la conversione delle classi esistenti a `unittest.TestCase`.
2. Sostituire `monkeypatch` con `patch` e gestire lifecycle del patcher.
3. Convertire `@pytest.mark.*` in skip condizionali `@unittest.skip` se necessario.
4. Sostituire `tmp_path` con `tempfile.TemporaryDirectory` e cleanup in `tearDown`.
5. Eseguire il batch e verificare verde.

**Dipendenze**: Fase 2 completata.

**Rischi**:
- Test parametrizzati presenti — mitigazione: convertire con `subTest` o espandere i casi
  mantenendo naming italiano descrittivo.
- Interazioni bot con stato condiviso — mitigazione: oggetti fresh per ogni test method.

**Criteri di completamento**:
- I tre file eseguiti verdi con `python -m unittest`.
- Parametrize rimosso o convertito a subTest.
- Nessuna directory temporanea lasciata su disco dopo il run.

**Commit suggerito**:
```
test(batch3): converti test_giocatore_automatico_bot_attivo, test_partita_bot_attivo, test_ui_terminale
```

---

### Fase 4 — Batch 4: funzioni standalone a bassa frizione

**Obiettivo**: incapsulare test con struttura semplice in TestCase uniformi senza rischio elevato.

**File da MODIFICARE**:
- `tests/unit/test_codici_loop.py`
- `tests/unit/test_imposta_focus_cartella_regression.py`
- `tests/unit/test_ottieni_giocatore_umano.py`
- `tests/unit/test_game_controller_loop.py`
- `tests/unit/test_renderer_report_finale.py`

**Azioni**:
1. Incapsulare funzioni di test standalone in classi `TestX(unittest.TestCase)`.
2. Estrarre setup condiviso in `setUp` se presente.
3. Rimuovere decoratori pytest non portabili.
4. Verificare discovery con `python -m unittest discover -s tests/unit`.

**Dipendenze**: Fase 3 completata.

**Rischi**:
- Funzioni che condividono stato implicito — mitigazione: portare lo stato in `setUp`.
- Nomi di test non coerenti con la convenzione italiana del corpus — mitigazione: rinominare
  con naming italiano descrittivo durante la conversione.

**Criteri di completamento**:
- I cinque file scoperti e verdi con `python -m unittest discover`.
- Naming coerente con il corpus gia verde.

**Commit suggerito**:
```
test(batch4): converti test standalone in TestCase — codici_loop, focus, ottieni_giocatore, controller_loop, renderer
```

---

### Fase 5 — Batch 5: logging e filesystem con cleanup rigoroso

**Obiettivo**: convertire i file che dipendono da `monkeypatch`, `tmp_path` e stato globale
del logger, imponendo cleanup rigoroso per ogni risorsa.

**File da MODIFICARE**:
- `tests/unit/test_game_logger.py`
- `tests/unit/test_event_logging.py`
- `tests/integration/test_event_coverage.py`
- `tests/integration/test_logging_integration.py`

**Azioni**:
1. Sostituire `tmp_path` con `tempfile.TemporaryDirectory`; registrare cleanup in `addCleanup`.
2. Sostituire `monkeypatch` su filesystem con `unittest.mock.patch` + ripristino esplicito.
3. Isolare singleton del logger per ogni test: reset in `setUp`, cleanup in `tearDown`.
4. Verificare assenza di handler residui dopo ogni test (check `len(logger.handlers)`).
5. Eseguire il batch e verificare verde.

**Dipendenze**: Fase 4 completata.

**Rischi**:
- Leak di handler sul logger singleton — mitigazione: `logger.handlers.clear()` in `tearDown`.
- File di log creati su disco durante i test — mitigazione: path sotto `tempfile.gettempdir()`,
  rimossi in `addCleanup`.
- Stato globale del modulo `game_logger` — mitigazione: reload del modulo o patch a livello
  di classe con `setUpClass`/`tearDownClass`.

**Criteri di completamento**:
- I quattro file eseguiti verdi con `python -m unittest`.
- Nessun file temporaneo residuo su disco dopo il run.
- Nessun handler logger residuo verificabile con check post-run.

**Commit suggerito**:
```
test(batch5): converti test_game_logger, test_event_logging, test_event_coverage, test_logging_integration
```

---

### Fase 6 — Validazione finale e chiusura

**Obiettivo**: confermare che l'intera suite e verde, la copertura e mantenuta e i criteri
di uniformita del DESIGN sono soddisfatti.

**File coinvolti**: nessuno modificato

**Azioni**:
1. Eseguire `python -m unittest discover -s tests -p "test_*.py"` sull'intera suite.
2. Verificare che il conteggio test verde sia uguale o superiore alla baseline Fase 0 piu
   i casi recuperati.
3. Eseguire `python -m py_compile tests/**/*.py` (o singoli file) per verifica sintattica.
4. Confrontare ciascun file convertito con la checklist di uniformita del DESIGN.
5. Aggiornare `CHANGELOG.md` con la sezione `[Unreleased]`.
6. Aggiornare `docs/API.md` e `docs/ARCHITECTURE.md` se la conversione ha rivelato
   differenze di contratto rilevanti.

**Criteri di completamento**:
- Suite verde al 100% con `python -m unittest discover`.
- Nessun file con `import pytest` residuo nei file convertiti.
- CHANGELOG.md aggiornato.
- Status PLAN escalato a COMPLETED su approvazione utente.

**Commit suggerito**:
```
test(validation): suite unittest verde — validazione finale feature conversione_test_pytest_unittest
```

---

## Test Plan

### Test di unita

- Ogni batch e validato eseguendo i file batch con `python -m unittest <moduli>`.
- Verifica sintattica: `python -m py_compile <file>` su ogni file convertito.

### Test di integrazione

- Esecuzione completa con `python -m unittest discover -s tests -p "test_*.py"` dopo ogni batch.
- Regression test: il conteggio test verdi non deve diminuire tra un batch e il successivo.

### Validazione uniformita

Per ogni file convertito verificare:
- `import unittest` presente, nessun `import pytest`.
- Classi ereditano da `unittest.TestCase`.
- `setUp`/`tearDown` o `addCleanup` per ogni risorsa patchata.
- Naming metodi `test_*` in italiano descrittivo.
- Nessun `@pytest.mark`, `@pytest.fixture`, `capsys`, `monkeypatch`, `tmp_path` residuo.

## Riferimenti

- Design: [DESIGN_conversione_test_pytest_unittest.md](../2%20-%20projects/DESIGN_conversione_test_pytest_unittest.md)
- Report analisi: [REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md](../4%20-%20reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md)
- TODO operativo: [TODO_conversione_test_pytest_unittest_v0.9.0.md](../5%20-%20todolist/TODO_conversione_test_pytest_unittest_v0.9.0.md)
- Coordinatore: [TODO.md](../todo.md)
