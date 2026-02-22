# 🎨 Design Document - Tasti Rapidi TUI (Navigazione da Terminale)

> **FASE: CONCEPT & FLOW DESIGN**
> Nessuna decisione tecnica qui - solo logica e flussi concettuali
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-22
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

1. **Sistema** (estrattore automatico): Estrae numero 45, annuncia "Estratto: 45."

2. **Utente**: Naviga fino alla cella che contiene 45 con Frecce
   → **Sistema**: Annuncia contenuto di ogni cella durante la navigazione

3. **Utente**: Preme `Invio` sulla cella con 45
   → **Sistema**: Segna il numero 45 sulla Cartella 1, annuncia
   "Numero 45 segnato. Ambo a 1 numero."

4. **Sistema**: Verifica condizioni di vittoria (ambo, terno, tombola)
   → **Sistema**: Se condizione raggiunta, annuncia la vincita

**Punto di arrivo**: Numero segnato sulla cartella, stato aggiornato

**Cosa cambia**: Stato cartella aggiornato, contatori ambo/terno/tombola aggiornati

---

### Scenario 4: Annuncio Stato Cartella

**Punto di partenza**: Qualsiasi stato di partita

**Flusso**:

1. **Utente**: Preme `I` (info)
   → **Sistema**: Annuncia stato completo della cartella attiva:
   "Cartella 2. Numeri segnati: 3 di 15. Ambo: 1. Terno: 0. Tombola: 0."

2. **Utente**: Preme `T` (tabellone)
   → **Sistema**: Annuncia gli ultimi numeri estratti:
   "Ultimi estratti: 45, 12, 67, 3, 88."

**Punto di arrivo**: Utente informato sullo stato corrente

**Cosa cambia**: Nessuna modifica allo stato del gioco

---

### Scenario 5: Edge Case - Tasto senza Focus Cartella

**Cosa succede se**: Utente preme Freccia Giù senza aver prima selezionato una cartella

**Sistema dovrebbe**: Restituire messaggio di errore descrittivo:
"Nessuna cartella selezionata. Premi un numero da 1 a 3 per selezionare una cartella."

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

1. **Utente**: Preme `Q` o `ESC`
   → **Sistema**: Chiede conferma: "Vuoi uscire dalla partita? Premi S per confermare, N per annullare."

2. **Utente**: Preme `S`
   → **Sistema**: Termina la partita, torna al menu principale

**Punto di arrivo**: Utente torna al menu

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

#### Navigazione Cartelle

- **Tasto `1` / `2` / `3` (e oltre se più cartelle)**:
  - Fa cosa? Seleziona direttamente la cartella corrispondente al numero
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Cartella N selezionata."

- **Tasto PagGiù**:
  - Fa cosa? Sposta il focus alla cartella successiva
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Cartella N selezionata." oppure "Già sull'ultima cartella."

- **Tasto PagSu**:
  - Fa cosa? Sposta il focus alla cartella precedente
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: "Cartella N selezionata." oppure "Già sulla prima cartella."

#### Navigazione Righe e Colonne

- **Freccia Giù**:
  - Fa cosa? Sposta il focus alla riga successiva della cartella attiva
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "Riga N. Numeri: [contenuto riga]."

- **Freccia Su**:
  - Fa cosa? Sposta il focus alla riga precedente della cartella attiva
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: "Riga N. Numeri: [contenuto riga]."

- **Freccia Destra**:
  - Fa cosa? Sposta il focus alla colonna successiva della riga attiva
  - Quando disponibile? Quando una riga è selezionata
  - Feedback atteso: "Colonna N. Numero: [valore]."

- **Freccia Sinistra**:
  - Fa cosa? Sposta il focus alla colonna precedente della riga attiva
  - Quando disponibile? Quando una riga è selezionata
  - Feedback atteso: "Colonna N. Numero: [valore]."

#### Azioni di Gioco

- **Tasto `Invio`**:
  - Fa cosa? Segna il numero nella cella attualmente a fuoco
  - Quando disponibile? Quando una cella è selezionata
  - Feedback atteso: "Numero N segnato." oppure messaggio di errore

- **Tasto `I`**:
  - Fa cosa? Annuncia lo stato completo della cartella attiva
  - Quando disponibile? Quando una cartella è selezionata
  - Feedback atteso: riepilogo numeri segnati, ambo, terno, tombola

- **Tasto `T`**:
  - Fa cosa? Annuncia gli ultimi numeri estratti dal tabellone
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: lista ultimi estratti

- **Tasto `E`**:
  - Fa cosa? Avanza l'estrazione (turno automatico o manuale)
  - Quando disponibile? Quando è il turno di estrazione
  - Feedback atteso: "Estratto: N."

#### Uscita e Controllo

- **Tasto `Q` o `ESC`**:
  - Fa cosa? Avvia procedura di uscita dalla partita
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: richiesta conferma S/N

- **Tasto `H` o `?`**:
  - Fa cosa? Legge l'elenco dei comandi disponibili
  - Quando disponibile? Sempre durante la partita
  - Feedback atteso: lista tasti e relative azioni

### Feedback Sistema

- **Quando tasto non riconosciuto**: "Tasto non valido. Premi H per l'elenco dei comandi."
- **Quando azione non disponibile nel contesto**: "[Azione] non disponibile ora. [Motivo]."
- **Quando navigazione oltre il bordo**: "Già [prima/ultima] [riga/colonna/cartella]."
- **Quando numero già segnato**: "Numero N già segnato su questa cartella."
- **Quando nessuna cartella selezionata**: "Nessuna cartella selezionata. Premi 1, 2 o 3 per scegliere."

### Navigazione Concettuale

```
1. Utente avvia partita → game loop attivo
2. Utente preme '1' → Cartella 1 attiva
3. Utente preme Freccia Giù → Riga 1 attiva, NVDA legge contenuto
4. Utente preme Freccia Destra → Colonna 1 attiva, NVDA legge numero
5. Sistema estrae numero → NVDA legge "Estratto: N"
6. Utente naviga fino al numero estratto con Frecce
7. Utente preme Invio → numero segnato, NVDA legge conferma
8. Ciclo riparte dal punto 5
```

---

## 🤔 Domande & Decisioni

### Domande Aperte

- [ ] Il tasto `E` per l'estrazione è necessario o l'estrazione è sempre automatica?
- [ ] Quando si segna un numero con Invio, deve verificare che sia effettivamente estratto
  o si permette la marcatura libera?

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
- **GiocatoreUmano (`bingo_game/players/giocatore_umano.py`)**: Espone già tutti
  i metodi di navigazione focus necessari (imposta_focus_cartella,
  sposta_focus_riga_su_semplice, sposta_focus_riga_giu_semplice,
  sposta_focus_colonna_sinistra_semplice, sposta_focus_colonna_destra_semplice,
  vai_a_cartella_precedente, vai_a_cartella_successiva).
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

✅ Selezionare una cartella premendo il suo numero (1, 2, 3…) o con PagSu/PagGiù
✅ Navigare righe e colonne della cartella con i tasti freccia
✅ Ascoltare il contenuto di ogni cella letto da NVDA in tempo reale
✅ Segnare un numero estratto premendo Invio sulla cella corrispondente
✅ Consultare lo stato della cartella con il tasto I e il tabellone con il tasto T
✅ Uscire dalla partita in sicurezza con Q o ESC + conferma
✅ Giocare una partita completa da terminale senza mai digitare comandi testuali

---

**Fine Design Document**
