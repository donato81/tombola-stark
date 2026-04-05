---
tipo: report
titolo: Analisi aggiornamento documentazione post-rimozione TUI
data_creazione: 2026-03-28
agente: Agent-Analyze
stato: bozza
task: aggiornamento_documentazione_post_TUI
versione_progetto: v0.9.1
---

# Analisi aggiornamento documentazione post-rimozione TUI

## Trigger

Allineare la documentazione pubblica dopo la rimozione della TUI, senza ancora
modificare i documenti target. L'analisi copre esclusivamente:

- CHANGELOG.md
- docs/API.md
- docs/ARCHITECTURE.md
- README.md
- docs/4 - reports/REPORT_DIAGNOSTICA_PROGETTO_2026-03-28.md
- docs/4 - reports/REPORT_FIX_UNICODE_PRINT_2026-03-28.md
- docs/4 - reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md
- docs/todo.md

## Sommario esecutivo

La rimozione dei moduli TUI e la migrazione progressiva della suite verso
unittest non sono ancora riflesse in modo coerente nella documentazione
pubblica. La situazione attuale e' asimmetrica:

- README.md e docs/ARCHITECTURE.md dichiarano gia' unittest come framework di test.
- docs/API.md contiene ancora sezioni intere dedicate a TerminalUI e TUI Game Loop.
- README.md descrive ancora il flusso di gioco TUI e i tasti rapidi via msvcrt.
- CHANGELOG.md in [Unreleased] contiene ancora voci positive su file TUI rimossi.
- docs/ARCHITECTURE.md documenta componenti UI non piu' presenti, ma conserva
  correttamente la nota sul passaggio a unittest nel tech stack.

Conclusione: l'aggiornamento richiesto e' principalmente documentale e di
riallineamento narrativo. Non servono modifiche al codice in questa fase.

## Dettaglio osservazioni

### 1. Sezioni TUI residue da rimuovere o sostituire

| Documento | Sezioni residue | Azione consigliata |
|---|---|---|
| CHANGELOG.md | [Unreleased] linee 38-51, 101-114, 125-130: voci Added/Changed su tui_commander.py, codici_tasti_tui.py, tui_partita.py e test TUI | Sostituire con una voce Removed/Changed che fotografa la rimozione TUI. Non riscrivere la storia delle release taggate gia' pubblicate. |
| docs/API.md | linee 1620-1709: sezioni Livello Interfaccia - TerminalUI e TUI Game Loop | Rimuovere o sostituire con una sezione di stato transitorio della UI. |
| docs/API.md | linee 870, 872, 980, 1074, 1105, 1138, 1153, 1184, 1205: riferimenti puntuali alla TUI come consumer dei wrapper/controller | Sostituire TUI con formulazione neutra: interfaccia chiamante, consumer UI, futura UI accessibile. |
| docs/ARCHITECTURE.md | linea 81: diagramma con ui_terminale.py; linee 188-220: tabella componenti UI e flusso TUI; linee 485-490 e 535-538: albero directory e responsabilita' UI; linee 743-748: timeline centrata sulla TUI | Riscrivere per lo stato post-rimozione: UI rimossa, renderers/locales residui, nuova UI non ancora definita. |
| README.md | linea 26: feature Menu TUI accessibile; linee 87-140: Come si gioca e Tasti Rapidi | Rimuovere la guida TUI operativa e inserire un placeholder sullo stato corrente dell'interfaccia. |

### 2. Stato della documentazione dei test

| Domanda | Evidenza | Esito |
|---|---|---|
| Il progetto dichiara gia' unittest come framework ufficiale? | docs/ARCHITECTURE.md linea 55 e README.md linee 292-299 indicano unittest | Si, coerente |
| La documentazione pubblica riflette gia' la rimozione di pytest? | REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md conferma la direzione architetturale; CHANGELOG.md contiene le voci della migrazione | Parzialmente si |
| Lo stato di tests/test_silent_controller.py e' documentato correttamente ovunque? | CHANGELOG.md documenta la migrazione a unittest; docs/API.md linea 1708 parla ancora di 15 test capsys in test_silent_controller.py | No, API.md e' da aggiornare |

Sintesi: la narrativa generale sui test e' gia' orientata a unittest, quindi non
serve una nuova sezione estesa sui test. Serve invece correggere i riferimenti
residui obsoleti, in particolare il richiamo a capsys nel changelog API interno.

### 3. Rilevanza dei report recenti

| Report | Impatto sul task |
|---|---|
| REPORT_DIAGNOSTICA_PROGETTO_2026-03-28.md | Fonte principale: mappa esatta le incongruenze post-rimozione TUI e separa moduli orfani, file rotti e documenti da aggiornare |
| REPORT_FIX_UNICODE_PRINT_2026-03-28.md | Nessun nuovo aggiornamento sostanziale richiesto ai documenti pubblici oltre a mantenere le voci gia' esistenti |
| REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md | Conferma che la direzione corretta e' unittest; utile solo per verificare che i documenti non parlino ancora di pytest come baseline |

### 4. Vincoli tecnici e redazionali

- Non modificare ancora CHANGELOG.md, docs/API.md, docs/ARCHITECTURE.md o README.md.
- Mantenere separate le informazioni storiche di release da quelle di stato attuale.
- Evitare placeholder vaghi: il README deve esplicitare che la TUI e' stata
  rimossa e che una nuova UI non e' ancora documentata.
- Non introdurre nuovi dettagli di codice o architettura non verificati dai file letti.

## Raccomandazioni

1. Trattare CHANGELOG.md in modo conservativo: aggiornare solo [Unreleased] e non
   cancellare le sezioni storiche versionate che descrivono rilasci passati.
2. Ripulire docs/API.md in due passaggi logici: rimozione delle sezioni TUI intere,
   poi sostituzione dei riferimenti TUI puntuali con terminologia neutra.
3. Riscrivere docs/ARCHITECTURE.md come fotografia dello stato attuale, non come
   archivio della TUI rimossa.
4. Sostituire in README.md le istruzioni operative TUI con un paragrafo di stato:
   motore di gioco attivo, interfaccia utente in ridefinizione.
5. Limitare gli aggiornamenti legati ai test a correzioni puntuali: unittest e'
   gia' il riferimento corretto; il solo residuo evidente e' la menzione capsys.

## File analizzati

- CHANGELOG.md
- docs/API.md
- docs/ARCHITECTURE.md
- README.md
- docs/4 - reports/REPORT_DIAGNOSTICA_PROGETTO_2026-03-28.md
- docs/4 - reports/REPORT_FIX_UNICODE_PRINT_2026-03-28.md
- docs/4 - reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md
- docs/todo.md

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Condiviso