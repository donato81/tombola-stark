# 🎨 Design Document - Menu Iniziale TUI e Integrazione Localizzazione

> **FASE: CONCEPT & FLOW DESIGN**
> Nessuna decisione tecnica qui - solo logica e flussi concettuali
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-19
- **Ultimo Aggiornamento**: 2026-02-19
- **Versione Documento**: v1.1
- **Stato**: READY
- **Versione Target**: v0.7.0
- **Autore**: AI Assistant + Nemex81
- **File Target**: `documentations/DESIGN_TERMINAL_START_MENU.md`

---

## 💡 L'Idea in 3 Righe

Vogliamo che l'utente possa avviare Tombola Stark da terminale tramite un flusso di configurazione sequenziale e accessibile: inserisce nome (max 15 caratteri), numero di bot (1-7) e numero di cartelle (1-6), poi la partita parte. Ogni testo mostrato all'utente proviene **esclusivamente** dai dizionari di localizzazione definiti in `bingo_game/ui/locales/it.py`, senza stringhe hardcoded nel modulo `ui_terminale.py`. La Fase 1 copre il menu iniziale pre-partita: dalla schermata di benvenuto fino alla chiamata a `crea_partita_standard()` + `avvia_partita_sicura()` del GameController.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Utente (Giocatore Umano)**: Inserisce nome, sceglie numero bot e cartelle da tastiera; usa screen reader
- **ui_terminale.py**: Modulo Interface layer — raccoglie input, valida, presenta output su terminale
- **GameController**: Application layer — riceve la configurazione tramite `crea_partita_standard()` e avvia la partita con `avvia_partita_sicura()`
- **TerminalRenderer**: Trasforma i dati strutturati (`EsitoAzione`, eventi) in righe di testo per il terminale
- **it.py (Localizzazione)**: Fonte esclusiva di tutte le stringhe mostrate all'utente

### Concetti Chiave (Cosa Esiste nel Sistema)

#### Configurazione di Avvio
- **Cos'è**: L'insieme delle scelte iniziali dell'utente prima che la partita inizi
- **Stati possibili**: Incompleta, Completa
- **Proprietà**: `nome` (str, max 15 caratteri, già `.strip()`pato), `numero_bot` (int 1..7), `numero_cartelle` (int 1..6)

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
GameController.crea_partita_standard()
  ↓ avviata con
GameController.avvia_partita_sicura()
  ↓ produce
