---

# Copilot Custom Instructions - Tombola Stark

## 👤 Profilo Utente e Interazione

* **Accessibilità Prima di Tutto**: L'utente è un programmatore non vedente che utilizza NVDA su Windows 11. Ogni proposta deve essere testabile da tastiera e compatibile con screen reader.
* **Feedback Testuale Strutturato**: Quando proponi modifiche, fornisci sempre:
  1. **Cosa**: Lista puntata delle modifiche applicate (file + line numbers)
  2. **Perché**: Rationale tecnico (1-2 frasi)
  3. **Impatto**: File di documentazione da aggiornare (se applicabile)
* **Formattazione Markdown**: Usa intestazioni gerarchiche (`##`, `###`) e liste (`-`, `1.`) per navigazione screen reader. Evita tabelle complesse o layout ASCII decorativi.
* **No Jargon Visivo**: Non usare espressioni come "come puoi vedere", "guarda qui", "nella parte superiore". Usa riferimenti testuali: "nel file X, linea Y", "nella sezione Z".

---

## 🏗️ Architettura e Standard di Codifica

### Clean Architecture (Strict Enforcement)

Il progetto segue **Clean Architecture a 4 layer**. Ogni modifica deve rispettare queste dipendenze:

```
Presentation → Application → Domain ← Infrastructure
    ↓              ↓            ↑
  (UI)       (Use Cases)   (Entities)
```

**Regole:**
- **Domain** (`bingo_game/`): Cartella, Partita, Tabellone, GiocatoreBase e business rules del gioco.
- **Players** (`bingo_game/players/`): GiocatoreUmano, GiocatoreAutomatico, mixin di gestione focus.
- **Events** (`bingo_game/events/`): EsitoAzione, eventi di output UI, eventi partita.
- **UI/TUI** (`bingo_game/ui/tui/`): Interfaccia terminale, navigazione utente, comandi interattivi.
- **Controller** (`bingo_game/game_controller.py`): Unico punto di accesso al dominio dalla TUI.

**Vietato:**
- ❌ Import Domain dalla TUI: `from bingo_game.players.giocatore_umano import GiocatoreUmano` nella TUI
- ❌ Import `wx` in qualsiasi parte del progetto (TUI terminale only)
- ❌ Business logic nelle classi UI (`bingo_game/ui/tui/`)
- ❌ Output diretto con `print()` fuori dal TerminalRenderer

**Esempio corretto di refactoring:**
```python
# ❌ ERRATO (TUI importa Domain direttamente)
# bingo_game/ui/tui/tui_partita.py
from bingo_game.players.giocatore_umano import GiocatoreUmano  # ❌

# ✅ CORRETTO (TUI accede Domain solo via Controller)
# bingo_game/ui/tui/tui_partita.py
from bingo_game.game_controller import ottieni_giocatore_umano, esegui_turno_sicuro

def gestisci_comando_cartella(partita, numero: int) -> None:
    giocatore = ottieni_giocatore_umano(partita)
    esito = giocatore.imposta_focus_cartella(numero)
    if esito.ok:
        _renderer.render_esito(esito)
    else:
        _stampa(MESSAGGI_ERRORI[esito.errore][0])
```

---

### Naming Conventions

* **Variabili/Funzioni**: `snake_case` (es. `imposta_focus_cartella`, `esegui_turno_sicuro`)
* **Classi**: `PascalCase` (es. `GiocatoreUmano`, `TerminalRenderer`, `EsitoAzione`)
* **Costanti**: `UPPER_SNAKE_CASE` (es. `MAX_CARTELLE_GIOCATORE`, `NUMERO_MIN_TOMBOLA`)
* **Private/Protected**: Prefisso `_` (es. `_indice_cartella_focus`, `_reset_focus_riga_e_colonna`)
* **Type Hints**: Sempre obbligatori per metodi pubblici

