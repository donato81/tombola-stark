"""
Test unitari per la feature pausa del gioco (v1.2.0).

Esercita i metodi reali _metti_in_pausa, _riprendi_gioco e _toggle_pausa
di FinestraGioco tramite un'istanza bare (FinestraGioco.__new__) con
dipendenze wx surrogate (MagicMock), senza duplicare la logica nel test.

I test sullo stub BaseRenderer (TestRendererAnnuncio) restano indipendenti
da wx.

Riferimento: docs/3 - coding plans/PLAN_pausa_gioco_v1.2.0.md — Fase 4
"""
from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import MagicMock

from bingo_game.ui.renderers.base_renderer import BaseRenderer, StatoConfigurazione
from bingo_game.events.eventi import EsitoAzione

try:
    from bingo_game.ui.finestra_gioco import FinestraGioco
except Exception:  # pragma: no cover - ambiente senza wx
    FinestraGioco = None  # type: ignore[assignment, misc]


# ---------------------------------------------------------------------------
# Stub BaseRenderer
# ---------------------------------------------------------------------------

class _RendererStub(BaseRenderer):
    """Implementazione minimale di BaseRenderer per i test della pausa."""

    def __init__(self) -> None:
        self.chiamate: list[tuple[str, Any]] = []

    def render_esito(self, esito: EsitoAzione) -> None:
        self.chiamate.append(("render_esito", esito))

    def mostra_schermata_configurazione(self, stato: StatoConfigurazione) -> None:
        self.chiamate.append(("mostra_schermata_configurazione", stato))

    def mostra_report_finale(self, dati_partita: dict) -> None:
        self.chiamate.append(("mostra_report_finale", dati_partita))

    def mostra_messaggio_sistema(self, testo: str) -> None:
        self.chiamate.append(("mostra_messaggio_sistema", testo))

    def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
        self.chiamate.append(("annuncia_numero_estratto", (numero, numero_turno)))

    def annuncia_premi_turno(self, premi: list) -> None:
        self.chiamate.append(("annuncia_premi_turno", premi))

    def annuncia_fase_turno(self, testo_fase: str) -> None:
        self.chiamate.append(("annuncia_fase_turno", testo_fase))

    def annuncia_avviso_timeout(self, secondi_rimanenti: int, livello: int = 80) -> None:
        self.chiamate.append(("annuncia_avviso_timeout", (secondi_rimanenti, livello)))

    def annuncia_avvio_pausa_turno(self, secondi: int) -> None:
        self.chiamate.append(("annuncia_avvio_pausa_turno", secondi))

    def annuncia_tutti_pronti(self) -> None:
        self.chiamate.append(("annuncia_tutti_pronti", None))

    def annuncia_pausa(self, testo: str) -> None:
        self.chiamate.append(("annuncia_pausa", testo))


# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------

def _crea_finestra(
    renderer: _RendererStub,
    estratti: int = 1,
    terminata: bool = False,
) -> "FinestraGioco":
    """
    Crea un'istanza bare di FinestraGioco senza chiamare __init__ (evita
    wx.Frame.__init__).  Imposta gli attributi necessari ai metodi
    _metti_in_pausa, _riprendi_gioco e _toggle_pausa; mocca i metodi che
    richiedono infrastruttura wx: _aggiorna_stato_pulsante,
    _avvia_timer_azione, _avvia_pausa_turno.
    _ferma_tutti_i_timer NON viene moccato perché è logica pura che
    opera su oggetti Mock/None.
    """
    fg: FinestraGioco = FinestraGioco.__new__(FinestraGioco)  # type: ignore[misc]
    fg._renderer = renderer

    # Stato turno UI
    fg._fase_turno_ui = "attesa_estrazione"
    fg._in_pausa = False
    fg._fase_pre_pausa = ""
    fg._ms_residui_azione = 0
    fg._ms_residui_pausa = 0
    fg._avvio_pausa_turno_mono = 0.0

    # Timer (None = non attivi)
    fg._timer_azione = None
    fg._timer_pausa = None
    fg._durata_finestra_corrente_ms = 60000
    fg._ms_trascorsi_azione = 0
    fg._durata_pausa_ms = 5000

    # Dipendenze dominio via Mock
    fg._partita = MagicMock()
    fg._partita.tabellone.get_conteggio_estratti.return_value = estratti
    fg._comandi_sistema = MagicMock()
    fg._comandi_sistema.is_terminata.return_value = terminata

    # Metodi che richiedono infrastruttura wx: sostituiti con Mock
    fg._aggiorna_stato_pulsante = MagicMock()
    fg._avvia_timer_azione = MagicMock()
    fg._avvia_pausa_turno = MagicMock()

    return fg


# ---------------------------------------------------------------------------
# TestMettereInPausa
# ---------------------------------------------------------------------------

@unittest.skipIf(FinestraGioco is None, "FinestraGioco/wxPython non disponibile nel test environment")
class TestMettereInPausa(unittest.TestCase):
    """Verifica il comportamento del metodo reale _metti_in_pausa."""

    def _make_stub(self, estratti: int = 1, terminata: bool = False) -> "FinestraGioco":
        renderer = _RendererStub()
        fg = _crea_finestra(renderer, estratti=estratti, terminata=terminata)
        fg._fase_turno_ui = "attesa_reclami"
        return fg

    def test_metti_in_pausa_salva_fase_pre_pausa(self) -> None:
        fg = self._make_stub()
        fg._fase_turno_ui = "attesa_reclami"
        fg._metti_in_pausa()
        self.assertEqual(fg._fase_pre_pausa, "attesa_reclami")

    def test_metti_in_pausa_imposta_stato_in_pausa(self) -> None:
        fg = self._make_stub()
        fg._metti_in_pausa()
        self.assertEqual(fg._fase_turno_ui, "in_pausa")

    def test_metti_in_pausa_ferma_timer(self) -> None:
        fg = self._make_stub()
        mock_timer_azione = MagicMock()
        mock_timer_pausa = MagicMock()
        fg._timer_azione = mock_timer_azione
        fg._timer_pausa = mock_timer_pausa
        fg._metti_in_pausa()
        self.assertIsNone(fg._timer_azione)
        self.assertIsNone(fg._timer_pausa)
        mock_timer_azione.Stop.assert_called_once()
        mock_timer_pausa.Stop.assert_called_once()

    def test_metti_in_pausa_imposta_flag_in_pausa(self) -> None:
        fg = self._make_stub()
        fg._metti_in_pausa()
        self.assertTrue(fg._in_pausa)

    def test_metti_in_pausa_calcola_residuo_azione(self) -> None:
        fg = self._make_stub()
        fg._ms_trascorsi_azione = 10000
        fg._durata_finestra_corrente_ms = 60000
        fg._metti_in_pausa()
        self.assertEqual(fg._ms_residui_azione, 50000)

    def test_metti_in_pausa_non_disponibile_prima_primo_turno(self) -> None:
        fg = self._make_stub(estratti=0)
        fg._fase_turno_ui = "attesa_estrazione"
        fg._metti_in_pausa()
        self.assertNotEqual(fg._fase_turno_ui, "in_pausa")
        self.assertFalse(fg._in_pausa)

    def test_metti_in_pausa_non_disponibile_partita_terminata(self) -> None:
        fg = self._make_stub(terminata=True)
        fg._metti_in_pausa()
        self.assertFalse(fg._in_pausa)

    def test_metti_in_pausa_annuncia_al_renderer(self) -> None:
        renderer = _RendererStub()
        fg = _crea_finestra(renderer)
        fg._fase_turno_ui = "attesa_reclami"
        fg._metti_in_pausa()
        nomi = [c[0] for c in renderer.chiamate]
        self.assertIn("annuncia_pausa", nomi)
        idx = nomi.index("annuncia_pausa")
        self.assertEqual(renderer.chiamate[idx][1], "Gioco in pausa.")


# ---------------------------------------------------------------------------
# TestRiprendereGioco
# ---------------------------------------------------------------------------