Partita in stato "in_corso"
```

---

## 🎬 Scenari & Flussi

### Scenario 1: Configurazione Completa con Successo

**Punto di partenza**: Utente esegue `python main.py`, terminale vuoto

**Flusso**:

1. **Sistema**: Mostra benvenuto dal catalogo (`CONFIG_BENVENUTO`)
   → **Output**: `"Benvenuto in Tombola Stark!"`

2. **Sistema**: Mostra prompt nome (`CONFIG_RICHIESTA_NOME`)
   → **Output**: `"Inserisci il tuo nome (max 15 caratteri): "`

3. **Utente**: Digita `"Marco"` e preme INVIO
   → **Sistema**: Applica `.strip()`, controlla non vuoto e lunghezza ≤ 15
   → Memorizza `nome = "Marco"`

4. **Sistema**: Mostra prompt bot (`CONFIG_RICHIESTA_BOT`)
   → **Output**: `"Inserisci il numero di bot (1-7): "`

5. **Utente**: Digita `"3"` e preme INVIO
   → **Sistema**: Valida (intero, in range 1..7)
   → Memorizza `numero_bot = 3`

6. **Sistema**: Mostra prompt cartelle (`CONFIG_RICHIESTA_CARTELLE`)
   → **Output**: `"Inserisci il numero di cartelle (1-6): "`

7. **Utente**: Digita `"2"` e preme INVIO
   → **Sistema**: Valida (intero, in range 1..6)
   → Memorizza `numero_cartelle = 2`

8. **Sistema**: Mostra conferma (`CONFIG_CONFERMA_AVVIO`)
   → **Output**: `"Configurazione completata. Avvio partita..."`
   → Chiama `crea_partita_standard(nome_giocatore_umano="Marco", num_cartelle_umano=2, num_bot=3)`
   → Chiama `avvia_partita_sicura(partita)`

**Punto di arrivo**: `Partita` in stato `"in_corso"`, flusso passa alla Fase 2

**Cosa cambia**: `ui_terminale.py` ha l'oggetto `partita` pronto per la fase di gioco

---

### Scenario 2: Input Bot di Tipo Non Valido (Non Intero)

**Punto di partenza**: Nome già acquisito, sistema in stato ATTESA_BOT

**Flusso**:

1. **Sistema**: Mostra `"Inserisci il numero di bot (1-7): "`

2. **Utente**: Digita `"tre"` e preme INVIO
   → **Sistema**: Tentativo di conversione `int("tre")` fallisce (`ValueError`)
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

### Scenario 4: Nome Non Valido

**Caso A — Nome vuoto**: Utente preme INVIO senza digitare alcun carattere (o solo spazi)

**Sistema dovrebbe**:
- Applicare `.strip()` → stringa risultante è `""`
- Mostrare `CONFIG_ERRORE_NOME_VUOTO`
- **Output**: `"Errore: Nome non valido."` / `"Inserisci almeno un carattere."`
- Riproporre il prompt del nome senza avanzare di stato

**Caso B — Nome troppo lungo**: Utente digita più di 15 caratteri

**Sistema dovrebbe**:
- Applicare `.strip()` → stringa non vuota ma `len(nome) > 15`
- Mostrare `CONFIG_ERRORE_NOME_TROPPO_LUNGO`
- **Output**: `"Errore: Nome troppo lungo."` / `"Inserisci al massimo 15 caratteri."`
- Riproporre il prompt del nome senza avanzare di stato

---

### Scenario 5: Numero Cartelle Non Valido

**Cosa succede se**: Utente inserisce un valore fuori range per le cartelle

**Sistema dovrebbe**:
- Se non intero: usare `MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]`
- Se intero fuori range 1..6: usare `CONFIG_ERRORE_CARTELLE_RANGE`
- **Output**: `"Errore: Numero cartelle non valido."` / `"Inserisci un valore tra 1 e 6."`
- Riproporre il prompt cartelle

> **Nota**: Il limite massimo di 6 cartelle è una scelta UX (anti-verbosità per screen reader), non un vincolo del Controller. Il GameController accetta qualsiasi valore `num_cartelle > 0`; la validazione avviene interamente a livello UI prima della chiamata API.

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
- **Trigger**: Input utente + validazione:
  1. `.strip()` applicato sempre
  2. Stringa risultante non vuota (`CONFIG_ERRORE_NOME_VUOTO` se fallisce)
  3. Lunghezza ≤ 15 caratteri (`CONFIG_ERRORE_NOME_TROPPO_LUNGO` se fallisce)

#### Stato C: ATTESA_BOT
- **Descrizione**: Nome acquisito; sistema attende il numero di bot (1-7)
- **Può passare a**: ATTESA_CARTELLE (bot valido), ATTESA_BOT (bot non valido → loop)
- **Trigger**: Input utente + validazione:
  1. Convertibile in `int` (`MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]` se fallisce)
  2. Valore in range 1..7 (`CONFIG_ERRORE_BOT_RANGE` se fallisce)

#### Stato D: ATTESA_CARTELLE
- **Descrizione**: Nome e bot acquisiti; sistema attende il numero di cartelle (1-6)
- **Può passare a**: AVVIO_PARTITA (cartelle valide), ATTESA_CARTELLE (cartelle non valide → loop)
- **Trigger**: Input utente + validazione:
  1. Convertibile in `int` (`MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]` se fallisce)
  2. Valore in range 1..6 (`CONFIG_ERRORE_CARTELLE_RANGE` se fallisce)

#### Stato E: AVVIO_PARTITA
- **Descrizione**: Tutti i dati validati; configurazione passata al GameController; conferma mostrata
- **Può passare a**: Fase di gioco (Fase 2 — fuori scope di questo design)
- **Trigger**:
  1. `partita = crea_partita_standard(nome_giocatore_umano=nome, num_cartelle_umano=numero_cartelle, num_bot=numero_bot)`
  2. `avvia_partita_sicura(partita)` → ritorna `True` se avvio riuscito

### Diagramma Stati (ASCII)

```
[AVVIO APPLICAZIONE]
        ↓
  [BENVENUTO]  ← stampa CONFIG_BENVENUTO
        ↓
 [ATTESA_NOME]  ←──────────────────────────────────────────────┐
        ↓ (nome valido: strip ok, non vuoto, len ≤ 15)         │
        │                                                       │ (stringa vuota dopo strip)
        │                       CONFIG_ERRORE_NOME_VUOTO ───────┤
        │                                                       │ (lunghezza > 15 caratteri)
        │                       CONFIG_ERRORE_NOME_TROPPO_LUNGO ┘
        ↓
 [ATTESA_BOT]  ←──────────────────────────────────────────────┐
        ↓ (bot valido: intero in 1..7)                         │
        │                                                       │ (non intero)
        │                       MESSAGGI_ERRORI[NUMERO_TIPO_NON_VALIDO] ─┐
        │                                                       │ (fuori 1..7)│
        │                       CONFIG_ERRORE_BOT_RANGE ────────┘────────────┘
        ↓
