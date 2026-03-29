---
type: plan
feature: fix_test_riga_eventi
agent: Agent-Plan
status: DRAFT
version: v1.0
design_ref: docs/2 - projects/DESIGN_fix_test_riga_eventi.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md
---

## Metadati

tipo: coding_plan
titolo: Piano tranche 1 modernizzazione test riga
data_creazione: 2026-03-29
agente: Agent-Plan
stato: bozza
feature: fix_test_riga_eventi
versione_progetto: v1.0
design: docs/2 - projects/DESIGN_fix_test_riga_eventi.md
report: docs/4 - reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md

## Contenuto

### Executive Summary

Tipo intervento: modernizzazione test
Priorita': P1
Branch: main
Versione di riferimento: v1.0
Scope: 20 test del gruppo riga in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
Codice applicativo: nessuna modifica prevista

### Problema e Obiettivo

I test di navigazione riga usano ancora assertion su stringhe renderizzate.
Questo li rende fragili e disallineati rispetto al contratto reale dei metodi,
che espongono `EsitoAzione` e eventi strutturati.

L'obiettivo della tranche 1 e' convertire i 20 test riga al pattern corretto,
senza toccare i metodi produttivi e senza uscire dal file di test.

### File coinvolti

- `tests/test_giocatore_umano.py` — MODIFY nella fase implementativa successiva
- `docs/4 - reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md` — CREATE
- `docs/2 - projects/DESIGN_fix_test_riga_eventi.md` — CREATE
- `docs/3 - coding plans/PLAN_fix_test_riga_eventi_v1.md` — CREATE
- `docs/5 - todolist/TODO_fix_test_riga_eventi_v1.md` — CREATE
- `docs/todo.md` — UPDATE

### Approccio operativo

L'implementazione dovra' seguire quattro micro-fasi, una per ogni gruppo di
metodo, con commit separato. Ogni micro-fase sostituira' le assertion su testo
con assertion su `ok`, `errore`, `evento` e sui campi dell'evento corretto.

### Fasi sequenziali

#### Fase 1 — su_semplice

Target:

- `test_sposta_focus_riga_su_semplice_cartella_mancante`
- `test_sposta_focus_riga_su_semplice_prima_riga`
- `test_sposta_focus_riga_su_semplice_movimento_normale`
- `test_sposta_focus_riga_su_semplice_auto_inizializzazione`
- `test_sposta_focus_riga_su_semplice_stato_interno`

Intervento:

- sostituire `assertEqual` testuali dei casi errore con verifiche su `ok`, `errore`, `evento`
- sostituire `assertIn("Riga 0:"...)` e ricerca numeri nel testo con confronti su `EventoNavigazioneRiga`
- mantenere i controlli sullo stato interno `_indice_riga_focus`

Commit previsto:

- `test(riga): modernizza su_semplice su EsitoAzione`

Controllo post-fase:

- eseguire i 5 test del gruppo
- confermare zero failure nel gruppo

#### Fase 2 — giu_semplice

Target:

- `test_sposta_focus_riga_giu_semplice_cartella_mancante`
- `test_sposta_focus_riga_giu_semplice_ultima_riga`
- `test_sposta_focus_riga_giu_semplice_movimento_normale`
- `test_sposta_focus_riga_giu_semplice_auto_inizializzazione`
- `test_sposta_focus_riga_giu_semplice_stato_interno`

Intervento:

- aggiornare i casi errore sui codici `CARTELLE_NESSUNA_ASSEGNATA` e `FOCUS_CARTELLA_NON_IMPOSTATO`
- aggiornare il caso limite massimo su `EventoNavigazioneRiga`
- aggiornare i casi movimento e auto-inizializzazione su `riga_semplice` e `numero_riga_corrente`

Commit previsto:

- `test(riga): modernizza giu_semplice su EsitoAzione`

Controllo post-fase:

- eseguire i 5 test del gruppo
- confermare zero failure nel gruppo

#### Fase 3 — su_avanzata

Target:

- `test_sposta_focus_riga_su_avanzata_cartella_mancante`
- `test_sposta_focus_riga_su_avanzata_prima_riga`
- `test_sposta_focus_riga_su_avanzata_movimento_normale`
- `test_sposta_focus_riga_su_avanzata_auto_inizializzazione`
- `test_sposta_focus_riga_su_avanzata_stato_cartella_con_segni`

Intervento:

- aggiornare i casi errore come sopra
- aggiornare il caso limite minimo su `EventoNavigazioneRigaAvanzata`
- nei casi di movimento confrontare l'intero triplo restituito da `get_dati_visualizzazione_riga_avanzata()`
- sostituire la ricerca di `*numero` con la verifica di `numeri_segnati_riga_ordinati`

Commit previsto:

- `test(riga): modernizza su_avanzata su evento strutturato`

Controllo post-fase:

- eseguire i 5 test del gruppo
- confermare zero failure nel gruppo

#### Fase 4 — giu_avanzata

Target:

- `test_sposta_focus_riga_giu_avanzata_cartella_mancante`
- `test_sposta_focus_riga_giu_avanzata_ultima_riga`
- `test_sposta_focus_riga_giu_avanzata_movimento_normale`
- `test_sposta_focus_riga_giu_avanzata_auto_inizializzazione`
- `test_sposta_focus_riga_giu_avanzata_stato_cartella_con_segni`

Intervento:

- aggiornare i casi errore come sopra
- aggiornare il caso limite massimo su `EventoNavigazioneRigaAvanzata`
- aggiornare i casi movimento e auto-inizializzazione sul triplo dati avanzati
- sostituire la ricerca testuale dell'asterisco con la lettura del campo strutturato dei numeri segnati

Commit previsto:

- `test(riga): modernizza giu_avanzata su evento strutturato`

Controllo post-fase:

- eseguire i 5 test del gruppo
- confermare zero failure nel gruppo

### Test Plan

Verifica per micro-fase:

- eseguire il sottoinsieme dei 5 test interessati
- controllare assenza di regressioni nel blocco appena toccato

Verifica finale:

- eseguire l'intero file [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- se richiesto dalla sessione di implementazione, eseguire la suite completa del progetto

### Rischi

- confondere numero riga 1-based dell'evento con indice interno 0-based
- mantenere assertion residue su testo nei casi con numeri segnati
- confrontare solo parte del payload avanzato invece dell'intero pacchetto dati
- toccare per errore test fuori tranche

### Dipendenze

- `docs/4 - reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md`
- `docs/2 - projects/DESIGN_fix_test_riga_eventi.md`

### Criteri di completamento

- 20 test aggiornati secondo il pattern strutturato
- nessun test del gruppo verde modificato
- file toccato in implementazione: solo `tests/test_giocatore_umano.py`
- suite ancora verde dopo la tranche

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso
