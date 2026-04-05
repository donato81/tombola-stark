---
type: todo
feature: ciclo_turno_fasi_reclami_collettivi
agent: Agent-Plan
status: IN_PROGRESS
version: v0.9.5
plan_ref: docs/3 - coding plans/PLAN_ciclo_turno_fasi_reclami_collettivi_v0.9.5.md
design_ref: docs/2 - projects/DESIGN_ciclo_turno_fasi_reclami_collettivi.md
date: 2026-04-01
report_ref: docs/4 - reports/REPORT_FATTIBILITA_FASI_TURNO_2026-04-01.md
---

## Metadati

tipo: todo_task
titolo: TODO separazione ciclo di turno in fasi distinte con verifica collettiva dei reclami
data_creazione: 2026-04-01
agente: Agent-Plan
stato: in_corso
feature: ciclo_turno_fasi_reclami_collettivi
versione_progetto: v0.9.5
plan: docs/3 - coding plans/PLAN_ciclo_turno_fasi_reclami_collettivi_v0.9.5.md
design: docs/2 - projects/DESIGN_ciclo_turno_fasi_reclami_collettivi.md
report: docs/4 - reports/REPORT_FATTIBILITA_FASI_TURNO_2026-04-01.md

## Riferimento PLAN

- Plan: [PLAN_ciclo_turno_fasi_reclami_collettivi_v0.9.5.md](../3%20-%20coding%20plans/PLAN_ciclo_turno_fasi_reclami_collettivi_v0.9.5.md)
- Design: [DESIGN_ciclo_turno_fasi_reclami_collettivi.md](../2%20-%20projects/DESIGN_ciclo_turno_fasi_reclami_collettivi.md)
- Report: [REPORT_FATTIBILITA_FASI_TURNO_2026-04-01.md](../4%20-%20reports/REPORT_FATTIBILITA_FASI_TURNO_2026-04-01.md)

## Contenuto

### Descrizione task

Separare il ciclo di turno monolitico di `Partita.esegui_turno()` in due fasi
esplicite — estrazione e verifica — con finestra di reclamo collettiva per umano
e bot. Correggere `verifica_premi()` per supportare la co-vincita con una logica
a doppia passata. Estendere `game_controller`, `comandi_partita`, `finestra_gioco`,
`BaseRenderer` e `WxRenderer` per supportare il flusso bifasico accessibile con NVDA.

### Priorita

P1

### Agente assegnato

Agent-CodeRouter

### Riferimento project/plan padre

- Project: [DESIGN_ciclo_turno_fasi_reclami_collettivi.md](../2%20-%20projects/DESIGN_ciclo_turno_fasi_reclami_collettivi.md)
- Plan: [PLAN_ciclo_turno_fasi_reclami_collettivi_v0.9.5.md](../3%20-%20coding%20plans/PLAN_ciclo_turno_fasi_reclami_collettivi_v0.9.5.md)
- Report: [REPORT_FATTIBILITA_FASI_TURNO_2026-04-01.md](../4%20-%20reports/REPORT_FATTIBILITA_FASI_TURNO_2026-04-01.md)

## Checklist operativa

### Passo 1 — Correzione verifica_premi (prerequisito)

- [x] Ristrutturare `verifica_premi()` in `partita.py` con doppia passata
- [x] Prima passata: raccogliere tutti i candidati validi per tipo senza assegnare
- [x] Seconda passata: assegnare il premio a tutti i candidati validi per tipo
- [x] Rimuovere chiusura anticipata del tipo premio durante la raccolta collettiva
- [x] Aggiornare i test in `test_partita.py` che verificano `verifica_premi()`
- [x] Verificare che il caso singolo vincitore non regredisca
- [x] Eseguire `pytest tests/test_partita.py` — tutti verdi prima di procedere

### Passo 2 — Split esegui_turno e attributo fase_turno_corrente

- [x] Aggiungere `fase_turno_corrente` a `Partita.__init__` (valore iniziale: `"attesa_estrazione"`)
- [x] Implementare `Partita.esegui_fase_estrazione() -> dict`
- [x] Implementare `Partita.esegui_fase_verifica() -> dict`
- [x] Mantenere `Partita.esegui_turno()` come wrapper compatibile
- [x] Aggiungere `turno_dichiarato_concluso: bool` a `GiocatoreBase`
- [x] Aggiungere metodo `GiocatoreBase.dichiara_fine_turno() -> None`
- [x] Aggiungere `Partita.tutti_hanno_dichiarato_fine() -> bool`
- [x] Valutare integrazione con `_passa_turno_core()` e decidere se richiamarla
- [x] Eseguire `pytest tests/test_partita.py` — tutti verdi prima di procedere

### Passo 3 — Wrapper game_controller e comandi_partita

- [x] Aggiungere `esegui_fase_estrazione_sicura(partita)` in `game_controller.py`
- [x] Aggiungere `esegui_fase_verifica_sicura(partita)` in `game_controller.py`
- [x] Mantenere `esegui_turno_sicuro(partita)` invariato
- [x] Aggiungere `esegui_fase_estrazione(partita)` in `ComandiSistema`
- [x] Aggiungere `esegui_fase_verifica(partita)` in `ComandiSistema`
- [x] Mantenere `esegui_turno(partita)` in `ComandiSistema` invariato
- [x] Aggiungere `dichiara_fine_turno(partita)` in `ComandiGiocatoreUmano`
- [x] Aggiungere test per nuovi metodi in `test_game_controller.py`
- [x] Aggiungere test per nuovi metodi in `test_comandi_partita.py`
- [x] Eseguire `pytest tests/test_game_controller.py tests/test_comandi_partita.py` — tutti verdi

### Passo 4 — Stato UI bifasico in finestra_gioco

- [x] Aggiungere `_fase_turno_ui` in `FinestraGioco.__init__`
- [x] Biforcazione contestuale di `_on_pulsante_principale()`
- [x] Ramo attesa estrazione: chiama fase estrazione, aggiorna display numero, cambia fase UI
- [x] Ramo attesa reclami: chiama fase verifica, annuncia premi, ripristina fase UI
- [x] Estendere `aggiorna_stato_pulsante` con etichette di fase
- [x] Aggiungere annuncio esplicito via vocalizzatore dopo ogni `SetLabel` (NVDA re-announce)
- [x] Verificare che `Ctrl+P` sia ancora associato correttamente
- [ ] Eseguire test non-GUI: `pytest tests/` — tutti verdi

### Passo 5 — Estensione BaseRenderer e WxRenderer

- [x] Aggiungere `annuncia_numero_estratto(numero, numero_turno)` come metodo astratto in `base_renderer.py`
- [x] Aggiungere `annuncia_premi_turno(premi)` come metodo astratto in `base_renderer.py`
- [x] Aggiungere `annuncia_fase_turno(fase)` come metodo astratto in `base_renderer.py`
- [x] Implementare `annuncia_numero_estratto` in `renderer_wx.py`
- [x] Implementare `annuncia_premi_turno` in `renderer_wx.py`
- [x] Implementare `annuncia_fase_turno` in `renderer_wx.py`
- [x] Aggiornare `finestra_gioco._annuncia_risultato_turno()` per usare le nuove primitive
- [x] Verificare che il log annunci riceva le voci come righe distinte
- [ ] Eseguire `pytest tests/` — tutti verdi

### Passo 6 — Test bifasici e aggiornamento suite esistente

- [x] Creare `tests/unit/test_fase_estrazione.py`
- [x] Creare `tests/unit/test_fase_verifica_co_vincita.py`
- [x] Creare `tests/unit/test_umano_dichiara_fine_turno.py`
- [x] Verificare `tests/integration/test_partita_bot_attivo.py` — 8 test invariati tramite wrapper
- [x] Verificare `tests/integration/test_event_coverage.py` — 3 test invariati
- [x] Verificare `tests/integration/test_logging_integration.py` — 2 test invariati
- [ ] Eseguire `pytest --cov=bingo_game tests/` — soglia coverage rispettata
- [x] Aggiornare questo TODO dopo ogni fase completata

## Note operative

- Il metodo compatibile `esegui_turno()` non va rimosso in questo ciclo.
  La rimozione e prevista per v1.0.0 fuori scope di questo piano.
- Ogni passo e atomico e committable separatamente.
- Il Passo 1 e prerequisito non negoziabile: non iniziare il Passo 2
  prima che tutti i test di `verifica_premi` siano verdi.
- La biforcazione in `finestra_gioco` (Passo 4) non introduce dipendenze
  verso i Passi 5, ma deve essere sviluppata dopo i Passi 2-3.
- Il Passo 6 va eseguito dopo tutti i passi implementativi.
- Verificare empiricamente il re-announce NVDA dell'etichetta pulsante
  su Windows con NVDA attivo prima di chiudere il Passo 4.

## Stato avanzamento

- Verifiche mirate rieseguite con esito verde: `tests/test_partita.py`, `tests/test_game_controller.py`, `tests/test_comandi_partita.py`, `tests/integration/test_partita_bot_attivo.py`, `tests/integration/test_event_coverage.py`, `tests/integration/test_logging_integration.py`, `tests/unit/test_fase_estrazione.py`, `tests/unit/test_fase_verifica_co_vincita.py`, `tests/unit/test_umano_dichiara_fine_turno.py`, `tests/unit/test_finestra_gioco_shortcuts.py`.
- Il full suite con coverage era già stato eseguito durante la validazione estesa e ha lasciato 10 failure residue, di cui 2 risolte con l'aggiornamento shortcut in `finestra_gioco.py`; resta comunque aperto il gate globale `pytest --cov=bingo_game tests/` finché non viene rieseguito e chiuso l'intero set residuo.
- La verifica empirica con NVDA reale resta manuale e non è stata automatizzata in questa sessione.
