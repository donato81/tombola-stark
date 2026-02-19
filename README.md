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
- ♿ **Accessibilità nativa** — Output strutturato compatibile con screen reader; ogni evento di gioco produce dati semantici pronti per la vocalizzazione TTS
- ⌨️ **Navigazione da tastiera** — Zero dipendenza dal mouse nell'architettura di controllo
- 🔊 **TTS integrato** — Supporto a Google TTS (`gTTS`) e `playsound` per feedback audio
- 🛡️ **Gestione errori robusta** — Gerarchia di eccezioni personalizzate per ogni modulo; controller fail-safe che non propaga mai crash all'interfaccia
- 🧩 **Architettura Clean** — Domain layer isolato, testabile indipendentemente da UI e framework esterni

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
- Aggiorna `API.md` per ogni nuova API pubblica

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
