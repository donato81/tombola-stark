# 🏗️ ARCHITECTURE.md - Tombola Stark

> **Documentazione architetturale di tombola-stark**  
> Ultimo aggiornamento: 2026-02-19 (v0.5.0)

---

## 📋 Scopo del Documento

Questo documento descrive l'**architettura corrente** di tombola-stark.

**Target**:
- Nuovi sviluppatori (onboarding)
- Contributori (capire le decisioni di design)
- Manutentori (garanzia di coerenza)
- Il futuro te stesso (ricordare il perché)

**Cosa c'è qui**:
- Panoramica del sistema
- Architettura a livelli e regole di dipendenza
- Pattern chiave e convenzioni
- Struttura delle directory
- Motivazioni delle scelte architetturali principali
- Architettura dell'accessibilità

**Cosa NON c'è qui**:
- Dettagli implementativi (vedere codice sorgente)
- Riferimento API (vedere `API.md`)
- Tutorial passo-passo (vedere `README.md`)

---

## 🎯 Panoramica del Sistema

### Cosa Fa Questo Progetto

**Tombola Stark** è un'implementazione accessibile del classico gioco della tombola italiana, progettata per essere giocata tramite tastiera e compatibile con screen reader. Il sistema gestisce partite con 1 giocatore umano e fino a 7 bot automatici, estraendo numeri da 1 a 90, assegnando premi (ambo, terno, quaterna, cinquina, tombola) e notificando il giocatore tramite output strutturato pronto per la vocalizzazione TTS.

Il progetto pone l'**accessibilità come requisito di primo livello**: ogni evento di gioco produce un output strutturato (dizionari, eventi) che uno strato superiore può vocalizzare senza modificare la logica di dominio.

### Paradigmi Architetturali

- **Separazione delle responsabilità**: Logica di gioco (dominio), orchestrazione (controller) e interfaccia sono livelli distinti con dipendenze unidirezionali.
- **Domain-Driven Design leggero**: Le regole di business (estrazione, verifica premi, tombola) vivono esclusivamente nel livello dominio.
- **Accessibility-First**: Il sistema di eventi (`bingo_game/events/`) è progettato per fornire messaggi strutturati pronti per TTS senza accoppiare il dominio a librerie UI.
- **Fail-safe Controller**: Il `game_controller` intercetta tutte le eccezioni del dominio, impedendo crash dell'interfaccia.

### Tech Stack

**Core**:
- **Python 3.10+** – Type hints, `from __future__ import annotations`, modern syntax
- **Standard Library** (`random`, `typing`, `dataclasses`) – Nessuna dipendenza esterna per il motore di gioco

**Testing**:
- **Pytest** – Test unitari e di integrazione (cartella `tests/`)

**Dipendenze** (`requirements.txt`):
- Librerie di supporto per l'interfaccia e l'accessibilità

---

## 🏛️ Architettura a Livelli

### Panoramica

Il sistema adotta una separazione a tre livelli principali con regole di dipendenza chiare. Ogni livello ha una responsabilità precisa e dipende solo dai livelli "interni". Il Dominio è il nucleo e non ha dipendenze esterne.

### Diagramma delle Dipendenze

```
┌───────────────────────────────────────────────┐
│          LIVELLO INTERFACCIA (futuro)          │
│  (UI terminale, screen reader, TTS, pannelli) │
│  Dipende da: Controller + Sistema Eventi       │
└───────────────────────────────────────────────┘
                      ↓ dipende da
┌───────────────────────────────────────────────┐
│          LIVELLO CONTROLLER                    │
│  (game_controller.py, comandi_partita.py)      │
│  Orchestrazione sicura, gestione eccezioni     │
└───────────────────────────────────────────────┘
                      ↓ dipende da
┌───────────────────────────────────────────────┐
│          LIVELLO DOMINIO                       │
│  (tabellone.py, cartella.py, partita.py,       │
│   players/, events/, exceptions/, validations/)│
│  ← ZERO dipendenze da livelli esterni          │
└───────────────────────────────────────────────┘

┌───────────────────────────────────────────────┐
│   INFRASTRUTTURA TRASVERSALE (Logging)         │
│  (bingo_game/logging/game_logger.py)           │
│  Accessibile da: Controller + Interfaccia      │
│  ← NON accessibile dal Dominio                 │
└───────────────────────────────────────────────┘
```

### Dettaglio dei Livelli

---

#### Livello Dominio (`bingo_game/`)

**Scopo**: Tutta la logica di business del gioco della tombola. Completamente indipendente da framework UI, librerie TTS e qualsiasi layer esterno.

**Componenti**:

| File / Directory | Ruolo |
|---|---|
| `tabellone.py` | Gestione numeri 1-90, estrazioni, storico |
| `cartella.py` | Cartella giocatore, segnatura numeri, verifica premi |
| `partita.py` | Coordinamento tabellone + giocatori, ciclo di gioco |
| `players/giocatore_base.py` | Classe base comune a tutti i giocatori |
| `players/giocatore_umano.py` | Giocatore umano con supporto eventi UI |
| `players/giocatore_automatico.py` | Bot automatico |
| `players/helper_focus.py` | Helper per la gestione del focus (accessibilità) |
| `players/helper_reclami_focus.py` | Helper per i reclami di vittoria |
| `events/` | Sistema di eventi strutturati |
| `exceptions/` | Gerarchia eccezioni personalizzate per ogni modulo |
| `validations/` | Logica di validazione riutilizzabile |

**Regole di Dipendenza**:
- ✅ Può dipendere da: altri componenti del dominio, standard library Python
- ❌ Non può dipendere da: controller, framework UI, librerie TTS esterne

**Esempio**:
```python
# bingo_game/partita.py - Pura logica di dominio
class Partita:
    def esegui_turno(self) -> dict:
        """Logica di gioco pura: estrae, aggiorna, verifica premi."""
        numero = self.estrai_prossimo_numero()
        premi = self.verifica_premi()
        tombola = self.has_tombola()
        if tombola:
            self.termina_partita()
        return {"numero_estratto": numero, "premi_nuovi": premi, ...}
```

---

#### Livello Controller (`bingo_game/game_controller.py`, `bingo_game/comandi_partita.py`)

**Scopo**: Orchestrazione dei casi d'uso. Fa da collante tra dominio e interfaccia. Non contiene logica di business: delega sempre al dominio e gestisce le eccezioni in modo sicuro.

**Funzioni principali** (in `game_controller.py`):
- `crea_partita_standard()` – Factory completa per una partita configurata
- `avvia_partita_sicura()` – Avvio con gestione sicura delle eccezioni
- `esegui_turno_sicuro()` – Esecuzione turno con intercettazione di tutti gli errori
- `ottieni_stato_sintetico()` – Snapshot validato per l'interfaccia
- `ha_partita_tombola()` / `partita_terminata()` – Sensori di stato per il loop di gioco

**Regole di Dipendenza**:
- ✅ Può dipendere da: livello dominio, standard library
- ❌ Non contiene: logica di business, codice UI, stringhe di vocalizzazione

**Esempio**:
```python
# game_controller.py - Orchestrazione sicura
def avvia_partita_sicura(partita: Partita) -> bool:
    try:
        partita.avvia_partita()  # Delega al dominio
        return True
    except PartitaGiocatoriInsufficientiException:
        print("❌ Giocatori insufficienti")
        return False
```

---

#### Livello Interfaccia (previsto / in sviluppo)

**Scopo**: Presentazione degli stati di gioco tramite terminale, vocalizzazione TTS, screen reader.

**Dipende da**:
- Controller (per ottenere risultati sicuri)
- Sistema `bingo_game/events/` (per messaggi strutturati pronti per TTS)
- Librerie TTS esterne (es. `pyttsx3`) o framework terminal (es. `curses`)

