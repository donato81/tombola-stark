---
type: plan
feature: test_eventi_ui
agent: Agent-Plan
status: DRAFT
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_test_eventi_ui_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per i test unitari di eventi_ui.py
data_creazione: 2026-03-30
agente: Agent-Plan
stato: bozza
feature: test_eventi_ui
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_test_eventi_ui_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Executive Summary

Tipo intervento: creazione nuovo file di test unitario
Priorita': P1
Branch: main
Versione di riferimento: v1.0.0
Scope: implementare [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)
coprendo esclusivamente le due dataclass del Gruppo B in `eventi_ui.py`
Vincoli: uso obbligatorio di unittest; nessuna modifica a file esistenti fuori da [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py);
nessun coinvolgimento dei Gruppi A, C, D o E

### Problema e Obiettivo

Il repository non possiede ancora una suite dedicata che congeli il contratto delle due dataclass
di focus definite in `eventi_ui.py`, pur essendo esse usate in molti punti della logica di focus.

L'obiettivo operativo di questo piano e' creare un solo file di test,
[tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py),
che verifichi costruzione, default e immutabilita' di:

- `EventoFocusAutoImpostato`
- `EventoFocusCartellaImpostato`

Il file dovra' essere implementato esclusivamente con unittest.

### Approccio tecnico

L'implementazione dovra' rispettare una sequenza lineare e verificabile.

Prima si legge il modulo [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py)
per fissare campi, tipi e valori default reali delle due dataclass.
Poi si crea il file di test con due classi ordinate per dataclass, entrambe basate su `unittest.TestCase`.
Infine si verifica che il file passi, che non contenga import di pytest e che non siano stati toccati
file esistenti fuori dal nuovo test target.

Il piano e' additivo: nessun file esistente in [bingo_game/](../../bingo_game/) o in altre aree di
[tests/](../../tests/) deve essere modificato.

### File coinvolti

- [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py) - READ
- [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py) - CREATE
- [docs/2 - projects/DESIGN_test_eventi_ui_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_ui_v1.0.0.md) - READ
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md) - READ

### Fasi sequenziali

#### Passo 1 - Lettura di eventi_ui.py

File coinvolti:

- [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py)

Operazione:

- READ

Contenuto atteso:

- inventario esatto dei campi di `EventoFocusAutoImpostato`
- inventario esatto dei campi di `EventoFocusCartellaImpostato`
- conferma del default `reset_riga_colonna=False`
- conferma dei tipi dichiarati e dell'uso di `frozen=True`

Dipendenze:

- usa come vincolo il perimetro definito in [DESIGN_test_eventi_ui_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_ui_v1.0.0.md)
- usa come base analitica [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

#### Passo 2 - Creazione di tests/unit/test_eventi_ui.py

File coinvolti:

- [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)

Operazione:

- CREATE

Contenuto atteso:

- due classi di test nell'ordine:
  `TestEventoFocusAutoImpostato`, `TestEventoFocusCartellaImpostato`
- uso esclusivo di unittest
- asserzioni limitate a costruzione, valori default, tipi accettati e immutabilita'

Dipendenze:

- richiede completato il Passo 1
- deve aderire al design in [DESIGN_test_eventi_ui_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_ui_v1.0.0.md)

#### Passo 3 - Verifica che tutti i test del file passino

File coinvolti:

- [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)

Operazione:

- VERIFY

Comando atteso:

- `python -m unittest tests.unit.test_eventi_ui -q`

Esito atteso:

- il nuovo file di test viene raccolto correttamente
- tutti i test del Gruppo B passano
- non emergono failure direttamente imputabili al file appena creato

Dipendenze:

- richiede completato il Passo 2

#### Passo 4 - Verifica assenza di pytest nel file

File coinvolti:

- [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)

Operazione:

- VERIFY

Esito atteso:

- il file non contiene `import pytest`
- il file non contiene fixture o costrutti pytest-specifici
- il file usa esclusivamente unittest come libreria di test

Dipendenze:

- richiede completato il Passo 2

#### Passo 5 - Chiusura senza modifiche fuori scope

File coinvolti:

- [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)
- nessun altro file di codice o test esistente

Operazione:

- VERIFY

Esito atteso:

- nessuna modifica a file esistenti fuori da [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py)
- nessun file in [bingo_game/](../../bingo_game/) toccato
- nessun test dei Gruppi A, C, D o E introdotto nel file nuovo

Dipendenze:

- richiede completati i Passi 3 e 4

### Dipendenze

- [docs/2 - projects/DESIGN_test_eventi_ui_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_ui_v1.0.0.md)
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- standard test del repository in `.github/instructions/tests.instructions.md`

### Rischi

- introdurre pytest come libreria di test, violando un vincolo esplicito del task
- omettere il controllo di immutabilita' e lasciare scoperto il comportamento `frozen=True`
- leggere i campi in modo incompleto e perdere il default `reset_riga_colonna=False`
- modificare accidentalmente file esistenti in [tests/](../../tests/) per riuso o refactor non richiesti
- includere scenari di gruppi successivi e trasformare un task semplice in una suite fuori perimetro

### Project padre

- [docs/2 - projects/DESIGN_test_eventi_ui_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_ui_v1.0.0.md)

### Criteri di completamento

- [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py) e' stato letto prima della scrittura del test
- [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py) esiste come unico nuovo file di test del task
- le classi nel file sono nell'ordine definito dal task
- `python -m unittest tests.unit.test_eventi_ui -q` e' stato eseguito come verifica finale del passo implementativo
- il file non contiene `import pytest`
- nessun file esistente fuori da [tests/unit/test_eventi_ui.py](../../tests/unit/test_eventi_ui.py) e' stato modificato

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso