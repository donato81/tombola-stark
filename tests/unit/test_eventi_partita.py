"""Test unitari per bingo_game/events/eventi_partita.py - Gruppo C.

Copertura:
- ReclamoVittoria
- EventoReclamoVittoria
- EventoEsitoReclamoVittoria
- EventoFineTurno

Libreria: solo unittest.
"""

from __future__ import annotations

import unittest

from bingo_game.events.eventi_partita import (
    EventoEsitoReclamoVittoria,
    EventoFineTurno,
    EventoReclamoVittoria,
    ReclamoVittoria,
)

# Compatibilità Python < 3.11: FrozenInstanceError non esiste come simbolo
# pubblico ma è sempre una sottoclasse di AttributeError.
try:
    from dataclasses import FrozenInstanceError as _FrozenErr  # type: ignore[attr-defined]
    _FROZEN_EXC: type[Exception] = _FrozenErr
except ImportError:
    _FROZEN_EXC = AttributeError  # type: ignore[assignment]


class TestReclamoVittoria(unittest.TestCase):
    """Test per la dataclass ReclamoVittoria."""

    def test_tombola_tipo_tombola(self) -> None:
        """tombola(): tipo='tombola'."""
        reclamo = ReclamoVittoria.tombola(indice_cartella=0)
        self.assertEqual(reclamo.tipo, "tombola")

    def test_tombola_indice_riga_none(self) -> None:
        """tombola(): indice_riga=None."""
        reclamo = ReclamoVittoria.tombola(indice_cartella=0)
        self.assertIsNone(reclamo.indice_riga)

    def test_vittoria_di_riga_ambo(self) -> None:
        """vittoria_di_riga() con tipo='ambo': indice_riga valorizzato."""
        reclamo = ReclamoVittoria.vittoria_di_riga(
            tipo="ambo",
            indice_cartella=0,
            indice_riga=1,
        )
        self.assertEqual(reclamo.tipo, "ambo")
        self.assertIsNotNone(reclamo.indice_riga)
        self.assertEqual(reclamo.indice_riga, 1)

    def test_vittoria_di_riga_terno(self) -> None:
        """vittoria_di_riga() con tipo='terno': indice_riga valorizzato."""
        reclamo = ReclamoVittoria.vittoria_di_riga(
            tipo="terno",
            indice_cartella=0,
            indice_riga=0,
        )
        self.assertEqual(reclamo.tipo, "terno")
        self.assertIsNotNone(reclamo.indice_riga)

    def test_vittoria_di_riga_quaterna(self) -> None:
        """vittoria_di_riga() con tipo='quaterna': indice_riga valorizzato."""
        reclamo = ReclamoVittoria.vittoria_di_riga(
            tipo="quaterna",
            indice_cartella=1,
            indice_riga=2,
        )
        self.assertEqual(reclamo.tipo, "quaterna")
        self.assertIsNotNone(reclamo.indice_riga)

    def test_vittoria_di_riga_cinquina(self) -> None:
        """vittoria_di_riga() con tipo='cinquina': indice_riga valorizzato."""
        reclamo = ReclamoVittoria.vittoria_di_riga(
            tipo="cinquina",
            indice_cartella=0,
            indice_riga=1,
        )
        self.assertEqual(reclamo.tipo, "cinquina")
        self.assertIsNotNone(reclamo.indice_riga)

    def test_immutabilita_frozen(self) -> None:
        """Assegnazione su istanza frozen solleva FrozenInstanceError o AttributeError."""
        reclamo = ReclamoVittoria.tombola(indice_cartella=0)
        with self.assertRaises(_FROZEN_EXC):
            reclamo.tipo = "ambo"  # type: ignore[misc]


class TestEventoReclamoVittoria(unittest.TestCase):
    """Test per la dataclass EventoReclamoVittoria."""

    def _reclamo_base(self) -> ReclamoVittoria:
        """Helper: ReclamoVittoria di tombola per gli scenari ante_turno."""
        return ReclamoVittoria.tombola(indice_cartella=0)

    def test_ante_turno_fase_ante_turno(self) -> None:
        """ante_turno(): fase='ANTE_TURNO'."""
        evento = EventoReclamoVittoria.ante_turno(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_turno=3,
            reclamo=self._reclamo_base(),
        )
        self.assertEqual(evento.fase, "ANTE_TURNO")

    def test_ante_turno_campi_id_giocatore(self) -> None:
        """ante_turno(): id_giocatore è memorizzato correttamente."""
        evento = EventoReclamoVittoria.ante_turno(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_turno=3,
            reclamo=self._reclamo_base(),
        )
        self.assertEqual(evento.id_giocatore, 1)

    def test_ante_turno_campi_nome_giocatore(self) -> None:
        """ante_turno(): nome_giocatore è memorizzato correttamente."""
        evento = EventoReclamoVittoria.ante_turno(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_turno=3,
            reclamo=self._reclamo_base(),
        )
        self.assertEqual(evento.nome_giocatore, "Mario")

    def test_ante_turno_campi_numero_turno(self) -> None:
        """ante_turno(): numero_turno è memorizzato correttamente."""
        evento = EventoReclamoVittoria.ante_turno(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_turno=3,
            reclamo=self._reclamo_base(),
        )
        self.assertEqual(evento.numero_turno, 3)

    def test_ante_turno_reclamo_presente(self) -> None:
        """ante_turno(): reclamo è il ReclamoVittoria passato."""
        reclamo = self._reclamo_base()
        evento = EventoReclamoVittoria.ante_turno(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_turno=3,
            reclamo=reclamo,
        )
        self.assertIs(evento.reclamo, reclamo)


