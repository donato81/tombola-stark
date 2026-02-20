# 📋 TODO — Silent Controller (v0.8.0)

> **Basato su**: `documentations/PLAN_SILENT_CONTROLLER.md`  
> **Design di riferimento**: `documentations/DESIGN_SILENT_CONTROLLER.md` (DESIGN FREEZE ✅ 2026-02-20)  
> **Branch di lavoro**: `feature/silent-controller-v0.8.0`  
> **Versione target**: `v0.8.0`  
> **Tipo**: REFACTOR  
> **Priorità**: HIGH  
> **Stato**: READY 🔵  
> **Ultimo aggiornamento**: 2026-02-20

---

## 📖 Riferimento Documentazione

Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
`documentations/PLAN_SILENT_CONTROLLER.md`

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase dell'implementazione.
Il piano completo contiene analisi, architettura, edge case e dettagli tecnici completi.

---

## 🤖 Istruzioni per Copilot Agent

Implementare le modifiche in modo **incrementale** su commit atomici e logici.

**Workflow per ogni commit:**

1. **Leggi questo TODO** → identifica il prossimo commit da implementare
2. **Consulta il piano completo** → rivedi la sezione pertinente in `PLAN_SILENT_CONTROLLER.md`
3. **Implementa modifiche** → codifica solo il commit corrente (scope limitato)
4. **Verifica meccanica** → esegui il comando di verifica indicato nel task
5. **Commit atomico** → messaggio conventional, scope chiaro, riferimento fase
6. **Aggiorna questo TODO** → spunta le checkbox completate
7. **RIPETI** → passa al commit successivo (torna al punto 1)

⚠️ **REGOLE FONDAMENTALI:**

- ✅ **Un commit per fase logica** (no mega-commit con tutto)
- ✅ **Dopo ogni commit**: aggiorna questo TODO spuntando le checkbox
- ✅ **Prima di ogni fase**: rileggi la sezione pertinente nel piano completo
- ✅ **Approccio sequenziale**: la Fase 2 dipende dalla Fase 1; non saltare l'ordine
- ✅ **Commit message format**: `type(scope): description [CX/9]`
- ❌ **NO commit multipli senza aggiornare TODO** (perde tracciabilità)
- ❌ **NO implementazione completa in un colpo** (viola incrementalità)

---

## ⚠️ Attenzioni Tecniche (Leggere PRIMA di ogni fase)

> Questi tre punti sono prerequisiti di correttezza architetturale. Verificarli attivamente, non darli per scontati.

### AT-1 — Verifica Baseline (prima di qualsiasi modifica)

- [ ] Eseguire `python -m pytest tests/ -q` **prima** di iniziare il commit C4
- [ ] Verificare che tutti i test esistenti siano **verdi** (0 failed, 0 error)
- [ ] Annotare il numero di test che passano come baseline di riferimento
- [ ] Se ci sono test falliti pre-esistenti: **segnalare e non procedere** finché non sono risolti

> **Motivazione**: il refactoring del controller (Fase 2) è ad alto impatto. Partire da una baseline verde garantisce che qualsiasi regressione introdotta sia attribuibile univocamente alle modifiche di questa feature.

### AT-2 — Prevenzione Circolarità Import

- [ ] Dopo C1 (creazione `codici_controller.py`): verificare che il file non importi nulla da `bingo_game.ui.*`
- [ ] Dopo C2 (modifica `it.py`): eseguire `python -c "from bingo_game.ui.locales.it import MESSAGGI_CONTROLLER"` → deve completarsi **senza `ImportError`**
- [ ] Verificare che il grafo delle dipendenze rispetti la direzione: `events/ ← locales/` (mai il contrario)
- [ ] Regola da rispettare: `codici_controller.py` ha **zero import** da qualsiasi modulo del progetto (solo letterali stringa)

> **Motivazione**: `bingo_game/events/` è un layer inferiore rispetto a `bingo_game/ui/`. Un import circolare `events → ui → events` causerebbe un `ImportError` silenzioso difficile da diagnosticare.

### AT-3 — Prefissi di Logging Context

