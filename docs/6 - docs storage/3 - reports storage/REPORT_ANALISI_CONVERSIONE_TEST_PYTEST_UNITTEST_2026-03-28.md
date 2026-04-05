## Metadati

tipo: report
titolo: Analisi conversione test pytest → unittest standard — Tombola Stark
data_creazione: 2026-03-28
agente: Agent-Analyze
stato: definitivo

---

## 1. Componenti coinvolti

### File pytest non conformi con fallimenti attivi (62 casi non-verdi)

| File | Posizione | Problema noto | Causa pytest-specifica |
|------|-----------|---------------|------------------------|
| `test_tui_commander.py` | `tests/unit/` | P1 — 46 errori setup | `@pytest.fixture(autouse=True)` + guard msvcrt condizionale + `@pytest.mark.unit` + `@pytest.mark.parametrize` |
| `test_flusso_game_loop.py` | `tests/flow/` | P2 — 13 fallimenti StopIteration | `@pytest.fixture`, `capsys`, `side_effect` lista finita |
| `test_silent_controller.py` | `tests/` | P4 — 1 fallimento ValueError | `@pytest.fixture` a livello modulo, classi non-TestCase, `capsys` |
| `test_tui_partita.py` | `tests/unit/` | P5 — test flaky | `@pytest.fixture`, stato globale msvcrt lasciato sporco |

### File pytest strutturalmente incompatibili (nessun fallimento attivo, ma non eseguibili da `unittest`)

| File | Posizione | Costrutto incompatibile |
|------|-----------|-------------------------|
| `test_giocatore_automatico_bot_attivo.py` | `tests/unit/` | Classe non-TestCase (`class TestGiocatoreAutomaticoBotAttivo`) |
| `test_partita_bot_attivo.py` | `tests/integration/` | Classe non-TestCase (`class TestPartitaBotAttivo`) |
| `test_ui_terminale.py` | `tests/unit/` | Classi non-TestCase (`TestValidazioneNome`, `TestValidazioneBot`) + `capsys` |
| `test_game_loop_tasti.py` | `tests/integration/` | `@pytest.fixture`, `@pytest.mark.integration`, guard msvcrt condizionale |
| `test_game_logger.py` | `tests/unit/` | `@pytest.fixture(autouse=True)`, `monkeypatch`, `tmp_path` |
| `test_event_logging.py` | `tests/unit/` | `@pytest.fixture(autouse=True)`, `monkeypatch`, `tmp_path` |
| `test_event_coverage.py` | `tests/integration/` | `@pytest.fixture(autouse=True)`, `monkeypatch`, `tmp_path` |
| `test_logging_integration.py` | `tests/integration/` | `@pytest.fixture`, `monkeypatch`, `tmp_path` |
| `test_codici_loop.py` | `tests/unit/` | Funzioni standalone senza classe (import `pytest`) |
| `test_renderer_report_finale.py` | `tests/unit/` | `@pytest.fixture`, funzioni standalone |
| `test_imposta_focus_cartella_regression.py` | `tests/unit/` | Funzioni standalone, import `pytest` |
| `test_ottieni_giocatore_umano.py` | `tests/unit/` | `@pytest.fixture`, funzioni standalone |
| `test_game_controller_loop.py` | `tests/unit/` | `@pytest.fixture`, funzioni standalone |

### File unittest già conformi (reference — NON da convertire)

| File | Posizione | Note |
|------|-----------|------|
| `test_cartella.py` | `tests/` | Riferimento canonico: `setUp()`, `class TestX(unittest.TestCase)` |
| `test_game_controller.py` | `tests/` | Riferimento canonico multi-classe |
| `test_giocatore_base.py` | `tests/` | Riferimento canonico |
| `test_giocatore_umano.py` | `tests/` | Riferimento canonico |
| `test_tabellone.py` | `tests/` | Riferimento canonico |
| `test_comandi_partita.py` | `tests/` | Riferimento canonico |
| `test_partita.py` | `tests/` | Già unittest — 1 failure P3 logico (non strutturale) |

---

## 2. Dipendenze

### Dipendenze pytest non portabili verso `unittest`

| Costrutto pytest | Occorrenze | File interessati | Equivalente unittest |
|-----------------|------------|------------------|---------------------|
| `@pytest.fixture` | 16 file | tutti i file non conformi | `setUp()` / `tearDown()` / helper privato `_crea_X()` |
| `@pytest.fixture(autouse=True)` | 5 file | `test_tui_commander`, `test_game_logger`, `test_event_logging`, `test_event_coverage`, `test_logging_integration` | `setUp()` + `tearDown()` |
| `capsys` / `capsys.readouterr()` | 5 file | `test_tui_commander`, `test_flusso_game_loop`, `test_silent_controller`, `test_tui_partita`, `test_ui_terminale` | `patch('sys.stdout', new_callable=io.StringIO)` |
| `monkeypatch.setattr()` | 4 file | `test_game_logger`, `test_event_logging`, `test_event_coverage`, `test_logging_integration` | `unittest.mock.patch()` come context manager + `addCleanup()` |
| `tmp_path` | 4 file | `test_game_logger`, `test_event_logging`, `test_event_coverage`, `test_logging_integration` | `tempfile.TemporaryDirectory()` in `setUp()` / `tearDown()` |
| `@pytest.mark.parametrize` | 3 file (est.) | `test_tui_commander`, `test_game_loop_tasti` | `self.subTest()` o espansione manuale |
| `@pytest.mark.unit` | 2 file | `test_tui_commander`, altri unit | da rimuovere (nessun equivalente) |
| `@pytest.mark.integration` | 1 file | `test_game_loop_tasti` | da rimuovere |
| Classe non-TestCase | 4 file | `test_giocatore_automatico_bot_attivo`, `test_partita_bot_attivo`, `test_ui_terminale`, `test_silent_controller` | aggiungere `(unittest.TestCase)` + trasformare fixture in `setUp()` |
| Funzioni standalone | 7 file | `test_codici_loop`, `test_renderer_report_finale`, `test_imposta_focus_cartella_regression`, `test_ottieni_giocatore_umano`, `test_game_controller_loop`, `test_tui_partita`, `test_flusso_game_loop` | incapsulare in `class TestX(unittest.TestCase)` con metodi `test_*` |

### Dipendenze cross-modulo che impattano il mock setup

- `bingo_game.ui.tui.tui_commander` importa `msvcrt` a livello di modulo.
  La guard condizionale `if "msvcrt" not in sys.modules` fallisce su Windows perché
  `msvcrt` è sempre disponibile come modulo reale, rendendo il mock inefficace.
  Questa logica deve diventare un'iniezione forzata (`sys.modules["msvcrt"] = MagicMock()`)
  eseguita in `setUp()` (o `setUpModule()`) prima di qualsiasi import del modulo TUI.

- `bingo_game.ui.tui.tui_partita` accede a `leggi_tasto` (da `tui_commander`) e a
  `partita_terminata` (da `game_controller`). Entrambi devono essere patchati come
  path stringa nel modulo target, non come oggetto diretto.

