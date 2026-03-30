## Metadati

tipo: report
titolo: Analisi moduli di validazione per suite unittest dedicata
data_creazione: 2026-03-30
agente: Agent-Orchestrator
stato: validato

## Contenuto

### Trigger

Analisi preliminare per creare una suite di test unitari diretta e isolata
per i moduli bingo_game/validations/validazioni_input.py e
bingo_game/validations/validazione_oggetti.py, con vincolo esplicito di
uso esclusivo di unittest.

### Sommario esecutivo

I due moduli di validazione espongono in totale otto funzioni e oggi non
sono coperte da test diretti. La copertura esistente e' solo indiretta,
quasi interamente tramite tests/test_giocatore_umano.py.

validazioni_input.py contiene sei funzioni pure o quasi pure che validano
tipo, range, stato del reclamo e whitelist del tipo di vittoria. Tutte
restituiscono EsitoAzione e non dipendono da stato esterno.

validazione_oggetti.py contiene due funzioni di validazione strutturale.
esito_tabellone_disponibile accetta sia un Tabellone reale sia oggetti
duck-typed compatibili. esito_coordinate_numero_coerenti dipende da
cartella.get_coordinate_numero(numero) e, in alcuni casi, puo' propagare
eccezioni dal chiamato.

La futura suite puo' essere costruita in due file unittest in tests/unit,
senza dipendere da altri componenti del gioco e senza usare pytest.

### Componenti coinvolti

- bingo_game/validations/validazioni_input.py
- bingo_game/validations/validazione_oggetti.py
- bingo_game/events/eventi.py per EsitoAzione
- bingo_game/tabellone.py per il controllo isinstance in esito_tabellone_disponibile
- bingo_game/cartella.py per il contratto get_coordinate_numero usato in duck typing
- bingo_game/players/giocatore_umano.py come principale chiamante applicativo indiretto
- tests/test_giocatore_umano.py come principale copertura indiretta attuale

### Dipendenze

- Tutte le funzioni restituiscono EsitoAzione.
- esito_numero_in_range_1_90 richiama esito_numero_intero.
- esito_numero_riga_in_range_1_3 richiama esito_numero_intero.
- esito_numero_colonna_in_range_1_9 richiama esito_numero_intero.
- esito_tabellone_disponibile usa isinstance(tabellone, Tabellone) e
  accetta anche oggetti che espongono is_numero_estratto oppure
  get_numeri_estratti.
- esito_coordinate_numero_coerenti chiama cartella.get_coordinate_numero(numero)
  e non intercetta eccezioni del metodo chiamato.

### Dettaglio osservazioni

#### a) Panoramica di ciascun modulo

##### Modulo: bingo_game/validations/validazioni_input.py

Numero funzioni: 6

Scopo generale:
- centralizzare validazioni di input riutilizzabili nel dominio applicativo;
- uniformare i fallimenti su codici errore di EsitoAzione;
- evitare eccezioni per i casi di input non valido piu' comuni.

Tipo di ritorno:
- tutte le funzioni ritornano EsitoAzione.

Funzioni presenti:
- esito_numero_intero
- esito_numero_in_range_1_90
- esito_numero_riga_in_range_1_3
- esito_numero_colonna_in_range_1_9
- esito_reclamo_turno_libero
- esito_tipo_vittoria_supportato

##### Modulo: bingo_game/validations/validazione_oggetti.py

Numero funzioni: 2

Scopo generale:
- verificare prerequisiti strutturali su oggetti di dominio prima di
  creare eventi o proseguire il flusso applicativo;
- trasformare alcune incoerenze in EsitoAzione, pur lasciando emergere
  eccezioni in alcuni casi non gestiti.

Tipo di ritorno:
- entrambe le funzioni ritornano EsitoAzione.

Funzioni presenti:
- esito_tabellone_disponibile
- esito_coordinate_numero_coerenti

#### b) Mappa funzione per funzione

##### esito_numero_intero(numero: object) -> EsitoAzione

Parametri accettati:
- numero: atteso int stretto; bool non e' accettato perche' il controllo e'
  type(numero) is int.

Input valido:
- restituisce ok=True, errore=None, evento=None.

Input non valido:
- float, str, None, bool e ogni non-int restituiscono
  ok=False, errore="NUMERO_TIPO_NON_VALIDO", evento=None.

Codici errore:
- NUMERO_TIPO_NON_VALIDO

Dipendenze:
- nessuna.

##### esito_numero_in_range_1_90(numero: object) -> EsitoAzione

Parametri accettati:
- numero: int compreso tra 1 e 90 inclusi.

Input valido:
- 1, 90 e qualsiasi intero nel range restituiscono ok=True.

Input non valido:
- tipo errato: propaga l'esito di esito_numero_intero con
  NUMERO_TIPO_NON_VALIDO;
- 0, negativi e valori maggiori di 90 restituiscono NUMERO_NON_VALIDO.

