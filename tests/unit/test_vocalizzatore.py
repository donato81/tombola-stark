"""
Test unitari per my_lib/vocalizzatore.py

Copertura:
- NullVocalizzatore: nessuna eccezione su vocalizza_testo
- Vocalizzatore: forwarding del testo al backend fake
- Vocalizzatore: forwarding di interrompi come interrupt=True/False
- Vocalizzatore: silenzio su eccezione del backend
- conformita' strutturale IVocalizzatore per entrambe le classi

Non incluso:
- test costruzione con Auto() senza patch: fragile in ambiente headless/CI.
  Auto() puo' sollevare errori se nessun screen reader e' attivo.
  Non e' stato introdotto un test fragile come da indicazioni del task.
"""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from my_lib.vocalizzatore import IVocalizzatore, NullVocalizzatore, Vocalizzatore


class TestNullVocalizzatore(unittest.TestCase):
    """Verifica che NullVocalizzatore sia una no-op silenziosa."""

    def test_vocalizza_testo_non_lancia_eccezioni(self) -> None:
        v = NullVocalizzatore()
        v.vocalizza_testo("testo di prova")

    def test_vocalizza_testo_con_interrompi_true_non_lancia_eccezioni(self) -> None:
        v = NullVocalizzatore()
        v.vocalizza_testo("testo di prova", interrompi=True)

    def test_null_vocalizzatore_implementa_ivocalizzatore(self) -> None:
        v = NullVocalizzatore()
        self.assertIsInstance(v, IVocalizzatore)


class TestVocalizzatore(unittest.TestCase):
    """Verifica il forwarding del backend e il comportamento best-effort."""

    def _make_backend(self) -> MagicMock:
        backend = MagicMock()
        backend.speak.return_value = None
        return backend

    def test_vocalizza_testo_chiama_speak_con_testo(self) -> None:
        backend = self._make_backend()
        v = Vocalizzatore(backend=backend)
        v.vocalizza_testo("ciao mondo")
        backend.speak.assert_called_once_with("ciao mondo", interrupt=False)

    def test_vocalizza_testo_interrompi_false_passa_interrupt_false(self) -> None:
        backend = self._make_backend()
        v = Vocalizzatore(backend=backend)
        v.vocalizza_testo("testo", interrompi=False)
        backend.speak.assert_called_once_with("testo", interrupt=False)

    def test_vocalizza_testo_interrompi_true_passa_interrupt_true(self) -> None:
        backend = self._make_backend()
        v = Vocalizzatore(backend=backend)
        v.vocalizza_testo("testo", interrompi=True)
        backend.speak.assert_called_once_with("testo", interrupt=True)

    def test_vocalizza_testo_silenzioso_su_eccezione_backend(self) -> None:
        backend = self._make_backend()
        backend.speak.side_effect = RuntimeError("backend non disponibile")
        v = Vocalizzatore(backend=backend)
        try:
            v.vocalizza_testo("testo")
        except Exception as exc:
            self.fail(f"vocalizza_testo ha propagato un'eccezione: {exc}")

    def test_vocalizzatore_implementa_ivocalizzatore(self) -> None:
        backend = self._make_backend()
        v = Vocalizzatore(backend=backend)
        self.assertIsInstance(v, IVocalizzatore)


if __name__ == "__main__":
    unittest.main()
