# Report Diagnosi Alfa — Tombola Stark

- Data: 2026-04-13
- Agente: Agent-Analyze
- Scope: diagnosi profonda su accessibilita NVDA, orientamento giocatore,
  report di fine partita, lettura vittorie
- Versione analizzata: Unreleased (post v0.13.0)

---

## 1. Pannelli NVDA letti come "panel" senza nome

### Problema

NVDA legge "panel" generico per i pannelli visivi della finestra di gioco.
Questo accade perche i seguenti componenti non hanno `SetName()`:

- `PannelloTabellone` (riga 91 di finestra_gioco.py): nessun `SetName()`.
  NVDA lo annuncia come "panel" senza contesto.
- `PannelloCartella` (riga 140): nessun `SetName()`. Letto come "panel".
- `PannelloRiepilogoFinale` (riga 292): nessun `SetName()`. Letto come "panel".
- `HeaderBar` (riga 496): nessun `SetName()`. Letto come "panel".
- Il `wx.Panel` radice `self._panel` creato in `_build_ui` (riga 636):
  nessun `SetName()`.

### Componenti gia conformi

- `PannelloGriglia` (riga 383): ha `SetName("Griglia cartella")` — corretto.
- Tutti i pulsanti hanno `SetName()` adeguato.
- Il `_log_ctrl` ha `SetName("Log annunci...")` — corretto.

### Intervento richiesto

Per ogni pannello privo di `SetName`, aggiungere una chiamata con etichetta
semantica comprensibile da NVDA:

- `PannelloTabellone`: `self.SetName("Tabellone estrazioni")`
- `PannelloCartella`: `self.SetName("Cartella giocatore")` (o nome dinamico)
- `PannelloRiepilogoFinale`: `self.SetName("Riepilogo finale partita")`
- `HeaderBar`: `self.SetName("Barra informativa partita")`
- `self._panel`: `self._panel.SetName("Area di gioco")`

Nota: poiche questi pannelli hanno `~wx.TAB_TRAVERSAL` (non focalizzabili),
NVDA li legge solo in modalita browse o con NVDA+Tab. Il `SetName` garantisce
comunque un'etichetta utile quando il giocatore esplora la finestra.

---

## 2. Assenza di guida orientativa all'avvio della partita

### Problema

Quando il giocatore preme "Inizia partita" nella finestra di gioco, non
riceve alcun messaggio di orientamento. Il flusso attuale:

1. Dalla configurazione si apre `FinestraGioco` (finestra_gioco.py riga 564).
2. Il focus va su `PannelloGriglia` (riga 625-628).
3. `_imposta_focus_iniziale()` imposta cartella 1, riga 1, colonna 1 (riga 1410).
4. Il renderer vocalizza "Cartella 1 selezionata" e le coordinate,
   ma non c'e nessun messaggio introduttivo.

Il giocatore non sa:

- Dove si trova nella finestra di gioco.
- Cosa deve fare come prima azione.
- Quali tasti sono disponibili.
- Che deve premere il pulsante "Inizia partita" per estrarre il primo numero.

### Intervento richiesto

Aggiungere un annuncio di benvenuto/orientamento vocale subito dopo il
focus iniziale, con contenuto simile a:

"Sei nella finestra di gioco. Premi Inizia partita o Ctrl+Invio per
estrarre il primo numero. Premi Ctrl+H per la guida ai tasti rapidi."

Posizione suggerita: alla fine di `_imposta_focus_iniziale()` oppure come
`wx.CallAfter` dopo il focus, nel costruttore di `FinestraGioco`.

---

## 3. Report di fine partita troppo minimale

### Problema

Il dizionario `dati_report` costruito alla fine della partita
(finestra_gioco.py righe 1031-1037) contiene:

```python
dati_report = {
    "turni_giocati": self._turno_corrente,
    "conteggio_estratti": self._partita.tabellone.get_conteggio_estratti(),
    "premi_gia_assegnati": list(getattr(self._partita, "premi_gia_assegnati", [])),
    "vincitore_tombola": self._ottieni_vincitore_tombola(),
    "giocatori": [g.nome for g in self._partita.giocatori],
}
```

### Dati mancanti nel report

- **Vincitori per tipo premio**: `premi_gia_assegnati` e un set di chiavi
  interne (es. `"cartella_0_riga_1_ambo"`) e non contiene il nome del
  vincitore. Il renderer costruisce il report usando queste chiavi opache,
  ottenendo output non leggibile.
- **Dettaglio per giocatore**: nessuna statistica per giocatore
  (numeri segnati, cartelle completate, premi vinti).
- **Cronologia premi con vincitori**: la `Partita` traccia `premi_tipo_chiusi`
  e `ultimo_premio_evento` ma non una lista storica completa
  `[(tipo, giocatore, turno)]`.
- **Numeri estratti in ordine**: manca la sequenza ordinata delle estrazioni.
- **Durata della partita**: nessun timestamp inizio/fine.
- **Stato cartelle del giocatore umano**: quanti numeri segnati, percentuale,
  se mancavano numeri alla tombola.

### Vocalizzazione report (renderer_wx.py righe 133-161)

Il testo vocalizzato e:

"Partita terminata. Turni giocati: N. Numeri estratti: N su 90.
Tombola vinta da: X. Premi assegnati: [lista opaca]."

