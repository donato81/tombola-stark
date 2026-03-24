# TODO - Refactor riepilogo sintetico Partita / GameController

**Branch**: `refactory-mappatura-tasti-game-play`  
**Tipo**: REFACTOR  
**Priorita'**: MEDIA  
**Stato**: IN CORSO

---

## Riferimento documentazione

Prima di iniziare l'implementazione consultare obbligatoriamente:

- `documentations/3 - planning/PLAN_refactor_riepilogo_sintetico_partita_gamecontroller.md`
- `documentations/2 - project/DESIGN_refactor_confini_partita_gamecontroller.md` come contesto di continuita'

Questo file TODO e' il sommario operativo della nuova mini-tranche.

---

## Workflow agente

Implementare le modifiche in modo incrementale su 3 commit atomici.

Workflow per ogni fase:

1. Leggere PLAN e contesto del refactor precedente.
2. Implementare solo la fase corrente.
3. Eseguire i test rilevanti.
4. Aggiornare questo TODO.
5. Preparare il commit atomico della fase.

Regole fondamentali:

- un commit per fase logica
- nessun ampliamento di scope oltre il riepilogo sintetico dello stato
- non toccare TUI salvo impatto minimo strettamente necessario
- non cambiare il contratto pubblico di `ottieni_stato_sintetico()`

---

## Checklist implementazione

### FASE 1 - Test di protezione del riepilogo sintetico

Commit: `test(controller): lock synthetic-state delegation toward Partita [Phase 1/3]`

- [x] leggere `PLAN_refactor_riepilogo_sintetico_partita_gamecontroller.md`
- [x] individuare il contratto pubblico di `ottieni_stato_sintetico()`
- [x] aggiungere o aggiornare test in `tests/test_game_controller.py`
- [x] valutare `tests/test_partita.py`: nessun aggiornamento necessario in questa fase
- [x] verificare che il formato atteso dalla TUI resti stabile
- [x] eseguire i test mirati della fase

### FASE 2 - Delega del riepilogo sintetico a Partita

Commit: `refactor(controller): delegate synthetic state summary to Partita [Phase 2/3]`

- [x] rileggere il piano prima della codifica
- [x] introdurre in `Partita` un metodo pubblico per il riepilogo sintetico
- [x] ridurre `ottieni_stato_sintetico()` a guardia e delega
- [x] mantenere logging e orchestration nel controller
- [x] evitare di ridefinire nel controller il significato dello stato di gioco
- [x] eseguire i test mirati della fase

### FASE 3 - Chiusura mini-tranche

Commit: `docs(tests): finalize synthetic-state boundary refactor [Phase 3/3]`

- [x] rieseguire i test del refactor
- [x] aggiornare questo TODO spuntando le fasi completate
- [x] annotare eventuali limiti rimasti per una tranche successiva
- [x] preparare i file per il commit finale della mini-tranche

### Note residue

- La tranche precedente ha gia' spostato il conteggio premi duplicato fuori dal controller.
- Questa mini-tranche non deve introdurre cambiamenti a TUI, loop di gioco o logging strutturale.
- L'ambiente locale potrebbe richiedere ancora `unittest` al posto di `pytest` finche' il venv non viene ripristinato.
- Limite residuo: `GameController.ottieni_stato_sintetico()` mantiene ancora validazioni difensive di bordo; una tranche futura potra' valutare se ridurle ulteriormente senza indebolire il contratto verso la TUI.

---

## Definizione di done

- [x] `Partita` espone un riepilogo sintetico proprio
- [x] `GameController` inoltra il riepilogo senza ricostruirlo
- [x] TUI e helper continuano a ricevere la stessa struttura utile
- [x] i test del confine sono verdi
- [x] la mini-tranche resta piccola e non amplia il refactor ad altre aree