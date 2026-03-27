# Report Analisi Stato Progetto — Tombola Stark

> Data: 27 marzo 2026
> Versione analizzata: [Unreleased] / v0.10.0 base

---

## Panoramica Generale

Il progetto è **circa all'80% di completamento** per un MVP giocabile in sessione singola.
L'architettura è ben strutturata e coerente, il motore di gioco è funzionale.
Le aree critiche sono la mancanza di vocalizzazione runtime integrata, la persistenza
e alcuni fix UX nel focus.

---

## Motore di Gioco — Stato Implementazione

### Completamente funzionante

- **Tabellone**: estrazione numeri 1-90 non ripetuti, storico estrazioni, reset.
- **Cartella**: generazione 15 numeri con 7 regole di validazione (3 max/colonna, 5/riga, range), segnatura, verifica premi.
- **Tutti e 5 i premi**: ambo, terno, quaterna, cinquina, tombola — verifica corretta, deduplicazione tramite set chiavi univoche.
- **Partita**: macchina a stati (`non_iniziata → in_corso → terminata`), orchestrazione tabellone + giocatori, turni.
- **GameController**: facade sicura, intercetta tutte le eccezioni, logging semantico, snapshot stato.
- **Bot automatici**: reclami automatici end-of-turn, gerarchia premi (tombola > cinquina > ...), terminazione partita.
- **Configurazione pre-partita**: `TerminalUI` a 5 stati per raccogliere nome, numero bot, cartelle.
- **Game loop interattivo v0.10.0**: 26 tasti mappati via `msvcrt` senza necessità di Invio, dispatch corretto.

### Parzialmente implementato

- **Focus colonna**: non viene auto-impostato alla prima apertura — è `None` finché l'utente
  non sposta esplicitamente la colonna. Crea un'esperienza non fluida con NVDA.
- **Navigazione avanzata** (`vai_a_riga_avanzata`, `vai_a_colonna_avanzata`): usa `input()`
  grezzo senza try/except robusto nel loop TUI.
- **Renderer output**: base implementato, formattazione multi-riga non sempre ottimizzata
  per screen reader.
- **Tasto Help (`?`)**: collegato ma restituisce messaggio statico, non dinamico.

---

## Architettura — Coerenza e Problemi

### Rispettata

- **Dominio isolato**: `tabellone.py`, `cartella.py`, `partita.py` — zero import da layer superiori.
- **Facade controller**: `GameController` espone solo operazioni sicure, senza stato di business.
- **Event-driven**: ogni azione ritorna `EsitoAzione(ok, evento, errore)`.
- **Immutabilità**: `ComandoTasto`, `ReclamoVittoria` sono frozen dataclass.
- **Logging**: zero `print()` in `src/`, tutto passa per `GameLogger`.

### Problemi identificati

1. **TUI accede direttamente a `GiocatoreUmano`** invece di passare per il controller.
2. **`accessible_output2`** è importato in `my_lib/vocalizzatore.py` ma non è in `requirements.txt`.
3. **`Partita.esegui_turno()`** modifica `_turno_corrente` come side effect senza restituirlo nel dict.
4. **wxPython** è in `requirements.txt` ma non viene usato da nessuna parte del codice.

---

## Cosa Manca Completamente

- **Vocalizzazione runtime**: `my_lib/vocalizzatore.py` esiste ma non è mai chiamato dal loop TUI.
- **Persistenza**: zero serializzazione — fine sessione equivale a perdita di tutti i dati.
- **GUI wxPython**: libreria installata, mai iniziata.
- **Configurazione avanzata**: nessun file `.ini`/`.json` per parametri.
- **Visualizzazione tabellone numeri estratti** in forma navigabile: dati presenti, rendering non richiamato.

---

## Passi Successivi — In Ordine di Priorità

### Priorità 1 — Fix UX immediati (v0.11.0)

1. **Auto-impostazione focus colonna** al primo accesso alla cartella.
2. **Robustezza input nei prompt** (`R`, `C`, `E`, `V`, `N`): try/except con re-prompt.
3. **Integrazione `Vocalizzatore` nel loop TUI** per NVDA.

### Priorità 2 — Fix architetturali (v0.11.0 / v0.12.0)

4. **Aggiungere `accessible_output2` a `requirements.txt`** (o fallback no-op).
5. **Rimuovere accesso diretto TUI → `GiocatoreUmano`**.

### Priorità 3 — Funzionalità nuove a bassa complessità

6. **Visualizzazione tabellone** nel loop (tasto `T`): dati già disponibili, manca il binding.
7. **Help dinamico** dal catalogo `codici_tasti_tui.py` anziché stringa statica.

### Priorità 4 — Completamento per produzione (v1.0.0)

8. **Persistenza partita** (JSON snapshot).
9. **CI GitHub Actions**.
10. **Build `.exe` via cx_freeze**.

### Priorità 5 — Roadmap futura (v2.0.0+)

11. **GUI wxPython** con pannelli navigabili e `wx.Accessible`.
12. **Modalità torneo / multi-partita**.

---

## Sintesi Quantitativa

| Area | Stato | Stima |
|------|-------|-------|
| Core Game Engine | Completo | 100% |
| Verifica Premi (5 tipi) | Completo | 100% |
| Bot automatici | Completo | 100% |
| Game loop TUI v0.10.0 | Completo | 95% |
| Navigazione focus giocatore | Parziale | 75% |
| Renderer output | Parziale | 70% |
| Vocalizzazione runtime | Mancante | 5% |
| Persistenza partita | Mancante | 0% |
| GUI wxPython | Mancante | 0% |
| **Totale stimato** | | **~80%** |

---

## Coerenza Architetturale — Giudizio Finale

L'architettura a livelli è rispettata nel nucleo. Le violazioni rilevate sono localizzate
e correggibili senza refactor esteso. Il sistema eventi è maturo e pronto per connettere
vocalizzazione e GUI senza modificare il dominio.

Il progetto è idoneo per sessione singola giocabile oggi.
Per v1.0.0 produzione i requisiti bloccanti sono: vocalizzazione integrata
e gestione robusta degli input.
