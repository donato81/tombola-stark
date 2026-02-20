# 📋 Piano di Implementazione - Menu Iniziale TUI (Fase 1)

> **Documento operativo pronto per esecuzione tecnica**
> Basato su `DESIGN_TERMINAL_START_MENU.md` v1.2 (stato: READY)

---

## 📊 Executive Summary

**Tipo**: FEATURE
**Priorità**: 🟠 ALTA
**Stato**: READY
**Branch**: `feature/terminal-start-menu`
**Versione Target**: `v0.7.0`
**Data Creazione**: 2026-02-19
**Autore**: AI Assistant + Nemex81
**Effort Stimato**: ~5 ore totali (3 ore Copilot + 2 ore review/testing)
**Commits Previsti**: 6 commit atomici

---

### Problema/Obiettivo

Tombola Stark non ha ancora un'interfaccia da terminale funzionante. Il file `bingo_game/ui/ui_terminale.py` esiste ma è vuoto (0 byte). L'utente non può avviare una partita da terminale.

**Obiettivo**: implementare la **Fase 1** dell'interfaccia TUI accessibile — il flusso di configurazione pre-partita (nome giocatore, numero bot, numero cartelle) — con piena compatibilità screen reader e zero stringhe hardcoded.

---

### Soluzione Proposta

Implementare la classe `TerminalUI` in `ui_terminale.py` come **macchina a stati sequenziale** (stati A→E) che usa esclusivamente `input()` standard Python e testi provenienti dai dizionari di `it.py`. La soluzione richiede 4 file modificati/creati e 2 file di infrastruttura preparatori.

Architettura della soluzione:
> **Infrastruttura** (`codici_configurazione.py`) → **Localizzazione** (`it.py` + 9 chiavi) → **UI** (`TerminalUI` con macchina a stati) → **Entry Point** (`main.py`) → **GameController** (`crea_partita_standard` + `avvia_partita_sicura`)

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---|---|---|
| **Severità** | ALTA | Nessuna TUI = nessuna partita da terminale |
| **Scope** | 4 file nuovi/modificati + 5 doc aggiornamenti | Lista completa in «File Structure» |
| **Rischio regressione** | BASSO | Nuovo modulo isolato; zero modifica al Domain |
| **Breaking changes** | NO | `ui_terminale.py` era vuoto; nessun consumer esistente |
| **Testing** | MEDIO | Mock `input()`/`print()` con `unittest.mock` |

---

## 🎯 Requisiti Funzionali

### 1. Infrastruttura Chiavi di Localizzazione

**Comportamento Atteso**:
1. Esiste `bingo_game/events/codici_configurazione.py` con 9 costanti-chiave
2. `it.py` importa `Codici_Configurazione` e definisce `MESSAGGI_CONFIGURAZIONE` immutabile
3. Ogni chiave mappa a una `tuple[str, ...]` con i testi italiani definitivi

**File Coinvolti**:
- `bingo_game/events/codici_configurazione.py` — CREARE 🔧
- `bingo_game/ui/locales/it.py` — ESTENDERE ⚙️

---

### 2. Implementazione UI con Macchina a Stati

**Comportamento Atteso**:
1. L'utente esegue `python main.py`
2. Il sistema mostra benvenuto e guida l'utente attraverso 3 prompt sequenziali
3. Ogni input non valido produce un messaggio di errore + re-prompt dello stesso campo
4. A configurazione completata, la partita viene avviata via GameController

**Validazione per campo** (ordine obbligatorio):
- **Nome**: `.strip()` sempre → non vuoto → `len ≤ 15`
- **Bot**: `int()` valido → range `1..7`
- **Cartelle**: `int()` valido → range `1..6`

**File Coinvolti**:
- `bingo_game/ui/ui_terminale.py` — IMPLEMENTARE 🔧 (attualmente vuoto)

---

### 3. Integrazione Sistema di Logging

**Comportamento Atteso**:
- `INFO`: avvio configurazione, configurazione completata con successo
- `WARNING`: ogni fallimento di validazione (nome vuoto, nome lungo, bot/cartelle fuori range, tipo non valido)
- `DEBUG`: ogni transizione di stato, valori dopo `.strip()`, parametri passati al Controller

**File Coinvolti**:
- `bingo_game/ui/ui_terminale.py` — logging integrato direttamente nella classe

---

### 4. Chiusura Documentale Post-Implementazione

**Comportamento Atteso**:
- `README.md` aggiornato con istruzioni di avvio TUI
- `CHANGELOG.md` con entry `v0.7.0`
- `API.md` e `ARCHITECTURE.md` allineati alla nuova interfaccia
- `DESIGN_LOGGING_SYSTEM.md` con nuovi eventi `[TUI]`

**File Coinvolti**: 5 file di documentazione (vedi Fase 6)

---

## 🏗️ Architettura

### Layer Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                  INTERFACE LAYER                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TerminalUI (ui_terminale.py)  ← NEW                   │  │
│  │  avvia() | _chiedi_nome() | _chiedi_bot()            │  │
│  │  _chiedi_cartelle() | _avvia_partita()              │  │
│  │  _stampa_righe() | _chiedi_input()                  │  │
│  └───────────────────────────────────────────────────────┘  │
│  Dipende da: MESSAGGI_CONFIGURAZIONE, MESSAGGI_ERRORI     │
└───────────────────────────────────────────────────────────────┘
                          ↓ chiama
┌───────────────────────────────────────────────────────────────┐
│                APPLICATION LAYER                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ game_controller.py  (già esistente ✅)                │  │
│  │  crea_partita_standard() | avvia_partita_sicura()    │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          ↓ produce
┌───────────────────────────────────────────────────────────────┐
│                   DOMAIN LAYER                              │
│  Partita | GiocatoreBase | CartellaBingo  (inalterato ✅)   │
└───────────────────────────────────────────────────────────────┘
```

### File Structure

```
bingo_game/
├── events/
│   ├── codici_errori.py               # GIA' ESISTENTE ✅ (pattern di riferimento)
│   └── codici_configurazione.py       # NEW 🔧 (Fase 1)
├── ui/
│   ├── locales/
│   │   └── it.py                       # MODIFIED ⚙️ (Fase 2) +MESSAGGI_CONFIGURAZIONE
│   ├── renderers/
│   │   └── renderer_terminal.py        # GIA' ESISTENTE ✅ (usato nella Fase 2+)
│   └── ui_terminale.py               # NEW 🔧 (Fase 3) classe TerminalUI
└── game_controller.py              # GIA' ESISTENTE ✅ (consumato da TerminalUI)

