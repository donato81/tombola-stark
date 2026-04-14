---
type: todo
titolo: Annuncio posizione focus dopo il benvenuto NVDA
feature: annuncio_posizione_focus_post_benvenuto_nvda
versione: 0.12.5
data_creazione: 2026-04-14
agent: Agent-Plan
status: IN_PROGRESS
plan_ref: docs/3 - coding plans/PLAN_annuncio_posizione_focus_post_benvenuto_nvda_v0.12.5.md
---

# TODO — Annuncio posizione focus dopo il benvenuto NVDA v0.12.5

Piano di riferimento: [PLAN_annuncio_posizione_focus_post_benvenuto_nvda_v0.12.5.md](../3%20-%20coding%20plans/PLAN_annuncio_posizione_focus_post_benvenuto_nvda_v0.12.5.md)

---

## Istruzioni per Agent-Code

- Il PLAN ha status **READY**: procedere con la codifica seguendo l'ordine delle fasi.
- Esegui le fasi nell'ordine indicato; ogni fase e committable separatamente.
- Non introdurre `print()` in nessun file di `bingo_game/`.
- Usa type hints su ogni metodo nuovo o modificato.
- Dopo ogni fase: `py_compile` sul file modificato prima del commit.
- Non riaprire il DESIGN; il PLAN e la fonte di verita operativa.
- La validazione manuale NVDA (Fase 3 — step 5) e obbligatoria: non saltarla
  e non sostituirla con i soli test automatici.

---

## Fase 1 — Secondo callback differito in `_annuncia_benvenuto_iniziale`

**File**: `bingo_game/ui/finestra_gioco.py`

- [x] Aprire il file e individuare `_annuncia_benvenuto_iniziale`
- [x] Verificare che il metodo non contenga gia una schedulazione per la posizione focus
- [x] Aggiungere al fondo del metodo:
      `wx.CallLater(200, self._annuncia_posizione_focus_iniziale)`
      (valore di partenza consigliato: 200 ms — empirico, da validare con NVDA)
- [x] Creare il nuovo metodo:
      ```python
      def _annuncia_posizione_focus_iniziale(self) -> None:
              self._dispatch(self._comandi.stato_focus())
      ```
- [x] `python -m py_compile bingo_game/ui/finestra_gioco.py` — zero errori
- [ ] Commit: `feat(ui): aggiungi annuncio posizione focus dopo benvenuto NVDA`

---

## Fase 2 — Aggiungere test UI per il secondo callback

**File**: `tests/ui/test_finestra_gioco.py`

- [x] Individuare test esistenti su `_annuncia_benvenuto_iniziale` e `wx.CallLater`
- [x] Aggiungere `test_annuncia_benvenuto_schedula_secondo_callafter`:
      patcha `wx.CallLater`, chiama `_annuncia_benvenuto_iniziale()`,
      verifica callable=`_annuncia_posizione_focus_iniziale` e delay `200`
- [x] Aggiungere `test_annuncia_posizione_usa_stato_focus`:
      mocka `_comandi.stato_focus` con evento fittizio, chiama
      `_annuncia_posizione_focus_iniziale()`, verifica `stato_focus()` chiamato
      una volta e relativo esito passato a `self._dispatch(...)`
- [x] Aggiungere `test_nessun_testo_posizione_in_benvenuto`:
      verifica che il testo del benvenuto non contenga stringhe posizione
      ("riga", "colonna") costruite localmente nel metodo di benvenuto
- [x] `python -m unittest tests.ui.test_finestra_gioco.TestFinestraGiocoAvvioSilenzioso -v` — 13 OK, zero nuovi failure
- [x] Test rinforzato: il secondo `wx.CallLater` vincola esplicitamente delay `200`
- [ ] Commit: `test(ui): aggiungi test secondo callafter e dispatch stato_focus`

---

## Fase 3 — Validazione sintattica, test suite e check manuale NVDA

- [x] `python -m py_compile bingo_game/ui/finestra_gioco.py` — zero errori
- [x] `python -m unittest tests.ui.test_finestra_gioco.TestFinestraGiocoAvvioSilenzioso -v` — 13 OK
- [x] `grep -r "print(" bingo_game/ui/finestra_gioco.py` — zero risultati (verificato)
- [ ] (opzionale) `mypy bingo_game/ui/finestra_gioco.py --strict` — zero errori
- [ ] CHECK MANUALE NVDA — OBBLIGATORIO (IN_ATTESA_UTENTE):
      - Avviare applicazione con NVDA attivo su Windows
      - Confermare partita dalla finestra di configurazione
      - Verificare che il benvenuto sia il primo annuncio applicativo (completo, non troncato)
      - Verificare che dopo pausa distinta si senta la posizione iniziale
        (es. "Cartella 1, riga 1, colonna 1") come secondo annuncio separato
      - Verificare assenza di overlap/troncamenti percepibili tra i due messaggi
      - Se necessario: regolare `<delay_tuned>` e ripetere la validazione

---

## Fase 4 — Sync documentazione e changelog

**File**: `CHANGELOG.md`, `docs/ARCHITECTURE.md`

- [x] Aggiungere voce `[Unreleased]` in `CHANGELOG.md`: fatto
- [x] Verificare che `_annuncia_posizione_focus_iniziale` sia privato (prefisso `_`): confermato — `docs/API.md` non aggiornato
- [x] `docs/ARCHITECTURE.md`: nessuna sezione descrive la sequenza CallLater — nessun aggiornamento necessario
- [ ] Commit: `docs: sync changelog dopo annuncio posizione focus v0.12.5`

---

## Stato finale attuale

- [x] Implementazione completata
- [x] Test automatici mirati completati
- [x] Changelog aggiornato
- [ ] Verifica manuale NVDA completata
- [ ] Commit manuali eseguiti
