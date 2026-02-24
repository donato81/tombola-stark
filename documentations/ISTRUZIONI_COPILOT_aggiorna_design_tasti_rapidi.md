# 📋 Istruzioni per Copilot — Aggiornamento DESIGN_tasti-rapidi-tui.md

> **Scopo**: Allineare il file di design alla mappatura tasti completa e definitiva.
> **Data**: 2026-02-24
> **Preparato da**: Perplexity AI su richiesta di Donato81

---

## 🎯 Obiettivo

Devi aggiornare il file:

```
documentations/2 - project/DESIGN_tasti-rapidi-tui.md
```

La fonte di verità per questa operazione è **esclusivamente** il file:

```
documentations/mappatura_tasti_terminale.md
```

Leggi prima la mappatura per intero, poi aggiorna il design seguendo le istruzioni
punto per punto riportate qui sotto.

---

## 📌 Regole Generali (NON DEROGABILI)

1. **NON modificare** la struttura del documento (intestazioni, sezioni, ordine).
2. **NON toccare** le sezioni: Metadata, L'Idea in 3 Righe, Attori e Concetti,
   Relazioni Concettuali, Stati e Transizioni, Opzioni Considerate, Scelta Finale,
   Note di Brainstorming, Riferimenti Contestuali, Vincoli da Rispettare.
3. **NON modificare** alcun file `.py` del progetto.
4. **NON aggiungere** codice tecnico o snippet Python nel design document:
   questo è un documento concettuale, non tecnico.
5. Aggiorna il metadata: `Ultimo Aggiornamento: 2026-02-24`,
   `Reviewer: Copilot (mappatura tasti allineata)`.

---

## ✏️ Modifiche da Eseguire — Passo per Passo

### PASSO 1 — Aggiorna la sezione "Mappatura Tasti Rapidi"

Questa è la sezione più importante. Sostituisci completamente il contenuto
della sezione `### Mappatura Tasti Rapidi` con i 10 gruppi descritti nel file
`documentations/mappatura_tasti_terminale.md`.

Per ogni gruppo, mantieni questo formato già presente nel documento:

```
- **Tasto `X`**:
  - Fa cosa? [descrizione azione]
  - Metodo chiamato: [nome_metodo_esatto]
  - Quando disponibile? [contesto]
  - Feedback atteso: "[testo che NVDA leggerà]"
  - Perché questo tasto? [motivazione ergonomica se presente nella mappatura]
```

Aggiungi il campo `Metodo chiamato` che nella versione attuale manca.
Usa esattamente i nomi dei metodi scritti nel file `mappatura_tasti_terminale.md`,
senza inventarne di nuovi e senza modificarli.

I 10 gruppi da copiare fedelmente sono:
- Gruppo 1: Navigazione riga semplice (Freccia Su, Freccia Giù)
- Gruppo 2: Navigazione riga avanzata (A, Z)
- Gruppo 3: Navigazione colonna semplice (Freccia Sinistra, Freccia Destra)
- Gruppo 4: Navigazione colonna avanzata (Q, W)
- Gruppo 5: Salto diretto a riga o colonna specifica (R, C) — con prompt numerico
- Gruppo 6: Gestione e navigazione cartelle (PagGiù, PagSu, tasti 1-6)
- Gruppo 7: Visualizzazione cartella corrente e tutte le cartelle (D, F, G, H)
- Gruppo 8: Consultazione del tabellone (U, I, O, L, E, N)
- Gruppo 9: Orientamento e stato corrente (?)
- Gruppo 10: Azioni di gioco (S, V, P, X)

---

### PASSO 2 — Correggi le contraddizioni sui tasti Q e X

Nel design attuale esiste questa contraddizione:
- `Q` era il tasto di uscita → ora `Q` è navigazione colonna avanzata sinistra
- Il tasto di uscita passa a `X`

Esegui queste due modifiche ovunque nel documento compaiano:

| Testo attuale da cercare | Testo corretto da sostituire |
|--------------------------|------------------------------|
| `Q` o `ESC` come tasto uscita | `X` come tasto uscita |
| `Premi Q per uscire` | `Premi X per uscire` |

Controlla **tutti gli scenari** e la **sezione Feedback Sistema** per questa sostituzione.

---

### PASSO 3 — Aggiorna lo Scenario 4 (Annuncio Stato)

Lo Scenario 4 attuale descrive:
- Tasto `I` → riepilogo cartella attiva
- Tasto `T` → ultimi numeri estratti

Nella nuova mappatura:
- Tasto `I` → ultimi 5 numeri estratti (`visualizza_ultimi_numeri_estratti`)
- Tasto `F` → riepilogo cartella avanzato (`visualizza_cartella_corrente_avanzata`)
- Tasto `T` è sparito

Aggiorna lo Scenario 4 sostituendo il flusso con questi due passi corretti.
Rinomina lo scenario in: **"Scenario 4: Consultazione Stato Cartella e Tabellone"**.

---

### PASSO 4 — Aggiorna lo Scenario 3 (Segnare un Numero)

Lo Scenario 3 attuale dice che l'utente segna un numero premendo `Invio`
sulla cella a fuoco.

Nella nuova mappatura la segnatura avviene con il tasto `S`, che dopo la
pressione chiede un prompt con il numero da segnare.