main.py                             # MODIFIED ⚙️ (Fase 4) entry point TUI

tests/
└── unit/
    └── test_ui_terminale.py          # NEW 🔧 (Fase 5) 7 unit tests

documentations/
├── PLAN_TERMINAL_START_MENU.md     # THIS FILE
├── DESIGN_TERMINAL_START_MENU.md   # GIA' ESISTENTE ✅ (v1.2 READY)
├── README.md                       # MODIFIED ⚙️ (Fase 6)
├── CHANGELOG.md                    # MODIFIED ⚙️ (Fase 6)
├── API.md                          # MODIFIED ⚙️ (Fase 6)
├── ARCHITECTURE.md                 # MODIFIED ⚙️ (Fase 6)
└── DESIGN_LOGGING_SYSTEM.md        # MODIFIED ⚙️ (Fase 6)
```

---

## 📝 Piano di Implementazione

---

### FASE 1: Infrastruttura Chiavi di Configurazione

**Priorità**: 🟠 ALTA (prerequisito per Fase 2)
**File**: `bingo_game/events/codici_configurazione.py`
**Operazione**: CREARE (file nuovo)

#### Codice Nuovo

```python
# bingo_game/events/codici_configurazione.py
"""Costanti-chiave per il dizionario MESSAGGI_CONFIGURAZIONE in it.py.

Segue il pattern di codici_errori.py: tipo alias + costanti stringa.
Importato da bingo_game/ui/locales/it.py per annotare
il dizionario MESSAGGI_CONFIGURAZIONE.

Version:
    v0.7.0: Creazione iniziale per Fase 1 TUI start menu.
"""
from __future__ import annotations

# Tipo alias per le chiavi del dizionario MESSAGGI_CONFIGURAZIONE
Codici_Configurazione = str

# --- Chiavi informative ---
CONFIG_BENVENUTO: Codici_Configurazione = "CONFIG_BENVENUTO"
CONFIG_CONFERMA_AVVIO: Codici_Configurazione = "CONFIG_CONFERMA_AVVIO"

# --- Chiavi prompt di input ---
CONFIG_RICHIESTA_NOME: Codici_Configurazione = "CONFIG_RICHIESTA_NOME"
CONFIG_RICHIESTA_BOT: Codici_Configurazione = "CONFIG_RICHIESTA_BOT"
CONFIG_RICHIESTA_CARTELLE: Codici_Configurazione = "CONFIG_RICHIESTA_CARTELLE"

# --- Chiavi errori di validazione nome ---
CONFIG_ERRORE_NOME_VUOTO: Codici_Configurazione = "CONFIG_ERRORE_NOME_VUOTO"
CONFIG_ERRORE_NOME_TROPPO_LUNGO: Codici_Configurazione = "CONFIG_ERRORE_NOME_TROPPO_LUNGO"

# --- Chiavi errori di validazione range ---
CONFIG_ERRORE_BOT_RANGE: Codici_Configurazione = "CONFIG_ERRORE_BOT_RANGE"
CONFIG_ERRORE_CARTELLE_RANGE: Codici_Configurazione = "CONFIG_ERRORE_CARTELLE_RANGE"
```

#### Rationale

`it.py` usa un tipo-chiave importato da `bingo_game/events/` per annotare ogni dizionario (`Codici_Errori` per `MESSAGGI_ERRORI`, `Codici_Ev` per `MESSAGGI_EVENTI`, ecc.). Senza `Codici_Configurazione`, `MESSAGGI_CONFIGURAZIONE` non può essere annotato in modo coerente. Il pattern è identico a `codici_errori.py` già presente nel progetto.

**Non ci sono regressioni perché**:
- File nuovo isolato, non modifica nulla di esistente
- Nessun import circolare: non importa da altri moduli di progetto

#### Testing Fase 1

Nessun test unitario autonomo richiesto per questo file (solo costanti stringa). La verifica avviene implicitamente nei test della Fase 5 (import corretto da `ui_terminale.py`).

**Commit Message**:
```
feat(events): add codici_configurazione.py with 9 config key constants

- New file following codici_errori.py pattern
- Defines Codici_Configurazione = str type alias
- 9 string constants for MESSAGGI_CONFIGURAZIONE dict in it.py
- Groups: informative keys, input prompt keys, validation error keys

Impact:
- Zero changes to existing files
- Prerequisite for Fase 2 (it.py extension)
```

---

### FASE 2: Estensione Catalogo Localizzazione

**Priorità**: 🟠 ALTA (prerequisito per Fase 3)
**File**: `bingo_game/ui/locales/it.py`
**Operazione**: ESTENDERE (aggiunta in coda al file esistente)

#### Codice da Aggiungere in coda a it.py

```python
# --- aggiunta in coda a bingo_game/ui/locales/it.py ---

# Import aggiunto in testa al file (insieme agli altri import di codici_*)
from bingo_game.events.codici_configurazione import Codici_Configurazione

