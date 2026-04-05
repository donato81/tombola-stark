## Metadati

tipo: report
titolo: Analisi incoerenze di stile e standard in tabellone.py
data_creazione: 2026-03-31
agente: Agent-Analyze
stato: validato

---

## Sommario esecutivo

`bingo_game/tabellone.py` è il modulo core con il numero maggiore di
incoerenze rispetto allo standard del progetto. Nessuna delle problematiche
riguarda la logica di gioco (che funziona correttamente, 665 test verdi),
ma tutte riguardano coerenza di stile, annotazioni di tipo e struttura
documentativa rispetto a `cartella.py`, `partita.py` e `giocatore_base.py`.

Il punto che probabilmente ricordavi riguarda le annotazioni di ritorno
(`-> ReturnType`) nelle firme dei metodi: nel progetto ogni metodo pubblico
le ha — in `tabellone.py` mancano su 11 dei 13 metodi.

---

## Elenco incoerenze per severità

---

### I-01 · ALTA — `from __future__ import annotations` mancante

Tutti i moduli core del progetto iniziano con questa direttiva:

- `cartella.py` riga 1
- `partita.py` riga 139
- `giocatore_base.py` riga 68
- `comandi_partita.py`, `game_controller.py`, tutti i moduli events/

`tabellone.py` non la importa. La direttiva è necessaria per abilitare
le annotazioni di tipo forward-reference e per la compatibilità con mypy
in modalità strict.

Fix: aggiungere `from __future__ import annotations` come prima riga
del modulo, subito dopo eventuali commenti iniziali.

---

### I-02 · ALTA — Annotazioni di ritorno (`-> ReturnType`) mancanti

**Questo è il punto che ricordavi.**

Nel progetto ogni metodo pubblico ha la firma con annotazione di ritorno:

```python
# in giocatore_base.py
def get_nome(self) -> str: ...
def aggiungi_cartella(self, cartella: Cartella) -> None: ...
def aggiorna_con_numero(self, numero: int) -> None: ...

# in partita.py
def get_numero_giocatori(self) -> int: ...
def aggiungi_giocatore(self, giocatore: GiocatoreBase) -> None: ...
```

In `tabellone.py` solo 2 metodi su 13 hanno l'annotazione completa:
- `is_numero_estratto(self, numero: int) -> bool` — presente ✓
- `get_ultimi_numeri_estratti(self, n: int = 5) -> tuple[int, ...]` — presente ✓

Metodi senza annotazione di ritorno (11):

| Metodo | Annotazione mancante corretta |
|--------|-------------------------------|
| `__init__(self)` | `-> None` |
| `_inizializza_tabellone(self)` | `-> None` |
| `estrai_numero(self)` | `-> int` |
| `reset_tabellone(self)` | `-> None` |
| `numeri_terminati(self)` | `-> bool` |
| `gestione_errore_numeri_terminati(self)` | `-> None` |
| `get_conteggio_estratti(self)` | `-> int` |
| `get_conteggio_disponibili(self)` | `-> int` |
| `get_numeri_estratti(self)` | `-> list[int]` |
| `get_numeri_disponibili(self)` | `-> list[int]` |
| `get_percentuale_avanzamento(self)` | `-> float` |
| `get_ultimo_numero_estratto(self)` | `-> int \| None` |
| `get_stato_tabellone(self)` | `-> dict[str, Any]` |

Fix: aggiungere `-> ReturnType` a ogni firma e, dove necessario,
aggiungere i parametri di input mancanti (es. `numero: int` in
`estrai_numero` non ne ha ma accetta scope implicito dal tabellone).

---

### I-03 · ALTA — Annotazioni di tipo sugli attributi di istanza mancanti

In `partita.py` e `giocatore_base.py` gli attributi vengono annotati
nell'`__init__`:

```python
# partita.py
self.giocatori: List[GiocatoreBase] = giocatori[:] if giocatori else []
self.stato_partita: str = "non_iniziata"
self.ultimo_numero_estratto: Optional[int] = None

# giocatore_base.py
self.cartelle: List[Cartella] = []
self._prossimo_indice_cartella: int = 1
self.reclamo_turno: Optional[ReclamoVittoria] = None
```

In `tabellone.py` gli attributi sono assegnati in `_inizializza_tabellone()`
senza alcuna annotazione:

```python
def _inizializza_tabellone(self):
    self.numeri_disponibili = set(range(1, 91))   # manca: set[int]
    self.numeri_estratti = set()                   # manca: set[int]
    self.ultimo_numero_estratto = None             # manca: int | None
    self.storico_estrazioni = []                   # manca: list[int]
```

Fix: aggiungere annotazioni di tipo a ciascun attributo.

---

### I-04 · MEDIA — Docstring di classe e docstring di modulo mancanti

`tabellone.py` inizia con commenti `#` inline:

```python
#import delle librerie necessarie
import random

class Tabellone:
    #costruttore della classe Tabellone
    def __init__(self):
```

Pattern del progetto (`partita.py`, `giocatore_base.py`):
- module docstring elaborata all'inizio del file (tripla virgolette)
- class docstring immediatamente dopo `class NomeClasse:`

Fix: aggiungere una module docstring descrittiva e una docstring di classe.

---

### I-05 · MEDIA — Docstring Python assenti su metodi "semplici"

Alcuni metodi hanno docstring Python complete con sezione Ritorna/Raises,
altri hanno solo commenti `#` inline:

Metodi con docstring Python presente:
- `is_numero_estratto`, `get_conteggio_estratti`, `get_conteggio_disponibili`
- `get_percentuale_avanzamento`, `get_ultimo_numero_estratto`
- `get_ultimi_numeri_estratti`, `get_stato_tabellone`

Metodi con solo commenti `#` (senza docstring):
- `_inizializza_tabellone`, `estrai_numero`, `reset_tabellone`
- `numeri_terminati`, `gestione_errore_numeri_terminati`
- `get_numeri_estratti`, `get_numeri_disponibili`

Il progetto non ha regola che obblighi una docstring per ogni metodo,
ma l'incoerenza all'interno dello stesso file è rilevante perché rende
il modulo visivamente disomogeneo e produce output mypy/pylint differenziato.

---

### I-06 · MEDIA — `raise ValueError` invece di eccezione di dominio

`gestione_errore_numeri_terminati()` solleva un `ValueError` generico:

```python
def gestione_errore_numeri_terminati(self):
    raise ValueError("Tutti i numeri sono stati estratti. ...")
```

Il pattern del progetto è usare eccezioni di dominio specifiche
(vedi `PartitaNumeriEsauritiException` in `partita.py`,
`CartellaNumeroTypeException` in `cartella.py`).

Il file `bingo_game/exceptions/tabellone_exceptions.py` esiste ma è vuoto.

Fix contestuale: prima definire le eccezioni in `tabellone_exceptions.py`,
poi importarle e sostituire `ValueError` con la specifica.

Nota: questa voce era già catalogata come osservazione nel
`REPORT_DIAGNOSI_COMPLETA_PROGETTO_2026-03-28.md` come anomalia lieve
(funziona perché `Partita` la intercetta comunque).

---

### I-07 · BASSA — String literals come separatori di sezione (pattern progetto)

`tabellone.py` usa string literals libere come intestazioni di sezione:

```python
"""metodi della classe tabellone"""
"""sezione: metodi di creazione del tabellone"""
"""sezione: metodi di stato/controllo"""
```

Questi sono no-op (Python li scarta). Lo stesso pattern è presente
in `cartella.py`, `partita.py`, `giocatore_base.py`: non è un'anomalia
esclusiva del tabellone ma un pattern trasversale all'intero progetto.

Nessun fix urgente; se il team decidesse di uniformare si dovrebbe
fare globalmente (con commenti `# --- Sezione ---` standard).

---

## Riepilogo incoerenze

| ID | Severità | Descrizione sintetica | File coinvolto |
|----|----------|-----------------------|----------------|
| I-01 | Alta | `from __future__ import annotations` mancante | `tabellone.py` riga 1 |
| I-02 | Alta | Return type hint mancante su 11 metodi | `tabellone.py` tutte le firme |
| I-03 | Alta | Attributi di istanza senza annotazione di tipo | `tabellone.py` `_inizializza_tabellone` |
| I-04 | Media | Module docstring e class docstring assenti | `tabellone.py` |
| I-05 | Media | Docstring Python assente su metodi "semplici" | `tabellone.py` 7 metodi |
| I-06 | Media | `raise ValueError` invece di `TabelloneException` | `tabellone.py` riga 97 + `tabellone_exceptions.py` |
| I-07 | Bassa | String literals come separatori di sezione | `tabellone.py` (pattern trasversale) |

---

## Contesto rispetto ai report precedenti

`REPORT_DIAGNOSI_COMPLETA_PROGETTO_2026-03-28.md` aveva già catalogato:
- VIOL-2: type hints mancanti (corrisponde a I-01 + I-02 + I-03 di questo report)
- anomalia `raise ValueError` (corrisponde a I-06)

Questo report approfondisce e cataloga ciascuna incoerenza separatamente
con il fix specifico, in preparazione a un eventuale task di allineamento.

---

## Suggerimento operativo

Se si vuole correggere questo modulo, l'ordine consigliato è:

1. Aggiungere `from __future__ import annotations` + `from typing import Any, Optional` (I-01)
2. Annotare gli attributi in `_inizializza_tabellone` (I-03)
3. Aggiungere i return type hint a tutte le firme (I-02)
4. Aggiungere module docstring e class docstring (I-04)
5. Definire `TabelloneNumeriEsauritiException` in `tabellone_exceptions.py` e sostituire `ValueError` (I-06)
6. Eventuale normalizzazione delle docstring dei metodi semplici (I-05)

I punti 1-4 sono modifiche puramente formali (non cambiano comportamento,
non rompono test). Il punto 5 richiede un piccolo test aggiuntivo.