- [ ] Ogni nuova chiamata `_log_safe()` in `game_controller.py` deve usare il prefisso corretto:
  - `[GAME]` per log via `_logger_game` (costruzione, turni, stato)
  - `[PRIZES]` per log via `_logger_prizes` (premi, tombola)
  - `[SYS]` per log via `_logger_system` (stati inattesi infrastruttura)
  - `[ERR]` per log via `_logger_errors` (parametri errati, eccezioni impreviste)
- [ ] Verificare i prefissi dopo C4, C5 e C6 con: `grep -n "_log_safe" bingo_game/game_controller.py`
- [ ] Nessun log deve usare `[CTRL]` come prefisso (prefisso riservato alla TUI in futuro)
- [ ] I nuovi messaggi di log devono essere in italiano o inglese tecnico: **mai con emoji** (✅❌🎉)

> **Motivazione**: i prefissi `[GAME]`, `[SYS]`, `[ERR]` permettono il filtraggio del log con `grep "\[ERR\]" tombola_stark.log` senza dover conoscere il nome del modulo. Questa convenzione è già stabilita nel `DESIGN_LOGGING_SYSTEM.md`.

---

## 🎯 Obiettivo Implementazione

- Eliminare le ~22 chiamate `print()` da `game_controller.py`, rendendolo completamente silenzioso verso stdout
- Sostituire i `print()` con `_log_safe()` verso i sub-logger già esistenti (Gruppi A e D) o rimuoverli (Gruppo B)
- Aggiungere `MESSAGGI_CONTROLLER` in `it.py` per permettere alla TUI di mostrare messaggi localizzati in risposta ai valori di ritorno del controller
- Verificare il silenzio con test `capsys` su tutte le funzioni pubbliche del controller
- Aggiornare la documentazione (`API.md`, `ARCHITECTURE.md`, `CHANGELOG.md`) nella stessa PR

---

## 📂 File Coinvolti

- `bingo_game/events/codici_controller.py` → **CREATE** (C1)
- `bingo_game/ui/locales/it.py` → **MODIFY** (C2)
- `bingo_game/ui/locales/__init__.py` → **MODIFY** (C3)
- `bingo_game/game_controller.py` → **MODIFY** (C4, C5, C6)
- `bingo_game/ui/ui_terminale.py` → **MODIFY** (C7)
- `tests/test_silent_controller.py` → **CREATE** (C8)
- `documentations/API.md` → **UPDATE** (C9)
- `documentations/ARCHITECTURE.md` → **UPDATE** (C9)
- `documentations/CHANGELOG.md` → **UPDATE** (C9)

---

## 🛠️ Checklist Implementazione

---

### COMMIT 1 (C1) — Infrastruttura Costanti

**File**: `bingo_game/events/codici_controller.py` (CREATE)  
**Messaggio**: `feat(events): add codici_controller.py — 4 CTRL_* string constants [C1/9]`

- [ ] Creare `bingo_game/events/codici_controller.py` con docstring di modulo
- [ ] Definire `CTRL_AVVIO_FALLITO_GENERICO: str = "ctrl.avvio_fallito_generico"`
- [ ] Definire `CTRL_TURNO_NON_IN_CORSO: str = "ctrl.turno_non_in_corso"`
- [ ] Definire `CTRL_NUMERI_ESAURITI: str = "ctrl.numeri_esauriti"`
- [ ] Definire `CTRL_TURNO_FALLITO_GENERICO: str = "ctrl.turno_fallito_generico"`
- [ ] Verificare che il file **non contenga nessun import** da moduli del progetto
- [ ] Eseguire `python -m py_compile bingo_game/events/codici_controller.py` → zero errori
- [ ] Eseguire `python -c "from bingo_game.events.codici_controller import CTRL_AVVIO_FALLITO_GENERICO; print(CTRL_AVVIO_FALLITO_GENERICO)"` → output: `ctrl.avvio_fallito_generico`
- [ ] Verificare AT-2: nessun import circolare possibile (file di soli letterali)

**Criterio di done C1**: 4 costanti importabili, nessun import interno, py_compile verde.

