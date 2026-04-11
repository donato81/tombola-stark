# REPORT — Analisi di fattibilita: Pausa del gioco

**Data**: 2026-04-11
**Autore**: Agent-Analyze
**Stato**: DRAFT — solo analisi, nessuna modifica al codice
**Obiettivo**: Analizzare il codebase per individuare le modalita migliori
di implementare una funzionalita di pausa del gioco, attivabile su
richiesta del giocatore umano.

---

## Sommario esecutivo

La funzionalita di pausa e fattibile e si integra in modo naturale
nell'architettura esistente. Il ciclo di gioco e gia strutturato a fasi
con timer espliciti, il che rende l'inserimento di uno stato di pausa
un'estensione logica del sistema.

**Fattibilita**: ALTA — nessuna ristrutturazione architetturale necessaria.
**Rischio**: BASSO — le modifiche sono localizzate nel layer di presentazione
e nel controller, senza toccare la logica di dominio.
**Complessita stimata**: MEDIA — richiede coordinamento tra timer UI, stati
della fase turno e accessibilita vocale.

---

## 1. Contesto e motivazione

Durante una partita di tombola, il giocatore potrebbe aver bisogno di
allontanarsi dal computer per un imprevisto. Attualmente non esiste un
meccanismo per sospendere la partita: i timer della finestra d'azione
continuano a scorrere e il turno si risolve automaticamente con timeout.

Uno stato di pausa permetterebbe di:

