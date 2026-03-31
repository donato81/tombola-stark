---
type: todo
feature: interfaccia_wx_finestre_configurazione_gioco
agent: Agent-Plan
status: DRAFT
version: v0.9.5
plan_ref: docs/3 - coding plans/PLAN_interfaccia_wx_finestre_configurazione_gioco_v0.9.5.md
design_ref: docs/2 - projects/DESIGN_interfaccia_wx_finestre_configurazione_gioco.md
date: 2026-03-31
report_ref: docs/4 - reports/idea_sviluppo_intefaccia.md
---

## Metadati

tipo: todo_task
titolo: TODO finestre wx di configurazione e gioco principale
data_creazione: 2026-03-31
agente: Agent-Plan
stato: in_corso
feature: interfaccia_wx_finestre_configurazione_gioco
versione_progetto: v0.9.5
plan: docs/3 - coding plans/PLAN_interfaccia_wx_finestre_configurazione_gioco_v0.9.5.md
design: docs/2 - projects/DESIGN_interfaccia_wx_finestre_configurazione_gioco.md
report: docs/4 - reports/idea_sviluppo_intefaccia.md

## Contenuto

### Descrizione task

Implementare il primo perimetro wxPython accessibile dedicato alla finestra di
configurazione partita e alla finestra di gioco principale, seguendo le decisioni
fissate nel design e nel report di analisi senza estendere lo scope a impostazioni
avanzate, cartelle affiancate o rifiniture visive finali.

### Priorita

P1

### Agente assegnato

Agent-CodeRouter

### Riferimento project/plan padre

- Project: [DESIGN_interfaccia_wx_finestre_configurazione_gioco.md](../2%20-%20projects/DESIGN_interfaccia_wx_finestre_configurazione_gioco.md)
- Plan: [PLAN_interfaccia_wx_finestre_configurazione_gioco_v0.9.5.md](../3%20-%20coding%20plans/PLAN_interfaccia_wx_finestre_configurazione_gioco_v0.9.5.md)
- Report: [idea_sviluppo_intefaccia.md](../4%20-%20reports/idea_sviluppo_intefaccia.md)

## Checklist operativa

### Passo 1 - Finestra di configurazione

- [x] Creare la struttura wx del frame di configurazione
- [x] Posizionare il focus iniziale sul primo controllo utile
- [x] Collegare i controlli minimi a ComandiSistema
- [x] Gestire conferma ed errori senza spostare logica di dominio nella UI

### Passo 2 - Transizione al frame di gioco

- [x] Aprire il frame di gioco principale dopo configurazione valida
- [x] Passare la partita creata al nuovo frame
- [x] Garantire annuncio naturale del cambio finestra via titolo frame
- [x] Chiudere o nascondere il frame precedente in modo coerente

### Passo 3 - Finestra di gioco principale

- [x] Creare il pannello griglia focalizzabile
- [x] Impostare focus iniziale sulla griglia all'apertura
- [x] Implementare Escape per uscire dalla griglia e Tab per rientrare
- [x] Aggiungere il pulsante principale a due stati
- [x] Aggiungere area log annunci consultabile

### Passo 4 - Binding e dialog di ricerca

- [x] Implementare i binding categoria A sul pannello griglia
- [x] Implementare i binding categoria B sul frame principale
- [x] Introdurre Ctrl+F con dialog modale di ricerca numero
- [x] Vocalizzare il risultato nel dialog prima della chiusura
- [x] Ripristinare il focus alla posizione precedente

### Passo 5 - Stato locale renderer e annunci

- [x] Aggiungere buffer ultimo annuncio per F6
- [x] Aggiornare il log annunci in parallelo alla vocalizzazione AO2 (duck typing aggiungi_a_log)
- [ ] Garantire che bot e premi non rubino il focus (da verificare con NVDA)
- [x] Collegare Ctrl+E alla consultazione della cronologia annunci

### Passo 6 - Validazione

- [x] Eseguire test non-GUI impattati dai wrapper UI
- [ ] Verificare smoke test manuale su Windows con NVDA
- [ ] Verificare empiricamente i tasti categoria C
- [x] Aggiornare questo TODO dopo ogni fase completata

## Note operative

- Il task copre solo configurazione e gioco principale.
- Le impostazioni avanzate e la finestra iniziale autonoma restano fuori scope.
- Ogni fase deve essere committable separatamente nel ciclo di implementazione.
- Dopo ogni fase completata va aggiornata la checklist prima di procedere alla successiva.

## Stato Avanzamento

- [x] Pianificato
- [x] In corso
- [ ] Completato
- [ ] Verificato
