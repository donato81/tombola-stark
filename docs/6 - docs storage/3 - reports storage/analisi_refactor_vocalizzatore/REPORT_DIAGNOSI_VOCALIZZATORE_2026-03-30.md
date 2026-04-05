## Metadati

tipo: report
titolo: Diagnosi profonda di my_lib/vocalizzatore.py — proposta di refactor
data_creazione: 2026-03-30
agente: Agent-Analyze
stato: definitivo
scopo: definire la direzione di refactor del modulo di vocalizzazione

---

## 1. Sintesi esecutiva

`my_lib/vocalizzatore.py` è un modulo di ~100 righe che fa da bridge verso
`accessible_output2` (AO2). Nel suo stato attuale presenta cinque criticità
principali:

- **9 dei 10 metodi pubblici sono dead code**: solo `vocalizza_testo()` è
  usato nel codebase (via `WxRenderer._ao2_vocalizza()`).
- **Nessuna interfaccia astratta**: `WxRenderer` dipende dalla classe concreta
  `Vocalizzatore`, non da un protocollo — impossibile sostituirla senza
  modificare il renderer.
- **Nessuna gestione degli errori**: se AO2 non è disponibile (nessun screen
  reader attivo, libreria non installata), `Auto()` e `speak()` sollevano
  eccezioni non catturate.
- **Zero test**: il file non ha copertura unitaria. La testabilità è ostacolata
  dal fatto che `Auto()` viene istanziato direttamente nel costruttore.
- **Mixed concerns senza separazione**: metodi infrastrutturali (wrapper AO2)
  convivono con metodi di dominio specifici (tabellone, liste) nella stessa
  classe.

---

## 2. Stato attuale del modulo

### 2.1 Struttura della classe

```
Vocalizzatore
├── __init__(self)                                → istanzia Auto() di AO2
│
├── — metodi base (wrapper AO2) —
├── vocalizza_testo(testo: str)                   → Auto.speak(testo)
├── vocalizza_numero(numero: int)                 → "Numero estratto: N"
├── vocalizza_errore(messaggio: str)              → "Attenzione, errore: ..."
│
├── — metodi dominio Tabellone —
├── messaggio_inizializzazione()                  → stringa fissa
├── messaggio_errore_numeri_terminati()           → stringa fissa
├── messaggio_numero_estratto(numero: int)        → delega a vocalizza_numero()
├── messaggio_reset_tabellone()                   → stringa fissa
│
├── — metodi dominio Liste —
├── vocalizza_numeri_estratti(numeri: list[int])  → lista formattata
├── vocalizza_numeri_disponibili(numeri: list[int]) → lista formattata
│
└── — metodo privato —
    _formatta_numeri_per_vocalizzazione(numeri)   → join con "; "
```

Totale: 10 metodi pubblici + 1 privato.

### 2.2 Dipendenza esterna

- Libreria: `accessible-output2==0.17`
- Import: `from accessible_output2.outputs.auto import Auto`
- Classe istanziata: `Auto()` — backend automatico che seleziona il
  technology layer disponibile (NVDA, JAWS, SAPI5, ecc.)
- L'intera logica di selezione screen reader è delegata ad AO2.

---

## 3. Analisi degli usi nel codebase

### 3.1 Unico punto di uso effettivo

```
bingo_game/ui/renderers/renderer_wx.py (riga 22)
    from my_lib.vocalizzatore import Vocalizzatore

renderer_wx.py (riga 84)
    self._vocalizzatore: Vocalizzatore = vocalizzatore  # DI nel costruttore

renderer_wx.py (riga 392)
    def _ao2_vocalizza(self, testo: str) -> None:
        self._vocalizzatore.vocalizza_testo(testo)
```

Il renderer riceve `Vocalizzatore` tramite dependency injection (corretto), ma
usa **solo** `vocalizza_testo()`. Tutti gli altri metodi non sono mai invocati.

### 3.2 Metodi effettivamente in uso

| Metodo | Chiamato da | Note |
|--------|-------------|-------|
| `vocalizza_testo()` | `WxRenderer._ao2_vocalizza()` | Unico metodo attivo |