**File previsti**:
- `bingo_game/ui/` (directory presente, da implementare)

---

#### Infrastruttura di Logging (trasversale)

**Scopo**: Sistema di logging centralizzato che traccia eventi di gioco, eccezioni e stato senza accoppiare il dominio a dipendenze esterne. È una **cross-cutting concern** accessibile solo da Controller e Interfaccia.

**Componenti**:

| File / Directory | Ruolo |
|---|---|
| `bingo_game/logging/game_logger.py` | Singleton `GameLogger` con file cumulativo e flush immediato |
| `logs/tombola_stark.log` | File di log cumulativo (append mode, non versionato) |

**Caratteristiche**:
- **Singleton**: Un'unica istanza condivisa per tutta l'applicazione
- **Flush immediato**: Ogni riga è scritta su disco immediatamente (leggibile in tempo reale)
- **Modalità DEBUG/INFO**: Controllata dal flag `--debug` in `main.py`
- **Marcatori di sessione**: Separano visivamente le esecuzioni nel file cumulativo
- **Sub-logger per categoria**: 
  - `tombola_stark.game` → eventi ciclo di vita partita (`[GAME]`)
  - `tombola_stark.prizes` → premi assegnati (`[PRIZE]`)
  - `tombola_stark.system` → configurazione e infrastruttura (`[SYS]`)
  - `tombola_stark.errors` → eccezioni e anomalie (`[ERR]`)

**Regole di Dipendenza** (CRITICHE):
- ✅ Può essere usato da: Controller (`game_controller.py`), Interfaccia (`main.py`)
- ❌ **NON può essere usato da**: Dominio (`tabellone.py`, `partita.py`, `cartella.py`, `players/`, `events/`, `exceptions/`)
- ❌ Il logging **non deve mai interrompere il gioco**: tutte le chiamate sono wrappate in `try/except Exception: pass`

**Esempio di utilizzo corretto**:
```python
# game_controller.py - ✅ CORRETTO: Solo il controller logga
from bingo_game.logging import GameLogger

def _log_safe(message, level="info", *args, logger=None):
    try:
        target = logger or GameLogger.get_instance()
        getattr(target, level)(message, *args)
    except Exception:
        pass  # Silenzioso in caso di errore

def avvia_partita_sicura(partita: Partita) -> bool:
    try:
        partita.avvia_partita()
        _log_safe("[GAME] Partita avviata — giocatori: %d", partita.get_numero_giocatori())
        return True
    except Exception as exc:
        _log_safe("[ERR] Avvio fallito: %s", "warning", str(exc))
        return False
```

**Esempio di uso errato** (da evitare):
```python
# bingo_game/partita.py - ❌ ERRATO: Il dominio NON logga mai
from bingo_game.logging import GameLogger  # ❌ VIETATO

class Partita:
    def esegui_turno(self):
        GameLogger.get_instance().info("Turno")  # ❌ VIETATO
        # ...
```

**Motivazione architetturale**:
Il dominio deve restare puro e privo di dipendenze esterne (ADR-001, ADR-003). Il logging è una concern dell'infrastruttura, non del business. Il controller intercetta già tutti gli eventi rilevanti e può aggiungervi logging senza inquinare il dominio.

---

## 🔒 Regole di Dipendenza

### La Regola d'Oro

> **Le dipendenze puntano sempre verso l'interno.**  
> Il Dominio è il nucleo e ha ZERO dipendenze esterne.  
> I livelli esterni dipendono da quelli interni, mai il contrario.

### Dipendenze Consentite

```
Interfaccia → Controller → Dominio
Interfaccia → Sistema Eventi (bingo_game/events/)
```

### Dipendenze Vietate

```
Dominio → Controller         ❌
Dominio → Librerie UI/TTS    ❌
Dominio → Stringhe localizzate ❌
Controller → Framework UI    ❌
```

### Violazioni Comuni da Evitare

#### 1. Logica di gioco nel Controller

**❌ SBAGLIATO**:
```python
# game_controller.py
def esegui_turno(partita):
    numero = random.randint(1, 90)  # ❌ Logica nel controller
    partita.ultimo_numero_estratto = numero
```

**✅ CORRETTO**:
```python
# game_controller.py
def esegui_turno_sicuro(partita):
    risultato = partita.esegui_turno()  # ✅ Delega al dominio
    return risultato
```

#### 2. Stringhe UI nel Dominio

**❌ SBAGLIATO**:
```python
# partita.py
def esegui_turno(self):
    print("Tombola! Hai vinto!")  # ❌ Output UI nel dominio
```

**✅ CORRETTO**:
```python
# partita.py
def esegui_turno(self):
    return {"tombola_rilevata": True, ...}  # ✅ Dato strutturato

# Interfaccia:
if turno["tombola_rilevata"]:
    speak("Tombola! Hai vinto!")  # ✅ UI parla
```

---

## 🎓 Pattern Architetturali Chiave

### Pattern 1: Output Strutturato per Accessibilità

**Dove usato**: `Partita.esegui_turno()`, `Partita.get_stato_completo()`, `game_controller.esegui_turno_sicuro()`

**Scopo**: Ogni azione di gioco ritorna un dizionario con dati strutturati (non stringhe formattate), permettendo all'interfaccia di comporre messaggi TTS nella lingua/stile preferito senza modificare il dominio.

```python
# Dominio ritorna dati strutturati
risultato = partita.esegui_turno()
# → {"numero_estratto": 42, "premi_nuovi": [{"giocatore": "Mario", "premio": "ambo", ...}]}

# Interfaccia compone il messaggio
if risultato["tombola_rilevata"]:
    speak("Tombola!")
for premio in risultato["premi_nuovi"]:
    speak(f"{premio['giocatore']} ha fatto {premio['premio']}!")
```

**Motivazione**: Il dominio rimane UI-agnostic. L'interfaccia (terminale, TTS, GUI) può cambiare completamente senza toccare la logica di gioco.

---

### Pattern 2: Gerarchia Eccezioni per Livello

**Dove usato**: `bingo_game/exceptions/`

**Scopo**: Ogni modulo del dominio ha le proprie eccezioni specifiche, organizzate in una gerarchia. Il controller intercetta solo le eccezioni pertinenti.

**Struttura**:
```
Exception
└── PartitaException
    ├── PartitaStatoException
    │   ├── PartitaGiaIniziataException
    │   ├── PartitaNonInCorsoException
    │   └── PartitaGiaTerminataException
    ├── PartitaRosterException
    │   ├── PartitaRosterPienoException
    │   ├── PartitaGiocatoriInsufficientiException
    │   ├── PartitaGiocatoreTypeException
    │   └── PartitaGiocatoreGiaPresenteException
    └── PartitaGiocoException
        └── PartitaNumeriEsauritiException
```

**Motivazione**: Il controller può fare `except PartitaException` come catch-all sicuro, oppure gestire casi specifici con eccezioni granulari.

---

### Pattern 3: Controller Fail-Safe

**Dove usato**: `game_controller.avvia_partita_sicura()`, `game_controller.esegui_turno_sicuro()`

**Scopo**: Le funzioni `*_sicuro()` non propagano mai eccezioni all'interfaccia. In caso di errore, ritornano `False` o `None`.

```python
def esegui_turno_sicuro(partita) -> Optional[dict]:
    try:
        return partita.esegui_turno()
    except PartitaNonInCorsoException:
        print("❌ Partita non in corso")
        return None
    except PartitaException:
        print("❌ Errore partita")
        return None
    except Exception:
        raise  # Solo errori critici imprevisti propagano
```

---

### Pattern 4: Sistema di Eventi per la Vocalizzazione

**Dove usato**: `bingo_game/events/`

**Scopo**: Il sistema di eventi fornisce oggetti strutturati che disaccoppiano la produzione di informazioni di gioco dalla loro presentazione.

**File**:
- `eventi_partita.py` – `ReclamoVittoria`, `EventoFineTurno`
- `eventi_output_ui_umani.py` – Messaggi strutturati per output terminale/TTS
- `codici_errori.py`, `codici_eventi.py`, `codici_messaggi_sistema.py`, `codici_output_ui_umani.py` – Costanti di categorizzazione

---

## 📂 Struttura Directory

```
tombola-stark/
├── bingo_game/                  # Pacchetto principale del gioco
│   ├── __init__.py
│   ├── tabellone.py             # Dominio: gestione estrazioni
│   ├── cartella.py              # Dominio: cartella e verifica premi
│   ├── partita.py               # Dominio: coordinamento partita
│   ├── game_controller.py       # Controller: orchestrazione sicura
│   ├── comandi_partita.py       # Controller: comandi di partita
│   ├── utils.py                 # Utility (placeholder)
│   ├── players/                 # Dominio: gerarchia giocatori
│   │   ├── __init__.py
│   │   ├── giocatore_base.py
│   │   ├── giocatore_umano.py
│   │   ├── giocatore_automatico.py
│   │   ├── helper_focus.py
│   │   └── helper_reclami_focus.py
│   ├── events/                  # Sistema di eventi strutturati
│   │   ├── __init__.py
│   │   ├── eventi.py
│   │   ├── eventi_partita.py
│   │   ├── eventi_ui.py
│   │   ├── eventi_output_ui_umani.py
│   │   ├── codici_errori.py
│   │   ├── codici_eventi.py
│   │   ├── codici_messaggi_sistema.py
│   │   └── codici_output_ui_umani.py
│   ├── exceptions/              # Gerarchia eccezioni per modulo
│   │   ├── __init__.py
│   │   ├── partita_exceptions.py
│   │   ├── cartella_exceptions.py
│   │   ├── giocatore_exceptions.py
│   │   ├── game_controller_exceptions.py
│   │   └── tabellone_exceptions.py
│   ├── validations/             # Logica di validazione
│   └── ui/                      # Placeholder interfaccia futura
├── my_lib/                      # Libreria di supporto
├── tests/                       # Suite di test
├── documentations/
│   ├── API.md                   # Questo file (riferimento API)
│   ├── ARCHITECTURE.md          # Questo file (architettura)
│   └── templates/
│       ├── TEMPLATE_example_API.md
│       └── TEMPLATE_example_ARCHITECTURE.md
├── main.py                      # Entry point
├── requirements.txt
└── README.md
```

### Responsabilità per Directory

#### `bingo_game/` (root)
- File di dominio principali: `tabellone.py`, `cartella.py`, `partita.py`
- Controller: `game_controller.py`, `comandi_partita.py`
- Nessuna logica UI, nessuna stringa localizzata

#### `bingo_game/players/`
- Gerarchia giocatori: base → umano / automatico
- Helper per accessibilità (focus, reclami)

#### `bingo_game/events/`
- Oggetti evento per disaccoppiare produzione e consumo
- Codici costanti per categorizzazione eventi e messaggi

#### `bingo_game/exceptions/`
- Un file per ogni modulo di dominio
- Gerarchia chiara: eccezione base → specializzazioni

#### `tests/`
- Test unitari per dominio (isolati)
- Test di integrazione per flussi multi-livello

---

## 🔄 Flusso dei Dati

### Flusso Tipico: Esecuzione di un Turno

