---
feature: fix_tab_navigation_finestra_gioco
agent: Agent-Plan
status: READY
version: v0.12.1
design_ref: docs/2 - projects/DESIGN_fix_tab_navigation_finestra_gioco.md
date: 2026-04-12
---

## Metadati

tipo: coding_plan
titolo: Fix navigazione Tab finestra di gioco — v0.12.1
data_creazione: 2026-04-12
agente: Agent-Plan
stato: READY

---

## 1. Executive Summary

- Tipo: bugfix accessibilita
- Priorita: alta — blocca navigazione da tastiera su controlli critici
- Branch: main
- Versione target: v0.12.1

---

## 2. Problema e Obiettivo

Il tasto Tab nella finestra di gioco non raggiunge i pulsanti:
- Cartella precedente / Cartella successiva (frecce)
- Selezione diretta cartella (1..N, creati dinamicamente)
- Dichiarazione vittorie (Ambo, Terno, Quaterna, Cinquina, Tombola)

Causa principale: PannelloGriglia usa wx.WANTS_CHARS che intercetta Tab
senza chiamare Navigate() per cedere il focus.

Causa secondaria: i pulsanti selezione cartella vengono creati tardivamente
(al primo turno) e finiscono in fondo al ciclo Tab invece che dopo le frecce.

Obiettivo: correggere entrambe le cause in 2 fasi atomiche committabili.

---

## 3. File coinvolti

| File | Operazione | Note |
|------|-----------|------|
| bingo_game/ui/finestra_gioco.py | MODIFY | Fix 1 e Fix 2 |

---

## 4. Fasi implementative

### Fase 1 — Fix navigate Tab in PannelloGriglia

File: bingo_game/ui/finestra_gioco.py
Metodo: PannelloGriglia._on_key_down

Inserire prima del ramo finale event.Skip() (circa riga 325):

```python
# Tab / Shift+Tab — naviga tra controlli della finestra
if key == wx.WXK_TAB:
    flags = wx.NavigationKeyEvent.IsForward
    if shift:
        flags = wx.NavigationKeyEvent.IsBackward
    self.Navigate(flags)
    return
```

Commit atomico: "fix(ui): Tab in PannelloGriglia ora cede il focus con Navigate()"

### Fase 2 — Fix ordine Tab pulsanti selezione cartella

File: bingo_game/ui/finestra_gioco.py
Metodo: FinestraGioco._crea_pulsanti_selezione_cartella

Aggiungere dopo il ciclo di creazione pulsanti e prima di self._panel.Layout():

```python
# Corregge ordine Tab: selezione cartella dopo freccia destra
if self._pulsanti_selezione:
    self._pulsanti_selezione[0].MoveAfterInTabOrder(self._btn_freccia_dx)
    for i in range(1, len(self._pulsanti_selezione)):
        self._pulsanti_selezione[i].MoveAfterInTabOrder(
            self._pulsanti_selezione[i - 1]
        )
```

Commit atomico: "fix(ui): ordine Tab pulsanti selezione cartella corretto con MoveAfterInTabOrder"

---

## 5. Test Plan

Nessun test unitario aggiuntivo richiesto: i widget wxPython non sono
testabili in CI headless (flag @pytest.mark.gui).

Verifica manuale (NVDA + Windows 11):
1. Avviare la partita
2. Premere Tab dalla griglia: il focus deve spostarsi su Cartella precedente
3. Con Tab continuare: Cartella successiva, poi pulsanti 1..N anche in ordine logico
4. Con Tab continuare: pulsanti premi (solo in fase attesa_reclami)
5. Con Shift+Tab verificare la direzione inversa

Test automatizzati da eseguire:
- pytest tests/ -m "not gui" --tb=short

---

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso
