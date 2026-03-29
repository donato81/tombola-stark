# Registro delle Modifiche

Tutte le modifiche rilevanti a questo progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Versionamento Semantico](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Fixed
- `main.py`: sostituisce l'import rotto di `TerminalUI` con un placeholder
  temporaneo; il programma torna avviabile con messaggio informativo sullo
  stato di transizione verso la nuova interfaccia.
- `tests/test_giocatore_umano.py`: modernizza i 20 test di navigazione riga su
  `EsitoAzione`, `EventoNavigazioneRiga` ed `EventoNavigazioneRigaAvanzata`,
  eliminando i confronti fragili su testo renderizzato e preservando la suite
  `unittest` verde; in validazione viene corretto anche un test legacy su
  `sposta_focus_colonna_sinistra_avanzata` ancora ancorato alla parola `vuota`.
 - `tests/test_giocatore_umano.py`: tranche 2 — modernizza 8 test legacy del
   gruppo "colonna sinistra" e stabilizza il blocco avanzato già strutturato
   (`test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni`),
   validazione: 67 test OK sul file, 366 test OK sulla suite completa.
 - `tests/test_giocatore_umano.py`: tranche 3 — modernizza i test del gruppo
   "colonna destra" (base + avanzata, 11 test aggiornati), sostituendo assertion
   su testo renderizzato con assertion strutturate su `EsitoAzione`,
   `EventoNavigazioneColonna` ed `EventoNavigazioneColonnaAvanzata`. Verifica
   finale: 67 test OK su `tests/test_giocatore_umano.py` (file target), 366 test
   OK sulla suite completa, 1 test skipped. Report e artefatti associati:
   `docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md`,
   `docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md`,
   `docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md`.

---

## [0.9.2] — 2026-03-28

### Added
- `docs/4 - reports/REPORT_ANALISI_STATO_2026-03-27.md`: aggiunge report di analisi
  stato progetto con roadmap prioritizzata (v0.11.0 → v2.0.0+).
- `docs/4 - reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md`:
  aggiunge il findings report per la conversione dei test pytest non verdi verso
  unittest standard, con batch di priorita, dipendenze e rischi.
- `docs/2 - projects/DESIGN_conversione_test_pytest_unittest.md`: aggiunge il
  documento di design della migrazione pytest → unittest, con strategia di
  uniformita, batching e criteri di accettazione.
- `docs/3 - coding plans/PLAN_conversione_test_pytest_unittest_v0.9.0.md`:
  aggiunge il piano operativo READY per la conversione incrementale dei test in
  sette fasi, dalla baseline alla validazione finale.
- `docs/5 - todolist/TODO_conversione_test_pytest_unittest_v0.9.0.md`:
  aggiunge la checklist operativa associata al piano di conversione dei test.
- `docs/5 - todolist/README.md`: aggiunge il README della cartella canonica per i
  TODO operativi, allineato al validatore documentale.
- `docs/4 - reports/REPORT_FIX_UNICODE_PRINT_2026-03-28.md`: aggiunge analisi
  mirata del fix P1 su `print()` con emoji (`comandi_partita.py`,
  `test_game_controller.py`) con inventario righe e impatto suite.
- `docs/2 - projects/DESIGN_fix_unicode_print.md`: aggiunge design della
  rimozione pura dei `print()` Unicode nel perimetro applicativo/test,
  con vincoli e criteri di accettazione.
- `docs/3 - coding plans/PLAN_fix_unicode_print_v0.9.1.md`: aggiunge piano
  operativo v0.9.1 per baseline, due fix incrementali e validazione finale.
- `docs/5 - todolist/TODO_fix_unicode_print_v0.9.1.md`: aggiunge checklist
  esecutiva READY allineata al piano `PLAN_fix_unicode_print_v0.9.1.md`.

### Fixed
- `bingo_game/comandi_partita.py`, `tests/test_game_controller.py`: rimuove i
  `print()` con emoji Unicode che causavano `UnicodeEncodeError` su Windows e
  ripristina la suite `unittest` verde (351 test OK).

### Changed
- `CHANGELOG.md`, `docs/API.md`, `docs/ARCHITECTURE.md`, `README.md`: riallinea la
  documentazione pubblica allo stato post-rimozione TUI senza riscrivere la
  cronologia delle release gia' versionate.
- `tests/test_silent_controller.py`: completa la migrazione pytest -> unittest con
  TestCase, setUp, helper `_build_*`, cattura stdout via `io.StringIO` e
  `self.assertRaises`; il TODO `migrazione_test_silent_controller_unittest`
  passa a `COMPLETED`.
- `tests/test_silent_controller.py`: migrazione completata e validata; eseguiti
  i test con `python -m unittest tests.test_silent_controller` (v0.9.1).
- `tests/test_silent_controller.py`: porta le classi a `unittest.TestCase` e converte gli `assert` a `assert` di `unittest`.
- `tests/test_silent_controller.py`: sostituisce fixture pytest con setUp/_build_* e usa patch di `sys.stdout` per la cattura stdout.
- `docs/TODO.md`: aggiornato il coordinatore documentale con i riferimenti al nuovo
  report di analisi, al DESIGN, al PLAN e al TODO della feature
  `conversione_test_pytest_unittest`.
- `docs/todo.md`: aggiornato il coordinatore documentale con i riferimenti a
  `DESIGN_fix_unicode_print.md`, `PLAN_fix_unicode_print_v0.9.1.md`,
  `REPORT_FIX_UNICODE_PRINT_2026-03-28.md` e
  `TODO_fix_unicode_print_v0.9.1.md`.
- `docs/todo.md`: aggiunge i link a design, piano e todo della migrazione
  `test_silent_controller` verso `unittest`.
- `docs/2 - projects/DESIGN_migrazione_test_silent_controller_unittest.md`,
  `docs/3 - coding plans/PLAN_migrazione_test_silent_controller_unittest_v0.9.1.md`,
  `docs/5 - todolist/TODO_migrazione_test_silent_controller_unittest_v0.9.1.md`:
  definisce analisi, strategia e checklist operative con stop prima del coding.
- `tests`: converte i batch 3, 4 e 5 della migrazione pytest → unittest e chiude
  la validazione finale con `python -m unittest discover` verde (303 test OK, 1 skip).
- `docs/3 - coding plans/PLAN_conversione_test_pytest_unittest_v0.9.0.md`:
  avanzato lo stato del piano fino a `COMPLETED` dopo l'esecuzione sequenziale
  delle fasi 3, 4, 5 e 6.
- `docs/5 - todolist/TODO_conversione_test_pytest_unittest_v0.9.0.md`:
  chiusa la checklist operativa con baseline finale `unittest discover`
  (303 OK, 1 skipped, 0 failure, 0 error).
- `tests/test_partita.py`: allinea il confronto tra stato sintetico e completo al
  subset comune di chiavi pubbliche, evitando una regressione su snapshot con ruoli diversi.
- `tests/flow/test_flusso_game_loop.py`, `tests/test_silent_controller.py`: rimuove
  la dipendenza import-time da pytest nei moduli legacy che bloccavano la discovery finale.
- `docs/API.md`: aggiornato a [Unreleased] (2026-03-27); aggiunta sezione
  `GiocatoreUmano` con `imposta_focus_cartella_fallback()` (v0.9.1) e
  `visualizza_ultimi_numeri_estratti()` (v0.10.0).
- `docs/ARCHITECTURE.md`: aggiornato a [Unreleased] (2026-03-27); struttura
  directory allineata alla nuova cartella `docs/` e fotografia architetturale
  aggiornata sul layer di presentazione post-rimozione TUI.
- `documentations/`: aggiunge design, piano, TODO del refactor Partita/GameController e report di analisi qualitativa.
- `CHANGELOG.md`: aggiornamento sezione [Unreleased] per includere i nuovi miglioramenti di stato e reporting del refactor.
- `bingo_game/game_controller.py`: il controller non mantiene piu' un conteggio premi duplicato; il riepilogo premi viene derivato dallo snapshot di `Partita`, mantenendo il dominio come owner dello stato di gioco.
- `bingo_game/partita.py`: aggiunto `get_stato_sintetico()` come snapshot pubblico primario dello stato di partita; `get_stato_completo()` delega allo stesso punto di costruzione.
- `bingo_game/game_controller.py`: `ottieni_stato_sintetico()` delega a `Partita.get_stato_sintetico()` e conserva solo guardie, validazione minima e logging di bordo.
- `bingo_game/game_controller.py`: `ottieni_stato_sintetico()` riduce le validazioni semantiche ridondanti e mantiene solo il bordo minimo su parametro, eccezioni interne, tipo dizionario e chiavi obbligatorie.
- `tests/test_game_controller.py`: aggiunge una regressione che fissa la delega dello snapshot premi tra `Partita` e `GameController`.
- `tests/test_game_controller.py`, `tests/test_partita.py`: consolidano il contratto del riepilogo sintetico e la coerenza tra snapshot di `Partita` e facade del controller.
- `tests/test_game_controller.py`: caratterizza il bordo residuo di `ottieni_stato_sintetico()` e documenta quali controlli restano al controller dopo la semplificazione.
- `bingo_game/players/giocatore_umano.py`: metodo rinominato da
  `visualizzaultiminumeriestratti` a `visualizza_ultimi_numeri_estratti`
  (conformita snake_case).
- `bingo_game/game_controller.py`: aggiunta Sezione 4 (v0.11.0) — 6 funzioni wrapper
  (`imposta_focus_cartella`, `imposta_focus_cartella_fallback`, `esegui_azione_giocatore`,
  `esegui_azione_giocatore_con_numero`, `stato_focus_corrente`, `riepilogo_cartella_corrente`)
  e 2 frozenset (`_METODI_CON_TABELLONE`, `_METODI_PROMPT_CON_TABELLONE`) come unica
  interfaccia autorizzata tra layer di presentazione e domain layer.

### Removed
- `documentations/`: rimossa la cartella legacy; tutta la documentazione
  migrata nella nuova struttura `docs/` (templates, projects, coding plans,
  reports, todo list, API.md, ARCHITECTURE.md).
- Riferimenti correnti alla TUI nella sezione `[Unreleased]`: rimossi i richiami
  a game loop, tasti rapidi via `msvcrt` e test TUI non piu' presenti nel
  repository dopo la rimozione dell'interfaccia terminale.
- Parsing comandi testuali (seguito da Invio) rimosso dal game loop principale.
  Il loop v0.10.0 usa esclusivamente `leggi_tasto()` via msvcrt.

---

## [v0.9.1] — 2026-02-21

### Fixed
- **Bug 1** (`bingo_game/players/giocatore_umano.py`): corretto `AttributeError` in `imposta_focus_cartella()` — la chiamata interna usava `self.reset_focus_riga_e_colonna()` (senza underscore) invece di `self._reset_focus_riga_e_colonna()`. Il focus non veniva mai impostato all'avvio della partita.
- **Bug 3** (`bingo_game/ui/tui/tui_partita.py`): aggiunto fallback esplicito in `_loop_partita()` — se `imposta_focus_cartella(1)` fallisce e il giocatore ha esattamente 1 cartella, il focus viene ora impostato tramite `imposta_focus_cartella_fallback()`.
- **Bug 2** (`bingo_game/ui/tui/tui_partita.py`): il comando `s` senza argomento ora chiede il numero interattivamente con prompt `"Quale numero vuoi segnare? (1-90):"` invece di restituire immediatamente errore.
- **Anomalia A** (`bingo_game/players/giocatore_umano.py`): corretto `AttributeError` latente in `sposta_focus_riga_giu_avanzata()` — la chiamata usava `self._inizializza_focus_riga_se_manca()` (metodo inesistente) invece di `self._esito_inizializza_focus_riga_se_manca()`.

### Refactored
- **Anomalia B** (`bingo_game/players/helper_focus.py`, `bingo_game/ui/tui/tui_partita.py`): sostituito accesso diretto all'attributo privato `_indice_cartella_focus` dal layer UI con il nuovo metodo pubblico `imposta_focus_cartella_fallback()`, ripristinando il rispetto del vincolo architetturale.
- **Anomalia C** (`bingo_game/ui/locales/it.py`, `bingo_game/ui/renderers/renderer_terminal.py`): corretto typo `AVVANZATA` → `AVANZATA` in tutte le chiavi di `MESSAGGI_OUTPUT_UI_UMANI` e nelle relative occorrenze nel renderer e nei test.

### Tests
- Aggiunto test per `imposta_focus_cartella_fallback()` in `tests/unit/test_imposta_focus_cartella_regression.py`
- Aggiunto test per `sposta_focus_riga_giu_avanzata()` con `_indice_riga_focus` inizialmente `None`
- Aggiornati test in `tests/unit/test_tui_partita.py` e `tests/flow/test_flusso_game_loop.py`

---

## [0.9.0] - 2026-02-21 — Game Loop Interattivo

### Added
- `bingo_game/ui/tui/tui_partita.py`: macchina a stati `_loop_partita()` con dispatch
  comandi `p/s/c/v/q/?`. Architettura function-based, zero import dal Domain Layer.
  Helper: `_gestisci_segna`, `_gestisci_riepilogo_cartella`, `_gestisci_riepilogo_tabellone`,
  `_gestisci_quit`, `_gestisci_help`, `_costruisci_report_finale`, `_emetti_report_finale`,
  `_stampa`.
- `bingo_game/events/codici_loop.py`: 8 costanti stringa per i codici evento del Game Loop
  (`LOOP_TURNO_AVANZATO`, `LOOP_NUMERO_ESTRATTO`, ecc.).
- `bingo_game/ui/locales/it.py`: 13 nuove chiavi `LOOP_*` in `MESSAGGI_OUTPUT_UI_UMANI`
  (prompt, help, quit, report finale, numero estratto, ecc.).
- `bingo_game/game_controller.py`: funzione `ottieni_giocatore_umano(partita)` — espone il
  primo `GiocatoreUmano` alla TUI senza che questa importi classi Domain.
- `tests/unit/test_game_controller_loop.py`: 10 unit test per `ottieni_giocatore_umano()`
  inclusi 3 smoke test di regressione.
- `tests/unit/test_tui_partita.py`: 14 unit test per `tui_partita.py`
  (quit, segna, help, report, focus auto, comando sconosciuto).
- `tests/unit/test_renderer_report_finale.py`: 8 unit test per la vocalizzazione gerarchica
  del renderer (tabellone 3 righe, segnazione 1 riga per esito, cartella 2 righe).
- `tests/flow/test_flusso_game_loop.py`: 12 scenari end-to-end che coprono tutti i comandi
  e i flussi di partita completa (con e senza vincitore).
- `README.md`: sezione "Come si gioca (v0.9.0)" con tabella comandi e note operative.

### Design Notes
- **Flessibilità di marcatura**: qualsiasi numero estratto è segnabile, non solo l'ultimo.
- **Azioni informative illimitate**: `s`, `c`, `v`, `?` non avanzano mai il turno; solo `p` chiama `esegui_turno_sicuro`.
- **Separazione layer**: la TUI accede al dominio esclusivamente tramite `game_controller`; nessun import diretto di `GiocatoreUmano`, `Partita`, `Tabellone` o `Cartella` in `tui_partita.py`.
- **Quit con allerta**: il comando `q` confermato logga `WARNING [ALERT] Partita interrotta dall'utente al turno #N.` su `tombola_stark.tui`.
- **Screen reader ready**: ogni riga di output è autonoma e ≤ 120 caratteri; nessuna ASCII art.

---

## [0.8.0] - 2026-02-20 — Silent Controller

### Changed
- `bingo_game/game_controller.py`: rimossi tutti i `print()` (~22 chiamate).
  I passaggi di costruzione vanno ora a log DEBUG via `_logger_game`.
  Gli output di stato sono trasportati dai valori di ritorno (`bool`, `dict`, `None`).
  I messaggi di errore sono gestiti dalla TUI via `MESSAGGI_CONTROLLER`.
- `bingo_game/ui/ui_terminale.py`: aggiunta guardia sul valore di ritorno di
  `avvia_partita_sicura` (percorso `False`) e helper sicuro `_ottieni_stato_sicuro`
  per la cattura di `ValueError` da `ottieni_stato_sintetico`.

### Added
- `bingo_game/events/codici_controller.py`: nuove costanti stringa
  `CTRL_AVVIO_FALLITO_GENERICO`, `CTRL_TURNO_NON_IN_CORSO`,
  `CTRL_NUMERI_ESAURITI`, `CTRL_TURNO_FALLITO_GENERICO`.
- `bingo_game/ui/locales/it.py`: nuovo dizionario `MESSAGGI_CONTROLLER`
  (4 voci) tipizzato con le costanti di `codici_controller.py`.
- `tests/test_silent_controller.py`: 15 test di non-regressione stdout
  con `capsys` per tutte le funzioni pubbliche del controller.

### Fixed
- Accessibilità: rimossi i messaggi con emoji che interferivano con gli screen reader.
- Architettura: eliminata la dipendenza `Controller → stdout`.

---

## [0.7.0] - 2026-02-19

### Aggiunto
- `TerminalUI` in `bingo_game/ui/ui_terminale.py`: interfaccia da terminale accessibile (screen reader) per il flusso di configurazione pre-partita (Fase 1). Macchina a stati A→E con 3 prompt sequenziali (nome, bot, cartelle) e loop di validazione con re-prompt.
- `bingo_game/events/codici_configurazione.py`: 9 costanti-chiave (`Codici_Configurazione`) per la localizzazione del menu di configurazione.
- `MESSAGGI_CONFIGURAZIONE` in `bingo_game/ui/locales/it.py`: dizionario con 9 chiavi e testi italiani per il flusso di configurazione.
- `bingo_game/ui/locales/__init__.py`: modulo di re-export per i dizionari di localizzazione.
- `tests/unit/test_ui_terminale.py`: 8 unit test con `unittest.mock` (mock di `input()`/`print()` e controller).

### Modificato
- `main.py`: rimossa stampa placeholder, aggiunto entry point `TerminalUI().avvia()`.
- `bingo_game/ui/locales/it.py`: esteso con dizionario `MESSAGGI_CONFIGURAZIONE` (9 chiavi).

---

## [Non Rilasciato]

### Aggiunto
- Strato interfaccia utente (`bingo_game/ui/`) — in sviluppo attivo.
- Navigazione da tastiera e integrazione TTS completa per il giocatore umano.
- Utility di supporto generali (`bingo_game/utils.py`).

---

## [0.5.0] - 2026-02-19

### Aggiunto
- Modulo `bingo_game/logging/` con `GameLogger` singleton: copertura completa di tutti gli eventi di gioco e di sistema organizzati in 4 categorie (`[GAME]`, `[PRIZE]`, `[SYS]`, `[ERR]`).
- Sub-logger gerarchici `tombola_stark.game`, `tombola_stark.prizes`, `tombola_stark.system`, `tombola_stark.errors` per filtraggio per categoria.
- 18 eventi distinti tracciati: ciclo di vita partita, tutti i tipi di premio, snapshot stato, riepilogo finale a fine sessione.
- `_log_prize_event()` e `_log_game_summary()` come helper privati nel controller.
- Contatori di sessione `_turno_corrente` e `_premi_totali` in `game_controller.py`.
- Test suite Fase 2: `tests/unit/test_event_logging.py` (7 test) e `tests/integration/test_event_coverage.py` (5 test).
- Documentazione completa del sistema di logging in `API.md` e `ARCHITECTURE.md`.

---

## [0.4.0] - 2026-02-19

### Aggiunto
- Modulo `bingo_game/logging/` con classe `GameLogger` Singleton: file di log cumulativo `logs/tombola_stark.log` in modalità append.
- `FlushingFileHandler`: ogni riga di log è scritta su disco immediatamente (flush dopo ogni `emit()`).
- Marcatori di sessione (AVVIATA/CHIUSA) con timestamp che separano visivamente le esecuzioni nel file cumulativo.
- Flag `--debug` via `argparse` in `main.py`: attiva il livello DEBUG per la tracciatura dettagliata di ogni turno.
- Aggancio del logger ai punti chiave di `game_controller.py` tramite helper `_log_safe()` (il logging non interrompe mai il gioco).
- Test suite Fase 1: `tests/unit/test_game_logger.py` (8 test) e `tests/integration/test_logging_integration.py` (3 test).

### Modificato
- `main.py`: aggiunto `argparse` per il flag `--debug` e blocco `try/finally` per la chiusura pulita del logger.
- `.gitignore`: aggiunta esclusione della cartella `logs/` e dei file `*.log`.
- `README.md`: istruzioni d'uso per il flag `--debug` e formato log file.

### Corretto
- `bingo_game/players/giocatore_umano.py`: rimossa parentesi chiusa duplicata (riga 59).
- `bingo_game/players/helper_reclami_focus.py`: corretto import `TipoVittoria` → `Tipo_Vittoria`.
- `bingo_game/events/eventi_output_ui_umani.py`: rimosso import `from __future__ import annotations` duplicato.

---

## [0.3.0] - 2026-02-18

### Aggiunto
- `API.md` nella cartella `documentations/`: riferimento completo di tutte le classi pubbliche, metodi, parametri e valori di ritorno. (commit [fbe71b2](https://github.com/donato81/tombola-stark/commit/fbe71b2e50af50083560e72ccc366a86acd0b85b))
- `ARCHITECTURE.md` nella cartella `documentations/`: documentazione dell'architettura a livelli (Dominio → Controller → Interfaccia), pattern chiave, flusso dei dati e architettura dell'accessibilità. (commit [fbe71b2](https://github.com/donato81/tombola-stark/commit/fbe71b2e50af50083560e72ccc366a86acd0b85b))
- Template di progetto (`documentations/templates/`) con modelli per API, Architettura, Changelog, Design Document, Piano di Implementazione e TODO. (commit [4781a8e](https://github.com/donato81/tombola-stark/commit/4781a8eaf972a43b5f530735462d87bcfd068314))

### Modificato
- `README.md` aggiornato con badge, descrizione accessibilità, istruzioni di installazione complete, struttura del progetto ad albero e link alla documentazione tecnica. (commit [3b47b4a](https://github.com/donato81/tombola-stark/commit/3b47b4ac1f911b9b2575cbaefeb8125ccb48f58c))
- Cartella `documentations/` riorganizzata: rimossa la directory di lavoro temporanea, aggiunta struttura definitiva per la documentazione. (commit [24ef07e](https://github.com/donato81/tombola-stark/commit/24ef07e0fed36dae2c17afea3d6b5e48893be7cb))

---

## [0.2.0] - 2026-02-16

### Aggiunto
- Cartella `documentations/` introdotta nel progetto come area dedicata alla documentazione tecnica. (commit [24ef07e](https://github.com/donato81/tombola-stark/commit/24ef07e0fed36dae2c17afea3d6b5e48893be7cb))

### Modificato
- Struttura del repository riorganizzata: rimossa la directory di lavoro temporanea con Perplexity, separazione netta tra codice sorgente e documentazione.

---

## [0.1.0] - 2026-02-12

*Rilascio iniziale — Motore di gioco core.*

### Aggiunto
- Classe `Tabellone`: gestione dei 90 numeri, estrazione casuale, storico estrazioni, percentuale di avanzamento, snapshot di stato. (commit [82bda90](https://github.com/donato81/tombola-stark/commit/82bda90bf62f898ef0c343d205a2ac48c1f24bf3))
- Classe `Cartella`: 3 righe × 5 numeri, segnatura automatica dei numeri estratti, verifica in tempo reale di ambo, terno, quaterna, cinquina e tombola per riga.
- Classe `Partita`: coordinamento tabellone e giocatori, ciclo di estrazione, verifica premi, gestione stati (`non_iniziata` → `in_corso` → `terminata`).
- Classe `GiocatoreBase`: gestione identità, cartelle multiple, aggiornamento con numero estratto, rilevamento tombola.
- Classe `GiocatoreUmano`: specializzazione per il giocatore umano con supporto al sistema di eventi per l'accessibilità.
- Classe `GiocatoreAutomatico`: bot di gioco senza interazione umana richiesta.
- Modulo `game_controller`: funzioni di orchestrazione fail-safe (`crea_partita_standard`, `avvia_partita_sicura`, `esegui_turno_sicuro`, `ottieni_stato_sintetico`).
- Sistema di eventi strutturati (`bingo_game/events/`) per output semantico pronto per la vocalizzazione TTS.
- Gerarchia di eccezioni personalizzate per ogni modulo: `partita_exceptions.py`, `cartella_exceptions.py`, `giocatore_exceptions.py`, `game_controller_exceptions.py`, `tabellone_exceptions.py`.
- Modulo `validations/` per la logica di validazione riutilizzabile.
- Suite di test unitari (`tests/`) per la validazione automatica di `Cartella`, `Tabellone`, `Partita` e `GiocatoreBase`.
- `main.py` come entry point dell'applicazione.
- `requirements.txt` con dipendenze: wxPython, gTTS, pygame, playsound, Pillow e librerie di supporto.

---

## Legenda

- **Aggiunto**: Nuove funzionalità
- **Modificato**: Modifiche a funzionalità esistenti
- **Deprecato**: Funzionalità in via di dismissione
- **Rimosso**: Funzionalità rimosse
- **Corretto**: Bug fix
- **Sicurezza**: Correzioni di vulnerabilità

---

*Per i dettagli tecnici completi, consulta la [storia dei commit](https://github.com/donato81/tombola-stark/commits/main) o [`documentations/ARCHITECTURE.md`](documentations/ARCHITECTURE.md).*

[Non Rilasciato]: https://github.com/donato81/tombola-stark/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/donato81/tombola-stark/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/donato81/tombola-stark/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/donato81/tombola-stark/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/donato81/tombola-stark/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/donato81/tombola-stark/releases/tag/v0.1.0