**Esempio di firma corretta:**
```python
def imposta_focus_cartella(self, numero_cartella: int) -> EsitoAzione:
    """
    Imposta il focus su una cartella specifica (input umano 1-based).

    Args:
        numero_cartella: Numero cartella in formato umano (1..N)

    Returns:
        EsitoAzione con ok=True e EventoFocusCartellaImpostato se riesce,
        ok=False con codice errore standardizzato altrimenti
    """
```

---

### Type Hints Enforcement

**Vietato:**
- ❌ `tabellone.count()` → AttributeError (metodo inesistente)
- ❌ Implicit returns senza annotazione
- ❌ `Any` come type hint di default

**Obbligatorio:**
- ✅ `tabellone.get_numeri_estratti() -> list[int]`
- ✅ Ogni public method con return type esplicito
- ✅ Parametri con type hints anche per metodi privati

**Esempio fix completo:**
```python
# ❌ ERRATO
def controlla_cartella(cartella):
    if cartella.count() > 0:  # AttributeError!
        return True

# ✅ CORRETTO
def controlla_cartella(cartella: Cartella) -> bool:
    if cartella.get_numeri_cartella():
        return True
    return False
```

---

### Logging (Sistema Categorizzato)

**MAI usare `print()` nel codice di produzione.** Usa i named logger dedicati per categoria:

```python
import logging

# Named logger per categoria — scegli quello corretto per contesto
_logger_partita  = logging.getLogger('tombola_stark.partita')   # lifecycle partita, turni, estrazioni
_logger_tui      = logging.getLogger('tombola_stark.tui')       # navigazione TUI, comandi utente
_logger_errori   = logging.getLogger('tombola_stark.errori')    # errori, warnings, eccezioni
```

**Routing dei file di output:**
- `tombola_stark.partita`  → `logs/partita.log`
- `tombola_stark.tui`      → `logs/tui.log`
- `tombola_stark.errori`   → `logs/errori.log`
- root                     → `logs/tombola_stark.log` (library logs)

**Regola propagate=False:** ogni named logger ha `propagate=False` — i messaggi
NON finiscono su `tombola_stark.log`. Questo è intenzionale. Non modificare mai
questo comportamento senza aggiornare `game_logger.py`.

**Vietato:**
- ❌ `print(f"Debug: {variable}")` → usa `logging.getLogger('tombola_stark.tui').debug()`
- ❌ Log con emoji o box ASCII → screen reader unfriendly
- ❌ `logging.getLogger()` (root logger) nel codice applicativo → usa named loggers
- ❌ Log in Domain layer senza dependency injection

---

### Accessibilità TUI (Screen Reader + Keyboard)

Ogni output TUI deve essere compatibile con NVDA su Windows 11:

**Checklist accessibilità TUI obbligatoria:**
- [ ] Ogni riga di output è autonoma e leggibile da NVDA senza contesto visivo
- [ ] Ogni riga non supera 120 caratteri (screen reader non tronca)
- [ ] Nessun carattere ASCII decorativo (box, linee, tabelle visive)
- [ ] Nessun colore ANSI o escape sequence (non interpretabili da NVDA)
- [ ] I comandi sono tasto singolo catturato con msvcrt (niente Invio obbligatorio)
- [ ] I comandi che richiedono argomento usano input() con prompt descrittivo
- [ ] Ogni azione produce almeno una riga di feedback testuale
- [ ] In caso di errore il messaggio descrive cosa fare, non solo cosa è andato storto

**Esempio corretto di output accessibile:**
```python
# CORRETTO — riga autonoma, descrittiva, entro 120 caratteri
print("Cartella 1 di 3 — Riga 2 — Numeri: 15, 32, 67 — Segnati: 1 di 3")

# VIETATO — output visivo non leggibile da screen reader
print("┌─────────────────────┐")
print("│  15  │  --  │  67  │")
print("└─────────────────────┘")
```

---

## 📚 Protocollo Allineamento Documentazione (Mandatorio)

### Struttura Cartella `documentations/`

