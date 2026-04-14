---
type: design
titolo: Lettura NVDA stato premi (ultima vittoria e prossimo premio)
feature: lettura_nvda_stato_premi
versione: 1.2.0
data_creazione: 2026-04-12
agent: Agent-Design
status: REVIEWED
---

# DESIGN — Lettura NVDA stato premi

## Idea in 3 righe

Aggiungere due tasti rapidi Categoria C (`Ctrl+G` e `Ctrl+I`) che
permettono al giocatore non vedente di rileggere con NVDA l'ultima
vittoria assegnata (tipo + nome vincitore) e quale premio è il prossimo
nella sequenza della tombola, senza interrompere il flusso di gioco.

---

## Obiettivo

Rendere accessibili via tastiera le informazioni sui premi assegnati
durante una partita, attualmente visibili solo nella HeaderBar visiva
non raggiungibile da screen reader. Il giocatore deve poter:

1. Sapere quale vittoria è stata assegnata per ultima e a chi
   (`Ctrl+G` — stato sintetico).
2. Rileggere la lista completa dei premi assegnati con i vincitori
   (`Ctrl+I` — dettaglio completo).

Questo consente decisioni informate sul momento di reclamare un premio
(F1-F5) senza dipendere da informazioni visive.

---

## Componenti coinvolti

| Componente | File | Ruolo |
|---|---|---|
| FinestraGioco | `bingo_game/ui/finestra_gioco.py` | Binding tasti, dispatch |
| Partita | `bingo_game/partita.py` | Sorgente dati premi |
| ComandiGiocatoreUmano | `bingo_game/comandi_partita.py` | Incapsula logica lettura stato |
| WxRenderer | `bingo_game/ui/renderers/renderer_wx.py` | Vocalizzazione NVDA |
| CodiciOutputUiUmani | `bingo_game/events/codici_output_ui_umani.py` | Template testi vocalizzati |
| EventiOutputUiUmani | `bingo_game/events/eventi_output_ui_umani.py` | Dataclass evento (opzionale) |

---

## Dipendenze

### Dati di dominio già disponibili

- `Partita.premi_tipo_chiusi: set` — tipi di premio già chiusi
  (es. `{"ambo", "terno"}`). Definito in `partita.py` riga 204.
- `Partita.premi_gia_assegnati: set` — chiavi assegnazione
  (es. `"cartella_0_riga_1_ambo"`). Riga 203. Non contiene nomi vincitori.

### Dato mancante — da aggiungere al dominio

`Partita.ultimo_premio_evento: Optional[Dict]` — dizionario dell'ultimo
evento premio restituito da `verifica_premi()`. Struttura:

```python
{
    "giocatore": str,        # nome del vincitore
    "id_giocatore": str,
    "cartella": int,
    "premio": str,           # "ambo" | "terno" | ... | "tombola"
    "riga": Optional[int]
}
```

Inizializzato a `None` in `__init__`, aggiornato in `verifica_premi()`
alla riga 652 al termine del ciclo di assegnazione (ultima iterazione).

### Sequenza premi fissi

Già disponibile in `finestra_gioco.py` riga 75 come `_TIPI_VITTORIA`:

```python
_TIPI_VITTORIA = ["ambo", "terno", "quaterna", "cinquina", "tombola"]
```

Usata per calcolare il prossimo premio non ancora chiuso.

---

## Rischi

### R1 — Conflitto NVDA con Ctrl+I

Ctrl+I potrebbe collidere con "leggi formato" in alcuni contesti NVDA.
**Mitigazione**: test empirico prima del rilascio. Alternative pronte:
`Ctrl+W` oppure `Ctrl+Y` (entrambi liberi nel frame).

### R2 — Stato premi al primo turno

`ultimo_premio_evento` è `None` prima che venga assegnato qualsiasi
premio. Il handler deve gestire esplicitamente questo caso e vocalizzare
"Nessun premio ancora assegnato." invece di sollevare eccezione.

### R3 — Partita terminata

Se `premi_tipo_chiusi` contiene tutti e 5 i tipi, il "prossimo premio"
non esiste. Il testo prodotto deve essere "Partita terminata, tutti i
premi assegnati." e non un indice out-of-range.

### R4 — Co-vittoria