- `bingo_game.logging.game_logger` usa path assoluti per i file di log (`_LOG_DIR`,
  `_LOG_FILE`). Nei test di logging, questi devono essere patchati via
  `unittest.mock.patch()` prima di `GameLogger.initialize()`. In unittest, l'ordine
  del patch (prima dell'inizializzazione) è critico e deve essere garantito dal
  `setUp()` della classe, non da un fixture.

---

## 3. Rischi

### Rischio A — ALTO | Perdita di copertura su `test_flusso_game_loop.py`
Il file ha 12 scenari complessi di integrazione (`_loop_partita`). Durante la
conversione, ogni scenario usa `capsys` per catturare l'output TUI e `side_effect`
a lista finita. Se il `side_effect` della lista `partita_terminata` non viene
aggiornato contestualmente alla conversione della fixture, i 13 fallimenti P2
si trascinano nel codice convertito.

Mitigazione: Prima di convertire la struttura, correggere i `side_effect`
aggiungendo un valore `True` finale, oppure usare `side_effect=itertools.chain(...)`.

### Rischio B — ALTO | Isolamento incompleto del mock `msvcrt` in `setUp()`
Se `setUp()` non pulisce `sys.modules["msvcrt"]` tra i test, lo stato del mock
si accumula tra metodi. Su Windows, il modulo reale `msvcrt` non ha `reset_mock()`,
causando `AttributeError` identico al P1 attuale.

Mitigazione: In `setUp()`, iniettare forzatamente un `MagicMock()` fresco
(`sys.modules["msvcrt"] = MagicMock()`). In `tearDown()`, ripristinare o
eliminare (`del sys.modules["msvcrt"]` se necessario).

### Rischio C — MEDIO | Sostituzione `monkeypatch` con `patch()` nei test di logging
I test `test_game_logger` e `test_logging_integration` usano `monkeypatch.setattr()`
per patchare `_LOG_DIR` e `_LOG_FILE` prima di `GameLogger.initialize()`. In
unittest, `unittest.mock.patch()` come context manager o come decoratore garantisce
lo stesso ordine, ma il cleanup automatico richiede `addCleanup(patcher.stop)` per
evitare leak tra test class.

Mitigazione: Usare `patch()` come context manager dentro `setUp()` con
`self.addCleanup(patcher.stop)`.

### Rischio D — MEDIO | Sostituzione `tmp_path` nei test di logging
`tmp_path` è un pytest fixture che crea una directory temporanea unica per test.
In unittest, `tempfile.TemporaryDirectory()` è l'equivalente diretto, ma deve
essere esplicitamente creato in `setUp()` e distrutto in `tearDown()` (o via
`self.addCleanup(tmpdir.cleanup)`).

### Rischio E — BASSO | Test parametrizzati in `test_tui_commander.py`
Il file usa `@pytest.mark.parametrize` su alcuni test (es. tasti freccia direzionali,
tasti 1-6 per selezione cartella). In unittest, l'approccio più chiaro è
`self.subTest(tasto=..., nome=...)` dentro un loop, mantenendo il singolo metodo
`test_*` parametrizzato. Alternativa: espansione in metodi separati (più verboso
ma più leggibile da NVDA).

### Rischio F — BASSO | Test P3 in `test_partita.py` (non strutturale)
`test_get_stato_sintetico_coincide_con_get_stato_completo` fallisce per un'assunzione
logica errata, non per incompatibilità pytest. Il file è già unittest standard.
La conversione dello schema si riduce a correggere l'`assertEqual` in un subset check.
Non rientra nella conversione pytest→unittest ma va risolto parallelamente.

---

## 4. Vincoli accessibilità NVDA

- **Naming metodi test**: I metodi `test_*` devono avere nomi descrittivi in italiano
  (stessa convenzione dei file unittest di riferimento). NVDA legge il nome del metodo
  nel feedback del test runner; nomi criptici o abbreviati riducono la comprensibilità.

- **Sostituzione `capsys` con `io.StringIO`**: Il pattern corretto per NVDA è
  annotare chiaramente nel docstring il significato dell'output catturato, perché
  il test è un contratto di accessibilità indiretta (testa che il testo mostrato
  all'utente umano sia corretto). Le asserzioni sull'output devono essere leggibili
  come frasi: `self.assertIn("42", output, "Il numero estratto deve comparire nell'output")`.

- **Test flaky (P5)**: Un test che passa/fallisce in modo imprevedibile è inaccessibile
  per un utente che usa il feedback del runner per validare il proprio lavoro. La
  stabilizzazione del mock `msvcrt` in `setUp()` ha priorità di accessibilità oltre
  che tecnica.

- **Struttura classi non-TestCase**: Le classi `TestX` senza `unittest.TestCase`
  non vengono rilevate da `python -m unittest discover`. Questo rende invisibili
  quei test all'utente che usa il runner standard; il problema è un vincolo di
  accessibilità del workflow (non solo strutturale).

- **Lunghezza output nei test TUI**: I test che catturano output testuale della TUI
  devono mantenere le asserzioni sui testi chiave (numeri, messaggi di errore,
  conferme) perché questi testi sono letti da NVDA durante il gioco reale. Non
  indebolire le asserzioni di output durante la conversione.

---

## Strategia di conversione proposta

### Batch 0 — Pre-condizioni (da eseguire prima di qualsiasi conversione)

Nessuna modifica ai file di test. Verificare:
- Eseguire `py -3.10 -m unittest discover tests/` per confermare la baseline: solo
  i file già unittest vengono raccolti; i file pytest vengono ignorati silenziosamente.
- Identificare il conteggio dei test unittest attualmente verdi (baseline di partenza).

### Batch 1 — Priorità CRITICA (sblocca 60 dei 62 casi non-verdi)

File da convertire per primi perché ogni conversione qui sblocca molti casi in 1 passata:

1. `tests/unit/test_tui_commander.py`
   - Converti fixture `reset_msvcrt` → `setUp()` con iniezione forzata `sys.modules["msvcrt"] = MagicMock()`
   - Rimuovi `@pytest.mark.unit`
   - Converti `@pytest.mark.parametrize` → `self.subTest()` o espansione metodi
   - Incapsula tutte le funzioni in `class TestTuiCommander(unittest.TestCase)`
   - Rimuovi import `pytest`; mantieni `from unittest.mock import MagicMock, patch`
   - Effetto atteso: sblocca 46 errori P1 + 19 warning P6 (parziale)

2. `tests/flow/test_flusso_game_loop.py`
   - Converti `@pytest.fixture partita_mock` → metodo `setUp()` nella classe
   - Converti `capsys` → `io.StringIO` con `patch('sys.stdout', ...)`
   - Correggi `side_effect=[False, False, False]` → `side_effect=itertools.chain(repeat(False, N), [True])`
     oppure usa `side_effect=lambda _: False` con exit controllata da contatore
   - Incapsula in `class TestFlussoGameLoop(unittest.TestCase)`
   - Effetto atteso: sblocca 13 fallimenti P2

3. `tests/test_silent_controller.py`
   - Le classi `TestControllerSilenzioso` e `TestContrattiRitorno` hanno già la
     struttura class-based; aggiungere `(unittest.TestCase)` a entrambe
   - Converti `@pytest.fixture partita_mock` e `@pytest.fixture partita_terminata_mock`
     → `setUp()` + attributi `self.partita_mock` / `self.partita_terminata_mock`
   - Converti `capsys` → `io.StringIO` con `patch()`
   - Aggiungi `return_value` per `get_stato_sintetico` nel mock (fix P4)
   - Effetto atteso: sblocca 1 fallimento P4

### Batch 2 — Priorità ALTA (stabilizza flakiness + incompatibilità strutturale TUI)

4. `tests/unit/test_tui_partita.py`
   - Converti `@pytest.fixture partita_mock` e `@pytest.fixture partita_mock_con_giocatore`
     → `setUp()` / helper privato `_crea_partita_mock()`
   - Incapsula tutte le funzioni in `class TestTuiPartita(unittest.TestCase)`
   - Rimuovi import `pytest`
   - Effetto atteso: stabilizza P5 (stato msvcrt pulito per ogni setUp)

5. `tests/integration/test_game_loop_tasti.py`
   - Converti `@pytest.fixture mock_partita` → `setUp()`
   - Rimuovi `@pytest.mark.integration`
   - Correggi guard msvcrt → iniezione forzata in `setUpModule()` o `setUp()`
   - Incapsula in `class TestGameLoopTasti(unittest.TestCase)`

### Batch 3 — Priorità MEDIA (classi non-TestCase con corpo già orientato alla classe)

6. `tests/unit/test_giocatore_automatico_bot_attivo.py`
   - Aggiungere `(unittest.TestCase)` a `class TestGiocatoreAutomaticoBotAttivo`
   - Rimuovi import `pytest`
   - Nessuna fixture complessa; conversione rapida

7. `tests/integration/test_partita_bot_attivo.py`
   - Aggiungere `(unittest.TestCase)` a `class TestPartitaBotAttivo`
   - Rimuovi import `pytest`
   - Nessuna fixture complessa; conversione rapida

8. `tests/unit/test_ui_terminale.py`
   - Aggiungere `(unittest.TestCase)` a `class TestValidazioneNome` e
     `class TestValidazioneBot`
   - Converti `capsys: pytest.CaptureFixture` → `io.StringIO` con `patch()`
   - Rimuovi import `pytest`

### Batch 4 — Priorità BASSA (funzioni standalone, minima frizione)

File con funzioni pytest standalone senza dipendenze complesse:

9. `tests/unit/test_codici_loop.py`
10. `tests/unit/test_imposta_focus_cartella_regression.py`
11. `tests/unit/test_ottieni_giocatore_umano.py`
12. `tests/unit/test_game_controller_loop.py`
13. `tests/unit/test_renderer_report_finale.py`

Per tutti: incapsulare le funzioni `test_*` in `class TestX(unittest.TestCase)`,
convertire `@pytest.fixture` → `setUp()` con attributo `self.X = ...`, rimuovere
import `pytest`.

### Batch 5 — Priorità BASSA (monkeypatch + tmp_path — maggiore lavoro di conversione)

File con dipendenza da `monkeypatch` e `tmp_path`:

14. `tests/unit/test_game_logger.py`
15. `tests/unit/test_event_logging.py`
16. `tests/integration/test_event_coverage.py`
17. `tests/integration/test_logging_integration.py`

Per tutti:
- `monkeypatch.setattr(module, attr, value)` → `patch('module.attr', value)` +
  `self.addCleanup(patcher.stop)`
- `tmp_path` → `tempfile.TemporaryDirectory()` in `setUp()` con
  `self.addCleanup(self._tmpdir.cleanup)`
- `@pytest.fixture(autouse=True) reset_logger` → `setUp()` + `tearDown()` con
  `GameLogger.shutdown()` e `GameLogger._initialized = False`

### Correzione parallela (non conversione strutturale)

- `tests/test_partita.py` riga 1381 (P3): correggere
  `self.assertEqual(stato_sintetico, stato_completo)` in subset check:
  `for k in stato_sintetico: self.assertEqual(stato_sintetico[k], stato_completo[k])`
  File già unittest — intervento chirurgico, non conversione.
