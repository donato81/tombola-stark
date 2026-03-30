"""
Test unitari per le classi E3 di eventi_output_ui_umani.py:
- EventoVerificaNumeroEstratto
- EventoUltimoNumeroEstratto
- EventoUltimiNumeriEstratti
- EventoRiepilogoTabellone
- EventoListaNumeriEstratti

Perimetro: solo E3. Zero mock, zero import pytest.
"""

import unittest
from bingo_game.events.eventi_output_ui_umani import (
    EventoVerificaNumeroEstratto,
    EventoUltimoNumeroEstratto,
    EventoUltimiNumeriEstratti,
    EventoRiepilogoTabellone,
    EventoListaNumeriEstratti,
)


class TestEventoVerificaNumeroEstratto(unittest.TestCase):

    def test_estratto_si_crea_evento_con_estratto_true(self):
        evento = EventoVerificaNumeroEstratto.estratto_si(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=42,
        )
        self.assertTrue(evento.estratto)
        self.assertEqual(evento.numero, 42)

    def test_estratto_no_crea_evento_con_estratto_false(self):
        evento = EventoVerificaNumeroEstratto.estratto_no(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=7,
        )
        self.assertFalse(evento.estratto)
        self.assertEqual(evento.numero, 7)

    def test_estratto_si_preserva_contesto_giocatore(self):
        evento = EventoVerificaNumeroEstratto.estratto_si(
            id_giocatore=99,
            nome_giocatore="Luigi",
            numero=1,
        )
        self.assertEqual(evento.id_giocatore, 99)
        self.assertEqual(evento.nome_giocatore, "Luigi")


class TestEventoUltimoNumeroEstratto(unittest.TestCase):

    def test_numero_presente_valorizza_ultimo_numero(self):
        evento = EventoUltimoNumeroEstratto.numero_presente(
            id_giocatore=1,
            nome_giocatore="Mario",
            ultimo_numero=90,
        )
        self.assertEqual(evento.ultimo_numero, 90)

    def test_nessuna_estrazione_valorizza_none(self):
        evento = EventoUltimoNumeroEstratto.nessuna_estrazione(
            id_giocatore=1,
            nome_giocatore="Mario",
        )
        self.assertIsNone(evento.ultimo_numero)

    def test_numero_presente_preserva_contesto_giocatore(self):
        evento = EventoUltimoNumeroEstratto.numero_presente(
            id_giocatore=5,
            nome_giocatore="Peach",
            ultimo_numero=77,
        )
        self.assertEqual(evento.id_giocatore, 5)
        self.assertEqual(evento.nome_giocatore, "Peach")


class TestEventoUltimiNumeriEstratti(unittest.TestCase):

    def test_crea_con_numeri_converte_in_tuple(self):
        evento = EventoUltimiNumeriEstratti.crea_con_numeri(
            id_giocatore=1,
            nome_giocatore="Mario",
            richiesti=5,
            numeri=[10, 20, 30],
        )
        self.assertIsInstance(evento.numeri, tuple)
        self.assertEqual(evento.numeri, (10, 20, 30))

    def test_crea_con_numeri_calcola_visualizzati(self):
        evento = EventoUltimiNumeriEstratti.crea_con_numeri(
            id_giocatore=1,
            nome_giocatore="Mario",
            richiesti=5,
            numeri=[10, 20, 30],
        )
        self.assertEqual(evento.visualizzati, 3)

    def test_crea_con_numeri_taglia_agli_ultimi_richiesti_se_overflow(self):
        evento = EventoUltimiNumeriEstratti.crea_con_numeri(
            id_giocatore=1,
            nome_giocatore="Mario",
            richiesti=5,
            numeri=[1, 2, 3, 4, 5, 6, 7],
        )
        self.assertEqual(len(evento.numeri), 5)
        self.assertEqual(evento.numeri, (3, 4, 5, 6, 7))
        self.assertEqual(evento.visualizzati, 5)

    def test_nessuna_estrazione_restituisce_tuple_vuota_e_zero(self):
        evento = EventoUltimiNumeriEstratti.nessuna_estrazione(
            id_giocatore=1,
            nome_giocatore="Mario",
            richiesti=5,
        )
        self.assertEqual(evento.numeri, ())
        self.assertEqual(evento.visualizzati, 0)

    def test_crea_con_numeri_entro_richiesti_non_taglia(self):
        evento = EventoUltimiNumeriEstratti.crea_con_numeri(
            id_giocatore=1,
            nome_giocatore="Mario",
            richiesti=5,
            numeri=[11, 22],
        )
        self.assertEqual(evento.numeri, (11, 22))
        self.assertEqual(evento.visualizzati, 2)


