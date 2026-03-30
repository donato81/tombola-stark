# Analisi e Piano Test — helper_focus.py
Data: 30 marzo 2026
Analista: Agent-Analyze

---

## Panoramica del file

`helper_focus.py` contiene la classe `GestioneFocusMixin`: un blocco di metodi
di utilità che viene "innestato" nel giocatore umano tramite ereditarietà multipla.
Il file non può essere istanziato da solo: lavora sugli attributi che il giocatore
umano dichiara nel proprio costruttore (`cartelle`, `_indice_cartella_focus`,
`_indice_riga_focus`, `_indice_colonna_focus`).

Il file è diviso in 5 sezioni tematiche e 15 metodi + 1 metodo pubblico di fallback.

---

## Sezione 1 — Incongruenze trovate nei metodi

### Incongruenza 1 — Docstring del Metodo 13 non aggiornata dopo la correzione

**Metodo:** `_esito_inizializza_focus_colonna_se_manca`

Il docstring dichiara ancora il vecchio valore di partenza (0) in tre punti,
mentre il codice usa correttamente il valore 4 (già corretto durante i lavori
sui bug del giocatore umano):

| Dove | Testo errato nel docstring |
|------|---------------------------|
| Scelta del default | "Colonna 0 = prima colonna" |
| Ritorna | "evento=EventoFocusAutoImpostato(tipo_focus='colonna', indice=0)" |
| Note | "assegnando la colonna 0" |

Il codice è corretto, il docstring è rimasto indietro. Non causa problemi
funzionali, ma induce confusione a chi legge.

---

### Incongruenza 2 — Docstring del Metodo 11 contraddice il codice

**Metodo:** `_esito_pronto_per_navigazione`

Il docstring descrive questo metodo come se avesse l'auto-impostazione abilitata:

> "con auto-impostazione abilitata: se il giocatore ha cartelle ma non ha ancora
> un focus, il focus può essere impostato automaticamente sulla prima cartella"

Il codice invece chiama:
```
self._esito_focus_cartella_valido(auto_imposta=False)
```

Quindi l'auto-impostazione è DISABILITATA. Si tratta di una descrizione rimasta
da una versione precedente, poi invertita nel codice (come nota il commento interno:
"senza auto-impostazione per rispettare il comportamento legacy dei test").

Anche questa è solo una discrepanza documentale. Il comportamento del codice è
quello giusto (verificato dai test di navigazione: se non c'è cartella in focus,
il metodo blocca con errore anziché auto-impostare).

---

### Incongruenza 3 — `_esito_focus_colonna_valido` definito ma mai chiamato

**Metodo:** `_esito_focus_colonna_valido` (Metodo 10)

Il metodo esiste, compila senza errori, ma non viene mai chiamato da nessuna parte
nel codice di produzione. Il suo equivalente per la riga (`_esito_focus_riga_valido`)
viene invece chiamato regolarmente da `reclama_vittoria` in `giocatore_umano.py`.

Questo crea una asimmetria: la riga ha il suo controllo completo integrato
nel flusso di gioco, la colonna no. Non è un bug oggi perché non esistono ancora
comandi di gioco che richiedano una colonna esplicitamente selezionata per
funzionare (come invece accade per le vittorie di riga). Ma è un candidato
naturale da testare e documentare per il futuro.

---

## Sezione 2 — Copertura test attuale

### Stato: NESSUN file di test dedicato

Non esiste un file `test_helper_focus.py` nel progetto. I metodi del Mixin
sono testati solo in modo indiretto, come effetto collaterale dei test su
`GiocatoreUmano`.

### Mappa per metodo: cosa è coperto oggi

| N. | Metodo | Coperto indirettamente | Note |
|----|--------|------------------------|------|
| 1  | `_esito_ha_cartelle` | SÌ | Tutti i test che partono senza cartelle lo toccano |
| 2  | `_esito_focus_cartella_impostato` | SÌ parziale | Caso auto_imposta=True non testato isolato |
| 3  | `_esito_focus_cartella_in_range` | SÌ parziale | Il caso "fuori range" non è mai esercitato |
| 4  | `_esito_focus_cartella_valido` | SÌ | Usato ovunque, coperto per effetto collaterale |
| 5  | `_esito_focus_riga_impostata` | SÌ parziale | Solo attraverso `_esito_focus_riga_valido` |
| 6  | `_esito_focus_riga_in_range` | SÌ parziale | Solo attraverso `_esito_focus_riga_valido`, caso "fuori range" non esercitato |
| 7  | `_esito_focus_riga_valido` | SÌ | Chiamato da `reclama_vittoria`, path happy |
| 8  | `_esito_focus_colonna_impostata` | NO | Solo usato internamente da metodo 10 non chiamato |
| 9  | `_esito_focus_colonna_in_range` | NO | Solo usato internamente da metodo 10 non chiamato |
| 10 | `_esito_focus_colonna_valido` | NO | Mai chiamato in produzione |
| 11 | `_esito_pronto_per_navigazione` | SÌ | Tutti i test freccia lo toccano |
| 12 | `_esito_inizializza_focus_riga_se_manca` | SÌ | Test auto-inizializzazione nei metodi freccia |
| 13 | `_esito_inizializza_focus_colonna_se_manca` | SÌ | Test auto-inizializzazione nei metodi freccia |
| 14 | `_reset_focus_riga_e_colonna` | SÌ | Test regressione + cambio cartella |
| 15 | `_reset_focus_cartella_riga_e_colonna` | NO | Nessun test diretto né indiretto trovato |
| –  | `imposta_focus_cartella_fallback` | SÌ | Test dedicato in test_imposta_focus_cartella_regression.py |

**Metodi senza copertura verificabile: 8, 9, 10, 15**

---

## Sezione 3 — Come costruire i test

### Sfida: il Mixin non può essere istanziato da solo

`GestioneFocusMixin` non ha `__init__` e presuppone che la classe concreta
abbia già `self.cartelle`, `self._indice_cartella_focus`, ecc.

Esistono due approcci:

#### Approccio A — Usare GiocatoreUmano come veicolo (come fanno i test attuali)

```python
from bingo_game.players.giocatore_umano import GiocatoreUmano
from bingo_game.cartella import Cartella

giocatore = GiocatoreUmano("Test", id_giocatore=1)
cartella = Cartella()
giocatore.aggiungi_cartella(cartella)
```

Vantaggi: zero codice stub, usa oggetti reali, identico ai test esistenti.
Svantaggi: ogni test porta tutta la dipendenza di GiocatoreUmano;
se qualcosa nel giocatore cambia, i test del mixin rischiano di rompersi.

#### Approccio B — Creare uno stub minimale della classe concreta

```python
class StubFocus(GestioneFocusMixin):
    def __init__(self):
        self.cartelle = []
        self._indice_cartella_focus = None
        self._indice_riga_focus = None
        self._indice_colonna_focus = None
```

Vantaggi: test isolati, veloci, nessuna dipendenza verso GiocatoreUmano.
Svantaggi: lo stub non ha `aggiungi_cartella`, quindi si lavora manipolando
direttamente `self.cartelle.append(Cartella())` oppure aggiungendo il metodo
allo stub stesso.

**Raccomandazione: Approccio B per i metodi del Mixin puro, Approccio A
per i test di integrazione che verificano il comportamento end-to-end.**

---

## Sezione 4 — Piano test proposto per metodo

### Gruppo 1 — Metodi cartella (1–4) — Test già parzialmente coperti

Priorità bassa: la copertura indiretta è sufficiente per i percorsi normali.
Aggiungere solo i casi mancanti:

#### Metodo 3 — `_esito_focus_cartella_in_range`
Scenario scoperto: focus impostato a un indice che non esiste più (fuori range).
```
test_esito_focus_cartella_in_range_fuori_range → ok=False, errore=FOCUS_CARTELLA_FUORI_RANGE
test_esito_focus_cartella_in_range_indice_negativo → ok=False, errore=FOCUS_CARTELLA_FUORI_RANGE
```

#### Metodo 2 — `_esito_focus_cartella_impostato` con auto_imposta=False
Scenario scoperto: cartella presente ma focus None, senza auto-impostazione.
```
test_esito_focus_cartella_impostato_rigoroso_senza_focus → ok=False, errore=FOCUS_CARTELLA_NON_IMPOSTATO
```

---

### Gruppo 2 — Metodi riga (5–7) — Test parzialmente coperti

#### Metodo 5 — `_esito_focus_riga_impostata`
Scenario diretto mancante: cartella valida, riga None.
```
test_esito_focus_riga_impostata_riga_assente → ok=False, errore=FOCUS_RIGA_NON_IMPOSTATA
test_esito_focus_riga_impostata_cartella_assente → ok=False (propagato da cartella)
test_esito_focus_riga_impostata_ok → ok=True
```

#### Metodo 6 — `_esito_focus_riga_in_range`
Scenari diretti mancanti:
```
test_esito_focus_riga_in_range_fuori_range_superiore → ok=False, errore=FOCUS_RIGA_FUORI_RANGE
test_esito_focus_riga_in_range_indice_negativo → ok=False, errore=FOCUS_RIGA_FUORI_RANGE
test_esito_focus_riga_in_range_ok → ok=True
```

#### Metodo 7 — `_esito_focus_riga_valido`
Già coperto in parte. Aggiungere:
```
test_esito_focus_riga_valido_riga_fuori_range → ok=False, errore=FOCUS_RIGA_FUORI_RANGE
```

