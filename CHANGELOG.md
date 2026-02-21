# Registro delle Modifiche

Tutte le modifiche rilevanti a questo progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Versionamento Semantico](https://semver.org/spec/v2.0.0.html).

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
