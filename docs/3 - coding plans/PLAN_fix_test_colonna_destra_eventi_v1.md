---
type: plan
feature: fix_test_colonna_destra_eventi
agent: Agent-Plan
status: DRAFT
version: v1.0
design_ref: docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md
---

## Metadati

tipo: coding_plan
titolo: Piano tranche 3 modernizzazione test colonna destra
data_creazione: 2026-03-29
agente: Agent-Plan
stato: bozza
feature: fix_test_colonna_destra_eventi
versione_progetto: v1.0
design: docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md
report: docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md

## Contenuto

### Executive Summary

Tipo intervento: modernizzazione test
Priorita': P1
Branch: main
Versione di riferimento: v1.0
Scope: test del gruppo colonna destra in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
Codice applicativo: nessuna modifica prevista
Nota: allo stato attuale tutti i test destra risultano legacy, ma l'implementazione dovra'
comunque leggere il corpo di ciascun test prima di modificarlo.

### Problema e Obiettivo

I test del gruppo colonna destra usano ancora assertion su stringhe
renderizzate. Questo li rende fragili e disallineati rispetto al contratto
reale dei metodi, che espongono `EsitoAzione` e eventi strutturati.

L'obiettivo della tranche 3 e' convertire i test legacy rimasti sul gruppo
colonna destra, senza toccare i metodi produttivi e senza uscire dal file di
test nella successiva implementazione.

### Approccio tecnico

L'implementazione dovra' seguire due micro-fasi, una per la versione base e una
per la versione avanzata. Ogni micro-fase sostituira' le assertion su testo con
assertion su `ok`, `errore`, `evento` e sui campi dell'evento corretto.

Guardia operativa obbligatoria:

- prima di modificare ogni singolo test, leggere il suo corpo nello stato reale del file
- se un test risultasse gia' strutturato, non modificarlo
- registrare nel TODO quali test sono stati effettivamente toccati e quali solo verificati

### File coinvolti

- `tests/test_giocatore_umano.py` — MODIFY nella fase implementativa successiva
- `docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md` — CREATE
- `docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md` — CREATE
- `docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md` — CREATE
- `docs/5 - todolist/TODO_fix_test_colonna_destra_eventi_v1.md` — CREATE
- `docs/todo.md` — UPDATE

### Fasi sequenziali

#### Micro-fase 1 — versione base

Target:

- `test_sposta_focus_colonna_destra_semplice_cartella_mancante`
- `test_sposta_focus_colonna_destra_semplice_ultima_colonna`
- `test_sposta_focus_colonna_destra_semplice_movimento_normale`
- `test_sposta_focus_colonna_destra_semplice_auto_inizializzazione`
- `test_sposta_focus_colonna_destra_semplice_colonna_vuota`
- `test_sposta_focus_colonna_destra_semplice_stato_interno`

Intervento:

- aggiornare i casi errore sui codici `CARTELLE_NESSUNA_ASSEGNATA` e `FOCUS_CARTELLA_NON_IMPOSTATO`
- aggiornare il caso limite massimo su `EventoNavigazioneColonna`
- aggiornare i casi movimento, auto-inizializzazione, colonna vuota e stato interno su
  `numero_colonna_corrente` e `colonna_semplice`
- mantenere i controlli sullo stato interno `_indice_colonna_focus`

Commit previsto:

- `test(colonna): modernizza destra base su EsitoAzione`

Controllo post-fase:

- eseguire i 6 test del gruppo base
- confermare zero failure nel gruppo

#### Micro-fase 2 — versione avanzata

Target:

- `test_sposta_focus_colonna_destra_avanzata_cartella_mancante`
- `test_sposta_focus_colonna_destra_avanzata_ultima_colonna`
- `test_sposta_focus_colonna_destra_avanzata_movimento_normale`
- `test_sposta_focus_colonna_destra_avanzata_auto_inizializzazione`
- `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni`

Intervento:

- aggiornare i casi errore sui codici `CARTELLE_NESSUNA_ASSEGNATA` e `FOCUS_CARTELLA_NON_IMPOSTATO`
- aggiornare il caso limite massimo su `EventoNavigazioneColonnaAvanzata`
- aggiornare il caso movimento normale confrontando il triplo di
  `get_dati_visualizzazione_colonna_avanzata(4)`
- aggiornare il caso auto-inizializzazione confrontando il triplo di
  `get_dati_visualizzazione_colonna_avanzata(5)`
- aggiornare il caso con segni su `numeri_segnati_colonna_ordinati` e `stato_colonna`

Commit previsto:

- `test(colonna): modernizza destra avanzata su evento strutturato`

Controllo post-fase:

- eseguire i 5 test del gruppo avanzata
- confermare che nessun test avanzato rimanga ancorato al renderer

### Test Plan

Verifica per micro-fase:

- eseguire il sottoinsieme dei test interessati
- controllare assenza di regressioni nel blocco appena toccato

Verifica finale:

- eseguire l'intero file [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- confermare che tutti i test colonna destra passano
- confermare che eventuali test gia' strutturati sono stati solo letti e non ritoccati

### Dipendenze

- `docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md`
- `docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md`

### Rischi

- confondere `numero_colonna_corrente` 1-based con `_indice_colonna_focus` 0-based
- sbagliare la colonna attesa nei casi di auto-inizializzazione base e avanzata
- mantenere assertion residue su testo nei casi colonna vuota o con segni
- modificare un test senza averne letto il corpo nello stato reale del file

### Project padre

- `docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md`

### Criteri di completamento

- test legacy del gruppo colonna destra aggiornati secondo il pattern strutturato
- nessuna modifica al codice produttivo
- eventuali test gia' strutturati lasciati invariati dopo verifica esplicita del corpo
- file toccato in implementazione: solo `tests/test_giocatore_umano.py`
- suite ancora verde dopo la tranche

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso