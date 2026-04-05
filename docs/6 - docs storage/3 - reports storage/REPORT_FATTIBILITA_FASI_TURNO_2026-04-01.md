# Report di Fattibilità — Nuovo Sistema a Fasi per il Ciclo di Turno

**Data:** 2026-04-01  
**Autore:** Agent-Analyze  
**Versione:** 1.0  
**Stato:** DRAFT  

---

## Premessa

Questo report risponde al quesito tecnico: è fattibile separare il ciclo di turno
attuale — oggi compresso in un unico blocco sincrono — in fasi distinte e sequenziali
visibili, collettive e coerenti con le regole reali della tombola?

Le otto domande di analisi vengono trattate una per una con riferimento diretto
al codice sorgente.

---

## Domanda 1 — Come funziona oggi il ciclo di turno?

Il ciclo di turno è interamente contenuto nel metodo `esegui_turno()`
in `bingo_game/partita.py` (riga 683). Si tratta di un blocco sequenziale
e indivisibile che esegue sei passi in un'unica chiamata:

1. **Estrazione** — `estrai_prossimo_numero()` aggiorna `ultimo_numero_estratto`
   e notifica tutti i giocatori via `aggiorna_con_numero()`.

2. **Reclami bot** — per ogni `GiocatoreAutomatico` viene chiamato
   `_valuta_potenziale_reclamo(premi_gia_assegnati, premi_tipo_chiusi)`.
   Se il bot trova un premio, imposta `reclamo_turno`.

3. **Verifica premi** — `verifica_premi()` scansiona tutti i giocatori
   che hanno `reclamo_turno != None`. Assegna i premi trovati
   e aggiorna i registri `premi_gia_assegnati` e `premi_tipo_chiusi`.

4. **Confronto bot** — per ogni bot che aveva un reclamo, si verifica
   se il reclamo corrisponde a un premio reale nei `premi_nuovi`.
   Produce la lista `reclami_bot`.

5. **Reset reclami** — `reset_reclamo_turno()` viene chiamato
   su tutti i giocatori (incluso l'umano).

6. **Tombola check** — `has_tombola()` decide se chiamare `termina_partita()`.

Il trigger esterno è `_on_pulsante_principale()` in
`bingo_game/ui/finestra_gioco.py`. Un singolo click delegato a
`esegui_turno_sicuro(partita)` in `bingo_game/game_controller.py`
scatena l'intera sequenza. Il numero estratto e gli eventuali premi
vengono annunciati insieme in `_annuncia_risultato_turno()`.

**Conclusione:** estrazione, segnazione, reclamo umano, reclami bot,
verifica e assegnazione sono tutti compressi in un istante opaco.
Dall'esterno il turno ha un solo punto di ingresso e un solo punto
di uscita. Le fasi interne non sono visibili né separabili.

---

## Domanda 2 — Esiste già un concetto di "fase di turno"?

No, non esiste come meccanismo di controllo.

`Partita.stato_partita` (stringa) tiene traccia dello stato della partita
(`"non_iniziata"`, `"in_corso"`, `"terminata"`), non della sotto-fase
del turno in corso.

Esiste però un'evidenza architetturale di valore: il tipo letterale
`Fase_Validazione_Reclamo` definito in
`bingo_game/events/eventi_partita.py` (riga 19):

```python
Fase_Validazione_Reclamo = Literal[
    "ANTE_TURNO",  # warning: il giocatore può ancora cambiare idea
    "FINE_TURNO",  # decisione definitiva della Partita dopo il passa turno
]
```

Questo tipo è usato nei dataclass `EventoReclamoVittoria` (fase = "ANTE_TURNO"
di default) e `EventoEsitoReclamoVittoria` (fase = "FINE_TURNO" di default).
La distinzione concettuale del ciclo in due momenti è quindi già presente
nel vocabolario del dominio eventi, ma non è collegata ad alcun meccanismo
di controllo del flusso in `Partita` o in `finestra_gioco.py`.

Il metodo `_passa_turno_core()` in `giocatore_base.py` (riga 288)
raccoglie il reclamo in un `EventoFineTurno` e resetta `reclamo_turno`.
È implementato ma **non viene mai chiamato** nel flusso attuale:
`esegui_turno()` resetta i reclami direttamente (passo 5), ignorando
questo metodo.

**Conclusione:** l'infrastruttura concettuale per le fasi esiste
nell'area eventi ma è inutilizzata. Il controllo di flusso
non la conosce.

---

## Domanda 3 — Quando reclamano i bot? Prima o dopo la chiusura del turno?

I bot reclamano **durante l'esecuzione del turno**, al passo 2 di
`esegui_turno()`, immediatamente dopo l'estrazione e prima che
`verifica_premi()` venga chiamata.

Il metodo `_valuta_potenziale_reclamo()` in
`bingo_game/players/giocatore_automatico.py` riceve uno snapshot
dei premi già assegnati (`premi_gia_assegnati`, `premi_tipo_chiusi`),
opera sulla propria cartella e restituisce un `ReclamoVittoria` o `None`.
Se il reclamo esiste, viene scritto su `giocatore.reclamo_turno`.

Questo significa che il reclamo bot avviene **nel medesimo stack call**
del turno umano. Non c'è una distinzione temporale reale fra "il bot
ha valutato" e "la Partita ha verificato": sono due righe consecutive
dello stesso metodo.

Il giocatore umano, al contrario, può impostare `reclamo_turno` solo
**prima** che venga premuto "Passa turno" (tramite F1-F5 in
`finestra_gioco.py`). Ma nel flusso corrente il tasto "Passa turno"
innesca anche l'estrazione: quindi il reclamo umano deve essere
dichiarato nel turno *precedente*, a numeri ancora sconosciuti,
oppure nel breve intervallo tra l'ascolto dell'annuncio e il prossimo
click — il che è praticamente impossibile con uno screen reader.

**Conclusione:** bot e umano non sono mai nella stessa finestra
temporale. Il bot valuta col numero già segnato; l'umano dovrebbe
reclamare prima di sentire il numero estratto. Questa asimmetria
è il problema principale che il sistema a fasi vuole risolvere.

---

## Domanda 4 — La raccolta dei reclami è collettiva o sequenziale?

`verifica_premi()` itera su tutti i giocatori in una singola
passata — la raccolta è collettiva nel senso che considera tutti
prima di ritornare. Tuttavia, l'assegnazione non è equa:

```python
# partita.py, riga ~637
if tipo not in self.premi_tipo_chiusi and chiave not in self.premi_gia_assegnati:
    self.premi_gia_assegnati.add(chiave)
    self.premi_tipo_chiusi.add(tipo)  # ← chiude il tipo subito
    nuovi_eventi.append(...)
    break
```

Il tipo viene aggiunto a `premi_tipo_chiusi` immediatamente dopo
il primo vincitore trovato. Se due giocatori hanno reclamato lo stesso tipo
nello stesso turno, il secondo verrà trovato nell'iterazione ma il tipo
sarà già chiuso e non otterrà il premio.

Il comportamento attuale è: **il primo trovato nell'ordine di iterazione
della lista vince**. Non c'è un passaggio di pre-raccolta di tutti i
candidati prima di decidere.

Per un sistema corretto di co-vincita (premi condivisi nello stesso turno)
il metodo `verifica_premi()` dovrebbe:

1. Prima passata: raccogliere tutti i candidati per tipo (senza assegnare).
2. Seconda passata: per ogni tipo trovato, assegnare il premio a tutti i
   candidati validi contemporaneamente.

**Conclusione:** la raccolta è "collettiva" nella struttura del loop
ma l'assegnazione è sequenziale e favorisce l'ordine di lista.
Serve una ristrutturazione di `verifica_premi()` per supportare
la co-vincita.

---

## Domanda 5 — Cosa servirebbe cambiare per separare la fase di estrazione da quella di verifica?

La separazione richiederebbe modifiche in quattro file.

### `bingo_game/partita.py`

- Spezzare `esegui_turno()` in due metodi pubblici:
  - `esegui_fase_estrazione() -> dict` — passi 1-2 (estrazione + reclami bot).
    Ritorna: numero estratto, stato partita.
  - `esegui_fase_verifica() -> dict` — passi 3-6 (verifica, confronto bot,
    reset, tombola check). Ritorna: premi_nuovi, reclami_bot, tombola_rilevata.
- Aggiungere a `Partita` un attributo di fase:
  `fase_turno_corrente: Literal["attesa_estrazione", "attesa_reclami", "chiusto"]`
- Aggiornare `verifica_premi()` con la logica di pre-raccolta a due passate
  per supportare la co-vincita (vedi Domanda 4).

### `bingo_game/game_controller.py`

- Aggiungere `esegui_fase_estrazione_sicura(partita)` — wrapper dello stesso
  pattern di `esegui_turno_sicuro` per la prima fase.
- Aggiungere `esegui_fase_verifica_sicura(partita)` — wrapper per la seconda.
- Mantenere `esegui_turno_sicuro` come metodo compatibile (chiama i due nuovi
  in sequenza) per non rompere i test esistenti durante la transizione.

### `bingo_game/comandi_partita.py`

- `ComandiSistema` dovrà esporre i due nuovi comandi:
  `esegui_fase_estrazione(partita)` e `esegui_fase_verifica(partita)`.
- Il metodo `esegui_turno(partita)` esistente può restare per compatibilità.

### `bingo_game/ui/finestra_gioco.py`

- `_on_pulsante_principale()` dovrà diventare consapevole della fase:
  - Prima pressione → chiama `esegui_fase_estrazione` → aggiorna display
    col numero estratto → cambia etichetta pulsante in "Ho finito".
  - Seconda pressione (o nuovo tasto) → chiama `esegui_fase_verifica`
    → annuncia premi → ripristina etichetta "Passa turno".
- Aggiungere un attributo di stato UI: `_fase_turno_ui` per tracciare
  in quale sotto-fase si trova la finestra.
- **Accessibilità critica:** la modifica dell'etichetta del pulsante deve
  essere annunciata da NVDA. Usare `self._btn_principale.SetLabel(...)` e
  verificare che `wx.AccessibleObject` propaghi il cambio. Procedura da
  validare con `validate-accessibility.skill.md`.

**Conteggio file modificati:** 4 file sorgente + test correlati.

---

### Domanda 5b — Come cambiano `finestra_gioco.py`, `base_renderer.py` e `renderer_wx.py` con la separazione in fasi?

Questa sezione analizza i tre file del layer di presentazione per rispondere
a domande specifiche sullo stato attuale e sulle modifiche necessarie.

---

#### `finestra_gioco.py`

**D5b-1 — Metodo che gestisce il click sul pulsante principale**

Il metodo è `_on_pulsante_principale(self, event: object)` (~riga 330).
La struttura è la seguente:

1. Controlla se la partita è terminata:
   `self._comandi_sistema.is_terminata(self._partita)` — se sì, vocalizza
   un messaggio e ritorna senza fare nulla.
2. Chiama `self._comandi_sistema.esegui_turno(self._partita)`.
   `ComandiSistema` è il livello intermedio; non si rivolge a `game_controller`
   direttamente. La catena è:
   `finestra_gioco → ComandiSistema.esegui_turno → esegui_turno_sicuro (game_controller) → partita.esegui_turno`.
3. Incrementa `self._turno_corrente`.
4. Chiama `self._annuncia_risultato_turno(risultato)` e poi
   `self._aggiorna_stato_pulsante()`.
5. Se la partita è terminata, vocalizza un messaggio finale e disabilita il pulsante.

Il metodo è anche raggiunto da `Ctrl+P` tramite `_on_char_hook` (~riga 290),
che chiama direttamente `self._on_pulsante_principale(None)`.

**D5b-2 — Aggiornamento etichetta pulsante a runtime**

Sì, esiste già. Il metodo pubblico `aggiorna_stato_pulsante(self, primo_turno_eseguito: bool)`
(~riga 378) usa `self._btn_principale.SetLabel(...)`.
I valori possibili sono `"Passa turno"` (se `primo_turno_eseguito=True`)
e `"Inizia partita"` (altrimenti). Il metodo **è esposto come interfaccia
per il renderer** (duck typing): `_handle_fine_turno` in `renderer_wx.py`
lo chiama via `hasattr`-check su `self._finestra`. Internamente,
il metodo privato corrispondente è `_aggiorna_stato_pulsante()` (~riga 395),
che calcola `primo_turno_eseguito` dal contatore di estrazioni del tabellone
e delega ad `aggiorna_stato_pulsante`.

Per il sistema bifasico, questo punto è già il posto giusto dove gestire
le etichette delle fasi: basterà estendere la logica del metodo con il
valore della fase corrente.

**D5b-3 — Metodo che elabora il risultato del turno e lo passa al renderer**

Il metodo è `_annuncia_risultato_turno(self, risultato: dict)` (~riga 400).
Legge `risultato["numero_estratto"]` e `risultato["premi_nuovi"]`,
costruisce una stringa flat (`testo`) e la passa a
`self._renderer.mostra_messaggio_sistema(testo)`.

Numero estratto e premi sono concatenati nello stesso testo e vocalizzati
insieme in un'unica chiamata. Non esiste un passaggio intermedio di
oggetti strutturati: il renderer riceve solo una stringa.

**D5b-4 — Stato corrente dell'interfaccia**

Non esiste un attributo di fase formale. Il solo attributo di stato
è `self._turno_corrente: int = 0` (~riga 202), che conta i turni eseguiti.
L'etichetta del pulsante (`"Inizia partita"` / `"Passa turno"`) funge
da proxy implicito dello stato, ma non è un meccanismo di controllo:
non viene letta né verificata prima di eseguire azioni.

Per il sistema a fasi servirà un attributo esplicito, ad esempio:
```python
self._fase_turno_ui: Literal["attesa_estrazione", "attesa_reclami"] = "attesa_estrazione"
```
da aggiungere in `__init__` e leggere in `_on_pulsante_principale`
per determinare quale fase eseguire al prossimo click.

---

#### `base_renderer.py`

**D5b-5 — Metodi pubblici esposti dal contratto `BaseRenderer`**

Il contratto dichiara quattro metodi astratti obbligatori:

| Metodo | Firma | Descrizione |
|---|---|---|
| `render_esito` | `(self, esito: EsitoAzione) -> None` | Renderizza esito di un'azione (ok/errore + evento) |
| `mostra_schermata_configurazione` | `(self, stato: StatoConfigurazione) -> None` | Schermata di configurazione iniziale |
| `mostra_report_finale` | `(self, dati_partita: dict[str, Any]) -> None` | Riepilogo di fine partita |
| `mostra_messaggio_sistema` | `(self, testo: str) -> None` | Messaggio generico di sistema |

È presente un metodo concreto (non astratto) ereditato da tutte le implementazioni:

| Metodo | Firma | Descrizione |
|---|---|---|
| `_formatta_testo_da_catalogo` | `(self, chiave: str, **kwargs) -> str` | Lookup nei cataloghi localizzati con formattazione |

**D5b-6 — Metodo separato per annunciare il numero estratto separatamente dai premi**

Non esiste. Il contratto `BaseRenderer` espone solo `mostra_messaggio_sistema(testo: str)`,
che riceve una stringa già costruita dal chiamante. La costruzione del testo
(numero + premi concatenati) avviene in `finestra_gioco._annuncia_risultato_turno()`,
non nel renderer. Il contratto non conosce la struttura del risultato del turno.

**D5b-7 — Metodo per annunciare la fase corrente del turno**

Non esiste. Va aggiunto al contratto. La firma proposta:

```python
@abstractmethod
def annuncia_fase_turno(self, fase: str) -> None:
    """
    Vocalizza e mostra la fase corrente del turno
    (es. 'Numero estratto. Dichiara la tua vittoria.',
         'Verifica in corso.', 'Turno concluso.').
    Il testo deve essere già risolto dal chiamante tramite catalogo.
    """
    ...
```

I due metodi aggiuntivi correlati, da valutare nello stesso ciclo di modifica:
- `annuncia_numero_estratto(numero: int, numero_turno: int) -> None`
- `annuncia_premi_turno(premi: list[dict]) -> None`

---

#### `renderer_wx.py`

**D5b-8 — Come funziona l'annuncio del risultato del turno**

Non esiste un metodo `_annuncia_risultato_turno()` nel renderer.
Il renderer non conosce il dict del turno. La produzione del testo avviene
esternamente in `finestra_gioco._annuncia_risultato_turno()` (vedi D5b-3).

Il renderer riceve una stringa via `mostra_messaggio_sistema(testo: str)` (~riga 148
di `renderer_wx.py`), che esegue due operazioni in sequenza:

1. `_wx_aggiorna_output(testo)` (~riga 637): aggiorna il pannello griglia
   tramite `self._finestra.mostra_testo(testo)` e aggiunge il testo al log
   annunci tramite `self._finestra.aggiungi_a_log(testo)` — entrambi
   via duck typing con `hasattr`.
2. `_ao2_vocalizza(testo)` (~riga 642): registra `self._ultimo_annuncio = testo`
   e chiama `self._vocalizzatore.vocalizza_testo(testo)`.

Nessuna widget specifica viene aggiornata per l'annuncio del turno
(i metodi `_wx_aggiorna_cartella` e `_wx_aggiorna_tabellone` sono stub).

**D5b-9 — Meccanismo di vocalizzazione via `accessible_output2`**

Il testo è vocalizzato tramite `_ao2_vocalizza(testo)` (~riga 642), che chiama
`self._vocalizzatore.vocalizza_testo(testo)`. Il vocalizzatore è di tipo
`IVocalizzatore` (interfaccia da `my_lib/vocalizzatore.py`) e viene iniettato
nel costruttore di `WxRenderer`:

```python
def __init__(self, finestra_principale: "wx.Frame", vocalizzatore: IVocalizzatore):
```

Non è un singleton né un metodo statico: è una dependency injection pura.
L'implementazione concreta di `IVocalizzatore` wrappa `accessible_output2`,
ma il renderer non conosce questa dipendenza. Il parametro `interrompi`
viene usato solo in `ripeti_ultimo_annuncio()` tramite
`self._vocalizzatore.vocalizza_testo(self._ultimo_annuncio, interrompi=True)`.

**D5b-10 — Metodi esistenti riusabili per chiamate separate**

Per un sistema bifasico ("prima il numero, poi i premi"), i metodi
attualmente esistenti che potrebbero essere riutilizzati sono:

| Metodo esistente | Riutilizzo possibile |
|---|---|
| `mostra_messaggio_sistema(testo)` | Riusabile per entrambe le fasi con testi distinti costruiti dal chiamante |
| `_ao2_vocalizza(testo)` | Già atomico, si presta a essere chiamato due volte se esposto |
| `_wx_aggiorna_output(testo)` | Già atomico, idem |

I metodi da aggiungere al contratto `BaseRenderer` (da implementare in `WxRenderer`):

- `annuncia_numero_estratto(numero: int, numero_turno: int) -> None` —
  costruisce e vocalizza "Turno N. Numero estratto: X." senza premi.
- `annuncia_premi_turno(premi: list[dict]) -> None` —
  costruisce e vocalizza i premi trovati (o "Nessun premio questo turno.").
- `annuncia_fase_turno(fase: str) -> None` —
  vocalizza la fase corrente (testo già risolto dal chiamante).

In `WxRenderer` ogni nuovo metodo dovrà seguire la struttura:
testo → `_wx_aggiorna_output(testo)` → `_ao2_vocalizza(testo)`.

**D5b-11 — Meccanismo per annunciare a NVDA un cambio di stato dell'interfaccia**

Non esiste un meccanismo dedicato. `_handle_fine_turno` (~riga 605) chiama
`self._finestra.aggiorna_stato_pulsante(primo_turno_eseguito=True)` via duck typing,
che a sua volta chiama `SetLabel("Passa turno")`. Questo **non garantisce
che NVDA vocalizzi il cambio**: `SetLabel()` aggiorna il testo del widget
ma il re-announce dipende dal focus. Se il focus non è sul pulsante al
momento del cambio, NVDA non legge la nuova etichetta.

Nel codice attuale non viene fatto nulla per forzare il re-announce.

L'approccio wxPython accessibile consigliato è chiamare esplicitamente
il vocalizzatore dopo il cambio di etichetta:

```python
# In aggiorna_stato_pulsante() o nel renderer dopo SetLabel():
self._btn_principale.SetLabel(nuova_etichetta)
# Re-announce esplicito per NVDA:
self._renderer._ao2_vocalizza(nuova_etichetta)
```

In alternativa, se il focus è già sul pulsante, `AccessibleObject.NotifyEvent`
con `wxACC_EVENT_OBJECT_NAMECHANGE` può triggherare il refresh accessibile —
ma questo approccio è fragile e non portabile su tutti gli screen reader.
La soluzione più robusta e coerente con lo stile del progetto è la
vocalizzazione esplicita tramite `_ao2_vocalizza`.

---

#### Note aggiuntive

**Widget `_log_ctrl` e doppio annuncio:**
`_wx_aggiorna_output` appende ogni testo al `_log_ctrl` (area log annunci)
via `aggiungi_a_log()`. Con il sistema bifasico, se vengono fatte due chiamate
separate ("numero estratto" e poi "premi del turno"), entrambe compariranno
nel log come righe distinte — comportamento desiderabile per la consultazione
con `Ctrl+E`. Non richiede modifiche.

**`_ultimo_annuncio` e tasto F6:**
`_ao2_vocalizza` aggiorna `self._ultimo_annuncio` ad ogni chiamata.
Con chiamate separate, F6 ripeterà solo l'ultimo annuncio (premi del turno),
non il primo (numero estratto). Se si vuole ripetere entrambi, il campo
andrebbe sostituito con una lista degli ultimi N annunci o con una
concatenazione esplicita prima di `_ao2_vocalizza`.

**`ComandiGiocatoreUmano` vs `ComandiSistema`:**
Il campo `self._comandi = ComandiGiocatoreUmano(partita)` e
`self._comandi_sistema = ComandiSistema()` coesistono in `FinestraGioco.__init__`.
`ComandiSistema` gestisce il ciclo di turno; `ComandiGiocatoreUmano` gestisce
navigazione, reclami e segnazione. Con la separazione in fasi, entrambi
dovranno esporre i nuovi metodi di fase: `ComandiSistema` per
`esegui_fase_estrazione` / `esegui_fase_verifica`; `ComandiGiocatoreUmano`
per `dichiara_fine_turno`.

---

#### Tabella riepilogativa — File di presentazione

| File | Stato attuale | Cosa va aggiunto/modificato |
|---|---|---|
| `finestra_gioco.py` | `_on_pulsante_principale` monofase; nessun attributo di fase UI | Aggiungere `_fase_turno_ui`; split del metodo in due rami contestuali; estendere `aggiorna_stato_pulsante` con etichette di fase |
| `base_renderer.py` | Contratto con 4 metodi; nessun metodo per numero/premi separati o per fase | Aggiungere `annuncia_numero_estratto`, `annuncia_premi_turno`, `annuncia_fase_turno` come metodi astratti |
| `renderer_wx.py` | `mostra_messaggio_sistema` generico; nessun re-announce NVDA su `SetLabel` | Implementare i 3 nuovi metodi del contratto; aggiungere vocalizzazione esplicita dopo ogni `SetLabel` di fase |

---

## Domanda 6 — Come gestire il segnale "Ho finito" del giocatore umano?

Oggi non esiste. L'unico segnale di fine disponibilità del giocatore
è la pressione di "Passa turno", che però nel sistema corrente innesca
anche l'estrazione. Una volta separato il ciclo, serve un modo per sapere
che l'umano ha terminato di valutare i propri reclami nel turno corrente.

### Tre opzioni, con pro e contro

#### Opzione A — Tasto dedicato "Ho finito" (nuovo shortcut)

- Aggiungere un tasto (es. `Invio` o `Spazio`) che segnali la fine
  della fase reclami senza premere il pulsante "Passa turno".
- Pro: semantica esplicita, nessuna ambiguità.
- Contro: aggiunge un tasto da memorizzare; con NVDA l'utente dovrà
  sentire la nuova label prima di sapere cosa fare.

#### Opzione B — Due pressioni del pulsante principale (comportamento contestuale)

- Prima pressione nel turno: estrai numero.
- Seconda pressione: "Ho finito, avvia verifica".
- Pro: nessun tasto nuovo, flusso lineare.
- Contro: l'utente potrebbe premere due volte rapidamente (double-click
  o doppio Invio); serve un guard temporale o modale.