---

### COMMIT 2 (C2) — Localizzazione Controller

**File**: `bingo_game/ui/locales/it.py` (MODIFY)  
**Messaggio**: `feat(locales): add MESSAGGI_CONTROLLER to it.py with typed import [C2/9]`

- [ ] Leggere il contenuto attuale di `it.py` prima di modificare (evitare sovrascritture)
- [ ] Aggiungere in cima al file l'import delle 4 costanti da `codici_controller`:
  ```python
  from bingo_game.events.codici_controller import (
      CTRL_AVVIO_FALLITO_GENERICO,
      CTRL_TURNO_NON_IN_CORSO,
      CTRL_NUMERI_ESAURITI,
      CTRL_TURNO_FALLITO_GENERICO,
  )
  ```
- [ ] Aggiungere in coda al file il dizionario `MESSAGGI_CONTROLLER: dict[str, str]` con 4 chiavi
- [ ] Verificare i 4 testi italiani corrispondono esattamente al DESIGN (nessuna variazione)
- [ ] Verificare che i dizionari pre-esistenti (`MESSAGGI_CONFIGURAZIONE`, `MESSAGGI_ERRORI`, ecc.) **non siano stati modificati**
- [ ] Eseguire `python -m py_compile bingo_game/ui/locales/it.py` → zero errori
- [ ] Eseguire `python -c "from bingo_game.ui.locales.it import MESSAGGI_CONTROLLER; print(len(MESSAGGI_CONTROLLER))"` → output: `4`
- [ ] Eseguire AT-2: `python -c "from bingo_game.ui.locales.it import MESSAGGI_CONTROLLER"` → **nessun `ImportError`**

**Criterio di done C2**: `MESSAGGI_CONTROLLER` con 4 chiavi importabile, nessun ImportError, dizionari esistenti intatti.

---

### COMMIT 3 (C3) — Export dal Package Locales

**File**: `bingo_game/ui/locales/__init__.py` (MODIFY)  
**Messaggio**: `feat(locales): export MESSAGGI_CONTROLLER from locales __init__ [C3/9]`

- [ ] Leggere il contenuto attuale di `__init__.py` prima di modificare
- [ ] Aggiungere `from bingo_game.ui.locales.it import MESSAGGI_CONTROLLER` nella sezione export
- [ ] Verificare che segua il pattern degli altri export già presenti (es. `MESSAGGI_CONFIGURAZIONE`)
- [ ] Verificare che gli export pre-esistenti **non siano stati rimossi o alterati**
- [ ] Eseguire `python -c "from bingo_game.ui.locales import MESSAGGI_CONTROLLER; print(type(MESSAGGI_CONTROLLER))"` → output: `<class 'dict'>`

**Criterio di done C3**: `MESSAGGI_CONTROLLER` importabile da `bingo_game.ui.locales` (path corto), export esistenti intatti.

---

### ⚠️ PRE-FASE 2 — Verifica Baseline (AT-1)

> Eseguire questi check **prima** di iniziare C4. Non procedere se falliscono.

- [ ] `python -m pytest tests/ -q` → annotare numero di test verdi come baseline
- [ ] `grep -n "print(" bingo_game/game_controller.py` → annotare numero di occorrenze (baseline ~22)
- [ ] Nessun test fallito pre-esistente: se ci sono fallimenti, segnalare e bloccare

---

### COMMIT 4 (C4) — Refactoring Gruppo A

**File**: `bingo_game/game_controller.py` (MODIFY)  
**Messaggio**: `refactor(controller): replace print() Gruppo A with _log_safe DEBUG [C4/9]`

> Gruppo A = 11 `print()` di scaffolding costruzione partita → `_log_safe` livello DEBUG via `_logger_game`

