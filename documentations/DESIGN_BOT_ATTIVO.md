# 🎨 Design Document - Bot Attivo: Giocatore Automatico Consapevole

> **FASE: CONCEPT & FLOW DESIGN**  
> Nessuna decisione tecnica qui - solo logica e flussi concettuali  
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-19
- **Stato**: DRAFT
- **Versione Target**: v0.6.0 (ipotesi)
- **Autore**: AI Assistant + donato81

---

## 💡 L'Idea in 3 Righe

Il giocatore automatico (bot) oggi si limita a segnare il numero estratto sulle proprie cartelle, senza fare altro. Vogliamo che il bot diventi un giocatore consapevole: dopo ogni estrazione, valuta autonomamente il proprio stato rispetto ai premi disponibili e, quando le condizioni lo permettono, alza la mano e reclama la vittoria esattamente come farebbe un giocatore umano.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Il Bot**: Giocatore automatico gestito dal sistema; riceve numeri, valuta le proprie cartelle, decide se reclamare un premio e comunica la propria decisione alla Partita tramite il sistema di eventi
- **La Partita**: Arbitro supremo; riceve il segnale di fine turno dal Bot (con o senza reclamo), valida la correttezza del reclamo e assegna o nega il premio
- **Il GameController**: Orchestratore del ciclo di gioco; gestisce la sequenza di turni e verifica l'avanzamento complessivo della partita
- **Il Sistema di Logging**: Registra ogni azione del Bot in modo silenzioso e trasparente

### Concetti Chiave

#### Il Turno del Bot
- **Cos'è**: L'unità minima di azione del Bot all'interno di un ciclo di gioco; inizia quando la Partita comunica un numero estratto e termina quando il Bot emette il segnale di fine turno
- **Stati possibili**: In attesa, In elaborazione, Completato (senza reclamo), Completato (con reclamo)
- **Proprietà**: È sempre autonomo; non richiede input umano; deve completarsi entro lo stesso ciclo in cui avviene l'estrazione

#### Il Potenziale di Reclamo
- **Cos'è**: Il risultato dell'autovalutazione del Bot sulle proprie cartelle dopo aver segnato un numero; risponde alla domanda "ho combinato qualcosa che merita di essere dichiarato?"
- **Stati possibili**: Nessuno (nessun premio realizzato), Premio Disponibile (il premio è ancora assegnabile), Premio Non Disponibile (già preso da qualcun altro)
- **Proprietà**: Viene calcolato a ogni turno dal Bot consultando le proprie cartelle e lo stato dei premi comunicato dalla Partita

#### Il Reclamo
- **Cos'è**: La dichiarazione formale con cui il Bot comunica di aver realizzato un premio; è un contenuto strutturato che viaggia dentro l'EventoFineTurno
- **Stati possibili**: Assente (nessun reclamo nel turno), Presente (reclamo inviato, in attesa di validazione), Validato (Partita ha confermato il premio), Rigettato (Partita ha negato il premio)
- **Proprietà**: Contiene informazioni sufficienti perché la Partita possa validarlo senza ambiguità (quale cartella, quale riga, quale premio)

### Relazioni Concettuali

```
Partita
  ↓ comunica numero estratto + stato premi disponibili
Il Bot
  ↓ segna il numero sulle proprie cartelle
  ↓ valuta il Potenziale di Reclamo
  ↓ decide se reclamare
EventoFineTurno (con o senza Reclamo)
  ↓ ricevuto e processato da
La Partita (arbitra e valida)
  ↓ se valido → assegna premio → log + vocalizzazione
  ↓ se non valido → ignora → log
```

---

## 🎬 Scenari & Flussi

### Scenario 1: Turno Normale — Il Bot Non Ha Niente da Reclamare

**Punto di partenza**: La Partita ha estratto un numero. Il Bot ha le sue cartelle aggiornate.

**Flusso**:

1. **Partita**: Comunica il numero estratto al Bot
   → **Bot**: Segna il numero su tutte le sue cartelle

2. **Bot**: Scansiona le proprie cartelle cercando combinazioni completate
   → **Bot**: Non trova nessun premio realizzato nel turno corrente

3. **Bot**: Non ha niente da dichiarare
   → **Bot**: Emette EventoFineTurno senza reclamo

4. **Partita**: Riceve EventoFineTurno senza reclamo
   → **Partita**: Registra il turno del Bot come completato, nessuna azione premi

**Punto di arrivo**: Il turno del Bot è chiuso. Si passa al prossimo giocatore o al turno successivo.

**Cosa cambia**: Le cartelle del Bot sono aggiornate con il nuovo numero.

---

### Scenario 2: Turno con Reclamo — Il Bot Dichiara Ambo

**Punto di partenza**: La Partita ha estratto un numero. Il Bot ha cartelle parzialmente segnate.

**Flusso**:

1. **Partita**: Comunica il numero estratto al Bot; lo stato dei premi indica che l'Ambo è ancora disponibile
   → **Bot**: Segna il numero su tutte le sue cartelle

2. **Bot**: Scansiona le proprie cartelle
   → **Bot**: Sulla Cartella 2, Riga 1 trova 2 numeri segnati su 2: Ambo completato!

3. **Bot**: Verifica che l'Ambo sia ancora disponibile (non già assegnato)
   → **Bot**: Conferma disponibilità → decide di reclamarlo

4. **Bot**: Prepara il reclamo con i dettagli (Cartella 2, Riga 1, premio "Ambo")
   → **Bot**: Emette EventoFineTurno con il reclamo allegato

5. **Partita**: Riceve EventoFineTurno con reclamo
   → **Partita**: Verifica indipendentemente che la Cartella 2, Riga 1 del Bot abbia effettivamente 2 numeri segnati

6. **Partita**: Reclamo validato con successo
   → **Partita**: Assegna l'Ambo al Bot; segna il premio come non più disponibile; genera evento di vocalizzazione

**Punto di arrivo**: Il Bot ha vinto l'Ambo. Il sistema ha loggato l'evento. L'utente ha ricevuto il feedback vocale.

**Cosa cambia**: L'Ambo è assegnato al Bot e non è più disponibile per gli altri giocatori.

---

### Scenario 3: Reclamo Rigettato — Il Premio È Già Stato Assegnato

**Punto di partenza**: Due Bot completano lo stesso premio nello stesso turno (condizione limite).

**Flusso**:

1. **Bot A** e **Bot B**: Entrambi segnano il numero estratto, entrambi completano la Terna
   → Entrambi valutano il Potenziale di Reclamo e lo trovano positivo

2. **Partita**: Processa prima l'EventoFineTurno del Bot A
   → **Partita**: Valida il reclamo, assegna la Terna al Bot A

3. **Partita**: Processa poi l'EventoFineTurno del Bot B
   → **Partita**: Trova che la Terna è già stata assegnata → rigetta il reclamo

