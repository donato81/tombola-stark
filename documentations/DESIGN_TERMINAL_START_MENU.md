# 🎨 Design Document - Menu Iniziale TUI e Integrazione Localizzazione

> **FASE: CONCEPT & FLOW DESIGN**
> Nessuna decisione tecnica qui - solo logica e flussi concettuali
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-19
- **Stato**: DRAFT
- **Versione Target**: v0.7.0 (ipotesi)
- **Autore**: AI Assistant + Nemex81
- **File Target**: `documentations/DESIGN_TERMINAL_START_MENU.md`

---

## 💡 L'Idea in 3 Righe

Vogliamo che l'utente possa avviare Tombola Stark da terminale tramite un flusso di configurazione sequenziale e accessibile: inserisce nome, numero di bot (1-7) e numero di cartelle, poi la partita parte. Ogni testo mostrato all'utente proviene **esclusivamente** dai dizionari di localizzazione definiti in `bingo_game/ui/locales/it.py`, senza stringhe hardcoded nel modulo `ui_terminale.py`. La Fase 1 copre il menu iniziale pre-partita: dalla schermata di benvenuto fino alla chiamata di configurazione del GameController.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Utente (Giocatore Umano)**: Inserisce nome, sceglie numero bot e cartelle da tastiera; usa screen reader
- **ui_terminale.py**: Modulo Interface layer — raccoglie input, valida, presenta output su terminale
- **GameController**: Application layer — riceve la configurazione e avvia la partita
- **TerminalRenderer**: Trasforma i dati strutturati (`EsitoAzione`, eventi) in righe di testo per il terminale
- **it.py (Localizzazione)**: Fonte esclusiva di tutte le stringhe mostrate all'utente

### Concetti Chiave (Cosa Esiste nel Sistema)

#### Configurazione di Avvio
- **Cos'è**: L'insieme delle scelte iniziali dell'utente prima che la partita inizi
- **Stati possibili**: Incompleta, Completa
- **Proprietà**: `nome` (str), `numero_bot` (int 1..7), `numero_cartelle` (int ≥ 1)

#### Chiave di Localizzazione
- **Cos'è**: Identificatore unico in un dizionario di `it.py` che mappa verso una o più righe di testo italiano
- **Stati possibili**: Presente nel catalogo, Assente (fallback di sistema)
- **Proprietà**: Stringa costante (es. `"CONFIG_BENVENUTO"`), valore è sempre una `tuple[str, ...]` immutabile

#### Prompt di Input
- **Cos'è**: Riga di testo mostrata all'utente che lo invita a digitare un valore
- **Stati possibili**: In attesa, Ricevuto, Errore di validazione
- **Proprietà**: Testo proveniente da `it.py`, valore digitato dall'utente, flag di validità

#### Messaggio di Errore di Configurazione
- **Cos'è**: Una o più righe di testo che spiegano perché un input non è accettabile
- **Stati possibili**: Mostrato, Non mostrato
- **Proprietà**: Testo da `MESSAGGI_CONFIGURAZIONE` (nuovo) o da `MESSAGGI_ERRORI` (riuso dove possibile)

### Relazioni Concettuali

```
Utente
  ↓ digita
Prompt di Input
  ↓ legge testo da
Chiave di Localizzazione (it.py → MESSAGGI_CONFIGURAZIONE)
  ↓ valore validato confluisce in
Configurazione di Avvio
  ↓ passata a
GameController
  ↓ avvia
Partita
```

---

## 🎬 Scenari & Flussi

### Scenario 1: Configurazione Completa con Successo

**Punto di partenza**: Utente esegue `python main.py`, terminale vuoto

**Flusso**:

1. **Sistema**: Mostra benvenuto dal catalogo (`CONFIG_BENVENUTO`)
   → **Output**: `"Benvenuto in Tombola Stark!"`

2. **Sistema**: Mostra prompt nome (`CONFIG_RICHIESTA_NOME`)
   → **Output**: `"Inserisci il tuo nome: "`

