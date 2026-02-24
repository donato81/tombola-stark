# 🎲 Tombola Stark — Tombola Accessibile

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)]()
[![wxPython](https://img.shields.io/badge/UI-wxPython%204.1.1-green)](https://wxpython.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20sviluppo-orange)]()

> *Portiamo la tradizione nel digitale: un simulatore di Tombola dinamico, accessibile e pronto per tutti.*

---

## 📖 Descrizione

**Tombola Stark** è un simulatore della classica tombola italiana, progettato con l'**accessibilità come priorità assoluta**. Il progetto nasce per rendere il gioco pienamente fruibile da utenti con disabilità visive, garantendo compatibilità con screen reader (NVDA, JAWS) e navigazione completa da tastiera, senza alcuna dipendenza dal mouse.

L'architettura è strutturata a livelli (Dominio → Controller → Interfaccia), con un motore di gioco completamente indipendente dalla UI e un sistema di eventi strutturati progettato per la vocalizzazione TTS di ogni azione di gioco.

---

## ✨ Caratteristiche

- 🎯 **Motore di gioco completo** — Gestione di 90 numeri, estrazione casuale certificata, storico estrazioni e percentuale di avanzamento
- 🎴 **Cartelle automatiche** — Generazione automatica di cartelle (3 righe × 5 numeri) con verifica in tempo reale di ambo, terno, quaterna, cinquina e tombola
- 👥 **Multiplayer locale** — Da 2 a 8 giocatori, con supporto simultaneo a 1 giocatore umano e fino a 7 bot automatici
- 🖥️ **Menu TUI accessibile (v0.7.0+)** — Interfaccia da terminale screen reader–friendly (NVDA/JAWS/Orca): 3 prompt sequenziali (nome, bot, cartelle) con validazione in loop e re-prompt automatico
- ♿️ **Accessibilità screen reader (v0.7.0+)** — Output lineare senza decorazioni grafiche, compatibile con NVDA, JAWS e Orca
- 🤖 **Bot Attivi (v0.6.0+)** — I bot dichiarano autonomamente i premi conseguiti in tempo reale, simulando il comportamento di giocatori umani. I reclami sono loggati e pronti per vocalizzazione TTS
- ♿️ **Accessibilità nativa** — Output strutturato compatibile con screen reader; ogni evento di gioco produce dati semantici pronti per la vocalizzazione TTS
- ⌨️ **Navigazione da tastiera** — Zero dipendenza dal mouse nell'architettura di controllo
- 🔊 **TTS integrato** — Supporto a Google TTS (`gTTS`) e `playsound` per feedback audio
- 🛡️ **Gestione errori robusta** — Gerarchia di eccezioni personalizzate per ogni modulo; controller fail-safe che non propaga mai crash all'interfaccia
- 🧩 **Architettura Clean** — Domain layer isolato, testabile indipendentemente da UI e framework esterni
- 📊 **Sistema di logging completo (v0.4.0+)** — File log cumulativo con marcatori di sessione, sub-logger per categoria (game/prizes/system/errors), modalità debug dettagliata

---

## 🖥️ Requisiti di Sistema

| Requisito | Dettaglio |
|---|---|
| **Sistema operativo** | Windows 10 / 11 |
| **Python** | 3.10 o superiore |
| **Dipendenze UI** | wxPython 4.1.1 |
| **Audio** | playsound, gTTS |
| **Connessione** | Necessaria per gTTS (generazione audio online) |

---

## 🚀 Installazione

### 1. Clona il repository

```bash
git clone https://github.com/donato81/tombola-stark.git
cd tombola-stark
```

### 2. Crea un ambiente virtuale

```bash
python -m venv venv
```

### 3. Attiva l'ambiente virtuale

**Windows (Command Prompt)**:
```cmd
venv\Scripts\activate
```

**Windows (PowerShell)**:
```powershell
venv\Scripts\Activate.ps1
```

### 4. Installa le dipendenze

```bash
pip install -r requirements.txt
```

> ⚠️ **Nota**: `wxPython` e `pywin32` sono dipendenze Windows-specifiche. L'installazione su altri sistemi operativi potrebbe richiedere adattamenti.

---

## 🕹️ Come si gioca (v0.9.1)

Avvia il gioco con `python main.py`, inserisci nome, numero di bot e cartelle, poi entra nel **Game Loop interattivo**.

### Comandi disponibili

| Comando | Descrizione |
|---------|-------------|
| `p` | **Prosegui** — estrai il prossimo numero e avanza al turno successivo |
| `s <N> [N2 N3 ...]` | **Segna** — segna uno o più numeri sulla cartella in focus (es. `s 42` oppure `s 42 15 7` o `s 42,15,7`) |
| `c` | **Cartella** — mostra il riepilogo della cartella in focus |
| `v` | **Tabellone** — mostra il riepilogo del tabellone (estratti / mancanti) |
| `q` | **Esci** — chiede conferma prima di uscire dalla partita |
| `?` | **Aiuto** — mostra l'elenco dei comandi e la cartella attualmente in focus |

### Note operative

- **Flessibilità di marcatura**: puoi segnare qualsiasi numero già estratto, non solo l'ultimo.
- **Azioni informative illimitate**: `s`, `c`, `v`, `?` non avanzano il turno — solo `p` lo fa.
- **Conferma obbligatoria per uscire**: il comando `q` chiede sempre conferma (`s` per confermare, qualsiasi altro tasto per annullare).
- **Report finale automatico**: al termine della partita (tombola o numeri esauriti) viene mostrato il riepilogo con vincitore, turni, estratti e premi.

---

## Tasti Rapidi (v0.10.0)

A partire dalla versione 0.10.0, il Game Loop usa tasti singoli via msvcrt (Windows). Non è necessario premere Invio.

### Gruppo 1 — Navigazione riga (semplice)

Freccia Su — sposta il focus di lettura alla riga precedente della cartella.
Freccia Giu — sposta il focus di lettura alla riga successiva della cartella.

### Gruppo 2 — Navigazione riga (avanzata)

A — vai alla prima riga disponibile superiore con numeri non ancora segnati.
Z — vai alla prima riga disponibile inferiore con numeri non ancora segnati.

### Gruppo 3 — Navigazione colonna (semplice)

Freccia Sinistra — sposta il focus alla colonna precedente nella riga corrente.
Freccia Destra — sposta il focus alla colonna successiva nella riga corrente.

### Gruppo 4 — Navigazione colonna (avanzata)

Q — vai alla prima colonna a sinistra non ancora segnata nella riga corrente.
W — vai alla prima colonna a destra non ancora segnata nella riga corrente.

### Gruppo 5 — Salto diretto (richiede numero)

R — vai direttamente alla riga indicata (prompt: numero da 1 a 3).
C — vai direttamente alla colonna indicata (prompt: numero da 1 a 9).

### Gruppo 6 — Navigazione cartella

Pagina Su — mostra il riepilogo della cartella precedente e sposta il focus su di essa.
Pagina Giu — mostra il riepilogo della cartella successiva e sposta il focus su di essa.
Tasti 1 a 6 — seleziona direttamente la cartella corrispondente.

### Gruppo 7 — Visualizzazione cartella

D — visualizza la cartella corrente in modalita semplice (numeri e stato segnatura).
F — visualizza la cartella corrente in modalita avanzata (dettaglio riga per riga).
G — visualizza tutte le cartelle in modalita semplice.
H — visualizza tutte le cartelle in modalita avanzata.

### Gruppo 8 — Consultazione tabellone

U — comunica l'ultimo numero estratto.
I — mostra gli ultimi 5 numeri estratti in ordine cronologico.
O — riepilogo tabellone (estratti, mancanti, percentuale avanzamento).
L — lista completa di tutti i numeri estratti finora.
E — verifica se un numero specifico e stato estratto (prompt: numero da 1 a 90).
N — cerca un numero nelle tue cartelle (prompt: numero da 1 a 90).

### Gruppo 9 — Orientamento

? — mostra lo stato del focus corrente (cartella, riga, colonna in focus).

### Gruppo 10 — Azioni di gioco

S — segna un numero sulla cartella in focus (prompt: numero da 1 a 90).
V — annuncia una vittoria (richiede configurazione avanzata).
P — passa al turno successivo ed estrai il prossimo numero.
X — esci dalla partita (chiede conferma: S per confermare, N per annullare).

---

## ▶️ Utilizzo

### Avvio del gioco

**Modalità normale** (solo eventi INFO):
```bash
python main.py
```

**Modalità debug** (include log dettagliato di ogni turno):
```bash
python main.py --debug
```

Il sistema di logging crea automaticamente la cartella `logs/` e scrive un file cumulativo `logs/tombola_stark.log` con tutti gli eventi di gioco. Ogni sessione è separata da marcatori con timestamp. Il file è leggibile in tempo reale durante l'esecuzione.

**Esempio di output del log**:
```
2026-02-19 12:30:45 | INFO  | tombola_stark.game   | [GAME] Partita creata — giocatore='Mario'
2026-02-19 12:30:46 | INFO  | tombola_stark.game   | [GAME] Partita avviata — giocatori: 2
2026-02-19 12:30:47 | DEBUG | tombola_stark.game   | [GAME] Turno #1 — estratto: 42
2026-02-19 12:30:55 | INFO  | tombola_stark.prizes | [PRIZE] AMBO — giocatore='Mario', cartella=1
```

### Utilizzo del motore di gioco via codice

Puoi usare direttamente le API del motore di gioco per integrarlo in altri progetti:

```python
from bingo_game.game_controller import (
    crea_partita_standard,
    avvia_partita_sicura,
    esegui_turno_sicuro,
    partita_terminata
)

# Crea una partita con 1 umano, 2 cartelle e 3 bot
partita = crea_partita_standard(
    nome_giocatore_umano="Mario",
    num_cartelle_umano=2,
    num_bot=3
)

# Avvia
avvia_partita_sicura(partita)

# Ciclo di gioco
while not partita_terminata(partita):
    turno = esegui_turno_sicuro(partita)
    if turno:
        print(f"Estratto: {turno['numero_estratto']}")
        for premio in turno["premi_nuovi"]:
            print(f"🎉 {premio['giocatore']} ha fatto {premio['premio']}!")
        if turno["tombola_rilevata"]:
            print("🏆 TOMBOLA!")
```

---

## 📂 Struttura del Progetto

```
tombola-stark/
├── bingo_game/                  # 🎯 Pacchetto principale del gioco
│   ├── tabellone.py             # Gestione numeri 1-90 ed estrazioni
│   ├── cartella.py              # Cartella giocatore e verifica premi
│   ├── partita.py               # Coordinamento partita
│   ├── game_controller.py       # Controller: orchestrazione sicura
│   ├── comandi_partita.py       # Comandi di partita
│   ├── players/                 # Gerarchia giocatori
│   │   ├── giocatore_base.py    # Classe base (umano + bot)
│   │   ├── giocatore_umano.py   # Giocatore umano
│   │   ├── giocatore_automatico.py  # Bot automatico
│   │   ├── helper_focus.py      # Helper accessibilità (focus)
│   │   └── helper_reclami_focus.py  # Helper reclami vittoria
│   ├── events/                  # Sistema eventi strutturati per TTS
│   │   ├── eventi_partita.py    # ReclamoVittoria, EventoFineTurno
│   │   ├── eventi_output_ui_umani.py  # Messaggi per UI umana
│   │   └── codici_*.py          # Costanti e codici di categorizzazione
│   ├── exceptions/              # Gerarchia eccezioni per modulo
│   │   ├── partita_exceptions.py
│   │   ├── giocatore_exceptions.py
│   │   ├── game_controller_exceptions.py
│   │   └── ...
│   ├── validations/             # Logica di validazione
│   └── ui/                      # Interfaccia utente (in sviluppo)
├── my_lib/                      # Libreria di supporto
├── tests/                       # Suite di test (pytest)
├── documentations/
│   ├── API.md                   # 📚 Riferimento API pubblico
│   ├── ARCHITECTURE.md          # 🏗️ Documentazione architetturale
│   ├── CHANGELOG.md             # 📝 Cronologia versioni e modifiche
│   └── templates/               # Template per nuovi documenti
├── main.py                      # ▶️ Entry point dell'applicazione
├── requirements.txt             # Dipendenze Python
└── README.md                    # Questo file
```

---

## 📚 Documentazione Tecnica

La documentazione tecnica completa è disponibile nella cartella [`documentations/`](documentations/):

| Documento | Descrizione |
|---|---|
| [`API.md`](documentations/API.md) | Riferimento completo di tutte le classi pubbliche, metodi, parametri e valori di ritorno |
| [`ARCHITECTURE.md`](documentations/ARCHITECTURE.md) | Architettura del software, suddivisione a livelli, pattern chiave e flusso dei dati |
| [`CHANGELOG.md`](documentations/CHANGELOG.md) | Cronologia delle versioni e modifiche apportate in ogni release |

---

## 🧪 Test

Il progetto utilizza **pytest** per i test unitari e di integrazione.

```bash
# Installa pytest se non già presente
pip install pytest

# Esegui tutti i test
pytest tests/

# Esegui con verbosità
pytest tests/ -v

# Esegui con report di copertura
pytest tests/ --cov=bingo_game
```

I test del livello dominio (`Tabellone`, `Cartella`, `Partita`, `GiocatoreBase`) sono progettati per essere eseguiti **in completo isolamento** da UI e framework esterni.

---

## 🤝 Contributi

I contributi sono benvenuti! Per contribuire al progetto:

1. **Fai un fork** del repository
2. **Crea un branch** per la tua feature:
   ```bash
   git checkout -b feature/nome-feature
   ```
3. **Effettua le modifiche** rispettando le convenzioni del progetto:
   - Regole di dipendenza tra livelli (vedi [`ARCHITECTURE.md`](documentations/ARCHITECTURE.md))
   - Naming conventions Python (`snake_case` per metodi, `PascalCase` per classi)
   - Aggiungi test per le nuove funzionalità
4. **Fai il commit** con messaggi convenzionali:
   ```bash
   git commit -m "feat: descrizione della feature"
   ```
5. **Apri una Pull Request** descrivendo le modifiche apportate

### Linee Guida per i Contributi

- Mantieni il **domain layer privo di dipendenze UI** (vedi regola d'oro in `ARCHITECTURE.md`)
- Ogni nuovo modulo deve avere il proprio file `*_exceptions.py`
- I messaggi in italiano vanno **solo** nel livello interfaccia o in `bingo_game/events/`, mai nel dominio
- Aggiorna `API.md` e `CHANGELOG.md` per ogni nuova API pubblica o release

---

## 📄 Licenza

Questo progetto è distribuito sotto licenza **MIT**.

Sei libero di usare, modificare e distribuire il codice, a condizione di mantenere l'intestazione di licenza originale.

Vedi il file [`LICENSE`](LICENSE) per il testo completo.

---

## 👤 Autore

**donato81** — [github.com/donato81](https://github.com/donato81)

---

<div align="center">

*Tombola Stark — Perché ogni giocatore merita di giocare.*

</div>
