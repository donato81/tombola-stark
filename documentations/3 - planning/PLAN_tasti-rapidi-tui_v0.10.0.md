# 📋 Piano di Implementazione - Tasti Rapidi TUI v0.10.0

> **Basato su**: documentations/2 - project/DESIGN_tasti-rapidi-tui.md
> **Obiettivo**: Realizzare la mappatura completa dei tasti rapidi per la
> navigazione e le azioni durante la partita, eliminando i comandi testuali.

---

## 📊 Executive Summary

**Tipo**: FEATURE  
**Priorità**: 🟠 ALTA  
**Stato**: DRAFT  
**Branch**: `refactory-mappatura-tasti-game-play`  
**Versione Target**: `v0.10.0`  
**Data Creazione**: 2026-02-24  
**Autore**: AI Assistant + Donato81  
**Effort Stimato**: 16 ore totali (10 ore Copilot + 6 ore review/testing)  
**Commits Previsti**: 8 commit atomici

---

### Problema/Obiettivo

Il sistema attuale richiede comandi testuali seguiti da Invio per la
navigazione e le azioni di gioco, causando elevata frizione e rallentamento
per l'utente NVDA. La nuova feature introduce tasti rapidi singoli (msvcrt)
per tutte le funzioni di gioco, rendendo l'esperienza fluida e accessibile.


### Soluzione Proposta

Implementare un modulo `tui_commander` che mappi byte (1 o 2) letti da
msvcrt a comandi logici. Separare la logica di interpretazione dal game loop
principale. Creare un file `codici_tasti_tui.py` contenente costanti per i
codici dei tasti speciali. Aggiornare `tui_partita.py` per usare il Commander
invece dei parser testuali esistenti. Estendere `bingo_game/ui/locales/it.py`
con i messaggi richiesti. Aggiornare i test unitari e di integrazione per
coprire i nuovi comportamenti.

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---------|---------|------|
| **Severità** | ALTA | Modifica UX principale della partita; impatta tutti i giocatori |
| **Scope** | 9 file | Vedi elenco file modificati sotto |
| **Rischio regressione** | MEDIO | Tocca game loop e input; regressioni possibili nella gestione focus |
| **Breaking changes** | SÌ | I comandi testuali vengono rimossi; eventuali script esterni devono adattarsi |
| **Testing** | COMPLESSO | Richiede numerosi test unitari e integrazione sul Commander e sul loop |

---

## 🎯 Requisiti Funzionali

### 1. Lettura tasti singoli da terminale

**Comportamento Atteso**:
1. Il sistema legge un byte da msvcrt: se è `\x00` o `\xe0` legge un secondo byte.
2. Il byte o coppia di byte viene passato al Commander per risolvere un comando.
3. Il game loop elabora il comando e ritorna un EsitoAzione.

**File Coinvolti**:
- `bingo_game/ui/tui/tui_commander.py` - [NUOVO]
- `bingo_game/ui/tui/tui_partita.py` - [MODIFICARE]


### 2. Definizione costanti codici tasti

**Comportamento Atteso**:
1. Tutti i codici dei tasti (freccia, pagine, lettere) sono definiti come costanti
   in `codici_tasti_tui.py` con valori corrispondenti a msvcrt.

**File Coinvolti**:
- `bingo_game/events/codici_controller.py` - [MODIFICARE] (se necessario)
- `bingo_game/ui/tui/codici_tasti_tui.py` - [NUOVO]


### 3. Mappatura comandi nel Commander

**Comportamento Atteso**:
1. Il Commander exporta funzione `comando_da_tasto(byte_seq)` restituisce
   callback lambda o enum identificatore.
2. Ogni tasto definito nella mappatura attiva il metodo corrispondente del
   controller (es. `sposta_focus_riga_su_semplice`).
3. Azioni con prompt (R, C, S, V, E, N) devono restituire un indicatore per
   richiedere input successivo.

**File Coinvolti**:
- `bingo_game/ui/tui/tui_commander.py` - [NUOVO]
- `bingo_game/game_controller.py` - [POSSIBILE AGGIUNTA DI METODI DI COMANDO MANCANTI]  
  (già esistono la maggior parte)


### 4. Aggiornamento loop in tui_partita

**Comportamento Atteso**:
1. Sostituire parsing comandi testuali con chiamate a `tui_commander`.
2. Gestire situazioni di prompt numerico e conferma S/N.
3. Rimuovere codice obsoleto relativo ai comandi testuali (es. `comandi_partita`).

**File Coinvolti**:
- `bingo_game/ui/tui/tui_partita.py` - [MODIFICARE]
- `bingo_game/ui/ui_terminale.py` - (verificare eventuali dipendenze)


### 5. Aggiornare localizzazione messaggi

**Comportamento Atteso**:
1. Aggiungere tutte le stringhe usate nella mappatura tasti e nei feedback.
2. Modificare messaggio di aiuto (tasto `?` invece di `H`).

**File Coinvolti**:
- `bingo_game/ui/locales/it.py` - [MODIFICARE]


### 6. Test

**Comportamento Atteso**:
1. Test unitari per ogni metodo del Commander, verificando tasto→comando.
2. Test integrati del game loop usando input simulato per sequenze di tasti.
3. Aggiornare test esistenti di `tui_partita` e controller.

