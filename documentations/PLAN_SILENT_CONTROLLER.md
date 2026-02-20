# 📋 Piano Operativo - Silent Controller v0.8.0

> **FASE: PLAN**  
> Documento operativo sequenziale per l'implementazione del Design "Silent Controller"  
> Riferimento design: `documentations/DESIGN_SILENT_CONTROLLER.md` (DESIGN FREEZE ✅ 2026-02-20)

---

## 📌 Metadata

- **Data Creazione**: 2026-02-20
- **Stato**: PLAN ATTIVO 🟡
- **Versione Target**: v0.8.0
- **Autore**: AI Assistant + donato81
- **Design di Riferimento**: `DESIGN_SILENT_CONTROLLER.md`
- **PR Target**: `feature/silent-controller-v0.8.0`

---

## ⚠️ Regola Fondamentale di Sequenza

Ogni fase deve essere **completata e committata** prima di iniziare la successiva.  
Il motivo è architetturale: le fasi successive dipendono dai file creati nelle fasi precedenti.

```
Fase 1 (infrastruttura) → Fase 2 (controller) → Fase 3 (TUI) → Fase 4 (test + docs)
         ↑                        ↑                    ↑
   codici_controller.py     import già esistente    MESSAGGI_CONTROLLER
   e it.py già pronti       sub-logger già attivi   già disponibile
```

**Non saltare passi.** Non avviare la Fase 2 se i file della Fase 1 non sono stati committati.

---

## 📂 File Coinvolti per Fase

| Fase | File Modificati / Creati |
|---|---|
| Fase 1 | `bingo_game/events/codici_controller.py` *(nuovo)*, `bingo_game/ui/locales/it.py` *(modifica)*, `bingo_game/ui/locales/__init__.py` *(modifica)* |
| Fase 2 | `bingo_game/game_controller.py` *(modifica)* |
| Fase 3 | `bingo_game/ui/ui_terminale.py` *(modifica)* |
| Fase 4 | `tests/test_silent_controller.py` *(nuovo)*, `documentations/API.md` *(modifica)*, `documentations/ARCHITECTURE.md` *(modifica)*, `documentations/CHANGELOG.md` *(modifica)* |

---

## 📊 Riepilogo Commit

| # | Fase | Messaggio Commit |
|---|---|---|
| C1 | 1 | `feat(events): add codici_controller.py — 4 CTRL_* string constants` |
| C2 | 1 | `feat(locales): add MESSAGGI_CONTROLLER to it.py with typed import` |
| C3 | 1 | `feat(locales): export MESSAGGI_CONTROLLER from locales __init__` |
| C4 | 2 | `refactor(controller): replace print() Gruppo A with _log_safe DEBUG` |
| C5 | 2 | `refactor(controller): replace print() Gruppo B+C — remove output, log WARNING/ERROR` |
| C6 | 2 | `refactor(controller): replace print() Gruppo D with _log_safe ERROR` |
| C7 | 3 | `feat(ui): add MESSAGGI_CONTROLLER guards in ui_terminale.py` |
| C8 | 4 | `test: add capsys non-regression tests for silent controller` |
| C9 | 4 | `docs: update API.md, ARCHITECTURE.md, CHANGELOG.md for v0.8.0` |

---

## ✅ Checklist Globale di Avanzamento

```
Fase 1 — Infrastruttura e Localizzazione
  [ ] C1 — codici_controller.py creato
  [ ] C2 — MESSAGGI_CONTROLLER aggiunto a it.py
  [ ] C3 — __init__.py locales aggiornato

Fase 2 — Refactoring Core (game_controller.py)
  [ ] C4 — Gruppo A sostituito (11 print → _log_safe DEBUG)
  [ ] C5 — Gruppo B+C sostituito (12 print rimossi)
  [ ] C6 — Gruppo D sostituito (5 print → _log_safe WARNING/ERROR)
  [ ] Verifica meccanica: grep -n "print(" game_controller.py → zero

Fase 3 — Adeguamento Interfaccia (ui_terminale.py)
  [ ] C7 — guardie MESSAGGI_CONTROLLER aggiunte in TUI

Fase 4 — Testing e Documentazione
  [ ] C8 — test capsys scritti e verdi
  [ ] C9 — API.md, ARCHITECTURE.md, CHANGELOG.md aggiornati
  [ ] PR aperta e review completata
```

---

## 🛠️ Fase 1 — Infrastruttura e Localizzazione

> **Prerequisiti**: nessuno.  
> **Obiettivo**: creare i mattoni su cui le fasi successive si appoggiano.  
> La Fase 2 non può iniziare finché questa fase non è completamente committata.

---

### Passo 1.1 — Creare `bingo_game/events/codici_controller.py`

**Commit**: `C1`  
**Messaggio**: `feat(events): add codici_controller.py — 4 CTRL_* string constants`  
**File creato**: `bingo_game/events/codici_controller.py`

**Posizione nel progetto**:
```
bingo_game/
  events/
    codici_controller.py   ← NUOVO
    codici_configurazione.py
    codici_errori.py
    codici_eventi.py
    __init__.py
```

**Contenuto del file**:
```python
"""
bingo_game/events/codici_controller.py

Costanti stringa per i codici evento del controller.
Segue il pattern di codici_configurazione.py, codici_errori.py, codici_eventi.py.

Questi codici sono usati come chiavi del dizionario MESSAGGI_CONTROLLER in it.py.
Il controller NON importa questo file: le costanti servono solo alla TUI e a it.py.
"""

# ---------------------------------------------------------------------------
# Codici evento: avvio partita
# ---------------------------------------------------------------------------

CTRL_AVVIO_FALLITO_GENERICO: str = "ctrl.avvio_fallito_generico"
"""
Qualsiasi fallimento di avvia_partita_sicura, indipendentemente dalla causa.
Riferimento design: Scenario 2, Gruppo C.
"""

# ---------------------------------------------------------------------------
# Codici evento: turno di gioco
# ---------------------------------------------------------------------------

CTRL_TURNO_NON_IN_CORSO: str = "ctrl.turno_non_in_corso"
"""
Turno richiesto con partita non nello stato 'in_corso'.
Riferimento design: Scenario 4, Gruppo C.
"""

CTRL_NUMERI_ESAURITI: str = "ctrl.numeri_esauriti"
"""
PartitaNumeriEsauritiException intercettata in esegui_turno_sicuro.
Riferimento design: Scenario 5, Gruppo C.
"""

CTRL_TURNO_FALLITO_GENERICO: str = "ctrl.turno_fallito_generico"
"""
Qualsiasi altro fallimento di esegui_turno_sicuro non altrimenti classificato.
Riferimento design: Gruppo C.
"""
```

**Verifica post-commit**:
```bash
python -c "from bingo_game.events.codici_controller import CTRL_AVVIO_FALLITO_GENERICO; print(CTRL_AVVIO_FALLITO_GENERICO)"
# Atteso: ctrl.avvio_fallito_generico
```

**Criterio di done C1**: il file esiste, è importabile, le 4 costanti hanno i valori corretti.

---

### Passo 1.2 — Aggiornare `bingo_game/ui/locales/it.py`

**Commit**: `C2`  
**Messaggio**: `feat(locales): add MESSAGGI_CONTROLLER to it.py with typed import`  
**File modificato**: `bingo_game/ui/locales/it.py`

**Operazione**:

1. **Aggiungere in cima al file**, dopo gli import già esistenti:

```python
from bingo_game.events.codici_controller import (
    CTRL_AVVIO_FALLITO_GENERICO,
    CTRL_TURNO_NON_IN_CORSO,
    CTRL_NUMERI_ESAURITI,
    CTRL_TURNO_FALLITO_GENERICO,
)
```

2. **Aggiungere in fondo al file**, dopo tutti i dizionari già esistenti:

```python
# ---------------------------------------------------------------------------
# Messaggi del controller (v0.8.0 — Silent Controller)
# Letti dalla TUI per rispondere ai valori di ritorno del controller.
# Il controller NON legge mai questo dizionario.
# ---------------------------------------------------------------------------

MESSAGGI_CONTROLLER: dict[str, str] = {
    CTRL_AVVIO_FALLITO_GENERICO: (
        "Impossibile avviare la partita. "
        "Riprova o riavvia l'applicazione."
    ),
    CTRL_TURNO_NON_IN_CORSO: (
        "Impossibile eseguire il turno: "
        "la partita non \u00e8 in corso."
    ),
    CTRL_NUMERI_ESAURITI: (
        "Tutti i 90 numeri sono stati estratti. "
        "La partita termina senza vincitore."
    ),
    CTRL_TURNO_FALLITO_GENERICO: (
        "Errore durante l'esecuzione del turno. "
        "La partita potrebbe essere terminata."
    ),
}
```

**Perché le costanti come chiavi**: un refactoring del valore di `CTRL_AVVIO_FALLITO_GENERICO` in `codici_controller.py` si propaga automaticamente qui, eliminando il rischio di disallineamento silenzioso tra i due file.

**Verifica post-commit**:
```bash
python -c "
from bingo_game.ui.locales.it import MESSAGGI_CONTROLLER
from bingo_game.events.codici_controller import CTRL_AVVIO_FALLITO_GENERICO
assert CTRL_AVVIO_FALLITO_GENERICO in MESSAGGI_CONTROLLER
print('OK —', len(MESSAGGI_CONTROLLER), 'chiavi')
"
# Atteso: OK — 4 chiavi
```

**Criterio di done C2**: `it.py` importa le costanti, `MESSAGGI_CONTROLLER` contiene esattamente 4 chiavi con i testi corretti.

---

### Passo 1.3 — Esportare da `bingo_game/ui/locales/__init__.py`

**Commit**: `C3`  
**Messaggio**: `feat(locales): export MESSAGGI_CONTROLLER from locales __init__`  
**File modificato**: `bingo_game/ui/locales/__init__.py`

**Operazione**: aggiungere `MESSAGGI_CONTROLLER` alla lista degli export esistenti nel `__init__.py`, coerentemente con il pattern degli altri dizionari già esportati (es. `MESSAGGI_CONFIGURAZIONE`, `MESSAGGI_ERRORI`).

```python
# Aggiungere alla sezione import/export esistente:
from bingo_game.ui.locales.it import MESSAGGI_CONTROLLER
```

**Verifica post-commit**:
```bash
python -c "
from bingo_game.ui.locales import MESSAGGI_CONTROLLER
print('Export OK —', type(MESSAGGI_CONTROLLER))
"
# Atteso: Export OK — <class 'dict'>
```

**Criterio di done C3**: `MESSAGGI_CONTROLLER` è importabile direttamente da `bingo_game.ui.locales` senza path completo.

> ✅ **Fase 1 completata.** Verificare che tutti e 3 i commit siano su `main` (o sul branch feature) prima di procedere.

---

## ⚙️ Fase 2 — Refactoring Core (`game_controller.py`)

> **Prerequisiti**: Fase 1 completamente committata.  
> **Obiettivo**: eliminare tutti i `print()` dal controller sostituendoli con `_log_safe()`.  
> I sub-logger (`_logger_game`, `_logger_prizes`, `_logger_system`, `_logger_errors`) e `_log_safe()` sono già presenti nel file: nessun nuovo import è necessario.

**Check preliminare — eseguire prima di modificare**:
```bash
grep -n "print(" bingo_game/game_controller.py
```
Annotare il numero di occorrenze trovate (atteso: ~22). Questo è il baseline da azzerare.

Secondo check:
```bash
python -m pytest tests/ -x -q 2>&1 | tail -5
```
Tutti i test esistenti devono essere verdi **prima** di iniziare il refactoring.

---

### Passo 2.1 — Sostituire Gruppo A (scaffolding di costruzione)

**Commit**: `C4`  
**Messaggio**: `refactor(controller): replace print() Gruppo A with _log_safe DEBUG`  
**File modificato**: `bingo_game/game_controller.py`

**Descrizione**: sostituire gli 11 `print()` di tipo scaffolding con chiamate `_log_safe(..., logging.DEBUG, logger=_logger_game)`. Questi `print()` descrivono i passaggi interni di costruzione della partita.

**Tabella di sostituzione completa (Gruppo A)**:

| `print()` da rimuovere | `_log_safe()` sostitutivo |
|---|---|
| `print("Creazione tabellone standard...")` | `_log_safe("[GAME] crea_partita_standard: tabellone creato.", logging.DEBUG, logger=_logger_game)` |
| `print(f"Creazione giocatore umano '{nome}' con {n} cartelle...")` | `_log_safe(f"[GAME] crea_partita_standard: giocatore umano creato. nome='{nome}', cartelle={n}.", logging.DEBUG, logger=_logger_game)` |
| `print(f"Creazione {n} bot automatici...")` | `_log_safe(f"[GAME] crea_partita_standard: {n} bot automatici richiesti.", logging.DEBUG, logger=_logger_game)` |
| `print(f"Partita composta da {n} giocatori totali")` | `_log_safe(f"[GAME] crea_partita_standard: lista giocatori composta. tot={n}.", logging.DEBUG, logger=_logger_game)` |
| `print("Inizializzazione oggetto Partita...")` | `_log_safe("[GAME] crea_partita_standard: oggetto Partita inizializzato.", logging.DEBUG, logger=_logger_game)` |
| `print("\u2705 Partita standard creata con successo!")` | `_log_safe("[GAME] crea_partita_standard: completato con successo.", logging.DEBUG, logger=_logger_game)` |
| `print(f"\ud83d\udcf8 Stato partita '{stato}' \u2014 {n} estratti, {m} giocatori")` | `_log_safe(f"[GAME] ottieni_stato_sintetico: stato='{stato}', estratti={n}, giocatori={m}.", logging.DEBUG, logger=_logger_game)` |
| `print(f"\ud83d\udd0d Controllo tombola: {n} giocatori, stato '{stato}'")` | `_log_safe(f"[GAME] ha_partita_tombola: verifica su {n} giocatori, stato='{stato}'.", logging.DEBUG, logger=_logger_game)` |
| `print("\u23f3 Nessuna tombola, gioco continua...")` | `_log_safe("[GAME] ha_partita_tombola: esito=False.", logging.DEBUG, logger=_logger_game)` |
| `print(f"\ud83d\udd0d Controllo fine partita: stato '{stato}'")` | `_log_safe(f"[GAME] partita_terminata: stato='{stato}'.", logging.DEBUG, logger=_logger_game)` |
| `print("\u25b6\ufe0f Partita in corso - continua il loop")` | `_log_safe("[GAME] partita_terminata: esito=False.", logging.DEBUG, logger=_logger_game)` |

**Verifica post-commit**:
```bash
grep -n "print(" bingo_game/game_controller.py
# Atteso: solo print() dei Gruppi B, C, D ancora presenti (~11 righe)
python -m pytest tests/ -x -q
# Atteso: tutti verdi
```

---

### Passo 2.2 — Sostituire Gruppo B+C (output di stato e messaggi di errore)

**Commit**: `C5`  
**Messaggio**: `refactor(controller): replace print() Gruppo B+C — remove output, log WARNING/ERROR`  
**File modificato**: `bingo_game/game_controller.py`

