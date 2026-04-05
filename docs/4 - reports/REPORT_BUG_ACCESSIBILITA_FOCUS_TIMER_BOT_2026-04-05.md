# Report di Analisi — Bug Accessibilità: Focus Iniziale, Timer Post-Dichiarazione, Annuncio Turno Bot

**Data**: 2026-04-05
**Tipo**: Analisi diagnostica
**Segnalato da**: log di partita fornito dall'utente
**Agente**: Agent-Analyze (read-only)

---

## Log originale di riferimento

```
Errore: Nessuna cartella selezionata.
Seleziona una cartella prima di continuare.
Cartella 1 selezionata.
Turno 1. Numero estratto: 35.
Numero 35 trovato in:
  Cartella 3, riga 3, colonna 4 (non segnato).
Cartella 3 selezionata.
Riga 3: 4  vuoto  26  35  47  55  vuoto  vuoto  vuoto
Numero 35 segnato (riga 3, colonna 4).
Turno dichiarato concluso. Attendo gli altri giocatori.
Attenzione: hai ancora 24 secondi per dichiarare la tua vittoria.
Tutti i giocatori sono pronti. Avvio verifica premi.
Nessun premio questo turno.
Turno terminato. Prossimo turno tra 5 secondi.
```

---

## Bug 1 — Focus non impostato su cartella 1, riga 1, colonna 1 all'avvio

### Sintomo

All'apertura di `FinestraGioco`, il focus wx è sul pannello griglia, ma nessuna cartella è selezionata internamente. Il giocatore non può navigare o segnare senza prima premere Ctrl+1 (o altro). Il log mostra:

```
Errore: Nessuna cartella selezionata.
Seleziona una cartella prima di continuare.
```

Questo avviene prima che il giocatore abbia interagito con il turno, perché qualsiasi pressione di tasto freccia nel pannello griglia fallisce se il focus interno è `None`.

### Causa radice

**File**: `bingo_game/ui/finestra_gioco.py`
**Metodo**: `FinestraGioco.__init__` (ultima riga)

```python
# Focus iniziale sulla griglia
self._pannello_griglia.SetFocus()
```

`SetFocus()` imposta il focus **wx** sul widget, ma non inizializza il focus **interno di gioco** su `GiocatoreUmano`.

In `GiocatoreUmano.__init__` (`bingo_game/players/giocatore_umano.py`, riga 91–93):

```python
self._indice_cartella_focus: Optional[int] = None
self._indice_riga_focus: Optional[int] = None
self._indice_colonna_focus: Optional[int] = None
```

Tutti e tre gli indici partono da `None`.

### Percorso di errore

1. Giocatore preme freccia nella griglia.
2. `PannelloGriglia._on_key_down` → `fg._comandi.riga_su()`.
3. `ComandiGiocatoreUmano.riga_su()` → `self._giocatore.sposta_focus_riga_su_semplice()`.
4. Interno: `_esito_focus_cartella_valido(auto_imposta=False)` → focus è `None` → `FOCUS_CARTELLA_NON_IMPOSTATO`.
5. Il renderer traduce l'errore in "Nessuna cartella selezionata. Seleziona una cartella prima di continuare."

### Impatto accessibilità

Per un utente NVDA: dopo l'avvio del gioco sente solo silenzio (pannello griglia senza contenuto annunciato), poi prova a navigare e sente un messaggio di errore. L'esperienza attesa è ricevere subito "Cartella 1 selezionata." e sapere dove si trova.

### Soluzione proposta

In `FinestraGioco.__init__`, dopo `self._pannello_griglia.SetFocus()`, aggiungere:

```python
# Inizializza focus di gioco su cartella 1, riga 1, colonna 1
wx.CallAfter(self._imposta_focus_iniziale)
```

Con il metodo privato:

```python
def _imposta_focus_iniziale(self) -> None:
    """Imposta il focus di gioco su cartella 1, riga 1, colonna 1 all'avvio."""
    self._dispatch(self._comandi.imposta_focus_cartella(1))
    self._dispatch(self._comandi.vai_a_riga(1))
    self._dispatch(self._comandi.vai_a_colonna(1))
```

`wx.CallAfter` garantisce che il loop degli eventi wx sia pienamente avviato prima dell'inizializzazione, evitando race condition con la configurazione del renderer. Le tre chiamate a `_dispatch` producono tre annunci sequenziali via NVDA:
1. "Cartella 1 selezionata."
2. Annuncio riga 1 con dati.
3. Annuncio colonna 1 con dati.

**File modificato**: `bingo_game/ui/finestra_gioco.py`
**Entità modificate**: `FinestraGioco.__init__`, nuovo metodo `_imposta_focus_iniziale`
**Metodi già esistenti riusati**: `ComandiGiocatoreUmano.imposta_focus_cartella`, `ComandiGiocatoreUmano.vai_a_riga`, `ComandiGiocatoreUmano.vai_a_colonna`

---

## Bug 2 — Avviso timer emesso dopo che il giocatore ha già dichiarato fine turno

### Sintomo

```
Turno dichiarato concluso. Attendo gli altri giocatori.
Attenzione: hai ancora 24 secondi per dichiarare la tua vittoria.
```

Il messaggio "Attenzione: hai ancora 24 secondi..." appare **dopo** che il giocatore ha già dichiarato la fine del turno. Per uno screen reader è rumore inutile: l'azione è già stata compiuta.

### Causa radice

**File**: `bingo_game/ui/finestra_gioco.py`
**Metodo**: `FinestraGioco._on_tick_azione` (riga ~422–440)

```python
def _on_tick_azione(self, event: wx.TimerEvent) -> None:
    if self._fase_turno_ui != "attesa_reclami":
        return
    self._ms_trascorsi_azione += self._tick_ms
    ...
    if pct >= 95 and 95 not in self._avvisi_emessi:
        self._avvisi_emessi.add(95)
        self._renderer.annuncia_avviso_timeout(secondi_rim, livello=95)
    elif pct >= 80 and 80 not in self._avvisi_emessi:
        self._avvisi_emessi.add(80)
        self._renderer.annuncia_avviso_timeout(secondi_rim, livello=80)
    elif pct >= 60 and 60 not in self._avvisi_emessi:
        self._avvisi_emessi.add(60)
        self._renderer.annuncia_avviso_timeout(secondi_rim, livello=60)
```

Il guard è `self._fase_turno_ui != "attesa_reclami"` ma questa fase **rimane attiva** finché tutti i giocatori (umano + bot) non dichiarano fine. Quando l'umano ha già dichiarato, la fase è ancora `"attesa_reclami"` in attesa dei bot, e il timer continua a emettere avvisi.

### Verifica numerica dal log

Con `durata_finestra_ms = 60000` (60 secondi impostati in configurazione):

- `TURNO_AVVISO_60` si emette a `pct >= 60`, cioè a `60% * 60s = 36s trascorsi` → `24s rimasti`.
- Corrisponde esattamente a "hai ancora 24 secondi" nel log.

Il giocatore ha dichiarato fine turno prima dei 36s, ma il timer ha comunque emesso l'avviso al raggiungimento della soglia.

### Testo del catalogo

`bingo_game/ui/locales/it.py`, riga 149:

```python
"TURNO_AVVISO_60": (
    "Attenzione: hai ancora {s} secondi per dichiarare la tua vittoria.",
),
```

### Impatto accessibilità

Un utente NVDA, dopo aver premuto Ctrl+P e ricevuto conferma, sente un secondo messaggio che gli dice di dichiarare la fine del turno. Questo crea confusione.

### Soluzione proposta

In `_on_tick_azione`, prima dei blocchi degli avvisi percentuali, aggiungere il check:

```python
# Se il giocatore umano ha già dichiarato fine turno, non emettere avvisi timeout.
if self._comandi.turno_gia_dichiarato():
    if self._ms_trascorsi_azione >= self._durata_finestra_corrente_ms:
        self._on_timeout_azione()
    return
```

In questa forma:
- Il timer continua a girare (necessario per il timeout dei bot).
- Nessun avviso vocale viene emesso se il giocatore ha già dichiarato.
- Il timeout viene comunque gestito correttamente se i bot non dichiarano entro il termine.

**File modificato**: `bingo_game/ui/finestra_gioco.py`
**Metodo modificato**: `FinestraGioco._on_tick_azione`
**Metodo già esistente riusato**: `ComandiGiocatoreUmano.turno_gia_dichiarato()`

---

## Bug 3 — Passaggio del turno dei bot non annunciato

### Sintomo

Le azioni dei bot durante la fase di reclami (`attesa_reclami`) sono completamente silenziose. Solo al termine del turno il giocatore sente "Tutti i giocatori sono pronti. Avvio verifica premi." senza sapere quanti o quali bot hanno già dichiarato.

### Causa radice

**File**: `bingo_game/ui/finestra_gioco.py`
**Metodo**: `FinestraGioco._dichiara_fine_bot` (riga ~488–495)

```python
def _dichiara_fine_bot(self, bot: object, premi_gia_assegnati: set, premi_tipo_chiusi: set) -> None:
    if self._fase_turno_ui != "attesa_reclami":
        return
    bot.dichiara_fine_fase_azione(premi_gia_assegnati, premi_tipo_chiusi)  # type: ignore[union-attr]
    self._controlla_tutti_pronti()
```

Non viene emesso nessun annuncio dopo `dichiara_fine_fase_azione`. Solo le vittorie dei bot vengono annunciate più tardi in `_esegui_verifica_premi` → `annuncia_premi_turno`.

### Attributo disponibile

`GiocatoreAutomatico` eredita `self.nome` da `GiocatoreBase`. Il `type: ignore[union-attr]` già presente indica che il type hint `bot: object` è loose, ma il valore reale è sempre `GiocatoreAutomatico` con attributo `nome: str`.

### Impatto accessibilità

Per un utente NVDA con più bot (es. 3 bot), c'è un silenzio completo tra "Turno dichiarato concluso." e "Tutti i giocatori sono pronti." Il giocatore non sa se i bot hanno risposto rapidamente o se sta aspettando il timeout.

### Soluzione proposta

In `_dichiara_fine_bot`, dopo `bot.dichiara_fine_fase_azione(...)`:

```python
nome_bot: str = getattr(bot, "nome", "Bot")
self._renderer.mostra_messaggio_sistema(f"{nome_bot} ha passato il turno.")
```

`getattr` con valore di fallback è il pattern sicuro dato il type hint `object` esistente, coerente con `_ottieni_numero_in_focus` che usa `getattr(self._renderer, "numero_in_focus", None)`.

**File modificato**: `bingo_game/ui/finestra_gioco.py`
**Metodo modificato**: `FinestraGioco._dichiara_fine_bot`
**Metodo già esistente riusato**: `WxRenderer.mostra_messaggio_sistema`

---

## Riepilogo

| # | Titolo | File | Metodo | Gravità |
|---|--------|------|--------|---------|
| 1 | Focus non inizializzato all'avvio | `finestra_gioco.py` | `__init__` | Alta — blocca uso immediato |
| 2 | Avviso timer dopo dichiarazione turno | `finestra_gioco.py` | `_on_tick_azione` | Media — rumore NVDA |
| 3 | Passaggio turno bot non annunciato | `finestra_gioco.py` | `_dichiara_fine_bot` | Media — manca informazione di contesto |

Tutti e tre i bug sono localizzati in `bingo_game/ui/finestra_gioco.py`. Nessuna modifica è necessaria al domain layer o al renderer: i metodi necessari esistono già.

---

## Prossimo step suggerito

Agent-Design per la stesura di `DESIGN_fix_accessibilita_focus_timer_bot.md`, oppure procedere direttamente con Agent-Code se si ritiene il design sufficientemente chiaro da questo report.
