# TODO - Refactor validazioni di bordo in ottieni_stato_sintetico

**Branch**: `refactory-mappatura-tasti-game-play`  
**Tipo**: REFACTOR  
**Priorita'**: MEDIA  
**Stato**: COMPLETATO

---

## Riferimento documentazione

Prima di iniziare l'implementazione consultare obbligatoriamente:

- `documentations/3 - planning/PLAN_refactor_validazioni_bordo_ottieni_stato_sintetico_gamecontroller.md`
- `documentations/2 - project/DESIGN_refactor_confini_partita_gamecontroller.md`
- `documentations/4 - todo file/TODO_refactor_riepilogo_sintetico_partita_gamecontroller.md` come contesto di continuita'

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
- nessun ampliamento di scope oltre il bordo di `ottieni_stato_sintetico()`
- non toccare TUI, `Partita` o altri metodi del controller salvo impatto minimo strettamente necessario
- non cambiare il contratto pubblico di `ottieni_stato_sintetico()`

---

## Checklist implementazione

### FASE 1 - Test di caratterizzazione del bordo

Commit: `test(controller): characterize border validations for synthetic state [Phase 1/3]`

- [x] leggere `PLAN_refactor_validazioni_bordo_ottieni_stato_sintetico_gamecontroller.md`
- [x] individuare quali validazioni devono restare responsabilita' del controller
- [x] aggiungere o aggiornare test in `tests/test_game_controller.py`
- [x] distinguere nei test input esterni invalidi da incoerenze interne non piu' attese
- [x] verificare che il contratto osservato dalla TUI resti stabile
- [x] eseguire i test mirati della fase

### FASE 2 - Riduzione delle validazioni ridondanti

Commit: `refactor(controller): trim redundant synthetic-state border checks [Phase 2/3]`

- [x] rileggere il piano prima della codifica
- [x] ridurre solo le validazioni ridondanti in `ottieni_stato_sintetico()`
- [x] mantenere la guardia sul parametro e il comportamento pubblico del bordo
- [x] evitare modifiche alla struttura del dizionario restituito
- [x] mantenere il refactor confinato al solo metodo target
- [x] eseguire i test mirati della fase

### FASE 3 - Chiusura mini-tranche

Commit: `docs(tests): finalize border-validation reduction on synthetic state [Phase 3/3]`

- [x] rieseguire i test del refactor
- [x] aggiornare questo TODO spuntando le fasi completate
- [x] annotare eventuali validazioni residue ancora giustificate
- [x] preparare i file per il commit finale della mini-tranche

### Note residue

- La tranche precedente ha gia' spostato la costruzione dello stato sintetico in `Partita`.
- Questa mini-tranche deve chiarire il confine del controller, non ridefinire il contratto del dominio.
- Se emerge che una validazione apparentemente ridondante e' invece osservata dalla TUI, va mantenuta e annotata.
- Esito Fase 1: restano chiaramente responsabilita' del controller la guardia sul parametro esterno e la traduzione di eccezioni interne di `Partita`; le altre difese strutturali sono ora fotografate come comportamento corrente da valutare nella Fase 2.
- Esito Fase 2: il controller conserva i controlli minimi di bordo su parametro, eccezioni interne, tipo dizionario e chiavi obbligatorie; non reinterpreta piu' invece il significato semantico di `stato_partita` ne' i tipi interni di `numeri_estratti` e `giocatori` quando lo snapshot di `Partita` e' gia' strutturalmente presente.
- Esito Fase 3: la tranche si chiude mantenendo nel controller solo il nucleo di validazione di bordo davvero necessario; le eventuali ulteriori riduzioni future dovranno essere giustificate da nuovi test o da un cambio esplicito del contratto verso la TUI.

---

## Definizione di done

- [x] `ottieni_stato_sintetico()` mantiene solo le validazioni davvero necessarie al bordo pubblico
- [x] il contratto verso TUI e helper resta invariato
- [x] il dominio continua a restare la fonte dello snapshot sintetico
- [x] i test del confine sono verdi
- [x] la mini-tranche resta piccola e confinata al metodo target