- [ ] Sostituire `print("Creazione tabellone standard...")` con `_log_safe("[GAME] crea_partita_standard: tabellone creato.", logging.DEBUG, logger=_logger_game)`
- [ ] Sostituire `print(f"Creazione giocatore umano '{nome}'...")` con log DEBUG equivalente
- [ ] Sostituire `print(f"Creazione {n} bot automatici...")` con log DEBUG equivalente
- [ ] Sostituire `print(f"Partita composta da {n} giocatori totali")` con log DEBUG equivalente
- [ ] Sostituire `print("Inizializzazione oggetto Partita...")` con log DEBUG equivalente
- [ ] Sostituire `print("✅ Partita standard creata con successo!")` con log DEBUG equivalente
- [ ] Sostituire `print(f"📸 Stato partita '...'...")` con log DEBUG equivalente
- [ ] Sostituire `print(f"🔍 Controllo tombola:...")` con log DEBUG equivalente
- [ ] Sostituire `print("⏳ Nessuna tombola, gioco continua...")` con log DEBUG equivalente
- [ ] Sostituire `print(f"🔍 Controllo fine partita:...")` con log DEBUG equivalente
- [ ] Sostituire `print("▶️ Partita in corso - continua il loop")` con log DEBUG equivalente
- [ ] Verificare AT-3: ogni nuova riga `_log_safe` usa prefisso `[GAME]` e nessuna emoji
- [ ] `python -m pytest tests/ -q` → nessuna regressione rispetto alla baseline
- [ ] `grep -n "print(" bingo_game/game_controller.py` → ~11 righe residue (Gruppi B, C, D)

**Criterio di done C4**: 11 print Gruppo A rimossi, test verdi, prefissi [GAME] corretti.

---

### COMMIT 5 (C5) — Refactoring Gruppo B+C

**File**: `bingo_game/game_controller.py` (MODIFY)  
**Messaggio**: `refactor(controller): replace print() Gruppo B+C — remove output, log WARNING [C5/9]`

> Gruppo B = 5 `print()` di output di stato → rimozione secca (la TUI legge il valore di ritorno)  
> Gruppo C = 7 `print()` di errori utente → rimozione + `_log_safe` WARNING via `_logger_errors` / `_logger_game`

**Gruppo B — rimozione secca:**

- [ ] Rimuovere `print("✅ Partita avviata con successo!")` → la TUI legge `True`
- [ ] Rimuovere `print(f"✅ Turno #{n}: {numero}")` → la TUI legge `dict["numero_estratto"]`
- [ ] Rimuovere `print(f"🎉 {n} nuovi premi!")` → la TUI legge `dict["premi_nuovi"]`
- [ ] Rimuovere `print("🎉 TOMBOLA RILEVATA...")` → la TUI legge `dict["tombola_rilevata"]`
- [ ] Rimuovere `print("🏁 Partita TERMINATA - esci dal loop")` → la TUI riceve `True` da `partita_terminata()`

**Gruppo C — rimozione + log WARNING:**

- [ ] Sostituire `print(f"❌ Impossibile avviare: {exc}")` con `_log_safe(f"[GAME] Avvio fallito: tipo='{type(exc).__name__}'.", logging.WARNING, logger=_logger_errors)`
- [ ] Sostituire `print(f"❌ Partita già avviata: {exc}")` con log WARNING equivalente (stesso template)
- [ ] Sostituire `print(f"❌ Errore partita generico: {exc}")` con log WARNING equivalente (stesso template)
- [ ] Sostituire `print(f"❌ Impossibile turno: stato '...'")`  con `_log_safe("[GAME] esegui_turno_sicuro: stato '...' non in corso.", logging.WARNING, logger=_logger_game)`
- [ ] Sostituire `print(f"🏁 Partita finita - Numeri esauriti: {exc}")` con log WARNING via `_logger_game`
- [ ] Sostituire `print(f"❌ Turno fallito - Partita non in corso: {exc}")` con log WARNING via `_logger_game`
- [ ] Sostituire `print(f"❌ Errore partita durante turno: {exc}")` con log WARNING via `_logger_game`
- [ ] Verificare AT-3: prefissi `[GAME]` e `[ERR]` corretti per ogni sostituzione, zero emoji
- [ ] `python -m pytest tests/ -q` → nessuna regressione
- [ ] `grep -n "print(" bingo_game/game_controller.py` → ~5 righe residue (solo Gruppo D)

