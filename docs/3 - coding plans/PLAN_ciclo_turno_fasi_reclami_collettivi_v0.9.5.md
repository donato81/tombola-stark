---
type: plan
feature: ciclo_turno_fasi_reclami_collettivi
agent: Agent-Plan
status: READY
version: v0.9.5
design_ref: docs/2 - projects/DESIGN_ciclo_turno_fasi_reclami_collettivi.md
date: 2026-04-01
report_ref: docs/4 - reports/REPORT_FATTIBILITA_FASI_TURNO_2026-04-01.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo separazione ciclo di turno in fasi distinte con verifica collettiva dei reclami
data_creazione: 2026-04-01
agente: Agent-Plan
stato: draft
feature: ciclo_turno_fasi_reclami_collettivi
versione_progetto: v0.9.5
design: docs/2 - projects/DESIGN_ciclo_turno_fasi_reclami_collettivi.md
report: docs/4 - reports/REPORT_FATTIBILITA_FASI_TURNO_2026-04-01.md

## Contenuto

### Executive Summary

Tipo intervento: refactoring architetturale del ciclo di turno con estensione del contratto renderer
Priorita: P1 — prerequisito di equita e accessibilita
Branch: feature/ciclo-turno-bifasico
Versione di riferimento: v0.9.5
Scope: separare `partita.esegui_turno` in due fasi esplicite, correggere la logica di
co-vincita in `verifica_premi`, aggiungere stato di fase a `Partita` e `FinestraGioco`,
estendere il contratto `BaseRenderer` con primitive atomiche di annuncio,
aggiornare `game_controller` e `comandi_partita` con wrapper di compatibilita transitoria.
Vincoli: il percorso monolitico `esegui_turno` deve sopravvivere durante la transizione;
nessun test esistente deve rompersi in modo non controllato prima che i wrapper siano in place.

### Problema e Obiettivo

Il metodo `esegui_turno()` in `bingo_game/partita.py` comprime estrazione,
reclami bot, verifica premi, reset e controllo tombola in un'unica chiamata sincrona
e indivisibile. Questo crea due problemi distinti.

Problema 1 — Asimmetria temporale tra umano e bot.
I bot reclamano con il numero gia segnato (passo 2 del turno), mentre l'umano
deve dichiarare la vittoria prima di sentire il numero estratto, o nel breve
intervallo tra annuncio e click successivo. Con NVDA e uno screen reader attivo
questa finestra e praticamente nulla.

Problema 2 — Assegnazione premi inequa in caso di co-vincita.
`verifica_premi()` chiude il tipo premio al primo giocatore trovato nell'ordine
di lista. Se due giocatori reclamano lo stesso tipo nello stesso turno, il secondo
non riceve il premio. Il comportamento attuale e un artefatto dell'ordine di iterazione,
non una regola di gioco.

Obiettivo: introdurre un modello bifasico esplicito con finestra di reclamo collettiva,
correggere la verifica con doppia passata, aggiungere stato di fase al dominio e alla UI,
estendere il contratto renderer con primitive atomiche compatibili con NVDA.

### File coinvolti

- [bingo_game/partita.py](../../bingo_game/partita.py) — MODIFY
  Aggiungere `esegui_fase_estrazione()`, `esegui_fase_verifica()`,
  attributo `fase_turno_corrente`, correzione `verifica_premi()` a doppia passata.
  Mantenere `esegui_turno()` come wrapper compatibile.

- [bingo_game/players/giocatore_base.py](../../bingo_game/players/giocatore_base.py) — MODIFY
  Aggiungere attributo `turno_dichiarato_concluso: bool` e metodo `dichiara_fine_turno()`.
  Verificare integrazione con `_passa_turno_core()` attualmente inutilizzato.

