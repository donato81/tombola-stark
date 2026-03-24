# Piano di Implementazione - Refactor confini Partita / GameController

---

## Executive Summary

Tipo: REFACTOR  
Priorita': MEDIA  
Stato: READY  
Branch: `refactory-mappatura-tasti-game-play`  
Versione target: refactor interno branch corrente  
Data creazione: 2026-03-24  
Autore: GitHub Copilot + donato81  
Effort stimato: 4-6 ore  
Commit previsti: 3 commit atomici

---

## Problema / Obiettivo

Ridurre la sovrapposizione di responsabilita' tra `bingo_game/partita.py` e `bingo_game/game_controller.py`, mantenendo invariata la scelta architetturale corrente:

- `Partita` resta motore del dominio e owner del game state.
- `GameController` resta factory della partita standard e facade applicativa per la TUI.

L'obiettivo non e' una riscrittura ampia, ma un primo refactor piccolo, sicuro e adatto a collaudare il workflow automatizzato degli agenti.

---

## Decisioni di Design gia' approvate

Le decisioni derivate dal design approvato sono:

1. Nessuna nuova factory separata in questa iterazione.
2. Nessuna modifica radicale alla TUI.
3. Il controller resta punto d'ingresso per `ui_terminale.py`.
4. Le decisioni di dominio devono vivere in `Partita`, non nel controller.
5. Il controller puo' adattare dati e loggare, ma non ridefinire la semantica del turno.

---

## Soluzione proposta

Il refactor viene suddiviso in tre fasi molto piccole:

1. Analisi contratti e test di protezione sul confine attuale.
2. Pulizia minima del controller sui punti di duplicazione o derivazione ridondante.
3. Allineamento test e documentazione operativa del refactor.

Questa divisione minimizza il rischio e permette di validare il sistema agenti su una modifica semplice ma reale.

---

## File coinvolti

### Codice

- `bingo_game/partita.py`
- `bingo_game/game_controller.py`

### Test

- `tests/test_partita.py`
- `tests/test_game_controller.py`
- `tests/unit/test_game_controller_loop.py`

### Documentazione workflow

- `documentations/2 - project/DESIGN_refactor_confini_partita_gamecontroller.md`
- `documentations/3 - planning/PLAN_refactor_confini_partita_gamecontroller.md`
- `documentations/4 - todo file/TODO_refactor_confini_partita_gamecontroller.md`

---

## Rischi e strategia di contenimento

### Rischi

- regressione su `esegui_turno_sicuro`
- regressione su `ottieni_stato_sintetico`
- divergenza tra stato in `Partita` e stato di supporto nel controller
- rottura del contratto atteso dalla TUI

### Contenimento

- partire da test di protezione prima del refactor
- limitare la prima iterazione a punti specifici e misurabili
- evitare modifiche contestuali in TUI o logging non indispensabili

---

## Piano di implementazione

### FASE 1 - Stabilizzazione del confine con test mirati

Commit previsto: `test(controller): add boundary regression coverage for Partita and GameController [Phase 1/3]`

Obiettivo:

- catturare con test il contratto reale tra `Partita` e `GameController`
- proteggere i punti sensibili prima di toccare il codice

Task:

- aggiungere o aggiornare test per `esegui_turno_sicuro`
- aggiungere o aggiornare test per `ottieni_stato_sintetico`
- verificare che il controller non alteri in modo inatteso i dati principali prodotti da `Partita`
- aggiungere uno smoke test sul flusso `Partita.esegui_turno()` -> `GameController.esegui_turno_sicuro()`

Exit criteria:

- test verdi sui contratti minimi del confine
- nessuna modifica di produzione ancora necessaria oltre all'eventuale supporto minimo al test

---

### FASE 2 - Refactor minimo del controller

Commit previsto: `refactor(controller): reduce duplicated game-state handling [Phase 2/3]`

Obiettivo:

- ridurre il piu' piccolo insieme di duplicazioni tra controller e dominio senza cambiare l'API pubblica verso la TUI

Task:

- analizzare in `game_controller.py` i punti dove il controller interpreta o conserva stato gia' posseduto da `Partita`
- rimuovere o semplificare almeno un punto di duplicazione reale e a basso rischio
- mantenere invariati i contratti pubblici di ritorno per TUI e test esistenti
- lasciare logging e orchestration nel controller, ma spostare eventuali decisioni di dominio dove gia' spettano a `Partita`

Possibili target iniziali:

- riduzione della logica difensiva ridondante sul dizionario turno
- chiarimento dell'uso dei contatori di modulo solo dove indispensabili alla telemetria
- migliore delega a `Partita.get_stato_completo()` senza ridefinire il significato del dato

Exit criteria:

- codice piu' lineare nel controller
- nessuna regressione sulla TUI
- test fase 1 ancora verdi

---

### FASE 3 - Allineamento finale e chiusura della tranche

Commit previsto: `docs(tests): align boundary refactor notes and finalize coverage [Phase 3/3]`

Obiettivo:

- chiudere la tranche con test finali e tracciabilita' documentale minima

Task:

- eseguire i test rilevanti del refactor
- rifinire eventuali test fragili o troppo dipendenti dall'implementazione interna
- aggiornare il TODO del task segnando le fasi completate
- documentare, se necessario, il risultato sintetico del refactor nei documenti di progetto gia' previsti dal flusso

Exit criteria:

- tutti i test mirati passano
- TODO aggiornato
- tranche pronta per eventuale fase successiva piu' ampia

---

## Sequenza consigliata

1. Scrivere prima i test di protezione.
2. Intervenire solo su `game_controller.py` e sui punti strettamente necessari di `partita.py`.
3. Verificare subito la compatibilita' con test esistenti e helper TUI.
4. Chiudere la tranche senza ampliare il perimetro del refactor.

---

## Criteri di successo

Il piano e' considerato completato se:

- il refactor riduce davvero almeno una duplicazione o ambiguita' concreta tra controller e dominio
- il contratto verso la TUI resta stabile
- i test dimostrano il confine desiderato in modo piu' chiaro di prima
- il perimetro della modifica resta piccolo e adatto a un primo collaudo del framework agenti