Codici errore:
- NUMERO_TIPO_NON_VALIDO
- NUMERO_NON_VALIDO

Dipendenze:
- esito_numero_intero.

##### esito_numero_riga_in_range_1_3(numero: object) -> EsitoAzione

Parametri accettati:
- numero: int compreso tra 1 e 3 inclusi.

Input valido:
- 1, 2, 3 restituiscono ok=True.

Input non valido:
- tipo errato: NUMERO_TIPO_NON_VALIDO;
- 0, negativi, 4 o superiori: NUMERO_RIGA_FUORI_RANGE.

Codici errore:
- NUMERO_TIPO_NON_VALIDO
- NUMERO_RIGA_FUORI_RANGE

Dipendenze:
- esito_numero_intero.

##### esito_numero_colonna_in_range_1_9(numero: object) -> EsitoAzione

Parametri accettati:
- numero: int compreso tra 1 e 9 inclusi.

Input valido:
- 1 e 9, oltre ai valori centrali, restituiscono ok=True.

Input non valido:
- tipo errato: NUMERO_TIPO_NON_VALIDO;
- 0, negativi, 10 o superiori: NUMERO_COLONNA_FUORI_RANGE.

Codici errore:
- NUMERO_TIPO_NON_VALIDO
- NUMERO_COLONNA_FUORI_RANGE

Dipendenze:
- esito_numero_intero.

##### esito_reclamo_turno_libero(reclamo_turno: object) -> EsitoAzione

Parametri accettati:
- reclamo_turno: qualunque object; l'unico caso valido e' None.

Input valido:
- None restituisce ok=True.

Input non valido:
- qualsiasi valore non None, anche falsy come 0, False o stringa vuota,
  restituisce RECLAMO_GIA_PRESENTE.

Codici errore:
- RECLAMO_GIA_PRESENTE

Dipendenze:
- nessuna.

##### esito_tipo_vittoria_supportato(tipo_vittoria: object) -> EsitoAzione

Parametri accettati:
- tipo_vittoria: attesa una stringa tra tombola, ambo, terno, quaterna,
  cinquina.

Input valido:
- ciascuno dei cinque valori supportati restituisce ok=True.

Input non valido:
- stringa sconosciuta, None, interi o stringhe con maiuscole diverse
  restituiscono TIPO_VITTORIA_NON_VALIDO.

Codici errore:
- TIPO_VITTORIA_NON_VALIDO

Dipendenze:
- nessuna.

##### esito_tabellone_disponibile(tabellone: object) -> EsitoAzione

Parametri accettati:
- tabellone: istanza Tabellone oppure oggetto compatibile che esponga
  is_numero_estratto o get_numeri_estratti.

Input valido:
- Tabellone reale restituisce ok=True;
- mock o stub con almeno uno dei due metodi compatibili restituisce ok=True.

Input non valido:
- None, object(), dict, stringa o oggetto privo dei metodi compatibili
  restituiscono TABELLONE_NON_DISPONIBILE.

Codici errore:
- TABELLONE_NON_DISPONIBILE

Dipendenze:
- Tabellone
- hasattr su is_numero_estratto e get_numeri_estratti.

##### esito_coordinate_numero_coerenti(cartella, numero: int) -> EsitoAzione

Parametri accettati:
- cartella: oggetto che esponga get_coordinate_numero(numero);
- numero: int gia' validato idealmente dal chiamante.

Input valido:
- se get_coordinate_numero restituisce una tupla di coordinate non None,
  l'esito e' ok=True.

Input non valido:
- numero non int: INPUTNONVALIDO;
- coordinate None: CARTELLA_STATO_INCOERENTE;
- cartella assente, metodo mancante o eccezione interna del metodo:
  l'eccezione si propaga al chiamante.

Codici errore:
- INPUTNONVALIDO
- CARTELLA_STATO_INCOERENTE

Dipendenze:
- cartella.get_coordinate_numero(numero).

#### c) Copertura attuale

Nessuna delle otto funzioni risulta coperta direttamente da test che la
importino e la invochino in prima persona.

Copertura per funzione:
- esito_numero_intero: coperta solo indirettamente
- esito_numero_in_range_1_90: coperta solo indirettamente
- esito_numero_riga_in_range_1_3: coperta solo indirettamente
- esito_numero_colonna_in_range_1_9: coperta solo indirettamente
- esito_reclamo_turno_libero: coperta solo indirettamente
- esito_tipo_vittoria_supportato: coperta solo indirettamente
- esito_tabellone_disponibile: coperta solo indirettamente
- esito_coordinate_numero_coerenti: coperta solo indirettamente

Principale fonte di copertura indiretta:
- tests/test_giocatore_umano.py

Classificazione complessiva:
- gia' coperta direttamente: nessuna funzione
- coperta solo indirettamente: tutte le otto funzioni
- non coperta affatto in modo osservabile: nessuna funzione, ma alcuni rami
  specifici risultano verosimilmente non esercitati, ad esempio bool rifiutato,
  duck typing del tabellone e propagazione eccezioni in coordinate.

