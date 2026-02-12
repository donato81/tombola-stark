"""
Test per il modulo comandi_partita.py

File: tests/test_comandi_partita.py

Testa la classe ComandiSistema verificando:
- Creazione partite (parametri validi/invalidi)
- Transizioni stato (non_iniziata → in_corso → terminata)
- Esecuzione turni (numero estratto, premi, coerenza)
- Lettura stato (numeri, giocatori, premi)
- Controllo tombola e terminazione

Total: 29 test strutturati che coprono TUTTI gli edge case.
"""

import unittest
from bingo_game.comandi_partita import ComandiSistema
from bingo_game.partita import Partita


class TestComandiSistema(unittest.TestCase):
    """Suite completa di test per ComandiSistema."""

    def setUp(self) -> None:
        """Prepara l'oggetto ComandiSistema per ogni test."""
        self.comandi = ComandiSistema()

    # =========================================================================
    # SEZIONE 1: Test crea_nuova_partita (5 test)
    # =========================================================================

    def test_crea_nuova_partita_successo_standard(self) -> None:
        """
        Verifica creazione partita con parametri validi.
        Ritorna Partita valida con giocatore umano e bot.
        """
        # 1. Esegui
        partita = self.comandi.crea_nuova_partita("Mario", 2, 3)

        # 2. Verifiche
        self.assertIsNotNone(partita)
        self.assertIsInstance(partita, Partita)
        self.assertEqual(partita.get_stato_partita(), "non_iniziata")
        self.assertEqual(partita.get_numero_giocatori(), 4)  # 1 umano + 3 bot

    def test_crea_nuova_partita_nome_vuoto(self) -> None:
        """
        Verifica che nome vuoto ritorna None (parametro invalido).
        """
        partita = self.comandi.crea_nuova_partita("", 1, 1)
        self.assertIsNone(partita)

    def test_crea_nuova_partita_nome_solo_spazi(self) -> None:
        """
        Verifica che nome con solo spazi ritorna None.
        """
        partita = self.comandi.crea_nuova_partita("   ", 1, 1)
        self.assertIsNone(partita)

    def test_crea_nuova_partita_cartelle_negative(self) -> None:
        """
        Verifica che cartelle negative ritornano None.
        """
        partita = self.comandi.crea_nuova_partita("Mario", -1, 1)
        self.assertIsNone(partita)

    def test_crea_nuova_partita_bot_zero_crea_uno(self) -> None:
        """
        Verifica che bot=0 crea comunque minimo 1 bot (regola sistema).
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 0)
        self.assertIsNotNone(partita)
        self.assertEqual(partita.get_numero_giocatori(), 2)  # 1 umano + 1 bot forzato

    def test_crea_nuova_partita_bot_eccessivi_ritorna_none(self) -> None:
        """
        Verifica che bot>7 ritorna None (massimo sistema: 1 umano + 7 bot = 8 totali).
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 8)
        self.assertIsNone(partita)

    # =========================================================================
    # SEZIONE 2: Test avvia_partita (4 test)
    # =========================================================================

    def test_avvia_partita_successo(self) -> None:
        """
        Verifica avvio riuscito: partita non_iniziata → in_corso.
        """
        # 1. Prepara
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.assertEqual(partita.get_stato_partita(), "non_iniziata")

        # 2. Esegui
        risultato = self.comandi.avvia_partita(partita)

        # 3. Verifiche
        self.assertTrue(risultato)
        self.assertEqual(partita.get_stato_partita(), "in_corso")

    def test_avvia_partita_parametro_invalido(self) -> None:
        """
        Verifica che parametro non-Partita ritorna False.
        """
        risultato = self.comandi.avvia_partita("non una partita")
        self.assertFalse(risultato)

    def test_avvia_partita_doppio_avvio_fallisce(self) -> None:
        """
        Verifica che secondo avvio fallisce (già in_corso).
        """
        # 1. Prepara e avvia
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)
        self.assertEqual(partita.get_stato_partita(), "in_corso")

        # 2. Tenta secondo avvio
        risultato = self.comandi.avvia_partita(partita)

        # 3. Verifica fallimento
        self.assertFalse(risultato)
        self.assertEqual(partita.get_stato_partita(), "in_corso")  # Rimane in_corso

    def test_avvia_partita_coerenza_stato_interno(self) -> None:
        """
        Verifica che lo stato interno di Partita è coerente dopo avvio.
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)

        # Verifica che is_terminata() è False (partita in corso)
        self.assertFalse(partita.is_terminata())

    # =========================================================================
    # SEZIONE 3: Test esegui_turno (5 test)
    # =========================================================================

    def test_esegui_turno_successo_struttura_dict(self) -> None:
        """
        Verifica esecuzione turno ritorna dict con chiavi essenziali.
        """
        # 1. Prepara
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)

        # 2. Esegui turno
        risultato = self.comandi.esegui_turno(partita)

        # 3. Verifiche struttura
        self.assertIsInstance(risultato, dict)
        self.assertIn("numero_estratto", risultato)
        self.assertIn("premi_nuovi", risultato)
        self.assertIn("tombola_rilevata", risultato)

    def test_esegui_turno_numero_valido_intervallo(self) -> None:
        """
        Verifica che numero estratto è tra 1-90 (tombola italiana).
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)

        risultato = self.comandi.esegui_turno(partita)

        numero = risultato["numero_estratto"]
        self.assertGreaterEqual(numero, 1)
        self.assertLessEqual(numero, 90)

    def test_esegui_turno_partita_non_in_corso(self) -> None:
        """
        Verifica che turno su partita non_iniziata ritorna None.
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        # NON avviata
        risultato = self.comandi.esegui_turno(partita)

        self.assertIsNone(risultato)

    def test_esegui_turno_parametro_invalido(self) -> None:
        """
        Verifica che parametro non-Partita ritorna None.
        """
        risultato = self.comandi.esegui_turno("non una partita")
        self.assertIsNone(risultato)

    def test_esegui_turno_multipli_incremento_conteggio(self) -> None:
        """
        Verifica che turni multipli incrementano conteggio estratti.
        """
        # 1. Prepara
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)
        self.assertEqual(partita.tabellone.get_conteggio_estratti(), 0)

        # 2. Esegui 5 turni
        numeri_estratti = []
        for i in range(5):
            risultato = self.comandi.esegui_turno(partita)
            self.assertIsNotNone(risultato)
            numeri_estratti.append(risultato["numero_estratto"])

        # 3. Verifiche
        self.assertEqual(partita.tabellone.get_conteggio_estratti(), 5)
        self.assertEqual(len(numeri_estratti), 5)
        # Numeri devono essere univoci (non ripetuti)
        self.assertEqual(len(set(numeri_estratti)), 5)

    # =========================================================================
    # SEZIONE 4: Test stato_partita (4 test)
    # =========================================================================

    def test_stato_partita_successo_struttura(self) -> None:
        """
        Verifica stato_partita ritorna dict con chiavi essenziali.
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)

        stato = self.comandi.stato_partita(partita)

        self.assertIsInstance(stato, dict)
        self.assertIn("stato_partita", stato)
        self.assertIn("numeri_estratti", stato)
        self.assertIn("giocatori", stato)
        self.assertIn("premi_gia_assegnati", stato)

    def test_stato_partita_parametro_invalido(self) -> None:
        """
        Verifica che parametro non-Partita ritorna None.
        """
        stato = self.comandi.stato_partita("non una partita")
        self.assertIsNone(stato)

    def test_stato_partita_coerenza_numeri_estratti(self) -> None:
        """
        Verifica coerenza: len(numeri_estratti) == conteggio tabellone.
        """
        # 1. Prepara
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)

        # 2. Esegui 3 turni
        for _ in range(3):
            self.comandi.esegui_turno(partita)

        # 3. Verifica stato
        stato = self.comandi.stato_partita(partita)
        self.assertEqual(len(stato["numeri_estratti"]), 3)
        self.assertEqual(len(stato["numeri_estratti"]), partita.tabellone.get_conteggio_estratti())

    def test_stato_partita_giocatori_validi(self) -> None:
        """
        Verifica lista giocatori è valida e contiene i nomi.
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 2)

        stato = self.comandi.stato_partita(partita)
        giocatori = stato["giocatori"]

        self.assertEqual(len(giocatori), 3)  # 1 umano + 2 bot
        self.assertEqual(giocatori[0]["nome"], "Mario")
        self.assertTrue(giocatori[1]["nome"].startswith("Bot"))

    # =========================================================================
    # SEZIONE 5: Test ha_tombola (4 test)
    # =========================================================================

    def test_ha_tombola_false_partita_nuova(self) -> None:
        """
        Verifica False su partita appena creata (nessuna tombola).
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)

        risultato = self.comandi.ha_tombola(partita)

        self.assertFalse(risultato)

    def test_ha_tombola_false_dopo_turni_iniziali(self) -> None:
        """
        Verifica False dopo pochi turni (improbabile tombola con 5 numeri).
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)

        for _ in range(5):
            self.comandi.esegui_turno(partita)

        risultato = self.comandi.ha_tombola(partita)
        self.assertFalse(risultato)

    def test_ha_tombola_parametro_invalido(self) -> None:
        """
        Verifica che parametro non-Partita ritorna False.
        """
        risultato = self.comandi.ha_tombola("non una partita")
        self.assertFalse(risultato)

    def test_ha_tombola_coerenza_con_partita_has_tombola(self) -> None:
        """
        Verifica risultato coincide con partita.has_tombola().
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)

        for _ in range(3):
            self.comandi.esegui_turno(partita)

        comandi_result = self.comandi.ha_tombola(partita)
        partita_result = partita.has_tombola()

        self.assertEqual(comandi_result, partita_result)

    # =========================================================================
    # SEZIONE 6: Test is_terminata (4 test)
    # =========================================================================

    def test_is_terminata_false_non_iniziata(self) -> None:
        """
        Verifica False su partita non_iniziata.
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)

        risultato = self.comandi.is_terminata(partita)

        self.assertFalse(risultato)

    def test_is_terminata_false_in_corso(self) -> None:
        """
        Verifica False su partita in_corso (dopo avvio).
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)

        risultato = self.comandi.is_terminata(partita)

        self.assertFalse(risultato)

    def test_is_terminata_true_dopo_terminazione(self) -> None:
        """
        Verifica True dopo terminazione forzata.
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)
        self.comandi.termina_partita(partita)

        risultato = self.comandi.is_terminata(partita)

        self.assertTrue(risultato)

    def test_is_terminata_parametro_invalido(self) -> None:
        """
        Verifica che parametro non-Partita ritorna False.
        """
        risultato = self.comandi.is_terminata("non una partita")
        self.assertFalse(risultato)

    # =========================================================================
    # SEZIONE 7: Test termina_partita (3 test)
    # =========================================================================

    def test_termina_partita_successo(self) -> None:
        """
        Verifica terminazione riuscita: stato diventa "terminata".
        """
        # 1. Prepara
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)
        self.assertEqual(partita.get_stato_partita(), "in_corso")

        # 2. Esegui terminazione
        risultato = self.comandi.termina_partita(partita)

        # 3. Verifiche
        self.assertTrue(risultato)
        self.assertEqual(partita.get_stato_partita(), "terminata")

    def test_termina_partita_parametro_invalido(self) -> None:
        """
        Verifica che parametro non-Partita ritorna False.
        """
        risultato = self.comandi.termina_partita("non una partita")
        self.assertFalse(risultato)

    def test_termina_partita_coerenza_is_terminata(self) -> None:
        """
        Verifica che dopo terminazione is_terminata() ritorna True.
        """
        partita = self.comandi.crea_nuova_partita("Mario", 1, 1)
        self.comandi.avvia_partita(partita)
        self.comandi.termina_partita(partita)

        self.assertTrue(self.comandi.is_terminata(partita))


if __name__ == "__main__":
    unittest.main()
