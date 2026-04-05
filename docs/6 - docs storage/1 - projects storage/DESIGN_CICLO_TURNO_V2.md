---
type: design
feature: ciclo_turno_v2
version: v1.0
date: 2026-04-01
agent: Agent-Design
status: DRAFT
report_ref: docs/4 - reports/REPORT_FATTIBILITA_CICLO_TURNO_V2_2026-04-01.md
---

## Metadati

tipo: design
titolo: Ciclo di Turno V2 — Finestra d'azione temporizzata, ritardo bot realistico, pausa tra turni
versione: v1.0
data: 2026-04-01
autore: Agent-Design
stato: DRAFT
riferimento_report: docs/4 - reports/REPORT_FATTIBILITA_CICLO_TURNO_V2_2026-04-01.md

---

## Obiettivo della modifica

### Cosa cambia

Il ciclo di turno attuale comprime in una sequenza automatica l'estrazione del numero,
la registrazione istantanea dei reclami dei bot e la verifica dei premi. Il giocatore
umano non dispone di nessuna finestra di tempo garantita tra il momento in cui sente il
numero (tramite NVDA) e il momento in cui il turno viene chiuso.

Il ciclo V2 introduce quattro fasi esplicite con responsabilità separate:
una fase di estrazione, una finestra d'azione a tempo configurabile in cui tutti i
giocatori (umano e bot) agiscono, una fase di verifica e assegnazione premi, e una
pausa contata tra un turno e il successivo.

### Perché

- Accessibilità: un utente con screen reader ha bisogno di tempo sufficiente per
  ascoltare il numero, navigare la propria cartella, segnare e dichiarare l'eventuale
  vittoria. Il ciclo attuale non garantisce questa finestra.
- Equità: i bot attualmente registrano il reclamo contemporaneamente all'estrazione,
  prima che l'umano abbia avuto qualsiasi opportunità di reagire. Con V2 bot e umano
  agiscono nella stessa finestra temporale.
- Configurabilità: la durata della finestra e della pausa devono essere adattabili
  al contesto (partita solitaria vs. multiplayer futuro) senza toccare il codice.

---

## Descrizione del nuovo ciclo di turno

### Le quattro fasi

#### FASE 1 — ESTRAZIONE

Il sistema estrae il prossimo numero dal tabellone e lo annuncia vocalmente.
I bot aggiornano internamente le proprie cartelle ma NON registrano ancora nessun
reclamo (`reclamo_turno` resta `None` per tutti i bot al termine di questa fase).
La responsabilità di analisi resta nel metodo `_valuta_potenziale_reclamo()` già
esistente, che viene chiamato solo come lettura senza effetti di stato.

Al termine della fase 1, il dominio si porta nello stato `"attesa_reclami"` e
la UI annuncia il numero e apre la finestra d'azione.

#### FASE 2 — AZIONE GIOCATORI

Si apre una finestra di tempo configurabile (`durata_finestra_azione_secondi`).
In questa finestra:
- Il giocatore umano naviga la propria cartella, segna il numero se presente,
  dichiara una vittoria con i tasti F1-F5 se applicabile, e quando ha finito
  preme il pulsante "Ho finito" (oppure Ctrl+P). Questo imposta
  `turno_dichiarato_concluso = True` per l'umano.
- Ogni bot, dopo un ritardo simulato realistico generato con distribuzione
  casuale all'interno della finestra disponibile, chiama `dichiara_fine_fase_azione()`.
  Questo metodo registra il reclamo (se presente) e imposta
  `turno_dichiarato_concluso = True` per il bot.

La durata della finestra segue queste regole:
- Valore predefinito per partite solitarie contro bot: **60 secondi**.
- Per partite multiplayer: configurabile dall'host con un tetto massimo
  (valore tetto: **PUNTO APERTO** — da decidere prima dell'implementazione;
  suggerimento provvisorio: 120 secondi).
- La durata è impostata prima dell'avvio della partita nella `FinestraConfigurazione`.

Avvisi vocali progressivi durante la fase 2:
- Al **60%** del tempo trascorso: "Attenzione: hai ancora {s} secondi per dichiarare la tua vittoria."
- All'**80%** del tempo trascorso: "Attenzione: {s} secondi rimanenti."
- Al **95%** del tempo trascorso: "Ultimo avviso: {s} secondi. Dichiara ora o il turno verrà saltato."

Terminazione anticipata: se il metodo `tutti_hanno_dichiarato_fine()` restituisce `True`
prima della scadenza del timer (tutti i giocatori, umano e bot, hanno dichiarato fine),
il timer viene fermato immediatamente e si avanza alla fase 3 senza attendere.

Comportamento in caso di timeout: se il timer scade senza che l'umano abbia dichiarato
fine, il turno dell'umano viene saltato (nessun `reclamo_turno` registrato per lui),
e il sistema avanza comunque alla fase 3 con i reclami dei bot già registrati.

#### FASE 3 — VERIFICA E ASSEGNAZIONE

Il sistema esegue `esegui_fase_verifica()` già esistente, che:
- raccoglie tutti i reclami validi (umano, se presente, e bot);
- verifica i premi con la logica a doppia passata già implementata;
- assegna i premi a tutti i co-vincitori;
- resetta gli stati di turno di tutti i giocatori;
- controlla la tombola e termina la partita se necessario.

Successivamente il renderer annuncia vocalmente i premi del turno.

#### FASE 4 — PAUSA TRA TURNI

Al termine della fase 3, il sistema annuncia vocalmente:
"Turno terminato. Prossimo turno tra {s} secondi."

Parte un conto alla rovescia della durata `durata_pausa_turni_secondi`.
Al termine del conto alla rovescia, il sistema ritorna automaticamente alla fase 1
riprendendo il ciclo senza intervento dell'utente.

La durata della pausa è configurabile separatamente dalla durata della finestra d'azione.

---

### Diagramma testuale del flusso

```
ATTESA ESTRAZIONE
        |
        v (click pulsante / Ctrl+P)
[FASE 1: ESTRAZIONE]
  - tabellone.estrai_numero()
  - bot: aggiorna_con_numero() — SOLO lettura interna
  - annuncia numero vocalmente
  - stato dominio: "attesa_reclami"
        |
        v (timer avviato)
[FASE 2: AZIONE GIOCATORI] <--- durata_finestra_azione_secondi
  |                              (default 60s)
  +-- umano: segna, dichiara vittoria, premi "Ho finito"
  |         -> turno_dichiarato_concluso = True
  +-- bot1: wx.CallLater(delay1) -> dichiara_fine_fase_azione()
  |         -> reclamo_turno registrato + turno_dichiarato_concluso = True
  +-- bot2: wx.CallLater(delay2) -> dichiara_fine_fase_azione()
  |         -> reclamo_turno registrato + turno_dichiarato_concluso = True
  |
  +-- avvisi vocali al 60%, 80%, 95% del tempo trascorso
  |
  +-- terminazione anticipata se tutti_hanno_dichiarato_fine() == True
  |     -> timer fermato, avanza subito
  |
  +-- timeout (timer scade senza dichiarazione umano)
        -> turno umano saltato (nessun reclamo)
        |
        v
[FASE 3: VERIFICA E ASSEGNAZIONE]
  - esegui_fase_verifica() [logica a doppia passata esistente]
  - premi assegnati a tutti i co-vincitori
  - annuncio vocale premi / nessun premio
  - reset stati turno
  - verifica tombola
        |
      [tombola?] -- SI --> partita terminata
        |
        NO
        v
[FASE 4: PAUSA TRA TURNI] <--- durata_pausa_turni_secondi
  - annuncio "Turno terminato. Prossimo turno tra {s} secondi."
  - conto alla rovescia
        |
        v (timer pausa scade)
ATTESA ESTRAZIONE (ricomincia dalla fase 1)
```

---

## Configurazioni introdotte

| Nome parametro | Tipo | Valore predefinito | Descrizione |
|----------------|------|--------------------|-------------|
| `durata_finestra_azione_secondi` | `int` | `60` | Durata in secondi della finestra d'azione (fase 2). Usato per partite solitarie contro bot. |
| `durata_finestra_azione_max_multiplayer_secondi` | `int` | PUNTO APERTO | Tetto massimo per la finestra d'azione in modalità multiplayer. Da decidere prima dell'implementazione. Suggerimento provvisorio: 120 secondi. |
| `durata_pausa_turni_secondi` | `int` | `5` | Durata in secondi della pausa tra un turno e il successivo (fase 4). Configurabile separatamente dalla finestra d'azione. |

I parametri `durata_finestra_azione_secondi` e `durata_pausa_turni_secondi` sono inseriti
nella `FinestraConfigurazione` come campi numerici (`wx.SpinCtrl`) prima dell'avvio della
partita e passati a `FinestraGioco` come parametri di costruzione.

---

## Comportamento in caso di timeout

1. Il timer della finestra d'azione scade (non c'è stata dichiarazione da parte dell'umano).
2. Il metodo `_on_timeout_azione()` in `FinestraGioco` viene chiamato dal wx.Timer.
3. Il renderer vocalizza: "Tempo scaduto. Il tuo turno è stato saltato."
4. `reclamo_turno` del giocatore umano rimane `None`.
5. I reclami dei bot eventualmente già registrati con `dichiara_fine_fase_azione()` rimangono validi.
6. Il sistema avanza direttamente alla fase 3 (`esegui_fase_verifica()`).
7. La verifica dei premi considera solo i reclami non-`None` (bot che hanno dichiarato).
8. La fase 4 (pausa) parte normalmente al termine della verifica.

---

## Comportamento in caso di co-vincita

La logica a doppia passata già presente in `verifica_premi()` (prima raccoglie tutti i candidati
validi per tipo, poi assegna il premio a ciascuno) è **sufficiente** per gestire la co-vincita
nel nuovo ciclo senza modifiche. Il fatto che i reclami siano ora registrati in momenti diversi
(umano a fine fase 2, bot a ritardo casuale durante fase 2) non cambia la struttura della
verifica: `esegui_fase_verifica()` legge lo stato `reclamo_turno` al momento della sua
chiamata, quando tutti i reclami validi sono già stati registrati (o il timer è scaduto).

Unica precondizione: `esegui_fase_verifica()` deve essere chiamata **solo dopo** la fine
della fase 2 (timer scaduto o tutti pronti), non prima.

---

## Comportamento in multiplayer (nota prospettica)

Il design V2 è strutturato per essere compatibile con il multiplayer futuro nei seguenti modi:

- La logica di "tutti hanno dichiarato fine" (`tutti_hanno_dichiarato_fine()`) è already
  indipendente dal numero di giocatori; funzionerà anche con più umani in rete.
- Il parametro `durata_finestra_azione_secondi` è configurabile a livello di partita
  (non hardcoded); in multiplayer l'host potrà impostare un valore diverso (fino al tetto
  massimo `durata_finestra_azione_max_multiplayer_secondi`).
- Il metodo `dichiara_fine_fase_azione()` dei bot è già progettato come un segnale esplicito
  callable da qualsiasi contesto (timer, network callback, input remoto in futuro).
- Il timer sul lato UI (`wx.Timer`) è incapsulato in `FinestraGioco`; in multiplayer
  potrebbe essere sostituito con un timer lato server senza toccare la logica di dominio.

---

## Criteri di accettazione

La modifica è considerata completa quando sono verificate tutte le seguenti condizioni:

1. Dopo `esegui_fase_estrazione()`, nessun bot ha `reclamo_turno != None`.
2. Dopo `dichiara_fine_fase_azione()` su un bot, quel bot ha `turno_dichiarato_concluso == True`
   e `reclamo_turno` è impostato (o `None` se non aveva premi da reclamare).
3. Se tutti i giocatori dichiarano fine prima della scadenza del timer, il timer si ferma
   e la fase 3 parte senza attendere l'intervallo restante.
4. Se il timer scade senza dichiarazione dell'umano, la fase 3 parte comunque e il reclamo
   dell'umano non viene considerato.
5. Gli avvisi vocali sono emessi ai corretti valori di percentuale (60%, 80%, 95%).
6. I testi annunciati da NVDA corrispondono alle chiavi definite in `it.py`.
7. La fase 4 (pausa) parte al termine della verifica e riavvia automaticamente la fase 1.
8. `durata_finestra_azione_secondi` e `durata_pausa_turni_secondi` sono leggibili dalla
   `FinestraConfigurazione` e passati correttamente alla logica del timer.
9. La co-vincita è gestita correttamente: due giocatori che reclamano lo stesso tipo nello
   stesso turno ricevono entrambi il premio.
10. Tutti i test elencati nella sezione "Test da aggiornare" del report di fattibilità passano.
11. Nessun `print()` in `src/`; nessun test di GUI senza `@pytest.mark.gui`.

---

## Elementi fuori scope

I seguenti elementi NON vengono modificati in questa sessione:

- La logica di co-vincita in `verifica_premi()`: è già corretta e non richiede modifiche.
- Il design visivo delle finestre: nessun cambiamento a layout, colori o proporzioni.
- Il multiplayer in rete: questo design prepara la compatibilità ma non implementa
  alcun layer di comunicazione tra istanze remote.
- Il sistema di persistenza delle statistiche di partita.
- Il log vocale con ripetizione avanzata (Ctrl+E): comportamento invariato.
- Il dialog di ricerca numero (Ctrl+F): comportamento invariato.
- Il renderer TUI (terminale): questo design riguarda esclusivamente il layer wx.
- Il parametro `durata_finestra_azione_max_multiplayer_secondi`: è un punto aperto
  che deve essere risolto prima dell'implementazione ma non è il focus di questo design.