3. **Utente**: Digita `"Marco"` e preme INVIO
   → **Sistema**: Valida (non vuoto, lunghezza accettabile)
   → Memorizza `nome = "Marco"`

4. **Sistema**: Mostra prompt bot (`CONFIG_RICHIESTA_BOT`)
   → **Output**: `"Inserisci il numero di bot (1-7): "`

5. **Utente**: Digita `"3"` e preme INVIO
   → **Sistema**: Valida (intero, in range 1..7)
   → Memorizza `numero_bot = 3`

6. **Sistema**: Mostra prompt cartelle (`CONFIG_RICHIESTA_CARTELLE`)
   → **Output**: `"Inserisci il numero di cartelle per giocatore: "`

7. **Utente**: Digita `"2"` e preme INVIO
   → **Sistema**: Valida (intero, ≥ 1)
   → Memorizza `numero_cartelle = 2`

8. **Sistema**: Mostra conferma (`CONFIG_CONFERMA_AVVIO`)
   → **Output**: `"Configurazione completata. Avvio partita..."`
   → Chiama `game_controller.configura(nome, numero_bot, numero_cartelle)`

**Punto di arrivo**: GameController configurato, partita in corso

**Cosa cambia**: `ui_terminale.py` ha la configurazione completa; il flusso passa alla Fase 2 (gioco)

---

### Scenario 2: Input Bot di Tipo Non Valido (Non Intero)

**Punto di partenza**: Nome già acquisito, sistema in stato ATTESA_BOT

**Flusso**:

1. **Sistema**: Mostra `"Inserisci il numero di bot (1-7): "`

2. **Utente**: Digita `"tre"` e preme INVIO
   → **Sistema**: Tentativo di conversione `int("tre")` fallisce
   → Mostra errore da `MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]` (già esistente in it.py)
   → **Output**: `"Errore: Tipo non valido."` / `"Inserisci un numero intero."`

3. **Sistema**: Ripropone lo stesso prompt bot senza avanzare di stato
   → **Output**: `"Inserisci il numero di bot (1-7): "`

4. **Utente**: Digita `"4"` → sistema valida con successo, avanza a ATTESA_CARTELLE

**Punto di arrivo**: Configurazione continua normalmente dopo la correzione

**Cosa cambia**: Nessun avanzamento di stato; lo stesso prompt viene riproposto

---

### Scenario 3: Input Bot Fuori Range (Intero ma Non nel Range 1-7)

**Punto di partenza**: Sistema in stato ATTESA_BOT

**Flusso**:

1. **Utente**: Digita `"10"` e preme INVIO
   → **Sistema**: Intero valido, ma non nel range 1..7
   → Mostra errore da `CONFIG_ERRORE_BOT_RANGE` (da MESSAGGI_CONFIGURAZIONE)
   → **Output**: `"Errore: Numero bot non valido."` / `"Inserisci un valore tra 1 e 7."`

2. **Sistema**: Ripropone il prompt bot

**Punto di arrivo**: Stesso stato ATTESA_BOT, prompt riproposto

---

### Scenario 4: Nome Vuoto (INVIO senza Testo)

**Cosa succede se**: Utente preme INVIO senza digitare alcun carattere

**Sistema dovrebbe**:
- Mostrare `CONFIG_ERRORE_NOME_VUOTO`
- **Output**: `"Errore: Nome non valido."` / `"Inserisci almeno un carattere."`
- Riproporre il prompt del nome senza avanzare di stato

---

### Scenario 5: Numero Cartelle Non Valido

**Cosa succede se**: Utente inserisce `"0"` o un valore negativo come numero di cartelle

**Sistema dovrebbe**:
- Se non intero: usare `MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]`
- Se intero ≤ 0: usare `CONFIG_ERRORE_CARTELLE_RANGE`
- **Output**: `"Errore: Numero cartelle non valido."` / `"Inserisci un valore maggiore di 0."`
- Riproporre il prompt cartelle

---

## 🔀 Stati e Transizioni

### Stati del Sistema (Flusso di Configurazione)

#### Stato A: BENVENUTO
- **Descrizione**: Applicazione appena avviata; viene mostrato il messaggio di benvenuto
- **Può passare a**: ATTESA_NOME
- **Trigger**: Avvio automatico al lancio dell'applicazione

#### Stato B: ATTESA_NOME
- **Descrizione**: Sistema attende inserimento del nome giocatore
- **Può passare a**: ATTESA_BOT (nome valido), ATTESA_NOME (nome non valido → loop)
- **Trigger**: Input utente + validazione stringa non vuota

#### Stato C: ATTESA_BOT
- **Descrizione**: Nome acquisito; sistema attende il numero di bot (1-7)
- **Può passare a**: ATTESA_CARTELLE (bot valido), ATTESA_BOT (bot non valido → loop)
- **Trigger**: Input utente + validazione intero in range 1..7

#### Stato D: ATTESA_CARTELLE
- **Descrizione**: Nome e bot acquisiti; sistema attende il numero di cartelle per giocatore
- **Può passare a**: AVVIO_PARTITA (cartelle valide), ATTESA_CARTELLE (cartelle non valide → loop)
- **Trigger**: Input utente + validazione intero ≥ 1

#### Stato E: AVVIO_PARTITA
- **Descrizione**: Tutti i dati validati; configurazione passata al GameController; conferma mostrata
- **Può passare a**: Fase di gioco (Fase 2 — fuori scope di questo design)
- **Trigger**: Chiamata a `game_controller.configura(nome, numero_bot, numero_cartelle)`

### Diagramma Stati (ASCII)

```
[AVVIO APPLICAZIONE]
        ↓
  [BENVENUTO]  ← stampa CONFIG_BENVENUTO
        ↓
 [ATTESA_NOME]  ←──────────────────────────────────┐
        ↓ (nome valido)                             │
        │                                           │ (nome non valido)
        │                    CONFIG_ERRORE_NOME_VUOTO ──┘
        ↓
 [ATTESA_BOT]  ←──────────────────────────────────┐
        ↓ (bot valido, 1..7)                        │
        │                                           │ (non intero)
        │                    MESSAGGI_ERRORI[NUMERO_TIPO_NON_VALIDO] ─┐
        │                                           │ (fuori range)   │
        │                    CONFIG_ERRORE_BOT_RANGE ─────────────────┘
        ↓
[ATTESA_CARTELLE]  ←───────────────────────────────┐
        ↓ (cartelle valide, ≥ 1)                    │
        │                                           │ (non intero)
        │                    MESSAGGI_ERRORI[NUMERO_TIPO_NON_VALIDO] ─┐
        │                                           │ (≤ 0)          │
        │                    CONFIG_ERRORE_CARTELLE_RANGE ────────────┘
        ↓
 [AVVIO_PARTITA]  ← stampa CONFIG_CONFERMA_AVVIO
        ↓
   [FASE DI GIOCO → Fase 2]
```

---

## 🎮 Interazione Utente (UX Concettuale)

### Principio di Accessibilità

L'intera Fase 1 usa **esclusivamente `input()` standard di Python** — nessuna libreria con interfacce curses o ncurses. L'output è lineare: una riga per ogni messaggio, un campo di input per volta. Questo garantisce piena compatibilità con screen reader (NVDA, JAWS, Orca) su qualsiasi piattaforma.

Regole di output:
- I messaggi di errore vengono stampati **prima** di riproporre il prompt (lo screen reader li legge in ordine corretto)
- Nessuna decorazione grafica (no box ASCII, no colori ANSI, no caratteri speciali non parlabili)
- Ogni riga della tupla in it.py viene stampata come riga separata (newline tra le righe)

### Comandi/Azioni Disponibili

- **INVIO dopo nome**:
  - Fa cosa? Conferma il nome digitato e tenta la validazione
  - Quando disponibile? Stato ATTESA_NOME
  - Feedback atteso: avanza a prompt bot (ok) oppure messaggio errore + riproposta prompt (ko)

- **INVIO dopo numero bot**:
  - Fa cosa? Conferma il numero di bot e tenta la validazione
  - Quando disponibile? Stato ATTESA_BOT
  - Feedback atteso: avanza a prompt cartelle (ok) oppure messaggio errore + riproposta prompt (ko)

- **INVIO dopo numero cartelle**:
  - Fa cosa? Conferma il numero di cartelle e tenta la validazione
  - Quando disponibile? Stato ATTESA_CARTELLE
  - Feedback atteso: avanza ad avvio partita (ok) oppure messaggio errore + riproposta prompt (ko)

### Feedback Sistema

- **Avvio**: `CONFIG_BENVENUTO` → stampa a schermo
- **Prompt nome**: `CONFIG_RICHIESTA_NOME` → usato come argomento di `input()`
- **Errore nome vuoto**: `CONFIG_ERRORE_NOME_VUOTO` → stampa multi-riga
- **Prompt bot**: `CONFIG_RICHIESTA_BOT` → usato come argomento di `input()`
- **Errore bot tipo**: `MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]` → stampa multi-riga
- **Errore bot range**: `CONFIG_ERRORE_BOT_RANGE` → stampa multi-riga
- **Prompt cartelle**: `CONFIG_RICHIESTA_CARTELLE` → usato come argomento di `input()`
- **Errore cartelle tipo**: `MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]` → stampa multi-riga
- **Errore cartelle range**: `CONFIG_ERRORE_CARTELLE_RANGE` → stampa multi-riga
- **Conferma avvio**: `CONFIG_CONFERMA_AVVIO` → stampa a schermo

### Navigazione Concettuale (Flusso Completo)

1. `python main.py` → sistema stampa benvenuto
2. Sistema mostra prompt nome → utente digita e preme INVIO
3. Errore? → messaggio + stesso prompt riproposto (torna al punto 2)
4. Ok → sistema mostra prompt bot → utente digita e preme INVIO
5. Errore? → messaggio + stesso prompt riproposto (torna al punto 4)
6. Ok → sistema mostra prompt cartelle → utente digita e preme INVIO
7. Errore? → messaggio + stesso prompt riproposto (torna al punto 6)
8. Ok → sistema stampa conferma, chiama GameController, la partita inizia (Fase 2)

---

## 🔗 Integrazione ui_terminale.py con bingo_game/ui/locales/it.py

### Principio Fondamentale

Il modulo `bingo_game/ui/ui_terminale.py` **non contiene nessuna stringa hardcoded**. Ogni testo visibile all'utente proviene esclusivamente dai dizionari di `bingo_game/ui/locales/it.py`. Questo vale per: messaggi di benvenuto, prompt di input, messaggi di conferma e messaggi di errore.

### Nuovo Dizionario MESSAGGI_CONFIGURAZIONE da Aggiungere a it.py

Per supportare la Fase 1, `it.py` dovrà essere esteso con un nuovo dizionario immutabile `MESSAGGI_CONFIGURAZIONE`. Deve seguire lo stesso pattern degli altri dizionari del file: `MappingProxyType`, chiavi stringa costanti, valori come `tuple[str, ...]`.

**Chiavi proposte**:

| Chiave | Testo Atteso | Note |
|---|---|---|
| `CONFIG_BENVENUTO` | `("Benvenuto in Tombola Stark!",)` | Riga singola, no placeholder |
| `CONFIG_RICHIESTA_NOME` | `("Inserisci il tuo nome: ",)` | Usata come prompt di `input()` |
| `CONFIG_RICHIESTA_BOT` | `("Inserisci il numero di bot (1-7): ",)` | Usata come prompt di `input()` |
| `CONFIG_RICHIESTA_CARTELLE` | `("Inserisci il numero di cartelle per giocatore: ",)` | Usata come prompt di `input()` |
| `CONFIG_CONFERMA_AVVIO` | `("Configurazione completata. Avvio partita...",)` | Mostra prima di avviare il GameController |
| `CONFIG_ERRORE_NOME_VUOTO` | `("Errore: Nome non valido.", "Inserisci almeno un carattere.",)` | 2 righe, no placeholder |
| `CONFIG_ERRORE_BOT_RANGE` | `("Errore: Numero bot non valido.", "Inserisci un valore tra 1 e 7.",)` | 2 righe, no placeholder |
| `CONFIG_ERRORE_CARTELLE_RANGE` | `("Errore: Numero cartelle non valido.", "Inserisci un valore maggiore di 0.",)` | 2 righe, no placeholder |

### Riuso dei Messaggi di Errore Già Esistenti

Gli errori di **tipo** (input non convertibile in `int`) usano le chiavi già presenti in `MESSAGGI_ERRORI`:
- `MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]` → `"Errore: Tipo non valido." / "Inserisci un numero intero."`

Questo evita duplicazioni nel catalogo e mantiene coerenza tra la fase di configurazione e la fase di gioco.

### Meccanismo di Accesso in ui_terminale.py (Pseudo-Codice Concettuale)

```python
# Importazioni (solo dal livello locales/renderers — non dal dominio)
from bingo_game.ui.locales.it import (
    MESSAGGI_CONFIGURAZIONE,
    MESSAGGI_ERRORI,
)

def _stampa_righe(righe: tuple[str, ...]) -> None:
    """Stampa ogni riga del catalogo su una linea separata."""
    for riga in righe:
        print(riga)

def _chiedi_input(chiave_prompt: str) -> str:
    """Usa la prima riga del catalogo come prompt per input()."""
    testo_prompt = MESSAGGI_CONFIGURAZIONE[chiave_prompt][0]
    return input(testo_prompt)
```

### Uso del TerminalRenderer nella Fase 1

Nella Fase 1 (start menu), `ui_terminale.py` **non usa** `TerminalRenderer.render_esito()` per i prompt di configurazione, poiché questi non sono `EsitoAzione` prodotti dal dominio. Il `TerminalRenderer` viene **istanziato** durante la fase di configurazione e tenuto pronto come attributo dell'oggetto TUI per la fase di gioco (Fase 2+). I messaggi di configurazione vengono stampati direttamente via `print()` usando le stringhe dai cataloghi di `it.py`.

```
Fase 1 (start menu):
  ui_terminale.py → MESSAGGI_CONFIGURAZIONE (it.py) → print() → terminale

Fase 2+ (in gioco):
  ui_terminale.py → GameController → EsitoAzione → TerminalRenderer.render_esito() → print() → terminale
```

---

## 🤔 Domande & Decisioni

### Domande Aperte

- [ ] Qual è il range valido per il numero di cartelle? (min 1, max? — da verificare con API.md/GameController)
- [ ] Il nome del giocatore ha una lunghezza massima? (anti-verbosità per screen reader)
- [ ] Il nome viene sanitizzato (`.strip()`) o passato as-is al GameController?
- [ ] Il messaggio `CONFIG_RICHIESTA_BOT` deve includere il range `(1-7)` nel testo o solo nel messaggio di errore?
- [ ] `main.py` istanzia direttamente `ui_terminale.py` oppure passa per un'altra entry point?

### Decisioni Prese

- ✅ **Nessuna stringa hardcoded in ui_terminale.py**: Tutto da `it.py` per coerenza con il progetto
- ✅ **Input sequenziale con `input()` standard**: No librerie esterne, massima compatibilità screen reader
- ✅ **Loop su errore**: In caso di input non valido si ripropone lo stesso prompt (no skip, no skip silenzioso)
- ✅ **Errori stampati PRIMA del prompt riproposto**: Coerente con l'ordine di lettura degli screen reader
- ✅ **TerminalRenderer non usato per i prompt di configurazione**: Solo per EsitoAzione di gioco
- ✅ **Nuovo dizionario MESSAGGI_CONFIGURAZIONE**: Separazione semantica dai messaggi di gioco
- ✅ **Riuso MESSAGGI_ERRORI per errori di tipo**: Nessuna duplicazione nel catalogo

### Assunzioni

- `game_controller.py` espone un metodo per ricevere la configurazione iniziale (nome, bot, cartelle)
- `main.py` è il punto di ingresso che istanzia e avvia la TUI
- Il terminale è configurato per UTF-8 (caratteri italiani supportati)
- L'utente usa uno screen reader compatibile con output testuale lineare (NVDA/JAWS/Orca)
- Il progetto non usa stdin/stdout reindirizzati (input interattivo reale)

---

## 🎯 Opzioni Considerate

### Opzione A: Input Diretto con `input()` Standard di Python

**Descrizione**: Ogni prompt usa la funzione `input(testo_da_catalogo)` di Python. Output lineare, un prompt per volta, zero dipendenze aggiuntive.

**Pro**:
- ✅ Compatibilità totale con screen reader (output lineare, no interferenze curses)
- ✅ Nessuna dipendenza esterna da aggiungere a `requirements.txt`
- ✅ Semplicissimo da testare (mock di `input()` e `print()`)
- ✅ Coerente con la filosofia "screen reader first" del progetto

**Contro**:
- ❌ Nessun completamento automatico o navigazione con frecce nell'input
- ❌ Meno "moderna" rispetto a librerie TUI avanzate

---

### Opzione B: Libreria prompt_toolkit

**Descrizione**: Usa `prompt_toolkit` per input interattivo con validazione inline, history e completamento automatico.

**Pro**:
- ✅ Esperienza utente più ricca (history, completamento, colori)
- ✅ Validazione in tempo reale mentre l'utente digita

**Contro**:
- ❌ Incompatibile con molti screen reader (gestione del terminale a basso livello interferisce con AT)
- ❌ Dipendenza esterna aggiuntiva
- ❌ Contro la filosofia di accessibilità consolidata del progetto
- ❌ Overkill per un flusso di 3 input sequenziali

---

### Scelta Finale

Scelta **Opzione A: `input()` standard** perché:
- Il progetto ha una filosofia "screen reader first" consolidata e documentata
- La Fase 1 è un flusso lineare semplice: non servono funzionalità avanzate
- Zero dipendenze aggiuntive = zero rischi di regressione
- Coerente con l'approccio già usato da `TerminalRenderer` per la fase di gioco

---

## ✅ Design Freeze Checklist

Questo design è pronto per la fase tecnica (PLAN) quando:

- [x] Tutti gli scenari principali mappati (ok + tutti i casi di errore)
- [x] Stati del sistema chiari e completi (5 stati ben definiti)
- [x] Flussi logici coprono tutti i casi d'uso rilevanti
- [ ] Domande aperte risolte (range cartelle, lunghezza max nome, sanitizzazione input)
- [x] UX interaction definita (input() lineare, prompt da catalogo, errori prima del re-prompt)
- [x] Opzioni valutate e scelta finale motivata
- [x] Integrazione localizzazione documentata (nuovo MESSAGGI_CONFIGURAZIONE specificato)
- [x] Nessun "buco logico" evidente nel flusso di validazione

**Next Step**: Creare `PLAN_TERMINAL_START_MENU.md` con:
- Firma esatta del metodo di configurazione in GameController (da `documentations/API.md`)
- Struttura classe/funzione di `ui_terminale.py` (con tipi, parametri, return type)
- Import e dipendenze esatte
- Testing strategy per i loop di validazione e il mocking di `input()`/`print()`

---

## 📝 Note di Brainstorming

