---
type: design
feature: test_eventi_output_bulk_focus
agent: Agent-Design
status: REVIEWED
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: design
titolo: Design test unitari per eventi output bulk e focus
data_creazione: 2026-03-30
agente: Agent-Design
stato: revisionato
feature: test_eventi_output_bulk_focus
versione_progetto: v1.0.0
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Idea in 3 righe

Il task definisce il design del file tests/unit/test_eventi_output_bulk_focus.py.
Il perimetro copre i due eventi bulk per tutte le cartelle e l'evento di stato focus del Gruppo E5.
L'obiettivo e' congelare la numerazione 1-based, l'aggregazione immutabile dei pacchetti cartella e la conversione degli indici di focus usando unittest, con MagicMock ammesso solo nei due factory bulk.

### Obiettivo

Definire il design tecnico del file tests/unit/test_eventi_output_bulk_focus.py limitando lo scope a:

- EventoVisualizzaTutteCartelleSemplice
- EventoVisualizzaTutteCartelleAvanzata
- EventoStatoFocusCorrente

### Contesto

Il report identifica E5 come l'unico sottogruppo che richiede mock, perche' i due factory crea_da_cartelle() usano duck typing e invocano metodi di Cartella.
La lettura di [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) mostra che:

- EventoVisualizzaTutteCartelleSemplice chiama get_griglia_semplice()
- EventoVisualizzaTutteCartelleAvanzata chiama get_dati_visualizzazione_avanzata()
- EventoStatoFocusCorrente crea_da_indici() converte ciascun indice opzionale in numero umano 1-based lasciando None invariato

La nota tecnica del report prescrive l'uso di unittest.mock.MagicMock solo per i factory bulk. Tutti gli altri casi del Gruppo E devono evitare mock.

### Componenti coinvolti

- File di produzione target: [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- File di test da creare in fase implementativa: tests/unit/test_eventi_output_bulk_focus.py
- Riferimento analitico: [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- Coordinatore documentale: [docs/todo.md](../todo.md)

### Scenari da coprire

#### EventoVisualizzaTutteCartelleSemplice

- crea_da_cartelle() calcola totale_cartelle come len della sequenza ricevuta
- crea_da_cartelle() numera le cartelle in modo 1-based nell'ordine naturale
- crea_da_cartelle() richiama get_griglia_semplice() per ogni cartella mock e restituisce cartelle come tuple immutabile

#### EventoVisualizzaTutteCartelleAvanzata

- crea_da_cartelle() calcola totale_cartelle come len della sequenza ricevuta
- crea_da_cartelle() numera le cartelle in modo 1-based nell'ordine naturale
- crea_da_cartelle() richiama get_dati_visualizzazione_avanzata() per ogni cartella mock e scompone correttamente il pacchetto avanzato
- la collezione finale cartelle deve essere una tuple di tuple coerente con il contratto della dataclass

#### EventoStatoFocusCorrente

- crea_da_indici() con tutti i focus a None restituisce numero_cartella=None, numero_riga=None e numero_colonna=None
- crea_da_indici() con solo indice_cartella valorizzato converte correttamente solo il focus cartella
- crea_da_indici() con tutti gli indici valorizzati converte ciascun indice in numero umano 1-based

### Decisioni architetturali

#### Decisione 1 - MagicMock consentito solo nei due factory bulk

Il file dovra' usare unittest.mock.MagicMock esclusivamente per simulare l'interfaccia minima richiesta dai due factory crea_da_cartelle(). Non sono ammessi mock per EventoStatoFocusCorrente.

#### Decisione 2 - Nessuna istanziazione reale di Cartella

Per il Gruppo E5 si testa il contratto dei factory, non il comportamento interno di Cartella. Il design evita dipendenze reali dal dominio cartella.

#### Decisione 3 - unittest-only

Il file dovra' usare solo unittest e unittest.mock, senza pytest.

### Criteri di completamento

Il design E5 sara' considerato corretto quando il futuro file di test:

- usera' solo unittest e unittest.mock
- usera' MagicMock solo per i due factory bulk
- restera' confinato a tests/unit/test_eventi_output_bulk_focus.py
- coprira' sia aggregazione bulk sia conversione degli indici di focus