class TestEventoRiepilogoTabellone(unittest.TestCase):

    def test_crea_converte_ultimi_estratti_in_tuple(self):
        evento = EventoRiepilogoTabellone.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_numeri=90,
            totale_estratti=10,
            totale_mancanti=80,
            percentuale_estrazione=11.11,
            ultimi_estratti=[5, 12, 33],
            ultimo_estratto=33,
        )
        self.assertIsInstance(evento.ultimi_estratti, tuple)
        self.assertEqual(evento.ultimi_estratti, (5, 12, 33))

    def test_crea_calcola_ultimi_visualizzati(self):
        evento = EventoRiepilogoTabellone.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_numeri=90,
            totale_estratti=10,
            totale_mancanti=80,
            percentuale_estrazione=11.11,
            ultimi_estratti=[5, 12, 33],
            ultimo_estratto=33,
        )
        self.assertEqual(evento.ultimi_visualizzati, 3)

    def test_crea_imposta_ultimo_estratto_none_se_lista_vuota(self):
        evento = EventoRiepilogoTabellone.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_numeri=90,
            totale_estratti=0,
            totale_mancanti=90,
            percentuale_estrazione=0.0,
            ultimi_estratti=[],
            ultimo_estratto=99,
        )
        self.assertIsNone(evento.ultimo_estratto)

    def test_crea_imposta_ultimo_estratto_none_anche_con_valore_passato(self):
        evento = EventoRiepilogoTabellone.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_numeri=90,
            totale_estratti=0,
            totale_mancanti=90,
            percentuale_estrazione=0.0,
            ultimi_estratti=[],
            ultimo_estratto=42,
        )
        self.assertIsNone(evento.ultimo_estratto)

    def test_crea_preserva_statistiche_con_estrazioni(self):
        evento = EventoRiepilogoTabellone.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_numeri=90,
            totale_estratti=45,
            totale_mancanti=45,
            percentuale_estrazione=50.0,
            ultimi_estratti=[10, 20],
            ultimo_estratto=20,
        )
        self.assertEqual(evento.totale_numeri, 90)
        self.assertEqual(evento.totale_estratti, 45)
        self.assertEqual(evento.totale_mancanti, 45)
        self.assertAlmostEqual(evento.percentuale_estrazione, 50.0)
        self.assertEqual(evento.ultimo_estratto, 20)


class TestEventoListaNumeriEstratti(unittest.TestCase):

    def test_crea_ordina_numeri_crescente(self):
        evento = EventoListaNumeriEstratti.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            numeri_estratti=[50, 10, 30, 20, 40],
        )
        self.assertEqual(evento.numeri_estratti, (10, 20, 30, 40, 50))

    def test_crea_converte_in_tuple(self):
        evento = EventoListaNumeriEstratti.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            numeri_estratti=[5, 3, 1],
        )
        self.assertIsInstance(evento.numeri_estratti, tuple)

    def test_crea_calcola_totale_estratti(self):
        evento = EventoListaNumeriEstratti.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            numeri_estratti=[5, 3, 1],
        )
        self.assertEqual(evento.totale_estratti, 3)

    def test_crea_lista_vuota(self):
        evento = EventoListaNumeriEstratti.crea(
            id_giocatore=1,
            nome_giocatore="Mario",
            numeri_estratti=[],
        )
        self.assertEqual(evento.numeri_estratti, ())
        self.assertEqual(evento.totale_estratti, 0)


if __name__ == "__main__":
    unittest.main()