**File Coinvolti**:
- `tests/unit/test_tui_commander.py` - [NUOVO]
- `tests/unit/test_tui_partita.py` - [MODIFICARE]
- `tests/integration/` - [AGGIUNGERE SCENARI DI GIOCO CON TASTI RAPIDI]


---

## 🏗️ Architettura (FEATURE)

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ tui_partita.py (loop + rendering)                     │   │
│  │ tui_commander.py (input handler)                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌────────────────────────┐  ┌─────────────────────────┐    │
│  │ game_controller.py     │  │ codici_tasti_tui.py?    │    │
│  └────────────────────────┘  └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│  ┌────────────────────────┐  ┌─────────────────────────┐    │
│  │ giocatore_*             │  │ partita/tabellone/etc.  │    │
│  └────────────────────────┘  └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
# nuovi/modified
bingo_game/ui/tui/tui_commander.py           # NEW
bingo_game/ui/tui/codici_tasti_tui.py        # NEW
bingo_game/ui/tui/tui_partita.py              # MODIFIED
bingo_game/ui/locales/it.py                  # MODIFIED
bingo_game/game_controller.py                # POSSIBLE minor

tests/unit/test_tui_commander.py            # NEW
tests/unit/test_tui_partita.py               # MODIFIED
tests/integration/test_game_loop_tasti.py     # NEW
```

---

## 📝 Piano di Implementazione

### FASE/COMMIT 1: Creare modulo dei codici tasti

**Priorità**: 🔴 CRITICA  
**File**: `bingo_game/ui/tui/codici_tasti_tui.py`

- Definire costanti per ciascun tasto usato in mappatura (freccia, pagine,
  lettere A,Z,Q,W,R,C,D,F,G,H,U,I,O,L,E,N,?,S,V,P,X).  
- Includere commenti con spiegazione e coppie byte per speciali.

### FASE/COMMIT 2: Sviluppare `tui_commander`

**Priorità**: 🔴 CRITICA  
**File**: `bingo_game/ui/tui/tui_commander.py`

- Funzione `leggi_tasto()` che usa msvcrt.getwch e restituisce stringa.
- Funzione `comando_da_tasto(tasto)` che mappa alle chiamate a game_controller
  o segnala prompt richiesto.
- Enumerare comandi e tradurli in callables o semplici stringhe da gestire nel loop.
- Aggiungere test unitari per ogni mappatura.

### FASE/COMMIT 3: Modificare loop in `tui_partita.py`

**Priorità**: 🟠 ALTA  
**File**: `bingo_game/ui/tui/tui_partita.py`

- Sostituire l'attuale `while` di lettura comandi testuali con chiamata a
  `tui_commander.leggi_tasto()` e `comando_da_tasto`.
- Gestire prompt numerici e conferme.  
- Rimuovere dipendenze da `comandi_partita` e parsing testuale.
- Aggiornare `_stampa()` per eventuali nuovi messaggi.

### FASE/COMMIT 4: Localizzazione e messaggi

**Priorità**: 🟡 MEDIA  
**File**: `bingo_game/ui/locales/it.py`

- Aggiungere tutte le stringhe utilizzate da comandi rapidi e dai feedback
  definiti nel design document.
- Aggiornare messaggio di help e di errore tasto non valido.

### FASE/COMMIT 5: Modifiche minori al controller

**Priorità**: 🟡 MEDIA  
**File**: `bingo_game/game_controller.py`

- Verificare che esistano tutti i metodi richiamati dal Commander.
- Aggiungere eventuali semplici wrapper se serve uniformità (es. segna_numero_manuale
  vs metodo precedente).  
- Aggiornare eventuali docstring.

### FASE/COMMIT 6: Test unitari

**Priorità**: 🔴 CRITICA  
**File**: 
- `tests/unit/test_tui_commander.py` (nuovo)  
- `tests/unit/test_tui_partita.py` (modifiche)

- Scrivere casi per ogni tasto/coppia.
- Simulare sequenze complete e verificare interazione con controller.

### FASE/COMMIT 7: Test di integrazione

**Priorità**: 🔴 CRITICA  
**File**: `tests/integration/test_game_loop_tasti.py` (nuovo)

- Script che simula una partita con estrazioni fittizie e pressione di tasti
  rapidi per selezionare cartelle, navigare, segnare numeri, dichiarare vittoria,
  uscire.
- Usare fixture `mock_partita` o simile.

### FASE/COMMIT 8: Pulizia e refactor finale

**Priorità**: 🟡 MEDIA  
**File**: vari

- Rimuovere codice inutilizzato (`comandi_partita.py` se non serve più).
- Aggiornare README.md con le istruzioni tasti rapidi.
- Aggiornare documentations/4 - todo file con checklist commit.

---

## ✅ Criteri di Completamento

- Tutte le funzionalità elencate nei requisiti funzionano con tasti rapidi.
- Tutti i test unitari e di integrazione passano con copertura ≥ 85% sui moduli
  interessati.
- Non rimangono comandi testuali attivi nel codice.
- Documenti aggiornati: README.md, CHANGELOG.md (entry `Unreleased - Added`),
  TODO v0.10.0.
- Il branch è pronto per la review e merge su `main` con merge commit.

---

*Fine del piano.*
