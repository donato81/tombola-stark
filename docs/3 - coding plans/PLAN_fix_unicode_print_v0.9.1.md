---
type: plan
feature: fix_unicode_print
agent: Agent-Plan
status: READY
version: v0.9.1
date: 2026-03-28
design: docs/2 - projects/DESIGN_fix_unicode_print.md
branch: main
---

# PLAN fix_unicode_print v0.9.1

## Executive Summary

| Campo | Valore |
|---|---|
| Tipo | fix / pulizia architetturale |
| Feature | fix_unicode_print |
| Priorita | alta — stabilizzazione suite CI e accessibilita NVDA |
| Branch | main |
| Versione target | v0.9.1 |
| Status | DRAFT |
| Design sorgente | [DESIGN_fix_unicode_print.md](../2%20-%20projects/DESIGN_fix_unicode_print.md) |

## Problema e Obiettivo

Il layer application (`bingo_game/comandi_partita.py`) contiene 18 chiamate `print()` con
Unicode emoji che introducono side effect di presentazione nel modulo di orchestrazione,
violano la separazione tra layer applicativo e layer di presentazione, e producono output
non strutturato su stdout durante l'esecuzione (CI, terminale, screen reader NVDA).

I test in `tests/test_game_controller.py` contengono 2 `print()` informativi che inquinano
il log di CI senza contribuire alla verifica tramite assert.

L'obiettivo e' la rimozione pura delle 20 righe indicate nel DESIGN, senza modificare
firme, logica, docstring o struttura. Il cambiamento e' a impatto comportamentale nullo.

La baseline attuale della suite produce **319 OK / 32 ERROR / 1 Skipped / 0 FAIL**.
Il target post-fix e' **351 OK / 0 ERROR / 1 Skipped / 0 FAIL**.

## Dipendenze Pre-Implementazione

- Design approvato: [DESIGN_fix_unicode_print.md](../2%20-%20projects/DESIGN_fix_unicode_print.md) — status REVIEWED
- Report di analisi: [REPORT_FIX_UNICODE_PRINT_2026-03-28.md](../4%20-%20reports/REPORT_FIX_UNICODE_PRINT_2026-03-28.md)
- Runner: `python -m unittest discover -s tests -p "test_*.py"` (venv attivo)
- Nessuna dipendenza funzionale da rimuovere o aggiungere
- Nessuna firma pubblica da modificare

## Fasi di Implementazione

---

### Fase 0 — Baseline e pre-condizioni

**Obiettivo**: confermare il punto di partenza della suite prima di qualsiasi modifica e
fissare il conteggio di riferimento per le fasi successive.

**File coinvolti**: nessuno modificato

**Azioni**:
1. Eseguire il runner di test completo:
   ```
   python -m unittest discover -s tests -p "test_*.py"
   ```
2. Verificare che il risultato corrisponda esattamente a **319 OK / 32 ERROR / 1 Skipped / 0 FAIL**.
3. Annotare qualsiasi scostamento rispetto alla baseline attesa prima di procedere.
4. Verificare che `bingo_game/comandi_partita.py` contenga le 18 righe `print()` elencate
   nel DESIGN alle righe 72, 76, 91, 96, 111, 117, 119, 121, 136, 141, 144, 159, 164, 179,
   184, 199, 204, 207.
5. Verificare che `tests/test_game_controller.py` contenga le 2 righe `print()` alle righe
   470 e 780.

**Criteri di completamento**:
- Suite eseguita e risultato documentato.
- Tutti i 20 `print()` target confermati presenti nelle righe indicate.
- Nessuna modifica al codice in questa fase.

**Rischi**: nessuno — operazione interamente read-only.

**Commit**: nessun commit richiesto in questa fase.

---

### Fase 1 — Fix FILE 1: rimozione print() da comandi_partita.py

**Obiettivo**: eliminare i 18 `print()` con Unicode emoji dal layer applicativo
`bingo_game/comandi_partita.py`, ripristinando la separazione architetturale tra
orchestrazione applicativa e presentazione su stdout.

**File da MODIFICARE**:
- `bingo_game/comandi_partita.py`

**Azioni**:

Rimuovere esclusivamente le seguenti righe (testo esatto dal DESIGN):

| Riga | Contenuto da rimuovere |
|------|------------------------|
| 72 | `print(f"✅ Partita creata: {nome_umano} vs {num_bot} bot")` |
| 76 | `print(f"❌ Errore creazione partita: {exc}")` |
| 91 | `print("❌ Parametro non è Partita valida")` |
| 96 | `print("🚀 Partita AVVIATA - Buon divertimento!")` |
| 111 | `print("❌ Parametro non è Partita valida")` |
| 117 | `print(f"🎲 Estratto numero: {numero}")` |
| 119 | `print(f"   🏆 {len(risultato['premi_nuovi'])} nuovi premi!")` |
| 121 | `print("   🎉 TOMBOLA RILEVATA!")` |
| 136 | `print("❌ Parametro non è Partita valida")` |
| 141 | `print(f"📊 Stato: {stato['stato_partita']} - {len(stato['numeri_estratti'])} estratti")` |
| 144 | `print(f"❌ Errore stato partita: {exc}")` |
| 159 | `print("❌ Parametro non è Partita valida")` |
| 164 | `print("🎉 TOMBOLA presente nella partita!")` |
| 179 | `print("❌ Parametro non è Partita valida")` |
| 184 | `print("🏁 Partita TERMINATA")` |
| 199 | `print("❌ Parametro non è Partita valida")` |
| 204 | `print("🛑 Partita TERMINATA forzatamente")` |
| 207 | `print(f"❌ Errore terminazione: {exc}")` |

Vincoli operativi per questa fase:
- Non introdurre logger, eventi, commenti o refactor.
- Non modificare rami condizionali, ritorni o gestione eccezioni adiacenti.
- Non modificare docstring.
- Non modificare firmature pubbliche.

Dopo la rimozione, eseguire:
```
python -m unittest discover -s tests -p "test_*.py"
```
e verificare che il conteggio OK aumenti rispetto alla baseline.

**Dipendenze**: Fase 0 completata.

**Rischi**: nessuno atteso. La rimozione di `print()` non e' contrattuale e non
interagisce con assert, ritorni o logica di controllo.

**Criteri di completamento**:
- Esattamente 18 righe rimosse da `bingo_game/comandi_partita.py`.
- Nessuna altra riga modificata nel file.
- `python -m py_compile bingo_game/comandi_partita.py` eseguito senza errori.
- Suite eseguita: conteggio OK superiore alla baseline (319).

**Commit suggerito**:
```
fix(application): rimuovi print() con Unicode emoji da comandi_partita.py
```

---

### Fase 2 — Fix FILE 2: rimozione print() da test_game_controller.py

**Obiettivo**: eliminare i 2 `print()` informativi da `tests/test_game_controller.py`,
riducendo il rumore CI e allineando i test al principio che l'osservabilita' deve
stare negli assert, non nell'output su stdout.

**File da MODIFICARE**:
- `tests/test_game_controller.py`

**Azioni**:

Rimuovere esclusivamente le seguenti righe (testo esatto dal DESIGN):

| Riga | Contenuto da rimuovere |
|------|------------------------|
| 470 | `print("✅ Test numeri esauriti: simulazione OK (test manuale consigliato)")` |
| 780 | `print(f"✅ Stato '{stato_target}': controller={controller_result}, partita={partita_result}")` |

Vincoli operativi per questa fase:
- Non modificare assert adiacenti.
- Non modificare setup, teardown o fixture.
- Non modificare logica di test o naming dei metodi.

Dopo la rimozione, eseguire:
```
python -m unittest discover -s tests -p "test_*.py"
```
e verificare avanzamento verso il target 351 OK.

**Dipendenze**: Fase 1 completata con verde parziale confermato.

**Rischi**: nessuno atteso. Le 2 righe sono puramente informative e non usate da
nessun assert.

**Criteri di completamento**:
- Esattamente 2 righe rimosse da `tests/test_game_controller.py`.
- Nessuna altra riga modificata nel file.
- `python -m py_compile tests/test_game_controller.py` eseguito senza errori.
- Suite eseguita: conteggio ERROR azzerato o ulteriormente ridotto.

**Commit suggerito**:
```
fix(tests): rimuovi print() informativi da test_game_controller.py
```

---

### Fase 3 — Validazione finale

**Obiettivo**: verificare che l'intera suite raggiunga il target post-fix e
confermare che nessuna firma, logica o struttura sia stata alterata.

**File coinvolti**: nessuno modificato

**Azioni**:
1. Eseguire il runner completo:
   ```
   python -m unittest discover -s tests -p "test_*.py"
   ```
2. Verificare che il risultato corrisponda esattamente a **351 OK / 0 ERROR / 1 Skipped / 0 FAIL**.
3. Eseguire `grep -rn "print(" bingo_game/comandi_partita.py` — deve restituire 0 occorrenze.
4. Eseguire `grep -n "print(" tests/test_game_controller.py` — deve restituire 0 occorrenze
   relative alle righe 470 e 780.
5. Verificare che nessuna firma pubblica di `ComandiSistema` sia cambiata rispetto alla
   baseline (confronto visivo o diff).
6. Verificare che nessun blocco `if/else`, `try/except` o `return` adiacente alle righe
   rimosse abbia subito alterazioni.

**Criteri di completamento**:
- **351 OK / 0 ERROR / 1 Skipped / 0 FAIL** confermato.
- Grep su `print()` nei due file target restituisce 0 occorrenze sulle righe elencate.
- Nessun cambio contrattuale rilevato.

**Rischi**: nessuno atteso — il fix e' una rimozione pura senza side effect
su contratti o flusso di controllo.

**Commit**: nessun commit aggiuntivo richiesto in questa fase.

---

## Test Plan

| Fase | Tipo | Comando | Risultato atteso |
|------|------|---------|-----------------|
| 0 | read-only | `python -m unittest discover -s tests -p "test_*.py"` | 319 OK / 32 ERROR / 1 Skipped / 0 FAIL |
| 1 | post-fix FILE 1 | `python -m unittest discover -s tests -p "test_*.py"` | incremento OK rispetto a 319 |
| 2 | post-fix FILE 2 | `python -m unittest discover -s tests -p "test_*.py"` | ulteriore incremento OK |
| 3 | validazione finale | `python -m unittest discover -s tests -p "test_*.py"` | 351 OK / 0 ERROR / 1 Skipped / 0 FAIL |

Nessun test aggiuntivo da scrivere: il fix e' una rimozione pura e la copertura
esistente e' sufficiente a verificare l'assenza di regressioni.
