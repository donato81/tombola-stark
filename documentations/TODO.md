# ✅ TODO — Implementazione Menu Iniziale TUI (v0.7.0)

> **Basato su**: `documentations/PLAN_TERMINAL_START_MENU.md` v1.0
> **Design di riferimento**: `documentations/DESIGN_TERMINAL_START_MENU.md` v1.2 (READY)
> **Branch di lavoro**: `feature/terminal-start-menu`
> **Versione target**: `v0.7.0`
> **Ultimo aggiornamento**: 2026-02-19

---

## 🚨 Regole Architetturali (ricordare sempre)

> Questi vincoli si applicano a **ogni** commit. Copilot deve rispettarli senza eccezioni.

- **Separazione dei layer**: `TerminalUI` (Interface Layer) consuma **solo** `game_controller.py` (Application Layer). Vietato importare direttamente dal Domain (`partita.py`, `giocatore_base.py`, ecc.).
- **Zero stringhe hardcoded**: ogni testo visibile all'utente deve provenire da `MESSAGGI_CONFIGURAZIONE` o `MESSAGGI_ERRORI` in `it.py`. Nessun `print("testo")` letterale in `ui_terminale.py`.
- **Logger centralizzato**: usare sempre `logging.getLogger(__name__)`. Non usare `print()` per debug. Prefisso `[TUI]` per tutti i messaggi di log dell'interfaccia.
- **Contratto API obbligatorio**: il metodo del Controller è sempre il two-step `crea_partita_standard()` + `avvia_partita_sicura()`. Nessun altro metodo di avvio esiste.

---

## COMMIT 1 — Infrastruttura Chiavi

**File**: `bingo_game/events/codici_configurazione.py` (CREARE)
**Messaggio commit**: `feat(events): add codici_configurazione.py with 9 config key constants`

### Task

- [ ] Creare il file `bingo_game/events/codici_configurazione.py`
- [ ] Aggiungere docstring modulo con descrizione, pattern di riferimento e `Version: v0.7.0`
- [ ] Definire `from __future__ import annotations`
- [ ] Definire il tipo alias `Codici_Configurazione = str`
- [ ] Aggiungere costante `CONFIG_BENVENUTO: Codici_Configurazione = "CONFIG_BENVENUTO"`
- [ ] Aggiungere costante `CONFIG_CONFERMA_AVVIO: Codici_Configurazione = "CONFIG_CONFERMA_AVVIO"`
- [ ] Aggiungere costante `CONFIG_RICHIESTA_NOME: Codici_Configurazione = "CONFIG_RICHIESTA_NOME"`
- [ ] Aggiungere costante `CONFIG_RICHIESTA_BOT: Codici_Configurazione = "CONFIG_RICHIESTA_BOT"`
- [ ] Aggiungere costante `CONFIG_RICHIESTA_CARTELLE: Codici_Configurazione = "CONFIG_RICHIESTA_CARTELLE"`
- [ ] Aggiungere costante `CONFIG_ERRORE_NOME_VUOTO: Codici_Configurazione = "CONFIG_ERRORE_NOME_VUOTO"`
- [ ] Aggiungere costante `CONFIG_ERRORE_NOME_TROPPO_LUNGO: Codici_Configurazione = "CONFIG_ERRORE_NOME_TROPPO_LUNGO"`
- [ ] Aggiungere costante `CONFIG_ERRORE_BOT_RANGE: Codici_Configurazione = "CONFIG_ERRORE_BOT_RANGE"`
- [ ] Aggiungere costante `CONFIG_ERRORE_CARTELLE_RANGE: Codici_Configurazione = "CONFIG_ERRORE_CARTELLE_RANGE"`
- [ ] Verificare coerenza di stile con `bingo_game/events/codici_errori.py` (pattern di riferimento)
- [ ] Verificare: `python -m py_compile bingo_game/events/codici_configurazione.py` → nessun errore

### Criterio di Successo

> Il commit è completo quando:
> `python -c "from bingo_game.events.codici_configurazione import CONFIG_BENVENUTO; print('OK')"` stampa `OK` senza errori.