**Descrizione**:
- **Gruppo B** (5 print): rimozione secca. Il valore di ritorno già trasporta tutta l'informazione. La TUI riceverà il valore e stamperà il testo appropriato da `it.py`.
- **Gruppo C** (7 print): rimozione + aggiunta `_log_safe` a livello `WARNING` via `_logger_errors` per preservare la diagnostica.

**Tabella Gruppo B — rimozione secca**:

| `print()` da rimuovere | Motivazione |
|---|---|
| `print("\u2705 Partita avviata con successo!")` | TUI legge `True` da `avvia_partita_sicura` |
| `print(f"\u2705 Turno #{n}: {numero}")` | TUI legge `numero_estratto` dal dict del turno |
| `print(f"\ud83c\udf89 {n} nuovi premi!")` | TUI legge `premi_nuovi` dal dict |
| `print("\ud83c\udf89 TOMBOLA RILEVATA nella partita!")` | TUI legge `tombola_rilevata=True` dal dict |
| `print("\ud83c\udfc1 Partita TERMINATA - esci dal loop")` | TUI riceve `True` da `partita_terminata()` |

**Tabella Gruppo C — rimozione + log WARNING**:

| `print()` da rimuovere | `_log_safe()` sostitutivo |
|---|---|
| `print(f"\u274c Impossibile avviare: {exc}")` | `_log_safe(f"[GAME] Avvio fallito: tipo='{type(exc).__name__}'.", logging.WARNING, logger=_logger_errors)` |
| `print(f"\u274c Partita gi\u00e0 avviata: {exc}")` | `_log_safe(f"[GAME] Avvio fallito: tipo='{type(exc).__name__}'.", logging.WARNING, logger=_logger_errors)` |
| `print(f"\u274c Errore partita generico: {exc}")` | `_log_safe(f"[GAME] Avvio fallito: tipo='{type(exc).__name__}'.", logging.WARNING, logger=_logger_errors)` |
| `print(f"\u274c Impossibile turno: stato '{stato}'")` | `_log_safe(f"[GAME] esegui_turno_sicuro: stato '{stato}' non in corso, turno saltato.", logging.WARNING, logger=_logger_game)` |
| `print(f"\ud83c\udfc1 Partita finita - Numeri esauriti: {exc}")` | `_log_safe(f"[GAME] esegui_turno_sicuro: PartitaNumeriEsauritiException. tipo='{type(exc).__name__}'.", logging.WARNING, logger=_logger_game)` |
| `print(f"\u274c Turno fallito - Partita non in corso: {exc}")` | `_log_safe(f"[GAME] esegui_turno_sicuro: turno fallito, partita non in corso. tipo='{type(exc).__name__}'.", logging.WARNING, logger=_logger_game)` |
| `print(f"\u274c Errore partita durante turno: {exc}")` | `_log_safe(f"[GAME] esegui_turno_sicuro: errore generico durante turno. tipo='{type(exc).__name__}'.", logging.WARNING, logger=_logger_game)` |