#### d) Casi limite da coprire

Per esito_numero_intero:
- int valido
- bool True e False da rifiutare esplicitamente
- float
- None

Per esito_numero_in_range_1_90:
- bordo inferiore 1
- bordo superiore 90
- 0
- 91
- negativo
- tipo errato

Per esito_numero_riga_in_range_1_3:
- 1
- 3
- 0
- 4
- tipo errato

Per esito_numero_colonna_in_range_1_9:
- 1
- 9
- 0
- 10
- tipo errato

Per esito_reclamo_turno_libero:
- None
- object() non None
- falsy non None come 0 o False

Per esito_tipo_vittoria_supportato:
- ciascun valore ammesso
- stringa sconosciuta
- maiuscolo o case mismatch
- None

Per esito_tabellone_disponibile:
- None
- Tabellone reale
- stub con solo get_numeri_estratti
- stub con solo is_numero_estratto
- object() non compatibile

Per esito_coordinate_numero_coerenti:
- coordinate valide
- coordinate None
- numero non int
- eccezione propagata dal metodo get_coordinate_numero

#### e) Rischi e anomalie

### Rischi

- Mismatch tra docstring e comportamento reale per i codici errore di riga e
  colonna.
- Docstring di esito_tabellone_disponibile piu' restrittiva del codice reale,
  che accetta anche oggetti duck-typed.
- esito_coordinate_numero_coerenti non difende da cartella assente o metodo
  mancante e quindi puo' rompere il contratto "solo EsitoAzione".
- INPUTNONVALIDO usa una forma del codice errore che appare anomala rispetto
  allo stile degli altri codici del progetto.

### Anomalie specifiche

- esito_numero_riga_in_range_1_3: docstring parla di NUMERO_NON_VALIDO ma il
  codice restituisce NUMERO_RIGA_FUORI_RANGE.
- esito_numero_colonna_in_range_1_9: docstring parla di NUMERO_NON_VALIDO ma
  il codice restituisce NUMERO_COLONNA_FUORI_RANGE.
- esito_tabellone_disponibile: comportamento reale piu' permissivo del testo.
- esito_coordinate_numero_coerenti: il nome suggerisce una validazione robusta,
  ma il ramo di errore e' incompleto sui problemi di shape dell'oggetto cartella.

#### f) Proposta di struttura test

File da creare:
- tests/unit/test_validazioni_input.py
- tests/unit/test_validazione_oggetti.py

Organizzazione suggerita:
- una classe unittest.TestCase per gruppo omogeneo di funzioni;
- file input con classi dedicate alle sei funzioni pure;
- file oggetti con classi dedicate alle due funzioni strutturali.

Approccio di isolamento:
- nessun mock necessario per le funzioni pure di validazioni_input.py;
- uso di oggetti reali o stub semplici per esito_tabellone_disponibile;
- uso di stub o MagicMock per la cartella in esito_coordinate_numero_coerenti.

Valutazione purezza:
- esito_numero_intero: pura
- esito_numero_in_range_1_90: pura, dipende solo da funzione interna
- esito_numero_riga_in_range_1_3: pura, dipende solo da funzione interna
- esito_numero_colonna_in_range_1_9: pura, dipende solo da funzione interna
- esito_reclamo_turno_libero: pura
- esito_tipo_vittoria_supportato: pura
- esito_tabellone_disponibile: quasi pura, dipende da shape dell'oggetto
- esito_coordinate_numero_coerenti: non completamente pura, dipende dal metodo
  di un oggetto esterno

Struttura consigliata dei test:
- classi separate per funzione o piccoli gruppi di funzione;
- naming esplicito del tipo test_nomefunzione_scenario_risultato_atteso;
- solo unittest, nessun pytest, nessun test di integrazione.

### Rischi

- Congelare nei test il comportamento reale e non la docstring e' corretto per
  questa fase, ma richiede di documentare chiaramente le divergenze.
- Alcuni rami di esito_coordinate_numero_coerenti potrebbero essere candidati a
  hardening successivo; i test devono esplicitare se si sta caratterizzando il
  comportamento attuale o il contratto desiderato.

### Vincoli accessibilità NVDA

- Nessun impatto UI diretto: le funzioni testate non producono interfaccia.
- I test devono restare lineari, leggibili e con naming descrittivo per
  compatibilita' con output testuale e screen reader.
- Nessun uso di output verboso o framework aggiuntivi che rendano meno
  leggibile il report di unittest.

### File analizzati

- bingo_game/validations/validazioni_input.py
- bingo_game/validations/validazione_oggetti.py
- bingo_game/events/eventi.py
- bingo_game/players/giocatore_umano.py
- bingo_game/cartella.py
- bingo_game/tabellone.py
- tests/test_giocatore_umano.py

## Stato Avanzamento

- [x] Bozza completata
- [x] Revisionato
- [x] Condiviso