```
documentations/
├── 1 - templates/                        # Template riutilizzabili
│   ├── TEMPLATE_example_DESIGN_DOCUMENT.md
│   ├── TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md
│   ├── TEMPLATE_exaple_TODO.md
│   ├── TEMPLATE_example_API.md
│   ├── TEMPLATE_example_ARCHITECTURE.md
│   └── TEMPLATE_example_CHANGELOG.md
├── 2 - project/                          # Design doc per feature attive
│   └── DESIGN_*.md
├── 3 - planning/                         # Piani di implementazione
│   └── PLAN_*_vX.Y.Z.md
├── 4 - todo file/                        # Cruscotto operativo attivo
│   └── TODO_vX.Y.Z.md
├── API.md                                # Riferimento API pubblica
├── ARCHITECTURE.md                       # Architettura del sistema
└── RAPPORTO_ANALISI_SISTEMA.md           # Analisi di sistema
```

**File root del repository:**
- `README.md` → presentazione pubblica del progetto
- `CHANGELOG.md` → storia delle versioni rilasciate

**Regole di posizionamento:**
- Un nuovo design doc → `documentations/2 - project/DESIGN_<feature>.md`
- Un piano di implementazione → `documentations/3 - planning/PLAN_<descrizione>_vX.Y.Z.md`
- Il cruscotto operativo → `documentations/4 - todo file/TODO_vX.Y.Z.md`
  (un solo file attivo per volta, sostituisce il precedente ad ogni branch)

---

### Creazione File di Progetto (Design Doc, Piano, TODO)

Ogni nuovo task non banale richiede la creazione di uno o più file di progetto **prima** di scrivere codice. I template si trovano in `documentations/1 - templates/`.

#### Quando creare un DESIGN Document

**Trigger (almeno uno dei seguenti):**
- L'utente descrive una nuova feature con comportamento non ovvio
- Il task implica decisioni architetturali (nuovo layer, nuovo pattern, nuovi attori)
- La feature coinvolge più di 3 file distinti in layer diversi
- Ci sono alternative di design da confrontare

**Template da usare:** `documentations/1 - templates/TEMPLATE_example_DESIGN_DOCUMENT.md`

**Nome file output:** `documentations/2 - project/DESIGN_<feature-slug>.md`

**Contenuto minimo obbligatorio:**
- Metadata (data, stato, versione target)
- Idea in 3 righe (cosa, perché, problema risolto)
- Attori e concetti chiave
- Flussi concettuali (no decisioni tecniche in questa fase)

**Esempio creazione:**
```
Utente: "Voglio aggiungere i tasti rapidi alla TUI"
→ Crea: documentations/2 - project/DESIGN_tasti-rapidi-tui.md
→ Usa: TEMPLATE_example_DESIGN_DOCUMENT.md come base
→ Stato iniziale: DRAFT
```

---

#### Quando creare un PLAN (Piano di Implementazione)

**Trigger (almeno uno dei seguenti):**
- Il task richiede più di 2 commit atomici
- Esiste già un DESIGN doc approvato da implementare
- Si tratta di un bugfix con root cause analisi richiesta
- Il task è un refactoring su più file

**Template da usare:** `documentations/1 - templates/TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`

**Nome file output:** `documentations/3 - planning/PLAN_<descrizione-slug>_vX.Y.Z.md`

**Contenuto minimo obbligatorio:**
- Executive Summary (tipo, priorità, stato, branch, versione target)
- Problema/Obiettivo (o Root Cause se bugfix)
- Lista file coinvolti con tipo operazione (CREATE / MODIFY / DELETE)
- Fasi di implementazione in ordine sequenziale
- Test plan (unit + integration)
- Criteri di completamento

**Esempio creazione:**
```
Utente: "Implementa i tasti rapidi descritti nel DESIGN"
→ Crea: documentations/3 - planning/PLAN_tasti-rapidi-tui_v0.10.0.md
→ Usa: TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md come base
→ Stato iniziale: DRAFT → poi READY prima del primo commit
```

---