```
1. [Interfaccia] Utente preme tasto "Estrai"
   │
   ↓ chiama
   │
2. [Controller] esegui_turno_sicuro(partita)
   │ Verifica stato, gestisce eccezioni
   │
   ↓ chiama
   │
3. [Dominio] Partita.esegui_turno()
   │  ├─ Tabellone.estrai_numero()           → int
   │  ├─ GiocatoreBase.aggiorna_con_numero() → aggiorna cartelle
   │  └─ Partita.verifica_premi()            → List[dict]
   │
   ↓ ritorna dict
   │
4. [Controller] Valida dict, ritorna Optional[dict]
   │
   ↓ ritorna a interfaccia
   │
5. [Interfaccia] Legge dict e vocalizza:
   │  ├─ numero_estratto  → "Estratto: 42"
   │  ├─ premi_nuovi      → "Mario ha fatto ambo!"
   │  └─ tombola_rilevata → "TOMBOLA!"
```

### Diagramma di Sequenza (Creazione Partita)

```
UI         Controller          Dominio
│               │                  │
│--crea_partita→│                  │
│               │--Tabellone()---> │
│               │--GiocatoreUmano→ │
│               │--GiocatoreAuto→  │
│               │--Partita(t, g)→  │
│               │<--partita obj----│
│<--partita obj-│                  │
│               │                  │
│--avvia------->│                  │
│               │--avvia_partita-->│
│               │<--True/False-----│
│<--bool--------│                  │
```

---

## ♿ Architettura dell'Accessibilità

L'accessibilità è un requisito fondamentale e non un'aggiunta postuma.

### Principi

- **Output strutturato prima di tutto**: Ogni evento di gioco produce dati (dict, oggetti evento) che qualsiasi interfaccia può consumare, inclusi screen reader.
- **Nessuna stringa hardcoded nel dominio**: I messaggi in italiano vivono solo nel livello interfaccia o nel sistema `events/`.
- **Navigazione da tastiera**: Nessuna dipendenza dal mouse nell'architettura di controllo.
- **Helper focus dedicati**: `helper_focus.py` e `helper_reclami_focus.py` gestiscono le interazioni di accessibilità del giocatore umano separatamente dalla logica di gioco.

### Sistema di Messaggi per TTS

```python
# Il dominio produce eventi semantici
evento = {
    "giocatore": "Lucia",
    "cartella": 1,
    "premio": "ambo",
    "riga": 0
}

# L'interfaccia (non nel dominio!) compone il messaggio TTS
messaggio = f"{evento['giocatore']} ha fatto {evento['premio']} sulla cartella {evento['cartella']}!"
speak(messaggio)
```

**File `bingo_game/events/eventi_output_ui_umani.py`**: Contiene la logica di composizione dei messaggi strutturati per l'output verso l'interfaccia umana, isolata dal motore di gioco.

### Helper di Accessibilità