# Nuovo dizionario immutabile (aggiunto dopo gli altri MappingProxyType)
MESSAGGI_CONFIGURAZIONE: Mapping[Codici_Configurazione, tuple[str, ...]] = MappingProxyType({
    # Messaggi informativi
    "CONFIG_BENVENUTO":              ("Benvenuto in Tombola Stark!",),
    "CONFIG_CONFERMA_AVVIO":         ("Configurazione completata. Avvio partita...",),
    # Prompt di input
    "CONFIG_RICHIESTA_NOME":         ("Inserisci il tuo nome (max 15 caratteri): ",),
    "CONFIG_RICHIESTA_BOT":          ("Inserisci il numero di bot (1-7): ",),
    "CONFIG_RICHIESTA_CARTELLE":     ("Inserisci il numero di cartelle (1-6): ",),
    # Errori validazione nome
    "CONFIG_ERRORE_NOME_VUOTO":          ("Errore: Nome non valido.",
                                          "Inserisci almeno un carattere.",),
    "CONFIG_ERRORE_NOME_TROPPO_LUNGO":   ("Errore: Nome troppo lungo.",
                                          "Inserisci al massimo 15 caratteri.",),
    # Errori validazione range
    "CONFIG_ERRORE_BOT_RANGE":           ("Errore: Numero bot non valido.",
                                          "Inserisci un valore tra 1 e 7.",),
    "CONFIG_ERRORE_CARTELLE_RANGE":      ("Errore: Numero cartelle non valido.",
                                          "Inserisci un valore tra 1 e 6.",),
})
```

#### Rationale

- Pattern identico ai 4 dizionari esistenti in `it.py`: `MappingProxyType` + `tuple[str, ...]` + tipo-chiave importato
- Separazione semantica: i messaggi di configurazione sono distinti dai messaggi di gioco (`MESSAGGI_ERRORI`, `MESSAGGI_EVENTI`, ecc.)
- Gli errori di **tipo** (input non intero) riusano `MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]` già esistente: nessuna duplicazione

**Non ci sono regressioni perché**:
- Aggiunta in coda: nessuna modifica ai dizionari esistenti
- `MappingProxyType` è immutabile: nessuna mutazione accidentale possibile

#### Commit Message
```
feat(locales): add MESSAGGI_CONFIGURAZIONE dict to it.py (9 keys)

- Import Codici_Configurazione from codici_configurazione.py
- New MappingProxyType dict following existing pattern
- 9 keys: 2 info, 3 prompts, 2 nome errors, 2 range errors
- Reuses MESSAGGI_ERRORI[NUMERO_TIPO_NON_VALIDO] for type errors

Impact:
- it.py extended, existing dicts untouched
- Prerequisite for Fase 3 (TerminalUI implementation)
```

---

### FASE 3: Implementazione TerminalUI

**Priorità**: 🟠 ALTA (core della feature)
**File**: `bingo_game/ui/ui_terminale.py`
**Operazione**: IMPLEMENTARE (file attualmente vuoto, 0 byte)

#### Codice Completo

```python
# bingo_game/ui/ui_terminale.py
"""Interfaccia utente da terminale per Tombola Stark.

Fase 1: flusso di configurazione pre-partita accessibile via screen reader.
Zero stringhe hardcoded: tutti i testi da MESSAGGI_CONFIGURAZIONE in it.py.
Usa esclusivamente input() standard Python per massima compatibilita' AT.

Version:
    v0.7.0: Implementazione iniziale Fase 1 (start menu).
"""
from __future__ import annotations

import logging

from bingo_game.ui.locales.it import MESSAGGI_CONFIGURAZIONE, MESSAGGI_ERRORI
from bingo_game.game_controller import crea_partita_standard, avvia_partita_sicura
from bingo_game.ui.renderers.renderer_terminal import TerminalRenderer

logger = logging.getLogger(__name__)

# Costanti di validazione (definite a livello modulo per chiarezza)
_LUNGHEZZA_MAX_NOME: int = 15
_BOT_MIN: int = 1
_BOT_MAX: int = 7
_CARTELLE_MIN: int = 1
_CARTELLE_MAX: int = 6