#### Opzione C — Raccolta automatica dopo timeout (timer)

- Dopo l'estrazione, concedere N secondi. Se l'umano non interagisce,
  la fase reclami chiude e la verifica avviene automaticamente.
- Pro: nessuna frizione per l'utente.
- Contro: inadatto ad accessibilità NVDA: lo screen reader potrebbe essere
  ancora in fase di lettura; l'utente non sente ancora il numero.
  **Non raccomandata come soluzione primaria.**

### Punto naturale di inserimento nel codice

Il punto meno invasivo è il seguente:

1. **`bingo_game/players/giocatore_base.py`** — aggiungere:
   `turno_dichiarato_concluso: bool = False`
   con un metodo `dichiara_fine_turno() -> None`.

2. **`bingo_game/partita.py`** — aggiungere il metodo:
   `tutti_hanno_dichiarato_fine() -> bool`
   che verifica che tutti i giocatori non automatici abbiano
   `turno_dichiarato_concluso == True`.

3. **`bingo_game/ui/finestra_gioco.py`** — il gestore di tasto
   chiama `comandi.dichiara_fine_turno(giocatore_umano)` e poi,
   se `tutti_hanno_dichiarato_fine()`, chiama `esegui_fase_verifica`.

**Nota:** `_passa_turno_core()` in `giocatore_base.py` esegue già
il reset di `reclamo_turno` via `EventoFineTurno`. Potrebbe essere
esteso per includere il reset di `turno_dichiarato_concluso`.
Al momento non viene chiamato nel flusso attivo.

---

## Domanda 7 — Quali test esistenti sarebbero impattati dalla separazione in fasi?

### Impatto diretto (test che chiamano i metodi che verrebbero modificati)

| File test | N. test coinvolti | Motivo |
|---|---|---|
| `tests/test_partita.py` | 4 | Chiamate dirette a `verifica_premi()` (righe 737, 823, 850, 908, 972) |
| `tests/integration/test_partita_bot_attivo.py` | 8 | Tutte e 8 le `def test_*` chiamano `partita.esegui_turno()` direttamente |
| `tests/test_game_controller.py` | 5 | Sezione 7 — `test_esegui_turno_sicuro_*` (righe 429, 447, 457, 464, 479) |
| `tests/test_comandi_partita.py` | 4 | Sezione `esegui_turno` (righe 139, 156, 169, 179, 186) |
| `tests/integration/test_event_coverage.py` | 3+ | `esegui_turno_sicuro` in riga 82, 93, 109 |
| `tests/integration/test_logging_integration.py` | 2 | `esegui_turno_sicuro` in righe 102, 124 |

### Impatto indiretto (test che osservano effetti collaterali del turno)

| File test | Motivo |
|---|---|
| `tests/test_giocatore_umano.py` | Logica di reclamo legata al timing del turno |
| `tests/test_giocatore_base.py` | `reset_reclamo_turno`, `_passa_turno_core` |
| `tests/integration/test_game_controller_loop.py` | Loop multi-turno; si basa su `esegui_turno_sicuro` |

