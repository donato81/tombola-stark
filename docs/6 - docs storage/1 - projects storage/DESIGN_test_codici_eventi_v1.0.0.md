---
type: design
feature: test_codici_eventi
agent: Agent-Design
status: REVIEWED
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: design
titolo: Design test di contratto per i moduli codici_*.py
data_creazione: 2026-03-30
agente: Agent-Design
stato: revisionato
feature: test_codici_eventi
versione_progetto: v1.0.0
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Idea in 3 righe

Il task introduce un solo file di test, [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py),
dedicato esclusivamente al contratto dei moduli codici_*.py usati come chiavi stabili.
L'obiettivo non e' testare logica di business, ma congelare i valori stringa e la coerenza
tra costanti esportate e Literal dichiarati, con una struttura ordinata per modulo.

### Obiettivo

Definire il design tecnico del file [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)
limitando il perimetro ai sette moduli elencati nel Gruppo A del report:

- [bingo_game/events/codici_configurazione.py](../../bingo_game/events/codici_configurazione.py)
- [bingo_game/events/codici_controller.py](../../bingo_game/events/codici_controller.py)
- [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)
- [bingo_game/events/codici_eventi.py](../../bingo_game/events/codici_eventi.py)
- [bingo_game/events/codici_loop.py](../../bingo_game/events/codici_loop.py)
- [bingo_game/events/codici_messaggi_sistema.py](../../bingo_game/events/codici_messaggi_sistema.py)
- [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py)

Il design deve fissare:

- la struttura interna del file di test
- la suddivisione in classi, una per modulo
- gli scenari di contratto da coprire e la logica delle asserzioni
- gli import minimi necessari
- i criteri di completamento verificabili prima dell'avvio implementativo

### Contesto

Il report di riferimento, [report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md),
ha gia' stabilito che il Gruppo A e' il punto di ingresso corretto per la copertura della cartella
events: i moduli codici_*.py hanno complessita' bassa, nessuna dipendenza da wx, nessuna I/O e
nessun comportamento runtime complesso, ma costituiscono il contratto nominale usato da renderer,
eventi e cataloghi.

Il rischio principale non e' un errore algoritmico ma una regressione silenziosa di naming:
una costante rinominata, un valore stringa cambiato o un Literal non riallineato possono rompere
lookup e refusi semantici senza produrre immediatamente errori chiari.

Il task resta volutamente confinato al Gruppo A. Non include scenari relativi a:

- dataclass di [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py)
- factory method di [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py)
- logica di [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py)
- classi di [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)

### Attori e Concetti

#### Attori

- file di test [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)
- i sette moduli codici_*.py del perimetro Gruppo A
 - unittest come runner unitario
- `typing.get_args` come meccanismo di estrazione dei valori dichiarati nei Literal

#### Concetti

- Contratto di stabilita' delle chiavi:
  ogni costante deve mantenere il valore stringa atteso, senza alias impliciti o rinominazioni silenziose.
- Coerenza costanti/Literal:
  l'insieme delle costanti pubbliche e l'insieme dei valori ammessi dal Literal devono restare allineati.
- Importabilita' del modulo:
  ogni modulo deve essere caricabile in isolamento senza side effect o errori di import.
- Partizionamento dei codici errore:
  in [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)
  i tre gruppi devono formare unione completa senza intersezioni indesiderate.

### Componenti coinvolti