class TerminalUI:
    """Interfaccia da terminale per Tombola Stark - Fase 1: configurazione.

    Gestisce il flusso di configurazione pre-partita come macchina a stati
    sequenziale (A: BENVENUTO -> B: ATTESA_NOME -> C: ATTESA_BOT ->
    D: ATTESA_CARTELLE -> E: AVVIO_PARTITA).

    Accessibilita':
        - Usa input() standard Python (compatibile NVDA/JAWS/Orca)
        - Output testuale lineare: nessuna decorazione grafica
        - Errori stampati PRIMA del re-prompt (ordine lettura screen reader)

    Version:
        v0.7.0: Implementazione iniziale.
    """

    def __init__(self) -> None:
        """Inizializza la TUI e istanzia il TerminalRenderer per Fase 2+.

        Il TerminalRenderer viene istanziato qui e tenuto pronto come
        attributo: non usato nella Fase 1, necessario dalla Fase 2+
        per il rendering degli EsitoAzione di gioco.

        Version:
            v0.7.0: Implementazione iniziale.
        """
        self._renderer = TerminalRenderer()
        logger.debug("[TUI] TerminalUI inizializzata.")

    def avvia(self) -> None:
        """Entry point pubblico. Orchestra il flusso A -> B -> C -> D -> E.

        Chiama in sequenza i metodi privati per ogni stato della macchina.
        Nessun parametro richiesto: tutti i dati vengono raccolti
        interattivamente tramite i metodi _chiedi_*.

        Version:
            v0.7.0: Implementazione iniziale.
        """
        logger.info("[TUI] Avvio configurazione partita.")
        self._mostra_benvenuto()
        nome = self._chiedi_nome()
        numero_bot = self._chiedi_bot()
        numero_cartelle = self._chiedi_cartelle()
        self._avvia_partita(nome, numero_bot, numero_cartelle)

    # ------------------------------------------------------------------ #
    # Metodi degli stati (macchina a stati A -> E)                        #
    # ------------------------------------------------------------------ #

    def _mostra_benvenuto(self) -> None:
        """Stato A: stampa il messaggio di benvenuto dal catalogo.

        Version:
            v0.7.0: Implementazione iniziale.
        """
        logger.debug("[TUI] Stato A: BENVENUTO")
        self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_BENVENUTO"])

    def _chiedi_nome(self) -> str:
        """Stato B: loop di acquisizione e validazione del nome giocatore.

        Applica .strip() come primo passo obbligatorio.
        Priorita' validazione: (1) strip -> (2) non vuoto -> (3) len <= 15.
        Al primo fallimento mostra errore e ripropone il prompt.

        Returns:
            str: Nome validato (strip applicato, 1..15 caratteri).

        Version:
            v0.7.0: Implementazione iniziale.
        """
        logger.debug("[TUI] Stato B: ATTESA_NOME")
        while True:
            input_raw = self._chiedi_input("CONFIG_RICHIESTA_NOME")
            nome = input_raw.strip()
            logger.debug(f"[TUI] Nome dopo strip: '{nome}' (len={len(nome)})")
            if len(nome) == 0:
                logger.warning("[TUI] Validazione nome fallita: stringa vuota dopo strip.")
                self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_NOME_VUOTO"])
                continue
            if len(nome) > _LUNGHEZZA_MAX_NOME:
                logger.warning(
                    f"[TUI] Validazione nome fallita: "
                    f"lunghezza {len(nome)} > {_LUNGHEZZA_MAX_NOME}."
                )
                self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_NOME_TROPPO_LUNGO"])
                continue
            logger.debug(f"[TUI] Nome valido acquisito: '{nome}'")
            return nome

    def _chiedi_bot(self) -> int:
        """Stato C: loop di acquisizione e validazione del numero di bot.

        Priorita' validazione: (1) tipo int -> (2) range 1..7.
        Errore di tipo usa MESSAGGI_ERRORI (riuso chiave esistente).

        Returns:
            int: Numero bot validato (range 1..7).

        Version:
            v0.7.0: Implementazione iniziale.
        """
        logger.debug("[TUI] Stato C: ATTESA_BOT")
        while True:
            input_raw = self._chiedi_input("CONFIG_RICHIESTA_BOT")
            try:
                valore = int(input_raw)
            except ValueError:
                logger.warning(
                    f"[TUI] Validazione bot fallita: '{input_raw}' non e' un intero."
                )
                self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])
                continue
            if not (_BOT_MIN <= valore <= _BOT_MAX):
                logger.warning(
                    f"[TUI] Validazione bot fallita: "
                    f"{valore} fuori range {_BOT_MIN}..{_BOT_MAX}."
                )
                self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_BOT_RANGE"])
                continue
            logger.debug(f"[TUI] Numero bot valido: {valore}")
            return valore

    def _chiedi_cartelle(self) -> int:
        """Stato D: loop di acquisizione e validazione del numero di cartelle.

        Priorita' validazione: (1) tipo int -> (2) range 1..6.
        Il range 1..6 e' una scelta UX (anti-verbosita' screen reader);
        il GameController accetta qualsiasi valore > 0.

        Returns:
            int: Numero cartelle validato (range 1..6).

        Version:
            v0.7.0: Implementazione iniziale.
        """
        logger.debug("[TUI] Stato D: ATTESA_CARTELLE")
        while True:
            input_raw = self._chiedi_input("CONFIG_RICHIESTA_CARTELLE")
            try:
                valore = int(input_raw)
            except ValueError:
                logger.warning(
                    f"[TUI] Validazione cartelle fallita: "
                    f"'{input_raw}' non e' un intero."
                )
                self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])
                continue
            if not (_CARTELLE_MIN <= valore <= _CARTELLE_MAX):
                logger.warning(
                    f"[TUI] Validazione cartelle fallita: "
                    f"{valore} fuori range {_CARTELLE_MIN}..{_CARTELLE_MAX}."
                )
                self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_CARTELLE_RANGE"])
                continue
            logger.debug(f"[TUI] Numero cartelle valido: {valore}")
            return valore

    def _avvia_partita(
        self,
        nome: str,
        numero_bot: int,
        numero_cartelle: int,
    ) -> None:
        """Stato E: passa la configurazione al GameController e avvia la partita.

        Stampa la conferma di avvio PRIMA di chiamare il Controller,
        cosi' lo screen reader legge la conferma prima del cambio di contesto.

        Args:
            nome: Nome giocatore validato (strip applicato, 1..15 char).
            numero_bot: Numero bot (1..7).
            numero_cartelle: Numero cartelle per giocatore (1..6).

        Version:
            v0.7.0: Implementazione iniziale.
        """
        logger.debug("[TUI] Stato E: AVVIO_PARTITA")
        self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_CONFERMA_AVVIO"])
        partita = crea_partita_standard(
            nome_giocatore_umano=nome,
            num_cartelle_umano=numero_cartelle,
            num_bot=numero_bot,
        )
        avvia_partita_sicura(partita)
        logger.info(
            f"[TUI] Configurazione completata. "
            f"Partita avviata: nome='{nome}', bot={numero_bot}, "
            f"cartelle={numero_cartelle}."
        )

    # ------------------------------------------------------------------ #
    # Helper privati                                                       #
    # ------------------------------------------------------------------ #

    def _stampa_righe(self, righe: tuple[str, ...]) -> None:
        """Stampa ogni riga della tupla su una linea separata.

        Nessuna decorazione grafica: output testuale puro compatibile
        con screen reader.

        Args:
            righe: Tupla di stringhe dal catalogo it.py.

        Version:
            v0.7.0: Implementazione iniziale.
        """
        for riga in righe:
            print(riga)

    def _chiedi_input(self, chiave_prompt: str) -> str:
        """Usa la prima riga del catalogo come testo del prompt per input().

        Args:
            chiave_prompt: Chiave in MESSAGGI_CONFIGURAZIONE.

        Returns:
            str: Testo grezzo inserito dall'utente (non processato).

        Version:
            v0.7.0: Implementazione iniziale.
        """
        testo_prompt = MESSAGGI_CONFIGURAZIONE[chiave_prompt][0]
        return input(testo_prompt)
```

#### Rationale

**Classe vs. modulo con funzioni**: la classe `TerminalUI` facilita il testing tramite dependency injection e rende esplicito lo stato condiviso (il `_renderer` pronto per Fase 2+). Coerente con il pattern `TerminalRenderer` già presente nel progetto.

**`_renderer` istanziato in `__init__` ma non usato in Fase 1**: segue il principio di "istanziare in anticipo" per evitare ritardi percettibili all'avvio della Fase 2. Il costo di istanziazione è trascurabile.

**Logging `[TUI]` come prefisso**: coerente con `[SYS]` usato nel sistema di logging centralizzato (v0.5.0). Distingue i log TUI da quelli del dominio nei file di log.

**Non ci sono regressioni perché**:
- `ui_terminale.py` era vuoto: nessun consumer precedente
- Il Domain layer non viene mai importato direttamente (rispetto ARCHITECTURE.md)

#### Commit Message
```
feat(ui): implement TerminalUI class with sequential state machine A-E

