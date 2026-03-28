"""
Test di regressione per Bug 1 v0.9.1:
`imposta_focus_cartella` chiamava `reset_focus_riga_e_colonna` (senza underscore)
invece di `_reset_focus_riga_e_colonna` (con underscore).

Verifica che dopo `imposta_focus_cartella(1)` il focus sia impostato correttamente
senza sollevare AttributeError.
"""
from __future__ import annotations

import unittest

from bingo_game.cartella import Cartella
from bingo_game.players.giocatore_umano import GiocatoreUmano


class TestImpostaFocusCartellaRegression(unittest.TestCase):
    """Test di regressione per imposta_focus_cartella."""

    def test_imposta_focus_cartella_non_solleva_eccezioni(self) -> None:
        """imposta_focus_cartella(1) non deve sollevare AttributeError (regressione Bug 1 v0.9.1)."""
        giocatore = GiocatoreUmano("TestReg", id_giocatore=1)
        giocatore.aggiungi_cartella(Cartella())

        esito = giocatore.imposta_focus_cartella(1)

        self.assertTrue(
            esito.ok,
            f"imposta_focus_cartella(1) deve avere successo, errore: {esito.errore}",
        )


    def test_imposta_focus_cartella_imposta_indice_zero(self) -> None:
        """Dopo imposta_focus_cartella(1), _indice_cartella_focus deve essere 0."""
        giocatore = GiocatoreUmano("TestReg", id_giocatore=1)
        giocatore.aggiungi_cartella(Cartella())

        giocatore.imposta_focus_cartella(1)

        self.assertEqual(giocatore._indice_cartella_focus, 0)


    def test_imposta_focus_cartella_cambio_cartella_non_solleva_eccezioni(self) -> None:
        """imposta_focus_cartella(2) su 2 cartelle non deve sollevare AttributeError (reset riga/colonna)."""
        giocatore = GiocatoreUmano("TestReg", id_giocatore=1)
        giocatore.aggiungi_cartella(Cartella())
        giocatore.aggiungi_cartella(Cartella())

        giocatore.imposta_focus_cartella(1)
        esito = giocatore.imposta_focus_cartella(2)

        self.assertTrue(esito.ok, f"Cambio focus cartella deve avere successo, errore: {esito.errore}")
        self.assertEqual(giocatore._indice_cartella_focus, 1)


if __name__ == "__main__":
    unittest.main()
