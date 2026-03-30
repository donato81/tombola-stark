---
type: design
feature: test_esito_azione
agent: Agent-Design
status: REVIEWED
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: design
titolo: Design test unitari per EsitoAzione in eventi.py
data_creazione: 2026-03-30
agente: Agent-Design
stato: revisionato
feature: test_esito_azione
versione_progetto: v1.0.0
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Idea in 3 righe

Il task definisce il design di un solo file di test, tests/unit/test_esito_azione.py,
dedicato a EsitoAzione nel modulo eventi.py, che e' il punto con la logica di rendering
di fallback piu' articolata del package events. L'obiettivo e' congelare factory methods,
branch di __str__, comportamento di __eq__ e __contains__ usando esclusivamente unittest.

### Obiettivo

Definire il design tecnico del file tests/unit/test_esito_azione.py limitando il perimetro
al solo Gruppo D del report e al comportamento pubblico della dataclass EsitoAzione in
[bingo_game/events/eventi.py](../../bingo_game/events/eventi.py).

Il design deve fissare:

- la struttura interna del file di test
- le quattro classi di test nell'ordine richiesto dal task
- gli scenari esatti da coprire per ciascuna classe con logica di asserzioni in stile unittest
- i valori stringa attesi dei rami coperti di __str__, ricavati dalla lettura del codice reale
- le dipendenze di import necessarie
- la strategia per gli eventi di supporto usati nei rami successo
- il vincolo esplicito sull'uso di unittest
- i criteri di completamento verificabili

### Contesto

Il report di riferimento, docs/4 - reports/report_lavori_test_eventi.md, stabilisce che il Gruppo D
copre EsitoAzione come unita' isolata e che il rischio principale e' la regressione silenziosa
di __str__, che contiene numerosi rami isinstance e fallback differenziati.

La lettura integrale di [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py) mostra che EsitoAzione espone:

- factory method successo(evento: Optional[EventoAzione] = None)
- factory method fallimento(errore: Codici_Errori)
- __str__ con rami distinti per errore, evento None, eventi focus, eventi di visualizzazione legacy,
  navigazione legacy, EventoSegnazioneNumero, EventoRicercaNumeroInCartelle e fallback generico
- __contains__ che delega a item in str(self)
- __eq__ con comportamento speciale quando other e' una stringa e l'errore e' CARTELLE_NESSUNA_ASSEGNATA
  o FOCUS_CARTELLA_NON_IMPOSTATO

Il task resta confinato al Gruppo D. Non include scenari relativi a:

- contratti dei moduli codici_*.py del Gruppo A
- dataclass di focus come unita' isolate del Gruppo B
- dataclass di partita come unita' isolate del Gruppo C
- classi di visualizzazione e navigazione di eventi_output_ui_umani.py come target primario del Gruppo E

Nota di perimetro importante:
in __str__ esistono ulteriori rami di compatibilita' per eventi di visualizzazione e navigazione,
ma il report del Gruppo D richiede esplicitamente la copertura dei rami costruzione, fallimento,
focus, segnazione, ricerca, fallback generico, __eq__ e __contains__. I rami di visualizzazione/navigazione
restano fuori dal design per non anticipare il Gruppo E.

### Attori e Concetti

#### Attori

- file di test tests/unit/test_esito_azione.py
- dataclass EsitoAzione
- EventoFocusCartellaImpostato
- EventoFocusAutoImpostato
- EventoSegnazioneNumero
- EventoRicercaNumeroInCartelle
- RisultatoRicercaNumeroInCartella
- unittest come libreria obbligatoria per i test

#### Concetti

- successi silenziosi con evento=None
- fallimenti con codice errore e rendering localizzato o fallback
- rendering di successo dipendente dal tipo concreto di evento
- fallback generico su str(evento) per tipi non riconosciuti
- comportamento speciale di confronto con stringhe in __eq__
- containment testuale basato sul rendering finale di __str__

### Componenti coinvolti

- File di produzione target: [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py)
- File di supporto per focus: [bingo_game/events/eventi_ui.py](../../bingo_game/events/eventi_ui.py)
- File di supporto per output umani: [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- File di supporto per codici errore: [bingo_game/events/codici_errori.py](../../bingo_game/events/codici_errori.py)
- File di supporto per codici output: [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py)
- File da creare in fase implementativa: tests/unit/test_esito_azione.py
- Riferimento analitico: [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- Coordinatore documentale: [docs/todo.md](../todo.md)

### Flussi Concettuali

#### Flusso 1 - Costruzione di EsitoAzione

1. Il test invoca EsitoAzione.successo() senza evento.
2. Verifica con self.assertTrue, self.assertIsNone e self.assertIsNone che ok sia True,
   errore sia None ed evento sia None.
3. Invoca EsitoAzione.successo(evento=...) con un evento concreto e verifica con self.assertIs
   che l'evento sia esattamente l'oggetto passato.
4. Invoca EsitoAzione.fallimento("ERRORE_INTERNO") e verifica con self.assertFalse, self.assertEqual,
   self.assertIsNone la coerenza di ok, errore ed evento.

#### Flusso 2 - Rendering di fallimento di __str__

1. Il test costruisce un EsitoAzione di fallimento per ciascun codice mappato richiesto.
2. Verifica con self.assertEqual(str(esito), testo_atteso) il rendering esatto.
3. Verifica anche il caso di errore non mappato, dove il codice usa il fallback f"Errore: {errore}".

Valori attesi ricavati dalla lettura del codice reale di __str__:

- CARTELLE_NESSUNA_ASSEGNATA -> "Errore: Non hai ancora assegnato nessuna cartella."
- FOCUS_CARTELLA_NON_IMPOSTATO -> "Non hai selezionato nessuna cartella"
- NUMERO_NON_VALIDO -> "Errore: numero non valido. Deve essere tra 1 e 90"
- NUMERO_TIPO_NON_VALIDO -> "Errore: tipo numero non valido"
- FOCUS_CARTELLA_FUORI_RANGE -> "Errore: focus cartella fuori range"
- ERRORE_INTERNO -> "Errore: ERRORE_INTERNO"

Lettura di [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py):
il modulo definisce le chiavi semantiche dell'output umano, ma i rami di fallimento di EsitoAzione.__str__
usano stringhe hardcoded nel metodo e non risolvono i testi tramite quei codici. Il design quindi fissa
come fonte autoritativa del testo atteso il codice effettivo di __str__.

#### Flusso 3 - Rendering di successo di __str__

1. Il test verifica il caso evento=None con self.assertEqual(str(esito), "Ok").
2. Costruisce un EventoFocusCartellaImpostato reale e verifica con self.assertIn che il testo contenga
   il numero_cartella, coerentemente con il template "Focus impostato sulla cartella {numero_cartella}.".
3. Costruisce un EventoFocusAutoImpostato reale e verifica con self.assertIn che il testo contenga
   tipo_focus e indice, coerentemente con "Focus auto-impostato su {tipo_focus} {indice}.".
4. Costruisce i quattro casi di EventoSegnazioneNumero con i factory reali del modulo e verifica con
   self.assertEqual il testo atteso per ciascun esito.
5. Costruisce i due casi di EventoRicercaNumeroInCartelle con i factory reali e verifica con self.assertEqual
   il testo non_trovato e con self.assertEqual o self.assertIn i contenuti multiriga del caso trovato.
6. Costruisce un evento di tipo non riconosciuto e verifica con self.assertEqual che str(esito) coincida con str(evento).

Valori attesi ricavati dalla lettura del codice reale di __str__:

- evento=None -> "Ok"
- EventoFocusCartellaImpostato -> "Focus impostato sulla cartella {numero_cartella}."
- EventoFocusAutoImpostato -> "Focus auto-impostato su {tipo_focus} {indice}."
- EventoSegnazioneNumero non_estratto -> "Numero {numero} non è ancora stato estratto"
- EventoSegnazioneNumero non_presente -> "Numero {numero} non è presente nella Cartella {numero_cartella}"
- EventoSegnazioneNumero gia_segnato -> "Numero {numero} è già stato segnato"
- EventoSegnazioneNumero segnato -> "Fatto! Segnato numero {numero}"
- EventoRicercaNumeroInCartelle non_trovato -> "Il numero {numero} non è presente nelle tue cartelle"
- EventoRicercaNumeroInCartelle trovato -> prima riga "Trovato {numero} in:" e poi una riga per risultato con template
  "Cartella {numero_cartella}: Riga {indice_riga + 1} Colonna {indice_colonna + 1} ({stato})"
- fallback generico -> str(evento)

Lettura di [bingo_game/events/codici_output_ui_umani.py](../../bingo_game/events/codici_output_ui_umani.py):
per i casi di segnazione e ricerca il modulo espone chiavi semantiche coerenti con i rami di __str__
come UMANI_SEGNAZIONE_NUMERO_SEGNATO, UMANI_SEGNAZIONE_NUMERO_GIA_SEGNATO,
UMANI_SEGNAZIONE_NUMERO_NON_PRESENTE, UMANI_SEGNAZIONE_NUMERO_NON_ESTRATTO,
UMANI_RICERCA_NUMERO_NON_TROVATO, UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_SINGOLARE,
UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_PLURALE, UMANI_RICERCA_NUMERO_RISULTATO_RIGA,
UMANI_RICERCA_NUMERO_STATO_SEGNATO e UMANI_RICERCA_NUMERO_STATO_DA_SEGNARE.
Il design registra che le chiavi esistono, ma il testo atteso del test resta quello hardcoded in __str__,
perche' EsitoAzione non delega ancora la formattazione a quel dizionario.

#### Flusso 4 - __eq__ e __contains__

1. Il test verifica che una stessa istanza di successo sia uguale a se stessa.
2. Confronta due successi distinti con gli stessi campi e verifica False.
3. Confronta un successo e un fallimento e verifica False.
4. Verifica che una stessa istanza di fallimento sia uguale a se stessa.
5. Confronta due fallimenti distinti con lo stesso codice e verifica False.
6. Verifica __contains__ con una stringa presente nel rendering finale e con una stringa assente.
7. Verifica il comportamento speciale di __eq__ quando other e' stringa.

Comportamento esatto osservato in [bingo_game/events/eventi.py](../../bingo_game/events/eventi.py):

- se errore == CARTELLE_NESSUNA_ASSEGNATA, __eq__(stringa) ritorna True per entrambe le stringhe:
  "Non hai selezionato nessuna cartella"
  "Errore: Non hai ancora assegnato nessuna cartella."
- se errore == FOCUS_CARTELLA_NON_IMPOSTATO, __eq__(stringa) ritorna True per entrambe le stringhe:
  "Non hai selezionato nessuna cartella"
  "Errore: Seleziona prima una cartella su cui segnare il numero."
- in tutti gli altri casi di other stringa, __eq__ confronta str(self) == other
- in tutti i confronti con oggetti non-stringa, __eq__ delega a super().__eq__(other), quindi il comportamento osservato e' di identita' dell'istanza, non di uguaglianza strutturale tra dataclass

### Decisioni Architetturali

#### Decisione 1 - Un solo file di test con quattro classi ordinate per responsabilita'

Il file tests/unit/test_esito_azione.py conterra' esattamente quattro classi nell'ordine:

1. TestEsitoAzioneCostruzione
2. TestEsitoAzioneStrFallimento
3. TestEsitoAzioneStrSuccesso
4. TestEsitoAzioneEqContains

Questa scelta isola nettamente costruzione, rendering di fallimento, rendering di successo e operatori magici.

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
- self.assertIn
- self.assertIs

#### Decisione 3 - Nessun mock per i rami focus, segnazione e ricerca del perimetro Gruppo D

La lettura dei moduli reali mostra che i rami richiesti dal task possono essere costruiti con factory o dataclass reali:

- EventoFocusCartellaImpostato si costruisce direttamente con campi primitivi
- EventoFocusAutoImpostato si costruisce direttamente con campi primitivi
- EventoSegnazioneNumero espone i factory segnato, gia_segnato, non_presente, non_estratto e non richiede Cartella reali
- RisultatoRicercaNumeroInCartella e EventoRicercaNumeroInCartelle espongono factory sufficienti a creare istanze reali

Di conseguenza, per gli scenari richiesti il design prescrive zero mock.

#### Decisione 4 - I rami di visualizzazione e navigazione legacy sono fuori perimetro Gruppo D

Pur essendo presenti nel codice di __str__, i rami per EventoVisualizzaCartellaSemplice,
EventoVisualizzaCartellaAvanzata, EventoVisualizzaTutteCartelleSemplice,
EventoVisualizzaTutteCartelleAvanzata, EventoNavigazioneColonnaAvanzata,
EventoNavigazioneColonna, EventoNavigazioneRiga e EventoNavigazioneRigaAvanzata
non vengono inclusi nel design di Gruppo D, perche' il report li colloca nella famiglia
di eventi output umani del Gruppo E.

#### Decisione 5 - Il testo atteso deve riflettere il codice attuale, non una localizzazione ideale

Il design fissa i valori attesi leggendo il codice reale di __str__. Se in futuro la logica di rendering
verra' spostata sul dizionario dei codici output, questi test dovranno essere aggiornati insieme al contratto.

### Struttura interna attesa del file di test

Il file tests/unit/test_esito_azione.py dovra' essere organizzato in questo ordine:

1. import __future__ se coerente con lo stile del repository
2. import unittest
3. import EsitoAzione dal modulo target
4. import delle classi di supporto necessarie dai moduli eventi_ui e eventi_output_ui_umani
5. eventuale definizione di un piccolo helper locale per costruire risultati di ricerca reali
6. definizione di TestEsitoAzioneCostruzione(unittest.TestCase)
7. definizione di TestEsitoAzioneStrFallimento(unittest.TestCase)
8. definizione di TestEsitoAzioneStrSuccesso(unittest.TestCase)
9. definizione di TestEsitoAzioneEqContains(unittest.TestCase)
10. eventuale entry point unittest.main() se coerente con lo stile del repository

### Scenari esatti da coprire per classe

#### TestEsitoAzioneCostruzione

- successo() senza evento: ok=True, errore=None, evento=None.
- successo() con evento valorizzato: ok=True, evento e' l'oggetto passato.
- fallimento("ERRORE_INTERNO"): ok=False, errore="ERRORE_INTERNO", evento=None.

Forma attesa delle asserzioni:

- self.assertTrue, self.assertFalse
- self.assertIsNone
- self.assertEqual
- self.assertIs

#### TestEsitoAzioneStrFallimento

- CARTELLE_NESSUNA_ASSEGNATA -> "Errore: Non hai ancora assegnato nessuna cartella."
- FOCUS_CARTELLA_NON_IMPOSTATO -> "Non hai selezionato nessuna cartella"
- NUMERO_NON_VALIDO -> "Errore: numero non valido. Deve essere tra 1 e 90"
- NUMERO_TIPO_NON_VALIDO -> "Errore: tipo numero non valido"
- FOCUS_CARTELLA_FUORI_RANGE -> "Errore: focus cartella fuori range"
- ERRORE_INTERNO -> fallback "Errore: ERRORE_INTERNO"

Forma attesa delle asserzioni:

- self.assertEqual(str(esito), testo_atteso)

#### TestEsitoAzioneStrSuccesso

- evento=None -> str(esito) == "Ok"
- evento=EventoFocusCartellaImpostato -> verifica testo con numero_cartella
- evento=EventoFocusAutoImpostato -> verifica testo con tipo_focus e indice
- evento=EventoSegnazioneNumero segnato -> "Fatto! Segnato numero {numero}"
- evento=EventoSegnazioneNumero gia_segnato -> "Numero {numero} è già stato segnato"
- evento=EventoSegnazioneNumero non_presente -> "Numero {numero} non è presente nella Cartella {numero_cartella}"
- evento=EventoSegnazioneNumero non_estratto -> "Numero {numero} non è ancora stato estratto"
- evento=EventoRicercaNumeroInCartelle non_trovato -> "Il numero {numero} non è presente nelle tue cartelle"
- evento=EventoRicercaNumeroInCartelle trovato -> verifica multiriga con intestazione e righe risultato
- evento non riconosciuto -> str(esito) == str(evento)

Forma attesa delle asserzioni:

- self.assertEqual per i casi a testo deterministico completo
- self.assertIn per controllare parti chiave dove il task richiede contenimento del numero_cartella,
  del tipo_focus o dell'indice
- self.assertEqual oppure combinazioni di self.assertIn sul caso multiriga della ricerca trovata

#### TestEsitoAzioneEqContains

- __eq__: stessa istanza successo() -> True
- __eq__: due istanze successo() distinte ma con stessi campi -> False
- __eq__: successo() vs fallimento() -> False
- __eq__: stessa istanza fallimento() -> True
- __eq__: due fallimenti distinti con stesso codice -> False
- __contains__: stringa presente nel rendering -> True
- __contains__: stringa assente nel rendering -> False
- __eq__ con stringa su CARTELLE_NESSUNA_ASSEGNATA -> True per entrambe le varianti lette nel codice
- __eq__ con stringa su FOCUS_CARTELLA_NON_IMPOSTATO -> True per entrambe le varianti lette nel codice

Forma attesa delle asserzioni:

- self.assertTrue e self.assertFalse su ==
- self.assertTrue e self.assertFalse su operatore in

### Dipendenze di import necessarie

Import di supporto previsti:

- import unittest

Import modulo target previsti:

- from bingo_game.events.eventi import EsitoAzione
- from bingo_game.events.eventi_ui import EventoFocusCartellaImpostato
- from bingo_game.events.eventi_ui import EventoFocusAutoImpostato
- from bingo_game.events.eventi_output_ui_umani import EventoSegnazioneNumero
- from bingo_game.events.eventi_output_ui_umani import RisultatoRicercaNumeroInCartella
- from bingo_game.events.eventi_output_ui_umani import EventoRicercaNumeroInCartelle

Import di riferimento per errori e stringhe:

- lettura preventiva di bingo_game/events/codici_errori.py durante la fase implementativa
- lettura preventiva di bingo_game/events/codici_output_ui_umani.py per allineare il design ai codici semantici presenti

### Strategia per oggetti Cartella

Per il perimetro richiesto dal Gruppo D non servono oggetti Cartella reali e non servono MagicMock,
perche' tutti gli eventi usati dai rami coperti dispongono di costruttori reali basati su tipi primitivi.

Il design registra comunque che eventuali mock con unittest.mock.MagicMock sarebbero rilevanti solo per rami
di visualizzazione bulk o cartella del Gruppo E, non per i rami richiesti qui.

### Vincolo esplicito su unittest

Il design richiede in modo vincolante che il file tests/unit/test_esito_azione.py sia implementato
con unittest e non con pytest.

L'uso di pytest e' consentito solo come eventuale runner esterno del repository,
non come libreria di test nel contenuto del file.

### Criteri di completamento verificabili

- il file di test e' strutturato in quattro classi nell'ordine richiesto
- ogni scenario del Gruppo D del report e' tracciato in una delle quattro classi
- il design riporta i valori stringa attesi dei rami coperti di __str__ leggendo il codice reale
- le asserzioni descritte sono esclusivamente in stile unittest
- il design descrive il comportamento speciale di __eq__ con stringhe per i due codici supportati
- il design motiva l'assenza di mock nei rami coperti
- il perimetro non introduce scenari dei Gruppi A, B, C o E

### Rischi e Vincoli

- Vincolo di scope: i rami legacy di visualizzazione e navigazione restano fuori da questo gruppo.
- Vincolo di libreria: il file non deve contenere import pytest.
- Rischio di drift: un cambio del testo hardcoded in __str__ romperebbe i test di rendering, che qui sono volutamente sensibili.
- Rischio di ambiguita': __eq__ con stringa non segue una convenzione standard e deve essere descritto esattamente come nel codice.
- Rischio di incompiutezza: omettere uno dei quattro esiti di EventoSegnazioneNumero lascerebbe scoperto uno dei rami obbligatori.

## Stato Avanzamento

- [x] Bozza completata
- [x] Revisionato
- [x] Approvato
- [ ] Archiviato