---
type: plan
feature: interfaccia_wx_finestre_configurazione_gioco
agent: Agent-Plan
status: DRAFT
version: v0.9.5
design_ref: docs/2 - projects/DESIGN_interfaccia_wx_finestre_configurazione_gioco.md
date: 2026-03-31
report_ref: docs/4 - reports/idea_sviluppo_intefaccia.md
---

## Metadati

tipo: coding_plan
titolo: Piano operativo finestre wx di configurazione e gioco principale
data_creazione: 2026-03-31
agente: Agent-Plan
stato: draft
feature: interfaccia_wx_finestre_configurazione_gioco
versione_progetto: v0.9.5
design: docs/2 - projects/DESIGN_interfaccia_wx_finestre_configurazione_gioco.md
report: docs/4 - reports/idea_sviluppo_intefaccia.md

## Contenuto

### Executive Summary

Tipo intervento: introduzione UI wxPython accessibile
Priorita: P1
Branch: main
Versione di riferimento: v0.9.5
Scope: definire e implementare il perimetro documentale e operativo per la finestra di configurazione partita e la finestra di gioco principale
Vincolo: restano fuori scope finestra iniziale autonoma, impostazioni avanzate, cartelle affiancate e rifiniture visive finali

### Problema e Obiettivo

Il repository possiede gia il motore di gioco, il sistema eventi e il primo perimetro
del renderer wx, ma non esiste ancora un piano operativo dedicato alle due finestre
centrali dell'esperienza utente: configurazione partita e gioco principale.

L'obiettivo del ciclo successivo e tradurre il DESIGN approvato in una sequenza di lavoro
 atomica, che permetta di costruire prima l'infrastruttura della finestra di configurazione,
poi la finestra di gioco, quindi i collegamenti tra focus, log annunci, ricerca numero e
pulsante principale a due stati, senza allargare lo scope oltre il necessario.

### File coinvolti

- [main.py](../../main.py) - MODIFY se necessario per bootstrap wx e apertura prima finestra utile
- [bingo_game/comandi_partita.py](../../bingo_game/comandi_partita.py) - MODIFY per completare la facciata dei comandi esposti alla UI
- [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py) - MODIFY per gestire stato locale, annunci, log e aggiornamenti widget
- [bingo_game/ui/renderers/base_renderer.py](../../bingo_game/ui/renderers/base_renderer.py) - MODIFY solo se servono piccoli adattamenti di contratto coerenti col design
- [my_lib/vocalizzatore.py](../../my_lib/vocalizzatore.py) - REUSE ONLY
- [bingo_game/ui/](../../bingo_game/ui) - CREATE nuovi moduli wx per frame, pannelli o dialog strettamente necessari
- [docs/2 - projects/DESIGN_interfaccia_wx_finestre_configurazione_gioco.md](../2%20-%20projects/DESIGN_interfaccia_wx_finestre_configurazione_gioco.md) - REFERENCE
- [docs/3 - coding plans/PLAN_interfaccia_wx_finestre_configurazione_gioco_v0.9.5.md](../3%20-%20coding%20plans/PLAN_interfaccia_wx_finestre_configurazione_gioco_v0.9.5.md) - CREATE
- [docs/5 - todolist/TODO_interfaccia_wx_finestre_configurazione_gioco_v0.9.5.md](../5%20-%20todolist/TODO_interfaccia_wx_finestre_configurazione_gioco_v0.9.5.md) - CREATE
- [docs/TODO.md](../TODO.md) - UPDATE

### Fasi sequenziali

#### Fase 1 - Struttura finestra di configurazione

File coinvolti:

- [bingo_game/ui/](../../bingo_game/ui)
- [bingo_game/comandi_partita.py](../../bingo_game/comandi_partita.py)

Operazione:

- CREATE o MODIFY dei moduli necessari per il frame di configurazione

Contenuto atteso:

- frame wx dedicato alla configurazione
- controlli minimi per nome giocatore, numero bot, numero cartelle e conferma
- focus iniziale sul primo controllo utile
- delega a ComandiSistema per creare la partita senza introdurre logica di dominio nel frame

#### Fase 2 - Transizione configurazione -> gioco

File coinvolti:

- [main.py](../../main.py)
- [bingo_game/ui/](../../bingo_game/ui)

Operazione:

- MODIFY del bootstrap e della transizione tra frame

Contenuto atteso:

- chiusura o hide controllato del frame di configurazione
- apertura del frame di gioco con titolo semantico
- trasferimento del riferimento alla partita creata
- preservazione del contesto necessario al renderer corrente

#### Fase 3 - Struttura finestra di gioco principale

File coinvolti:

- [bingo_game/ui/](../../bingo_game/ui)
- [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)

Operazione:

- CREATE o MODIFY dei componenti del frame di gioco

Contenuto atteso:

- pannello griglia focalizzabile come centro della navigazione
- pulsante principale a due stati: Inizia partita e Passa turno
- area log annunci consultabile
- wiring dei tasti categoria A e B definiti nel report

#### Fase 4 - Dialog modale ricerca numero e focus preservation

File coinvolti:

- [bingo_game/ui/](../../bingo_game/ui)
- [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)

Operazione:

- CREATE del dialog e MODIFY del renderer o del frame chiamante

Contenuto atteso:

- Ctrl+F apre dialog modale con focus iniziale sul campo input
- Invio conferma la ricerca
- AO2 vocalizza l'esito nel dialog prima della chiusura
- chiusura automatica e ritorno del focus al punto logico precedente

#### Fase 5 - Stato locale renderer e consultazione annunci

File coinvolti:

- [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py)

Operazione:

- MODIFY

Contenuto atteso:

- buffer ultimo annuncio per F6
- coda o sequenza ordinata degli annunci automatici
- aggiornamento coerente del widget log con Ctrl+E per consultazione
- nessun furto di focus durante vocalizzazione bot o premi

#### Fase 6 - Validazione minima non-GUI e smoke test manuale

File coinvolti:

- [tests/](../../tests)

Operazione:

- MODIFY solo se servono test mirati ai wrapper o al renderer headless-safe
- smoke test manuale su Windows con NVDA per i binding critici

Contenuto atteso:

- verifica che il bootstrap non rompa il motore esistente
- verifica comportamentale minima dei comandi esposti alla UI
- check empirico dei tasti categoria C prima del rilascio della feature completa

### Test Plan

- Eseguire test non-GUI mirati su eventuali wrapper introdotti in [bingo_game/comandi_partita.py](../../bingo_game/comandi_partita.py)
- Validare che il renderer continui a funzionare in modalita headless-safe con vocalizzatore nullo quando applicabile
- Eseguire smoke test manuale su Windows 11 con NVDA per:
  - apertura finestra configurazione
  - passaggio alla finestra di gioco
  - focus iniziale sulla griglia
  - dialog ricerca numero Ctrl+F
  - tasti categoria C da verificare empiricamente

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso