type: plan
status: READY
feature: refactor-validazioni-bordo-ottieni-stato-sintetico-gamecontroller
agent: Agent-Plan
date: 2026-03-24
---

# Piano di Implementazione - Refactor validazioni di bordo in ottieni_stato_sintetico

---

## Executive Summary

Tipo: REFACTOR  
Priorita': MEDIA  
Stato: READY  
Branch: `refactory-mappatura-tasti-game-play`  
Versione target: refactor interno branch corrente  
Data creazione: 2026-03-24  
Autore: GitHub Copilot + donato81  
Effort stimato: 2-4 ore  
Commit previsti: 3 commit atomici

---

## Problema / Obiettivo

La mini-tranche precedente ha spostato la costruzione dello stato sintetico dentro `Partita`, lasciando `GameController.ottieni_stato_sintetico()` come bordo applicativo con guardie e validazioni difensive.

Resta pero' un punto ancora affinabile: una parte delle validazioni strutturali nel controller potrebbe essere ridondante rispetto al contratto ormai espresso dal dominio e protetto dai test.

L'obiettivo di questa nuova tranche e' capire quali controlli devono davvero restare nel controller e ridurre quelli superflui, mantenendo invariati:

- firma pubblica del metodo;
- struttura del dizionario restituito;
- contratto verso TUI e helper esistenti;
- comportamento osservabile in caso di input non valido.

---

## Decisioni di Design gia' approvate e riusate

Questa mini-tranche eredita le decisioni del refactor precedente:

1. `Partita` resta owner dello stato di gioco e della semantica del riepilogo.
2. `GameController` resta facade applicativa verso TUI e helper UI.
3. Nessuna modifica architetturale alla TUI.
4. Nessuna nuova factory, service o DTO aggiuntivo.
5. Nessun ampliamento verso loop partita, logging strutturale o creazione partita.

---

## Soluzione proposta

Il refactor viene suddiviso in tre passi minimi:

1. Bloccare con test il comportamento che deve restare al controller come bordo pubblico.
2. Ridurre in `ottieni_stato_sintetico()` le validazioni ridondanti rispetto al contratto gia' garantito da `Partita`.
3. Rieseguire i test mirati e chiudere la tranche con aggiornamento minimo della documentazione operativa.

Il principio guida e' semplice: il controller puo' ancora validare il parametro d'ingresso e difendere il proprio bordo pubblico, ma non deve duplicare inutilmente la semantica di uno snapshot che il dominio sa gia' costruire.

---

## File coinvolti

### Codice

- `bingo_game/game_controller.py`

### Test

- `tests/test_game_controller.py`

### Documentazione workflow

- `documentations/3 - planning/PLAN_refactor_validazioni_bordo_ottieni_stato_sintetico_gamecontroller.md`
- `documentations/4 - todo file/TODO_refactor_validazioni_bordo_ottieni_stato_sintetico_gamecontroller.md`

---

## Rischi e strategia di contenimento

### Rischi

- rimuovere una validazione ancora necessaria al bordo pubblico del controller;
- indebolire in modo involontario il contratto osservato dalla TUI;
- introdurre test troppo dipendenti dall'implementazione interna anziche' dal comportamento pubblico;
- ampliare il refactor oltre `ottieni_stato_sintetico()`.

### Contenimento

- partire da test di caratterizzazione sul comportamento osservabile del metodo;
- non cambiare chiavi, tipi attesi o messaggi di errore pubblicamente rilevanti senza test;
- limitare il diff al solo metodo target e ai test direttamente collegati;
- lasciare fuori da questa tranche `Partita`, TUI e altri metodi del controller.

---

## Piano di implementazione

### FASE 1 - Test di caratterizzazione del bordo controller

Commit previsto: `test(controller): characterize border validations for synthetic state [Phase 1/3]`

Obiettivo:

- distinguere con test cio' che e' ancora responsabilita' del controller da cio' che e' ormai garantito da `Partita`

Task:

- rileggere il comportamento pubblico attuale di `ottieni_stato_sintetico()`;
- aggiungere o aggiornare test in `tests/test_game_controller.py` sui casi che devono restare coperti dal controller;
- separare, nei test, gli input non validi esterni dalle incoerenze interne ormai non attese dal dominio;
- verificare che il contratto osservabile dalla TUI resti espresso chiaramente nei test.

Exit criteria:

- test verdi che documentano il bordo pubblico desiderato;
- perimetro delle validazioni ancora necessarie reso esplicito.

---

### FASE 2 - Riduzione delle validazioni ridondanti nel controller

Commit previsto: `refactor(controller): trim redundant synthetic-state border checks [Phase 2/3]`

Obiettivo:

- alleggerire `ottieni_stato_sintetico()` senza cambiare il contratto pubblico verso la TUI

Task:

- rimuovere o ridurre solo le validazioni che duplicano controlli gia' stabilizzati nel dominio;
- mantenere nel controller la guardia sul parametro e la responsabilita' di fallimento coerente verso il bordo applicativo;
- evitare qualunque modifica alla struttura del dizionario restituito;
- mantenere logging e orchestration di bordo solo dove ancora sensati.

Exit criteria:

- `ottieni_stato_sintetico()` piu' lineare e leggibile;
- nessuna regressione sui test della fase 1;
- nessuna modifica a TUI, `Partita` o altri punti del controller.

---

### FASE 3 - Chiusura mini-tranche

Commit previsto: `docs(tests): finalize border-validation reduction on synthetic state [Phase 3/3]`

Obiettivo:

- chiudere la tranche senza estenderne il perimetro

Task:

- rieseguire i test mirati del confine;
- aggiornare il TODO della mini-tranche;
- annotare eventuali validazioni residue ancora giustificate nel controller;
- allineare `CHANGELOG.md` solo se la tranche viene implementata davvero.

Exit criteria:

- test mirati verdi;
- TODO aggiornato;
- motivazione chiara dei controlli rimasti nel controller.

---

## Sequenza consigliata

1. Bloccare prima il comportamento che deve restare pubblico nel controller.
2. Ridurre solo i controlli veramente ridondanti.
3. Rieseguire subito i test mirati.
4. Chiudere la tranche senza ampliare il refactor ad altri metodi.

---

## Criteri di successo

Il piano e' considerato completato se:

- il controller mantiene solo le validazioni davvero necessarie al proprio bordo pubblico;
- il dominio continua a essere la fonte dello snapshot sintetico;
- la TUI continua a ricevere lo stesso formato utile di informazione;
- il refactor resta piccolo, testabile e confinato a `ottieni_stato_sintetico()`.