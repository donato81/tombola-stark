---
type: plan
status: READY
feature: refactor-riepilogo-sintetico-partita-gamecontroller
agent: Agent-Plan
date: 2026-03-24
---

# Piano di Implementazione - Refactor riepilogo sintetico Partita / GameController

---

## Executive Summary

Tipo: REFACTOR  
Priorita': MEDIA  
Stato: DRAFT  
Branch: `refactory-mappatura-tasti-game-play`  
Versione target: refactor interno branch corrente  
Data creazione: 2026-03-24  
Autore: GitHub Copilot + donato81  
Effort stimato: 2-4 ore  
Commit previsti: 3 commit atomici

---

## Problema / Obiettivo

La tranche precedente ha chiarito che `Partita` e' owner dello stato di gioco e che `GameController` non deve mantenere copie ridondanti di dati di dominio.

Resta pero' un punto ancora migliorabile: il riepilogo sintetico dello stato passa ancora dal controller tramite `ottieni_stato_sintetico(partita)`, che oggi:

- chiama `Partita.get_stato_completo()`;
- valida in modo difensivo il dizionario ritornato;
- decide implicitamente che il riepilogo pubblico coincida con quella fotografia completa.

L'obiettivo di questa mini-tranche e' spostare ancora di piu' verso `Partita` la responsabilita' del riepilogo sintetico, lasciando al controller solo guardie, logging e inoltro del risultato.

---

## Decisioni di Design gia' approvate e riusate

Questa mini-tranche eredita le decisioni del refactor precedente:

1. `Partita` resta owner dello stato e della semantica del gioco.
2. `GameController` resta facade applicativa verso TUI e helper UI.
3. Nessuna modifica architetturale alla TUI.
4. Nessuna nuova factory o service aggiuntivo.
5. Nessun ampliamento verso logging, loop partita o creazione partita.

---

## Soluzione proposta

Il refactor viene suddiviso in tre passi molto piccoli:

1. Fissare con test il fatto che il riepilogo sintetico e' una responsabilita' owned da `Partita` e solo esposta dal controller.
2. Aggiungere in `Partita` un metodo dedicato al riepilogo sintetico e semplificare `ottieni_stato_sintetico()` in `game_controller.py` come puro adattatore/guardia.
3. Rieseguire i test mirati e chiudere la tranche con aggiornamento minimo della documentazione operativa.

---

## File coinvolti

### Codice

- `bingo_game/partita.py`
- `bingo_game/game_controller.py`

### Test

- `tests/test_partita.py`
- `tests/test_game_controller.py`

### Documentazione workflow

- `documentations/3 - planning/PLAN_refactor_riepilogo_sintetico_partita_gamecontroller.md`
- `documentations/4 - todo file/TODO_refactor_riepilogo_sintetico_partita_gamecontroller.md`

---

## Rischi e strategia di contenimento

### Rischi

- regressione sul contratto pubblico di `ottieni_stato_sintetico()`
- rottura di helper TUI che si aspettano lo stesso formato del dizionario
- duplicazione parziale ancora presente se il controller continua a reinterpretare il dato

### Contenimento

- partire da test di protezione sul formato di output
- non cambiare chiavi o struttura osservabile dalla TUI
- introdurre un metodo nuovo in `Partita` senza toccare il flusso del turno
- mantenere nel controller solo i controlli difensivi davvero necessari al bordo applicativo

---

## Piano di implementazione

### FASE 1 - Protezione del confine sul riepilogo sintetico

Commit previsto: `test(controller): lock synthetic-state delegation toward Partita [Phase 1/3]`

Obiettivo:

- fissare con test che il riepilogo sintetico e' esposto dal controller ma nasce dalla partita

Task:

- analizzare il formato attuale di `ottieni_stato_sintetico()`
- aggiungere o aggiornare test in `tests/test_game_controller.py` sul contratto del riepilogo sintetico
- aggiungere o aggiornare test in `tests/test_partita.py` solo per il nuovo metodo sintetico se necessario
- verificare che il controller non alteri le chiavi pubbliche attese

Exit criteria:

- test verdi sul formato pubblico del riepilogo
- confine desiderato espresso chiaramente nei test

---

### FASE 2 - Spostamento del riepilogo sintetico verso Partita

Commit previsto: `refactor(controller): delegate synthetic state summary to Partita [Phase 2/3]`

Obiettivo:

- far si' che `Partita` esponga un riepilogo sintetico dedicato e che il controller si limiti a inoltrarlo

Task:

- introdurre in `bingo_game/partita.py` un metodo piccolo e pubblico per il riepilogo sintetico
- ridurre `ottieni_stato_sintetico()` in `bingo_game/game_controller.py` a guardia, delega e log minimo
- evitare di trasformare `get_stato_completo()` in un nuovo punto di accoppiamento indiretto
- mantenere stabile il contratto esterno verso TUI e helper esistenti

Exit criteria:

- `Partita` e' fonte esplicita del riepilogo sintetico
- `GameController` non ricostruisce il quadro dello stato se il dominio lo sa gia'
- test fase 1 ancora verdi

---

### FASE 3 - Chiusura mini-tranche

Commit previsto: `docs(tests): finalize synthetic-state boundary refactor [Phase 3/3]`

Obiettivo:

- chiudere la mini-tranche senza estendere il perimetro del refactor

Task:

- rieseguire i test mirati del confine `Partita` / `GameController`
- aggiornare il TODO della mini-tranche
- annotare eventuali limiti residui per tranche successive
- allineare `CHANGELOG.md` solo se la tranche viene implementata davvero

Exit criteria:

- test mirati verdi
- TODO aggiornato
- nessun ampliamento a TUI, logging o loop di gioco

---

## Sequenza consigliata

1. Fissare prima il contratto del riepilogo sintetico.
2. Introdurre il metodo sintetico in `Partita`.
3. Ridurre il controller a semplice delega con guardie.
4. Chiudere la tranche subito dopo il ripristino dei test mirati.

---

## Criteri di successo

Il piano e' considerato completato se:

- il riepilogo sintetico nasce in modo piu' esplicito da `Partita`
- `GameController` appare piu' chiaramente come facade e meno come interprete dello stato
- la TUI continua a ricevere lo stesso formato utile di informazione
- il perimetro resta piccolo e mirato solo al riepilogo dello stato