4. **Partita**: Log dell'evento (reclamo rigettato)
   → Nessun feedback vocale per il rigetto (evento silenzioso per l'utente)

**Punto di arrivo**: La Terna è assegnata al Bot A. Il Bot B non riceve il premio, ma il gioco prosegue regolarmente.

**Cosa cambia**: Solo il primo reclamo valido viene premiato. I reclami successivi sullo stesso premio sono silenziosamente ignorati.

---

### Scenario 4: Il Bot Reclama la Tombola

**Cosa succede se**: Il Bot completa tutte e 15 le celle di almeno una cartella.

**Sistema dovrebbe**: Il Bot emette un EventoFineTurno con reclamo di tipo Tombola. La Partita valida, assegna il premio, e avvia la sequenza di chiusura della partita (cambio di stato, vocalizzazione finale, logging del riepilogo).

---

### Scenario 5: Il Bot Ha Più Premi Disponibili nello Stesso Turno

**Cosa succede se**: In un singolo turno, il Bot completa simultaneamente due premi diversi (condizione teoricamente possibile in partita avanzata, es. Terna e Quaterna sulla stessa cartella).

**Sistema dovrebbe**: Il Bot identifica il premio più alto realizzato tra quelli ancora disponibili e reclama solo quello. Non è possibile reclamare più premi nello stesso turno con un singolo EventoFineTurno. Il premio inferiore, se non già assegnato ad altri, resterà disponibile e potrà essere reclamato nei turni successivi.

---

## 🔀 Stati e Transizioni

### Stati del Bot nel Turno

#### Stato A: In Attesa
- **Descrizione**: Il Bot è in attesa che la Partita estragga il prossimo numero e comunichi lo stato dei premi disponibili
- **Può passare a**: In Elaborazione
- **Trigger**: La Partita comunica il numero estratto

#### Stato B: In Elaborazione
- **Descrizione**: Il Bot ha ricevuto il numero, lo sta segnando sulle cartelle e sta valutando il Potenziale di Reclamo
- **Può passare a**: Completato Senza Reclamo, Completato Con Reclamo
- **Trigger**: Fine della scansione interna delle cartelle

#### Stato C: Completato Senza Reclamo
- **Descrizione**: Il Bot ha segnato il numero ma non ha trovato nessun premio disponibile da reclamare; emette EventoFineTurno vuoto
- **Può passare a**: In Attesa
- **Trigger**: Ricezione del prossimo numero estratto dalla Partita

#### Stato D: Completato Con Reclamo
- **Descrizione**: Il Bot ha trovato un premio disponibile, lo ha preparato come reclamo formale e lo ha allegato all'EventoFineTurno
- **Può passare a**: In Attesa (dopo validazione Partita)
- **Trigger**: La Partita ha processato il reclamo (approvato o rigettato)

### Diagramma Stati del Turno del Bot (ASCII)

```
[PARTITA: numero estratto + stato premi]
              ↓
        [In Attesa]
              ↓ numero ricevuto
       [In Elaborazione]
          ↙           ↘
  [nessun premio]   [premio trovato
   disponibile]      + disponibile]
       ↓                   ↓
[Completato           [Completato
senza reclamo]        con reclamo]
       ↓                   ↓
[EventoFineTurno] [EventoFineTurno
    (vuoto)]       + Reclamo]
          ↘           ↙
        [Partita riceve e valida]
                 ↓
          [In Attesa] ← (turno successivo)
```

---

## 🎤 Interazione con le Parti del Gioco

### Il Bot come Attore Silenzioso

- **Cosa fa il Bot?**
  - Agisce automaticamente senza richiedere input dall'utente
  - Emette sempre un EventoFineTurno al termine del suo ciclo di elaborazione
  - Non gestisce direttamente la UI: delega tutto alla Partita che veicolerà i messaggi

- **Quando agisce?**
  - Esclusivamente durante il proprio turno, all'interno del ciclo orchestrato dal GameController

- **Feedback verso l'utente?**
  - Nessun feedback diretto dal Bot
  - La Partita, ricevuto un reclamo valido, genera un evento di vocalizzazione: *"Il Bot 'Stark-1' dichiara Ambo sulla Cartella 2!"*
  - Il sistema di logging registra ogni azione rilevante del Bot nella categoria `prizes` o `system`

### Vocalizzazione dei Reclami del Bot

- **Quando il Bot reclama un premio inferiore alla tombola**: Sistema comunica *"[Nome Bot] dichiara [Premio] sulla Cartella [N]!"*
- **Quando il Bot reclama la tombola**: Sistema comunica *"[Nome Bot] ha fatto TOMBOLA sulla Cartella [N]! Partita terminata."*
- **Quando il reclamo del Bot viene rigettato**: Nessun messaggio vocale (evento silenzioso, solo log interno)

---

## 🤔 Domande & Decisioni

### Domande Aperte

- [ ] Il Bot deve reclamare **sempre** il premio più alto disponibile, oppure può avere una "strategia" (es. tenere nascosta la quaterna per aspettare la cinquina)?
- [ ] In caso di più Bot che completano lo stesso premio nello stesso turno, l'ordine di processamento è deterministico (es. per indice giocatore) o casuale?
- [ ] Il feedback vocale per i reclami del Bot deve essere distinto stilisticamente dal feedback per i reclami del giocatore umano?

### Decisioni Prese

- ✅ **La Partita rimane l'arbitro unico**: Il Bot non assegna mai premi a sé stesso; si limita a dichiarare. È la Partita a validare e assegnare
- ✅ **Il Bot usa EventoFineTurno esattamente come il giocatore umano**: Nessun canale speciale o privilegiato; completo rispetto del sistema di eventi esistente
- ✅ **Il reclamo rigettato è silenzioso per l'utente**: Solo logging interno; nessun messaggio vocale per i casi limite
- ✅ **Un solo reclamo per turno**: Il Bot dichiara al massimo un premio per turno, il più alto tra quelli disponibili

### Assunzioni

- Il sistema di eventi (`EventoFineTurno`, `ReclamoVittoria`) è già operativo e non necessita di modifiche strutturali
- La Partita espone già un modo per interrogare lo stato dei premi disponibili, oppure tale capacità verrà aggiunta nella fase PLAN
- Il GameController orchestra già i turni in modo sequenziale; non è necessario un meccanismo asincrono

---

## 🎯 Opzioni Considerate

### Opzione A: Bot Reattivo (Scelta)

**Descrizione**: Il Bot valuta lo stato dopo ogni numero estratto e reclama immediatamente se le condizioni sono soddisfatte. Nessuna memoria tra un turno e l'altro, nessuna strategia a lungo termine.

**Pro**:
- ✅ Perfettamente allineato con l'architettura esistente (`EventoFineTurno` già pronto)
- ✅ Comportamento prevedibile e testabile
- ✅ Rispetta il principio di disaccoppiamento: il Bot non conosce lo stato degli altri giocatori
- ✅ Implementazione minima, massima coerenza con il sistema

**Contro**:
- ❌ Il Bot non è "strategico": reclama sempre il massimo disponibile senza tattica
- ❌ Non può "bluffare" o ritardare una dichiarazione (non è un requisito attuale)

---

### Opzione B: Bot Strategico con Memoria

**Descrizione**: Il Bot mantiene uno stato interno tra i turni e può decidere di aspettare (es. avere la quaterna ma aspettare la cinquina prima di dichiarare).

**Pro**:
- ✅ Comportamento più "umano" e imprevedibile
- ✅ Potrebbe aumentare l'interesse del gioco nel lungo periodo

**Contro**:
- ❌ Complessità sproporzionata per questa fase del progetto
- ❌ Richiede estensioni significative all'architettura degli eventi
- ❌ Introduce rischi di inconsistenza (il Bot attende, ma nel frattempo qualcun altro prende il premio)

---

### Scelta Finale

Scelta **Opzione A: Bot Reattivo** perché è la soluzione proporzionata alla fase attuale del progetto, perfettamente integrabile con l'architettura esistente e priva di rischi architetturali. Il comportamento strategico potrà essere valutato in una versione futura come estensione modulare e opzionale.

---

## ✅ Design Freeze Checklist

- [x] Tutti gli scenari principali mappati (turno normale, reclamo, reclamo rigettato, tombola, premi multipli)
- [x] Stati del sistema chiari e completi
- [x] Flussi logici coprono tutti i casi d'uso principali
- [ ] Domande aperte risolte (3 domande ancora aperte — da chiudere prima della fase PLAN)
- [x] Interazione con le parti del gioco definita
- [x] Nessun buco logico evidente
- [x] Opzioni valutate e scelta finale motivata

**Stato**: DRAFT → da portare a DESIGN FREEZE dopo chiusura delle 3 domande aperte

**Next Step**: Chiudere le domande aperte, poi creare `PLAN_BOT_ATTIVO.md` con le decisioni implementative specifiche.

---

## 📝 Note di Brainstorming

- In futuro si potrebbe introdurre un "profilo di personalità" per ogni Bot (aggressivo, prudente, casuale) che determini la strategia di reclamo; l'architettura reattiva scelta oggi è compatibile con questa estensione futura
- Il sistema di logging del Bot si integra naturalmente con il sub-logger `prizes` già introdotto in v0.5.0; le azioni del Bot non richiedono nuove categorie di log
- La sezione `ComandiGiocatoreUmano` in `comandi_partita.py` è ancora un placeholder: lo sviluppo del Bot attivo potrà dare indicazioni utili su quali comandi esporre anche per il giocatore umano
- Verificare se `_passa_turno_core()` in `GiocatoreBase` è già sufficiente come base per il turno del Bot, o se è necessario un override in `GiocatoreAutomatico`
- Il file di diario potrebbe essere il punto di partenza per un futuro sistema di replay delle partite, ricostruendo la sequenza di azioni dei Bot

---

## 📚 Riferimenti Contestuali

### Feature Correlate
- **Sistema di eventi** (`bingo_game/events/eventi_partita.py`): `EventoFineTurno` e `ReclamoVittoria` sono già presenti e operativi; il Bot li utilizzerà senza modifiche strutturali
- **GiocatoreBase** (`bingo_game/players/giocatore_base.py`): `_passa_turno_core()` e attributo `reclamo_turno` sono già implementati; il Bot eredita questa logica
- **GiocatoreAutomatico** (`bingo_game/players/giocatore_automatico.py`): shell pronta per ospitare la nuova logica di introspezione e reclamo
- **GameController** (`bingo_game/game_controller.py`): `esegui_turno_sicuro()` gestisce già premi e tombola; verrà esteso in fase PLAN per processare i reclami provenienti dai Bot
- **Sistema di Logging** (`bingo_game/logging/`): Sub-logger `prizes` e `system` già operativi da v0.5.0; le azioni del Bot si integrano naturalmente

### Vincoli da Rispettare
- Il Bot deve essere trattato dal sistema esattamente come il giocatore umano: nessun canale privilegiato
- La logica di validazione dei premi rimane centralizzata nella Partita; il Bot non valida mai sé stesso
- Ogni azione rilevante del Bot deve essere loggata nel sistema di logging centralizzato
- Il sistema di feedback vocale per i reclami del Bot deve rispettare i principi di accessibilità già stabiliti nel progetto

---

## 🎯 Risultato Finale Atteso

Una volta implementato, il sistema garantirà:

✅ Il Bot segna i numeri estratti autonomamente, senza intervento umano (già implementato)  
✅ Il Bot valuta le proprie cartelle dopo ogni estrazione e identifica eventuali premi realizzati  
✅ Il Bot reclama il premio più alto disponibile tramite il sistema di eventi già esistente  
✅ La Partita valida ogni reclamo del Bot esattamente come quello del giocatore umano  
✅ L'utente percepisce le azioni del Bot tramite feedback vocale generato dalla Partita  
✅ Ogni azione rilevante del Bot è tracciata nel sistema di logging centralizzato  
✅ Il comportamento del Bot è modulare ed estendibile verso future strategie più complesse  

---

**Fine Design Document**
