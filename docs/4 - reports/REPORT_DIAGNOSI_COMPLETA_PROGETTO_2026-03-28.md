---
tipo: report
titolo: Diagnosi completa del progetto — Tombola Stark
data: 2026-03-28
agente: Agent-Analyze
stato: definitivo
---

# Diagnosi completa del progetto — Tombola Stark
**Data**: 2026-03-28 | **Agente**: Agent-Analyze | **Versione analizzata**: branch `main`

---

## Sommario esecutivo

Il progetto ha un **nucleo di dominio stabile e ben testato** (366 test, 365 OK, 1 FAIL).
Tuttavia presenta **2 bug critici** che rompono funzionalità core a runtime — uno blocca
l'avvio dell'applicazione, l'altro rompe ogni vincita annunciata dal giocatore umano —
più diverse aree non ancora implementate legate all'assenza di un layer UI dopo la
rimozione della TUI (v0.10.0).

| Categoria | N. | Severità |
|---|---|---|
| Bug critici | 2 | CRITICO |
| Regressioni test | 1 | ALTO |
| Violazioni standard | 2 | MEDIO |
| Moduli orfani / da decidere | 4 | BASSO |
| Aree non implementate | 5 | PROGETTUALE |

---

## 1 — Stato test suite

Esecuzione: `py -3.10 -m unittest discover -s tests -q`

| Metrica | Valore |
|---|---|
| Test totali | 366 |
| Passati | 365 |
| Falliti | 1 |
| Errori di setup | 0 |
| Skipped | 0 |

Miglioramento rispetto all'ultimo report (`REPORT_DIAGNOSTICA_PROGETTO_2026-03-28.md`):
da 351 test / 32 errori a **366 test / 0 errori / 1 failure**.

---

## 2 — Bug critici

### BUG-1 · CRITICO — `main.py` non avviabile: TerminalUI rimossa

**Causa**: `main.py` importa `TerminalUI` da `bingo_game.ui.ui_terminale`, modulo
eliminato nel commit che ha rimosso la TUI.

```
ModuleNotFoundError: No module named 'bingo_game.ui.ui_terminale'
```

**Effetto**: l'applicazione non parte. Qualsiasi utente che esegue `python main.py`
ottiene immediatamente `ImportError`.

**File coinvolto**: `main.py`, riga 4

```python
from bingo_game.ui.ui_terminale import TerminalUI  # modulo rimosso
```

**Fix necessario**: sostituire il body di `main()` con un placeholder esplicito
(es. stampa a stdout dello stato "avvio non disponibile") oppure con il prototipo
della nuova UI, finché non viene implementato il nuovo layer di presentazione.

---

### BUG-2 · CRITICO — Factory methods orfani in `eventi_partita.py`

**Causa**: i `@classmethod` `tombola`, `vittoria_di_riga` e `ante_turno` sono
definiti **a livello di modulo** invece che dentro le classi `ReclamoVittoria`
ed `EventoReclamoVittoria`. Si tratta di un difetto di indentazione che ha
staccato i factory methods dai loro dataclass.

**Prova runtime**:

```python
>>> ReclamoVittoria.tombola(indice_cartella=0)
AttributeError: type object 'ReclamoVittoria' has no attribute 'tombola'
```

**Effetto**: `GiocatoreUmano.annuncia_vittoria()` (linea 2245, 2254, 2264) usa
`ReclamoVittoria.tombola(...)`, `ReclamoVittoria.vittoria_di_riga(...)` e
`EventoReclamoVittoria.ante_turno(...)`. **Ogni chiamata produce AttributeError**,
rendendo impossibile al giocatore umano annunciare qualsiasi vincita durante la partita.

I metodi orfani esistono solo come simboli di modulo non associati a nessuna classe:
```
bingo_game.events.eventi_partita.tombola          # @classmethod libero
bingo_game.events.eventi_partita.vittoria_di_riga  # @classmethod libero
bingo_game.events.eventi_partita.ante_turno        # @classmethod libero
```

**File coinvolti**:
- `bingo_game/events/eventi_partita.py` — indentazione mancante per 3 factory methods
- `bingo_game/players/giocatore_umano.py` — righe 2245, 2254, 2264

**Fix necessario**: rientrare i metodi `tombola`, `vittoria_di_riga` (dentro
`ReclamoVittoria`) e `ante_turno` (dentro `EventoReclamoVittoria`) con 4 spazi
per allinearli come metodi di classe.

**Nota sulla copertura test**: il fatto che la suite segni 0 errori non copre
questo bug perché nessun test corrente chiama `annuncia_vittoria()` con il
percorso tombola/riga. Il bug è **completamente scoperto dai test**.

---

## 3 — Regressione test

### FAIL-1 · ALTO — `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`

**File**: `tests/test_giocatore_umano.py`, riga 1153

**Traccia**:
```
AssertionError: 'vuota' not found in EsitoAzione(ok=True, errore=None,
evento=EventoNavigazioneColonnaAvanzata(id_giocatore=1, nome_giocatore='Mario',
direzione='sinistra', esito='mostra', ...))
```

**Causa**: Il test verifica `assertIn("Colonna 4:", risultato)` e
`assertIn("vuota", risultato)` dove `risultato` è un `EsitoAzione` (dataclass
strutturata), non una stringa formattata. Il test è stato scritto per un'API
che restituiva stringhe plain-text, mentre il metodo ora restituisce un evento
strutturato (`EventoNavigazioneColonnaAvanzata`).

**Percorso logico nel test**:
1. `assertIn("Colonna 4:", risultato)` — supera perché la colonna 4 della
   `cartella1` è vuota (nessun numero in colonna indice 4) quindi questo
   ramo `if` non è raggiunto in modo diretto
2. `numeri_colonna4 = cartella1.get_numeri_colonna(4)` — restituisce lista vuota
3. `else: assertIn("vuota", risultato)` — FALLISCE: il campo `esito` del
   dataclass è `'mostra'`, non `'vuota'`

**Fix necessario**: aggiornare il test per verificare l'EsitoAzione strutturata:

```python
# Verifica corretta per API attuale
self.assertTrue(risultato.ok)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonnaAvanzata)
self.assertEqual(risultato.evento.numero_colonna_corrente, 4)
# Se colonna vuota:
self.assertEqual(risultato.evento.colonna_semplice, ('-', '-', '-'))
```

---

## 4 — Violazioni standard di codifica

### VIOL-1 · MEDIO — `print()` in codice di produzione: `cartella.py` riga 350

**File**: `bingo_game/cartella.py`, metodo `_valida_cartella()`, riga 350

```python
print("Validazione completata: Cartella VALIDA! Tutte le 7 regole rispettate.")
```

**Effetto**: ogni volta che viene creata una Cartella, viene scritto su stdout,
violando la convenzione "zero print() in src/". Questo genera il rumore visibile
nei log dei test ("Validazione completata...").

**Gli altri `print()` in `cartella.py`** (righe 811–1072) si trovano **dentro
blocchi docstring** (sezioni `Examples:`) come codice illustrativo, non vengono
eseguiti.

**Fix**: sostituire la riga 350 con un'istruzione `logger.debug(...)` o
semplicemente rimuoverla (la validazione solleva `RuntimeError` se fallisce,
quindi il messaggio di successo è ridondante).

### VIOL-2 · MEDIO — Type hints mancanti in `tabellone.py`

`tabellone.py` è l'unico modulo del nucleo che non usa type hints sulle
firme dei metodi pubblici. Tutti gli altri moduli del progetto aderiscono
allo standard con `from __future__ import annotations`.

Metodi senza type hints: `estrai_numero()`, `reset_tabellone()`,
`numeri_terminati()`, `gestione_errore_numeri_terminati()`,
`get_conteggio_estratti()`.

**Fix**: aggiungere `from __future__ import annotations` e annotare le firme
dei metodi pubblici con i tipi appropriati.

---

## 5 — Moduli orfani (da decidere)

Questi moduli esistono, sono importabili e sintatticamente corretti, ma non
hanno consumer dopo la rimozione della TUI. Non causano errori: richiedono
una decisione architetturale.

| Modulo | Stato | Consumer pre-TUI | Consumer post-TUI |
|---|---|---|---|
| `bingo_game/ui/renderers/renderer_terminal.py` | Orfano | TUI rimossa | nessuno |
| `bingo_game/ui/locales/it.py` | Parzialmente orfano | TUI rimossa | solo renderer |
| `bingo_game/events/codici_loop.py` | Orfano | TUI rimossa | nessuno |
| `bingo_game/ui/tui/__init__.py` | Vuoto | `tests/flow/` (rimossi) | nessuno |

**Nota**: il `renderer_terminal.py` copre 8 test via `test_renderer_report_finale.py`
che continuano a essere verdi. Non è del tutto morto, ma non è integrato nel flusso
applicativo.

---

## 6 — Aree non ancora implementate (`da implementare`)

Queste funzionalità sono dichiarate come obiettivo nel codice/documentazione
ma non hanno ancora un'implementazione completa.

### 6.1 — Layer UI (assenza totale post-TUI)

**Priorità**: CRITICA

Il progetto ha rimosso la TUI senza un rimpiazzo. `main.py` è un entry point
rotto. Non esiste nessuna interfaccia fruibile dall'utente finale.

Il `project-profile.md` dichiara wxPython come target UI, ma non esiste nemmeno
un file di scaffolding nella directory `bingo_game/ui/`.

**Punti concreti mancanti**:
- `main.py`: entry point funzionante
- `bingo_game/ui/wx/` (o equivalente): nessun file
- Nessun form wxPython per configurare la partita
- Nessun pannello per mostrare numeri estratti, cartelle, premi
- Nessuna integrazione con screen reader (NVDA priority)

### 6.2 — `Partita.get_stato_giocatori()`

**Priorità**: MEDIA

La docstring di `partita.py` (riga ~120) la lista come da implementare:

> `get_stato_giocatori()`: ritorna una rappresentazione sintetica dello
> stato dei giocatori (es. nome, id, numero di cartelle, presenza di tombola).

Il metodo `get_stato_completo()` esiste ed è completo; `get_stato_giocatori()`
come metodo separato non è stato mai aggiunto.

### 6.3 — Annuncio vincite (rotto da BUG-2)

**Priorità**: CRITICA (dipende da BUG-2)

`GiocatoreUmano.annuncia_vittoria()` è implementata a livello di codice, ma
il percorso runtime è completamente bloccato dal BUG-2 (factory methods fuori
dalla classe). Di fatto questa feature non è mai stata verificabile.

### 6.4 — Ciclo di gioco interattivo completo

**Priorità**: ALTA

Il controller (`ComandiSistema`, `ComandiGiocatoreUmano`) è implementato e
testato. Ma il ciclo che:
1. crea la partita
2. avvia la partita
3. gestisce il turno interattivo (estrazione + annuncio + verifica vittorie)
4. termina la partita

...non ha un entry point funzionante che un utente possa utilizzare.
Esiste in `tests/unit/test_game_controller_loop.py` come scenario test, non
come funzionalità esponibile.

### 6.5 — Pipeline CI configurata

**Priorità**: BASSA

Esiste `scripts/ci-local-validate.py` e `scripts/validate_gates.py`, ma non
esiste nessun file di configurazione per GitHub Actions (`.github/workflows/`
è assente o vuota). La CI è solo locale.

---

## 7 — Coerenza architetturale

### Layer boundaries

