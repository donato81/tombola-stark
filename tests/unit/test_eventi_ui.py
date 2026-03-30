"""Test unitari per bingo_game/events/eventi_ui.py — Gruppo B.

Copertura:
- EventoFocusAutoImpostato
- EventoFocusCartellaImpostato

Libreria: solo unittest (nessun pytest).
"""

from __future__ import annotations

import unittest

from bingo_game.events.eventi_ui import (
    EventoFocusAutoImpostato,
    EventoFocusCartellaImpostato,
)

# Compatibilità Python < 3.11: FrozenInstanceError non esiste come simbolo
# pubblico ma è sempre una sottoclasse di AttributeError.
try:
    from dataclasses import FrozenInstanceError as _FrozenErr  # type: ignore[attr-defined]
    _FROZEN_EXC: type[Exception] = _FrozenErr
except ImportError:
    _FROZEN_EXC = AttributeError  # type: ignore[assignment]


class TestEventoFocusAutoImpostato(unittest.TestCase):
    """Test per la dataclass EventoFocusAutoImpostato."""

    def test_costruzione_con_cartella_e_indice_zero(self) -> None:
        """Costruzione base: tipo_focus='cartella', indice=0."""
        evento = EventoFocusAutoImpostato(tipo_focus="cartella", indice=0)
        self.assertEqual(evento.tipo_focus, "cartella")
        self.assertEqual(evento.indice, 0)

    def test_valori_ammessi_tipo_focus_riga(self) -> None:
        """Il valore 'riga' è ammesso per tipo_focus."""
        evento = EventoFocusAutoImpostato(tipo_focus="riga", indice=1)
        self.assertEqual(evento.tipo_focus, "riga")

    def test_valori_ammessi_tipo_focus_colonna(self) -> None:
        """Il valore 'colonna' è ammesso per tipo_focus."""
        evento = EventoFocusAutoImpostato(tipo_focus="colonna", indice=2)
        self.assertEqual(evento.tipo_focus, "colonna")

    def test_immutabilita_frozen(self) -> None:
        """Assegnazione su istanza frozen solleva FrozenInstanceError o AttributeError."""
        evento = EventoFocusAutoImpostato(tipo_focus="cartella", indice=0)
        with self.assertRaises(_FROZEN_EXC):
            evento.tipo_focus = "riga"  # type: ignore[misc]


class TestEventoFocusCartellaImpostato(unittest.TestCase):
    """Test per la dataclass EventoFocusCartellaImpostato."""

    def _costruisci_base(self) -> EventoFocusCartellaImpostato:
        """Helper: istanza con campi obbligatori e default."""
        return EventoFocusCartellaImpostato(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_cartella=1,
            indice_cartella=0,
        )

    def test_costruzione_base_campi_obbligatori(self) -> None:
        """Costruzione con tutti i campi obbligatori: i valori sono memorizzati correttamente."""
        evento = self._costruisci_base()
        self.assertEqual(evento.id_giocatore, 1)
        self.assertEqual(evento.nome_giocatore, "Mario")
        self.assertEqual(evento.numero_cartella, 1)
        self.assertEqual(evento.indice_cartella, 0)

    def test_default_reset_riga_colonna_false(self) -> None:
        """reset_riga_colonna vale False per default."""
        evento = self._costruisci_base()
        self.assertFalse(evento.reset_riga_colonna)

    def test_costruzione_con_reset_riga_colonna_true(self) -> None:
        """Costruzione con reset_riga_colonna=True: il campo è impostato correttamente."""
        evento = EventoFocusCartellaImpostato(
            id_giocatore=None,
            nome_giocatore="Luigi",
            numero_cartella=2,
            indice_cartella=1,
            reset_riga_colonna=True,
        )
        self.assertTrue(evento.reset_riga_colonna)

    def test_immutabilita_frozen(self) -> None:
        """Assegnazione su istanza frozen solleva FrozenInstanceError o AttributeError."""
        evento = self._costruisci_base()
        with self.assertRaises(_FROZEN_EXC):
            evento.nome_giocatore = "Nuovo"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
