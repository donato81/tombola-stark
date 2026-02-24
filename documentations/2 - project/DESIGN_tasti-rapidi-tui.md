# 🎨 Design Document - Tasti Rapidi TUI (Navigazione da Terminale)

> **FASE: CONCEPT & FLOW DESIGN**
> Nessuna decisione tecnica qui - solo logica e flussi concettuali
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-22
- **Ultimo Aggiornamento**: 2026-02-24
- **Reviewer**: Copilot (mappatura tasti allineata)
- **Stato**: FROZEN
- **Versione Target**: v0.10.0
- **Autore**: AI Assistant + Donato81

---

## 💡 L'Idea in 3 Righe

Vogliamo che l'utente possa navigare la partita di tombola interamente da tastiera
con tasti rapidi intuitivi (frecce, PagSu/PagGiù, tasti numerici), senza dover
digitare comandi testuali seguiti da Invio. Questo elimina la frizione attuale
tra l'intenzione dell'utente e l'azione del sistema, rendendo il gioco fluido
e accessibile per un utente NVDA su Windows 11.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Utente**: Gioca a tombola da terminale, naviga cartelle e celle, segna numeri estratti
- **Sistema TUI**: Legge i tasti premuti, interpreta il comando corrispondente, delega al dominio
- **Game Controller**: Unico punto di accesso al dominio dalla TUI; esegue le azioni richieste
- **GiocatoreUmano**: Entità di dominio che gestisce il focus e le operazioni sulle cartelle
- **TerminalRenderer**: Produce l'output testuale verso il terminale (letto da NVDA)

### Concetti Chiave (Cosa Esiste nel Sistema)

#### Focus Cartella
- **Cos'è**: La cartella attualmente "attiva" su cui l'utente sta operando
- **Stati possibili**: Non impostato (None), Impostato (cartella 1..N)
- **Proprietà**: Deve essere impostato prima di poter navigare righe/colonne o segnare numeri

#### Focus Riga
- **Cos'è**: La riga corrente all'interno della cartella attiva
- **Stati possibili**: Non impostato (None), Impostata (riga 1..3)
- **Proprietà**: Dipende dal Focus Cartella; si azzera al cambio cartella

#### Focus Colonna
- **Cos'è**: La colonna corrente all'interno della riga attiva
- **Stati possibili**: Non impostata (None), Impostata (colonna 1..9)
- **Proprietà**: Dipende dal Focus Riga; si azzera al cambio riga

#### Tasto Rapido
- **Cos'è**: Un singolo tasto (o coppia di byte per tasti speciali) che mappa a un comando
- **Stati possibili**: Tasto normale (1 byte), Tasto speciale (2 byte: prefisso + codice)
- **Proprietà**: Catturato con msvcrt senza attendere Invio

#### Comando
- **Cos'è**: L'azione logica che il tasto rapido esegue sul dominio
- **Stati possibili**: Navigazione (cambia focus senza modificare stato), Azione (modifica stato)
- **Proprietà**: Ogni comando produce sempre un feedback testuale verso il terminale

### Relazioni Concettuali

```
Utente preme tasto
  ↓
Sistema TUI legge byte (1 o 2)
  ↓
TUI Commander mappa tasto → Comando
  ↓
Game Controller esegue Comando sul dominio
  ↓
GiocatoreUmano modifica Focus / stato cartelle
  ↓
EsitoAzione ritorna al Commander
  ↓
TerminalRenderer stampa feedback
  ↓
NVDA legge il feedback all'utente
```

---

## 🎬 Scenari & Flussi

### Scenario 1: Navigazione tra Cartelle

**Punto di partenza**: Partita avviata, nessuna cartella selezionata

**Flusso**:

1. **Utente**: Preme il tasto `1`
   → **Sistema**: Imposta focus su Cartella 1, annuncia "Cartella 1 selezionata."

2. **Utente**: Preme il tasto `2`
   → **Sistema**: Sposta focus su Cartella 2, annuncia "Cartella 2 selezionata."

3. **Utente**: Preme PagGiù
   → **Sistema**: Sposta focus alla cartella successiva (es. Cartella 3), annuncia "Cartella 3 selezionata."

4. **Utente**: Preme PagSu
   → **Sistema**: Torna alla cartella precedente (es. Cartella 2), annuncia "Cartella 2 selezionata."

**Punto di arrivo**: Focus impostato su una cartella specifica

**Cosa cambia**: Focus Cartella aggiornato, Focus Riga e Focus Colonna azzerati

---

### Scenario 2: Navigazione all'interno di una Cartella

**Punto di partenza**: Cartella 1 selezionata, nessuna riga/colonna attiva

**Flusso**:

1. **Utente**: Preme Freccia Giù
   → **Sistema**: Imposta focus su Riga 1 della Cartella 1, annuncia
   "Riga 1. Numeri: 5, 0, 23, 0, 45, 0, 67, 0, 88."

2. **Utente**: Preme Freccia Giù di nuovo
   → **Sistema**: Sposta focus su Riga 2, annuncia contenuto riga 2

3. **Utente**: Preme Freccia Destra
   → **Sistema**: Imposta focus su Colonna 1 della Riga 2, annuncia
   "Colonna 1. Numero: 12."

4. **Utente**: Preme Freccia Destra di nuovo
   → **Sistema**: Sposta focus su Colonna 2, annuncia contenuto colonna 2

5. **Utente**: Preme Freccia Sinistra
   → **Sistema**: Torna a Colonna 1, annuncia contenuto colonna 1

6. **Utente**: Preme Freccia Su
   → **Sistema**: Torna a Riga 1, azzera Focus Colonna, annuncia contenuto riga 1

**Punto di arrivo**: Utente ha navigato righe e colonne della cartella

**Cosa cambia**: Focus Riga e Focus Colonna aggiornati

---

### Scenario 3: Segnare un Numero Estratto

**Punto di partenza**: Cartella 1 selezionata, focus su Riga 2, Colonna 3

**Flusso**:

1. **Sistema**: Estrae automaticamente numero 45, annuncia "Estratto: 45."

2. **Utente**: Naviga fino alla cella che contiene 45 con Frecce
   → **Sistema**: Annuncia contenuto di ogni cella durante la navigazione

3. **Utente**: Preme `S`
   → **Sistema**: Chiede: "Numero da segnare:"
   → **Utente**: Digita il numero e preme Invio
   → **Sistema**: Segna il numero sulla cartella in focus, annuncia
   "Numero 45 segnato. Ambo a 1 numero."

**Nota**: La segnatura verifica sempre che il numero sia già stato estratto (protezione anti-baro già implementata nel dominio).

4. **Sistema**: Verifica condizioni di vittoria (ambo, terno, tombola)
   → **Sistema**: Se condizione raggiunta, annuncia la vincita

**Punto di arrivo**: Numero segnato sulla cartella, stato aggiornato

**Cosa cambia**: Stato cartella aggiornato, contatori ambo/terno/tombola aggiornati

---

### Scenario 4: Consultazione Stato Cartella e Tabellone

**Punto di partenza**: Qualsiasi stato di partita

**Flusso**:

1. **Utente**: Preme `I`
   → **Sistema**: Annuncia gli ultimi cinque numeri estratti in ordine di estrazione:
   "Ultimi estratti: 45, 12, 67, 3, 88."

2. **Utente**: Preme `F`
   → **Sistema**: Annuncia riepilogo cartella avanzato con indicazione numeri segnati,
   riepiloghi per riga e totale complessivo della cartella in focus.

**Punto di arrivo**: Utente informato sullo stato corrente

**Cosa cambia**: Nessuna modifica allo stato del gioco

---

### Scenario 5: Edge Case - Tasto senza Focus Cartella

**Cosa succede se**: Utente preme Freccia Giù senza aver prima selezionato una cartella

**Sistema dovrebbe**: Restituire messaggio di errore descrittivo:
"Nessuna cartella selezionata. Premi un numero da 1 a 6 per selezionare una cartella."

---

### Scenario 6: Edge Case - Navigazione oltre i Bordi

**Cosa succede se**: Utente preme Freccia Giù quando è già sull'ultima riga

**Sistema dovrebbe**: Non modificare il focus, annunciare:
"Già sull'ultima riga della cartella."

**Cosa succede se**: Utente preme PagGiù sull'ultima cartella

**Sistema dovrebbe**: Non modificare il focus, annunciare:
"Già sull'ultima cartella."

---

### Scenario 7: Uscita e Pausa

**Punto di partenza**: Partita in corso

**Flusso**:

1. **Utente**: Preme `X`
   → **Sistema**: Chiede conferma: "Vuoi uscire dalla partita? Premi S per confermare, N per annullare."

2. **Utente**: Preme `S`
   → **Sistema**: Termina la partita, torna al menu principale

**Punto di arrivo**: Utente torna al menu

---

### Scenario 8: Dichiarazione Vittoria

**Punto di partenza**: Partita in corso, giocatore ritiene di aver raggiunto una vincita

**Flusso**:

1. **Utente**: Preme `V`
   → **Sistema**: Chiede il tipo di vincita: "Tipo di vincita (ambo/terno/quaterna/cinquina/tombola):"

2. **Utente**: Digita il tipo e preme Invio
   → **Sistema**: Verifica la condizione di vittoria sulla cartella in focus
   → Se valida: annuncia la vincita e aggiorna lo stato
   → Se non valida: annuncia il motivo del rifiuto

**Punto di arrivo**: Vincita registrata o rifiutata con spiegazione

---

## 🔀 Stati e Transizioni

### Stati del Sistema (Game Loop)

#### Stato A: Attesa Tasto
- **Descrizione**: Il game loop è in attesa che l'utente prema un tasto
- **Può passare a**: Elaborazione Comando
- **Trigger**: Utente preme qualsiasi tasto

#### Stato B: Elaborazione Comando
- **Descrizione**: Il sistema ha letto il tasto e sta eseguendo il comando corrispondente
- **Può passare a**: Attesa Tasto, Attesa Conferma
- **Trigger**: Comando completato o comando che richiede conferma (es. uscita)

#### Stato C: Attesa Conferma
- **Descrizione**: Il sistema attende una risposta S/N dall'utente
- **Può passare a**: Attesa Tasto (se N), Fine Partita (se S)
- **Trigger**: Utente preme S o N

#### Stato D: Fine Partita
- **Descrizione**: La partita è terminata (vittoria o uscita volontaria)
- **Può passare a**: Menu Principale
- **Trigger**: Condizione di vittoria raggiunta o conferma uscita

### Diagramma Stati (ASCII)

```
[Avvio Partita]
      ↓
[Attesa Tasto] ←──────────────────────────┐
      ↓ (tasto premuto)                   │
[Elaborazione Comando]                    │
      ↓ ok                                │ (completato)
[TerminalRenderer stampa feedback] ───────┘
      ↓ (comando = uscita)
[Attesa Conferma]
      ↓ S                ↓ N
[Fine Partita]    [Attesa Tasto]
      ↓
[Menu Principale]
```

---

## 🎮 Interazione Utente (UX Concettuale)

### Mappatura Tasti Rapidi

#### Gruppo 1 — Navigazione riga semplice

- **Tasto `Freccia Su`**:
  - Fa cosa? Sposta il cursore alla riga precedente e legge i numeri grezzi della riga
  - Metodo chiamato: sposta_focus_riga_su_semplice
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "Riga N. Numeri: [contenuto riga]."

- **Tasto `Freccia Giù`**:
  - Fa cosa? Sposta il cursore alla riga successiva e legge i numeri grezzi della riga
  - Metodo chiamato: sposta_focus_riga_giu_semplice
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "Riga N. Numeri: [contenuto riga]."

#### Gruppo 2 — Navigazione riga avanzata

- **Tasto `A`**:
  - Fa cosa? Sale alla riga precedente con analisi completa: numeri segnati, numeri mancanti e stato della vincita
  - Metodo chiamato: sposta_focus_riga_su_avanzata
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "[riga con analisi completa del contenuto]"
  - Perché questo tasto? Si trova in colonna verticale sulla tastiera italiana e risulta intuitivo insieme a Z

- **Tasto `Z`**:
  - Fa cosa? Scende alla riga successiva con analisi completa: numeri segnati, numeri mancanti e stato della vincita
  - Metodo chiamato: sposta_focus_riga_giu_avanzata
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "[riga con analisi completa del contenuto]"
  - Perché questo tasto? Si trova in colonna verticale con A sulla tastiera italiana, intuitivi come coppia su/giù

#### Gruppo 3 — Navigazione colonna semplice

- **Tasto `Freccia Sinistra`**:
  - Fa cosa? Sposta il cursore alla colonna precedente e legge il numero della singola cella
  - Metodo chiamato: sposta_focus_colonna_sinistra
  - Quando disponibile? Quando una riga è selezionata
  - Feedback atteso: "Colonna N. Numero: [valore]."

- **Tasto `Freccia Destra`**:
  - Fa cosa? Sposta il cursore alla colonna successiva e legge il numero della singola cella
  - Metodo chiamato: sposta_focus_colonna_destra
  - Quando disponibile? Quando una riga è selezionata
  - Feedback atteso: "Colonna N. Numero: [valore]."

#### Gruppo 4 — Navigazione colonna avanzata

- **Tasto `Q`**:
  - Fa cosa? Va alla colonna precedente con analisi verticale completa della colonna
  - Metodo chiamato: sposta_focus_colonna_sinistra_avanzata
  - Quando disponibile? Quando una riga è selezionata
  - Feedback atteso: "[analisi verticale completa della colonna]"
  - Perché questo tasto? È il primo tasto in alto a sinistra della tastiera, facile da trovare senza guardare

- **Tasto `W`**:
  - Fa cosa? Va alla colonna successiva con analisi verticale completa della colonna
  - Metodo chiamato: sposta_focus_colonna_destra_avanzata
  - Quando disponibile? Quando una riga è selezionata
  - Feedback atteso: "[analisi verticale completa della colonna]"
  - Perché questo tasto? È il secondo tasto in alto a sinistra dopo Q, facile da trovare senza guardare

#### Gruppo 5 — Salto diretto a riga o colonna specifica

- **Tasto `R`**:
  - Fa cosa? Chiede il numero di riga da raggiungere (1-3), salta direttamente a quella riga e mostra l'analisi avanzata
  - Metodo chiamato: vai_a_riga_avanzata
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "[prompt numerico] → [analisi avanzata riga]"
  - Perché questo tasto? R come iniziale di Riga

- **Tasto `C`**:
  - Fa cosa? Chiede il numero di colonna da raggiungere (1-9), salta direttamente a quella colonna e mostra l'analisi avanzata
  - Metodo chiamato: vai_a_colonna_avanzata
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "[prompt numerico] → [analisi avanzata colonna]"
  - Perché questo tasto? C come iniziale di Colonna

#### Gruppo 6 — Gestione e navigazione cartelle

- **Tasto `PagGiù`**:
  - Fa cosa? Avanza alla cartella successiva e legge immediatamente il riepilogo con i numeri mancanti ai vari premi
  - Metodo chiamato: riepilogo_cartella_successiva
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Cartella N selezionata. [riepilogo premi]"

- **Tasto `PagSu`**:
  - Fa cosa? Torna alla cartella precedente con lo stesso riepilogo
  - Metodo chiamato: riepilogo_cartella_precedente
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Cartella N selezionata. [riepilogo premi]"

- **Tasti `1` / `2` / `3` / `4` / `5` / `6`**:
  - Fa cosa? Salta direttamente alla cartella corrispondente al numero e ascolta subito lo stato di quella cartella
  - Metodo chiamato: imposta_focus_cartella + riepilogo_cartella_corrente
  - Quando disponibile? Sempre durante la partita (fino al numero di cartelle possedute)
  - Feedback atteso: "Cartella N selezionata. [riepilogo stato]"

#### Gruppo 7 — Visualizzazione cartella corrente e tutte le cartelle

- **Tasto `D`**:
  - Fa cosa? Mostra tutti i numeri della cartella in focus nella forma grezza, senza indicare lo stato di segnazione
  - Metodo chiamato: visualizza_cartella_corrente_semplice
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "[tutti i numeri della cartella senza stato]"
  - Perché questo tasto? D come iniziale di Display

- **Tasto `F`**:
  - Fa cosa? Mostra la cartella in focus con indicazione dei numeri segnati, riepiloghi per riga e totale complessivo
  - Metodo chiamato: visualizza_cartella_corrente_avanzata
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "[cartella con analisi completa numeri segnati e riepiloghi]"
  - Perché questo tasto? F come Full display

- **Tasto `G`**:
  - Fa cosa? Mostra in sequenza tutte le cartelle del giocatore nella forma semplice
  - Metodo chiamato: visualizza_tutte_cartelle_semplice
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "[sequenza tutte le cartelle forma semplice]"
  - Perché questo tasto? G come iniziale di Globale

- **Tasto `H`**:
  - Fa cosa? Mostra tutte le cartelle con analisi avanzata completa di ogni riga e colonna
  - Metodo chiamato: visualizza_tutte_cartelle_avanzata
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "[tutte le cartelle con analisi completa]"
  - Perché questo tasto? Sulla stessa fila centrale dei tasti D, F, G, premibili comodamente con la mano destra

#### Gruppo 8 — Consultazione del tabellone

- **Tasto `U`**:
  - Fa cosa? Legge l'ultimo numero uscito nell'estrazione più recente
  - Metodo chiamato: comunica_ultimo_numero_estratto
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Ultimo estratto: N"
  - Perché questo tasto? U come iniziale di Ultimo

- **Tasto `I`**:
  - Fa cosa? Legge gli ultimi cinque numeri estratti in ordine di estrazione
  - Metodo chiamato: visualizza_ultimi_numeri_estratti
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Ultimi estratti: N1, N2, N3, N4, N5"
  - Perché questo tasto? I come "Indietro", per richiamare la cronologia recente

- **Tasto `O`**:
  - Fa cosa? Fornisce una panoramica completa del tabellone: numeri usciti, mancanti, percentuale avanzamento e ultimi estratti
  - Metodo chiamato: riepilogo_tabellone
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "[panoramica completa tabellone]"
  - Perché questo tasto? O come iniziale di Overview

- **Tasto `L`**:
  - Fa cosa? Legge la lista completa e ordinata di tutti i numeri usciti dall'inizio della partita
  - Metodo chiamato: lista_numeri_estratti
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "[lista completa numeri estratti ordinata]"
  - Perché questo tasto? L come iniziale di Lista

- **Tasto `E`**:
  - Fa cosa? Chiede quale numero verificare e risponde se quel numero è già stato estratto oppure no
  - Metodo chiamato: verifica_numero_estratto
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "[prompt numerico] → [numero estratto/non estratto]"
  - Perché questo tasto? E come iniziale di Estratto

- **Tasto `N`**:
  - Fa cosa? Chiede quale numero cercare e risponde in quali cartelle del giocatore si trova quel numero e se è già stato segnato
  - Metodo chiamato: cerca_numero_nelle_cartelle
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "[prompt numerico] → [posizione numero nelle cartelle]"
  - Perché questo tasto? N come iniziale di Numero

#### Gruppo 9 — Orientamento e stato corrente

- **Tasto `?`**:
  - Fa cosa? In qualsiasi momento dice in quale cartella, riga e colonna si trova il cursore
  - Metodo chiamato: stato_focus_corrente
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Focus: Cartella N, Riga N, Colonna N"
  - Perché questo tasto? È il comando di orientamento universale da usare quando si perde il filo della navigazione

#### Gruppo 10 — Azioni di gioco

- **Tasto `S`**:
  - Fa cosa? Chiede quale numero segnare sulla cartella in focus
  - Metodo chiamato: segna_numero_manuale
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "[prompt numerico] → [numero segnato/errore]"
  - Perché questo tasto? S come iniziale di Segna

- **Tasto `V`**:
  - Fa cosa? Chiede il tipo di vincita da dichiarare tra ambo, terno, quaterna, cinquina e tombola
  - Metodo chiamato: annuncia_vittoria
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "[prompt tipo vincita] → [vincita registrata/rifiutata]"
  - Perché questo tasto? V come iniziale di Vittoria

- **Tasto `P`**:
  - Fa cosa? Passa al turno successivo e avvia l'estrazione del numero successivo
  - Metodo chiamato: passa_turno (+ estrazione automatica)
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Estratto: N"
  - Perché questo tasto? P come iniziale di Prosegui

- **Tasto `X`**:
  - Fa cosa? Avvia la procedura di uscita dalla partita con richiesta di conferma esplicita
  - Metodo chiamato: [procedura uscita]
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Vuoi uscire dalla partita? Premi S per confermare, N per annullare."
  - Perché questo tasto? X come iniziale di eXit e per la sua posizione angolare sulla tastiera, difficile da premere per sbaglio

### Feedback Sistema

- **Quando tasto non riconosciuto**: "Tasto non valido. Premi H per l'elenco dei comandi."
- **Quando azione non disponibile nel contesto**: "[Azione] non disponibile ora. [Motivo]."
- **Quando navigazione oltre il bordo**: "Già [prima/ultima] [riga/colonna/cartella]."
- **Quando numero già segnato**: "Numero N già segnato su questa cartella."
- **Quando nessuna cartella selezionata**: "Nessuna cartella selezionata. Premi 1, 2, 3, 4, 5 o 6 per scegliere."

### Navigazione Concettuale

```
1. Utente avvia partita → game loop attivo
2. Sistema estrae automaticamente il primo numero → NVDA legge "Estratto: N"
3. Utente preme 1-6 → cartella selezionata, NVDA legge riepilogo
4. Utente preme Freccia Giù (o A) → riga attiva, NVDA legge contenuto
5. Utente preme Freccia Destra (o Q/W) → colonna attiva, NVDA legge numero
6. Utente preme S → digita numero → numero segnato, NVDA legge conferma
7. Utente preme P → turno successivo, sistema estrae nuovo numero
8. Ciclo riparte dal punto 2
```

---

## 🤔 Domande & Decisioni

### Domande Aperte

- [x] **RISOLTA — La segnatura tramite tasto S verifica sempre che il numero sia
  già stato estratto (protezione anti-baro implementata nel metodo
  segna_numero_manuale del dominio). Non è possibile segnare numeri non estratti.**

### Decisioni Prese

- ✅ **Tasti speciali letti con msvcrt a 2 byte**: Frecce e PagSu/PagGiù producono
  il prefisso `\xe0` seguito dal codice specifico. Il sistema legge sempre entrambi
  i byte prima di interpretare il comando.

- ✅ **Nessun Invio obbligatorio**: Tutti i comandi di navigazione e azione si
  attivano al singolo tasto. Solo le conferme esplicite (es. uscita) usano un
  secondo tasto S/N.

- ✅ **Separazione Commander dal Game Loop**: La logica di mappatura tasto→comando
  vive in un modulo dedicato (`tui_commander`), non nel game loop principale.
  Questo mantiene `tui_partita.py` pulito e testabile separatamente.

- ✅ **Nessun output visivo**: Nessuna tabella, nessun colore ANSI, nessun box
  ASCII. Ogni feedback è una riga di testo autonoma leggibile da NVDA.

- ✅ **Compatibilità futura con altri frontend**: Il Commander è un layer
  intercambiabile. In futuro un frontend web o GUI può sostituire il Commander
  senza toccare il dominio.

- ✅ **I numeri da 1 a 6 selezionano la cartella corrispondente**: Scelta coerente
  con il numero massimo di cartelle per giocatore nel dominio attuale.
  Se in futuro il numero massimo cambia, si aggiorna solo il Commander.

- ✅ **Decisione A — Segnatura con tasto S e prompt**: La segnatura di un numero 
  avviene tramite il tasto `S` seguito da un prompt numerico. Non si usa `Invio` 
  sulla cella navigata. Questa scelta evita segnature accidentali durante la 
  navigazione e mantiene un gesto esplicito per un'azione irreversibile.

- ✅ **Decisione B — Metodi avanzati inclusi nella v0.10.0**: Per navigazione 
  riga e colonna sono previsti sia i metodi semplici (frecce) sia i metodi 
  avanzati (A/Z per righe, Q/W per colonne). I metodi avanzati leggono anche 
  lo stato di segnatura di ogni cella, informazione essenziale per un utente 
  NVDA che naviga senza vedere la cartella.

- ✅ **Decisione C — Estrazione automatica a inizio turno**: L'estrazione del 
  numero avviene automaticamente all'inizio di ogni turno, prima che il sistema 
  aspetti il tasto dell'utente. Il ciclo di ogni turno è: estrai numero → 
  annuncia a NVDA → attendi tasto utente. Il tasto `P` avanza al turno successivo 
  e innesca la prossima estrazione automatica.

### Assunzioni

- L'utente opera su Windows 11 con terminale cmd.exe o Windows Terminal
- NVDA legge automaticamente l'output standard riga per riga senza chiamate speak()
- Il numero massimo di cartelle per giocatore non supera 6 durante la v0.10.0
- La libreria msvcrt è disponibile (Windows only, già nel progetto)
- Il dominio (`GiocatoreUmano`) espone già tutti i metodi di navigazione necessari

---

## 🎯 Opzioni Considerate

### Opzione A: Comandi Testuali (sistema attuale)

**Descrizione**: L'utente digita una stringa di comando (es. `c1`, `rs`, `rg`) e preme Invio.

**Pro**:
- ✅ Già implementato e funzionante
- ✅ Non richiede gestione byte speciali

**Contro**:
- ❌ Richiede Invio dopo ogni comando (frizione alta)
- ❌ L'utente deve ricordare i codici testuali
- ❌ Non naturale per la navigazione continua (su/giù/sinistra/destra)
- ❌ Difficile da usare con screen reader per navigazione veloce

---

### Opzione B: Tasti Rapidi con msvcrt (scelta adottata)

**Descrizione**: Ogni tasto (o coppia di byte) mappa direttamente a un comando.
Il game loop legge un tasto alla volta, senza attendere Invio.

**Pro**:
- ✅ Nessun Invio obbligatorio: ogni azione è immediata
- ✅ Tasti mnemonici e intuitivi (frecce per navigare, numeri per cartelle)
- ✅ Ideale per screen reader: feedback immediato dopo ogni tasto
- ✅ Separazione netta tra input (Commander) e logica (Controller)
- ✅ Facilmente estendibile con nuovi tasti senza toccare il dominio

**Contro**:
- ❌ Richiede gestione esplicita dei 2 byte per tasti speciali
- ❌ Windows only (msvcrt), ma il progetto è già Windows only

---

### Opzione C: Combinazione ibrida (comandi testuali + tasti rapidi)

**Descrizione**: Mantenere i comandi testuali esistenti affiancandoli ai tasti rapidi.

**Pro**:
- ✅ Retrocompatibilità totale

**Contro**:
- ❌ Doppia logica di input da mantenere
- ❌ Confusione per l'utente su quale modalità usare
- ❌ Complessità inutile: i comandi testuali diventano obsoleti

---

### Scelta Finale

Scelto **Opzione B: Tasti Rapidi con msvcrt** come sistema primario, eliminando
i comandi testuali esistenti. Motivazione:
- Il progetto è già Windows only, msvcrt non aggiunge dipendenze esterne
- L'utente NVDA beneficia massimamente del feedback immediato senza Invio
- La separazione Commander/GameLoop migliora la manutenibilità a lungo termine
- L'Opzione C (ibrida) non aggiunge valore reale e aumenta la complessità

---

## ✅ Design Freeze Checklist

Questo design è pronto per la fase tecnica (PLAN) quando:

- [x] Tutti gli scenari principali mappati (7 scenari inclusi edge case)
- [x] Stati del sistema chiari e completi (4 stati del game loop)
- [x] Flussi logici coprono tutti i casi d'uso
- [x] Domande aperte risolte o documentate
- [x] UX interaction definita (mappatura tasti, feedback, navigazione)
- [x] Nessun buco logico evidente
- [x] Opzioni valutate e scelta finale motivata

**Next Step**: Creare `documentations/3 - planning/PLAN_tasti-rapidi-tui_v0.10.0.md` con:
- Decisioni API e architettura (4 blocchi di implementazione)
- Struttura file da creare: `codici_tasti_tui.py`, `tui_commander.py`
- Modifiche a `tui_partita.py` e `bingo_game/ui/locales/it.py`
- Testing strategy dettagliata

---

## 📝 Note di Brainstorming

- In futuro: il Commander potrebbe essere sostituito da un input handler per
  interfaccia web (es. Flask + WebSocket) senza toccare il dominio
- Il pattern Commander è facilmente estendibile per aggiungere nuovi tasti
  in future versioni senza rischiare regressioni
- Possibile estensione futura: tasto `R` per ripetere l'ultimo messaggio
  (utile se NVDA non ha letto in tempo)
- Il file di localizzazione `it.py` deve contenere tutti i messaggi di errore
  e feedback in italiano, mai hardcoded nel Commander

---

## 📚 Riferimenti Contestuali

### Feature Correlate

- **Game Controller (`bingo_game/game_controller.py`)**: Unico punto di accesso
  al dominio dalla TUI. Il Commander chiama solo funzioni esposte dal Controller.
- **GiocatoreUmano (`bingo_game/players/giocatore_umano.py`)**: GiocatoreUmano espone tutti i metodi di navigazione e azione necessari:
  imposta_focus_cartella, riepilogo_cartella_corrente,
  riepilogo_cartella_precedente, riepilogo_cartella_successiva,
  sposta_focus_riga_su_semplice, sposta_focus_riga_giu_semplice,
  sposta_focus_riga_su_avanzata, sposta_focus_riga_giu_avanzata,
  sposta_focus_colonna_sinistra, sposta_focus_colonna_destra,
  sposta_focus_colonna_sinistra_avanzata, sposta_focus_colonna_destra_avanzata,
  vai_a_riga_avanzata, vai_a_colonna_avanzata,
  visualizza_cartella_corrente_semplice, visualizza_cartella_corrente_avanzata,
  visualizza_tutte_cartelle_semplice, visualizza_tutte_cartelle_avanzata,
  comunica_ultimo_numero_estratto, visualizza_ultimi_numeri_estratti,
  riepilogo_tabellone, lista_numeri_estratti,
  verifica_numero_estratto, cerca_numero_nelle_cartelle,
  stato_focus_corrente, segna_numero_manuale, annuncia_vittoria.
- **EsitoAzione (`bingo_game/events/`)**: Ogni operazione sul dominio ritorna
  EsitoAzione. Il Commander verifica sempre esito.ok prima di chiamare il renderer.
- **TerminalRenderer (`bingo_game/ui/tui/`)**: Produce l'output testuale.
  Il Commander non chiama mai print() direttamente.
- **Localizzazione (`bingo_game/ui/locales/it.py`)**: Tutti i messaggi di
  feedback e di errore risiedono qui.

### Vincoli da Rispettare

- Nessun import diretto del Domain dalla TUI (tutto passa per game_controller.py)
- Nessun print() fuori da TerminalRenderer e dalla funzione _stampa() di tui_partita.py
- Nessun carattere ASCII decorativo o colore ANSI nell'output
- Ogni messaggio deve essere su una riga separata, entro 120 caratteri
- I tasti speciali (frecce, PagSu/PagGiù) richiedono lettura a 2 byte con msvcrt
- EsitoAzione.ok deve essere verificato prima di accedere a EsitoAzione.evento

---

## 🎯 Risultato Finale Atteso (High-Level)

Una volta implementato, l'utente potrà:

✅ Selezionare una cartella premendo il suo numero (1-6) o con PagSu/PagGiù
✅ Navigare righe con frecce (lettura semplice) o con A/Z (lettura avanzata con stato segnatura)
✅ Navigare colonne con frecce (lettura semplice) o con Q/W (lettura avanzata verticale)
✅ Saltare direttamente a una riga (R) o colonna (C) specifica con prompt numerico
✅ Visualizzare la cartella corrente in modo semplice (D) o avanzato (F)
✅ Visualizzare tutte le cartelle in modo semplice (G) o avanzato (H)
✅ Consultare il tabellone: ultimo estratto (U), ultimi 5 (I), panoramica (O), lista completa (L)
✅ Verificare se un numero è stato estratto (E) o cercarlo nelle cartelle (N)
✅ Segnare un numero estratto con S + prompt (protezione anti-baro attiva)
✅ Dichiarare una vincita con V + tipo di vincita
✅ Avanzare al turno successivo e innescare la prossima estrazione con P
✅ Uscire dalla partita in sicurezza con X + conferma
✅ Sapere sempre dove si trova il cursore premendo ?
✅ Giocare una partita completa da terminale senza mai digitare comandi testuali

---

**Fine Design Document**