- File da creare: [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py)
- Riferimento analitico: [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- Coordinatore documentale: [docs/todo.md](../todo.md)

Nessun altro file di test e nessun file in [bingo_game/events/](../../bingo_game/events/) rientrano
nel perimetro di modifica di questo design.

### Flussi Concettuali

#### Flusso 1 - Verifica importabilita' di un modulo codici

1. Il test importa il modulo target.
2. Verifica che l'import non sollevi eccezioni.
3. Usa il modulo importato come sorgente di costanti e alias Literal per le asserzioni successive.

#### Flusso 2 - Verifica costanti stringa esatte

1. Il test identifica le costanti pubbliche del modulo.
2. Per ogni costante confronta nome simbolico e valore stringa atteso.
3. L'asserzione fallisce se una costante cambia valore o viene rimossa.

#### Flusso 3 - Verifica coerenza con Literal

1. Il test estrae i valori del Literal dichiarato dal modulo.
2. Costruisce l'insieme delle costanti pubbliche pertinenti.
3. Confronta i due insiemi e fallisce se esistono valori mancanti, extra o disallineati.

#### Flusso 4 - Verifica partizionamento codici errore

1. Il test estrae i valori da `Codici_Errori_Generici`, `Codici_Errori_Ui` e `Codici_Errori_Partita`.
2. Verifica che ogni gruppo sia internamente consistente e senza sovrapposizioni con gli altri.
3. Verifica che la loro unione coincida con l'insieme atteso del contratto globale `Codici_Errori`.

### Decisioni Architetturali

#### Decisione 1 - Un solo file di test, una classe per modulo

Il file [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py) conterra'
sette classi di test, una per ciascun modulo del Gruppo A, nell'ordine stabilito dal report:

1. `TestCodiciConfigurazione`
2. `TestCodiciController`
3. `TestCodiciErrori`
4. `TestCodiciEventi`
5. `TestCodiciLoop`
6. `TestCodiciMessaggiSistema`
7. `TestCodiciOutputUiUmani`

Questa scelta rende il file leggibile, evita dispersione in molti moduli micro-test e mantiene
allineato il perimetro del Gruppo A a un singolo artefatto implementativo.

#### Decisione 2 - Test di contratto, non test di implementazione interna

Le asserzioni non devono dipendere da dettagli accidentali come ordine fisico delle righe,
commenti o stile di dichiarazione. Il contratto osservabile e' limitato a:

- simboli esportati e importabili
- valore stringa delle costanti
- insieme dei valori ammessi dai Literal

Questa scelta minimizza la fragilita' del test rispetto a refactor non funzionali.

#### Decisione 3 - Asserzioni per modulo differenziate in base al tipo di contenuto

I moduli si dividono in due famiglie.

Famiglia A, solo costanti stringa esplicite:

- [bingo_game/events/codici_configurazione.py](../../bingo_game/events/codici_configurazione.py)
- [bingo_game/events/codici_controller.py](../../bingo_game/events/codici_controller.py)
- [bingo_game/events/codici_eventi.py](../../bingo_game/events/codici_eventi.py)
- [bingo_game/events/codici_loop.py](../../bingo_game/events/codici_loop.py)
- [bingo_game/events/codici_messaggi_sistema.py](../../bingo_game/events/codici_messaggi_sistema.py)

Per questi moduli il design richiede:

- test di importabilita'
- test del valore esatto di ogni costante pubblica
- test di allineamento con il Literal, se il Literal esiste nel modulo

Famiglia B, Literal senza costanti Final corrispondenti complete:

- [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)
- [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py)

Per questi moduli il design richiede:

- test di importabilita'
- test di contenuto del Literal rispetto all'insieme atteso
- test di copertura, unione e assenza di sovrapposizioni quando applicabile

Questa distinzione evita di imporre una forma di asserzione incompatibile con moduli che non espongono
costanti Final nominali per ogni chiave.

#### Decisione 4 - codici_errori usa test di teoria degli insiemi

Per [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) il fulcro non e'
il confronto nome-costante/valore, ma la validazione di tre proprieta':

- completezza dell'unione dei tre Literal specifici
- assenza di duplicati tra gruppi
- allineamento del contratto aggregato `Codici_Errori`

Le asserzioni dovranno quindi essere espresse come confronti tra insiemi e intersezioni vuote.

#### Decisione 5 - Nessun mock, nessuna fixture, nessuna dipendenza esterna

Il Gruppo A non richiede mock, fixture condivise, file temporanei o avvio del motore.
Il file di test deve dipendere solo da:

- `unittest`
- `typing.get_args`
- import diretti dai sette moduli target

Questo mantiene la suite veloce, deterministica e coerente con il runner `unittest`.

### Struttura interna attesa del file di test

Il file [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py) dovra' essere organizzato in questo ordine:

1. import `unittest` e helper di typing necessari
2. import dei sette moduli o dei simboli necessari per ogni classe
3. definizione di classi che estendono `unittest.TestCase`; i metodi di test devono seguire il prefisso `test_`
4. sette classi di test nell'ordine fissato dal Gruppo A
5. metodi `test_<scenario>` focalizzati su un solo contratto osservabile per volta

Non sono previsti helper privati complessi. Se servira' un supporto comune, dovra' essere ridotto
alla sola estrazione dei valori di un Literal per non mescolare logica di produzione nel test.

### Scenari esatti da coprire per classe

#### TestCodiciConfigurazione

- Import del modulo riuscito.
- Presenza delle costanti previste dal contratto del report.
- Per ogni costante, uguaglianza tra valore esportato e stringa attesa.

Forma attesa delle asserzioni:

- confronto diretto costante = stringa attesa
- eventuale confronto tra insieme dei nomi attesi e simboli effettivamente presenti

#### TestCodiciController

- Import del modulo riuscito.
- Valore esatto delle quattro costanti controller.
- Assenza di costanti mancanti rispetto al set atteso.

Forma attesa delle asserzioni:

- confronto diretto simbolo = stringa attesa
- confronto insiemistico del catalogo costanti attese

#### TestCodiciErrori

- Import del modulo riuscito.
- Contenuto esatto di `Codici_Errori_Generici`.
- Contenuto esatto di `Codici_Errori_Ui`.
- Contenuto esatto di `Codici_Errori_Partita`.
- Intersezione vuota tra i tre gruppi.
- Uguaglianza tra unione dei tre gruppi e insieme atteso di `Codici_Errori`.

Forma attesa delle asserzioni:

- confronto set = set atteso
- confronto intersezione = insieme vuoto
- confronto unione = insieme atteso globale

#### TestCodiciEventi

- Import del modulo riuscito.
- Valore esatto di `EVENTO_FOCUS_AUTO_IMPOSTATO`.
- Allineamento tra costante Final e `Codici_Eventi`.

Forma attesa delle asserzioni:

- confronto diretto costante = stringa attesa
- confronto tra insieme delle costanti pubbliche e valori del Literal

#### TestCodiciLoop

- Import del modulo riuscito.
- Valore esatto delle otto costanti loop.
- Coerenza completa tra costanti Final e `Codici_Loop`.

Forma attesa delle asserzioni:

- confronto diretto costante = stringa attesa
- uguaglianza tra insieme valori costanti e insieme valori Literal

#### TestCodiciMessaggiSistema

- Import del modulo riuscito.
- Valore esatto di ogni costante di messaggio sistema.
- Coerenza completa tra costanti Final e `Codici_Messaggi_Sistema`.

Forma attesa delle asserzioni:

- confronto diretto costante = stringa attesa
- uguaglianza tra insieme valori costanti e insieme valori Literal

#### TestCodiciOutputUiUmani

- Import del modulo riuscito.
- Contenuto esatto del Literal `Codici_Output_Ui_Umani` rispetto al set atteso di chiavi.
- Nessun duplicato semantico nel set risultante.

Forma attesa delle asserzioni:

- confronto set = set atteso
- confronto di cardinalita' tra sequenza dichiarata e insieme risultante per rilevare duplicati

### Dipendenze di import necessarie

Import di supporto previsti:

- `import unittest`
- `from typing import get_args`

Import modulo target previsti:

- `from bingo_game.events import codici_configurazione`
- `from bingo_game.events import codici_controller`
- `from bingo_game.events import codici_errori`
- `from bingo_game.events import codici_eventi`
- `from bingo_game.events import codici_loop`
- `from bingo_game.events import codici_messaggi_sistema`
- `from bingo_game.events import codici_output_ui_umani`

Non sono previste dipendenze da:

- wxPython
- mock
- filesystem
- controller o avvio partita

### Rischi e Vincoli

- Vincolo di scope: nessun test fuori dal Gruppo A puo' entrare in questo file.
- Vincolo di forma: il file deve restare uno solo, in [tests/unit/](../../tests/unit/).
- Rischio di false assunzioni: i moduli senza costanti Final complete non devono essere forzati in uno schema di test errato.
- Rischio di drift documentale: il set atteso delle chiavi deve derivare esclusivamente dai sette moduli del perimetro e dal report padre, non da ipotesi su moduli futuri.
- Vincolo operativo: nessuna modifica a file esistenti fuori da [tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py) nel ciclo implementativo derivato da questo design.

### Coding plans correlati

- [PLAN_test_codici_eventi_v1.0.0.md](../3%20-%20coding%20plans/PLAN_test_codici_eventi_v1.0.0.md)

### Criteri di completamento verificabili

Il design si considera soddisfatto quando il futuro file
[tests/unit/test_codici_eventi.py](../../tests/unit/test_codici_eventi.py):

- contiene esattamente sette classi di test, una per modulo del Gruppo A
- applica la struttura `unittest.TestCase` in modo uniforme
- verifica importabilita' di tutti e sette i moduli
- verifica il valore stringa delle costanti dove il modulo espone costanti nominali
- verifica la coerenza con Literal dove il Literal e' parte del contratto del modulo
- verifica per [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py) completezza, unione e assenza di sovrapposizioni
- non introduce test relativi ai Gruppi B, C, D o E

## Stato Avanzamento

- [x] Bozza completata
- [x] Revisionato
- [x] Approvato
- [ ] Archiviato