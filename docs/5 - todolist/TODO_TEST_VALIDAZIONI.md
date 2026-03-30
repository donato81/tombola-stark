---
type: todo
feature: test_validazioni
agent: Agent-Plan
status: COMPLETED
version: v1.0
plan_ref: docs/3 - coding plans/PLAN_TEST_VALIDAZIONI.md
design_ref: docs/2 - projects/DESIGN_TEST_VALIDAZIONI.md
date: 2026-03-30
report_ref: docs/4 - reports/REPORT_ANALISI_VALIDAZIONI_2026-03-30.md
---

## Metadati

tipo: todo_task
titolo: TODO suite unittest per i moduli di validazione
data_creazione: 2026-03-30
agente: Agent-Plan
stato: completed
feature: test_validazioni
versione_progetto: v1.0
plan: docs/3 - coding plans/PLAN_TEST_VALIDAZIONI.md
design: docs/2 - projects/DESIGN_TEST_VALIDAZIONI.md
report: docs/4 - reports/REPORT_ANALISI_VALIDAZIONI_2026-03-30.md

## Contenuto

### Descrizione task

Scrivere una suite unittest diretta e isolata per
bingo_game/validations/validazioni_input.py e
bingo_game/validations/validazione_oggetti.py.

### Priorita

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: DESIGN_TEST_VALIDAZIONI.md
- Plan: PLAN_TEST_VALIDAZIONI.md
- Report: REPORT_ANALISI_VALIDAZIONI_2026-03-30.md

## Checklist operativa

### File: tests/unit/test_validazioni_input.py

- [x] Creare il file tests/unit/test_validazioni_input.py

#### Classe: TestEsitoNumeroIntero

- [x] test_esito_numero_intero_int_valido_restituisce_ok
- [x] test_esito_numero_intero_bool_restituisce_tipo_non_valido
- [x] test_esito_numero_intero_float_restituisce_tipo_non_valido
- [x] test_esito_numero_intero_none_restituisce_tipo_non_valido

#### Classe: TestEsitoNumeroInRange190

- [x] test_esito_numero_in_range_1_90_con_1_restituisce_ok
- [x] test_esito_numero_in_range_1_90_con_90_restituisce_ok
- [x] test_esito_numero_in_range_1_90_con_0_restituisce_numero_non_valido
- [x] test_esito_numero_in_range_1_90_con_91_restituisce_numero_non_valido
- [x] test_esito_numero_in_range_1_90_con_tipo_errato_restituisce_tipo_non_valido

#### Classe: TestEsitoNumeroRigaInRange13

- [x] test_esito_numero_riga_in_range_1_3_con_1_restituisce_ok
- [x] test_esito_numero_riga_in_range_1_3_con_3_restituisce_ok
- [x] test_esito_numero_riga_in_range_1_3_con_0_restituisce_numero_riga_fuori_range
- [x] test_esito_numero_riga_in_range_1_3_con_4_restituisce_numero_riga_fuori_range
- [x] test_esito_numero_riga_in_range_1_3_con_tipo_errato_restituisce_tipo_non_valido

#### Classe: TestEsitoNumeroColonnaInRange19

- [x] test_esito_numero_colonna_in_range_1_9_con_1_restituisce_ok
- [x] test_esito_numero_colonna_in_range_1_9_con_9_restituisce_ok
- [x] test_esito_numero_colonna_in_range_1_9_con_0_restituisce_numero_colonna_fuori_range
- [x] test_esito_numero_colonna_in_range_1_9_con_10_restituisce_numero_colonna_fuori_range
- [x] test_esito_numero_colonna_in_range_1_9_con_tipo_errato_restituisce_tipo_non_valido

#### Classe: TestEsitoReclamoTurnoLibero

- [x] test_esito_reclamo_turno_libero_con_none_restituisce_ok
- [x] test_esito_reclamo_turno_libero_con_oggetto_restituisce_reclamo_gia_presente

#### Classe: TestEsitoTipoVittoriaSupportato

- [x] test_esito_tipo_vittoria_supportato_tombola_restituisce_ok
- [x] test_esito_tipo_vittoria_supportato_ambo_restituisce_ok
- [x] test_esito_tipo_vittoria_supportato_terno_restituisce_ok
- [x] test_esito_tipo_vittoria_supportato_quaterna_restituisce_ok
- [x] test_esito_tipo_vittoria_supportato_cinquina_restituisce_ok
- [x] test_esito_tipo_vittoria_supportato_valore_sconosciuto_restituisce_tipo_vittoria_non_valido
- [x] test_esito_tipo_vittoria_supportato_maiuscolo_restituisce_tipo_vittoria_non_valido
- [x] test_esito_tipo_vittoria_supportato_none_restituisce_tipo_vittoria_non_valido

### File: tests/unit/test_validazione_oggetti.py

- [x] Creare il file tests/unit/test_validazione_oggetti.py

#### Classe: TestEsitoTabelloneDisponibile

- [x] test_esito_tabellone_disponibile_none_restituisce_tabellone_non_disponibile
- [x] test_esito_tabellone_disponibile_tabellone_reale_restituisce_ok
- [x] test_esito_tabellone_disponibile_stub_con_get_numeri_estratti_restituisce_ok
- [x] test_esito_tabellone_disponibile_stub_con_is_numero_estratto_restituisce_ok
- [x] test_esito_tabellone_disponibile_oggetto_incompatibile_restituisce_tabellone_non_disponibile

#### Classe: TestEsitoCoordinateNumeroCoerenti

- [x] test_esito_coordinate_numero_coerenti_coordinate_presenti_restituisce_ok
- [x] test_esito_coordinate_numero_coerenti_coordinate_none_restituisce_cartella_stato_incoerente
- [x] test_esito_coordinate_numero_coerenti_numero_non_int_restituisce_inputnonvalido
- [x] test_esito_coordinate_numero_coerenti_eccezione_del_metodo_cartella_viene_propagata

### Verifica finale

- [x] Eseguire python -m unittest discover tests/unit
- [x] Confermare che tutti i test della nuova suite siano verdi

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato