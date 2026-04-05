---
type: plan
feature: migrazione_test_silent_controller_unittest
status: DRAFT
agent: Agent-Plan
version: 0.9.1
date: 2026-03-28
design: docs/2 - projects/DESIGN_migrazione_test_silent_controller_unittest.md
branch: feature/migrazione-test-silent-controller-unittest
---

# PLAN migrazione_test_silent_controller_unittest v0.9.1

## Executive Summary

- Tipo: correzione mirata di test
- Feature: migrazione_test_silent_controller_unittest
- Priorita: alta, per chiudere l'ultimo file rimasto a meta migrazione pytest -> unittest
- Branch: feature/migrazione-test-silent-controller-unittest
- Versione target: v0.9.1
- Design sorgente: [DESIGN_migrazione_test_silent_controller_unittest.md](../2%20-%20projects/DESIGN_migrazione_test_silent_controller_unittest.md)

## Problema e Obiettivo

Il file tests/test_silent_controller.py contiene ancora dipendenze strutturali da pytest che impediscono l'esecuzione pulita con unittest e producono gli errori gia osservati nella suite completa: fixture non trovate, pytest.raises residuo e test che dipendono da capsys.

L'obiettivo del piano e convertire il file a unittest puro, senza alterare il codice applicativo e senza espandere lo scope ad altri file di test. Il risultato atteso e un file scoperto ed eseguibile con python -m unittest tests.test_silent_controller e compatibile con il resto della suite.

## File coinvolti

### MODIFY

- tests/test_silent_controller.py

### VERIFY ONLY

- tests/test_game_controller.py
- tests/unit/test_game_controller_loop.py

### DOCUMENTAZIONE

- docs/2 - projects/DESIGN_migrazione_test_silent_controller_unittest.md
- docs/3 - coding plans/PLAN_migrazione_test_silent_controller_unittest_v0.9.1.md
- docs/5 - todolist/TODO_migrazione_test_silent_controller_unittest_v0.9.1.md
- docs/todo.md

## Fasi sequenziali

### Fase 1 — Portare le classi a unittest.TestCase

Azioni:

1. Aggiungere import unittest e io nel file target.
2. Far ereditare TestControllerSilenzioso, TestContrattiRitorno e TestMESSAGGICONTROLLER da unittest.TestCase.
3. Sostituire gli assert nativi con assert unittest coerenti al comportamento atteso.

Criteri di completamento:

- Nessuna classe di test resta semplice classe Python.
- Nessun assert nativo resta nel file, salvo eventuali assert interni non di test che qui non sono previsti.

### Fase 2 — Convertire le fixture pytest in helper o setUp

Azioni:

1. Trasformare partita_mock in factory privata di mock Partita in stato in_corso.
2. Trasformare partita_terminata_mock in factory privata di mock Partita in stato terminata.
3. Rimuovere i parametri fixture dalle firme dei test method.
4. Assicurare che i test che mutano il mock ricevano un'istanza nuova ad ogni esecuzione.
5. Usare setUp() come pattern preferito per lo stato condiviso in TestControllerSilenzioso e TestContrattiRitorno, in coerenza con il pattern gia adottato in tests/unit/test_game_controller_loop.py.
6. Riservare l'helper privato _build_partita_in_corso() ai soli test che modificano il mock inline (es. impostazione di side_effect o override di return_value), per garantire un mock fresco senza effetti collaterali tra test.

Criteri di completamento:

- Nessun test method accetta parametri diversi da self.
- Nessun riferimento concettuale a fixture pytest resta nel file.

### Fase 3 — Convertire capsys in cattura stdout unittest

Azioni:

1. Sostituire l'uso di capsys.readouterr().out con patch di sys.stdout e io.StringIO.
2. Applicare la cattura localmente ai soli test della classe TestControllerSilenzioso.
3. Verificare che ciascun test continui a validare buffer vuoto.
4. Iniziare la conversione da test_crea_partita_standard_silenzioso, il caso piu articolato (patch annidate + cattura stdout), e usarlo come modello stilistico per i restanti sette test della classe.

Criteri di completamento:

- Nessuna firma di test usa piu capsys.
- Tutti i test di silenziosita verificano buffer.getvalue() uguale a stringa vuota.

### Fase 4 — Convertire pytest.raises e rifinire il file

Azioni:

1. Sostituire pytest.raises(ValueError) con self.assertRaises(ValueError).
2. Rimuovere ogni dipendenza residua da pytest, inclusi eventuali import.
3. Valutare uso di self.subTest nel loop su MESSAGGI_CONTROLLER per failure piu leggibili per chiave.

Criteri di completamento:

- Nessun import pytest nel file.
- Nessuna stringa pytest o costrutto pytest rimane nel codice del test.

### Fase 5 — Validazione locale mirata

Azioni:

1. Eseguire python -m unittest tests.test_silent_controller.
2. Eseguire un grep su tests/test_silent_controller.py per confermare assenza di pytest.
3. Eseguire una rilettura veloce del file per verificare coerenza con i riferimenti stilistici.

Criteri di completamento:

- File verde in isolamento con unittest.
- Assenza totale di dipendenze pytest.

## Test Plan

- Test principale: python -m unittest tests.test_silent_controller
- Verifica strutturale: grep pytest su tests/test_silent_controller.py deve restituire zero occorrenze rilevanti
- Verifica stilistica: confronto manuale con i pattern di [tests/test_game_controller.py](../../tests/test_game_controller.py) e [tests/unit/test_game_controller_loop.py](../../tests/unit/test_game_controller_loop.py)

## Rischi operativi

- Reimpiego accidentale dello stesso mock tra test con side effect diversi.
- Cattura stdout definita troppo estesa e quindi poco affidabile.
- Conversione parziale degli assert che lascerebbe il file ancora eterogeneo.

## Gate di uscita

- Il file target passa con unittest in esecuzione isolata.
- Il file non importa pytest.
- Il file usa solo classi TestCase, helper espliciti e patch standard library.
