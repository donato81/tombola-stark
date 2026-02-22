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
from bingo_game.game_controller import ottieni_stato_sintetico, esegui_turno_sicuro

def gestisci_comando_cartella(numero: str) -> None:
    esito = esegui_turno_sicuro('imposta_focus_cartella', int(numero))
    if esito.ok:
        renderer.render(esito.evento)
    else:
        renderer.render_errore(esito.errore)
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

### Logging (Sistema Categorizzato v0.4.0)

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

**Usare i semantic helpers di `game_logger.py`:**
```python
from bingo_game.logging.game_logger import (
    GameLogger,
)
```

**Vietato:**
- ❌ `print(f"Debug: {variable}")` → usa `logging.getLogger('tombola_stark.partita').debug()`
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

### Struttura Cartella `docs/`

```
docs/
├── 1 - templates/          # Template riutilizzabili (PR body, design doc, TODO)
├── 2 - projects/           # Design doc e piani pre-merge per feature attive
│   ├── DESIGN_*.md         # Analisi architetturale di una feature
│   └── PLAN_*.md           # Piano di implementazione/fix con checklist
├── 3 - coding plans/       # Piani di coding dettagliati (step-by-step implementazione)
├── API.md                  # Riferimento API pubblica di tutti i moduli
├── ARCHITECTURE.md         # Architettura del sistema e data flow
├── TESTING.md              # Guida testing e convenzioni
└── TODO.md                 # Cruscotto operativo del branch attivo (stato: IN PROGRESS / DONE)
```

**Regole di posizionamento:**
- Un nuovo design doc → `docs/2 - projects/DESIGN_<feature>.md`
- Un piano di fix/implementazione → `docs/2 - projects/PLAN_<descrizione>_vX.Y.Z.md`
- `docs/TODO.md` esiste solo durante un branch di lavoro attivo; è il cruscotto
  operativo da spuntare durante l'implementazione. Va aggiornato dopo ogni commit.

---

### Creazione File di Progetto (Design Doc, Piano, TODO)

Ogni nuovo task non banale richiede la creazione di uno o più file di progetto **prima** di scrivere codice. I modelli si trovano in `docs/1 - templates/`.

#### Quando creare un DESIGN Document

**Trigger (almeno uno dei seguenti):**
- L'utente descrive una nuova feature con comportamento non ovvio
- Il task implica decisioni architetturali (nuovo layer, nuovo pattern, nuovi attori)
- La feature coinvolge più di 3 file distinti in layer diversi
- Ci sono alternative di design da confrontare

**Template da usare:** `docs/1 - templates/TEMPLATE_example_DESIGN_DOCUMENT.md`

**Nome file output:** `docs/2 - projects/DESIGN_<feature-slug>.md`

**Contenuto minimo obbligatorio:**
- Metadata (data, stato, versione target)
- Idea in 3 righe (cosa, perché, problema risolto)
- Attori e concetti chiave
- Flussi concettuali (no decisioni tecniche in questa fase)