---

## COMMIT 2 — Localizzazione

**File**: `bingo_game/ui/locales/it.py` (ESTENDERE)
**Messaggio commit**: `feat(locales): add MESSAGGI_CONFIGURAZIONE dict to it.py (9 keys)`

### Task

- [ ] Aprire `bingo_game/ui/locales/it.py` e leggere il contenuto attuale
- [ ] Aggiungere in testa al file (insieme agli altri import di `codici_*`):
  `from bingo_game.events.codici_configurazione import Codici_Configurazione`
- [ ] Verificare che `MappingProxyType` e `Mapping` siano già importati (lo sono)
- [ ] Aggiungere in **coda al file** (dopo tutti gli altri dizionari esistenti) il dizionario:
  `MESSAGGI_CONFIGURAZIONE: Mapping[Codici_Configurazione, tuple[str, ...]] = MappingProxyType({...})`
- [ ] Inserire la chiave `"CONFIG_BENVENUTO": ("Benvenuto in Tombola Stark!",)`
- [ ] Inserire la chiave `"CONFIG_CONFERMA_AVVIO": ("Configurazione completata. Avvio partita...",)`
- [ ] Inserire la chiave `"CONFIG_RICHIESTA_NOME": ("Inserisci il tuo nome (max 15 caratteri): ",)`
- [ ] Inserire la chiave `"CONFIG_RICHIESTA_BOT": ("Inserisci il numero di bot (1-7): ",)`
- [ ] Inserire la chiave `"CONFIG_RICHIESTA_CARTELLE": ("Inserisci il numero di cartelle (1-6): ",)`
- [ ] Inserire la chiave `"CONFIG_ERRORE_NOME_VUOTO": ("Errore: Nome non valido.", "Inserisci almeno un carattere.",)`
- [ ] Inserire la chiave `"CONFIG_ERRORE_NOME_TROPPO_LUNGO": ("Errore: Nome troppo lungo.", "Inserisci al massimo 15 caratteri.",)`
- [ ] Inserire la chiave `"CONFIG_ERRORE_BOT_RANGE": ("Errore: Numero bot non valido.", "Inserisci un valore tra 1 e 7.",)`
- [ ] Inserire la chiave `"CONFIG_ERRORE_CARTELLE_RANGE": ("Errore: Numero cartelle non valido.", "Inserisci un valore tra 1 e 6.",)`
- [ ] Verificare che i dizionari esistenti non siano stati modificati
- [ ] Verificare: `python -m py_compile bingo_game/ui/locales/it.py` → nessun errore

### Criterio di Successo

> Il commit è completo quando:
> `python -c "from bingo_game.ui.locales.it import MESSAGGI_CONFIGURAZIONE; print(len(MESSAGGI_CONFIGURAZIONE))"` stampa `9`.

---

## COMMIT 3 — Implementazione Core UI

**File**: `bingo_game/ui/ui_terminale.py` (IMPLEMENTARE — attualmente vuoto)
**Messaggio commit**: `feat(ui): implement TerminalUI class with sequential state machine A-E`

### Task — Struttura Classe

- [ ] Aggiungere `from __future__ import annotations` e docstring modulo
- [ ] Importare `logging` (libreria standard)
- [ ] Importare `MESSAGGI_CONFIGURAZIONE` e `MESSAGGI_ERRORI` da `bingo_game.ui.locales.it`
- [ ] Importare `crea_partita_standard` e `avvia_partita_sicura` da `bingo_game.game_controller`
- [ ] Importare `TerminalRenderer` da `bingo_game.ui.renderers.renderer_terminal`
- [ ] Definire `logger = logging.getLogger(__name__)` a livello modulo
- [ ] Definire costanti modulo: `_LUNGHEZZA_MAX_NOME = 15`, `_BOT_MIN = 1`, `_BOT_MAX = 7`, `_CARTELLE_MIN = 1`, `_CARTELLE_MAX = 6`
- [ ] Creare classe `TerminalUI` con docstring Google-style completa

### Task — Metodo `__init__`

- [ ] Istanziare `self._renderer = TerminalRenderer()` (per Fase 2+, non usato ora)
- [ ] Aggiungere `logger.debug("[TUI] TerminalUI inizializzata.")`
- [ ] Aggiungere docstring con nota su `_renderer` e `Version: v0.7.0`

### Task — Metodo `avvia()` (entry point pubblico)

- [ ] Aggiungere `logger.info("[TUI] Avvio configurazione partita.")` (**INFO** obbligatorio)
- [ ] Chiamare `self._mostra_benvenuto()`
- [ ] Chiamare `nome = self._chiedi_nome()`
- [ ] Chiamare `numero_bot = self._chiedi_bot()`
- [ ] Chiamare `numero_cartelle = self._chiedi_cartelle()`
- [ ] Chiamare `self._avvia_partita(nome, numero_bot, numero_cartelle)`

### Task — Metodo `_mostra_benvenuto()` (Stato A)

- [ ] Aggiungere `logger.debug("[TUI] Stato A: BENVENUTO")` (**DEBUG** transizione)
- [ ] Chiamare `self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_BENVENUTO"])`

### Task — Metodo `_chiedi_nome()` (Stato B)

- [ ] Aggiungere `logger.debug("[TUI] Stato B: ATTESA_NOME")` (**DEBUG** transizione)
- [ ] Implementare loop `while True:`
- [ ] Acquisire `input_raw = self._chiedi_input("CONFIG_RICHIESTA_NOME")`
- [ ] Applicare `nome = input_raw.strip()` (OBBLIGATORIO: primo passo)
- [ ] Aggiungere `logger.debug(f"[TUI] Nome dopo strip: '{nome}' (len={len(nome)})")` (**DEBUG** sanitizzazione)
- [ ] Controllo vuoto: `if len(nome) == 0:` → `logger.warning(...)` (**WARNING** obbligatorio) + `self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_NOME_VUOTO"])` + `continue`
- [ ] Controllo lunghezza: `if len(nome) > _LUNGHEZZA_MAX_NOME:` → `logger.warning(...)` (**WARNING** obbligatorio) + `self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_NOME_TROPPO_LUNGO"])` + `continue`
- [ ] Aggiungere `logger.debug(f"[TUI] Nome valido acquisito: '{nome}'")` (**DEBUG**) + `return nome`
- [ ] Verificare ordine priorità: (1) strip → (2) non vuoto → (3) len ≤ 15

### Task — Metodo `_chiedi_bot()` (Stato C)

- [ ] Aggiungere `logger.debug("[TUI] Stato C: ATTESA_BOT")` (**DEBUG** transizione)
- [ ] Implementare loop `while True:`
- [ ] Acquisire `input_raw = self._chiedi_input("CONFIG_RICHIESTA_BOT")`
- [ ] Try/except `int(input_raw)` → `except ValueError:` → `logger.warning(...)` (**WARNING**) + `self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])` + `continue`
- [ ] Controllo range: `if not (_BOT_MIN <= valore <= _BOT_MAX):` → `logger.warning(...)` (**WARNING**) + `self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_BOT_RANGE"])` + `continue`
- [ ] Aggiungere `logger.debug(f"[TUI] Numero bot valido: {valore}")` + `return valore`
- [ ] Verificare riuso `MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]` (non creare chiave duplicata)

### Task — Metodo `_chiedi_cartelle()` (Stato D)

- [ ] Aggiungere `logger.debug("[TUI] Stato D: ATTESA_CARTELLE")` (**DEBUG** transizione)
- [ ] Implementare loop `while True:`
- [ ] Acquisire `input_raw = self._chiedi_input("CONFIG_RICHIESTA_CARTELLE")`
- [ ] Try/except `int(input_raw)` → `except ValueError:` → `logger.warning(...)` (**WARNING**) + `self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])` + `continue`
- [ ] Controllo range: `if not (_CARTELLE_MIN <= valore <= _CARTELLE_MAX):` → `logger.warning(...)` (**WARNING**) + `self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_CARTELLE_RANGE"])` + `continue`
- [ ] Aggiungere `logger.debug(f"[TUI] Numero cartelle valido: {valore}")` + `return valore`
- [ ] Ricordare: limite 1–6 è scelta UX (screen reader), non vincolo del Controller

