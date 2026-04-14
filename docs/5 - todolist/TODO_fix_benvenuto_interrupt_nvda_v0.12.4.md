---
type: todo
titolo: Fix definitivo benvenuto NVDA — CallLater + focus stabilizzato v0.12.4
feature: fix_benvenuto_interrupt_nvda
versione: 0.12.4
data_creazione: 2026-04-14
agent: Agent-Plan
status: READY
plan_ref: docs/3 - coding plans/PLAN_fix_benvenuto_interrupt_nvda_v0.12.4.md
---

# TODO — Fix definitivo benvenuto NVDA v0.12.4

Piano di riferimento: [PLAN_fix_benvenuto_interrupt_nvda_v0.12.4.md](../3%20-%20coding%20plans/PLAN_fix_benvenuto_interrupt_nvda_v0.12.4.md)

---

## Istruzioni per Agent-Code

- Esegui le fasi nell'ordine indicato; ogni fase e committable separatamente.
- Non introdurre print() in nessun file di src/ o bingo_game/.
- Usa type hints su ogni metodo nuovo o modificato.
- Dopo ogni fase: py_compile sul file modificato prima del commit.
- Non riaprire il DESIGN; il PLAN e la fonte di verita operativa.
- Non richiedere pause intermedie all'orchestratore: procedi fino a Fase 4 inclusa.

---

## Fase 1 — Refactor `_imposta_focus_iniziale` in FinestraGioco

**File**: `bingo_game/ui/finestra_gioco.py`

- [x] Aprire il file e individuare `_imposta_focus_iniziale`
- [x] Verificare se `_annuncia_benvenuto_iniziale` esiste gia come metodo separato
- [x] Spostare `_pannello_griglia.SetFocus()` come ultima istruzione sincrona
- [x] Rimuovere qualsiasi chiamata diretta sincrona a `mostra_messaggio_benvenuto`
      o `_annuncia_benvenuto_iniziale` dal corpo di `_imposta_focus_iniziale`
- [x] Aggiungere al fondo del metodo: `wx.CallLater(350, self._annuncia_benvenuto_iniziale)`
- [x] Creare (o verificare) il metodo:
      ```python
      def _annuncia_benvenuto_iniziale(self) -> None:
          self._renderer.mostra_messaggio_benvenuto(self._testo_benvenuto)
      ```
- [x] py_compile: `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [ ] Commit: `fix(ui): stabilizza focus prima del benvenuto NVDA`

---

## Fase 2 — Aggiornare test UI per nuovo ordine SetFocus/CallLater

**File**: `tests/ui/test_finestra_gioco.py`

- [x] Individuare test esistenti su `_imposta_focus_iniziale` e `SetFocus`
- [x] Aggiornare/aggiungere `test_imposta_focus_iniziale_ordine`:
      verifica che SetFocus avvenga prima di `wx.CallLater` nel flusso sincrono
- [x] Aggiungere `test_callafter_delay_350`:
      patcha `wx.CallLater`, verifica delay=350 e callable=`_annuncia_benvenuto_iniziale`
- [x] Aggiungere `test_annuncia_benvenuto_chiama_renderer`:
      chiama direttamente `_annuncia_benvenuto_iniziale`, verifica che
      `mostra_messaggio_benvenuto` sia chiamato con il testo orientativo corretto
- [x] Aggiungere `test_nessun_benvenuto_sincrono`:
      verifica che `mostra_messaggio_benvenuto` NON sia chiamato nel corpo
      sincrono di `_imposta_focus_iniziale`
- [x] Eseguire suite: `pytest tests/ui/ -v`
- [ ] Commit: `test(ui): aggiorna test FinestraGioco per CallLater e ordine focus`

---

## Fase 3 — Validazione pre-commit

- [x] `python -m py_compile bingo_game/ui/finestra_gioco.py` — zero errori
- [x] `pytest tests/ui/ -v` — 9/9 test AvvioSilenzioso passati; 3 failure preesistenti non correlate
- [x] `grep -r "print(" bingo_game/ui/finestra_gioco.py` — zero risultati
- [ ] (opzionale) `mypy bingo_game/ui/finestra_gioco.py --strict` — zero errori

---

## Fase 4 — Sync documentazione e changelog

**File**: `CHANGELOG.md`, `docs/ARCHITECTURE.md`

- [x] Aggiungere in `CHANGELOG.md` sotto `[Unreleased]`:
      ```
      ### Fixed
      - Fix definitivo benvenuto NVDA: SetFocus prima del parlato,
        annuncio differito con wx.CallLater(350) e interrupt=True (v0.12.4)
      ```
- [x] Verificare se il bootstrap flow e descritto in `docs/ARCHITECTURE.md`;
      (verificato: nessuna modifica necessaria)
- [ ] Commit: `docs: sync changelog e architettura dopo fix benvenuto v0.12.4`
 

---

## Stato avanzamento complessivo

- [x] Fase 1 completata (codice implementato, py_compile OK) — commit non eseguito
- [x] Fase 2 completata (test aggiornati e verdi) — commit non eseguito
- [x] Fase 3 superata (validazione)
- [x] Fase 4: CHANGELOG.md aggiornato e docs/ARCHITECTURE.md verificata — commit non eseguito
- [ ] TODO chiuso (in attesa di verifica manuale NVDA e commit dei cambiamenti)

### Riepilogo validazione (stato attuale)

- **Validazione tecnica:** superata (root cause coperto dai fix applicati).
- **Test target:** verdi per gli scenari interessati (test UI target: 9/9 passati).
- **Failure residui:** 3 failure UI preesistenti rimangono non correlate al fix
      (sono documentati nei report di test e non bloccano la release del fix).
- **CHANGELOG.md:** aggiornato sotto `[Unreleased]`.
- **docs/ARCHITECTURE.md:** controllato — nessuna modifica necessaria.
- **Verifica manuale NVDA:** ancora pendente — necessario test E2E con NVDA reale
      su macchina Windows con AO2/NVDA per conferma definitiva del comportamento
      vocale `interrupt=True` in produzione.