#### Quando creare/aggiornare il TODO

**Trigger creazione (tutti devono essere veri):**
- Esiste un PLAN approvato (stato READY)
- Il branch di lavoro è attivo
- L'implementazione multi-fase è appena iniziata

**Template da usare:** `documentations/1 - templates/TEMPLATE_exaple_TODO.md`

**Nome file output:** `documentations/4 - todo file/TODO_vX.Y.Z.md`
(un solo file attivo per volta, il nome rispecchia la versione target)

**Regole operative:**
- Il TODO è un **cruscotto**, non un documento tecnico: sommario operativo consultabile in 30 secondi
- Il link al PLAN completo (fonte di verità) deve essere in cima al TODO
- Ogni checkbox spuntata corrisponde a un commit già eseguito
- Va aggiornato **dopo ogni commit**, non in batch a fine lavoro
- Al merge su `main` il TODO viene archiviato nella stessa cartella con suffisso `_DONE`

**Contenuto minimo obbligatorio:**
- Riferimento al PLAN completo (link relativo)
- Istruzioni per Copilot Agent (workflow incrementale)
- Obiettivo in 3-5 righe
- Lista file coinvolti
- Checklist implementazione per layer
- Criteri di completamento

**Esempio aggiornamento post-commit:**
```
Dopo commit "feat(tui): aggiunto codici_tasti_tui.py":
→ Apri documentations/4 - todo file/TODO_v0.10.0.md
→ Spunta: [x] Blocco 1 — Creato codici_tasti_tui.py
→ Salva e includi nel commit successivo
```

---

#### Relazione tra i Tre File (Flusso Canonico)

```
documentations/2 - project/DESIGN_<feature>.md       (CONCEPT - "cosa vogliamo")
      ↓  approva
documentations/3 - planning/PLAN_<feature>_vX.Y.Z.md (TECNICO - "come lo facciamo")
      ↓  inizia
documentations/4 - todo file/TODO_vX.Y.Z.md          (OPERATIVO - "dove siamo")
      ↓  aggiorna dopo ogni commit
      ↓  a merge completato → rinomina in TODO_vX.Y.Z_DONE.md
```

**Vincoli di sequenza:**
- Non creare un PLAN senza aver prima chiarito i requisiti (DESIGN o discussione esplicita)
- Non iniziare commit di codice senza un TODO aggiornato se il task ha più di 2 fasi
- Non modificare un DESIGN doc a stato FROZEN senza aggiornare il PLAN corrispondente

#### Workflow Completo di Creazione (Step-by-Step)

Quando l'utente introduce un nuovo task significativo:

1. **Valuta la complessità**: meno di 2 file e 1 commit → nessun file di progetto necessario
2. **Crea DESIGN** (se architetturale): copia `TEMPLATE_example_DESIGN_DOCUMENT.md`, compila sezioni obbligatorie, salva in `documentations/2 - project/`
3. **Crea PLAN**: copia `TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`, collega al DESIGN se esiste, definisci fasi, salva in `documentations/3 - planning/`
4. **Crea TODO**: copia `TEMPLATE_exaple_TODO.md`, metti link al PLAN in cima, trascrivi le fasi come checklist, salva in `documentations/4 - todo file/`
5. **Inizia implementazione**: segui il workflow incrementale descritto nel TODO
6. **Aggiorna TODO** dopo ogni commit (spunta checkbox)
7. **A merge completato**: aggiorna `CHANGELOG.md`, rinomina TODO in `TODO_vX.Y.Z_DONE.md`

---

### Trigger Events (quando aggiornare docs)

Dopo **ogni modifica al codice** (`.py`), esegui questo audit:

**1. documentations/API.md**
Aggiorna se modifichi:
- Signature metodi pubblici (parametri, return type, nome)
- Classi esportate da `__init__.py`
- Enum/costanti pubbliche
- Comportamento documentato (side effects, validazioni)

