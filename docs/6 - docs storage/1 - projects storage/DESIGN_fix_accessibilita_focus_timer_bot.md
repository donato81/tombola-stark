---
type: design
feature: fix_accessibilita_focus_timer_bot
agent: Agent-Design
status: REVIEWED
version: v0.9.5
date: 2026-04-05
report_ref: docs/4 - reports/REPORT_BUG_ACCESSIBILITA_FOCUS_TIMER_BOT_2026-04-05.md
---

# DESIGN — Fix accessibilità: focus iniziale, soppressione avvisi timer, annuncio turno bot

## Idea in 3 righe

Tre correzioni distinte e atomiche tutte localizzate in `FinestraGioco`:
all'avvio del gioco il focus di navigazione viene inizializzato su cartella 1,
riga 1, colonna 1; gli avvisi vocali del timer di turno vengono soppressi se
il giocatore ha già dichiarato fine turno; ogni bot che dichiara fine turno
emette un annuncio vocale tramite il renderer.
Nessuna modifica è necessaria al domain layer o al renderer.

---

## Obiettivo

### Bug 1 — Focus non impostato all'avvio

All'apertura di `FinestraGioco`, `SetFocus()` posiziona il focus wx
sul pannello griglia ma non inizializza il focus interno di gioco
(`GiocatoreUmano._indice_cartella_focus = None`). Qualsiasi pressione
di tasto freccia genera subito il messaggio di errore "Nessuna cartella
selezionata." Per un utente NVDA l'esperienza attesa è ricevere il
contesto di posizione subito dopo l'avvio, senza dover premere Ctrl+1.

### Bug 2 — Avvisi timer dopo dichiarazione turno umano

`_on_tick_azione` controlla soltanto che la fase UI sia `attesa_reclami`,
ma questa fase rimane attiva finché tutti i giocatori (umano + bot)
non dichiarano. Se il giocatore dichiara prima del raggiungimento di una
soglia percentuale (60%, 80%, 95%), il timer emette comunque l'avviso
vocale. Per uno screen reader è rumore inutile e potenzialmente confusivo:
l'utente ha già agito.

### Bug 3 — Passaggio turno bot silenzioso

`_dichiara_fine_bot` registra la dichiarazione del bot ma non emette
alcun annuncio. Il giocatore sente solo silenzio tra la propria conferma
e il messaggio collettivo "Tutti i giocatori sono pronti.", senza
informazioni su quanti bot abbiano già risposto.

---

## Componenti coinvolti

| Componente | Path | Ruolo nel fix |
|---|---|---|
| `FinestraGioco` | `bingo_game/ui/finestra_gioco.py` | Unico file modificato — tutti e tre i bug risiedono qui |
| `ComandiGiocatoreUmano` | `bingo_game/comandi_partita.py` | Metodo `turno_gia_dichiarato()` già presente (v0.9.5) — riutilizzato per Bug 2 |
| `WxRenderer.mostra_messaggio_sistema` | `bingo_game/ui/renderers/renderer_wx.py` | Canale di output vocale — già usato per altri annunci, riutilizzato per Bug 3 |
| `GiocatoreAutomatico` | `bingo_game/players/giocatore_automatico.py` | Attributo `nome` (ereditato da `GiocatoreBase`) — letto via `getattr` per Bug 3 |

---

## Dipendenze

- `FinestraGioco.__init__` → `ComandiGiocatoreUmano.imposta_focus_cartella`, `vai_a_riga`, `vai_a_colonna` — già esistenti (Bug 1)
- `FinestraGioco._on_tick_azione` → `ComandiGiocatoreUmano.turno_gia_dichiarato()` — già esistente da fix hotkey (Bug 2)
- `FinestraGioco._dichiara_fine_bot` → `WxRenderer.mostra_messaggio_sistema` — già esistente (Bug 3)
- Nessuna nuova dipendenza introdotta: tutti i metodi riutilizzati esistono già nel codebase.

---

