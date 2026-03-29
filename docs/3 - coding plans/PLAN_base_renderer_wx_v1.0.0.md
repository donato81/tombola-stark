---
type: plan
feature: base_renderer_wx
agent: Agent-Plan
status: DRAFT
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_base_renderer_wx_v1.0.0.md
date: 2026-03-30
report_ref: docs/4 - reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo introduzione BaseRenderer e WxRenderer
data_creazione: 2026-03-30
agente: Agent-Plan
stato: bozza
feature: base_renderer_wx
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_base_renderer_wx_v1.0.0.md
report: docs/4 - reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md

## Contenuto

### Executive Summary

Tipo intervento: introduzione nuovo layer UI
Priorita': P1
Branch: main
Versione di riferimento: v1.0.0
Scope: definire e creare il nuovo contratto renderer wx, eliminando il renderer terminale
Vincolo: nessun test in questo ciclo; solo struttura produttiva e riallineamento import

### Problema e Obiettivo

Il progetto possiede ancora un solo renderer,
[bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py),
costruito per una UI testuale basata su `Sequence[str]`. Questo contratto non e'
compatibile con la futura interfaccia wxPython accessibile.

L'obiettivo del ciclo successivo sara' introdurre due nuovi moduli produttivi:

- [bingo_game/ui/renderers/base_renderer.py](bingo_game/ui/renderers/base_renderer.py)
- [bingo_game/ui/renderers/renderer_wx.py](bingo_game/ui/renderers/renderer_wx.py)

e preparare la rimozione del renderer terminale senza ancora entrare nel merito
dei test di comportamento.

### Approccio tecnico

L'implementazione dovra' seguire una sequenza strettamente ordinata.

Prima si elimina il vecchio punto di verita' terminale, poi si introduce il
contratto astratto, poi il renderer wx con struttura completa ma handler ancora
stub, infine si censiscono e riallineano gli import ancora ancorati a
`TerminalRenderer`.

Il piano non prevede test in questo ciclo. Eventuali file di test impattati dalla
rimozione del renderer terminale vengono solo censiti come dipendenze note.

### File coinvolti

- [bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py) - DELETE
- [bingo_game/ui/renderers/base_renderer.py](bingo_game/ui/renderers/base_renderer.py) - CREATE
- [bingo_game/ui/renderers/renderer_wx.py](bingo_game/ui/renderers/renderer_wx.py) - CREATE
- [bingo_game/ui/renderers/__init__.py](bingo_game/ui/renderers/__init__.py) - MODIFY se necessario per export espliciti
- [tests/unit/test_renderer_report_finale.py](tests/unit/test_renderer_report_finale.py) - ANALYZE ONLY in questo ciclo; impatto noto da pianificare dopo
- [docs/4 - reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md](../4%20-%20reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md) - CREATE
- [docs/2 - projects/DESIGN_base_renderer_wx_v1.0.0.md](../2%20-%20projects/DESIGN_base_renderer_wx_v1.0.0.md) - CREATE
- [docs/3 - coding plans/PLAN_base_renderer_wx_v1.0.0.md](../3%20-%20coding%20plans/PLAN_base_renderer_wx_v1.0.0.md) - CREATE
- [docs/5 - todolist/TODO_base_renderer_wx_v1.0.0.md](../5%20-%20todolist/TODO_base_renderer_wx_v1.0.0.md) - CREATE
- [docs/todo.md](../todo.md) - UPDATE

### Fasi sequenziali

#### Fase 1 - Eliminazione renderer_terminal.py

File coinvolti:

- [bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py)

Operazione:

- DELETE

Dipendenze:

- nessuna dipendenza precedente
- ma richiede che il contenuto analitico e le logiche pure siano gia' state
  documentate nel report e nel design

Nota:

- eliminare il file, non rinominarlo e non adattarlo

#### Fase 2 - Creazione base_renderer.py

File coinvolti:

- [bingo_game/ui/renderers/base_renderer.py](bingo_game/ui/renderers/base_renderer.py)

Operazione:

- CREATE

Contenuto atteso:

- dataclass `StatoConfigurazione`
- classe astratta `BaseRenderer`
- quattro metodi astratti pubblici
- metodo concreto `_formatta_testo_da_catalogo()`

Dipendenze:

- Fase 1 completata logicamente
- usa le decisioni fissate in
  [DESIGN_base_renderer_wx_v1.0.0.md](../2%20-%20projects/DESIGN_base_renderer_wx_v1.0.0.md)

#### Fase 3 - Creazione renderer_wx.py

File coinvolti:

- [bingo_game/ui/renderers/renderer_wx.py](bingo_game/ui/renderers/renderer_wx.py)

Operazione:

- CREATE

Contenuto atteso:

- costruttore con injection di `wx.Frame` e `Vocalizzatore`
- metodo `render_esito()` completo
- dispatcher `_dispatch_evento()` completo
- metodi `_wx_*` e `_ao2_*`
- handler privati presenti come struttura completa ma con corpo stub

Dipendenze:

- richiede l'esistenza di [bingo_game/ui/renderers/base_renderer.py](bingo_game/ui/renderers/base_renderer.py)
- riusa il catalogo bloccato in [bingo_game/ui/locales/it.py](bingo_game/ui/locales/it.py)
- riusa il wrapper [my_lib/vocalizzatore.py](my_lib/vocalizzatore.py)

#### Fase 4 - Aggiornamento import che referenziano TerminalRenderer

File coinvolti:

- [bingo_game/ui/renderers/__init__.py](bingo_game/ui/renderers/__init__.py) se necessario
- [tests/unit/test_renderer_report_finale.py](tests/unit/test_renderer_report_finale.py) come riferimento noto

Operazione:

- MODIFY solo dove indispensabile per non lasciare import produttivi rotti
- ANALYZE ONLY sui test fuori scope

Esito atteso della verifica nel repository attuale:

- nessun import produttivo di `TerminalRenderer`
- un solo import di test in
  [tests/unit/test_renderer_report_finale.py](tests/unit/test_renderer_report_finale.py)

Decisione operativa:

- aggiornare gli eventuali import produttivi se esistono
- registrare il file di test come follow-up, senza riscriverlo in questo ciclo

Dipendenze:

- Fasi 2 e 3 completate

#### Fase 5 - Nessun test in questo ciclo

File coinvolti:

- nessun nuovo file di test

Operazione:

- nessuna implementazione test
- nessuna riscrittura dei test legacy del renderer terminale

Dipendenze:

- vincolo trasversale a tutte le fasi precedenti

### Dipendenze

- [docs/4 - reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md](../4%20-%20reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md)
- [docs/2 - projects/DESIGN_base_renderer_wx_v1.0.0.md](../2%20-%20projects/DESIGN_base_renderer_wx_v1.0.0.md)
- [my_lib/vocalizzatore.py](my_lib/vocalizzatore.py)
- [bingo_game/ui/locales/it.py](bingo_game/ui/locales/it.py)

### Rischi

- copiare nel nuovo dispatcher la duplicazione del reclamo presente nel terminal renderer
- eliminare il renderer terminale senza censire il test ancora ancorato al vecchio contratto
- far scivolare logica di sequenza della configurazione dentro il renderer
- rendere `_formatta_testo_da_catalogo()` troppo debole, costringendo gli handler a gestire lookup manuali
- introdurre un `renderer_wx.py` troppo pieno di logica concreta invece che di perimetro e stub ordinati

### Project padre

- [docs/2 - projects/DESIGN_base_renderer_wx_v1.0.0.md](../2%20-%20projects/DESIGN_base_renderer_wx_v1.0.0.md)

### Criteri di completamento

- `renderer_terminal.py` eliminato
- `base_renderer.py` creato con contratto definitivo e `StatoConfigurazione`
- `renderer_wx.py` creato con struttura completa e handler stub
- nessun import produttivo rimasto verso `TerminalRenderer`
- nessun test scritto o riscritto in questo ciclo

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso