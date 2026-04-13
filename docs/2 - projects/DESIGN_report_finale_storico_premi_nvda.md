---
type: design
feature: report_finale_storico_premi_nvda
agent: Agent-Design
status: REVIEWED
version: v0.15.0
date: 2026-04-13
report_ref: docs/4 - reports/REPORT_DIAGNOSI_ALFA_2026-04-13.md
---

# DESIGN — Report finale esaustivo e storico premi NVDA

## Metadati

tipo: design
titolo: Chiusura gap alfa su report finale, storico premi e lettura NVDA dei vincitori
data_creazione: 2026-04-13
agente: Agent-Design
stato: REVIEWED
versione_target: v0.15.0
report_riferimento: docs/4 - reports/REPORT_DIAGNOSI_ALFA_2026-04-13.md

---

## 1. Idea in 3 righe

Completare il perimetro informativo della partita aggiungendo una
struttura storica dei premi assegnati nel dominio e riusandola sia per
la lettura NVDA dei premi sia per il report finale di fine partita.
L'obiettivo e rimuovere l'uso delle chiavi opache di `premi_gia_assegnati`
nei flussi di presentazione, sostituendole con dati espliciti e coerenti.
Il risultato atteso e una chiusura piu solida della versione alfa sul
fronte accessibilita, orientamento post-partita e leggibilita dei premi.

---

## 2. Attori e Concetti

- `Partita`: sorgente della verita per i premi; oggi mantiene
  `premi_gia_assegnati`, `premi_tipo_chiusi` e `ultimo_premio_evento`, ma
  non conserva uno storico completo dei vincitori.
- `ComandiGiocatoreUmano`: costruisce i testi vocali `Ctrl+G` e `Ctrl+I`.
  Attualmente `Ctrl+I` non puo leggere i vincitori perche non ha uno
  storico consultabile.
- `FinestraGioco`: crea il dizionario `dati_report` a fine partita.
  Oggi passa al renderer un set di chiavi opache, non un report narrabile.
- `WxRenderer`: vocalizza il riepilogo finale e i messaggi on demand.
  Ha bisogno di una struttura dati piu ricca ma stabile.
- `PannelloRiepilogoFinale`: vista testuale/visiva del termine partita.
  Deve mostrare vincitore, premi leggibili e statistiche minime per il
  giocatore umano.
- `storico_premi`: nuova lista ordinata di eventi premio, con un record per
  ogni assegnazione valida.
- `report_finale_partita`: contratto di output strutturato verso la UI,
  distinto dallo stato sintetico di bordo.

---

## 3. Flussi Concettuali

### 3.1 Assegnazione premio e persistenza nello storico

```text
verifica_premi() individua nuovi candidati validi
  -> Partita registra le chiavi in premi_gia_assegnati
  -> Partita registra i tipi in premi_tipo_chiusi
  -> Partita crea un evento esplicito con premio, giocatore, cartella, riga, turno
  -> l'evento viene aggiunto a storico_premi mantenendo l'ordine temporale
  -> ultimo_premio_evento resta l'ultimo elemento registrato
```

### 3.2 Lettura NVDA dei premi durante la partita

```text
Utente preme Ctrl+G
  -> FinestraGioco chiama ComandiGiocatoreUmano.stato_premi()
  -> il comando legge ultimo_premio_evento e premi_tipo_chiusi
  -> restituisce testo sintetico: ultimo premio + prossimo premio

Utente preme Ctrl+I
  -> FinestraGioco chiama ComandiGiocatoreUmano.dettaglio_premi()
  -> il comando legge storico_premi
  -> restituisce elenco completo con premio e vincitore per ogni voce
```

### 3.3 Generazione report finale di partita

```text
Partita terminata o tombola rilevata
  -> FinestraGioco costruisce dati_report_finale ricco
  -> include storico_premi, numeri estratti, statistiche giocatori,
     riepilogo umano e vincitore tombola
  -> WxRenderer vocalizza un sommario leggibile
  -> PannelloRiepilogoFinale mostra i dettagli essenziali senza chiavi opache
```

---

## 4. Decisioni Architetturali

### D1 — Introdurre `storico_premi` nel dominio

La persistenza del vincitore non puo restare nel layer di presentazione.
Il dominio e l'unico punto affidabile in cui il premio viene validato e
assegnato. Per questo `Partita` deve esporre `storico_premi` come lista di
eventi espliciti e ordinati, separata dal set tecnico `premi_gia_assegnati`.

### D2 — Mantenere `premi_gia_assegnati` come struttura tecnica interna

Il set esistente resta utile per prevenire duplicazioni e garantire lookup
O(1), ma non deve piu essere riusato dalla UI come dato di report.
Questa separazione evita ambiguita tra identita tecnica del premio e dato
narrabile per l'utente.

### D3 — Contratto dedicato per il report finale

Il report finale non coincide con `get_stato_sintetico()`. Serve un payload
specifico con dati di riepilogo, cronologia premi e statistiche umane. Il
contratto va costruito in `FinestraGioco` usando dati forniti dal dominio,
senza demandare al renderer trasformazioni deduttive complesse.

### D4 — Riutilizzo dello stesso storico per Ctrl+I e report finale

La lettura NVDA dei vincitori e il riepilogo finale devono leggere la stessa
fonte dati. In questo modo si evita divergenza tra cio che il giocatore sente
durante la partita e cio che ritrova a fine partita.

### D5 — Statistiche umane minime ma utili

Per la chiusura alfa sono sufficienti statistiche sintetiche, non analitiche:
- numeri segnati / numeri totali sulle cartelle dell'umano
- numeri mancanti alla tombola per ogni cartella umana
- elenco premi vinti dal giocatore umano

Questo livello di dettaglio migliora l'orientamento senza introdurre una
telemetria complessa o un refactor esteso dei modelli di gioco.

---

## 5. Rischi e Vincoli

### R1 — Backward compatibility dei test esistenti

`Partita` e gia molto coperta dai test. L'aggiunta di `storico_premi` deve
essere additive-only e non alterare il comportamento di `premi_gia_assegnati`
o `premi_tipo_chiusi`.

### R2 — Co-vittorie nello stesso turno

Lo storico deve registrare ogni vincitore separatamente, anche quando lo
stesso tipo premio viene assegnato a piu giocatori nello stesso turno.
L'ordine di registrazione deve restare quello di validazione del dominio.

### R3 — Accessibilita NVDA

Il testo finale vocalizzato deve essere breve nel sommario iniziale e piu
esteso solo nel pannello/log. Non bisogna introdurre popup o finestre
aggiuntive al termine della partita.

### R4 — Coerenza con il codice attuale

G1 e G2 risultano gia chiusi nel codice corrente. Questo design copre solo i
gap residui G3, G4, G5 e G6 del report di diagnosi alfa.

### R5 — Nessun coupling renderer-dominio

Il renderer non deve ricostruire da solo i vincitori partendo da stringhe o
chiavi interne. Tutte le strutture necessarie devono arrivare gia esplicite.

---

## 6. Perimetro di implementazione previsto

File primari coinvolti:

- `bingo_game/partita.py`
- `bingo_game/comandi_partita.py`
- `bingo_game/ui/finestra_gioco.py`
- `bingo_game/ui/renderers/renderer_wx.py`

File secondari possibili:

- `tests/test_partita.py`
- `tests/test_comandi_partita.py`
- `CHANGELOG.md`
- `docs/API.md`
- `docs/ARCHITECTURE.md` se viene esplicitato il nuovo contratto di report

---

## 7. Esito atteso per la chiusura alfa

Al termine del lavoro il progetto deve poter offrire:

- lettura `Ctrl+I` con vincitori reali e non solo tipi premio
- report finale con cronologia premi leggibile
- riepilogo finale con dati utili al giocatore umano
- eliminazione completa delle chiavi opache dal testo vocalizzato

Questo pacchetto documenta il minimo architetturale ancora necessario per
considerare il flusso di partita abbastanza rifinito da chiudere l'alfa.