### Test potenzialmente nuovi da scrivere

- `test_fase_estrazione_aggiorna_numero` — verifica che solo il numero cambi.
- `test_fase_verifica_assegna_premi_collettivi` — due giocatori reclamano
  lo stesso ambo nello stesso turno, entrambi lo ricevono.
- `test_umano_dichiara_fine_senza_reclamo` — nessun premio assegnato.
- `test_umano_dichiara_fine_con_reclamo_valido` — premio assegnato.
- `test_passaggio_di_fase_bloccato_se_turno_non_estratto` — la fase verifica
  non può iniziare prima dell'estrazione.

**Strategia consigliata per la migrazione:**
mantenere `esegui_turno()` come metodo di compatibilità che chiama
i due nuovi metodi in sequenza, in modo che i test esistenti
non vadano rotti in un colpo solo. I test nuovi verificheranno
i metodi separati.

---

## Domanda 8 — Rischi e complicazioni non evidenti

### Rischio 1 — Annuncio NVDA del cambio etichetta pulsante

Quando l'etichetta di `_btn_principale` cambia da "Passa turno"
a "Ho finito" (o analogo), wxPython potrebbe non propagare il cambio
allo screen reader automaticamente. Se il focus è sul pulsante al momento
del cambio, NVDA leggerà la vecchia etichetta. È necessario testare
esplicitamente il comportamento con `wx.Accessible` o forzare un
re-announce via `wx.PostEvent` con un evento di accessibilità.
Riferimento: `validate-accessibility.skill.md`.

