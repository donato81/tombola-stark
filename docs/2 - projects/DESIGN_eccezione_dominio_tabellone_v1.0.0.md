---
type: design
feature: eccezione_dominio_tabellone
agent: Agent-Design
status: DRAFT
version: v1.0.0
date: 2026-03-31
report_ref: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md
---

## Metadati

tipo: design
titolo: Introduzione di una eccezione di dominio per il tabellone
data_creazione: 2026-03-31
agente: Agent-Design
stato: draft
feature: eccezione_dominio_tabellone
versione_progetto: v1.0.0
report: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md

## Contenuto

### Idea in 3 righe

Questo ciclo corregge esclusivamente l'incoerenza I-06 del report su
`bingo_game/tabellone.py`, sostituendo un `ValueError` generico con una
eccezione di dominio specifica. L'obiettivo e' allineare il modulo al pattern
eccezioni gia' presente nel progetto, senza alterare il gameplay. La modifica
include anche il test unitario dedicato e la verifica del punto di intercettazione
in `bingo_game/partita.py`.

### Attori e Concetti

#### Attori

- `TabelloneNumeriEsauritiException`
- `bingo_game/exceptions/tabellone_exceptions.py`
- `bingo_game/tabellone.py`
- `bingo_game/partita.py`
- `tests/unit/test_tabellone_eccezioni.py`
- report `REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md`

#### Concetti

- eccezione di dominio specifica
- sostituzione di `ValueError` generico
- adattamento della clausola di intercettazione nel layer applicativo
- test unitario dedicato con `unittest`
- invarianza comportamentale del gameplay

### Flussi Concettuali

1. Il tabellone rileva che non ci sono piu' numeri disponibili.
2. Invece di sollevare `ValueError`, solleva `TabelloneNumeriEsauritiException`
   con lo stesso messaggio testuale gia' in uso.
3. La partita continua a convertire il fallimento del tabellone in
   `PartitaNumeriEsauritiException`, mantenendo invariato il comportamento
   osservabile verso i chiamanti del layer applicativo.
4. Un test unitario diretto verifica sia il tipo di eccezione sia il contenuto
   del messaggio.

### Decisioni Architetturali

#### Obiettivo del ciclo

Il ciclo interviene solo sulla incoerenza **I-06** del report, che segnala in
`bingo_game/tabellone.py` l'uso di `raise ValueError(...)` al posto di una
eccezione di dominio dedicata. Il pattern di riferimento nel progetto e'
quello gia' adottato da eccezioni come `PartitaNumeriEsauritiException` e
`CartellaNumeroTypeException`: errori di dominio espressi con classi nominate,
posizionate nei moduli `*_exceptions.py` del relativo componente.

#### Definizione di `TabelloneNumeriEsauritiException`

Struttura attesa:

- nome classe: `TabelloneNumeriEsauritiException`
- ereditarieta': `Exception`
- docstring descrittiva che spieghi che viene sollevata quando si tenta di
  estrarre un numero da un tabellone che ha esaurito tutti i numeri disponibili

Posizionamento:

- file: `bingo_game/exceptions/tabellone_exceptions.py`

Scelta di gerarchia:

- in questo ciclo la nuova eccezione estende direttamente `Exception`, come
  richiesto dal task;
- non viene introdotta alcuna gerarchia aggiuntiva e non si altera quella
  delle eccezioni gia' esistenti del progetto.

#### Modifica a `gestione_errore_numeri_terminati()`

Situazione attuale attesa:

```python
def gestione_errore_numeri_terminati(self) -> None:
    raise ValueError("Tutti i numeri sono stati estratti. Impossibile estrarre un altro numero.")
```

Situazione finale attesa:

```python
def gestione_errore_numeri_terminati(self) -> None:
    raise TabelloneNumeriEsauritiException(
        "Tutti i numeri sono stati estratti. Impossibile estrarre un altro numero."
    )
```

Vincolo progettuale:

- il messaggio testuale resta identico;
- la firma del metodo resta invariata;
- l'unica variazione e' il tipo di eccezione sollevata.

#### Analisi di `partita.py`

Nel codice attuale `bingo_game/partita.py` usa una intercettazione esplicita di
`ValueError` nel blocco che delega a `self.tabellone.estrai_numero()`:

```python
try:
    numero_estratto = self.tabellone.estrai_numero()
except ValueError as exc:
    raise PartitaNumeriEsauritiException(...) from exc
```

Conclusione del design:

- `partita.py` non intercetta `Exception` generica;
- per mantenere invariato il comportamento runtime sara' necessario aggiornare
  questa clausola da `except ValueError` a
  `except TabelloneNumeriEsauritiException`;
- il mapping verso `PartitaNumeriEsauritiException` resta invariato, quindi il
  layer applicativo continua a presentare lo stesso errore di alto livello ai
  consumer della partita.

#### Strategia di test

Viene creato il file `tests/unit/test_tabellone_eccezioni.py` con `unittest`
esclusivo.

Casi da coprire:

1. `Tabellone.gestione_errore_numeri_terminati()` solleva
   `TabelloneNumeriEsauritiException`.
2. Il messaggio dell'eccezione e' esattamente:
   `"Tutti i numeri sono stati estratti. Impossibile estrarre un altro numero."`

Strategia di implementazione del test:

- istanziare un `Tabellone` reale;
- invocare direttamente `gestione_errore_numeri_terminati()` dentro
  `assertRaises` oppure `assertRaisesRegex`;
- usare solo `unittest`, senza `pytest` e senza modificare test preesistenti.

#### Garanzia di invarianza comportamentale

Il gameplay non cambia perche':

- il punto logico che rileva l'esaurimento dei numeri resta lo stesso;
- il messaggio testuale dell'errore resta identico;
- `partita.py` continuera' a tradurre l'errore del tabellone in
  `PartitaNumeriEsauritiException`, quindi il contratto osservabile a livello
  applicativo non cambia;
- il nuovo test aggiunge copertura senza alterare la suite esistente.

Di conseguenza, il ciclo ha impatto sul tipo di eccezione interna del dominio
Tabellone, ma non modifica il flusso di gioco ne' l'esperienza runtime gia'
presidiata dai test verdi.

### Rischi e Vincoli

#### Rischi

- rischio principale: dimenticare l'aggiornamento della clausola in
  `bingo_game/partita.py`, causando una mancata traduzione dell'eccezione nel
  layer applicativo;
- rischio secondario: introdurre una differenza nel messaggio testuale,
  rompendo i confronti o l'aspettativa documentata dal task.

#### Vincoli

- il report `REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md` e' l'unica
  fonte di verita' ammessa;
- si toccano solo `bingo_game/exceptions/tabellone_exceptions.py`,
  `bingo_game/tabellone.py`, `bingo_game/partita.py` se necessario e il nuovo
  test `tests/unit/test_tabellone_eccezioni.py` nel ciclo di implementazione;
- il ciclo corrente si ferma dopo design, plan, TODO e aggiornamento del
  coordinatore generale.

#### Cosa non rientra in questo ciclo

Sono esplicitamente esclusi:

- modifiche alla logica di gioco del tabellone oltre alla sostituzione del
  tipo di eccezione;
- modifiche ai test esistenti;
- interventi sulle incoerenze I-01, I-02, I-03, I-04, I-05 e I-07;
- introduzione di nuove eccezioni oltre a `TabelloneNumeriEsauritiException`;
- modifiche alla gerarchia delle eccezioni gia' esistenti;
- qualsiasi implementazione di codice in questa fase documentale.