- Class TerminalUI in ui_terminale.py (previously empty)
- States: BENVENUTO->ATTESA_NOME->ATTESA_BOT->ATTESA_CARTELLE->AVVIO_PARTITA
- Validation: .strip() + non-empty + len<=15 for name
- Validation: int() + range 1..7 for bots, 1..6 for boards
- Logging: INFO for start/complete, WARNING for validation fails,
  DEBUG for state transitions and sanitized values
- Zero hardcoded strings: all text from MESSAGGI_CONFIGURAZIONE
- Reuses MESSAGGI_ERRORI[NUMERO_TIPO_NON_VALIDO] for type errors
- Calls crea_partita_standard() + avvia_partita_sicura() (API.md)
- TerminalRenderer instantiated in __init__ for Fase 2+ readiness
- Screen reader compliant: linear output, errors before re-prompt

Impact:
- New feature: TUI start menu fully functional
- Zero changes to Domain or Application layers
```

---

### FASE 4: Collegamento Entry Point

**Priorità**: 🟠 ALTA
**File**: `main.py`
**Operazione**: AGGIORNARE (aggiungere istanziazione `TerminalUI`)

#### Codice da Integrare

```python
# Aggiunta in main.py (verificare contenuto attuale prima di modificare)
from bingo_game.ui.ui_terminale import TerminalUI

def main() -> None:
    """Entry point principale di Tombola Stark.

    Istanzia e avvia l'interfaccia da terminale.

    Version:
        v0.7.0: Collegamento TerminalUI.
    """
    tui = TerminalUI()
    tui.avvia()


if __name__ == "__main__":
    main()
```

> **Nota operativa**: Verificare il contenuto attuale di `main.py` prima di modificare. Se esiste già una funzione `main()`, integrare l'istanziazione di `TerminalUI` senza sovrascrivere logica esistente.

#### Commit Message
```
feat(main): wire TerminalUI to application entry point

- Import and instantiate TerminalUI in main.py
- tui.avvia() called as first action at startup
- Prerequisite for manual TC01-TC05 verification protocol

Impact:
- Application now launchable with: python main.py
```

---

### FASE 5: Unit Testing

**Priorità**: 🟠 ALTA
**File**: `tests/unit/test_ui_terminale.py`
**Operazione**: CREARE (7 test case che coprono TC01–TC04 + flusso felice + edge case)

#### Codice Test Completo

```python
# tests/unit/test_ui_terminale.py
"""Unit test per TerminalUI - Fase 1 (start menu).

Usa unittest.mock per simulare input() e print() senza interazione reale
con il terminale. Ogni test verifica un singolo comportamento atomico.
Corrispondenza con il Protocollo di Verifica Manuale del DESIGN v1.2:
    test_tc01 -> TC01, test_tc02 -> TC02,
    test_tc03_* -> TC03, test_tc04 -> TC04,
    test_flusso_felice -> TC05 (parziale, automatizzabile).

Version:
    v0.7.0: Creazione iniziale.
"""
from __future__ import annotations

from unittest.mock import patch, MagicMock
import pytest

from bingo_game.ui.ui_terminale import TerminalUI


class TestValidazioneNome:
    """Test Stato B: validazione nome giocatore (TC01, TC02)."""

    def test_tc01_nome_vuoto_dopo_strip(self):
        """TC01: input di soli spazi -> CONFIG_ERRORE_NOME_VUOTO + re-prompt."""
        sequenza_input = iter(["   ", "Marco"])
        with patch("builtins.input", side_effect=lambda _: next(sequenza_input)), \
             patch("builtins.print") as mock_print, \
             patch("bingo_game.ui.ui_terminale.TerminalRenderer"):
            tui = TerminalUI()
            nome = tui._chiedi_nome()
        assert nome == "Marco"
        righe_stampate = [c.args[0] for c in mock_print.call_args_list]
        assert "Errore: Nome non valido." in righe_stampate

    def test_tc02_nome_troppo_lungo(self):
        """TC02: nome > 15 char -> CONFIG_ERRORE_NOME_TROPPO_LUNGO + re-prompt."""
        sequenza_input = iter(["NomeMoltoLungoOltreQuindici", "Marco"])
        with patch("builtins.input", side_effect=lambda _: next(sequenza_input)), \
             patch("builtins.print") as mock_print, \
             patch("bingo_game.ui.ui_terminale.TerminalRenderer"):
            tui = TerminalUI()
            nome = tui._chiedi_nome()
        assert nome == "Marco"
        righe_stampate = [c.args[0] for c in mock_print.call_args_list]
        assert "Errore: Nome troppo lungo." in righe_stampate

    def test_strip_applicato_prima_del_check(self):
        """Strip e' applicato prima del controllo non-vuoto."""
        with patch("builtins.input", return_value="  Marco  "), \
             patch("builtins.print"), \
             patch("bingo_game.ui.ui_terminale.TerminalRenderer"):
            tui = TerminalUI()
            nome = tui._chiedi_nome()
        assert nome == "Marco"


class TestValidazioneBot:
    """Test Stato C: validazione numero bot (TC03)."""

    def test_tc03_bot_sotto_range(self):
        """TC03a: input '0' -> CONFIG_ERRORE_BOT_RANGE + re-prompt."""
        sequenza_input = iter(["0", "3"])
        with patch("builtins.input", side_effect=lambda _: next(sequenza_input)), \
             patch("builtins.print") as mock_print, \
             patch("bingo_game.ui.ui_terminale.TerminalRenderer"):
            tui = TerminalUI()
            bot = tui._chiedi_bot()
        assert bot == 3
        righe_stampate = [c.args[0] for c in mock_print.call_args_list]
        assert "Errore: Numero bot non valido." in righe_stampate

    def test_tc03_bot_sopra_range(self):
        """TC03b: input '9' -> CONFIG_ERRORE_BOT_RANGE + re-prompt."""
        sequenza_input = iter(["9", "3"])
        with patch("builtins.input", side_effect=lambda _: next(sequenza_input)), \
             patch("builtins.print") as mock_print, \
             patch("bingo_game.ui.ui_terminale.TerminalRenderer"):
            tui = TerminalUI()
            bot = tui._chiedi_bot()
        assert bot == 3
        righe_stampate = [c.args[0] for c in mock_print.call_args_list]
        assert "Errore: Numero bot non valido." in righe_stampate

    def test_bot_tipo_non_valido(self):
        """Input non intero usa MESSAGGI_ERRORI[NUMERO_TIPO_NON_VALIDO]."""
        sequenza_input = iter(["tre", "3"])
        with patch("builtins.input", side_effect=lambda _: next(sequenza_input)), \
             patch("builtins.print") as mock_print, \
             patch("bingo_game.ui.ui_terminale.TerminalRenderer"):
            tui = TerminalUI()
            bot = tui._chiedi_bot()
        assert bot == 3
        righe_stampate = [c.args[0] for c in mock_print.call_args_list]
        assert "Errore: Tipo non valido." in righe_stampate