[ATTESA_CARTELLE]  ←───────────────────────────────────────────┐
        ↓ (cartelle valide: intero in 1..6)                    │
        │                                                       │ (non intero)
        │                       MESSAGGI_ERRORI[NUMERO_TIPO_NON_VALIDO] ─┐
        │                                                       │ (fuori 1..6)│
        │                       CONFIG_ERRORE_CARTELLE_RANGE ───┘────────────┘
        ↓
 [AVVIO_PARTITA]  ← stampa CONFIG_CONFERMA_AVVIO
        ↓ crea_partita_standard() + avvia_partita_sicura()
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
- Il prompt di `input()` usa sempre la **prima riga** della tupla del catalogo come argomento diretto

### Comandi/Azioni Disponibili

- **INVIO dopo nome**:
  - Fa cosa? Applica `.strip()` e tenta la validazione (non vuoto, lunghezza ≤ 15)
  - Quando disponibile? Stato ATTESA_NOME
  - Feedback atteso: avanza a prompt bot (ok) oppure messaggio errore + riproposta prompt (ko)

- **INVIO dopo numero bot**:
  - Fa cosa? Tenta conversione `int()` e valida il range 1..7
  - Quando disponibile? Stato ATTESA_BOT
  - Feedback atteso: avanza a prompt cartelle (ok) oppure messaggio errore + riproposta prompt (ko)

- **INVIO dopo numero cartelle**:
  - Fa cosa? Tenta conversione `int()` e valida il range 1..6
  - Quando disponibile? Stato ATTESA_CARTELLE
  - Feedback atteso: avanza ad avvio partita (ok) oppure messaggio errore + riproposta prompt (ko)

### Feedback Sistema

| Evento | Chiave Catalogo | Dizionario | Note |
|---|---|---|---|
| Avvio applicazione | `CONFIG_BENVENUTO` | `MESSAGGI_CONFIGURAZIONE` | Stampa via `print()` |
| Prompt nome | `CONFIG_RICHIESTA_NOME` | `MESSAGGI_CONFIGURAZIONE` | Argomento di `input()` |
| Errore nome vuoto | `CONFIG_ERRORE_NOME_VUOTO` | `MESSAGGI_CONFIGURAZIONE` | Stampa multi-riga prima del re-prompt |
| Errore nome troppo lungo | `CONFIG_ERRORE_NOME_TROPPO_LUNGO` | `MESSAGGI_CONFIGURAZIONE` | Stampa multi-riga prima del re-prompt |
| Prompt bot | `CONFIG_RICHIESTA_BOT` | `MESSAGGI_CONFIGURAZIONE` | Argomento di `input()` |
| Errore bot tipo | `NUMERO_TIPO_NON_VALIDO` | `MESSAGGI_ERRORI` | Riuso chiave esistente |
| Errore bot range | `CONFIG_ERRORE_BOT_RANGE` | `MESSAGGI_CONFIGURAZIONE` | Stampa multi-riga prima del re-prompt |
| Prompt cartelle | `CONFIG_RICHIESTA_CARTELLE` | `MESSAGGI_CONFIGURAZIONE` | Argomento di `input()` |
| Errore cartelle tipo | `NUMERO_TIPO_NON_VALIDO` | `MESSAGGI_ERRORI` | Riuso chiave esistente |
| Errore cartelle range | `CONFIG_ERRORE_CARTELLE_RANGE` | `MESSAGGI_CONFIGURAZIONE` | Stampa multi-riga prima del re-prompt |
| Conferma avvio | `CONFIG_CONFERMA_AVVIO` | `MESSAGGI_CONFIGURAZIONE` | Stampa prima della chiamata al Controller |

### Navigazione Concettuale (Flusso Completo)

1. `python main.py` → sistema stampa benvenuto
2. Sistema mostra prompt nome → utente digita e preme INVIO
3. Errore? → messaggio + stesso prompt riproposto (torna al punto 2)
4. Ok → sistema mostra prompt bot → utente digita e preme INVIO
5. Errore? → messaggio + stesso prompt riproposto (torna al punto 4)
6. Ok → sistema mostra prompt cartelle → utente digita e preme INVIO
7. Errore? → messaggio + stesso prompt riproposto (torna al punto 6)
8. Ok → sistema stampa conferma, chiama `crea_partita_standard()` poi `avvia_partita_sicura()`, la partita inizia (Fase 2)

---

## 🔗 Integrazione ui_terminale.py con bingo_game/ui/locales/it.py

### Principio Fondamentale

Il modulo `bingo_game/ui/ui_terminale.py` **non contiene nessuna stringa hardcoded**. Ogni testo visibile all'utente proviene esclusivamente dai dizionari di `bingo_game/ui/locales/it.py`. Questo vale per: messaggi di benvenuto, prompt di input, messaggi di conferma e messaggi di errore.

### Nuovo Dizionario MESSAGGI_CONFIGURAZIONE da Aggiungere a it.py

Per supportare la Fase 1, `it.py` dovrà essere esteso con un nuovo dizionario immutabile `MESSAGGI_CONFIGURAZIONE`. Deve seguire esattamente lo stesso pattern degli altri dizionari del file: `MappingProxyType`, chiavi stringa costanti, valori come `tuple[str, ...]`.

**Chiavi richieste** (9 totali):

| Chiave | Testo Atteso | Note |
|---|---|---|
| `CONFIG_BENVENUTO` | `("Benvenuto in Tombola Stark!",)` | Riga singola, no placeholder |
| `CONFIG_RICHIESTA_NOME` | `("Inserisci il tuo nome (max 15 caratteri): ",)` | Prima riga usata come argomento di `input()` |
| `CONFIG_RICHIESTA_BOT` | `("Inserisci il numero di bot (1-7): ",)` | Prima riga usata come argomento di `input()` |
| `CONFIG_RICHIESTA_CARTELLE` | `("Inserisci il numero di cartelle (1-6): ",)` | Prima riga usata come argomento di `input()` |
| `CONFIG_CONFERMA_AVVIO` | `("Configurazione completata. Avvio partita...",)` | Stampa prima di chiamare il Controller |
| `CONFIG_ERRORE_NOME_VUOTO` | `("Errore: Nome non valido.", "Inserisci almeno un carattere.",)` | 2 righe, no placeholder |
| `CONFIG_ERRORE_NOME_TROPPO_LUNGO` | `("Errore: Nome troppo lungo.", "Inserisci al massimo 15 caratteri.",)` | 2 righe, no placeholder |
| `CONFIG_ERRORE_BOT_RANGE` | `("Errore: Numero bot non valido.", "Inserisci un valore tra 1 e 7.",)` | 2 righe, no placeholder |
| `CONFIG_ERRORE_CARTELLE_RANGE` | `("Errore: Numero cartelle non valido.", "Inserisci un valore tra 1 e 6.",)` | 2 righe, no placeholder |