**Esempio:**
```python
# Prima
def sposta_focus_riga_su_semplice(self) -> EsitoAzione:

# Dopo — aggiunto parametro opzionale
def sposta_focus_riga_su_semplice(self, loop: bool = False) -> EsitoAzione:
```
→ **Aggiorna `documentations/API.md`**: sezione `## GiocatoreUmano.sposta_focus_riga_su_semplice` — parametro aggiunto, aggiorna esempio d'uso

---

**2. documentations/ARCHITECTURE.md**
Aggiorna se modifichi:
- Struttura cartelle (`bingo_game/`, `documentations/`, `tests/`)
- Data flow tra layer (nuovi moduli, nuovi adapter)
- Design patterns adottati (nuovi commander, dispatcher)
- Dipendenze esterne (nuove librerie in `requirements.txt`)

**Esempio:**
- Aggiungi `bingo_game/ui/tui/tui_commander.py`
→ **Aggiorna `documentations/ARCHITECTURE.md`**: sezione "UI/TUI Layer" + diagramma struttura cartelle

---

**3. CHANGELOG.md** (nella root del repository)
Aggiorna **sempre** dopo merge su `main`:
- Nuove feature → sezione `## [Unreleased] - Added`
- Bug fix → `## [Unreleased] - Fixed`
- Breaking changes → `## [Unreleased] - Changed` + ⚠️ warning

**Formato:**
```markdown
## [Unreleased]

### Added
- tui_commander.py: Nuovo modulo commander per mappatura tasti rapidi TUI

### Fixed
- tui_partita.py: Corretto reset focus riga al cambio cartella

### Changed
- ⚠️ BREAKING: Rimosso comando testuale `c` sostituito da tasto PagGiù
```

---

**4. README.md** (nella root del repository)
Aggiorna se modifichi:
- Entry point (`main.py`)
- Comandi disponibili durante la partita (nuovi tasti rapidi)
- Requisiti sistema (nuove dipendenze in `requirements.txt`)
- Setup environment (nuovi passi installazione)

---

### Workflow di Sync (Step-by-Step)

Quando l'utente dice *"applica le modifiche"*:

1. **Esegui modifiche codice** (`.py` files)
2. **Audit immediato**:
   ```
   Modifiche a bingo_game/players/giocatore_umano.py (line 105):
   - Aggiunto metodo sposta_focus_riga_su_semplice()

   📋 Impatto documentazione:
   - documentations/API.md: ✅ Richiede aggiornamento (nuova sezione GiocatoreUmano)
   - documentations/ARCHITECTURE.md: ⬜ Nessun impatto strutturale
   - CHANGELOG.md: ✅ Aggiungi entry [Unreleased] - Added
   - README.md: ⬜ Nessun impatto
   ```
3. **Proposta aggiornamento**:
   ```
   Vuoi che aggiorni:
   1. documentations/API.md (nuova sezione metodo)
   2. CHANGELOG.md (entry Added)

   Rispondi "sì" per procedere, "solo 1" per API.md, "no" per saltare.
   ```
4. **Applica aggiornamenti docs** se confermato
5. **Verifica finale**:
   ```
   ✅ Codice e documentazione sincronizzati:
   - bingo_game/players/giocatore_umano.py (modified)
   - documentations/API.md (updated, sezione GiocatoreUmano)
   - CHANGELOG.md (updated, [Unreleased] section)
   ```

---

### Integrità Link e Cross-References

Prima di chiudere un task, verifica:

- [ ] Ogni file Python pubblico ha entry in `documentations/API.md`
- [ ] Ogni sezione `documentations/API.md` ha link a `documentations/ARCHITECTURE.md` per contesto
- [ ] Il TODO attivo in `documentations/4 - todo file/` riflette il progresso reale
- [ ] `CHANGELOG.md` ha entry per ogni modifica in `main`
- [ ] Nessun link rotto nei file Markdown

---

## 🛠️ Testing e Validazione

### Test Coverage Requirement

