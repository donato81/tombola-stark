---
status: REVIEWED
feature: refactor-confini-partita-gamecontroller
agent: Agent-Design
date: 2026-03-24
---

# Design Document - Refactor confini Partita / GameController

> FASE: DESIGN ARCHITETTURALE
> Refactor incrementale, senza introdurre nuove factory o una riscrittura dei layer.

---

## Metadata

- Data inizio: 2026-03-24
- Stato: REVIEWED
- Versione target: refactor interno branch corrente
- Autore: GitHub Copilot + donato81

---

## Contesto

Il repository contiene gia' un dominio di gioco funzionante, una TUI operativa e un controller applicativo che fa da punto di accesso per l'interfaccia. Nel tempo, pero', alcune responsabilita' si sono distribuite in modo poco netto tra Partita e GameController.

L'obiettivo di questo design non e' ripensare tutta l'architettura, ma chiarire i confini tra game logic e orchestration con un refactor piccolo, progressivo e testabile.

---

## Problema attuale

Le responsabilita' di dominio e di coordinamento applicativo sono oggi parzialmente mescolate:

- Partita e' gia' owner di stato, estrazioni, premi e flusso del turno.
- GameController mantiene anche stato di sessione aggiuntivo (`_turno_corrente`, `_premi_totali`, `_partita_terminata_logged`).
- GameController valida e ristruttura in modo difensivo parte dei dati gia' prodotti dal dominio.
- La logica di post-processing del turno vive in parte nel controller, anche quando riguarda il significato del risultato di gioco.
- La TUI dipende dal controller, quindi qualsiasi refactor deve preservare quel punto di accesso.

Il rischio e' avere due sorgenti di verita' parziali: una nel dominio e una nel controller.

---

## Obiettivi

1. Rendere Partita owner esplicito della game logic e dello stato di gioco.
2. Ridurre il controller a facade applicativa e orchestration.
3. Conservare la TUI come consumatore del controller, senza import diretti del domain layer.
4. Evitare breaking change ampie nelle API pubbliche gia' usate da TUI e test.
5. Preparare il terreno a refactor successivi piu' piccoli e mirati.

---

## Non obiettivi

- Introdurre una nuova factory separata o un service container.
- Riscrivere la TUI.
- Cambiare la struttura generale del package `bingo_game`.
- Spostare subito tutto il logging fuori dal controller.
- Rifare integralmente i test esistenti.

---

## Stato attuale osservato

### Partita

Partita gestisce gia':

- roster giocatori
- stato partita (`non_iniziata`, `in_corso`, `terminata`)
- estrazione del numero
- aggiornamento giocatori
- verifica premi
- esecuzione del turno
- produzione di uno stato completo della partita

### GameController

GameController gestisce oggi:

- creazione di tabellone, giocatori, cartelle e partita standard
- avvio sicuro della partita
- esecuzione sicura del turno con logging, controllo errori e normalizzazione output
- query di stato sintetico per la UI
- verifica terminazione partita
- recupero del giocatore umano per isolamento TUI

### Punto critico

Il confine corretto non e' spostare la creazione fuori dal controller, ma distinguere meglio:

- cosa appartiene al dominio
- cosa appartiene alla traduzione applicativa verso UI/logging

---

## Decisione architetturale approvata

La decisione approvata e' mantenere GameController come factory della partita standard e come facade applicativa.

Quindi:

- GameController continua a creare oggetti e a offrire helper ad alto livello alla TUI.
- Partita diventa il punto unico di verita' per transizioni, risultati di gioco e stato del turno.
- Il controller smette progressivamente di trattenere logica che interpreta il dominio oltre il necessario.

Questa scelta e' la piu' adatta a un primo collaudo del workflow agenti perche' limita il perimetro del cambiamento.

---

## Responsabilita' future di Partita

Partita deve essere responsabile di:

- stato della partita e relative transizioni
- ultimo numero estratto
- premi assegnati e loro progressione
- risultato semantico del turno
- informazioni di dominio coerenti e complete per i layer superiori

Partita non deve occuparsi di:

- stdout
- formattazione messaggi utente
- logging di presentazione
- policy UI/TUI

---

## Responsabilita' future di GameController

GameController deve essere responsabile di:

- composizione iniziale della partita standard
- orchestrazione applicativa tra TUI e dominio
- gestione centralizzata delle eccezioni pubbliche verso l'interfaccia
- logging tecnico e di alto livello
- adattamento dei dati di dominio in una forma comoda per la UI, senza ridefinirne il significato

GameController non deve diventare owner di:

- stato del turno separato da quello di Partita
- conteggi che possono divergere dal dominio
- logica di assegnazione o interpretazione dei premi
- decisioni di dominio duplicate

---

## Impatto su TUI

La TUI non cambia il proprio punto di accesso: continua a consumare GameController.

Impatto atteso:

- nessuna modifica concettuale al layer presentation
- possibile semplificazione futura del codice TUI grazie a output controller piu' coerenti
- nessun import nuovo dal dominio nella TUI

---

## Impatto su test

I test dovranno concentrarsi su due fronti:

1. Partita come source of truth del risultato del turno.
2. GameController come adapter/facade che non altera il significato del dato di dominio.

Le regressioni piu' probabili riguardano:

- dizionario di ritorno di `esegui_turno_sicuro`
- query di stato in `ottieni_stato_sintetico`
- compatibilita' con i test esistenti di controller e partita

---

## Strategia di migrazione incrementale

### Passo 1

Mappare con precisione quali campi e quali decisioni del turno sono realmente calcolati in Partita e quali sono ancora arricchiti dal controller.

### Passo 2

Ridurre i duplicati di stato nel controller dove il dato e' gia' disponibile o derivabile dal dominio senza ambiguita'.

### Passo 3

Stabilizzare un contratto minimo e chiaro tra `Partita.esegui_turno()` e `GameController.esegui_turno_sicuro()`.

### Passo 4

Aggiornare o aggiungere test mirati che dimostrino che il controller orchestra ma non ridefinisce la semantica di gioco.

### Passo 5

Solo dopo la stabilizzazione, valutare ulteriori pulizie interne al controller.

---

## Rischi

1. Spostare troppo presto logica dal controller al dominio senza test di supporto.
2. Rompere il formato dei dati attesi dalla TUI.
3. Introdurre refactor troppo ampi per un primo collaudo del framework agenti.
4. Confondere logging tecnico con logica di business.

---

## Criteri di completamento

Il refactor si considera completato quando:

- il confine tra dominio e controller e' documentato e attuato nei punti minimi concordati
- Partita resta owner esplicito di stato e risultato di gioco
- GameController continua a fare orchestration senza duplicare decisioni di dominio chiave
- TUI continua a funzionare senza conoscere classi del domain layer
- i test esistenti rilevanti passano e i nuovi test di regressione coprono il nuovo confine

---

## Esito atteso per la fase successiva

La fase di planning deve tradurre questo design in un piano atomico, con una prima iterazione molto contenuta:

- chiarimento contratti Partita/Controller
- rimozione o riduzione di uno o pochi punti di duplicazione reale
- test di protezione prima e dopo il refactor
