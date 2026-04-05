## Metadati

tipo: report
titolo: Analisi placeholder temporaneo per main.py
data_creazione: 2026-03-28
agente: Agent-Analyze
stato: bozza

## Contenuto

### Trigger

Richiesta di pianificazione per ripristinare l'avviabilita' di main.py con un
placeholder temporaneo compatibile con lo stato post-rimozione TUI del progetto
Tombola Stark v0.9.2, senza introdurre una nuova interfaccia definitiva.

### Sommario esecutivo

Il file main.py e' attualmente non avviabile per un import diretto verso un
modulo rimosso: `bingo_game.ui.ui_terminale`. Il problema si manifesta prima
ancora dell'ingresso in `main()`, quindi impedisce qualsiasi bootstrap
dell'applicazione.

L'intervento corretto e' un placeholder minimale e onesto: nessuna UI nuova,
nessuna simulazione del game loop, mantenimento del parsing del flag `--debug`
e del ciclo `GameLogger.initialize()` / `GameLogger.shutdown()`, con un
messaggio esplicito che informi l'utente che l'interfaccia e' in transizione.

Non risultano test che importino o validino direttamente `main.py`, quindi il
placeholder ha impatto nullo sulla suite attuale salvo la possibilita' di
ripristinare l'import di `main` e l'esecuzione di `python main.py` senza errori.

### Dettaglio osservazioni

#### 1. Problema attuale

- File coinvolto: `main.py`
- Riga esatta: 4
- Import rotto:

```python
from bingo_game.ui.ui_terminale import TerminalUI
```

- Errore atteso all'avvio:

```text
ModuleNotFoundError: No module named 'bingo_game.ui.ui_terminale'
```

La directory `bingo_game/ui/` esiste ancora ma non contiene alcun modulo
`ui_terminale.py`. Sono presenti soltanto sottopacchetti residuali
(`locales/`, `renderers/`, `tui/`) che non costituiscono una UI eseguibile.

#### 2. Vincoli dell'intervento

- Il placeholder non deve importare moduli TUI rimossi o moduli UI non ancora
  definiti.
- Il placeholder non deve fingere l'esistenza della futura UI wxPython.
- Il placeholder dovrebbe restare sostituibile con una futura GUI senza dover
  rifattorizzare il bootstrap del logger o il parsing base degli argomenti.
- Il mantenimento del flag `--debug` e' utile: consente di continuare a
  inizializzare il logger in modalita' dettagliata anche durante questa fase di
  transizione.
- Il mantenimento del ciclo `GameLogger.initialize()` / `GameLogger.shutdown()`
  ha senso perche' il logger e' indipendente dalla UI ed e' gia' progettato
  per essere inizializzato all'avvio dell'applicazione.

#### 3. Comportamento atteso del placeholder

All'esecuzione di `python main.py`, il programma dovrebbe:

1. leggere il flag `--debug` se presente;
2. inizializzare il `GameLogger`;
3. mostrare un messaggio testuale chiaro e lineare, adatto a console e screen reader;
4. terminare con codice di uscita 0, senza eccezioni;
5. chiudere sempre il logger nel blocco `finally`.

Messaggio atteso, come contenuto funzionale:

- applicazione disponibile come motore/logging;
- interfaccia utente non ancora disponibile;
- stato di transizione verso una futura UI.

#### 4. Impatto sulla suite di test

La ricerca nei test non ha trovato riferimenti diretti a `main.py`, `import main`
o `from main import ...`. Non esiste un `tests/test_main.py`.

Conclusione:

- nessun test attuale va aggiornato solo per introdurre il placeholder;
- la validazione minima richiesta resta manuale: `python main.py` non deve
  lanciare `ImportError`.

#### 5. Informazioni rilevanti non previste ma utili

- `.github/project-profile.md` risulta disallineato rispetto alla release
  corrente: frontmatter e sezione identita' riportano ancora la versione `0.9.0`.
  E' un'informazione di contesto utile ma non modificabile in questo task,
  perche' il file ricade nell'area framework protetta.
- Il logger di progetto e' autonomo rispetto alla UI e scrive su
  `logs/tombola_stark.log` con session marker di apertura/chiusura, quindi puo'
  essere mantenuto integralmente anche con un entry point placeholder.

### Raccomandazioni

- Sostituire l'import di `TerminalUI` con nessun import UI.
- Conservare `argparse` e il flag `--debug`.
- Conservare `GameLogger.initialize()` e `GameLogger.shutdown()`.
- Stampare un solo messaggio informativo, corto e sostituibile in futuro.
- Aggiornare `CHANGELOG.md` in una fase implementativa successiva con una voce
  `Fixed` dedicata a `main.py`.

### File analizzati

- `main.py`
- `bingo_game/logging/game_logger.py`
- `docs/todo.md`
- `.github/project-profile.md`
- `tests/**/*.py` (ricerca riferimenti a `main.py`)

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Condiviso