---
type: report
feature: fix_test_destra_avanzata_rifinitura
agent: Agent-Analyze
status: DRAFT
date: 2026-03-29
title: Report analisi rifinitura test colonna destra avanzata
---

## Metadati

- tipo: report
- titolo: Report analisi rifinitura test colonna destra avanzata
- data_creazione: 2026-03-29
- agente: Agent-Analyze
- stato: bozza
- feature: fix_test_destra_avanzata_rifinitura
- versione_target: v1.0

## Trigger

Questa rifinitura nasce dalla **validazione post-Tranche 3**, non da una nuova
analisi del codice produttivo.

Dopo la Tranche 3 (modernizzazione test colonna destra, feature
`fix_test_colonna_destra_eventi`), la revisione delle assertion introdotte ha
evidenziato due asimmetrie nei test della variante avanzata destra: un campo
evento verificato nelle case di errore ma non nella case di successo, e una
asserzione condizionale che puo' essere silenziosamente saltata. Lo stesso
pattern di fragilita' condizionale e' presente in modo simmetrico anche nel test
corrispondente della variante sinistra avanzata.

Nessuna regressione e' stata rilevata nel codice applicativo. Il perimetro di
intervento e' limitato a `tests/test_giocatore_umano.py`.

## Sommario Esecutivo

Tipo intervento: rifinitura assertion di test gia' modernizzati
Scope: 3 test in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
Codice applicativo: **nessuna modifica prevista**

I test da correggere sono:

1. `test_sposta_focus_colonna_destra_avanzata_movimento_normale` — incompleto:
   manca la verifica esplicita che `risultato.evento.limite` sia `None` nel
   caso di movimento riuscito.

2. `test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni` —
   fragile: la verifica sul numero segnato e' condizionale (`if numero_da_segnare
   is not None`) e puo' essere saltata silenziosamente se la colonna 4 della
   cartella di test risulta vuota.

3. `test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni` —
   stessa fragilita' simmetrica: la verifica sul numero segnato e' condizionale
   (`if numero_da_segnare is not None`) e puo' essere saltata se la colonna 3
   risulta vuota.

Il contratto di `EsitoAzione` e degli eventi non cambia; si corregge solo la
**completezza e l'incondizionalita' delle asserzioni** nei test gia'
modernizzati.

## Componenti Coinvolti

- [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)

Nessun altro file e' coinvolto. Il codice applicativo e la struttura degli
eventi non richiedono modifiche.

## Diagnosi Puntuale dei Tre Test

### 1. test_sposta_focus_colonna_destra_avanzata_movimento_normale (riga 1421)

Contesto: verifica spostamento normale da indice 3 a indice 4 (colonna 5,
1-based) con la variante avanzata.

Asserzioni presenti:

- `assertTrue(risultato.ok)`
- `assertIsNone(risultato.errore)`
- `assertIsInstance(risultato.evento, EventoNavigazioneColonnaAvanzata)`
- `assertEqual(risultato.evento.esito, "mostra")`
- `assertEqual(risultato.evento.numero_colonna_corrente, 5)`
- `assertEqual(risultato.evento.colonna_semplice, dati_attesi[0])`
- `assertEqual(risultato.evento.stato_colonna, dati_attesi[1])`
- `assertEqual(risultato.evento.numeri_segnati_colonna_ordinati, dati_attesi[2])`
- `assertEqual(self.giocatore._indice_colonna_focus, 4)`

Asserzione mancante:

```python
self.assertIsNone(risultato.evento.limite)
```

Motivazione: il test `test_sposta_focus_colonna_destra_avanzata_ultima_colonna`
verifica esplicitamente `assertEqual(risultato.evento.limite, "massimo")` per il
caso limite, e verifica a `None` i campi payload. Per simmetria, il caso di
movimento riuscito deve verificare esplicitamente che `limite` sia `None`.
Senza questa asserzione, una regressione che popola `limite` in caso di successo
sarebbe non rilevata.

### 2. test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni (riga 1470)

Contesto: verifica il payload strutturato della colonna avanzata in presenza di
numeri segnati. Spostamento da indice 3 a indice 4 (colonna 5, 1-based).

Scenario del test: la colonna 4 (1-based) viene interrogata con
`self.cartella1.get_numeri_colonna(4)`; se la lista non e' vuota, il primo
numero viene segnato con `segna_numero`.

Fragilita' rilevata: la verifica del numero segnato e' condizionale:

```python
if numero_da_segnare is not None:
    self.assertIn(numero_da_segnare, risultato.evento.numeri_segnati_colonna_ordinati)
```

Se `get_numeri_colonna(4)` restituisce lista vuota per la cartella di test,
`numero_da_segnare` vale `None` e l'unica assertion sullo stato dei segni viene
saltata silenziosamente. Il test passa senza aver verificato il comportamento
con numeri segnati.

Correzione attesa: garantire che la condizione sia sempre vera, oppure refactorare
il test per usare `unittest.skipIf` esplicito e un test separato con fixture
sempre valorizzata; in alternativa, scegliere una colonna la cui presenza di
numeri sia garantita dalla cartella di test.

### 3. test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni (riga 1330)

Contesto: verifica il payload strutturato della colonna sinistra avanzata in
presenza di numeri segnati. Spostamento da indice 4 a indice 3 (colonna 4,
1-based).

Fragilita' rilevata: stessa struttura condizionale simmetrica:

```python
if numero_da_segnare is not None:
    self.assertIn(numero_da_segnare, risultato.evento.numeri_segnati_colonna_ordinati)
```

Se `get_numeri_colonna(3)` restituisce lista vuota, la verifica del numero
segnato viene saltata. Il problema e' identico per natura e per impatto al test
destra corrispondente.

Nota: questo test appartiene alla variante sinistra avanzata. Viene incluso in
questa rifinitura per coerenza simmetrica con la destra, non perche' sia emerso
da un fallimento indipendente.

## Contratto Atteso Confermato

Il contratto di `EsitoAzione` e degli eventi strutturati non cambia:

- `EventoNavigazioneColonnaAvanzata` continua a esporre: `esito`, `limite`,
  `numero_colonna_corrente`, `colonna_semplice`, `stato_colonna`,
  `numeri_segnati_colonna_ordinati`.
- In caso di movimento riuscito (`esito="mostra"`): `limite` deve essere `None`,
  gli altri campi payload devono essere valorizzati.
- In caso di limite (`esito="limite"`): `limite` valorizzato, campi payload a
  `None`.

Nessuna modifica alle firme dei metodi, alla struttura degli eventi o al codice
applicativo e' richiesta da questa rifinitura.

## Dipendenze

Documenti di riferimento della Tranche 3:

- [docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md](docs/4%20-%20reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md)
- [docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md](docs/2%20-%20projects/DESIGN_fix_test_colonna_destra_eventi.md)
- [docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md](docs/3%20-%20coding%20plans/PLAN_fix_test_colonna_destra_eventi_v1.md)

Documenti di contesto delle tranches precedenti:

- [docs/4 - reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md](docs/4%20-%20reports/REPORT_FIX_TEST_COLONNA_SINISTRA_EVENTI_2026-03-29.md)
- [docs/4 - reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md](docs/4%20-%20reports/REPORT_FIX_TEST_RIGA_EVENTI_2026-03-29.md)
