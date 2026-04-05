# Stato del Progetto — Tombola Stark

Data: 31 marzo 2026
Versione corrente: 0.9.5 (Unreleased in lavorazione)

---

## Scopo di questo report

Capire se il motore di gioco e tutto il lavoro fatto finora sono completi e solidi, in modo da poter passare con tranquillita alla fase successiva: costruire l'interfaccia grafica accessibile con wxPython e Accessible Output 2.

---

## Situazione generale in breve

Il progetto si trova in buone condizioni. Il motore del gioco (la logica che fa funzionare la tombola) e praticamente completo e ben strutturato. C'e un sistema di eventi gia pronto che fa da ponte tra il motore e qualsiasi interfaccia futura. Ci sono solo piccoli problemi da risolvere prima di partire con l'interfaccia grafica.

---

## Cosa funziona e cosa e completo

### Il Tabellone (gestione numeri 1-90)

Il tabellone fa tutto quello che deve fare:
- Estrae numeri a caso tra quelli rimasti
- Tiene traccia di quali numeri sono usciti e quali no
- Fornisce statistiche (percentuale avanzamento, ultimi numeri estratti)
- Si puo resettare completamente per una nuova partita
- Ha la sua eccezione dedicata quando i numeri finiscono

Stato: completo e funzionante.

### La Cartella (cartella del giocatore)

La cartella e il pezzo piu ricco di funzionalita:
- Si genera automaticamente rispettando le regole della tombola italiana (3 righe, 9 colonne, 5 numeri per riga)
- Segna i numeri estratti
- Verifica i premi riga per riga (ambo, terno, quaterna, cinquina)
- Verifica la tombola (cartella completamente segnata)
- Offre visualizzazioni sia semplici che avanzate (con indicazione dei segni)
- Naviga per riga e per colonna

Stato: completo e funzionante. Ha 35 metodi, tutti coperti da test.

### La Partita (coordinamento del gioco)

La partita orchestra tutto il flusso:
- Crea e gestisce il roster di giocatori (minimo 2, massimo 8)
- Gestisce gli stati della partita (non iniziata, in corso, terminata)
- Esegue turni completi (estrae, aggiorna giocatori, verifica premi)
- Assegna i premi senza duplicati (ricorda quali sono gia stati dati)
- Rileva la tombola e termina la partita
- Fornisce stato completo e sintetico per l'interfaccia

Stato: completo e funzionante. Ha 19 metodi pubblici.

### I Giocatori

Due tipi di giocatore, entrambi funzionanti:
- Giocatore umano: 31 metodi per navigazione completa (cartelle, righe, colonne), segnatura, ricerca numeri, reclamo vittorie, gestione del turno
- Giocatore automatico: eredita la logica base, si aggiorna automaticamente con i numeri estratti
- Mixin di gestione focus: helper centralizzato per gestire quale cartella/riga/colonna il giocatore sta "guardando"

Stato: completo. Il giocatore umano ha tutta la logica necessaria per ogni azione che si fa durante una partita.

### Il Controller (orchestrazione sicura)

Il controller fa da "cuscinetto di sicurezza" tra il motore e l'interfaccia:
- Crea partite complete con una sola chiamata (tabellone + giocatori + cartelle)
- Avvia partite in modo sicuro gestendo ogni eccezione
- Esegue turni catturando gli errori
- Fornisce lo stato sintetico della partita
- Ha un sistema di logging organizzato per categorie (game, prizes, system, errors)
- Non scrive mai sullo schermo direttamente (zero print)

Stato: completo e funzionante.

### Il Sistema Comandi

Classe ComandiSistema e ComandiGiocatoreUmano che espongono metodi semplici all'interfaccia senza richiedere conoscenza del controller. L'interfaccia puo chiamare metodi come "crea_nuova_partita", "avvia_partita", "esegui_turno" senza sapere cosa c'e sotto.

Stato: completo. Ponte pronto per essere usato dall'interfaccia wx.

### Il Sistema Eventi

Questo e un pilastro fondamentale per l'accessibilita. Ogni azione del gioco produce un evento strutturato (un oggetto dati, non una stringa) che contiene tutte le informazioni necessarie per:
- Mostrare qualcosa sullo schermo (widget wxPython)
- Dire qualcosa con la voce (Accessible Output 2)

I componenti sono:
- EsitoAzione: successo o fallimento con codice errore o evento allegato
- 26 tipi di eventi diversi per ogni situazione di gioco (navigazione, segnatura, tabellone, premi, ecc.)
- Codici errore centralizzati (nessuna stringa sparsa nel codice)
- Codici per configurazione, controller, messaggi sistema, output UI

Stato: completo e testato a fondo. 100% dei codici coperti da test.

### Le Eccezioni

Gerarchia completa di eccezioni personalizzate per ogni modulo:
- Tabellone, Cartella, Partita, Giocatore, Controller
- Ogni errore ha la sua eccezione specifica con messaggio chiaro

Stato: complete.

### Le Validazioni

Modulo dedicato per validare input e oggetti, usato sia dal giocatore umano che dal controller. Validazioni per tipo, range, coerenza.

Stato: complete e testate (29 test sulle validazioni input, 9 sulle validazioni oggetti).

### Il Catalogo Testi (Localizzazione)

Un file con tutti i messaggi in italiano, organizzati per categoria:
- Messaggi errori
- Messaggi configurazione
- Messaggi eventi
- Messaggi output UI
- Messaggi sistema
- Messaggi controller

Nessuna stringa e scritta direttamente nel codice del gioco. Tutto passa dal catalogo.

Stato: completo per l'italiano.

---

## Cosa e gia stato fatto per l'interfaccia wx

Esiste gia una base concreta:
- BaseRenderer: contratto astratto che definisce cosa deve fare qualsiasi interfaccia (render_esito, mostra_schermata_configurazione, mostra_report_finale)
- WxRenderer: prima implementazione concreta con struttura completa del dispatcher che smista tutti i 26 tipi di evento al handler corretto
- Separazione clear tra layer widget (prefisso _wx_) e layer voce (prefisso _ao2_)
- Il vocalizzatore e pronto: IVocalizzatore (contratto), NullVocalizzatore (per test), Vocalizzatore (adattatore verso Accessible Output 2)

Tuttavia: tutti gli handler del WxRenderer sono ancora stub vuoti (contengono solo "pass" e un commento TODO). Non c'e ancora nessun widget wx reale, nessun pannello, nessuna finestra.

---

## Stato dei test

Risultato dell'esecuzione completa: 642 test eseguiti, 639 passano, 3 errori.

I 3 errori sono:
1. test_estrai_numeri_esaurito (test_tabellone): il test si aspetta un ValueError, ma il codice ora lancia TabelloneNumeriEsauritiException (cambio introdotto nella versione unreleased ma non ancora riflesso in questo vecchio test)
2. test_gestione_errore_numeri_terminati (test_tabellone): stesso problema — test vecchio non aggiornato al nuovo tipo di eccezione
3. test_vocalizzatore (tests/unit): non riesce a importare perche il modulo accessible_output2 non e installato nell'ambiente di test

Nessuno di questi errori indica un problema nel motore di gioco. Sono solo disallineamenti tra codice aggiornato e test non ancora aggiornati.

### Copertura dei test per modulo

- Tabellone: test completi
- Cartella: test completi
- Partita: test completi
- Game Controller: test completi (inclusi test del loop e del silent controller)
- Giocatore Base: test completi
- Giocatore Umano: 67 test (copertura estesa)
- Giocatore Automatico: test specifici (bot attivo)
- Helper Focus: 21 test diretti
- Comandi Partita: test completi
- Validazioni: 38 test diretti
- Sistema Eventi: test completi per tutti i gruppi (A-E), 100% copertura
- Vocalizzatore: 8 test (ma richiedono accessible_output2 installato)
- Event Logging e Game Logger: test dedicati

---

## Problemi da risolvere prima di passare all'interfaccia wx

### Problema 1 — Aggiornare 2 test del tabellone (priorita bassa)

Due test vecchi aspettano ValueError invece della nuova TabelloneNumeriEsauritiException. Fix rapido: cambiare l'eccezione attesa nei test. Non e un problema di logica, solo di allineamento.

### Problema 2 — Installare accessible_output2 nell'ambiente (prerequisito)

Il modulo vocalizzatore importa accessible_output2 a livello di modulo. Se la libreria non e installata, il test fallisce e anche il renderer wx non puo funzionare. Prima di lavorare sull'interfaccia, accessible_output2 deve essere installato e funzionante nel virtual environment.

### Problema 3 — main.py e un placeholder (atteso)

Il file main.py attualmente stampa solo un messaggio "interfaccia non ancora disponibile". Questo e intenzionale: sara sostituito con il vero avvio dell'app wx quando l'interfaccia sara pronta.

---

## Si puo passare all'interfaccia wx?

Si, con buona sicurezza. Il quadro e il seguente:

### Cosa e gia pronto e solido

- Tutta la logica di gioco (dominio) e completa e testata
- Il controller orchestra tutto in modo sicuro
- Il sistema eventi produce dati strutturati per ogni situazione
- Il catalogo testi e pronto per l'italiano
- Il contratto del renderer (BaseRenderer) e definito
- La struttura del WxRenderer con dispatcher completo e gia in piedi
- Il vocalizzatore e progettato con dependency injection (facile da usare nei test)
- La separazione tra logica e presentazione e rispettata ovunque

### Cosa manca per l'interfaccia

- Creare la finestra principale wx (wx.Frame) con i pannelli necessari
- Implementare i widget: pannello cartella, pannello tabellone, pannello output, pannello configurazione, pannello report finale
- Riempire gli stub del WxRenderer con la logica reale (aggiornamento widget + vocalizzazione)
- Collegare i comandi da tastiera ai metodi di ComandiSistema e ComandiGiocatoreUmano
- Testare l'accessibilita con NVDA
- Creare il loop principale dell'applicazione wx

### Rischi minimi

- I 2 test disallineati del tabellone sono un fix da pochi minuti
- Il modulo accessible_output2 e gia in requirements.txt, basta installarlo
- Non ci sono lacune nella logica di gioco che potrebbero emergere durante lo sviluppo dell'interfaccia

---

## Mappa riassuntiva

| Area | Stato | Note |
|---|---|---|
| Tabellone | Completo | 2 test da allineare alla nuova eccezione |
| Cartella | Completo | 35 metodi, tutti testati |
| Partita | Completo | 19 metodi, ciclo di gioco funzionante |
| Giocatore Umano | Completo | 31 metodi, supporto focus completo |
| Giocatore Automatico | Completo | Bot funzionante |
| Controller | Completo | Orchestrazione sicura, zero print |
| Comandi Partita | Completo | Ponte pronto per interfaccia |
| Sistema Eventi | Completo | 26 tipi di evento, testati al 100% |
| Eccezioni | Complete | Gerarchia per ogni modulo |
| Validazioni | Complete | 38 test diretti |
| Catalogo testi | Completo | Italiano, struttura estensibile |
| BaseRenderer | Completo | Contratto astratto definito |
| WxRenderer | Struttura pronta | Dispatcher completo, handler vuoti (stub) |
| Vocalizzatore | Completo | Richiede accessible_output2 installato |
| Test | 639/642 verdi | 3 errori non bloccanti |
| main.py | Placeholder | Da sostituire con avvio app wx |

---

## Conclusione

Il progetto e nella condizione ideale per passare alla fase di costruzione dell'interfaccia grafica. Il motore di gioco e completo, testato e stabile. Il sistema eventi e il catalogo testi sono gia pensati per alimentare l'interfaccia senza toccare la logica. La struttura del renderer wx e gia impostata e aspetta solo di essere riempita con i widget reali.

I problemi aperti sono trascurabili (2 test da aggiornare, 1 libreria da installare) e non bloccano in alcun modo lo sviluppo dell'interfaccia.