**Esempio creazione:**
```
Utente: "Voglio aggiungere un sistema audio con varianti per difficoltà"
→ Crea: docs/2 - projects/DESIGN_audio_system.md
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

**Template da usare:** `docs/1 - templates/TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`

**Nome file output:** `docs/2 - projects/PLAN_<descrizione-slug>_vX.Y.Z.md`

**Contenuto minimo obbligatorio:**
- Executive Summary (tipo, priorità, stato, branch, versione target)
- Problema/Obiettivo (o Root Cause se bugfix)
- Lista file coinvolti con tipo operazione (CREATE / MODIFY / DELETE)
- Fasi di implementazione in ordine sequenziale
- Test plan (unit + integration)
- Criteri di completamento

**Esempio creazione:**
```
Utente: "Implementa il sistema audio descritto nel DESIGN"
→ Crea: docs/2 - projects/PLAN_audio-system_v3.4.0.md
→ Usa: TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md come base
→ Stato iniziale: DRAFT → poi READY prima del primo commit
```

---

#### Quando creare/aggiornare il TODO

**Trigger creazione (tutti devono essere veri):**
- Esiste un PLAN approvato (stato READY)
- Il branch di lavoro è attivo
- L'implementazione multi-fase è appena iniziata

**Template da usare:** `docs/1 - templates/TEMPLATE_exaple_TODO.md`

**Nome file output:** `docs/TODO.md` (uno solo, sostituisce il precedente ad ogni branch)

**Regole operative:**
- Il TODO è un **cruscotto**, non un documento tecnico: sommario operativo consultabile in 30 secondi
- Il link al PLAN completo (fonte di verità) deve essere in cima al TODO
- Ogni checkbox spuntata corrisponde a un commit già eseguito
- Va aggiornato **dopo ogni commit**, non in batch a fine lavoro
- Al merge su `main` il TODO viene archiviato o eliminato

**Contenuto minimo obbligatorio:**
- Riferimento al PLAN completo (link relativo)
- Istruzioni per Copilot Agent (workflow incrementale)
- Obiettivo in 3-5 righe
- Lista file coinvolti
- Checklist implementazione per layer
- Criteri di completamento

**Esempio aggiornamento post-commit:**
```
Dopo commit "feat(domain): aggiunto AudioEvent model":
→ Apri docs/TODO.md
→ Spunta: [x] Modifica modello / entità (Domain layer)
→ Salva e includi nel commit successivo (o commit separato "docs: aggiorna TODO fase 1")
```

---

#### Relazione tra i Tre File (Flusso Canonico)

```
DESIGN_<feature>.md          (CONCEPT - "cosa vogliamo")
      ↓  approva
PLAN_<feature>_vX.Y.Z.md     (TECNICO - "come lo facciamo")
      ↓  inizia
docs/TODO.md                 (OPERATIVO - "dove siamo")
      ↓  aggiorna dopo ogni commit
      ↓  a merge completato → archivia/elimina TODO
```

**Vincoli di sequenza:**
- Non creare un PLAN senza aver prima chiarito i requisiti (DESIGN o discussione esplicita)
- Non iniziare commit di codice senza un TODO aggiornato se il task ha più di 2 fasi
- Non modificare uno DESIGN doc a FROZEN senza aggiornare il PLAN corrispondente

#### Workflow Completo di Creazione (Step-by-Step)

Quando l'utente introduce un nuovo task significativo:

1. **Valuta la complessità**: meno di 2 file e 1 commit → nessun file di progetto necessario
2. **Crea DESIGN** (se architetturale): copia `TEMPLATE_example_DESIGN_DOCUMENT.md`, compila sezioni obbligatorie, salva in `docs/2 - projects/`
3. **Crea PLAN**: copia `TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`, collega al DESIGN se esiste, definisci fasi, salva in `docs/2 - projects/`
4. **Crea TODO**: copia `TEMPLATE_exaple_TODO.md`, metti link al PLAN in cima, trascrivi le fasi come checklist, salva come `docs/TODO.md`
5. **Inizia implementazione**: segui il workflow incrementale descritto nel TODO
6. **Aggiorna TODO** dopo ogni commit (spunta checkbox)
7. **A merge completato**: aggiorna CHANGELOG, archivia o elimina `docs/TODO.md`

---

### Trigger Events (quando aggiornare docs)

Dopo **ogni modifica al codice** (`.py`), esegui questo audit:

**1. API.md**  
Aggiorna se modifichi:
- Signature metodi pubblici (parametri, return type, nome)
- Classi esportate da `__init__.py`
- Enum/costanti pubbliche
- Comportamento documentato (side effects, validazioni)

**Esempio:**
```python
# Prima
def create_profile(self, name: str, set_as_default: bool = False) -> Optional[UserProfile]:

# Dopo
def create_profile(self, name: str, is_guest: bool = False) -> Optional[UserProfile]:
```
→ **Aggiorna `docs/API.md`**: sezione `## GiocatoreUmano.imposta_focus_cartella` — parametro aggiunto, aggiorna esempio d'uso

---

**2. ARCHITECTURE.md**  
Aggiorna se modifichi:
- Struttura cartelle (`bingo_game/`, `docs/`, `tests/`)
- Data flow tra layer (nuovi adapter, repositories)
- Design patterns adottati (nuovi command, observers)
- Dipendenze esterne (nuove librerie in `requirements.txt`)

**Esempio:**
- Aggiungi `bingo_game/events/` per event sourcing
→ **Aggiorna `docs/ARCHITECTURE.md`**: sezione "Domain Layer" + diagramma struttura cartelle

---

**3. CHANGELOG.md**  
Aggiorna **sempre** dopo merge su `main`:
- Nuove feature → sezione `## [Unreleased] - Added`
- Bug fix → `## [Unreleased] - Fixed`
- Breaking changes → `## [Unreleased] - Changed` + ⚠️ warning

**Formato:**
```markdown
## [Unreleased]

### Added
- GiocatoreUmano: Aggiunto metodo `ottieni_stato_focus()` per informazioni focus corrente (#PR)

### Fixed
- API.md: Corretto return type `ensure_guest_profile()` (None → bool) (#Issue)

### Changed
- ⚠️ BREAKING: `create_profile()` parametro `set_as_default` rinominato `is_guest`
```

---

**4. README.md**  
Aggiorna se modifichi:
- Entry point (`acs.py` → `acs_wx.py`)
- Comandi CLI (nuove opzioni `--verbose`, `--profile`)
- Requisiti sistema (Python 3.9 → 3.11, nuove dipendenze)
- Setup environment (nuovi passi installazione)

---

### Workflow di Sync (Step-by-Step)

Quando l'utente dice *"applica le modifiche"*:

1. **Esegui modifiche codice** (`.py` files)
2. **Audit immediato**:
   ```
   Modifiche a bingo_game/players/giocatore_umano.py (line 105):
   - Cambiato return type: None → bool
   
   📋 Impatto documentazione:
   - docs/API.md: ✅ Richiede aggiornamento (sezione GiocatoreUmano.imposta_focus_cartella)
   - docs/ARCHITECTURE.md: ⬜ Nessun impatto
   - CHANGELOG.md: ✅ Aggiungi entry [Unreleased] - Fixed
   ```
3. **Proposta aggiornamento**:
   ```
   Vuoi che aggiorni:
   1. docs/API.md (fix return type + esempio)
   2. CHANGELOG.md (entry Fixed)
   
   Rispondi "sì" per procedere, "solo 1" per docs/API.md, "no" per saltare.
   ```
4. **Applica aggiornamenti docs** se confermato
5. **Verifica finale**:
   ```
   ✅ Codice e documentazione sincronizzati:
   - bingo_game/players/giocatore_umano.py (modified)
   - docs/API.md (updated, sezione GiocatoreUmano.imposta_focus_cartella)
   - CHANGELOG.md (updated, [Unreleased] section)
   ```

---

### Integrità Link e Cross-References

Prima di chiudere un task, verifica:

- [ ] Ogni file Python pubblico ha entry in `docs/API.md`
- [ ] Ogni sezione `docs/API.md` ha link a `docs/ARCHITECTURE.md` per contesto
- [ ] `docs/TODO.md` riflette task aperti (nessun TODO completato dimenticato)
- [ ] `CHANGELOG.md` ha entry per ogni modifica in `main`
- [ ] Nessun link rotto (es. `[GiocatoreUmano](docs/API.md#giocatoreumano)` → verifica anchor esiste)

