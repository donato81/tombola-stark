---
type: todo
feature: test_esito_azione
agent: Agent-Plan
status: DRAFT
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_test_esito_azione_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_test_esito_azione_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: todo_task
titolo: TODO operativo per i test unitari di EsitoAzione
data_creazione: 2026-03-30
agente: Agent-Plan
stato: bozza
feature: test_esito_azione
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_test_esito_azione_v1.0.0.md
design: docs/2 - projects/DESIGN_test_esito_azione_v1.0.0.md
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Descrizione task

Creare il file tests/unit/test_esito_azione.py per coprire costruzione, rendering e operatori magici
di EsitoAzione nel perimetro del Gruppo D, senza toccare altri file di test e senza modificare file in [bingo_game/](../../bingo_game/).

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Scadenza (opzionale)

Non definita

### Riferimento project/plan padre

- Project: [DESIGN_test_esito_azione_v1.0.0.md](../2%20-%20projects/DESIGN_test_esito_azione_v1.0.0.md)
- Plan: [PLAN_test_esito_azione_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_esito_azione_v1.0.0.md)
- Report: [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)

## Checklist operativa

### Passo 1 - Leggere eventi.py integralmente

- [ ] Leggere [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py) e annotare la firma di successo()
- [ ] Leggere [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py) e annotare la firma di fallimento()
- [ ] Leggere [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py) e annotare tutti i rami coperti di __str__ nel perimetro Gruppo D
- [ ] Leggere [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py) e annotare il comportamento di __eq__ con stringhe
- [ ] Leggere [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py) e annotare il comportamento di __contains__

### Passo 2 - Leggere eventi_output_ui_umani.py

- [ ] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i campi di EventoSegnazioneNumero
- [ ] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i campi di RisultatoRicercaNumeroInCartella
- [ ] Leggere [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) e annotare i campi di EventoRicercaNumeroInCartelle
- [ ] Verificare che i factory methods disponibili permettano i casi successo richiesti senza mock

### Passo 3 - Leggere codici_errori.py

- [ ] Leggere [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) e annotare CARTELLE_NESSUNA_ASSEGNATA
- [ ] Leggere [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) e annotare FOCUS_CARTELLA_NON_IMPOSTATO
- [ ] Leggere [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) e annotare NUMERO_NON_VALIDO
- [ ] Leggere [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) e annotare NUMERO_TIPO_NON_VALIDO
- [ ] Leggere [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) e annotare FOCUS_CARTELLA_FUORI_RANGE
- [ ] Leggere [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) e annotare ERRORE_INTERNO

### Passo 4 - Leggere codici_output_ui_umani.py

- [ ] Leggere [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py) e annotare i codici per segnazione numero
- [ ] Leggere [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py) e annotare i codici per ricerca numero
- [ ] Verificare che il contesto semantico dei codici output sia coerente con i rami testati di __str__

### Passo 5 - Creare tests/unit/test_esito_azione.py

- [ ] Creare tests/unit/test_esito_azione.py
- [ ] Usare esclusivamente unittest come libreria di test
- [ ] Inserire TestEsitoAzioneCostruzione come prima classe del file
- [ ] Inserire TestEsitoAzioneStrFallimento come seconda classe del file
- [ ] Inserire TestEsitoAzioneStrSuccesso come terza classe del file
- [ ] Inserire TestEsitoAzioneEqContains come quarta classe del file
- [ ] Coprire lo scenario successo() senza evento
- [ ] Coprire lo scenario successo() con evento valorizzato
- [ ] Coprire lo scenario fallimento("ERRORE_INTERNO")
- [ ] Coprire il ramo __str__ di fallimento per CARTELLE_NESSUNA_ASSEGNATA
- [ ] Coprire il ramo __str__ di fallimento per FOCUS_CARTELLA_NON_IMPOSTATO
- [ ] Coprire il ramo __str__ di fallimento per NUMERO_NON_VALIDO
- [ ] Coprire il ramo __str__ di fallimento per NUMERO_TIPO_NON_VALIDO
- [ ] Coprire il ramo __str__ di fallimento per FOCUS_CARTELLA_FUORI_RANGE
- [ ] Coprire il ramo __str__ di fallimento per il fallback ERRORE_INTERNO
- [ ] Coprire il ramo __str__ di successo con evento None
- [ ] Coprire il ramo __str__ di successo con EventoFocusCartellaImpostato
- [ ] Coprire il ramo __str__ di successo con EventoFocusAutoImpostato
- [ ] Coprire il ramo __str__ di successo con EventoSegnazioneNumero esito segnato
- [ ] Coprire il ramo __str__ di successo con EventoSegnazioneNumero esito gia_segnato
- [ ] Coprire il ramo __str__ di successo con EventoSegnazioneNumero esito non_presente
- [ ] Coprire il ramo __str__ di successo con EventoSegnazioneNumero esito non_estratto
- [ ] Coprire il ramo __str__ di successo con EventoRicercaNumeroInCartelle esito non_trovato
- [ ] Coprire il ramo __str__ di successo con EventoRicercaNumeroInCartelle esito trovato
- [ ] Coprire il fallback generico di __str__ con evento non riconosciuto
- [ ] Coprire __eq__ tra due successi identici
- [ ] Coprire __eq__ tra successo e fallimento
- [ ] Coprire __eq__ tra due fallimenti con stesso codice
- [ ] Coprire __eq__ con stringa per CARTELLE_NESSUNA_ASSEGNATA
- [ ] Coprire __eq__ con stringa per FOCUS_CARTELLA_NON_IMPOSTATO
- [ ] Coprire __contains__ con stringa presente nel rendering
- [ ] Coprire __contains__ con stringa assente nel rendering

### Passo 6 - Verificare che tutti i test del file passino

- [ ] Eseguire python -m unittest tests.unit.test_esito_azione -q
- [ ] Verificare che tests/unit/test_esito_azione.py venga raccolto dal runner
- [ ] Verificare che tutti i test del Gruppo D passino

### Passo 7 - Verificare assenza di pytest

- [ ] Verificare che il file non contenga import di pytest
- [ ] Verificare che il file non contenga fixture pytest
- [ ] Verificare che il file usi solo unittest come libreria di test

### Passo 8 - Confermare il rispetto del perimetro

- [ ] Verificare che nessun file esistente fuori da tests/unit/test_esito_azione.py sia stato modificato
- [ ] Verificare che nessun file in [bingo_game/](../../bingo_game/) sia stato toccato
- [ ] Verificare che il file nuovo non includa scenari dei Gruppi A, B, C o E

## Note operative

- Nessun mock necessario per i rami focus, segnazione e ricerca del perimetro richiesto.
- Nessuna dipendenza da wx, filesystem o avvio partita.
- Il file deve usare unittest.TestCase e asserzioni della standard library.
- I testi attesi dei casi di __str__ devono essere ricavati dal codice reale di [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py).
- I codici di errore dei casi negativi devono essere ricavati da [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py).

## Stato Avanzamento

- [x] Pianificato
- [ ] In corso
- [ ] Completato
- [ ] Verificato