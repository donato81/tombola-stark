---
type: plan
feature: test_eventi_output_cartella
agent: Agent-Plan
status: READY
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_test_eventi_output_cartella_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per i test unitari degli eventi output cartella
data_creazione: 2026-03-30
agente: Agent-Plan
stato: pronto
feature: test_eventi_output_cartella
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_test_eventi_output_cartella_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Executive Summary

Tipo intervento: creazione nuovo file di test unitario
Priorita': P1
Scope: implementare tests/unit/test_eventi_output_cartella.py per il sottogruppo E1
Vincoli: uso obbligatorio di unittest; nessun mock; nessuna modifica a bingo_game/ o ad altri file di test

### Problema e Obiettivo

Il repository non possiede ancora una suite dedicata alle classi E1 di eventi_output_ui_umani.py.
L'obiettivo operativo del piano e' creare tests/unit/test_eventi_output_cartella.py per congelare conversioni 1-based, ordinamenti, calcoli derivati e dati immutabili del perimetro E1.

### File coinvolti

- [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) - READ
- [docs/2 - projects/DESIGN_test_eventi_output_cartella_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_cartella_v1.0.0.md) - READ
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md) - READ
- tests/unit/test_eventi_output_cartella.py - CREATE

### Fasi sequenziali

#### Passo 1 - Leggere integralmente il perimetro E1 nel modulo di produzione

- Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- Annotare campi e factory method di EventoRiepilogoCartellaCorrente, EventoLimiteNavigazioneCartelle, EventoVisualizzaCartellaSemplice ed EventoVisualizzaCartellaAvanzata

#### Passo 2 - Preparare dati di test reali e immutabili

- Definire una griglia semplice 3x9 in forma tuple
- Definire un pacchetto dati_avanzati con griglia, stato_cartella e numeri_segnati_ordinati
- Definire sequenze numeri_non_segnati non ordinate per verificare l'ordinamento imposto dal factory

#### Passo 3 - Creare tests/unit/test_eventi_output_cartella.py

- Creare una classe di test per ciascuna dataclass del gruppo E1
- Usare solo unittest.TestCase e asserzioni standard library
- Coprire conversioni 0-based -> 1-based, ordinamenti, campi derivati e preservazione dei campi di input

#### Passo 4 - Verificare il file in isolamento

- Eseguire python -m unittest tests.unit.test_eventi_output_cartella -q
- Verificare che tutti i test del file passino

#### Passo 5 - Verificare assenza di pytest

- Confermare che il file non contenga import pytest
- Confermare che il file non contenga fixture pytest
- Confermare che il file usi solo unittest

#### Passo 6 - Confermare il rispetto del perimetro

- Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato modificato
- Verificare che nessun altro file in tests/unit/ sia stato modificato

### Definizione di completamento

Il piano E1 si considera completato quando esiste un solo nuovo file di test, validato con unittest, limitato al perimetro E1 e privo di qualunque dipendenza da pytest o mock.