**Criterio di done C5**: 12 print Gruppo B+C eliminati, test verdi, log WARNING presenti con tipo eccezione.

---

### COMMIT 6 (C6) — Refactoring Gruppo D

**File**: `bingo_game/game_controller.py` (MODIFY)  
**Messaggio**: `refactor(controller): replace print() Gruppo D with _log_safe ERROR [C6/9]`

> Gruppo D = 5 `print()` di errori infrastruttura gravi → `_log_safe` livello ERROR/WARNING via `_logger_errors` / `_logger_system`

- [ ] Sostituire `print(f"⚠️ Avvio completato ma stato inatteso: {stato}")` con `_log_safe(f"[SYS] avvia_partita_sicura: stato post-avvio inatteso='{stato}'.", logging.WARNING, logger=_logger_system)`
- [ ] Sostituire `print("❌ ERRORE: Oggetto non è una Partita valida")` (in `avvia`) con `_log_safe(f"[ERR] avvia_partita_sicura: parametro non è Partita. tipo='{type(partita).__name__}'.", logging.ERROR, logger=_logger_errors)`
- [ ] Sostituire `print("❌ ERRORE: Parametro non è una Partita valida")` (in `esegui_turno`) con `_log_safe(f"[ERR] esegui_turno_sicuro: parametro non è Partita. tipo='{type(partita).__name__}'.", logging.ERROR, logger=_logger_errors)`
- [ ] Sostituire `print(f"💥 Errore critico imprevisto: {exc}")` (in `avvia`) con `_log_safe(f"[ERR] avvia_partita_sicura: eccezione imprevista. tipo='{type(exc).__name__}'.", logging.ERROR, logger=_logger_errors)`
- [ ] Sostituire `print(f"💥 Errore critico imprevisto nel turno: {exc}")` con `_log_safe(f"[ERR] esegui_turno_sicuro: eccezione imprevista. tipo='{type(exc).__name__}'.", logging.ERROR, logger=_logger_errors)`
- [ ] Verificare AT-3: prefissi `[SYS]` e `[ERR]` corretti, nessuna emoji
- [ ] `python -m pytest tests/ -q` → nessuna regressione
- [ ] **`grep -n "print(" bingo_game/game_controller.py` → ZERO RISULTATI** 🚨

**Criterio di done C6**: `grep print(` restituisce zero. Il controller è silenzioso. Nessuna regressione.

---

### COMMIT 7 (C7) — Guardie TUI

**File**: `bingo_game/ui/ui_terminale.py` (MODIFY)  
**Messaggio**: `feat(ui): add MESSAGGI_CONTROLLER guards in ui_terminale.py [C7/9]`

- [ ] Aggiungere import `from bingo_game.ui.locales import MESSAGGI_CONTROLLER`
- [ ] Aggiungere import delle 4 costanti `CTRL_*` da `bingo_game.events.codici_controller`
- [ ] Nel metodo che chiama `avvia_partita_sicura`: aggiungere guardia sul `False` con `MESSAGGI_CONTROLLER[CTRL_AVVIO_FALLITO_GENERICO]`
- [ ] Nel metodo che chiama `esegui_turno_sicuro`: aggiungere guardia sul `None` con `MESSAGGI_CONTROLLER[CTRL_TURNO_FALLITO_GENERICO]` come fallback
- [ ] Catturare `ValueError` di `ottieni_stato_sintetico` con blocco `try/except ValueError`
- [ ] Verificare che nessun nuovo testo sia hardcoded in `ui_terminale.py` (tutti i messaggi via `MESSAGGI_CONTROLLER`)
- [ ] Verificare che nessun nuovo import dal Domain layer sia stato aggiunto
- [ ] `python -m py_compile bingo_game/ui/ui_terminale.py` → zero errori
- [ ] `python -m pytest tests/ -q` → nessuna regressione

**Criterio di done C7**: TUI gestisce i tre casi di ritorno anomalo, nessun hardcoding, nessuna regressione.

---

### COMMIT 8 (C8) — Test di Non-Regressione

