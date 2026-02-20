# 📋 Piano di Implementazione — Game Loop (v0.9.0)

---

## 📊 Executive Summary

**Tipo**: FEATURE  
**Priorità**: 🔴 CRITICA  
**Stato**: READY  
**Branch**: `feat/v0.9.0-game-loop`  
**Versione Target**: `v0.9.0`  
**Data Creazione**: 2026-02-21  
**Autore**: AI Assistant + Nemex81  
**Effort Stimato**: 12 ore totali (8 ore Copilot + 4 ore review/testing)  
**Commits Previsti**: 5 commit atomici

---

### Problema/Obiettivo

Implementare il Game Loop interattivo della TUI di tombola-stark: la macchina a stati `_loop_partita` che governa ogni turno di gioco, la gestione di tutti i comandi utente (`p`, `s`, `c`, `v`, `q`, `?`), la vocalizzazione gerarchica dei risultati e il report finale di partita.

Le **decisioni di design risolte** (da `DESIGN_GAME_LOOP.md`) che guidano questo piano sono:

- **Flessibilità Marcatura**: è consentito segnare qualsiasi numero già estratto (presente nel tabellone), non solo l'ultimo. Garantisce tolleranza agli errori dell'utente.
- **Azioni Informative**: nessun limite al numero di azioni informative (`s`, `c`, `?`) eseguibili prima di avanzare il turno. L'utente ha controllo totale.
- **Comando Help (`?`)**: mostra riepilogo comandi + focus corrente (cartella attiva).
- **Navigazione Cartelle**: rinviata a v0.10.0. Nella v0.9.0 il focus è impostato automaticamente sulla prima cartella (`indice=0`).

---

### Soluzione Proposta

Architettura a **tre componenti coordinati**, rispettando la separazione dei layer:

1. **Infrastruttura (`codici_loop.py` + `it.py`)**: costanti e messaggi UI per il loop.
2. **Controller (`game_controller.py`)**: helper `ottieni_giocatore_umano()` che espone il `GiocatoreUmano` senza che la TUI importi oggetti Domain.
3. **TUI Core (`tui_partita.py`)**: macchina a stati `_loop_partita` + dispatch comandi.
4. **Renderer (`renderer_terminal.py`)**: estensione con vocalizzazione gerarchica e report finale.

> **Vincolo architetturale**: la TUI non importa MAI classi del Domain Layer (`GiocatoreUmano`, `Partita`, `Tabellone`, ecc.). Ogni accesso al dominio passa attraverso il Controller.

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---------|---------|------|
| **Severità** | ALTA | Blocca tutte le sessioni di gioco interattivo |
| **Scope** | 6 file (3 nuovi, 3 modificati) | Vedere File Structure |
| **Rischio regressione** | MEDIO | Il Controller viene esteso, non modificato |
| **Breaking changes** | NO | Nessuna API pubblica esistente viene alterata |
| **Testing** | COMPLESSO | Richiede mock di `Partita` + test di flusso |

---

## 🎯 Requisiti Funzionali

### 1. Loop Principale con Macchina a Stati

**Comportamento Atteso**:
1. Al lancio del loop il sistema imposta automaticamente il focus sulla prima cartella (indice 0).
2. Il loop estrae il numero corrente e lo vocalizza.
3. L'utente può eseguire un numero illimitato di azioni informative (`s`, `c`, `?`) prima di confermare il turno con `p`.
4. Il comando `p` avanza il turno (estrazione successiva) e riavvia il loop.
5. Il comando `q` interrompe la partita previa conferma esplicita, con logging di allerta.
6. Alla fine della partita (tombola o numeri esauriti) viene emesso il report finale.

**File Coinvolti**:
- `bingo_game/ui/tui/tui_partita.py` — DA CREARE 🔧
- `bingo_game/game_controller.py` — MODIFICARE ⚙️

---

### 2. Gestione Segnazione Numero (`s`)

**Comportamento Atteso**:
1. L'utente digita `s <numero>` (es. `s 42`).
2. Il sistema verifica che `<numero>` sia presente nel tabellone (già estratto).
3. Se valido: segna il numero sulla cartella in focus e vocalizza il feedback.
4. Se non estratto: feedback errore, nessuna modifica allo stato.
5. **Qualsiasi numero estratto è segnabile**, non solo l'ultimo — tolleranza errori.

**File Coinvolti**:
- `bingo_game/ui/tui/tui_partita.py` — gestione input `s`
- `bingo_game/ui/renderers/renderer_terminal.py` — `_render_evento_segnazione_numero()` già presente ✅

---

### 3. Comandi Informativi (`c`, `?`)

**Comportamento Atteso**:
- `c`: mostra riepilogo cartella in focus (`EventoRiepilogoCartellaCorrente`).
- `?`: mostra lista comandi disponibili + cartella attualmente in focus.
- Entrambi sono eseguibili senza avanzare il turno (azioni informative pure).

**File Coinvolti**:
- `bingo_game/ui/tui/tui_partita.py` — dispatch comandi
- `bingo_game/ui/locales/it.py` — aggiungere chiavi `LOOP_HELP_*` in `MESSAGGI_OUTPUT_UI_UMANI`

---

### 4. Comando Quit (`q`) con Conferma e Logging

**Comportamento Atteso**:
1. Utente digita `q`.
2. Sistema chiede conferma: `"Vuoi davvero uscire? (s/n)"`.
3. Se confermato: logga un WARNING (`[ALERT] Partita interrotta dall'utente al turno #N`) e termina.
4. Se annullato: riprende il loop corrente senza modifiche.