- `helper_focus.py`: Gestisce la navigazione del focus tra cartelle e numeri per il giocatore umano
- `helper_reclami_focus.py`: Gestisce il flusso di reclamo di una vincita (l'umano dichiara ambo/tombola nel suo turno)

---

## 🚨 Strategia di Gestione degli Errori

### Filosofia

Gli errori vengono catturati ai confini tra livelli e convertiti in valori di ritorno sicuri o messaggi per l'utente. Il dominio lancia eccezioni specifiche, il controller le intercetta, l'interfaccia vocalizza il risultato.

### Pattern per Livello

**Dominio** → lancia eccezioni specifiche:
```python
if self.stato_partita != "in_corso":
    raise PartitaNonInCorsoException("Impossibile estrarre: partita non avviata.")
```

**Controller** → intercetta, ritorna valore sicuro:
```python
try:
    partita.avvia_partita()
    return True
except PartitaGiaIniziataException as exc:
    print(f"❌ {exc}")
    return False
```

**Interfaccia** → vocalizza all'utente:
```python
if not avvia_partita_sicura(partita):
    speak("Impossibile avviare la partita. Controlla il numero di giocatori.")
```

### Codici di Errore Strutturati

Il modulo `bingo_game/events/codici_errori.py` fornisce costanti per categorizzare gli errori in modo uniforme, permettendo all'interfaccia di mappare i codici a messaggi localizzati.

---

## 🧪 Strategia di Testing

### Approccio

- **Test del dominio in isolamento**: Tabellone, Cartella, GiocatoreBase, Partita testati senza dipendenze dal controller o UI
- **Coverage target**: >80% per il livello dominio
- **Piramide**: Test unitari pesanti (dominio), test di integrazione per flussi controller+dominio

### Test Unitari

```python
def test_estrai_numero_riduce_disponibili():
    t = Tabellone()
    assert t.get_conteggio_disponibili() == 90
    t.estrai_numero()
    assert t.get_conteggio_disponibili() == 89

def test_numeri_terminati_solleva_eccezione():
    t = Tabellone()
    for _ in range(90):
        t.estrai_numero()
    with pytest.raises(ValueError):
        t.estrai_numero()
```

### Test di Integrazione

```python
def test_flusso_partita_completa():
    partita = crea_partita_standard("Test", 1, 1)
    assert avvia_partita_sicura(partita) is True
    assert partita.get_stato_partita() == "in_corso"
    while not partita_terminata(partita):
        turno = esegui_turno_sicuro(partita)
        assert turno is not None
    assert partita.get_stato_partita() == "terminata"
```

---

## 📈 Evoluzione e Sviluppi Futuri

### Storia delle Versioni

- **v0.1.0** (2026-02): Architettura iniziale. Dominio completo (Tabellone, Cartella, Partita, Players). Controller di alto livello implementato. Sistema eventi e gerarchia eccezioni stabiliti.

### Aree di Sviluppo Futuro

- **`bingo_game/ui/`** (directory presente, vuota): Strato interfaccia terminale/TTS da implementare
- **`bingo_game/utils.py`** (file presente, vuoto): Utility di supporto da aggiungere
- **Modalità multiplayer estesa**: Struttura pronta per estensione fino a 8 giocatori

---

## 🎯 Decision Records

### ADR-001: Controller Separato dal Dominio

- **Status**: Accettato
- **Data**: 2026-02
- **Contesto**: Il dominio lancia eccezioni specifiche che non devono mai crashare l'interfaccia
- **Decisione**: Introdurre `game_controller.py` come livello di orchestrazione fail-safe
- **Conseguenze**:
  - ✅ L'interfaccia non deve gestire eccezioni di dominio
  - ✅ Il dominio rimane testabile in isolamento
  - ❌ Un livello extra da mantenere aggiornato con il dominio

---

### ADR-002: Sistema di Eccezioni per Modulo

- **Status**: Accettato
- **Data**: 2026-02
- **Contesto**: Necessità di distinguere errori di stato partita, di roster, di gioco, di giocatore
- **Decisione**: Un file `*_exceptions.py` per ogni modulo di dominio con gerarchia chiara
- **Conseguenze**:
  - ✅ `except PartitaException` come catch-all sicuro nel controller
  - ✅ Messaggi di errore chiari e specifici per ogni scenario
  - ❌ Più file da mantenere sincronizzati con l'evoluzione del dominio

---

### ADR-003: Output Strutturato per Accessibilità

- **Status**: Accettato
- **Data**: 2026-02
- **Contesto**: Il gioco deve essere utilizzabile con screen reader senza modificare il dominio
- **Decisione**: Tutti i metodi di stato e ciclo di gioco ritornano dizionari con dati semantici, non stringhe formattate
- **Conseguenze**:
  - ✅ Il dominio è completamente UI-agnostic
  - ✅ Qualsiasi interfaccia può consumare gli stessi dati
  - ❌ L'interfaccia deve implementare la composizione di tutti i messaggi

---

## 📚 Documentazione Correlata

**Interna**:
- `documentations/API.md` – Riferimento API pubblico per tutte le classi e funzioni
- `documentations/templates/` – Template per nuovi documenti
- `README.md` – Guida utente e installazione

---

*Ultimo aggiornamento: 2026-02-19 (v0.5.0)*  
*Documento vivente: aggiornare ad ogni cambiamento architetturale significativo.*
