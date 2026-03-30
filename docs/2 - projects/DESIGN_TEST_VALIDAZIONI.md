---
type: design
feature: test_validazioni
agent: Agent-Design
status: DRAFT
version: v1.0
date: 2026-03-30
report_ref: docs/4 - reports/REPORT_ANALISI_VALIDAZIONI_2026-03-30.md
---

## Metadati

tipo: design
titolo: Design suite unittest per i moduli di validazione
data_creazione: 2026-03-30
agente: Agent-Design
stato: draft
feature: test_validazioni
versione_progetto: v1.0
report: docs/4 - reports/REPORT_ANALISI_VALIDAZIONI_2026-03-30.md

## Contenuto

### Obiettivo

Portare a copertura diretta e isolata tutte le funzioni di validazione in
bingo_game/validations/validazioni_input.py e
bingo_game/validations/validazione_oggetti.py, usando esclusivamente
unittest e senza dipendenze da altri componenti del gioco come soggetto
primario del test.

La suite deve fissare il contratto effettivo di ciascuna funzione su tre
assi: valore di ok, codice errore e assenza di evento. Dove docstring e
codice divergono, il test deve descrivere il comportamento reale oggi in
produzione.

### Approccio di testing

Le funzioni di validazioni_input.py sono funzioni pure o quasi pure:
- non dipendono da stato globale;
- ricevono valori semplici;
- restituiscono sempre EsitoAzione senza side effect.

Per queste funzioni l'approccio corretto e' la chiamata diretta, senza mock,
senza fixture condivise e senza componenti di supporto.

Le funzioni di validazione_oggetti.py richiedono invece un supporto minimo:
- esito_tabellone_disponibile puo' essere testata sia con un Tabellone reale
  sia con stub compatibili che espongano i metodi attesi;
- esito_coordinate_numero_coerenti richiede un oggetto cartella con
  get_coordinate_numero(numero), quindi e' sufficiente uno stub semplice o un
  MagicMock.

Scelte operative:
- nessun mock dove non serve;
- uso di oggetti reali solo quando il contratto lo richiede davvero, ad esempio
  per il ramo isinstance(Tabellone);
- uso di stub o MagicMock per i rami duck-typed e per la cartella.

Motivazione:
- massima leggibilita';
- zero dipendenze superflue;
- test stabili e poco fragili;
- piena coerenza con il vincolo unittest-only del task.

### Struttura dei file di test

File da creare in tests/unit/:
- tests/unit/test_validazioni_input.py
- tests/unit/test_validazione_oggetti.py

Organizzazione interna proposta:

Per tests/unit/test_validazioni_input.py:
- class TestEsitoNumeroIntero(unittest.TestCase)
- class TestEsitoNumeroInRange190(unittest.TestCase)
- class TestEsitoNumeroRigaInRange13(unittest.TestCase)
- class TestEsitoNumeroColonnaInRange19(unittest.TestCase)
- class TestEsitoReclamoTurnoLibero(unittest.TestCase)
- class TestEsitoTipoVittoriaSupportato(unittest.TestCase)

Per tests/unit/test_validazione_oggetti.py:
- class TestEsitoTabelloneDisponibile(unittest.TestCase)
- class TestEsitoCoordinateNumeroCoerenti(unittest.TestCase)

Raggruppamento scelto:
- una classe per funzione o per contratto omogeneo;
- nessuna classe omnibus;
- nessuna dipendenza tra classi di test.

### Lista completa dei test da implementare

#### File: tests/unit/test_validazioni_input.py

##### Classe: TestEsitoNumeroIntero

- test_esito_numero_intero_int_valido_restituisce_ok
- test_esito_numero_intero_bool_restituisce_tipo_non_valido
- test_esito_numero_intero_float_restituisce_tipo_non_valido
- test_esito_numero_intero_none_restituisce_tipo_non_valido

##### Classe: TestEsitoNumeroInRange190

- test_esito_numero_in_range_1_90_con_1_restituisce_ok
- test_esito_numero_in_range_1_90_con_90_restituisce_ok
- test_esito_numero_in_range_1_90_con_0_restituisce_numero_non_valido
- test_esito_numero_in_range_1_90_con_91_restituisce_numero_non_valido
- test_esito_numero_in_range_1_90_con_tipo_errato_restituisce_tipo_non_valido

##### Classe: TestEsitoNumeroRigaInRange13

- test_esito_numero_riga_in_range_1_3_con_1_restituisce_ok
- test_esito_numero_riga_in_range_1_3_con_3_restituisce_ok
- test_esito_numero_riga_in_range_1_3_con_0_restituisce_numero_riga_fuori_range
- test_esito_numero_riga_in_range_1_3_con_4_restituisce_numero_riga_fuori_range
- test_esito_numero_riga_in_range_1_3_con_tipo_errato_restituisce_tipo_non_valido

##### Classe: TestEsitoNumeroColonnaInRange19

- test_esito_numero_colonna_in_range_1_9_con_1_restituisce_ok
- test_esito_numero_colonna_in_range_1_9_con_9_restituisce_ok
- test_esito_numero_colonna_in_range_1_9_con_0_restituisce_numero_colonna_fuori_range
- test_esito_numero_colonna_in_range_1_9_con_10_restituisce_numero_colonna_fuori_range
- test_esito_numero_colonna_in_range_1_9_con_tipo_errato_restituisce_tipo_non_valido

##### Classe: TestEsitoReclamoTurnoLibero

- test_esito_reclamo_turno_libero_con_none_restituisce_ok
- test_esito_reclamo_turno_libero_con_oggetto_restituisce_reclamo_gia_presente

##### Classe: TestEsitoTipoVittoriaSupportato

- test_esito_tipo_vittoria_supportato_tombola_restituisce_ok
- test_esito_tipo_vittoria_supportato_ambo_restituisce_ok
- test_esito_tipo_vittoria_supportato_terno_restituisce_ok
- test_esito_tipo_vittoria_supportato_quaterna_restituisce_ok
- test_esito_tipo_vittoria_supportato_cinquina_restituisce_ok
- test_esito_tipo_vittoria_supportato_valore_sconosciuto_restituisce_tipo_vittoria_non_valido
- test_esito_tipo_vittoria_supportato_maiuscolo_restituisce_tipo_vittoria_non_valido
- test_esito_tipo_vittoria_supportato_none_restituisce_tipo_vittoria_non_valido

#### File: tests/unit/test_validazione_oggetti.py

##### Classe: TestEsitoTabelloneDisponibile

- test_esito_tabellone_disponibile_none_restituisce_tabellone_non_disponibile
- test_esito_tabellone_disponibile_tabellone_reale_restituisce_ok
- test_esito_tabellone_disponibile_stub_con_get_numeri_estratti_restituisce_ok
- test_esito_tabellone_disponibile_stub_con_is_numero_estratto_restituisce_ok
- test_esito_tabellone_disponibile_oggetto_incompatibile_restituisce_tabellone_non_disponibile

##### Classe: TestEsitoCoordinateNumeroCoerenti

- test_esito_coordinate_numero_coerenti_coordinate_presenti_restituisce_ok
- test_esito_coordinate_numero_coerenti_coordinate_none_restituisce_cartella_stato_incoerente
- test_esito_coordinate_numero_coerenti_numero_non_int_restituisce_inputnonvalido
- test_esito_coordinate_numero_coerenti_eccezione_del_metodo_cartella_viene_propagata

### Ordine di scrittura dei test

Ordine raccomandato:
1. esito_numero_intero
2. esito_numero_in_range_1_90
3. esito_numero_riga_in_range_1_3
4. esito_numero_colonna_in_range_1_9
5. esito_reclamo_turno_libero
6. esito_tipo_vittoria_supportato
7. esito_tabellone_disponibile
8. esito_coordinate_numero_coerenti

Motivazione:
- prima le funzioni completamente pure e senza dipendenze;
- poi le funzioni di range che congelano i codici errore reali;
- infine le funzioni che richiedono stub o oggetti di supporto.

### Cosa NON fare

- Non usare pytest.
- Non usare altri framework di test.
- Non trasformare questi test in test di integrazione su GiocatoreUmano.
- Non introdurre mock complessi se uno stub locale basta.
- Non correggere in questa fase i moduli Python di produzione.
- Non modificare docstring o codici errore nel medesimo task di preparazione.

## Stato Avanzamento

- [x] Design creato
- [x] Validato
- [ ] Passato a implementazione