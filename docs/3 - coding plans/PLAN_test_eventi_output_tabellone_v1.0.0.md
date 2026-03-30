---
type: plan
feature: test_eventi_output_tabellone
agent: Agent-Plan
status: DRAFT
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_test_eventi_output_tabellone_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per i test unitari degli eventi output tabellone
data_creazione: 2026-03-30
agente: Agent-Plan
stato: bozza
feature: test_eventi_output_tabellone
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_test_eventi_output_tabellone_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Executive Summary

Tipo intervento: creazione nuovo file di test unitario
Priorita': P1
Scope: implementare tests/unit/test_eventi_output_tabellone.py per il sottogruppo E3
Vincoli: uso obbligatorio di unittest; nessun mock; nessuna modifica a bingo_game/ o ad altri file di test

### Problema e Obiettivo

Il repository non possiede ancora una suite dedicata agli eventi di interrogazione tabellone del Gruppo E3.
L'obiettivo operativo del piano e' creare tests/unit/test_eventi_output_tabellone.py per congelare factory method, normalizzazioni difensive e campi derivati del perimetro E3.

### File coinvolti

- [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) - READ
- [docs/2 - projects/DESIGN_test_eventi_output_tabellone_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_tabellone_v1.0.0.md) - READ
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md) - READ
- tests/unit/test_eventi_output_tabellone.py - CREATE

### Fasi sequenziali

#### Passo 1 - Leggere integralmente il perimetro E3 nel modulo di produzione

- Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- Annotare factory e campi delle cinque classi del gruppo E3

#### Passo 2 - Preparare dati di test reali

- Definire numeri singoli e sequenze di numeri per i casi con dati
- Definire casi vuoti per le factory nessuna_estrazione e per il riepilogo con zero estratti
- Definire un caso di overflow su richiesti per verificare il taglio agli ultimi elementi

#### Passo 3 - Creare tests/unit/test_eventi_output_tabellone.py

- Creare una classe di test per ciascuna famiglia funzionale del gruppo E3
- Usare solo unittest.TestCase
- Verificare normalizzazione a tuple, conteggi derivati e comportamento difensivo di ultimo_estratto

#### Passo 4 - Verificare il file in isolamento

- Eseguire python -m unittest tests.unit.test_eventi_output_tabellone -q
- Verificare che tutti i test del file passino

#### Passo 5 - Verificare assenza di pytest

- Confermare che il file non contenga import pytest
- Confermare che il file non contenga fixture pytest
- Confermare che il file usi solo unittest

#### Passo 6 - Confermare il rispetto del perimetro

- Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato modificato
- Verificare che nessun altro file in tests/unit/ sia stato modificato

### Definizione di completamento

Il piano E3 si considera completato quando esiste un solo nuovo file di test, validato con unittest, confinato agli eventi tabellone e privo di pytest o mock.
