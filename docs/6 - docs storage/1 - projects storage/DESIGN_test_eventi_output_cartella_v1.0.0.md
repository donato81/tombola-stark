---
type: design
feature: test_eventi_output_cartella
agent: Agent-Design
status: REVIEWED
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: design
titolo: Design test unitari per eventi output cartella
data_creazione: 2026-03-30
agente: Agent-Design
stato: revisionato
feature: test_eventi_output_cartella
versione_progetto: v1.0.0
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Idea in 3 righe

Il task definisce il design del file tests/unit/test_eventi_output_cartella.py.
Il perimetro copre solo le classi di riepilogo cartella, limite navigazione cartelle e visualizzazione singola cartella del Gruppo E1.
L'obiettivo e' congelare conversioni 0-based -> 1-based, ordinamenti, campi derivati e immutabilita' usando solo unittest.

### Obiettivo

Definire il design tecnico del file tests/unit/test_eventi_output_cartella.py limitando lo scope a:

- EventoRiepilogoCartellaCorrente
- EventoLimiteNavigazioneCartelle
- EventoVisualizzaCartellaSemplice
- EventoVisualizzaCartellaAvanzata

Il design deve fissare struttura del file, scenari minimi, dati di input reali, vincolo unittest-only ed esclusione esplicita di bulk, focus, tabellone, segnazione e ricerca.

### Contesto

Il report di riferimento colloca E1 come prima tranche del Gruppo E perche' raccoglie le classi piu' usate dai renderer.
La lettura integrale di [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) mostra che tutte le classi E1 sono dataclass frozen e usano factory method o costruzione diretta con soli primitivi, tuple e dict gia' normalizzati.

Il task non include:

- EventoVisualizzaTutteCartelleSemplice
- EventoVisualizzaTutteCartelleAvanzata
- EventoStatoFocusCorrente
- eventi di navigazione riga o colonna
- eventi di tabellone
- eventi di segnazione o ricerca

### Componenti coinvolti

- File di produzione target: [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- File di test da creare in fase implementativa: tests/unit/test_eventi_output_cartella.py
- Riferimento analitico: [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- Coordinatore documentale: [docs/todo.md](../todo.md)

### Scenari da coprire

#### EventoRiepilogoCartellaCorrente

- crea_da_cartella() converte indice_cartella 0-based in numero_cartella 1-based
- crea_da_cartella() ordina numeri_non_segnati e li restituisce come tuple
- crea_da_cartella() calcola mancanti come len dei numeri non segnati ordinati
- crea_da_cartella() preserva id_giocatore, nome_giocatore, numeri_segnati, totale_numeri e percentuale

#### EventoLimiteNavigazioneCartelle

- limite_minimo() imposta limite=minimo e numero_cartella_corrente=1
- limite_massimo() imposta limite=massimo e numero_cartella_corrente=totale_cartelle
- i campi id_giocatore, nome_giocatore, direzione e totale_cartelle devono restare coerenti con gli input

#### EventoVisualizzaCartellaSemplice

- crea_da_cartella() converte indice_cartella 0-based in numero_cartella 1-based
- crea_da_cartella() preserva totale_cartelle e griglia_semplice senza mutazioni
- la griglia deve rimanere una struttura immutabile a tuple, non una lista

#### EventoVisualizzaCartellaAvanzata

- costruzione diretta della dataclass con campi completi
- crea_da_dati_avanzati() converte indice_cartella 0-based in numero_cartella 1-based
- crea_da_dati_avanzati() scompone correttamente il pacchetto dati_avanzati in griglia_semplice, stato_cartella e numeri_segnati_ordinati
- i campi avanzati devono restare coerenti con i dati di input senza introdurre trasformazioni fuori contratto

### Decisioni architetturali

#### Decisione 1 - Un solo file di test con quattro classi ordinate per responsabilita'

Il file tests/unit/test_eventi_output_cartella.py dovra' contenere quattro classi di test distinte, una per ciascuna dataclass del perimetro E1.

#### Decisione 2 - Nessun mock in E1

Tutte le classi E1 possono essere costruite con soli primitivi e tuple. Il design esclude MagicMock e qualsiasi double di Cartella in questo file.

#### Decisione 3 - unittest e' la sola libreria ammessa

Il file dovra' usare solo unittest della standard library. Sono esclusi import pytest, fixture pytest e qualsiasi marker pytest.

### Criteri di completamento

Il design E1 sara' considerato corretto quando il futuro file di test:

- usera' esclusivamente unittest
- restera' confinato a tests/unit/test_eventi_output_cartella.py
- coprira' tutte le conversioni e i campi derivati elencati sopra
- non introdurra' mock o dipendenze esterne