class TestValidazioneCartelle:
    """Test Stato D: validazione numero cartelle (TC04)."""

    def test_tc04_cartelle_fuori_range(self):
        """TC04: input '7' -> CONFIG_ERRORE_CARTELLE_RANGE + re-prompt."""
        sequenza_input = iter(["7", "2"])
        with patch("builtins.input", side_effect=lambda _: next(sequenza_input)), \
             patch("builtins.print") as mock_print, \
             patch("bingo_game.ui.ui_terminale.TerminalRenderer"):
            tui = TerminalUI()
            cartelle = tui._chiedi_cartelle()
        assert cartelle == 2
        righe_stampate = [c.args[0] for c in mock_print.call_args_list]
        assert "Errore: Numero cartelle non valido." in righe_stampate


class TestFlussoFelice:
    """Test del flusso completo senza errori."""

    def test_flusso_felice_completo(self):
        """Sequenza valida -> crea_partita_standard chiamata con i parametri corretti."""
        sequenza_input = iter(["Marco", "3", "2"])
        mock_partita = MagicMock()
        with patch("builtins.input", side_effect=lambda _: next(sequenza_input)), \
             patch("builtins.print"), \
             patch("bingo_game.ui.ui_terminale.TerminalRenderer"), \
             patch("bingo_game.ui.ui_terminale.crea_partita_standard",
                   return_value=mock_partita) as mock_crea, \
             patch("bingo_game.ui.ui_terminale.avvia_partita_sicura") as mock_avvia:
            tui = TerminalUI()
            tui.avvia()
        mock_crea.assert_called_once_with(
            nome_giocatore_umano="Marco",
            num_cartelle_umano=2,
            num_bot=3,
        )
        mock_avvia.assert_called_once_with(mock_partita)
```

#### Commit Message
```
test(ui): add unit tests for TerminalUI validation loops (7 tests)

- TestValidazioneNome: TC01 (nome vuoto), TC02 (nome lungo), strip priority
- TestValidazioneBot: TC03a (sotto range), TC03b (sopra range), tipo non valido
- TestValidazioneCartelle: TC04 (fuori range)
- TestFlussoFelice: flusso completo con verifica parametri Controller
- All tests use unittest.mock.patch for input()/print() simulation
- TerminalRenderer mocked in all tests (isolation)

Impact:
- 7 tests covering all TC01-TC04 + flusso felice
- TC05 (screen reader) remains manual per design protocol
```

---

### FASE 6: Aggiornamenti Documentali Post-Implementazione

**Priorità**: 🟡 MEDIA
**File coinvolti**: 5 (aggiornamenti separati in commit unico)
**Operazione**: AGGIORNARE

| File | Sezione da Aggiornare | Contenuto da Aggiungere |
|---|---|---|
| `README.md` | Sezione "Avvio" o "Come Usare" | `python main.py` come comando di avvio; descrizione flusso di configurazione (nome/bot/cartelle); nota accessibilità screen reader |
| `CHANGELOG.md` | Nuova entry `[v0.7.0]` | Feature: TUI Fase 1 (start menu), `TerminalUI`, `MESSAGGI_CONFIGURAZIONE`, `codici_configurazione.py`; lista file nuovi/modificati |
| `API.md` | Sezione nuova "Interface Layer / TerminalUI" | `TerminalUI.avvia()` come unico metodo pubblico; firma, descrizione, side effects, dipendenze |
| `ARCHITECTURE.md` | Diagramma layer Interface | Aggiungere `TerminalUI` nel layer Interface; flusso TUI: `main.py -> TerminalUI -> GameController` |
| `DESIGN_LOGGING_SYSTEM.md` | Sezione "Eventi Registrati" | Nuovi eventi `[TUI]`: INFO avvio/fine configurazione, WARNING per ogni tipo di errore di validazione, DEBUG per transizioni stato |

#### Commit Message
```
docs: update README, CHANGELOG, API, ARCHITECTURE, LOGGING for v0.7.0

- README: add TUI startup instructions and accessibility note
- CHANGELOG: v0.7.0 entry with TerminalUI feature list
- API.md: document TerminalUI.avvia() public interface
- ARCHITECTURE.md: add TerminalUI to Interface layer diagram
- DESIGN_LOGGING_SYSTEM.md: register new [TUI] log events

Impact:
- Documentation fully aligned with v0.7.0 implementation
```

---

## 🧪 Testing Strategy

### Unit Tests (7 test totali)

#### `tests/unit/test_ui_terminale.py`
- [x] `test_tc01_nome_vuoto_dopo_strip` — TC01: soli spazi -> errore nome vuoto
- [x] `test_tc02_nome_troppo_lungo` — TC02: 28 char -> errore nome lungo
- [x] `test_strip_applicato_prima_del_check` — `"  Marco  "` -> nome `"Marco"` senza errori
- [x] `test_tc03_bot_sotto_range` — TC03a: `"0"` -> errore bot range
- [x] `test_tc03_bot_sopra_range` — TC03b: `"9"` -> errore bot range
- [x] `test_bot_tipo_non_valido` — `"tre"` -> riuso `MESSAGGI_ERRORI`
- [x] `test_tc04_cartelle_fuori_range` — TC04: `"7"` -> errore cartelle range
- [x] `test_flusso_felice_completo` — sequenza valida -> `crea_partita_standard` con parametri corretti

### Integration Test (1 test)

```python
def test_integrazione_tui_game_controller():
    """Test end-to-end: TerminalUI -> GameController -> Partita in_corso."""
    sequenza_input = iter(["Marco", "2", "1"])
    with patch("builtins.input", side_effect=lambda _: next(sequenza_input)), \
         patch("builtins.print"):
        tui = TerminalUI()
        tui.avvia()  # Chiama GameController reale (no mock)
    # Se non solleva eccezioni, la partita e' stata avviata correttamente
