---
type: plan
feature: aggiornamento_documentazione_post_TUI
agent: Agent-Plan
status: COMPLETED
version: v0.9.1
date: 2026-03-28
design_ref: docs/2 - projects/DESIGN_aggiornamento_documentazione_post_TUI_2026-03-28.md
report_ref: docs/4 - reports/ANALISI_aggiornamento_documentazione_post_TUI_2026-03-28.md
---

# PLAN aggiornamento_documentazione_post_TUI_2026-03-28

## Problema da risolvere

La documentazione pubblica del progetto mostra ancora la TUI come interfaccia
corrente, nonostante i moduli correlati siano stati rimossi. In parallelo, la
parte test e' gia' quasi allineata a unittest, ma esistono ancora riferimenti
locali obsoleti come la menzione di capsys per tests/test_silent_controller.py.

Obiettivo del piano: aggiornare CHANGELOG.md, docs/API.md,
docs/ARCHITECTURE.md e README.md in modo coerente con lo stato attuale del
repository, senza cambiare codice e senza introdurre una nuova UI fittizia.

## Approccio tecnico

L'implementazione documentale verra' eseguita in quattro blocchi logici, con
validazione finale di coerenza trasversale.

### Fase 1 - Pulizia CHANGELOG.md

Scopo:

- riallineare [Unreleased] allo stato post-rimozione TUI;
- mantenere intatte le release storiche gia' versionate;
- conservare le voci recenti corrette su unittest e silent controller.

Azioni previste:

1. Identificare le voci in [Unreleased] che parlano come attuali di moduli TUI rimossi.
2. Consolidarle in una o piu' voci che descrivano la rimozione TUI o il cleanup documentale.
3. Verificare che le voci su migrazione pytest -> unittest e su
   tests/test_silent_controller.py restino coerenti e non duplicate.

### Fase 2 - Aggiornamento docs/API.md

Scopo:

- rimuovere sezioni intere non piu' valide;
- neutralizzare i riferimenti TUI ancora presenti nelle API rimaste valide.

Azioni previste:

1. Eliminare il blocco Livello Interfaccia - TerminalUI.
2. Eliminare il blocco Livello Interfaccia - TUI Game Loop.
3. Riscrivere i riferimenti sparsi alla TUI nei wrapper e nelle note di versione.
4. Aggiornare il riferimento a tests/test_silent_controller.py, rimuovendo il
   richiamo a capsys come stato corrente.

### Fase 3 - Aggiornamento docs/ARCHITECTURE.md

Scopo:

- far corrispondere il documento alla struttura reale del repository;
- mantenere valida la parte testing gia' aggiornata a unittest.

Azioni previste:

1. Sostituire i diagrammi e le tabelle che citano ui_terminale.py e i moduli TUI rimossi.
2. Aggiornare la sezione UI per riflettere lo stato attuale: layer in transizione,
   eventuali moduli residui non equivalenti a una UI completa.
3. Conservare esplicitamente la nota che unittest e' il framework di test corrente.

### Fase 4 - Aggiornamento README.md

Scopo:

- evitare istruzioni non eseguibili;
- presentare correttamente lo stato del progetto al lettore esterno.

Azioni previste:

1. Rimuovere la feature bullet del Menu TUI accessibile.
2. Rimuovere la sezione Come si gioca basata sul game loop TUI.
3. Rimuovere la sezione Tasti Rapidi via msvcrt.
4. Inserire un placeholder chiaro sullo stato dell'interfaccia: TUI rimossa,
   motore di gioco e suite test ancora presenti, nuova UI non ancora documentata.

### Fase 5 - Validazione finale

Scopo:

- confermare che i quattro documenti non si contraddicano;
- verificare che i riferimenti ai test siano coerenti.

Checklist di uscita:

- nessuna sezione pubblica descrive la TUI come UI attuale;
- unittest resta l'unico framework di test dichiarato come standard corrente;
- tests/test_silent_controller.py non e' piu' descritto come file capsys-based;
- README.md non contiene istruzioni di gioco non piu' eseguibili.

## File da modificare

- CHANGELOG.md
- docs/API.md
- docs/ARCHITECTURE.md
- README.md

## Dipendenze

- docs/4 - reports/ANALISI_aggiornamento_documentazione_post_TUI_2026-03-28.md
- docs/2 - projects/DESIGN_aggiornamento_documentazione_post_TUI_2026-03-28.md
- docs/4 - reports/REPORT_DIAGNOSTICA_PROGETTO_2026-03-28.md
- docs/4 - reports/REPORT_FIX_UNICODE_PRINT_2026-03-28.md
- docs/4 - reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md

## Rischi

| Rischio | Impatto | Mitigazione |
|---|---|---|
| Cancellare storia utile dal changelog | Medio | Limitare il rewrite a [Unreleased] e lasciare intatte le release storiche |
| Sostituire riferimenti TUI con descrizioni troppo vaghe | Medio | Usare formule neutrali ma verificabili, senza inventare la nuova UI |
| Lasciare incoerenze sui test tra documenti | Medio | Ricontrollare unittest e silent controller in tutti i file target |
| Documentare come attivo un modulo solo residuale o orfano | Alto | Basarsi solo su repository attuale e report diagnostico gia' raccolto |

## Project padre

- docs/2 - projects/DESIGN_aggiornamento_documentazione_post_TUI_2026-03-28.md

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso