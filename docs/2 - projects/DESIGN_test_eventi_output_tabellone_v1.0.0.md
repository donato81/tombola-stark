---
type: design
feature: test_eventi_output_tabellone
agent: Agent-Design
status: DRAFT
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/report_lavori_test_eventi.md
---

## Metadati

tipo: design
titolo: Design test unitari per eventi output tabellone
data_creazione: 2026-03-30
agente: Agent-Design
stato: bozza
feature: test_eventi_output_tabellone
versione_progetto: v1.0.0
report: docs/4 - reports/report_lavori_test_eventi.md

## Contenuto

### Idea in 3 righe

Il task definisce il design del file tests/unit/test_eventi_output_tabellone.py.
Il perimetro copre gli eventi di interrogazione del tabellone e i riepiloghi read-only del Gruppo E3.
L'obiettivo e' congelare i factory method, le normalizzazioni difensive e i campi derivati usando solo unittest.

### Obiettivo

Definire il design tecnico del file tests/unit/test_eventi_output_tabellone.py limitando lo scope a:

- EventoVerificaNumeroEstratto
- EventoUltimoNumeroEstratto
- EventoUltimiNumeriEstratti
- EventoRiepilogoTabellone
- EventoListaNumeriEstratti

### Contesto

Il report identifica E3 come gruppo di interrogazioni semplici e riepiloghi del tabellone.
La lettura di [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py) mostra che questo sottoinsieme e' composto da dataclass frozen con factory method che normalizzano tuple, conteggi e casi vuoti. In particolare, EventoUltimiNumeriEstratti limita difensivamente la lista ai richiesti e EventoRiepilogoTabellone forza ultimo_estratto a None quando non esistono ultimi estratti.

### Componenti coinvolti

- File di produzione target: [bingo_game/events/eventi_output_ui_umani.py](../../bingo_game/events/eventi_output_ui_umani.py)
- File di test da creare in fase implementativa: tests/unit/test_eventi_output_tabellone.py
- Riferimento analitico: [docs/4 - reports/report_lavori_test_eventi.md](../4%20-%20reports/report_lavori_test_eventi.md)
- Coordinatore documentale: [docs/todo.md](../todo.md)

### Scenari da coprire

#### EventoVerificaNumeroEstratto

- estratto_si() crea un evento con estratto=True
- estratto_no() crea un evento con estratto=False

#### EventoUltimoNumeroEstratto

- numero_presente() valorizza ultimo_numero con int
- nessuna_estrazione() valorizza ultimo_numero=None

#### EventoUltimiNumeriEstratti

- crea_con_numeri() converte la sequenza in tuple e calcola visualizzati=len(numeri)
- crea_con_numeri() mantiene solo gli ultimi richiesti elementi se la sequenza supera richiesti
- nessuna_estrazione() restituisce numeri=() e visualizzati=0

#### EventoRiepilogoTabellone

- crea() converte ultimi_estratti in tuple
- crea() calcola ultimi_visualizzati
- crea() imposta ultimo_estratto=None se ultimi_estratti e' vuoto anche quando l'input passa un valore diverso
- crea() preserva totale_numeri, totale_estratti, totale_mancanti e percentuale_estrazione

#### EventoListaNumeriEstratti

- crea() ordina numeri_estratti in modo crescente
- crea() converte la sequenza ordinata in tuple
- crea() calcola totale_estratti correttamente

### Decisioni architetturali

#### Decisione 1 - Priorita' ai rami di normalizzazione

In E3 i test devono concentrarsi soprattutto sui comportamenti derivati e difensivi, non sulla semplice assegnazione di campi.

#### Decisione 2 - Nessun mock in E3

Il gruppo usa solo primitivi e tuple. Non sono ammessi MagicMock o fixture esterne.

#### Decisione 3 - unittest-only

Il file dovra' usare esclusivamente unittest della standard library.

### Criteri di completamento

Il design E3 sara' considerato corretto quando il futuro file di test:

- usera' solo unittest
- restera' confinato a tests/unit/test_eventi_output_tabellone.py
- coprira' sia i casi positivi sia i casi vuoti o normalizzati dei factory method