Aggiorna il passo 3 dello scenario così:

```
Utente preme S
→ Sistema chiede: "Numero da segnare:"
→ Utente digita il numero e preme Invio
→ Sistema segna il numero sulla cartella in focus, annuncia conferma
```

Nota da aggiungere nello scenario: la segnatura verifica sempre che il numero
sia già stato estratto (protezione anti-baro già implementata nel dominio).

---

### PASSO 5 — Aggiorna lo Scenario 7 (Uscita)

Lo Scenario 7 attuale indica `Q` o `ESC` come tasto uscita.
Sostituisci con `X` come da nuova mappatura.

---

### PASSO 6 — Aggiungi lo Scenario 8 (Dichiarazione Vittoria)

Aggiungi un nuovo scenario dopo lo Scenario 7, con questo contenuto:

**Scenario 8: Dichiarazione Vittoria**

Punto di partenza: Partita in corso, giocatore ritiene di aver raggiunto una vincita.

Flusso:
1. Utente preme `V`
   → Sistema chiede il tipo di vincita: "Tipo di vincita (ambo/terno/quaterna/cinquina/tombola):"
2. Utente digita il tipo e preme Invio
   → Sistema verifica la condizione di vittoria sulla cartella in focus
   → Se valida: annuncia la vincita e aggiorna lo stato
   → Se non valida: annuncia il motivo del rifiuto

Punto di arrivo: Vincita registrata o rifiutata con spiegazione.

---

### PASSO 7 — Aggiorna lo Scenario 5 (Edge Case - No Focus Cartella)

Il messaggio di errore attuale dice:
`"Nessuna cartella selezionata. Premi un numero da 1 a 3 per selezionare una cartella."`

Correggi con:
`"Nessuna cartella selezionata. Premi un numero da 1 a 6 per selezionare una cartella."`

(il limite è 6, non 3, come da mappatura e dal dominio)

---

### PASSO 8 — Aggiungi le tre decisioni mancanti nella sezione "Decisioni Prese"

Aggiungi questi tre punti alla lista delle decisioni già presenti:

**Decisione A — Segnatura con tasto S e prompt:**
La segnatura di un numero avviene tramite il tasto `S` seguito da un prompt
numerico. Non si usa `Invio` sulla cella navigata. Questa scelta evita
segnature accidentali durante la navigazione e mantiene un gesto esplicito
per un'azione irreversibile.

**Decisione B — Metodi avanzati inclusi nella v0.10.0:**
Per navigazione riga e colonna sono previsti sia i metodi semplici (frecce)
sia i metodi avanzati (A/Z per righe, Q/W per colonne). I metodi avanzati
leggono anche lo stato di segnatura di ogni cella, informazione essenziale
per un utente NVDA che naviga senza vedere la cartella.

**Decisione C — Estrazione automatica a inizio turno:**
L'estrazione del numero avviene automaticamente all'inizio di ogni turno,
prima che il sistema aspetti il tasto dell'utente. Il ciclo di ogni turno è:
estrai numero → annuncia a NVDA → attendi tasto utente. Il tasto `P` avanza
al turno successivo e innesca la prossima estrazione automatica.

---

### PASSO 9 — Chiudi la domanda aperta sulla segnatura

Nella sezione "Domande Aperte" c'è questa domanda ancora aperta:

```
- [ ] Quando si segna un numero con Invio, deve verificare che sia effettivamente
  estratto o si permette la marcatura libera?
```

Sostituiscila con questa voce chiusa:

```
- [x] RISOLTA — La segnatura tramite tasto S verifica sempre che il numero sia
  già stato estratto (protezione anti-baro implementata nel metodo
  segna_numero_manuale del dominio). Non è possibile segnare numeri non estratti.
```

---

### PASSO 10 — Aggiorna la sezione "Navigazione Concettuale"

Sostituisci il diagramma testuale attuale con questo flusso aggiornato che
riflette la nuova mappatura:

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

### PASSO 11 — Aggiorna la sezione "Risultato Finale Atteso"

Sostituisci i bullet point finali con questa versione aggiornata:

```
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
```

---

### PASSO 12 — Aggiorna i Riferimenti Contestuali

Nella sezione "Feature Correlate", aggiorna il paragrafo su `GiocatoreUmano`
per includere tutti i metodi ora referenziati dalla nuova mappatura:

```
GiocatoreUmano espone tutti i metodi di navigazione e azione necessari:
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
```

---

## ✅ Verifica Finale Prima di Salvare

Prima di salvare il file, controlla che:

- [ ] Non esista più nessun riferimento a `Q` come tasto uscita
- [ ] Non esista più nessun riferimento a `T` come tasto tabellone
- [ ] Non esista più `Invio` come tasto di segnatura autonoma
- [ ] Tutti e 10 i gruppi della mappatura siano rappresentati nella sezione tasti
- [ ] La domanda aperta sulla segnatura sia marcata come risolta
- [ ] Le tre nuove decisioni (A, B, C) siano presenti nella sezione Decisioni Prese
- [ ] Lo Scenario 8 (Vittoria) sia aggiunto
- [ ] Il metadata riporti la data di oggi e il reviewer corretto

---

*Fine istruzioni — fonte di verità: `documentations/mappatura_tasti_terminale.md`*
