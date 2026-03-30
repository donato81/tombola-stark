---
type: plan
feature: test_eventi_partita
agent: Agent-Plan
status: READY
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_test_eventi_partita_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per i test unitari di eventi_partita.py
data_creazione: 2026-03-30
agente: Agent-Plan
stato: pronto
feature: test_eventi_partita
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_test_eventi_partita_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Executive Summary

Tipo intervento: creazione nuovo file di test unitario
Priorita': P1
Branch: main
Versione di riferimento: v1.0.0
Scope: implementare tests/unit/test_eventi_partita.py coprendo esclusivamente le quattro dataclass del Gruppo C in eventi_partita.py
Vincoli: uso obbligatorio di unittest; lettura preventiva di codici_errori.py per i codici validi di fallimento; nessuna modifica a file esistenti fuori da tests/unit/test_eventi_partita.py; nessun coinvolgimento dei Gruppi A, B, D o E

### Problema e Obiettivo

Il repository non possiede ancora una suite dedicata che congeli i factory methods e gli invarianti di business
delle dataclass definite in eventi_partita.py.

L'obiettivo operativo di questo piano e' creare un solo file di test,
tests/unit/test_eventi_partita.py, che verifichi:

- ReclamoVittoria
- EventoReclamoVittoria
- EventoEsitoReclamoVittoria
- EventoFineTurno

Il file dovra' essere implementato esclusivamente con unittest e dovra' usare nei test di fallimento
un codice errore valido letto da bingo_game/events/codici_errori.py prima della scrittura del file.

### Approccio tecnico

L'implementazione dovra' rispettare una sequenza lineare e verificabile.

Prima si legge bingo_game/events/eventi_partita.py per fissare campi, factory methods, valori default,
parametri obbligatori e facoltativi delle quattro dataclass. Subito dopo si legge bingo_game/events/codici_errori.py
per ricavare i valori stringa validi da usare nei test di fallimento, ad esempio VERIFICA_FALLITA.
Solo a quel punto si crea tests/unit/test_eventi_partita.py con quattro classi di test ordinate per dataclass,
tutte basate su unittest.TestCase. Infine si verifica che il file passi, che non contenga import o fixture pytest
e che non siano stati toccati file esistenti fuori dal nuovo test target.

Il piano e' additivo: nessun file esistente in bingo_game/ o in altre aree di tests/ deve essere modificato.

### File coinvolti

- [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py) - READ
- [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) - READ
- tests/unit/test_eventi_partita.py - CREATE
- [docs/2 - projects/DESIGN_test_eventi_partita_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_partita_v1.0.0.md) - READ
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md) - READ

### Fasi sequenziali

#### Passo 1 - Lettura di eventi_partita.py

File coinvolti:

- [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py)

Operazione:

- READ

Contenuto atteso:

- inventario esatto dei campi di ReclamoVittoria, EventoReclamoVittoria, EventoEsitoReclamoVittoria, EventoFineTurno
- elenco dei factory methods disponibili
- conferma dei valori default, inclusi fase e campi opzionali
- conferma dei parametri obbligatori e facoltativi

Dipendenze:

- usa come vincolo il perimetro definito in [DESIGN_test_eventi_partita_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_partita_v1.0.0.md)
- usa come base analitica [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

#### Passo 2 - Lettura di codici_errori.py

File coinvolti:

- [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)

Operazione:

- READ

Contenuto atteso:

- identificazione dei valori stringa validi da usare come argomento errore nei test di fallimento
- selezione di un codice esplicito del dominio partita, ad esempio VERIFICA_FALLITA
- conferma che il valore scelto appartenga ai codici previsti dal modulo

Dipendenze:

- richiede completato il Passo 1

#### Passo 3 - Creazione di tests/unit/test_eventi_partita.py

File coinvolti:

- tests/unit/test_eventi_partita.py

Operazione:

- CREATE

Contenuto atteso:

- quattro classi di test nell'ordine: TestReclamoVittoria, TestEventoReclamoVittoria, TestEventoEsitoReclamoVittoria, TestEventoFineTurno
- uso esclusivo di unittest
- applicazione della strategia FrozenInstanceError oppure AttributeError per i test di immutabilita'
- copertura limitata agli scenari del Gruppo C

Dipendenze:

- richiede completati i Passi 1 e 2
- deve aderire al design in [DESIGN_test_eventi_partita_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_partita_v1.0.0.md)

#### Passo 4 - Verifica che tutti i test del file passino

File coinvolti:

- tests/unit/test_eventi_partita.py

Operazione:

- VERIFY

Comando atteso:

- python -m unittest tests.unit.test_eventi_partita -q

Esito atteso:

- il nuovo file di test viene raccolto correttamente
- tutti i test del Gruppo C passano
- non emergono failure direttamente imputabili al file appena creato

Dipendenze:

- richiede completato il Passo 3

#### Passo 5 - Verifica assenza di pytest nel file

File coinvolti:

- tests/unit/test_eventi_partita.py

Operazione:

- VERIFY

Esito atteso:

- il file non contiene import di pytest
- il file non contiene fixture pytest
- il file usa esclusivamente unittest come libreria di test

Dipendenze:

- richiede completato il Passo 3

#### Passo 6 - Chiusura senza modifiche fuori scope

File coinvolti:

- tests/unit/test_eventi_partita.py
- nessun altro file di codice o test esistente

Operazione:

- VERIFY

Esito atteso:

- nessuna modifica a file esistenti fuori da tests/unit/test_eventi_partita.py
- nessun file in bingo_game/ toccato
- nessun test dei Gruppi A, B, D o E introdotto nel file nuovo

Dipendenze:

- richiede completati i Passi 4 e 5

### Dipendenze

- [docs/2 - projects/DESIGN_test_eventi_partita_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_partita_v1.0.0.md)
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- standard test del repository in .github/instructions/tests.instructions.md

### Rischi

- introdurre pytest come libreria di test, violando un vincolo esplicito del task
- usare un codice errore non presente in codici_errori.py e rendere il test negativo incoerente con il dominio
- omettere i parametri opzionali di EventoEsitoReclamoVittoria e lasciare scoperto il factory method piu' ricco
- confondere i casi tombola con i casi di riga e perdere un invariante di business essenziale
- modificare accidentalmente file esistenti in tests/ per riuso o refactor non richiesti

### Project padre

- [docs/2 - projects/DESIGN_test_eventi_partita_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_partita_v1.0.0.md)

### Criteri di completamento

- bingo_game/events/eventi_partita.py e' stato letto prima della scrittura del test
- bingo_game/events/codici_errori.py e' stato letto prima della scrittura del test di fallimento
- tests/unit/test_eventi_partita.py esiste come unico nuovo file di test del task
- le classi nel file sono nell'ordine definito dal task
- python -m unittest tests.unit.test_eventi_partita -q e' stato eseguito come verifica finale del passo implementativo
- il file non contiene import pytest
- il file non contiene fixture pytest
- nessun file esistente fuori da tests/unit/test_eventi_partita.py e' stato modificato

## Stato Avanzamento

- [x] Definito
- [x] In implementazione
- [x] Test superati
- [x] Chiuso