class TestEventoEsitoReclamoVittoria(unittest.TestCase):
    """Test per la dataclass EventoEsitoReclamoVittoria."""

    def _reclamo_base(self) -> ReclamoVittoria:
        """Helper: ReclamoVittoria di riga per gli scenari di esito."""
        return ReclamoVittoria.vittoria_di_riga(
            tipo="ambo",
            indice_cartella=0,
            indice_riga=1,
        )

    def test_successo_ok_true(self) -> None:
        """successo(): ok=True."""
        evento = EventoEsitoReclamoVittoria.successo(
            id_giocatore=1,
            nome_giocatore="Mario",
            reclamo=self._reclamo_base(),
        )
        self.assertTrue(evento.ok)

    def test_successo_errore_none(self) -> None:
        """successo(): errore=None."""
        evento = EventoEsitoReclamoVittoria.successo(
            id_giocatore=1,
            nome_giocatore="Mario",
            reclamo=self._reclamo_base(),
        )
        self.assertIsNone(evento.errore)

    def test_fallimento_ok_false(self) -> None:
        """fallimento(): ok=False."""
        evento = EventoEsitoReclamoVittoria.fallimento(
            id_giocatore=1,
            nome_giocatore="Mario",
            reclamo=self._reclamo_base(),
            errore="VERIFICA_FALLITA",
        )
        self.assertFalse(evento.ok)

    def test_fallimento_errore_valorizzato(self) -> None:
        """fallimento(): errore valorizzato con codice valido 'VERIFICA_FALLITA'."""
        evento = EventoEsitoReclamoVittoria.fallimento(
            id_giocatore=1,
            nome_giocatore="Mario",
            reclamo=self._reclamo_base(),
            errore="VERIFICA_FALLITA",
        )
        self.assertEqual(evento.errore, "VERIFICA_FALLITA")

    def test_successo_con_parametri_opzionali(self) -> None:
        """successo() con indice_turno e numero_estratto opzionali valorizzati."""
        evento = EventoEsitoReclamoVittoria.successo(
            id_giocatore=1,
            nome_giocatore="Mario",
            reclamo=self._reclamo_base(),
            indice_turno=5,
            numero_estratto=42,
        )
        self.assertEqual(evento.indice_turno, 5)
        self.assertEqual(evento.numero_estratto, 42)

    def test_fallimento_con_parametri_opzionali(self) -> None:
        """fallimento() con indice_turno e numero_estratto opzionali valorizzati."""
        evento = EventoEsitoReclamoVittoria.fallimento(
            id_giocatore=None,
            nome_giocatore="Bot",
            reclamo=self._reclamo_base(),
            errore="VERIFICA_FALLITA",
            indice_turno=3,
            numero_estratto=17,
        )
        self.assertFalse(evento.ok)
        self.assertEqual(evento.errore, "VERIFICA_FALLITA")
        self.assertEqual(evento.indice_turno, 3)
        self.assertEqual(evento.numero_estratto, 17)


class TestEventoFineTurno(unittest.TestCase):
    """Test per la dataclass EventoFineTurno."""

    def test_crea_senza_reclamo_reclamo_turno_none(self) -> None:
        """crea() senza reclamo: reclamo_turno=None."""
        evento = EventoFineTurno.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_turno=2,
        )
        self.assertIsNone(evento.reclamo_turno)

    def test_crea_con_reclamo_identita(self) -> None:
        """crea() con reclamo: reclamo_turno è il ReclamoVittoria passato."""
        reclamo = ReclamoVittoria.tombola(indice_cartella=0)
        evento = EventoFineTurno.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_turno=2,
            reclamo_turno=reclamo,
        )
        self.assertIs(evento.reclamo_turno, reclamo)


if __name__ == "__main__":
    unittest.main()
