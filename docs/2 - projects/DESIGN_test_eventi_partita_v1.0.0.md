---
type: design
feature: test_eventi_partita
agent: Agent-Design
status: DRAFT
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: design
titolo: Design test unitari per factory methods e invarianti di eventi_partita.py
data_creazione: 2026-03-30
agente: Agent-Design
stato: bozza
feature: test_eventi_partita
versione_progetto: v1.0.0
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Idea in 3 righe

Il task definisce il design di un solo file di test, tests/unit/test_eventi_partita.py,
dedicato alle quattro dataclass frozen del Gruppo C nel modulo eventi_partita.py.
L'obiettivo e' congelare factory methods e invarianti di business usando esclusivamente
unittest e asserzioni della standard library, senza anticipare scenari di altri gruppi.

### Obiettivo

Definire il design tecnico del file tests/unit/test_eventi_partita.py limitando il perimetro
al solo Gruppo C del report e alle quattro dataclass del modulo bingo_game/events/eventi_partita.py:

- ReclamoVittoria
- EventoReclamoVittoria
- EventoEsitoReclamoVittoria
- EventoFineTurno

Il design deve fissare:

- la struttura interna del file di test
- le quattro classi di test, una per dataclass, nell'ordine richiesto dal task
- gli scenari esatti da coprire per ciascuna classe con logica di asserzioni in stile unittest
- le dipendenze di import necessarie, inclusa la lettura dei codici di errore di riferimento
- il vincolo esplicito sull'uso di unittest
- la strategia di compatibilita' FrozenInstanceError o AttributeError per i controlli di immutabilita'
- i criteri di completamento verificabili

### Contesto

Il report di riferimento, docs/4 - reports/report_lavori_test_eventi.md, stabilisce che il Gruppo C
copre il modulo eventi_partita.py e riguarda factory methods con invarianti di business critici.

Le quattro dataclass incapsulano regole che non devono regredire silenziosamente:

- tombola deve avere indice_riga=None
- le vittorie di riga devono avere indice_riga valorizzato
- EventoReclamoVittoria.ante_turno deve forzare fase="ANTE_TURNO"
- EventoEsitoReclamoVittoria deve esporre esiti coerenti tra ok ed errore
- EventoFineTurno deve incapsulare in modo trasparente un reclamo opzionale

Il task resta confinato al Gruppo C. Non include scenari relativi a:

- costanti e Literal dei moduli codici_*.py del Gruppo A
- dataclass di focus in eventi_ui.py del Gruppo B
- logica di EsitoAzione in eventi.py del Gruppo D
- classi di eventi_output_ui_umani.py del Gruppo E

### Attori e Concetti

#### Attori

- file di test tests/unit/test_eventi_partita.py
- dataclass ReclamoVittoria
- dataclass EventoReclamoVittoria
- dataclass EventoEsitoReclamoVittoria
- dataclass EventoFineTurno
- unittest come libreria obbligatoria per i test
- FrozenInstanceError come segnale primario di immutabilita'

#### Concetti

- Factory method come punto ufficiale di costruzione degli oggetti
- Invarianti di business gia' codificati nelle factory del modulo
- Coerenza tra esito positivo/negativo e campo errore
- Contesto opzionale nei metodi di esito, tramite indice_turno e numero_estratto
- Immutabilita' delle dataclass frozen come parte del contratto pubblico

### Componenti coinvolti

- File di produzione di riferimento: [bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py)
- File di supporto in sola lettura: [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)
- File da creare in fase implementativa: tests/unit/test_eventi_partita.py
- Riferimento analitico: [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- Coordinatore documentale: [docs/todo.md](../todo.md)

Nessun altro file di test e nessun altro modulo del package events rientrano
nel perimetro di questo design.

### Flussi Concettuali

#### Flusso 1 - ReclamoVittoria tramite factory methods

1. Il test costruisce un reclamo tombola con ReclamoVittoria.tombola(indice_cartella=...).
2. Verifica con self.assertEqual e self.assertIsNone che tipo sia "tombola" e indice_riga sia None.
3. Costruisce reclami di riga con ReclamoVittoria.vittoria_di_riga per i tipi "ambo", "terno",
   "quaterna" e "cinquina".
4. Verifica con self.assertEqual e self.assertIsNotNone che indice_riga sia valorizzato correttamente.
5. Verifica l'immutabilita' con self.assertRaises accettando FrozenInstanceError oppure AttributeError.

#### Flusso 2 - EventoReclamoVittoria.ante_turno

1. Il test prepara un ReclamoVittoria coerente.
2. Invoca EventoReclamoVittoria.ante_turno con i campi richiesti.
3. Verifica con self.assertEqual che fase sia "ANTE_TURNO" e che tutti i campi passati siano preservati.
4. Verifica che il reclamo associato sia esattamente quello fornito al factory method.

#### Flusso 3 - EventoEsitoReclamoVittoria.successo e fallimento

1. Il test prepara un ReclamoVittoria coerente.
2. Invoca successo() e verifica con self.assertTrue, self.assertIsNone e self.assertEqual che ok, errore,
   fase e reclamo siano coerenti.
3. Invoca fallimento() con un codice errore valido, ad esempio "VERIFICA_FALLITA", e verifica con
   self.assertFalse e self.assertEqual la coerenza del payload.
4. Ripete gli scenari con indice_turno e numero_estratto valorizzati per confermare la persistenza
   dei parametri opzionali.

#### Flusso 4 - EventoFineTurno.crea con e senza reclamo

1. Il test invoca EventoFineTurno.crea senza reclamo_turno esplicito.
2. Verifica con self.assertIsNone che reclamo_turno sia None.
3. Prepara un ReclamoVittoria e invoca crea con reclamo_turno valorizzato.
4. Verifica con self.assertIs che reclamo_turno sia esattamente l'oggetto passato.

### Decisioni Architetturali

#### Decisione 1 - Un solo file di test con quattro classi ordinate per dataclass

Il file tests/unit/test_eventi_partita.py conterra' esattamente quattro classi di test,
nell'ordine fissato dal task:

1. TestReclamoVittoria
2. TestEventoReclamoVittoria
3. TestEventoEsitoReclamoVittoria
4. TestEventoFineTurno

Questa scelta mantiene la suite leggibile e aderente al perimetro del modulo.

#### Decisione 2 - unittest e' la sola libreria ammessa

Il file deve usare esclusivamente unittest della standard library.

Il design esclude esplicitamente:

- import pytest
- fixture pytest
- marker pytest come libreria di test

Le asserzioni previste devono essere espresse con primitive unittest, per esempio:

- self.assertEqual
- self.assertIsNone
- self.assertIsNotNone
- self.assertTrue
- self.assertFalse
- self.assertIs
- self.assertRaises

#### Decisione 3 - I codici errore dei test negativi devono derivare da codici_errori.py

Per gli scenari di fallimento di EventoEsitoReclamoVittoria, il design richiede di usare
valori stringa validi definiti in bingo_game/events/codici_errori.py. Il caso guida e'
"VERIFICA_FALLITA", gia' indicato dal report e presente tra i codici del dominio partita.

#### Decisione 4 - Compatibilita' immutabilita' uguale al Gruppo B

I test di immutabilita' devono adottare la stessa strategia del Gruppo B:
accettare FrozenInstanceError come esito primario e AttributeError come fallback compatibile.
Questo evita fragilita' dovute a differenze di esposizione del simbolo in ambienti Python diversi.

#### Decisione 5 - Gli scenari restano sui factory methods e sugli invarianti dichiarati

Il file di test non deve introdurre logica ulteriore o integrazione con Partita, UI, wx,
filesystem o avvio di gioco. La suite deve limitarsi a:

- costruzione corretta degli oggetti tramite factory
- verifica dei valori default e dei campi opzionali
- verifica degli invarianti codificati dal modulo
- verifica di immutabilita' per ReclamoVittoria

### Struttura interna attesa del file di test

Il file tests/unit/test_eventi_partita.py dovra' essere organizzato in questo ordine:

1. import __future__ se coerente con lo stile del repository
2. import unittest
3. import compatibile di FrozenInstanceError con fallback su AttributeError
4. import delle quattro dataclass dal modulo target
5. eventuale import del codice errore usato come riferimento oppure uso del valore stringa letto da codici_errori.py
6. definizione di TestReclamoVittoria(unittest.TestCase)
7. definizione di TestEventoReclamoVittoria(unittest.TestCase)
8. definizione di TestEventoEsitoReclamoVittoria(unittest.TestCase)
9. definizione di TestEventoFineTurno(unittest.TestCase)
10. eventuale entry point unittest.main() se coerente con lo stile del repository

Sono ammessi piccoli helper privati solo se servono a evitare duplicazione nella costruzione di un reclamo valido.

### Scenari esatti da coprire per classe

#### TestReclamoVittoria

- tombola(): tipo="tombola", indice_riga=None.
- vittoria_di_riga() con tipo="ambo": indice_riga valorizzato.
- vittoria_di_riga() con tipo="terno": indice_riga valorizzato.
- vittoria_di_riga() con tipo="quaterna": indice_riga valorizzato.
- vittoria_di_riga() con tipo="cinquina": indice_riga valorizzato.
- immutabilita': tentativo di assegnazione a un campo con attesa di FrozenInstanceError oppure AttributeError.

Forma attesa delle asserzioni:

- self.assertEqual per tipo, indice_cartella, indice_riga
- self.assertIsNone per il caso tombola
- self.assertIsNotNone per i casi di riga
- self.assertRaises per l'immutabilita'

#### TestEventoReclamoVittoria

- ante_turno(): fase="ANTE_TURNO", campi presenti e corretti.

Forma attesa delle asserzioni:

- self.assertEqual per id_giocatore, nome_giocatore, numero_turno, fase
- self.assertIs oppure self.assertEqual per il reclamo associato

#### TestEventoEsitoReclamoVittoria

- successo(): ok=True, errore=None.
- fallimento(): ok=False, errore valorizzato con codice valido, ad esempio "VERIFICA_FALLITA".
- successo() con indice_turno e numero_estratto opzionali valorizzati.
- fallimento() con parametri opzionali valorizzati.

Forma attesa delle asserzioni:

- self.assertTrue per il caso successo
- self.assertFalse per il caso fallimento
- self.assertIsNone per errore nel successo
- self.assertEqual per errore, fase, indice_turno, numero_estratto e campi comuni

#### TestEventoFineTurno

- crea() senza reclamo: reclamo_turno=None.
- crea() con reclamo: reclamo_turno e' il ReclamoVittoria passato.

Forma attesa delle asserzioni:

- self.assertEqual per id_giocatore, nome_giocatore, numero_turno
- self.assertIsNone per il caso senza reclamo
- self.assertIs per il caso con reclamo

### Dipendenze di import necessarie

Import di supporto previsti:

- import unittest
- import compatibile di FrozenInstanceError da dataclasses

Import modulo target previsti:

- from bingo_game.events.eventi_partita import ReclamoVittoria
- from bingo_game.events.eventi_partita import EventoReclamoVittoria
- from bingo_game.events.eventi_partita import EventoEsitoReclamoVittoria
- from bingo_game.events.eventi_partita import EventoFineTurno

Import di riferimento per il caso errore:

- lettura preventiva di bingo_game/events/codici_errori.py durante la fase implementativa
- eventuale uso del valore stringa "VERIFICA_FALLITA" coerente con il modulo

Non sono previste dipendenze da:

- pytest come libreria di test
- wxPython
- mock
- filesystem
- controller o avvio partita

### Vincolo esplicito su unittest

Il design richiede in modo vincolante che il file tests/unit/test_eventi_partita.py
sia implementato con unittest e non con pytest.

L'uso di pytest e' consentito solo come eventuale runner esterno del repository,
non come libreria di test nel contenuto del file.

### Criteri di completamento verificabili

- il file di test e' strutturato in quattro classi nell'ordine richiesto
- ogni scenario del Gruppo C del report e' tracciato in una delle quattro classi
- le asserzioni descritte sono esclusivamente in stile unittest
- la strategia di immutabilita' accetta FrozenInstanceError oppure AttributeError
- il design cita il riferimento a codici_errori.py per il caso di fallimento
- il perimetro non introduce scenari dei Gruppi A, B, D o E

### Rischi e Vincoli

- Vincolo di scope: nessuno scenario oltre eventi_partita.py puo' entrare in questo file.
- Vincolo di libreria: il file non deve contenere import pytest.
- Rischio di drift: usare codici errore non presenti in codici_errori.py renderebbe fragile il test di fallimento.
- Rischio di incompiutezza: omettere i parametri opzionali di EventoEsitoReclamoVittoria lascerebbe scoperto un factory method critico.
- Rischio di regressione: confondere tombola con vittorie di riga romperebbe un invariante di business essenziale.

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Approvato
- [ ] Archiviato