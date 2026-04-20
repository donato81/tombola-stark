# Registro delle Modifiche

Tutte le modifiche rilevanti a questo progetto sono documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Versionamento Semantico](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Fixed
- Pannello riepilogo finale appare grigio a fine partita: corretto `self.Layout()` → `self._panel.Layout()` (il sizer è sul panel figlio, non sul frame), aggiunti `Hide()` per tutti gli elementi UI che occupavano spazio nel sizer (header, pulsanti, log), aggiunto `self._panel.Refresh()` per ridisegno GDI su Windows, rimosso `wx.CallAfter(SetFocus)` duplicato (`bingo_game/ui/finestra_gioco.py`)

### Added
- Segnazione numeri sulla cartella tramite click sinistro del mouse (bingo_game/ui/finestra_gioco.py)
- Overlay visivo temporaneo del numero estratto per utenti vedenti senza screen reader (`bingo_game/ui/overlay_numero.py`, integrazione in `bingo_game/ui/finestra_gioco.py` e `bingo_game/ui/renderers/renderer_wx.py`)
- Lampeggio visivo del pulsante "Ho finito — avvia verifica" durante la fase `attesa_reclami`: il pulsante alterna cromaticamente tra arancione e giallo-oro (1 Hz) per segnalare all'utente vedente l'azione richiesta a chiusura turno. Nessun impatto su NVDA. (`bingo_game/ui/finestra_gioco.py`, `bingo_game/ui/tema.py`)

## [0.14.0-alpha] — 2026-04-14

### Changed
- Pulizia pre-release alfa: rimosso `bingo_game/utils.py` (file vuoto mai
  importato), rimosso il metodo `Cartella.stampa_cartella()` (mai chiamato,
  bypassa il pattern eventi/renderer), rimossa la costante
  `RECLAMO_ASSENTE` da `bingo_game/events/codici_errori.py` (definita ma mai
  usata nel codice applicativo), rimosse 6 costanti colore non referenziate da
  `bingo_game/ui/tema.py` (`COLORE_MENU_BG_2`, `COLORE_ACCENT_DORATO`,
  `COLORE_VERDE_SCURO`, `COLORE_VERDE_RIPRENDI`, `COLORE_ACCENT_ARANCIONE`,
  `COLORE_ACCENT_VERDE`).

### Fixed
- Corretti 6 test falliti in `tests/unit/test_dialogo_ricerca_persistente.py`:
  le costanti wx (`WXK_RETURN`, `WXK_ESCAPE`, `ID_OK`, `ID_CANCEL`) non erano
  disponibili in ambiente headless; aggiunti fallback numerici nel blocco try
  del file di test.
- Corretti 2 test in `tests/unit/test_comandi_stato_premi.py`:
  `TestDettaglioPremiConPremi` non popolava `storico_premi` su `Partita` prima
  di invocare `dettaglio_premi()`, causando il fallimento delle asserzioni;
  i test ora impostano lo storico correttamente. Adeguata anche la capitalizzazione
  attesa ("Ambo", "Terno") coerente con il comportamento di `.capitalize()`.

### Added
- Spelling cifre doppie post-annuncio estratto (accessibilità NVDA): dopo ogni
  estrazione di un numero a due cifre (10–90), NVDA legge un secondo annuncio
  separato con le singole cifre in forma verbale italiana (es. "Sei. Uno." per 61,
  "Cinque. Zero." per 50). La logica è pura e isolata nella funzione
  `_spelling_numero` di `bingo_game/ui/finestra_gioco.py`; le stringhe verbali
  risiedono in `CIFRE_VERBALI` e `LOOP_SPELLING_NUMERO_ESTRATTO` in
  `bingo_game/ui/locales/it.py`.
- Annuncio posizione focus iniziale dopo il benvenuto NVDA (v0.12.5): dopo il
  messaggio di benvenuto orientativo, un secondo callback differito
  (`wx.CallLater(200, ...)`) invoca `_annuncia_posizione_focus_iniziale`, che
  chiama `self._dispatch(self._comandi.stato_focus())` riutilizzando il path
  event-driven esistente. L'utente sente così la posizione logica iniziale
  (cartella/riga/colonna) come secondo annuncio separato, senza duplicare
  testo posizione nel messaggio di benvenuto
  (`bingo_game/ui/finestra_gioco.py`, test aggiunti in
  `tests/ui/test_finestra_gioco.py`).

### Fixed
- Fix definitivo benvenuto NVDA (v0.12.4): stabilizzato l'ordine di focus
  e parlato all'avvio — `SetFocus` eseguito prima del parlato, annuncio
  differito con `wx.CallLater(350, ...)` e `interrupt=True` per svuotare
  la coda AO2 prima del messaggio orientativo (file interessato:
  `bingo_game/ui/finestra_gioco.py`, test aggiornati in
  `tests/ui/test_finestra_gioco.py`).

- G2-bis: completato ripristino annuncio NVDA di benvenuto all'avvio partita —
  secondo intervento: aggiunto metodo `mostra_messaggio_benvenuto` in `WxRenderer`
  che vocalizza con `interrompi=True`, svuotando la coda NVDA prima del messaggio
  orientativo; rimossa chiamata `SetFocus` dal costruttore di `FinestraGioco` e
  spostata come ultima istruzione di `_imposta_focus_iniziale`, dopo il benvenuto,
  per eliminare gli annunci NVDA nativi che coprivano il messaggio
  (`bingo_game/ui/renderers/renderer_wx.py`, `bingo_game/ui/finestra_gioco.py`).
- G1: aggiunto SetName semantico a PannelloTabellone, PannelloCartella,
  PannelloRiepilogoFinale, HeaderBar e pannello radice — NVDA non legge
  più "panel" generico.
- G2: ripristinato annuncio NVDA di benvenuto all'avvio partita:
  introdotto flag `_avvio_silenzioso` in `FinestraGioco`; i tre dispatch
  iniziali di posizionamento (cartella/riga/colonna) vengono ora eseguiti
  in modalità silenziosa, lasciando la coda AO2 pronta per il messaggio
  orientativo; rimosso il `wx.CallAfter` annidato — `mostra_messaggio_sistema`
  viene chiamato direttamente al termine di `_imposta_focus_iniziale`
  (`bingo_game/ui/finestra_gioco.py`).
- G4: `Ctrl+I` (`dettaglio_premi`) ora legge i vincitori reali di ogni premio
  con testo "Ambo vinto da X, cartella Y." invece della lista di soli tipi.
- G6: `PannelloRiepilogoFinale` ora visualizza i premi leggibili da `storico_premi`
  in ordine logico (ambo → tombola), eliminando l'output "? per ?".

### Added
- G5: introdotto `Partita.storico_premi: list[dict]` valorizzato in tempo reale
  durante ogni assegnazione premi; ogni record include `giocatore`, `id_giocatore`,
  `cartella`, `premio`, `riga`, `turno`.
- G3: `dati_report` arricchito con `storico_premi`, `numeri_estratti` e
  `riepilogo_umano` (numeri segnati, premi vinti del giocatore umano).
  Il testo vocalizzato a fine partita non contiene più stringhe opache.
- `FinestraGuidaRegole`: nuovo `wx.Dialog` modale con cinque capitoli di regole
  del gioco navigabili (Precedente / Successivo). Apertura con `Ctrl+Shift+H` da
  `FinestraGioco` e da voce menu Guida / pulsante Guida in `FinestraPrincipale`.
  Chiusura con `Escape` o pulsante Chiudi; focus iniziale sul `wx.TextCtrl` del
  capitolo 1; al cambio pagina NVDA legge il titolo del capitolo via `wx.CallAfter`.
- `bingo_game/ui/locales/it_guida.py`: modulo locale con `GUIDA_CAPITOLI`
  (5 capitoli, testi definitivi con accenti) e `GUIDA_UI` (etichette pulsanti
  e template pagina). Struttura `Sequence[tuple[str, tuple[str, ...]]]` + `MappingProxyType`.
- `finestra_gioco.py`: hotkey `Ctrl+Shift+H` aggiunta (categoria C) per aprire
  `FinestraGuidaRegole`; hotkey `Ctrl+H` ristretta a `not shift` per evitare
  conflitto.
- `finestra_principale.py`: metodo `_on_guida` implementato (sostituisce
  il placeholder) — apre `FinestraGuidaRegole` in modale.
- `finestra_aiuto_tasti_rapidi.py`: aggiunta riga `Ctrl+Shift+H` nel testo
  categoria C, dopo la riga `Ctrl+H`.

---

## [0.13.0] — 2026-04-13

### Added
- `FinestraAiutoTastiRapidi`: nuovo `wx.Dialog` modale con elenco statico
  tasti rapidi (35 binding), apribile con `Ctrl+H` da `FinestraGioco`.
  Chiusura con `Escape` o pulsante Chiudi, focus iniziale sul `wx.TextCtrl`
  read-only, ripristino focus su `PannelloGriglia` alla chiusura.
- Header Bar visiva in cima a FinestraGioco (turno, ultimo estratto, premi)
- Colori semantici sui pulsanti principali (verde/blu/arancione/grigio per fase)
- Animazione lampeggio post-estrazione sulla cella cartella (~2 secondi, wx.Timer)
- Stile visivo scuro sul log annunci (sfondo #263238, testo #B0BEC5, Courier New 10pt)

### Changed
- bingo_game/ui/finestra_principale.py: applicato stile visivo del menu principale con titolo, sottotitolo NVDA, pulsanti tematizzati e acceleratori Ctrl+N, Ctrl+I, Ctrl+G, Ctrl+Q; aggiornata coerentemente la dimensione finestra in bingo_game/ui/tema.py a 400x380.
- bingo_game/ui/finestra_configurazione.py: bot e cartelle da SpinCtrl a wx.Choice (selezione da lista, nessun input libero); applicato stile visivo completo (sfondo, etichette colorate, titolo bold blu, pulsante Avvia verde, messaggio errore rosso); DIMENSIONE_FINESTRA_CONFIGURAZIONE aggiornata da 500×430 a 500×460 in tema.py.

---

## [0.12.1] — 2026-04-12

### Fixed — Accessibilita Tab navigazione (v0.12.1)

- `bingo_game/ui/finestra_gioco.py`: `PannelloGriglia._on_key_down` gestisce ora
  esplicitamente `WXK_TAB` e `Shift+WXK_TAB` chiamando `self.Navigate(IsForward)`
  / `Navigate(IsBackward)`; il flag `wx.WANTS_CHARS` intercettava Tab senza cedere
  il focus al ciclo `TAB_TRAVERSAL`, rendendo irraggiungibili con Tab tutti i
  pulsanti della finestra (frecce cartella, selezione, premi).
- `bingo_game/ui/finestra_gioco.py`: `_crea_pulsanti_selezione_cartella` chiama ora
  `MoveAfterInTabOrder` dopo la creazione dinamica dei pulsanti `1..N`; i pulsanti
  vengono posizionati immediatamente dopo `_btn_freccia_dx` nell'ordine Tab,
  eliminando il posizionamento errato in fondo al ciclo focus causato dalla
  creazione tardiva al primo turno.

### Fase 2 — Pulsanti interattivi

- `bingo_game/ui/finestra_gioco.py`: aggiunto Gruppo 1 — pulsanti freccia `◀` `▶` ai
  lati del `PannelloCartella` per navigazione via mouse tra le cartelle
  (`cartella_precedente` / `cartella_successiva`); abilitati durante la partita attiva,
  disabilitati a fine partita e in pausa.
- `bingo_game/ui/finestra_gioco.py`: aggiunto Gruppo 2 — riga di pulsanti `1`…`N` per
  selezione diretta cartella, creati dinamicamente al primo avvio della partita
  (`_crea_pulsanti_selezione_cartella`); evidenziazione blu sul pulsante della
  cartella corrente (`aggiorna_selezione_cartella` / `_aggiorna_evidenziazione_selezione`).
- `bingo_game/ui/finestra_gioco.py`: aggiunto Gruppo 3 — pulsanti `Ambo`, `Terno`,
  `Quaterna`, `Cinquina`, `Tombola` per dichiarazione premi; abilitati solo in fase
  `attesa_reclami`, disabilitati con label ` ✓` per premi già assegnati definitivamente.
- `bingo_game/ui/renderers/renderer_wx.py`: in `_handle_focus_cartella_impostato`
  aggiunta chiamata duck typing `aggiorna_selezione_cartella` per aggiornare
  l'evidenziazione visiva del pulsante cartella corrente.

### Added
- `bingo_game/ui/finestra_gioco.py`: collega le griglie visive allo stato dinamico della partita (v0.11.1)
- `bingo_game/ui/tema.py`: nuovo modulo con tutte le costanti visive (colori, font, dimensioni)
  usate dall'interfaccia grafica; aggiunge `DIMENSIONE_CELLA_TABELLONE` e `DIMENSIONE_CELLA_CARTELLA`
  per le griglie di gioco.
- `bingo_game/ui/finestra_gioco.py`: nuove classi `PannelloTabellone` (griglia 9×10, numeri 1-90)
  e `PannelloCartella` (griglia 9×3, 15 numeri placeholder), entrambe non focalizzabili e colorate
  con le costanti di `tema.py`; integrate in `FinestraGioco._build_ui` affiancate orizzontalmente.
- `bingo_game/ui/finestra_gioco.py`: dimensione finestra di gioco aggiornata da 700×500 a
  1000×700 (da `DIMENSIONE_FINESTRA_GIOCO` in `tema.py`).
- `bingo_game/ui/finestra_gioco.py`: `PannelloTabellone.aggiorna()` e `PannelloCartella.aggiorna()`
  collegano le griglie visive allo stato live della partita; `_aggiorna_griglie_visive()` viene
  chiamato automaticamente dopo ogni estrazione, dopo la verifica premi e all'avvio del gioco.
- `bingo_game/ui/renderers/renderer_wx.py`: `_wx_aggiorna_tabellone()` e `_wx_aggiorna_cartella()`
  implementati (via duck typing su `pannello_tabellone` e `pannello_cartella`); aggiunto
  `_indice_cartella_corrente` allo stato interno; `_handle_visualizza_cartella_semplice` e
  `_handle_visualizza_cartella_avanzata` chiamano ora `_wx_aggiorna_cartella` dopo `_wx_aggiorna_output`.
- `bingo_game/ui/renderers/renderer_wx.py`: sincronizzazione visiva in tempo reale (Fase 5):
  `_handle_focus_cartella_impostato` e `_handle_segnazione_numero` (solo esito `segnato`) chiamano
  `_wx_aggiorna_cartella()` che delega a `_finestra._aggiorna_griglie_visive()` per aggiornare
  `PannelloCartella` immediatamente dopo cambio cartella o segnazione riuscita.
  - Aggiornamento Fase 4: miglioramenti runtime — aggiunti logging diagnostico e
    normalizzazione input in `_wx_aggiorna_tabellone` e `_wx_aggiorna_cartella`.

## [0.10.0] — 2026-04-11

### Fixed
- `bingo_game/ui/finestra_gioco.py`: il tasto rapido `F6` nella griglia richiama ora correttamente `self._renderer.ripeti_ultimo_annuncio()` dal frame di gioco; prima tentava di accedere a `fg._finestra._renderer` e generava `AttributeError`, lasciando NVDA silente.
- `bingo_game/ui/renderers/renderer_wx.py`: `Ctrl+Shift+V` ora costruisce e vocalizza il contenuto avanzato completo di tutte le cartelle, inclusa l'evidenziazione dei numeri segnati; prima annunciava solo il conteggio delle cartelle senza leggerne alcuna.
- `bingo_game/ui/finestra_gioco.py`: all'avvio del frame di gioco il focus logico viene impostato automaticamente su cartella 1, riga 1, colonna 1 tramite `wx.CallAfter(_imposta_focus_iniziale)`; in precedenza NVDA non annunciava la cella iniziale e le frecce non producevano feedback fino al primo clic.
- `bingo_game/ui/finestra_gioco.py`: gli avvisi vocali del timer di reclamo (60 %, 80 %, 95 %) non vengono più emessi dopo che il giocatore umano ha già dichiarato la fine del proprio turno; il guard in `_on_tick_azione` chiama `_on_timeout_azione()` se il tempo è scaduto e poi ritorna senza emettere notifiche.
- `bingo_game/ui/finestra_gioco.py`: il passaggio del turno di ogni bot viene ora annunciato tramite `mostra_messaggio_sistema` ("<NomeBot> ha passato il turno.") prima di chiamare `_controlla_tutti_pronti`; in precedenza il turno bot era silente per NVDA.
- `bingo_game/comandi_partita.py`: aggiunto metodo pubblico `ComandiGiocatoreUmano.turno_gia_dichiarato()` per permettere al layer di presentazione di interrogare se il giocatore umano ha già dichiarato la fine del turno di reclamo; evita condizioni di race e semplifica la logica di abilitazione dei suggerimenti (hotkey/feedback).
- `bingo_game/ui/finestra_gioco.py`, `bingo_game/ui/dialogo_ricerca.py`: corretto il feedback legato alla hotkey `Ctrl+P` durante la fase `attesa_reclami` e reso `DialogoRicerca` persistente fino a chiusura esplicita; risolve il comportamento di feedback mancante e la chiusura involontaria del dialog durante l'interazione.
- `bingo_game/ui/finestra_gioco.py`: alla fine della pausa tra turni il frame riavvia automaticamente la stessa logica di estrazione del pulsante principale, evitando che il ciclo V2 resti fermo in attesa di un click manuale.
- `bingo_game/ui/finestra_gioco.py`: introdotta una protezione esplicita di mutua esclusione tra timer della finestra d'azione e timer della pausa; ogni transizione ora ferma sempre l'eventuale timer precedente prima di avviarne uno nuovo.
- `bingo_game/comandi_partita.py`: aggiunto metodo `ComandiSistema.ottieni_giocatore_umano(partita)` — era assente dalla facade pur essendo la funzione corrispondente già importata da `game_controller`; causava `AttributeError` nel ciclo turno V2 quando il layer UI lo invocava tramite `ComandiSistema`.

- `bingo_game/players/giocatore_umano.py`: corretto un bug per cui il reclamo di vittoria del giocatore umano (ambo, terno, quaterna, cinquina, tombola) veniva ignorato silenziosamente ogni turno. La causa era che il sistema cercava la cartella del giocatore tramite un numero sbagliato (0 anziché 1), non la trovava, e scartava il reclamo senza produrre alcun messaggio di errore. Di conseguenza, nella co-vincita il premio veniva assegnato solo al bot. Ora il reclamo usa il numero identificativo corretto della cartella e il premio viene assegnato a tutti i co-vincitori.


- `bingo_game/ui/renderers/renderer_wx.py`: modalità avanzata NVDA — il testo "Avanzata" è ora la prima parola pronunciata (prima era troncato dopo "Riga N"); i numeri segnati usano il token "N segnato" al posto di "[N]" (parentesi quadre silenti con NVDA); aggiunto conteggio segnati da `stato_riga`/`stato_colonna` nel messaggio breve; corretti `_handle_vai_a_riga_avanzata` e `_handle_vai_a_colonna_avanzata` che non esponevano la label "Avanzata".
- `bingo_game/ui/finestra_gioco.py`: rimossa l'opzione `wx.TE_AUTO_SCROLL` non supportata da wxPython Phoenix; il frame di gioco ora si istanzia correttamente dopo `Avvia partita`.
- `bingo_game/ui/finestra_gioco.py`: corretto il parent di `PannelloGriglia` per renderlo coerente con il `wx.Panel` gestito dal sizer della finestra di gioco; eliminata l'assertion wx durante il caricamento del frame.
- `bingo_game/players/helper_focus.py`: la navigazione tastiera auto-seleziona di nuovo la prima cartella disponibile quando il focus cartella non è ancora impostato; eliminato il falso errore ricorrente `Non hai selezionato nessuna cartella` al primo movimento.
- `bingo_game/comandi_partita.py`: rimossi gli stub duplicati in `ComandiGiocatoreUmano` che sovrascrivevano la facade reale di `segna_numero(numero)` e rompevano la segnazione manuale dal layer wx.

### Changed
- `bingo_game/ui/finestra_gioco.py`: hotkey passa-turno spostata da `Ctrl+P` a `Ctrl+Enter` per maggiore ergonomia d'uso continuato da tastiera; aggiunta costante modulo `_KEY_RETURN` per robustezza in ambienti di test con stub wx parziale.
- `my_lib/vocalizzatore.py`: refactor strutturale R2 — introdotti `IVocalizzatore` (Protocol), `NullVocalizzatore` (no-op headless-safe), backend iniettabile nel costruttore di `Vocalizzatore`, protezione best-effort `try/except` in `vocalizza_testo`, inoltro di `interrompi` come `interrupt=` verso AO2; rimossi 9 metodi dead code.
- `bingo_game/ui/renderers/renderer_wx.py`: type hint del parametro `vocalizzatore` e dell'attributo `_vocalizzatore` aggiornati da `Vocalizzatore` a `IVocalizzatore` per dependency inversion.
- `bingo_game/ui/renderers/renderer_wx.py`: introdotto stato locale per ultimo annuncio e log, feedback runtime per eventi principali, duck typing verso i frame wx e supporto operativo a F6 e Ctrl+E.
- `bingo_game/comandi_partita.py`: `ComandiGiocatoreUmano` non e' piu' un placeholder; ora espone una facade dei comandi del giocatore umano per il layer di presentazione.
- `docs/API.md` e `docs/ARCHITECTURE.md`: sincronizzate con l'entry point wx attivo e con i nuovi componenti frame/dialog della UI.
- Pausa di gioco (v1.2.0): la documentazione del presentation layer ora descrive la pausa UI-only con binding `Ctrl+P`, pulsante "Pausa", visualizzazione del timer residuo e annuncio completo alla ripresa.
- `bingo_game/tabellone.py`: allineamento formale del modulo (type hints, docstring) senza modifiche logiche; unit tests eseguiti con successo (329 passed, 0 failed).
- `bingo_game/tabellone.py`: sostituito `ValueError` con `TabelloneNumeriEsauritiException` nel caso di numeri esauriti, mantenendo invariato il messaggio testuale e la logica di gioco.
- `bingo_game/partita.py`: aggiornato il blocco di intercettazione dell'estrazione per tradurre `TabelloneNumeriEsauritiException` in `PartitaNumeriEsauritiException` senza cambiare il comportamento runtime.

### Added
- `bingo_game/ui/dialogo_ricerca.py`: nuova classe `DialogoRicercaNumero` — dialog persistente di ricerca numero che vocalizza i risultati; non utilizza più una chiusura automatica: quando trova risultati rimane aperto, abilita un pulsante esplicito `Vai al risultato` e attende la conferma dell'utente.
- `bingo_game/events/codici_eventi.py`: aggiunte costanti `PAUSA_ATTIVATA`, `PAUSA_DISATTIVATA` per notifiche strutturate della pausa.
- `bingo_game/ui/renderers/base_renderer.py`: aggiunto metodo `annuncia_pausa(self, testo: str) -> None` nel contratto del renderer per supportare l'annuncio di pausa/ripresa.
- `bingo_game/ui/finestra_gioco.py`: aggiunto pulsante "Pausa" e binding `Ctrl+P`; la UI gestisce il timer residuo della finestra di azione, sospende le azioni durante la pausa e invia l'annuncio completo al resume.
- `bingo_game/ui/finestra_gioco.py`: apre `DialogoRicercaNumero` in modalità modale e, se il dialog ritorna `wx.ID_OK` con `_primo_risultato` valorizzato (l'utente ha premuto `Vai al risultato`), naviga al primo risultato tramite `_naviga_a_risultato_ricerca()` migliorando l'esperienza accessibile di ricerca.
- `tests/unit/test_ciclo_turno_v2_azioni_2_3.py`: nuova suite unitaria dedicata ad Azione 2 e Azione 3 del Ciclo Turno V2; copre riavvio automatico dopo la pausa e arresto esplicito dei timer concorrenti.
- `tests/unit/test_vocalizzatore.py`: suite unittest per `my_lib/vocalizzatore.py`; 8 test su `NullVocalizzatore` e `Vocalizzatore` con backend fake iniettabile; nessun patch su AO2.
- `bingo_game/exceptions/tabellone_exceptions.py`: introdotta `TabelloneNumeriEsauritiException` come eccezione di dominio specifica del tabellone.
- `tests/unit/test_tabellone_eccezioni.py`: nuovo test unittest dedicato alla verifica del tipo di eccezione e del messaggio per il caso di numeri esauriti del tabellone.
- `main.py`: avvia `wx.App`, `Vocalizzatore`, `WxRenderer` e `FinestraPrincipale` come nuovo entry point wx dell'applicazione.
- `bingo_game/ui/finestra_principale.py`, `bingo_game/ui/finestra_configurazione.py`, `bingo_game/ui/finestra_gioco.py`, `bingo_game/ui/dialogo_ricerca.py`: aggiunti frame/dialog principali di presentazione per l'interfaccia wx.

### Added
- `FinestraPrincipale`: nuovo frame wxPython con menu principale (Nuova partita, Impostazioni, Guida, Esci); primo punto di ingresso dell'applicazione dopo l'avvio

### Changed
- `main.py`: apre `FinestraPrincipale` come prima finestra invece di `FinestraConfigurazione`
- `FinestraConfigurazione`: aggiunto parametro `parent_frame` a `__init__` per propagare il riferimento al menu principale verso `FinestraGioco`
- `FinestraGioco`: aggiunto parametro `finestra_principale` a `__init__` e pulsante "Torna al menu principale" (visibile solo a partita terminata)

### Added
- `tests/unit/test_fase_estrazione.py`: test unitario per la fase di estrazione (ciclo bifasico)
- `tests/unit/test_fase_verifica_co_vincita.py`: test unitario per la fase di verifica e risoluzione reclami collettivi
- `tests/unit/test_umano_dichiara_fine_turno.py`: test che simula la dichiarazione manuale di fine turno da parte di un giocatore umano

### Changed
- `bingo_game/partita.py`: introdotti `esegui_fase_estrazione()`, `esegui_fase_verifica()` e `tutti_hanno_dichiarato_fine()`; aggiornato il comportamento per la gestione dei reclami collettivi e della co-vincita nello stesso turno.
-### Added
- `bingo_game/players/giocatore_base.py`: piccolo aggiornamento di API per supportare `reset_reclamo_turno()` nel contesto dei reclami collettivi.
- `bingo_game/ui/renderers/base_renderer.py` / `bingo_game/ui/renderers/renderer_wx.py`: estesi i contratti renderer con i metodi `annuncia_numero_estratto`, `annuncia_premi_turno` e `annuncia_fase_turno` per supportare l'orchestrazione accessibile del flusso bifasico.
- `docs/API.md`, `docs/ARCHITECTURE.md`: aggiornati per documentare il nuovo flusso bifasico del turno, le nuove API pubbliche e l'impatto sul layer di presentazione/accessibilità.

---

## [0.9.5] — 2026-03-30

### Added
- `tests/unit/test_validazioni_input.py`: suite unittest diretta per `bingo_game/validations/validazioni_input.py`; 29 test su 6 funzioni (esito_numero_intero, esito_numero_in_range_1_90, esito_numero_riga_in_range_1_3, esito_numero_colonna_in_range_1_9, esito_reclamo_turno_libero, esito_tipo_vittoria_supportato).
- `tests/unit/test_validazione_oggetti.py`: suite unittest diretta per `bingo_game/validations/validazione_oggetti.py`; 9 test su 2 funzioni (esito_tabellone_disponibile, esito_coordinate_numero_coerenti); usa MagicMock per stub duck-typed.

---

## [0.9.4] — 2026-03-30

### Added
- `bingo_game/ui/renderers/base_renderer.py`: introduce il contratto astratto del layer di presentazione con `BaseRenderer` e lo stato immutabile `StatoConfigurazione` per il flusso di configurazione.
- `bingo_game/ui/renderers/renderer_wx.py`: aggiunge `WxRenderer`, prima implementazione concreta del renderer accessibile con dependency injection di `wx.Frame` e `Vocalizzatore`.
- `tests/unit/test_codici_eventi.py`: aggiunto nuovo test di Gruppo A (unittest TestCase; validazione: 66/66 passati, coverage 100% sui moduli Gruppo A).
- `tests/unit/test_eventi_ui.py`: aggiunti test di Gruppo B per `bingo_game/events/eventi_ui.py` (unittest; verifica delle dataclass `EventoFocusAutoImpostato` e `EventoFocusCartellaImpostato`).
- `tests/unit/test_eventi_partita.py`: aggiunti test di Gruppo C per `bingo_game/events/eventi_partita.py` (unittest; copertura delle dataclass `ReclamoVittoria`, `EventoReclamoVittoria`, `EventoEsitoReclamoVittoria`, `EventoFineTurno`).
- `tests/unit/test_esito_azione.py`: aggiunto nuovo test di Gruppo D per `bingo_game/events/eventi.py` che verifica il comportamento di `EsitoAzione` e le sue comparazioni test-friendly con stringhe.
- `tests/unit/test_eventi_output_cartella.py`, `tests/unit/test_eventi_output_navigazione.py`, `tests/unit/test_eventi_output_tabellone.py`, `tests/unit/test_eventi_output_segnazione.py`, `tests/unit/test_eventi_output_bulk_focus.py`: aggiunti i test del Gruppo E per `bingo_game/events/eventi_output_ui_umani.py` (suddivisi E1–E5); validazione: 100/100 passati. Nota: due rischi residui non bloccanti su edge-case duck-typing `Cartella` nei factory methods.

### Changed
- `requirements.txt`: aggiorna versioni dipendenze per Python 3.11 e aggiunge `accessible-output2`.
- `bingo_game/ui/renderers/__init__.py`: esporta il nuovo perimetro pubblico del package renderer (`BaseRenderer`, `StatoConfigurazione`, `WxRenderer`).
- `docs/API.md` e `docs/ARCHITECTURE.md`: sincronizzano la documentazione con il nuovo layer di presentazione wx e con il contratto renderer effettivamente implementato.
- `bingo_game/events/eventi.py`: la documentazione e il comportamento pubblico di `EsitoAzione.__eq__` sono stati allineati; `EsitoAzione` supporta confronti con `str` (mapping di alcuni codici errore a messaggi legacy) per compatibilità con test esistenti.
 - `bingo_game/comandi_partita.py`: espone `ComandiGiocatoreUmano` come facade pubblico per il layer di presentazione.
 - `bingo_game/ui/renderers/renderer_wx.py`: estende il renderer con buffer per l'ultimo annuncio (F6), feedback base eventi e binding di tasti (es. F6, Ctrl+E) mantenendo duck-typing verso il frame.

### Removed
- `bingo_game/ui/renderers/renderer_terminal.py`: rimuove il renderer terminale legacy dal perimetro architetturale corrente.

---

## [0.9.3] — 2026-03-29

### Fixed
- `main.py`: sostituisce l'import rotto di `TerminalUI` con un placeholder
  temporaneo; il programma torna avviabile con messaggio informativo sullo
  stato di transizione verso la nuova interfaccia.
- `tests/test_giocatore_umano.py`: modernizza i 20 test di navigazione riga su
  `EsitoAzione`, `EventoNavigazioneRiga` ed `EventoNavigazioneRigaAvanzata`,
  eliminando i confronti fragili su testo renderizzato e preservando la suite
  `unittest` verde; in validazione viene corretto anche un test legacy su
  `sposta_focus_colonna_sinistra_avanzata` ancora ancorato alla parola `vuota`.
 - `tests/test_giocatore_umano.py`: tranche 2 — modernizza 8 test legacy del
   gruppo "colonna sinistra" e stabilizza il blocco avanzato già strutturato
   (`test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni`),
   validazione: 67 test OK sul file, 366 test OK sulla suite completa.
 - `tests/test_giocatore_umano.py`: tranche 3 — modernizza i test del gruppo
   "colonna destra" (base + avanzata, 11 test aggiornati), sostituendo assertion
   su testo renderizzato con assertion strutturate su `EsitoAzione`,
   `EventoNavigazioneColonna` ed `EventoNavigazioneColonnaAvanzata`. Verifica
   finale: 67 test OK su `tests/test_giocatore_umano.py` (file target), 366 test
   OK sulla suite completa, 1 test skipped. Report e artefatti associati:
   `docs/4 - reports/REPORT_FIX_TEST_COLONNA_DESTRA_EVENTI_2026-03-29.md`,
   `docs/3 - coding plans/PLAN_fix_test_colonna_destra_eventi_v1.md`,
   `docs/2 - projects/DESIGN_fix_test_colonna_destra_eventi.md`.

- `tests/test_giocatore_umano.py`: rifinitura finale — completa la correzione di
  tre test avanzati di navigazione colonna (2 destra, 1 sinistra), consolidando
  le asserzioni su `EsitoAzione` e rendendo deterministico il setup dei casi con
  numeri segnati; verifica finale: 67/67 OK sul file target, 366/366 OK sulla
  suite completa. Artefatti associati:
  `docs/4 - reports/REPORT_FIX_TEST_DESTRA_AVANZATA_RIFINITURA_2026-03-29.md`,
  `docs/3 - coding plans/PLAN_fix_test_destra_avanzata_rifinitura_v1.md`,
  `docs/2 - projects/DESIGN_fix_test_destra_avanzata_rifinitura.md`.

---

## [0.9.2] — 2026-03-28

### Added
- `docs/4 - reports/REPORT_ANALISI_STATO_2026-03-27.md`: aggiunge report di analisi
  stato progetto con roadmap prioritizzata (v0.11.0 → v2.0.0+).
- `docs/4 - reports/REPORT_ANALISI_CONVERSIONE_TEST_PYTEST_UNITTEST_2026-03-28.md`:
  aggiunge il findings report per la conversione dei test pytest non verdi verso
  unittest standard, con batch di priorita, dipendenze e rischi.
- `docs/2 - projects/DESIGN_conversione_test_pytest_unittest.md`: aggiunge il
  documento di design della migrazione pytest → unittest, con strategia di
  uniformita, batching e criteri di accettazione.
- `docs/3 - coding plans/PLAN_conversione_test_pytest_unittest_v0.9.0.md`:
  aggiunge il piano operativo READY per la conversione incrementale dei test in
  sette fasi, dalla baseline alla validazione finale.
- `docs/5 - todolist/TODO_conversione_test_pytest_unittest_v0.9.0.md`:
  aggiunge la checklist operativa associata al piano di conversione dei test.
- `docs/5 - todolist/README.md`: aggiunge il README della cartella canonica per i
  TODO operativi, allineato al validatore documentale.
- `docs/4 - reports/REPORT_FIX_UNICODE_PRINT_2026-03-28.md`: aggiunge analisi
  mirata del fix P1 su `print()` con emoji (`comandi_partita.py`,
  `test_game_controller.py`) con inventario righe e impatto suite.
- `docs/2 - projects/DESIGN_fix_unicode_print.md`: aggiunge design della
  rimozione pura dei `print()` Unicode nel perimetro applicativo/test,
  con vincoli e criteri di accettazione.
- `docs/3 - coding plans/PLAN_fix_unicode_print_v0.9.1.md`: aggiunge piano
  operativo v0.9.1 per baseline, due fix incrementali e validazione finale.
- `docs/5 - todolist/TODO_fix_unicode_print_v0.9.1.md`: aggiunge checklist
  esecutiva READY allineata al piano `PLAN_fix_unicode_print_v0.9.1.md`.

### Fixed
- `bingo_game/comandi_partita.py`, `tests/test_game_controller.py`: rimuove i
  `print()` con emoji Unicode che causavano `UnicodeEncodeError` su Windows e
  ripristina la suite `unittest` verde (351 test OK).

### Changed
- `CHANGELOG.md`, `docs/API.md`, `docs/ARCHITECTURE.md`, `README.md`: riallinea la
  documentazione pubblica allo stato post-rimozione TUI senza riscrivere la
  cronologia delle release gia' versionate.
- `tests/test_silent_controller.py`: completa la migrazione pytest -> unittest con
  TestCase, setUp, helper `_build_*`, cattura stdout via `io.StringIO` e
  `self.assertRaises`; il TODO `migrazione_test_silent_controller_unittest`
  passa a `COMPLETED`.
- `tests/test_silent_controller.py`: migrazione completata e validata; eseguiti
  i test con `python -m unittest tests.test_silent_controller` (v0.9.1).
- `tests/test_silent_controller.py`: porta le classi a `unittest.TestCase` e converte gli `assert` a `assert` di `unittest`.
- `tests/test_silent_controller.py`: sostituisce fixture pytest con setUp/_build_* e usa patch di `sys.stdout` per la cattura stdout.
- `docs/TODO.md`: aggiornato il coordinatore documentale con i riferimenti al nuovo
  report di analisi, al DESIGN, al PLAN e al TODO della feature
  `conversione_test_pytest_unittest`.
- `docs/todo.md`: aggiornato il coordinatore documentale con i riferimenti a
  `DESIGN_fix_unicode_print.md`, `PLAN_fix_unicode_print_v0.9.1.md`,
  `REPORT_FIX_UNICODE_PRINT_2026-03-28.md` e
  `TODO_fix_unicode_print_v0.9.1.md`.
- `docs/todo.md`: aggiunge i link a design, piano e todo della migrazione
  `test_silent_controller` verso `unittest`.
- `docs/2 - projects/DESIGN_migrazione_test_silent_controller_unittest.md`,
  `docs/3 - coding plans/PLAN_migrazione_test_silent_controller_unittest_v0.9.1.md`,
  `docs/5 - todolist/TODO_migrazione_test_silent_controller_unittest_v0.9.1.md`:
  definisce analisi, strategia e checklist operative con stop prima del coding.
- `tests`: converte i batch 3, 4 e 5 della migrazione pytest → unittest e chiude
  la validazione finale con `python -m unittest discover` verde (303 test OK, 1 skip).
- `docs/3 - coding plans/PLAN_conversione_test_pytest_unittest_v0.9.0.md`:
  avanzato lo stato del piano fino a `COMPLETED` dopo l'esecuzione sequenziale
  delle fasi 3, 4, 5 e 6.
- `docs/5 - todolist/TODO_conversione_test_pytest_unittest_v0.9.0.md`:
  chiusa la checklist operativa con baseline finale `unittest discover`
  (303 OK, 1 skipped, 0 failure, 0 error).
- `tests/test_partita.py`: allinea il confronto tra stato sintetico e completo al
  subset comune di chiavi pubbliche, evitando una regressione su snapshot con ruoli diversi.
- `tests/flow/test_flusso_game_loop.py`, `tests/test_silent_controller.py`: rimuove
  la dipendenza import-time da pytest nei moduli legacy che bloccavano la discovery finale.
- `docs/API.md`: aggiornato a [Unreleased] (2026-03-27); aggiunta sezione
  `GiocatoreUmano` con `imposta_focus_cartella_fallback()` (v0.9.1) e
  `visualizza_ultimi_numeri_estratti()` (v0.10.0).
- `docs/ARCHITECTURE.md`: aggiornato a [Unreleased] (2026-03-27); struttura
  directory allineata alla nuova cartella `docs/` e fotografia architetturale
  aggiornata sul layer di presentazione post-rimozione TUI.
- `documentations/`: aggiunge design, piano, TODO del refactor Partita/GameController e report di analisi qualitativa.
- `CHANGELOG.md`: aggiornamento sezione [Unreleased] per includere i nuovi miglioramenti di stato e reporting del refactor.
- `bingo_game/game_controller.py`: il controller non mantiene piu' un conteggio premi duplicato; il riepilogo premi viene derivato dallo snapshot di `Partita`, mantenendo il dominio come owner dello stato di gioco.
- `bingo_game/partita.py`: aggiunto `get_stato_sintetico()` come snapshot pubblico primario dello stato di partita; `get_stato_completo()` delega allo stesso punto di costruzione.
- `bingo_game/game_controller.py`: `ottieni_stato_sintetico()` delega a `Partita.get_stato_sintetico()` e conserva solo guardie, validazione minima e logging di bordo.
- `bingo_game/game_controller.py`: `ottieni_stato_sintetico()` riduce le validazioni semantiche ridondanti e mantiene solo il bordo minimo su parametro, eccezioni interne, tipo dizionario e chiavi obbligatorie.
- `tests/test_game_controller.py`: aggiunge una regressione che fissa la delega dello snapshot premi tra `Partita` e `GameController`.
- `tests/test_game_controller.py`, `tests/test_partita.py`: consolidano il contratto del riepilogo sintetico e la coerenza tra snapshot di `Partita` e facade del controller.
- `tests/test_game_controller.py`: caratterizza il bordo residuo di `ottieni_stato_sintetico()` e documenta quali controlli restano al controller dopo la semplificazione.
- `bingo_game/players/giocatore_umano.py`: metodo rinominato da
  `visualizzaultiminumeriestratti` a `visualizza_ultimi_numeri_estratti`
  (conformita snake_case).
- `bingo_game/game_controller.py`: aggiunta Sezione 4 (v0.11.0) — 6 funzioni wrapper
  (`imposta_focus_cartella`, `imposta_focus_cartella_fallback`, `esegui_azione_giocatore`,
  `esegui_azione_giocatore_con_numero`, `stato_focus_corrente`, `riepilogo_cartella_corrente`)
  e 2 frozenset (`_METODI_CON_TABELLONE`, `_METODI_PROMPT_CON_TABELLONE`) come unica
  interfaccia autorizzata tra layer di presentazione e domain layer.

### Removed
- `documentations/`: rimossa la cartella legacy; tutta la documentazione
  migrata nella nuova struttura `docs/` (templates, projects, coding plans,
  reports, todo list, API.md, ARCHITECTURE.md).
- Riferimenti correnti alla TUI nella sezione `[Unreleased]`: rimossi i richiami
  a game loop, tasti rapidi via `msvcrt` e test TUI non piu' presenti nel
  repository dopo la rimozione dell'interfaccia terminale.
- Parsing comandi testuali (seguito da Invio) rimosso dal game loop principale.
  Il loop v0.10.0 usa esclusivamente `leggi_tasto()` via msvcrt.

---

## [v0.9.1] — 2026-02-21

### Fixed
- **Bug 1** (`bingo_game/players/giocatore_umano.py`): corretto `AttributeError` in `imposta_focus_cartella()` — la chiamata interna usava `self.reset_focus_riga_e_colonna()` (senza underscore) invece di `self._reset_focus_riga_e_colonna()`. Il focus non veniva mai impostato all'avvio della partita.
- **Bug 3** (`bingo_game/ui/tui/tui_partita.py`): aggiunto fallback esplicito in `_loop_partita()` — se `imposta_focus_cartella(1)` fallisce e il giocatore ha esattamente 1 cartella, il focus viene ora impostato tramite `imposta_focus_cartella_fallback()`.
- **Bug 2** (`bingo_game/ui/tui/tui_partita.py`): il comando `s` senza argomento ora chiede il numero interattivamente con prompt `"Quale numero vuoi segnare? (1-90):"` invece di restituire immediatamente errore.
- **Anomalia A** (`bingo_game/players/giocatore_umano.py`): corretto `AttributeError` latente in `sposta_focus_riga_giu_avanzata()` — la chiamata usava `self._inizializza_focus_riga_se_manca()` (metodo inesistente) invece di `self._esito_inizializza_focus_riga_se_manca()`.

### Refactored
- **Anomalia B** (`bingo_game/players/helper_focus.py`, `bingo_game/ui/tui/tui_partita.py`): sostituito accesso diretto all'attributo privato `_indice_cartella_focus` dal layer UI con il nuovo metodo pubblico `imposta_focus_cartella_fallback()`, ripristinando il rispetto del vincolo architetturale.
- **Anomalia C** (`bingo_game/ui/locales/it.py`, `bingo_game/ui/renderers/renderer_terminal.py`): corretto typo `AVVANZATA` → `AVANZATA` in tutte le chiavi di `MESSAGGI_OUTPUT_UI_UMANI` e nelle relative occorrenze nel renderer e nei test.

### Tests
- Aggiunto test per `imposta_focus_cartella_fallback()` in `tests/unit/test_imposta_focus_cartella_regression.py`
- Aggiunto test per `sposta_focus_riga_giu_avanzata()` con `_indice_riga_focus` inizialmente `None`
- Aggiornati test in `tests/unit/test_tui_partita.py` e `tests/flow/test_flusso_game_loop.py`

---

## [0.9.0] - 2026-02-21 — Game Loop Interattivo

### Added
- `bingo_game/ui/tui/tui_partita.py`: macchina a stati `_loop_partita()` con dispatch
  comandi `p/s/c/v/q/?`. Architettura function-based, zero import dal Domain Layer.
  Helper: `_gestisci_segna`, `_gestisci_riepilogo_cartella`, `_gestisci_riepilogo_tabellone`,
  `_gestisci_quit`, `_gestisci_help`, `_costruisci_report_finale`, `_emetti_report_finale`,
  `_stampa`.
- `bingo_game/events/codici_loop.py`: 8 costanti stringa per i codici evento del Game Loop
  (`LOOP_TURNO_AVANZATO`, `LOOP_NUMERO_ESTRATTO`, ecc.).
- `bingo_game/ui/locales/it.py`: 13 nuove chiavi `LOOP_*` in `MESSAGGI_OUTPUT_UI_UMANI`
  (prompt, help, quit, report finale, numero estratto, ecc.).
- `bingo_game/game_controller.py`: funzione `ottieni_giocatore_umano(partita)` — espone il
  primo `GiocatoreUmano` alla TUI senza che questa importi classi Domain.
- `tests/unit/test_game_controller_loop.py`: 10 unit test per `ottieni_giocatore_umano()`
  inclusi 3 smoke test di regressione.
- `tests/unit/test_tui_partita.py`: 14 unit test per `tui_partita.py`
  (quit, segna, help, report, focus auto, comando sconosciuto).
- `tests/unit/test_renderer_report_finale.py`: 8 unit test per la vocalizzazione gerarchica
  del renderer (tabellone 3 righe, segnazione 1 riga per esito, cartella 2 righe).
- `tests/flow/test_flusso_game_loop.py`: 12 scenari end-to-end che coprono tutti i comandi
  e i flussi di partita completa (con e senza vincitore).
- `README.md`: sezione "Come si gioca (v0.9.0)" con tabella comandi e note operative.

### Design Notes
- **Flessibilità di marcatura**: qualsiasi numero estratto è segnabile, non solo l'ultimo.
- **Azioni informative illimitate**: `s`, `c`, `v`, `?` non avanzano mai il turno; solo `p` chiama `esegui_turno_sicuro`.
- **Separazione layer**: la TUI accede al dominio esclusivamente tramite `game_controller`; nessun import diretto di `GiocatoreUmano`, `Partita`, `Tabellone` o `Cartella` in `tui_partita.py`.
- **Quit con allerta**: il comando `q` confermato logga `WARNING [ALERT] Partita interrotta dall'utente al turno #N.` su `tombola_stark.tui`.
- **Screen reader ready**: ogni riga di output è autonoma e ≤ 120 caratteri; nessuna ASCII art.

---

## [0.8.0] - 2026-02-20 — Silent Controller

### Changed
- `bingo_game/game_controller.py`: rimossi tutti i `print()` (~22 chiamate).
  I passaggi di costruzione vanno ora a log DEBUG via `_logger_game`.
  Gli output di stato sono trasportati dai valori di ritorno (`bool`, `dict`, `None`).
  I messaggi di errore sono gestiti dalla TUI via `MESSAGGI_CONTROLLER`.
- `bingo_game/ui/ui_terminale.py`: aggiunta guardia sul valore di ritorno di
  `avvia_partita_sicura` (percorso `False`) e helper sicuro `_ottieni_stato_sicuro`
  per la cattura di `ValueError` da `ottieni_stato_sintetico`.

### Added
- `bingo_game/events/codici_controller.py`: nuove costanti stringa
  `CTRL_AVVIO_FALLITO_GENERICO`, `CTRL_TURNO_NON_IN_CORSO`,
  `CTRL_NUMERI_ESAURITI`, `CTRL_TURNO_FALLITO_GENERICO`.
- `bingo_game/ui/locales/it.py`: nuovo dizionario `MESSAGGI_CONTROLLER`
  (4 voci) tipizzato con le costanti di `codici_controller.py`.
- `tests/test_silent_controller.py`: 15 test di non-regressione stdout
  con `capsys` per tutte le funzioni pubbliche del controller.

### Fixed
- Accessibilità: rimossi i messaggi con emoji che interferivano con gli screen reader.
- Architettura: eliminata la dipendenza `Controller → stdout`.

---

## [0.7.0] - 2026-02-19

### Aggiunto
- `TerminalUI` in `bingo_game/ui/ui_terminale.py`: interfaccia da terminale accessibile (screen reader) per il flusso di configurazione pre-partita (Fase 1). Macchina a stati A→E con 3 prompt sequenziali (nome, bot, cartelle) e loop di validazione con re-prompt.
- `bingo_game/events/codici_configurazione.py`: 9 costanti-chiave (`Codici_Configurazione`) per la localizzazione del menu di configurazione.
- `MESSAGGI_CONFIGURAZIONE` in `bingo_game/ui/locales/it.py`: dizionario con 9 chiavi e testi italiani per il flusso di configurazione.
- `bingo_game/ui/locales/__init__.py`: modulo di re-export per i dizionari di localizzazione.
- `tests/unit/test_ui_terminale.py`: 8 unit test con `unittest.mock` (mock di `input()`/`print()` e controller).

### Modificato
- `main.py`: rimossa stampa placeholder, aggiunto entry point `TerminalUI().avvia()`.
- `bingo_game/ui/locales/it.py`: esteso con dizionario `MESSAGGI_CONFIGURAZIONE` (9 chiavi).

---

## [Non Rilasciato]

### Aggiunto
- Strato interfaccia utente (`bingo_game/ui/`) — in sviluppo attivo.
- Navigazione da tastiera e integrazione TTS completa per il giocatore umano.
- Utility di supporto generali (`bingo_game/utils.py`).
 - `tests/unit/test_helper_focus.py`: aggiunti test diretti per `GestioneFocusMixin` (implementazione e verifica completate).
 - Documentazione del task aggiornata: `docs/2 - projects/DESIGN_TEST_HELPER_FOCUS.md`, `docs/3 - coding plans/PLAN_TEST_HELPER_FOCUS.md`, `docs/5 - todolist/TODO_TEST_HELPER_FOCUS.md` (stato: COMPLETED). Vedi report: `docs/4 - reports/report_verifica_lavori_test_helper_focus.md`.

---

## [0.5.0] - 2026-02-19

### Aggiunto
- Modulo `bingo_game/logging/` con `GameLogger` singleton: copertura completa di tutti gli eventi di gioco e di sistema organizzati in 4 categorie (`[GAME]`, `[PRIZE]`, `[SYS]`, `[ERR]`).
- Sub-logger gerarchici `tombola_stark.game`, `tombola_stark.prizes`, `tombola_stark.system`, `tombola_stark.errors` per filtraggio per categoria.
- 18 eventi distinti tracciati: ciclo di vita partita, tutti i tipi di premio, snapshot stato, riepilogo finale a fine sessione.
- `_log_prize_event()` e `_log_game_summary()` come helper privati nel controller.
- Contatori di sessione `_turno_corrente` e `_premi_totali` in `game_controller.py`.
- Test suite Fase 2: `tests/unit/test_event_logging.py` (7 test) e `tests/integration/test_event_coverage.py` (5 test).
- Documentazione completa del sistema di logging in `API.md` e `ARCHITECTURE.md`.

---

## [0.4.0] - 2026-02-19

### Aggiunto
- Modulo `bingo_game/logging/` con classe `GameLogger` Singleton: file di log cumulativo `logs/tombola_stark.log` in modalità append.
- `FlushingFileHandler`: ogni riga di log è scritta su disco immediatamente (flush dopo ogni `emit()`).
- Marcatori di sessione (AVVIATA/CHIUSA) con timestamp che separano visivamente le esecuzioni nel file cumulativo.
- Flag `--debug` via `argparse` in `main.py`: attiva il livello DEBUG per la tracciatura dettagliata di ogni turno.
- Aggancio del logger ai punti chiave di `game_controller.py` tramite helper `_log_safe()` (il logging non interrompe mai il gioco).
- Test suite Fase 1: `tests/unit/test_game_logger.py` (8 test) e `tests/integration/test_logging_integration.py` (3 test).

### Modificato
- `main.py`: aggiunto `argparse` per il flag `--debug` e blocco `try/finally` per la chiusura pulita del logger.
- `.gitignore`: aggiunta esclusione della cartella `logs/` e dei file `*.log`.
- `README.md`: istruzioni d'uso per il flag `--debug` e formato log file.

### Corretto
- `bingo_game/players/giocatore_umano.py`: rimossa parentesi chiusa duplicata (riga 59).
- `bingo_game/players/helper_reclami_focus.py`: corretto import `TipoVittoria` → `Tipo_Vittoria`.
- `bingo_game/events/eventi_output_ui_umani.py`: rimosso import `from __future__ import annotations` duplicato.

---

## [0.3.0] - 2026-02-18

### Aggiunto
- `API.md` nella cartella `documentations/`: riferimento completo di tutte le classi pubbliche, metodi, parametri e valori di ritorno. (commit [fbe71b2](https://github.com/donato81/tombola-stark/commit/fbe71b2e50af50083560e72ccc366a86acd0b85b))
- `ARCHITECTURE.md` nella cartella `documentations/`: documentazione dell'architettura a livelli (Dominio → Controller → Interfaccia), pattern chiave, flusso dei dati e architettura dell'accessibilità. (commit [fbe71b2](https://github.com/donato81/tombola-stark/commit/fbe71b2e50af50083560e72ccc366a86acd0b85b))
- Template di progetto (`documentations/templates/`) con modelli per API, Architettura, Changelog, Design Document, Piano di Implementazione e TODO. (commit [4781a8e](https://github.com/donato81/tombola-stark/commit/4781a8eaf972a43b5f530735462d87bcfd068314))

### Modificato
- `README.md` aggiornato con badge, descrizione accessibilità, istruzioni di installazione complete, struttura del progetto ad albero e link alla documentazione tecnica. (commit [3b47b4a](https://github.com/donato81/tombola-stark/commit/3b47b4ac1f911b9b2575cbaefeb8125ccb48f58c))
- Cartella `documentations/` riorganizzata: rimossa la directory di lavoro temporanea, aggiunta struttura definitiva per la documentazione. (commit [24ef07e](https://github.com/donato81/tombola-stark/commit/24ef07e0fed36dae2c17afea3d6b5e48893be7cb))

---

## [0.2.0] - 2026-02-16

### Aggiunto
- Cartella `documentations/` introdotta nel progetto come area dedicata alla documentazione tecnica. (commit [24ef07e](https://github.com/donato81/tombola-stark/commit/24ef07e0fed36dae2c17afea3d6b5e48893be7cb))

### Modificato
- Struttura del repository riorganizzata: rimossa la directory di lavoro temporanea con Perplexity, separazione netta tra codice sorgente e documentazione.

---

## [0.1.0] - 2026-02-12

*Rilascio iniziale — Motore di gioco core.*

### Aggiunto
- Classe `Tabellone`: gestione dei 90 numeri, estrazione casuale, storico estrazioni, percentuale di avanzamento, snapshot di stato. (commit [82bda90](https://github.com/donato81/tombola-stark/commit/82bda90bf62f898ef0c343d205a2ac48c1f24bf3))
- Classe `Cartella`: 3 righe × 5 numeri, segnatura automatica dei numeri estratti, verifica in tempo reale di ambo, terno, quaterna, cinquina e tombola per riga.
- Classe `Partita`: coordinamento tabellone e giocatori, ciclo di estrazione, verifica premi, gestione stati (`non_iniziata` → `in_corso` → `terminata`).
- Classe `GiocatoreBase`: gestione identità, cartelle multiple, aggiornamento con numero estratto, rilevamento tombola.
- Classe `GiocatoreUmano`: specializzazione per il giocatore umano con supporto al sistema di eventi per l'accessibilità.
- Classe `GiocatoreAutomatico`: bot di gioco senza interazione umana richiesta.
- Modulo `game_controller`: funzioni di orchestrazione fail-safe (`crea_partita_standard`, `avvia_partita_sicura`, `esegui_turno_sicuro`, `ottieni_stato_sintetico`).
- Sistema di eventi strutturati (`bingo_game/events/`) per output semantico pronto per la vocalizzazione TTS.
- Gerarchia di eccezioni personalizzate per ogni modulo: `partita_exceptions.py`, `cartella_exceptions.py`, `giocatore_exceptions.py`, `game_controller_exceptions.py`, `tabellone_exceptions.py`.
- Modulo `validations/` per la logica di validazione riutilizzabile.
- Suite di test unitari (`tests/`) per la validazione automatica di `Cartella`, `Tabellone`, `Partita` e `GiocatoreBase`.
- `main.py` come entry point dell'applicazione.
- `requirements.txt` con dipendenze: wxPython, gTTS, pygame, playsound, Pillow e librerie di supporto.

---

## Legenda

- **Aggiunto**: Nuove funzionalità
- **Modificato**: Modifiche a funzionalità esistenti
- **Deprecato**: Funzionalità in via di dismissione
- **Rimosso**: Funzionalità rimosse
- **Corretto**: Bug fix
- **Sicurezza**: Correzioni di vulnerabilità

---

*Per i dettagli tecnici completi, consulta la [storia dei commit](https://github.com/donato81/tombola-stark/commits/main) o [`documentations/ARCHITECTURE.md`](documentations/ARCHITECTURE.md).*

[Non Rilasciato]: https://github.com/donato81/tombola-stark/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/donato81/tombola-stark/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/donato81/tombola-stark/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/donato81/tombola-stark/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/donato81/tombola-stark/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/donato81/tombola-stark/releases/tag/v0.1.0