```

### Manual Testing Checklist (TC05)

- [ ] **TC05**: Eseguire `python main.py` con NVDA/JAWS/Orca attivo
  - [ ] Benvenuto letto immediatamente all'avvio
  - [ ] Ogni prompt letto prima che il cursore attenda input
  - [ ] Errore di validazione letto PRIMA del re-prompt (testare TC01 manualmente)
  - [ ] Nessun artefatto grafico vocalizzato (nessuna emoji, nessun box Unicode)
  - [ ] Conferma di avvio letta prima che la Fase 2 inizi

---

## 🎓 Architectural Patterns Reference

### State Machine Pattern (Macchina a Stati Sequenziale)

**Quando Usare**: flussi di input utente con stati discreti e transizioni condizionali

```python
# Pattern: ogni stato e' un metodo privato con loop di validazione interno
def _chiedi_valore(self) -> tipo_atteso:
    while True:
        raw = self._chiedi_input("CHIAVE_PROMPT")
        # validazione...
        if condizione_errore:
            self._stampa_righe(MESSAGGI["CHIAVE_ERRORE"])
            continue  # re-loop: stesso stato
        return valore_validato  # avanzamento: stato successivo
```

**Pro**: stato locale al metodo, nessuna variabile di stato esterna, testabile in isolamento.

### Dependency Injection per Testing

**Quando Usare**: metodi che chiamano `input()`/`print()` o funzioni del Controller

```python
# Pattern per i test: patch dei side-effect
with patch("builtins.input", side_effect=iter(["val1", "val2"])), \
     patch("builtins.print"), \
     patch("bingo_game.ui.ui_terminale.crea_partita_standard") as mock:
    tui = TerminalUI()
    tui.avvia()
mock.assert_called_once_with(...)
```

---

## ✅ Validation & Acceptance

### Success Criteria

**Funzionali**:
- [ ] `python main.py` avvia il flusso di configurazione senza errori
- [ ] I 3 prompt vengono mostrati in sequenza
- [ ] Ogni errore di validazione mostra il messaggio corretto e ripropone il prompt
- [ ] La partita viene avviata dopo la configurazione completa
- [ ] Nessuna stringa hardcoded in `ui_terminale.py` (grep verifica zero literal)

**Tecnici**:
- [ ] Zero breaking changes per il codice esistente
- [ ] Test coverage ≥ 90% per `ui_terminale.py`
- [ ] Tutti i 7 unit test passano: `pytest tests/unit/test_ui_terminale.py -v`
- [ ] Nessun errore di import: `python -c "from bingo_game.ui.ui_terminale import TerminalUI"`

**Code Quality**:
- [ ] Tutti i file committati compilano senza errori (`python -m py_compile`)
- [ ] Type hints completi su tutti i metodi pubblici e privati
- [ ] Docstring Google-style su classe e tutti i metodi
- [ ] `CHANGELOG.md` aggiornato con entry `v0.7.0`

**Accessibilità**:
- [ ] TC05 superato: NVDA/JAWS/Orca legge i messaggi nell'ordine corretto
- [ ] Nessuna decorazione grafica nel output (no ANSI, no box, no emoji stampate)
- [ ] Errori stampati sempre PRIMA del re-prompt

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T: Stringhe Hardcoded

```python
# SBAGLIATO - stringa hardcoded in ui_terminale.py
print("Benvenuto in Tombola Stark!")  # ❌
nome = input("Inserisci il tuo nome: ")  # ❌
```

**Perché non funziona**: viola il principio fondamentale del progetto; rompe la catena di localizzazione; impossibile da testare senza leggere il source.

### ❌ DON'T: Metodo Controller Inesistente

```python
# SBAGLIATO - game_controller.configura() non esiste nell'API
game_controller.configura(nome, bot, cartelle)  # ❌ NameError
```

**Perché non funziona**: il metodo `configura()` non esiste. Il contratto corretto da `API.md` è sempre il two-step:
```python
partita = crea_partita_standard(nome_giocatore_umano=nome, num_cartelle_umano=cartelle, num_bot=bot)  # ✅
avvia_partita_sicura(partita)  # ✅
```

### ❌ DON'T: Saltare .strip() o Invertire l'Ordine di Validazione

```python
# SBAGLIATO - check lunghezza prima del check vuoto
nome = input_raw  # no strip ❌
if len(nome) > 15:  # check lunghezza prima ❌
    ...
if len(nome) == 0:  # check vuoto dopo ❌
    ...