### Nuovo File codici_configurazione.py Richiesto

Per mantenere la coerenza con il pattern dell'intero modulo `it.py` — che importa un tipo-chiave tipato da `bingo_game/events/` per ogni dizionario — è necessario creare:

```
bingo_game/events/codici_configurazione.py  ← DA CREARE (nuovo)
```

Questo file definisce le costanti-chiave del dizionario `MESSAGGI_CONFIGURAZIONE`, esattamente come `codici_errori.py` fa per `MESSAGGI_ERRORI`. Il tipo `Codici_Configurazione = str` verrà importato in `it.py` per annotare il nuovo dizionario.

### Riuso dei Messaggi di Errore Già Esistenti

Gli errori di **tipo** (input non convertibile in `int`) usano le chiavi già presenti in `MESSAGGI_ERRORI`:
- `MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]` → `"Errore: Tipo non valido." / "Inserisci un numero intero."`

Questo evita duplicazioni nel catalogo e mantiene coerenza semantica: lo stesso tipo di errore (input non intero) produce lo stesso messaggio sia nella fase di configurazione che nella fase di gioco.

### Meccanismo di Accesso in ui_terminale.py (Pseudo-Codice Concettuale)

```python
# Importazioni (solo dal livello locales — mai dal Domain direttamente)
from bingo_game.ui.locales.it import (
    MESSAGGI_CONFIGURAZIONE,
    MESSAGGI_ERRORI,
)
from bingo_game.game_controller import (
    crea_partita_standard,
    avvia_partita_sicura,
)

def _stampa_righe(righe: tuple[str, ...]) -> None:
    """Stampa ogni riga del catalogo su una linea separata."""
    for riga in righe:
        print(riga)

def _chiedi_input(chiave_prompt: str) -> str:
    """Usa la prima riga del catalogo come testo del prompt per input()."""
    testo_prompt = MESSAGGI_CONFIGURAZIONE[chiave_prompt][0]
    return input(testo_prompt)

# Flusso di avvio (pseudo-codice stato E):
#   partita = crea_partita_standard(
#       nome_giocatore_umano=nome,        # str, già .strip()pato e validato
#       num_cartelle_umano=numero_cartelle, # int, validato range 1..6
#       num_bot=numero_bot,               # int, validato range 1..7
#   )
#   avvia_partita_sicura(partita)         # → True se avvio riuscito
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

Tutte le domande aperte sono state risolte. Il design è in stato **READY**.

### Decisioni Prese

- ✅ **Nessuna stringa hardcoded in ui_terminale.py**: Tutto da `it.py` per coerenza con il progetto
- ✅ **Input sequenziale con `input()` standard**: No librerie esterne, massima compatibilità screen reader
- ✅ **Loop su errore**: In caso di input non valido si ripropone lo stesso prompt (no skip, no skip silenzioso)
- ✅ **Errori stampati PRIMA del prompt riproposto**: Coerente con l'ordine di lettura degli screen reader
- ✅ **TerminalRenderer non usato per i prompt di configurazione**: Solo per EsitoAzione di gioco (Fase 2+)
- ✅ **Nuovo dizionario MESSAGGI_CONFIGURAZIONE**: Separazione semantica dai messaggi di gioco; 9 chiavi totali
- ✅ **Riuso MESSAGGI_ERRORI per errori di tipo**: Nessuna duplicazione nel catalogo
- ✅ **Range cartelle: 1–6**: Limite superiore imposto dalla UI per accessibilità (anti-verbosità screen reader); il Controller non ha questo vincolo
- ✅ **Lunghezza massima nome: 15 caratteri**: Anti-verbosità per screen reader; validazione UI-side prima della chiamata al Controller
- ✅ **Sanitizzazione nome con `.strip()`**: Applicata sempre come primo passo; stringa vuota dopo strip = input non valido (`CONFIG_ERRORE_NOME_VUOTO`)
- ✅ **Metodo Controller corretto**: `crea_partita_standard(nome_giocatore_umano, num_cartelle_umano, num_bot)` + `avvia_partita_sicura(partita)` (da `documentations/API.md`)
- ✅ **Nuovo file `codici_configurazione.py`**: Richiesto per mantenere la coerenza del pattern di importazione in `it.py`

### Assunzioni

- `game_controller.py` espone `crea_partita_standard()` e `avvia_partita_sicura()` come da `documentations/API.md` (v0.6.0+)
- `main.py` è il punto di ingresso che istanzia e avvia la TUI
- Il terminale è configurato per UTF-8 (caratteri italiani supportati)
- L'utente usa uno screen reader compatibile con output testuale lineare (NVDA/JAWS/Orca)
- Il progetto non usa stdin/stdout reindirizzati (input interattivo reale)
- `GiocatoreNomeValueException` non viene mai raggiunta in produzione grazie alla pre-validazione UI-side (`.strip()` + check lunghezza), ma deve essere gestita come difesa interna nel PLAN

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

- [x] Tutti gli scenari principali mappati (ok + tutti i casi di errore, incluso nome troppo lungo)
- [x] Stati del sistema chiari e completi (5 stati ben definiti con trigger di validazione dettagliati)
- [x] Flussi logici coprono tutti i casi d'uso rilevanti
- [x] Domande aperte risolte (range cartelle 1-6, lunghezza max nome 15, sanitizzazione con `.strip()`)
- [x] UX interaction definita (input() lineare, prompt da catalogo, errori prima del re-prompt)
- [x] Opzioni valutate e scelta finale motivata
- [x] Integrazione localizzazione documentata (9 chiavi MESSAGGI_CONFIGURAZIONE + riuso MESSAGGI_ERRORI)
- [x] Nessun "buco logico" evidente nel flusso di validazione
- [x] Contratto API corretto verificato (crea_partita_standard + avvia_partita_sicura da API.md)
- [x] Requisito codici_configurazione.py identificato e documentato

**→ Stato: READY — Procedere con `PLAN_TERMINAL_START_MENU.md`**

---

## 📝 Note di Brainstorming

- Fase 2 del TUI: navigazione in-game con tastiera — già parzialmente coperta da `TerminalRenderer`
- Il range 1-7 per i bot è confermato dall'API: `ControllerBotExcessException` se `num_bot > 7`, `ControllerBotNegativeException` se `num_bot < 0`; con 0 bot la partita non potrebbe avviarsi (`MIN_GIOCATORI = 2`), quindi il minimo 1 nella UI è anche una protezione logica
- Il limite 1-6 per le cartelle è esclusivamente UX (screen reader anti-verbosità): il Controller accetta qualsiasi `num_cartelle > 0`
- Il `.strip()` sul nome previene anche nomi con solo spazi che il `GiocatoreBase` rifiuterebbe con `GiocatoreNomeValueException`
- `_stampa_righe()` e `_chiedi_input()` sono candidati naturali a diventare helper privati nella classe `TerminalUI` — da definire nel PLAN
- Considerare se `ui_terminale.py` deve essere una classe (`TerminalUI`) o un modulo con funzioni; la classe facilita il testing tramite dependency injection di `input`/`print`
- Il sistema di logging è già attivo (v0.5.0): la Fase 1 può loggare evento `[SYS]` di avvio configurazione senza rompere nulla

---

## 📚 Riferimenti Contestuali

### File del Repository Analizzati

- `bingo_game/ui/locales/it.py` — Catalogo stringhe italiano; contiene `MESSAGGI_ERRORI`, `MESSAGGI_EVENTI`, `MESSAGGI_OUTPUT_UI_UMANI`, `MESSAGGI_SISTEMA`; va esteso con `MESSAGGI_CONFIGURAZIONE`
- `bingo_game/events/codici_errori.py` — Pattern di riferimento per il nuovo `codici_configurazione.py`
- `bingo_game/ui/renderers/renderer_terminal.py` — Classe `TerminalRenderer` con `render_esito()` orchestratore; usato nella Fase 2
- `bingo_game/ui/ui_terminale.py` — Modulo TUI da progettare e implementare (attualmente vuoto — 0 byte)
- `bingo_game/game_controller.py` — Controller da consumare; contratto formale verificato in `documentations/API.md`
- `documentations/ARCHITECTURE.md` — Vincoli layer architetturali (Interface → Controller, mai Domain direttamente)
- `documentations/API.md` — Contratti API del GameController (v0.6.0): `crea_partita_standard()`, `avvia_partita_sicura()`

### File da Creare/Modificare (Fase Implementativa)

| File | Azione | Motivo |
|---|---|---|
| `bingo_game/events/codici_configurazione.py` | **CREARE** | Costanti-chiave tipate per `MESSAGGI_CONFIGURAZIONE` |
| `bingo_game/ui/locales/it.py` | **ESTENDERE** | Aggiungere `MESSAGGI_CONFIGURAZIONE` con 9 chiavi |
| `bingo_game/ui/ui_terminale.py` | **IMPLEMENTARE** | Classe `TerminalUI` con macchina a stati Fase 1 |
| `main.py` (o entry point) | **AGGIORNARE** | Istanziare e avviare `TerminalUI` |

### Feature Correlate

- **DESIGN_BOT_ATTIVO.md**: Configurazione dei bot — il range 1-7 è confermato coerente con questa feature
- **DESIGN_LOGGING_SYSTEM.md**: Il sistema di logging è già attivo (v0.5.0) — la Fase 1 può emettere log `[SYS]` di avvio configurazione

### Vincoli da Rispettare (da ARCHITECTURE.md)

- Il livello Interface (`ui_terminale.py`) consuma **solo** il Controller (`game_controller.py`), mai il Domain direttamente
- Tutte le stringhe visibili all'utente devono provenire da `it.py` (`MappingProxyType`, tuple di righe)
- Output esclusivamente lineare e testuale: nessuna decorazione grafica (no box ASCII, no colori ANSI, no Unicode decorativo)
- Coerenza con il pattern `TerminalRenderer`: catalogo → accesso per chiave → output testo pulito

---

## 🎯 Risultato Finale Atteso (High-Level)

Una volta implementata la Fase 1, l'utente potrà:

✅ Avviare Tombola Stark da terminale e ricevere un messaggio di benvenuto chiaro e accessibile
✅ Inserire il proprio nome (max 15 caratteri) in modo guidato con un prompt testuale proveniente dal catalogo
✅ Ricevere feedback immediato se il nome è vuoto o troppo lungo, con ri-prompt automatico
✅ Scegliere il numero di bot (1-7) con validazione completa e messaggi d'errore accessibili
✅ Scegliere il numero di cartelle (1-6) con validazione e feedback d'errore
✅ Ricevere una conferma di avvio partita prima che la fase di gioco inizi
✅ Ottenere feedback immediato e correttivo per ogni input non valido senza uscire dall'applicazione
✅ Fruire dell'intera esperienza di configurazione tramite screen reader senza barriere

---

**Fine Design Document**

---

*Salvato in: `documentations/DESIGN_TERMINAL_START_MENU.md`*
*Segue il template: `documentations/templates/TEMPLATE_example_DESIGN_DOCUMENT.md`*
*Versione documento: v1.1 — Ultimo aggiornamento: 2026-02-19*
