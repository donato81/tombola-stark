# 🎨 Design Document - Sistema di Logging Centralizzato

> **FASE: CONCEPT & FLOW DESIGN**  
> Nessuna decisione tecnica qui - solo logica e flussi concettuali  
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-18
- **Stato**: DESIGN FREEZE ✅
- **Versione Target**: v0.4.0 (ipotesi)
- **Autore**: AI Assistant + donato81

---

## 💡 L'Idea in 3 Righe

Tombola Stark non ha oggi nessun meccanismo per ricordare cosa è successo durante una sessione di gioco. Se qualcosa va storto, non c'è modo di capire quando, dove e perché. Vogliamo introdurre un sistema che tenga un diario automatico degli eventi rilevanti, semplice da consultare e proporzionato alle dimensioni del progetto.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Il Gioco**: Produce eventi durante la partita (estrazioni, premi, fine partita) che vale la pena registrare
- **Il Controllore**: Intercetta situazioni anomale e le segnala
- **L'Interfaccia**: Produce azioni legate all'accessibilità (feedback vocali, navigazione) che possono essere utili tracciare
- **Il Sistema di Logging**: Ascolta tutti gli attori e scrive il diario in modo silenzioso e non invasivo
- **Lo Sviluppatore**: Legge il diario quando qualcosa non funziona come previsto

### Concetti Chiave

#### Il Diario di Sessione
- **Cos'è**: Un file di testo che viene scritto automaticamente durante l'esecuzione del gioco, raccogliendo tutto ciò che accade in ordine cronologico
- **Stati possibili**: Inesistente (prima del primo avvio), Attivo (sessione in corso), Consultabile (sessione terminata)
- **Proprietà**: Ogni riga riporta quando è successa una cosa, quanto era importante, e da quale parte del gioco proveniva

#### Il Livello di Importanza
- **Cos'è**: Una classificazione del peso di ogni evento registrato, che va dall'informazione di routine fino all'errore grave
- **Stati possibili**: Informazione normale, Situazione anomala gestita, Errore inatteso
- **Proprietà**: Permette allo sviluppatore di filtrare rapidamente ciò che è rilevante

#### La Modalità di Dettaglio
- **Cos'è**: Un interruttore che decide quanto è verboso il diario
- **Stati possibili**: Normale (solo ciò che conta), Dettagliato (tutto, inclusi i passaggi interni)
- **Proprietà**: La modalità dettagliata è attivabile dallo sviluppatore tramite flag da riga di comando; non è esposta nell'interfaccia utente

### Relazioni Concettuali

```
Il Gioco
  ↓ genera eventi
Il Controllore
  ↓ segnala anomalie
L'Interfaccia
  ↓ produce azioni accessibilità
        ↓ tutti confluiscono in
   Il Sistema di Logging
        ↓ scrive (append, flush immediato)
   Il Diario Permanente (tombola_stark.log)
        ↓ letto da
   Lo Sviluppatore (anche a caldo, durante l'esecuzione)
```

---

## 🎬 Scenari & Flussi

### Scenario 1: Avvio di una Nuova Sessione

**Punto di partenza**: L'utente lancia l'applicazione per la prima volta.

**Flusso**:

1. **Utente**: Avvia il gioco
   → **Sistema**: Verifica se esiste già un posto dove scrivere il diario; se no, lo crea automaticamente senza chiedere nulla all'utente

2. **Sistema**: Apre il diario in modalità append e annota che la sessione è iniziata, con data e ora
   → **Sistema**: Da questo momento in poi ogni evento rilevante viene registrato automaticamente

3. **Utente**: Inizia a giocare normalmente, ignaro del diario
   → **Sistema**: Continua a scrivere in silenzio

**Punto di arrivo**: Il diario è attivo, l'utente non ha fatto nulla di speciale, il gioco funziona normalmente.

**Cosa cambia**: Esiste ora un posto dove vengono registrati gli eventi della sessione, accumulati a quelli delle sessioni precedenti.

---

### Scenario 2: Partita Regolare in Corso

**Punto di partenza**: La partita è avviata, si stanno estraendo i numeri.

**Flusso**:

1. **Utente**: Richiede l'estrazione del prossimo numero
   → **Sistema di Logging**: Annota silenziosamente che un numero è stato estratto e a che punto della partita si è arrivati

2. **Sistema**: Rileva che un giocatore ha fatto ambo
   → **Sistema di Logging**: Annota il premio, il giocatore e il momento in cui è avvenuto

3. **Sistema**: Rileva la tombola e chiude la partita
   → **Sistema di Logging**: Annota la fine della partita con un riepilogo essenziale

**Punto di arrivo**: L'intera partita è tracciata cronologicamente nel diario.

**Cosa cambia**: Il diario contiene la storia completa di quella sessione di gioco, in coda alla storia delle sessioni precedenti.

---

### Scenario 3: Situazione Anomala Gestita

**Punto di partenza**: Qualcosa di inatteso viene tentato (es. avviare una partita già in corso).

**Flusso**:

1. **Controllore**: Intercetta la situazione anomala e la gestisce senza far crashare il gioco
   → **Sistema di Logging**: Annota che si è verificata una situazione anomala, con un livello di importanza più alto del normale

2. **Gioco**: Continua a funzionare normalmente
   → **Sistema di Logging**: Riprende a registrare eventi ordinari

**Punto di arrivo**: L'anomalia è registrata, il gioco non si è interrotto.

**Cosa cambia**: Lo sviluppatore può consultare il diario e trovare la segnalazione con il suo livello di importanza elevato.

---

### Scenario 4: Lo Sviluppatore Consulta il Diario a Caldo

**Punto di partenza**: L'applicazione è in esecuzione e lo sviluppatore vuole monitorare cosa sta accadendo in tempo reale.

**Flusso**:

1. **Sviluppatore**: Apre il file di log con un editor di testo o con un comando tipo `tail -f tombola_stark.log`
   → Vede la cronologia degli eventi fino all'ultimo flush

2. **Sviluppatore**: Nuovi eventi vengono generati dal gioco
   → Il sistema scrive immediatamente ogni riga con flush esplicito; l'editor mostra le nuove righe in tempo reale

3. **Sviluppatore**: Identifica il comportamento che sta analizzando
   → Chiude l'editor; il gioco non è mai stato interrotto

**Punto di arrivo**: Lo sviluppatore ha potuto leggere il diario live senza fermare l'applicazione.

**Cosa cambia**: Il flush immediato garantisce che nessun evento rimanga in memoria tampone — ogni riga è su disco non appena viene scritta.

---

### Scenario 5: Lo Sviluppatore Cerca un Problema in una Sessione Passata

**Punto di partenza**: Qualcosa non ha funzionato come previsto durante una sessione.

**Flusso**:

1. **Sviluppatore**: Apre il diario
   → Vede la cronologia di tutte le sessioni, separate da marcatori di avvio/chiusura con timestamp

2. **Sviluppatore**: Cerca le righe con livello di importanza elevato nella sessione di interesse
   → Trova rapidamente il momento esatto in cui si è verificato il problema e quale parte del gioco lo ha generato

3. **Sviluppatore**: Corregge il problema
   → Alla sessione successiva verifica che il diario non riporti più quella segnalazione

**Punto di arrivo**: Il problema è identificato e risolto.

**Cosa cambia**: Il tempo di diagnosi si riduce drasticamente rispetto all'assenza di qualsiasi tracciabilità.

---

### Scenario 6: Modalità Dettagliata Attivata

**Cosa succede se**: Lo sviluppatore vuole capire ogni singolo passaggio interno del gioco durante una sessione di debug.

**Come si attiva**: Avviando l'applicazione con un flag da riga di comando (es. `--debug` o `--verbose`). Non è esposta nell'interfaccia grafica.

**Sistema dovrebbe**: Scrivere nel diario anche tutti i dettagli interni, non solo gli eventi rilevanti per l'utente. Questa modalità non è pensata per l'uso quotidiano e può rendere il diario molto verboso.

---

## 🔀 Stati e Transizioni

### Stati del Sistema di Logging

#### Stato A: Dormiente
- **Descrizione**: L'applicazione non è ancora avviata; il sistema di logging non esiste
- **Può passare a**: Attivo
- **Trigger**: L'utente avvia l'applicazione

