# Registro delle Modifiche

Tutte le modifiche rilevanti a questo progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Versionamento Semantico](https://semver.org/spec/v2.0.0.html).

---

## [Non Rilasciato]

### Aggiunto
- Strato interfaccia utente (`bingo_game/ui/`) — in sviluppo attivo.
- Navigazione da tastiera e integrazione TTS completa per il giocatore umano.
- Utility di supporto generali (`bingo_game/utils.py`).

---

## [0.3.0] - 2026-02-18

### Aggiunto
- `API.md` nella cartella `documentations/`: riferimento completo di tutte le classi pubbliche, metodi, parametri e valori di ritorno. (commit [fbe71b2](https://github.com/donato81/tombola-stark/commit/fbe71b2e50af50083560e72ccc366a86acd0b85b))
- `ARCHITECTURE.md` nella cartella `documentations/`: documentazione dell'architettura a livelli (Dominio → Controller → Interfaccia), pattern chiave, flusso dei dati e architettura dell'accessibilità. (commit [fbe71b2](https://github.com/donato81/tombola-stark/commit/fbe71b2e50af50083560e72ccc366a86acd0b85b))
- Template di progetto (`documentations/templates/`) con modelli per API, Architettura, Changelog, Design Document, Piano di Implementazione e TODO. (commit [4781a8e](https://github.com/donato81/tombola-stark/commit/4781a8eaf972a43b5f530735462d87bcfd068314))

### Modificato
- `README.md` aggiornato con badge, descrizione accessibilità, istruzioni di installazione complete, struttura del progetto ad albero e link alla documentazione tecnica. (commit [3b47b4a](https://github.com/donato81/tombola-stark/commit/3b47b4ac1f911b9b2575cbaefeb8125ccb48f58c))
- Cartella `documentations/` riorganizzata: rimossa la directory di lavoro temporanea, aggiunta struttura definitiva per la documentazione. (commit [24ef07e](https://github.com/donato81/tombola-stark/commit/24ef07e0fed36dae2c17afea3d6b5e48893be7cb))

---

## [0.2.0] - 2026-02-16

### Aggiunto
- Cartella `documentations/` introdotta nel progetto come area dedicata alla documentazione tecnica. (commit [24ef07e](https://github.com/donato81/tombola-stark/commit/24ef07e0fed36dae2c17afea3d6b5e48893be7cb))

### Modificato
- Struttura del repository riorganizzata: rimossa la directory di lavoro temporanea con Perplexity, separazione netta tra codice sorgente e documentazione.

---

## [0.1.0] - 2026-02-12

*Rilascio iniziale — Motore di gioco core.*

### Aggiunto
- Classe `Tabellone`: gestione dei 90 numeri, estrazione casuale, storico estrazioni, percentuale di avanzamento, snapshot di stato. (commit [82bda90](https://github.com/donato81/tombola-stark/commit/82bda90bf62f898ef0c343d205a2ac48c1f24bf3))
- Classe `Cartella`: 3 righe × 5 numeri, segnatura automatica dei numeri estratti, verifica in tempo reale di ambo, terno, quaterna, cinquina e tombola per riga.
- Classe `Partita`: coordinamento tabellone e giocatori, ciclo di estrazione, verifica premi, gestione stati (`non_iniziata` → `in_corso` → `terminata`).
- Classe `GiocatoreBase`: gestione identità, cartelle multiple, aggiornamento con numero estratto, rilevamento tombola.
- Classe `GiocatoreUmano`: specializzazione per il giocatore umano con supporto al sistema di eventi per l'accessibilità.
- Classe `GiocatoreAutomatico`: bot di gioco senza interazione umana richiesta.
- Modulo `game_controller`: funzioni di orchestrazione fail-safe (`crea_partita_standard`, `avvia_partita_sicura`, `esegui_turno_sicuro`, `ottieni_stato_sintetico`).
- Sistema di eventi strutturati (`bingo_game/events/`) per output semantico pronto per la vocalizzazione TTS.
- Gerarchia di eccezioni personalizzate per ogni modulo: `partita_exceptions.py`, `cartella_exceptions.py`, `giocatore_exceptions.py`, `game_controller_exceptions.py`, `tabellone_exceptions.py`.
- Modulo `validations/` per la logica di validazione riutilizzabile.
- Suite di test unitari (`tests/`) per la validazione automatica di `Cartella`, `Tabellone`, `Partita` e `GiocatoreBase`.
- `main.py` come entry point dell'applicazione.
- `requirements.txt` con dipendenze: wxPython, gTTS, pygame, playsound, Pillow e librerie di supporto.

---

## Legenda

- **Aggiunto**: Nuove funzionalità
- **Modificato**: Modifiche a funzionalità esistenti
- **Deprecato**: Funzionalità in via di dismissione
- **Rimosso**: Funzionalità rimosse
- **Corretto**: Bug fix
- **Sicurezza**: Correzioni di vulnerabilità

---

*Per i dettagli tecnici completi, consulta la [storia dei commit](https://github.com/donato81/tombola-stark/commits/main) o [`documentations/ARCHITECTURE.md`](documentations/ARCHITECTURE.md).*

[Non Rilasciato]: https://github.com/donato81/tombola-stark/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/donato81/tombola-stark/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/donato81/tombola-stark/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/donato81/tombola-stark/releases/tag/v0.1.0
