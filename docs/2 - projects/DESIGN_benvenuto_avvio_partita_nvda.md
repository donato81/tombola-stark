---
type: design
titolo: Ripristino annuncio di benvenuto NVDA all'avvio partita
feature: benvenuto_avvio_partita_nvda
versione: 0.12.2
data_creazione: 2026-04-14
agent: Agent-Design
status: DRAFT
---

# DESIGN — Ripristino annuncio di benvenuto NVDA all'avvio partita

## Idea in 3 righe

All'ingresso nella finestra di gioco, l'utente non vedente deve sentire
un solo annuncio orientativo chiaro, non una sequenza di messaggi tecnici
di navigazione. La fix sposta il focus logico iniziale senza vocalizzarlo,
poi emette subito il benvenuto con priorita alta per NVDA.

---

## Obiettivo

Ripristinare la lettura del messaggio iniziale nella finestra di gioco,
cosi che l'utente sappia immediatamente:

1. di essere entrato nella partita;
2. come iniziare il primo turno;
3. come aprire la guida ai tasti rapidi.

La finestra deve continuare a inizializzare cartella, riga e colonna di
focus come oggi, ma senza produrre annunci tecnici che coprano il messaggio
di benvenuto.

---

## Attori e Concetti

| Attore / Concetto | File | Ruolo |
|---|---|---|
| FinestraGioco | bingo_game/ui/finestra_gioco.py | coordina focus iniziale e annuncio di ingresso |
| WxRenderer | bingo_game/ui/renderers/renderer_wx.py | vocalizza tramite AO2/NVDA |
| Vocalizzatore AO2 | my_lib/vocalizzatore.py | backend best-effort per output vocale |
| NVDA focus events | runtime UI | possono interrompere o sovrascrivere letture in coda |
| Report analisi | docs/4 - reports/REPORT_ANALISI_benvenuto_non_letto_avvio_partita_2026-04-14.md | evidenza tecnica del problema |

---

## Flussi Concettuali

### Flusso attuale

1. La configurazione apre FinestraGioco.
2. Il costruttore schedula `_imposta_focus_iniziale()` con `wx.CallAfter`.
3. `_imposta_focus_iniziale()` esegue tre dispatch di navigazione iniziale.
4. Ogni dispatch produce un annuncio AO2.
5. Il messaggio di benvenuto viene emesso solo dopo, in un `CallAfter` annidato.
6. NVDA e la coda AO2 rendono il benvenuto tardivo o impercettibile.

### Flusso target

1. La configurazione apre FinestraGioco.
2. `_imposta_focus_iniziale()` imposta il focus logico iniziale in modalita silenziosa.
3. Le griglie visive vengono aggiornate normalmente.
4. Il messaggio di benvenuto viene emesso una sola volta, subito, con priorita sulla coda precedente.
5. L'utente sente direttamente l'istruzione utile per iniziare la partita.

---

## Decisioni Architetturali

### D1 — Soppressione locale dei dispatch vocali iniziali

La soppressione della vocalizzazione deve restare confinata a FinestraGioco.
Non va modificato il comportamento standard del renderer, che e corretto per
tutte le altre interazioni della partita.

### D2 — Benvenuto con interruzione esplicita

Il messaggio di benvenuto deve essere emesso con `interrompi=True`, oppure
tramite un helper equivalente, per svuotare eventuale rumore residuo in coda.

### D3 — Eliminazione del CallAfter annidato

Il benvenuto non deve essere schedulato in un secondo ciclo idle. Va emesso
alla fine dell'inizializzazione silenziosa, cosi da ridurre la latenza e il
rischio di interferenze da focus change.

### D4 — Nessuna modifica a renderer, configurazione o vocalizzatore

La causa radice e nell'ordine delle operazioni di FinestraGioco. Il renderer
e il backend TTS rimangono invariati per evitare regressioni sistemiche.

---

## Rischi e Vincoli

### R1 — Regressione sul focus logico iniziale

Silenziare i dispatch iniziali non deve impedire l'allineamento corretto di
cartella, riga e colonna interne. Serve una soluzione che mantenga gli stessi
side effect di stato senza produrre voce.

### R2 — Doppia lettura del benvenuto

Se il benvenuto resta in `CallAfter` o viene emesso sia prima sia dopo il focus,
NVDA potrebbe leggerlo due volte. Il punto di emissione deve restare unico.

### R3 — Compatibilita con NVDA

Il testo deve restare breve, lineare e senza popup. Nessuna modale o tooltip.

### R4 — Copertura test limitata

Il comportamento reale dipende da NVDA in runtime Windows. I test automatici
potranno verificare il flusso di chiamata, ma non la resa audio completa.

---

## Report correlato

- [REPORT_ANALISI_benvenuto_non_letto_avvio_partita_2026-04-14.md](../4%20-%20reports/REPORT_ANALISI_benvenuto_non_letto_avvio_partita_2026-04-14.md)
