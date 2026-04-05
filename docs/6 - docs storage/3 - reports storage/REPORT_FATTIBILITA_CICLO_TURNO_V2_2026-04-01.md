---
type: report
feature: ciclo_turno_v2
agent: Agent-Analyze
status: COMPLETATO
date: 2026-04-01
design_ref: docs/2 - projects/DESIGN_CICLO_TURNO_V2.md
---

## Metadati

tipo: report_fattibilita
titolo: Fattibilità — Ciclo di Turno V2 con finestra temporale, avvisi vocali e pausa tra turni
data: 2026-04-01
agente: Agent-Analyze
stato: COMPLETATO

---

## Executive Summary

Il ciclo di turno attuale è già parzialmente bifasico: estrazione e verifica sono
separate in due metodi distinti (`esegui_fase_estrazione` e `esegui_fase_verifica`)
e la finestra grafica usa uno stato UI in due posizioni. Tuttavia la finestra d'azione
del giocatore umano non ha nessun limite temporale, i bot registrano il proprio
reclamo immediatamente al momento dell'estrazione (non con ritardo simulato), e non
esiste alcuna pausa tra un turno e il successivo.

Il nuovo design V2 aggiunge una finestra d'azione a tempo configurabile, avvisi vocali
progressivi al 60%, 80% e 95% del tempo trascorso, la rilocazione dei reclami bot in
fase 2 (con ritardo simulato), e una pausa contata tra i turni. Le modifiche toccano il
dominio, la finestra grafica, il renderer, la localizzazione e la configurazione partita.
Il rischio è valutato ALTO per la complessità asincrona del layer wx e per l'impatto
su test esistenti che dipendono dal comportamento corrente di `esegui_fase_estrazione`.

La modifica è consigliata in sotto-fasi sequenziali, non come unico blocco.

---

## Mappa dei file coinvolti

| File | Metodo / Attributo | Stato attuale | Stato dopo modifica |
|------|--------------------|---------------|---------------------|
| `bingo_game/partita.py` | `esegui_fase_estrazione()` | Estrae il numero E registra immediatamente i reclami dei bot | Estrae il numero soltanto; i bot analizzano internamente ma non registrano ancora nessun reclamo |
| `bingo_game/partita.py` | `tutti_hanno_dichiarato_fine()` | Controlla solo i giocatori non automatici | Deve controllare TUTTI i giocatori (umano + bot), perché anche i bot dichiarano "sono pronto" in fase 2 |
| `bingo_game/partita.py` | `fase_turno_corrente` | Valori: `"attesa_estrazione"`, `"attesa_reclami"` | Potenziale aggiunta del valore `"azione_giocatori"` oppure sostituzione semantica di `"attesa_reclami"` |
| `bingo_game/partita.py` | `esegui_fase_verifica()` | Verifica e chiude il turno | Nessuna modifica necessaria; la logica a doppia passata è già presente |
| `bingo_game/players/giocatore_automatico.py` | `_valuta_potenziale_reclamo()` | Analizza e restituisce un oggetto `ReclamoVittoria`, chiamato da `esegui_fase_estrazione` | Rimane di sola analisi; viene chiamato nella fase 2 con un ritardo simulato invece che nella fase 1 |
| `bingo_game/players/giocatore_automatico.py` | `dichiara_fine_fase_azione()` | Non esiste | Da creare: chiama `_valuta_potenziale_reclamo()`, registra `reclamo_turno` e imposta `turno_dichiarato_concluso = True` |
| `bingo_game/players/giocatore_base.py` | `dichiara_fine_turno()` | Esiste; imposta `turno_dichiarato_concluso = True` | Nessuna modifica; viene usato anche dai bot tramite `dichiara_fine_fase_azione` |
| `bingo_game/players/giocatore_base.py` | `turno_dichiarato_concluso` | Esiste; resettato da `esegui_fase_verifica` | Nessuna modifica; reset immutato |
| `bingo_game/ui/finestra_gioco.py` | `_on_pulsante_principale()` | Logica bifasica a click; fase 2 immediata senza timer | Deve avviare un `wx.Timer` dopo la fase 1 e gestire avvisi vocali progressivi e terminazione anticipata |
| `bingo_game/ui/finestra_gioco.py` | `_fase_turno_ui` | `"attesa_estrazione"`, `"attesa_reclami"` | Aggiungere stato `"pausa_turno"` per la fase 4 |
| `bingo_game/ui/finestra_gioco.py` | `_timer_azione` | Non esiste | Da creare: istanza di `wx.Timer` per la finestra d'azione |
| `bingo_game/ui/finestra_gioco.py` | `_timer_pausa` | Non esiste | Da creare: istanza di `wx.Timer` per la pausa tra turni |
| `bingo_game/ui/finestra_gioco.py` | (metodi timer) | Non esistono | Da creare: `_avvia_timer_azione()`, `_on_tick_azione()`, `_on_timeout_azione()`, `_on_all_ready()`, `_avvia_pausa_turno()`, `_on_tick_pausa()`, `_pianifica_risposta_bot()` |
| `bingo_game/ui/renderers/base_renderer.py` | (nuovi metodi astratti) | Non esistono | `annuncia_avviso_timeout(secondi_rimanenti)`, `annuncia_avvio_pausa_turno(secondi)`, `annuncia_tutti_pronti()` |
| `bingo_game/ui/renderers/renderer_wx.py` | (implementazioni) | Non esistono | Implementa i tre nuovi metodi astratti di `BaseRenderer` con vocalizzazione AO2 e scrittura log |
| `bingo_game/ui/finestra_configurazione.py` | `_build_ui()` | 3 campi: nome, numero bot, numero cartelle | Aggiungere 2 campi: `durata_finestra_azione_secondi` e `durata_pausa_turni_secondi` |
| `bingo_game/ui/locales/it.py` | `MESSAGGI_*` | Esistenti; nessuna chiave per timer/avvisi | Aggiungere almeno 6 nuove chiavi: avviso timeout ai tre livelli, avvio pausa, tutti pronti, tempo scaduto |
| `bingo_game/events/codici_eventi.py` | Costanti evento | Esistenti | Aggiungere nuovi codici per avvisi timer, pausa e dichiarazione bot |
| `bingo_game/comandi_partita.py` | `ComandiSistema` | Espone `esegui_fase_estrazione` e `esegui_fase_verifica` | Nessuna modifica obbligatoria; i bot vengono pianificati dalla UI tramite `wx.CallLater` |

---

## Metodi riutilizzabili

- `Partita.esegui_fase_verifica()` — riutilizzabile al 100% senza modifiche; la logica a doppia passata
  per la co-vincita è già presente e corretta.

- `Partita.tutti_hanno_dichiarato_fine()` — riutilizzabile come base, ma richiede estensione logica:
  la condizione di uscita anticipata in V2 riguarda tutti i giocatori (umano + bot), non solo l'umano.

- `GiocatoreBase.dichiara_fine_turno()` — già pronto per umano e bot; riutilizzabile senza modifiche.

- `GiocatoreBase.turno_dichiarato_concluso` — flag già presente e resettato correttamente da
  `esegui_fase_verifica()`; nessuna modifica.

- `GiocatoreAutomatico._valuta_potenziale_reclamo()` — la logica di analisi non cambia; cambia solo
  il punto in cui viene chiamato (fase 2 invece di fase 1).

- `GiocatoreUmano.passa_turno()` e `_passa_turno_core()` — attualmente non usati dalla UI wx;
  disponibili come alternativa per impacchettare lo stato di fine turno se si vuole standardizzare.

- `BaseRenderer.annuncia_numero_estratto()`, `annuncia_premi_turno()`, `annuncia_fase_turno()` —
  già presenti; non richiedono modifiche per il nucleo V2.

- `FinestraGioco.aggiorna_stato_pulsante()` — già presente; basta aggiornare le etichette per
  riflettere i nuovi stati (es. "Ho finito — turno in corso").

---

## Metodi da creare

- `GiocatoreAutomatico.dichiara_fine_fase_azione()` — chiama `_valuta_potenziale_reclamo()`,
  registra `reclamo_turno` e chiama `dichiara_fine_turno()`. Punto di ingresso sicuro callable
  con `wx.CallLater` dalla UI dopo il ritardo simulato.

- `FinestraGioco._avvia_timer_azione(durata_ms)` — crea e avvia un `wx.Timer` one-shot;
  salva il timestamp di avvio per calcolare le percentuali di avviso.

- `FinestraGioco._on_tick_azione(event)` — gestore del tick periodico del timer; controlla
  percentuale trascorsa; emette avvisi vocali ai valori 60%, 80%, 95%; non blocca.

- `FinestraGioco._on_timeout_azione()` — chiamato allo scadere del timer; salta il reclamo
  dell'umano se non ha dichiarato fine; avanza alla fase 3 (verifica).

- `FinestraGioco._on_all_ready()` — chiamato quando `tutti_hanno_dichiarato_fine()` diventa True;
  ferma il timer; annuncia "Tutti pronti"; avanza alla fase 3.

- `FinestraGioco._pianifica_risposta_bot()` — per ogni bot calcola un ritardo casuale realistico
  all'interno della finestra disponibile e schedula `wx.CallLater` su `dichiara_fine_fase_azione`.

- `FinestraGioco._avvia_pausa_turno(durata_ms)` — avvia il timer di pausa tra turni; annuncia
  il conto alla rovescia; riavvia automaticamente dalla fase 1 al termine.

- `FinestraGioco._on_tick_pausa(event)` — gestore del tick della pausa; aggiorna l'annuncio
  del conto alla rovescia a intervalli configurabili.

- `BaseRenderer.annuncia_avviso_timeout(secondi_rimanenti: int)` — metodo astratto; vocalizza
  un avviso proporzionale al tempo rimasto.

- `BaseRenderer.annuncia_avvio_pausa_turno(secondi: int)` — metodo astratto; annuncia inizio
  pausa e durata.

- `BaseRenderer.annuncia_tutti_pronti()` — metodo astratto; annuncia che tutti i giocatori hanno
  dichiarato fine e che la verifica sta per partire.

- Implementazioni corrispondenti in `WxRenderer` per i tre metodi astratti sopra.

---

## Test da aggiornare

- `tests/unit/test_fase_estrazione.py` — il test verifica che dopo `esegui_fase_estrazione()`
  i bot abbiano `reclamo_turno` impostato; questa aspettativa sarà falsa dopo la modifica.

- `tests/integration/test_partita_bot_attivo.py` — i test chiamano `esegui_turno()` o
  `esegui_fase_estrazione()` e si aspettano reclami bot nella fase di estrazione; devono essere
  adattati al nuovo flusso.

- `tests/unit/test_umano_dichiara_fine_turno.py` — test diretto su `dichiara_fine_turno()`;
  richiede almeno un caso aggiuntivo per il flusso bot.

- `tests/test_partita.py` — test su `esegui_turno()` che si aspettano reclami bot nel risultato;
  da verificare caso per caso.

- `tests/test_game_controller.py` — `esegui_turno_sicuro()` delega a `esegui_turno()`;
  i test che assumono reclami bot immediati devono essere adattati.

- `tests/unit/test_game_controller_loop.py` — verifica il loop di turni; da aggiornare
  se usa `esegui_turno_sicuro` con aspettative su reclami bot nel risultato di estrazione.

---

## Nuovi test da scrivere

- `tests/unit/test_ciclo_turno_v2_estrazione.py` — verifica che dopo `esegui_fase_estrazione()`
  i bot abbiano analizzato internamente ma NON registrino ancora `reclamo_turno`.

- `tests/unit/test_ciclo_turno_v2_bot_declaration.py` — verifica che dopo
  `dichiara_fine_fase_azione()` il bot abbia `reclamo_turno` impostato e
  `turno_dichiarato_concluso == True`.

- `tests/unit/test_ciclo_turno_v2_early_exit.py` — verifica che quando tutti dichiarano
  fine prima del timeout, `tutti_hanno_dichiarato_fine()` torni True e il turno avanzi.

- `tests/unit/test_ciclo_turno_v2_timeout_umano.py` — verifica il comportamento quando
  il timer scade senza dichiarazione dell'umano: nessun reclamo registrato per l'umano,
  la verifica parte ugualmente.

- `tests/unit/test_ciclo_turno_v2_config.py` — verifica che i parametri `durata_finestra_azione_secondi`
  e `durata_pausa_turni_secondi` siano letti correttamente e passati a `FinestraGioco`.

- `tests/unit/test_ciclo_turno_v2_tutti_pronti.py` — verifica la nuova semantica di
  `tutti_hanno_dichiarato_fine()` che deve considerare anche i bot.

- `tests/unit/test_ciclo_turno_v2_avvisi_timer.py` — verifica i calcoli delle percentuali
  60%/80%/95% e che vengano emessi gli avvisi corretti nel momento giusto (test con timer finto).

---

## Punti di annuncio vocale

| Momento | Testo annuncio suggerito | Priorità |
|---------|--------------------------|----------|
| Fine fase 1 — numero estratto | "Numero {n}. Turno {t}. Dichiara la tua vittoria o premi Ho finito." | P1 |
| Inizio fase 2 — finestra aperta | "Hai {s} secondi per agire." | P1 |
| Avviso al 60% del tempo trascorso | "Attenzione: hai ancora {s} secondi per dichiarare la tua vittoria." | P1 |
| Avviso all'80% del tempo trascorso | "Attenzione: {s} secondi rimanenti." | P1 |
| Avviso al 95% del tempo trascorso | "Ultimo avviso: {s} secondi. Dichiara ora o il turno verrà saltato." | P1 |
| Timeout — turno umano saltato | "Tempo scaduto. Il tuo turno è stato saltato." | P1 |
| Terminazione anticipata — tutti pronti | "Tutti i giocatori sono pronti. Avvio verifica premi." | P1 |
| Inizio fase 3 — verifica | "Verifica premi in corso." | P2 |
| Premio assegnato (per ciascuno) | "{tipo} assegnato a {giocatore}." | P1 |
| Nessun premio nel turno | "Nessun premio questo turno." | P2 |
| Inizio fase 4 — pausa | "Turno terminato. Prossimo turno tra {s} secondi." | P1 |
| Conto alla rovescia pausa (ogni 10s) | "{s} secondi al prossimo turno." | P3 |

---

## Dipendenze bloccanti

1. `base_renderer.py` deve dichiarare i nuovi metodi astratti **prima** che `renderer_wx.py`
   e `finestra_gioco.py` possano usarli. Se creati nell'ordine sbagliato, l'interprete
   Python solleva `TypeError` all'istanziazione di `WxRenderer`.

2. La modifica a `esegui_fase_estrazione()` (rimozione registrazione reclami bot) romperà
   immediatamente i test in `test_fase_estrazione.py` e `test_partita_bot_attivo.py`.
   Questi test devono essere aggiornati **nella stessa sotto-fase** in cui si modifica il dominio,
   non in un passaggio successivo.

3. Il massimo della durata della finestra d'azione in modalità multiplayer non è specificato
   nel prompt originale ("tetto massimo da definire in fase di analisi"). **Punto aperto**:
   il valore non è stato definito e deve essere deciso prima di scrivere il parametro di
   configurazione per la `FinestraConfigurazione`. Suggerimento: 120 secondi come tetto
   ragionevole; da confermare con l'utente.

4. Il meccanismo di ritardo simulato per i bot (usando `wx.CallLater`) vincola l'implementazione
   al thread principale wx. Se si introduce un `threading.Timer` alternativo, occorre verificare
   la compatibilità con il GIL e il thread wx prima di procedere.

---

## Stima del rischio

**Rischio: ALTO**

Motivazioni:
- La logica di timer asincrono in wxPython (`wx.Timer`, `wx.CallLater`) è difficile da
  testare in isolamento senza un framework wx attivo. I test che coinvolgono il timer
  richiedono mock o sostituzioni ad hoc.
- Modificare `esegui_fase_estrazione()` rimuovendo la registrazione dei reclami bot è una
  rottura del contratto esistente e causerà fallimenti immediati in almeno due suite di test.
- Cinque file in tre layer diversi (dominio, controller, UI/renderer) devono essere
  modificati in modo coerente; un errore in qualsiasi passaggio intermedio lascia il sistema
  in uno stato ibrido difficile da diagnosticare.
- La gestione dell'accessibilità (NVDA) aggiunge un vincolo non testabile automaticamente:
  l'ordine di annuncio, il focus e la ripetizione vocale devono essere verificati manualmente.
- Il valore massimo per la finestra multiplayer è un punto aperto che blocca il design
  completo del modulo di configurazione.

---

## Conclusione

La modifica è consigliata come **sequenza di sotto-fasi distinte e commitabili**,
non come unico blocco. In particolare:

1. Sotto-fase A — Dominio: modificare `esegui_fase_estrazione()` e aggiornare i test rotti.
2. Sotto-fase B — Bot declaration: creare `dichiara_fine_fase_azione()` e adattare
   `tutti_hanno_dichiarato_fine()`.
3. Sotto-fase C — Renderer: aggiungere i metodi astratti e le implementazioni wx.
4. Sotto-fase D — UI timer: aggiungere i timer in `finestra_gioco.py` e pianificazione bot.
5. Sotto-fase E — Configurazione: aggiungere i nuovi parametri a `FinestraConfigurazione`.
6. Sotto-fase F — Test e accessibilità: scrivere i nuovi test e verificare NVDA manualmente.

Prima di iniziare l'implementazione occorre risolvere il punto aperto sul valore massimo
della finestra d'azione in multiplayer.