**File**: `tests/test_silent_controller.py` (CREATE)  
**Messaggio**: `test: add capsys non-regression tests for silent controller [C8/9]`

- [ ] Creare `tests/test_silent_controller.py` con docstring di modulo
- [ ] Implementare fixture `partita_mock` (Partita in stato `in_corso`)
- [ ] Implementare fixture `partita_terminata_mock` (Partita in stato `terminata`)
- [ ] **Classe `TestControllerSilenzioso`** (8 test `capsys.readouterr().out == ""`):
  - [ ] `test_crea_partita_standard_silenzioso`
  - [ ] `test_avvia_partita_sicura_true_silenzioso`
  - [ ] `test_avvia_partita_sicura_false_silenzioso`
  - [ ] `test_esegui_turno_sicuro_dict_silenzioso`
  - [ ] `test_esegui_turno_sicuro_none_silenzioso`
  - [ ] `test_partita_terminata_false_silenzioso`
  - [ ] `test_partita_terminata_true_silenzioso`
  - [ ] `test_ottieni_stato_sintetico_dict_silenzioso`
- [ ] **Classe `TestContrattiRitorno`** (4 test):
  - [ ] `test_avvia_partita_sicura_ritorna_true`
  - [ ] `test_avvia_partita_sicura_ritorna_false_su_eccezione`
  - [ ] `test_ottieni_stato_sintetico_lancia_valueerror_su_non_partita`
  - [ ] `test_esegui_turno_sicuro_ritorna_none_su_partita_non_in_corso`
- [ ] **Classe `TestMESSAGGICONTROLLER`** (3 test):
  - [ ] `test_quattro_chiavi`
  - [ ] `test_chiavi_sono_costanti_corrette`
  - [ ] `test_valori_sono_stringhe_non_vuote`
- [ ] Eseguire `python -m pytest tests/test_silent_controller.py -v` → **tutti 15 verdi**
- [ ] Eseguire `python -m pytest tests/ -q` → nessuna regressione sull'intera suite

**Criterio di done C8**: 15 test verdi, nessuna regressione.

---

### COMMIT 9 (C9) — Chiusura Documentale

**File**: `documentations/API.md`, `documentations/ARCHITECTURE.md`, `documentations/CHANGELOG.md` (UPDATE)  
**Messaggio**: `docs: update API.md, ARCHITECTURE.md, CHANGELOG.md for v0.8.0 [C9/9]`

**`API.md`:**
- [ ] Rimuovere ogni nota su `print()` o stdout nelle firme di `crea_partita_standard`
- [ ] Rimuovere ogni nota su `print()` o stdout nelle firme di `avvia_partita_sicura`
- [ ] Rimuovere ogni nota su `print()` o stdout nelle firme di `esegui_turno_sicuro`
- [ ] Rimuovere ogni nota su `print()` o stdout nelle firme di `ottieni_stato_sintetico`
- [ ] Rimuovere ogni nota su `print()` o stdout nelle firme di `partita_terminata`
- [ ] Rimuovere ogni nota su `print()` o stdout nelle firme di `ha_partita_tombola`
- [ ] Aggiornare le descrizioni con i contratti di ritorno corretti (vedi tabella in PLAN sezione 4.2.1)
- [ ] Verifica: `grep -n "stdout\|print()" documentations/API.md` → zero riferimenti alle funzioni controller

**`ARCHITECTURE.md`:**
- [ ] Rimuovere la freccia `Controller → stdout` dal diagramma layer
- [ ] Aggiornare il diagramma flusso dati: `game_controller → (bool/dict/None) → ui_terminale → stdout`
- [ ] Aggiungere regola invariante: *"Il Controller non scrive mai su stdout"*
- [ ] Aggiungere `bingo_game/events/codici_controller.py` alla mappa moduli con descrizione v0.8.0

