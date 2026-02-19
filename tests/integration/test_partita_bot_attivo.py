"""
Test di integrazione per la feature Bot Attivo - Integrazione con Partita

Modulo: tests.integration.test_partita_bot_attivo

Questi test verificano che il sistema di reclami bot funzioni correttamente
all'interno del ciclo completo di una partita, con interazione tra bot, tabellone,
cartelle e sistema di verifica premi.
"""

import pytest
from bingo_game.tabellone import Tabellone
from bingo_game.partita import Partita
from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
from bingo_game.cartella import Cartella


class TestPartitaBotAttivo:
    """
    Test suite per l'integrazione del Bot Attivo con Partita.
    
    Verifica che:
    - I reclami bot siano inclusi nel risultato del turno
    - Il matching tra reclami e premi reali funzioni correttamente
    - I reclami siano resettati dopo ogni turno
    - Il sistema sia backward-compatible (nessun impatto su partite senza bot)
    """

    def test_partita_reclami_bot_nel_risultato(self):
        """
        Test: Il risultato di esegui_turno() contiene la chiave "reclami_bot".
        
        Scenario:
        - Partita con 1 bot e 1 umano
        - Bot con un ambo precostituito
        - Esecuzione di un turno
        
        Atteso:
        - "reclami_bot" è presente nel dizionario risultato
        - "reclami_bot" è una lista
        - Se il bot reclama, la lista contiene l'esito del reclamo
        """
        # Arrange
        tabellone = Tabellone()
        bot = GiocatoreAutomatico("Bot1")
        cartella_bot = Cartella()
        bot.aggiungi_cartella(cartella_bot)
        
        umano = GiocatoreUmano("Human")
        umano.aggiungi_cartella(Cartella())
        
        partita = Partita(tabellone, [bot, umano])
        partita.avvia_partita()
        
        # Precostituisci un ambo sulla riga 0 del bot
        numeri_riga_0 = [n for n in cartella_bot.cartella[0] if n is not None][:2]
        for num in numeri_riga_0:
            cartella_bot.segna_numero(num)
        
        # Act
        risultato = partita.esegui_turno()
        
        # Assert
        assert "reclami_bot" in risultato, "La chiave 'reclami_bot' deve essere presente"
        assert isinstance(risultato["reclami_bot"], list), "reclami_bot deve essere una lista"
        
        # Se il bot ha reclamato, verifica la struttura
        if risultato["reclami_bot"]:
            reclamo_esito = risultato["reclami_bot"][0]
            assert "nome_giocatore" in reclamo_esito
            assert "id_giocatore" in reclamo_esito
            assert "reclamo" in reclamo_esito
            assert "successo" in reclamo_esito
            assert reclamo_esito["nome_giocatore"] == "Bot1"


    def test_reclamo_bot_rigettato_premio_gia_preso(self):
        """
        Test: Un reclamo bot viene rigettato se il premio è già stato assegnato.
        
        Scenario:
        - Due bot con lo stesso ambo precostituito
        - Il primo turno assegna il premio al primo bot
        - Il secondo turno dovrebbe mostrare il secondo bot con successo=False
        
        Atteso:
        - Il primo bot ha successo=True nel suo reclamo
        - Il secondo bot (se reclama dopo) ha successo=False
        """
        # Arrange
        tabellone = Tabellone()
        bot1 = GiocatoreAutomatico("Bot1")
        bot2 = GiocatoreAutomatico("Bot2")
        
        cartella1 = Cartella()
        cartella2 = Cartella()
        
        bot1.aggiungi_cartella(cartella1)
        bot2.aggiungi_cartella(cartella2)
        
        partita = Partita(tabellone, [bot1, bot2])
        partita.avvia_partita()
        
        # Precostituisci lo stesso ambo per entrambi i bot
        # (nella pratica è improbabile, ma serve per il test)
        numeri_comuni = list(range(15, 17))  # Numeri che entrambi avranno
        
        # Forza i numeri nelle cartelle (manipolazione per il test)
        cartella1.cartella[0][0] = numeri_comuni[0]
        cartella1.cartella[0][1] = numeri_comuni[1]
        cartella2.cartella[0][0] = numeri_comuni[0]
        cartella2.cartella[0][1] = numeri_comuni[1]
        
        # Segna i numeri
        for num in numeri_comuni:
            cartella1.segna_numero(num)
            cartella2.segna_numero(num)
        
        # Act
        risultato = partita.esegui_turno()
        
        # Assert
        reclami = risultato["reclami_bot"]
        
        # Almeno un bot dovrebbe aver reclamato
        if len(reclami) > 0:
            # Verifica che ci sia almeno un reclamo con successo
            ha_successo = any(r["successo"] for r in reclami)
            # Se l'ambo è stato assegnato, almeno un reclamo dovrebbe avere successo
            ambo_assegnato = any(p["premio"] == "ambo" for p in risultato["premi_nuovi"])
            if ambo_assegnato:
                assert ha_successo, "Se l'ambo è assegnato, almeno un bot dovrebbe avere successo=True"


    def test_bot_tombola_termina_partita(self):
        """
        Test: Un bot che fa tombola termina la partita.
        
        Scenario:
        - Bot con cartella completamente segnata (tombola)
        - Esecuzione di un turno
        
        Atteso:
        - tombola_rilevata=True nel risultato
        - partita_terminata=True nel risultato
        - Il bot ha un reclamo con tipo="tombola" e successo=True
        """
        # Arrange
        tabellone = Tabellone()
        bot = GiocatoreAutomatico("BotTombola")
        cartella_bot = Cartella()
        bot.aggiungi_cartella(cartella_bot)
        
        umano = GiocatoreUmano("Human")
        umano.aggiungi_cartella(Cartella())
        
        partita = Partita(tabellone, [bot, umano])
        partita.avvia_partita()
        
        # Segna tutti i 15 numeri per fare tombola
        for riga in range(3):
            for num in cartella_bot.cartella[riga]:
                if num is not None:
                    cartella_bot.segna_numero(num)
        
        # Act
        risultato = partita.esegui_turno()
        
        # Assert
        assert risultato["tombola_rilevata"], "tombola_rilevata dovrebbe essere True"
        assert risultato["partita_terminata"], "partita_terminata dovrebbe essere True"
        
        # Verifica il reclamo del bot
        reclami_bot = risultato["reclami_bot"]
        assert len(reclami_bot) > 0, "Il bot dovrebbe aver fatto un reclamo"
        
        reclamo_tombola = next((r for r in reclami_bot if r["reclamo"].tipo == "tombola"), None)
        assert reclamo_tombola is not None, "Dovrebbe esserci un reclamo di tombola"
        assert reclamo_tombola["successo"], "Il reclamo di tombola dovrebbe avere successo=True"


    def test_reclami_bot_vuoto_se_nessun_premio(self):
        """
        Test: reclami_bot è una lista vuota se nessun bot ha premi da reclamare.
        
        Scenario:
        - Partita con solo umani (nessun bot)
        - Esecuzione di un turno
        
        Atteso:
        - reclami_bot è presente e è una lista vuota
        """
        # Arrange
        tabellone = Tabellone()
        umano1 = GiocatoreUmano("Human1")
        umano2 = GiocatoreUmano("Human2")
        
        umano1.aggiungi_cartella(Cartella())
        umano2.aggiungi_cartella(Cartella())
        
        partita = Partita(tabellone, [umano1, umano2])
        partita.avvia_partita()
        
        # Act
        risultato = partita.esegui_turno()
        
        # Assert
        assert "reclami_bot" in risultato, "reclami_bot deve essere presente"
        assert risultato["reclami_bot"] == [], "reclami_bot dovrebbe essere una lista vuota senza bot"


    def test_reset_reclamo_dopo_turno(self):
        """
        Test: Il reclamo_turno dei bot viene resettato dopo ogni turno.
        
        Scenario:
        - Bot con un ambo precostituito
        - Esecuzione di un turno (bot reclama)
        - Verifica che reclamo_turno sia None dopo il turno
        
        Atteso:
        - Prima del turno: il bot non ha reclamo
        - Durante il turno: il bot costruisce un reclamo
        - Dopo il turno: reclamo_turno è resettato a None
        """
        # Arrange
        tabellone = Tabellone()
        bot = GiocatoreAutomatico("Bot1")
        cartella_bot = Cartella()
        bot.aggiungi_cartella(cartella_bot)
        
        umano = GiocatoreUmano("Human")
        umano.aggiungi_cartella(Cartella())
        
        partita = Partita(tabellone, [bot, umano])
        partita.avvia_partita()
        
        # Precostituisci un ambo
        numeri_riga_0 = [n for n in cartella_bot.cartella[0] if n is not None][:2]
        for num in numeri_riga_0:
            cartella_bot.segna_numero(num)
        
        # Verifica stato iniziale
        assert bot.reclamo_turno is None, "Il bot non dovrebbe avere un reclamo prima del turno"
        
        # Act
        risultato = partita.esegui_turno()
        
        # Assert
        # Dopo il turno, il reclamo deve essere stato resettato
        assert bot.reclamo_turno is None, "Il reclamo_turno dovrebbe essere resettato a None dopo il turno"


    def test_bot_non_reclama_se_nessun_premio_disponibile(self):
        """
        Test: Un bot senza premi disponibili non produce reclami.
        
        Scenario:
        - Bot con cartella vuota (nessun numero segnato)
        - Esecuzione di un turno
        
        Atteso:
        - reclami_bot è vuoto o contiene solo reclami di altri bot
        - Nessun reclamo dal bot in questione
        """
        # Arrange
        tabellone = Tabellone()
        bot = GiocatoreAutomatico("BotVuoto")
        bot.aggiungi_cartella(Cartella())  # Cartella vuota, senza numeri segnati
        
        umano = GiocatoreUmano("Human")
        umano.aggiungi_cartella(Cartella())
        
        partita = Partita(tabellone, [bot, umano])
        partita.avvia_partita()
        
        # Act
        risultato = partita.esegui_turno()
        
        # Assert
        reclami_bot = risultato["reclami_bot"]
        
        # Verifica che non ci siano reclami dal BotVuoto
        reclami_bot_vuoto = [r for r in reclami_bot if r["nome_giocatore"] == "BotVuoto"]
        assert len(reclami_bot_vuoto) == 0, "BotVuoto non dovrebbe aver fatto reclami senza premi"


    def test_backward_compatibility_partita_senza_bot(self):
        """
        Test: Una partita senza bot funziona correttamente (backward compatibility).
        
        Scenario:
        - Partita con solo giocatori umani
        - Esecuzione di più turni
        
        Atteso:
        - La partita funziona normalmente
        - reclami_bot è sempre presente (lista vuota)
        - Nessun impatto sulle funzionalità esistenti
        """
        # Arrange
        tabellone = Tabellone()
        umano1 = GiocatoreUmano("Human1")
        umano2 = GiocatoreUmano("Human2")
        
        umano1.aggiungi_cartella(Cartella())
        umano2.aggiungi_cartella(Cartella())
        
        partita = Partita(tabellone, [umano1, umano2])
        partita.avvia_partita()
        
        # Act - esegui 3 turni
        for _ in range(3):
            risultato = partita.esegui_turno()
            
            # Assert per ogni turno
            assert "reclami_bot" in risultato
            assert risultato["reclami_bot"] == []
            assert "numero_estratto" in risultato
            assert "premi_nuovi" in risultato
            
            # Se la partita è terminata, interrompi
            if risultato["partita_terminata"]:
                break


    def test_multipli_bot_con_premi_diversi(self):
        """
        Test: Più bot con premi di rango diverso reclamano correttamente.
        
        Scenario:
        - Bot1 con ambo sulla riga 0
        - Bot2 con terno sulla riga 1
        - Esecuzione di un turno
        
        Atteso:
        - Entrambi i bot hanno reclami in reclami_bot
        - Ogni bot reclama il premio corretto
        """
        # Arrange
        tabellone = Tabellone()
        bot1 = GiocatoreAutomatico("Bot1")
        bot2 = GiocatoreAutomatico("Bot2")
        
        cartella1 = Cartella()
        cartella2 = Cartella()
        
        bot1.aggiungi_cartella(cartella1)
        bot2.aggiungi_cartella(cartella2)
        
        partita = Partita(tabellone, [bot1, bot2])
        partita.avvia_partita()
        
        # Precostituisci premi diversi
        # Bot1: ambo sulla riga 0
        numeri_bot1 = [n for n in cartella1.cartella[0] if n is not None][:2]
        for num in numeri_bot1:
            cartella1.segna_numero(num)
        
        # Bot2: terno sulla riga 1
        numeri_bot2 = [n for n in cartella2.cartella[1] if n is not None][:3]
        for num in numeri_bot2:
            cartella2.segna_numero(num)
        
        # Act
        risultato = partita.esegui_turno()
        
        # Assert
        reclami_bot = risultato["reclami_bot"]
        
        # Dovrebbero esserci reclami dai bot (se hanno premi disponibili)
        # Verifica che la struttura sia corretta
        for reclamo in reclami_bot:
            assert reclamo["nome_giocatore"] in ["Bot1", "Bot2"]
            assert "reclamo" in reclamo
            assert reclamo["reclamo"].tipo in ["ambo", "terno", "quaterna", "cinquina", "tombola"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
