---
type: design
feature: conversione_test_pytest_unittest
status: REVIEWED
agent: Agent-Design
version: 0.9.0
date: 2026-03-28
source_report: docs/4 - reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md
---

# DESIGN conversione_test_pytest_unittest

## Idea in 3 righe

Convertire in modo controllato i test pytest non passanti o non rilevati dal runner standard in test unittest uniformi al corpus gia verde in tests/.
La migrazione avviene per batch ordinati per impatto e rischio, preservando semantica, copertura utile e leggibilita dei test per il workflow accessibile del progetto.
L'obiettivo non e solo far eseguire i test, ma stabilire un modello unico di struttura, setup, mocking e validazione compatibile con python -m unittest discover.

## Obiettivo

Definire la strategia architetturale e operativa per convertire i test pytest non passanti in test unittest standard.

La feature deve:

- uniformare i test convertiti allo stile dei test unittest gia verdi presenti in tests/;
- rimuovere le dipendenze strutturali da fixture, mark e utility pytest non portabili;
- introdurre una strategia di batching che massimizzi il recupero rapido della suite e minimizzi regressioni;
- esplicitare dipendenze tecniche, rischi di migrazione e criteri di accettazione misurabili.

## Contesto

Il contesto di partenza e il findings report verificato [REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md](../4%20-%20reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md), che identifica:

- file pytest con fallimenti attivi o incompatibilita strutturali con unittest;
- file unittest gia conformi da usare come riferimento canonico;
- dipendenze specifiche da pytest da sostituire con costrutti standard library;
- rischi di migrazione legati a mock di msvcrt, output TUI, side effect finiti e logging su filesystem.

Il repository ha gia una baseline di test unittest verdi in tests/ che rappresenta la convenzione target. La conversione non introduce un secondo modello di test: consolida il progetto su un unico runner standard, coerente con il workflow accessibile dell'utente e con la discovery nativa di unittest.

## Attori e Concetti

### Attori

- Agent-Analyze: produce il report di findings e identifica priorita, rischi e dipendenze.
- Agent-Design: definisce strategia, criteri di uniformita e ordine dei batch.
- Agent-Plan: traduce il design in fasi operative committabili, ma non fa parte di questo deliverable.
- Agent-Code: applica la conversione ai file di test seguendo il design approvato.
- Utente: valida il design e conferma la transizione da DRAFT a REVIEWED.

### Concetti

- Test unittest canonico: file strutturato con import unittest, classi TestX(unittest.TestCase), setUp o helper espliciti, assert leggibili e compatibilita con unittest discover.
- Migrazione in place: conversione del file esistente senza duplicare suite parallele pytest e unittest.
- Batch di migrazione: gruppo di file convertiti insieme per impatto tecnico omogeneo e rischio controllabile.
- Uniformita: allineamento sintattico, semantico e operativo ai test unittest gia verdi nel progetto.

## Componenti coinvolti

### Input documentali

- Findings report di analisi: [docs/4 - reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md](../4%20-%20reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md)
- Coordinatore documentale: [docs/TODO.md](../TODO.md)

### Test suite coinvolta

- File pytest con fallimenti attivi o incompatibilita strutturali in [tests](../../tests)
- File unittest gia verdi in [tests](../../tests) usati come reference canonica

### Meccanismi tecnici da standardizzare

- conversione di @pytest.fixture in setUp, tearDown o helper privati;
- sostituzione di capsys con patch di sys.stdout e io.StringIO;
- sostituzione di monkeypatch con unittest.mock.patch e cleanup esplicito;
- sostituzione di tmp_path con tempfile.TemporaryDirectory gestito da cleanup;
- conversione di test parametrizzati in self.subTest oppure in casi espansi quando la leggibilita prevale;
- isolamento del mock di msvcrt prima degli import o nel setup del modulo target;
- mantenimento dei path di patch al modulo chiamante, non all'oggetto originario.

## Flussi Concettuali

### Flusso 1: classificazione e prioritizzazione

1. Partire dal findings report e classificare i file per rischio, dipendenze pytest e volume di casi recuperabili.
2. Usare i file unittest gia verdi come baseline formale di struttura e naming.
3. Assegnare ogni file a un batch unico, evitando migrazioni trasversali non motivate.

### Flusso 2: conversione strutturale di un batch

1. Portare il file al modello unittest canonico.
2. Sostituire fixture e utility pytest con equivalenti standard library.
3. Rendere deterministico setup, cleanup e mocking di risorse globali o esterne.
4. Rieseguire il batch con unittest e verificare che la semantica dei test resti invariata o esplicitamente corretta.

### Flusso 3: consolidamento progressivo della suite

1. Completare i batch ad alto impatto per recuperare rapidamente la maggior parte dei test non verdi.
2. Proseguire con batch di incompatibilita strutturale a rischio medio o basso.
3. Trattare separatamente i bug logici non strutturali gia presenti in file unittest, senza confonderli con la conversione pytest -> unittest.

## Vincoli

- Nessuna introduzione di nuovo codice applicativo: lo scope riguarda solo la progettazione della migrazione dei test.
- Nessuna creazione del PLAN in questa fase.
- La suite target deve essere eseguibile con python -m unittest discover senza dipendenza funzionale da pytest.
- I test convertiti devono mantenere naming descrittivo in italiano, coerente con i test gia presenti e leggibile da screen reader.
- Le asserzioni su output TUI non devono essere indebolite durante la migrazione.
- I test convertiti non devono lasciare stato globale sporco tra esecuzioni, in particolare su sys.modules, logger singleton, stdout e directory temporanee.
- La migrazione deve essere additiva sul piano del valore, ma in place sul piano dei file: niente duplicazione permanente di test equivalenti in due framework diversi.

## Decisioni di Design

### 1. Modello target unico: unittest standard library

La conversione converge su unittest come unico modello strutturale per la suite gestita dalla feature. Questa scelta elimina il costo cognitivo e operativo di mantenere convenzioni miste e rende il runner standard una fonte di verita unica per discovery, esecuzione e reporting.

### 2. Uniformita guidata dai file gia verdi

I file unittest gia conformi in tests/ sono il riferimento di stile, non un esempio opzionale. I test convertiti devono replicarne la forma base:

- import unittest come runner principale;
- classi TestX unittest.TestCase;
- setUp o helper espliciti al posto di fixture implicite;
- uso di unittest.mock per patch e doppi;
- assert leggibili e orientate al comportamento osservabile.

### 3. Conversione in place, non doppia manutenzione

Ogni file pytest viene convertito sul posto. Non si mantiene una variante pytest parallela. Questo riduce drift, evita suite duplicate e semplifica il controllo di copertura reale.

### 4. Batching per rischio e ritorno immediato

L'ordine di migrazione non segue solo il path dei file, ma il rapporto tra casi recuperati, complessita tecnica e rischio di regressione. I file che sbloccano molti errori o fallimenti vengono trattati prima, pur imponendo mitigazioni dedicate sui punti fragili gia emersi dal report.

### 5. Separazione tra conversione strutturale e fix logici

Un bug logico in un file gia unittest non viene conteggiato come conversione pytest -> unittest. Va eventualmente corretto nello stesso programma di lavoro, ma con tracciamento concettuale separato. Questo mantiene chiaro il confine tra migrazione di framework e correzione di comportamento.

### 6. Cleanup esplicito per tutte le risorse sensibili

Le risorse che in pytest erano assorbite da fixture implicite devono diventare esplicite in unittest. La decisione progettuale e rendere obbligatorio il cleanup locale di:

- sys.modules e mock di msvcrt;
- stdout catturato;
- patcher avviati manualmente;
- logger singleton o stato statico;
- directory e file temporanei.

### 7. Conservazione della semantica di test e del valore accessibile

La conversione non deve ridurre la qualita delle asserzioni. Nei test TUI e di accessibilita, i messaggi testati restano parte del contratto. Se un costrutto pytest viene sostituito, deve preservare il significato della verifica e non solo la sua eseguibilita tecnica.

## Strategia di batching

### Batch 0: baseline e pre-condizioni

Scopo: fissare il punto di partenza della suite unittest e la discovery reale del repository.

Contenuto:

- conferma dei file gia raccolti da unittest discover;
- quantificazione dei test gia verdi;
- verifica che i file pytest incompatibili siano effettivamente fuori dalla baseline o in stato non verde.

### Batch 1: recupero critico ad alto impatto

Scopo: sbloccare la maggior parte dei casi non verdi concentrati in pochi file ad alta densita di problemi.

Target prioritari secondo il findings report:

- tests/unit/test_tui_commander.py
- tests/flow/test_flusso_game_loop.py
- tests/test_silent_controller.py

Razionali:

- massimo recupero rapido di errori e fallimenti;
- problemi tecnici gia noti e mitigabili;
- forte valore di stabilizzazione per TUI, loop e mock globali.

### Batch 2: consolidamento TUI e input da tastiera

Scopo: rimuovere flakiness e incompatibilita strutturali residue nei test TUI e di loop tastiera.

Target:

- tests/unit/test_tui_partita.py
- tests/integration/test_game_loop_tasti.py

### Batch 3: conversioni class-based a media frizione

Scopo: promuovere classi di test gia quasi conformi a pieno unittest standard.

Target:

- tests/unit/test_giocatore_automatico_bot_attivo.py
- tests/integration/test_partita_bot_attivo.py
- tests/unit/test_ui_terminale.py

### Batch 4: funzioni standalone a bassa frizione

Scopo: incapsulare test semplici in TestCase uniformi senza introdurre rischio elevato.

Target:

- tests/unit/test_codici_loop.py
- tests/unit/test_imposta_focus_cartella_regression.py
- tests/unit/test_ottieni_giocatore_umano.py
- tests/unit/test_game_controller_loop.py
- tests/unit/test_renderer_report_finale.py

### Batch 5: logging e filesystem con cleanup rigoroso

Scopo: convertire i file che dipendono da monkeypatch, tmp_path e stato globale del logger.

Target:

- tests/unit/test_game_logger.py
- tests/unit/test_event_logging.py
- tests/integration/test_event_coverage.py
- tests/integration/test_logging_integration.py

Razionali:

- conversione piu laboriosa ma meccanicamente chiara;
- richiede disciplina sul cleanup per evitare leak tra test.

## Criteri di uniformita

Un file convertito e considerato uniforme solo se rispetta tutti i criteri seguenti:

- usa unittest come runner e struttura primaria;
- non richiede fixture, mark o helper pytest per essere eseguito;
- e scoperto da unittest discover;
- adotta classi TestCase o, se strettamente necessario, pattern compatibili con discovery standard;
- centralizza setup e cleanup in metodi espliciti o helper chiaramente nominati;
- usa patch sui path del modulo sotto test, non su alias opachi;
- mantiene nomi di test descrittivi e coerenti con lo stile gia presente in tests/;
- conserva il contenuto informativo delle asserzioni, in particolare sui messaggi TUI e sui contratti di logging.

## Dipendenze e rischi

### Dipendenze principali

- disponibilita dei file unittest gia verdi come reference pattern;
- ordine corretto di patching nei moduli TUI e logging;
- sostituti standard library per fixture pytest, output capture e filesystem temporaneo;
- esecuzione con unittest discover come meccanismo di verifica primaria.

### Rischi principali

- accumulo di stato nel mock di msvcrt tra test;
- persistenza di side effect finiti nei test di game loop;
- perdita di copertura semantica durante la sostituzione di capsys o parametrize;
- leak di patch o stato singleton nei test di logging;
- confusione tra fix di conversione e fix di bug logici preesistenti.

### Mitigazioni

- imporre cleanup esplicito e locale per ogni risorsa patchata;
- trattare i casi TUI e loop con priorita alta e con verifica dedicata della determinismo;
- usare subTest solo dove migliora la leggibilita, altrimenti espandere i casi;
- separare nel tracciamento i fix strutturali dai fix logici non direttamente legati a pytest.

## Criteri di accettazione

La feature e pronta per passare alla pianificazione operativa quando il design viene considerato adeguato a guidare una migrazione incrementale e verificabile.

In termini architetturali e operativi, il design e accettato se:

- definisce un modello target unico e non ambiguo per i test convertiti;
- identifica i file e i gruppi di conversione con un ordine motivato;
- esplicita i criteri di uniformita rispetto ai test unittest gia verdi;
- separa chiaramente dipendenze, rischi, mitigazioni e limiti di scope;
- fa riferimento esplicito al findings report di analisi come fonte dei dati di partenza;
- non introduce PLAN, codice o decisioni fuori dal perimetro del design.

## Coding plans correlati

Nessuno in questa fase. Il PLAN della feature dovra essere prodotto solo dopo review del presente design e sua eventuale promozione a stato REVIEWED.

## Limiti residui

- Il presente documento non risolve i fallimenti, ma definisce il percorso di conversione e i suoi vincoli.
- I numeri di baseline dei test verdi e dei test convertiti dovranno essere confermati in fase di esecuzione del futuro PLAN.
- Eventuali problemi logici gia presenti in file unittest esistenti restano fuori dal perimetro stretto della conversione, anche se potranno essere affrontati in parallelo in una fase successiva.