#### Stato B: Attivo
- **Descrizione**: Il diario è aperto in modalità append con flush immediato e riceve eventi da tutte le parti del gioco
- **Può passare a**: Dormiente
- **Trigger**: L'utente chiude l'applicazione

### Diagramma Stati

```
[Applicazione chiusa]
        ↓ utente avvia il gioco
    [Dormiente]
        ↓ sistema inizializzato (append su file esistente o nuovo)
     [Attivo] ←─────────────────┐
        ↓ evento di gioco           │
  [Scrive nel diario + flush]        │
        ↓ scrittura completata      │
     [Attivo] ─────────────────┘
        ↓ utente chiude il gioco
    [Dormiente]
```

---

## 🎤 Interazione con le Parti del Gioco

### Cosa Registra Ogni Parte

- **Il Gioco (estrazioni, premi, partita)**:
  - Fa cosa? Registra gli eventi di gioco significativi (avvio partita, numeri estratti, premi assegnati, fine partita)
  - Quando disponibile? Per tutta la durata della partita
  - Feedback atteso: Nessuno per l'utente; solo scrittura silenziosa nel diario

- **Il Controllore**:
  - Fa cosa? Registra le situazioni anomale che ha intercettato e gestito
  - Quando disponibile? Ogni volta che viene invocato
  - Feedback atteso: Nessuno per l'utente; la segnalazione appare nel diario con livello elevato

- **L'Interfaccia e l'Accessibilità**:
  - Fa cosa? Registra le azioni di navigazione e i messaggi vocali emessi
  - Quando disponibile? Quando l'interfaccia sarà implementata
  - Feedback atteso: Nessuno per l'utente; traccia utile per verificare che il flusso di accessibilità funzioni correttamente

### Formato Concettuale di ogni Voce del Diario

Ogni riga del diario risponde a quattro domande:

```
QUANDO è successo? | QUANTO era importante? | CHI lo ha generato? | COSA è successo?
```

### Marcatore di Sessione

All'avvio e alla chiusura dell'applicazione, il sistema scrive una riga separatrice che identifica i confini di ogni sessione nel diario cumulativo:

```
────────────────────────────────────────────
SESSIONE AVVIATA: 2026-02-18 19:50:00
────────────────────────────────────────────
... eventi della sessione ...
────────────────────────────────────────────
SESSIONE CHIUSA:  2026-02-18 20:10:00
────────────────────────────────────────────
```

---

## 🤔 Domande & Decisioni

### Domande Aperte

*(Nessuna — tutte le domande sono state risolte)*

### Decisioni Prese

- ✅ **Un solo diario per tutto il gioco**: proporzionato alle dimensioni del progetto; nessuna separazione per categoria necessaria
- ✅ **Il sistema è completamente silenzioso per l'utente**: nessuna notifica, nessun messaggio, nessuna interazione richiesta
- ✅ **La cartella del diario viene creata automaticamente**: l'utente non deve fare nulla di manuale
- ✅ **Il diario non entra mai nel repository del codice**: è un artefatto locale di ogni installazione
- ✅ **Accumulo cumulativo**: tutte le sessioni si accumulano nello stesso file; ogni sessione è delimitata da marcatori con timestamp
- ✅ **Flush immediato dopo ogni scrittura**: il diario è consultabile in tempo reale anche mentre l'app è in esecuzione
- ✅ **Modalità dettagliata attivata via flag da riga di comando**: non esposta all'utente nell'interfaccia grafica; solo per lo sviluppatore

### Assunzioni

- L'applicazione gira su una singola macchina, usata da una persona alla volta
- Le sessioni di tombola sono brevi (decine di minuti al massimo); il volume di dati da registrare è contenuto
- Non esiste nessun requisito di analisi statistica o storicizzazione a lungo termine dei log

---

## 🎯 Opzioni Considerate

### Opzione A: Diario Unico (Scelta)

**Descrizione**: Un solo file di diario raccoglie tutti gli eventi del gioco, ordinati cronologicamente, con livelli di importanza differenziati per filtrare rapidamente.

**Pro**:
- ✅ Proporzionato alle dimensioni reali del progetto
- ✅ Semplicissimo da consultare: un file, una storia
- ✅ Zero complessità di gestione
- ✅ Sufficiente per diagnosticare qualsiasi problema in un'app monoutente

**Contro**:
- ❌ In sessioni molto lunghe o con modalità dettagliata attiva, il file può diventare verboso

---

### Opzione B: Diari Multipli per Categoria

**Descrizione**: File separati per eventi di gioco, errori e interfaccia.

**Pro**:
- ✅ Separazione netta per chi deve analizzare solo una categoria
- ✅ Più facile da filtrare per categoria specifica

**Contro**:
- ❌ Sovradimensionato per un'app desktop monoutente
- ❌ Più file da gestire, aprire e sincronizzare mentalmente
- ❌ La separazione aggiunge complessità senza un beneficio reale a queste dimensioni

---

### Scelta Finale

Scelta **Opzione A: Diario Unico** perché Tombola Stark è un'applicazione desktop monoutente con sessioni brevi e un volume di eventi contenuto. La soluzione deve essere proporzionata al problema: un diario unico è tutto ciò che serve per avere piena tracciabilità senza aggiungere complessità inutile.

---

## ✅ Design Freeze Checklist

- [x] Tutti gli scenari principali mappati
- [x] Stati del sistema chiari e completi
- [x] Flussi logici coprono tutti i casi d'uso principali
- [x] Domande aperte risolte ✅ (tutte e 3 chiuse il 2026-02-18)
- [x] Interazione con le parti del gioco definita
- [x] Nessun buco logico evidente
- [x] Opzioni valutate e scelta finale motivata

**Stato**: ~~DRAFT~~ → **DESIGN FREEZE** ✅

**Next Step**: Creare `PLAN_LOGGING_SYSTEM.md` con le decisioni implementative specifiche.

---

## 📝 Note di Brainstorming

- In futuro, se il gioco evolvesse verso una versione multiplayer online, la struttura a diario unico potrebbe non essere più sufficiente — ma è il momento giusto per rivalutarlo, non oggi
- Il diario potrebbe diventare la base per un futuro sistema di replay della partita, rileggendo gli eventi registrati in ordine cronologico
- Il file cumulativo crescerà nel tempo; in una versione futura si potrà valutare una rotazione automatica (es. archivio dopo N sessioni o dopo un certo peso in KB)
- Verificare se ha senso che anche le azioni dei bot vengano tracciate, o solo quelle del giocatore umano

---

## 📚 Riferimenti Contestuali

### Feature Correlate
- **Sistema di eventi** (`bingo_game/events/`): Gli eventi strutturati già esistenti sono i candidati naturali da tracciare nel diario
- **Controllore** (`game_controller`): Il pattern fail-safe già presente è il punto naturale dove registrare le anomalie gestite
- **Accessibilità** (`GiocatoreUmano`, `helper_focus`): Le azioni di navigazione accessibilità sono buoni candidati per la tracciabilità

### Vincoli da Rispettare
- Il sistema di logging non deve mai interrompere o rallentare il gioco, nemmeno in caso di errore di scrittura del diario
- Il diario è un artefatto locale: non entra nel repository del codice
- La soluzione deve rimanere proporzionata: un'app desktop monoutente non ha bisogno di infrastrutture da sistema distribuito
- Il flush immediato non deve mai bloccare il thread principale del gioco

---

## 🎯 Risultato Finale Atteso

Una volta implementato, il sistema garantirà:

✅ Ogni evento rilevante della partita è tracciato automaticamente, senza intervento dell'utente  
✅ Quando qualcosa va storto, lo sviluppatore apre un solo file e trova la risposta in pochi secondi  
✅ Le situazioni anomale sono distinguibili a colpo d'occhio dagli eventi ordinari  
✅ Il diario è consultabile in tempo reale, anche mentre il gioco è in esecuzione  
✅ Tutte le sessioni sono accumulate nello stesso file, separate da marcatori chiari  
✅ In modalità dettagliata (flag `--debug`), ogni passaggio interno è visibile per una diagnosi approfondita  
✅ Il sistema entra in funzione da solo all'avvio e non richiede mai attenzione da parte dell'utente  

---

**Fine Design Document**
