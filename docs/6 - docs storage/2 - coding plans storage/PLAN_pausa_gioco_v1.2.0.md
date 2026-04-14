---
type: plan
feature: pausa_gioco
status: READY
agent: Agent-Plan
versione: 1.2.0
design_ref: docs/2 - projects/DESIGN_pausa_gioco.md
data_creazione: 2026-04-11
---

# PLAN: Pausa del gioco (v1.2.0)

## 1. Executive Summary

- **Tipo**: Feature — nuova funzionalita
- **Priorita**: Media — migliora UX per interruzioni impreviste
- **Branch**: main (sviluppo su main, commit atomici)
- **Versione target**: 1.2.0 (minor bump: nuova feature)
- **Design di riferimento**: `docs/2 - projects/DESIGN_pausa_gioco.md`
- **Scope**: Layer UI esclusivamente. Zero modifiche al dominio.

---

## 2. Problema e Obiettivo

### Problema

Durante una partita attiva non esiste meccanismo per sospendere il gioco.
Se il giocatore deve allontanarsi, i timer scorrono e il turno si risolve
automaticamente per timeout. Alla ripresa il giocatore e fuori sincronia.

### Obiettivo

Aggiungere un tasto rapido (`Ctrl+P`) e un pulsante visibile ("Pausa")
che congelino tutti i timer e il ciclo automatico. Alla ripresa i timer
ripartono dal tempo residuo e NVDA annuncia lo stato completo.

---

## 3. File coinvolti

| File | Operazione | Dettaglio |
|------|------------|-----------|
| `bingo_game/ui/finestra_gioco.py` | MODIFY | Stato "in_pausa", attributi, metodi, binding, guardie, pulsante |
| `bingo_game/ui/renderers/base_renderer.py` | MODIFY | Metodo astratto `annuncia_pausa` |
| `bingo_game/ui/renderers/renderer_wx.py` | MODIFY | Implementazione `annuncia_pausa` |
| `bingo_game/ui/locales/it.py` | MODIFY | Testi pausa/ripresa |
| `bingo_game/events/codici_eventi.py` | MODIFY | Costanti PAUSA_ATTIVATA, PAUSA_DISATTIVATA |
| `tests/unit/test_pausa_gioco.py` | CREATE | Suite test pausa/ripresa |

---

## 4. Fasi implementative

### Fase 1 — Infrastruttura eventi e locales

**File**: `bingo_game/events/codici_eventi.py` (MODIFY)

Aggiungere due nuove costanti al modulo:
```python
PAUSA_ATTIVATA:   Final = "PAUSA_ATTIVATA"
PAUSA_DISATTIVATA: Final = "PAUSA_DISATTIVATA"
```
Aggiornare il tipo Literal `Codici_Eventi` con i due nuovi valori.

**File**: `bingo_game/ui/locales/it.py` (MODIFY)

Aggiungere al dizionario dei messaggi (nella sezione eventi o sistema):
- `"PAUSA_ATTIVATA"`: `"Gioco in pausa."`
- `"PAUSA_DISATTIVATA_ESTRAZIONE"`: `"Gioco ripreso. Fase: Attesa nuova estrazione."`
- `"PAUSA_DISATTIVATA_RECLAMI"`: `"Gioco ripreso. Fase: Finestra reclami aperta. Tempo rimanente: {s} secondi."`
- `"PAUSA_DISATTIVATA_PAUSA_TURNO"`: `"Gioco ripreso. Fase: Pausa breve tra turni. Tempo rimanente: {s} secondi."`

**File**: `bingo_game/ui/renderers/base_renderer.py` (MODIFY)

Aggiungere il metodo astratto:
```python
@abstractmethod
def annuncia_pausa(self, testo: str) -> None:
    """Vocalizza lo stato di pausa o ripresa del gioco."""
    ...
```

**File**: `bingo_game/ui/renderers/renderer_wx.py` (MODIFY)

Implementare il metodo concreto:
```python
def annuncia_pausa(self, testo: str) -> None:
    self._wx_aggiorna_output(testo)
    self._ao2_vocalizza(testo)
```

Precondizione: nessuna dipendenza da altre fasi. Committable da sola.

---

### Fase 2 — Attributi e logica pausa in FinestraGioco

**File**: `bingo_game/ui/finestra_gioco.py` (MODIFY)

#### 2a. Aggiungere import `time` in testa al modulo

```python
import time
```

#### 2b. Aggiungere attributi nel costruttore `__init__` (dopo gli attributi timer esistenti)

```python
# --- Stato pausa ---
self._in_pausa: bool = False
self._fase_pre_pausa: str = ""
self._ms_residui_azione: int = 0
self._ms_residui_pausa: int = 0
self._avvio_pausa_turno_mono: float = 0.0
```

#### 2c. Modificare `_avvia_pausa_turno` per salvare il timestamp di avvio

Aggiungere all'inizio del metodo (prima di creare il timer):
```python
self._avvio_pausa_turno_mono = time.monotonic()
```

#### 2d. Aggiungere metodo `_toggle_pausa`

```python
def _toggle_pausa(self) -> None:
    if self._in_pausa:
        self._riprendi_gioco()
    else:
        self._metti_in_pausa()
```

#### 2e. Aggiungere metodo `_metti_in_pausa`

Precondizioni: partita attiva e almeno un numero estratto.

```python
def _metti_in_pausa(self) -> None:
    if self._comandi_sistema.is_terminata(self._partita):
        return
    if self._partita.tabellone.get_conteggio_estratti() == 0:
        return  # Pausa disponibile solo durante partita attiva
    self._fase_pre_pausa = self._fase_turno_ui
    # Calcola residuo timer azione (se attivo)
    self._ms_residui_azione = max(
        0, self._durata_finestra_corrente_ms - self._ms_trascorsi_azione
    )
    # Calcola residuo timer pausa turno (se attivo)
    if self._timer_pausa is not None and self._avvio_pausa_turno_mono > 0:
        elapsed = int((time.monotonic() - self._avvio_pausa_turno_mono) * 1000)
        self._ms_residui_pausa = max(0, self._durata_pausa_ms - elapsed)
    else:
        self._ms_residui_pausa = 0
    self._ferma_tutti_i_timer()
    self._in_pausa = True
    self._fase_turno_ui = "in_pausa"
    self._aggiorna_stato_pulsante()
    self._renderer.annuncia_pausa("Gioco in pausa.")
```

#### 2f. Aggiungere metodo `_riprendi_gioco`

```python
def _riprendi_gioco(self) -> None:
    self._in_pausa = False
    self._fase_turno_ui = self._fase_pre_pausa
    self._aggiorna_stato_pulsante()
    # Costruisce testo di ripresa con stato completo
    _mappa_fase = {
        "attesa_estrazione": "Attesa nuova estrazione",
        "attesa_reclami": "Finestra reclami aperta",
        "pausa_turno": "Pausa breve tra turni",
    }
    desc_fase = _mappa_fase.get(self._fase_pre_pausa, self._fase_pre_pausa)
    if self._fase_pre_pausa == "attesa_reclami" and self._ms_residui_azione > 0:
        secondi = max(1, self._ms_residui_azione // 1000)
        testo = f"Gioco ripreso. Fase: {desc_fase}. Tempo rimanente: {secondi} secondi."
        self._avvia_timer_azione(self._ms_residui_azione)
    elif self._fase_pre_pausa == "pausa_turno" and self._ms_residui_pausa > 0:
        secondi = max(1, self._ms_residui_pausa // 1000)
        testo = f"Gioco ripreso. Fase: {desc_fase}. Tempo rimanente: {secondi} secondi."
        self._avvia_pausa_turno(self._ms_residui_pausa)
    else:
        testo = f"Gioco ripreso. Fase: {desc_fase}."
    self._renderer.annuncia_pausa(testo)
```

#### 2g. Guard in `_on_pulsante_principale`

Aggiungere all'inizio del metodo, dopo il check `is_terminata`:
```python
if self._in_pausa:
    return
```

Precondizione: dipende da Fase 1 (annuncia_pausa). Committable dopo Fase 1.

---

### Fase 3 — Pulsante "Pausa" e binding Ctrl+P in FinestraGioco

**File**: `bingo_game/ui/finestra_gioco.py` (MODIFY)

#### 3a. Aggiungere pulsante `_btn_pausa` in `_build_ui`

Inserire dopo la creazione di `_btn_principale`:
```python
self._btn_pausa = wx.Button(panel, label="Metti in pausa")
self._btn_pausa.Disable()  # Disabilitato fino al primo turno
sizer.Add(self._btn_pausa, 0, wx.ALL | wx.EXPAND, 5)
self.Bind(wx.EVT_BUTTON, self._on_pausa, self._btn_pausa)
```

#### 3b. Aggiungere handler `_on_pausa`

```python
def _on_pausa(self, event: object) -> None:
    self._toggle_pausa()
```

#### 3c. Aggiungere binding `Ctrl+P` in `_on_char_hook`

Aggiungere nella sezione "Categoria B" subito dopo Ctrl+Enter:
```python
# Ctrl+P — pausa/ripresa
if ctrl and key == ord("P"):
    self._toggle_pausa()
    return
```

#### 3d. Aggiornare `aggiorna_stato_pulsante` per gestire "in_pausa"

Nel metodo pubblico `aggiorna_stato_pulsante`:
```python
if fase == "in_pausa":
    label = "Gioco in pausa"
    self._btn_principale.SetLabel(label)
    self._btn_principale.Disable()
    if hasattr(self, "_btn_pausa"):
        self._btn_pausa.SetLabel("Riprendi")
        self._btn_pausa.Enable()
    self._renderer.annuncia_fase_turno(label)
    return
```

Per tutti gli altri stati, abilitare/disabilitare `_btn_pausa` in base
al conteggio estratti:
```python
# Abilita btn_pausa solo se la partita e' attiva
if hasattr(self, "_btn_pausa"):
    partita_attiva = (
        self._partita.tabellone.get_conteggio_estratti() > 0
        and not self._comandi_sistema.is_terminata(self._partita)
        and fase != "pausa_turno"
    )
    self._btn_pausa.SetLabel("Metti in pausa")
    if partita_attiva:
        self._btn_pausa.Enable()
    else:
        self._btn_pausa.Disable()
```

Precondizione: dipende da Fase 2. Committable dopo Fase 2.

---

### Fase 4 — Test unitari

**File**: `tests/unit/test_pausa_gioco.py` (CREATE)

Creare una suite unittest con le seguenti classi / casi:

#### TestMettereInPausa (stub FinestraGioco)
- `test_metti_in_pausa_salva_fase_pre_pausa`: verifica che
  `_fase_pre_pausa` sia impostata correttamente.
- `test_metti_in_pausa_imposta_stato_in_pausa`: verifica che
  `_fase_turno_ui` diventi `"in_pausa"`.
- `test_metti_in_pausa_ferma_timer`: verifica che dopo la pausa
  `_timer_azione` e `_timer_pausa` siano `None`.
- `test_metti_in_pausa_calcola_residuo_azione`: con
  `_ms_trascorsi_azione = 10000` e `_durata_finestra_corrente_ms = 60000`,
  il residuo deve essere 50000.
- `test_metti_in_pausa_non_disponibile_prima_primo_turno`: se
  `get_conteggio_estratti() == 0`, `_fase_turno_ui` non cambia.
- `test_metti_in_pausa_non_disponibile_partita_terminata`: se
  `is_terminata() == True`, non cambia stato.

#### TestRiprendereGioco
- `test_riprendi_ripristina_fase_pre_pausa`: `_fase_turno_ui`
  torna al valore salvato in `_fase_pre_pausa`.
- `test_riprendi_da_attesa_reclami_riavvia_timer_azione`: se
  `_fase_pre_pausa == "attesa_reclami"` e residuo > 0, il timer
  azione viene riavviato.
- `test_riprendi_da_pausa_turno_riavvia_timer_pausa`: se
  `_fase_pre_pausa == "pausa_turno"` e residuo > 0, il timer pausa
  viene riavviato.
- `test_riprendi_da_attesa_estrazione_nessun_timer`: se
  `_fase_pre_pausa == "attesa_estrazione"`, nessun timer viene avviato.
- `test_toggle_due_volte_torna_stato_originale`: due pressioni di
  Ctrl+P riportano allo stato di partenza.

#### TestRendererAnnuncio
- `test_annuncia_pausa_chiamato_su_metti_in_pausa`: il renderer
  riceve la chiamata con testo "Gioco in pausa."
- `test_annuncia_pausa_chiamato_su_riprendi`: il renderer riceve
  la chiamata con testo che inizia con "Gioco ripreso."
- `test_annuncia_ripresa_include_secondi_residui`: il testo di
  ripresa include il numero di secondi rimanenti quando un timer
  era attivo.

Precondizione: dipende da Fasi 2 e 3. I test usano stub di FinestraGioco
senza dipendenza wx (headless-safe).

---

## 5. Test Plan

### Unit test (`tests/unit/test_pausa_gioco.py`)

- Toggle pausa: attivazione e disattivazione
- Calcolo tempo residuo timer azione
- Calcolo tempo residuo timer pausa turno
- Guard precondizioni (partita non avviata, partita terminata)
- Comportamento renderer (mock)

### Verifica accessibilita (manuale, NVDA)

- Ctrl+P durante "attesa_estrazione": NVDA vocalizza "Gioco in pausa."
- Ctrl+P durante "attesa_reclami": pausa attiva, timer azione congelato
- Ctrl+P di ripresa: NVDA vocalizza stato completo con secondi residui
- Tab raggiunge il pulsante "Metti in pausa" / "Riprendi"
- Il pulsante e DISABILITATO prima del primo turno
- Nessuna progressione automatica del gioco durante la pausa

### Pre-commit checklist

```bash
python -m py_compile bingo_game/ui/finestra_gioco.py
python -m py_compile bingo_game/ui/renderers/base_renderer.py
python -m py_compile bingo_game/ui/renderers/renderer_wx.py
python -m py_compile bingo_game/events/codici_eventi.py
pytest tests/unit/test_pausa_gioco.py -v
pytest -m "not gui" -q
```
