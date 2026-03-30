# Report Pianificazione Test — helper_focus.py e helper_reclami_focus.py

Data: 2026-03-30
Agente: Agent-Analyze
Stato: COMPLETO

---

## 1. Perimetro dell'analisi

Due file mixin nella directory `bingo_game/players/`:

| File | Classe | Metodi | LOC |
|------|--------|--------|-----|
| helper_focus.py | GestioneFocusMixin | 16 | ~760 |
| helper_reclami_focus.py | ReclamiFocusMixin | 3 | ~180 |

Entrambi i mixin sono usati via ereditarietà multipla in `GiocatoreUmano`:
```python
class GiocatoreUmano(GestioneFocusMixin, ReclamiFocusMixin, GiocatoreBase):
```

---

## 2. Dipendenze esterne

### Attributi richiesti dal contesto host (self)

| Attributo | Tipo | Usato da |
|-----------|------|----------|
| self.cartelle | list[Cartella] | Entrambi i mixin |
| self._indice_cartella_focus | Optional[int] | Entrambi i mixin |
| self._indice_riga_focus | Optional[int] | Entrambi i mixin |
| self._indice_colonna_focus | Optional[int] | GestioneFocusMixin |
| self.id_giocatore | Optional[int] | ReclamiFocusMixin |
| self.nome | str | ReclamiFocusMixin |

### Import esterni

- `EsitoAzione` da `bingo_game.events.eventi`
- `EventoFocusAutoImpostato`, `EventoFocusCartellaImpostato` da `bingo_game.events.eventi_ui`
- `Tipo_Vittoria`, `ReclamoVittoria`, `EventoReclamoVittoria` da `bingo_game.events.eventi_partita`

### Attributi richiesti da Cartella (duck typing)

- `cartella.righe` (int, default 3)
- `cartella.colonne` (int, default 9)

---

## 3. Inventario metodi — helper_focus.py (GestioneFocusMixin)

### Sezione 1: Focus Cartella (4 metodi)

| # | Metodo | Tipo | Modifica stato | Note |
|---|--------|------|----------------|------|
| 1 | _esito_ha_cartelle() | guard | No | Controllo base: lista non vuota |
| 2 | _esito_focus_cartella_impostato(auto_imposta=True) | guard+setter | Si (se auto) | Auto-imposta indice 0 + EventoFocusAutoImpostato |
| 3 | _esito_focus_cartella_in_range() | guard | No | Strict: verifica 0 <= indice < len(cartelle) |
| 4 | _esito_focus_cartella_valido(auto_imposta=True) | composito | Si (se auto) | Compone metodo 2 + metodo 3, propaga evento |

### Sezione 2: Focus Riga (3 metodi)

| # | Metodo | Tipo | Modifica stato | Note |
|---|--------|------|----------------|------|
| 5 | _esito_focus_riga_impostato() | guard | No | Strict: richiede cartella valida (auto_imposta=False) + riga not None |
| 6 | _esito_focus_riga_in_range() | guard | No | Strict: verifica 0 <= indice < cartella.righe |
| 7 | _esito_focus_riga_valido() | composito | No | Compone metodo 5 + metodo 6 (BUG: vedi sezione 5) |

### Sezione 3: Focus Colonna (3 metodi)

| # | Metodo | Tipo | Modifica stato | Note |
|---|--------|------|----------------|------|
| 8 | _esito_focus_colonna_impostata() | guard | No | Strict: richiede cartella valida + colonna not None |
| 9 | _esito_focus_colonna_in_range() | guard | No | Strict: verifica 0 <= indice < cartella.colonne |
| 10 | _esito_focus_colonna_valido() | composito | No | Compone metodo 8 + metodo 9 |

### Sezione 4: Navigazione e inizializzazione (3 metodi)

| # | Metodo | Tipo | Modifica stato | Note |
|---|--------|------|----------------|------|
| 11 | _esito_pronto_per_navigazione() | guard | No | Delega a metodo 4 con auto_imposta=False |
| 12 | _esito_inizializza_focus_riga_se_manca() | setter | Si | Auto-imposta riga 0 se None + EventoFocusAutoImpostato |
| 13 | _esito_inizializza_focus_colonna_se_manca() | setter | Si | Auto-imposta colonna 4 se None + EventoFocusAutoImpostato |

### Sezione 5: Reset (3 metodi)

| # | Metodo | Tipo | Modifica stato | Note |
|---|--------|------|----------------|------|
| 14 | _reset_focus_riga_e_colonna() | reset | Si | None su riga e colonna, cartella invariata |
| 15 | _reset_focus_cartella_riga_e_colonna() | reset | Si | None su tutti e 3 i focus |
| 16 | imposta_focus_cartella_fallback() | setter | Si | Imposta indice 0 senza validazioni |

---

## 4. Inventario metodi — helper_reclami_focus.py (ReclamiFocusMixin)

| # | Metodo | Tipo | Modifica stato | Note |
|---|--------|------|----------------|------|
| 1 | _esito_prerequisiti_reclamo_cartella() | guard | No | Delega a _esito_focus_cartella_valido(auto_imposta=False) |
| 2 | _esito_prerequisiti_reclamo_riga() | guard | No | Compone metodo 1 + check riga + check range riga |
| 3 | _esito_crea_evento_reclamo_da_focus(tipo) | factory | No | Crea EventoReclamoVittoria (BUG: vedi sezione 5) |

---

## 5. Bug e anomalie riscontrate

### BUG-1: Typo nel nome metodo (_esito_focus_riga_valido, linea 356)

- **Dove**: helper_focus.py, metodo 7 (`_esito_focus_riga_valido`), linea 356
- **Problema**: Chiama `self._esito_focus_riga_impostata()` (femminile) ma il metodo si chiama `_esito_focus_riga_impostato()` (maschile, definito a linea 230)
- **Impatto**: AttributeError a runtime quando viene invocato `_esito_focus_riga_valido()`
- **Severita**: ALTA (crash a runtime)

### BUG-2: Parametro inatteso in chiamata (_esito_focus_riga_valido)

- **Dove**: giocatore_umano.py, linea 2250
- **Problema**: Chiama `self._esito_focus_riga_valido(auto_imposta=False)` ma la signature del metodo e `def _esito_focus_riga_valido(self)` — non accetta `auto_imposta`
- **Impatto**: TypeError a runtime ("got an unexpected keyword argument 'auto_imposta'")
- **Severita**: ALTA (crash a runtime nel flusso `annuncia_vittoria` per vittorie di riga)

### BUG-3: Parametro mancante in EventoReclamoVittoria (_esito_crea_evento_reclamo_da_focus)

- **Dove**: helper_reclami_focus.py, metodo 3 (`_esito_crea_evento_reclamo_da_focus`), linee ~160-167
- **Problema**: Costruisce `EventoReclamoVittoria(id_giocatore=..., nome_giocatore=..., reclamo=..., fase=...)` senza passare il campo obbligatorio `numero_turno: int` (richiesto dal dataclass)
- **Impatto**: TypeError a runtime ("missing 1 required positional argument: 'numero_turno'")
- **Severita**: MEDIA (il metodo risulta dead code, vedi BUG-4)

### BUG-4: Dead code — ReclamiFocusMixin metodo 3

- **Dove**: helper_reclami_focus.py, `_esito_crea_evento_reclamo_da_focus`
- **Problema**: Il metodo non e mai chiamato da nessun punto del codebase. `GiocatoreUmano.annuncia_vittoria()` implementa la stessa logica direttamente (incluso il passaggio di `numero_turno`)
- **Impatto**: Codice morto con bug latente (BUG-3). I metodi prerequisiti (metodi 1 e 2) sono anchessi chiamati solo da metodo 3, rendendo l'intero mixin potenzialmente dead code
- **Severita**: BASSA (non causa crash, ma aumenta complessita e rischio di confusione)

---

## 6. Strategia di testing

### Approccio: Stub host class

Poiche entrambi sono mixin (non istanziabili direttamente), ogni test file creera una classe stub minima:

```python
class StubGiocatore(GestioneFocusMixin):
    def __init__(self):
        self.cartelle = []
        self._indice_cartella_focus = None
        self._indice_riga_focus = None
        self._indice_colonna_focus = None
```

Per ReclamiFocusMixin, lo stub estendera anche GestioneFocusMixin (dipendenza diretta) e aggiungera `id_giocatore` e `nome`.

Per simulare `Cartella` nei test si usera un semplice stub con attributi `righe` e `colonne`, senza bisogno di MagicMock.

### Pattern dei test

Ogni metodo segue il pattern EsitoAzione con ramificazioni chiare:
- Percorso ok=True (evento present o None)
- Percorso ok=False per ogni codice errore distinto
- Verifica side-effect su stato interno (per metodi setter/reset)
- Verifica propagazione evento (per metodi compositi)

---

## 7. Organizzazione in fasi

### Fase F1 — Focus Cartella e Riga (test_helper_focus_cartella_riga.py)

**Copertura**: Metodi 1-7 (sezioni 1 e 2)
**Stima test**: 28-35

Dettaglio test per metodo:

- **Metodo 1** `_esito_ha_cartelle` (2 test)
  - cartelle vuote -> ok=False, errore=CARTELLE_NESSUNA_ASSEGNATA
  - cartelle presenti -> ok=True

- **Metodo 2** `_esito_focus_cartella_impostato` (4 test)
  - nessuna cartella -> propaga errore CARTELLE_NESSUNA_ASSEGNATA
  - focus None + auto_imposta=True -> ok=True, evento=EventoFocusAutoImpostato(cartella, 0), stato cambiato
  - focus None + auto_imposta=False -> ok=False, errore=FOCUS_CARTELLA_NON_IMPOSTATO
  - focus gia impostato -> ok=True, evento=None

- **Metodo 3** `_esito_focus_cartella_in_range` (5 test)
  - nessuna cartella -> propaga CARTELLE_NESSUNA_ASSEGNATA
  - focus None -> errore FOCUS_CARTELLA_NON_IMPOSTATO
  - focus negativo -> errore FOCUS_CARTELLA_FUORI_RANGE
  - focus >= len(cartelle) -> errore FOCUS_CARTELLA_FUORI_RANGE
  - focus valido -> ok=True

- **Metodo 4** `_esito_focus_cartella_valido` (5 test)
  - nessuna cartella -> propaga errore
  - focus None + auto_imposta=True -> ok=True, evento propagato da metodo 2
  - focus None + auto_imposta=False -> ok=False
  - focus fuori range dopo auto-impostazione -> (edge case: 1 cartella, auto ok)
  - focus in range -> ok=True, evento=None

- **Metodo 5** `_esito_focus_riga_impostato` (4 test)
  - cartella non valida -> propaga errore cartella
  - cartella valida, riga None -> errore FOCUS_RIGA_NON_IMPOSTATA
  - cartella valida, riga impostata -> ok=True
  - nessuna cartella -> propaga CARTELLE_NESSUNA_ASSEGNATA

- **Metodo 6** `_esito_focus_riga_in_range` (5 test)
  - cartella non valida -> propaga errore
  - riga None -> errore FOCUS_RIGA_NON_IMPOSTATA
  - riga negativa -> errore FOCUS_RIGA_FUORI_RANGE
  - riga >= cartella.righe -> errore FOCUS_RIGA_FUORI_RANGE
  - riga valida -> ok=True

- **Metodo 7** `_esito_focus_riga_valido` (3 test + verifica BUG-1)
  - Nota: se BUG-1 non e stato corretto, questo metodo crasha con AttributeError. I test devono documentare il comportamento atteso post-fix
  - riga non impostata -> ok=False
  - riga fuori range -> ok=False
  - riga valida -> ok=True

### Fase F2 — Focus Colonna, Navigazione e Reset (test_helper_focus_colonna_nav_reset.py)

**Copertura**: Metodi 8-16 (sezioni 3, 4, 5)
**Stima test**: 22-28

Dettaglio test per metodo:

- **Metodo 8** `_esito_focus_colonna_impostata` (3 test)
  - cartella non valida -> propaga errore
  - colonna None -> errore FOCUS_COLONNA_NON_IMPOSTATA
  - colonna impostata -> ok=True

- **Metodo 9** `_esito_focus_colonna_in_range` (5 test)
  - cartella non valida -> propaga errore
  - colonna None -> errore FOCUS_COLONNA_NON_IMPOSTATA
  - colonna negativa -> errore FOCUS_COLONNA_FUORI_RANGE
  - colonna >= cartella.colonne -> errore FOCUS_COLONNA_FUORI_RANGE
  - colonna valida -> ok=True

- **Metodo 10** `_esito_focus_colonna_valido` (3 test)
  - colonna non impostata -> ok=False
  - colonna fuori range -> ok=False
  - colonna valida -> ok=True

- **Metodo 11** `_esito_pronto_per_navigazione` (3 test)
  - nessuna cartella -> ok=False
  - focus cartella non impostato -> ok=False
  - focus valido -> ok=True, evento propagato

- **Metodo 12** `_esito_inizializza_focus_riga_se_manca` (3 test)
  - navigazione non possibile -> propaga errore
  - riga None -> ok=True, stato cambiato a 0, evento EventoFocusAutoImpostato(riga, 0)
  - riga gia impostata -> ok=True, evento=None, stato invariato

- **Metodo 13** `_esito_inizializza_focus_colonna_se_manca` (3 test)
  - navigazione non possibile -> propaga errore
  - colonna None -> ok=True, stato cambiato a 4, evento EventoFocusAutoImpostato(colonna, 4)
  - colonna gia impostata -> ok=True, evento=None, stato invariato

- **Metodo 14** `_reset_focus_riga_e_colonna` (2 test)
  - stato pre-esistente -> riga e colonna diventano None, cartella invariata
  - stato gia None -> nessun effetto collaterale

- **Metodo 15** `_reset_focus_cartella_riga_e_colonna` (2 test)
  - stato pre-esistente -> tutti e 3 i focus diventano None
  - stato gia None -> nessun effetto collaterale

- **Metodo 16** `imposta_focus_cartella_fallback` (2 test)
  - cartelle presenti -> focus impostato a 0
  - cartelle vuote -> nessun cambio di stato

### Fase F3 — Reclami Focus (test_helper_reclami_focus.py)

**Copertura**: Tutti i 3 metodi di ReclamiFocusMixin
**Stima test**: 15-20

Dettaglio test per metodo:

- **Metodo 1** `_esito_prerequisiti_reclamo_cartella` (3 test)
  - nessuna cartella -> propaga CARTELLE_NESSUNA_ASSEGNATA
  - focus cartella non impostato -> propaga FOCUS_CARTELLA_NON_IMPOSTATO
  - focus cartella valido -> ok=True, evento=None (helper silenzioso)

- **Metodo 2** `_esito_prerequisiti_reclamo_riga` (5 test)
  - nessuna cartella -> propaga errore cartella
  - focus cartella non impostato -> propaga errore cartella
  - focus cartella ok, riga None -> FOCUS_RIGA_NON_IMPOSTATA
  - focus cartella ok, riga fuori range -> FOCUS_RIGA_FUORI_RANGE
  - focus cartella ok, riga valida -> ok=True

- **Metodo 3** `_esito_crea_evento_reclamo_da_focus` (8 test)
  - Nota: prima di testare, BUG-3 (numero_turno mancante) deve essere corretto
  - tipo=tombola, prerequisiti falliti -> ok=False
  - tipo=tombola, prerequisiti ok -> ok=True, evento=EventoReclamoVittoria con indice_riga=None
  - tipo=ambo, prerequisiti riga falliti -> ok=False
  - tipo=ambo, prerequisiti ok -> ok=True, reclamo con tipo=ambo e indice_riga valorizzato
  - tipo=terno, prerequisiti ok -> ok=True, verifica coerenza tipo
  - tipo=quaterna, prerequisiti ok -> verifica struttura reclamo
  - tipo=cinquina, prerequisiti ok -> verifica struttura reclamo
  - verifica fase="ANTE_TURNO" su tutti gli eventi generati

---

## 8. Riepilogo fasi e stima

| Fase | File test | Metodi coperti | Test stimati |
|------|-----------|----------------|--------------|
| F1 | test_helper_focus_cartella_riga.py | 1-7 (cartella + riga) | 28-35 |
| F2 | test_helper_focus_colonna_nav_reset.py | 8-16 (colonna + nav + reset) | 22-28 |
| F3 | test_helper_reclami_focus.py | 1-3 (reclami) | 15-20 |
| **Totale** | **3 file** | **19 metodi** | **65-83** |

---

## 9. Dipendenze tra fasi

```
F1 (cartella + riga) -- indipendente, punto di partenza obbligatorio
 |
 +-- F2 (colonna + nav + reset) -- puo essere sviluppata in parallelo a F3
 |
 +-- F3 (reclami) -- dipende da F1 per lo stub, puo essere parallela a F2
```

Ordine consigliato: F1 -> F2 e F3 (parallele o in sequenza)

---

## 10. Prerequisiti e blocchi

### Prima di iniziare l'implementazione dei test

1. **Decidere se correggere i BUG-1, BUG-2, BUG-3** prima di scrivere i test, oppure scrivere i test che documentano il comportamento atteso post-fix (test-first approach)
2. **Valutare** se `_esito_crea_evento_reclamo_da_focus` (BUG-4, dead code) debba essere mantenuto, rimosso o integrato in `annuncia_vittoria`
3. **Stub Cartella**: servira uno stub minimale con attributi `righe` (default 3) e `colonne` (default 9), senza necessita di MagicMock

### Vincoli tecnici

- Solo unittest (zero pytest), coerente con le convenzioni del progetto
- Nessun MagicMock necessario: gli stub con attributi semplici sono sufficienti
- I file test andranno in `tests/unit/`

---

## 11. Raccomandazioni

1. **Priorita alta**: Correggere BUG-1 e BUG-2 prima della fase F1, perche impattano metodo 7 che e usato in produzione
2. **Priorita media**: Decidere il destino di ReclamiFocusMixin (BUG-3/BUG-4) prima della fase F3
3. **Pattern stub**: Definire lo stub host class nella fase F1 e riutilizzarlo (eventualmente estraendolo in un modulo condiviso se necessario)
4. **Simmetria riga/colonna**: I metodi colonna (8-10) sono simmetrici ai metodi riga (5-7). I test possono seguire la stessa struttura con adattamenti minimi