@unittest.skipIf(FinestraGioco is None, "FinestraGioco/wxPython non disponibile nel test environment")
class TestRiprendereGioco(unittest.TestCase):
    """Verifica il comportamento del metodo reale _riprendi_gioco."""

    def _make_in_pausa(
        self,
        fase_pre: str = "attesa_estrazione",
        residuo_azione: int = 0,
        residuo_pausa: int = 0,
    ) -> "FinestraGioco":
        renderer = _RendererStub()
        fg = _crea_finestra(renderer)
        fg._in_pausa = True
        fg._fase_turno_ui = "in_pausa"
        fg._fase_pre_pausa = fase_pre
        fg._ms_residui_azione = residuo_azione
        fg._ms_residui_pausa = residuo_pausa
        return fg

    def test_riprendi_ripristina_fase_pre_pausa(self) -> None:
        fg = self._make_in_pausa(fase_pre="attesa_reclami")
        fg._riprendi_gioco()
        self.assertEqual(fg._fase_turno_ui, "attesa_reclami")

    def test_riprendi_disattiva_flag_in_pausa(self) -> None:
        fg = self._make_in_pausa()
        fg._riprendi_gioco()
        self.assertFalse(fg._in_pausa)

    def test_riprendi_da_attesa_reclami_riavvia_timer_azione(self) -> None:
        fg = self._make_in_pausa(fase_pre="attesa_reclami", residuo_azione=30000)
        fg._riprendi_gioco()
        fg._avvia_timer_azione.assert_called_once_with(30000)

    def test_riprendi_da_pausa_turno_riavvia_timer_pausa(self) -> None:
        fg = self._make_in_pausa(fase_pre="pausa_turno", residuo_pausa=3000)
        fg._riprendi_gioco()
        fg._avvia_pausa_turno.assert_called_once_with(3000)

    def test_riprendi_da_attesa_estrazione_nessun_timer(self) -> None:
        fg = self._make_in_pausa(fase_pre="attesa_estrazione")
        fg._riprendi_gioco()
        fg._avvia_timer_azione.assert_not_called()
        fg._avvia_pausa_turno.assert_not_called()

    def test_riprendi_annuncia_stato_completo_con_tempo(self) -> None:
        renderer = _RendererStub()
        fg = _crea_finestra(renderer)
        fg._in_pausa = True
        fg._fase_turno_ui = "in_pausa"
        fg._fase_pre_pausa = "attesa_reclami"
        fg._ms_residui_azione = 30000
        fg._riprendi_gioco()
        nomi = [c[0] for c in renderer.chiamate]
        self.assertIn("annuncia_pausa", nomi)
        idx = nomi.index("annuncia_pausa")
        testo = renderer.chiamate[idx][1]
        self.assertIn("30 secondi", testo)

    def test_riprendi_annuncia_stato_senza_tempo_se_estrazione(self) -> None:
        renderer = _RendererStub()
        fg = _crea_finestra(renderer)
        fg._in_pausa = True
        fg._fase_turno_ui = "in_pausa"
        fg._fase_pre_pausa = "attesa_estrazione"
        fg._riprendi_gioco()
        nomi = [c[0] for c in renderer.chiamate]
        self.assertIn("annuncia_pausa", nomi)
        idx = nomi.index("annuncia_pausa")
        testo = renderer.chiamate[idx][1]
        self.assertIn("Attesa nuova estrazione", testo)
        self.assertNotIn("secondi", testo)


# ---------------------------------------------------------------------------
# TestRendererAnnuncio
# ---------------------------------------------------------------------------

class TestRendererAnnuncio(unittest.TestCase):
    """Verifica che annuncia_pausa sia un metodo concreto nel renderer stub."""

    def test_annuncia_pausa_viene_registrato(self) -> None:
        renderer = _RendererStub()
        renderer.annuncia_pausa("Gioco in pausa.")
        nomi = [c[0] for c in renderer.chiamate]
        self.assertIn("annuncia_pausa", nomi)

    def test_annuncia_pausa_testo_passato_correttamente(self) -> None:
        renderer = _RendererStub()
        renderer.annuncia_pausa("Gioco ripreso. Fase: Attesa nuova estrazione.")
        idx = [c[0] for c in renderer.chiamate].index("annuncia_pausa")
        self.assertEqual(
            renderer.chiamate[idx][1],
            "Gioco ripreso. Fase: Attesa nuova estrazione.",
        )

    @unittest.skipIf(FinestraGioco is None, "FinestraGioco/wxPython non disponibile nel test environment")
    def test_toggle_pausa_attiva_poi_riprende(self) -> None:
        renderer = _RendererStub()
        fg = _crea_finestra(renderer)
        fg._fase_turno_ui = "attesa_reclami"
        # Prima chiamata: mette in pausa
        fg._toggle_pausa()
        self.assertTrue(fg._in_pausa)
        # Seconda chiamata: riprende
        fg._toggle_pausa()
        self.assertFalse(fg._in_pausa)
        self.assertEqual(fg._fase_turno_ui, "attesa_reclami")


if __name__ == "__main__":
    unittest.main()
