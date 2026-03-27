# Analisi qualitativa del codice — Tombola Stark

## 1. Architettura reale osservata

- Entry point: `main.py`.
- Domain core: `bingo_game/partita.py`, `bingo_game/tabellone.py`, `bingo_game/cartella.py`.
- Application/controller: `bingo_game/game_controller.py`.
- UI terminale: `bingo_game/ui/ui_terminale.py`.
- Supporto: `bingo_game/players`, `bingo_game/events`, `bingo_game/validations`, `bingo_game/exceptions`, `bingo_game/logging`.

La logica del gioco è centrata in `Partita`; il controller espone create/avvia/esegui_turno; la TUI delega al controller e non accede direttamente al dominio.

## 2. Stato qualitativo del codice

### Punti forti
- separazione concettuale tra domain, controller e UI
- eccezioni specifiche in `bingo_game/exceptions`
- set di test esistenti su `tabellone`, `cartella`, `partita`
- flusso TUI configurazione/loop già strutturato con stato macchina

### Aree di attenzione
- `game_controller.py` rischia responsabilità e accoppiamento elevati
- consumo di variabili di modulo per stato di partita/logging
- commenti molto estesi, che rendono la lettura del codice più lenta

## 3. Rischi per implementazioni future

1. modifiche al flusso estrazioni/premi in `Partita` possono rompere il loop e i test di integrazione
2. eventuali estensioni del controller potrebbero generare un mega-file difficile da mantenere
3. potenziale fragilità sul passaggio stato -> UI (riporti, controller/stato di partita)

## 4. Testing qualitativo

- copertura focalizzata sui moduli fondamentali: `Cartella`, `Tabellone`, `Partita`.
- area meno coperta: `game_controller`, loop completo TUI, gestione eventi su `bingo_game/events`.

## 5. Allineamento con design/plan

- in documentations ci sono file `PLAN_*` e `DESIGN_*` coerenti con le feature principali (Terminal start menu, Game loop, logging, silent controller, bot attivo)
- il codice reale è abbastanza allineato a queste roadmap (con un dominio valido e TUI presente), ma è necessario validare se tutte le specifiche su eventi/controlli sono implementate.

## 6. Raccomandazione pratica (ordine prossimo lavoro)

1. rifattorizzare i confini tra `Partita` e `GameController` (game logic vs orchestration)
2. implementare flusso turno con test di integrazione in `tests/test_partita.py` e `tests/test_game_controller.py`
3. estendere TUI in `bingo_game/ui/ui_terminale.py` con nuovo scenario (o refactor del loop esistente)
4. aggiungere test end-to-end minimo (crea+avvia+turno) per prevenire regressioni

## 7. File da leggere per primi

- `README.md`
- `main.py`
- `bingo_game/partita.py`
- `bingo_game/game_controller.py`
- `bingo_game/ui/ui_terminale.py`
- `tests/test_partita.py`
- `tests/test_game_controller.py`
- `tests/test_silent_controller.py`

## 8. Mismatch e note

- il profilo in `.github/project-profile.md` indica `clean-architecture-4-layer`; il progetto reale usa una versione semplificata ma efficace, quindi il team deve mantenere la disciplina di separazione.
- la feature `tasti rapidi` è in place e integrata con la TUI; il prossimo focus va sul game loop e gestione premi prima di aggiungere nuove funzionalità complex.
