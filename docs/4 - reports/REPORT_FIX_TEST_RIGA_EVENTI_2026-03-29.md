---
type: report
feature: fix_test_riga_eventi
agent: Agent-Analyze
status: DRAFT
date: 2026-03-29
title: Report analisi tranche 1 modernizzazione test riga
---

## Metadati

tipo: report
titolo: Report analisi tranche 1 modernizzazione test riga
data_creazione: 2026-03-29
agente: Agent-Analyze
stato: bozza
feature: fix_test_riga_eventi
versione_target: v1.0

## Contenuto

### Trigger

La suite contiene 20 test del gruppo riga in [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py)
che leggono ancora il testo renderizzato del risultato invece di verificare
il contratto strutturato restituito dai metodi di navigazione.

Questa tranche copre solo i quattro gruppi riga:

- `sposta_focus_riga_su_semplice` / alias `sposta_focus_riga_su`
- `sposta_focus_riga_giu_semplice` / alias `sposta_focus_riga_giu`
- `sposta_focus_riga_su_avanzata`
- `sposta_focus_riga_giu_avanzata`

### Sommario esecutivo

I 20 test di riga hanno lo stesso difetto logico: osservano la frase finale
anziche' l'esito strutturato del comando. I metodi di navigazione riga non
devono essere verificati tramite stringhe come `Riga 0:` o `Sei alla prima riga`.
Devono essere verificati tramite `EsitoAzione` e tramite il tipo di evento
incapsulato.

I casi si dividono in tre famiglie:

- errore di prerequisito: `ok=False`, `errore` valorizzato, `evento=None`
- limite: `ok=True`, `errore=None`, evento con `esito="limite"`
- movimento riuscito: `ok=True`, `errore=None`, evento con `esito="mostra"`

Le versioni semplici usano `EventoNavigazioneRiga`.
Le versioni avanzate usano `EventoNavigazioneRigaAvanzata`.

### Componenti coinvolti

- [tests/test_giocatore_umano.py](tests/test_giocatore_umano.py) come unico file da aggiornare in implementazione.
- [bingo_game/players/giocatore_umano.py](bingo_game/players/giocatore_umano.py) come sorgente dei quattro metodi.
- [bingo_game/players/helper_focus.py](bingo_game/players/helper_focus.py) per il gate `_esito_pronto_per_navigazione()`.
- [bingo_game/events/eventi.py](bingo_game/events/eventi.py) per il contratto `EsitoAzione`.
- [bingo_game/events/eventi_output_ui_umani.py](bingo_game/events/eventi_output_ui_umani.py) per `EventoNavigazioneRiga` e `EventoNavigazioneRigaAvanzata`.

### Contratti osservabili

#### Contratto di errore

- `risultato.ok == False`
- `risultato.errore == "CARTELLE_NESSUNA_ASSEGNATA"` se il giocatore non ha cartelle
- `risultato.errore == "FOCUS_CARTELLA_NON_IMPOSTATO"` se le cartelle esistono ma il focus cartella e' `None`
- `risultato.evento is None`

#### Contratto di limite semplice

- `risultato.ok == True`
- `risultato.errore is None`
- `isinstance(risultato.evento, EventoNavigazioneRiga)`
- `risultato.evento.esito == "limite"`
- `risultato.evento.limite == "minimo"` oppure `"massimo"`
- `risultato.evento.riga_semplice is None`

#### Contratto di movimento semplice

- `risultato.ok == True`
- `risultato.errore is None`
- `isinstance(risultato.evento, EventoNavigazioneRiga)`
- `risultato.evento.esito == "mostra"`
- `risultato.evento.numero_riga_corrente` e' 1-based
- `risultato.evento.riga_semplice == self.cartella1.get_riga_semplice(indice_atteso)`
- `risultato.evento.limite is None`

#### Contratto di limite avanzato

- `risultato.ok == True`
- `risultato.errore is None`
- `isinstance(risultato.evento, EventoNavigazioneRigaAvanzata)`
- `risultato.evento.esito == "limite"`
- `risultato.evento.limite == "minimo"` oppure `"massimo"`
- `risultato.evento.riga_semplice is None`
- `risultato.evento.stato_riga is None`
- `risultato.evento.numeri_segnati_riga_ordinati is None`

#### Contratto di movimento avanzato

- `risultato.ok == True`
- `risultato.errore is None`
- `isinstance(risultato.evento, EventoNavigazioneRigaAvanzata)`
- `risultato.evento.esito == "mostra"`
- `risultato.evento.numero_riga_corrente` e' 1-based
- `risultato.evento.riga_semplice == dati_attesi[0]`
- `risultato.evento.stato_riga == dati_attesi[1]`
- `risultato.evento.numeri_segnati_riga_ordinati == dati_attesi[2]`
- `risultato.evento.limite is None`

### Diagnosi puntuale dei 20 test

#### Gruppo A — sposta_focus_riga_su_semplice

1. `test_sposta_focus_riga_su_semplice_cartella_mancante`
   - confronto errato attuale: `assertEqual` su stringa utente
   - scenario: errore
   - verifica corretta:
     - scenario 1 senza cartelle: `ok=False`, `errore="CARTELLE_NESSUNA_ASSEGNATA"`, `evento=None`
     - scenario 2 focus cartella mancante: `ok=False`, `errore="FOCUS_CARTELLA_NON_IMPOSTATO"`, `evento=None`

2. `test_sposta_focus_riga_su_semplice_prima_riga`
   - confronto errato attuale: `assertEqual` su stringa di limite
   - scenario: limite minimo
   - verifica corretta:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneRiga`
     - `evento.esito="limite"`, `evento.limite="minimo"`
     - `evento.numero_riga_corrente == 1`
     - `_indice_riga_focus` invariato a `0`

3. `test_sposta_focus_riga_su_semplice_movimento_normale`
   - confronto errato attuale: `assertIn("Riga 0:", risultato)` e ricerca numeri nel testo
   - scenario: movimento riuscito
   - verifica corretta:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneRiga`
     - `evento.esito="mostra"`
     - `evento.numero_riga_corrente == 1`
     - `evento.riga_semplice == self.cartella1.get_riga_semplice(0)`
     - `_indice_riga_focus == 0`

4. `test_sposta_focus_riga_su_semplice_auto_inizializzazione`
   - confronto errato attuale: `assertIn("Riga 0:", risultato)`
   - scenario: movimento riuscito da focus riga `None`
   - verifica corretta:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneRiga`
     - `evento.esito="mostra"`
     - `evento.numero_riga_corrente == 1`
     - `evento.riga_semplice == self.cartella1.get_riga_semplice(0)`
     - `_indice_riga_focus == 0`

5. `test_sposta_focus_riga_su_semplice_stato_interno`
   - confronto errato attuale: `assertIn("Riga 1:", risultato)`
   - scenario: movimento riuscito con cartella che contiene numeri segnati, ma variante semplice
   - verifica corretta:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneRiga`
     - `evento.esito="mostra"`
     - `evento.numero_riga_corrente == 2`
     - `evento.riga_semplice == self.cartella1.get_riga_semplice(1)`
     - `_indice_riga_focus == 1`

#### Gruppo B — sposta_focus_riga_giu_semplice

6. `test_sposta_focus_riga_giu_semplice_cartella_mancante`
   - confronto errato attuale: `assertEqual` su stringa utente
   - scenario: errore
   - verifica corretta:
     - primo scenario: `errore="CARTELLE_NESSUNA_ASSEGNATA"`
     - secondo scenario: `errore="FOCUS_CARTELLA_NON_IMPOSTATO"`
     - in entrambi: `ok=False`, `evento=None`

7. `test_sposta_focus_riga_giu_semplice_ultima_riga`
   - confronto errato attuale: `assertEqual` su stringa di limite
   - scenario: limite massimo
   - verifica corretta:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneRiga`
     - `evento.esito="limite"`, `evento.limite="massimo"`
     - `evento.numero_riga_corrente == 3`
     - `_indice_riga_focus == 2`

8. `test_sposta_focus_riga_giu_semplice_movimento_normale`
   - confronto errato attuale: `assertIn("Riga 1:", risultato)` e ricerca numeri nel testo
   - scenario: movimento riuscito
   - verifica corretta:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneRiga`
     - `evento.esito="mostra"`
     - `evento.numero_riga_corrente == 2`
     - `evento.riga_semplice == self.cartella1.get_riga_semplice(1)`
     - `_indice_riga_focus == 1`

9. `test_sposta_focus_riga_giu_semplice_auto_inizializzazione`
   - confronto errato attuale: `assertIn("Riga 1:", risultato)`
   - scenario: movimento riuscito da focus riga `None`
   - verifica corretta:
     - `ok=True`, `errore=None`
     - evento `EventoNavigazioneRiga`
     - `evento.esito="mostra"`
     - `evento.numero_riga_corrente == 2`
     - `evento.riga_semplice == self.cartella1.get_riga_semplice(1)`
     - `_indice_riga_focus == 1`

10. `test_sposta_focus_riga_giu_semplice_stato_interno`
    - confronto errato attuale: `assertIn("Riga 1:", risultato)`
    - scenario: movimento riuscito con cartella segnata, ma variante semplice
    - verifica corretta:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneRiga`
      - `evento.esito="mostra"`
      - `evento.numero_riga_corrente == 2`
      - `evento.riga_semplice == self.cartella1.get_riga_semplice(1)`
      - `_indice_riga_focus == 1`

#### Gruppo C — sposta_focus_riga_su_avanzata

11. `test_sposta_focus_riga_su_avanzata_cartella_mancante`
    - confronto errato attuale: `assertEqual` su stringa utente
    - scenario: errore
    - verifica corretta:
      - primo scenario: `errore="CARTELLE_NESSUNA_ASSEGNATA"`
      - secondo scenario: `errore="FOCUS_CARTELLA_NON_IMPOSTATO"`
      - in entrambi: `ok=False`, `evento=None`

12. `test_sposta_focus_riga_su_avanzata_prima_riga`
    - confronto errato attuale: `assertEqual` su stringa di limite
    - scenario: limite minimo
    - verifica corretta:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneRigaAvanzata`
      - `evento.esito="limite"`, `evento.limite="minimo"`
      - `evento.numero_riga_corrente == 1`
      - `evento.riga_semplice is None`
      - `evento.stato_riga is None`
      - `evento.numeri_segnati_riga_ordinati is None`
      - `_indice_riga_focus == 0`

13. `test_sposta_focus_riga_su_avanzata_movimento_normale`
    - confronto errato attuale: ricerca di intestazione e numeri nel testo
    - scenario: movimento riuscito avanzato
    - verifica corretta:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneRigaAvanzata`
      - `evento.esito="mostra"`
      - `evento.numero_riga_corrente == 1`
      - `evento.riga_semplice == self.cartella1.get_dati_visualizzazione_riga_avanzata(0)[0]`
      - `evento.stato_riga == self.cartella1.get_dati_visualizzazione_riga_avanzata(0)[1]`
      - `evento.numeri_segnati_riga_ordinati == self.cartella1.get_dati_visualizzazione_riga_avanzata(0)[2]`
      - `_indice_riga_focus == 0`

14. `test_sposta_focus_riga_su_avanzata_auto_inizializzazione`
    - confronto errato attuale: `assertIn("Riga 0:", risultato)`
    - scenario: movimento riuscito avanzato da focus riga `None`
    - verifica corretta:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneRigaAvanzata`
      - `evento.esito="mostra"`
      - `evento.numero_riga_corrente == 1`
      - verifica completa dei tre blocchi dati avanzati sulla riga `0`
      - `_indice_riga_focus == 0`

15. `test_sposta_focus_riga_su_avanzata_stato_cartella_con_segni`
    - confronto errato attuale: `assertIn(f"*{numero}", risultato)`
    - scenario: movimento riuscito avanzato con numeri segnati
    - verifica corretta:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneRigaAvanzata`
      - `evento.esito="mostra"`
      - il numero marcato compare in `evento.numeri_segnati_riga_ordinati`
      - `evento.stato_riga` riflette i conteggi aggiornati
      - `_indice_riga_focus == 0`

#### Gruppo D — sposta_focus_riga_giu_avanzata

16. `test_sposta_focus_riga_giu_avanzata_cartella_mancante`
    - confronto errato attuale: `assertEqual` su stringa utente
    - scenario: errore
    - verifica corretta:
      - primo scenario: `errore="CARTELLE_NESSUNA_ASSEGNATA"`
      - secondo scenario: `errore="FOCUS_CARTELLA_NON_IMPOSTATO"`
      - in entrambi: `ok=False`, `evento=None`

17. `test_sposta_focus_riga_giu_avanzata_ultima_riga`
    - confronto errato attuale: `assertEqual` su stringa di limite
    - scenario: limite massimo
    - verifica corretta:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneRigaAvanzata`
      - `evento.esito="limite"`, `evento.limite="massimo"`
      - `evento.numero_riga_corrente == 3`
      - `evento.riga_semplice is None`
      - `evento.stato_riga is None`
      - `evento.numeri_segnati_riga_ordinati is None`
      - `_indice_riga_focus == 2`

