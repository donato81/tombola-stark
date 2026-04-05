---
type: design
feature: aggiornamento_documentazione_post_TUI
agent: Agent-Design
status: COMPLETED
version: v0.9.1
date: 2026-03-28
report_ref: docs/4 - reports/ANALISI_aggiornamento_documentazione_post_TUI_2026-03-28.md
---

# DESIGN aggiornamento_documentazione_post_TUI_2026-03-28

## Obiettivo

Definire come aggiornare la documentazione pubblica del progetto dopo la
rimozione della TUI, preservando la storia rilevante ma rimuovendo la
descrizione operativa di componenti non piu' presenti.

## Contesto

Il codice sorgente non espone piu' l'interfaccia TUI documentata in README.md,
docs/API.md e docs/ARCHITECTURE.md. Inoltre, la migrazione dei test da pytest a
unittest e la conversione di tests/test_silent_controller.py sono gia' avvenute,
ma alcuni riferimenti pubblici non sono ancora stati riallineati.

La documentazione va aggiornata con un criterio coerente:

- distinguere lo stato corrente del progetto dalla storia delle release;
- eliminare la documentazione operativa TUI non piu' eseguibile;
- mantenere valide le note storiche che aiutano a capire l'evoluzione;
- non inventare ancora la futura UI.

## Componenti coinvolti

| File | Ruolo nel redesign documentale |
|---|---|
| CHANGELOG.md | Allineare [Unreleased] alla rimozione TUI senza riscrivere i rilasci storici gia' taggati |
| docs/API.md | Rimuovere le sezioni API di TerminalUI e TUI Game Loop; neutralizzare i riferimenti TUI residui nei wrapper controller |
| docs/ARCHITECTURE.md | Sostituire la fotografia architetturale TUI con lo stato attuale post-rimozione |
| README.md | Rimuovere istruzioni d'uso TUI e inserire stato corrente dell'interfaccia |

## Decisioni di design

### Decisione 1 - CHANGELOG conservativo

Le sezioni storiche versionate che descrivono l'introduzione della TUI non vanno
cancellate. Sono parte della cronologia del prodotto. L'intervento dovra'
concentrarsi sulla sezione [Unreleased], che oggi comunica ancora come attuali
componenti ormai rimossi.

### Decisione 2 - API focalizzata sul presente

Le sezioni dedicate a TerminalUI e TUI Game Loop saranno rimosse integralmente
perche' descrivono moduli non presenti nel repository. I punti dell'API che
parlano della TUI come consumer dei wrapper saranno riscritti in modo neutro,
senza introdurre dettagli sulla futura UI.

Formulazioni target ammesse:

- interfaccia chiamante
- consumer UI
- layer di presentazione
- futura UI accessibile

Formulazioni da evitare:

- TUI
- TerminalUI
- game loop TUI
- tasti rapidi via msvcrt come percorso corrente

### Decisione 3 - ARCHITECTURE come fotografia corrente

docs/ARCHITECTURE.md deve passare da documento storico misto a fotografia dello
stato attuale. Le sezioni che descrivono `ui_terminale.py`, `tui_partita.py`,
`tui_commander.py` e `codici_tasti_tui.py` saranno sostituite da:

- descrizione del core domain/application ancora valido;
- nota sul layer UI attualmente non definito o in transizione;
- elenco dei moduli residui dell'area UI eventualmente ancora presenti ma non
  piu' orchestrati come interfaccia completa.

### Decisione 4 - README senza falsa operativita'

README.md non deve piu' dire all'utente di avviare `python main.py` per entrare
nel game loop TUI, ne' presentare comandi e tasti rapidi non piu' supportati.
La sezione d'uso sara' sostituita con una nota di stato che chiarisce:

- motore di gioco e test ancora presenti;
- interfaccia terminale rimossa;
- nuova UI non ancora descritta in documentazione.

### Decisione 5 - Aggiornamento test minimizzato

Non serve ridisegnare la documentazione dei test. Il framework ufficiale e'
gia' unittest in README.md e docs/ARCHITECTURE.md. L'intervento si limita a:

- rimuovere eventuali menzioni residue a pytest come baseline corrente;
- aggiornare il riferimento a tests/test_silent_controller.py da capsys a
  migrazione completata su unittest con cattura stdout non-pytest.

## Criteri di accettazione

1. Nessun documento pubblico descrive piu' TerminalUI o TUI Game Loop come
   funzionalita' correnti del progetto.
2. CHANGELOG.md conserva la storia versionata e riallinea solo la narrativa di
   [Unreleased] allo stato post-rimozione TUI.
3. README.md non contiene piu' istruzioni operative basate su comandi TUI o
   tasti rapidi via msvcrt.
4. docs/API.md non contiene piu' le sezioni dei moduli rimossi e non usa TUI
   come consumer implicito delle API ancora valide.
5. docs/ARCHITECTURE.md continua a dichiarare unittest come stack di test.
6. La documentazione di tests/test_silent_controller.py non cita piu' capsys come
   stato corrente del file.

## Vincoli

- Nessuna modifica al codice sorgente in questo task.
- Nessuna invenzione sulla nuova UI oltre a un placeholder di stato.
- Nessuna perdita di cronologia utile delle release passate.
- Linguaggio coerente con l'accessibilita': descrivere stato e limiti in modo
  diretto, senza marketing o ambiguita'.

## Coding plans correlati

- docs/3 - coding plans/PLAN_aggiornamento_documentazione_post_TUI_2026-03-28.md

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Approvato
- [ ] Archiviato