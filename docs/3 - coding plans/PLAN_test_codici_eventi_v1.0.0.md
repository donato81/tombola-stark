---
type: plan
feature: test_codici_eventi
agent: Agent-Plan
status: READY
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_test_codici_eventi_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per test di contratto sui moduli codici_*.py
data_creazione: 2026-03-30
agente: Agent-Plan
stato: pronto
feature: test_codici_eventi
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_test_codici_eventi_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Executive Summary

Tipo intervento: creazione nuovo file di test unitario
Priorita': P1
Branch: main
Versione di riferimento: v1.0.0
Scope: implementare [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)
coprendo esclusivamente i sette moduli codici_*.py del Gruppo A
Vincoli: nessuna modifica a file esistenti fuori da [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py);
nessun coinvolgimento dei Gruppi B, C, D o E

### Problema e Obiettivo

Il repository non possiede ancora una suite dedicata che congeli il contratto nominale
dei moduli codici_*.py usati come chiavi da eventi, renderer e cataloghi.

L'obiettivo operativo di questo piano e' creare un solo file di test,
[tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py),
che verifichi importabilita', valori stringa esatti e coerenza con Literal dei sette moduli:

- [bingo_game/events/codici_configurazione.py](../../bingo_game/events/codici_configurazione.py)
- [bingo_game/events/codici_controller.py](../../bingo_game/events/codici_controller.py)
- [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)
- [bingo_game/events/codici_eventi.py](../../bingo_game/events/codici_eventi.py)
- [bingo_game/events/codici_loop.py](../../bingo_game/events/codici_loop.py)
- [bingo_game/events/codici_messaggi_sistema.py](../../bingo_game/events/codici_messaggi_sistema.py)
- [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py)

### Approccio tecnico

L'implementazione dovra' rispettare una sequenza lineare e verificabile.

Prima si rileggono i sette moduli target per fissare l'insieme esatto delle costanti e dei Literal.
Poi si crea il nuovo file di test con sette classi ordinate per modulo, una per ciascun file del Gruppo A.
Infine si esegue la suite unitaria con `python -m unittest tests.unit.test_codici_eventi -q` per validare che il nuovo file passi senza
introdurre regressioni, lasciando invariato tutto il resto del repository.

Il piano e' additivo: nessun file esistente in [bingo_game/](../../bingo_game/) o in altre aree di
[tests/](../../tests/) deve essere modificato.

### File coinvolti

- [bingo_game/events/codici_configurazione.py](../../bingo_game/events/codici_configurazione.py) - READ
- [bingo_game/events/codici_controller.py](../../bingo_game/events/codici_controller.py) - READ
- [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) - READ
- [bingo_game/events/codici_eventi.py](../../bingo_game/events/codici_eventi.py) - READ
- [bingo_game/events/codici_loop.py](../../bingo_game/events/codici_loop.py) - READ
- [bingo_game/events/codici_messaggi_sistema.py](../../bingo_game/events/codici_messaggi_sistema.py) - READ
- [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py) - READ
- [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py) - CREATE
- [docs/2 - projects/DESIGN_test_codici_eventi_v1.0.0.md](../2%20-%20projects/DESIGN_test_codici_eventi_v1.0.0.md) - READ
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md) - READ

### Fasi sequenziali

#### Passo 1 - Rilettura dei sette moduli codici_*.py

File coinvolti:

- [bingo_game/events/codici_configurazione.py](../../bingo_game/events/codici_configurazione.py)
- [bingo_game/events/codici_controller.py](../../bingo_game/events/codici_controller.py)
- [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)
- [bingo_game/events/codici_eventi.py](../../bingo_game/events/codici_eventi.py)
- [bingo_game/events/codici_loop.py](../../bingo_game/events/codici_loop.py)
- [bingo_game/events/codici_messaggi_sistema.py](../../bingo_game/events/codici_messaggi_sistema.py)
- [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py)

Operazione:

- READ

Contenuto atteso:

- inventario esatto delle costanti stringa per ogni modulo
- estrazione dei valori ammessi dai Literal
- conferma del mapping atteso per il caso speciale di [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)

Dipendenze:

- usa come vincolo il perimetro definito in [DESIGN_test_codici_eventi_v1.0.0.md](../2%20-%20projects/DESIGN_test_codici_eventi_v1.0.0.md)
- usa come base analitica [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

#### Passo 2 - Creazione di tests/unit/test_codici_eventi.py

File coinvolti:

- [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)

Operazione:

- CREATE

Contenuto atteso:

- una classe di test per modulo, nell'ordine:
  codici_configurazione, codici_controller, codici_errori, codici_eventi,
  codici_loop, codici_messaggi_sistema, codici_output_ui_umani
- marcatore unit coerente con gli standard del repository
- asserzioni di contratto limitate a importabilita', costanti attese e Literal

Dipendenze:

- richiede completato il Passo 1
- deve aderire al design in [DESIGN_test_codici_eventi_v1.0.0.md](../2%20-%20projects/DESIGN_test_codici_eventi_v1.0.0.md)

#### Passo 3 - Verifica suite con `unittest`

File coinvolti:

- [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)

Operazione:

- VERIFY

Comando atteso:

- `python -m unittest tests.unit.test_codici_eventi -q`

Esito atteso:

- il nuovo file di test viene raccolto correttamente
- i test del Gruppo A passano
- non emergono failure direttamente imputabili al file appena creato

Dipendenze:

- richiede completato il Passo 2

#### Passo 4 - Chiusura senza modifiche fuori scope

File coinvolti:

- [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)
- nessun altro file di codice o test esistente

Operazione:

- VERIFY

Esito atteso:

- nessuna modifica a file esistenti fuori da [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)
- nessun file in [bingo_game/](../../bingo_game/) toccato
- nessun test dei Gruppi B, C, D o E introdotto nel file nuovo

Dipendenze:

- richiede completato il Passo 3

### Dipendenze

- [docs/2 - projects/DESIGN_test_codici_eventi_v1.0.0.md](../2%20-%20projects/DESIGN_test_codici_eventi_v1.0.0.md)
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- standard test del repository in `.github/instructions/tests.instructions.md`

### Rischi

- creare un file che includa scenari oltre il Gruppo A, aumentando scope e tempo di review
- usare un ordine di classi diverso da quello stabilito dal report, riducendo tracciabilita'
- confrontare i Literal in modo incompleto e lasciare fuori chiavi o duplicati
- modificare accidentalmente file esistenti in [tests/](../../tests/) per riuso o refactor non richiesti
- eseguire `python -m unittest tests.unit.test_codici_eventi -q` senza aver prima congelato i set attesi, rendendo i failure meno leggibili

### Project padre

- [docs/2 - projects/DESIGN_test_codici_eventi_v1.0.0.md](../2%20-%20projects/DESIGN_test_codici_eventi_v1.0.0.md)

### Criteri di completamento

- i sette moduli target sono stati riletti e mappati prima della scrittura del test
- [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py) esiste come unico nuovo file di test del task
- le classi nel file sono nell'ordine definito dal report Gruppo A
- `python -m unittest tests.unit.test_codici_eventi -q` e' stato eseguito come verifica finale del passo implementativo
- nessun file esistente fuori da [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py) e' stato modificato

## Stato Avanzamento

- [x] Definito
- [x] In implementazione
- [x] Test superati
- [x] Chiuso