**File Coinvolti**:
- `bingo_game/ui/tui/tui_partita.py` — logica quit + confirm
- `bingo_game/events/codici_loop.py` — DA CREARE 🔧
- `bingo_game/ui/locales/it.py` — messaggi conferma quit

---

### 5. Report Finale di Partita

**Comportamento Atteso**:
1. Al termine della partita (tombola o numeri esauriti) il renderer emette un report su più righe:
   - Vincitore/i della tombola (se presente).
   - Totale turni giocati.
   - Numeri estratti / 90.
   - Riepilogo premi assegnati.
2. Il report deve essere leggibile anche via screen reader (righe brevi, senza ASCII art).

**File Coinvolti**:
- `bingo_game/ui/renderers/renderer_terminal.py` — aggiungere `_render_report_finale()`
- `bingo_game/events/codici_loop.py` — costante `LOOP_REPORT_FINALE`
- `bingo_game/ui/locales/it.py` — chiavi `LOOP_REPORT_*`

---

## 🏗️ Architettura

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION / TUI LAYER                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ tui_partita.py — _loop_partita()                      │   │
│  │  - _dispatch_comando(cmd, args) → Sequence[str]       │   │
│  │  - _gestisci_quit() → bool                            │   │
│  │  - _gestisci_help() → Sequence[str]                   │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ renderer_terminal.py — TerminalRenderer               │   │
│  │  + _render_report_finale(evento) → Sequence[str]      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲ usa solo dict/EsitoAzione
                            │ NON importa classi Domain
┌─────────────────────────────────────────────────────────────┐
│                 APPLICATION / CONTROLLER LAYER               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ game_controller.py                                    │   │
│  │  + ottieni_giocatore_umano(partita) → GiocatoreUmano │   │
│  │  (già presenti: esegui_turno_sicuro, ottieni_stato)   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│  Partita · GiocatoreUmano · Tabellone · Cartella             │
│  (invariato per v0.9.0)                                      │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
bingo_game/
├── events/
│   └── codici_loop.py                    # NEW — costanti codici loop
├── ui/
│   ├── locales/
│   │   └── it.py                         # MODIFIED — chiavi LOOP_* in MESSAGGI_OUTPUT_UI_UMANI
│   ├── renderers/
│   │   └── renderer_terminal.py          # MODIFIED — _render_report_finale()
│   └── tui/
│       └── tui_partita.py                # NEW — _loop_partita() + dispatch comandi
└── game_controller.py                    # MODIFIED — ottieni_giocatore_umano()

tests/
├── unit/
│   ├── test_codici_loop.py               # NEW: ~5 tests
│   ├── test_game_controller_loop.py      # NEW: ~10 tests
│   └── test_renderer_report_finale.py   # NEW: ~8 tests
└── flow/
    └── test_flusso_game_loop.py          # NEW: ~6 scenari end-to-end

documentations/3 - planning/
└── PLAN_GAME_LOOP.md                     # THIS FILE
```

---

## 📝 Piano di Implementazione

### FASE 1: Infrastruttura — Costanti e Messaggi

**Priorità**: 🔴 CRITICA  
**File nuovi**: `bingo_game/events/codici_loop.py`  
**File modificati**: `bingo_game/ui/locales/it.py`

#### 1a. Creare `bingo_game/events/codici_loop.py`

```python
# bingo_game/events/codici_loop.py
"""
Costanti per i codici di evento del Game Loop (v0.9.0).
"""
from __future__ import annotations

# ---- Codici loop principali ----
LOOP_TURNO_AVANZATO          = "loop.turno_avanzato"
LOOP_NUMERO_ESTRATTO         = "loop.numero_estratto"
LOOP_SEGNAZIONE_OK           = "loop.segnazione_ok"
LOOP_REPORT_FINALE           = "loop.report_finale"
LOOP_QUIT_CONFERMATO         = "loop.quit_confermato"
LOOP_QUIT_ANNULLATO          = "loop.quit_annullato"
LOOP_HELP                    = "loop.help"
LOOP_FOCUS_AUTO              = "loop.focus_auto"
```

**Vantaggi**:
- ✅ Nessuna stringa hardcoded nei layer superiori.
- ✅ Coerente con i moduli `codici_errori.py` e `codici_eventi.py` già esistenti.

#### 1b. Aggiungere chiavi in `it.py` — `MESSAGGI_OUTPUT_UI_UMANI`

Aggiungere le seguenti chiavi al dizionario `MESSAGGI_OUTPUT_UI_UMANI`:

```python
# ---- Game Loop v0.9.0 ----
"LOOP_NUMERO_ESTRATTO":                  ("Numero estratto: {numero}.",),
"LOOP_PROMPT_COMANDO":                   ("Comando (p=prosegui s=segna c=cartella v=tabellone q=esci ?=aiuto):",),
"LOOP_HELP_COMANDI":                     (
    "p — prosegui al prossimo turno",
    "s <N> — segna il numero N sulla cartella",
    "c — riepilogo cartella in focus",
    "v — riepilogo tabellone",
    "q — esci dalla partita (chiede conferma)",
    "? — mostra questo aiuto",
),
"LOOP_HELP_FOCUS":                       ("Cartella in focus: {numero_cartella}.",),
"LOOP_QUIT_CONFERMA":                    ("Vuoi davvero uscire? La partita non verrà salvata. (s/n)",),
"LOOP_QUIT_ANNULLATO":                   ("Uscita annullata. Partita in corso.",),
"LOOP_REPORT_FINALE_INTESTAZIONE":       ("=== FINE PARTITA ===",),
"LOOP_REPORT_FINALE_TURNI":              ("Turni giocati: {turni}.",),
"LOOP_REPORT_FINALE_ESTRATTI":           ("Numeri estratti: {estratti}/90.",),
"LOOP_REPORT_FINALE_VINCITORE":          ("Vincitore Tombola: {nome}!",),
"LOOP_REPORT_FINALE_NESSUN_VINCITORE":   ("Partita terminata senza tombola.",),
"LOOP_REPORT_FINALE_PREMI":              ("Premi assegnati: {premi}.",),
"LOOP_COMANDO_NON_RICONOSCIUTO":         ("Comando non riconosciuto. Digita ? per l'aiuto.",),
```

**Rationale**:
- Tutti i testi UI sono in `it.py`, mai hardcoded nella TUI o nel renderer.
- Il renderer e la TUI leggono da `MESSAGGI_OUTPUT_UI_UMANI` come già avviene per tutti gli altri eventi.

#### Testing Fase 1

```python
# tests/unit/test_codici_loop.py
def test_costanti_loop_sono_stringhe():
    from bingo_game.events.codici_loop import LOOP_TURNO_AVANZATO
    assert isinstance(LOOP_TURNO_AVANZATO, str)

def test_chiavi_messaggi_loop_presenti_in_it():
    from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI
    chiavi_attese = [
        "LOOP_NUMERO_ESTRATTO", "LOOP_PROMPT_COMANDO", "LOOP_HELP_COMANDI",
        "LOOP_QUIT_CONFERMA", "LOOP_REPORT_FINALE_INTESTAZIONE",
    ]
    for chiave in chiavi_attese:
        assert chiave in MESSAGGI_OUTPUT_UI_UMANI, f"Chiave mancante: {chiave}"
```

**Commit Message**:
```
feat(infra): add codici_loop.py and LOOP_* keys in it.py for v0.9.0 game loop

- New: bingo_game/events/codici_loop.py with 8 loop event constants
- Modified: it.py — added 13 LOOP_* keys in MESSAGGI_OUTPUT_UI_UMANI
- All UI strings centralized in locale catalogue (no hardcoding)

Impact:
- Enables Fase 2–4 without modifying locale structure
- Zero breaking changes to existing keys

Testing:
- test_codici_loop.py: 5 unit tests
```

---

### FASE 2: Controller — Helper `ottieni_giocatore_umano`

**Priorità**: 🔴 CRITICA  
**File**: `bingo_game/game_controller.py`  

#### Codice da Aggiungere

```python
def ottieni_giocatore_umano(partita: Partita) -> Optional[GiocatoreUmano]:
    """
    Ritorna il primo GiocatoreUmano della partita, oppure None se non trovato.

    Scopo:
    - Permettere alla TUI di accedere al GiocatoreUmano senza importare
      classi del Domain Layer.
    - La TUI chiama questo helper e ottiene l'oggetto; non ne conosce
      il tipo concreto (Duck Typing sufficiente).

    Parametri:
    - partita: Partita — istanza in qualsiasi stato.

    Ritorna:
    - GiocatoreUmano: il primo giocatore umano trovato.
    - None: se nessun GiocatoreUmano è presente.

    Raises:
    - ValueError: se partita non è un'istanza di Partita.

    Version:
        v0.9.0: Prima implementazione per il Game Loop.
    """
    if not isinstance(partita, Partita):
        raise ValueError(
            f"ottieni_giocatore_umano: atteso Partita, ricevuto {type(partita).__name__}"
        )

    for giocatore in partita.get_giocatori():
        if isinstance(giocatore, GiocatoreUmano):
            _log_safe(
                "[GAME] ottieni_giocatore_umano: trovato '%s'.",
                "debug", giocatore.nome, logger=_logger_game
            )
            return giocatore

    _log_safe(
        "[GAME] ottieni_giocatore_umano: nessun GiocatoreUmano trovato.",
        "warning", logger=_logger_game
    )
    return None
```

**Vantaggi**:
- ✅ La TUI resta isolata dal Domain Layer.
- ✅ Pattern già usato per `ottieni_stato_sintetico` e `esegui_turno_sicuro`.
- ✅ Log consistente con il resto del controller.

#### Testing Fase 2

```python
# tests/unit/test_game_controller_loop.py
def test_ottieni_giocatore_umano_presente():
    partita = _crea_partita_test()  # fixture helper
    giocatore = ottieni_giocatore_umano(partita)
    assert giocatore is not None
    assert hasattr(giocatore, 'nome')

def test_ottieni_giocatore_umano_non_presente_ritorna_none():
    partita = _crea_partita_solo_bot()  # fixture solo bot
    giocatore = ottieni_giocatore_umano(partita)
    assert giocatore is None

def test_ottieni_giocatore_umano_parametro_non_partita():
    with pytest.raises(ValueError):
        ottieni_giocatore_umano("non_una_partita")
```

**Commit Message**:
```
feat(controller): add ottieni_giocatore_umano() helper for TUI isolation

- Added: ottieni_giocatore_umano(partita) in game_controller.py
- Returns first GiocatoreUmano or None, no Domain imports in TUI
- Consistent logging with _log_safe / _logger_game

Impact:
- TUI can access human player without importing Domain classes
- No changes to existing public API

Testing:
- test_game_controller_loop.py: 10 unit tests
```

---

### FASE 3: TUI Core — `_loop_partita` e Dispatch Comandi

**Priorità**: 🔴 CRITICA  
**File**: `bingo_game/ui/tui/tui_partita.py` (NUOVO)

#### Struttura del Modulo

```python
# bingo_game/ui/tui/tui_partita.py
"""
TUI interattiva per il ciclo di gioco (Game Loop) — v0.9.0.

Responsabilità:
- Macchina a stati _loop_partita: governa ogni turno di gioco.
- Dispatch dei comandi utente: p, s, c, v, q, ?.
- Interfaccia testuale pura: legge input da stdin, scrive su stdout.
- NON importa classi Domain (GiocatoreUmano, Partita, ecc.).
  Accede al dominio esclusivamente tramite game_controller.
"""
from __future__ import annotations
import logging
from typing import Optional