- **Minimum**: 85% coverage per `bingo_game/players/` e `bingo_game/events/`
- **Target**: 90%+ coverage globale
- Ogni nuovo metodo pubblico **deve** avere almeno 1 test unitario

**Comando pre-commit:**
```bash
pytest tests/ --cov=bingo_game --cov-report=term-missing --cov-fail-under=85
```

---

### Test Pattern (Esempio da seguire)

```python
# tests/players/test_giocatore_umano.py
import pytest
from bingo_game.players.giocatore_umano import GiocatoreUmano
from tests.helpers import crea_cartella_test

class TestImpostaFocusCartella:
    @pytest.fixture
    def giocatore(self):
        """Setup giocatore con cartelle per test focus."""
        g = GiocatoreUmano(nome="Test")
        g.cartelle = [crea_cartella_test(), crea_cartella_test()]
        return g

    def test_imposta_focus_cartella_valida_ritorna_successo(self, giocatore):
        """Verifica che il focus su cartella valida ritorni EsitoAzione ok=True."""
        esito = giocatore.imposta_focus_cartella(1)
        assert esito.ok is True
        assert esito.evento is not None
        assert giocatore._indice_cartella_focus == 0  # 1-based → 0-based

    def test_imposta_focus_cartella_fuori_range_ritorna_errore(self, giocatore):
        """Verifica che un indice fuori range ritorni ok=False con codice errore."""
        esito = giocatore.imposta_focus_cartella(99)
        assert esito.ok is False
        assert esito.errore == "NUMERO_CARTELLA_FUORI_RANGE"
```

**Naming convention test:**
- `test_<method>_<scenario>_<expected_behavior>`
- Esempio: `test_imposta_focus_cartella_fuori_range_ritorna_errore`

---

### Marker Pytest

**Marker obbligatori — applicali sempre:**

```python
@pytest.mark.unit        # Test senza dipendenze esterne (no filesystem reale, no msvcrt)
@pytest.mark.integration # Test che coinvolgono più layer insieme
```

**Comandi standard:**
```bash
# Smoke test obbligatorio pre-merge
pytest -m "unit" -v

# Test completi
pytest -v

# Solo test di un modulo specifico
pytest tests/players/test_giocatore_umano.py -v
```

---

## 🔍 Pre-Commit Checklist (Auto-Eseguita)

Prima di ogni commit, verifica silentemente:

1. **Syntax**: `python -m py_compile bingo_game/**/*.py` (0 errori)
2. **Type Hints**: `mypy bingo_game/ --strict --python-version 3.8` (0 errori)
3. **Imports**: `pylint bingo_game/ --disable=all --enable=cyclic-import` (nessun import circolare)
4. **Logging**: `grep -r "print(" bingo_game/ --include="*.py"` (0 occorrenze fuori da TerminalRenderer)
5. **Docs Sync**: `CHANGELOG.md` modificato nelle ultime 48h? (verifica manuale)
6. **Tests**: `pytest tests/ --cov=bingo_game --cov-report=term --cov-fail-under=85` (100% pass)

**Output esempio comando Git per ottenere SHA:**
```bash
git ls-tree HEAD bingo_game/players/giocatore_umano.py

# Output:
# 100644 blob 98184f34cc642e2b393591a1dad4f45b0108e49c    bingo_game/players/giocatore_umano.py
#              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#              Questo è il SHA da usare in create_or_update_file
```

**Se uno fallisce:**
```
⚠️ Pre-commit check FAILED:
- mypy: Found 3 type errors in bingo_game/ui/tui/tui_commander.py
- docs: CHANGELOG.md non aggiornato (ultima modifica: 2 giorni fa)

Vuoi che fixo automaticamente o preferisci revisione manuale?
```

---

## 📝 Convenzioni Git Commit

### Atomic Commits Policy

**Un commit = una unità logica di cambiamento.** Regole operative:

- ✅ Un commit per file modificato se le modifiche hanno motivazioni diverse
- ✅ Un commit per task logico (es. "aggiunta costanti tasti", "aggiunto commander")
- ❌ No mega-commit che mescolano fix di codice + aggiornamenti docs + test
- ❌ No commit "WIP" o "fix fix fix" su branch destinati alla PR