18. `test_sposta_focus_riga_giu_avanzata_movimento_normale`
    - confronto errato attuale: ricerca di intestazione e numeri nel testo
    - scenario: movimento riuscito avanzato
    - verifica corretta:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneRigaAvanzata`
      - `evento.esito="mostra"`
      - `evento.numero_riga_corrente == 2`
      - confronto completo dei tre blocchi dati avanzati sulla riga `1`
      - `_indice_riga_focus == 1`

19. `test_sposta_focus_riga_giu_avanzata_auto_inizializzazione`
    - confronto errato attuale: `assertIn("Riga 1:", risultato)`
    - scenario: movimento riuscito avanzato da focus riga `None`
    - verifica corretta:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneRigaAvanzata`
      - `evento.esito="mostra"`
      - `evento.numero_riga_corrente == 2`
      - confronto completo dei tre blocchi dati avanzati sulla riga `1`
      - `_indice_riga_focus == 1`

20. `test_sposta_focus_riga_giu_avanzata_stato_cartella_con_segni`
    - confronto errato attuale: `assertIn(f"*{numero}", risultato)`
    - scenario: movimento riuscito avanzato con numeri segnati
    - verifica corretta:
      - `ok=True`, `errore=None`
      - evento `EventoNavigazioneRigaAvanzata`
      - `evento.esito="mostra"`
      - il numero marcato compare in `evento.numeri_segnati_riga_ordinati`
      - `evento.stato_riga` riflette i conteggi aggiornati
      - `_indice_riga_focus == 2` allestito e poi `1` o `2` secondo scenario di test effettivo; nella implementazione va mantenuto il comportamento reale del metodo

### Pattern generali da adottare

#### Pattern errore

```python
self.assertFalse(risultato.ok)
self.assertEqual(risultato.errore, "CODICE_ATTESO")
self.assertIsNone(risultato.evento)
```

#### Pattern limite semplice

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneRiga)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "minimo" oppure "massimo")
```

#### Pattern limite avanzato

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneRigaAvanzata)
self.assertEqual(risultato.evento.esito, "limite")
self.assertEqual(risultato.evento.limite, "minimo" oppure "massimo")
self.assertIsNone(risultato.evento.riga_semplice)
self.assertIsNone(risultato.evento.stato_riga)
self.assertIsNone(risultato.evento.numeri_segnati_riga_ordinati)
```

#### Pattern movimento semplice

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneRiga)
self.assertEqual(risultato.evento.esito, "mostra")
self.assertEqual(risultato.evento.numero_riga_corrente, numero_umano_atteso)
self.assertEqual(risultato.evento.riga_semplice, self.cartella1.get_riga_semplice(indice_atteso))
self.assertIsNone(risultato.evento.limite)
```

#### Pattern movimento avanzato

```python
dati_attesi = self.cartella1.get_dati_visualizzazione_riga_avanzata(indice_atteso)

self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneRigaAvanzata)
self.assertEqual(risultato.evento.esito, "mostra")
self.assertEqual(risultato.evento.numero_riga_corrente, numero_umano_atteso)
self.assertEqual(risultato.evento.riga_semplice, dati_attesi[0])
self.assertEqual(risultato.evento.stato_riga, dati_attesi[1])
self.assertEqual(risultato.evento.numeri_segnati_riga_ordinati, dati_attesi[2])
self.assertIsNone(risultato.evento.limite)
```

### Rischi e vincoli

- Nessuna modifica deve uscire da `docs/` in queste fasi.
- Non va toccato nessun test gia' corretto del gruppo verde.
- Il numero riga esposto negli eventi e' 1-based, mentre lo stato interno resta 0-based.
- I casi con segni non devono piu' cercare l'asterisco nel testo; devono leggere `numeri_segnati_riga_ordinati` e `stato_riga`.

### Conclusione

La tranche 1 e' ben delimitata, non richiede cambi architetturali e puo'
essere implementata in quattro micro-fasi atomiche, una per gruppo di metodo.
Il passaggio chiave e' spostare l'attenzione dei test dal testo renderizzato al
contratto dati del comando.