**`CHANGELOG.md`:**
- [ ] Aggiungere sezione `## [v0.8.0] - 2026-02-20 Silent Controller`
- [ ] Sezione `### Changed`: game_controller.py (rimozione ~22 print), ui_terminale.py (guardie)
- [ ] Sezione `### Added`: codici_controller.py (4 costanti), MESSAGGI_CONTROLLER (4 voci), test_silent_controller.py (15 test)
- [ ] Sezione `### Fixed`: accessibilità (rimozione emoji), architettura (eliminazione dipendenza Controller → stdout)

**Criterio di done C9**: i 3 file documentali aggiornati, nessuna menzione di stdout/print() nelle firme del controller in API.md.

---

## ✅ Criteri di Completamento

L'implementazione è considerata completa quando **tutte** queste condizioni sono soddisfatte:

- [ ] `grep -n "print(" bingo_game/game_controller.py` → **zero risultati**
- [ ] `python -m pytest tests/test_silent_controller.py` → **15 passed, 0 failed**
- [ ] `python -m pytest tests/` → **nessuna regressione** rispetto alla baseline AT-1
- [ ] `bingo_game/events/codici_controller.py` esiste con 4 costanti corrette
- [ ] `MESSAGGI_CONTROLLER` ha 4 chiavi con testi non vuoti
- [ ] `MESSAGGI_CONTROLLER` esportabile da `bingo_game.ui.locales`
- [ ] TUI gestisce `False` di `avvia_partita_sicura`
- [ ] TUI cattura `ValueError` di `ottieni_stato_sintetico`
- [ ] `API.md`, `ARCHITECTURE.md`, `CHANGELOG.md` aggiornati
- [ ] Tutti i log usano i prefissi corretti `[GAME]`/`[SYS]`/`[ERR]` senza emoji

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] Aggiornare `CHANGELOG.md` con entry v0.8.0 (già nel C9)
- [ ] Aggiornare `API.md` (già nel C9)
- [ ] Aggiornare `ARCHITECTURE.md` (già nel C9)
- [ ] Versione: **MINOR** (v0.7.0 → v0.8.0) — nuova feature retrocompatibile
- [ ] PR aperta con titolo: `feat: Silent Controller v0.8.0 — rimozione print(), logging e localizzazione`
- [ ] PR approvata e mergiata su `main`
- [ ] Questo `TODO.md` aggiornato come `COMPLETATO ✅`

---

## 🏁 Checklist di Chiusura Branch

- [ ] Tutti i 9 commit completati con i messaggi convenzionali corretti
- [ ] `grep -n "print(" bingo_game/game_controller.py` → zero risultati
- [ ] `pytest tests/test_silent_controller.py` → 15 passed
- [ ] `pytest tests/` → nessuna regressione
- [ ] AT-1 (baseline pre-refactoring) verificata
- [ ] AT-2 (no import circolari) verificata dopo C1 e C2
- [ ] AT-3 (prefissi log corretti) verificata dopo C4, C5, C6
- [ ] Documentazione allineata (C9 completato)
- [ ] Branch `feature/silent-controller-v0.8.0` → PR aperta verso `main`
- [ ] PR approvata e merged
- [ ] `TODO.md` marcato `COMPLETATO ✅`

---

## 📌 Note Operative

- Il controller già possiede `_log_safe`, `_logger_game`, `_logger_prizes`, `_logger_system`, `_logger_errors`: **non creare nuovi logger**.
- I log INFO esistenti per premi e tombola in `esegui_turno_sicuro` **vanno preservati** (non rimuoverli).
- Il flag `_partita_terminata_logged` già esistente in `partita_terminata()` **va preservato** per evitare log ripetuti.
- `ottieni_stato_sintetico` è l'**unica** funzione del controller che mantiene il `ValueError`: non convertirlo in `False`/`None`.
- Se `_logger_system` non fosse ancora inizializzato nel controller, aggiungerlo seguendo il pattern degli altri sub-logger.
- I testi di `MESSAGGI_CONTROLLER` devono essere identici al DESIGN (nessuna variazione editoriale autonoma).

---

> *TODO precedente (v0.7.0 — Menu Iniziale TUI): completato ✅ — archiviato il 2026-02-20*

*Generato da: `documentations/PLAN_SILENT_CONTROLLER.md`*  
*Data generazione: 2026-02-20*
