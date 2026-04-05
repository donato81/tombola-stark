---
type: plan
feature: fix_test_colonna_sinistra_eventi
agent: Agent-Plan
status: READY
version: v1.0
design_ref: docs/2 - projects/DESIGN_fix_test_colonna_sinistra_eventi.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md
---

## Metadati

tipo: coding_plan
titolo: Piano tranche 2 modernizzazione test colonna sinistra
data_creazione: 2026-03-29
agente: Agent-Plan
stato: bozza
feature: fix_test_colonna_sinistra_eventi
versione_progetto: v1.0
design: docs/2 - projects/DESIGN_fix_test_colonna_sinistra_eventi.md
report: docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md

## Contenuto

### Executive Summary

Tipo intervento: modernizzazione test
Priorita': P1
Branch: main
Versione di riferimento: v1.0
Scope: test del gruppo colonna sinistra in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
Codice applicativo: nessuna modifica prevista
Nota: `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale` e' fuori scope perche' gia' verde

### Problema e Obiettivo

I test del gruppo colonna sinistra usano ancora assertion su stringhe
renderizzate. Questo li rende fragili e disallineati rispetto al contratto
reale dei metodi, che espongono `EsitoAzione` e eventi strutturati.

L'obiettivo della tranche 2 e' convertire i test legacy rimasti sul gruppo
colonna sinistra, senza toccare i metodi produttivi e senza uscire dal file di
test.

### File coinvolti

- `tests/test_giocatore_umano.py` — MODIFY nella fase implementativa successiva
- `docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md` — CREATE
- `docs/2 - projects/DESIGN_fix_test_colonna_sinistra_eventi.md` — CREATE
- `docs/3 - coding plans/PLAN_fix_test_colonna_sinistra_eventi_v1.md` — CREATE
- `docs/5 - todolist/TODO_fix_test_colonna_sinistra_eventi_v1.md` — CREATE
- `docs/todo.md` — UPDATE

### Approccio operativo

L'implementazione dovra' seguire due micro-fasi, una per la versione base e una
per la versione avanzata. Ogni micro-fase sostituira' le assertion su testo con
assertion su `ok`, `errore`, `evento` e sui campi dell'evento corretto.

### Fasi sequenziali

#### Micro-fase 1 — versione base

Target:

- `test_sposta_focus_colonna_sinistra_semplice_cartella_mancante`
- `test_sposta_focus_colonna_sinistra_semplice_prima_colonna`
- `test_sposta_focus_colonna_sinistra_semplice_movimento_normale`
- `test_sposta_focus_colonna_sinistra_semplice_auto_inizializzazione`
- `test_sposta_focus_colonna_sinistra_semplice_colonna_vuota`

Intervento:

- aggiornare i casi errore sui codici `CARTELLE_NESSUNA_ASSEGNATA` e `FOCUS_CARTELLA_NON_IMPOSTATO`
- aggiornare il caso limite minimo su `EventoNavigazioneColonna`
- aggiornare i casi movimento, auto-inizializzazione e colonna vuota su `numero_colonna_corrente` e `colonna_semplice`
- mantenere i controlli sullo stato interno `_indice_colonna_focus`

Commit previsto:

- `test(colonna): modernizza sinistra base su EsitoAzione`

Controllo post-fase:

- eseguire i 5 test del gruppo base
- confermare zero failure nel gruppo

#### Micro-fase 2 — versione avanzata

Target:

- `test_sposta_focus_colonna_sinistra_avanzata_cartella_mancante`
- `test_sposta_focus_colonna_sinistra_avanzata_prima_colonna`
- `test_sposta_focus_colonna_sinistra_avanzata_auto_inizializzazione`
- `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni` solo se al momento dell'implementazione risultasse ancora legacy

Non toccare:

- `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`

Intervento:

- aggiornare i casi errore sui codici `CARTELLE_NESSUNA_ASSEGNATA` e `FOCUS_CARTELLA_NON_IMPOSTATO`
- aggiornare il caso limite minimo su `EventoNavigazioneColonnaAvanzata`
- aggiornare il caso auto-inizializzazione confrontando il triplo di `get_dati_visualizzazione_colonna_avanzata(3)`
- se necessario, aggiornare il caso con segni su `numeri_segnati_colonna_ordinati` e `stato_colonna`

Commit previsto:

- `test(colonna): modernizza sinistra avanzata su evento strutturato`

Controllo post-fase:

- eseguire i test del gruppo avanzata
- rieseguire anche `movimento_normale` per confermare che resta verde e invariato

### Test Plan

Verifica per micro-fase:

- eseguire il sottoinsieme dei test interessati
- controllare assenza di regressioni nel blocco appena toccato

Verifica finale:

- eseguire l'intero file [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- confermare che tutti i test colonna sinistra passano
- confermare che il test avanzato gia' verde non e' stato alterato

### Rischi

- confondere `numero_colonna_corrente` 1-based con `_indice_colonna_focus` 0-based
- mantenere assertion residue su testo nei casi colonna vuota o con segni
- toccare per errore il test avanzato movimento normale gia' corretto
- assumere che tutti e 4 i test avanzati siano ancora legacy quando uno di essi puo' risultare gia' aggiornato nello stato corrente del file

### Dipendenze

- `docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md`
- `docs/2 - projects/DESIGN_fix_test_colonna_sinistra_eventi.md`

### Criteri di completamento

- test legacy del gruppo colonna sinistra aggiornati secondo il pattern strutturato
- `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale` intatto e verde
- file toccato in implementazione: solo `tests/test_giocatore_umano.py`
- suite ancora verde dopo la tranche

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso
