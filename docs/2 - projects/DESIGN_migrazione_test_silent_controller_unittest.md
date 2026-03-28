---
type: design
feature: migrazione_test_silent_controller_unittest
status: DRAFT
agent: Agent-Design
version: 0.9.1
date: 2026-03-28
source_test: tests/test_silent_controller.py
reference_tests:
  - tests/test_game_controller.py
  - tests/unit/test_game_controller_loop.py
---

# DESIGN migrazione_test_silent_controller_unittest

## Idea in 3 righe

Convertire completamente tests/test_silent_controller.py a unittest standard library, eliminando ogni residuo costrutto pytest senza alterare il comportamento verificato.
La migrazione deve riallineare il file al pattern gia adottato nel repository: classi TestCase, setup esplicito, mock deterministici e cattura stdout con patch di sys.stdout.
L'obiettivo e sbloccare il file rimasto a meta migrazione senza toccare codice applicativo e senza indebolire le asserzioni sui contratti del controller.

## Attori e Concetti

### Attori

- Agent-Analyze: ispeziona il file ibrido e identifica ogni costrutto pytest residuo.
- Agent-Design: definisce la struttura target del file convertito e i criteri di equivalenza comportamentale.
- Agent-Plan: traduce il design in passi operativi atomici e committabili.
- Agent-Code: eseguira la migrazione del file dopo approvazione utente del piano.
- Utente: approva design e piano prima di qualsiasi modifica ai test.

### Concetti

- File ibrido: file che usa import e mocking compatibili con unittest ma mantiene fixture parametrizzate, assert nativi e utility pytest.
- Fixture pytest residua: funzione helper passata come parametro ai test method, da sostituire con setUp o helper privati.
- Cattura stdout unittest: patch di sys.stdout con io.StringIO per verificare assenza di output.
- Contratto invariato: il significato dei test rimane lo stesso dopo la conversione; cambia solo il meccanismo tecnico con cui il test prepara l'input e osserva l'output.

## Flussi Concettuali

### Flusso 1: ricostruzione dello stato condiviso

1. Portare le fixture partita_mock e partita_terminata_mock dentro metodi helper o nel setUp delle classi che ne hanno bisogno.
2. Garantire che ogni test riceva un MagicMock fresco, senza side effect ereditati da altri test.
3. Conservare le stesse precondizioni logiche oggi codificate nelle fixture pytest.

### Flusso 2: sostituzione dei costrutti pytest

1. Trasformare ogni classe di test in sottoclasse di unittest.TestCase.
2. Sostituire capsys con patch di sys.stdout e lettura tramite getvalue().
3. Sostituire pytest.raises con self.assertRaises come context manager.
4. Sostituire gli assert nativi con assertEqual, assertTrue, assertFalse, assertIsNone, assertIn e simili per coerenza stilistica con il resto della suite.

### Flusso 3: mantenimento del contratto osservabile

1. I test di silenziosita devono continuare a verificare che l'output standard resti vuoto.
2. I test di contratto devono continuare a verificare i booleani, i None e le eccezioni attese.
3. I test sul dizionario MESSAGGI_CONTROLLER devono continuare a verificare cardinalita, chiavi e contenuto stringa non vuoto.

## Decisioni Architetturali

### 1. Struttura target a tre TestCase espliciti

Le classi TestControllerSilenzioso, TestContrattiRitorno e TestMESSAGGICONTROLLER devono diventare sottoclassi di unittest.TestCase. Questa scelta e coerente con i file gia convertiti del repository e rende il file compatibile con unittest discover senza adattatori.

### 2. Factory private al posto delle fixture pytest

Le attuali funzioni partita_mock e partita_terminata_mock non devono piu essere trattate come fixture parametrizzate. La struttura target piu semplice e robusta e:

- un helper _build_partita_in_corso per produrre un mock Partita valido per i test di flusso standard;
- un helper _build_partita_terminata per i test sullo stato finale;
- eventuale riuso tramite setUp solo nelle classi che usano sempre la stessa variante di mock.

Questa scelta evita condivisione accidentale di side effect tra test che mutano il mock, come quelli che impostano avvia_partita.side_effect o cambiano get_stato_partita.return_value.

### 3. Cattura stdout con patch locale per test method

