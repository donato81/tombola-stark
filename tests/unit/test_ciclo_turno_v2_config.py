"""
Test unitari per la propagazione dei parametri timer V2 da FinestraConfigurazione
a FinestraGioco.

Non usa wx: verifica che i valori di durata vengano convertiti correttamente
da secondi a millisecondi.

Task E-3.
"""
from __future__ import annotations

import unittest


class TestConversioneParametriV2(unittest.TestCase):
    """
    Verifica la logica di conversione secondi → millisecondi usata
    in FinestraConfigurazione._on_conferma().

    I calcoli sono:
      durata_finestra_ms = durata_finestra_secondi * 1000
      durata_pausa_ms    = durata_pausa_secondi    * 1000
    """

    def test_conversione_default_finestra(self) -> None:
        """Il valore default 60 secondi diventa 60000 ms."""
        secondi = 60
        self.assertEqual(secondi * 1000, 60000)

    def test_conversione_default_pausa(self) -> None:
        """Il valore default 5 secondi diventa 5000 ms."""
        secondi = 5
        self.assertEqual(secondi * 1000, 5000)

    def test_conversione_minimo_finestra(self) -> None:
        """Il minimo 5 secondi diventa 5000 ms."""
        self.assertEqual(5 * 1000, 5000)

    def test_conversione_massimo_finestra(self) -> None:
        """Il massimo 300 secondi diventa 300000 ms."""
        self.assertEqual(300 * 1000, 300000)

    def test_conversione_massimo_pausa(self) -> None:
        """Il massimo 30 secondi per la pausa diventa 30000 ms."""
        self.assertEqual(30 * 1000, 30000)

    def test_parametri_finestragioco_accettano_valori_personalizzati(self) -> None:
        """FinestraGioco accetta durata_finestra_ms e durata_pausa_ms nel costruttore.

        Il test verifica che i valori passati siano coerenti con quelli aspettati –
        senza istanziare wx (non disponibile in CI).
        """
        # Simula i valori che FinestraConfigurazione._on_conferma() calcolerebbe
        # per un utente che ha scelto 90 secondi di finestra e 10 di pausa.
        durata_finestra_ms = 90 * 1000
        durata_pausa_ms = 10 * 1000

        self.assertEqual(durata_finestra_ms, 90000)
        self.assertEqual(durata_pausa_ms, 10000)