from bingo_game.game_controller import (
    esegui_turno_sicuro,
    ottieni_stato_sintetico,
    ottieni_giocatore_umano,
    partita_terminata,
)
from bingo_game.ui.locales import MESSAGGI_OUTPUT_UI_UMANI
from bingo_game.ui.renderers.renderer_terminal import TerminalRenderer

_logger_tui = logging.getLogger("tombola_stark.tui")
_renderer   = TerminalRenderer()


def _loop_partita(partita) -> None:
    """
    Macchina a stati principale del Game Loop.

    Flusso per ogni turno:
    1. Imposta focus automatico sulla prima cartella (se non già impostato).
    2. Attende input utente.
    3. Dispatcha il comando.
    4. Se comando=p: avanza il turno (esegui_turno_sicuro).
    5. Ripete fino a partita terminata o quit confermato.

    Separazione layer:
    - Non importa Partita, GiocatoreUmano o altri Domain objects.
    - Riceve `partita` come opaque handle passato dal chiamante.

    Args:
        partita: handle opaco della partita (istanza Partita, non tipizzata
                 qui per non violare la separazione dei layer).

    Version:
        v0.9.0: Prima implementazione.
    """
    # 1. Focus automatico sulla prima cartella
    giocatore = ottieni_giocatore_umano(partita)
    if giocatore is not None:
        try:
            giocatore.imposta_focus_cartella(0)  # 0-based, prima cartella
        except Exception:
            pass  # Il focus non è bloccante

    # 2. Prompt iniziale
    _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_PROMPT_COMANDO"][0])

    # 3. Loop principale
    while not partita_terminata(partita):
        raw = input("> ").strip()
        if not raw:
            continue

        parti = raw.split(maxsplit=1)
        cmd   = parti[0].lower()
        args  = parti[1] if len(parti) > 1 else ""

        # --- Azioni informative (nessun limite) ---
        if cmd == "?":
            for riga in _gestisci_help(partita):
                _stampa(riga)
            continue

        if cmd == "c":
            for riga in _gestisci_riepilogo_cartella(partita):
                _stampa(riga)
            continue

        if cmd == "v":
            for riga in _gestisci_riepilogo_tabellone(partita):
                _stampa(riga)
            continue

        if cmd == "s":
            for riga in _gestisci_segna(partita, args):
                _stampa(riga)
            continue

        # --- Azione avanzamento turno ---
        if cmd == "p":
            risultato = esegui_turno_sicuro(partita)
            if risultato is None:
                _stampa("Errore durante l'avanzamento del turno.")
                continue
            numero = risultato.get("numero_estratto", "?")
            _stampa(
                MESSAGGI_OUTPUT_UI_UMANI["LOOP_NUMERO_ESTRATTO"][0].format(
                    numero=numero
                )
            )
            _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_PROMPT_COMANDO"][0])
            continue

        # --- Quit con conferma ---
        if cmd == "q":
            if _gestisci_quit(partita):
                break  # Uscita confermata
            continue

        # --- Comando non riconosciuto ---
        _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_COMANDO_NON_RICONOSCIUTO"][0])

    # 4. Report finale (partita terminata o quit)
    _emetti_report_finale(partita)


def _gestisci_help(partita) -> list[str]:
    """
    Ritorna le righe del comando ?:
    - lista comandi
    - cartella attualmente in focus
    """
    righe: list[str] = list(MESSAGGI_OUTPUT_UI_UMANI["LOOP_HELP_COMANDI"])
    giocatore = ottieni_giocatore_umano(partita)
    if giocatore is not None:
        try:
            focus = giocatore.get_focus_cartella()
            if focus is not None:
                numero_cartella = focus + 1  # 0-based -> 1-based
                righe.append(
                    MESSAGGI_OUTPUT_UI_UMANI["LOOP_HELP_FOCUS"][0].format(
                        numero_cartella=numero_cartella
                    )
                )
        except Exception:
            pass
    return righe


def _gestisci_segna(partita, args: str) -> list[str]:
    """
    Gestisce il comando s <numero>.

    Flessibilità marcatura (decisione v0.9.0):
    - È consentito segnare qualsiasi numero già estratto (presente nel tabellone),
      non solo l'ultimo estratto.

    Args:
        partita: handle opaco partita.
        args: stringa contenente il numero da segnare (es. "42").

    Returns:
        list[str]: righe di feedback da stampare.
    """
    try:
        numero = int(args.strip())
    except (ValueError, AttributeError):
        return ["Numero non valido. Uso: s <numero>"]

    giocatore = ottieni_giocatore_umano(partita)
    if giocatore is None:
        return ["Giocatore umano non trovato."]

    try:
        esito = giocatore.segna_numero(numero)
        return list(_renderer.render_esito(esito))
    except Exception as exc:
        _logger_tui.warning("[TUI] _gestisci_segna: eccezione. %s", exc)
        return ["Errore durante la segnazione."]


def _gestisci_riepilogo_cartella(partita) -> list[str]:
    """Ritorna il riepilogo della cartella in focus."""
    giocatore = ottieni_giocatore_umano(partita)
    if giocatore is None:
        return ["Giocatore umano non trovato."]
    try:
        esito = giocatore.riepilogo_cartella_corrente()
        return list(_renderer.render_esito(esito))
    except Exception as exc:
        _logger_tui.warning("[TUI] _gestisci_riepilogo_cartella: eccezione. %s", exc)
        return ["Errore nel riepilogo cartella."]