| Layer | Conformità | Note |
|---|---|---|
| Dominio | ✅ RISPETTATO | Nessuna dipendenza da controller o UI |
| Controller | ✅ RISPETTATO | Nessun print(), nessuna logica di business |
| Infrastruttura (Logging) | ✅ RISPETTATO | Non accessibile dal dominio |
| Presentazione | ⚠️ ROTTO | main.py rotto, nessuna UI disponibile |

### Sistema di eccezioni

La gerarchia eccezioni (`bingo_game/exceptions/`) è coerente e ben strutturata.
Ogni modulo ha le proprie eccezioni specifiche. L'unica anomalia:

- `tabellone.py` usa `raise ValueError(...)` nel metodo `gestione_errore_numeri_terminati()`
  invece di una `TabelloneException` specifica. Funziona perché `Partita` la intercetta
  e la riconverte in `PartitaNumeriEsauritiException`, ma è incoerente con il pattern
  del progetto.

### Sistema eventi

Il sistema `EsitoAzione` + eventi strutturati (`EventoNavigazioneColonnaAvanzata`, ecc.)
è ben progettato. Un problema formale: `EsitoAzione.__str__()` non gestisce il caso
`ok=True` con `evento != None`, lasciando che venga visualizzato il `__repr__` automatico
del dataclass anziché un messaggio leggibile.

---

## 8 — Riepilogo priorità di intervento

### P0 — Blocca runtime (fix immediato)

| ID | Azione | File |
|---|---|---|
| BUG-2 | Rientrare i factory methods dentro le classi in `eventi_partita.py` | `bingo_game/events/eventi_partita.py` |
| BUG-1 | Sostituire l'import di `TerminalUI` in `main.py` con placeholder funzionante | `main.py` |

### P1 — Qualità test e standard

| ID | Azione | File |
|---|---|---|
| FAIL-1 | Aggiornare il test per la nuova API EsitoAzione strutturata | `tests/test_giocatore_umano.py` |
| VIOL-1 | Rimuovere `print()` da `_valida_cartella()` in cartella.py | `bingo_game/cartella.py` riga 350 |
| VIOL-2 | Aggiungere type hints ai metodi pubblici di `tabellone.py` | `bingo_game/tabellone.py` |

### P2 — Documentazione (già in piano)

- Aggiornare `docs/API.md` (sezioni TUI obsolete)
- Aggiornare `docs/ARCHITECTURE.md` (file TUI rimossi)
- Aggiornare `README.md` (comandi TUI)
- Aggiornare `CHANGELOG.md` (voce `Removed` per TUI)

### P3 — Decisioni architetturali (futura UI)

- Definire la roadmap per la nuova UI (wxPython)
- Decidere il destino di `renderer_terminal.py`, `codici_loop.py`, `locales/it.py`
- Scaffolding iniziale della directory `bingo_game/ui/wx/`

---

## 9 — Dipendenze circuitali e accoppiamento

Nessuna dipendenza circolare rilevata. Il modulo `__init__.py` di ogni package
espone solo i simboli necessari al livello superiore. Il grafo delle dipendenze
segue il flusso unidirezionale `Domain ← Controller ← UI`.

---

## 10 — Conclusione

Il **nucleo di gioco** (Tabellone, Cartella, Partita, Players, GameController,
sistema eventi, eccezioni, validazioni) è **solido, testato e architetturalmente
coerente**. Con 365/366 test verdi, la regressione residua è isolata e facilmente
correggibile.

I **due bug critici** (BUG-1 e BUG-2) impediscono l'uso pratico del software:
l'app non si avvia e le vincite non possono essere annunciate. Entrambi richiedono
fix localizzati e non invasivi (rientro di codice per BUG-2, sostituzione import
per BUG-1).

Le **5 aree non implementate** sono tutte concentrate nel layer di presentazione.
Prima del layer UI nessun'altra parte del progetto risulta incompleta.