**Comando verifica** (chiedi all'utente di eseguire):
```bash
# Verifica link rotti in Markdown
grep -r '\[.*\](.*)' docs/ | grep -v http | while read line; do
  # Parse e verifica esistenza file/anchor
done
```

---

## 🛠️ Testing e Validazione

### Test Coverage Requirement

- **Minimum**: 85% coverage per `bingo_game/players/` e `bingo_game/events/`
- **Target**: 90%+ coverage globale
- Ogni nuovo metodo pubblico **deve** avere almeno 1 test unitario

**Comando pre-commit:**
```bash
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=85
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
        # Arrange
        # (fixture già pronta)

        # Act
        esito = giocatore.imposta_focus_cartella(1)

        # Assert
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

### Marker Pytest e CI Strategy

**Marker obbligatori — applicali sempre:**

```python
@pytest.mark.unit   # Test senza dipendenze esterne (no wx, no filesystem reale)
@pytest.mark.gui    # Test che richiedono wx e display (Xvfb o Windows)
```

**Regole di assegnazione:**
- Test che usano solo `tmp_path`, mock, o oggetti puri → `@pytest.mark.unit`
- Test che istanziano `wx.App`, dialog, o frame → `@pytest.mark.gui`
- Test di integrazione tra layer senza UI → `@pytest.mark.unit`

**Comandi standard:**
```bash
# CI-safe (headless, niente display): smoke test obbligatorio pre-merge
pytest -m "not gui" -v

# Test completi (richiede display o Xvfb)
pytest -v

# Solo unit test di un modulo specifico (esempio)
pytest tests/infrastructure/test_categorized_logger.py -v
```

**Isolamento test logging:** il modulo `logging` di Python è un singleton di
processo. Qualsiasi test che chiama `setup_logging()` o `setup_categorized_logging()`
**deve** avere una fixture `reset_logging` con cleanup pre+post yield. Vedi
`tests/infrastructure/test_categorized_logger.py` come riferimento canonico.

---

## 🔍 Pre-Commit Checklist (Auto-Eseguita)

Prima di ogni commit, verifica silentemente:

1. **Syntax**: `python -m py_compile bingo_game/**/*.py` (0 errori)
2. **Type Hints**: `mypy bingo_game/ --strict --python-version 3.8` (0 errori, 100% copertura type hints)
3. **Imports**: `pylint bingo_game/ --disable=all --enable=cyclic-import` (nessun import circolare)
4. **Logging**: `grep -r "print(" bingo_game/ --include="*.py" --exclude="__main__.py"` (must return 0 occorrenze)
5. **Docs Sync**: Changelog modificato nelle ultime 48h? (verifica manuale)
6. **Tests**: `pytest tests/ --cov=bingo_game --cov-report=term --cov-fail-under=85` (100% pass, coverage >= 85%)

**Output esempio comando Git:**
```bash
# Ottenere SHA prima di update file
git ls-tree HEAD bingo_game/players/giocatore_umano.py

# Output:
# 100644 blob 47f9717e9064973963357a3cbf64eac57b4a8fe3	bingo_game/players/giocatore_umano.py
#              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#              Questo è il SHA da usare in create_or_update_file
```

**Se uno fallisce:**
```
⚠️ Pre-commit check FAILED:
- mypy: Found 3 type errors in bingo_game/players/giocatore_umano.py
- docs: CHANGELOG.md non aggiornato (ultima modifica: 2 giorni fa)

Vuoi che fixo automaticamente o preferisci revisione manuale?
```

---

## 📝 Convenzioni Git Commit

### Atomic Commits Policy

**Un commit = una unità logica di cambiamento.** Regole operative:

- ✅ Un commit per file modificato se le modifiche hanno motivazioni diverse
- ✅ Un commit per task logico (es. "fix firma", "aggiunta test", "fix docstring")
- ❌ No mega-commit che mescolano fix di codice + aggiornamenti docs + test
- ❌ No commit "WIP" o "fix fix fix" su branch destinati alla PR

**Ordine di commit consigliato** quando si lavora su un task con dipendenze:
1. Pre-requisiti (es. aggiungere un parametro a una firma)
2. Implementazione principale
3. Test
4. Aggiornamento documentazione (API.md, CHANGELOG.md)
5. Aggiornamento cruscotto operativo (TODO.md)

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

**Scope:** `domain`, `application`, `infrastructure`, `presentation`, `docs`, `tests`

**Esempio:**
```
fix(domain): corretto return type GiocatoreUmano.imposta_focus_cartella

- Cambiato da `-> None` a `-> bool`
- Aggiornato docs/API.md sezione GiocatoreUmano
- Aggiunto test per error handling (coverage +2%)

Refs: #42, docs/3 - coding plans/PLAN-docs-allineamento-v3.2.2.md
```

---

## 🌿 Branch Workflow e Release Process

### Naming branch

| Tipo | Pattern | Esempio |
|---|---|---|
| Feature | `feature/<slug>` | `feature/timer-overtime` |
| Fix | `fix/<slug>` | `fix/focus-cartella-crash` |
| Hotfix | `hotfix/<slug>` | `hotfix/guest-profile-null` |
| Refactor | `refactor/<slug>` | `refactor/clean-arch-domain` |
| Docs | `docs/<slug>` | `docs/api-update-v3.3` |

### Quando creare un branch vs committare su `main`

- **Branch separato**: qualsiasi feature, fix non banale, refactor, o lavoro
  che richiede più di 1 commit.
- **Commit diretto su `main`**: solo hotfix monocommit urgenti o aggiornamenti
  di documentazione pura (nessun `.py` modificato).

### Release process (step obbligatori)

1. Tutti i fix e i task del branch completati e verificati
2. PR aperta verso `main` con body che linka design doc e piano (se esistono)
3. Checklist PR spuntata (vedi template `docs/1 - templates/`)
4. Merge con **merge commit** (`--no-ff`) — preserva storia del branch
5. Subito dopo il merge, creare il tag di versione:
   ```bash
   git checkout main && git pull origin main
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
6. Aggiornare footer `CHANGELOG.md`:
   - Rinominare `## [Unreleased]` in `## [X.Y.Z] — YYYY-MM-DD`
   - Aggiungere nuovo `## [Unreleased]` vuoto in cima
   - Aggiornare i link di comparazione in fondo al file

### Versionamento (SemVer)

- `MAJOR` (X): breaking changes all'API pubblica
- `MINOR` (Y): nuove feature retrocompatibili
- `PATCH` (Z): bug fix retrocompatibili
- `BUILD` (W) *(facoltativo)*: bugfix minori o aggiornamenti di documentazione pura (es. `v3.3.0.1`)

---

## 🚨 Critical Warnings (Non Ignorare Mai)

1. **NO IMPORT DOMAIN DALLA TUI**:
   La TUI (tui_partita.py, tui_menu.py) non deve mai importare classi Domain
   direttamente. Tutto il dominio è accessibile solo tramite game_controller.py.
   - ❌ VIETATO: `from bingo_game.players.giocatore_umano import GiocatoreUmano`
   - ✅ CORRETTO: `from bingo_game.game_controller import ottieni_giocatore_umano`

2. **ESITO_AZIONE: CONTROLLA SEMPRE ok PRIMA DI LEGGERE evento**:
   Ogni metodo di GiocatoreUmano ritorna EsitoAzione. Non accedere mai
   a esito.evento senza aver prima verificato esito.ok is True.
   - ❌ VIETATO: `renderer.render(esito.evento)`
   - ✅ CORRETTO: `if esito.ok: renderer.render(esito.evento)`

3. **FOCUS CARTELLA NON SI AUTO-IMPOSTA NEI COMANDI DI AZIONE**:
   I metodi che modificano stato (segna_numero_manuale, annuncia_vittoria,
   vai_a_riga_avanzata, vai_a_colonna_avanzata) hanno auto_imposta=False.
   Se il focus cartella è None, ritornano errore. È responsabilità dell'utente
   selezionare prima la cartella con imposta_focus_cartella(n).

4. **NESSUN print() NEL CODICE DI PRODUZIONE**:
   Tutta la produzione di output passa per TerminalRenderer.
   Usare print() direttamente nel codice applicativo viola l'architettura
   e produce output non tracciabile e non localizzabile.
   - ❌ VIETATO: `print("Numero segnato!")`
   - ✅ CORRETTO: `_renderer.render(esito.evento)`

5. **NESSUNA STRINGA DI TESTO NEL DOMAIN LAYER**:
   I metodi di GiocatoreUmano, Partita, Tabellone e Cartella non producono
   mai stringhe pronte per l'utente. Producono solo EsitoAzione con eventi
   dati. Le stringhe esistono solo in ui/locales/it.py e vengono assemblate
   dal TerminalRenderer.

---

## 🎯 Output verso NVDA in Tombola Stark

NVDA su Windows 11 legge automaticamente l'output standard del terminale (cmd.exe
o Windows Terminal) riga per riga, non appena viene stampato con print().
Non è necessario nessun metodo speak() esplicito.

Per garantire che NVDA legga correttamente ogni messaggio:
- Ogni messaggio deve essere su una riga separata (no \r, no escape ANSI)
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
3. ✅ Verifica accessibilità (ARIA, keyboard, screen reader)
4. ✅ Audit documentazione (proponi sync)
5. ✅ Esegui test coverage check
6. ✅ Fornisci riepilogo testuale strutturato

**Frase magica per audit completo:**
*"Codice, documentazione e test sono sincronizzati al 100% secondo gli standard v2.3+"*

Quando l'utente la richiede, esegui tutti i 6 check pre-commit + verifica manuale cross-references docs prima di confermare sync.

---
