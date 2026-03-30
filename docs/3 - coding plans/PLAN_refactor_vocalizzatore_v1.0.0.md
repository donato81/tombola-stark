---
type: plan
feature: refactor_vocalizzatore
agent: Agent-Plan
status: DRAFT
version: v1.0.0
design_ref: docs/2 - projects/DESIGN_refactor_vocalizzatore_v1.0.0.md
date: 2026-03-31
report_ref: docs/4 - reports/analisi_refactor_vocalizzatore/REPORT_DIAGNOSI_VOCALIZZATORE_2026-03-30.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo refactor strutturale R2 per my_lib/vocalizzatore.py
data_creazione: 2026-03-31
agente: Agent-Plan
stato: draft
feature: refactor_vocalizzatore
versione_progetto: v1.0.0
design: docs/2 - projects/DESIGN_refactor_vocalizzatore_v1.0.0.md
report: docs/4 - reports/analisi_refactor_vocalizzatore/REPORT_DIAGNOSI_VOCALIZZATORE_2026-03-30.md

## Contenuto

### Riferimento design

- Design padre: docs/2 - projects/DESIGN_refactor_vocalizzatore_v1.0.0.md

### Obiettivo operativo

Implementare il refactor R2 del modulo [my_lib/vocalizzatore.py](../..//my_lib/vocalizzatore.py)
introducendo un contratto stabile `IVocalizzatore`, una implementazione
silenziosa `NullVocalizzatore`, una classe `Vocalizzatore` ridotta al solo
adattatore AO2 e una minima modifica di type hint in
[bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py).

Il ciclo si considera chiuso solo quando la suite `tests/unit` e' verde con
zero failure e zero error.

### Passi sequenziali

#### Passo 1 - Definizione del contratto `IVocalizzatore`

Cosa si modifica:

- introdurre `IVocalizzatore` come `Protocol` con il metodo
  `vocalizza_testo(self, testo: str, interrompi: bool = False) -> None`.

File coinvolto:

- [my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py)

Risultato atteso:

- esiste un contratto tipizzato, minimale e strutturale per la vocalizzazione;
- il contratto e' importabile dal renderer e dai test futuri;
- il modulo non dipende da ereditarieta' nominale.

#### Passo 2 - Definizione di `NullVocalizzatore`

Cosa si modifica:

- aggiungere `NullVocalizzatore` nello stesso modulo del contratto;
- implementare `vocalizza_testo()` come no-op silenziosa.

File coinvolto:

- [my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py)

Risultato atteso:

- esiste uno stub headless-safe conforme a `IVocalizzatore`;
- i test e gli ambienti senza AO2 possono usare una implementazione muta;
- nessun backend esterno viene inizializzato da `NullVocalizzatore`.

#### Passo 3 - Refactor di `Vocalizzatore`

Cosa si modifica:

- rimuovere i 9 metodi dead code indicati nel report;
- aggiungere costruttore con backend opzionale iniettabile;
- aggiornare type hints e docstring;
- implementare `try/except` best-effort in `vocalizza_testo()`;
- inoltrare il parametro `interrompi` al backend AO2.

File coinvolto:

- [my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py)

Risultato atteso:

- `Vocalizzatore` resta un adapter AO2 minimale e testabile;
- il modulo espone solo il contratto reale usato dal codebase;
- un errore di AO2 non blocca il gioco.

#### Passo 4 - Aggiornamento del type hint in `WxRenderer`

Cosa si modifica:

- sostituire il type hint del parametro `vocalizzatore` nel costruttore da
  `Vocalizzatore` a `IVocalizzatore`;
- sostituire il type hint dell'attributo `_vocalizzatore` sulla riga di
  assegnazione immediatamente successiva.

File coinvolto:

- [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)

Risultato atteso:

- il renderer dipende dal contratto astratto;
- nessun'altra parte del renderer viene toccata;
- il comportamento runtime resta invariato.

#### Passo 5 - Scrittura dei test unitari

Cosa si modifica:

- creare `tests/unit/test_vocalizzatore.py` con `unittest` puro;
- testare `NullVocalizzatore`;
- testare `Vocalizzatore` usando un backend fake iniettabile con metodo
  `speak()`;
- non usare mai `pytest`;
- non usare mai `patch()` su `Auto`.

File coinvolto:

- [tests/unit/test_vocalizzatore.py](../../tests/unit/test_vocalizzatore.py)

Risultato atteso:

- esistono test diretti e isolati del contratto vocale;
- i test non richiedono screen reader attivo;
- la suite verifica forwarding del testo, forwarding di `interrompi` e
  comportamento silenzioso su eccezione.

#### Passo 6 - Esecuzione dell'intera suite

Cosa si modifica:

- nessun file sorgente;
- esecuzione della suite con discovery su `tests/unit`.

File coinvolti:

- [tests/unit/test_vocalizzatore.py](../../tests/unit/test_vocalizzatore.py)
- intera cartella `tests/unit`

Risultato atteso:

- comando finale verde;
- zero failure;
- zero error;
- il refactor e' considerato chiuso solo dopo questa verifica.

### Vincoli operativi

- AO2 resta l'unico backend reale;
- nessuna introduzione di altri motori TTS;
- nessuno spostamento di file;
- nessuna integrazione con `it.py` in questo ciclo;
- test esclusivamente con `unittest`.

### Comando finale da eseguire

python -m unittest discover tests/unit

## Stato Avanzamento

- [x] Piano redatto
- [ ] Validazione umana
- [ ] Approvato per implementazione
- [ ] Esecuzione coding non avviata