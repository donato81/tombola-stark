# TODO - Refactor confini Partita / GameController

**Branch**: `refactory-mappatura-tasti-game-play`  
**Tipo**: REFACTOR  
**Priorita'**: MEDIA  
**Stato**: READY

---

## Riferimento documentazione

Prima di iniziare l'implementazione consultare obbligatoriamente:

- `documentations/2 - project/DESIGN_refactor_confini_partita_gamecontroller.md`
- `documentations/3 - planning/PLAN_refactor_confini_partita_gamecontroller.md`

Questo file TODO e' il sommario operativo della tranche corrente.

---

## Workflow agente

Implementare le modifiche in modo incrementale su 3 commit atomici.

Workflow per ogni fase:

1. Leggere DESIGN e PLAN del task.
2. Implementare solo la fase corrente.
3. Eseguire i test rilevanti.
4. Aggiornare questo TODO.
5. Preparare il commit atomico della fase.

Regole fondamentali:

- un commit per fase logica
- nessun ampliamento di scope oltre il confine Partita / GameController
- non toccare TUI salvo impatto minimo strettamente necessario
- proteggere il contratto pubblico del controller verso la UI

---

## Checklist implementazione

### FASE 1 - Test di protezione del confine

Commit: `test(controller): add boundary regression coverage for Partita and GameController [Phase 1/3]`

- [ ] leggere `PLAN_refactor_confini_partita_gamecontroller.md`
- [ ] identificare i contratti minimi tra `Partita.esegui_turno()` e `GameController.esegui_turno_sicuro()`
- [ ] aggiungere o aggiornare test in `tests/test_game_controller.py`
- [ ] aggiungere o aggiornare test in `tests/test_partita.py` solo se necessario al contratto
- [ ] verificare che i dati chiave del turno non vengano alterati dal controller
- [ ] eseguire i test mirati della fase

### FASE 2 - Refactor minimo del controller

Commit: `refactor(controller): reduce duplicated game-state handling [Phase 2/3]`

- [ ] rileggere il piano prima della codifica
- [ ] individuare un punto piccolo e reale di duplicazione tra dominio e controller
- [ ] ridurre la duplicazione senza cambiare l'API pubblica verso TUI
- [ ] mantenere logging e orchestration nel controller
- [ ] evitare di spostare nuova logica di UI nel dominio
- [ ] eseguire i test mirati della fase

### FASE 3 - Chiusura tranche

Commit: `docs(tests): align boundary refactor notes and finalize coverage [Phase 3/3]`

- [ ] rieseguire i test del refactor
- [ ] aggiornare questo TODO spuntando le fasi completate
- [ ] annotare eventuali limiti rimasti per una tranche successiva
- [ ] preparare i file per il commit finale della tranche

---

## Definizione di done

- [ ] `Partita` resta owner chiaro del game state
- [ ] `GameController` resta facade applicativa senza duplicare decisioni di dominio chiave
- [ ] TUI non richiede modifiche architetturali per continuare a funzionare
- [ ] i test del confine sono verdi
- [ ] la tranche e' chiusa senza allargare il refactor oltre il necessario