## Rischi

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| `wx.CallAfter` ritarda il focus iniziale oltre l'annuncio NVDA del titolo finestra | Bassa | Medio | Testare empiricamente su NVDA; se necessario usare `wx.CallLater(100, ...)` con ritardo esplicito di 100ms |
| Annunci multipli all'avvio (cartella + riga + colonna) sovrappongono vocalmente | Media | Medio | Separare in tre chiamate sequenziali con `_dispatch` — NVDA mette in coda gli annunci |
| `getattr(bot, "nome", "Bot")` ritorna "Bot" se il nome non è impostato | Bassa | Basso | Il costruttore di `GiocatoreAutomatico` imposta sempre un nome; fallback accettabile |

---

## Vincoli accessibilità NVDA

- **Bug 1**: il focus iniziale deve essere annunciato prima che il giocatore interagisca; l'inizializzazione con `wx.CallAfter` garantisce che il renderer sia già collegato alla finestra quando vengono emessi gli annunci.
- **Bug 2**: nessun testo vocale deve essere emesso verso un giocatore che ha già compiuto l'azione richiesta; la soppressione è totale sulle soglie percentuali.
- **Bug 3**: l'annuncio del bot deve essere breve e informativo (`"<Nome> ha passato il turno."`), non interrompere la navigazione dell'utente.
- Tutti i testi prodotti passano per `mostra_messaggio_sistema` (già testato NVDA-compatibile) o per `_dispatch` → renderer (stesso canale).

---

## Attori e Concetti

### Attori

- `FinestraGioco`: frame principale, punto di intervento per tutti e tre i bug.
- `ComandiGiocatoreUmano`: boundary applicativo, espone `turno_gia_dichiarato()` già disponibile.
- `WxRenderer`: emissione testo verso log, widget e AO2; canale di feedback accessibile.
- `GiocatoreAutomatico`: bot con attributo `nome`.
- NVDA/JAWS: destinatario finale del feedback; ogni annuncio deve essere tempestivo e non sovrapposto a silenzi non informativi.

### Concetti

- **Focus iniziale contestualizzato**: l'avvio del gioco deve produrre un annuncio
  di posizione (cartella/riga/colonna) senza richiedere input da parte dell'utente.
- **Soppressione avvisi contestuali**: un avviso temporale diventa rumore se
  l'azione che sollecita è già stata compiuta.
- **Trasparenza delle azioni bot**: in un gioco cooperativo-competitivo il
  giocatore ha diritto a sapere quando gli altri partecipanti hanno dichiarato.

---

## Flussi concettuali

### Flusso 1 — Avvio finestra di gioco (Bug 1)

1. `FinestraGioco.__init__` completa la costruzione dei widget wx.
2. `wx.CallAfter(self._imposta_focus_iniziale)` schedula l'inizializzazione
   del focus dopo che il loop degli eventi wx è avviato.
3. `_imposta_focus_iniziale` chiama in sequenza:
   - `self._dispatch(self._comandi.imposta_focus_cartella(1))` → annuncia "Cartella 1 selezionata."
   - `self._dispatch(self._comandi.vai_a_riga(1))` → annuncia dati riga 1
   - `self._dispatch(self._comandi.vai_a_colonna(1))` → annuncia dati colonna 1

### Flusso 2 — Tick timer dopo dichiarazione turno umano (Bug 2)

1. `_on_tick_azione` viene chiamato ogni 500ms.
2. Prima di calcolare la percentuale e controllare le soglie avvisi:
   - Se `self._comandi.turno_gia_dichiarato()` è `True`: nessun avviso vocale.
   - Se il timer è scaduto: chiama `_on_timeout_azione()` e ritorna.
3. Altrimenti: percorso normale con avvisi percentuali.

### Flusso 3 — Dichiarazione turno bot (Bug 3)

1. `wx.CallLater` richiama `_dichiara_fine_bot` con il ritardo simulato.
2. Dopo `bot.dichiara_fine_fase_azione(...)`:
   - `nome_bot = getattr(bot, "nome", "Bot")`
   - `self._renderer.mostra_messaggio_sistema(f"{nome_bot} ha passato il turno.")`
3. `_controlla_tutti_pronti()` come da comportamento esistente.

---

## Coding plans correlati

- `docs/3 - coding plans/PLAN_fix_accessibilita_focus_timer_bot_v0.9.5.md` (da produrre in Fase 3)
