---
type: plan
feature: allineamento_standard_tabellone
agent: Agent-Plan
status: DRAFT
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_allineamento_standard_tabellone_v1.0.0.md
date: 2026-03-31
report_ref: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo per l'allineamento standard di bingo_game/tabellone.py
data_creazione: 2026-03-31
agente: Agent-Plan
stato: draft
feature: allineamento_standard_tabellone
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_allineamento_standard_tabellone_v1.0.0.md
report: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md

## Contenuto

### Executive Summary

- Tipo intervento: allineamento formale e documentale
- Priorita': P1
- Branch: main
- Versione task: v1.0.0
- Obiettivo: correggere solo I-01, I-02, I-03, I-04 e I-05 in `bingo_game/tabellone.py`
- Vincolo di chiusura: `python -m unittest discover tests/unit` verde con zero failure e zero error

### Problema e obiettivo

`bingo_game/tabellone.py` presenta incoerenze di stile e standard gia' documentate nel report del 2026-03-31. Il piano operativo ha l'obiettivo di riallineare il file ai pattern di `bingo_game/partita.py` e `bingo_game/players/giocatore_base.py` senza modificare in alcun modo la logica di gioco, i flussi di estrazione o la gestione delle strutture dati.

### File coinvolti

- MODIFY: `bingo_game/tabellone.py`
- MODIFY: `docs/todo.md`
- CREATE: `docs/2 - projects/DESIGN_allineamento_standard_tabellone_v1.0.0.md`
- CREATE: `docs/3 - coding plans/PLAN_allineamento_standard_tabellone_v1.0.0.md`
- CREATE: `docs/5 - todolist/TODO_allineamento_standard_tabellone_v1.0.0.md`

Nota di fase:

- In questo ciclo documentale si producono design, plan e TODO e si aggiorna il coordinatore;
- la modifica a `bingo_game/tabellone.py` e' descritta ma non viene ancora eseguita.

### Fasi sequenziali

#### Passo 1 - Aggiunta `from __future__ import annotations` e import necessari (I-01)

Cosa si modifica:

- aggiungere `from __future__ import annotations` in testa a `bingo_game/tabellone.py`;
- aggiungere gli import di typing strettamente necessari, ad esempio `Any`.

File coinvolto:

- `bingo_game/tabellone.py`

Risultato atteso:

- il modulo usa la stessa base di tipizzazione dei file core di riferimento;
- le annotazioni moderne introdotte nei passi successivi risultano coerenti e leggibili.

#### Passo 2 - Annotazione degli attributi di istanza in `_inizializza_tabellone` (I-03)

Cosa si modifica:

- annotare `numeri_disponibili`, `numeri_estratti`, `ultimo_numero_estratto` e `storico_estrazioni` direttamente nel metodo `_inizializza_tabellone()` con i tipi definiti dal report.

File coinvolto:

- `bingo_game/tabellone.py`

Risultato atteso:

- lo stato interno della classe e' esplicito;
- il metodo mantiene esattamente le stesse assegnazioni e lo stesso ordine di inizializzazione.

#### Passo 3 - Aggiunta annotazioni di ritorno a tutti gli 11 metodi (I-02)

Cosa si modifica:

- completare tutte le firme prive di return type hint con i tipi stabiliti nel report.

File coinvolto:

- `bingo_game/tabellone.py`

Risultato atteso:

- tutte le firme del modulo risultano esplicite e consistenti;
- nessun valore di ritorno esistente viene modificato.

#### Passo 4 - Aggiunta module docstring e class docstring (I-04)

Cosa si modifica:

- introdurre una module docstring in apertura file;
- introdurre una class docstring immediatamente dopo `class Tabellone:`.

File coinvolto:

- `bingo_game/tabellone.py`

Risultato atteso:

- il file adotta il formato documentale gia' usato in `partita.py` e `giocatore_base.py`;
- scopo del modulo e responsabilita' della classe sono leggibili a colpo d'occhio.

#### Passo 5 - Aggiunta docstring Python ai 7 metodi che ne sono privi (I-05)

Cosa si modifica:

- aggiungere docstring a `_inizializza_tabellone`, `estrai_numero`, `reset_tabellone`, `numeri_terminati`, `gestione_errore_numeri_terminati`, `get_numeri_estratti`, `get_numeri_disponibili`.

File coinvolto:

- `bingo_game/tabellone.py`

Risultato atteso:

- i metodi oggi documentati solo con commenti inline diventano coerenti con il resto del file;
- la documentazione interna del modulo risulta uniforme.

#### Passo 6 - Esecuzione dell'intera suite per verifica invarianza

Cosa si modifica:

- nessun file sorgente;
- esecuzione della suite di regressione richiesta.

File coinvolti:

- intera cartella `tests/unit`

Risultato atteso:

- comando `python -m unittest discover tests/unit` completato con zero failure e zero error;
- il ciclo si considera chiuso solo con questa conferma di invarianza.

### Test Plan

- Test di regressione richiesto: `python -m unittest discover tests/unit`
- Criterio di successo: zero failure, zero error
- Motivo: validare che le modifiche formali a `tabellone.py` non alterino il comportamento del nucleo applicativo

### Stato avanzamento

- [x] Piano redatto
- [ ] Validazione umana
- [ ] Approvato per implementazione
- [ ] Implementazione avviata
- [ ] Suite `tests/unit` verde
