---
type: plan
feature: test_eventi_output_segnazione
agent: Agent-Plan
status: DRAFT
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_test_eventi_output_segnazione_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per i test unitari degli eventi output segnazione e ricerca
data_creazione: 2026-03-30
agente: Agent-Plan
stato: bozza
feature: test_eventi_output_segnazione
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_test_eventi_output_segnazione_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Executive Summary

Tipo intervento: creazione nuovo file di test unitario
Priorita': P1
Scope: implementare tests/unit/test_eventi_output_segnazione.py per il sottogruppo E4
Vincoli: uso obbligatorio di unittest; nessun mock; nessuna modifica a bingo_game/ o ad altri file di test

### Problema e Obiettivo

Il repository non possiede ancora una suite dedicata agli eventi E4 di segnazione e ricerca.
L'obiettivo operativo del piano e' creare tests/unit/test_eventi_output_segnazione.py per congelare i quattro esiti di segnazione, il calcolo dei campi derivati e l'ordinamento dei risultati di ricerca.

### File coinvolti

- [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) - READ
- [docs/2 - projects/DESIGN_test_eventi_output_segnazione_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_segnazione_v1.0.0.md) - READ
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md) - READ
- tests/unit/test_eventi_output_segnazione.py - CREATE

### Fasi sequenziali

#### Passo 1 - Leggere integralmente il perimetro E4 nel modulo di produzione

- Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- Annotare i quattro factory di EventoSegnazioneNumero, la factory di RisultatoRicercaNumeroInCartella e i due factory di EventoRicercaNumeroInCartelle

#### Passo 2 - Preparare dati di test reali

- Definire input numerici e progressi cartella coerenti
- Definire coordinate per i rami con numero presente
- Definire una lista di risultati non ordinata per verificare il sort deterministico nel caso trovato

#### Passo 3 - Creare tests/unit/test_eventi_output_segnazione.py

- Usare solo unittest.TestCase
- Separare i test dei quattro esiti di segnazione dai test di ricerca
- Verificare numero_cartella 1-based, mancanti, coordinate None nei rami previsti e ordinamento risultati

#### Passo 4 - Verificare il file in isolamento

- Eseguire python -m unittest tests.unit.test_eventi_output_segnazione -q
- Verificare che tutti i test del file passino

#### Passo 5 - Verificare assenza di pytest

- Confermare che il file non contenga import pytest
- Confermare che il file non contenga fixture pytest
- Confermare che il file usi solo unittest

#### Passo 6 - Confermare il rispetto del perimetro

- Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato modificato
- Verificare che nessun altro file in tests/unit/ sia stato modificato

### Definizione di completamento

Il piano E4 si considera completato quando esiste un solo nuovo file di test, validato con unittest, confinato al perimetro segnazione e ricerca e privo di pytest o mock.
