# Piano generale del progetto Tombola Stark

## 1. Descrizione del progetto Tombola Stark

Tombola Stark è un progetto per creare una versione digitale e accessibile della tombola italiana, pensata in particolare per persone non vedenti o ipovedenti.

La versione attuale del progetto è scritta in Python e contiene già la logica principale di gioco: tabellone, cartelle, giocatori umani e automatici, estrazione dei numeri ed eventi di vincita.

L’obiettivo di questo documento è descrivere in modo semplice la direzione generale del progetto, prima di entrare nei dettagli tecnici [web:23][web:31].

## 2. Obiettivo della migrazione a Flutter/Dart

L’obiettivo è creare una nuova applicazione desktop usando Flutter e Dart, partendo dalla logica esistente in Python.  
La nuova applicazione dovrà mantenere le stesse regole di gioco, ma aggiungere un’interfaccia grafica completamente accessibile con NVDA, utilizzabile solo con la tastiera.  
L'accessibilità è il requisito fondamentale del progetto: ogni elemento dell'interfaccia deve essere leggibile e navigabile tramite screen reader NVDA, senza eccezioni [web:15].

## 3. Motivazioni dell’approccio sistemico

Invece di convertire il codice “al volo”, voglio impostare il lavoro in modo sistemico, cioè partire da un piano chiaro e da regole scritte, e solo dopo passare alla scrittura del codice.  
Questo modo di lavorare riduce gli errori, rende il processo più prevedibile e permette di usare meglio strumenti come GitHub Copilot e i suoi agenti, che funzionano molto bene quando hanno istruzioni chiare da seguire.  
Per questo progetto Tombola Stark, che è il mio primo approccio sistemico, l’obiettivo è costruire una base solida e stabile, concentrandomi solo su questo obiettivo.

## 4. Principi guida del progetto

  I principi guida che voglio seguire sono:

1. Accessibilità prima di tutto: ogni scelta tecnica deve tenere conto dell’uso con NVDA e con la tastiera.  
2. Stabilità del codice: preferire soluzioni robuste e stabili, anche se non sono le più “eleganti” dal punto di vista teorico.  
3. Coerenza: mantenere lo stesso stile di codice e le stesse regole in tutti i file del progetto.  
4. Documentazione completa e specifica: scrivere documenti dettagliati per ogni sezione e argomento del progetto. Documenti chiari e precisi riducono gli errori e rendono il lavoro sistemico più sicuro e prevedibile [web:31].

## 5. Ambito della migrazione

L’ambito principale di questa migrazione include:

- la riscrittura della logica di gioco da Python a Dart,
- la progettazione e lo sviluppo dell’interfaccia Flutter per Windows,
- l’integrazione con NVDA e l’uso completo da tastiera [web:15].

Non sono inclusi, almeno in una prima fase:

- il supporto ad altre piattaforme (mobile, web, macOS, Linux),
- modalità di gioco avanzate o varianti delle regole tradizionali della tombola.

## 6. Strategia ad alto livello

La strategia generale sarà suddivisa in fasi:

1. Analizzare e documentare la logica esistente in Python.
2. Definire l’architettura di base del progetto Flutter/Dart.
3. Migrare la logica di gioco in Dart, senza interfaccia, con test di base.
4. Progettare e costruire l’interfaccia Flutter accessibile per Windows.
5. Raffinare l’accessibilità e l’esperienza d’uso con NVDA.

Queste fasi potranno essere adattate, ma servono come traccia iniziale [web:23][web:10].

## 7. Ruolo degli agenti e di Copilot

Il progetto userà GitHub Copilot e i suoi agenti come strumenti di supporto alla scrittura del codice e alla conversione da Python a Dart.

Per funzionare bene, gli agenti avranno bisogno di istruzioni chiare, che saranno scritte in appositi file di progetto (istruzioni, prompt, agenti, skills) [web:11][web:14].

L’obiettivo è arrivare al punto in cui posso delegare agli agenti la conversione di parti del codice, sapendo che seguiranno le regole definite in questo piano.

## 8. Requisiti di accessibilità

La nuova applicazione dovrà rispettare questi requisiti di base:

1. Essere completamente utilizzabile tramite tastiera.
2. Essere pienamente leggibile e navigabile tramite NVDA [web:15].
3. Fornire etichette testuali chiare per ogni elemento dell’interfaccia, senza elementi “muti”.
4. Evitare interazioni che richiedono il mouse o azioni non accessibili.

Questi requisiti verranno poi dettagliati in documenti e istruzioni specifiche.

## 9. Rischi principali e mitigazioni

Alcuni rischi principali del progetto sono:

1. La complessità della migrazione, che può portare a errori logici se non si procede per passi piccoli.
2. La possibile difficoltà nel garantire un’accessibilità completa se non vengono testate spesso le funzionalità con NVDA [web:15].
3. La dipendenza dagli strumenti di intelligenza artificiale, che vanno guidati con istruzioni chiare per evitare risultati incoerenti [web:26][web:29].

Per ridurre questi rischi, il progetto prevede:

- una migrazione graduale, partendo da moduli semplici,
- test frequenti con NVDA, anche su piccole parti dell’interfaccia,
- una cura particolare nella scrittura delle istruzioni per Copilot e gli agenti.
