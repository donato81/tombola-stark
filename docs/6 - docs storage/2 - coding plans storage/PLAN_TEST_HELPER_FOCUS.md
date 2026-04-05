---
type: plan
feature: test_helper_focus
agent: Agent-Plan
status: COMPLETED
version: v1.0
design_ref: docs/2 - projects/DESIGN_TEST_HELPER_FOCUS.md
date: 2026-03-30
report_ref: docs/4 - reports/report_verifica_lavori_test_helper_focus.md
---

## Metadati

tipo: coding_plan
titolo: Piano implementazione test diretti per GestioneFocusMixin
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completato
feature: test_helper_focus
versione_progetto: v1.0
design: docs/2 - projects/DESIGN_TEST_HELPER_FOCUS.md
report: docs/4 - reports/report_verifica_lavori_test_helper_focus.md

## Contenuto

### Riferimento design

- Design padre: `docs/2 - projects/DESIGN_TEST_HELPER_FOCUS.md`

### Obiettivo operativo

Creare `tests/unit/test_helper_focus.py` con test diretti in `unittest`
per `GestioneFocusMixin`, usando lo stub minimale concordato e lasciando
intatti i docstring e i file Python di produzione.

### Fasi di implementazione

#### Fase 1 — Stub

Cosa si fa:
- creare nel file di test la classe `StubFocus`
- riportare la definizione concordata senza variazioni

File coinvolto:
- `tests/unit/test_helper_focus.py`

Criterio di completamento:
- lo stub esiste nel file e contiene esattamente gli attributi richiesti

#### Fase 2 — setUp

Cosa si fa:
- creare `TestGestioneFocusMixin(unittest.TestCase)`
- aggiungere `setUp` con istanza di `StubFocus` e una `Cartella` di test

File coinvolto:
- `tests/unit/test_helper_focus.py`

Criterio di completamento:
- ogni test puo' riusare stub e cartella senza setup duplicato

#### Fase 3 — Gruppo 1

Cosa si fa:
- implementare i test del gruppo cartella sui metodi 2 e 3

File coinvolto:
- `tests/unit/test_helper_focus.py`

Criterio di completamento:
- presenti i 3 test di cartella con assertion su `ok` ed `errore`

#### Fase 4 — Gruppo 2

Cosa si fa:
- implementare i test del gruppo riga sui metodi 5, 6 e 7

File coinvolto:
- `tests/unit/test_helper_focus.py`

Criterio di completamento:
- presenti i 7 test riga con copertura diretta dei casi assenti, fuori range e ok

#### Fase 5 — Gruppo 3

Cosa si fa:
- implementare i test del gruppo colonna sui metodi 8, 9 e 10

File coinvolto:
- `tests/unit/test_helper_focus.py`

Criterio di completamento:
- presenti i 9 test colonna, speculari a quelli del gruppo riga

#### Fase 6 — Gruppo 4

Cosa si fa:
- implementare i test del reset completo sul metodo 15

File coinvolto:
- `tests/unit/test_helper_focus.py`

Criterio di completamento:
- presenti i 2 test reset e verificano che tutti i focus diventino None

#### Fase 7 — Verifica esecuzione

Cosa si fa:
- eseguire `python -m unittest tests/unit/test_helper_focus.py`

File coinvolto:
- `tests/unit/test_helper_focus.py`

Criterio di completamento:
- tutti i test del file passano senza failure ne' error

### Nota vincolante

Il lavoro non puo' essere considerato concluso finche' tutti i test del file
`tests/unit/test_helper_focus.py` non risultano verdi.

## Stato Avanzamento

- [x] Piano definito
- [x] Approvato
- [x] In implementazione
- [x] Verificato