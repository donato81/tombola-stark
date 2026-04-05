---
type: design
feature: refactor_vocalizzatore
agent: Agent-Design
status: COMPLETED
version: v1.0.0
date: 2026-03-31
report_ref: docs/4 - reports/analisi_refactor_vocalizzatore/REPORT_DIAGNOSI_VOCALIZZATORE_2026-03-30.md
---

## Metadati

tipo: design
titolo: Design refactor strutturale R2 per my_lib/vocalizzatore.py
data_creazione: 2026-03-31
agente: Agent-Design
stato: completato
feature: refactor_vocalizzatore
versione_progetto: v1.0.0
report: docs/4 - reports/analisi_refactor_vocalizzatore/REPORT_DIAGNOSI_VOCALIZZATORE_2026-03-30.md

## Contenuto

### Idea in 3 righe

Il refactor R2 riduce `my_lib/vocalizzatore.py` al suo contratto reale,
introducendo un'interfaccia astratta stabile e una implementazione silenziosa
per test e ambienti headless. L'obiettivo e' risolvere le criticita' P1, P2,
P3 e P4 del report diagnostico senza cambiare motore TTS, senza spostare file e
senza ampliare lo scope al catalogo testi.

### Obiettivo del refactor

Il refactor interviene su quattro criticita' esplicitamente diagnosticate nel
report padre:

- **P1 - Nessuna interfaccia astratta**:
  `WxRenderer` dipende oggi dalla classe concreta `Vocalizzatore`. Il refactor
  introduce `IVocalizzatore` per invertire la dipendenza e permettere
  sostituzione del backend senza toccare il renderer.
- **P2 - Nessuna gestione delle eccezioni**:
  `Vocalizzatore.vocalizza_testo()` adottera' un comportamento best-effort con
  `try/except`, in modo che un errore AO2 non blocchi il gioco.
- **P3 - Dead code**:
  i 9 metodi pubblici inutilizzati vengono rimossi. La classe mantiene solo la
  superficie minima coerente con l'unico uso reale nel codebase.
- **P4 - Testabilita' difficile**:
  il costruttore accettera' un backend opzionale iniettabile, cosi' i test non
  dipenderanno da AO2 attivo e non richiederanno `patch()` su `Auto`.

Il refactor non cambia il motore di vocalizzazione. `accessible-output2`
resta l'unico backend reale supportato.

### Contesto

Il report di diagnosi ha fissato come fonte di verita' i seguenti fatti:

- `WxRenderer` usa soltanto `vocalizza_testo()`.
- `my_lib/vocalizzatore.py` contiene 9 metodi dead code.
- AO2 e' una dipendenza esterna legittima del modulo.
- Il posizionamento raccomandato per questo ciclo e' **Opzione A**:
  mantenere il file in `my_lib/` e introdurre il contratto senza spostamenti.

Questo design assume tali conclusioni come gia' validate e non le rivaluta.

### Attori e concetti

#### Attori

- `IVocalizzatore`
- `Vocalizzatore`
- `NullVocalizzatore`
- `WxRenderer`
- backend AO2 `Auto`
- suite `tests/unit/test_vocalizzatore.py`

#### Concetti

- **Dependency inversion**:
  il renderer dipende da un contratto, non dal backend concreto.
- **Best-effort accessibility**:
  la vocalizzazione non deve mai bloccare il gioco in caso di errore del
  backend TTS.
- **Headless-safe testing**:
  i test devono poter verificare il comportamento senza screen reader attivo.
- **Surface minimization**:
  il modulo espone solo i metodi realmente necessari.

### Componenti coinvolti

- File da refactorizzare: [my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py)
- File da modificare per type hint: [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)
- File di test da creare nel ciclo successivo: [tests/unit/test_vocalizzatore.py](../../tests/unit/test_vocalizzatore.py)
- Report padre: [docs/4 - reports/analisi_refactor_vocalizzatore/REPORT_DIAGNOSI_VOCALIZZATORE_2026-03-30.md](../4%20-%20reports/analisi_refactor_vocalizzatore/REPORT_DIAGNOSI_VOCALIZZATORE_2026-03-30.md)

### Decisioni architetturali

#### Decisione 1 - Il contratto e' `Protocol`, non `ABC`

Viene introdotto un `Protocol` denominato `IVocalizzatore` con almeno questa
firma:

```python
class IVocalizzatore(Protocol):
    def vocalizza_testo(self, testo: str, interrompi: bool = False) -> None:
        ...
```

Motivazione della scelta di `Protocol` rispetto ad `ABC`:

- il codebase usa gia' dependency injection leggera e type hints, non una
  gerarchia pesante di classi astratte per i servizi di presentazione;
- `Protocol` consente compatibilita' strutturale: qualsiasi oggetto con la
  stessa firma puo' essere passato a `WxRenderer` senza ereditarieta'
  esplicita;
- i test possono usare facilmente stub semplici o `NullVocalizzatore` senza
  introdurre vincoli di sottoclasse;
- per questo caso d'uso serve un contratto minimo di comportamento, non una
  gerarchia con logica condivisa.

`ABC` sarebbe piu' verboso e imporrebbe ereditarieta' nominale dove il
problema reale e' solo la sostituibilita' del servizio.

#### Decisione 2 - Struttura finale di `Vocalizzatore`

La classe concreta `Vocalizzatore` sopravvive come adapter AO2 minimale.
La struttura finale attesa e':

- `__init__(self, backend: object | None = None) -> None`
- `vocalizza_testo(self, testo: str, interrompi: bool = False) -> None`

I 9 metodi dead code identificati nel report vengono rimossi integralmente:

- `vocalizza_numero`
- `vocalizza_errore`
- `messaggio_inizializzazione`
- `messaggio_errore_numeri_terminati`
- `messaggio_numero_estratto`
- `messaggio_reset_tabellone`
- `vocalizza_numeri_estratti`
- `vocalizza_numeri_disponibili`
- `_formatta_numeri_per_vocalizzazione`

Il costruttore riceve un backend opzionale iniettabile. Se il backend non e'
fornito, istanzia `Auto()` come oggi. Se il backend e' fornito, viene usato
direttamente. Questo consente test deterministici senza screen reader attivo.

Il metodo `vocalizza_testo()` implementa la protezione best-effort:

```python
def vocalizza_testo(self, testo: str, interrompi: bool = False) -> None:
    try:
        self._backend.speak(testo, interrupt=interrompi)
    except Exception:
        return
```

La scelta di fallire silenziosamente e' intenzionale: il gameplay non deve mai
interrompersi per un errore del layer TTS.

#### Decisione 3 - Introduzione di `NullVocalizzatore`

Viene introdotta una classe `NullVocalizzatore` che implementa
`IVocalizzatore` e scarta ogni richiesta di voce:

```python
class NullVocalizzatore:
    def vocalizza_testo(self, testo: str, interrompi: bool = False) -> None:
        return
```

Scopo:

- test unitari headless;
- ambienti CI senza screen reader;
- wiring applicativo futuro per modalita' muta o fallback di sicurezza.

Posizionamento scelto:

- **stesso file del contratto**, cioe' [my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py)

Motivazione:

- il contratto, l'implementazione reale e quella nulla restano nello stesso
  punto di verita';
- il modulo e' molto piccolo dopo la rimozione del dead code, quindi non serve
  frammentarlo ulteriormente;
- i test futuri potranno importare `IVocalizzatore`, `Vocalizzatore` e
  `NullVocalizzatore` da un solo modulo.

#### Decisione 4 - Modifica minima a `WxRenderer`

In [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)
si modifica una sola firma nel costruttore.

Stato attuale rilevato:

```python
def __init__(
    self,
    finestra_principale: wx.Frame,
    vocalizzatore: Vocalizzatore,
) -> None:
    self._finestra: wx.Frame = finestra_principale
    self._vocalizzatore: Vocalizzatore = vocalizzatore
```

Stato finale atteso:

```python
def __init__(
    self,
    finestra_principale: wx.Frame,
    vocalizzatore: IVocalizzatore,
) -> None:
    self._finestra: wx.Frame = finestra_principale
    self._vocalizzatore: IVocalizzatore = vocalizzatore
```

Nel file attuale il cambio riguarda il parametro annotato nella firma del
costruttore e il type hint dell'attributo assegnato immediatamente sotto.
Nessun'altra modifica al renderer rientra in questo refactor.

#### Decisione 5 - Nessuno spostamento di file

[my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py) resta nella posizione
attuale. Questa e' l'Opzione A del report diagnostico.

Motivazione breve:

- minimizza il rischio del ciclo;
- evita churn sugli import;
- isola il refactor al problema reale, che e' contrattuale e di testabilita',
  non di packaging;
- permette di validare prima il nuovo bordo architetturale e solo in un ciclo
  successivo, se necessario, il riposizionamento fisico del file.

### Impatto sulla suite di test

Con `NullVocalizzatore` e con il backend iniettabile:

- i test futuri di `WxRenderer` possono passare un oggetto conforme a
  `IVocalizzatore` senza `patch()` su `Auto`;
- i test di `Vocalizzatore` possono usare un backend fake con metodo `speak()`
  per verificare il forwarding di `testo` e `interrompi`;
- i test di `NullVocalizzatore` verificano semplicemente l'assenza di errori e
  il comportamento silenzioso.

Questo elimina la necessita' di patchare direttamente `Auto` nelle suite future
e riduce l'accoppiamento dei test all'implementazione interna di AO2.

### Cosa non rientra in questo refactor

Sono esplicitamente fuori scope:

- spostamento fisico di [my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py)
  in un altro package;
- integrazione delle stringhe vocali con [bingo_game/ui/locales/it.py](../../bingo_game/ui/locales/it.py);
- introduzione di altri motori TTS oltre ad AO2;
- modifiche comportamentali ulteriori a [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)
  oltre al type hint del parametro e dell'attributo;
- wiring applicativo completo di `NullVocalizzatore` nell'applicazione;
- test del renderer diversi da quelli necessari per sfruttare il nuovo
  contratto in futuro.

### Criteri di completamento del design

Il design si considera corretto quando descrive in modo non ambiguo:

- il contratto `IVocalizzatore`;
- la forma finale di `Vocalizzatore`;
- il ruolo e il posizionamento di `NullVocalizzatore`;
- la modifica puntuale a `WxRenderer`;
- il mantenimento del file in `my_lib/`;
- l'impatto sui test;
- le esclusioni di scope.

## Stato Avanzamento

- [x] Design redatto
- [x] Validazione umana
- [x] Approvato per planning esecutivo
- [x] Pronto per implementazione
- [x] Implementazione completata — 2026-03-31