### Task — Metodo `_avvia_partita()` (Stato E)

- [ ] Aggiungere `logger.debug("[TUI] Stato E: AVVIO_PARTITA")` (**DEBUG** transizione)
- [ ] Chiamare `self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_CONFERMA_AVVIO"])` (PRIMA del Controller)
- [ ] Chiamare `partita = crea_partita_standard(nome_giocatore_umano=nome, num_cartelle_umano=numero_cartelle, num_bot=numero_bot)`
- [ ] Chiamare `avvia_partita_sicura(partita)`
- [ ] Aggiungere `logger.info(f"[TUI] Configurazione completata. nome='{nome}', bot={numero_bot}, cartelle={numero_cartelle}.")` (**INFO** obbligatorio)

### Task — Helper Privati

- [ ] Implementare `_stampa_righe(self, righe: tuple[str, ...]) -> None`: loop `for riga in righe: print(riga)`
- [ ] Implementare `_chiedi_input(self, chiave_prompt: str) -> str`: `return input(MESSAGGI_CONFIGURAZIONE[chiave_prompt][0])`
- [ ] Aggiungere docstring Google-style a entrambi gli helper

### Task — Verifica Post-Implementazione

- [ ] Nessuna stringa hardcoded: `grep -n '"Benvenuto\|"Inserisci\|"Errore\|"Configurazione' bingo_game/ui/ui_terminale.py` deve restituire **0 righe**
- [ ] Nessun import dal Domain layer (`partita.py`, `giocatore_base.py`, ecc.)
- [ ] Verifica sintassi: `python -m py_compile bingo_game/ui/ui_terminale.py`
- [ ] Verifica import: `python -c "from bingo_game.ui.ui_terminale import TerminalUI; print('OK')"`

### Criterio di Successo

> Il commit è completo quando:
> - `python -c "from bingo_game.ui.ui_terminale import TerminalUI; print('OK')"` stampa `OK`
> - I log `[TUI]` compaiono nel file di log eseguendo manualmente `python main.py` con input validi
> - I 3 livelli di log sono presenti: almeno un `INFO`, un `WARNING` (inserendo un input errato), un `DEBUG`

---

## COMMIT 4 — Integrazione Entry Point

**File**: `main.py` (AGGIORNARE)
**Messaggio commit**: `feat(main): wire TerminalUI to application entry point`

### Task

- [ ] Leggere il contenuto attuale di `main.py` prima di modificare
- [ ] Aggiungere import: `from bingo_game.ui.ui_terminale import TerminalUI`
- [ ] Verificare se esiste già una funzione `main()`: in caso sì, integrare senza sovrascrivere
- [ ] Aggiungere istanziazione e avvio: `tui = TerminalUI()` + `tui.avvia()`
- [ ] Assicurarsi che il blocco `if __name__ == "__main__":` chiami `main()`
- [ ] Verificare sintassi: `python -m py_compile main.py`
- [ ] Test rapido di avvio manuale: `python main.py` → compare il messaggio di benvenuto

### Criterio di Successo

> Il commit è completo quando:
> `python main.py` avvia il flusso di configurazione completo senza errori e permette di inserire nome, bot e cartelle.
> Questo abilita anche l’esecuzione manuale del Protocollo TC01–TC05.

---

## COMMIT 5 — Testing

**File**: `tests/unit/test_ui_terminale.py` (CREARE)
**Messaggio commit**: `test(ui): add unit tests for TerminalUI validation loops (7 tests)`

### Task — Setup File di Test

- [ ] Creare il file `tests/unit/test_ui_terminale.py`
- [ ] Aggiungere `from __future__ import annotations` e docstring modulo con riferimento ai TC
- [ ] Importare `from unittest.mock import patch, MagicMock`
- [ ] Importare `import pytest`
- [ ] Importare `from bingo_game.ui.ui_terminale import TerminalUI`

### Task — Classe `TestValidazioneNome` (Stato B)

- [ ] Implementare `test_tc01_nome_vuoto_dopo_strip`: input `["   ", "Marco"]` → verifica errore `"Errore: Nome non valido."` + ritorno `"Marco"`
- [ ] Implementare `test_tc02_nome_troppo_lungo`: input `["NomeMoltoLungoOltreQuindici", "Marco"]` → verifica errore `"Errore: Nome troppo lungo."`
- [ ] Implementare `test_strip_applicato_prima_del_check`: input `"  Marco  "` → ritorno `"Marco"` (nessun errore, strip corretto)

### Task — Classe `TestValidazioneBot` (Stato C)

- [ ] Implementare `test_tc03_bot_sotto_range`: input `["0", "3"]` → verifica errore `"Errore: Numero bot non valido."`
- [ ] Implementare `test_tc03_bot_sopra_range`: input `["9", "3"]` → verifica errore `"Errore: Numero bot non valido."`
- [ ] Implementare `test_bot_tipo_non_valido`: input `["tre", "3"]` → verifica errore `"Errore: Tipo non valido."` (riuso `MESSAGGI_ERRORI`)

### Task — Classe `TestValidazioneCartelle` (Stato D)

- [ ] Implementare `test_tc04_cartelle_fuori_range`: input `["7", "2"]` → verifica errore `"Errore: Numero cartelle non valido."`

### Task — Classe `TestFlussoFelice`

- [ ] Implementare `test_flusso_felice_completo`: input `["Marco", "3", "2"]` → verifica `crea_partita_standard(nome_giocatore_umano="Marco", num_cartelle_umano=2, num_bot=3)` chiamato correttamente
- [ ] Verifica `avvia_partita_sicura(mock_partita)` chiamata con l’oggetto restituito da `crea_partita_standard`

### Task — Esecuzione Unit Test

- [ ] Eseguire: `python -m pytest tests/unit/test_ui_terminale.py -v`
- [ ] Verificare: **tutti e 7 i test verdi** prima di procedere al Commit 6
- [ ] In caso di fallimento: consultare sezione "Troubleshooting" del `PLAN_TERMINAL_START_MENU.md`

### Task — Protocollo di Verifica Manuale TC01–TC05

> Eseguire `python main.py` e seguire manualmente ogni test case

- [ ] **TC01**: inserire `"   "` (3 spazi) come nome → atteso: errore `CONFIG_ERRORE_NOME_VUOTO` + re-prompt
- [ ] **TC02**: inserire `"NomeMoltoLungoOltreQuindici"` (28 char) come nome → atteso: errore `CONFIG_ERRORE_NOME_TROPPO_LUNGO`
- [ ] **TC03**: inserire `"0"` come numero bot → atteso: errore `CONFIG_ERRORE_BOT_RANGE`; poi inserire `"9"` → stesso errore
- [ ] **TC04**: inserire `"7"` come numero cartelle → atteso: errore `CONFIG_ERRORE_CARTELLE_RANGE`
- [ ] **TC05**: eseguire l’intero flusso con **screen reader attivo** (NVDA / JAWS / Orca):
  - [ ] Il messaggio di benvenuto viene letto all’avvio
  - [ ] Ogni prompt viene letto prima dell’attesa input
  - [ ] Gli errori vengono letti PRIMA del re-prompt
  - [ ] Nessun artefatto grafico vocalizzato (nessun box, nessuna emoji)
  - [ ] La conferma di avvio viene letta prima del passaggio alla Fase 2

### Criterio di Successo

> Il commit è completo quando:
> - `pytest tests/unit/test_ui_terminale.py` restituisce **7 passed, 0 failed**
> - I 5 test case manuali (TC01–TC05) sono stati eseguiti e smarcati

