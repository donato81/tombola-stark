---
type: todo
feature: migrazione_test_silent_controller_unittest
status: DONE
version: 0.9.1
date: 2026-03-28
plan: docs/3 - coding plans/PLAN_migrazione_test_silent_controller_unittest_v0.9.1.md
---

# TODO migrazione_test_silent_controller_unittest v0.9.1

Piano padre: [PLAN_migrazione_test_silent_controller_unittest_v0.9.1.md](../3%20-%20coding%20plans/PLAN_migrazione_test_silent_controller_unittest_v0.9.1.md)

Istruzioni per Agent-Code: eseguire una fase alla volta. Non toccare codice applicativo. Validare il file target con unittest dopo ogni blocco significativo.

## Fase 1 — Portare le classi a TestCase

- [x] Aggiungere import unittest e io nel file tests/test_silent_controller.py.
- [x] Far ereditare tutte e tre le classi da unittest.TestCase.
- [x] Convertire gli assert nativi in assert unittest coerenti con il contratto di ogni test.

## Fase 2 — Sostituire le fixture pytest

- [x] Convertire partita_mock in helper privato o pattern equivalente unittest.
- [x] Convertire partita_terminata_mock in helper privato o pattern equivalente unittest.
- [x] Rimuovere i parametri fixture dalle firme dei test method.
- [x] Garantire un mock fresco nei test che impostano side_effect o cambiano return_value.
- [x] Preferire setUp() come pattern per lo stato condiviso nelle classi TestControllerSilenzioso e TestContrattiRitorno; usare helper privato _build_partita_in_corso() e _build_partita_terminata() solo nei test che modificano il mock inline (es. quelli che impostano side_effect o cambiano return_value).

- Nota: Fase 2 confermata completata in commit "test(tests): fase 2 - sostituire le fixture pytest".
## Fase 3 — Convertire capsys

Nota: il test piu complesso della fase e test_crea_partita_standard_silenzioso perche combina patch annidate multiple con la cattura stdout. Convertire questo test per primo e usarlo come riferimento stilistico per gli altri sette.

- [x] Sostituire capsys con patch di sys.stdout e io.StringIO nei test di silenziosita.
- [x] Verificare che ogni test confronti stdout con stringa vuota.
- [x] Completato il 2026-03-28.

## Fase 4 — Convertire pytest.raises e chiudere i residui pytest

- [x] Sostituire pytest.raises(ValueError) con self.assertRaises(ValueError).
- [x] Rimuovere ogni riferimento a pytest dal file.
- [x] Valutare subTest nel loop finale di TestMESSAGGICONTROLLER.

Completamento: 2026-03-28

## Fase 5 — Validazione

- [ ] Eseguire python -m unittest tests.test_silent_controller.
- [ ] Verificare che grep pytest sul file target non trovi dipendenze residue.
- [ ] Confermare allineamento stilistico con i file unittest di riferimento.
