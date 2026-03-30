---
type: design
feature: test_eventi_output_segnazione
agent: Agent-Design
status: REVIEWED
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: design
titolo: Design test unitari per eventi output segnazione e ricerca
data_creazione: 2026-03-30
agente: Agent-Design
stato: revisionato
feature: test_eventi_output_segnazione
versione_progetto: v1.0.0
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Idea in 3 righe

Il task definisce il design del file tests/unit/test_eventi_output_segnazione.py.
Il perimetro copre gli eventi di segnazione numero e di ricerca numero nelle cartelle del Gruppo E4.
L'obiettivo e' congelare i quattro esiti di segnazione, la conversione numero_cartella 1-based e l'ordinamento dei risultati di ricerca usando solo unittest.

### Obiettivo

Definire il design tecnico del file tests/unit/test_eventi_output_segnazione.py limitando lo scope a:

- EventoSegnazioneNumero
- RisultatoRicercaNumeroInCartella
- EventoRicercaNumeroInCartelle

### Contesto

Il report identifica E4 come secondo sottogruppo a priorita' alta dentro il Gruppo E.
La lettura di [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) mostra quattro factory su EventoSegnazioneNumero con un contratto comune: numero_cartella deriva sempre da indice_cartella + 1 e mancanti deriva sempre da totale_numeri - numeri_segnati. I casi non_presente e non_estratto lasciano le coordinate a None. La ricerca usa un risultato atomico per cartella e un aggregatore che ordina i risultati per indice_cartella.

### Componenti coinvolti

- File di produzione target: [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- File di test da creare in fase implementativa: tests/unit/test_eventi_output_segnazione.py
- Riferimento analitico: [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- Coordinatore documentale: [docs/todo.md](../todo.md)

### Scenari da coprire

#### EventoSegnazioneNumero

- segnato() valorizza coordinate, esito=segnato, numero_cartella 1-based e mancanti corretti
- gia_segnato() valorizza coordinate, esito=gia_segnato, numero_cartella 1-based e mancanti corretti
- non_presente() lascia indice_riga=None e indice_colonna=None mantenendo progresso coerente
- non_estratto() lascia indice_riga=None e indice_colonna=None mantenendo progresso coerente

#### RisultatoRicercaNumeroInCartella

- crea() converte indice_cartella in numero_cartella 1-based
- crea() preserva indice_riga, indice_colonna e segnato

#### EventoRicercaNumeroInCartelle

- non_trovato() restituisce esito=non_trovato e risultati=()
- trovato() converte la sequenza in tuple ordinate per indice_cartella crescente
- trovato() preserva numero, totale_cartelle, id_giocatore e nome_giocatore

### Decisioni architetturali

#### Decisione 1 - Copertura esaustiva dei quattro esiti di segnazione

Il file dovra' trattare separatamente tutti i quattro rami di EventoSegnazioneNumero per evitare regressioni silenziose su coordinate o progresso.

#### Decisione 2 - Nessun mock in E4

Anche E4 usa solo primitivi e factory pure. Non e' previsto alcun MagicMock.

#### Decisione 3 - unittest-only

Il file dovra' usare solo unittest e asserzioni della standard library.

### Criteri di completamento

Il design E4 sara' considerato corretto quando il futuro file di test:

- usera' esclusivamente unittest
- restera' confinato a tests/unit/test_eventi_output_segnazione.py
- coprira' tutti i quattro esiti di segnazione
- coprira' sia il caso non_trovato sia il caso trovato con ordinamento deterministico