> **Nota**: i 3 `print()` del Gruppo C relativi ai fallimenti di `avvia_partita_sicura` usano tutti lo stesso template di log (tipo dell'eccezione) perché mappano tutti su `CTRL_AVVIO_FALLITO_GENERICO`. La distinzione è nel tipo dell'eccezione loggata, non nel messaggio.

**Verifica post-commit**:
```bash
grep -n "print(" bingo_game/game_controller.py
# Atteso: solo print() Gruppo D (~5 righe)
python -m pytest tests/ -x -q
# Atteso: tutti verdi
```

---

### Passo 2.3 — Sostituire Gruppo D (avvisi infrastruttura)

**Commit**: `C6`  
**Messaggio**: `refactor(controller): replace print() Gruppo D with _log_safe ERROR`  
**File modificato**: `bingo_game/game_controller.py`

**Descrizione**: sostituire i 5 `print()` di Gruppo D con `_log_safe` a livello `ERROR` via `_logger_errors`. Questi sono errori di programmazione gravi o stati inattesi dell'infrastruttura.

**Tabella Gruppo D**:

| `print()` da rimuovere | `_log_safe()` sostitutivo |
|---|---|
| `print(f"\u26a0\ufe0f Avvio completato ma stato inatteso: {stato}")` | `_log_safe(f"[SYS] avvia_partita_sicura: stato post-avvio inatteso='{stato}'.", logging.WARNING, logger=_logger_system)` |
| `print("\u274c ERRORE: Oggetto non \u00e8 una Partita valida")` (in avvia) | `_log_safe(f"[ERR] avvia_partita_sicura: parametro non \u00e8 Partita. tipo='{type(partita).__name__}'.", logging.ERROR, logger=_logger_errors)` |
| `print("\u274c ERRORE: Parametro non \u00e8 una Partita valida")` (in turno) | `_log_safe(f"[ERR] esegui_turno_sicuro: parametro non \u00e8 Partita. tipo='{type(partita).__name__}'.", logging.ERROR, logger=_logger_errors)` |
| `print(f"\ud83d\udca5 Errore critico imprevisto: {exc}")` (avvia) | `_log_safe(f"[ERR] avvia_partita_sicura: eccezione imprevista. tipo='{type(exc).__name__}'.", logging.ERROR, logger=_logger_errors)` |
| `print(f"\ud83d\udca5 Errore critico imprevisto nel turno: {exc}")` | `_log_safe(f"[ERR] esegui_turno_sicuro: eccezione imprevista. tipo='{type(exc).__name__}'.", logging.ERROR, logger=_logger_errors)` |

**Verifica post-commit — la più importante della Fase 2**:
```bash
grep -n "print(" bingo_game/game_controller.py
# ATTESO: nessun output (zero risultati)

python -m pytest tests/ -x -q
# Atteso: tutti verdi
```

Se `grep` restituisce ancora righe, il commit C6 è incompleto. Non procedere alla Fase 3.

> ✅ **Fase 2 completata.** `game_controller.py` è ora silenzioso. Procedere alla Fase 3.

---

## 🖥️ Fase 3 — Adeguamento Interfaccia (`ui_terminale.py`)

> **Prerequisiti**: Fase 2 completamente committata e `grep` a zero.  
> **Obiettivo**: aggiungere nella TUI le guardie sui valori di ritorno del controller e la visualizzazione dei messaggi localizzati da `MESSAGGI_CONTROLLER`.  
> La TUI oggi non controlla il `False` di `avvia_partita_sicura` — questa è la modifica principale.

---

### Passo 3.1 — Adeguare `ui_terminale.py`

**Commit**: `C7`  
**Messaggio**: `feat(ui): add MESSAGGI_CONTROLLER guards in ui_terminale.py`  
**File modificato**: `bingo_game/ui/ui_terminale.py`

**Operazione A — Import del dizionario**:

Aggiungere nella sezione import già esistente:
```python
from bingo_game.ui.locales import MESSAGGI_CONTROLLER
from bingo_game.events.codici_controller import (
    CTRL_AVVIO_FALLITO_GENERICO,
    CTRL_TURNO_NON_IN_CORSO,
    CTRL_NUMERI_ESAURITI,
    CTRL_TURNO_FALLITO_GENERICO,
)
```

**Operazione B — Guardia su `avvia_partita_sicura` (Scenario 2)**:

Nel metodo della TUI che chiama `avvia_partita_sicura` (es. `_avvia_partita` o equivalente), aggiungere la guardia sul `False`:

```python
# Prima (senza guardia):
esito = controller.avvia_partita_sicura(partita)
# prosegue senza controllare esito

# Dopo (con guardia):
esito = controller.avvia_partita_sicura(partita)
if not esito:
    self._renderer.stampa(MESSAGGI_CONTROLLER[CTRL_AVVIO_FALLITO_GENERICO])
    return  # o gestione appropriata al flusso della TUI
```

**Operazione C — Guardie su `esegui_turno_sicuro` (Scenari 3-4)**:

Nel metodo della TUI che chiama `esegui_turno_sicuro`, aggiungere distinzione sul `None`:

```python
risultato = controller.esegui_turno_sicuro(partita)
if risultato is None:
    # Determinare la causa specifica non è necessario lato TUI:
    # il log ha già la diagnostica. Usare il messaggio generico
    # oppure affinare con un secondo campo di ritorno se richiesto.
    self._renderer.stampa(MESSAGGI_CONTROLLER[CTRL_TURNO_FALLITO_GENERICO])
    return
# Se risultato è un dict: passarlo al renderer
self._renderer.elabora_turno(risultato)
```

> **Nota**: la distinzione tra `CTRL_TURNO_NON_IN_CORSO`, `CTRL_NUMERI_ESAURITI` e `CTRL_TURNO_FALLITO_GENERICO` è già nel log. Se la TUI deve mostrare messaggi diversi ai diversi casi `None`, il controller dovrà essere esteso con un campo aggiuntivo nel dizionario di ritorno o con un enum dedicato — ma questa è una decisione da prendere nell'implementazione concreta. Il design attuale prevede un unico `None`.

**Operazione D — Cattura `ValueError` di `ottieni_stato_sintetico` (Scenario 6)**:

```python
try:
    stato = controller.ottieni_stato_sintetico(partita)
except ValueError as e:
    self._renderer.stampa(f"Errore critico nel riepilogo: {e}")
    return
# prosegue con stato valido
```

**Verifica post-commit**:
```bash
python -m pytest tests/ -x -q
# Atteso: tutti verdi

# Test manuale: avviare l'applicazione e verificare che:
# 1. Il flusso normale funzioni senza output extra
# 2. Un avvio fallito mostri il messaggio localizzato
```

> ✅ **Fase 3 completata.** La TUI ora gestisce tutti i ritorni del controller. Procedere alla Fase 4.

---

## 🧪 Fase 4 — Testing e Documentazione Finale

> **Prerequisiti**: Fasi 1-3 completamente committate.  
> **Obiettivo**: rendere la modifica verificabile e documentata in modo permanente.

---

### Passo 4.1 — Scrivere i test di non-regressione

**Commit**: `C8`  
**Messaggio**: `test: add capsys non-regression tests for silent controller`  
**File creato**: `tests/test_silent_controller.py`

**Struttura del file di test**:

```python
"""
tests/test_silent_controller.py

Test di non-regressione stdout per game_controller.py.
Verifica che nessuna funzione pubblica del controller emetta su stdout.

Criterio di done: capsys.readouterr().out == "" in tutti i percorsi.
"""
import pytest
from unittest.mock import MagicMock, patch
from bingo_game import game_controller as ctrl


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def partita_mock():
    """Mock minimale di un oggetto Partita in stato 'in_corso'."""
    p = MagicMock()
    p.stato = "in_corso"
    p.giocatori = [MagicMock(), MagicMock()]
    p.avvia_partita.return_value = None
    return p


@pytest.fixture
def partita_terminata_mock():
    """Mock di Partita in stato 'terminata'."""
    p = MagicMock()
    p.stato = "terminata"
    return p


# ---------------------------------------------------------------------------
# Test stdout — percorsi felici
# ---------------------------------------------------------------------------

class TestControllerSilenzioso:
    """Verifica che il controller non emetta nulla su stdout in nessuna condizione."""

    def test_crea_partita_standard_silenzioso(self, capsys):
        """crea_partita_standard non deve emettere su stdout."""
        with patch.object(ctrl, "crea_tabellone_standard", return_value=MagicMock()):
            ctrl.crea_partita_standard(nome="Test", num_bot=1, num_cartelle=3)
        assert capsys.readouterr().out == ""

    def test_avvia_partita_sicura_true_silenzioso(self, capsys, partita_mock):
        """avvia_partita_sicura percorso True non deve emettere su stdout."""
        ctrl.avvia_partita_sicura(partita_mock)
        assert capsys.readouterr().out == ""

    def test_avvia_partita_sicura_false_silenzioso(self, capsys, partita_mock):
        """avvia_partita_sicura percorso False (qualsiasi eccezione) non deve emettere."""
        partita_mock.avvia_partita.side_effect = Exception("errore simulato")
        ctrl.avvia_partita_sicura(partita_mock)
        assert capsys.readouterr().out == ""

    def test_esegui_turno_sicuro_dict_silenzioso(self, capsys, partita_mock):
        """esegui_turno_sicuro percorso dict non deve emettere su stdout."""
        partita_mock.esegui_turno.return_value = {"numero_estratto": 42, "premi_nuovi": [], "tombola_rilevata": False}
        ctrl.esegui_turno_sicuro(partita_mock)
        assert capsys.readouterr().out == ""

    def test_esegui_turno_sicuro_none_silenzioso(self, capsys, partita_mock):
        """esegui_turno_sicuro percorso None non deve emettere su stdout."""
        partita_mock.stato = "non_in_corso"
        ctrl.esegui_turno_sicuro(partita_mock)
        assert capsys.readouterr().out == ""

    def test_partita_terminata_false_silenzioso(self, capsys, partita_mock):
        """partita_terminata percorso False non deve emettere su stdout."""
        ctrl.partita_terminata(partita_mock)
        assert capsys.readouterr().out == ""

    def test_partita_terminata_true_silenzioso(self, capsys, partita_terminata_mock):
        """partita_terminata percorso True non deve emettere su stdout."""
        ctrl.partita_terminata(partita_terminata_mock)
        assert capsys.readouterr().out == ""

    def test_ottieni_stato_sintetico_dict_silenzioso(self, capsys, partita_mock):
        """ottieni_stato_sintetico percorso dict non deve emettere su stdout."""
        ctrl.ottieni_stato_sintetico(partita_mock)
        assert capsys.readouterr().out == ""


# ---------------------------------------------------------------------------
# Test contratti di ritorno
# ---------------------------------------------------------------------------

class TestContrattiRitorno:
    """Verifica che i contratti di ritorno del controller siano rispettati."""

    def test_avvia_partita_sicura_ritorna_true(self, partita_mock):
        assert ctrl.avvia_partita_sicura(partita_mock) is True

    def test_avvia_partita_sicura_ritorna_false_su_eccezione(self, partita_mock):
        partita_mock.avvia_partita.side_effect = Exception("errore")
        assert ctrl.avvia_partita_sicura(partita_mock) is False

    def test_ottieni_stato_sintetico_lancia_valueerror_su_non_partita(self):
        with pytest.raises(ValueError):
            ctrl.ottieni_stato_sintetico("non_una_partita")

    def test_esegui_turno_sicuro_ritorna_none_su_partita_non_in_corso(self, partita_mock):
        partita_mock.stato = "non_in_corso"
        assert ctrl.esegui_turno_sicuro(partita_mock) is None


# ---------------------------------------------------------------------------
# Test dizionario localizzazione
# ---------------------------------------------------------------------------

class TestMESSAGGICONTROLLER:
    """Verifica la struttura di MESSAGGI_CONTROLLER in it.py."""

    def test_quattro_chiavi(self):
        from bingo_game.ui.locales import MESSAGGI_CONTROLLER
        assert len(MESSAGGI_CONTROLLER) == 4

    def test_chiavi_sono_costanti_corrette(self):
        from bingo_game.ui.locales import MESSAGGI_CONTROLLER
        from bingo_game.events.codici_controller import (
            CTRL_AVVIO_FALLITO_GENERICO,
            CTRL_TURNO_NON_IN_CORSO,
            CTRL_NUMERI_ESAURITI,
            CTRL_TURNO_FALLITO_GENERICO,
        )
        assert CTRL_AVVIO_FALLITO_GENERICO in MESSAGGI_CONTROLLER
        assert CTRL_TURNO_NON_IN_CORSO in MESSAGGI_CONTROLLER
        assert CTRL_NUMERI_ESAURITI in MESSAGGI_CONTROLLER
        assert CTRL_TURNO_FALLITO_GENERICO in MESSAGGI_CONTROLLER

    def test_valori_sono_stringhe_non_vuote(self):
        from bingo_game.ui.locales import MESSAGGI_CONTROLLER
        for chiave, valore in MESSAGGI_CONTROLLER.items():
            assert isinstance(valore, str), f"Valore non stringa per chiave: {chiave}"
            assert len(valore) > 0, f"Valore vuoto per chiave: {chiave}"
```

**Verifica post-commit**:
```bash
python -m pytest tests/test_silent_controller.py -v
# Atteso: tutti verdi, zero FAILED

python -m pytest tests/ -q
# Atteso: tutti i test del progetto verdi (no regressioni)
```

**Criterio di done C8**: tutti i test di `test_silent_controller.py` passano, nessuna regressione sui test esistenti.

---

### Passo 4.2 — Aggiornare documentazione finale

**Commit**: `C9`  
**Messaggio**: `docs: update API.md, ARCHITECTURE.md, CHANGELOG.md for v0.8.0`  
**File modificati**: `documentations/API.md`, `documentations/ARCHITECTURE.md`, `documentations/CHANGELOG.md`

---

#### 4.2.1 — `API.md`

**Obiettivo**: rimuovere ogni riferimento a stdout o `print()` dalle firme e note delle funzioni del controller.

**Aggiornamenti richiesti per funzione**:

| Funzione | Rimuovere | Aggiungere |
|---|---|---|
| `crea_partita_standard` | Note su `print()` di costruzione | "Scrive log DEBUG via `_logger_game` per ogni sotto-passo" |
| `avvia_partita_sicura` | Note su messaggi di avvio/errore stampati | "Ritorna `True`/`False`. Fallimenti loggati a `WARNING` via `_logger_errors`." |
| `esegui_turno_sicuro` | Note su stampa turno/premi | "Ritorna `dict` o `None`. Premi loggati a `INFO` via `_logger_prizes`." |
| `ottieni_stato_sintetico` | Note su stampa stato | "Ritorna `dict`. Lancia `ValueError` se il parametro non è un oggetto `Partita` valido." |
| `partita_terminata` | Note su stampa stato loop | "Ritorna `bool`. Stato loggato a `DEBUG` via `_logger_game`." |
| `ha_partita_tombola` | Note su stampa tombola | "Ritorna `bool`. Verifica loggata a `DEBUG` via `_logger_game`." |

**Criterio di done API.md**: `grep -n "stdout\|print()" documentations/API.md` non deve restituire riferimenti alle funzioni del controller.

---

#### 4.2.2 — `ARCHITECTURE.md`

**Obiettivo**: aggiornare i diagrammi per riflettere il pattern Silent Controller.

**4 modifiche richieste**:

**1. Diagramma layer** — rimuovere la freccia `Controller → stdout`:
```
# Prima:
game_controller.py → stdout
game_controller.py → (valori) → ui_terminale.py → stdout

# Dopo:
game_controller.py → (bool/dict/None) → ui_terminale.py → stdout
game_controller.py → (log) → tombola_stark.log
```

**2. Regole architetturali invarianti** — aggiungere:
```
- Il Controller non scrive mai su stdout.
  Verificabile con: grep -n "print(" bingo_game/game_controller.py → zero risultati.
```

**3. Mappa moduli v0.8.0** — aggiungere:
```
bingo_game/events/codici_controller.py
  Costanti stringa per i codici evento del controller (CTRL_*).
  Usate come chiavi di MESSAGGI_CONTROLLER in it.py.
  Introdotto in v0.8.0.
```

**4. Sezione versioni** — aggiungere nota v0.8.0:
```
v0.8.0: Refactoring "Silent Controller" — game_controller.py non scrive più su stdout.
        Nuovo modulo bingo_game/events/codici_controller.py.
        Nuovo dizionario MESSAGGI_CONTROLLER in it.py.
```

**Criterio di done ARCHITECTURE.md**: il diagramma riflette il flusso `Controller → valori → TUI → stdout`.

---

#### 4.2.3 — `CHANGELOG.md`

**Obiettivo**: documentare le modifiche v0.8.0.

**Voce da aggiungere in cima** (o nella sezione v0.8.0 se già presente):

```markdown
## [v0.8.0] - 2026-02-20 Silent Controller

### Changed
- `bingo_game/game_controller.py`: rimossi tutti i `print()` (~22 chiamate).
  I passaggi di costruzione vanno ora a log `DEBUG` via `_logger_game`.
  Gli output di stato sono trasportati dai valori di ritorno (`bool`, `dict`, `None`).
  I messaggi di errore sono gestiti dalla TUI via `MESSAGGI_CONTROLLER`.
- `bingo_game/ui/ui_terminale.py`: aggiunte guardie sui valori di ritorno
  di `avvia_partita_sicura` (percorso `False`) e `ottieni_stato_sintetico`
  (cattura `ValueError`).

### Added
- `bingo_game/events/codici_controller.py`: nuove costanti stringa
  `CTRL_AVVIO_FALLITO_GENERICO`, `CTRL_TURNO_NON_IN_CORSO`,
  `CTRL_NUMERI_ESAURITI`, `CTRL_TURNO_FALLITO_GENERICO`.
- `bingo_game/ui/locales/it.py`: nuovo dizionario `MESSAGGI_CONTROLLER`
  (4 voci) tipizzato con le costanti di `codici_controller.py`.
- `tests/test_silent_controller.py`: test di non-regressione stdout
  con `capsys` per tutte le funzioni pubbliche del controller.

### Fixed
- Accessibilità: rimossi i messaggi con emoji (`\u2705`, `\u274c`, `\ud83c\udf89`, `\ud83c\udfc1`) che
  interferivano con gli screen reader.
- Architettura: eliminata la dipendenza di fatto `Controller → stdout`
  che impediva il controllo esclusivo dell'output da parte della TUI.
```

**Criterio di done C9**: i tre file documentali sono aggiornati, il testo rispecchia le modifiche reali effettuate.

> ✅ **Fase 4 completata.** Tutti i 9 commit sono su `main` (o sul branch feature).

---

## 🔄 Apertura PR e Review Finale

Se il lavoro è stato fatto su un branch `feature/silent-controller-v0.8.0`:

```bash
git push origin feature/silent-controller-v0.8.0
```

Aprire la PR con:
- **Titolo**: `feat: Silent Controller v0.8.0 — rimozione print(), logging e localizzazione`
- **Descrizione**: linkare `DESIGN_SILENT_CONTROLLER.md` e questo `PLAN_SILENT_CONTROLLER.md`
- **Label**: `refactor`, `v0.8.0`

**Checklist di review PR**:

```
[ ] grep -n "print(" bingo_game/game_controller.py → zero risultati
[ ] pytest tests/test_silent_controller.py → tutti verdi
[ ] pytest tests/ → nessuna regressione
[ ] API.md aggiornato (nessun riferimento a stdout nelle firme controller)
[ ] ARCHITECTURE.md aggiornato (diagramma riflette Silent Controller)
[ ] CHANGELOG.md aggiornato (voce v0.8.0 presente)
[ ] codici_controller.py importabile e costanti corrette
[ ] MESSAGGI_CONTROLLER ha esattamente 4 chiavi
[ ] TUI gestisce False di avvia_partita_sicura
[ ] TUI cattura ValueError di ottieni_stato_sintetico
```

---

## 🚨 Problemi Noti e Contingenze

| Problema | Probabilità | Mitigazione |
|---|---|---|
| Test esistenti con `capsys` sul controller | Bassa (da verificare pre-Fase 2) | Aggiornare i test: rimuovere le assert su stdout, verificare i valori di ritorno |
| `__init__.py` di `locales` non esiste o ha struttura diversa | Bassa | Adattare il passo 1.3 al pattern effettivo del file |
| La TUI usa `print()` diretto invece del renderer per alcuni messaggi | Media | Adattare l'Operazione B/C del passo 3.1 al codice reale |
| `esegui_turno_sicuro` non distingue i diversi tipi di `None` | Media | La TUI usa `CTRL_TURNO_FALLITO_GENERICO` come fallback; affinare in sprint futuro |
| Sub-logger `_logger_system` non ancora inizializzato nel controller | Bassa | Verificare header del file e aggiungere se mancante, seguendo il pattern degli altri |

---

## 🎯 Definition of Done v0.8.0

La feature è **completa** quando tutte queste condizioni sono soddisfatte simultaneamente:

1. ✅ `grep -n "print(" bingo_game/game_controller.py` → **zero risultati**
2. ✅ `pytest tests/test_silent_controller.py` → **tutti verdi**
3. ✅ `pytest tests/` → **nessuna regressione**
4. ✅ `bingo_game/events/codici_controller.py` esiste con **4 costanti** corrette
5. ✅ `MESSAGGI_CONTROLLER` in `it.py` ha **4 chiavi** con testi non vuoti
6. ✅ `MESSAGGI_CONTROLLER` esportato da `bingo_game.ui.locales`
7. ✅ La TUI gestisce il `False` di `avvia_partita_sicura` con `CTRL_AVVIO_FALLITO_GENERICO`
8. ✅ La TUI cattura il `ValueError` di `ottieni_stato_sintetico`
9. ✅ `API.md`, `ARCHITECTURE.md`, `CHANGELOG.md` aggiornati
10. ✅ PR approvata e mergiata su `main`

---

**Fine Piano Operativo**