**Ordine di commit consigliato** quando si lavora su un task con dipendenze:
1. Pre-requisiti (es. aggiungere costanti o codici necessari)
2. Implementazione principale
3. Test
4. Aggiornamento documentazione (API.md, ARCHITECTURE.md, CHANGELOG.md)
5. Aggiornamento cruscotto operativo (TODO)

---

**Format obbligatorio:**
```
<type>(<scope>): <subject>

<body (opzionale)>

<footer (opzionale)>
```

**Types:**
- `feat`: Nuova feature
- `fix`: Bug fix
- `docs`: Solo documentazione
- `refactor`: Refactoring senza cambio comportamento
- `test`: Aggiunta/modifica test
- `chore`: Maintenance (deps, build, config)

**Scope:** `domain`, `players`, `events`, `tui`, `controller`, `docs`, `tests`

**Esempio:**
```
feat(tui): aggiunto tui_commander.py con mappatura tasti rapidi

- Creato bingo_game/ui/tui/tui_commander.py
- Creato bingo_game/events/codici_tasti_tui.py
- Aggiornato documentations/ARCHITECTURE.md sezione UI/TUI
- Aggiornato documentations/API.md con nuove funzioni pubbliche

Refs: documentations/3 - planning/PLAN_tasti-rapidi-tui_v0.10.0.md
```

---

## 🌿 Branch Workflow e Release Process

### Naming branch

| Tipo | Pattern | Esempio |
|---|---|---|
| Feature | `feature/<slug>` | `feature/tasti-rapidi-tui` |
| Fix | `fix/<slug>` | `fix/focus-cartella-crash` |
| Hotfix | `hotfix/<slug>` | `hotfix/segna-numero-errore` |
| Refactor | `refactor/<slug>` | `refactor/clean-arch-tui` |
| Docs | `docs/<slug>` | `docs/api-update-v0.10` |

### Quando creare un branch vs committare su `main`

- **Branch separato**: qualsiasi feature, fix non banale, refactor, o lavoro che richiede più di 1 commit.
- **Commit diretto su `main`**: solo hotfix monocommit urgenti o aggiornamenti di documentazione pura (nessun `.py` modificato).

### Release process (step obbligatori)

1. Tutti i fix e i task del branch completati e verificati
2. PR aperta verso `main` con body che linka design doc e piano
3. Merge con **merge commit** (`--no-ff`) — preserva storia del branch
4. Subito dopo il merge, creare il tag di versione:
   ```bash
   git checkout main && git pull origin main
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
5. Aggiornare `CHANGELOG.md`:
   - Rinominare `## [Unreleased]` in `## [X.Y.Z] — YYYY-MM-DD`
   - Aggiungere nuovo `## [Unreleased]` vuoto in cima
6. Rinominare il TODO attivo in `TODO_vX.Y.Z_DONE.md`

### Versionamento (SemVer)

- `MAJOR` (X): breaking changes all'API pubblica
- `MINOR` (Y): nuove feature retrocompatibili
- `PATCH` (Z): bug fix retrocompatibili

---

## 🚨 Critical Warnings (Non Ignorare Mai)

1. **NO IMPORT DOMAIN DALLA TUI**:
   La TUI (`tui_partita.py`, `tui_commander.py`) non deve mai importare classi Domain
   direttamente. Tutto il dominio è accessibile solo tramite `game_controller.py`.
   - ❌ VIETATO: `from bingo_game.players.giocatore_umano import GiocatoreUmano`
   - ✅ CORRETTO: `from bingo_game.game_controller import ottieni_giocatore_umano`

