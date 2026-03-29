---
type: todo
feature: base_renderer_wx
agent: Agent-Plan
status: DRAFT
version: v1.0.0
plan_ref: docs/3 - coding plans/PLAN_base_renderer_wx_v1.0.0.md
design_ref: docs/2 - projects/DESIGN_base_renderer_wx_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md
---

## Metadati

tipo: todo_task
titolo: TODO introduzione BaseRenderer e WxRenderer
data_creazione: 2026-03-30
agente: Agent-Plan
stato: in_corso
feature: base_renderer_wx
versione_progetto: v1.0.0
plan: docs/3 - coding plans/PLAN_base_renderer_wx_v1.0.0.md
design: docs/2 - projects/DESIGN_base_renderer_wx_v1.0.0.md
report: docs/4 - reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md

## Contenuto

### Descrizione task

Introdurre il nuovo layer UI wxPython composto da `BaseRenderer` e `WxRenderer`,
preparando la rimozione del renderer terminale e congelando il nuovo contratto di
presentazione senza entrare nel ciclo test.

### Priorita

P1

### Agente assegnato

Agent-Code (via Agent-CodeRouter)

### Riferimento project/plan padre

- Project: [DESIGN_base_renderer_wx_v1.0.0.md](../2%20-%20projects/DESIGN_base_renderer_wx_v1.0.0.md)
- Plan: [PLAN_base_renderer_wx_v1.0.0.md](../3%20-%20coding%20plans/PLAN_base_renderer_wx_v1.0.0.md)
- Report: [REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md](../4%20-%20reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md)

## Checklist operativa

### Passo 1 - Creazione BaseRenderer

- [x] Creare [bingo_game/ui/renderers/base_renderer.py](../../bingo_game/ui/renderers/base_renderer.py)
- [x] Definire `StatoConfigurazione` con i campi fissati nel design (dataclass frozen)
- [x] Definire i quattro metodi astratti pubblici di `BaseRenderer`
- [x] Implementare il metodo concreto `_formatta_testo_da_catalogo()` senza stringhe hardcoded

### Passo 2 - Creazione WxRenderer

- [x] Creare [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)
- [x] Implementare il costruttore con injection di `wx.Frame` e `Vocalizzatore`
- [x] Implementare `render_esito()` con gestione errore, evento e successo silenzioso
- [x] Creare `_dispatch_evento()` coprendo tutte le famiglie evento previste (senza duplicazioni)
- [x] Creare gli handler `_handle_*` come stub strutturali ordinati per famiglia
- [x] Separare esplicitamente i metodi `_wx_*` dai metodi `_ao2_*`

### Passo 3 - Verifica import rimasti su TerminalRenderer

- [x] Cercare tutti i riferimenti a `TerminalRenderer` nel repository
- [x] Nessun import produttivo trovato; repository produttivo gia' pulito
- [x] Registrato impatto noto: [tests/unit/test_renderer_report_finale.py](../../tests/unit/test_renderer_report_finale.py) importa ancora `TerminalRenderer` — da gestire nel ciclo test successivo, fuori scope in questo ciclo
- [x] Aggiornato [bingo_game/ui/renderers/__init__.py](../../bingo_game/ui/renderers/__init__.py) con export espliciti

### Passo 4 - Eliminazione renderer_terminal.py

- [x] Eliminare [bingo_game/ui/renderers/renderer_terminal.py](../../bingo_game/ui/renderers/renderer_terminal.py)

Conferma utente ricevuta tramite guardia eliminazione file. Il renderer terminale
e' stato rimosso solo dopo la presenza del nuovo contratto (`base_renderer.py`),
del nuovo renderer wx (`renderer_wx.py`) e dopo verifica che nessun import
produttivo residuo lo referenziasse piu'.

### Passo 5 - Chiusura senza test

- [x] Confermato: nessun test e' stato scritto in questo ciclo
- [x] Confermato: nessun test legacy del renderer terminale e' stato adattato in questo ciclo
- [x] Impatto noto registrato al Passo 3

## Note operative

- `_formatta_testo_da_catalogo()` e' il solo punto autorizzato di lookup e formattazione del catalogo.
- `mostra_schermata_configurazione()` riceve stato gia' deciso dal controller: il renderer non governa la sequenza.
- `mostra_report_finale()` documenta le chiavi attese in docstring e segna come TODO il futuro `DatiReportFinale`.
- Gli handler `_handle_*` in `WxRenderer` sono stub strutturali: la logica widget e vocale verra' completata nel ciclo successivo.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [x] Completato
- [x] Verificato