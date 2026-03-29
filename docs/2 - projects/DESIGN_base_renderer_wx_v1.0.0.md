---
type: design
feature: base_renderer_wx
agent: Agent-Design
status: DRAFT
version: v1.0.0
date: 2026-03-30
report_ref: docs/4 - reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md
---

## Metadati

tipo: design
titolo: Design introduzione BaseRenderer e WxRenderer
data_creazione: 2026-03-30
agente: Agent-Design
stato: bozza
feature: base_renderer_wx
versione_progetto: v1.0.0
report: docs/4 - reports/REPORT_ANALISI_BASE_RENDERER_WX_2026-03-30.md

## Contenuto

### Idea in 3 righe

Il progetto sostituisce il renderer terminale con un contratto astratto stabile,
orientato a una UI che agisce direttamente su widget e vocalizzazione.
`BaseRenderer` congela il bordo tra logica di gioco e presentazione, mentre
`WxRenderer` realizza quel bordo in wxPython riusando il catalogo esistente.
La priorita' non e' ancora implementare gli handler, ma rendere definitiva e
testabile l'interfaccia che guidera' il ciclo di sviluppo successivo.

### Obiettivo

Definire in modo definitivo:

- la firma di `BaseRenderer`
- il ruolo di `StatoConfigurazione`
- la struttura interna di `WxRenderer`
- il contratto documentato di `mostra_report_finale(dati_partita: dict)`
- il perimetro di eliminazione futura di
  [bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py)

### Contesto

Lo stato attuale del progetto espone un solo renderer,
[bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py),
basato su `Sequence[str]`. Questo schema era corretto per la TUI, ma non e'
piu' coerente con il nuovo obiettivo: una UI wxPython accessibile, sincronizzata
con vocalizzazione AO2 e interamente alimentata dal catalogo
[bingo_game/ui/locales/it.py](bingo_game/ui/locales/it.py).

Le decisioni architetturali gia' validate impongono:

- nessuna stringa hardcoded nel renderer
- ordine fisso handler: testo -> widget -> voce
- dependency injection per finestra wx e vocalizzatore
- nessun test in questo ciclo

### Attori e Concetti

#### Attori

- `EsitoAzione`
- `BaseRenderer`
- `WxRenderer`
- `StatoConfigurazione`
- `Vocalizzatore`
- catalogo `it.py`
- dataclass evento da `bingo_game/events/`

#### Concetti

- Contratto di bordo:
  il renderer e' l'unico punto dove il dominio tocca l'interfaccia.
- Successo silenzioso:
  `ok=True` e `evento=None` non producono nessuna azione UI.
- Configurazione guidata dal controller:
  il renderer mostra uno stato, ma non decide la sequenza dei passi.
- Sincronizzazione visivo/voce:
  ogni handler aggiorna prima la UI visiva e subito dopo vocalizza lo stesso testo.

### Componenti coinvolti

- Nuovo file: [bingo_game/ui/renderers/base_renderer.py](bingo_game/ui/renderers/base_renderer.py)
- Nuovo file: [bingo_game/ui/renderers/renderer_wx.py](bingo_game/ui/renderers/renderer_wx.py)
- File da eliminare nel ciclo successivo:
  [bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py)
- Catalogo bloccato: [bingo_game/ui/locales/it.py](bingo_game/ui/locales/it.py)
- Wrapper voce: [my_lib/vocalizzatore.py](my_lib/vocalizzatore.py)
- Eventi bloccati: [bingo_game/events/eventi.py](bingo_game/events/eventi.py) e moduli collegati

### Flussi Concettuali

#### Flusso 1 - renderizzazione di un errore

1. Il controller passa `EsitoAzione` con `ok=False`.
2. `BaseRenderer.render_esito()` delegato in `WxRenderer` riconosce il caso errore.
3. Il renderer recupera il testo da `MESSAGGI_ERRORI` o, in fallback, da `MESSAGGI_SISTEMA`.
4. Aggiorna il widget di output.
5. Vocalizza lo stesso testo.

#### Flusso 2 - renderizzazione di un evento standard

1. Il controller passa `EsitoAzione` con `ok=True` e `evento` valorizzato.
2. `WxRenderer` smista l'evento nel dispatcher centrale.
3. L'handler costruisce il testo dal catalogo con `_formatta_testo_da_catalogo()`.
4. Aggiorna i widget wx dedicati.
5. Vocalizza il testo tramite `Vocalizzatore`.

#### Flusso 3 - successo silenzioso

1. Il controller passa `EsitoAzione` con `ok=True` e `evento=None`.
2. `WxRenderer.render_esito()` termina senza effetto collaterale.

#### Flusso 4 - configurazione iniziale

1. Il controller costruisce `StatoConfigurazione` per il passo corrente.
2. Chiama `mostra_schermata_configurazione(stato)`.
3. Il renderer visualizza il pannello corretto e vocalizza il messaggio catalogato.
4. La decisione sul passo successivo resta fuori dal renderer.

#### Flusso 5 - report finale

1. Il controller normalizza i dati finali della partita in `dati_partita`.
2. Chiama `mostra_report_finale(dati_partita)`.
3. Il renderer mostra riepilogo e voce usando chiavi gia' documentate.

### Decisioni Architetturali

#### Decisione 1 - BaseRenderer resta leggero ma non vuoto

`BaseRenderer` contiene solo quattro metodi pubblici astratti e un unico metodo
concreto condiviso, `_formatta_testo_da_catalogo()`. Il metodo concreto non ha
effetti collaterali: effettua solo lookup e formattazione dei testi.

#### Decisione 2 - StatoConfigurazione vive nello stesso modulo del contratto

`StatoConfigurazione` viene definito in
[bingo_game/ui/renderers/base_renderer.py](bingo_game/ui/renderers/base_renderer.py)
come dataclass frozen. In questo modo il contratto astratto e il tipo di stato
che il contratto usa restano nello stesso punto di verita'.

Struttura proposta:

```python
@dataclass(frozen=True)
class StatoConfigurazione:
    fase_corrente: Literal["nome", "bot", "cartelle", "conferma"]
    codice_messaggio: Codici_Configurazione
    codice_errore: Optional[Codici_Configurazione] = None
    nome_giocatore: Optional[str] = None
    numero_bot: Optional[int] = None
    numero_cartelle: Optional[int] = None
```

#### Decisione 3 - _formatta_testo_da_catalogo centralizza il catalogo intero

Per rendere valida la firma decisa `(_formatta_testo_da_catalogo(self, chiave, **kwargs))`,
il metodo concreto in `BaseRenderer` deve conoscere tutti i cataloghi del modulo
locale e cercare la chiave in quest'ordine:

1. `MESSAGGI_ERRORI`
2. `MESSAGGI_EVENTI`
3. `MESSAGGI_OUTPUT_UI_UMANI`
4. `MESSAGGI_SISTEMA`
5. `MESSAGGI_CONFIGURAZIONE`

Se la chiave manca, il fallback deve comunque arrivare da `MESSAGGI_SISTEMA`, mai
da stringhe scritte a mano.

#### Decisione 4 - WxRenderer usa dependency injection pura

Firma del costruttore:

```python
def __init__(self, finestra_principale: wx.Frame, vocalizzatore: Vocalizzatore) -> None
```

Il renderer non crea la finestra e non crea il backend AO2. Riceve entrambe le
dipendenze dall'esterno.

#### Decisione 5 - Dispatcher completo ma senza duplicazioni ambigue

`WxRenderer._dispatch_evento()` deve riprodurre la copertura del dispatcher del
terminale, ma non copiarne la duplicazione sul reclamo. Ogni tipo evento deve
avere un solo handler di destinazione.

Famiglie da gestire:

- Focus e navigazione
- Visualizzazione cartelle
- Navigazione riga
- Navigazione colonna
- Segnazione e ricerca
- Tabellone
- Flusso partita

#### Decisione 6 - Separazione `_wx_*` e `_ao2_*`

Ogni handler privato costruisce il testo e poi chiama due layer distinti:

- `_wx_*` per i widget
- `_ao2_*` per la voce

Questo garantisce allineamento percettivo e permette test indipendenti nel ciclo
successivo.

### Firma definitiva proposta di BaseRenderer

```python
class BaseRenderer(ABC):
    @abstractmethod
    def render_esito(self, esito: EsitoAzione) -> None: ...

    @abstractmethod
    def mostra_schermata_configurazione(self, stato: StatoConfigurazione) -> None: ...

    @abstractmethod
    def mostra_report_finale(self, dati_partita: dict) -> None: ...

    @abstractmethod
    def mostra_messaggio_sistema(self, testo: str) -> None: ...

    def _formatta_testo_da_catalogo(self, chiave: str, **kwargs) -> str: ...
```

### Docstring definitivo proposto per mostra_report_finale

```python
def mostra_report_finale(self, dati_partita: dict) -> None:
    """
    Presenta il riepilogo finale della partita.

    Chiavi attese in `dati_partita`:
    - `turni_giocati`: int
    - `stato_partita`: str
    - `numeri_estratti`: list[int]
    - `premi_gia_assegnati`: list[str]
    - `giocatori`: list[dict]

    Chiavi facoltative ma consigliate:
    - `conteggio_estratti`: int
    - `conteggio_premi`: int
    - `conteggio_giocatori`: int
    - `vincitore_tombola`: str | None

    Nota:
    - `DatiReportFinale` e' un refactor futuro raccomandato, ma fuori scope in
      questo ciclo.
    """
```

### Struttura completa proposta di WxRenderer

#### Metodi pubblici

- `__init__(finestra_principale, vocalizzatore)`
- `render_esito(esito)`
- `mostra_schermata_configurazione(stato)`
- `mostra_report_finale(dati_partita)`
- `mostra_messaggio_sistema(testo)`

#### Metodi privati di orchestrazione

- `_dispatch_evento(evento)`
- `_handle_errore(esito)`
- un `_handle_*` per ogni famiglia evento

#### Layer widget

- `_wx_aggiorna_output(testo)`
- `_wx_aggiorna_cartella(...)`
- `_wx_aggiorna_tabellone(...)`
- `_wx_mostra_configurazione(stato)`
- `_wx_mostra_report_finale(dati_partita)`

#### Layer voce

- `_ao2_vocalizza(testo)`

#### Helper puri recuperati dal terminale

- `_indice_umano(indice_zero_based)`
- `_raggruppa_numeri_per_decine(numeri)`
- `_segnati_set(numeri_segnati)`

### Schema eliminazione renderer_terminal.py

1. Censire tutti i riferimenti a `TerminalRenderer`.
2. Migrare il package renderers al nuovo contratto.
3. Eliminare il file terminale solo dopo la presenza dei due nuovi moduli.
4. Registrare il test
   [tests/unit/test_renderer_report_finale.py](tests/unit/test_renderer_report_finale.py)
   come impatto noto e fuori scope in questa fase.

### TODO esplicito fuori scope

- Introdurre in futuro una dataclass `DatiReportFinale`
- Pianificare la riscrittura o sostituzione di
  [tests/unit/test_renderer_report_finale.py](tests/unit/test_renderer_report_finale.py)
- Eliminare definitivamente
  [bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py)
  solo nel ciclo implementativo successivo

### Rischi e Vincoli

- Accessibilita': il renderer non puo' divergere tra testo mostrato e testo vocalizzato.
- Backward compatibility: il vecchio test sul report finale non e' compatibile con
  il nuovo contratto UI e va trattato come follow-up.
- Pulizia architetturale: la configurazione iniziale non deve scivolare nel renderer
  come sequenza decisionale.
- Vincolo catalogo: nessuna modifica a
  [bingo_game/ui/locales/it.py](bingo_game/ui/locales/it.py) in questo ciclo.

### Coding plans correlati

- Previsto: [PLAN_base_renderer_wx_v1.0.0.md](../3%20-%20coding%20plans/PLAN_base_renderer_wx_v1.0.0.md)

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Approvato
- [ ] Archiviato