- Congelare tutti i timer attivi (finestra d'azione, pausa tra turni)
- Impedire l'avanzamento automatico del gioco
- Mantenere integro lo stato della partita
- Riprendere esattamente dal punto in cui si era interrotta

---

## 2. Analisi dell'architettura corrente

### 2.1 Macchina a stati esistente

Il gioco utilizza due livelli di stato paralleli:

**Livello dominio** (`Partita.stato_partita`):
- `"non_iniziata"` -> `"in_corso"` -> `"terminata"`

**Livello dominio (sotto-fase turno)** (`Partita.fase_turno_corrente`):
- `"attesa_estrazione"` -> `"attesa_reclami"` -> (reset ad attesa_estrazione)

**Livello UI** (`FinestraGioco._fase_turno_ui`):
- `"attesa_estrazione"` -> `"attesa_reclami"` -> `"pausa_turno"` -> (loop)

### 2.2 Timer attivi durante la partita

Sono presenti due timer gestiti dalla FinestraGioco:

- `_timer_azione` (wx.Timer): scatta ogni 500 ms durante la fase
  `"attesa_reclami"`, gestisce avvisi vocali progressivi (60%, 80%, 95%) e
  il timeout della finestra d'azione.
- `_timer_pausa` (wx.Timer, ONE_SHOT): scatta dopo `durata_pausa_ms`
  durante la fase `"pausa_turno"`, avvia automaticamente il turno successivo.

Entrambi sono gestiti con mutua esclusione tramite `_ferma_tutti_i_timer()`.

### 2.3 Punti di ingresso azione utente

L'utente interagisce con Ctrl+Enter o il pulsante principale per:

- `"attesa_estrazione"`: avviare estrazione numero
- `"attesa_reclami"`: dichiarare fine turno
- `"pausa_turno"`: pulsante disabilitato, stato non interattivo

### 2.4 Vincolo accessibilita

Ogni cambio di stato deve essere annunciato vocalmente tramite il renderer
(vocalizzatore AO2) per compatibilita NVDA. Il focus tastiera deve restare
prevedibile.

---

## 3. Proposte di implementazione

### 3.1 Opzione A — Pausa a livello UI (RACCOMANDATA)

**Principio**: La pausa e un concetto puramente di presentazione. Il dominio
non conosce il concetto di pausa; i timer e la progressione automatica
vivono esclusivamente nella FinestraGioco.

**Strategia**:

1. Aggiungere uno stato `"in_pausa"` alla macchina a stati UI di
   FinestraGioco (`_fase_turno_ui`)
2. Memorizzare lo stato da cui si e entrati in pausa
   (es. `_fase_pre_pausa`) per poter ripristinare correttamente
3. Alla pausa: fermare tutti i timer, salvare i millisecondi residui
4. Alla ripresa: riavviare i timer dal tempo residuo salvato
5. Annuncio vocale di ingresso e uscita dalla pausa

**Vantaggi**:
- Rispetta la Clean Architecture: zero modifiche al dominio
- I bot non ricevono nuove istruzioni, rimangono nel loro stato corrente
- La logica e interamente contenuta in `finestra_gioco.py`
- Il controller e il dominio non hanno bisogno di sapere che esiste la pausa

**Svantaggi**:
- Se in futuro il gioco diventa multiplayer, la pausa solo lato UI non
  bastera (ma per ora il design e single-player + bot locali)

**File che verrebbero modificati**:
- `bingo_game/ui/finestra_gioco.py` — logica pausa, binding tasto, gestione timer
- `bingo_game/ui/renderers/renderer_wx.py` — metodi di annuncio pausa
- `bingo_game/ui/renderers/base_renderer.py` — contratto astratto nuovo metodo
- `bingo_game/ui/locales/it.py` — testi localizzati per messaggi pausa
- `bingo_game/events/codici_eventi.py` — costanti evento pausa (opzionale)

### 3.2 Opzione B — Pausa a livello dominio (NON raccomandata per ora)

**Principio**: Aggiungere `"in_pausa"` come stato valido di
`Partita.stato_partita`.

**Strategia**:

1. Estendere la macchina a stati di Partita: `in_corso` -> `in_pausa` -> `in_corso`
2. Aggiungere metodi `metti_in_pausa()` e `riprendi_partita()` in Partita
3. Proteggere i metodi di estrazione e verifica premi dal nuovo stato
4. Il controller espone wrapper sicuri per pausa/ripresa

**Vantaggi**:
- Modello di stato esplicito e testabile a livello dominio
- Pronto per una futura evoluzione multiplayer o persistenza

**Svantaggi**:
- Modifica invasiva al dominio per un comportamento che e puramente UI
- Richiede aggiornamento di tutti i guard clause che controllano
  `stato_partita != "in_corso"` in Partita
- Viola il principio: la pausa non e una regola di business della tombola

### 3.3 Opzione C — Approccio ibrido (pausa UI + flag dominio read-only)

**Principio**: La pausa resta a livello UI, ma viene scritto un flag
booleano leggero nel dominio per scopi di query.

**Strategia**:

1. Aggiungere `Partita.is_in_pausa: bool = False` (solo attributo, no logica)
2. La UI imposta il flag tramite il controller quando entra in pausa
3. I metodi del dominio NON controllano il flag (non cambia la logica)
4. Utile per `get_stato_sintetico()` e per il report finale

**Vantaggi**:
- Il dominio puo riportare lo stato di pausa senza governarlo
- Transizione futura piu semplice verso Opzione B

**Svantaggi**:
- Introduce accoppiamento leggero tra UI e dominio
- Il flag potrebbe diventare fonte di bug se non sincronizzato

---

## 4. Raccomandazione

**Opzione A (Pausa a livello UI)** e la scelta raccomandata perche:

- Rispetta i confini architetturali esistenti
- La complessita e contenuta nel layer di presentazione
- Non regredisce i test di dominio esistenti
- E coerente con il design attuale dove tutti i timer sono gestiti dalla UI

---

## 5. Dettaglio tecnico dell'Opzione A

### 5.1 Interazione utente (proposta binding)

La pausa deve essere attivabile da un tasto rapido con le seguenti proprieta:

- Funzionare in qualsiasi fase del turno (estrazione, reclami, pausa turno)
- Non confliggere con binding esistenti
- Essere raggiungibile senza combinazioni complesse
- Il tasto agisce come toggle: una pressione pausa, la successiva riprende
- Un pulsante visibile nella UI per utenti non da tastiera e raggiungibile
  tramite Tab

**Candidati hotkey**:

- `P` (solo nel pannello griglia): semplice e intuitivo. Il tasto `P`
  non e attualmente usato nella Categoria A. Facile da memorizzare.
  Problematico: potrebbe confliggere con NVDA se non e sul pannello griglia.
- `Ctrl+P`: classico per "Pausa". Attualmente libero in FinestraGioco.
  Potenziale conflitto con NVDA: `Ctrl+P` non ha binding NVDA predefiniti
  noti, ma va verificato empiricamente.
- `Escape` (con doppia pressione): la prima Escape esce dalla griglia
  (gia usato), la seconda potrebbe mettere in pausa. Semantica confusa,
  non raccomandato.
- `F7`: successivo ai tasti funzione gia usati (F1-F6), nessun conflitto.
  Non intuitivo ma privo di rischi. Buon candidato secondario.

**Raccomandazione hotkey**: `Ctrl+P` come hotkey primaria (Categoria B,
intercettata a livello frame) + un pulsante "Pausa" nella UI.
Se il test empirico NVDA mostra conflitto, ripiegare su `F7`.

### 5.2 Nuovi attributi in FinestraGioco

```python
# Stato pausa
self._in_pausa: bool = False
self._fase_pre_pausa: str = ""  # fase UI prima della pausa
self._ms_residui_azione: int = 0  # tempo residuo timer azione
self._ms_residui_pausa: int = 0   # tempo residuo timer pausa turno
```

### 5.3 Metodi da aggiungere in FinestraGioco

```python
def _toggle_pausa(self) -> None:
    """Toggle tra stato di pausa e stato precedente."""
    if self._in_pausa:
        self._riprendi_gioco()
    else:
        self._metti_in_pausa()

def _metti_in_pausa(self) -> None:
    """Congela il gioco: ferma timer, salva stato residuo."""
    if self._comandi_sistema.is_terminata(self._partita):
        return
    self._in_pausa = True
    self._fase_pre_pausa = self._fase_turno_ui
    # Calcola tempo residuo timer azione
    if self._timer_azione is not None:
        self._ms_residui_azione = max(
            0, self._durata_finestra_corrente_ms - self._ms_trascorsi_azione
        )
    # Calcola tempo residuo timer pausa turno
    # (nota: per il ONE_SHOT serve tracciare il tempo trascorso)
    self._ferma_tutti_i_timer()
    self._fase_turno_ui = "in_pausa"
    self._aggiorna_stato_pulsante()
    self._renderer.annuncia_pausa("Gioco in pausa.")

def _riprendi_gioco(self) -> None:
    """Ripristina il gioco dalla pausa."""
    self._in_pausa = False
    self._fase_turno_ui = self._fase_pre_pausa
    self._aggiorna_stato_pulsante()
    # Riavvia timer dal tempo residuo
    if self._fase_pre_pausa == "attesa_reclami" and self._ms_residui_azione > 0:
        self._avvia_timer_azione(self._ms_residui_azione)
    elif self._fase_pre_pausa == "pausa_turno" and self._ms_residui_pausa > 0:
        self._avvia_pausa_turno(self._ms_residui_pausa)
    self._renderer.annuncia_pausa("Gioco ripreso.")
```

### 5.4 Guardia sulla progressione automatica

Tutti i metodi che avanzano il gioco devono controllare `_in_pausa`:

- `_on_pulsante_principale()`: aggiungere guard `if self._in_pausa: return`
- `_on_tick_azione()`: aggiungere guard `if self._in_pausa: return`
- `_on_tick_pausa()`: aggiungere guard `if self._in_pausa: return`
- `_dichiara_fine_bot()`: i bot CallLater gia schedulati devono verificare
  se il gioco e in pausa e, se si, rischedulare o ignorare

### 5.5 Gestione del pulsante durante la pausa

```python
# In aggiorna_stato_pulsante, aggiungere caso:
if fase == "in_pausa":
    label = "Gioco in pausa — premi Ctrl+P per riprendere"
    self._btn_principale.SetLabel(label)
    self._btn_principale.Disable()
```

### 5.6 Impatto sul renderer

Nel renderer vanno aggiunti:

- `BaseRenderer.annuncia_pausa(testo: str)` — contratto astratto
- `WxRenderer.annuncia_pausa(testo: str)` — aggiorna widget + vocalizza
- Costante evento `PAUSA_ATTIVATA` e `PAUSA_DISATTIVATA` in codici_eventi.py
- Testi localizzati in `it.py`

### 5.7 Gestione timer pausa turno (ONE_SHOT)

Il timer pausa turno (`_timer_pausa`) e un ONE_SHOT e non ha un tick
ricorrente. Per calcolare il tempo residuo servira:

- Salvare il timestamp di avvio della pausa turno (`_inizio_pausa_turno_ms`)
- Calcolare il residuo come: `durata_ms - (now - inizio)`
- Usare `wx.GetApp().GetTopWindow().GetHandle()` o `wx.GetLocalTimeMillis()`
  per ottenere il timestamp corrente (oppure `time.monotonic()`)

Alternativa: convertire anche il timer pausa turno in un timer tick
ricorrente (come gia fatto per il timer azione), cosi il residuo e
sempre calcolabile come `durata - ms_trascorsi`.

---

## 6. Riepilogo file coinvolti dall'Opzione A

| File | Tipo modifica | Complessita |
|------|---------------|-------------|
| `bingo_game/ui/finestra_gioco.py` | Logica pausa, attributi, binding, guardie | MEDIA |
| `bingo_game/ui/renderers/base_renderer.py` | Nuovo metodo astratto `annuncia_pausa` | BASSA |
| `bingo_game/ui/renderers/renderer_wx.py` | Implementazione `annuncia_pausa` | BASSA |
| `bingo_game/ui/locales/it.py` | Nuovi testi pausa | BASSA |
| `bingo_game/events/codici_eventi.py` | Costanti `PAUSA_ATTIVATA`, `PAUSA_DISATTIVATA` | BASSA |
| `docs/API.md` | Documentare nuovi metodi | BASSA |
| `docs/ARCHITECTURE.md` | Aggiornare schema stati UI | BASSA |
| `tests/unit/` | Nuovi test per logica pausa | MEDIA |

---

## 7. Rischi e mitigazioni

### 7.1 Bot schedulati con CallLater durante la pausa

I bot sono schedulati con `wx.CallLater` con ritardi casuali. Se il gioco
viene messo in pausa dopo che il CallLater e stato registrato, il callback
scattera comunque. Mitigazione: il guard `if self._in_pausa: return` nel
metodo `_dichiara_fine_bot` impedisce progressione. Quando si riprende,
i bot che non hanno ancora dichiarato verranno gestiti dal timeout
residuo.

### 7.2 Pausa durante la fase "pausa_turno"

Se l'utente mette in pausa durante la pausa automatica tra turni,
il timer ONE_SHOT deve essere congelato e ripristinato. Questa e la
sottoparte piu delicata dell'implementazione (vedi sezione 5.7).

### 7.3 Conflitto hotkey con NVDA

`Ctrl+P` non ha un binding noto in NVDA, ma va verificato empiricamente.
Fallback: `F7`.

### 7.4 Pausa prima dell'avvio partita

Se il giocatore preme il tasto pausa prima del primo turno
(`_fase_turno_ui == "attesa_estrazione"` e nessun turno eseguito),
non ci sono timer attivi. La pausa sarebbe un no-op o potrebbe
semplicemente bloccare il pulsante "Inizia partita". Raccomandazione:
consentire la pausa solo se almeno un turno e stato eseguito.

---

## 8. Risposte dell'utente alle domande aperte

**Registrate il 2026-04-11 — fonte: utente.**

1. **Timer residuo**: alla ripresa i timer ripartono dal tempo
   residuo precedente, non dal tempo pieno.
2. **Hotkey**: `Ctrl+P` confermato come hotkey primaria.
3. **Pulsante visibile**: si, pulsante "Pausa" visibile nella UI
   e raggiungibile con Tab.
4. **Pausa prima del primo turno**: la pausa e attiva solo durante
   la partita attiva (almeno un numero gia estratto). Prima
   dell'avvio del primo turno la pausa non e disponibile.
5. **Feedback vocale alla ripresa**: annuncio completo dello stato
   alla ripresa: "Gioco ripreso. Fase: <fase>.
   Tempo rimanente: <N> secondi." (se timer attivo).

---

## 9. Prossimi passi

Una volta validato questo report:

1. Agent-Design: crea DESIGN_pausa_gioco.md con le scelte confermate
2. Agent-Plan: crea PLAN_pausa_gioco.md con le fasi di implementazione
3. Agent-Code / Agent-CodeUI: implementazione incrementale
4. Agent-Validate: test copertura pausa/ripresa
5. Agent-Docs: aggiornamento API.md e ARCHITECTURE.md
