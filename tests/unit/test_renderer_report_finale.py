"""
Test unitari per TerminalRenderer — vocalizzazione gerarchica (Fase 4/5 v0.9.0)

Verifica i contratti di output dei metodi renderer critici per il Game Loop:
1.  _render_evento_riepilogo_tabellone → esattamente 3 righe.
2.  Tutte le righe di _render_evento_riepilogo_tabellone ≤ 120 caratteri.
3.  _render_evento_segnazione_numero esito 'segnato' → 1 riga con il numero.
4.  _render_evento_segnazione_numero esito 'gia_segnato' → 1 riga.
5.  _render_evento_segnazione_numero esito 'non_presente' → 1 riga.
6.  _render_evento_segnazione_numero esito 'non_estratto' → 1 riga.
7.  _render_evento_fine_turno senza reclamo → 1 riga.
8.  _render_evento_riepilogo_cartella_corrente → esattamente 2 righe.
"""
from __future__ import annotations

import unittest


class TestRendererReportFinale(unittest.TestCase):
    """Test unittest per il renderer del report finale."""

    def setUp(self) -> None:
        from bingo_game.events.eventi_output_ui_umani import (
            EventoRiepilogoCartellaCorrente,
            EventoRiepilogoTabellone,
            EventoSegnazioneNumero,
        )
        from bingo_game.events.eventi_partita import EventoFineTurno
        from bingo_game.ui.renderers.renderer_terminal import TerminalRenderer

        self.renderer = TerminalRenderer()
        self.evento_riepilogo_tabellone = EventoRiepilogoTabellone(
            id_giocatore=1,
            nome_giocatore="TestPlayer",
            totale_numeri=90,
            totale_estratti=10,
            totale_mancanti=80,
            percentuale_estrazione=11.1,
            ultimi_estratti=(5, 23, 42),
            ultimi_visualizzati=3,
            ultimo_estratto=42,
        )
        self.evento_segnazione_segnato = EventoSegnazioneNumero(
            id_giocatore=1,
            nome_giocatore="TestPlayer",
            esito="segnato",
            numero=42,
            indice_cartella=0,
            numero_cartella=1,
            totale_cartelle=1,
            indice_riga=1,
            indice_colonna=2,
            numeri_segnati=5,
            totale_numeri=15,
            mancanti=10,
            percentuale=33.3,
        )
        self.evento_segnazione_gia_segnato = EventoSegnazioneNumero(
            id_giocatore=1,
            nome_giocatore="TestPlayer",
            esito="gia_segnato",
            numero=42,
            indice_cartella=0,
            numero_cartella=1,
            totale_cartelle=1,
            indice_riga=None,
            indice_colonna=None,
            numeri_segnati=5,
            totale_numeri=15,
            mancanti=10,
            percentuale=33.3,
        )
        self.evento_segnazione_non_presente = EventoSegnazioneNumero(
            id_giocatore=1,
            nome_giocatore="TestPlayer",
            esito="non_presente",
            numero=7,
            indice_cartella=0,
            numero_cartella=1,
            totale_cartelle=1,
            indice_riga=None,
            indice_colonna=None,
            numeri_segnati=5,
            totale_numeri=15,
            mancanti=10,
            percentuale=33.3,
        )
        self.evento_segnazione_non_estratto = EventoSegnazioneNumero(
            id_giocatore=1,
            nome_giocatore="TestPlayer",
            esito="non_estratto",
            numero=88,
            indice_cartella=0,
            numero_cartella=1,
            totale_cartelle=1,
            indice_riga=None,
            indice_colonna=None,
            numeri_segnati=5,
            totale_numeri=15,
            mancanti=10,
            percentuale=33.3,
        )
        self.evento_fine_turno = EventoFineTurno(
            id_giocatore=1,
            nome_giocatore="TestPlayer",
            numero_turno=5,
            reclamo_turno=None,
        )
        self.evento_riepilogo_cartella = EventoRiepilogoCartellaCorrente(
            id_giocatore=1,
            nome_giocatore="TestPlayer",
            indice_cartella=0,
            numero_cartella=1,
            numeri_segnati=3,
            totale_numeri=15,
            mancanti=12,
            percentuale=20.0,
            numeri_non_segnati=(10, 20, 30, 40),
        )


# ---------------------------------------------------------------------------
# Test 1 — _render_evento_riepilogo_tabellone: esattamente 3 righe
# ---------------------------------------------------------------------------

    def test_riepilogo_tabellone_tre_righe(self) -> None:
        """_render_evento_riepilogo_tabellone deve ritornare esattamente 3 righe."""
        righe = self.renderer._render_evento_riepilogo_tabellone(self.evento_riepilogo_tabellone)
        self.assertEqual(len(righe), 3, f"Attese 3 righe, ottenute {len(righe)}: {righe}")


# ---------------------------------------------------------------------------
# Test 2 — _render_evento_riepilogo_tabellone: tutte ≤ 120 caratteri
# ---------------------------------------------------------------------------

    def test_riepilogo_tabellone_righe_max_120(self) -> None:
        """Tutte le righe di _render_evento_riepilogo_tabellone devono essere ≤ 120 caratteri."""
        righe = self.renderer._render_evento_riepilogo_tabellone(self.evento_riepilogo_tabellone)
        for index, riga in enumerate(righe, start=1):
            self.assertLessEqual(len(riga), 120, f"Riga {index} supera 120 caratteri ({len(riga)}): {riga!r}")


# ---------------------------------------------------------------------------
# Test 3 — _render_evento_segnazione_numero 'segnato': 1 riga con numero
# ---------------------------------------------------------------------------

    def test_segnazione_segnato_una_riga_con_numero(self) -> None:
        """_render_evento_segnazione_numero esito 'segnato' deve produrre 1 riga con il numero."""
        righe = self.renderer._render_evento_segnazione_numero(self.evento_segnazione_segnato)
        self.assertEqual(len(righe), 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}")
        self.assertIn("42", righe[0], f"Numero 42 non trovato nella riga: {righe[0]!r}")


# ---------------------------------------------------------------------------
# Test 4 — _render_evento_segnazione_numero 'gia_segnato': 1 riga
# ---------------------------------------------------------------------------

    def test_segnazione_gia_segnato_una_riga(self) -> None:
        """_render_evento_segnazione_numero esito 'gia_segnato' deve produrre 1 riga."""
        righe = self.renderer._render_evento_segnazione_numero(self.evento_segnazione_gia_segnato)
        self.assertEqual(len(righe), 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}")


# ---------------------------------------------------------------------------
# Test 5 — _render_evento_segnazione_numero 'non_presente': 1 riga
# ---------------------------------------------------------------------------

    def test_segnazione_non_presente_una_riga(self) -> None:
        """_render_evento_segnazione_numero esito 'non_presente' deve produrre 1 riga."""
        righe = self.renderer._render_evento_segnazione_numero(self.evento_segnazione_non_presente)
        self.assertEqual(len(righe), 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}")


# ---------------------------------------------------------------------------
# Test 6 — _render_evento_segnazione_numero 'non_estratto': 1 riga
# ---------------------------------------------------------------------------

    def test_segnazione_non_estratto_una_riga(self) -> None:
        """_render_evento_segnazione_numero esito 'non_estratto' deve produrre 1 riga."""
        righe = self.renderer._render_evento_segnazione_numero(self.evento_segnazione_non_estratto)
        self.assertEqual(len(righe), 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}")


# ---------------------------------------------------------------------------
# Test 7 — _render_evento_fine_turno senza reclamo: 1 riga
# ---------------------------------------------------------------------------

    def test_fine_turno_senza_reclamo_una_riga(self) -> None:
        """_render_evento_fine_turno senza reclamo deve produrre 1 riga."""
        righe = self.renderer._render_evento_fine_turno(self.evento_fine_turno)
        self.assertEqual(len(righe), 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}")


# ---------------------------------------------------------------------------
# Test 8 — _render_evento_riepilogo_cartella_corrente: esattamente 2 righe
# ---------------------------------------------------------------------------

    def test_riepilogo_cartella_corrente_due_righe(self) -> None:
        """_render_evento_riepilogo_cartella_corrente deve produrre esattamente 2 righe."""
        righe = self.renderer._render_evento_riepilogo_cartella_corrente(self.evento_riepilogo_cartella)
        self.assertEqual(len(righe), 2, f"Attese 2 righe, ottenute {len(righe)}: {righe}")


if __name__ == "__main__":
    unittest.main()
