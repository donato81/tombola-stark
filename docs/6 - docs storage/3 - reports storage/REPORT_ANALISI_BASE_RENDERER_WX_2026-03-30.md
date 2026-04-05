## Metadati

tipo: report
titolo: Analisi introduzione layer UI wxPython con BaseRenderer e WxRenderer
data_creazione: 2026-03-30
agente: Agent-Analyze
stato: definitivo

## Contenuto

### Trigger

Preparare il perimetro documentale per la sostituzione del renderer terminale
con un nuovo layer UI basato su wxPython e vocalizzazione tramite
accessible_output2, senza ancora scrivere codice di produzione.

### Sommario esecutivo

Lo stato attuale del layer UI mostra un solo renderer concreto,
[bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py),
interamente costruito intorno al contratto `Sequence[str]`. Questo contratto e'
incompatibile con il modello wx desiderato, dove il renderer agisce
direttamente su widget e voce.

Il progetto possiede gia' il catalogo testuale completo in
[bingo_game/ui/locales/it.py](bingo_game/ui/locales/it.py) e un wrapper AO2 in
[my_lib/vocalizzatore.py](my_lib/vocalizzatore.py). Manca invece un contratto
astratto stabile per il renderer, manca uno stato esplicito per la schermata di
configurazione e manca un renderer wx che riusi la logica pura oggi dispersa nel
renderer terminale.

L'analisi conferma che il piano e' fattibile senza toccare il dominio, ma segnala
quattro punti di attenzione: duplicazione di branch nel dispatcher terminale,
presenza di un test ancora accoppiato al vecchio contratto testuale, assenza del
tipo `StatoConfigurazione` e necessita' di documentare in modo esplicito il
payload atteso da `mostra_report_finale`.

### Dettaglio osservazioni

#### 1. Stato attuale del layer UI

- Esiste un solo renderer concreto:
  [bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py).
- Il package
  [bingo_game/ui/renderers/__init__.py](bingo_game/ui/renderers/__init__.py)
  e' vuoto.
- Non esistono ancora:
  - `base_renderer.py`
  - `renderer_wx.py`
  - un tipo `StatoConfigurazione`

Il renderer terminale usa un dispatcher centrale in `render_esito()` che copre le
famiglie evento richieste dal task. Il valore riusabile non e' il formato
testuale finale, ma la mappa mentale degli eventi e alcune trasformazioni pure.

#### 2. Logica pura da recuperare dal renderer terminale

Le seguenti trasformazioni sono indipendenti dal terminale e possono essere
spostate nei metodi privati del futuro renderer wx:

- Conversione indice 0-based -> 1-based per la UI:
  `numero_umano = evento.indice + 1`
- Raggruppamento dei numeri estratti per decine nel report completo:
  bucket `(1, 9)`, `(10, 19)`, `(20, 29)`, `(30, 39)`, `(40, 49)`,
  `(50, 59)`, `(60, 69)`, `(70, 79)`, `(80, 90)`
- Lookup dei numeri segnati con set per i renderer avanzati:
  `segnati_set = set(evento.numeri_segnati_ordinati)`
- Pattern di costruzione token per righe/colonne avanzate:
  - `-` -> parola catalogata per cella vuota
  - numero segnato -> `N*`
  - numero non segnato -> `N`

#### 3. Wrapper accessible_output2 gia' presente

Percorso:
[my_lib/vocalizzatore.py](my_lib/vocalizzatore.py)

Forma attuale del wrapper:

- Classe: `Vocalizzatore`
- Costruttore: `__init__(self)` senza parametri
- Inizializzazione interna: `self.speaker = Auto()`
- Metodi esposti:
  - `vocalizza_testo(testo: str)`
  - `vocalizza_numero(numero: int)`
  - `vocalizza_errore(messaggio: str)`
  - `messaggio_inizializzazione()`
  - `messaggio_errore_numeri_terminati()`
  - `messaggio_numero_estratto(numero: int)`
  - `messaggio_reset_tabellone()`
  - `vocalizza_numeri_estratti(numeri: list[int])`
  - `vocalizza_numeri_disponibili(numeri: list[int])`

Conclusione pratica:

- il wrapper esiste e puo' essere iniettato nel futuro `WxRenderer`
- il costruttore oggi non accetta dipendenze esterne
- il renderer wx non deve importare `Auto()` direttamente
- la firma futura del costruttore wx puo' dipendere da `Vocalizzatore`

#### 4. StatoConfigurazione

Ricerca nel codebase: nessuna occorrenza di `StatoConfigurazione`.

Esistono gia' pero' i codici e i testi della configurazione iniziale:

- chiavi in
  [bingo_game/events/codici_configurazione.py](bingo_game/events/codici_configurazione.py)
- testi in
  [bingo_game/ui/locales/it.py](bingo_game/ui/locales/it.py)

Conclusione:

- `StatoConfigurazione` va creato ex novo
- collocazione consigliata:
  [bingo_game/ui/renderers/base_renderer.py](bingo_game/ui/renderers/base_renderer.py)
- forma consigliata: dataclass frozen e esplicita, perche' rappresenta uno stato
  coerente della UI e non un dizionario occasionale

Campi minimi consigliati:

- `fase_corrente`: `"nome" | "bot" | "cartelle" | "conferma"`
- `codice_messaggio`: chiave di `MESSAGGI_CONFIGURAZIONE`
- `codice_errore`: opzionale, sempre chiave di `MESSAGGI_CONFIGURAZIONE`
- `nome_giocatore`: opzionale
- `numero_bot`: opzionale
- `numero_cartelle`: opzionale

#### 5. Chiavi attese per mostra_report_finale

Le chiavi si ricavano da due fonti gia' presenti:

- snapshot dominio in
  [bingo_game/partita.py](bingo_game/partita.py)
- riepilogo finale nel controller in
  [bingo_game/game_controller.py](bingo_game/game_controller.py)

`Partita.get_stato_completo()` fornisce gia' queste chiavi stabili:

- `stato_partita`
- `ultimo_numero_estratto`
- `numeri_estratti`
- `numeri_mancanti`
- `giocatori`
- `premi_gia_assegnati`
- `conteggio_giocatori`

Il controller usa inoltre due valori derivati per il riepilogo:

- `turni_giocati`
- `vincitore_tombola` ricavato dal primo giocatore con `ha_tombola`

Per il contratto del renderer finale sono quindi consigliate come chiavi
obbligatorie del dizionario `dati_partita`:

- `turni_giocati: int`
- `stato_partita: str`
- `numeri_estratti: list[int]`
- `premi_gia_assegnati: list[str]`
- `giocatori: list[dict]`

Chiavi derivate ma utili da documentare nel docstring:

- `conteggio_estratti: int`
- `conteggio_premi: int`
- `vincitore_tombola: str | None`
- `conteggio_giocatori: int`

#### 6. Dipendenze di import future

Per [bingo_game/ui/renderers/base_renderer.py](bingo_game/ui/renderers/base_renderer.py):

- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass`
- `from typing import Literal, Optional`
- `from bingo_game.events.eventi import EsitoAzione`
- `from bingo_game.events.codici_configurazione import Codici_Configurazione`
- `from bingo_game.ui.locales import MESSAGGI_ERRORI, MESSAGGI_EVENTI, MESSAGGI_OUTPUT_UI_UMANI, MESSAGGI_SISTEMA, MESSAGGI_CONFIGURAZIONE`

Per [bingo_game/ui/renderers/renderer_wx.py](bingo_game/ui/renderers/renderer_wx.py):

- `import wx`
- `from my_lib.vocalizzatore import Vocalizzatore`
- `from bingo_game.ui.renderers.base_renderer import BaseRenderer, StatoConfigurazione`
- `from bingo_game.events.eventi import EsitoAzione`
- import di tutte le dataclass evento gia' gestite dal dispatcher terminale

#### 7. Riferimenti attuali a TerminalRenderer

Ricerca nel repository:

- nessun import produttivo di `TerminalRenderer`
- un solo import di test in
  [tests/unit/test_renderer_report_finale.py](tests/unit/test_renderer_report_finale.py)

Questo e' un punto importante per il plan:

- il codice produttivo puo' eliminare `renderer_terminal.py` senza migrazioni di import applicative
- resta pero' un riferimento di test legato al vecchio contratto `Sequence[str]`
- il file di test non va riscritto in questa fase, ma va censito esplicitamente
  come dipendenza futura della rimozione del terminal renderer

#### 8. Rischi e punti di attenzione

- Duplicazione nel dispatcher terminale:
  `EventoReclamoVittoria` appare due volte nel flusso `isinstance`; il secondo
  ramo risulta di fatto irraggiungibile e non va copiato alla cieca nel design wx.
- Il metodo concreto `_formatta_testo_da_catalogo(chiave, **kwargs)` e' stabile
  solo se centralizza davvero il lookup sui cinque dizionari del catalogo.
- `mostra_report_finale(dati_partita: dict)` resta accettabile solo se il
  docstring documenta in modo esplicito le chiavi obbligatorie.
- L'assenza di stringhe hardcoded impone che qualunque testo di fallback venga
  comunque preso da `MESSAGGI_SISTEMA`.

### Raccomandazioni

1. Definire `StatoConfigurazione` come dataclass frozen nello stesso modulo di
   `BaseRenderer`, per evitare un quinto file produttivo in questo ciclo.
2. Fare di `_formatta_testo_da_catalogo()` il punto unico di lookup e formattazione
   dei cinque dizionari del catalogo, con fallback solo verso `MESSAGGI_SISTEMA`.
3. Progettare `WxRenderer` con dispatcher completo, ma con handler ancora stub nel
   ciclo successivo, cosi' da congelare prima l'interfaccia e poi l'implementazione.
4. Registrare nel plan il test
   [tests/unit/test_renderer_report_finale.py](tests/unit/test_renderer_report_finale.py)
   come file impattato dalla rimozione del terminal renderer, pur restando fuori
   scope implementativo immediato.

### File analizzati

- [bingo_game/ui/renderers/renderer_terminal.py](bingo_game/ui/renderers/renderer_terminal.py)
- [bingo_game/ui/renderers/__init__.py](bingo_game/ui/renderers/__init__.py)
- [bingo_game/ui/locales/it.py](bingo_game/ui/locales/it.py)
- [bingo_game/events/codici_configurazione.py](bingo_game/events/codici_configurazione.py)
- [bingo_game/events/eventi.py](bingo_game/events/eventi.py)
- [bingo_game/partita.py](bingo_game/partita.py)
- [bingo_game/game_controller.py](bingo_game/game_controller.py)
- [my_lib/vocalizzatore.py](my_lib/vocalizzatore.py)
- [tests/unit/test_renderer_report_finale.py](tests/unit/test_renderer_report_finale.py)

## Stato Avanzamento

- [x] Bozza completata
- [x] Revisionato
- [x] Condiviso