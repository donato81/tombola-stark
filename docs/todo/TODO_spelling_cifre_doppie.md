# TODO — Spelling cifre doppie nei numeri estratti

**Data:** 2026-04-14
**Riferimento piano:** `docs/3 - coding plans/PLAN_spelling_cifre_doppie.md`
**Riferimento design:** `docs/2 - projects/DESIGN_spelling_cifre_doppie.md`
**Riferimento analisi:** `docs/4 - reports/REPORT_ANALISI_spelling_cifre_doppie_2026-04-14.md`
**Stato:** IN CORSO

---

## Prerequisiti

- [ ] Verificare che il fix benvenuto interrupt NVDA (`PLAN_fix_benvenuto_interrupt_nvda_v0.12.4.md`) sia completato e committato prima di iniziare questa feature.

---

## Implementazione

- [x] **Passo 1+2** — Aggiungere `CIFRE_VERBALI` (dizionario int→str, cifre 0–9 in italiano) in `bingo_game/ui/locales/it.py`
- [x] **Passo 1+2** — Aggiungere chiave `LOOP_SPELLING_NUMERO_ESTRATTO` con template `"{decina}. {unita}."` nel catalogo di `bingo_game/ui/locales/it.py`
- [ ] **Commit** — `feat(locales): aggiungi CIFRE_VERBALI e LOOP_SPELLING_NUMERO_ESTRATTO`
- [x] **Passo 3** — Aggiungere funzione pura `_spelling_numero(n: int) -> str` in `bingo_game/ui/finestra_gioco.py` con import di `CIFRE_VERBALI` e template da `locales/it.py`
- [ ] **Commit** — `feat(ui): aggiungi funzione _spelling_numero per spelling NVDA`
- [x] **Passo 4** — Aggiungere chiamata `self._renderer.mostra_messaggio_sistema(_spelling_numero(numero))` nel Punto A (estrazione turno principale) di `finestra_gioco.py`, con guardia `isinstance(numero, int) and numero >= 10`
- [x] **Passo 5** — Aggiungere stessa chiamata nel Punto B (azione automatica/bot) di `finestra_gioco.py`, con stessa guardia
- [ ] **Commit** — `feat(ui): aggiungi spelling cifre doppie post-annuncio estratto`

---

## Test manuale con NVDA

- [ ] **Test 5.1** — Estrarre un multiplo di 10 (es. 20, 50, 70): verificare che NVDA annunci "[decina_verbale]. Zero."
- [ ] **Test 5.2** — Estrarre un numero con unità significativa (es. 45, 67): verificare "[decina]. [unita]."
- [ ] **Test 5.3** — Estrarre il numero 90: verificare "Nove. Zero."
- [ ] **Test 5.4** — Nessuna regressione: griglia aggiornata, pulsanti funzionanti, `logs/stderr_capture.txt` senza nuove eccezioni

---

## Documentazione post-implementazione

- [x] Aggiornare `CHANGELOG.md` sezione `[Unreleased]`:
  `Added: spelling cifre doppie post-annuncio nel flusso di estrazione (accessibilità NVDA)`
- [ ] Marcare questo TODO come COMPLETATO
