## Metadati

tipo: report_diagnostica
titolo: Diagnosi Ciclo di Turno V2 — stato di avanzamento e problemi rilevati
data: 2026-04-01
agente: Agent-Analyze
piano_riferimento: docs/3 - coding plan/PLAN_CICLO_TURNO_V2.md

---

## Premessa

Questo documento descrive in modo chiaro e senza tecnicismi lo stato
attuale del progetto rispetto al piano del Ciclo di Turno V2.
L'obiettivo è capire cosa funziona già, cosa manca e quali problemi
impediscono alla partita di girare correttamente secondo il ciclo
desiderato: estrazione, azione giocatori, verifica premi, pausa, ripetizione.

---

## Parte 1 — Cosa prevede il piano (riassunto semplice)

Il ciclo di gioco V2 prevede che ogni turno di partita si svolga così:

1. Il sistema estrae un numero e lo annuncia a voce.
2. Si apre una finestra di tempo (impostabile dall'utente, per esempio 60 secondi).
   In questa finestra tutti i giocatori agiscono:
   - Il giocatore umano ascolta il numero, naviga le sue cartelle, segna il numero,
     e se ha ottenuto un premio lo dichiara. Quando ha finito preme "Ho finito".
   - I bot automatici fanno la stessa cosa da soli, con un ritardo casuale per
     simulare un comportamento realistico.
3. Quando tutti hanno finito (o quando il tempo scade), il sistema verifica i
   premi realmente ottenuti, li annuncia a voce.
4. Il sistema annuncia "Turno terminato, prossimo turno fra X secondi", attende,
   e poi riparte automaticamente dalla fase 1 senza premere alcun pulsante.

---

## Parte 2 — Cosa è già stato costruito (per ogni sotto-fase del piano)

### Sotto-fase A — Separazione estrazione dai reclami bot: COMPLETATA

La parte del motore di gioco che estrae i numeri è stata correttamente separata
dalla parte che gestisce i reclami dei giocatori. Quando il sistema estrae un
numero, i bot aggiornano le loro cartelle ma non dichiarano ancora nessuna
vittoria. Questo è esattamente ciò che serve al ciclo V2.

I metodi coinvolti esistono e funzionano:
- La partita ha una fase di "estrazione" e una fase di "verifica" separate.
- I test confermano che dopo l'estrazione i bot non hanno reclami.

### Sotto-fase B — Bot che dichiarano fine fase: COMPLETATA

I bot hanno il metodo per dire "ho finito la mia azione e questo è il mio
eventuale reclamo". Funziona correttamente: il bot analizza le sue cartelle,
decide se ha un premio da reclamare, lo registra e segnala che ha concluso.

I test coprono i casi:
- Bot senza premi disponibili.
- Bot con ambo, terno, fino a tombola.
- Evita di reclamare premi già assegnati.
- Funziona correttamente tra un turno e il successivo (reset).

### Sotto-fase C — Messaggi vocali e annunci: COMPLETATA

Il sistema di annunci vocali è stato esteso con tutti i messaggi previsti:
- Avviso al 60%, 80% e 95% del tempo trascorso.
- Messaggio "tempo scaduto".
- Messaggio "tutti pronti, avvio verifica".
- Messaggio "turno terminato, prossimo turno fra X secondi".
- Conto alla rovescia durante la pausa.

Tutti i testi sono presenti nel catalogo italiano e i test confermano che
il sistema di annunci funziona.

### Sotto-fase D — Finestra d'azione, timer e pausa nella finestra di gioco: PARZIALMENTE COMPLETATA

Questa è la parte più complessa e dove risiedono i problemi principali.
Ecco cosa c'è e cosa manca:

Cosa esiste già:
- Il pulsante principale gestisce le tre fasi (inizio, "Ho finito", pausa).
- Il timer che conta il tempo della finestra d'azione esiste e funziona.
- Gli avvisi progressivi al 60%, 80%, 95% vengono emessi dal timer.
- La schedulazione dei bot con ritardi casuali è implementata.
- Il controllo "tutti pronti" con terminazione anticipata esiste.
- La verifica premi al termine della finestra è implementata.
- La pausa tra turni con timer è implementata.

Cosa non funziona (problemi trovati):
Vedere la sezione "Problemi" più avanti.

### Sotto-fase E — Configurazione: COMPLETATA

La finestra di configurazione iniziale include già i due nuovi campi:
- Durata della finestra d'azione (da 5 a 300 secondi, predefinito 60).
- Durata della pausa tra turni (da 1 a 30 secondi, predefinito 5).

I valori vengono letti e passati correttamente alla finestra di gioco.
I test confermano che la conversione funziona.

### Sotto-fase F — Test finali e verifica accessibilità: IN CORSO

Esistono già 7 file di test V2 con 36 test, tutti verdi.
Manca la verifica manuale con lo screen reader NVDA, che è bloccata
dai problemi elencati di seguito.

---

## Parte 3 — Problemi trovati che impediscono il funzionamento

### Problema 1 — Metodo mancante per ottenere il giocatore umano (BLOCCANTE)

Quando il giocatore preme "Ho finito" nella fase di attesa reclami,
la finestra di gioco cerca di trovare il giocatore umano per dirgli
"hai dichiarato fine". Lo fa chiamando un metodo sulla classe
ComandiSistema che però non esiste su quella classe.

In pratica: il metodo `ottieni_giocatore_umano` esiste come funzione
a livello del controller di gioco, ed è anche importato nel file dei
comandi, ma non è stato aggiunto come metodo della classe ComandiSistema.
La finestra di gioco prova a chiamarlo come se fosse un metodo di quella
classe, e questo causa un errore che blocca l'applicazione al primo
tentativo di premere "Ho finito".

Impatto: ogni volta che il giocatore prova a dichiarare fine del suo
turno, l'applicazione va in errore. Questo rende impossibile completare
un turno manualmente.

### Problema 2 — La pausa non rilancia automaticamente il turno successivo

Dopo la verifica dei premi, la pausa viene avviata e un timer conta
i secondi impostati. Quando il timer scade, il sistema riporta lo stato
a "pronto per estrarre" e aggiorna l'etichetta del pulsante.

Tuttavia, il turno successivo non parte automaticamente: il sistema si
ferma e aspetta che l'utente prema di nuovo il pulsante per estrarre.
Questo non corrisponde al ciclo desiderato, dove dopo la pausa il
sistema deve riprendere da solo dalla fase 1 (estrazione) senza
intervento dell'utente.

Impatto: l'utente deve premere il pulsante a ogni turno, che è esattamente
il comportamento che volevamo eliminare con il V2.

### Problema 3 — Conflitto timer quando più timer condividono lo stesso binding

La finestra di gioco usa due timer separati (uno per la finestra d'azione
e uno per la pausa), ma li collega entrambi allo stesso tipo di evento
sulla stessa finestra. Il timer della pausa usa un collegamento one-shot
che potrebbe interferire con il timer della finestra d'azione se per qualche
ragione entrambi sono attivi. In condizioni normali questo non dovrebbe
succedere perché il timer d'azione viene fermato prima di avviare la pausa,
ma è un rischio se le tempistiche si sovrappongono.

Impatto: potenziale ma non certo. Più un rischio di stabilità che un
problema concreto già osservato.

### Problema 4 — Il primo turno richiede comunque un clic manuale

Anche con il V2, la partita inizia solo quando l'utente preme per la prima
volta "Inizia partita". Questo è corretto e intenzionale per il primo turno.
Ma vale la pena chiarire che il ciclo "automatico senza pulsanti" si applica
dal secondo turno in poi.

Impatto: nessuno, è comportamento atteso. Lo segnalo solo per chiarezza.

---

## Parte 4 — Riepilogo a colpo d'occhio

| Parte del piano | Stato | Funziona? |
|---|---|---|
| A — Estrazione separata dai reclami | Fatta | Si |
| B — Bot che dichiarano fine | Fatta | Si |
| C — Messaggi vocali nuovi | Fatta | Si |
| D — Timer, finestra d'azione, pausa | Quasi fatta | No, ha problemi |
| E — Configurazione durate | Fatta | Si |
| F — Test finali e NVDA | In corso | Bloccata dai problemi |

I 721 test automatici passano tutti (36 specifici per il V2).
I problemi sono nella parte visiva e interattiva (finestra di gioco).

---

## Parte 5 — Cosa va fatto per completare il ciclo

In ordine di priorità:

### Azione 1 — Aggiungere il metodo mancante in ComandiSistema

Bisogna aggiungere il metodo `ottieni_giocatore_umano` alla classe
ComandiSistema, che al suo interno chiama la funzione omonima già
esistente nel controller. È una modifica di poche righe.

Alternativa: modificare la finestra di gioco per chiamare direttamente
la funzione del controller invece di passare dalla classe ComandiSistema.
Entrambe le soluzioni funzionano.

### Azione 2 — Far ripartire automaticamente il turno dopo la pausa

Quando il timer della pausa scade, invece di fermarsi e aspettare un
clic, il sistema deve automaticamente lanciare un nuovo turno, cioè
chiamare la stessa logica di estrazione che oggi viene chiamata dal
pulsante. In pratica, alla fine della pausa il codice deve simulare
un "clic automatico" sul pulsante di estrazione.

### Azione 3 — Verificare la separazione dei timer

Assicurarsi che i due timer (finestra d'azione e pausa) non possano
mai essere attivi contemporaneamente. Aggiungere una protezione che
ferma esplicitamente qualsiasi timer precedente prima di avviarne
uno nuovo.

### Azione 4 — Verifica manuale con NVDA

Una volta risolti i problemi precedenti, eseguire una sessione di
gioco completa con lo screen reader NVDA per verificare:
- Il numero estratto viene annunciato subito.
- Gli avvisi al 60%, 80%, 95% sono udibili senza sovrapposizioni.
- Il messaggio "tutti pronti" o "tempo scaduto" viene annunciato.
- La pausa viene annunciata con il conteggio.
- Il turno successivo riparte automaticamente.
- Il pulsante "Ho finito" è raggiungibile con Tab e annunciato da NVDA.

---

## Parte 6 — Come funziona il codice oggi

### Flusso attuale (quello che succede quando avvii l'applicazione)

1. Si apre la finestra di configurazione con i campi: nome, bot, cartelle,
   durata finestra d'azione, durata pausa tra turni.
2. L'utente inserisce i dati e preme "Avvia partita".
3. Si apre la finestra di gioco con il pulsante "Inizia partita" e la griglia.
4. L'utente preme "Inizia partita":
   - Un numero viene estratto e annunciato.
   - Il pulsante diventa "Ho finito — avvia verifica".
   - Parte un timer di 60 secondi (o il valore impostato).
   - I bot vengono schedulati per rispondere con ritardi casuali.
5. L'utente preme "Ho finito":
   - QUI IL SISTEMA VA IN ERRORE (Problema 1: metodo mancante).
   - Se il problema non ci fosse: l'umano verrebbe segnato come "ha finito",
     e se tutti i giocatori avessero finito, si avanzerebbe alla verifica.
6. Se il timer scade senza premere "Ho finito":
   - Il sistema avanza comunque alla verifica premi (questo funziona).
7. Dopo la verifica premi:
   - Viene annunciata la pausa.
   - Il timer della pausa parte.
   - Quando scade, il pulsante torna a "Passa turno" ma il turno NON
     riparte da solo (Problema 2: manca l'auto-rilancio).
8. L'utente deve premere di nuovo il pulsante per ogni turno.

### Come dovrebbe funzionare (obiettivo)

1-4: identici (sono corretti).
5. L'utente preme "Ho finito":
   - L'umano viene segnato come "ha finito".
   - Se tutti hanno finito: il timer si ferma, si annuncia "tutti pronti",
     si esegue la verifica premi, si annunciano i premi.
   - Si annuncia "turno terminato, prossimo turno fra X secondi".
6. Se il timer scade: stessa cosa ma senza il messaggio "tutti pronti".
7. Il timer della pausa conta, e quando finisce il sistema AUTOMATICAMENTE
   estrae il prossimo numero e riparte dalla fase 1.
8. L'utente non preme nulla tra un turno e l'altro.

---

## Conclusione

Il progetto è in buono stato. La maggior parte del lavoro previsto dal piano V2
è stata completata: il motore di gioco, i bot, gli annunci vocali, la configurazione
e i test funzionano tutti. Restano due interventi concreti per far funzionare il
ciclo completo:
- Aggiungere il metodo mancante (poche righe).
- Far ripartire il turno automaticamente dopo la pausa (una modifica nella
  gestione dello scadere del timer della pausa).

Con queste due modifiche, il ciclo di turno V2 dovrebbe funzionare come previsto.
