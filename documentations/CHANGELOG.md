# 📝 CHANGELOG.md - Tombola Stark

> Tutte le modifiche rilevanti al progetto sono documentate in questo file.
>
> Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.0.0/).
> Il progetto segue il [Semantic Versioning](https://semver.org/lang/it/).

---

## [v0.8.0] - 2026-02-20

### Feature: Silent Controller — Rimozione `print()` e Localizzazione Messaggi

#### Aggiunto
- **`bingo_game/events/codici_controller.py`**: 4 costanti stringa `CTRL_*` per i codici
  di risposta del controller (`ctrl.avvio_fallito_generico`, `ctrl.turno_non_in_corso`,
  `ctrl.numeri_esauriti`, `ctrl.turno_fallito_generico`). File privo di import interni
  (nessun rischio di circolarità).
- **`MESSAGGI_CONTROLLER`** in `bingo_game/ui/locales/it.py`: dizionario `dict[str, str]`
  con 4 chiavi (una per ogni costante `CTRL_*`) contenente i testi localizzati in italiano
  da mostrare all'utente in risposta ai valori di ritorno anomali del controller.
- **Export `MESSAGGI_CONTROLLER`** da `bingo_game/ui/locales/__init__.py`: importabile
  via path corto `from bingo_game.ui.locales import MESSAGGI_CONTROLLER`.
- **`tests/test_silent_controller.py`**: 15 nuovi test (tutti verdi):
  - Classe `TestControllerSilenzioso` (8 test `capsys`): verifica che tutte le funzioni
    pubbliche del controller non emettano nulla su stdout.
  - Classe `TestContrattiRitorno` (4 test): verifica i contratti di ritorno
    (`True`/`False`, `dict`/`None`, `ValueError`).
  - Classe `TestMESSAGGICONTROLLER` (3 test): verifica le 4 chiavi, i valori stringa
    non vuoti e la corrispondenza con le costanti `CTRL_*`.

#### Modificato
- **`bingo_game/game_controller.py`**: rimosse ~22 chiamate `print()` suddivise in 3 gruppi:
  - *Gruppo A* (11 `print()`): scaffolding costruzione partita → sostituiti con
    `_log_safe(..., logging.DEBUG, logger=_logger_game)` con prefisso `[GAME]`.
  - *Gruppo B* (5 `print()`): output di stato (`"✅ Partita avviata"`, ecc.) → rimossi
    (la TUI legge già il valore di ritorno `bool`/`dict`).
  - *Gruppo C+D* (7+5 `print()`): errori utente ed errori infrastruttura → sostituiti
    con `_log_safe(..., logging.WARNING/ERROR, logger=_logger_errors/_logger_system)`
    con prefissi `[GAME]`, `[ERR]`, `[SYS]` senza emoji.
  - `grep -n "print(" bingo_game/game_controller.py` → **zero risultati** post-modifica.
- **`bingo_game/ui/ui_terminale.py`**: aggiunte guardie TUI per i casi di ritorno anomalo
  del controller:
  - Import di `MESSAGGI_CONTROLLER` e delle 4 costanti `CTRL_*`.
  - Guardia sul `False` di `avvia_partita_sicura` con messaggio localizzato.
  - Helper `_ottieni_stato_sicuro` per catturare `ValueError` di `ottieni_stato_sintetico`.
- **`documentations/API.md`**: aggiornate le firme di tutte le funzioni pubbliche del
  controller con note `v0.8.0` (rimozione riferimenti a `stdout`/`print()`, contratti
  di ritorno espliciti).
- **`documentations/ARCHITECTURE.md`**: aggiornato diagramma livelli (rimozione freccia
  `Controller → stdout`), aggiunta regola invariante *"Il Controller non scrive mai su
  stdout"*, aggiunta `codici_controller.py` alla tabella componenti, aggiornamento
  flusso TUI.

#### Fixed
- **Accessibilità**: rimossi tutti i caratteri emoji (`✅`, `❌`, `🎉`, `💥`) dai
  messaggi di log del controller. I log erano potenzialmente vocalizzati dai screen
  reader come sequenze Unicode non significative.
- **Architettura**: eliminata la dipendenza `Controller → stdout`. Il controller è ora
  rigorosamente silenzioso; tutta la comunicazione verso l'utente passa attraverso
  la TUI che legge i valori di ritorno.
- **Pattern `_log_safe`**: ogni chiamata usa il prefisso categorizzato (`[GAME]`,
  `[ERR]`, `[SYS]`) come da `DESIGN_LOGGING_SYSTEM.md`, abilitando il filtraggio
  con `grep "\[ERR\]" tombola_stark.log`.

#### Test
- 15 nuovi test in `tests/test_silent_controller.py` (tutti verdi)
- Nessuna regressione sulla suite preesistente

---

## [v0.7.0] - 2026-02-20

### Feature: TUI Start Menu Fase 1 — Macchina a Stati A→E

#### Aggiunto
- **`bingo_game/ui/ui_terminale.py`**: classe `TerminalUI` con macchina a stati
  sequenziale A→E per la configurazione pre-partita:
  - Stato A (Benvenuto): messaggio introduttivo accessibile
  - Stato B (Nome): input nome giocatore con `strip()`, validazione non vuoto, max 15 caratteri
  - Stato C (Bot): input numero bot (1–7) con re-prompt automatico su valore non valido
  - Stato D (Cartelle): input numero cartelle (1–6) con re-prompt automatico
  - Stato E (Avvio): chiamata `crea_partita_standard()` + `avvia_partita_sicura()` (two-step obbligatorio)
- **`bingo_game/events/codici_configurazione.py`**: 9 costanti `Codici_Configurazione`
  per i messaggi del flusso di configurazione.
- **`MESSAGGI_CONFIGURAZIONE`** in `bingo_game/ui/locales/it.py`: testi localizzati
  in italiano per i 5 stati del flusso TUI.
- **`main.py`**: aggiornato per istanziare `TerminalUI` e avviare il flusso di
  configurazione via `tui.avvia()`.
- **8 unit test** per `TerminalUI` (flusso happy path, validazioni, re-prompt).

#### Modificato
- **`bingo_game/ui/locales/it.py`**: aggiunta sezione `MESSAGGI_CONFIGURAZIONE`.
- **`bingo_game/ui/locales/__init__.py`**: export di `MESSAGGI_CONFIGURAZIONE`.
- **`documentations/API.md`**: documentata la classe `TerminalUI` con il metodo
  pubblico `avvia()`, validazioni integrate e dipendenze.
- **`documentations/ARCHITECTURE.md`**: aggiornata sezione Livello Interfaccia con
  componenti attivi v0.7.0 e flusso TUI.
- **`README.md`**: aggiunta feature *"Menu TUI accessibile (v0.7.0+)"* nella sezione
  Caratteristiche.

#### Test
- 8 nuovi test unitari per `TerminalUI`
- Nessuna regressione sulla suite preesistente

---

## [v0.6.0] - 2026-02-19

### Feature: Bot Attivo — Reclami Autonomi dei Bot

#### Aggiunto
- **`GiocatoreAutomatico._valuta_potenziale_reclamo()`**: metodo interno che analizza le
  cartelle del bot e costruisce un `ReclamoVittoria` per il premio di rango più alto
  disponibile, escludendo quelli già assegnati.
- **`GiocatoreBase.is_automatico()`**: metodo polimorfico che permette a `Partita` di
  distinguere bot da giocatori umani senza usare `isinstance()`. Ritorna `False` in
  `GiocatoreBase`/`GiocatoreUmano`, `True` in `GiocatoreAutomatico`.
- **`GiocatoreBase.reset_reclamo_turno()`**: metodo per azzerare `reclamo_turno` dopo
  che la Partita ha processato il turno corrente.
- **Chiave `reclami_bot`** nel dizionario restituito da `Partita.esegui_turno()`: lista
  degli esiti dei reclami dei bot nel turno (backward-compatible, sempre presente).
- **Campo `id_giocatore`** negli eventi premio di `verifica_premi()`: consente matching
  robusto tra reclami bot e premi reali anche con nomi giocatori duplicati.
- **Fase reclami bot** nel ciclo di `Partita.esegui_turno()`: i bot valutano e dichiarano
  i premi tra l'aggiornamento numeri e la verifica premi ufficiale.
- **Logging reclami bot** in `game_controller.esegui_turno_sicuro()`: gli esiti
  (ACCETTATO/RIGETTATO) sono tracciati su `tombola_stark.prizes`.
- **ADR-004** in `ARCHITECTURE.md`: documenta la decisione architetturale per il Bot Attivo.

#### Modificato
- `Partita.verifica_premi()`: aggiunto campo `id_giocatore` a tutti gli eventi tombola
  e di riga per supportare il matching robusto.
- `Partita.esegui_turno()`: integrata fase reclami bot (Step 3–6 nel flusso di turno).
- `documentations/API.md`: documentati `is_automatico()`, `reset_reclamo_turno()`,
  `_valuta_potenziale_reclamo()`, chiave `reclami_bot`, campo `id_giocatore`.
- `documentations/ARCHITECTURE.md`: aggiornato flusso turno (v0.6.0), aggiunto ADR-004,
  storia delle versioni aggiornata.
- `documentations/README.md`: aggiunta feature "Bot Attivi (v0.6.0+)" nella sezione
  Caratteristiche.

#### Ottimizzazione
- `GiocatoreAutomatico._valuta_potenziale_reclamo()`: aggiunta istruzione `break` dopo
  aver trovato il tipo di premio più alto per ogni riga, evitando verifiche non necessarie.

#### Test
- Aggiunti 8 test unitari per `GiocatoreAutomatico` (reclami, selezione premio, casi limite)
- Aggiunti 8 test di integrazione per il flusso `Partita.esegui_turno()` con reclami bot
- Totale test: 36 (tutti passanti, zero regressioni)

---

## [v0.5.0] - 2026-02

### Feature: Sistema di Logging Fase 2 — Copertura Completa

#### Aggiunto
- Copertura completa di 18 eventi di gioco distinti nel logging:
  - Ciclo di vita partita: creazione, avvio, fine, riepilogo finale
  - Estrazioni: ogni turno (modalità DEBUG), numeri esauriti
  - Premi: ambo, terno, quaterna, cinquina, tombola (per giocatore, cartella, riga)
  - Errori: tutte le eccezioni gestite dal controller
- Sub-logger per categoria:
  - `tombola_stark.game` — eventi ciclo di vita partita (`[GAME]`)
  - `tombola_stark.prizes` — premi assegnati (`[PRIZE]`)
  - `tombola_stark.system` — configurazione e infrastruttura (`[SYS]`)
  - `tombola_stark.errors` — eccezioni e anomalie (`[ERR]`)
- Riepilogo finale partita nel log (numero turni, premi totali, vincitore tombola)
- Helper `_log_safe()` nel controller: il logging non propaga mai eccezioni al gioco

#### Modificato
- `game_controller.py`: integrazione logging completo in tutte le funzioni pubbliche
- `documentations/API.md`: documentato `GameLogger` con sub-logger e pattern `_log_safe()`

---

## [v0.4.0] - 2026-02

### Feature: Sistema di Logging Fase 1 — Infrastruttura Base

#### Aggiunto
- **`GameLogger`** (`bingo_game/logging/game_logger.py`): Singleton per il logging
  centralizzato dell'applicazione.
- File di log cumulativo `logs/tombola_stark.log` in modalità append con flush immediato
  (ogni riga scritta su disco immediatamente, leggibile in tempo reale).
- Marcatori di sessione: separatori visivi con timestamp all'avvio e alla chiusura.
- Flag `--debug` in `main.py`: attiva il livello DEBUG per log dettagliati di ogni turno.
- Formato log strutturato: `YYYY-MM-DD HH:MM:SS | LEVEL | LOGGER_NAME | MESSAGE`

#### Modificato
- `main.py`: aggiunto parsing argomenti CLI (`--debug`), inizializzazione e shutdown
  di `GameLogger` nel blocco `try/finally`.

---

## [v0.1.0] - 2026-02

### Rilascio Iniziale

#### Aggiunto

**Motore di Gioco (Dominio)**:
- `Tabellone`: gestione numeri 1–90, estrazione casuale, storico estrazioni, percentuale
  avanzamento.
- `Cartella`: generazione automatica (3 righe × 5 numeri), segnatura numeri, verifica
  premi (ambo, terno, quaterna, cinquina, tombola).
- `Partita`: coordinamento tabellone + giocatori, ciclo di estrazioni, verifica premi,
  determinazione fine partita. Supporto 2–8 giocatori.
- `GiocatoreBase`: classe base con identità (nome, id), gestione cartelle, aggiornamento
  numeri.
- `GiocatoreUmano`: specializzazione per il giocatore umano con supporto eventi UI.
- `GiocatoreAutomatico`: bot automatico, eredita da `GiocatoreBase`.

**Controller**:
- `game_controller.py`: funzioni di orchestrazione fail-safe (`crea_partita_standard`,
  `avvia_partita_sicura`, `esegui_turno_sicuro`, `ottieni_stato_sintetico`,
  `ha_partita_tombola`, `partita_terminata`).
- `comandi_partita.py`: comandi di partita ausiliari.

**Infrastruttura**:
- Gerarchia eccezioni personalizzate per ogni modulo (`partita_exceptions.py`,
  `giocatore_exceptions.py`, `game_controller_exceptions.py`, `cartella_exceptions.py`,
  `tabellone_exceptions.py`).
- Sistema eventi strutturati (`bingo_game/events/`): `ReclamoVittoria`, `EventoFineTurno`,
  messaggi UI, codici eventi/errori.
- Validazioni riutilizzabili (`bingo_game/validations/`).
- Helper accessibilità: `helper_focus.py`, `helper_reclami_focus.py`.

**Documentazione**:
- `documentations/API.md`: riferimento API pubblico completo.
- `documentations/ARCHITECTURE.md`: architettura a livelli, pattern chiave, ADR.
- `README.md`: guida utente, installazione, utilizzo.

**Testing**:
- Suite pytest per dominio (test unitari) e flussi controller+dominio (test integrazione).

---

*Ultimo aggiornamento: 2026-02-20 (v0.8.0)*
