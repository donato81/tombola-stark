---
type: plan
feature: test_validazioni
agent: Agent-Plan
status: COMPLETED
version: v1.0
design_ref: docs/2 - projects/DESIGN_TEST_VALIDAZIONI.md
date: 2026-03-30
report_ref: docs/4 - reports/REPORT_ANALISI_VALIDAZIONI_2026-03-30.md
---

## Metadati

tipo: coding_plan
titolo: Piano di implementazione suite unittest per i moduli di validazione
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completed
feature: test_validazioni
versione_progetto: v1.0
design: docs/2 - projects/DESIGN_TEST_VALIDAZIONI.md
report: docs/4 - reports/REPORT_ANALISI_VALIDAZIONI_2026-03-30.md

## Contenuto

### Riferimento design

- Design padre: docs/2 - projects/DESIGN_TEST_VALIDAZIONI.md

### Obiettivo operativo

Creare una suite unittest diretta per i moduli di validazione, composta da
due file in tests/unit, senza modificare file di produzione e senza usare
pytest. Il lavoro si considera chiuso solo con suite verde sul comando di
discovery finale.

### Fasi di implementazione

#### Fase 1 - Creazione file tests/unit/test_validazioni_input.py

Cosa si fa:
- creare il file tests/unit/test_validazioni_input.py;
- aggiungere import unittest e import delle sei funzioni target;
- definire le classi di test per i gruppi di validazione input.

File coinvolto:
- tests/unit/test_validazioni_input.py

Criterio di completamento:
- il file esiste;
- contiene tutte le classi previste dal design;
- i test coprono i casi base, i bordi del range e i tipi errati.

#### Fase 2 - Implementazione test per esito_numero_intero

Cosa si fa:
- scrivere i test su int valido, bool, float e None.

File coinvolto:
- tests/unit/test_validazioni_input.py

Criterio di completamento:
- i quattro casi producono l'esito atteso su ok ed errore.

#### Fase 3 - Implementazione test per i range numerici

Cosa si fa:
- scrivere i test per esito_numero_in_range_1_90;
- scrivere i test per esito_numero_riga_in_range_1_3;
- scrivere i test per esito_numero_colonna_in_range_1_9.

File coinvolto:
- tests/unit/test_validazioni_input.py

Criterio di completamento:
- i bordi validi sono verdi;
- i fuori range restituiscono i codici reali del codice;
- i tipi errati propagano NUMERO_TIPO_NON_VALIDO.

#### Fase 4 - Implementazione test per reclamo e tipo vittoria

Cosa si fa:
- scrivere i test per esito_reclamo_turno_libero;
- scrivere i test per esito_tipo_vittoria_supportato.

File coinvolto:
- tests/unit/test_validazioni_input.py

Criterio di completamento:
- tutti i cinque tipi vittoria validi sono coperti;
- i casi non validi e i casi non None per il reclamo sono coperti.

#### Fase 5 - Creazione file tests/unit/test_validazione_oggetti.py

Cosa si fa:
- creare il file tests/unit/test_validazione_oggetti.py;
- aggiungere import unittest, unittest.mock e i riferimenti necessari;
- definire stub o MagicMock minimi per tabellone e cartella.

File coinvolto:
- tests/unit/test_validazione_oggetti.py

Criterio di completamento:
- il file esiste;
- e' indipendente dagli altri test;
- usa solo unittest e unittest.mock.

#### Fase 6 - Implementazione test per esito_tabellone_disponibile

Cosa si fa:
- coprire None;
- coprire istanza reale di Tabellone;
- coprire stub con get_numeri_estratti;
- coprire stub con is_numero_estratto;
- coprire oggetto incompatibile.

File coinvolto:
- tests/unit/test_validazione_oggetti.py

Criterio di completamento:
- sono coperti sia il ramo isinstance sia il ramo duck-typed.

#### Fase 7 - Implementazione test per esito_coordinate_numero_coerenti

Cosa si fa:
- coprire il caso con coordinate valide;
- coprire il caso con coordinate None;
- coprire il numero non int;
- coprire la propagazione di un'eccezione del metodo cartella.

File coinvolto:
- tests/unit/test_validazione_oggetti.py

Criterio di completamento:
- i tre esiti deterministici sono verificati;
- la propagazione eccezione e' documentata come comportamento attuale.

#### Fase 8 - Verifica finale della suite

Cosa si fa:
- eseguire il file input in isolamento;
- eseguire il file oggetti in isolamento;
- eseguire la discovery finale sull'intera cartella tests/unit.

File coinvolti:
- tests/unit/test_validazioni_input.py
- tests/unit/test_validazione_oggetti.py

Criterio di completamento:
- tutti i test risultano verdi;
- nessun failure;
- nessun error;
- nessun uso di pytest nei file creati.

### Nota vincolante

Tutti i test devono passare prima di considerare il lavoro concluso.
La fase di coding non si potra' considerare chiusa finche' la suite non
risulta verde sul comando finale.

### Comando finale da eseguire

python -m unittest discover tests/unit

## Stato Avanzamento

- [x] Piano definito
- [x] Validato
- [x] In implementazione
- [x] Verificato