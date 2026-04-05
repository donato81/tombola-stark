---
type: plan
feature: test_eventi_output_navigazione
agent: Agent-Plan
status: READY
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_test_eventi_output_navigazione_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per i test unitari degli eventi output navigazione
data_creazione: 2026-03-30
agente: Agent-Plan
stato: pronto
feature: test_eventi_output_navigazione
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_test_eventi_output_navigazione_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Executive Summary

Tipo intervento: creazione nuovo file di test unitario
Priorita': P1
Scope: implementare tests/unit/test_eventi_output_navigazione.py per il sottogruppo E2
Vincoli: uso obbligatorio di unittest; nessun mock; nessuna modifica a bingo_game/ o ad altri file di test

### Problema e Obiettivo

Il repository non possiede ancora una suite dedicata alle classi E2 di navigazione.
L'obiettivo operativo del piano e' creare tests/unit/test_eventi_output_navigazione.py per congelare i rami mostra/limite, le conversioni 1-based e la scomposizione dei pacchetti avanzati del perimetro E2.

### File coinvolti

- [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) - READ
- [docs/2 - projects/DESIGN_test_eventi_output_navigazione_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_navigazione_v1.0.0.md) - READ
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md) - READ
- tests/unit/test_eventi_output_navigazione.py - CREATE

### Fasi sequenziali

#### Passo 1 - Leggere integralmente il perimetro E2 nel modulo di produzione

- Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- Annotare factory e campi delle sei classi del gruppo E2

#### Passo 2 - Preparare dati di test per rami mostra e limite

- Definire tuple riga_semplice e colonna_semplice
- Definire pacchetti dati_riga_avanzati e dati_colonna_avanzati con dict di stato e tuple ordinate
- Definire casi minimi e massimi per totale_righe e totale_colonne

#### Passo 3 - Creare tests/unit/test_eventi_output_navigazione.py

- Separare i test per riga, riga avanzata, colonna, colonna avanzata e i due eventi diretti
- Usare solo unittest.TestCase
- Verificare mostra, limite minimo, limite massimo e coercizione a tuple negli eventi diretti

#### Passo 4 - Verificare il file in isolamento

- Eseguire python -m unittest tests.unit.test_eventi_output_navigazione -q
- Verificare che tutti i test del file passino

#### Passo 5 - Verificare assenza di pytest

- Confermare che il file non contenga import pytest
- Confermare che il file non contenga fixture pytest
- Confermare che il file usi solo unittest

#### Passo 6 - Confermare il rispetto del perimetro

- Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato modificato
- Verificare che nessun altro file in tests/unit/ sia stato modificato

### Definizione di completamento

Il piano E2 si considera completato quando esiste un solo nuovo file di test, validato con unittest, confinato al perimetro delle sei classi di navigazione e privo di pytest o mock.