---

### Gruppo 3 — Metodi colonna (8–10) — NESSUNA copertura, priorità alta

Questi tre metodi sono del tutto scoperti. Seguono la stessa logica simmetrica
dei metodi riga (5–7), quindi i test si scrivono specularmente.

#### Metodo 8 — `_esito_focus_colonna_impostata`
```
test_esito_focus_colonna_impostata_colonna_assente → ok=False, errore=FOCUS_COLONNA_NON_IMPOSTATA
test_esito_focus_colonna_impostata_cartella_assente → ok=False (propagato da cartella)
test_esito_focus_colonna_impostata_ok → ok=True
```

#### Metodo 9 — `_esito_focus_colonna_in_range`
```
test_esito_focus_colonna_in_range_fuori_range_superiore → ok=False, errore=FOCUS_COLONNA_FUORI_RANGE
test_esito_focus_colonna_in_range_indice_negativo → ok=False, errore=FOCUS_COLONNA_FUORI_RANGE
test_esito_focus_colonna_in_range_ok → ok=True
```

#### Metodo 10 — `_esito_focus_colonna_valido`
```
test_esito_focus_colonna_valido_colonna_assente → ok=False
test_esito_focus_colonna_valido_colonna_fuori_range → ok=False, errore=FOCUS_COLONNA_FUORI_RANGE
test_esito_focus_colonna_valido_ok → ok=True
```

---

### Gruppo 4 — Metodi reset (14–15)

#### Metodo 14 — `_reset_focus_riga_e_colonna`
Già coperto indirettamente. Nessun test urgente da aggiungere.

#### Metodo 15 — `_reset_focus_cartella_riga_e_colonna`
Nessun test trovato. Aggiungere:
```
test_reset_focus_cartella_riga_e_colonna_azzera_tutto
  → dopo il reset: _indice_cartella_focus=None, _indice_riga_focus=None, _indice_colonna_focus=None
test_reset_focus_cartella_riga_e_colonna_da_stato_impostato
  → partendo da tutti e tre i focus impostati, verificare che tornino tutti None
```

---

## Sezione 5 — Struttura file test suggerita

```
tests/unit/test_helper_focus.py
```

Scheletro di riferimento:

```python
import unittest
from bingo_game.players.helper_focus import GestioneFocusMixin
from bingo_game.cartella import Cartella


class StubFocus(GestioneFocusMixin):
    """Stub minimale per testare GestioneFocusMixin in isolamento."""
    def __init__(self):
        self.cartelle = []
        self._indice_cartella_focus = None
        self._indice_riga_focus = None
        self._indice_colonna_focus = None


class TestGestioneFocusMixin(unittest.TestCase):

    def setUp(self):
        self.stub = StubFocus()
        self.cartella = Cartella()

    # --- Gruppo 1: cartella ---

    def test_esito_ha_cartelle_senza_cartelle(self):
        # ...

    # --- Gruppo 2: riga ---

    def test_esito_focus_riga_impostata_riga_assente(self):
        # ...

    # --- Gruppo 3: colonna ---

    def test_esito_focus_colonna_impostata_colonna_assente(self):
        # ...

    # --- Gruppo 4: reset ---

    def test_reset_focus_cartella_riga_e_colonna_azzera_tutto(self):
        # ...
```

---

## Sezione 6 — Ordine di esecuzione consigliato

Per costruire i test in modo sicuro e incrementale:

1. **Prima**: scrivere e far passare i test per i metodi 5, 6, 7 (riga)
   — sono simmetrici rispetto ai test di riga già esistenti in test_giocatore_umano.py,
   quindi facili da scrivere con confidenza.

2. **Poi**: replicare la struttura per i metodi 8, 9, 10 (colonna)
   — identica logica, porta la copertura a zero lacune sul Mixin.

3. **Infine**: aggiungere il test per il metodo 15 (reset completo)
   — semplice, nessuna dipendenza esterna.

4. **Separatamente**: correggere il docstring del metodo 13 e del metodo 11
   — non richiedono nuovi test, solo allineamento della documentazione al codice.

---

## Riepilogo esecutivo

| Priorità | Azione |
|----------|--------|
| ALTA | Scrivere test per metodi 8, 9, 10 (colonna: zero copertura) |
| ALTA | Scrivere test per metodi 5, 6, 7 (riga: copertura parziale) |
| MEDIA | Aggiungere test per metodo 15 (reset completo) |
| MEDIA | Aggiungere caso "fuori range" per metodo 3 |
| BASSA | Correggere docstring metodo 13 (valore 0 → 4 in tre punti) |
| BASSA | Correggere docstring metodo 11 (auto_imposta=True → False) |
| INFO | `_esito_focus_colonna_valido` non ha chiamanti in produzione: nessuna azione urgente, da monitorare |
