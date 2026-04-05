---
type: design
feature: fix_hotkey_f6_ctrl_shift_v
agent: Agent-Design
status: REVIEWED
version: v0.9.5
date: 2026-04-05
---

# DESIGN — Fix hotkey F6 e Ctrl+Shift+V

## 1. Idea in 3 righe

Due hotkey della finestra di gioco (`F6` e `Ctrl+Shift+V`) producono risultati
errati a runtime. `F6` crasha con `AttributeError` per un riferimento attributo
sbagliato. `Ctrl+Shift+V` non vocalizza alcuna cartella per un handler incompleto.

## 2. Attori e Concetti

| Attore / Concetto | Ruolo nel bug |
|---|---|
| `PannelloGriglia` (`finestra_gioco.py`) | Gestisce `EVT_KEY_DOWN`; qui risiede il bug F6 |
| `FinestraGioco` (`finestra_gioco.py`) | Frame principale; possiede `self._renderer` direttamente |
| `WxRenderer` (`renderer_wx.py`) | Contiene `ripeti_ultimo_annuncio()` e `_handle_visualizza_tutte_cartelle_avanzata()` |
| `EventoVisualizzaTutteCartelleAvanzata` (`eventi_output_ui_umani.py`) | Porta i dati di tutte le cartelle (griglia, stato, segnati) per il renderer |
| `IVocalizzatore` / `_ao2_vocalizza` | Layer voce che effettua la sintesi NVDA |

## 3. Flussi Concettuali

### Flusso A — F6 (stato attuale, errato)

```
[Utente preme F6]
  → PannelloGriglia._on_key_down
      → fg._finestra._renderer.ripeti_ultimo_annuncio()
                  ^^^^^^^^
                  AttributeError: FinestraGioco non ha '_finestra'
                  (è un attr di PannelloGriglia, non di FinestraGioco)
```

### Flusso A — F6 (corretto)

```
[Utente preme F6]
  → PannelloGriglia._on_key_down
      → fg è self._finestra  (FinestraGioco)
      → fg._renderer.ripeti_ultimo_annuncio()
          → IVocalizzatore.vocalizza_testo(ultimo_annuncio)
          → NVDA legge l'ultimo testo vocalizzato
```

### Flusso B — Ctrl+Shift+V (stato attuale, incompleto)

```
[Utente preme Ctrl+Shift+V]
  → PannelloGriglia._on_key_down
      → fg._dispatch(fg._comandi.visualizza_tutte_avanzate())
          → GiocatoreUmano.visualizza_tutte_cartelle_avanzata()
              → EventoVisualizzaTutteCartelleAvanzata.crea_da_cartelle(...)
                  → evento.cartelle = ((num, griglia, stato, segnati), ...)
          → WxRenderer.render_esito() → _dispatch_evento()
              → _handle_visualizza_tutte_cartelle_avanzata(evento)
                  → _wx_aggiorna_output("Tutte le N cartelle (avanzata).")
                  → _ao2_vocalizza("Tutte le N cartelle mostrate in modalità avanzata.")
                  [PROBLEMA: evento.cartelle non viene iterato → nessun contenuto]
```

### Flusso B — Ctrl+Shift+V (corretto)

```
[Utente preme Ctrl+Shift+V]
  ...
  → _handle_visualizza_tutte_cartelle_avanzata(evento)
      → per ogni (numero_c, griglia_semplice, stato_cartella, segnati) in evento.cartelle:
          → segnati_set = set(segnati)
          → per ogni riga in griglia_semplice:
              → celle = _formatta_cella(c, evidenziata=c in segnati_set)
          → parti.append("Cartella N: riga1 riga2 riga3")
      → testo = "\n".join(parti)
      → _wx_aggiorna_output(testo)           [area di testo/log aggiornata]
      → _ao2_vocalizza(testo)                [NVDA legge tutte le cartelle]
```

## 4. Decisioni Architetturali

### D1 — Bug F6: correzione con un solo carattere (attributo sbagliato)

La catena `fg._finestra._renderer` è semanticamente errata:
- `fg` è già l'istanza `FinestraGioco`, ottenuta in `PannelloGriglia.__init__`
  come `self._finestra = finestra`.
- `FinestraGioco` espone `self._renderer` direttamente (assegnato in `__init__`).
- Non esiste `FinestraGioco._finestra`.

Correzione: `fg._renderer.ripeti_ultimo_annuncio()`.
Nessuna modifica all'architettura, nessuna refactoring.

### D2 — Bug Ctrl+Shift+V: handler da completare (non stub)

L'handler `_handle_visualizza_tutte_cartelle_avanzata` è allo stato di stub
strutturale: output e vocalization esistono ma non usano i dati dell'evento.

Pattern di riferimento interno (già funzionante e testato):
- `_handle_visualizza_cartella_avanzata` → singola cartella avanzata:
  itera la griglia, chiama `_formatta_cella(c, evidenziata=...)` per i segnati,
  costruisce `testo` e chiama sia `_wx_aggiorna_output(testo)` sia `_ao2_vocalizza(testo)`.
- `_handle_visualizza_tutte_cartelle_semplice` → tutte le cartelle semplice:
  itera `evento.cartelle`, costruisce `testo`, aggiorna output,
  vocalizza solo il conteggio ("Tutte le N cartelle mostrate.").

Scelta per la versione avanzata:
- Itera `evento.cartelle` (identico allo semplice)
- Per ogni cartella usa `_formatta_cella(c, evidenziata=...)` (come singola avanzata)
- `_wx_aggiorna_output(testo)` con il contenuto completo
- `_ao2_vocalizza(testo)` con il contenuto completo (comportamento "avanzata":
  vocalizzo completo, coerente con `_handle_visualizza_cartella_avanzata`)

### D3 — Nessuna modifica al dominio né agli eventi

I bug sono localizzati esclusivamente nel layer di presentazione
(`finestra_gioco.py` e `renderer_wx.py`). Gli eventi di dominio e il
layer `GiocatoreUmano` sono corretti e non richiedono modifiche.

## 5. Rischi e Vincoli

| Rischio | Mitigazione |
|---|---|
| La vocalizzazione di N cartelle avanzate può essere lunga | Comportamento intenzionale: l'utente ha esplicitamente richiesto "tutte". L'interruzione è possibile via NVDA. |
| `_formatta_cella` con `evidenziata=True` deve distinguere int da "-" | Guard `isinstance(c, int)` già presente in tutti i handler analoghi. |
| Test esistenti su `_handle_visualizza_tutte_cartelle_avanzata` potrebbero assumere il comportamento stub | Verificare nella fase di test; aggiornare assertions se necessario. |
| `ripeti_ultimo_annuncio` richiede che `_ultimo_annuncio` sia stato impostato | Già gestito: se vuoto, vocalizza "Nessun annuncio precedente." |