La lista premi tenta di leggere `p.get('premio')` e `p.get('giocatore')`
ma i dati nel set `premi_gia_assegnati` sono stringhe chiave, non dizionari.
Questo genera output "? per ?" per ogni premio.

### Pannello visivo riepilogo (PannelloRiepilogoFinale)

Il pannello mostra solo: titolo, vincitore, turni, estratti su 90 e una
lista premi. Ma la lista premi soffre dello stesso problema dei dati opachi.

### Intervento richiesto

- Mantenere nella `Partita` una lista storica dei premi assegnati con
  tipo, giocatore, turno e cartella (non solo chiavi).
- Includere nel `dati_report` questa lista storica, i numeri estratti
  in ordine e le statistiche per giocatore.
- Arricchire il testo vocalizzato con:
  - Elenco premi per tipo e vincitore.
  - Statistica giocatore umano (numeri segnati / totali).
  - Quanti numeri mancavano alla tombola per il giocatore umano.
- Aggiornare `PannelloRiepilogoFinale.mostra()` per visualizzare
  tutti questi dati.

---

## 4. Lettura NVDA ultima vittoria e prossimo premio (Ctrl+G / Ctrl+I)

### Stato attuale

- **Ctrl+G** (`stato_premi`): funziona correttamente.
  Restituisce: "Ultimo premio: X vinto da Y. Prossimo: Z."
  I dati provengono da `ultimo_premio_evento` (dizionario con
  "premio" e "giocatore") e `premi_tipo_chiusi`.

- **Ctrl+I** (`dettaglio_premi`): **parzialmente funzionante**.
  Restituisce solo i tipi di premio chiusi senza vincitori:
  "Premi assegnati in questa partita: - ambo - terno"
  **Manca il nome del vincitore per ogni premio.**

### Causa

`dettaglio_premi()` (comandi_partita.py righe 480-497) legge solo
`premi_tipo_chiusi` (set di stringhe tipo) senza accedere ai dati dei
vincitori. Non esiste una struttura dati nella Partita che mappi
`tipo -> [(giocatore, cartella, turno)]`.

### Intervento richiesto

- Aggiungere alla `Partita` un attributo `storico_premi: list[dict]`
  che accumuli ogni premio assegnato con tipo, giocatore, cartella e turno.
- `dettaglio_premi()` deve ricostruire l'elenco da `storico_premi`
  producendo output: "Ambo vinto da Bot1. Terno vinto da Giocatore."
- Stessa lista va usata anche nel report finale (punto 3).

---

## 5. Riepilogo gap per chiusura versione alfa

### Gia funzionante

- Ciclo di gioco completo: estrazione, segnazione, reclami, verifica premi,
  tombola, pausa, ripresa.
- Navigazione completa cartelle (semplice e avanzata), righe, colonne.
- Binding tastiera completi (3 categorie, 35+ combinazioni).
- Guida tasti rapidi (Ctrl+H) e guida regole (Ctrl+Shift+H).
- Pausa/ripresa gioco (Ctrl+P) con ripristino timer.
- Ricerca numeri nelle cartelle (Ctrl+F).
- Timer finestra d'azione con avvisi progressivi.
- Griglie visive sincronizzate (tabellone + cartella con colori semantici).
- Animazione lampeggio su cella estratta.
- Header bar informativa.
- Finestra principale, configurazione, transizioni tra finestre.
- Test NVDA superati.

### Gap da risolvere per l'alfa

| ID | Area | Priorita | Descrizione |
|----|------|----------|-------------|
| G1 | NVDA | Alta | Pannelli senza SetName (Tabellone, Cartella, Riepilogo, Header, Panel radice) |
| G2 | NVDA | Alta | Nessun messaggio di orientamento all'avvio della finestra di gioco |
| G3 | Report | Alta | Report di fine partita minimale: manca dettaglio vincitori, statistiche, cronologia |
| G4 | NVDA | Media | Ctrl+I non mostra i vincitori dei premi, solo i tipi |
| G5 | Dominio | Media | Manca storico_premi nella Partita (necessario per G3 e G4) |
| G6 | Report | Bassa | Pannello riepilogo visivo (PannelloRiepilogoFinale) da arricchire |

### Stima impatto

- G1: modifica puntuale in `finestra_gioco.py` — 5 righe `SetName()`.
- G2: aggiunta messaggio vocale in `_imposta_focus_iniziale()` o
  nel costruttore — 3-5 righe codice + 1 entry locale.
- G3+G5: modifica strutturale in `partita.py` (nuovo attributo
  `storico_premi`), aggiornamento in `_assegna_premi()`, modifica in
  `finestra_gioco.py` (costruzione `dati_report`) e in
  `renderer_wx.py` (`mostra_report_finale`).
- G4: aggiornamento `dettaglio_premi()` in `comandi_partita.py` per
  leggere da `storico_premi` invece che da `premi_tipo_chiusi`.
- G6: aggiornamento `PannelloRiepilogoFinale.mostra()` per i nuovi dati.

---

## 6. Suggerimento prossimo agente

Per implementare i gap identificati, il passo successivo e:

- **Agent-Design**: per definire la struttura `storico_premi` e il
  contratto del report finale arricchito (impatta dominio e UI).
- **Agent-Code**: per le modifiche puntuali G1 e G2 (basso rischio).
