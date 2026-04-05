# Report di Analisi — Proposta Interfaccia wxPython Tombola Stark

**Autore analisi:** Agent-Analyze
**Data:** 31 marzo 2026
**Oggetto:** Valutazione della bozza di design comportamentale per l'interfaccia wxPython accessibile
**Versione motore:** 0.9.5
**Modalita:** Sola lettura — nessun file di progetto modificato

---

## Sommario

Questo report analizza la proposta di interfaccia wxPython fornita dall'utente confrontandola con lo stato attuale del codebase di Tombola Stark. L'analisi copre: allineamento architetturale, copertura del sistema eventi, fattibilita dei tasti rapidi, gap identificati e raccomandazioni.

---

## 1. Allineamento architetturale

### 1.1 Layer separation — Molto buono

La proposta rispecchia correttamente la catena di dipendenze gia documentata in ARCHITECTURE.md:

```
ComandiSistema / ComandiGiocatoreUmano
        |
   GameController
        |
   Partita -> Tabellone / Giocatori / Cartelle
        |
   WxRenderer (dispatcher gia presente)
     +-- handler widget (_wx_*)
     +-- handler voce (_ao2_*) -> Vocalizzatore -> AO2
```

Il renderer_wx.py esistente riceve gia `wx.Frame` e `IVocalizzatore` tramite dependency injection, senza creare ne la finestra ne il backend AO2. Questo e coerente con il principio della proposta: la GUI e un layer sopra il motore, non un sostituto.

### 1.2 Sistema eventi — Dichiarazione corretta

La proposta afferma che il sistema eventi e "chiuso e completo con 26 tipi di evento". Verificato nel codebase:

- 3 handler focus/navigazione
- 6 handler visualizzazione cartelle
- 3 handler navigazione riga
- 3 handler navigazione colonna
- 2 handler segnazione/ricerca
- 5 handler tabellone
- 3 handler flusso partita (reclamo, esito reclamo, fine turno)
- 1 handler errore generico
- 1 handler evento sconosciuto

Totale: 27 handler nel dispatcher (inclusi errore e sconosciuto). Tutti gli handler sono stub con commento TODO. Il dispatcher effettivamente copre tutte le famiglie di interazione previste dalla proposta.

### 1.3 Contratto BaseRenderer — Allineato

Il BaseRenderer in base_renderer.py definisce 4 metodi astratti:
- `render_esito(esito)` — dispatcher principale
- `mostra_schermata_configurazione(stato)` — configurazione
- `mostra_report_finale(dati_partita)` — riepilogo fine partita
- `mostra_messaggio_sistema(testo)` — messaggi generici

La proposta prevede esattamente queste fasi: configurazione (Finestra 2), gioco con eventi (Finestra 3), report finale. Il contratto e sufficiente.

---

## 2. Copertura della mappa tasti rispetto al dominio

### 2.1 Metodi GiocatoreUmano gia implementati

GiocatoreUmano in players/giocatore_umano.py ha gia i metodi per:
- `imposta_focus_cartella(numero)` — mappa a Ctrl+1..6
- `riepilogo_cartella_corrente()` — mappa a consultazione cartella
- `riepilogo_cartella_precedente/successiva()` — mappa a Ctrl+frecce
- Navigazione riga (su/giu con modalita semplice e avanzata)
- Navigazione colonna (sinistra/destra con modalita semplice e avanzata)
- Segnazione numero — mappa a Spazio
- Ricerca numero in cartelle — mappa a Ctrl+F
- Reclamo vittoria (ambo/terno/quaterna/cinquina/tombola) — mappa a F1..F5
- Passa turno con reclamo opzionale — mappa a Ctrl+P

La mappa tasti della proposta copre quasi 1:1 i metodi gia presenti nel dominio. Questo e un punto di forza significativo: non servono nuovi metodi nel dominio per supportare l'interfaccia proposta.

### 2.2 Metodi ComandiSistema gia implementati

ComandiSistema in comandi_partita.py espone:
- `crea_nuova_partita(nome, num_cartelle, num_bot)` — Finestra 2
- `avvia_partita(partita)` — pulsante "Inizia partita"
- `esegui_turno(partita)` — pulsante "Passa turno"
- `stato_partita(partita)` — consultazioni varie
- `ha_tombola(partita)` — verifica fine partita
- `is_terminata(partita)` — condizione uscita loop

### 2.3 ComandiGiocatoreUmano — Placeholder

La classe ComandiGiocatoreUmano e attualmente un placeholder vuoto con solo `__init__`. Non espone ancora nessun metodo. L'interfaccia wx dovra chiamare direttamente i metodi di GiocatoreUmano oppure questa classe dovra essere completata come facade.

Questo e un gap implementativo, non di design: i metodi nel dominio esistono, manca solo il layer di facciata.

---

## 3. Valutazione delle scelte di design

### 3.1 Punti di forza

- **Accessibilita come base, non come strato aggiuntivo**: la regola "se non ha un tasto rapido, non esiste" e coerente con l'architettura accessibility-first del progetto
- **Modalita cartella singola come default**: riduce il carico cognitivo per lo screen reader, la modalita affiancata e opt-in
- **Focus preservation**: "il focus torna esattamente dove era" e il comportamento corretto per NVDA; il sistema di focus nel dominio (helper_focus.py + GestioneFocusMixin) supporta gia questo pattern
- **Bot senza furto di focus**: Accessible Output 2 puo vocalizzare senza spostare il focus wx; gli eventi dei bot passano dal renderer voce (_ao2_*) senza toccare i widget di input
- **Annuncio iniziale con vocabolario coerente**: "Cartella 1 di N, riga 1" fin dal primo momento insegna il formato di navigazione
- **Dichiarazione vittoria con F1-F5**: diretti, senza modificatori, non conflittuali con NVDA
- **Pulsante a due stati**: semplifica l'interfaccia a un singolo punto di azione principale

### 3.2 Punti di attenzione

#### 3.2.1 Tasti potenzialmente conflittuali con wx o NVDA — Strategia di binding definita

I tasti rapidi sono divisi in tre categorie di binding, dal piu debole al piu forte:

**Categoria A — Binding normale su pannello griglia (wx.EVT_KEY_DOWN)**:
- Frecce direzionali (navigazione riga e colonna, semplice e avanzata)
- Shift + frecce
- Tasti 1/2/3 (solo quando il pannello griglia ha il focus)
- Escape
- Spazio (segnazione numero)
- V, Shift+V, Shift+Ctrl+V (visualizzazione cartella)
- S (stato focus)
- F1, F2, F3, F4, F5 (dichiarazione vittoria)
- F6 (ripeti ultimo annuncio)

**Categoria B — Binding forte sulla finestra principale (wx.EVT_CHAR_HOOK con event.Skip(False) per bloccare la propagazione)**:
- Ctrl+P (passa turno — conflitto potenziale con stampa wx)
- Ctrl+F (cerca numero — conflitto potenziale con ricerca wx)
- Alt+1..9 (salta a colonna — conflitto potenziale con menu accelerator wx)
- Ctrl+1..6 (salta a cartella)

**Categoria C — Tasti a rischio intercettazione NVDA, da verificare empiricamente su NVDA reale PRIMA dell'implementazione dei binding**:
- Ctrl+T (ultimo numero estratto — NVDA puo usarlo per leggere l'ora)
- Ctrl+L (lista numeri estratti — potenziale conflitto NVDA)
- Ctrl+U (ultimi 5 estratti — verificare)
- Ctrl+R (riepilogo tabellone — verificare)

Per i tasti di categoria C: implementarli con wx.EVT_CHAR_HOOK come categoria B, ma documentare esplicitamente nel codice che richiedono verifica empirica su NVDA prima del rilascio. Se i test empirici rivelano conflitti, i tasti alternativi candidati sono: Ctrl+Shift+T, Ctrl+Shift+L, Ctrl+Shift+U, Ctrl+Shift+R.

#### 3.2.2 Tasti numerici 1/2/3 per righe — Decisione definita

Decisione: un pannello wx dedicato alla griglia cattura i tasti 1/2/3 quando ha il focus. Il meccanismo di contesto e definito come segue:
- Il focus entra nella griglia automaticamente all'apertura della finestra di gioco
- Il tasto Escape esce dalla griglia e sposta il focus verso i pulsanti
- Il tasto Tab permette di rientrare nella griglia dai pulsanti

I tasti 1/2/3 sono nella Categoria A (binding su pannello griglia, wx.EVT_KEY_DOWN): sono attivi solo quando il pannello griglia ha il focus e non sono intercettati dalla finestra principale.

#### 3.2.3 Strategia finestre — Decisione definita

Decisione: tre wx.Frame separati. Ogni cambio di finestra e un vero cambio di finestra; NVDA annuncia automaticamente il cambio leggendo il titolo del nuovo frame, senza richiedere annunci manuali tramite AO2. Il WxRenderer dovra essere adattato per ricevere un riferimento al frame corrente aggiornato ad ogni transizione.

#### 3.2.4 Finestra impostazioni condivisa

La proposta prevede una finestra impostazioni richiamabile sia dall'avvio che durante la partita. Questo implica un wx.Dialog modale. E una scelta corretta: il Dialog modale mantiene il focus e NVDA lo annuncia naturalmente. Al ritorno, il focus torna alla finestra chiamante.

---

## 4. Gap identificati

### 4.1 Game loop e integrazione con wx event loop — Risolto

Decisione: il click del pulsante "Passa turno" / "Inizia partita" chiama `ComandiSistema.esegui_turno()` in modo sincrono nel main thread wx, senza threading. Il turno e veloce e non richiede operazioni I/O pesanti. Dopo l'esecuzione del turno, il renderer aggiorna la UI e AO2 vocalizza gli eventi in sequenza ordinata: numero estratto -> premi bot -> premi umano -> fine turno.

### 4.2 Sequenza annunci bot e premi

La proposta dice che "eventi dei bot vengono vocalizzati automaticamente senza spostare il focus" e registrati in un'area testuale consultabile. Questo implica:
- Un widget wx.TextCtrl di log (read-only) accessibile con un tasto rapido dedicato
- Una coda di annunci AO2 ordinata (numero estratto -> premi bot -> premi umano -> fine turno)
- Tasto rapido per consultare il log degli annunci (non presente nella mappa tasti attuale)

**Gap risolto**: aggiunto Ctrl+E come tasto per consultare la cronologia degli annunci (vedi matrice al punto 5).

### 4.3 Stato "Inizia partita" vs "Passa turno"

Il pulsante a due stati richiede:
- Uno stato booleano che cambi dopo la prima estrazione
- Il cambio di etichetta wx del pulsante (SetLabel)
- NVDA legge l'etichetta se il focus e sul pulsante

Il dominio non ha un flag "primo turno eseguito" esplicito. Si puo derivare da `tabellone.storico_estrazioni` (lista vuota = primo turno). Non serve modificare il dominio.

### 4.4 Tasto F6 "Ripeti ultimo annuncio"

Questo richiede un buffer dell'ultimo testo vocalizzato nel renderer_wx. Attualmente il renderer non mantiene stato tra le chiamate (ogni handler e indipendente). Servira aggiungere un attributo `_ultimo_annuncio: str` nel WxRenderer.

### 4.5 Tasto S "Stato focus corrente"

Il dominio ha gia `EventoStatoFocusCorrente` e il relativo handler stub nel renderer. Il metodo corrispondente in GiocatoreUmano esiste gia (restituisce cartella/riga/colonna in focus). Nessun gap.

---

## 5. Copertura eventi vs tasti rapidi — Matrice

| Tasto | Azione proposta | Evento dominio esistente | Metodo dominio | Stato |
|---|---|---|---|---|
| Ctrl+frecce | Naviga cartelle | EventoRiepilogoCartellaCorrente, EventoLimiteNavigazioneCartelle | riepilogo_cartella_precedente/successiva | Coperto |
| Ctrl+1..6 | Salta a cartella N | EventoFocusCartellaImpostato | imposta_focus_cartella | Coperto |
| Frecce su/giu | Riga semplice | EventoNavigazioneRiga | navigazione riga semplice | Coperto |
| Shift+frecce su/giu | Riga avanzata | EventoNavigazioneRigaAvanzata | navigazione riga avanzata | Coperto |
| 1/2/3 | Salta a riga N | EventoVaiARigaAvanzata | vai a riga diretta | Coperto |
| Frecce sx/dx | Colonna semplice | EventoNavigazioneColonna | navigazione colonna semplice | Coperto |
| Shift+frecce sx/dx | Colonna avanzata | EventoNavigazioneColonnaAvanzata | navigazione colonna avanzata | Coperto |
| Alt+1..9 | Salta a colonna N | EventoVaiAColonnaAvanzata | vai a colonna diretta | Coperto |
| V | Visualizza semplice | EventoVisualizzaCartellaSemplice | visualizza cartella semplice | Coperto |
| Shift+V | Visualizza avanzata | EventoVisualizzaCartellaAvanzata | visualizza cartella avanzata | Coperto |
| Shift+Ctrl+V | Visualizza tutte | EventoVisualizzaTutteCartelleAvanzata | visualizza tutte cartelle | Coperto |
| Spazio | Segna numero | EventoSegnazioneNumero | segnazione numero | Coperto |
| Ctrl+F | Cerca numero | EventoRicercaNumeroInCartelle | ricerca numero in cartelle | Coperto |
| Ctrl+T | Ultimo estratto | EventoUltimoNumeroEstratto | ultimo numero estratto | Coperto |
| Ctrl+U | Ultimi 5 estratti | EventoUltimiNumeriEstratti | ultimi numeri estratti | Coperto |
| Ctrl+R | Riepilogo tabellone | EventoRiepilogoTabellone | riepilogo tabellone | Coperto |
| Ctrl+L | Lista completa | EventoListaNumeriEstratti | lista numeri estratti | Coperto |
| S | Stato focus | EventoStatoFocusCorrente | stato focus corrente | Coperto |
| F6 | Ripeti annuncio | Nessuno (da aggiungere nel renderer) | Nessuno | Gap renderer |
| F1..F5 | Dichiara vittoria | EventoReclamoVittoria | annuncia_ambo/terno/etc. | Coperto |
| Ctrl+P | Passa turno | EventoFineTurno | passa turno con reclamo | Coperto |
| Escape | Esci griglia | Nessuno (gestione wx pura) | Nessuno | Nuovo (solo wx) |
| Ctrl+E | Consulta log annunci | Nessuno (widget TextCtrl log) | Nessuno | Nuovo (solo wx — widget TextCtrl log) |

Copertura: 21 su 24 azioni hanno gia eventi e metodi nel dominio. I 3 gap (F6, Escape, Ctrl+E) sono risolvibili nel layer di presentazione senza modifiche al dominio.

---

## 6. Aspetti non definiti nella proposta (dichiarati)

La proposta dichiara esplicitamente di non definire:
- Scelta dei widget wxPython specifici
- Layout visivo per utenti vedenti
- Colori, font e stili grafici
- Modalita cartelle affiancate

Queste esclusioni sono corrette per una specifica comportamentale. Saranno materia del DESIGN tecnico successivo.

---

## 7. Raccomandazioni

### 7.1 Punti da chiarire nel design tecnico

- **Input ricerca numero (Ctrl+F)**: Ctrl+F apre un dialog modale con un campo di testo dove l'utente digita il numero da cercare e preme Invio per confermare. Il dialog si apre con il focus gia sul campo di input. AO2 vocalizza il risultato direttamente nel dialog prima che si chiuda (es. "Numero 45 trovato in cartella 2, riga 1, gia segnato" oppure "Numero 45 non presente in nessuna cartella"). Il dialog si chiude automaticamente dopo aver fornito il risultato e il focus torna esattamente sulla posizione precedente. Il dialog NON rimane aperto in attesa di ulteriori ricerche: per cercare un altro numero l'utente preme nuovamente Ctrl+F. Decisione definitiva.
- **Verifica empirica tasti Categoria C**: prima dell'implementazione dei binding, testare su NVDA reale che Ctrl+T, Ctrl+U, Ctrl+R, Ctrl+L arrivino all'applicazione. Se necessario, adottare le alternative Ctrl+Shift+* documentate al punto 3.2.1

### 7.2 Adattamenti necessari al codebase esistente

- **ComandiGiocatoreUmano**: completare la classe come facade per i metodi di GiocatoreUmano, in modo che l'interfaccia wx chiami la facade e non il dominio direttamente
- **WxRenderer._ultimo_annuncio**: aggiungere buffer per supportare F6
- **WxRenderer init**: adattare per supportare aggiornamento del riferimento al frame corrente a ogni transizione tra le tre finestre
- **Stub handler**: tutti i 26 handler sono stub (TODO); il grosso del lavoro di implementazione e qui

### 7.3 Rischi bassi

- Il sistema eventi e effettivamente completo per le interazioni proposte
- Il pattern EsitoAzione -> dispatcher -> handler (_wx_ + _ao2_) e gia validato
- Il Vocalizzatore e gia iniettabile e testabile (NullVocalizzatore per test, Vocalizzatore reale per produzione)
- I cataloghi messaggi (locales/it.py) hanno gia i codici per tutti gli eventi

---

## 8. Conclusione

La proposta e solida e ben allineata con l'architettura esistente. Il 91% delle azioni previste dalla mappa tasti ha gia eventi e metodi nel dominio. I gap sono nel layer di presentazione (stub handler da implementare, ComandiGiocatoreUmano da completare, buffer F6) e non richiedono modifiche al motore di gioco.

Tutti i punti critici identificati in fase di analisi sono stati risolti con decisioni definitive:
1. **Strategia finestre**: tre wx.Frame separati — NVDA annuncia automaticamente il cambio di finestra
2. **Contesto griglia**: pannello wx dedicato, focus automatico all'apertura, Escape per uscire, Tab per rientrare
3. **Strategia binding tasti**: tre categorie (A normale, B EVT_CHAR_HOOK, C EVT_CHAR_HOOK con tag verifica NVDA)
4. **Game loop**: sincrono nel main thread wx, nessun threading necessario
5. **Input ricerca numero (Ctrl+F)**: dialog modale con campo di input, AO2 vocalizza nel dialog, chiusura automatica, focus preservation

Il documento e completo in tutte le sue parti e pronto per la fase di design tecnico.

---

*Report generato da Agent-Analyze in modalita read-only. Nessun file di progetto e stato modificato.*