- [bingo_game/game_controller.py](../../bingo_game/game_controller.py) — MODIFY
  Aggiungere `esegui_fase_estrazione_sicura(partita)` e `esegui_fase_verifica_sicura(partita)`
  con lo stesso pattern di gestione eccezioni di `esegui_turno_sicuro`.
  Mantenere `esegui_turno_sicuro` per compatibilita con i test esistenti.

- [bingo_game/comandi_partita.py](../../bingo_game/comandi_partita.py) — MODIFY
  Esporre `esegui_fase_estrazione(partita)` e `esegui_fase_verifica(partita)` in
  `ComandiSistema`. Mantenere `esegui_turno(partita)` per compatibilita.
  Aggiungere `dichiara_fine_turno(giocatore)` in `ComandiGiocatoreUmano`.

- [bingo_game/ui/finestra_gioco.py](../../bingo_game/ui/finestra_gioco.py) — MODIFY
  Aggiungere attributo `_fase_turno_ui: Literal["attesa_estrazione", "attesa_reclami"]`.
  Biforcazione contestuale di `_on_pulsante_principale()`.
  Estendere `aggiorna_stato_pulsante` con etichette di fase.
  Annuncio esplicito del cambio etichetta via vocalizzatore (NVDA re-announce).

- [bingo_game/ui/renderers/base_renderer.py](../../bingo_game/ui/renderers/base_renderer.py) — MODIFY
  Aggiungere metodi astratti: `annuncia_numero_estratto(numero, numero_turno)`,
  `annuncia_premi_turno(premi)`, `annuncia_fase_turno(fase)`.

- [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py) — MODIFY
  Implementare i tre nuovi metodi del contratto con schema:
  testo costruito -> `_wx_aggiorna_output(testo)` -> `_ao2_vocalizza(testo)`.
  Aggiungere vocalizzazione esplicita dopo ogni `SetLabel` di fase.

- [tests/test_partita.py](../../tests/test_partita.py) — MODIFY
  Adattare i test che chiamano `verifica_premi()` direttamente al nuovo comportamento
  a doppia passata. Aggiungere test per `esegui_fase_estrazione` e `esegui_fase_verifica`
  e per `fase_turno_corrente`.

- [tests/test_game_controller.py](../../tests/test_game_controller.py) — MODIFY
  Aggiungere test per `esegui_fase_estrazione_sicura` e `esegui_fase_verifica_sicura`.
  Verificare che `esegui_turno_sicuro` continui a passare invariato.

- [tests/test_comandi_partita.py](../../tests/test_comandi_partita.py) — MODIFY
  Aggiungere test per i nuovi metodi di fase in `ComandiSistema` e
  `dichiara_fine_turno` in `ComandiGiocatoreUmano`.

- [tests/integration/test_partita_bot_attivo.py](../../tests/integration/test_partita_bot_attivo.py) — MODIFY
  Verificare compatibilita: tutte e 8 le chiamate a `esegui_turno()` devono
  continuare a funzionare tramite wrapper. Aggiungere test bifasici separati.

- [tests/integration/test_event_coverage.py](../../tests/integration/test_event_coverage.py) — MODIFY
  Verificare che le chiamate a `esegui_turno_sicuro` restino verdi.

- [tests/unit/](../../tests/unit/) — CREATE
  Nuovi test unitari per le fasi separate:
  `test_fase_estrazione_aggiorna_numero.py`,
  `test_fase_verifica_co_vincita.py`,
  `test_umano_dichiara_fine_turno.py`.

### Fasi sequenziali

#### Fase 1 — Correzione verifica_premi con doppia passata (prerequisito)

File coinvolti:

- [bingo_game/partita.py](../../bingo_game/partita.py)
- [tests/test_partita.py](../../tests/test_partita.py)

Operazione: MODIFY

Contenuto atteso:

- Ristrutturare `verifica_premi()` con due passate distinte.
  Prima passata: raccogliere tutti i candidati validi per tipo senza assegnare.
  Seconda passata: assegnare il premio a tutti i candidati validi per lo stesso tipo.
