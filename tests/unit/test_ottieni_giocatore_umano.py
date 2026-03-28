"""
Test unitari per game_controller.ottieni_giocatore_umano() — v0.9.0

Verifica:
1. Con partita standard: ritorna GiocatoreUmano non-None.
2. Con partita standard: il nome corrisponde a quello inserito.
3. Con parametro non-Partita: ritorna None senza eccezioni.
4. Smoke test regressione: esegui_turno_sicuro non è rotto dopo le modifiche.
"""
from __future__ import annotations

import unittest


class TestOttieniGiocatoreUmano(unittest.TestCase):
    """Test unittest per ottieni_giocatore_umano()."""

    def setUp(self) -> None:
        from bingo_game.game_controller import avvia_partita_sicura, crea_partita_standard

        self.partita_configurata = crea_partita_standard(
            nome_giocatore_umano="TestUmano",
            num_cartelle_umano=1,
            num_bot=1,
        )
        avvia_partita_sicura(self.partita_configurata)


# ---------------------------------------------------------------------------
# Test 1 — Ritorna GiocatoreUmano non-None
# ---------------------------------------------------------------------------

    def test_ottieni_giocatore_umano_ritorna_non_none(self) -> None:
        """Con partita valida deve ritornare un oggetto non-None."""
        from bingo_game.game_controller import ottieni_giocatore_umano

        risultato = ottieni_giocatore_umano(self.partita_configurata)
        self.assertIsNotNone(risultato, "ottieni_giocatore_umano ha ritornato None su partita valida")


# ---------------------------------------------------------------------------
# Test 2 — Il nome corrisponde
# ---------------------------------------------------------------------------

    def test_ottieni_giocatore_umano_nome_corretto(self) -> None:
        """Il GiocatoreUmano restituito deve avere il nome usato in crea_partita_standard."""
        from bingo_game.game_controller import ottieni_giocatore_umano

        giocatore = ottieni_giocatore_umano(self.partita_configurata)
        self.assertIsNotNone(giocatore)
        self.assertEqual(giocatore.nome, "TestUmano", f"Nome atteso 'TestUmano', ottenuto '{giocatore.nome}'")


# ---------------------------------------------------------------------------
# Test 3 — Con parametro non-Partita ritorna None
# ---------------------------------------------------------------------------

    def test_ottieni_giocatore_umano_parametro_invalido_ritorna_none(self) -> None:
        """Con parametro non-Partita deve ritornare None senza sollevare eccezioni."""
        from bingo_game.game_controller import ottieni_giocatore_umano

        self.assertIsNone(ottieni_giocatore_umano(None))
        self.assertIsNone(ottieni_giocatore_umano("non-partita"))
        self.assertIsNone(ottieni_giocatore_umano(42))


# ---------------------------------------------------------------------------
# Test 4 — Smoke test: esegui_turno_sicuro non è rotto
# ---------------------------------------------------------------------------

    def test_esegui_turno_sicuro_smoke(self) -> None:
        """Dopo le modifiche del controller, esegui_turno_sicuro deve ancora funzionare."""
        from bingo_game.game_controller import esegui_turno_sicuro

        risultato = esegui_turno_sicuro(self.partita_configurata)
        self.assertIsNotNone(risultato, "esegui_turno_sicuro ha ritornato None su partita valida")
        self.assertIn("numero_estratto", risultato)
        self.assertIn("tombola_rilevata", risultato)


if __name__ == "__main__":
    unittest.main()
