---
type: plan
feature: fix_test_destra_avanzata_rifinitura
agent: Agent-Plan
status: READY
version: v1.0
design_ref: docs/2 - projects/DESIGN_fix_test_destra_avanzata_rifinitura.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md
---

## Metadati

tipo: coding_plan
titolo: Piano rifinitura test colonna destra avanzata
data_creazione: 2026-03-29
agente: Agent-Plan
stato: pronto
feature: fix_test_destra_avanzata_rifinitura
versione_progetto: v1.0
design: docs/2 - projects/DESIGN_fix_test_destra_avanzata_rifinitura.md
report: docs/4 - reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md

## Executive Summary

Tipo intervento: rifinitura test
Priorita': P1
Branch: main
Versione di riferimento: v1.0
Scope: 3 test in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
Codice applicativo: nessuna modifica prevista
Nota: i 3 test target sono stati identificati dal report come incompleti o fragili
dopo la tranche 3 di modernizzazione. L'implementazione dovra' leggere il corpo
di ogni test prima di modificarlo.

## Problema e Obiettivo

Dopo la tranche 3 (modernizzazione destra avanzata), tre test del gruppo colonna
destra avanzata rimangono incompleti o non coprono in modo robusto il comportamento
atteso:

- manca una `assertIsNone` sul campo limite nel test di movimento normale avanzato destra
- il setup del test avanzato destra con segni non garantisce che i numeri segnati
  siano effettivamente presenti in colonna prima dell'azione
- il test simmetrico sinistra avanzata presenta lo stesso problema di setup

L'obiettivo e' completare le asserzioni mancanti e rafforzare i setup critici,
senza toccare il codice applicativo e senza modificare test non target.

## Approccio tecnico

L'implementazione segue due tipologie di intervento distinte.

### Tipologia A — aggiunta riga mancante

Applicabile a `test_sposta_focus_colonna_destra_avanzata_movimento_normale`.
Si tratta di aggiungere una singola `assertIsNone` nel punto corretto del test,
verificando che il campo `limite` dell'evento sia `None` nel caso di movimento
interno non a bordo.

### Tipologia B — rafforzamento setup

Applicabile a:

- `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni`
- `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni`

Si tratta di integrare il setup del test assicurandosi che i numeri segnati
appartengano effettivamente alla colonna oggetto dell'azione, rendendo
il test deterministico indipendentemente dalla sequenza di segni.

### Guardia operativa obbligatoria

Prima di modificare ogni singolo test, leggere il corpo nello stato reale del file.
Se un test risultasse gia' corretto, non modificarlo e registrare la verifica
nel TODO. Non alterare test adiacenti durante le operazioni di editing.

## File coinvolti

- `tests/test_giocatore_umano.py` — MODIFY nella fase implementativa
- `docs/4 - reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md` — CREATE
- `docs/2 - projects/DESIGN_fix_test_destra_avanzata_rifinitura.md` — CREATE
- `docs/3 - coding plans/PLAN_fix_test_destra_avanzata_rifinitura_v1.md` — CREATE
- `docs/5 - todolist/TODO_fix_test_destra_avanzata_rifinitura_v1.md` — CREATE (fase successiva)
- `docs/todo.md` — UPDATE (fase successiva)

## Fasi sequenziali

### Micro-fase 1 — aggiunta assertIsNone limite in movimento normale avanzato destra

Target:

- `test_sposta_focus_colonna_destra_avanzata_movimento_normale`

Intervento:

- leggere il corpo del test nello stato reale del file
- individuare il blocco di assertion sull'evento `EventoNavigazioneColonnaAvanzata`
- aggiungere `assertIsNone` sul campo `limite` immediatamente dopo le assertion
  gia' presenti sullo stesso evento, nel punto semanticamente corretto per il
  caso di movimento interno non a bordo colonna
- non modificare le assertion esistenti ne' le righe adiacenti

Commit previsto:

- `test(colonna): aggiungi assertIsNone limite in movimento normale avanzato destra`

Controllo post-fase:

- eseguire il solo test target
- verificare che il test raggiunga l'asserzione aggiunta senza errori
- verificare che nessun altro test del gruppo avanzata risulti modificato

### Micro-fase 2 — rafforzamento setup con segni destra avanzata

Target:

- `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni`

Intervento:

- leggere il corpo del test nello stato reale del file
- identificare la sezione di setup che costruisce i numeri segnati
- modificare il setup in modo che i numeri segnati appartengano
  con certezza alla colonna destra target dell'azione
- non modificare la sezione di esecuzione ne' le assertion esistenti

Commit previsto:

- `test(colonna): rafforza setup con segni in destra avanzata`

Controllo post-fase:

- eseguire il solo test target
- verificare esecuzione deterministica su piu' run consecutive
- verificare che nessun altro test con segni risulti modificato

### Micro-fase 3 — rafforzamento simmetrico sinistra avanzata

Target:

- `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni`

Intervento:

- leggere il corpo del test nello stato reale del file
- applicare lo stesso rafforzamento del setup adottato nella micro-fase 2
  per garantire che i numeri segnati appartengano alla colonna sinistra
  target dell'azione
- non modificare la sezione di esecuzione ne' le assertion esistenti

Commit previsto:

- `test(colonna): rafforza setup con segni in sinistra avanzata`

Controllo post-fase:

- eseguire il solo test target
- verificare esecuzione deterministica su piu' run consecutive
- eseguire l'intero [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py) e
  confermare suite verde

## Test Plan

Verifica per micro-fase:

- eseguire il sottoinsieme dei test interessati dopo ogni micro-fase
- confermare assenza di regressioni nel blocco appena toccato
- annotare quali test sono stati letti ma non modificati

Verifica finale:

- eseguire l'intero file [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
- confermare che i 3 test target eseguono tutte le asserzioni previste
- confermare che nessun test non target e' stato modificato
- confermare suite verde senza eccezioni o errori non attesi

## Dipendenze

- `docs/4 - reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md`
- `docs/2 - projects/DESIGN_fix_test_destra_avanzata_rifinitura.md`

## Rischi

- aggiungere `assertIsNone` nel punto sbagliato del test di movimento normale,
  portando a un falso positivo o a un errore non correlato al caso d'uso
- costruire un setup che non garantisce l'appartenenza dei numeri alla colonna,
  lasciando il test ancora non deterministico
- modificare accidentalmente un test adiacente durante l'editing del setup
  nei test con segni

## Criteri di completamento

- i 3 test target eseguono sempre tutte le asserzioni senza saltare blocchi
- l'intera suite [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py) e' verde
- nessun test non target risulta modificato rispetto allo stato pre-intervento
- l'unico file di implementazione toccato e' `tests/test_giocatore_umano.py`