`verifica_premi()` può restituire più eventi nello stesso turno. Il
valore di `ultimo_premio_evento` viene sovrascritto per ogni vincitore
del turno, quindi conserva solo l'ultimo della lista. Questo è il
comportamento atteso: la feature è "ultima vittoria registrata", non
"tutte le vittorie del turno" (quel caso è coperto da `Ctrl+I`).

---

## Vincoli accessibilità NVDA

- I tasti `Ctrl+G` e `Ctrl+I` devono essere intercettati in
  `EVT_CHAR_HOOK` (Categoria C), non in `EVT_KEY_DOWN`, per garantire
  comportamento coerente con NVDA attivo.
- Il testo vocalizzato deve essere consegnato tramite
  `renderer.mostra_messaggio_sistema(testo)` che usa `wx.lib.nvda` o
  equivalente per output screen reader sincrono.
- Non usare popup, tooltip o finestre modale — interferiscono con il
  focus NVDA.
- Il testo deve essere breve (max 2 frasi) per non sovraccaricare la
  coda vocale. Il tasto `Ctrl+I` produce un elenco multi-riga; ogni
  premio va su una riga separata nel testo passato al renderer.
- Mantenere coerenza con il pattern esistente di `Ctrl+T`, `Ctrl+L`,
  `Ctrl+R`: risposta immediata, nessun side effect sul gioco.

---

## Decisioni architetturali

### D1 — Opzione C per il vincitore dell'ultimo premio

Scelta: **Opzione C** (attributo `ultimo_premio_evento` su `Partita`).

Motivazione: il dato necessario (nome vincitore) transita già in
`verifica_premi()` ma viene perso dopo. Memorizzarlo costa 1 attributo
e 1 riga di aggiornamento nel dominio. Alternativa B (log renderer)
crea accoppiamento presentazione-dominio non accettabile in Clean
Architecture.

### D2 — Metodo in ComandiGiocatoreUmano

La logica di calcolo prossimo premio e costruzione testo appartiene al
layer application (`comandi_partita.py`), non alla presentazione.
`FinestraGioco` chiama `comando.stato_premi()` e `comando.dettaglio_premi()`;
i metodi restituiscono testo pronto per la vocalizzazione.

Motivazione: separa la logica di business dalla UI; testabile
indipendentemente dal contesto wx.

### D3 — Due tasti distinti (non toggle)

Scelta: **due tasti separati** invece di un singolo tasto con doppia
pressione temporizzata.

Motivazione: la variante temporizzata aggiunge complessità gestionale
(stato interno, timer) non giustificata per questa feature. I tasti
rapidi NVDA devono essere prevedibili.

### D4 — Codici template centralizzati

Aggiungere i codici stringa in `codici_output_ui_umani.py` per garantire
che i testi vocalizzati siano internazionalizzabili e testabili. I
template devono includere `{ultimo_premio}`, `{vincitore}`,
`{prossimo_premio}` come placeholder.

---

## Struttura dati

### Modifica a Partita (dominio — minima)

```python
# In __init__:
self.ultimo_premio_evento: Optional[Dict[str, Any]] = None

# In verifica_premi(), dopo nuovi_eventi.append(...):
if nuovi_eventi:
    self.ultimo_premio_evento = nuovi_eventi[-1]
```

### Nuovi metodi in ComandiGiocatoreUmano (application)

```python
_SEQUENZA_PREMI: list[str] = ["ambo", "terno", "quaterna", "cinquina", "tombola"]

def stato_premi(self) -> str:
    """
    Restituisce testo sintetico: ultimo premio assegnato + prossimo.
    Gestisce: nessun premio ancora, partita terminata.
    """
    ...

def dettaglio_premi(self) -> str:
    """
    Restituisce elenco completo dei premi assegnati con vincitori.
    Fonte: self._partita.premi_gia_assegnati (set chiavi) + lookup
    vincitori tramite giocatori registrati.
    """
    ...
```

### Nuovi codici in CodiciOutputUiUmani

```python
UMANI_STATO_PREMI_SINTETICO = (
    "Ultimo premio: {ultimo_premio} vinto da {vincitore}. "
    "Prossimo: {prossimo_premio}."
)
UMANI_STATO_PREMI_NESSUNO = "Nessun premio ancora assegnato. Prossimo: {prossimo_premio}."
UMANI_STATO_PREMI_TUTTI = "Tutti i premi sono stati assegnati."
UMANI_DETTAGLIO_PREMI_HEADER = "Premi assegnati in questa partita:"
UMANI_DETTAGLIO_PREMI_VOCE = "{premio} - vinto da {vincitore} (cartella {cartella})"
```

---

## Interfaccia utente (tasti rapidi)

### Ctrl+G — Stato premi sintetico (Categoria C)

- **Trigger**: `EVT_CHAR_HOOK`, `key == ord("G")` con `evt.ControlDown()`
- **Output**: una riga vocalizzata, es.:
  - "Ultimo premio: ambo vinto da Bot 1. Prossimo: terno."
  - "Nessun premio ancora assegnato. Prossimo: ambo."
  - "Tutti i premi sono stati assegnati."
- **Side effect**: nessuno sul gioco

### Ctrl+I — Dettaglio premi completo (Categoria C)

- **Trigger**: `EVT_CHAR_HOOK`, `key == ord("I")` con `evt.ControlDown()`
- **Output**: elenco multi-riga vocalizzato, es.:
  ```
  Premi assegnati in questa partita:
  ambo - vinto da Bot 2 (cartella 1)
  terno - vinto da Giocatore (cartella 0)
  ```
- **Fallback se nessun premio**: "Nessun premio ancora assegnato."
- **Side effect**: nessuno sul gioco

### Aggiornamento tabella tasti (docs/API.md)

La sezione "Categoria C" dovrà includere le due nuove voci dopo
l'implementazione.

---

## Sequenza di chiamata

### Ctrl+G — Flusso completo

```
[Utente pressa Ctrl+G]
        |
FinestraGioco._on_char_hook()
        |
        +-- verifica: partita in corso?
        |   NO -> evt.Skip(), nessuna azione
        |   SI ->
        |
ComandiGiocatoreUmano.stato_premi()
        |
        +-- legge self._partita.ultimo_premio_evento
        |   None -> "Nessun premio ancora assegnato. Prossimo: ambo."
        |   Dict -> formatta con template UMANI_STATO_PREMI_SINTETICO
        |
        +-- calcola prossimo_premio:
            for p in _SEQUENZA_PREMI:
                if p not in self._partita.premi_tipo_chiusi:
                    return p
            return "tutti assegnati"
        |
WxRenderer.mostra_messaggio_sistema(testo)
        |
[NVDA vocalizza il testo]
```

### Ctrl+I — Flusso completo

```
[Utente pressa Ctrl+I]
        |
FinestraGioco._on_char_hook()
        |
        +-- verifica: partita in corso?
        |   NO -> evt.Skip()
        |   SI ->
        |
ComandiGiocatoreUmano.dettaglio_premi()
        |
        +-- se premi_gia_assegnati vuoto:
        |       return "Nessun premio ancora assegnato."
        |
        +-- per ogni giocatore in partita.giocatori:
        |       per ogni cartella in giocatore.get_cartelle():
        |           per ogni tipo in _SEQUENZA_PREMI:
        |               chiavi = {f"cartella_{c.indice}_*_{tipo}", ...}
        |               se chiave in premi_gia_assegnati:
        |                   aggiungi voce all'elenco
        |
        +-- return header + "\n".join(voci)
        |
WxRenderer.mostra_messaggio_sistema(testo)
        |
[NVDA vocalizza il testo]
```

### Aggiornamento ultimo_premio_evento (dominio)

```
Partita.verifica_premi()
        |
        +-- ciclo assegnazione candidati -> nuovi_eventi
        |
        [dopo il ciclo, se nuovi_eventi non vuoto]
        |
        self.ultimo_premio_evento = nuovi_eventi[-1]
        |
        return nuovi_eventi
```

---

## Riferimenti

- Report analisi:
  `docs/4 - reports/REPORT_ANALISI_lettura_nvda_stato_premi_2026-04-12.md`
- Codice sorgente chiave:
  - `bingo_game/partita.py` — righe 203-204 (attributi premi), 576-662 (verifica_premi)
  - `bingo_game/ui/finestra_gioco.py` — riga 75 (_TIPI_VITTORIA), righe 33-38 (binding C)
  - `bingo_game/events/codici_output_ui_umani.py` — template esistenti
