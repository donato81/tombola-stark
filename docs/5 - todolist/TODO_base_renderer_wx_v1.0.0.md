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
stato: bozza
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

Agent-Code

### Riferimento project/plan padre

- Project: [DESIGN_base_renderer_wx_v1.0.0.md](../2%20-%20projects/DESIGN_base_renderer_wx_v1.0.0.md)
- Plan: [PLAN_base_renderer_wx_v1.0.0.md](../3%20-%20coding%20plans/PLAN_base_renderer_wx_v1.0.0.md)
- Report: [REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md](../4%20-%20reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md)

## Checklist operativa

### Passo 1 - Eliminazione renderer terminale

- [ ] Rileggere [bingo_game/ui/renderers/renderer_terminal.py](../../bingo_game/ui/renderers/renderer_terminal.py) prima della rimozione
- [ ] Confermare che le logiche pure da recuperare sono gia' documentate
- [ ] Eliminare [bingo_game/ui/renderers/renderer_terminal.py](../../bingo_game/ui/renderers/renderer_terminal.py)

### Passo 2 - Creazione BaseRenderer

- [ ] Creare [bingo_game/ui/renderers/base_renderer.py](../../bingo_game/ui/renderers/base_renderer.py)
- [ ] Definire `StatoConfigurazione` con i campi fissati nel design
- [ ] Definire i quattro metodi astratti pubblici di `BaseRenderer`
- [ ] Implementare il metodo concreto `_formatta_testo_da_catalogo()` senza stringhe hardcoded

### Passo 3 - Creazione WxRenderer

- [ ] Creare [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)
- [ ] Implementare il costruttore con injection di `wx.Frame` e `Vocalizzatore`
- [ ] Implementare `render_esito()` con gestione errore, evento e successo silenzioso
- [ ] Creare `_dispatch_evento()` coprendo tutte le famiglie evento previste
- [ ] Creare gli handler `_handle_*` come stub ordinati
- [ ] Separare esplicitamente i metodi `_wx_*` dai metodi `_ao2_*`

### Passo 4 - Verifica import rimasti su TerminalRenderer

- [ ] Cercare tutti i riferimenti a `TerminalRenderer` nel repository
- [ ] Aggiornare eventuali import produttivi se presenti
- [ ] Registrare l'impatto del test [tests/unit/test_renderer_report_finale.py](../../tests/unit/test_renderer_report_finale.py) senza riscriverlo in questo ciclo

### Passo 5 - Chiusura senza test

- [ ] Confermare che nessun test e' stato scritto in questo ciclo
- [ ] Confermare che nessun test legacy del renderer terminale e' stato adattato in questo ciclo
- [ ] Aggiornare questo TODO dopo ogni passo completato

## Note operative

- `_formatta_testo_da_catalogo()` e' il solo punto autorizzato di lookup e formattazione del catalogo.
- `mostra_schermata_configurazione()` riceve stato gia' deciso dal controller: il renderer non governa la sequenza.
- `mostra_report_finale()` deve documentare le chiavi attese in docstring e segnare come TODO il futuro `DatiReportFinale`.

## Stato Avanzamento

- [x] Pianificato
- [ ] In corso
- [ ] Completato
- [ ] Verificato