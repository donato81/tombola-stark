## Metadati

tipo: report
titolo: Diagnostica coerenza test vs codice — Tombola Stark
data_creazione: 2026-03-28
agente: Agent-Docs
stato: bozza

## Contenuto

### Trigger

Richiesta manuale di analisi diagnostica dei test presenti nel progetto
per validare la coerenza con il codice attuale (28-03-2026).

### Sommario esecutivo

Suite di 500 test raccolta in 0.21s. Esecuzione completa: ~16s.

| Categoria        | Conteggio | Percentuale |
|------------------|-----------|-------------|
| Passati          | 438       | 87,6%       |
| Falliti          | 16        | 3,2%        |
| Errori (setup)   | 46        | 9,2%        |
| Saltati          | 1         | 0,2%        |
| Warning          | 19        | —           |

I 62 casi non-verdi si raggruppano in 5 problemi distinti con cause
radice identificate. Nessun problema blocca il dominio core
(cartella, partita, tabellone, giocatori automatici) che risulta verde.
Le anomalie sono concentrate nel layer TUI (v0.10.0) e in due test
con assunzioni errate sullo schema di `get_stato_sintetico`.

---

### Dettaglio osservazioni

#### PROBLEMA 1 — CRITICO | 46 errori di setup su `test_tui_commander.py`

Causa: Il file inietta `msvcrt` in `sys.modules` solo se assente
(`if "msvcrt" not in sys.modules`). Su Windows, `msvcrt` è sempre
presente come modulo reale. Il fixture `reset_msvcrt` chiama
`msvcrt_mock.reset_mock()` sul modulo reale che non ha l'attributo
→ `AttributeError: module 'msvcrt' has no attribute 'reset_mock'`.

File:
- `tests/unit/test_tui_commander.py` righe 31-44

Fix proposto: Sostituire la guardia condizionale con un'iniezione
forzata incondizionale, oppure usare
`unittest.mock.patch.dict(sys.modules, {"msvcrt": MagicMock()})`
come fixture autouse con scope="module".

---

#### PROBLEMA 2 — ALTO | 13 fallimenti in `test_flusso_game_loop.py` — StopIteration

Causa: I test mockano `partita_terminata` con
`side_effect=[False, False, False]` (3 valori fissi). La logica
attuale di `_loop_partita` (refactored in v0.10.0 con tasti rapidi)
chiama `partita_terminata` più volte del previsto perché il loop
esegue controlli aggiuntivi dopo la conferma del comando `q`.
La lista di `side_effect` si esaurisce → `StopIteration`.

Esempio traccia:
```
bingo_game/ui/tui/tui_partita.py:99 in _loop_partita
    while not partita_terminata(partita):
StopIteration
```

File:
- `tests/flow/test_flusso_game_loop.py` (tutti i test del file)
- `bingo_game/ui/tui/tui_partita.py` riga 99

Fix proposto: Aggiornare i `side_effect` aggiungendo almeno un valore
`True` finale per le chiamate post-conferma, oppure usare
`side_effect=lambda _: False` fino alla condizione di uscita attesa.

---

#### PROBLEMA 3 — MEDIO | test_get_stato_sintetico_coincide_con_get_stato_completo — AssertionError

Causa: Il test assume `get_stato_sintetico() == get_stato_completo()`
ma i due metodi hanno una divergenza intenzionale:
- `get_stato_sintetico()`: 5 chiavi (`stato_partita`,
  `ultimo_numero_estratto`, `numeri_estratti`, `giocatori`,
  `premi_gia_assegnati`)
- `get_stato_completo()`: 7 chiavi (aggiunge `numeri_mancanti`
  e `conteggio_giocatori`)

File:
- `tests/test_partita.py` riga 1381
- `bingo_game/partita.py` righe 891-920

Fix proposto: Aggiornare il test per confrontare solo le 5 chiavi
comuni (subset check), non uguaglianza diretta tra i due dict.

---

#### PROBLEMA 4 — MEDIO | test_ottieni_stato_sintetico_dict_silenzioso — ValueError

Causa: `game_controller.ottieni_stato_sintetico()` chiama
`partita.get_stato_sintetico()` e verifica che ritorni un `dict`.
Il mock spec'd su `Partita` ritorna un `MagicMock` (non un dict).
Il fixture/test non configura `return_value` per `get_stato_sintetico`.

```
ValueError: Partita.get_stato_sintetico() non ha ritornato un
dizionario valido
```

File:
- `tests/test_silent_controller.py` riga 116
- `bingo_game/game_controller.py` riga 520

Fix proposto: Aggiungere nel fixture o nel test:
`partita_mock.get_stato_sintetico.return_value = {"stato_partita": ..., ...}`

---

#### PROBLEMA 5 — BASSO | test_loop_comando_non_riconosciuto_no_crash — test flaky

Causa: Il test passa in isolamento ma fallisce nella suite completa.
Dipendenza dall'ordine di esecuzione: uno stato globale
(mock di `msvcrt` o di `leggi_tasto`) viene lasciato sporco
da un test precedente.

File:
- `tests/unit/test_tui_partita.py`

Fix proposto: Aggiungere `tests/conftest.py` con fixture `autouse`
per cleanup sistematico del mock `msvcrt` tra tutti i test.

---

#### PROBLEMA 6 — BASSO | 19 PytestUnknownMarkWarning

Causa: I marker `pytest.mark.unit` e `pytest.mark.integration`
non sono registrati in `pyproject.toml` o `pytest.ini`.

File:
- `tests/unit/test_tui_commander.py`
- `tests/integration/test_game_loop_tasti.py`

Fix proposto: Aggiungere in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
markers = [
    "unit: test unitari isolati",
    "integration: test di integrazione multi-modulo",
]
```

---

### Copertura per modulo (stima da raccolta)

| Modulo                        | Test dedicati | Stato        |
|-------------------------------|---------------|--------------|
| `cartella.py`                 | ~80 test      | Verde        |
| `partita.py`                  | ~55 test      | 1 failure P3 |
| `game_controller.py`          | ~40 test      | 1 failure P4 |
| `tabellone.py`                | ~15 test      | Verde        |
| `giocatore_base.py`           | ~10 test      | Verde        |
| `tui_commander.py`            | ~40 test      | 46 errori P1 |
| `tui_partita.py`              | ~30 test      | 13 fail P2   |
| `giocatore_automatico.py`     | ~8 test       | Verde        |
| `utils.py`                    | nessuno       | Non coperto  |
| `comandi_partita.py`          | nessuno       | Non coperto  |
| `vocalizzatore.py` (my_lib)   | nessuno       | Non coperto  |

---

### Raccomandazioni

Ordine di priorità intervento:

1. P1 — Fix guard `msvcrt` in `test_tui_commander.py`
   → sblocca 46 errori immediatamente
2. P2 — Allinea `side_effect` in `test_flusso_game_loop.py`
   → sblocca 13 fallimenti post-refactor v0.10.0
3. P3/P4 — Correggi assunzioni su `get_stato_sintetico`
   → risolve 2 fallimenti domain/controller
4. P5 — Aggiungi `conftest.py` con cleanup autouse
   → stabilizza il test flaky
5. P6 — Registra marker in `pyproject.toml`
   → elimina 19 warning dalla suite

Moduli senza copertura (`utils.py`, `comandi_partita.py`,
`vocalizzatore.py`) da includere nella roadmap di testing
per aumentare la copertura del dominio.

---

### File analizzati

- `tests/` (intera struttura: root, flow/, integration/, unit/)
- `tests/unit/test_tui_commander.py`
- `tests/flow/test_flusso_game_loop.py`
- `tests/test_partita.py`
- `tests/test_silent_controller.py`
- `tests/unit/test_tui_partita.py`
- `bingo_game/partita.py`
- `bingo_game/game_controller.py`
- `bingo_game/ui/tui/tui_partita.py`

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Condiviso
