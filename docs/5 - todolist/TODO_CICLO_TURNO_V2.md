---
type: todo
feature: ciclo_turno_v2
version: v1.0
date: 2026-04-01
status: IN_PIANIFICAZIONE
plan_ref: docs/3 - coding plan/PLAN_CICLO_TURNO_V2.md
design_ref: docs/2 - projects/DESIGN_CICLO_TURNO_V2.md
---

## Metadati

tipo: todo_per_feature
titolo: Todo operativo — Ciclo di Turno V2
versione: v1.0
data: 2026-04-01
stato: IN_PIANIFICAZIONE

---

## Aggiornamento implementazione

- 2026-04-01 — Completate Azione 2 e Azione 3 della sotto-fase D in `bingo_game/ui/finestra_gioco.py`.
- Azione 2: `_on_tick_pausa()` riporta la UI in `attesa_estrazione` e invoca automaticamente `_on_pulsante_principale(None)` per riaprire subito il turno successivo.
- Azione 3: aggiunto `_ferma_tutti_i_timer()` e usato nei passaggi tra finestra d'azione, timeout, terminazione anticipata e pausa per impedire timer attivi contemporaneamente.
- Validazione automatica eseguita: `tests/unit/test_ciclo_turno_v2_azioni_2_3.py`, `tests/unit/test_ciclo_turno_v2_timeout_umano.py`, `tests/unit/test_ciclo_turno_v2_tutti_pronti.py`, `tests/unit/test_ciclo_turno_v2_early_exit.py`, `tests/unit/test_ciclo_turno_v2_config.py` -> 33 test verdi.

---

## Prerequisiti (da verificare prima di iniziare)

- [ ] PRE-1 — Decidere il valore del tetto massimo `durata_finestra_azione_max_multiplayer_secondi`
  con l'utente. File da aggiornare: `DESIGN_CICLO_TURNO_V2.md` e `PLAN_CICLO_TURNO_V2.md`.
- [ ] PRE-2 — Eseguire `py -3.x -m unittest discover tests -q` e verificare 0 fallimenti
  sulla base corrente prima di iniziare qualsiasi modifica.
- [ ] PRE-3 — Impostare `DESIGN_CICLO_TURNO_V2.md` in stato REVIEWED dopo revisione utente.

---

## Task di implementazione

### Sotto-fase A — Dominio: disaccoppiamento reclami bot

| N | Descrizione | File coinvolto | Dipendenza | Criterio di completamento |
|---|-------------|----------------|-----------|--------------------------|
| A-1 | Rimuovere da `esegui_fase_estrazione()` il blocco che itera i bot e registra `reclamo_turno` | `bingo_game/partita.py` | PRE-2 completata | Il metodo non modifica `reclamo_turno` di nessun bot dopo l'estrazione |
| A-2 | Modificare `tutti_hanno_dichiarato_fine()` per includere anche i giocatori automatici nel controllo | `bingo_game/partita.py` | A-1 completata | Il metodo ritorna `False` se anche un solo bot ha `turno_dichiarato_concluso == False` |
| A-3 | Aggiornare `test_fase_estrazione.py`: rimuovere l'aspettativa che i bot abbiano `reclamo_turno` impostato dopo la fase di estrazione | `tests/unit/test_fase_estrazione.py` | A-1 completata | Test verde; nessun `AssertionError` su reclami bot |
| A-4 | Aggiornare `test_partita_bot_attivo.py`: adattare i test che si aspettano reclami bot nel risultato di `esegui_fase_estrazione()` o `esegui_turno()` | `tests/integration/test_partita_bot_attivo.py` | A-1 completata | Tutti i test del file sono verdi |
| A-5 | Verificare `test_partita.py` e `test_game_controller.py`: identificare e aggiornare i casi che dipendono dalla registrazione immediata dei reclami bot | `tests/test_partita.py`, `tests/test_game_controller.py` | A-1 completata | Nessun test rotto nei due file |
| A-6 | Verificare `test_game_controller_loop.py`: stessa analisi | `tests/unit/test_game_controller_loop.py` | A-1 completata | File verde |
| A-7 | Eseguire la pre-commit checklist completa; committare la sotto-fase A | tutti i file A | A-3, A-4, A-5, A-6 completati | Exit code 0 da `unittest discover`; commit atomico con messaggio convenzionale |

---

### Sotto-fase B — Dominio: dichiarazione fine fase per i bot

| N | Descrizione | File coinvolto | Dipendenza | Criterio di completamento |
|---|-------------|----------------|-----------|--------------------------|
| B-1 | Creare `dichiara_fine_fase_azione(premi_gia_assegnati, premi_tipo_chiusi)` in `GiocatoreAutomatico`: chiama `_valuta_potenziale_reclamo()`, imposta `reclamo_turno`, chiama `dichiara_fine_turno()` | `bingo_game/players/giocatore_automatico.py` | A-7 completata | Il metodo imposta `reclamo_turno` e `turno_dichiarato_concluso == True` |
| B-2 | Creare `tests/unit/test_ciclo_turno_v2_bot_declaration.py` con test per `dichiara_fine_fase_azione()` | `tests/unit/test_ciclo_turno_v2_bot_declaration.py` | B-1 completata | Almeno 4 test verdi: no reclamo, ambo, tombola, reset corretto tra turni |
| B-3 | Creare `tests/unit/test_ciclo_turno_v2_early_exit.py`: verifica che quando tutti dichiarano fine `tutti_hanno_dichiarato_fine()` torni `True` | `tests/unit/test_ciclo_turno_v2_early_exit.py` | B-1, A-2 completati | Test verde con umano + 1 bot |
| B-4 | Creare `tests/unit/test_ciclo_turno_v2_tutti_pronti.py`: verifica la nuova semantica di `tutti_hanno_dichiarato_fine()` con più bot | `tests/unit/test_ciclo_turno_v2_tutti_pronti.py` | A-2 completata | Test verde con 1 umano + 3 bot |
| B-5 | Pre-commit checklist; committare la sotto-fase B | tutti i file B | B-2, B-3, B-4 completati | Exit code 0; commit atomico |

---

### Sotto-fase C — Renderer: nuovi annunci vocali

| N | Descrizione | File coinvolto | Dipendenza | Criterio di completamento |
|---|-------------|----------------|-----------|--------------------------|
| C-1 | Aggiungere metodi astratti `annuncia_avviso_timeout(secondi_rimanenti)`, `annuncia_avvio_pausa_turno(secondi)`, `annuncia_tutti_pronti()` a `BaseRenderer` | `bingo_game/ui/renderers/base_renderer.py` | B-5 completata | Classe astratta non istanziabile se i metodi non sono implementati |
| C-2 | Implementare i tre metodi in `WxRenderer` seguendo il pattern: testo catalogo → log widget → AO2 speak | `bingo_game/ui/renderers/renderer_wx.py` | C-1 completata | `WxRenderer` istanziabile senza errori |
| C-3 | Aggiungere 7 nuove chiavi testo in `it.py`: `TURNO_AVVISO_60`, `TURNO_AVVISO_80`, `TURNO_AVVISO_95`, `TURNO_TIMEOUT_SALTATO`, `TURNO_TUTTI_PRONTI`, `TURNO_PAUSA_INIZIO`, `TURNO_PAUSA_COUNTDOWN` | `bingo_game/ui/locales/it.py` | C-1 completata | Le chiavi sono presenti nel dizionario corretto |
| C-4 | Creare `tests/unit/test_ciclo_turno_v2_avvisi_vocali.py` con renderer stub; verificare che i tre metodi vengano chiamati | `tests/unit/test_ciclo_turno_v2_avvisi_vocali.py` | C-2, C-3 completati | Test verde con renderer stub |
| C-5 | Pre-commit checklist; committare la sotto-fase C | tutti i file C | C-4 completata | Exit code 0; commit atomico |

---

### Sotto-fase D — UI: timer, pianificazione bot, pausa

| N | Descrizione | File coinvolto | Dipendenza | Criterio di completamento |
|---|-------------|----------------|-----------|--------------------------|
| D-1 | Aggiungere attributo `_durata_finestra_ms` e `_durata_pausa_ms` al costruttore di `FinestraGioco` | `bingo_game/ui/finestra_gioco.py` | C-5 completata | I valori sono letti dai parametri con default 60000 e 5000 ms |
| D-2 | Implementare `_avvia_timer_azione(durata_ms)` e `_on_tick_azione(event)` con calcolo percentuale e avvisi vocali | `bingo_game/ui/finestra_gioco.py` | D-1 completata | Gli avvisi vengono emessi ai corretti valori percentuali |
| D-3 | Implementare `_on_timeout_azione()`: eventuale skip reclamo umano + avanzamento a verifica | `bingo_game/ui/finestra_gioco.py` | D-2 completata | La fase 3 parte al timeout; nessun blocco se umano non ha dichiarato fine |
| D-4 | Implementare `_on_all_ready()`: ferma il timer + avanza a verifica in anticipo | `bingo_game/ui/finestra_gioco.py` | D-2 completata | La fase 3 parte prima del timeout quando tutti sono pronti |
| D-5 | Implementare `_pianifica_risposta_bot()`: calcola ritardi casuali e schedula `wx.CallLater` per ogni bot | `bingo_game/ui/finestra_gioco.py` | D-1 completata | I bot chiamano `dichiara_fine_fase_azione()` con ritardi distribuiti |
| D-6 | Modificare `_on_pulsante_principale()`: alla fine della fase 1 chiamare `_avvia_timer_azione()` e `_pianifica_risposta_bot()` invece di avanzare direttamente | `bingo_game/ui/finestra_gioco.py` | D-2, D-5 completati | La fase 2 si apre con il timer attivo e i bot pianificati |
| D-7 | Implementare `_avvia_pausa_turno(durata_ms)` e `_on_tick_pausa(event)`: conto alla rovescia + riavvio automatico | `bingo_game/ui/finestra_gioco.py` | D-3, D-4 completati | La fase 1 riparte automaticamente al termine della pausa |
| D-8 | Aggiungere stato `"pausa_turno"` a `_fase_turno_ui`; aggiornare le etichette del pulsante per i nuovi stati | `bingo_game/ui/finestra_gioco.py` | D-7 completata | Il pulsante mostra etichette corrette in ogni stato |
| D-9 | Verifica manuale con NVDA: ciclo completo, avvisi vocali, terminazione anticipata, timeout, pausa | manuale | D-8 completata | Checklist NVDA spuntata; nessun annuncio mancante o sovrapposto |
| D-10 | Pre-commit checklist; committare la sotto-fase D | tutti i file D | D-9 completata | Commit atomico; nessun test GUI rotto |

---

### Sotto-fase E — Configurazione: nuovi parametri UI

| N | Descrizione | File coinvolto | Dipendenza | Criterio di completamento |
|---|-------------|----------------|-----------|--------------------------|
| E-1 | Aggiungere `wx.SpinCtrl` per `durata_finestra_azione_secondi` (5-300, default 60) e `durata_pausa_turni_secondi` (1-30, default 5) in `_build_ui()` | `bingo_game/ui/finestra_configurazione.py` | D-10 completata | I due campi sono visibili e raggiungibili via Tab |
| E-2 | Leggere i valori in `_on_conferma()` e passarli al costruttore di `FinestraGioco` | `bingo_game/ui/finestra_configurazione.py` | E-1 completata | I valori inseriti dall'utente arrivano ai timer |
| E-3 | Creare `tests/unit/test_ciclo_turno_v2_config.py`: verifica che i parametri siano passati correttamente | `tests/unit/test_ciclo_turno_v2_config.py` | E-2 completata | Test verde |
| E-4 | Pre-commit checklist; committare la sotto-fase E | tutti i file E | E-3 completata | Exit code 0; commit atomico |

---

### Sotto-fase F — Test di completamento

| N | Descrizione | File coinvolto | Dipendenza | Criterio di completamento |
|---|-------------|----------------|-----------|--------------------------|
| F-1 | Creare `tests/unit/test_ciclo_turno_v2_estrazione.py`: verifica che dopo `esegui_fase_estrazione()` nessun bot abbia `reclamo_turno != None` | `tests/unit/test_ciclo_turno_v2_estrazione.py` | E-4 completata | Test verde |
| F-2 | Creare `tests/unit/test_ciclo_turno_v2_timeout_umano.py`: verifica il flusso completo di timeout senza dichiarazione umano | `tests/unit/test_ciclo_turno_v2_timeout_umano.py` | E-4 completata | Test verde (con timer finto o mock) |
| F-3 | Eseguire la suite completa: `py -3.x -m unittest discover tests -q` | tutti | F-1, F-2 completati | Exit code 0; 0 fallimenti |
| F-4 | Verifica `grep -r "print(" bingo_game/` restituisce 0 risultati | tutti i file | F-3 completata | Output vuoto |

---

## Task di test (riepilogo file)

| File | Tipo | Azione |
|------|------|--------|
| `tests/unit/test_fase_estrazione.py` | Aggiornamento | Task A-3 |
| `tests/integration/test_partita_bot_attivo.py` | Aggiornamento | Task A-4 |
| `tests/test_partita.py` | Verifica + aggiornamento | Task A-5 |
| `tests/test_game_controller.py` | Verifica + aggiornamento | Task A-5 |
| `tests/unit/test_game_controller_loop.py` | Verifica + aggiornamento | Task A-6 |
| `tests/unit/test_ciclo_turno_v2_bot_declaration.py` | Nuovo | Task B-2 |
| `tests/unit/test_ciclo_turno_v2_early_exit.py` | Nuovo | Task B-3 |
| `tests/unit/test_ciclo_turno_v2_tutti_pronti.py` | Nuovo | Task B-4 |
| `tests/unit/test_ciclo_turno_v2_avvisi_vocali.py` | Nuovo | Task C-4 |
| `tests/unit/test_ciclo_turno_v2_config.py` | Nuovo | Task E-3 |
| `tests/unit/test_ciclo_turno_v2_estrazione.py` | Nuovo | Task F-1 |
| `tests/unit/test_ciclo_turno_v2_timeout_umano.py` | Nuovo | Task F-2 |

---

## Task di documentazione

| N | Descrizione | File coinvolto | Dipendenza |
|---|-------------|----------------|-----------|
| DOC-1 | Aggiornare `CHANGELOG.md` sezione `[Unreleased]`: aggiungere voci `Added` e `Changed` per ogni sotto-fase | `CHANGELOG.md` | Dopo ogni sotto-fase completata |
| DOC-2 | Aggiornare `docs/API.md`: aggiungere signature di `dichiara_fine_fase_azione()`, `annuncia_avviso_timeout()`, `annuncia_avvio_pausa_turno()`, `annuncia_tutti_pronti()` | `docs/API.md` | Dopo sotto-fase B e C |
| DOC-3 | Aggiornare `docs/ARCHITECTURE.md`: riflettere il nuovo ciclo a 4 fasi nel diagramma del flusso di turno | `docs/ARCHITECTURE.md` | Dopo sotto-fase D |
| DOC-4 | Risolvere il punto aperto su `durata_finestra_azione_max_multiplayer_secondi` e aggiornare `DESIGN_CICLO_TURNO_V2.md` | `docs/2 - projects/DESIGN_CICLO_TURNO_V2.md` | Prerequisito PRE-1 |
