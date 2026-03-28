---
type: plan
feature: main_placeholder
agent: Agent-Plan
status: DRAFT
version: v0.9.2
design_ref: docs/2 - projects/DESIGN_main_placeholder.md
date: 2026-03-28
report_ref: docs/4 - reports/REPORT_ANALISI_main_placeholder_2026-03-28.md
---

## Metadati

tipo: coding_plan
titolo: Piano implementativo placeholder temporaneo per main.py
data_creazione: 2026-03-28
agente: Agent-Plan
stato: bozza
feature: main_placeholder
versione_progetto: v0.9.2
design: docs/2 - projects/DESIGN_main_placeholder.md
report: docs/4 - reports/REPORT_ANALISI_main_placeholder_2026-03-28.md

## Contenuto

### Obiettivo

Ripristinare l'avvio di `main.py` con un placeholder temporaneo chiaro,
compatibile con il logging esistente e privo di dipendenze verso moduli UI rimossi.

### Problema da risolvere

`main.py` importa `TerminalUI` da `bingo_game.ui.ui_terminale`, modulo non piu'
presente nel repository. L'errore blocca l'avvio dell'applicazione prima ancora
che il logger venga inizializzato e impedisce qualsiasi esecuzione di
`python main.py`.

### Approccio tecnico

Applicare una modifica puntuale al solo `main.py`, rimuovendo l'import rotto e
sostituendo l'avvio della TUI con un messaggio placeholder stampato a terminale.
Mantenere `argparse`, il flag `--debug` e il blocco di inizializzazione/chiusura
di `GameLogger` per preservare la struttura di bootstrap futura.

### File da modificare

- `main.py` — MODIFY
- `CHANGELOG.md` — MODIFY
- Nessun file di test da creare o aggiornare in questa implementazione

### Fasi di implementazione

#### Fase A — Rimuovere import rotto e codice TUI

- eliminare l'import di `TerminalUI`;
- rimuovere l'istanziazione della TUI e la chiamata a `avvia()`.

#### Fase B — Scrivere il nuovo corpo di `main()`

- mantenere `_parse_args()`;
- inizializzare `GameLogger`;
- stampare il messaggio placeholder;
- chiudere il logger nel `finally`.

#### Fase C — Aggiornare docstring e commenti

- allineare la docstring del file e di `main()` al nuovo ruolo temporaneo;
- mantenere i commenti essenziali e non verbosi.

#### Fase D — Verificare avvio manuale

- eseguire `python main.py`;
- verificare assenza di `ImportError` e chiusura corretta del processo.

#### Fase E — Aggiornare CHANGELOG.md

- aggiungere una voce `Fixed` che documenti la sostituzione dell'entry point
  rotto con un placeholder temporaneo.

### Dipendenze

- `docs/4 - reports/REPORT_ANALISI_main_placeholder_2026-03-28.md`
- `docs/2 - projects/DESIGN_main_placeholder.md`

### Rischi

- Inserire un messaggio troppo dettagliato, trasformando il placeholder in una
  pseudo-UI non voluta.
- Rimuovere il logger e perdere coerenza col bootstrap futuro.
- Aggiornare `main.py` senza allineare il changelog della release.

### Messaggio di commit

`fix(main): sostituisce entry point rotto con placeholder temporaneo`

### Criteri di completamento

- `python main.py` non solleva piu' `ImportError`.
- Il placeholder non importa moduli UI rimossi.
- Il flag `--debug` continua a essere accettato.
- `GameLogger.initialize()` e `GameLogger.shutdown()` restano nel flusso.
- `CHANGELOG.md` contiene la voce `Fixed` relativa a `main.py`.

### Project padre

- `docs/2 - projects/DESIGN_main_placeholder.md`

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso