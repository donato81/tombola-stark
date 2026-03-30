# Report: Ordine di sviluppo test — bingo_game/events/

**Data**: 2026-03-30  
**Agente**: Agent-Analyze  
**Ambito**: analisi dei file `bingo_game/events/` per definire l'ordine di sviluppo dei test mancanti  
**Stato**: DRAFT

---

## 1. Inventario file analizzati

La cartella `bingo_game/events/` contiene 12 file (escluso `__init__.py` vuoto):

| File | Natura | Dipendenze progetto | Complessità testabile |
|------|--------|--------------------|-----------------------|
| `codici_configurazione.py` | 9 costanti stringa (`str`) | nessuna | bassa |
| `codici_controller.py` | 4 costanti stringa (`str`) | nessuna | bassa |
| `codici_errori.py` | `Literal` Union in 3 gruppi | solo `typing` | media |
| `codici_eventi.py` | 1 costante `Final` + `Literal` | solo `typing` | bassa |
| `codici_loop.py` | 8 costanti `Final` + `Literal` | solo `typing` | bassa |
| `codici_messaggi_sistema.py` | ~20 costanti `Final` + `Literal` | solo `typing` | bassa |
| `codici_output_ui_umani.py` | `Literal` con ~70 chiavi | solo `typing` | bassa |
| `eventi_ui.py` | 2 dataclass frozen | solo `typing` | media |
| `eventi_partita.py` | 4 dataclass frozen + factory methods | `codici_errori` | alta |
| `eventi.py` | `EsitoAzione` + `EventoAzione` Union | `codici_errori`, `eventi_ui`, `eventi_partita`, `eventi_output_ui_umani` | molto alta |
| `eventi_output_ui_umani.py` | 20 dataclass frozen + factory methods | `typing`, dipendenza duck-typed su `Cartella` | alta |

---

## 2. Analisi dei test esistenti — gap identificati

### Test attualmente presenti che toccano il modulo events

- `tests/unit/test_event_logging.py` — testa `GameLogger`, usa i nomi dei sub-logger come stringhe; non testa alcuna classe di `events/`.
- `tests/integration/test_event_coverage.py` — testa che il logging produca le righe attese a partire da una partita completa; non testa le strutture dati degli eventi.
- `tests/unit/test_imposta_focus_cartella_regression.py` — regression test su `GiocatoreUmano`, produce `EsitoAzione` come effetto collaterale, ma non ne verifica la struttura.
- `tests/test_giocatore_umano.py` — verifica comportamenti di `GiocatoreUmano`; usa `EsitoAzione.ok` e `EsitoAzione.errore`, ma non testa `__str__`, `__eq__`, `__contains__`.

### Gap rilevati

Nessun file di test testa direttamente:
- le costanti dei file `codici_*.py` (contratto di stabilità dei valori)
- `EsitoAzione` come unità isolata (logica `__str__` con numerosi branch `isinstance`, `__eq__`, `__contains__`)
- le dataclass di `eventi_ui.py`, `eventi_partita.py`, `eventi_output_ui_umani.py` come unità isolate

---

## 3. Grafo delle dipendenze

```
codici_configurazione   (livello 0)
codici_controller       (livello 0)
codici_errori           (livello 1, solo typing)
codici_eventi           (livello 1, solo typing)
codici_loop             (livello 1, solo typing)
codici_messaggi_sistema (livello 1, solo typing)
codici_output_ui_umani  (livello 1, solo typing)
eventi_ui               (livello 2, solo typing)
eventi_partita          (livello 3) → codici_errori
eventi.py               (livello 4) → codici_errori + eventi_ui + eventi_partita + eventi_output_ui_umani
eventi_output_ui_umani  (livello 3/4) → duck-type su oggetti Cartella nei factory methods
```

Il nodo con più dipendenze è `eventi.py`: per testare `EsitoAzione.__str__` sul percorso completo occorre che tutti gli altri moduli siano già verificati autonomamente.

---

## 4. Ordine di sviluppo proposto

### Gruppo A — Test di contratto sui codici (priorità: copertura rapida, bassa complessità)

**File da creare**: `tests/unit/test_codici_eventi.py`

Raggruppa in un unico file i test di contratto per tutti i file `codici_*.py`.  
Il costo è basso; il beneficio è alto: i codici sono usati come chiavi stringa nei renderer e negli eventi — un refuso non viene catturato da mypy se si confronta un `Literal` con un `Final` scritto male.

Scenari da coprire per ciascun modulo:
- Ogni costante `Final` esiste con il valore stringa esatto (es. `assert LOOP_TURNO_AVANZATO == "LOOP_TURNO_AVANZATO"`).
- Le costanti `Final` e i `Literal` sono coerenti (stesso insieme di valori).
- Il modulo è importabile senza errori.
- `Codici_Errori_Generici | Codici_Errori_Ui | Codici_Errori_Partita` coprono senza sovrapposizioni l'insieme atteso di codici.

**Moduli coperti**: `codici_configurazione`, `codici_controller`, `codici_errori`, `codici_eventi`, `codici_loop`, `codici_messaggi_sistema`, `codici_output_ui_umani`.

---

### Gruppo B — Test su eventi_ui (priorità: alta, complessità bassa)

**File da creare**: `tests/unit/test_eventi_ui.py`

`EventoFocusAutoImpostato` e `EventoFocusCartellaImpostato` hanno pochi campi ma sono usati in molti punti della logica di focus di `GiocatoreUmano`. Verificarli in isolamento stabilizza il contratto.

Scenari da coprire:
- `EventoFocusAutoImpostato`: costruzione con `tipo_focus="cartella"`, `indice=0`; immutabilità (`frozen=True`); verifica dei tipi accettati per `tipo_focus`.
- `EventoFocusCartellaImpostato`: costruzione; default `reset_riga_colonna=False`; costruzione con `reset_riga_colonna=True`; immutabilità.

**Nessuna dipendenza su altri moduli del progetto.**

---

### Gruppo C — Test su eventi_partita (priorità: alta, complessità media-alta)

**File da creare**: `tests/unit/test_eventi_partita.py`

I factory methods di `ReclamoVittoria`, `EventoReclamoVittoria`, `EventoEsitoReclamoVittoria` e `EventoFineTurno` incapsulano invarianti importanti (tombola senza riga, ambo con riga, fase ANTE_TURNO vs FINE_TURNO, ok/errore mai contemporaneamente valorizzati o entrambi nulli).

Scenari da coprire:

**ReclamoVittoria**:
- `tombola()`: `tipo="tombola"`, `indice_riga=None`
- `vittoria_di_riga()` con tutti i tipi (ambo, terno, quaterna, cinquina): `indice_riga` valorizzato
- immutabilità (`frozen=True`)

**EventoReclamoVittoria**:
- `ante_turno()`: `fase="ANTE_TURNO"`, campi presenti e corretti

**EventoEsitoReclamoVittoria**:
- `successo()`: `ok=True`, `errore=None`
- `fallimento()`: `ok=False`, `errore` valorizzato (es. `"VERIFICA_FALLITA"`)
- `successo()` con `indice_turno` e `numero_estratto` opzionali valorizzati
- `fallimento()` con parametri opzionali

**EventoFineTurno**:
- `crea()` senza reclamo: `reclamo_turno=None`
- `crea()` con reclamo: `reclamo_turno` è il `ReclamoVittoria` passato

---

### Gruppo D — Test su EsitoAzione (priorità: very alta, complessità molto alta)

**File da creare**: `tests/unit/test_esito_azione.py`

`EsitoAzione.__str__` contiene la logica di rendering di fallback più articolata del progetto: 10+ branch `isinstance`, 2 metodi magici aggiuntivi (`__eq__`, `__contains__`). È il file a più alto rischio di regressione silenziosa tra tutti quelli della cartella `events/`.

Scenari da coprire:

**Costruzione e invarianti**:
- `EsitoAzione.successo()`: `ok=True`, `errore=None`, `evento=None` (default)
- `EsitoAzione.successo(evento=...)`: `evento` valorizzato
- `EsitoAzione.fallimento("ERRORE_INTERNO")`: `ok=False`, `errore` valorizzato, `evento=None`

**`__str__` — ramo fallimento**:
- `CARTELLE_NESSUNA_ASSEGNATA` → testo atteso
- `FOCUS_CARTELLA_NON_IMPOSTATO` → testo atteso
- `NUMERO_NON_VALIDO` → testo atteso
- `NUMERO_TIPO_NON_VALIDO` → testo atteso
- `FOCUS_CARTELLA_FUORI_RANGE` → testo atteso
- codice non mappato → fallback `f"Errore: {errore}"`

**`__str__` — ramo successo, evento=None**:
- ritorna `"Ok"`

**`__str__` — ramo successo, evento=EventoFocusCartellaImpostato**:
- ritorna frase con `numero_cartella`

**`__str__` — ramo successo, evento=EventoFocusAutoImpostato**:
- ritorna frase con `tipo_focus` e `indice`

**`__str__` — ramo successo, evento=EventoSegnazioneNumero**:
- tutti e 4 gli esiti: `segnato`, `gia_segnato`, `non_presente`, `non_estratto`

**`__str__` — ramo successo, evento=EventoRicercaNumeroInCartelle**:
- esito `non_trovato`
- esito `trovato` con lista risultati (verifica multiriga)

**`__str__` — fallback generico**:
- evento non riconosciuto → `str(evento)`

**`__eq__` e `__contains__`**:
- confronto con stringa per errori `CARTELLE_NESSUNA_ASSEGNATA` e `FOCUS_CARTELLA_NON_IMPOSTATO` (ammettono forme alternative)
- `__contains__` su stringa presente/assente nel rendering

**Dipendenze**: tutti i moduli dei Gruppi A, B e C devono essere stabili prima di refactoring aggressivi su questo modulo.

---

### Gruppo E — Test su eventi_output_ui_umani (priorità: alta, complessità alta, suddivisione consigliata)

Il file contiene 20 classi. Si consiglia di suddividere i test in sotto-file tematici:

#### E1 — Cartella base e navigazione cartelle
**File**: `tests/unit/test_eventi_output_cartella.py`

Classi coperte:
- `EventoRiepilogoCartellaCorrente`: `crea_da_cartella()` — verifica conversione `0-based → 1-based`, ordinamento `numeri_non_segnati`, calcolo `mancanti`
- `EventoLimiteNavigazioneCartelle`: `limite_minimo()` (numero_cartella_corrente=1), `limite_massimo()` (numero_cartella_corrente=totale_cartelle)
- `EventoVisualizzaCartellaSemplice`: `crea_da_cartella()` — verifica conversione indice, immutabilità griglia
- `EventoVisualizzaCartellaAvanzata`: costruzione, campi presenti

#### E2 — Navigazione riga e colonna
**File**: `tests/unit/test_eventi_output_navigazione.py`

Classi coperte:
- `EventoNavigazioneRiga`: factory methods per i due esiti ("mostra", "limite")
- `EventoNavigazioneRigaAvanzata`: costruzione con `stato_riga` dict
- `EventoNavigazioneColonna`: factory methods per i due esiti
- `EventoNavigazioneColonnaAvanzata`: costruzione con `stato_colonna` dict
- `EventoVaiARigaAvanzata`: costruzione e campi
- `EventoVaiAColonnaAvanzata`: costruzione e campi

#### E3 — Tabellone e interrogazioni
**File**: `tests/unit/test_eventi_output_tabellone.py`

Classi coperte:
- `EventoVerificaNumeroEstratto`: esito `True`/`False`
- `EventoUltimoNumeroEstratto`: con e senza numero estratto
- `EventoUltimiNumeriEstratti`: lista vuota e lista con elementi
- `EventoRiepilogoTabellone`: campi estratti/totale
- `EventoListaNumeriEstratti`: struttura per decine

#### E4 — Segnazione e ricerca
**File**: `tests/unit/test_eventi_output_segnazione.py`

Classi coperte:
- `EventoSegnazioneNumero`: tutti e 4 gli esiti (`segnato`, `gia_segnato`, `non_presente`, `non_estratto`)
- `RisultatoRicercaNumeroInCartella`: costruzione, campi `numero_cartella` (1-based), `segnato`
- `EventoRicercaNumeroInCartelle`: esito `non_trovato`, esito `trovato` con lista risultati

#### E5 — Bulk (tutte le cartelle) e focus
**File**: `tests/unit/test_eventi_output_bulk_focus.py`

Classi coperte:
- `EventoVisualizzaTutteCartelleSemplice`: `crea_da_cartelle()` con oggetti Cartella mock
- `EventoVisualizzaTutteCartelleAvanzata`: `crea_da_cartelle()` con oggetti Cartella mock (sia `get_griglia_semplice` che `get_dati_visualizzazione_avanzata`)
- `EventoStatoFocusCorrente`: costruzione con tutte le combinazioni di focus presente/assente

**Nota tecnica sui factory con Cartella**: `crea_da_cartelle()` usa duck typing (`Sequence[object]`) e chiama `get_griglia_semplice()` e `get_dati_visualizzazione_avanzata()`. È consigliabile usare `unittest.mock.MagicMock` con `spec=Cartella` per isolare i test senza istanziare cartelle reali.

---

## 5. Riepilogo per priorità e sequenza di sviluppo

| Priorità | Gruppo | File di test da creare | Motivo |
|----------|--------|------------------------|--------|
| 1 | A | `test_codici_eventi.py` | Base stabile, costo basso, copertura rapida |
| 2 | B | `test_eventi_ui.py` | Dipendenza zero, fondamento per Gruppo D |
| 3 | C | `test_eventi_partita.py` | Factory con invarianti business critici |
| 4 | D | `test_esito_azione.py` | Logica `__str__` complessa, rischio regressione più alto |
| 5 | E1 | `test_eventi_output_cartella.py` | Classi più usate dai renderer |
| 6 | E4 | `test_eventi_output_segnazione.py` | Logica esito con 4 varianti |
| 7 | E2 | `test_eventi_output_navigazione.py` | 6 classi, factory simili tra loro |
| 8 | E3 | `test_eventi_output_tabellone.py` | Interrogazioni read-only, struttura semplice |
| 9 | E5 | `test_eventi_output_bulk_focus.py` | Richiede mock di Cartella, più lento da setup |

---

## 6. Marker e collocazione suggeriti

Tutti i test dei Gruppi A–E rientrano nella categoria `@pytest.mark.unit`:
- nessuna dipendenza da `wx`
- nessuna I/O su file
- nessun avvio di gioco

Collocazione: `tests/unit/` per tutti i file indicati.

Fixture condivise (da definire in `tests/unit/conftest.py` se non esiste già):
- `griglia_semplice_3x9()` — griglia di esempio per le classi di visualizzazione
- `cartella_mock()` — `MagicMock` con interfaccia minima di `Cartella`
- `reclamo_tombola()` — `ReclamoVittoria.tombola(indice_cartella=0)`
- `reclamo_ambo()` — `ReclamoVittoria.vittoria_di_riga(tipo="ambo", indice_cartella=0, indice_riga=0)`

---

## 7. Note finali

- I file `codici_*.py` non hanno logica di business: il valore del test su di essi è stabilità di contratto (nessun refuso nascosto) e documentazione eseguibile. Una singola suite di smoke test per tutti vale più che saltarli.
- `EsitoAzione.__str__` è il componente a più alto rischio: molti branch `isinstance` e doppio override `__eq__` + `__contains__` aumentano la probabilità di regressioni invisibili. È il test più urgente in termini di rischio.
- Gli eventi `eventi_output_ui_umani.py` sono tutti `frozen=True`: la suite può essere completamente deterministica senza setup/teardown complessi.
- I factory methods con duck typing su `Cartella` (`EventoVisualizzaTutteCartelleSemplice`, `EventoVisualizzaTutteCartelleAvanzata`) sono gli unici che richiedono mock; il resto è puro Python senza effetti collaterali.
