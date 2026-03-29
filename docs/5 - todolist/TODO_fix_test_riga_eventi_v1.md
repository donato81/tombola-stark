---
type: todo
feature: fix_test_riga_eventi
agent: Agent-Plan
status: DRAFT
version: v1.0
plan_ref: docs/3 - coding plans/PLAN_fix_test_riga_eventi_v1.md
design_ref: docs/2 - projects/DESIGN_fix_test_riga_eventi.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md
---

## Metadati

tipo: todo_task
titolo: TODO tranche 1 modernizzazione test riga
data_creazione: 2026-03-29
agente: Agent-Plan
stato: bozza
feature: fix_test_riga_eventi
versione_progetto: v1.0
plan: docs/3 - coding plans/PLAN_fix_test_riga_eventi_v1.md
design: docs/2 - projects/DESIGN_fix_test_riga_eventi.md
report: docs/4 - reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md

## Contenuto

### Descrizione task

Modernizzare i 20 test del gruppo riga in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py),
sostituendo assertion su testo renderizzato con assertion strutturate su
`EsitoAzione`, `EventoNavigazioneRiga` ed `EventoNavigazioneRigaAvanzata`.

### Priorita

P1

### Agente assegnato

Agent-Code

### Riferimento project/plan padre

- Project: [DESIGN_fix_test_riga_eventi.md](../2%20-%20projects/DESIGN_fix_test_riga_eventi.md)
- Plan: [PLAN_fix_test_riga_eventi_v1.md](../3%20-%20coding%20plans/PLAN_fix_test_riga_eventi_v1.md)
- Report: [REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md](../4%20-%20reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md)

## Checklist operativa

### Micro-fase 1 — su_semplice

- [ ] Aggiornare `test_sposta_focus_riga_su_semplice_cartella_mancante`
- [ ] Aggiornare `test_sposta_focus_riga_su_semplice_prima_riga`
- [ ] Aggiornare `test_sposta_focus_riga_su_semplice_movimento_normale`
- [ ] Aggiornare `test_sposta_focus_riga_su_semplice_auto_inizializzazione`
- [ ] Aggiornare `test_sposta_focus_riga_su_semplice_stato_interno`
- [ ] Verificare il gruppo `su_semplice`

### Micro-fase 2 — giu_semplice

- [ ] Aggiornare `test_sposta_focus_riga_giu_semplice_cartella_mancante`
- [ ] Aggiornare `test_sposta_focus_riga_giu_semplice_ultima_riga`
- [ ] Aggiornare `test_sposta_focus_riga_giu_semplice_movimento_normale`
- [ ] Aggiornare `test_sposta_focus_riga_giu_semplice_auto_inizializzazione`
- [ ] Aggiornare `test_sposta_focus_riga_giu_semplice_stato_interno`
- [ ] Verificare il gruppo `giu_semplice`

### Micro-fase 3 — su_avanzata

- [ ] Aggiornare `test_sposta_focus_riga_su_avanzata_cartella_mancante`
- [ ] Aggiornare `test_sposta_focus_riga_su_avanzata_prima_riga`
- [ ] Aggiornare `test_sposta_focus_riga_su_avanzata_movimento_normale`
- [ ] Aggiornare `test_sposta_focus_riga_su_avanzata_auto_inizializzazione`
- [ ] Aggiornare `test_sposta_focus_riga_su_avanzata_stato_cartella_con_segni`
- [ ] Verificare il gruppo `su_avanzata`

### Micro-fase 4 — giu_avanzata

- [ ] Aggiornare `test_sposta_focus_riga_giu_avanzata_cartella_mancante`
- [ ] Aggiornare `test_sposta_focus_riga_giu_avanzata_ultima_riga`
- [ ] Aggiornare `test_sposta_focus_riga_giu_avanzata_movimento_normale`
- [ ] Aggiornare `test_sposta_focus_riga_giu_avanzata_auto_inizializzazione`
- [ ] Aggiornare `test_sposta_focus_riga_giu_avanzata_stato_cartella_con_segni`
- [ ] Verificare il gruppo `giu_avanzata`

### Chiusura tranche

- [ ] Eseguire verifica finale del file [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- [ ] Confermare che i 20 test riga sono allineati al contratto eventi
- [ ] Aggiornare questo TODO marcando le fasi completate

## Stato Avanzamento

- [x] Pianificato
- [ ] In corso
- [ ] Completato
- [ ] Verificato
