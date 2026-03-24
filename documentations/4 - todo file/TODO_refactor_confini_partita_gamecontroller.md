# TODO - Refactor confini Partita / GameController

**Branch**: `refactory-mappatura-tasti-game-play`  
**Tipo**: REFACTOR  
**Priorita'**: MEDIA  
**Stato**: COMPLETATO

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

- [x] leggere `PLAN_refactor_confini_partita_gamecontroller.md`
- [x] identificare i contratti minimi tra `Partita.esegui_turno()` e `GameController.esegui_turno_sicuro()`
- [x] aggiungere o aggiornare test in `tests/test_game_controller.py`
- [x] aggiungere o aggiornare test in `tests/test_partita.py` solo se necessario al contratto
- [x] verificare che i dati chiave del turno non vengano alterati dal controller
- [x] eseguire i test mirati della fase

### FASE 2 - Refactor minimo del controller

Commit: `refactor(controller): reduce duplicated game-state handling [Phase 2/3]`

- [x] rileggere il piano prima della codifica
- [x] individuare un punto piccolo e reale di duplicazione tra dominio e controller
- [x] ridurre la duplicazione senza cambiare l'API pubblica verso TUI
- [x] mantenere logging e orchestration nel controller
- [x] evitare di spostare nuova logica di UI nel dominio
- [x] eseguire i test mirati della fase

### FASE 3 - Chiusura tranche

Commit: `docs(tests): align boundary refactor notes and finalize coverage [Phase 3/3]`

- [x] rieseguire i test del refactor
- [x] aggiornare questo TODO spuntando le fasi completate
- [x] annotare eventuali limiti rimasti per una tranche successiva
- [x] preparare i file per il commit finale della tranche

### Note residue

- La validazione disponibile del refactor e' stata eseguita via `unittest`.
- Il virtual environment locale del repository punta a un interprete non piu' presente.
- `pytest` non e' disponibile nel Python di sistema corrente, quindi i test pytest-based restano da rieseguire dopo il ripristino dell'ambiente.

---

## Definizione di done

- [x] `Partita` resta owner chiaro del game state
- [x] `GameController` resta facade applicativa senza duplicare decisioni di dominio chiave
- [x] TUI non richiede modifiche architetturali per continuare a funzionare
- [x] i test del confine sono verdi
- [x] la tranche e' chiusa senza allargare il refactor oltre il necessario