- Fase 2 del TUI: navigazione in-game con tastiera — già parzialmente coperta da `TerminalRenderer`
- I bot in `bingo_game/players/` hanno probabilmente già un'implementazione: il range 1-7 deve essere verificato con il GameController prima del PLAN
- Possibile estensione futura: `CONFIG_RICHIESTA_CARTELLE` potrebbe includere un hint con il range valido nel testo del prompt
- Accessibilità: verificare che i messaggi di errore vengano sempre stampati **prima** di riproporre il prompt (screen reader li legge in ordine)
- Il pattern `MappingProxyType` con `tuple[str, ...]` per i valori è mandatorio in `MESSAGGI_CONFIGURAZIONE` — coerenza con tutti gli altri dizionari di `it.py`
- Potenziale: `_stampa_righe()` potrebbe diventare un helper condiviso nel modulo `ui_terminale.py`
- Considerare se `ui_terminale.py` deve essere una classe (`TerminalUI`) o un modulo con funzioni; la classe facilita il testing per dipendency injection di `input`/`print`

---

## 📚 Riferimenti Contestuali

### File del Repository Analizzati

- `bingo_game/ui/locales/it.py` — Catalogo stringhe italiano; contiene `MESSAGGI_ERRORI`, `MESSAGGI_EVENTI`, `MESSAGGI_OUTPUT_UI_UMANI`, `MESSAGGI_SISTEMA`; va esteso con `MESSAGGI_CONFIGURAZIONE`
- `bingo_game/ui/renderers/renderer_terminal.py` — Classe `TerminalRenderer` con `render_esito()` orchestratore; usato nella Fase 2
- `bingo_game/ui/ui_terminale.py` — Modulo TUI da progettare e implementare (attualmente vuoto)
- `bingo_game/game_controller.py` — Controller da consumare; contratto formale in `documentations/API.md`
- `documentations/ARCHITECTURE.md` — Vincoli layer architetturali (Interface → Controller, mai Domain direttamente)
- `documentations/API.md` — Contratti API del GameController

### Feature Correlate

- **DESIGN_BOT_ATTIVO.md**: Configurazione dei bot — la scelta del numero di bot (1-7) si interfaccia con questa feature; range da verificare
- **DESIGN_LOGGING_SYSTEM.md**: Il sistema di logging è già attivo — il lancio dell'applicazione e la configurazione potrebbero generare log di avvio

### Vincoli da Rispettare (da ARCHITECTURE.md)

- Il livello Interface (`ui_terminale.py`) consuma **solo** il Controller (`game_controller.py`), mai il Domain direttamente
- Tutte le stringhe visibili all'utente devono provenire da `it.py` (`MappingProxyType`, tuple di righe)
- Output esclusivamente lineare e testuale: nessuna decorazione grafica (no box ASCII, no colori ANSI, no Unicode decorativo)
- Coerenza con il pattern `TerminalRenderer`: catalogo → accesso per chiave → output testo pulito

---

## 🎯 Risultato Finale Atteso (High-Level)

Una volta implementata la Fase 1, l'utente potrà:

✅ Avviare Tombola Stark da terminale e ricevere un messaggio di benvenuto chiaro e accessibile
✅ Inserire il proprio nome in modo guidato con un prompt testuale proveniente dal catalogo
✅ Scegliere il numero di bot (1-7) con validazione completa e messaggi d'errore accessibili
✅ Scegliere il numero di cartelle per giocatore con validazione e feedback d'errore
✅ Ricevere una conferma di avvio partita prima che la fase di gioco inizi
✅ Ottenere feedback immediato e correttivo per ogni input non valido senza uscire dall'applicazione
✅ Fruire dell'intera esperienza di configurazione tramite screen reader senza barriere

---

**Fine Design Document**

---

*Salvato in: `documentations/DESIGN_TERMINAL_START_MENU.md`*
*Segue il template: `documentations/templates/TEMPLATE_example_DESIGN_DOCUMENT.md`*
