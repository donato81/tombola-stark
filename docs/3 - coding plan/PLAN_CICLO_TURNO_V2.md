---
type: plan
feature: ciclo_turno_v2
version: v1.0
date: 2026-04-01
agent: Agent-Plan
status: DRAFT
design_ref: docs/2 - projects/DESIGN_CICLO_TURNO_V2.md
report_ref: docs/4 - reports/REPORT_FATTIBILITA_CICLO_TURNO_V2_2026-04-01.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo — Ciclo di Turno V2 con finestra d'azione temporizzata
versione: v1.0
data: 2026-04-01
agente: Agent-Plan
stato: DRAFT
feature: ciclo_turno_v2
design: docs/2 - projects/DESIGN_CICLO_TURNO_V2.md
report: docs/4 - reports/REPORT_FATTIBILITA_CICLO_TURNO_V2_2026-04-01.md

---

## Dipendenze prerequisite

Prima di iniziare l'implementazione devono essere risolte le seguenti condizioni:

1. **Punto aperto — valore massimo finestra multiplayer**: il campo
   `durata_finestra_azione_max_multiplayer_secondi` non ha un valore definito.
   Deve essere deciso con l'utente prima di scrivere il codice di configurazione.
   Il piano assume come valore provvisorio 120 secondi.

2. **Codice stabile**: la suite di test corrente deve passare al 100% prima di iniziare
   (`py -3.x -m unittest discover tests -q`). Non avviare il ciclo V2 su una base rotta.

3. **DESIGN_CICLO_TURNO_V2.md deve essere in stato REVIEWED**: questo piano è DRAFT fino
   alla revisione del design da parte dell'utente.

---

## Fasi di implementazione

### SOTTO-FASE A — Dominio: disaccoppiamento reclami bot da fase estrazione

**Obiettivo**: modificare il dominio affinché `esegui_fase_estrazione()` non registri più
i reclami dei bot; aggiornare `tutti_hanno_dichiarato_fine()` per includere i bot;
aggiornare tutti i test rotti.

**File da modificare**:
- `bingo_game/partita.py`
- `tests/unit/test_fase_estrazione.py`
- `tests/integration/test_partita_bot_attivo.py`
- `tests/test_partita.py` (verifica caso per caso)
- `tests/test_game_controller.py` (verifica caso per caso)
- `tests/unit/test_game_controller_loop.py` (verifica caso per caso)

**Metodi coinvolti**:
- `Partita.esegui_fase_estrazione()`: rimuovere il blocco che itera i bot e imposta
  `reclamo_turno`. I bot aggiornano le cartelle tramite `aggiorna_giocatori_con_numero()`
  (già chiamato da `estrai_prossimo_numero()`) ma non registrano nessun reclamo.
- `Partita.tutti_hanno_dichiarato_fine()`: cambiare la condizione da "solo non-automatici"
  a "tutti i giocatori".

**Output atteso**:
- `esegui_fase_estrazione()` ritorna `{"numero_estratto": int, "fase": "attesa_reclami"}`
  senza nessun campo reclami_bot nella risposta.
- Tutti i test esistenti aggiornati e verdi.
- Nessun nuovo test scritto in questa sotto-fase (solo aggiornamenti).

---

### SOTTO-FASE B — Dominio: nuovo metodo bot per dichiarazione fine fase

**Obiettivo**: creare il metodo `dichiara_fine_fase_azione()` in `GiocatoreAutomatico`;
scrivere nuovi test unitari per questo metodo.

**File da modificare**:
- `bingo_game/players/giocatore_automatico.py`

**File da creare**:
- `tests/unit/test_ciclo_turno_v2_bot_declaration.py`
- `tests/unit/test_ciclo_turno_v2_early_exit.py`
- `tests/unit/test_ciclo_turno_v2_tutti_pronti.py`

**Metodi coinvolti**:
- `GiocatoreAutomatico.dichiara_fine_fase_azione(premi_gia_assegnati, premi_tipo_chiusi)`:
  1. Chiama `_valuta_potenziale_reclamo(premi_gia_assegnati, premi_tipo_chiusi)`.
  2. Imposta `self.reclamo_turno = reclamo` (può essere `None` se nessun premio).
  3. Chiama `self.dichiara_fine_turno()` (imposta `turno_dichiarato_concluso = True`).
- `Partita.tutti_hanno_dichiarato_fine()`: già modificato in sotto-fase A.

**Output atteso**:
- Il bot può dichiarare fine in un momento arbitrario durante la fase 2.
- `tutti_hanno_dichiarato_fine()` ritorna `True` solo quando anche tutti i bot hanno
  chiamato `dichiara_fine_fase_azione()`.
- Nuovi test verdi.

---

### SOTTO-FASE C — Renderer: nuovi metodi astratti e implementazioni wx

**Obiettivo**: estendere il contratto `BaseRenderer` con i nuovi metodi di annuncio;
implementarli in `WxRenderer`; aggiungere le nuove chiavi testo in `it.py`.

**File da modificare**:
- `bingo_game/ui/renderers/base_renderer.py`
- `bingo_game/ui/renderers/renderer_wx.py`
- `bingo_game/ui/locales/it.py`

**File da creare**:
- `tests/unit/test_ciclo_turno_v2_avvisi_vocali.py` (può usare un renderer stub)

**Metodi coinvolti**:
- `BaseRenderer.annuncia_avviso_timeout(secondi_rimanenti: int)`: abstract.
- `BaseRenderer.annuncia_avvio_pausa_turno(secondi: int)`: abstract.
- `BaseRenderer.annuncia_tutti_pronti()`: abstract.
- `WxRenderer`: implementazione concreta di ciascuno dei tre metodi; segue il pattern
  esistente (testo → log widget → AO2 speak).
- `it.py`: aggiungere le chiavi:
  - `TURNO_AVVISO_60` — testo avviso al 60% del tempo trascorso
  - `TURNO_AVVISO_80` — testo avviso all'80%
  - `TURNO_AVVISO_95` — testo avviso al 95%
  - `TURNO_TIMEOUT_SALTATO` — "Tempo scaduto. Il tuo turno è stato saltato."
  - `TURNO_TUTTI_PRONTI` — "Tutti i giocatori sono pronti. Avvio verifica premi."
  - `TURNO_PAUSA_INIZIO` — "Turno terminato. Prossimo turno tra {s} secondi."
  - `TURNO_PAUSA_COUNTDOWN` — "{s} secondi al prossimo turno."

**Output atteso**:
- `WxRenderer` istanziabile senza errori con i nuovi metodi implementati.
- Test renderer stub verdi (verificano solo che i metodi siano chiamati, non la vocalizzazione).

---

### SOTTO-FASE D — UI: timer e orchestrazione fase 2 e fase 4

**Obiettivo**: aggiungere i due timer in `FinestraGioco`, implementare la logica
di avvisi vocali progressivi, la pianificazione dei bot con `wx.CallLater`,
la terminazione anticipata e la pausa tra turni.

**File da modificare**:
- `bingo_game/ui/finestra_gioco.py`

**Metodi da creare**:
- `FinestraGioco._avvia_timer_azione(durata_ms: int)` — istanzia `wx.Timer`, salva
  timestamp di avvio, avvia il tick ogni 1000 ms.
- `FinestraGioco._on_tick_azione(event)` — controlla percentuale trascorsa;
  emette avvisi ai valori 60%, 80%, 95%; controlla `tutti_hanno_dichiarato_fine()`.
- `FinestraGioco._on_timeout_azione()` — chiama `_partita` per chiudere la fase,
  avanza a verifica.
- `FinestraGioco._on_all_ready()` — ferma il timer; annuncia "tutti pronti"; avanza.
- `FinestraGioco._pianifica_risposta_bot()` — per ogni bot nella partita calcola
  un ritardo casuale (es. `random.uniform(1.0, durata * 0.9)` secondi) e schedula
  `wx.CallLater(delay_ms, bot.dichiara_fine_fase_azione, ...)` passando gli snapshot
  di `premi_gia_assegnati` e `premi_tipo_chiusi` al momento della pianificazione.
- `FinestraGioco._avvia_pausa_turno(durata_ms: int)` — ferma timer azione se ancora
  attivo; istanzia secondo `wx.Timer`; annuncia pausa.
- `FinestraGioco._on_tick_pausa(event)` — countdown vocale; al tick finale riavvia
  `_on_pulsante_principale` con flag automatico.

**Modifica esistente**:
- `FinestraGioco._on_pulsante_principale()`: al termine della fase 1, invece di
  cambiare solo `_fase_turno_ui`, chiama `_avvia_timer_azione()` e
  `_pianifica_risposta_bot()`. Non chiama direttamente la fase 3: è il timer
  (o la terminazione anticipata) a farlo.
- `FinestraGioco._fase_turno_ui`: aggiungere il valore `"pausa_turno"`.

**Output atteso**:
- Ciclo completo funzionante con tutto il flusso V2 (manuale + timer + annunci).
- Nessun test automatico GUI in questa sotto-fase (wx.Timer non è testabile senza
  loop wx attivo). Verifica manuale su Windows con NVDA.

---

### SOTTO-FASE E — Configurazione: nuovi parametri in FinestraConfigurazione

**Obiettivo**: aggiungere i due nuovi campi di configurazione nella finestra di
setup partita; passarli a `FinestraGioco` al momento della creazione.

**File da modificare**:
- `bingo_game/ui/finestra_configurazione.py`
- `bingo_game/ui/finestra_gioco.py` (costruttore: accettare i due parametri)
- `main.py` (passaggio parametri: da verificare)

**Metodi coinvolti**:
- `FinestraConfigurazione._build_ui()`: aggiungere due `wx.SpinCtrl`:
  - `durata_finestra_azione_secondi` (min=5, max=300, default=60)
  - `durata_pausa_turni_secondi` (min=1, max=30, default=5)
- `FinestraConfigurazione._on_conferma()`: leggere i valori e passarli a `FinestraGioco`.
- `FinestraGioco.__init__()`: accettare i due parametri come argomenti opzionali con
  default già definiti (backward compatibility).

**File da creare**:
- `tests/unit/test_ciclo_turno_v2_config.py`

**Output atteso**:
- L'utente può regolare durata finestra e pausa dalla schermata di avvio.
- I valori sono propagati correttamente al timer di `FinestraGioco`.
- Test config verdi.

---

### SOTTO-FASE F — Test di completamento e verifica accessibilità

**Obiettivo**: completare la copertura test; eseguire la verifica accessibilità manuale
con NVDA.

**File da creare**:
- `tests/unit/test_ciclo_turno_v2_estrazione.py`
- `tests/unit/test_ciclo_turno_v2_timeout_umano.py`

**Checklist verifica manuale NVDA**:
- Il numero estratto viene annunciato immediatamente dopo il click.
- I tre avvisi vocali progressivi sono leggibili e non sovrapposti.
- Il messaggio "Tutti pronti" o "Tempo scaduto" è annunciato correttamente.
- La pausa tra turni è annunciata con il conteggio.
- Il pulsante "Ho finito" è raggiungibile via Tab e annunciato correttamente da NVDA.

**Output atteso**:
- Tutti i nuovi test verdi.
- Tutti i test esistenti (non GUI) verdi.
- Verifica manuale NVDA completata e annotata nel CHANGELOG.

---

## Ordine obbligatorio delle fasi

```
A --> B --> C --> D --> E --> F
```

- **A prima di B**: la modifica a `esegui_fase_estrazione()` deve essere stabile prima
  di aggiungere `dichiara_fine_fase_azione()`, per evitare interferenze nella logica dei test.
- **B prima di C**: i nuovi metodi del bot vengono chiamati dalla UI; il dominio deve
  essere pronto prima che il renderer sia esteso.
- **C prima di D**: `FinestraGioco` usa i metodi del renderer; se questi non esistono
  l'applicazione non si avvia.
- **D prima di E**: la configurazione passa parametri al costruttore di `FinestraGioco`;
  il costruttore deve già accettarli.
- **E prima di F**: i test di configurazione richiedono che la UI e il costruttore siano
  già allineati.

---

## Strategia di test

- **Sotto-fasi A, B, C, E, F**: test automatici, eseguibili con
  `py -3.x -m unittest discover tests -q` o `pytest -m "not gui"`.
- **Sotto-fase D**: non testabile automaticamente per il timer wx. Verifica manuale
  obbligatoria con NVDA su Windows 11 prima del commit.
- Prima di ogni commit di sotto-fase, eseguire `python -m py_compile` su tutti i file
  modificati e la pre-commit checklist completa definita in `workflow-standard.instructions.md`.

---

## Strategia di rollback

Se una sotto-fase introduce regressioni non recuperabili:

1. Identificare i commit della sotto-fase con `git log --oneline -10`.
2. Se i commit non sono stati pushati: `git reset --soft HEAD~N` (N = numero di commit
   della sotto-fase) per tornare allo stato precedente.
3. Se i commit sono stati pushati: creare un commit di revert per ciascuna modifica
   in ordine inverso, partendo dall'ultima sotto-fase rotta.
4. Aggiornare `TODO_CICLO_TURNO_V2.md` rimuovendo la spunta dalla sotto-fase rotta.
5. Segnalare il problema nel CHANGELOG sezione `[Unreleased]` con tag `Fixed:`.

La procedura completa è in `.github/skills/rollback-procedure.skill.md`.

---

## Criteri di completamento del piano

Il piano è considerato completato quando:

1. Tutte le sei sotto-fasi hanno status "completato" in `TODO_CICLO_TURNO_V2.md`.
2. Tutti i test (non GUI) passano: `py -3.x -m unittest discover tests -q` exit code 0.
3. Nessun `print()` nei file di produzione: `grep -r "print(" bingo_game/` ritorna 0 risultati.
4. Il CHANGELOG sezione `[Unreleased]` contiene le voci per tutte le modifiche introdotte.
5. La verifica manuale NVDA è stata eseguita e documentata.
6. Il punto aperto sul valore massimo per la finestra multiplayer è stato risolto
   e il parametro `durata_finestra_azione_max_multiplayer_secondi` è definito nel codice.