```

**Perché non funziona**: un input di soli spazi non verrebbe mai rifiutato come "vuoto" se il check lunghezza viene prima. La sequenza obbligatoria è: `strip()` -> `non vuoto` -> `len <= 15`.

### ❌ DON'T: Importare dal Domain Layer Direttamente

```python
# SBAGLIATO - viola ARCHITECTURE.md
from bingo_game.domain.partita import Partita  # ❌
from bingo_game.players.giocatore_base import GiocatoreBase  # ❌
```

**Perché non funziona**: il layer Interface deve consumare solo il Controller. L'accesso diretto al Domain bypassa il contratto architetturale.

---

## 📦 Commit Strategy

### 6 Commit Atomici (branch `feature/terminal-start-menu`)

1. **Commit 1** — Infrastruttura chiavi
   - `feat(events): add codici_configurazione.py with 9 config key constants`
   - Files: `bingo_game/events/codici_configurazione.py`

2. **Commit 2** — Localizzazione
   - `feat(locales): add MESSAGGI_CONFIGURAZIONE dict to it.py (9 keys)`
   - Files: `bingo_game/ui/locales/it.py`

3. **Commit 3** — Implementazione UI
   - `feat(ui): implement TerminalUI class with sequential state machine A-E`
   - Files: `bingo_game/ui/ui_terminale.py`

4. **Commit 4** — Entry point
   - `feat(main): wire TerminalUI to application entry point`
   - Files: `main.py`

5. **Commit 5** — Testing
   - `test(ui): add unit tests for TerminalUI validation loops (7 tests)`
   - Files: `tests/unit/test_ui_terminale.py`

6. **Commit 6** — Documentazione
   - `docs: update README, CHANGELOG, API, ARCHITECTURE, LOGGING for v0.7.0`
   - Files: `README.md`, `CHANGELOG.md`, `API.md`, `ARCHITECTURE.md`, `DESIGN_LOGGING_SYSTEM.md`

---

## 📝 Note Operative per Copilot

### Istruzioni Step-by-Step

1. **Commit 1 — Crea `bingo_game/events/codici_configurazione.py`**
   - Copia il codice dalla sezione "FASE 1 - Codice Nuovo"
   - Verifica pattern con `codici_errori.py` esistente per coerenza
   - Nessun test richiesto per questo commit

2. **Commit 2 — Estendi `bingo_game/ui/locales/it.py`**
   - Aggiungi l'import di `Codici_Configurazione` in testa al file, insieme agli altri import di `codici_*`
   - Aggiungi `MESSAGGI_CONFIGURAZIONE` in coda, dopo gli altri dizionari
   - Verifica che `MappingProxyType` sia già importato (lo è, da altri dizionari)

3. **Commit 3 — Implementa `bingo_game/ui/ui_terminale.py`**
   - Il file è attualmente vuoto: incolla il codice completo dalla sezione "FASE 3"
   - Verifica che la chiave `"NUMERO_TIPO_NON_VALIDO"` sia quella corretta in `MESSAGGI_ERRORI` (controllare `it.py`)

4. **Commit 4 — Aggiorna `main.py`**
   - Leggere il contenuto attuale di `main.py` prima di modificare
   - Aggiungere import e istanziazione `TerminalUI().avvia()`

5. **Commit 5 — Crea `tests/unit/test_ui_terminale.py`**
   - Copia il codice dalla sezione "FASE 5"
   - Esegui: `python -m pytest tests/unit/test_ui_terminale.py -v`
   - Tutti e 7 i test devono essere verdi prima del commit 6

6. **Commit 6 — Aggiornamenti documentali**
   - Seguire la tabella nella sezione "FASE 6"
   - Completare TC05 manuale con screen reader prima di chiudere il branch

### Verifica Rapida Pre-Commit

```bash
# Sintassi Python (tutti i file nuovi/modificati)
python -m py_compile bingo_game/events/codici_configurazione.py
python -m py_compile bingo_game/ui/locales/it.py
python -m py_compile bingo_game/ui/ui_terminale.py

# Import check
python -c "from bingo_game.ui.ui_terminale import TerminalUI; print('OK')"

# Unit tests
python -m pytest tests/unit/test_ui_terminale.py -v

# Nessuna stringa hardcoded (deve restituire 0 righe)
grep -n '"Benvenuto\|"Inserisci\|"Errore\|"Configurazione' bingo_game/ui/ui_terminale.py
```

### Troubleshooting

**Se `ImportError: cannot import name 'MESSAGGI_CONFIGURAZIONE'`**:
- Verificare che l'import di `Codici_Configurazione` sia stato aggiunto in `it.py`
- Verificare che `codici_configurazione.py` sia nel path corretto: `bingo_game/events/`

**Se `KeyError: 'NUMERO_TIPO_NON_VALIDO'`**:
- Verificare il nome esatto della chiave in `it.py` -> `MESSAGGI_ERRORI`
- Potrebbe essere `"TIPO_NON_VALIDO"` o altra variante: adattare il riferimento in `ui_terminale.py`

**Se i test falliscono per `StopIteration`**:
- La sequenza di input mock ha meno elementi di quanti ne richiede il loop
- Aggiungere un valore valido finale alla `sequenza_input` per permettere l'uscita dal loop

---

## 🚀 Risultato Finale Atteso

Una volta completata l'implementazione:

✅ **TUI Funzionante**: `python main.py` avvia il flusso di configurazione completo
✅ **Accessibilità Garantita**: output testuale lineare, compatibile NVDA/JAWS/Orca (TC05 superato)
✅ **Validazione Robusta**: tutti i casi di errore gestiti (TC01–TC04 superati)
✅ **Zero Stringhe Hardcoded**: ogni testo da `MESSAGGI_CONFIGURAZIONE` in `it.py`
✅ **Logging Operativo**: eventi `[TUI]` visibili nei log (INFO/WARNING/DEBUG)
✅ **Test Suite Verde**: 7 unit test + 1 integration test passano
✅ **Documentazione Allineata**: README, CHANGELOG, API, ARCHITECTURE, LOGGING aggiornati

**Metriche Successo**:
- Coverage `ui_terminale.py`: ≥ 90%
- Commit atomici: 6 (nessun commit "WIP" o misto)
- Stringhe hardcoded in `ui_terminale.py`: 0
- Violazioni layer architetturali: 0

---

## 📊 Progress Tracking

| Fase | Operazione | Status | Commit | Data | Note |
|---|---|---|---|---|---|
| Fase 1 | CREARE `codici_configurazione.py` | [ ] | — | — | Prerequisito per Fase 2 |
| Fase 2 | ESTENDERE `it.py` | [ ] | — | — | Prerequisito per Fase 3 |
| Fase 3 | IMPLEMENTARE `TerminalUI` | [ ] | — | — | Core della feature |
| Fase 4 | AGGIORNARE `main.py` | [ ] | — | — | Abilita test manuali TC01-TC05 |
| Fase 5 | CREARE unit tests | [ ] | — | — | 7 test, tutti verdi richiesti |
| Fase 5b | Eseguire TC05 manuale | [ ] | — | — | Screen reader test |
| Fase 6 | Aggiornamenti documentali | [ ] | — | — | Post-implementazione |
| Review | Code review + merge | [ ] | — | — | Branch -> main |

---

**Fine Piano di Implementazione**

---

*Salvato in: `documentations/PLAN_TERMINAL_START_MENU.md`*
*Basato su: `documentations/DESIGN_TERMINAL_START_MENU.md` v1.2*
*Segue il template: `documentations/templates/TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md`*
*Versione documento: v1.0 — Data: 2026-02-19*
