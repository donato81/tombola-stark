---
type: todo
feature: fix_unicode_print
status: READY
version: v0.9.1
date: 2026-03-28
plan: docs/3 - coding plans/PLAN_fix_unicode_print_v0.9.1.md
---

# TODO fix_unicode_print v0.9.1

Piano padre: [PLAN_fix_unicode_print_v0.9.1.md](../3%20-%20coding%20plans/PLAN_fix_unicode_print_v0.9.1.md)

Istruzioni per Agent-Code: esegui una fase alla volta. Dopo ogni fase esegui il runner
`python -m unittest discover -s tests -p "test_*.py"` e verifica il conteggio prima di
proseguire. Non passare alla fase successiva se la fase corrente non ha soddisfatto
i propri criteri di completamento.

---

## Fase 0 — Baseline e pre-condizioni

- [ ] Eseguire `python -m unittest discover -s tests -p "test_*.py"` e annotare il risultato.
- [ ] Verificare che il risultato corrisponda a **319 OK / 32 ERROR / 1 Skipped / 0 FAIL**.
- [ ] Verificare che `bingo_game/comandi_partita.py` contenga le 18 righe `print()` target
      alle righe 72, 76, 91, 96, 111, 117, 119, 121, 136, 141, 144, 159, 164, 179, 184, 199, 204, 207.
- [ ] Verificare che `tests/test_game_controller.py` contenga le 2 righe `print()` target
      alle righe 470 e 780.
- [ ] Documentare qualsiasi scostamento dalla baseline attesa prima di procedere.

Criteri: baseline 319 OK / 32 ERROR / 1 Skipped / 0 FAIL confermata. Tutti i 20 print() target presenti. Nessun commit richiesto.

---

## Fase 1 — Fix FILE 1: rimozione print() da comandi_partita.py

File da MODIFICARE:
- `bingo_game/comandi_partita.py`

- [ ] Rimuovere riga 72: `print(f"✅ Partita creata: {nome_umano} vs {num_bot} bot")`
- [ ] Rimuovere riga 76: `print(f"❌ Errore creazione partita: {exc}")`
- [ ] Rimuovere riga 91: `print("❌ Parametro non è Partita valida")`
- [ ] Rimuovere riga 96: `print("🚀 Partita AVVIATA - Buon divertimento!")`
- [ ] Rimuovere riga 111: `print("❌ Parametro non è Partita valida")`
- [ ] Rimuovere riga 117: `print(f"🎲 Estratto numero: {numero}")`
- [ ] Rimuovere riga 119: `print(f"   🏆 {len(risultato['premi_nuovi'])} nuovi premi!")`
- [ ] Rimuovere riga 121: `print("   🎉 TOMBOLA RILEVATA!")`
- [ ] Rimuovere riga 136: `print("❌ Parametro non è Partita valida")`
- [ ] Rimuovere riga 141: `print(f"📊 Stato: {stato['stato_partita']} - {len(stato['numeri_estratti'])} estratti")`
- [ ] Rimuovere riga 144: `print(f"❌ Errore stato partita: {exc}")`
- [ ] Rimuovere riga 159: `print("❌ Parametro non è Partita valida")`
- [ ] Rimuovere riga 164: `print("🎉 TOMBOLA presente nella partita!")`
- [ ] Rimuovere riga 179: `print("❌ Parametro non è Partita valida")`
- [ ] Rimuovere riga 184: `print("🏁 Partita TERMINATA")`
- [ ] Rimuovere riga 199: `print("❌ Parametro non è Partita valida")`
- [ ] Rimuovere riga 204: `print("🛑 Partita TERMINATA forzatamente")`
- [ ] Rimuovere riga 207: `print(f"❌ Errore terminazione: {exc}")`
- [ ] Eseguire `python -m py_compile bingo_game/comandi_partita.py` senza errori.
- [ ] Eseguire la suite: conteggio OK superiore a 319 confermato.
- [ ] Nessuna firma pubblica, docstring, logica condizionale o gestione eccezioni alterata.
- [ ] Commit: `fix(application): rimuovi print() con Unicode emoji da comandi_partita.py`

Criteri: esattamente 18 righe rimosse. py_compile OK. Suite avanzata rispetto alla baseline.

---

## Fase 2 — Fix FILE 2: rimozione print() da test_game_controller.py

File da MODIFICARE:
- `tests/test_game_controller.py`

- [ ] Rimuovere riga 470: `print("✅ Test numeri esauriti: simulazione OK (test manuale consigliato)")`
- [ ] Rimuovere riga 780: `print(f"✅ Stato '{stato_target}': controller={controller_result}, partita={partita_result}")`
- [ ] Eseguire `python -m py_compile tests/test_game_controller.py` senza errori.
- [ ] Eseguire la suite: conteggio ERROR azzerato o ulteriormente ridotto confermato.
- [ ] Nessun assert adiacente, setup, teardown o naming dei metodi alterato.
- [ ] Commit: `fix(tests): rimuovi print() informativi da test_game_controller.py`

Criteri: esattamente 2 righe rimosse. py_compile OK. Suite avanzata verso il target.

---

## Fase 3 — Validazione finale

File coinvolti: nessuno modificato.

- [ ] Eseguire `python -m unittest discover -s tests -p "test_*.py"` e verificare
      **351 OK / 0 ERROR / 1 Skipped / 0 FAIL**.
- [ ] Eseguire `grep -rn "print(" bingo_game/comandi_partita.py` — deve restituire 0 occorrenze
      sulle righe precedentemente elencate.
- [ ] Eseguire `grep -n "print(" tests/test_game_controller.py` — deve restituire 0 occorrenze
      sulle righe 470 e 780 originali.
- [ ] Verificare che nessuna firma pubblica di `ComandiSistema` sia cambiata rispetto alla baseline.
- [ ] Verificare che nessun blocco `if/else`, `try/except` o `return` adiacente alle righe
      rimosse abbia subito alterazioni.
- [ ] Aggiornare `CHANGELOG.md` sezione `[Unreleased]` con voce `Fixed`.

Criteri: **351 OK / 0 ERROR / 1 Skipped / 0 FAIL** confermato. Grep restituisce 0 sulle righe target. CHANGELOG aggiornato.