I test oggi basati su capsys devono usare patch('sys.stdout', new_callable=io.StringIO) applicata al singolo metodo o incapsulata in un helper. La cattura deve rimanere locale al test, non globale alla classe, per evitare contaminazioni tra casi.

### 4. assertRaises come unico sostituto di pytest.raises

Il test che oggi usa pytest.raises(ValueError) deve essere convertito a:

with self.assertRaises(ValueError):
    ...

Questa scelta mantiene la stessa semantica e rimuove l'ultima dipendenza diretta da pytest.

### 5. Uniformita stilistica con i test di riferimento

Il file convertito deve imitare i pattern gia visibili in tests/test_game_controller.py e tests/unit/test_game_controller_loop.py:

- import unittest in testa al file;
- annotazioni di ritorno sui metodi di test dove gia usate nel corpus;
- uso di self.assert* invece di assert nativo;
- eventuale setUp per stato condiviso leggibile;
- commenti di sezione solo se aiutano la scansione del file.

## Rischi e Vincoli

### Rischi

- Riutilizzare lo stesso MagicMock in piu test potrebbe propagare side effect e falsare i risultati.
- Una patch stdout definita a livello errato potrebbe nascondere output reale o introdurre coupling tra test.
- La conversione meccanica degli assert senza allineamento al contratto potrebbe preservare l'esecuzione ma indebolire la leggibilita.

### Vincoli

- Nessuna modifica al codice applicativo del controller o del dominio.
- Nessuna dipendenza residua da pytest nel file finale.
- Il file deve restare eseguibile con python -m unittest tests.test_silent_controller.
- Le asserzioni di silenziosita devono restare binarie: stdout vuoto oppure test fallito.
- Il piano corrente si ferma prima dell'implementazione: nessuna modifica ai test in questa iterazione.

## Analisi dettagliata del file attuale

### Struttura generale

Il file contiene tre classi di test ma nessuna eredita da unittest.TestCase. La discovery pytest funziona per convenzione, quella unittest no. Il file e quindi in stato ibrido: usa unittest.mock ma dipende ancora dalla meccanica di pytest per fixture, output capture e exception assertions.

### Helper e fixture residue

#### partita_mock

- Costrutto pytest presente: fixture implicita usata come parametro dei test method.
- Equivalente unittest: helper privato che ritorna un MagicMock fresco oppure inizializzazione in setUp.
- Adattamento logico: la logica resta invariata; serve solo garantire un mock nuovo per ogni test che lo modifica.

#### partita_terminata_mock

- Costrutto pytest presente: fixture implicita usata come parametro del test method.
- Equivalente unittest: helper privato separato o attributo valorizzato in setUp.
- Adattamento logico: invariato.

### Classe TestControllerSilenzioso

- Costrutto pytest presente a livello classe: mancata ereditarieta da unittest.TestCase.
- Equivalente unittest: class TestControllerSilenzioso(unittest.TestCase).
- Adattamento logico: invariato.

#### test_crea_partita_standard_silenzioso

- Costrutto pytest presente: capsys e assert nativo.
- Equivalente unittest: patch di sys.stdout con io.StringIO e self.assertEqual(buffer.getvalue(), "").
- Adattamento logico: invariato.

#### test_avvia_partita_sicura_true_silenzioso

- Costrutti pytest presenti: capsys, fixture partita_mock, assert nativo.
- Equivalente unittest: mock ottenuto da helper/setUp, patch sys.stdout, self.assertEqual.
- Adattamento logico: invariato.

#### test_avvia_partita_sicura_false_silenzioso

- Costrutti pytest presenti: capsys, fixture partita_mock, assert nativo.
- Equivalente unittest: mock fresco da helper, impostazione side_effect inline, patch sys.stdout, self.assertEqual.
- Adattamento logico: invariato.

#### test_esegui_turno_sicuro_dict_silenzioso

- Costrutti pytest presenti: capsys, fixture partita_mock, assert nativo.
- Equivalente unittest: helper/setUp + patch sys.stdout + self.assertEqual.
- Adattamento logico: invariato.

#### test_esegui_turno_sicuro_none_silenzioso

- Costrutti pytest presenti: capsys, fixture partita_mock, assert nativo.
- Equivalente unittest: mock fresco, override del return_value inline, patch sys.stdout, self.assertEqual.
- Adattamento logico: invariato.

#### test_partita_terminata_false_silenzioso

- Costrutti pytest presenti: capsys, fixture partita_mock, assert nativo.
- Equivalente unittest: helper/setUp + patch sys.stdout + self.assertEqual.
- Adattamento logico: invariato.

#### test_partita_terminata_true_silenzioso

- Costrutti pytest presenti: capsys, fixture partita_terminata_mock, assert nativo.
- Equivalente unittest: helper/setUp + patch sys.stdout + self.assertEqual.
- Adattamento logico: invariato.

#### test_ottieni_stato_sintetico_dict_silenzioso

- Costrutti pytest presenti: capsys, fixture partita_mock, assert nativo.
- Equivalente unittest: helper/setUp + patch sys.stdout + self.assertEqual.
- Adattamento logico: invariato.

### Classe TestContrattiRitorno

- Costrutto pytest presente a livello classe: mancata ereditarieta da unittest.TestCase.
- Equivalente unittest: class TestContrattiRitorno(unittest.TestCase).
- Adattamento logico: invariato.

#### test_avvia_partita_sicura_ritorna_true

- Costrutti pytest presenti: fixture partita_mock e assert nativo.
- Equivalente unittest: helper/setUp + self.assertTrue.
- Adattamento logico: invariato.

#### test_avvia_partita_sicura_ritorna_false_su_eccezione

- Costrutti pytest presenti: fixture partita_mock e assert nativo.
- Equivalente unittest: helper/setUp + self.assertFalse.
- Adattamento logico: invariato.

#### test_ottieni_stato_sintetico_lancia_valueerror_su_non_partita

- Costrutto pytest presente: pytest.raises.
- Equivalente unittest: self.assertRaises(ValueError).
- Adattamento logico: invariato.

#### test_esegui_turno_sicuro_ritorna_none_su_partita_non_in_corso

- Costrutti pytest presenti: fixture partita_mock e assert nativo.
- Equivalente unittest: helper/setUp + self.assertIsNone.
- Adattamento logico: invariato.

### Classe TestMESSAGGICONTROLLER

- Costrutto pytest presente a livello classe: mancata ereditarieta da unittest.TestCase.
- Equivalente unittest: class TestMESSAGGICONTROLLER(unittest.TestCase).
- Adattamento logico: invariato.

#### test_quattro_chiavi

- Costrutto pytest presente: assert nativo.
- Equivalente unittest: self.assertEqual.
- Adattamento logico: invariato.

#### test_chiavi_sono_costanti_corrette

- Costrutto pytest presente: assert nativo multiplo.
- Equivalente unittest: self.assertIn per ciascuna chiave.
- Adattamento logico: invariato.

#### test_valori_sono_stringhe_non_vuote

- Costrutto pytest presente: assert nativo in loop.
- Equivalente unittest: self.assertIsInstance e self.assertGreater, eventualmente con self.subTest(chiave=chiave).
- Adattamento logico: lieve miglioramento consigliato con subTest per isolare eventuali failure per chiave.

## Struttura target del file corretto

### Import attesi

- import io
- import unittest
- from unittest.mock import MagicMock, patch
- import dei moduli applicativi gia presenti

### Organizzazione proposta

1. Docstring di modulo aggiornata per dichiarare esplicitamente il target unittest.
2. Eventuali helper privati di costruzione mock a livello modulo o come metodi di classe.
3. Tre classi TestCase:
   - TestControllerSilenzioso
   - TestContrattiRitorno
   - TestMESSAGGICONTROLLER
4. Eventuale blocco finale unittest.main solo se il resto della suite usa questo pattern nel sottoinsieme di riferimento; altrimenti opzionale.

### Gestione fixture convertite in setUp

- TestControllerSilenzioso puo usare helper privati per evitare di condividere un unico mock mutabile.
- TestContrattiRitorno puo usare lo stesso helper, richiamato all'inizio di ogni test.
- TestMESSAGGICONTROLLER non richiede fixture.

### Gestione stdout

La cattura stdout deve essere locale ai singoli test con pattern uniforme:

with patch('sys.stdout', new_callable=io.StringIO) as buffer:
    ctrl.funzione(...)
self.assertEqual(buffer.getvalue(), "")

### Gestione assertRaises

Il solo caso di eccezione va convertito con context manager unittest, senza import pytest.