### 3.3 Metodi inutilizzati (dead code)

| Metodo | Stato |
|--------|-------|
| `vocalizza_numero()` | Dead code |
| `vocalizza_errore()` | Dead code |
| `messaggio_inizializzazione()` | Dead code |
| `messaggio_errore_numeri_terminati()` | Dead code |
| `messaggio_numero_estratto()` | Dead code |
| `messaggio_reset_tabellone()` | Dead code |
| `vocalizza_numeri_estratti()` | Dead code |
| `vocalizza_numeri_disponibili()` | Dead code |
| `_formatta_numeri_per_vocalizzazione()` | Dead code (usato solo dai metodi sopra) |

Queste API erano state progettate per un renderer precedente (TerminalRenderer)
che è stato rimosso. Il ciclo di refactor `base_renderer_wx_v1.0.0` (2026-03-30)
non ha ripulito `Vocalizzatore`.

### 3.4 Nessun test per il modulo

`tests/unit/test_renderer_report_finale.py` — citato nel CHANGELOG — è stato
rimosso dalla cartella `tests/` nel ciclo di refactor del renderer terminale.
Nessun altro file di test copre `vocalizzatore.py`.

---

## 4. Problemi identificati

### ALTA PRIORITÀ

**P1 — Nessuna interfaccia astratta**

`WxRenderer` dipende dalla classe concreta `Vocalizzatore`:

```python
# renderer_wx.py riga 81
vocalizzatore: Vocalizzatore,
```

Questo viola il principio di Dependency Inversion: il renderer di alto livello
(presentation) dipende dal dettaglio (AO2 concrete). Se si volesse:
- Aggiungere un secondo backend TTS (gTTS, Windows SAPI diretta)
- Mock nei test senza `patch()`
- Un `NullVocalizzatore` per modalità muta in CI o headless

... occorre modificare `WxRenderer`. Non esiste contratto astratto.

**P2 — Nessuna gestione delle eccezioni**

```python
def __init__(self):
    self.speaker = Auto()  # puede lanciare eccezione se AO2 non disponibile

def vocalizza_testo(self, testo: str):
    self.speaker.speak(testo)  # puede lanciare eccezione a runtime
```

Se NVDA non è attivo o `accessible-output2` non è installato correttamente,
l'intera applicazione crasha. La vocalizzazione deve essere best-effort per
un'app accessibile: un errore TTS non deve mai bloccare il gioco.

**P3 — Dead code (9 metodi)**

Il 90% della superficie pubblica è codice inutilizzato che:
- Aumenta la superficie di test necessaria
- Crea falsa impression di API ricca
- Maschera il vero contratto atteso (solo `vocalizza_testo`)

### MEDIA PRIORITÀ

**P4 — Testabilità difficile**

Il costruttore chiama `Auto()` direttamente. Per testare qualsiasi metodo
occorre:

```python
with patch("my_lib.vocalizzatore.Auto") as mock_cls:
    mock_cls.return_value = MagicMock()
    voc = Vocalizzatore()
```

Un pattern più testabile userebbe injection del backend:

```python
def __init__(self, backend: Auto | None = None) -> None:
    self._backend = backend or Auto()
```

**P5 — Stringhe hardcoded, fuori dal catalogo locales**

```python
def vocalizza_numero(self, numero: int):
    testo = f"Numero estratto: {numero}"  # hardcoded, non nel catalogo it.py

def vocalizza_errore(self, messaggio: str):
    testo = f"Attenzione, errore: {messaggio}"  # hardcoded
```

Il catalogo `bingo_game/ui/locales/it.py` è la source of truth per tutti i
testi esposti all'utente. Le stringhe di Vocalizzatore bypassano questo sistema.

**P6 — Ridondanza `vocalizza_numero` / `messaggio_numero_estratto`**

```python
def vocalizza_numero(self, numero: int):
    testo = f"Numero estratto: {numero}"
    self.speaker.speak(testo)

def messaggio_numero_estratto(self, numero: int):
    self.vocalizza_numero(numero)  # produce la stessa identica stringa
```

Due API per la stessa cosa: confusione sul contratto.

### BASSA PRIORITÀ

**P7 — Type hints incompleti**

```python
def __init__(self):   # manca -> None
    self.speaker = Auto()
```

Non conforme a `python.instructions.md` che richiede type hints su tutti i
metodi pubblici.

**P8 — Commenti inline ridondanti invece di docstring**

```python
#metodo per vocalizzare il messaggio di reset del tabellone
def messaggio_reset_tabellone(self):
    #richiama il metodo per vocalizzare il testo passando il messaggio di reset
    self.vocalizza_testo("Reset del tabellone.")
```

Il commento descrive solo ciò che il codice fa già: nessun valore aggiunto.
Lo standard `python.instructions.md` richiede docstring significativi, non
commenti ridondanti su ogni riga.

**P9 — Parametro `interrupt` di AO2 non esposto**

`Auto.speak()` accetta un parametro `interrupt: bool` che, se `True`, interrompe
la frase in corso e vocalizza subito quella nuova. Utile per messaggi urgenti
(errore, tombola). Questo parametro non è mai esposto nella classe attuale.

**P10 — Posizionamento module `my_lib/`**

Il percorso `my_lib/vocalizzatore.py` è al di fuori del package `bingo_game/`
e non appartiene esplicitamente a nessuno dei 4 layer. La documentazione
architetturale lo descrive come "bridge verso accessible_output2", collocandolo
nel **layer di presentazione trasversale**. Tuttavia il posizionamento fisico
non comunica questa intenzione.

---

## 5. Analisi architetturale

### 5.1 Posizionamento attuale

```
my_lib/vocalizzatore.py   ← fuori dalla Clean Architecture
    ↑
bingo_game/ui/renderers/renderer_wx.py (Presentation layer)
```

Il layer di presentazione importa direttamente la classe concreta da un
percorso esterno all'architettura.

### 5.2 Posizionamento ideale

Secondo la Clean Architecture del progetto, un componente che:
- Dipende da una libreria esterna (`accessible-output2`)
- Implementa un'interfaccia di servizio
- Viene iniettato nel presentation layer tramite DI

appartiene all'**Infrastructure layer** (o al layer di presentazione stesso
se è strettamente UI-only).

Due opzioni valide:

**Opzione A — Rimane in `my_lib/`, si aggiunge Protocol**

```
my_lib/vocalizzatore.py          (implementazione concreta, invariata)
bingo_game/ui/renderers/         (qui si definisce IVocalizzatore Protocol)
```

Pro: minima modifica strutturale, nessun spostamento di file.
Contro: `my_lib/` resta fuori dall'architettura, ambivalente.

**Opzione B — Spostamento in `bingo_game/ui/`**

```
bingo_game/ui/vocalizzatore.py   (implementazione concreta)
bingo_game/ui/renderers/         (Protocol definito qui)
```

Pro: tutto il layer UI è sotto `bingo_game/ui/`, coerenza strutturale.
Contro: richiede aggiornamento dell'import in `renderer_wx.py` e
        `docs/ARCHITECTURE.md`.

**Opzione C — Infrastructure namespace nuovo**

```
bingo_game/infrastructure/accessibilita/vocalizzatore.py
```

Pro: separazione esplicita infrastruttura vs presentazione.
Contro: crea un nuovo package `infrastructure/` non ancora presente.

### 5.3 Raccomandazione architetturale

**Opzione A nel breve termine** (minimo impatto, massima stabilità del ciclo
attuale), **Opzione B nel lungo termine** quando il layer UI sarà più maturo.

---

## 6. Audit della superficie API utile

Considerando l'unico caso d'uso attuale (`WxRenderer._ao2_vocalizza()`),
il contratto minimo necessario è:

```python
class IVocalizzatore(Protocol):
    def vocalizza(self, testo: str, interrompi: bool = False) -> None: ...
```

oppure, mantenendo il nome `vocalizza_testo` per compatibilità:

```python
class IVocalizzatore(Protocol):
    def vocalizza_testo(self, testo: str) -> None: ...
```

Tutti gli altri metodi attuali possono essere **rimossi** dalla classe
`Vocalizzatore` oppure spostati in un helper separato se si prevede di
riattivarli in futuro.

---

## 7. Rischi del refactor

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Rottura import in renderer_wx | Bassa | Alta | Test verde pre/post refactor |
| Perdita accidentale di metodi utili futuri | Media | Media | Deprecare prima di eliminare |
| AO2 non disponibile in CI | Alta | Media | NullVocalizzatore per test |
| Regressione nei 657 test attuali | Bassissima | Alta | Eseguire suite completa post-refactor |

---

## 8. Opzioni di refactor — sintesi decisionale

Questa sezione è il materiale di lavoro per la decisione utente.

### Opzione R1 — Refactor minimo (sicuro)

Scope: solo `my_lib/vocalizzatore.py`.

Modifiche:
1. Aggiungere `-> None` a `__init__`.
2. Sostituire commenti ridondanti con docstring.
3. Rimuovere i 9 metodi dead code.
4. Aggiungere try/except sulla chiamata `Auto.speak()` (best-effort).
5. Aggiungere docstring a `vocalizza_testo` con contratto esplicito.

Non cambia:
- Posizionamento del file (`my_lib/`)
- Interface (nessuna Protocol ancora)
- Import in `renderer_wx.py`

Risultato: file da ~100 a ~30 righe. API: solo `vocalizza_testo()`.

---

### Opzione R2 — Refactor strutturale (raccomandato)

Scope: `my_lib/vocalizzatore.py` + `bingo_game/ui/renderers/base_renderer.py`
(o un nuovo `bingo_game/ui/i_vocalizzatore.py`).

Modifiche aggiuntive rispetto a R1:
1. Definire `IVocalizzatore` come `Protocol` (o `ABC`).
2. `Vocalizzatore` implementa `IVocalizzatore`.
3. `WxRenderer.__init__` type-hints su `IVocalizzatore` invece di `Vocalizzatore`.
4. Creare `NullVocalizzatore` (stub silenzioso per test e CI).
5. Esporre il parametro `interrompi: bool = False` su `vocalizza_testo`.

Risultato: `Vocalizzatore` è sostituibile (gTTS, SAPI, Null). I test di
`WxRenderer` non richiedono più `patch("my_lib.vocalizzatore.Auto")`.

---

### Opzione R3 — Refactor completo con spostamento (futuro)

Come R2 + spostamento fisico in `bingo_game/ui/vocalizzatore.py`.
Da valutare in un ciclo dedicato con piano di migrazione degli import.

---

## 9. Prerequisiti prima del refactor

Prima di implementare qualunque opzione:

1. Eseguire `python -m unittest discover tests/` → 657 test verdi (già confermato).
2. Verificare che `renderer_wx.py` riga 392 sia l'unico punto di chiamata a
   `Vocalizzatore` nel codebase (confermato dalla grep: 1 solo file importa
   il modulo).
3. Confermare che i metodi dead code non siano pianificati in nessun TODO/PLAN
   attivo (verificato: `docs/todo.md` non riporta task attivi sul vocalizzatore).

---

## 10. Checklist diagnostica (riepilogo)

- [x] Modulo letto integralmente
- [x] Usi nel codebase mappati (1 file: `renderer_wx.py`)
- [x] Metodi dead code identificati (9 su 10 pubblici)
- [x] Dipendenza da AO2 analizzata
- [x] Rischi di testabilità documentati
- [x] Posizionamento architetturale valutato (3 opzioni)
- [x] Opzioni di refactor definite (R1, R2, R3)
- [x] Nessun file modificato (report read-only)

---

## 11. Prossimi passi suggeriti

Scegliere tra:

- **"procedi con R1"** → refactor minimo, modifica solo `vocalizzatore.py`
- **"procedi con R2"** → refactor strutturale con Protocol e NullVocalizzatore
- **"procedi con R3"** → refactor completo con spostamento (richiede più cicli)

Per R2 (raccomandato), l'agente suggerisce di aprire un ciclo:
`Agent-Design → Agent-Plan → Agent-Code` con DESIGN_refactor_vocalizzatore.md.
