---
type: plan
feature: test_esito_azione
agent: Agent-Plan
status: READY
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_test_esito_azione_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per i test unitari di EsitoAzione
data_creazione: 2026-03-30
agente: Agent-Plan
stato: pronto
feature: test_esito_azione
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_test_esito_azione_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Executive Summary

Tipo intervento: creazione nuovo file di test unitario
Priorita': P1
Branch: main
Versione di riferimento: v1.0.0
Scope: implementare tests/unit/test_esito_azione.py coprendo esclusivamente EsitoAzione nel perimetro Gruppo D
Vincoli: uso obbligatorio di unittest; lettura preventiva di eventi.py, eventi_output_ui_umani.py, codici_errori.py e codici_output_ui_umani.py; nessuna modifica a file esistenti fuori da tests/unit/test_esito_azione.py; nessun coinvolgimento dei Gruppi A, B, C o E

### Problema e Obiettivo

Il repository non possiede ancora una suite dedicata che congeli il comportamento di EsitoAzione,
in particolare la logica di rendering di fallback di __str__, il comportamento speciale di __eq__ con stringhe
e il containment testuale di __contains__.

L'obiettivo operativo di questo piano e' creare un solo file di test,
tests/unit/test_esito_azione.py, che verifichi:

- factory methods successo() e fallimento()
- __str__ nel ramo fallimento
- __str__ nel ramo successo per gli eventi del perimetro Gruppo D
- __eq__ e __contains__

Il file dovra' essere implementato esclusivamente con unittest.

### Approccio tecnico

L'implementazione dovra' rispettare una sequenza lineare e verificabile.

Prima si legge integralmente bingo_game/events/eventi.py per ricavare firme, rami reali di __str__,
comportamento di __eq__ e __contains__. Poi si leggono i moduli di supporto per conoscere i campi esatti
degli eventi usati nei rami successo e i codici usati dai fallimenti. Solo dopo queste letture si crea
tests/unit/test_esito_azione.py con quattro classi di test ordinate per responsabilita', tutte basate su unittest.TestCase.
Infine si verifica che il file passi, che non contenga import o fixture pytest e che non siano stati toccati
file esistenti fuori dal nuovo test target.

Il piano e' additivo: nessun file esistente in bingo_game/ o in altre aree di tests/ deve essere modificato.

### File coinvolti

- [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py) - READ
- [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) - READ
- [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) - READ
- [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py) - READ
- tests/unit/test_esito_azione.py - CREATE
- [docs/2 - projects/DESIGN_test_esito_azione_v1.0.0.md](../2%20-%20projects/DESIGN_test_esito_azione_v1.0.0.md) - READ
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md) - READ

### Fasi sequenziali

#### Passo 1 - Lettura integrale di eventi.py

File coinvolti:

- [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py)

Operazione:

- READ

Contenuto atteso:

- firma esatta di successo()
- firma esatta di fallimento()
- logica completa di __str__
- logica completa di __eq__
- logica completa di __contains__
- elenco dei tipi concreti riconosciuti da isinstance nei rami di __str__

Dipendenze:

- usa come vincolo il perimetro definito in [DESIGN_test_esito_azione_v1.0.0.md](../2%20-%20projects/DESIGN_test_esito_azione_v1.0.0.md)
- usa come base analitica [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

#### Passo 2 - Lettura di eventi_output_ui_umani.py

File coinvolti:

- [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)

Operazione:

- READ

Contenuto atteso:

- campi esatti di EventoSegnazioneNumero
- campi esatti di RisultatoRicercaNumeroInCartella
- campi esatti di EventoRicercaNumeroInCartelle
- conferma che i factory disponibili permettono la costruzione degli eventi richiesti senza mock

Dipendenze:

- richiede completato il Passo 1

#### Passo 3 - Lettura di codici_errori.py

File coinvolti:

- [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)

Operazione:

- READ

Contenuto atteso:

- identificazione dei valori stringa esatti dei codici usati nei test di fallimento
- conferma di CARTELLE_NESSUNA_ASSEGNATA, FOCUS_CARTELLA_NON_IMPOSTATO,
  NUMERO_NON_VALIDO, NUMERO_TIPO_NON_VALIDO, FOCUS_CARTELLA_FUORI_RANGE, ERRORE_INTERNO

Dipendenze:

- richiede completato il Passo 1

#### Passo 4 - Lettura di codici_output_ui_umani.py

File coinvolti:

- [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py)

Operazione:

- READ

Contenuto atteso:

- identificazione delle chiavi stringa coerenti con i rami di segnazione e ricerca usati da __str__
- conferma che i testi attesi dei test derivano dal codice di __str__, mentre il modulo dei codici output
  fornisce il contesto semantico dei messaggi umani

Dipendenze:

- richiede completato il Passo 1

#### Passo 5 - Creazione di tests/unit/test_esito_azione.py

File coinvolti:

- tests/unit/test_esito_azione.py

Operazione:

- CREATE

Contenuto atteso:

- quattro classi di test nell'ordine: TestEsitoAzioneCostruzione, TestEsitoAzioneStrFallimento,
  TestEsitoAzioneStrSuccesso, TestEsitoAzioneEqContains
- uso esclusivo di unittest
- copertura limitata agli scenari del Gruppo D
- nessun mock per i rami focus, segnazione e ricerca del perimetro richiesto

Dipendenze:

- richiede completati i Passi 1, 2, 3 e 4
- deve aderire al design in [DESIGN_test_esito_azione_v1.0.0.md](../2%20-%20projects/DESIGN_test_esito_azione_v1.0.0.md)

#### Passo 6 - Verifica che tutti i test del file passino

File coinvolti:

- tests/unit/test_esito_azione.py

Operazione:

- VERIFY

Comando atteso:

- python -m unittest tests.unit.test_esito_azione -q

Esito atteso:

- il nuovo file di test viene raccolto correttamente
- tutti i test del Gruppo D passano
- non emergono failure direttamente imputabili al file appena creato

Dipendenze:

- richiede completato il Passo 5

#### Passo 7 - Verifica assenza di pytest nel file

File coinvolti:

- tests/unit/test_esito_azione.py

Operazione:

- VERIFY

Esito atteso:

- il file non contiene import di pytest
- il file non contiene fixture pytest
- il file usa esclusivamente unittest come libreria di test

Dipendenze:

- richiede completato il Passo 5

#### Passo 8 - Chiusura senza modifiche fuori scope

File coinvolti:

- tests/unit/test_esito_azione.py
- nessun altro file di codice o test esistente

Operazione:

- VERIFY

Esito atteso:

- nessuna modifica a file esistenti fuori da tests/unit/test_esito_azione.py
- nessun file in bingo_game/ toccato
- nessun test dei Gruppi A, B, C o E introdotto fuori dal perimetro richiesto

Dipendenze:

- richiede completati i Passi 6 e 7

### Dipendenze

- [docs/2 - projects/DESIGN_test_esito_azione_v1.0.0.md](../2%20-%20projects/DESIGN_test_esito_azione_v1.0.0.md)
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- standard test del repository in .github/instructions/tests.instructions.md

### Rischi

- introdurre pytest come libreria di test, violando un vincolo esplicito del task
- fissare testi attesi diversi da quelli realmente presenti in __str__
- descrivere in modo scorretto il comportamento di __eq__, sia nei casi stringa sia nei confronti tra istanze
- includere i rami legacy di visualizzazione e navigazione, anticipando il Gruppo E
- omettere uno dei quattro esiti di EventoSegnazioneNumero o uno dei due esiti di EventoRicercaNumeroInCartelle

### Project padre

- [docs/2 - projects/DESIGN_test_esito_azione_v1.0.0.md](../2%20-%20projects/DESIGN_test_esito_azione_v1.0.0.md)

### Criteri di completamento

- bingo_game/events/eventi.py e' stato letto integralmente prima della scrittura del test
- bingo_game/events/eventi_output_ui_umani.py e' stato letto prima della costruzione dei casi successo
- bingo_game/events/codici_errori.py e' stato letto prima della scrittura dei casi fallimento
- bingo_game/events/codici_output_ui_umani.py e' stato letto prima di fissare il contesto dei messaggi umani
- tests/unit/test_esito_azione.py esiste come unico nuovo file di test del task
- le classi nel file sono nell'ordine definito dal task
- python -m unittest tests.unit.test_esito_azione -q e' stato eseguito come verifica finale del passo implementativo
- il file non contiene import pytest
- il file non contiene fixture pytest
- nessun file esistente fuori da tests/unit/test_esito_azione.py e' stato modificato

## Stato Avanzamento

- [x] Definito
- [x] In implementazione
- [x] Test superati
- [x] Chiuso