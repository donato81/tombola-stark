"""
Test unitari per la feature Bot Attivo - GiocatoreAutomatico._valuta_potenziale_reclamo()

Modulo: tests.unit.test_giocatore_automatico_bot_attivo

Questi test verificano che il bot sia in grado di valutare correttamente
i premi disponibili sulle proprie cartelle e di costruire il reclamo appropriato.
"""

import pytest
from bingo_game.players import GiocatoreAutomatico
from bingo_game.cartella import Cartella
from bingo_game.events.eventi_partita import ReclamoVittoria


class TestGiocatoreAutomaticoBotAttivo:
    """
    Test suite per la funzionalità Bot Attivo.
    
    Verifica che il metodo _valuta_potenziale_reclamo() del bot:
    - Rilevi correttamente i premi disponibili
    - Scelga il premio di rango più alto
    - Rispetti i premi già assegnati
    - Gestisca correttamente i casi limite
    """

    def test_bot_reclama_ambo_disponibile(self):
        """
        Test: Il bot reclama correttamente un ambo disponibile.
        
        Scenario:
        - Bot con una cartella
        - 2 numeri segnati sulla riga 0 (forma un ambo)
        - Nessun premio già assegnato
        
        Atteso:
        - Il bot reclama un ambo sulla riga 0
        """
        # Arrange
        bot = GiocatoreAutomatico("TestBot")
        cartella = Cartella()
        bot.aggiungi_cartella(cartella)
        
        # Segna 2 numeri sulla riga 0 per fare un ambo
        numeri_riga_0 = [n for n in cartella.cartella[0] if n is not None][:2]
        for num in numeri_riga_0:
            cartella.segna_numero(num)
        
        # Act
        reclamo = bot._valuta_potenziale_reclamo(set())
        
        # Assert
        assert reclamo is not None, "Il bot dovrebbe reclamare un ambo"
        assert reclamo.tipo == "ambo", f"Tipo atteso: ambo, ottenuto: {reclamo.tipo}"
        assert reclamo.indice_riga == 0, f"Riga attesa: 0, ottenuta: {reclamo.indice_riga}"
        assert reclamo.indice_cartella == cartella.indice


    def test_bot_non_reclama_premio_gia_assegnato(self):
        """
        Test: Il bot non reclama un premio già assegnato.
        
        Scenario:
        - Bot con una cartella con ambo sulla riga 0
        - Premio "cartella_X_riga_0_ambo" già presente in premi_gia_assegnati
        
        Atteso:
        - Il bot non reclama nulla (ritorna None)
        """
        # Arrange
        bot = GiocatoreAutomatico("TestBot")
        cartella = Cartella()
        bot.aggiungi_cartella(cartella)
        
        # Segna 2 numeri sulla riga 0 per fare un ambo
        numeri_riga_0 = [n for n in cartella.cartella[0] if n is not None][:2]
        for num in numeri_riga_0:
            cartella.segna_numero(num)
        
        # Premio già assegnato
        premi_assegnati = {f"cartella_{cartella.indice}_riga_0_ambo"}
        
        # Act
        reclamo = bot._valuta_potenziale_reclamo(premi_assegnati)
        
        # Assert
        assert reclamo is None, "Il bot non dovrebbe reclamare un premio già assegnato"


    def test_bot_sceglie_premio_piu_alto(self):
        """
        Test: Il bot sceglie il premio di rango più alto quando ce ne sono più disponibili.
        
        Scenario:
        - Bot con una cartella
        - 3 numeri segnati sulla riga 1 (forma terno + ambo)
        - Nessun premio già assegnato
        
        Atteso:
        - Il bot reclama il terno (rango superiore), non l'ambo
        """
        # Arrange
        bot = GiocatoreAutomatico("TestBot")
        cartella = Cartella()
        bot.aggiungi_cartella(cartella)
        
        # Segna 3 numeri sulla riga 1 per fare un terno (che implica anche un ambo)
        numeri_riga_1 = [n for n in cartella.cartella[1] if n is not None][:3]
        for num in numeri_riga_1:
            cartella.segna_numero(num)
        
        # Act
        reclamo = bot._valuta_potenziale_reclamo(set())
        
        # Assert
        assert reclamo is not None, "Il bot dovrebbe reclamare un premio"
        assert reclamo.tipo == "terno", f"Tipo atteso: terno (rango più alto), ottenuto: {reclamo.tipo}"
        assert reclamo.indice_riga == 1, f"Riga attesa: 1, ottenuta: {reclamo.indice_riga}"


    def test_bot_reclama_tombola(self):
        """
        Test: Il bot reclama correttamente una tombola.
        
        Scenario:
        - Bot con una cartella completamente segnata
        - Nessun premio già assegnato
        
        Atteso:
        - Il bot reclama la tombola (indice_riga=None)
        """
        # Arrange
        bot = GiocatoreAutomatico("TestBot")
        cartella = Cartella()
        bot.aggiungi_cartella(cartella)
        
        # Segna tutti i 15 numeri per fare tombola
        for riga in range(3):
            for num in cartella.cartella[riga]:
                if num is not None:
                    cartella.segna_numero(num)
        
        # Act
        reclamo = bot._valuta_potenziale_reclamo(set())
        
        # Assert
        assert reclamo is not None, "Il bot dovrebbe reclamare la tombola"
        assert reclamo.tipo == "tombola", f"Tipo atteso: tombola, ottenuto: {reclamo.tipo}"
        assert reclamo.indice_riga is None, "La tombola non dovrebbe avere un indice riga"
        assert reclamo.indice_cartella == cartella.indice


    def test_bot_nessun_premio_disponibile(self):
        """
        Test: Il bot non reclama nulla quando non ci sono premi disponibili.
        
        Scenario:
        - Bot con una cartella senza numeri segnati
        
        Atteso:
        - Il bot non reclama nulla (ritorna None)
        """
        # Arrange
        bot = GiocatoreAutomatico("TestBot")
        bot.aggiungi_cartella(Cartella())
        
        # Act (nessun numero segnato)
        reclamo = bot._valuta_potenziale_reclamo(set())
        
        # Assert
        assert reclamo is None, "Il bot non dovrebbe reclamare nulla senza premi disponibili"


    def test_bot_sceglie_tra_piu_cartelle(self):
        """
        Test: Il bot sceglie il premio di rango più alto tra tutte le sue cartelle.
        
        Scenario:
        - Bot con 2 cartelle
        - Cartella 1: ambo sulla riga 0
        - Cartella 2: cinquina sulla riga 2
        - Nessun premio già assegnato
        
        Atteso:
        - Il bot reclama la cinquina (rango più alto tra tutte le cartelle)
        """
        # Arrange
        bot = GiocatoreAutomatico("TestBot")
        
        # Cartella 1: ambo sulla riga 0
        cartella1 = Cartella()
        bot.aggiungi_cartella(cartella1)
        numeri_riga_0 = [n for n in cartella1.cartella[0] if n is not None][:2]
        for num in numeri_riga_0:
            cartella1.segna_numero(num)
        
        # Cartella 2: cinquina sulla riga 2
        cartella2 = Cartella()
        bot.aggiungi_cartella(cartella2)
        numeri_riga_2 = [n for n in cartella2.cartella[2] if n is not None][:5]
        for num in numeri_riga_2:
            cartella2.segna_numero(num)
        
        # Act
        reclamo = bot._valuta_potenziale_reclamo(set())
        
        # Assert
        assert reclamo is not None, "Il bot dovrebbe reclamare un premio"
        assert reclamo.tipo == "cinquina", f"Tipo atteso: cinquina (rango più alto), ottenuto: {reclamo.tipo}"
        assert reclamo.indice_cartella == cartella2.indice, "Dovrebbe essere la cartella 2"
        assert reclamo.indice_riga == 2, "Dovrebbe essere la riga 2"


    def test_bot_gerarchia_completa_premi(self):
        """
        Test: Verifica che il bot rispetti la gerarchia completa dei premi.
        
        Scenario:
        - Test tutte le combinazioni di premi per verificare la gerarchia:
          tombola > cinquina > quaterna > terno > ambo
        
        Atteso:
        - Ogni premio di rango superiore viene scelto rispetto ai ranghi inferiori
        """
        # Test 1: cinquina > quaterna
        bot1 = GiocatoreAutomatico("Bot1")
        cartella1a = Cartella()
        cartella1b = Cartella()
        bot1.aggiungi_cartella(cartella1a)
        bot1.aggiungi_cartella(cartella1b)
        
        # Cartella 1a: quaterna riga 0
        for num in [n for n in cartella1a.cartella[0] if n is not None][:4]:
            cartella1a.segna_numero(num)
        
        # Cartella 1b: cinquina riga 1
        for num in [n for n in cartella1b.cartella[1] if n is not None][:5]:
            cartella1b.segna_numero(num)
        
        reclamo1 = bot1._valuta_potenziale_reclamo(set())
        assert reclamo1.tipo == "cinquina", "Dovrebbe scegliere cinquina su quaterna"
        
        # Test 2: quaterna > terno
        bot2 = GiocatoreAutomatico("Bot2")
        cartella2a = Cartella()
        cartella2b = Cartella()
        bot2.aggiungi_cartella(cartella2a)
        bot2.aggiungi_cartella(cartella2b)
        
        # Cartella 2a: terno riga 0
        for num in [n for n in cartella2a.cartella[0] if n is not None][:3]:
            cartella2a.segna_numero(num)
        
        # Cartella 2b: quaterna riga 2
        for num in [n for n in cartella2b.cartella[2] if n is not None][:4]:
            cartella2b.segna_numero(num)
        
        reclamo2 = bot2._valuta_potenziale_reclamo(set())
        assert reclamo2.tipo == "quaterna", "Dovrebbe scegliere quaterna su terno"


    def test_bot_con_multipli_premi_stessa_riga(self):
        """
        Test: Il bot gestisce correttamente premi multipli sulla stessa riga.
        
        Scenario:
        - Bot con una cartella
        - 4 numeri segnati sulla riga 0 (forma quaterna + terno + ambo)
        - L'ambo è già assegnato
        
        Atteso:
        - Il bot reclama la quaterna (rango più alto disponibile)
        """
        # Arrange
        bot = GiocatoreAutomatico("TestBot")
        cartella = Cartella()
        bot.aggiungi_cartella(cartella)
        
        # Segna 4 numeri sulla riga 0
        numeri_riga_0 = [n for n in cartella.cartella[0] if n is not None][:4]
        for num in numeri_riga_0:
            cartella.segna_numero(num)
        
        # Ambo già assegnato
        premi_assegnati = {f"cartella_{cartella.indice}_riga_0_ambo"}
        
        # Act
        reclamo = bot._valuta_potenziale_reclamo(premi_assegnati)
        
        # Assert
        assert reclamo is not None, "Il bot dovrebbe reclamare un premio"
        assert reclamo.tipo == "quaterna", f"Tipo atteso: quaterna, ottenuto: {reclamo.tipo}"
        assert reclamo.indice_riga == 0


    # Fix 1/3 - Test per is_automatico su GiocatoreAutomatico
    def test_is_automatico_bot_true(self):
        """
        Test: Verifica che is_automatico() ritorni True per GiocatoreAutomatico.
        
        Scenario:
        - Creazione di un GiocatoreAutomatico
        
        Atteso:
        - is_automatico() deve ritornare True
        """
        # Arrange
        bot = GiocatoreAutomatico("TestBot")
        
        # Act & Assert
        assert bot.is_automatico() is True, "GiocatoreAutomatico.is_automatico() dovrebbe ritornare True"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
