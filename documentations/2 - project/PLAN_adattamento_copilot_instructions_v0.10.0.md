# PLAN — Adattamento copilot-instructions.md al Progetto Tombola Stark

**Tipo:** Adattamento documento di configurazione  
**Priorità:** Alta  
**Stato:** READY  
**Branch:** main  
**Versione target:** v0.10.0  
**Data creazione:** 2026-02-22  
**File sorgente da modificare:** `.github/copilot-instructions.md`

---

## Executive Summary

Il file `.github/copilot-instructions.md` è stato importato da un progetto esterno
(Solitario Classico Accessibile) e contiene numerosi riferimenti, esempi di codice,
architetture e avvisi critici specifici di quel progetto. Nessuno di questi contenuti
è pertinente a Tombola Stark. L'obiettivo di questo piano è adattare completamente
il file affinché Copilot riceva istruzioni corrette, coerenti con l'architettura,
i moduli, i pattern e i vincoli reali di questo progetto.

Il rischio di non intervenire è concreto: Copilot potrebbe generare codice che
importa classi inesistenti, usa path di layer sbagliati, applica pattern da wxPython
o produce esempi di test basati su un dominio completamente diverso.

---

## Problema Dettagliato

### Problema 1 — Titolo e identità del documento

**Attuale:**
```
# Copilot Custom Instructions - Solitario Classico Accessibile
```

**Impatto:** Copilot identifica il progetto in modo errato fin dalla prima riga.
Ogni inferenza contestuale parte da un'identità sbagliata.

**Soluzione:** Sostituire il titolo con:
```
# Copilot Custom Instructions - Tombola Stark
```

**Motivazione:** Il titolo è il primo elemento letto da Copilot e orienta tutto
il contesto del documento. Deve rispecchiare il progetto reale.

---

### Problema 2 — Struttura dei layer (Clean Architecture)

**Attuale:** I path indicati sono:
```
src/domain/
src/application/
src/infrastructure/
src/presentation/
```
Con esempi di import come:
```python
from src.infrastructure.ui.dialogs import VictoryDialog
from src.application.game_engine import GameEngine
```

**Impatto:** Copilot genererà import con path inesistenti. Il progetto Tombola Stark
non ha una cartella `src/` e i layer sono organizzati diversamente.

**Soluzione:** Sostituire con la struttura reale del progetto:
```
bingo_game/                  # radice del package applicativo
bingo_game/players/          # GiocatoreUmano, GiocatoreBase, bot, mixin
bingo_game/events/           # EsitoAzione, eventi di output UI, eventi partita
bingo_game/validations/      # funzioni di validazione input e oggetti
bingo_game/ui/               # TUI, renderer, localizzazione
bingo_game/ui/tui/           # tui_partita.py, tui_menu.py
bingo_game/ui/renderers/     # TerminalRenderer
bingo_game/ui/locales/       # it.py (dizionario stringhe UI)
bingo_game/game_controller.py  # unico punto di accesso al dominio dalla UI
```

Con esempi di import corretti:
```python
# CORRETTO — accesso al dominio dalla TUI solo via controller
from bingo_game.game_controller import esegui_turno_sicuro, ottieni_stato_sintetico

# VIETATO — import diretto di classi Domain dalla TUI
from bingo_game.players.giocatore_umano import GiocatoreUmano  # NO dalla TUI
```

**Motivazione:** Copilot deve conoscere la struttura reale per generare import
corretti e rispettare il vincolo architetturale principale del progetto:
la TUI non importa mai classi Domain direttamente.

---

### Problema 3 — Esempi nei naming conventions

**Attuale:** Gli esempi usano nomi del dominio solitario:
```python
def ensure_guest_profile(self, name: str, set_as_default: bool = False) -> Optional[UserProfile]:
draw_count, SessionOutcome, ProfileService, MAX_RECENT_SESSIONS
```

**Impatto:** Copilot impara naming e firme che non appartengono a questo progetto
e potrebbe replicarle nei suggerimenti.

**Soluzione:** Sostituire con esempi reali del progetto:
```python
# Variabili/Funzioni: snake_case
imposta_focus_cartella, sposta_focus_riga_su_semplice, esegui_turno_sicuro

# Classi: PascalCase
GiocatoreUmano, GestioneFocusMixin, TerminalRenderer, EsitoAzione

# Costanti: UPPER_SNAKE_CASE
MAX_CARTELLE_GIOCATORE, NUMERO_MIN_TOMBOLA, NUMERO_MAX_TOMBOLA

# Private: prefisso _
_indice_cartella_focus, _reset_focus_riga_e_colonna, _esito_ha_cartelle

# Esempio di firma corretta:
def imposta_focus_cartella(self, numero_cartella: int) -> EsitoAzione:
    """
    Imposta il focus su una cartella specifica (input umano 1-based).

    Args:
        numero_cartella: Numero cartella in formato umano (1..N).

    Returns:
        EsitoAzione con ok=True e EventoFocusCartellaImpostato se riesce,
        ok=False con codice errore standardizzato altrimenti.
    """
```

**Motivazione:** Gli esempi nei naming conventions sono quelli che Copilot
imita più direttamente nella generazione di nuovo codice.

---

### Problema 4 — Logging: nome file root e named loggers

**Attuale:**
```python
_game_logger  = logging.getLogger('game')
_ui_logger    = logging.getLogger('ui')
_error_logger = logging.getLogger('error')
_timer_logger = logging.getLogger('timer')
# root → logs/solitario.log
```

**Impatto:** Il named logger `timer` non esiste in questo progetto. Il file root
`solitario.log` ha un nome errato.

**Soluzione:** Aggiornare con i logger reali di Tombola Stark:
```python
_logger_partita  = logging.getLogger('tombola_stark.partita')   # lifecycle partita, turni, estrazioni
_logger_tui      = logging.getLogger('tombola_stark.tui')       # navigazione TUI, comandi utente
_logger_errori   = logging.getLogger('tombola_stark.errori')    # errori, warnings, eccezioni
# root → logs/tombola_stark.log
```

Routing file di output:
```
tombola_stark.partita  → logs/partita.log
tombola_stark.tui      → logs/tui.log
tombola_stark.errori   → logs/errori.log
root                   → logs/tombola_stark.log
```

**Motivazione:** I named logger sono usati in ogni modulo del progetto. Copilot
deve conoscere i nomi esatti per non inventarne di propri.

---

### Problema 5 — Sezione Accessibilità UI: wxPython vs TUI terminale

**Attuale:** L'intera sezione accessibilità è orientata a wxPython:
```python
class VictoryDialog(wx.Dialog):
    def __init__(self, parent, outcome, profile):
        super().__init__(parent, title="Partita Vinta!")
        self.screen_reader.speak("Hai vinto!")
        btn_rematch = wx.Button(self, wx.ID_YES, "&Rivincita")
```
Con checklist su `SetLabel()`, `SetFocus()`, `wx.ID_CANCEL`, acceleratori wx.

**Impatto:** Copilot potrebbe suggerire di aggiungere import wx o componenti
grafici in un progetto che è esclusivamente a riga di comando.

**Soluzione:** Sostituire l'intera sezione con una checklist TUI da terminale:

```
Checklist accessibilità TUI obbligatoria:
- Ogni riga di output è autonoma e leggibile da NVDA senza contesto visivo
- Ogni riga non supera 120 caratteri (screen reader non tronca)
- Nessun carattere ASCII decorativo (box, linee, tabelle visive)
- Nessun colore ANSI o escape sequence (non interpretabili da NVDA)
- I comandi sono tasto singolo catturato con msvcrt (niente Invio obbligatorio)
- I comandi che richiedono argomento usano input() con prompt descrittivo
- Ogni azione produce almeno una riga di feedback testuale
- In caso di errore il messaggio descrive cosa fare, non solo cosa è andato storto
```

Esempio corretto di output accessibile:
```python
# CORRETTO — riga autonoma, descrittiva, entro 120 caratteri
print("Cartella 1 di 3 — Riga 2 — Numeri: 15, 32, 67 — Segnati: 1 di 3")

# VIETATO — output visivo non leggibile da screen reader
print("┌─────────────────────┐")
print("│  15  │  --  │  67  │")
print("└─────────────────────┘")
```

**Motivazione:** Tombola Stark è progettato per un utente non vedente che usa
NVDA su Windows 11 con terminale a riga di comando. Non esiste e non esisterà
mai una GUI grafica. Mantenere riferimenti wx genera confusione e suggerimenti
di codice inutilizzabili.

---

### Problema 6 — Esempio test pattern

**Attuale:**
```python
# tests/domain/services/test_profile_service.py
from src.domain.services.profile_service import ProfileService

class TestProfileService:
    def test_ensure_guest_profile_creates_if_missing(self, service):
        result = service.ensure_guest_profile()
        assert result is True
        assert service.storage.exists("profile_000")
```

**Impatto:** Copilot impara la struttura dei test da un esempio completamente
estraneo al progetto, con path e classi inesistenti.

**Soluzione:** Sostituire con un esempio reale coerente con il progetto:
```python
# tests/players/test_giocatore_umano.py
import pytest
from bingo_game.players.giocatore_umano import GiocatoreUmano
from tests.helpers import crea_cartella_test

class TestImposta Focus Cartella:
    @pytest.fixture
    def giocatore(self):
        g = GiocatoreUmano(nome="Test")
        g.cartelle = [crea_cartella_test(), crea_cartella_test()]
        return g

    def test_imposta_focus_cartella_valida_ritorna_successo(self, giocatore):
        """Verifica che il focus su cartella valida ritorni EsitoAzione ok=True."""
        # Arrange
        # (fixture già pronta)

        # Act
        esito = giocatore.imposta_focus_cartella(1)

        # Assert
        assert esito.ok is True
        assert esito.evento is not None
        assert giocatore._indice_cartella_focus == 0  # 1-based → 0-based

    def test_imposta_focus_cartella_fuori_range_ritorna_errore(self, giocatore):
        """Verifica che un indice fuori range ritorni ok=False con codice errore."""
        esito = giocatore.imposta_focus_cartella(99)
        assert esito.ok is False
        assert esito.errore == "NUMERO_CARTELLA_FUORI_RANGE"
```

**Motivazione:** Gli esempi di test insegnano a Copilot il pattern Arrange-Act-Assert
specifico del progetto, inclusi i nomi dei codici errore e la struttura di EsitoAzione.

---

### Problema 7 — Critical Warnings: avvisi irrilevanti

**Attuale:**
```
1. Guest Profile Protection: profilo_000 intoccabile
2. Timer Overtime: EndReason.VICTORY vs VICTORY_OVERTIME
3. Draw Count Duality: GameService.draw_count vs ScoringService.stock_draw_count
4. Pile.count() Bug: usa pile.get_card_count()
```

**Impatto:** Tutti e quattro gli avvisi sono specifici del solitario e non hanno
nessuna applicazione in Tombola Stark. Copilot potrebbe cercare di applicarli.

**Soluzione:** Sostituire con gli avvisi critici reali di Tombola Stark:

```
1. NO IMPORT DOMAIN DALLA TUI
   La TUI (tui_partita.py, tui_menu.py) non deve mai importare classi Domain
   direttamente. Tutto il dominio è accessibile solo tramite game_controller.py.
   VIETATO: from bingo_game.players.giocatore_umano import GiocatoreUmano
   CORRETTO: from bingo_game.game_controller import ottieni_giocatore_umano

2. ESITO_AZIONE: CONTROLLA SEMPRE ok PRIMA DI LEGGERE evento
   Ogni metodo di GiocatoreUmano ritorna EsitoAzione. Non accedere mai
   a esito.evento senza aver prima verificato esito.ok is True.
   VIETATO: renderer.render(esito.evento)
   CORRETTO: if esito.ok: renderer.render(esito.evento)

3. FOCUS CARTELLA NON SI AUTO-IMPOSTA NEI COMANDI DI AZIONE
   I metodi che modificano stato (segna_numero_manuale, annuncia_vittoria,
   vai_a_riga_avanzata, vai_a_colonna_avanzata) hanno auto_imposta=False.
   Se il focus cartella è None, ritornano errore. È responsabilità dell'utente
   selezionare prima la cartella con imposta_focus_cartella(n).

4. NESSUN print() NEL CODICE DI PRODUZIONE
   Tutta la produzione di output passa per TerminalRenderer.
   Usare print() direttamente nel codice applicativo viola l'architettura
   e produce output non tracciabile e non localizzabile.
   VIETATO: print("Numero segnato!")
   CORRETTO: _renderer.render(esito.evento)

5. NESSUNA STRINGA DI TESTO NEL DOMAIN LAYER
   I metodi di GiocatoreUmano, Partita, Tabellone e Cartella non producono
   mai stringhe pronte per l'utente. Producono solo EsitoAzione con eventi
   dati. Le stringhe esistono solo in ui/locales/it.py e vengono assemblate
   dal TerminalRenderer.
```

**Motivazione:** Gli avvisi critici sono la sezione più letta da Copilot quando
incontra pattern dubbi. Devono rispecchiare esattamente i vincoli di questo progetto.

---

### Problema 8 — Sezione TTS Feedback

**Attuale:** La sezione descrive un metodo `tts_spoken()` legato a `screen_reader.speak()`
in un contesto wx, con riferimento a dialogs grafici.

**Impatto:** Il meccanismo TTS descritto non esiste in Tombola Stark. L'output
verso NVDA avviene tramite il normale output su stdout del terminale Windows,
che NVDA legge automaticamente.

**Soluzione:** Sostituire la sezione con una nota sul funzionamento dell'accessibilità
in questo progetto:

```
Output verso NVDA in Tombola Stark

NVDA su Windows 11 legge automaticamente l'output standard del terminale (cmd.exe
o Windows Terminal) riga per riga, non appena viene stampato con print().
Non è necessario nessun metodo speak() esplicito.

Per garantire che NVDA legga correttamente ogni messaggio:
- Ogni messaggio deve essere su una riga separata (no \r, no escape ANSI)
- Messaggi lunghi vanno spezzati in righe tematiche autonome
- I messaggi di errore devono essere self-contained: NVDA non ha contesto visivo
- Non usare caratteri speciali, simboli Unicode decorativi o emoji

Esempio di output corretto per NVDA:
    print("Cartella 1 selezionata.")
    print("Numeri mancanti per ambo: 2.")
    print("Numeri mancanti per terno: 3.")

Esempio di output non accessibile:
    print(f"🎯 Cartella 1 | Ambo: 2 | Terno: 3")
```

**Motivazione:** Comprendere come funziona realmente l'accessibilità in questo
progetto evita che Copilot suggerisca dipendenze TTS esterne non necessarie.

---

### Problema 9 — Riferimenti sparsi al dominio del solitario

**Attuale:** In vari punti del file compaiono termini del solitario:
- "carte", "pile", "mazzo", "pescata", "stock"
- "VictoryDialog", "GameEngine", "ProfileService"
- "EndReason.VICTORY", "draw_count"
- "pile.count()", "pile.get_card_count()"
- path come `src/infrastructure/ui/dialogs/`

**Impatto:** Copilot riceve segnali contrastanti sul dominio del progetto
ogni volta che elabora le istruzioni.

**Soluzione:** Sostituire tutti questi termini con il vocabolario di Tombola Stark:
- "cartella", "numero", "tabellone", "estrazione", "turno", "reclamo"
- "GiocatoreUmano", "TerminalRenderer", "GestioneFocusMixin", "EsitoAzione"
- "Tipo_Vittoria.AMBO", "Tipo_Vittoria.TOMBOLA"
- "tabellone.is_numero_estratto(n)", "cartella.get_numeri_cartella()"
- path come `bingo_game/ui/tui/`

**Motivazione:** La coerenza lessicale del documento è fondamentale per il
funzionamento delle istruzioni di Copilot. Ogni termine estraneo introduce rumore.

---

## Lista File Coinvolti

| File | Operazione | Note |
|------|------------|------|
| `.github/copilot-instructions.md` | MODIFY | File principale da adattare |
| `documentations/2 - project/PLAN_adattamento_copilot_instructions_v0.10.0.md` | CREATE | Questo file |

---

## Fasi di Implementazione

### Fase 1 — Titolo e identità
Modificare la prima riga del file da "Solitario Classico Accessibile" a "Tombola Stark".

### Fase 2 — Struttura Clean Architecture
Sostituire tutti i path `src/domain/`, `src/application/`, `src/infrastructure/`,
`src/presentation/` con i path reali di `bingo_game/` e relativi sottomoduli.
Rimuovere ogni riferimento a wxPython, `wx.*`, `VictoryDialog`.

### Fase 3 — Naming conventions ed esempi
Sostituire gli esempi di firma e nome con classi e metodi reali del progetto.

### Fase 4 — Logging
Aggiornare i named logger e il nome del file root da `solitario.log` a `tombola_stark.log`.

### Fase 5 — Accessibilità UI
Rimuovere l'intera checklist wx e l'esempio VictoryDialog.
Inserire checklist TUI terminale e regole output per NVDA.

### Fase 6 — Test pattern
Sostituire l'esempio ProfileService con un esempio su GiocatoreUmano/EsitoAzione.

### Fase 7 — Critical Warnings
Rimuovere i 4 avvisi del solitario.
Inserire i 5 avvisi critici di Tombola Stark.

### Fase 8 — Sezione TTS
Sostituire la descrizione del metodo tts_spoken() con la nota sul funzionamento
di NVDA tramite stdout del terminale.

### Fase 9 — Pulizia terminologia sparsa
Scansione completa del file per sostituire ogni termine residuo del solitario
con il vocabolario corretto di Tombola Stark.

---

## Criteri di Completamento

- Il file non contiene più nessun riferimento a "solitario", "carte", "pile",
  "mazzo", "pescata", "stock", "wx", "wxPython", "ProfileService", "GameEngine",
  "draw_count", "profile_000", "EndReason", "pile.count()".
- Tutti i path di import negli esempi usano `bingo_game/` come radice.
- La sezione accessibilità non contiene codice wx.
- I Critical Warnings descrivono vincoli reali di Tombola Stark.
- Il file può essere letto da un membro esterno del progetto e dare un quadro
  corretto dell'architettura, dei pattern e dei vincoli del progetto.
