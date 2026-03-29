---
type: design
feature: fix_test_destra_avanzata_rifinitura
agent: Agent-Design
status: DRAFT
version: v1.0
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md
---

## Metadati

- type: design
- feature: fix_test_destra_avanzata_rifinitura
- agent: Agent-Design
- status: DRAFT
- version: v1.0
- date: 2026-03-29
- report_ref: docs/4 - reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md

## Idea in 3 righe

Si correggono 2 test sulla destra avanzata e 1 sulla sinistra avanzata per
garantire che le asserzioni siano sempre eseguite indipendentemente dalla
distribuzione casuale dei numeri nelle colonne.

## Obiettivo

Definire il perimetro della rifinitura post-Tranche 3 sui test avanzati di
movimento colonna, completando il pattern di asserzione del caso riuscito e
rendendo deterministici i setup con numeri segnati senza introdurre modifiche
al codice produttivo.

## Contesto

La lezione operativa della validazione post-Tranche 3 e' netta: una tranche puo'
chiudere la conversione semantica dei test dai confronti testuali al contratto
strutturato di `EsitoAzione` e restare comunque incompleta se alcune asserzioni
critiche non sono uniformi o se un ramo condizionale puo' saltare la verifica
principale.

La validazione della tranche precedente ha infatti individuato due fragilita'
residue nei test della destra avanzata e una fragilita' simmetrica nella
sinistra avanzata. Non e' emersa alcuna anomalia del comportamento applicativo:
il problema e' interamente nel livello di test e riguarda affidabilita',
completezza e robustezza delle verifiche.

Questa rifinitura si colloca quindi come chiusura tecnica della Tranche 3:
mantiene invariati attori, contratto, metodi e file produttivi, ma irrigidisce
il modo in cui il test dimostra il comportamento atteso anche quando la
distribuzione dei numeri in cartella rende alcune colonne meno affidabili come
fixture implicita.

## Attori e Concetti

### Attori

Gli attori restano gli stessi della Tranche 3. Nessun nuovo attore viene
introdotto.

- `GiocatoreUmano`
- `EsitoAzione`
- `EventoNavigazioneColonnaAvanzata`
- `Cartella`
- [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)

### Concetti

- Movimento riuscito avanzato:
  - `ok=True`
  - `errore=None`
  - `evento.esito == "mostra"`
  - `evento.limite == None`
  - payload avanzato coerente con la colonna raggiunta

- Test robusto con segni:
  - il setup deve garantire almeno un numero reale nella colonna target
  - la verifica del numero segnato non deve dipendere da un ramo opzionale

- Simmetria destra/sinistra:
  - la robustezza del setup va applicata nello stesso modo sui due test
    avanzati con segni

## Flussi Concettuali

### Flusso 1 - aggiunta assertIsNone(risultato.evento.limite) nel test movimento normale avanzato destra

1. Il test prepara uno spostamento avanzato riuscito verso destra.
2. Invoca `sposta_focus_colonna_destra_avanzata` in un caso non di bordo.
3. Verifica `ok=True`, `errore=None` ed evento di tipo corretto.
4. Verifica il payload della colonna raggiunta.
5. Aggiunge la verifica esplicita che `risultato.evento.limite` sia `None`.
6. Conferma l'aggiornamento del focus interno.

### Flusso 2 - rafforzamento test con segni destra avanzata con setup che garantisce almeno un numero nella colonna target

1. Il test seleziona una colonna target la cui presenza di almeno un numero e'
   garantita dal modello standard della cartella.
2. Marca un numero reale appartenente a quella colonna.
3. Invoca `sposta_focus_colonna_destra_avanzata`.
4. Verifica il payload avanzato della colonna raggiunta.
5. Esegue sempre l'asserzione sul numero segnato, senza rami condizionali che
   possano saltarla.

### Flusso 3 - rafforzamento simmetrico test con segni sinistra avanzata

1. Il test simmetrico verso sinistra adotta la stessa logica di setup robusto.
2. Seleziona una colonna target con almeno un numero garantito.
3. Marca un numero reale della colonna.
4. Invoca `sposta_focus_colonna_sinistra_avanzata`.
5. Verifica sempre il numero segnato e il payload avanzato senza condizioni
   opzionali.

## Decisioni Architetturali

### Decisione 1 - assertIsNone(evento.limite) fa parte del pattern standard di movimento riuscito

Nel contratto degli eventi avanzati di navigazione, il caso di successo non deve
solo valorizzare `esito="mostra"` e il payload della colonna, ma deve anche
esplicitare l'assenza di un limite. Per questo `assertIsNone(evento.limite)`
non e' una rifinitura cosmetica: e' parte del pattern standard di movimento
riuscito avanzato.

### Decisione 2 - un test con ramo condizionale che puo' saltare la verifica principale non e' affidabile

Se la verifica centrale del caso d'uso viene eseguita solo quando il setup trova
casualmente un numero in colonna, il test non dimostra il comportamento che
dichiara di coprire. La presenza di un ramo `if numero_da_segnare is not None`
va quindi eliminata a favore di un setup che renda l'asserzione sempre eseguita.

### Decisione 3 - la colonna 0 fascia 1-9 contiene sempre almeno un numero in una cartella tombola standard ed e' il setup piu' robusto

Per eliminare la dipendenza dalla distribuzione casuale dei numeri, il setup deve
ancorarsi a una proprieta' strutturale della cartella standard. La colonna 0,
fascia 1-9, contiene sempre almeno un numero e fornisce quindi il punto di
appoggio piu' robusto per costruire un test con segni che non possa degradare in
successo spurio.

## Pattern di asserzione aggiornato per movimento riuscito avanzato

```python
dati_attesi = self.cartella1.get_dati_visualizzazione_colonna_avanzata(indice_atteso)

self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonnaAvanzata)
self.assertEqual(risultato.evento.esito, "mostra")
self.assertEqual(risultato.evento.numero_colonna_corrente, numero_umano_atteso)
self.assertEqual(risultato.evento.colonna_semplice, dati_attesi[0])
self.assertEqual(risultato.evento.stato_colonna, dati_attesi[1])
self.assertEqual(risultato.evento.numeri_segnati_colonna_ordinati, dati_attesi[2])
self.assertIsNone(risultato.evento.limite)
self.assertEqual(self.giocatore._indice_colonna_focus, indice_atteso)
```

## Vincoli

- Solo [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py) potra'
  essere modificato in implementazione.
- Nessuna modifica al codice produttivo.
- Nessuna estensione di scope oltre i 3 test identificati dal report.
- Nessun nuovo attore, evento o contratto applicativo.

## Rischi

- Toccare test gia' corretti durante l'implementazione della rifinitura.
- Scegliere una colonna che possa risultare vuota e lasciare quindi il test
  ancora condizionale o non deterministico.
- Introdurre una simmetria solo parziale tra test destra e sinistra avanzata.

## Criteri di accettazione

- I 3 test target eseguono sempre le loro asserzioni senza rami che le saltano.
- Il test di movimento normale avanzato destra verifica esplicitamente che
  `evento.limite` sia `None`.
- I due test avanzati con segni usano un setup che garantisce almeno un numero
  nella colonna target.
- Nessuna modifica al codice produttivo.

## Coding plans correlati

- [docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md](docs/3%20-%20coding%20plans/PLAN_fix_test_colonna_destra_eventi_v1.md)
- [docs/3 - coding plans/PLAN_fix_test_destra_avanzata_rifinitura_v1.md](docs/3%20-%20coding%20plans/PLAN_fix_test_destra_avanzata_rifinitura_v1.md)