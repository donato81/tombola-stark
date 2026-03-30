---
type: design
feature: allineamento_standard_tabellone
agent: Agent-Design
status: DRAFT
version: v1.0.0
date: 2026-03-31
report_ref: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md
---

## Metadati

tipo: design
titolo: Allineamento standard formale di bingo_game/tabellone.py
data_creazione: 2026-03-31
agente: Agent-Design
stato: draft
feature: allineamento_standard_tabellone
versione_progetto: v1.0.0
report: docs/4 - reports/REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md

## Contenuto

### Idea in 3 righe

Questo ciclo allinea `bingo_game/tabellone.py` agli standard formali gia'
adottati nel resto del nucleo del progetto, senza introdurre alcuna modifica
comportamentale. L'intervento copre esclusivamente le incoerenze I-01, I-02,
I-03, I-04 e I-05 del report di riferimento. L'obiettivo e' rendere il modulo
coerente con i pattern di `partita.py` e `giocatore_base.py` su type hints,
docstring e struttura documentativa.

### Attori e concetti

#### Attori

- `Tabellone`
- `bingo_game/tabellone.py`
- report `REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md`
- file modello `bingo_game/partita.py`
- file modello `bingo_game/players/giocatore_base.py`
- suite `tests/unit`

#### Concetti

- allineamento formale del modulo
- annotazioni di tipo su firme e attributi
- module docstring e class docstring
- docstring Python uniformi sui metodi pubblici e di supporto
- invarianza comportamentale della logica di gioco

### Flussi concettuali

1. Si assume come fonte di verita' esclusiva il report `REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md`.
2. Si interviene solo su `bingo_game/tabellone.py` con modifiche formali: import, type hints, docstring di modulo/classe e docstring dei metodi.
3. Non si modifica alcun ramo logico, alcuna condizione, alcun `return`, alcuna eccezione e alcun algoritmo del tabellone.
4. La chiusura del ciclo e' subordinata alla suite `python -m unittest discover tests/unit` con zero failure e zero error.

### Decisioni architetturali

#### Obiettivo del ciclo

Il ciclo corregge esclusivamente le seguenti incoerenze del report:

- **I-01**: aggiunta di `from __future__ import annotations` e degli import di typing necessari.
- **I-02**: aggiunta delle annotazioni di ritorno mancanti sulle firme dei metodi.
- **I-03**: aggiunta delle annotazioni di tipo agli attributi di istanza inizializzati in `_inizializza_tabellone()`.
- **I-04**: aggiunta di module docstring e class docstring secondo il pattern del progetto.
- **I-05**: aggiunta di docstring Python ai 7 metodi che oggi hanno solo commenti inline.

La motivazione e' chiudere il disallineamento formale del modulo core che oggi risulta meno tipizzato e meno documentato rispetto agli altri file del nucleo.

#### Elenco completo delle modifiche attese su `tabellone.py`

##### I-01 - Import iniziale del modulo

Sezione coinvolta:

- riga iniziale del file, prima di `import random`

Modifica attesa:

- aggiunta di `from __future__ import annotations`
- aggiunta degli import necessari di typing, in particolare `Any`

Risultato atteso:

- il modulo segue il medesimo bootstrap tipizzato di `partita.py` e `giocatore_base.py`;
- il file puo' usare annotazioni moderne come `int | None`, `list[int]`, `dict[str, Any]` in modo uniforme e compatibile con gli strumenti statici.

##### I-02 - Firme dei metodi senza annotazione di ritorno

Sezioni coinvolte:

- costruttore `__init__`
- sezione "metodi di creazione del tabellone"
- sezione "metodi di stato/controllo"
- blocco finale dei metodi di query sullo stato

Metodi da annotare:

- `__init__` -> `None`
- `_inizializza_tabellone` -> `None`
- `estrai_numero` -> `int`
- `reset_tabellone` -> `None`
- `numeri_terminati` -> `bool`
- `gestione_errore_numeri_terminati` -> `None`
- `get_conteggio_estratti` -> `int`
- `get_conteggio_disponibili` -> `int`
- `get_numeri_estratti` -> `list[int]`
- `get_numeri_disponibili` -> `list[int]`
- `get_percentuale_avanzamento` -> `float`
- `get_ultimo_numero_estratto` -> `int | None`
- `get_stato_tabellone` -> `dict[str, Any]`

Risultato atteso:

- tutte le firme di `Tabellone` risultano esplicite e allineate allo standard del progetto;
- i valori di ritorno gia' esistenti restano invariati, cambia solo la formalizzazione del contratto.

##### I-03 - Attributi inizializzati in `_inizializza_tabellone()`

Sezione coinvolta:

- metodo `_inizializza_tabellone()`

Attributi da annotare:

- `self.numeri_disponibili: set[int]`
- `self.numeri_estratti: set[int]`
- `self.ultimo_numero_estratto: int | None`
- `self.storico_estrazioni: list[int]`

Risultato atteso:

- lo stato interno del tabellone e' descritto in modo esplicito;
- il file risulta coerente con il pattern gia' usato in `partita.py` e `giocatore_base.py` per gli attributi di istanza.

##### I-04 - Docstring di modulo e di classe

Sezioni coinvolte:

- apertura del file
- blocco immediatamente successivo a `class Tabellone:`

Modifica attesa:

- aggiunta di una module docstring descrittiva che presenti scopo del modulo, responsabilita' della classe e note d'uso essenziali;
- aggiunta di una class docstring che descriva il ruolo di `Tabellone` nella partita.

Risultato atteso:

- il file adotta la stessa struttura documentativa di `partita.py` e `giocatore_base.py`;
- l'intento del modulo e della classe diventa leggibile senza ispezionare l'implementazione.

##### I-05 - Docstring Python sui 7 metodi privi

Sezioni coinvolte:

- `_inizializza_tabellone`
- `estrai_numero`
- `reset_tabellone`
- `numeri_terminati`
- `gestione_errore_numeri_terminati`
- `get_numeri_estratti`
- `get_numeri_disponibili`

Modifica attesa:

- sostituzione del solo commento descrittivo inline come fonte principale di documentazione;
- introduzione di docstring coerenti con quelle gia' presenti nel file, includendo quando utile scopo, ritorno e comportamento osservabile.

Risultato atteso:

- il modulo non presenta piu' una mescolanza tra metodi con docstring estesa e metodi con soli commenti;
- la leggibilita' interna del file diventa uniforme.

#### Garanzia di invarianza comportamentale

Le modifiche previste non possono alterare la logica di gioco perche':

- `from __future__ import annotations` influenza solo la valutazione delle annotazioni, non il flusso runtime del tabellone;
- i type hint di firma e di attributo non cambiano i valori assegnati, i rami decisionali o gli effetti collaterali;
- module docstring, class docstring e method docstring sono contenuto documentale, non istruzioni eseguibili della logica applicativa;
- nessuna delle modifiche previste tocca `random.choice`, la manipolazione dei set, la cronologia delle estrazioni o la gestione dell'errore corrente.

Per questo motivo il ciclo e' formalmente a rischio basso: migliora espressivita' e tipizzazione del codice senza alterarne il comportamento osservabile.

#### Pattern di riferimento

I modelli stilistici di riferimento per questo ciclo sono:

- `bingo_game/partita.py`
- `bingo_game/players/giocatore_base.py`

Questi file vengono usati come baseline per:

- presenza di `from __future__ import annotations`;
- annotazione esplicita di attributi e ritorni;
- struttura con module docstring e class docstring;
- stile generale delle docstring descrittive.

### Rischi e vincoli

#### Rischi

- rischio principale: introdurre incoerenze sintattiche nelle annotazioni se i tipi non vengono trascritti esattamente come definiti dal report;
- rischio secondario: docstring formulate in modo non coerente con il lessico gia' presente nel file.

#### Vincoli

- il report `REPORT_ANALISI_INCOERENZE_TABELLONE_2026-03-31.md` e' l'unica fonte di verita' ammessa per il contenuto del ciclo;
- nessuna modifica logica e' consentita in `bingo_game/tabellone.py`;
- il ciclo si ferma dopo Fase 3: design, plan, TODO specifico e aggiornamento del coordinatore generale;
- l'avvio dell'implementazione richiede validazione umana successiva.

### Cosa non rientra in questo ciclo

Sono esplicitamente esclusi:

- incoerenza **I-06** relativa a `ValueError` e alle eccezioni di dominio;
- incoerenza **I-07** relativa alle string literals usate come separatori di sezione;
- qualsiasi modifica a file Python diversi da `bingo_game/tabellone.py`;
- qualsiasi modifica ai file di test esistenti;
- creazione di nuovi test;
- qualsiasi intervento su `bingo_game/exceptions/tabellone_exceptions.py`;
- qualsiasi inizio della Fase 4 di implementazione all'interno di questo ciclo.