---

## COMMIT 6 — Chiusura Documentale

**File**: 5 file di documentazione (AGGIORNARE)
**Messaggio commit**: `docs: update README, CHANGELOG, API, ARCHITECTURE, LOGGING for v0.7.0`

### Task — `README.md`

- [ ] Aggiungere o aggiornare la sezione "Avvio" con il comando: `python main.py`
- [ ] Aggiungere descrizione breve del flusso di configurazione (nome → bot → cartelle)
- [ ] Aggiungere nota accessibilità: compatibile con screen reader NVDA/JAWS/Orca
- [ ] Verificare che la versione indicata nel README sia allineata a `v0.7.0`

### Task — `CHANGELOG.md`

- [ ] Aggiungere nuova sezione `## [v0.7.0] - 2026-xx-xx` in cima alla lista versioni
- [ ] Sezione `### Aggiunto`:
  - `TerminalUI`: interfaccia da terminale, flusso configurazione pre-partita (Fase 1)
  - `codici_configurazione.py`: 9 costanti-chiave per localizzazione configurazione
  - `MESSAGGI_CONFIGURAZIONE` in `it.py`: 9 chiavi con testi italiani
  - `tests/unit/test_ui_terminale.py`: 7 unit test (mock input/print)
- [ ] Sezione `### Modificato`:
  - `main.py`: aggiunto entry point `TerminalUI.avvia()`
  - `it.py`: esteso con dizionario `MESSAGGI_CONFIGURAZIONE`

### Task — `API.md`

- [ ] Aggiungere sezione dedicata `TerminalUI` (Interface Layer)
- [ ] Documentare il metodo pubblico: `TerminalUI.avvia() -> None`
- [ ] Includere: descrizione, side effects (avvia la partita), dipendenze (GameController), note di accessibilità
- [ ] Specificare che è l’unico metodo pubblico consumabile da `main.py`

### Task — `ARCHITECTURE.md`

- [ ] Aggiungere `TerminalUI` nel diagramma del layer Interface
- [ ] Aggiornare il flusso TUI: `main.py` → `TerminalUI` → `GameController`
- [ ] Specificare che `TerminalRenderer` è istanziato in `TerminalUI.__init__` ma usato dalla Fase 2+

### Task — `DESIGN_LOGGING_SYSTEM.md`

- [ ] Aggiungere sezione o tabella con i nuovi eventi `[TUI]`
- [ ] Registrare: `INFO` — avvio configurazione, configurazione completata
- [ ] Registrare: `WARNING` — nome vuoto, nome troppo lungo, bot tipo non valido, bot fuori range, cartelle tipo non valido, cartelle fuori range
- [ ] Registrare: `DEBUG` — transizioni di stato (A→B→C→D→E), valori dopo `.strip()`, valori validati

### Criterio di Successo

> Il commit è completo quando tutti e 5 i file sono stati aggiornati e il branch `feature/terminal-start-menu` è pronto per il merge in `main`.

---

## 🏁 Checklist di Chiusura Branch

- [ ] Tutti i 6 commit completati con i messaggi convenzionali corretti
- [ ] `python -m pytest tests/unit/test_ui_terminale.py` → 7 passed, 0 failed
- [ ] `python main.py` → flusso completo funzionante
- [ ] TC01–TC05 eseguiti manualmente e smarcati
- [ ] Nessuna stringa hardcoded in `ui_terminale.py` (grep pulito)
- [ ] Nessun import dal Domain layer in `ui_terminale.py`
- [ ] Tutti i log `[TUI]` presenti nei livelli corretti (INFO/WARNING/DEBUG)
- [ ] Documentazione allineata (Commit 6 completato)
- [ ] Branch `feature/terminal-start-menu` → PR aperta verso `main`
- [ ] PR approvata e merged
- [ ] `TODO.md` archiviato o aggiornato come `COMPLETATO`

---

*Generato da: `documentations/PLAN_TERMINAL_START_MENU.md` v1.0*
*Data generazione: 2026-02-19*
