---
type: design
feature: test_eventi_output_navigazione
agent: Agent-Design
status: DRAFT
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: design
titolo: Design test unitari per eventi output navigazione
data_creazione: 2026-03-30
agente: Agent-Design
stato: bozza
feature: test_eventi_output_navigazione
versione_progetto: v1.0.0
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Idea in 3 righe

Il task definisce il design del file tests/unit/test_eventi_output_navigazione.py.
Il perimetro copre le classi di navigazione riga e colonna, semplici e avanzate, piu' i due eventi diretti vai-a.
L'obiettivo e' congelare esiti mostra/limite, conversioni 0-based -> 1-based e scomposizione dei pacchetti avanzati usando solo unittest.

### Obiettivo

Definire il design tecnico del file tests/unit/test_eventi_output_navigazione.py limitando lo scope a:

- EventoNavigazioneRiga
- EventoNavigazioneRigaAvanzata
- EventoNavigazioneColonna
- EventoNavigazioneColonnaAvanzata
- EventoVaiARigaAvanzata
- EventoVaiAColonnaAvanzata

### Contesto

Il report colloca E2 come gruppo omogeneo di sei classi con factory method paralleli tra riga e colonna.
La lettura di [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) mostra che i rami semplici distinguono esito mostra e limite, mentre i rami avanzati aggiungono dict di stato e tuple di numeri segnati. Gli eventi diretti vai-a non hanno direzione, limite o esito e rappresentano solo il caso riuscito.

Il task non include bulk, focus, cartella singola, tabellone, segnazione o ricerca.

### Componenti coinvolti

- File di produzione target: [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- File di test da creare in fase implementativa: tests/unit/test_eventi_output_navigazione.py
- Riferimento analitico: [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- Coordinatore documentale: [docs/todo.md](../todo.md)

### Scenari da coprire

#### EventoNavigazioneRiga

- mostra_riga() converte indice_riga_corrente in numero_riga_corrente 1-based
- mostra_riga() imposta esito=mostra, riga_semplice valorizzata e limite=None
- limite_minimo() imposta esito=limite, numero_riga_corrente=1, riga_semplice=None e limite=minimo
- limite_massimo() imposta esito=limite, numero_riga_corrente=totale_righe, riga_semplice=None e limite=massimo

#### EventoNavigazioneRigaAvanzata

- mostra_riga() scompone dati_riga_avanzati in riga_semplice, stato_riga e numeri_segnati_riga_ordinati
- mostra_riga() converte indice_riga_corrente in numero_riga_corrente 1-based
- limite_minimo() e limite_massimo() valorizzano solo i campi coerenti con il ramo limite

#### EventoNavigazioneColonna

- mostra_colonna() converte indice_colonna_corrente in numero_colonna_corrente 1-based
- mostra_colonna() imposta esito=mostra, colonna_semplice valorizzata e limite=None
- limite_minimo() imposta numero_colonna_corrente=1 e limite=minimo
- limite_massimo() imposta numero_colonna_corrente=totale_colonne e limite=massimo

#### EventoNavigazioneColonnaAvanzata

- mostra_colonna() scompone dati_colonna_avanzati in colonna_semplice, stato_colonna e numeri_segnati_colonna_ordinati
- mostra_colonna() converte indice_colonna_corrente in numero_colonna_corrente 1-based
- limite_minimo() e limite_massimo() azzerano i campi avanzati nel ramo limite

#### EventoVaiARigaAvanzata

- crea_da_dati_riga_avanzati() preserva numero_riga umano passato in input
- crea_da_dati_riga_avanzati() forza riga_semplice e numeri_segnati_riga_ordinati a tuple
- crea_da_dati_riga_avanzati() preserva stato_riga senza trasformazioni aggiuntive

#### EventoVaiAColonnaAvanzata

- crea_da_dati_colonna_avanzati() preserva numero_colonna umano passato in input
- crea_da_dati_colonna_avanzati() forza colonna_semplice e numeri_segnati_colonna_ordinati a tuple
- crea_da_dati_colonna_avanzati() preserva stato_colonna senza trasformazioni aggiuntive

### Decisioni architetturali

#### Decisione 1 - Test separati per famiglie parallele

Il file dovra' separare test riga, riga avanzata, colonna, colonna avanzata, vai-a-riga e vai-a-colonna per rendere immediata la diagnosi di regressione.

#### Decisione 2 - Nessun mock in E2

Anche in E2 i costruttori lavorano solo su primitivi, tuple e dict gia' pronti. Non e' previsto uso di MagicMock.

#### Decisione 3 - unittest-only

Il file dovra' usare solo unittest. Import pytest, fixture pytest e marker pytest sono vietati.

### Criteri di completamento

Il design E2 sara' considerato corretto quando il futuro file di test:

- usera' esclusivamente unittest
- restera' confinato a tests/unit/test_eventi_output_navigazione.py
- coprira' esiti mostra e limite per le quattro classi di navigazione
- coprira' i due eventi diretti vai-a con verifica dei campi avanzati