- Rimuovere la chiusura anticipata del tipo premio (`premi_tipo_chiusi.add(tipo)`)
  prima del completamento della raccolta collettiva.
- Aggiornare i test in `test_partita.py` che testano `verifica_premi()`
  per verificare il comportamento corretto in caso di co-vincita.
- Verificare che i test esistenti non rompano il comportamento del caso
  singolo vincitore (nessuna regressione attesa).

Commit: `fix(domain): verifica_premi con doppia passata per co-vincita nello stesso turno`

#### Fase 2 — Split esegui_turno e attributo fase_turno_corrente

File coinvolti:

- [bingo_game/partita.py](../../bingo_game/partita.py)
- [bingo_game/players/giocatore_base.py](../../bingo_game/players/giocatore_base.py)

Operazione: MODIFY

Contenuto atteso:

- Aggiungere a `Partita`: attributo `fase_turno_corrente: Literal["attesa_estrazione", "attesa_reclami", "chiusa"]`
  inizializzato a `"attesa_estrazione"` in `__init__`.
- Implementare `esegui_fase_estrazione() -> dict` che esegue:
  estrazione numero, notifica giocatori, reclami bot.
  Imposta `fase_turno_corrente = "attesa_reclami"`.
  Ritorna: `{"numero_estratto": int, "fase": str}`.
- Implementare `esegui_fase_verifica() -> dict` che esegue:
  verifica premi (con la nuova doppia passata), confronto reclami bot,
  reset reclami, controllo tombola.
  Imposta `fase_turno_corrente = "attesa_estrazione"` al termine.
  Ritorna: `{"premi_nuovi": list, "reclami_bot": list, "tombola_rilevata": bool}`.
- Mantenere `esegui_turno()` come wrapper compatibile che chiama i due nuovi
  metodi in sequenza. Non rimuoverlo in questa fase.
- In `giocatore_base.py`: aggiungere `turno_dichiarato_concluso: bool = False`
  e metodo `dichiara_fine_turno() -> None`. Valutare integrazione con
  `_passa_turno_core()` e, se coerente, richiamarla internamente.
- In `Partita`: aggiungere `tutti_hanno_dichiarato_fine() -> bool` che verifica
  che tutti i giocatori non automatici abbiano `turno_dichiarato_concluso == True`.
  Resettare `turno_dichiarato_concluso` in `esegui_fase_verifica()`.

Commit: `feat(domain): split esegui_turno in fasi distinte con fase_turno_corrente`

#### Fase 3 — Wrapper game_controller e comandi_partita

File coinvolti:

- [bingo_game/game_controller.py](../../bingo_game/game_controller.py)
- [bingo_game/comandi_partita.py](../../bingo_game/comandi_partita.py)

Operazione: MODIFY

Contenuto atteso:

- In `game_controller.py`: aggiungere `esegui_fase_estrazione_sicura(partita) -> dict`
  e `esegui_fase_verifica_sicura(partita) -> dict` con lo stesso schema di
  gestione eccezioni e logging di `esegui_turno_sicuro`.
  Mantenere `esegui_turno_sicuro` invariato.
- In `ComandiSistema`: esporre `esegui_fase_estrazione(partita) -> dict`
  e `esegui_fase_verifica(partita) -> dict` che delegano ai nuovi wrapper.
  Mantenere `esegui_turno(partita)` per compatibilita.
- In `ComandiGiocatoreUmano`: aggiungere `dichiara_fine_turno(partita) -> None`
  che chiama `giocatore_umano.dichiara_fine_turno()`.
- Aggiungere test per i nuovi metodi di fase in `test_game_controller.py`
  e `test_comandi_partita.py`.

Commit: `feat(application): wrapper bifasici in game_controller e comandi_partita`

#### Fase 4 — Stato UI bifasico in finestra_gioco

File coinvolti:

- [bingo_game/ui/finestra_gioco.py](../../bingo_game/ui/finestra_gioco.py)

Operazione: MODIFY

Contenuto atteso:

- Aggiungere in `__init__`:
  `self._fase_turno_ui: Literal["attesa_estrazione", "attesa_reclami"] = "attesa_estrazione"`.
- Biforcazione contestuale di `_on_pulsante_principale()`:
  - Se `_fase_turno_ui == "attesa_estrazione"`: chiama `esegui_fase_estrazione`,
    aggiorna display col numero estratto, imposta `_fase_turno_ui = "attesa_reclami"`,
    aggiorna etichetta pulsante.
  - Se `_fase_turno_ui == "attesa_reclami"`: chiama `esegui_fase_verifica`,
    annuncia premi, resetta `_fase_turno_ui = "attesa_estrazione"`,
    ripristina etichetta pulsante.
- Estendere `aggiorna_stato_pulsante` con le etichette di fase
  ("Passa turno" per attesa estrazione, "Ho finito — avvia verifica" per attesa reclami).
- Dopo ogni `SetLabel` del pulsante, aggiungere annuncio esplicito via vocalizzatore
  per garantire che NVDA legga la nuova etichetta indipendentemente dalla posizione focus.
- Binding `Ctrl+P` gia associato a `_on_pulsante_principale`: nessuna modifica necessaria.

Commit: `feat(presentation): stato UI bifasico e etichette contestuali in finestra_gioco`

#### Fase 5 — Estensione BaseRenderer e implementazione WxRenderer

File coinvolti:

- [bingo_game/ui/renderers/base_renderer.py](../../bingo_game/ui/renderers/base_renderer.py)
- [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)

Operazione: MODIFY

Contenuto atteso:

- In `base_renderer.py`: aggiungere tre metodi astratti:
  - `annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None`
    Vocalizza il numero estratto nel contesto del turno corrente, senza premi.
  - `annuncia_premi_turno(self, premi: list[dict]) -> None`
    Vocalizza i premi assegnati nel turno (o "Nessun premio questo turno.").
  - `annuncia_fase_turno(self, fase: str) -> None`
    Vocalizza la fase corrente del turno (testo gia risolto dal chiamante tramite catalogo).
- In `renderer_wx.py`: implementare i tre metodi seguendo lo schema:
  1. Costruire il testo.
  2. Chiamare `_wx_aggiorna_output(testo)` per aggiornare il pannello e il log.
  3. Chiamare `_ao2_vocalizza(testo)` per vocalizzare.
- Aggiornare `finestra_gioco._annuncia_risultato_turno()` per usare le nuove
  primitive al posto della stringa flat precedente.
- Verificare che il `_log_ctrl` riceva entrambe le voci come righe distinte
  (comportamento gia corretto con le chiamate separate, nessuna modifica strutturale).

Commit: `feat(presentation): BaseRenderer con primitive atomiche per annunci di turno`

#### Fase 6 — Aggiornamento test esistenti e nuovi test per fasi separate

File coinvolti:

- [tests/test_partita.py](../../tests/test_partita.py)
- [tests/test_game_controller.py](../../tests/test_game_controller.py)
- [tests/test_comandi_partita.py](../../tests/test_comandi_partita.py)
- [tests/integration/test_partita_bot_attivo.py](../../tests/integration/test_partita_bot_attivo.py)
- [tests/integration/test_event_coverage.py](../../tests/integration/test_event_coverage.py)
- [tests/unit/](../../tests/unit/)

Operazione: MODIFY + CREATE

Contenuto atteso:

- Adattare i test impattati direttamente:
  - `test_partita.py`: 4-5 test su `verifica_premi()` aggiornati per co-vincita.
  - `test_game_controller.py`: 5 test su `esegui_turno_sicuro` verificati invariati;
    aggiungere 4 test per i nuovi wrapper bifasici.
  - `test_comandi_partita.py`: verificare compatibilita dei test esistenti;
    aggiungere test per i nuovi comandi di fase.
  - `test_partita_bot_attivo.py`: verificare che tutte le 8 chiamate
    a `esegui_turno()` continuino a passare via wrapper.
  - `test_event_coverage.py`: verificare le 3 chiamate a `esegui_turno_sicuro`.
- Creare nuovi test unitari in `tests/unit/`:
  - `test_fase_estrazione_aggiorna_numero.py`:
    solo il numero cambia, fase aggiornata, premi non assegnati.
  - `test_fase_verifica_co_vincita.py`:
    due giocatori reclamano il medesimo ambo nello stesso turno, entrambi lo ricevono.
  - `test_umano_dichiara_fine_turno.py`:
    dichiarazione senza reclamo non produce premi; dichiarazione con reclamo valido assegna il premio.
  - `test_passaggio_fase_bloccato.py`:
    `esegui_fase_verifica` non puo essere chiamata se `fase_turno_corrente != "attesa_reclami"`.

Commit: `test(domain/application): test bifasici e aggiornamento suite esistente`

### Test Plan

#### Unit test (nuovi)

| Test | File | Descrizione |
|------|------|-------------|
| `test_fase_estrazione_aggiorna_numero` | `tests/unit/test_fase_estrazione.py` | `esegui_fase_estrazione` aggiorna `ultimo_numero_estratto` e imposta `fase_turno_corrente = "attesa_reclami"`. Nessun premio assegnato. |
| `test_fase_verifica_co_vincita` | `tests/unit/test_fase_verifica_co_vincita.py` | Due giocatori con reclamo valido sullo stesso ambo nello stesso turno ricevono entrambi il premio. |
| `test_umano_dichiara_fine_senza_reclamo` | `tests/unit/test_umano_dichiara_fine_turno.py` | `dichiara_fine_turno()` su giocatore umano senza reclamo non produce premi. |
| `test_umano_dichiara_fine_con_reclamo_valido` | `tests/unit/test_umano_dichiara_fine_turno.py` | `dichiara_fine_turno()` seguito da `esegui_fase_verifica` assegna il premio valido. |
| `test_passaggio_fase_bloccato` | `tests/unit/test_fase_verifica_co_vincita.py` | `esegui_fase_verifica` lancia eccezione se `fase_turno_corrente != "attesa_reclami"`. |

#### Test esistenti da verificare invarianti

| File | N. test | Strategia |
|------|---------|-----------|
| `tests/test_partita.py` | 4-5 su `verifica_premi` | Aggiornare per comportamento a doppia passata. Verificare caso singolo vincitore. |
| `tests/integration/test_partita_bot_attivo.py` | 8 | `esegui_turno()` resta wrapper: nessuna regressione attesa. |
| `tests/test_game_controller.py` | 5 su `esegui_turno_sicuro` | Invariati. Aggiungere 4 test per nuovi wrapper. |
| `tests/test_comandi_partita.py` | 4 su `esegui_turno` | Invariati via metodo compatibile. Aggiungere test per fasi. |
| `tests/integration/test_event_coverage.py` | 3 su `esegui_turno_sicuro` | Devono restare verdi senza modifiche. |
| `tests/integration/test_logging_integration.py` | 2 su `esegui_turno_sicuro` | Devono restare verdi senza modifiche. |

#### Strategia di compatibilita transitoria

Il metodo `esegui_turno()` in `Partita` e i wrapper `esegui_turno_sicuro`
in `game_controller` e `esegui_turno` in `comandi_partita` restano attivi
per tutta la durata del ciclo di implementazione. I nuovi metodi bifasici
sono addittivi: nessun metodo esistente viene rimosso o modificato nella firma
prima che tutti i test siano aggiornati. La rimozione dei wrapper di compatibilita
e pianificata per la versione v1.0.0, fuori scope di questo piano.
