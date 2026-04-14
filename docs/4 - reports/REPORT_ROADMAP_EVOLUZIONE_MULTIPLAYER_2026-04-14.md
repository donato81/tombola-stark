# REPORT — Roadmap Evoluzione verso Multiplayer Online

> **Data analisi**: 14 aprile 2026  
> **Versione baseline**: 0.14.0-alpha  
> **Autore analisi**: Agent-Analyze (Tombola Stark Framework)  
> **Priorita del report**: strategico / pianificazione a lungo termine

---

## 1. Baseline: Stato Attuale (v0.14.0-alpha)

### Punti di forza dell'architettura esistente

- **Clean Architecture a 3 livelli** (Dominio, Controller, Presentazione) gia ben separata.
  Il dominio e puro Python standard-library senza dipendenze esterne: facile da isolare.
- **Sistema eventi strutturati** (`bingo_game/events/`) gia progettato per
  comunicare stati di gioco senza accoppiamento UI. Questo e il contratto naturale
  per una futura comunicazione di rete.
- **Accessibilita NVDA-first** consolidata: ogni feature nuova deve mantenere
  questo vincolo, anche quando si aggiungono suoni o UI più ricche.

### Lacune rispetto alla visione target

| Lacuna | Impatto per il multiplayer |
|--------|---------------------------|
| Nessun layer di persistenza (Infrastructure) | Blocca utenti, statistiche, salvataggi |
| Nessun sistema utente / identita | Blocca auth, lobby, crediti |
| Solo partita locale, 1 umano + bot | Blocca multiplayer |
| Nessuna comunicazione di rete | Blocca gioco online |
| Nessun suono | Riduce coinvolgimento |
| Nessuna economia virtuale | Blocca monetizzazione futura |

---

## 2. Requisiti Identificati dall'Utente

1. Sistema di salvataggio (gia pronto per evolversi in cloud)
2. Scheda utente dettagliata (profilo, registrazione, login)
3. Statistiche di gioco (vittorie, partite giocate, ecc.)
4. Salvataggio e ripresa della partita
5. Sistema crediti (gratuiti ora, a pagamento in futuro)
6. Suoni per migliorare l'esperienza di gioco
7. Multiplayer online come traguardo finale

---

## 3. Analisi di Fattibilita

### 3.1 Sistema di Salvataggio

**Fattibilita**: Alta  
**Tecnologia consigliata**: SQLite (locale), migrabile verso PostgreSQL/MySQL per il server.  
**Note architetturali**: Richiede l'introduzione di un quarto layer: **Infrastructure**.
La classe `Partita` e gia serializzabile logicamente (tabellone, giocatori, premi, turni):
mancano solo le repository per scrivere e leggere da DB.  
**Pattern da usare**: Repository Pattern + Unit of Work.  
Il contratto dei repository deve usare interfacce astratte (`ABC`) in modo che il layer
di Infrastructure possa essere sostituito senza toccare Dominio o Controller.

### 3.2 Scheda Utente / Registrazione / Login

**Fattibilita**: Media-Alta (per uso locale), Media (per uso online)  
**Note architetturali**:
- Per la versione locale: hash della password con `bcrypt` o `argon2`, nessun testo
  in chiaro su db. Questo e sufficiente per proteggere i dati locali.
- Per la versione online: aggiungere JWT (JSON Web Tokens) per sessioni stateless.
  La scelta di JWT oggi rende la migrazione al server quasi indolore domani.
- Il modello `Utente` vive nel Domain. Le operazioni di auth (hashing, token) vivono
  nell'Infrastructure. Il Controller usa un `AuthService` come middleware.
- La UI aggiunge una FinestraRegistrazione e una FinestraLogin in wxPython
  con pieno supporto NVDA (label, TabOrder, AcceleratorTable).

### 3.3 Statistiche di Gioco

**Fattibilita**: Alta (dopo persistenza)  
**Note architetturali**:
- I dati minimi da tracciare: `partite_giocate`, `vittorie`, `premi_ottenuti`
  (ambo, terno, quaterna, cinquina, tombola), `monete_vinte`, `monete_perse`.
- Il `GameController` gia ha `ottieni_stato_sintetico()`: puo essere esteso
  per passare i risultati a un `StatisticheRepository` al termine di ogni partita.
- In futuro, le statistiche possono alimentare un sistema di classifiche online.

### 3.4 Salvataggio e Ripresa della Partita

**Fattibilita**: Alta (dopo persistenza)  
**Note architetturali**:
- Lo stato completo da serializzare: numeri estratti da tabellone, cartelle con
  numeri segnati, premi assegnati, stato giocatori, configurazione partita.
- La classe `Partita` ha gia `get_stato_completo()`: questo metodo e il punto
  di serializzazione naturale.
- Si aggiunge un metodo `ripristina_da_stato(stato: dict)` / factory in Controller.
- Il flusso UI: nuovo menu "Continua partita" in FinestraPrincipale, dialog di
  selezione partita salvata.
- Vincolo: lo snapshot deve essere atomico (usa transazione DB) per evitare
  stati corrotti.

### 3.5 Sistema Crediti

**Fattibilita**: Alta per crediti virtuali gratuiti, Media per integrazione pagamento  
**Note architetturali**:
- Crediti come campo intero in `Utente` su DB. Ogni partita costa X crediti, la
  vittoria ne restituisce di piu.
- Il `CreditiService` (Infrastructure) gestisce debit/credit con log delle transazioni
  (per audit futuro e anti-cheat).
- Per la monetizzazione online: integrare Stripe o PayPal nel server tramite webhook;
  non tocca il client wxPython.
- Accessibilita: il saldo crediti deve essere annunciato da NVDA a ogni variazione
  significativa (wx.PostEvent con evento dedicato).

### 3.6 Sound Effects

**Fattibilita**: Alta  
**Note architetturali**:
- Usare `pygame.mixer` o la libreria `playsound` (piu leggera). Per accessibilita
  NVDA: i suoni NON sostituiscono mai il parlato. Sono strato aggiuntivo.
- Suoni suggeriti: estrazione numero, ambo, terno, quaterna, cinquina, tombola,
  click navigazione, errore, benvenuto.
- Aggiungere opzione "Disabilita suoni" nella finestra configurazione (on/off).
- I file audio risiedono in `bingo_game/assets/sounds/` come `.wav` o `.ogg`.
- Il `SoundManager` e un singleton nel layer Infrastructure (mai nel Dominio).

### 3.7 Multiplayer Online

**Fattibilita**: Media (con requisiti tecnici non banali)  
**Note architetturali**:
- Richiede un server dedicato (Python + FastAPI o Django Channels).
- Comunicazione real-time tramite WebSockets (non polling HTTP).
- Il client wxPython comunica col server via un `NetworkAdapter` nel layer
  Infrastructure. Il layer Dominio non sa nulla di rete.
- La lobby online: stanze di gioco, wait room, lista giocatori connessi.
- Il tabellone e gestito lato server (autorita sul numero estratto) per
  prevenire cheating.
- Richiede CDN/cloud per i salvataggi (sostituisce SQLite locale con API REST).

---

## 4. Roadmap delle Fasi (Ordine Logico Consigliato)

La sequenza rispetta le dipendenze tecnologiche: ogni fase sblocca la successiva.

---

### FASE 1 — Infrastructure Layer + Persistenza Locale

> Versione target: **v0.15.x-beta**  
> Priorita: CRITICA — tutto il resto dipende da questa fase

**Deliverable**:
- Introduzione del layer `bingo_game/infrastructure/` con:
  - `database/db_manager.py` (SQLite, connessione, migrazione schema)
  - `repositories/` (interfacce ABC + implementazioni SQLite):
    - `PartitaRepository`
    - `UtenteRepository` (base, per fase 2)
    - `StatisticheRepository` (base, per fase 3)
- Schema DB iniziale: tabelle `partite`, `utenti`, `statistiche`, `crediti_log`
- Nessuna UI ancora: solo layer dati testabile via unit test

**Impatto architetturale**:
- Aggiunta dipendenza `bingo_game/infrastructure/` senza toccare Domain
- Controller aggiornato per usare repositories (iniezione dipendenza)
- Test: 90%+ coverage sul layer Infrastructure

---

### FASE 2 — Sistema Utente: Profilo, Registrazione, Login

> Versione target: **v0.16.x-beta**  
> Priorita: ALTA — abilita personalizzazione e statistiche personali

**Deliverable**:
- Modello `Utente` in `bingo_game/domain/models/utente.py`
- `AuthService` in `bingo_game/application/auth_service.py`
- Hash password con `argon2-cffi` (piu sicuro di bcrypt per nuovi progetti)
- JWT per sessioni (libreria: `PyJWT`)
- UI wxPython:
  - `FinestraRegistrazione` (nome, email, password, conferma password)
  - `FinestraLogin` (email, password, "Ricordami")
  - Profilo utente accessibile da menu principale
- Validazione input con feedback NVDA real-time (es. "Password troppo corta")
- Accessibilita NVDA: tutti i form con label wx.StaticText associati

**Impatto architetturale**:
- Domain: nuovo modello `Utente`
- Infrastructure: `UtenteRepository` implementato
- Presentation: 2 nuove finestre + menu aggiornato

---

### FASE 3 — Statistiche di Gioco e Storico

> Versione target: **v0.17.x-beta**  
> Priorita: ALTA — valore percepito alto per l'utente

**Deliverable**:
- Salvataggio automatico risultato post-partita nel `StatisticheRepository`
- Finestra "Le tue statistiche" con:
  - Partite giocate / vinte / perse
  - Premi ottenuti per tipo (ambo, terno, ...)
  - Miglior partita (meno turni per tombola)
  - Crediti totali guadagnati/persi
- Export opzionale statistiche come file `.txt` (accessibilita: leggibile da NVDA)
- Grafico a barre testuale (ASCII) per utenti screen-reader

---

### FASE 4 — Salvataggio e Ripresa della Partita

> Versione target: **v0.18.x-beta**  
> Priorita: MEDIA-ALTA — QoL significativa

**Deliverable**:
- Metodo `Partita.serializz_stato()` (snapshot completo)
- `PartitaRepository.salva_checkpoint(utente_id, stato)` con transazione atomica
- Menu "Pausa e Salva" durante la partita (gia esiste "Pausa": da estendere)
- Finestra "Continua partita" all'avvio con lista partite sospese
- Limite: max 3 partite sospese per utente (free tier)
- Versioning schema: ogni checkpoint include version tag per compatibilita futura

---

### FASE 5 — Sistema Crediti Virtuali

> Versione target: **v0.19.x-beta**  
> Priorita: MEDIA

**Deliverable**:
- Campo `crediti` in `Utente`, gestito da `CreditiService`
- Costo partita configurabile (default: 0 crediti per ora)
- Premio vittoria configurabile per tipo (tombola > cinquina > ... > ambo)
- Log transazioni in tabella `crediti_log` (audit trail)
- Saldo crediti visibile in FinestraPrincipale e FinestraGioco
- Annuncio NVDA del saldo a ogni variazione
- "Crediti bonus" all'apertura giornaliera (prepara il modello daily reward)

---

### FASE 6 — Sound Effects & Audio Enhancement

> Versione target: **v0.20.x-beta**  
> Priorita: MEDIA — alto impatto sull'esperienza

**Deliverable**:
- `SoundManager` singleton in `bingo_game/infrastructure/audio/sound_manager.py`
- Libreria: `pygame.mixer` (gia disponibile in ecosistema wxPython/Windows)
- Suoni da produrre:
  - `numero_estratto.wav` — campana o effetto leggero
  - `ambo.wav`, `terno.wav`, `quaterna.wav`, `cinquina.wav` — escalation crescente
  - `tombola.wav` — effetto celebrativo
  - `click_navigazione.wav` — feedback navigazione tastiera
  - `errore.wav` — azione non valida
  - `benvenuto.wav` — avvio applicazione
- Opzione "Suoni: ON/OFF" nella FinestraConfigurazione
- Volume regolabile (slider accessibile NVDA)
- I suoni NON si sovrappongono al parlato NVDA: usare threading non bloccante

---

### FASE 7 — Modalita Multiplayer Locale (stesso PC, turni alternati)

> Versione target: **v1.0.x**  
> Priorita: BASSA-MEDIA — step intermedio verso il multiplayer online

**Deliverable**:
- Supporto a piu giocatori umani registrati sullo stesso PC
- Turni alternati con notifica NVDA del passaggio turno
- Sistema "profilo attivo" per login rapido
- Statistiche per ciascun utente aggiornate al termine della partita

---

### FASE 8 — Pre-Online: API Layer e Auth Distribuita

> Versione target: **v1.1.x**  
> Priorita: BASSA (preparatoria)

**Deliverable**:
- Definizione interfacce `NetworkAdapter` astratte in Infrastructure
  (cosi il domain e controller non cambiano nella fase 9)
- Server FastAPI minimale (Python, stessa lingua del client): endpoint CRUD per
  utenti e partite, autenticazione JWT
- Migrazione DB locale SQLite → PostgreSQL sul server
- Sync cloud dei salvataggi tramite API REST (get/post checkpoint)
- Test di integrazione client-server in ambiente locale

---

### FASE 9 — Multiplayer Online

> Versione target: **v2.0.x**  
> Priorita: TRAGUARDO FINALE

**Deliverable**:
- Server FastAPI + WebSockets (Django Channels come alternativa)
- Sistema Lobby: crea stanza, cerca stanza, lista stanze pubbliche
- Autorità tabellone lato server (anti-cheat: il numero estratto viene dal server)
- Chat testuale in lobby (accessibile NVDA: lettura automatica nuovi messaggi)
- Classifica globale (leaderboard)
- Sync crediti online (crediti locali restano per offline, cloud per online)
- Client wxPython aggiornato con `NetworkAdapter` WebSocket implementato

---

## 5. Dipendenze tra Fasi (Grafo)

```
Fase 1 (Infrastructure/DB)
    └── Fase 2 (Utenti/Auth)
            └── Fase 3 (Statistiche)
            └── Fase 4 (Salvataggio)
                    └── Fase 5 (Crediti)
                            └── Fase 7 (Multiplayer Locale)
                                    └── Fase 8 (API Layer)
                                            └── Fase 9 (Multiplayer Online)
Fase 6 (Suoni) — indipendente, inseribile dopo Fase 1 in qualsiasi momento
```

---

## 6. Suggerimenti Aggiuntivi (Extra Value)

Oltre ai requisiti dichiarati, questi elementi aumenterebbero significativamente
la qualita e il coinvolgimento del prodotto finale:

### 6.1 Sistema Achievement / Trofei

- Traguardi sbloccabili: "Prima tombola", "10 partite senza perdere", "Ambo fulmine"
- Annuncio NVDA dello sblocco con effetto sonoro dedicato
- Visible nel profilo utente

### 6.2 Modalita Veloce / Timer

- Variante con timer per estrazione (pressione psicologica)
- Gia presente la gestione `STRICT/PERMISSIVE` nell'architettura: da espandere

### 6.3 Tema Visivo Personalizzabile

- Tema chiaro / scuro / alto contrasto (accessibilita visiva + preferenza utente)
- Gia esiste `bingo_game/ui/tema.py`: estendere con profili tema

### 6.4 Daily Challenge

- Una partita "sfida del giorno" con configurazione speciale e premi crediti bonus
- Incentiva il ritorno giornaliero all'app

### 6.5 Replay Partita

- Possibilita di rivedere la sequenza di estrazione di una partita conclusa
- Utile per statistiche avanzate e debug

### 6.6 Modalita Torneo (fase online)

- Bracket a eliminazione diretta tra N giocatori online
- Premi crediti scalabili in base alla posizione

### 6.7 Notifiche Push (versione online)

- Notifiche Windows quando una stanza è pronta o un amico ti invita
- Implementabile con `windows-toasts` (Python, Windows 10/11)

### 6.8 Esportazione Cartella (accessibilita)

- Esporta la propria cartella come file `.txt` leggibile da NVDA
  o come immagine per condivisione social

---

## 7. Stack Tecnologico Consigliato per Fasi Future

| Componente | Tecnologia | Note |
|------------|-----------|------|
| Persistenza locale | SQLite + `sqlite3` stdlib | Zero dipendenze extra |
| Persistenza server | PostgreSQL + `asyncpg` | Performance async |
| ORM | `SQLAlchemy 2.x` | Supporta sia SQLite che PG |
| Auth | `argon2-cffi` + `PyJWT` | Sicuro, moderno |
| Server API | `FastAPI` | Veloce, type-safe, async |
| WebSocket | `websockets` / FastAPI nativo | Per multiplayer real-time |
| Audio | `pygame.mixer` | Gia in ecosistema wxPython |
| Pagamento (futuro) | Stripe API | Webhook, no PCI scope |

---

## 8. Stima di Complessita per Fase

| Fase | Complessita | Durata Stimata (sviluppo singolo dev) | Prerequisiti |
|------|------------|--------------------------------------|-------------|
| 1 — Infrastructure | Media | 2-3 settimane | Nessuno |
| 2 — Utenti / Auth | Media | 2-3 settimane | Fase 1 |
| 3 — Statistiche | Bassa | 1 settimana | Fase 2 |
| 4 — Salvataggio | Media | 1-2 settimane | Fase 1, 2 |
| 5 — Crediti | Bassa | 1 settimana | Fase 2, 4 |
| 6 — Suoni | Bassa | 1 settimana | Autonoma |
| 7 — Multiplayer Locale | Bassa | 1 settimana | Fase 2-5 |
| 8 — API Layer | Alta | 3-4 settimane | Fase 7 |
| 9 — Multiplayer Online | Alta | 4-6 settimane | Fase 8 |

---

## 9. Rischi e Mitigazioni

| Rischio | Impatto | Mitigazione |
|---------|---------|-------------|
| Rottura accessibilita NVDA con neue UI | Alto | Validare ogni nuova finestra con checklist `validate-accessibility.skill.md` |
| Schema DB non evolutivo | Alto | Usare migrazioni (`Alembic`) fin dalla Fase 1 |
| Password in chiaro su DB | Critico | `argon2-cffi` obbligatorio, hash al momento della registrazione |
| Crediti manipolabili localmente | Medio | Log transazioni + checksum lato server in Fase 8 |
| Suoni bloccano parlato NVDA | Alto | SoundManager su thread separato senza blocco UI |
| Latenza WebSocket in gioco online | Medio | Logica di predizione lato client + reconciliation server |

---

## 10. Conclusione

L'architettura attuale di Tombola Stark e **gia ben posizionata** per questa
evoluzione. Il rispetto della Clean Architecture, sistema eventi, e nessuna
logica di business nel layer UI sono elementi che facilitano l'aggiunta di
Infrastructure senza riscrivere il dominio.

**L'investimento piu critico e la Fase 1** (Infrastructure Layer + SQLite):
sblocca tutte le fasi successive e richiede attenzione nella definizione
delle interfacce repository per non dover fare refactor quando si passa al server.

**L'accessibilita NVDA rimane un vincolo non negoziabile** in ogni fase:
ogni nuova finestra, ogni notifica, ogni suono deve essere progettato con
NVDA come utente primario.

Il traguardo del multiplayer online e raggiungibile in un orizzonte di
6-12 mesi di sviluppo attivo, procedendo fase per fase senza saltare prerequisiti.

---

*Report generato da Agent-Analyze — Tombola Stark Framework v1.10.3*
