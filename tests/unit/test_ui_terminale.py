"""Unit tests per bingo_game.ui.ui_terminale.TerminalUI (v0.7.0).

Copertura test case manuali TC01–TC04 e flusso felice TC05.
Riferimento piano: documentations/PLAN_TERMINAL_START_MENU.md
"""
from __future__ import annotations

import io
import unittest
from unittest.mock import MagicMock, patch

from bingo_game.ui.ui_terminale import TerminalUI


class TestValidazioneNome(unittest.TestCase):
    """Test Stato B: validazione nome giocatore."""

    def test_tc01_nome_vuoto_dopo_strip(self) -> None:
        """TC01: input di soli spazi → errore CONFIG_ERRORE_NOME_VUOTO, poi nome valido."""
        with (
            patch("builtins.input", side_effect=["   ", "Marco"]),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            tui = TerminalUI()
            nome = tui._chiedi_nome()

        self.assertEqual(nome, "Marco")
        self.assertIn("Errore: Nome non valido.", stdout.getvalue())

    def test_tc02_nome_troppo_lungo(self) -> None:
        """TC02: nome > 15 char → errore CONFIG_ERRORE_NOME_TROPPO_LUNGO, poi nome valido."""
        with (
            patch("builtins.input", side_effect=["NomeMoltoLungoOltreQuindici", "Marco"]),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            tui = TerminalUI()
            nome = tui._chiedi_nome()

        self.assertEqual(nome, "Marco")
        self.assertIn("Errore: Nome troppo lungo.", stdout.getvalue())

    def test_strip_applicato_prima_del_check(self) -> None:
        """Strip corretto: '  Marco  ' → 'Marco' senza errori."""
        with patch("builtins.input", return_value="  Marco  "):
            tui = TerminalUI()
            nome = tui._chiedi_nome()

        self.assertEqual(nome, "Marco")


class TestValidazioneBot(unittest.TestCase):
    """Test Stato C: validazione numero di bot."""

    def test_tc03_bot_sotto_range(self) -> None:
        """TC03a: bot = 0 → errore CONFIG_ERRORE_BOT_RANGE, poi valore valido."""
        with (
            patch("builtins.input", side_effect=["0", "3"]),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            tui = TerminalUI()
            valore = tui._chiedi_bot()

        self.assertEqual(valore, 3)
        self.assertIn("Errore: Numero bot non valido.", stdout.getvalue())

    def test_tc03_bot_sopra_range(self) -> None:
        """TC03b: bot = 9 → errore CONFIG_ERRORE_BOT_RANGE, poi valore valido."""
        with (
            patch("builtins.input", side_effect=["9", "3"]),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            tui = TerminalUI()
            valore = tui._chiedi_bot()

        self.assertEqual(valore, 3)
        self.assertIn("Errore: Numero bot non valido.", stdout.getvalue())

    def test_bot_tipo_non_valido(self) -> None:
        """Input non intero → riuso MESSAGGI_ERRORI['NUMERO_TIPO_NON_VALIDO']."""
        with (
            patch("builtins.input", side_effect=["tre", "3"]),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            tui = TerminalUI()
            valore = tui._chiedi_bot()

        self.assertEqual(valore, 3)
        self.assertIn("Errore: Tipo non valido.", stdout.getvalue())


class TestValidazioneCartelle(unittest.TestCase):
    """Test Stato D: validazione numero di cartelle."""

    def test_tc04_cartelle_fuori_range(self) -> None:
        """TC04: cartelle = 7 → errore CONFIG_ERRORE_CARTELLE_RANGE, poi valore valido."""
        with (
            patch("builtins.input", side_effect=["7", "2"]),
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            tui = TerminalUI()
            valore = tui._chiedi_cartelle()

        self.assertEqual(valore, 2)
        self.assertIn("Errore: Numero cartelle non valido.", stdout.getvalue())


class TestFlussoFelice(unittest.TestCase):
    """Test del flusso completo con input validi."""

    def test_flusso_felice_completo(self) -> None:
        """TC05: input validi → crea_partita_standard e avvia_partita_sicura chiamati correttamente."""
        mock_partita = MagicMock()

        with (
            patch("sys.stdout", new_callable=io.StringIO) as stdout,
            patch("builtins.input", side_effect=["Marco", "3", "2"]),
            patch(
                "bingo_game.ui.ui_terminale.crea_partita_standard",
                return_value=mock_partita,
            ) as mock_crea,
            patch(
                "bingo_game.ui.ui_terminale.avvia_partita_sicura",
                return_value=True,
            ) as mock_avvia,
            patch("bingo_game.ui.ui_terminale._loop_partita") as mock_loop,
        ):
            tui = TerminalUI()
            tui.avvia()

        mock_crea.assert_called_once_with(
            nome_giocatore_umano="Marco",
            num_cartelle_umano=2,
            num_bot=3,
        )
        mock_avvia.assert_called_once_with(mock_partita)
        mock_loop.assert_called_once_with(mock_partita)
        self.assertIn("Benvenuto in Tombola Stark!", stdout.getvalue())
        self.assertIn("Configurazione completata. Avvio partita...", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
