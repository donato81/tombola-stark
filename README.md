# 🎲 Tombola Stark — Tombola Accessibile

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)]()
[![UI](https://img.shields.io/badge/UI-In%20ridefinizione-lightgrey)]()
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

> ⚠️ **Nota**: alcune dipendenze restano Windows-specifiche e l'assetto dell'interfaccia utente e' in ridefinizione.

---

## 📌 Stato dell'interfaccia

La TUI storica e' stata rimossa dal repository e la nuova UI non e' ancora documentata.
Lo stato corrente del progetto e' questo:

- il motore di gioco resta disponibile e testato;
- il controller continua a esporre API sicure per creare, avviare e far avanzare una partita;
- i componenti di supporto per localizzazione, rendering ed eventi restano disponibili;
- questa documentazione non descrive ancora un flusso utente finale basato su una nuova interfaccia.

---

## ▶️ Utilizzo

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
│   └── ui/                      # Componenti di supporto del layer presentazione
├── my_lib/                      # Libreria di supporto
├── tests/                       # Suite di test (unittest)
├── docs/
│   ├── API.md                   # 📚 Riferimento API pubblico
│   ├── ARCHITECTURE.md          # 🏗️ Documentazione architetturale
│   ├── 1 - templates/           # Template di documentazione progetto
│   ├── 2 - projects/            # DESIGN_<feature>.md
│   ├── 3 - coding plans/        # PLAN_<feature>_vX.Y.Z.md
│   ├── 4 - reports/             # REPORT_<tipo>_<data>.md
│   └── 5 - todolist/            # TODO_<feature>_vX.Y.Z.md
├── main.py                      # ▶️ Entry point dell'applicazione
├── requirements.txt             # Dipendenze Python
└── README.md                    # Questo file
```

---

## 📚 Documentazione Tecnica

La documentazione tecnica completa è disponibile nella cartella [`docs/`](docs/):

| Documento | Descrizione |
|---|---|
| [`API.md`](docs/API.md) | Riferimento completo di tutte le classi pubbliche, metodi, parametri e valori di ritorno |
| [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Architettura del software, suddivisione a livelli, pattern chiave e flusso dei dati |
| [`CHANGELOG.md`](CHANGELOG.md) | Cronologia delle versioni e modifiche apportate in ogni release |

---

## 🧪 Test

Il progetto utilizza **unittest** (standard library) per i test unitari e di integrazione.

```bash
# Esegui tutti i test
python -m unittest discover -s tests -p "test_*.py"

# Esegui con verbosità
python -m unittest discover -s tests -p "test_*.py" -v
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
    - Regole di dipendenza tra livelli (vedi [`ARCHITECTURE.md`](docs/ARCHITECTURE.md))
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
