# MAPPATURA TASTI RAPIDI — TOMBOLA STARK v0.10.0

Report testuale completo. Tutti i tasti sono singoli, catturati con msvcrt senza combinazioni. Quando un comando richiede un argomento numerico, il programma chiede il valore con un prompt dedicato dopo la pressione del tasto.

***

## Gruppo 1 — Navigazione riga semplice

Freccia Su chiama sposta_focus_riga_su_semplice. Sposta il cursore alla riga precedente e legge i numeri grezzi della riga.

Freccia Giù chiama sposta_focus_riga_giu_semplice. Sposta il cursore alla riga successiva e legge i numeri grezzi della riga.

***

## Gruppo 2 — Navigazione riga avanzata

Tasto A chiama sposta_focus_riga_su_avanzata. Sale alla riga precedente con analisi completa: numeri segnati, numeri mancanti e stato della vincita.

Tasto Z chiama sposta_focus_riga_giu_avanzata. Scende alla riga successiva con la stessa analisi completa. I tasti A e Z sono stati scelti perché si trovano in colonna verticale sulla tastiera italiana e risultano intuitivi come coppia su e giù.

***

## Gruppo 3 — Navigazione colonna semplice

Freccia Sinistra chiama sposta_focus_colonna_sinistra. Sposta il cursore alla colonna precedente e legge il numero della singola cella.

Freccia Destra chiama sposta_focus_colonna_destra. Sposta il cursore alla colonna successiva e legge il numero della singola cella.

***

## Gruppo 4 — Navigazione colonna avanzata

Tasto Q chiama sposta_focus_colonna_sinistra_avanzata. Va alla colonna precedente con analisi verticale completa della colonna.

Tasto W chiama sposta_focus_colonna_destra_avanzata. Va alla colonna successiva con la stessa analisi verticale completa. I tasti Q e W sono stati scelti perché sono i primi due tasti in alto a sinistra della tastiera, facili da trovare senza guardare.

***

## Gruppo 5 — Salto diretto a riga o colonna specifica

Tasto R chiama vai_a_riga_avanzata. Dopo la pressione il programma chiede il numero di riga da raggiungere, accetta i valori da 1 a 3. Il cursore salta direttamente a quella riga e mostra l'analisi avanzata. R è stato scelto come iniziale di Riga.

Tasto C chiama vai_a_colonna_avanzata. Dopo la pressione il programma chiede il numero di colonna da raggiungere, accetta i valori da 1 a 9. Il cursore salta direttamente a quella colonna e mostra l'analisi avanzata. C è stato scelto come iniziale di Colonna.

***

## Gruppo 6 — Gestione e navigazione cartelle

Tasto PagGiù chiama riepilogo_cartella_successiva. Avanza alla cartella successiva e legge immediatamente il riepilogo con i numeri mancanti ai vari premi.

Tasto PagSu chiama riepilogo_cartella_precedente. Torna alla cartella precedente con lo stesso riepilogo.

Tasti numerici da 1 a 6 chiamano imposta_focus_cartella seguita immediatamente da riepilogo_cartella_corrente. Premendo il numero della cartella si salta direttamente ad essa e si ascolta subito lo stato di quella cartella.

***

## Gruppo 7 — Visualizzazione della cartella corrente e di tutte le cartelle

Tasto D chiama visualizza_cartella_corrente_semplice. Mostra tutti i numeri della cartella in focus nella forma grezza, senza indicare lo stato di segnazione. D è stato scelto come iniziale di Display.

Tasto F chiama visualizza_cartella_corrente_avanzata. Mostra la cartella in focus con indicazione dei numeri segnati, riepiloghi per riga e totale complessivo. F è stato scelto come Full display.

Tasto G chiama visualizza_tutte_cartelle_semplice. Mostra in sequenza tutte le cartelle del giocatore nella forma semplice. G è stato scelto come iniziale di Globale.

Tasto H chiama visualizza_tutte_cartelle_avanzata. Mostra tutte le cartelle con analisi avanzata completa di ogni riga e colonna. I tasti D, F, G, H sono sulla stessa fila centrale della tastiera e si premono comodamente con la mano destra uno accanto all'altro.

***

## Gruppo 8 — Consultazione del tabellone

Tasto U chiama comunica_ultimo_numero_estratto. Legge l'ultimo numero uscito nell'estrazione più recente. U è stato scelto come iniziale di Ultimo.

Tasto I chiama visualizzaultiminumeriestratti. Legge gli ultimi cinque numeri estratti in ordine di estrazione. I è stato scelto come Indietro, per richiamare la cronologia recente.

Tasto O chiama riepilogo_tabellone. Fornisce una panoramica completa del tabellone: quanti numeri sono usciti, quanti mancano, la percentuale di avanzamento e gli ultimi estratti. O è stato scelto come iniziale di Overview.

Tasto L chiama lista_numeri_estratti. Legge la lista completa e ordinata di tutti i numeri usciti dall'inizio della partita. L è stato scelto come iniziale di Lista.

Tasto E chiama verifica_numero_estratto. Dopo la pressione il programma chiede quale numero verificare. Risponde se quel numero è già stato estratto oppure no. E è stato scelto come iniziale di Estratto.

Tasto N chiama cerca_numero_nelle_cartelle. Dopo la pressione il programma chiede quale numero cercare. Risponde in quali cartelle del giocatore si trova quel numero e se è già stato segnato. N è stato scelto come iniziale di Numero.

***

## Gruppo 9 — Orientamento e stato corrente

Tasto punto interrogativo chiama stato_focus_corrente. In qualsiasi momento dice in quale cartella, riga e colonna si trova il cursore. È il comando di orientamento da usare ogni volta che si perde il filo della navigazione.

***

## Gruppo 10 — Azioni di gioco

Tasto S chiama segna_numero_manuale. Dopo la pressione il programma chiede quale numero segnare sulla cartella in focus. S è stato scelto come iniziale di Segna.

Tasto V chiama annuncia_vittoria. Dopo la pressione il programma chiede il tipo di vincita da dichiarare tra ambo, terno, quaterna, cinquina e tombola. V è stato scelto come iniziale di Vittoria.

Tasto P chiama passa_turno e avvia l'estrazione del numero successivo. È il comando principale del turno, invariato rispetto alla versione precedente. P è stato scelto come iniziale di Prosegui.

Tasto X avvia la procedura di uscita dalla partita con richiesta di conferma esplicita. X è stato scelto come iniziale di eXit e per la sua posizione angolare sulla tastiera, difficile da premere per sbaglio.