2. **ESITO_AZIONE: CONTROLLA SEMPRE ok PRIMA DI LEGGERE evento**:
   Ogni metodo di GiocatoreUmano ritorna EsitoAzione. Non accedere mai
   a `esito.evento` senza aver prima verificato `esito.ok is True`.
   - ❌ VIETATO: `renderer.render_esito(esito.evento)`
   - ✅ CORRETTO: `if esito.ok: renderer.render_esito(esito)`

3. **FOCUS CARTELLA NON SI AUTO-IMPOSTA NEI COMANDI DI AZIONE**:
   I metodi che modificano stato (`segna_numero_manuale`, `annuncia_vittoria`,
   `vai_a_riga_avanzata`, `vai_a_colonna_avanzata`) hanno `auto_imposta=False`.
   Se il focus cartella è None, ritornano errore. È responsabilità dell'utente
   selezionare prima la cartella con `imposta_focus_cartella(n)`.

4. **NESSUN print() NEL CODICE DI PRODUZIONE**:
   Tutta la produzione di output passa per `TerminalRenderer`.
   L'unica eccezione è la funzione `_stampa()` in `tui_partita.py`,
   che è un wrapper esplicito su print() creato appositamente per il mock nei test.
   - ❌ VIETATO: `print("Numero segnato!")` nel codice applicativo
   - ✅ CORRETTO: `_stampa(riga)` oppure `_renderer.render_esito(esito)`

5. **NESSUNA STRINGA DI TESTO NEL DOMAIN LAYER**:
   I metodi di `GiocatoreUmano`, `Partita`, `Tabellone` e `Cartella` non producono
   mai stringhe pronte per l'utente. Producono solo `EsitoAzione` con eventi dati.
   Le stringhe esistono solo in `bingo_game/ui/locales/it.py` e vengono assemblate
   dal `TerminalRenderer`.

6. **I TASTI SPECIALI CON msvcrt PRODUCONO DUE BYTE**:
   Su Windows, msvcrt.getwch() ritorna `\x00` o `\xe0` come primo byte per i tasti
   speciali (frecce, PagSu, PagGiù). In quel caso va letto immediatamente un secondo
   byte per ottenere il codice completo. Non trattare mai il primo byte `\xe0` o `\x00`
   come un comando standalone.
   ```python
   # Lettura corretta tasto singolo con msvcrt
   tasto = msvcrt.getwch()
   if tasto in ('\x00', '\xe0'):
       tasto = tasto + msvcrt.getwch()  # legge secondo byte
   ```

---

## 🎯 Output verso NVDA in Tombola Stark

NVDA su Windows 11 legge automaticamente l'output standard del terminale (cmd.exe
o Windows Terminal) riga per riga, non appena viene stampato con print().
Non è necessario nessun metodo speak() esplicito.

Per garantire che NVDA legga correttamente ogni messaggio:
- Ogni messaggio deve essere su una riga separata (no `\r`, no escape ANSI)
- Messaggi lunghi vanno spezzati in righe tematiche autonome
- I messaggi di errore devono essere self-contained: NVDA non ha contesto visivo
- Non usare caratteri speciali, simboli Unicode decorativi o emoji

Esempio di output corretto per NVDA:
```python
print("Cartella 1 selezionata.")
print("Numeri mancanti per ambo: 2.")
print("Numeri mancanti per terno: 3.")
```

Esempio di output non accessibile:
```python
print(f"🎯 Cartella 1 | Ambo: 2 | Terno: 3")
```

---

## 🎯 Promemoria Finale

**Quando l'utente chiede modifiche:**
1. ✅ Applica modifiche con type hints completi
2. ✅ Aggiungi logging semantico (no print)
3. ✅ Verifica accessibilità (keyboard, screen reader, NVDA)
4. ✅ Audit documentazione (proponi sync)
5. ✅ Esegui test coverage check
6. ✅ Fornisci riepilogo testuale strutturato

**Frase magica per audit completo:**
*"Codice, documentazione e test sono sincronizzati al 100% secondo gli standard Tombola Stark."*

Quando l'utente la richiede, esegui tutti i 6 check pre-commit + verifica manuale cross-references docs prima di confermare sync.

---
