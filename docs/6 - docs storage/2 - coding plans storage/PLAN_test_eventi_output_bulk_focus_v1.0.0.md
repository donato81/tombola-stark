---
type: plan
feature: test_eventi_output_bulk_focus
agent: Agent-Plan
status: READY
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_test_eventi_output_bulk_focus_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per i test unitari degli eventi output bulk e focus
data_creazione: 2026-03-30
agente: Agent-Plan
stato: pronto
feature: test_eventi_output_bulk_focus
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_test_eventi_output_bulk_focus_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Executive Summary

Tipo intervento: creazione nuovo file di test unitario
Priorita': P1
Scope: implementare tests/unit/test_eventi_output_bulk_focus.py per il sottogruppo E5
Vincoli: uso obbligatorio di unittest; MagicMock consentito solo nei due factory bulk; nessuna modifica a bingo_game/ o ad altri file di test

### Problema e Obiettivo

Il repository non possiede ancora una suite dedicata alle classi E5 di aggregazione bulk e stato focus.
L'obiettivo operativo del piano e' creare tests/unit/test_eventi_output_bulk_focus.py per congelare numerazione 1-based, aggregazione immutabile dei pacchetti cartella e conversione degli indici di focus.

### File coinvolti

- [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) - READ
- [docs/2 - projects/DESIGN_test_eventi_output_bulk_focus_v1.0.0.md](../2%20-%20projects/DESIGN_test_eventi_output_bulk_focus_v1.0.0.md) - READ
- [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md) - READ
- tests/unit/test_eventi_output_bulk_focus.py - CREATE

### Fasi sequenziali

#### Passo 1 - Leggere integralmente il perimetro E5 nel modulo di produzione

- Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- Annotare i due factory crea_da_cartelle() e il factory crea_da_indici() di EventoStatoFocusCorrente

#### Passo 2 - Preparare doppi di test solo dove richiesto

- Preparare MagicMock con interfaccia minima per get_griglia_semplice() nel caso semplice
- Preparare MagicMock con interfaccia minima per get_dati_visualizzazione_avanzata() nel caso avanzato
- Preparare casi reali a primitivi per EventoStatoFocusCorrente senza mock

#### Passo 3 - Creare tests/unit/test_eventi_output_bulk_focus.py

- Usare unittest.TestCase e unittest.mock.MagicMock
- Verificare totale_cartelle, numerazione 1-based, ordine naturale e shape della tuple finale nei due factory bulk
- Verificare le combinazioni principali di focus presente e assente su EventoStatoFocusCorrente

#### Passo 4 - Verificare il file in isolamento

- Eseguire python -m unittest tests.unit.test_eventi_output_bulk_focus -q
- Verificare che tutti i test del file passino

#### Passo 5 - Verificare assenza di pytest

- Confermare che il file non contenga import pytest
- Confermare che il file non contenga fixture pytest
- Confermare che il file usi solo unittest e unittest.mock

#### Passo 6 - Confermare il rispetto del perimetro

- Verificare che MagicMock sia usato solo nei due factory bulk
- Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato modificato
- Verificare che nessun altro file in tests/unit/ sia stato modificato

### Definizione di completamento

Il piano E5 si considera completato quando esiste un solo nuovo file di test, validato con unittest, confinato al perimetro bulk/focus e con MagicMock usato esclusivamente dove previsto dal report.