def _gestisci_riepilogo_tabellone(partita) -> list[str]:
    """Ritorna il riepilogo del tabellone."""
    try:
        stato = ottieni_stato_sintetico(partita)
        estratti = len(stato.get("numeri_estratti", []))
        ultimo   = stato.get("ultimo_numero_estratto")
        riga_estratti = f"Estratti: {estratti}/90."
        riga_ultimo   = f"Ultimo numero: {ultimo}." if ultimo else "Nessun numero estratto."
        return [riga_estratti, riga_ultimo]
    except Exception as exc:
        _logger_tui.warning("[TUI] _gestisci_riepilogo_tabellone: eccezione. %s", exc)
        return ["Errore nel riepilogo tabellone."]


def _gestisci_quit(partita) -> bool:
    """
    Gestisce il comando q con conferma esplicita.

    Decisione v0.9.0:
    - Il quit richiede sempre conferma (prevenzione uscite accidentali).
    - Se confermato, logga un WARNING con il turno corrente.

    Returns:
        True se l'utente ha confermato l'uscita, False altrimenti.
    """
    _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_QUIT_CONFERMA"][0])
    risposta = input("> ").strip().lower()
    if risposta == "s":
        try:
            stato = ottieni_stato_sintetico(partita)
            turno = len(stato.get("numeri_estratti", []))
        except Exception:
            turno = "?"
        _logger_tui.warning(
            "[ALERT] Partita interrotta dall'utente al turno #%s.", turno
        )
        return True
    _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_QUIT_ANNULLATO"][0])
    return False


def _emetti_report_finale(partita) -> None:
    """Stampa il report finale a partita conclusa."""
    try:
        stato = ottieni_stato_sintetico(partita)
        righe = _costruisci_report_finale(stato)
        for riga in righe:
            _stampa(riga)
    except Exception as exc:
        _logger_tui.warning("[TUI] _emetti_report_finale: eccezione. %s", exc)


def _costruisci_report_finale(stato: dict) -> list[str]:
    """Costruisce le righe del report finale a partire dallo stato sintetico."""
    M = MESSAGGI_OUTPUT_UI_UMANI
    righe: list[str] = [
        M["LOOP_REPORT_FINALE_INTESTAZIONE"][0],
        M["LOOP_REPORT_FINALE_TURNI"][0].format(
            turni=len(stato.get("numeri_estratti", []))
        ),
        M["LOOP_REPORT_FINALE_ESTRATTI"][0].format(
            estratti=len(stato.get("numeri_estratti", []))
        ),
    ]
    vincitori = [
        g["nome"] for g in stato.get("giocatori", []) if g.get("ha_tombola")
    ]
    if vincitori:
        for nome in vincitori:
            righe.append(M["LOOP_REPORT_FINALE_VINCITORE"][0].format(nome=nome))
    else:
        righe.append(M["LOOP_REPORT_FINALE_NESSUN_VINCITORE"][0])
    righe.append(
        M["LOOP_REPORT_FINALE_PREMI"][0].format(
            premi=len(stato.get("premi_gia_assegnati", []))
        )
    )
    return righe


def _stampa(riga: str) -> None:
    """Wrapper su print — facilita il mock nei test."""
    print(riga)
```

**Rationale architetturale**:
1. `_loop_partita` non conosce `Partita`, `GiocatoreUmano` o `Tabellone` — li riceve come handle opaco.
2. Ogni comando è una funzione `_gestisci_*` con contratto `list[str]` — testabile isolatamente.
3. `_gestisci_quit` logga su `tombola_stark.tui` con level WARNING per visibilità nel log.
4. Le azioni informative (`?`, `c`, `v`, `s`) non chiamano mai `esegui_turno_sicuro` — nessun side effect sul game state.

#### Testing Fase 3

```python
# tests/unit/test_tui_partita.py
def test_gestisci_quit_confermato(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 's')
    assert _gestisci_quit(_mock_partita()) is True

def test_gestisci_quit_annullato(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    assert _gestisci_quit(_mock_partita()) is False

def test_gestisci_segna_numero_non_valido():
    righe = _gestisci_segna(_mock_partita(), "xyz")
    assert "non valido" in righe[0].lower()

def test_costruisci_report_finale_con_vincitore():
    stato = {"numeri_estratti": list(range(45)), "giocatori": [{"nome": "Mario", "ha_tombola": True}], "premi_gia_assegnati": ["tombola"]}
    righe = _costruisci_report_finale(stato)
    assert any("Mario" in r for r in righe)
```

**Commit Message**:
```
feat(tui): implement _loop_partita state machine and command dispatch

- New: bingo_game/ui/tui/tui_partita.py
- State machine: p/s/c/v/q/? commands with unlimited informative actions
- Marking flexibility: any extracted number can be marked (not only last)
- Quit: explicit confirmation + WARNING log with turn number
- No Domain Layer imports in TUI (controller-only access)
- Auto-focus on first card at loop start

Impact:
- Core interactive loop for v0.9.0
- Card navigation deferred to v0.10.0 (focus auto = first card)

Testing:
- test_tui_partita.py: unit tests per comando
```

---

### FASE 4: Renderer — Vocalizzazione Gerarchica e Report Finale

**Priorità**: 🟠 ALTA  
**File**: `bingo_game/ui/renderers/renderer_terminal.py`

#### Metodo da Aggiungere: `_render_report_finale`

Il renderer viene esteso con il supporto per un ipotetico `EventoReportFinale` (o i dati vengono passati direttamente come dict dalla TUI tramite `_costruisci_report_finale`). Per coerenza con il progetto, la TUI usa `_costruisci_report_finale` internamente; il renderer resta agnostico dal loop.

Per la **vocalizzazione gerarchica** (screen reader) il renderer deve garantire:
- Ogni riga è autonoma e leggibile senza contesto precedente.
- Nessuna riga supera i 100 caratteri (limite screen reader).
- Il report finale usa separatori testuali (`===`) senza ASCII art.

Se in futuro si vorrà aggiungere un `EventoReportFinale` al catalogo eventi, si potrà aggiungere la gestione in `render_esito()` (step 29) senza breaking changes.

**Nessuna modifica al corpo del renderer** è necessaria per la Fase 4: la vocalizzazione gerarchica è già garantita dai metodi esistenti. L'unica verifica richiesta è che:

```python
# Verificare che _render_evento_riepilogo_tabellone restituisca
# esattamente 3 righe autonome compatibili con TTS
righe = renderer._render_evento_riepilogo_tabellone(evento_mock)
assert len(righe) == 3
assert all(isinstance(r, str) for r in righe)
```

#### Testing Fase 4

```python
# tests/unit/test_renderer_report_finale.py
def test_render_riepilogo_tabellone_3_righe():
    renderer = TerminalRenderer()
    evento = EventoRiepilogoTabellone(
        totale_estratti=10, totale_numeri=90, totale_mancanti=80,
        percentuale_estrazione=11.1, ultimi_estratti=(5, 12, 33),
        ultimi_visualizzati=3, ultimo_estratto=33,
    )
    righe = renderer._render_evento_riepilogo_tabellone(evento)
    assert len(righe) == 3
    assert all(len(r) <= 120 for r in righe)

def test_render_segnazione_numero_segnato():
    renderer = TerminalRenderer()
    evento = EventoSegnazioneNumero(
        numero=42, esito="segnato", numero_cartella=1,
        indice_riga=0, indice_colonna=4
    )
    righe = renderer._render_evento_segnazione_numero(evento)
    assert len(righe) == 1
    assert "42" in righe[0]
```

**Commit Message**:
```
feat(renderer): verify hierarchical vocalization for game loop events

- Validated: _render_evento_riepilogo_tabellone returns 3 TTS-safe rows
- Validated: _render_evento_segnazione_numero handles all 4 outcomes
- Added: 8 new unit tests for renderer loop coverage
- No structural changes (renderer already complete for v0.9.0 scope)

Impact:
- Screen reader compatibility confirmed for game loop output
- Zero breaking changes

Testing:
- test_renderer_report_finale.py: 8 unit tests
```

---

### FASE 5: Chiusura — Test, Regressione e Docs

**Priorità**: 🟠 ALTA  
**File**: test suite + documentazione

#### 5a. Test di Regressione (272+ test esistenti)

```bash
# Esegui TUTTI i test esistenti: nessuna regressione ammessa
python -m pytest tests/ -v --tb=short
# Target: 272+ test PASSED, 0 FAILED, 0 ERROR
```

Se qualche test fallisce a causa delle modifiche a `game_controller.py` o `it.py`, correggere prima di procedere con i test di flusso.

#### 5b. Test di Flusso End-to-End

```python
# tests/flow/test_flusso_game_loop.py
def test_flusso_p_avanza_turno():
    """Simula: avvio loop → p → turno avanzato → loop prosegue."""
    ...

def test_flusso_s_segna_numero_estratto():
    """Simula: avvio → p (estrae 42) → s 42 → numero segnato."""
    ...

def test_flusso_s_numero_non_estratto_errore():
    """Simula: s 42 senza aver estratto 42 → errore non estratto."""
    ...

def test_flusso_q_conferma_uscita():
    """Simula: q → s (conferma) → log WARNING emesso."""
    ...

def test_flusso_q_annulla_continua():
    """Simula: q → n (annulla) → loop continua."""
    ...

def test_flusso_report_finale_tombola():
    """Simula partita fino a tombola → report con vincitore."""
    ...
```

#### 5c. Aggiornamento Documentazione

| File | Modifica |
|------|----------|
| `docs/API.md` | Aggiungere sezione `ottieni_giocatore_umano()` + `_loop_partita()` |
| `docs/ARCHITECTURE.md` | Aggiornare Layer Diagram con `tui_partita.py` e `codici_loop.py` |
| `docs/README.md` | Aggiornare sezione "Come si gioca" con lista comandi v0.9.0 |
| `docs/CHANGELOG.md` | Aggiungere entry `[0.9.0] - Game Loop` |

**Commit Message**:
```
docs(v0.9.0): update API.md, ARCHITECTURE.md, README.md, CHANGELOG.md

- API.md: added ottieni_giocatore_umano() and _loop_partita() docs
- ARCHITECTURE.md: updated layer diagram with TUI and codici_loop
- README.md: added game commands section (p/s/c/v/q/?)
- CHANGELOG.md: added [0.9.0] Game Loop entry

Testing:
- 272+ existing tests: all PASSED
- 6 new flow tests: all PASSED
```

---

## 🧪 Testing Strategy

### Unit Tests (~31 test nuovi)

#### `tests/unit/test_codici_loop.py` (5 test)
- [ ] Costanti sono stringhe non vuote
- [ ] Nessuna costante duplicata
- [ ] Chiavi LOOP_* presenti in `MESSAGGI_OUTPUT_UI_UMANI`
- [ ] Template con placeholder formattabili
- [ ] Import `codici_loop` senza side effect

#### `tests/unit/test_game_controller_loop.py` (10 test)
- [ ] `ottieni_giocatore_umano` ritorna primo umano
- [ ] Ritorna `None` se solo bot
- [ ] Raises `ValueError` su input non-Partita
- [ ] Log WARNING se nessun umano trovato
- [ ] Nessuna regressione su `crea_partita_standard`

#### `tests/unit/test_tui_partita.py` (8 test)
- [ ] `_gestisci_quit` → True se confermato
- [ ] `_gestisci_quit` → False se annullato
- [ ] `_gestisci_segna` → errore su input non numerico
- [ ] `_gestisci_help` → contiene tutte le chiavi comandi
- [ ] `_costruisci_report_finale` → contiene vincitore se presente
- [ ] `_costruisci_report_finale` → "nessun vincitore" se assente
- [ ] `_gestisci_riepilogo_tabellone` → 2 righe
- [ ] `_loop_partita` → focus auto su prima cartella

#### `tests/unit/test_renderer_report_finale.py` (8 test)
- [ ] `_render_evento_riepilogo_tabellone` → 3 righe
- [ ] Nessuna riga supera 120 caratteri
- [ ] `_render_evento_segnazione_numero` → 1 riga per ogni esito
- [ ] Test con `EventoFineTurno` → 1 riga

### Integration / Flow Tests (6 scenari)

#### `tests/flow/test_flusso_game_loop.py`
- [ ] Flusso `p` avanza turno
- [ ] Flusso `s` segna numero estratto
- [ ] Flusso `s` numero non estratto → errore
- [ ] Flusso `q` + conferma → log WARNING
- [ ] Flusso `q` + annulla → loop continua
- [ ] Flusso partita completa → report finale con vincitore

---

## ✅ Validation & Acceptance

### Success Criteria

**Funzionali**:
- [ ] Comando `p` avanza il turno e vocalizza il numero estratto
- [ ] Comando `s <N>` segna qualsiasi numero estratto (non solo l'ultimo)
- [ ] Comando `?` mostra help + cartella in focus
- [ ] Comando `q` chiede conferma prima di uscire
- [ ] Report finale mostra vincitore/i, turni, numeri estratti, premi
- [ ] Focus automatico su prima cartella all'avvio del loop

**Tecnici**:
- [ ] Zero breaking changes su API esistenti
- [ ] 272+ test di regressione: tutti PASSED
- [ ] 31+ nuovi unit test: tutti PASSED
- [ ] 6 test di flusso: tutti PASSED
- [ ] Nessuna importazione Domain Layer in `tui_partita.py`
- [ ] Quit logga WARNING con numero turno

**Code Quality**:
- [ ] PEP8 compliant (max-line-length=120)
- [ ] Type hints completi nei metodi pubblici
- [ ] Docstring Google style su tutti i metodi pubblici
- [ ] `CHANGELOG.md` aggiornato con `[0.9.0]`

**Accessibilità**:
- [ ] Nessuna riga output supera 120 caratteri
- [ ] Report finale leggibile via screen reader
- [ ] Ogni riga di output è autonoma e autoesplicativa

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T — Importare Domain Layer nella TUI

```python
# WRONG — viola separazione dei layer
from bingo_game.players import GiocatoreUmano  # ❌

def _gestisci_segna(partita, args):
    if isinstance(partita.get_giocatori()[0], GiocatoreUmano):  # ❌
        ...
```

### ✅ DO — Usare il Controller come mediatore

```python
# CORRECT — la TUI non sa chi è GiocatoreUmano
from bingo_game.game_controller import ottieni_giocatore_umano  # ✅

def _gestisci_segna(partita, args):
    giocatore = ottieni_giocatore_umano(partita)  # ✅ — opaque handle
    if giocatore is not None:
        esito = giocatore.segna_numero(numero)
```

---

### ❌ DON'T — Avanzare il turno su comandi informativi

```python
# WRONG — s non deve chiamare esegui_turno_sicuro
def _gestisci_segna(partita, args):
    giocatore.segna_numero(numero)
    esegui_turno_sicuro(partita)  # ❌ avanza turno inaspettatamente
```

### ✅ DO — Separare azioni informative da avanzamento

```python
# CORRECT — solo 'p' chiama esegui_turno_sicuro
if cmd == "s":
    for riga in _gestisci_segna(partita, args):  # nessun side effect turno
        _stampa(riga)
    continue  # ✅ — loop riprende senza avanzare
```

---

## 📦 Commit Strategy

### Atomic Commits (5 totali)

1. **Commit 1** — Infrastruttura
   - `feat(infra): add codici_loop.py and LOOP_* keys in it.py for v0.9.0 game loop`
   - Files: `bingo_game/events/codici_loop.py`, `bingo_game/ui/locales/it.py`
   - Tests: `tests/unit/test_codici_loop.py`

2. **Commit 2** — Controller
   - `feat(controller): add ottieni_giocatore_umano() helper for TUI isolation`
   - Files: `bingo_game/game_controller.py`
   - Tests: `tests/unit/test_game_controller_loop.py`

3. **Commit 3** — TUI Core
   - `feat(tui): implement _loop_partita state machine and command dispatch`
   - Files: `bingo_game/ui/tui/tui_partita.py`
   - Tests: `tests/unit/test_tui_partita.py`

4. **Commit 4** — Renderer
   - `feat(renderer): verify hierarchical vocalization for game loop events`
   - Files: `bingo_game/ui/renderers/renderer_terminal.py` (se necessario)
   - Tests: `tests/unit/test_renderer_report_finale.py`

5. **Commit 5** — Chiusura
   - `docs(v0.9.0): update API.md, ARCHITECTURE.md, README.md, CHANGELOG.md`
   - Files: `docs/API.md`, `docs/ARCHITECTURE.md`, `docs/README.md`, `docs/CHANGELOG.md`
   - Tests: `tests/flow/test_flusso_game_loop.py` (suite completa)

---

## 📚 References

### Internal Architecture Docs
- `documentations/DESIGN_GAME_LOOP.md` — Design decisions v0.9.0
- `docs/ARCHITECTURE.md` — Clean Architecture layers
- `docs/API.md` — Public API reference
- `documentations/1 - templates/TEMPLATE_example_PIANO_IMPLEMENTAZIONE.md` — Template usato

### Related Code Files
- `bingo_game/game_controller.py` — Controller layer (orchestration)
- `bingo_game/ui/renderers/renderer_terminal.py` — TerminalRenderer esistente
- `bingo_game/ui/locales/it.py` — Catalogo messaggi italiano
- `bingo_game/events/codici_errori.py` — Pattern costanti eventi esistente
- `bingo_game/events/codici_eventi.py` — Pattern costanti eventi esistente

---

## 📝 Note Operative per Copilot

### Istruzioni Step-by-Step

1. **Fase 1 — Infrastruttura**:
   - Crea `bingo_game/events/codici_loop.py` con le 8 costanti indicate.
   - Apri `bingo_game/ui/locales/it.py`, naviga a `MESSAGGI_OUTPUT_UI_UMANI` e aggiungi le 13 chiavi `LOOP_*` in fondo al dizionario.
   - Salva entrambi i file.

2. **Fase 2 — Controller**:
   - Apri `bingo_game/game_controller.py`.
   - Aggiungi la funzione `ottieni_giocatore_umano()` dopo `partita_terminata()` (ultima funzione del file).
   - Nessuna modifica alle funzioni esistenti.

3. **Fase 3 — TUI Core**:
   - Crea `bingo_game/ui/tui/tui_partita.py` con il contenuto indicato.
   - Verifica che non ci siano import di classi Domain (`GiocatoreUmano`, `Partita`, ecc.).

4. **Fase 4 — Renderer**:
   - Esegui i test `test_renderer_report_finale.py` senza modificare il renderer.
   - Se un test fallisce, aggiungi solo il minimo necessario al renderer.

5. **Fase 5 — Chiusura**:
   - Esegui `python -m pytest tests/ -v` e verifica 272+ PASSED.
   - Aggiorna i 4 file di documentazione.

### Verifica Rapida Pre-Commit

```bash
# Sintassi
python -m py_compile bingo_game/events/codici_loop.py
python -m py_compile bingo_game/ui/tui/tui_partita.py

# Type check (opzionale)
mypy bingo_game/ui/tui/tui_partita.py --strict

# Style
pycodestyle bingo_game/ui/tui/tui_partita.py --max-line-length=120

# Test regressione
python -m pytest tests/ -v --tb=short

# Test nuovi
python -m pytest tests/unit/test_codici_loop.py tests/unit/test_game_controller_loop.py tests/unit/test_tui_partita.py tests/unit/test_renderer_report_finale.py tests/flow/test_flusso_game_loop.py -v
```

### Troubleshooting

**Se `ottieni_giocatore_umano` non trova il giocatore**:
- Verifica che `crea_partita_standard` sia chiamata con `nome_giocatore_umano` non vuoto.
- Controlla che `partita.get_giocatori()` ritorni la lista completa.

**Se la TUI importa classi Domain**:
- Sostituisci l'import diretto con una chiamata a `ottieni_giocatore_umano(partita)`.
- Il typing hint del parametro `partita` in `_loop_partita` resta senza annotazione di tipo.

**Se un test di flusso fallisce per `input()`**:
- Usa `monkeypatch.setattr('builtins.input', iter(['p', 'q', 's']).__next__)` per simulare sequenze di comandi.

---

## 🚀 Risultato Finale Atteso

Una volta completata l'implementazione:

✅ **Game Loop Operativo**: la TUI avvia e gestisce un'intera partita interattiva con comandi `p/s/c/v/q/?`.
✅ **Marcatura Flessibile**: l'utente può segnare qualsiasi numero estratto, non solo l'ultimo — tolleranza errori garantita.
✅ **Azioni Informative Illimitate**: `?`, `c`, `v`, `s` non consumano il turno, l'utente ha controllo totale.
✅ **Quit Sicuro**: `q` chiede sempre conferma e logga WARNING con il numero di turno corrente.
✅ **Screen Reader Ready**: ogni riga di output è autonoma, ≤ 120 caratteri, senza ASCII art.
✅ **Zero Regressioni**: 272+ test esistenti tutti PASSED.

---

## 📊 Progress Tracking

| Fase | Status | Commit | Data Completamento | Note |
|------|--------|--------|-------------------|------|
| Fase 1 — Infrastruttura | [ ] PENDING | - | - | `codici_loop.py` + `it.py` |
| Fase 2 — Controller | [ ] PENDING | - | - | `ottieni_giocatore_umano()` |
| Fase 3 — TUI Core | [ ] PENDING | - | - | `tui_partita.py` |
| Fase 4 — Renderer | [ ] PENDING | - | - | Verifica vocalizzazione |
| Fase 5 — Chiusura | [ ] PENDING | - | - | 272+ test + docs |

---

**Fine Piano — PLAN_GAME_LOOP.md**

**Piano Version**: v1.0  
**Data Creazione**: 2026-02-21  
**Autore**: AI Assistant + Nemex81  
**Versione Target**: v0.9.0 — Game Loop  
