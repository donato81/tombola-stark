---
type: design
feature: main_placeholder
agent: Agent-Design
status: DRAFT
version: v0.9.2
date: 2026-03-28
report_ref: docs/4 - reports/REPORT_ANALISI_main_placeholder_2026-03-28.md
---

## Metadati

tipo: design
titolo: Design placeholder temporaneo per main.py
data_creazione: 2026-03-28
agente: Agent-Design
stato: bozza
feature: main_placeholder
versione_progetto: v0.9.2
report: docs/4 - reports/REPORT_ANALISI_main_placeholder_2026-03-28.md

## Contenuto

### Obiettivo

Definire una sostituzione minima, onesta e reversibile dell'entry point rotto
`main.py`, ripristinando l'avvio dell'applicazione senza dipendere da moduli UI
rimos­si e senza introdurre una nuova interfaccia definitiva.

### Contesto

Il file `main.py` importa `TerminalUI` da un modulo eliminato con la rimozione
della TUI. Di conseguenza il programma fallisce all'import time. Il progetto ha
ancora un motore di gioco e un sistema di logging validi, ma non dispone piu'
di una UI eseguibile. Serve quindi uno stub temporaneo che renda l'applicazione
avviabile e chiarisca il suo stato di transizione.

### Componenti coinvolti

| Componente | Ruolo |
|---|---|
| `main.py` | unico file sorgente da modificare nella fase implementativa |
| `bingo_game/logging/game_logger.py` | bootstrap e chiusura del logging |
| `CHANGELOG.md` | voce `Fixed` da aggiungere nella fase implementativa |

### Approccio scelto

Stub con messaggio informativo a terminale, nessuna dipendenza UI.

Il nuovo `main.py` deve:

- mantenere solo import standard e import ancora validi nel repository;
- eliminare l'import di `TerminalUI`;
- inizializzare il logger come oggi;
- stampare un messaggio chiaro e lineare per l'utente;
- chiudere sempre il logger;
- restare facilmente sostituibile da una futura GUI wxPython.

### Struttura del nuovo main.py

Import da mantenere:

- `import argparse`
- `from bingo_game.logging import GameLogger`

Import da rimuovere:

- `from bingo_game.ui.ui_terminale import TerminalUI`

Schema logico:

```text
def _parse_args():
    parser = argparse.ArgumentParser(...)
    parser.add_argument("--debug", ...)
    return parser.parse_args()

def _build_placeholder_message() -> str:
    return <messaggio statico>

def main() -> None:
    args = _parse_args()
    GameLogger.initialize(debug_mode=args.debug)
    try:
        print(_build_placeholder_message())
    finally:
        GameLogger.shutdown()
```

### Testo esatto del messaggio da mostrare all'utente

```text
Tombola Stark: interfaccia utente non ancora disponibile.
Il progetto e' in transizione verso una nuova UI.
Il motore applicativo e il logging restano disponibili per lo sviluppo.
```

Il testo e' volutamente breve, lineare e privo di decorazioni non necessarie,
cosi' da risultare leggibile anche con screen reader.

### Gestione del logger

`GameLogger` va mantenuto.

Motivazione:

- e' indipendente dall'interfaccia;
- il placeholder rappresenta comunque l'avvio dell'applicazione;
- mantenere il bootstrap del logger evita un futuro rework quando arrivera'
  la nuova UI;
- il flag `--debug` resta immediatamente utile per il bootstrap in sviluppo.

### Gestione del flag --debug

`argparse` va mantenuto.

Motivazione:

- il parsing esiste gia' ed e' semplice;
- non introduce dipendenze extra;
- consente di attivare il logging DEBUG anche durante la fase di transizione;
- evita di cambiare l'interfaccia CLI pubblica del file in modo non necessario.

### Compatibilita' futura

Quando sara' disponibile la nuova interfaccia, `main.py` dovra' essere
sostituito intervenendo solo in un punto: il corpo di `main()` dopo
l'inizializzazione del logger. `_parse_args()` potra' essere mantenuta o estesa,
e il blocco `try/finally` restera' valido per proteggere sempre la chiusura del
logging.

### Vincoli

- Nessun import da moduli rimossi.
- Nessuna UI fittizia.
- Nessuna logica di gioco nel placeholder.
- Messaggio accessibile e sostituibile.

### Coding plans correlati

- `docs/3 - coding plans/PLAN_main_placeholder.md`

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Approvato
- [ ] Archiviato