### Rischio 2 — Segnale "Ho finito" prima della segnazione

Se l'umano dichiara fine turno prima di segnare il numero sulla cartella
(tramite frecce + Barra spazio), il sistema dovrà confrontare i reclami
con una cartella non aggiornata. Oggi la segnazione è automatica
(`aggiorna_con_numero()` viene chiamata dall'estrazione su tutti i giocatori).
Questo rischio non esiste nel progetto corrente ma potrebbe emergere
se in futuro la segnazione diventasse manuale. Da documentare come
invariante: "la segnazione avviene prima della fine del turno".

### Rischio 3 — `_passa_turno_core()` inutilizzato

`giocatore_base.py` riga 288 implementa `_passa_turno_core()` che
costruisce un `EventoFineTurno` e resetta `reclamo_turno`.
Nel flusso corrente non viene mai chiamato: il reset avviene
direttamente in `esegui_turno()` passo 5.
Con la separazione in fasi, `_passa_turno_core()` potrebbe diventare
il metodo naturale per il segnale "Ho finito" del giocatore umano —
ma bisogna decidere esplicitamente chi lo chiama (il giocatore stesso?
la Partita? il controller?) e allinearlo con il nuovo flusso.
Lasciarlo inutilizzato crea confusione; va o rimosso o integrato.

### Rischio 4 — Premi chiusi nel mezzo del loop (bug di equità attuale)

Già descritto nella Domanda 4. Con la separazione in fasi, se non si
corregge anche `verifica_premi()`, si introduce un rischio più visibile:
il giocatore umano potrebbe dichiarare un reclamo valido per un tipo già
chiuso da un bot che ha reclamato in anticipo nella stessa fase.
La correzione di `verifica_premi()` (pre-raccolta + assegnazione collettiva)
è quindi un prerequisito della separazione in fasi, non un'opzione.

### Rischio 5 — Stato di fase non serializzato

Se in futuro si volesse salvare/ripristinare una partita interrotta
tra una fase e l'altra, `fase_turno_corrente` dovrebbe essere parte
dello stato serializzato. Oggi `get_stato_completo()` non include
sotto-fasi. Da considerare nella struttura del nuovo attributo.

### Rischio 6 — Multiplayer e segnale asincrono

In uno scenario futuro con più umani, "tutti hanno dichiarato fine"
diventa una barriera di sincronizzazione distribuita. Il modello
`tutti_hanno_dichiarato_fine()` funziona in memoria locale ma va
ridisegnato per una comunicazione asincrona. Non è un rischio immediato,
ma l'architettura del segnale dovrebbe essere definita in modo da
non creare un accoppiamento irreversibile con la versione locale.

---

## Sintesi e Raccomandazioni

| Aspetto | Stato attuale | Cambiamento necessario |
|---|---|---|
| Ciclo di turno | Monoblocco in `esegui_turno()` | Dividere in `esegui_fase_estrazione` + `esegui_fase_verifica` |
| Concetto di fase | Presente negli eventi, assente nel controllo | Aggiungere `fase_turno_corrente` a `Partita` |
| Raccolta reclami | Collettiva ma assegnazione sequenziale | Correggere `verifica_premi()` con doppia passata |
| Segnale "Ho finito" umano | Inesistente | Nuovo attributo + metodo in `giocatore_base`, check in `Partita` |
| UI pulsante | Singolo comportamento | Comportamento contestuale per fase |
| Test esistenti | 22+ test direttamente impattati | Mantenere compatibilità via wrapper durante transizione |

**La separazione è tecnicamente fattibile.** I punti di modifica sono
ben localizzati in quattro file sorgente e la struttura degli eventi
già anticipa il modello a due fasi. Il rischio principale non è
tecnico ma di regressione nei test: la migrazione deve avvenire
in modo incrementale, mantenendo la compatibilità all'indietro
fino a quando i test sono aggiornati.

**Prerequisito non negoziabile:** la correzione della logica di chiusura
premi in `verifica_premi()` deve precedere o accompagnare la separazione,
altrimenti il nuovo sistema sarà formalmente bifasico ma sostanzialmente
inequo come quello attuale.

---

*File correlati analizzati:*
[bingo_game/partita.py](../../bingo_game/partita.py) •
[bingo_game/game_controller.py](../../bingo_game/game_controller.py) •
[bingo_game/comandi_partita.py](../../bingo_game/comandi_partita.py) •
[bingo_game/ui/finestra_gioco.py](../../bingo_game/ui/finestra_gioco.py) •
[bingo_game/players/giocatore_base.py](../../bingo_game/players/giocatore_base.py) •
[bingo_game/players/giocatore_automatico.py](../../bingo_game/players/giocatore_automatico.py) •
[bingo_game/events/eventi_partita.py](../../bingo_game/events/eventi_partita.py)
