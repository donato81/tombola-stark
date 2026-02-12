import unittest
from unittest.mock import Mock, patch
from bingo_game.cartella import Cartella
from bingo_game.players.giocatore_umano import GiocatoreUmano

class TestGiocatoreUmano(unittest.TestCase):
    """
    Suite di test per la classe GiocatoreUmano.
    Verifica le funzionalità specifiche dell'interazione umana,
    come la gestione del focus sulle cartelle.
    """

    def setUp(self):
        """
        Preparazione dell'ambiente di test.
        Viene eseguito prima di ogni singolo test.
        """
        # Creiamo un giocatore umano di base
        self.giocatore = GiocatoreUmano("Mario", id_giocatore=1)
        
        # Creiamo alcune cartelle fittizie per i test
        # (Non serve che siano cartelle valide generate, bastano oggetti Cartella)
        self.cartella1 = Cartella()
        self.cartella2 = Cartella()
        self.cartella3 = Cartella()

    # ---------------------------------------------------------------------
    # TEST METODO: imposta_focus_cartella
    # ---------------------------------------------------------------------

    def test_imposta_focus_valido(self):
        """
        Verifica che il focus venga impostato correttamente con un input valido.
        
        Scenario:
        - Giocatore ha 3 cartelle.
        - Utente chiede di selezionare la cartella 2.
        
        Risultato atteso:
        - L'indice interno di focus diventa 1 (2 - 1).
        - Il messaggio di ritorno conferma l'avvenuto cambio focus.
        """
        # Aggiungiamo 3 cartelle al giocatore
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.aggiungi_cartella(self.cartella2)
        self.giocatore.aggiungi_cartella(self.cartella3)

        # Azione: Imposta focus sulla cartella 2
        risultato = self.giocatore.imposta_focus_cartella(2)

        # Verifica: L'indice interno deve essere 1 (base-0)
        self.assertEqual(
            self.giocatore._indice_cartella_focus, 
            1, 
            "L'indice del focus dovrebbe essere 1 per la cartella numero 2."
        )

        # Verifica: Il messaggio deve confermare l'azione
        self.assertEqual(
            risultato, 
            "Focus impostato sulla cartella 2.",
            "Il messaggio di conferma non è corretto."
        )

    def test_imposta_focus_numero_troppo_alto(self):
        """
        Verifica che il metodo rifiuti un numero cartella superiore al posseduto.
        
        Scenario:
        - Giocatore ha 3 cartelle.
        - Utente chiede di selezionare la cartella 4 (o 7, che è oltre il max 6).
        
        Risultato atteso:
        - L'indice di focus NON cambia (resta quello iniziale, es. 0).
        - Il messaggio di ritorno segnala l'errore.
        """
        # Aggiungiamo 3 cartelle
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.aggiungi_cartella(self.cartella2)
        self.giocatore.aggiungi_cartella(self.cartella3)
        
        # Salviamo il focus iniziale (che dovrebbe essere 0 di default)
        focus_iniziale = self.giocatore._indice_cartella_focus

        # Azione: Tentativo errato (cartella 4 su 3 disponibili)
        risultato = self.giocatore.imposta_focus_cartella(4)

        # Verifica: Il focus non deve essere cambiato
        self.assertEqual(
            self.giocatore._indice_cartella_focus, 
            focus_iniziale,
            "Il focus non dovrebbe cambiare se l'input è fuori range."
        )

        # Verifica: Il messaggio deve contenere un errore
        self.assertIn(
            "Errore", 
            risultato, 
            "Dovrebbe essere ritornato un messaggio di errore."
        )

    def test_imposta_focus_numero_troppo_basso(self):
        """
        Verifica che il metodo rifiuti numeri < 1 (es. 0 o negativi).
        
        Scenario:
        - Giocatore ha cartelle.
        - Utente inserisce 0 o -1.
        
        Risultato atteso:
        - Rifiuto con messaggio di errore.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        
        # Azione: Tentativo con 0
        risultato = self.giocatore.imposta_focus_cartella(0)

        # Verifica: Messaggio di errore
        self.assertIn("Errore", risultato)

    def test_imposta_focus_senza_cartelle(self):
        """
        Verifica il comportamento quando il giocatore non ha ancora cartelle.
        
        Scenario:
        - Giocatore appena creato, nessuna cartella assegnata.
        - Utente prova a impostare focus su 1.
        
        Risultato atteso:
        - Rifiuto specifico ("Non hai ancora assegnato nessuna cartella").
        """
        # Nota: non aggiungiamo cartelle al giocatore

        # Azione
        risultato = self.giocatore.imposta_focus_cartella(1)

        # Verifica
        self.assertEqual(
            risultato,
            "Errore: Non hai ancora assegnato nessuna cartella.",
            "Dovrebbe segnalare che non ci sono cartelle disponibili."
        )


    # ---------------------------------------------------------------------
    # TEST METODO: visualizza_cartella_corrente_semplice
    # ---------------------------------------------------------------------

    def test_visualizza_cartella_corrente_valida(self):
        """
        Verifica che il metodo restituisca correttamente la stringa della cartella
        quando il focus è impostato su una cartella valida.
        
        Scenario:
        - Giocatore ha 2 cartelle.
        - Focus impostato sulla cartella 1 (indice 0).
        
        Risultato atteso:
        - Il metodo ritorna una stringa (non None).
        - La stringa ritornata corrisponde alla stampa della cartella puntata.
        """
        # Aggiungiamo 2 cartelle al giocatore
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.aggiungi_cartella(self.cartella2)

        # Impostiamo manualmente il focus sulla prima cartella (indice 0)
        # Nota: usiamo il metodo pubblico per simulare l'azione reale
        self.giocatore.imposta_focus_cartella(1)

        # Azione: Richiediamo la visualizzazione
        risultato = self.giocatore.visualizza_cartella_corrente_semplice()

        # Verifica: Il risultato non deve essere None
        self.assertIsNotNone(
            risultato,
            "Il metodo dovrebbe ritornare una stringa se il focus è valido."
        )

        # Verifica: Il risultato deve essere una stringa
        self.assertIsInstance(
            risultato, 
            str,
            "Il tipo di ritorno deve essere una stringa."
        )

        # Verifica di coerenza: La stringa deve essere quella della cartella 1
        # (Confrontiamo con la chiamata diretta alla cartella)
        atteso = self.cartella1.stampa_cartella()
        self.assertEqual(
            risultato, 
            atteso,
            "La visualizzazione ritornata non corrisponde alla cartella in focus."
        )

    def test_visualizza_cartella_corrente_nessun_focus(self):
        """
        Verifica che il metodo ritorni None se il giocatore ha cartelle
        ma non ne ha selezionata nessuna (focus = None).
        
        Scenario:
        - Giocatore con cartelle assegnate.
        - Nessun focus impostato (stato iniziale o reset).
        
        Risultato atteso:
        - Ritorna None (nessuna visualizzazione disponibile).
        """
        # Aggiungiamo una cartella
        self.giocatore.aggiungi_cartella(self.cartella1)

        # Assicuriamoci che il focus sia None (simuliamo stato iniziale)
        self.giocatore._indice_cartella_focus = None

        # Azione
        risultato = self.giocatore.visualizza_cartella_corrente_semplice()

        # Verifica
        self.assertIsNone(
            risultato,
            "Se non c'è focus, il metodo deve ritornare None."
        )

    def test_visualizza_cartella_corrente_senza_cartelle(self):
        """
        Verifica che il metodo gestisca correttamente il caso di un giocatore
        appena creato senza cartelle assegnate.
        
        Scenario:
        - Giocatore vuoto (0 cartelle).
        
        Risultato atteso:
        - Ritorna None senza errori.
        """
        # Nota: Non aggiungiamo cartelle al giocatore (lista vuota)

        # Azione
        risultato = self.giocatore.visualizza_cartella_corrente_semplice()

        # Verifica
        self.assertIsNone(
            risultato,
            "Se il giocatore non ha cartelle, il metodo deve ritornare None."
        )


    # ---------------------------------------------------------------------
    # TEST METODO: visualizza_cartella_corrente_avanzata
    # ---------------------------------------------------------------------

    def test_visualizza_cartella_corrente_avanzata_con_focus(self):
        """
        Verifica che il metodo restituisca la rappresentazione AVANZATA della cartella
        in focus, includendo indicatori di stato (asterischi) e riepilogo.
        
        Scenario:
        - Giocatore con 1 cartella.
        - Un numero viene segnato manualmente sulla cartella (simulazione gioco).
        - Focus impostato su quella cartella.
        
        Risultato atteso:
        - Ritorna una stringa (non None).
        - La stringa contiene l'asterisco '*' (indicatore numero segnato).
        - La stringa contiene il testo di riepilogo ("Totale segnati").
        """
        # Aggiungiamo una cartella al giocatore
        self.giocatore.aggiungi_cartella(self.cartella1)
        
        # Recuperiamo un numero presente nella cartella per segnarlo
        # (Sappiamo che cartella1 ha dei numeri, prendiamone uno a caso dalla prima riga)
        numeri_riga_0 = self.cartella1.get_numeri_riga(0)
        numero_da_segnare = numeri_riga_0[0]
        
        # Segniamo il numero sulla cartella
        self.cartella1.segna_numero(numero_da_segnare)
        
        # Impostiamo il focus
        self.giocatore.imposta_focus_cartella(1) # Indice 0 (Utente vede 1)

        # Azione: Richiediamo visualizzazione avanzata
        risultato = self.giocatore.visualizza_cartella_corrente_avanzata()

        # Verifica 1: Non deve essere None
        self.assertIsNotNone(
            risultato, 
            "Il metodo deve ritornare una stringa se il focus è valido."
        )

        # Verifica 2: Deve contenere l'asterisco per il numero segnato
        # Costruiamo la stringa attesa per quel numero (es. "*42")
        stringa_segnata = f"*{numero_da_segnare}"
        self.assertIn(
            stringa_segnata,
            risultato,
            f"La visualizzazione avanzata deve contenere l'indicatore di stato '{stringa_segnata}'."
        )

        # Verifica 3: Deve contenere il riepilogo statistico
        self.assertIn(
            "Totale segnati:",
            risultato,
            "La visualizzazione avanzata deve includere il riepilogo ('Totale segnati')."
        )

    def test_visualizza_cartella_corrente_avanzata_nessun_focus(self):
        """
        Verifica che il metodo ritorni None se non c'è focus attivo,
        anche se ci sono cartelle.
        
        Scenario:
        - Giocatore con cartelle.
        - Focus rimosso (None).
        
        Risultato atteso:
        - Ritorna None.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None # Rimuoviamo focus

        risultato = self.giocatore.visualizza_cartella_corrente_avanzata()

        self.assertIsNone(
            risultato,
            "Senza focus, il metodo deve ritornare None."
        )

    def test_visualizza_cartella_corrente_avanzata_senza_cartelle(self):
        """
        Verifica che il metodo ritorni None se il giocatore non ha cartelle.
        
        Scenario:
        - Giocatore appena inizializzato.
        
        Risultato atteso:
        - Ritorna None.
        """
        risultato = self.giocatore.visualizza_cartella_corrente_avanzata()

        self.assertIsNone(
            risultato,
            "Senza cartelle, il metodo deve ritornare None."
        )


    # ---------------------------------------------------------------------
    # TEST METODO: visualizza_tutte_cartelle_semplice
    # ---------------------------------------------------------------------

    def test_visualizza_tutte_cartelle_semplice_standard(self):
        """
        Verifica che il metodo restituisca correttamente la concatenazione delle stampe
        di tutte le cartelle possedute dal giocatore.
        
        Scenario:
        - Giocatore con 2 cartelle aggiunte.
        
        Risultato atteso:
        - Il risultato non è None.
        - Il risultato contiene le intestazioni per entrambe le cartelle ("Cartella 1", "Cartella 2").
        - Il risultato contiene parti delle stampe delle singole cartelle.
        """
        # Aggiungiamo 2 cartelle al giocatore
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.aggiungi_cartella(self.cartella2)

        # Azione
        risultato = self.giocatore.visualizza_tutte_cartelle_semplice()

        # Verifica 1: Risultato valido
        self.assertIsNotNone(
            risultato,
            "Il metodo deve ritornare una stringa se ci sono cartelle."
        )

        # Verifica 2: Presenza intestazioni numerate
        self.assertIn(
            "--- Cartella 1 ---",
            risultato,
            "Deve essere presente l'intestazione per la prima cartella."
        )
        self.assertIn(
            "--- Cartella 2 ---",
            risultato,
            "Deve essere presente l'intestazione per la seconda cartella."
        )

        # Verifica 3: Contenuto effettivo (verifichiamo che ci sia almeno un pezzo della stampa)
        # Prendiamo un numero dalla prima cartella e vediamo se c'è
        numero_test = self.cartella1.get_numeri_riga(0)[0]
        self.assertIn(
            str(numero_test),
            risultato,
            "I numeri delle cartelle devono essere presenti nella stampa concatenata."
        )

    def test_visualizza_tutte_cartelle_semplice_lista_vuota(self):
        """
        Verifica che il metodo restituisca None se il giocatore non possiede cartelle.
        
        Scenario:
        - Giocatore appena creato (0 cartelle).
        
        Risultato atteso:
        - Ritorna None.
        """
        # Nessuna cartella aggiunta

        # Azione
        risultato = self.giocatore.visualizza_tutte_cartelle_semplice()

        # Verifica
        self.assertIsNone(
            risultato,
            "Se non ci sono cartelle, il metodo deve ritornare None."
        )


    # ---------------------------------------------------------------------
    # TEST METODO: visualizza_tutte_cartelle_avanzata
    # ---------------------------------------------------------------------

    def test_visualizza_tutte_cartelle_avanzata_con_segni(self):
        """
        Verifica che il metodo restituisca la concatenazione delle stampe AVANZATE
        di tutte le cartelle, includendo marcatori di stato e riepiloghi.
        
        Scenario:
        - Giocatore con 2 cartelle.
        - Un numero viene segnato sulla prima cartella.
        - La seconda cartella rimane intonsa.
        
        Risultato atteso:
        - Il risultato non è None.
        - Sono presenti le intestazioni per entrambe le cartelle.
        - È presente l'asterisco (*) per il numero segnato nella cartella 1.
        - Sono presenti i riepiloghi ("Totale segnati") per entrambe.
        """
        # Aggiungiamo 2 cartelle
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.aggiungi_cartella(self.cartella2)
        
        # Segniamo un numero sulla cartella 1 per renderla diversa
        numeri_c1 = self.cartella1.get_numeri_riga(0)
        num_segnato = numeri_c1[0]
        self.cartella1.segna_numero(num_segnato)

        # Azione
        risultato = self.giocatore.visualizza_tutte_cartelle_avanzata()

        # Verifica 1: Risultato valido
        self.assertIsNotNone(
            risultato,
            "Il metodo deve ritornare una stringa se ci sono cartelle."
        )

        # Verifica 2: Intestazioni
        self.assertIn("--- Cartella 1 ---", risultato)
        self.assertIn("--- Cartella 2 ---", risultato)

        # Verifica 3: Contenuto avanzato (Asterisco)
        # Cerchiamo la stringa segnata (es. "*42")
        marker_atteso = f"*{num_segnato}"
        self.assertIn(
            marker_atteso,
            risultato,
            f"La stampa deve contenere l'indicatore di segnazione '{marker_atteso}'."
        )

        # Verifica 4: Riepiloghi
        # La stringa "Totale segnati:" deve apparire 2 volte (una per cartella)
        conteggio_riepiloghi = risultato.count("Totale segnati:")
        self.assertEqual(
            conteggio_riepiloghi,
            2,
            "Deve esserci un riepilogo statistico per ogni cartella presente."
        )

    def test_visualizza_tutte_cartelle_avanzata_lista_vuota(self):
        """
        Verifica che il metodo restituisca None se il giocatore non ha cartelle.
        
        Scenario:
        - Giocatore vuoto.
        
        Risultato atteso:
        - Ritorna None.
        """
        # Nessuna cartella aggiunta

        risultato = self.giocatore.visualizza_tutte_cartelle_avanzata()

        self.assertIsNone(
            risultato,
           "Senza cartelle, il metodo deve ritornare None."
        )


    # ---------------------------------------------------------------------
    # TEST METODI: sposta_focus_riga_su/giu (VERSIONE SEMPLICE)
    # ---------------------------------------------------------------------

    def test_sposta_focus_riga_su_semplice_cartella_mancante(self):
        """
        Verifica che sposta_focus_riga_su() gestisca correttamente l'assenza di cartella focus
        nella versione semplice (stampa_riga_semplice).
        
        Scenario:
        - Giocatore senza cartelle o senza focus impostato.
        
        Risultato atteso:
        - Ritorna messaggio "Non hai selezionato nessuna cartella".
        """
        # Scenario 1: Giocatore senza cartelle
        risultato1 = self.giocatore.sposta_focus_riga_su()
        self.assertEqual(
            risultato1,
            "Non hai selezionato nessuna cartella",
            "Senza cartelle deve ritornare messaggio appropriato."
        )

        # Scenario 2: Focus rimosso manualmente
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None
        risultato2 = self.giocatore.sposta_focus_riga_su()
        self.assertEqual(
            risultato2,
            "Non hai selezionato nessuna cartella",
            "Senza focus attivo deve ritornare messaggio appropriato."
        )

    def test_sposta_focus_riga_su_semplice_prima_riga(self):
        """
        Verifica che il metodo blocchi lo spostamento dalla prima riga (indice 0)
        nella versione semplice.
        
        Scenario:
        - Focus su riga 0, tentativo di spostamento verso l'alto.
        
        Risultato atteso:
        - Ritorna "Sei alla prima riga, non puoi andare oltre".
        - Indice riga non cambia (rimane 0).
        """
        # Setup: cartella + focus riga 0
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 0

        risultato = self.giocatore.sposta_focus_riga_su()
        
        self.assertEqual(
            risultato,
            "Sei alla prima riga, non puoi andare oltre",
            "Blocco dalla prima riga deve restituire messaggio corretto."
        )
        
        self.assertEqual(
            self.giocatore._indice_riga_focus,
            0,
            "Indice riga invariato su blocco."
        )

    def test_sposta_focus_riga_su_semplice_movimento_normale(self):
        """
        Verifica spostamento normale da riga 1→0 con stampa semplice.
        
        Scenario:
        - Focus riga 1 → Freccia SU → Focus riga 0 + "Riga 0: 5 12 24..."
        
        Risultato atteso:
        - Contiene "Riga 0:" e numeri puri (NO asterischi, NO stats).
        - Indice riga = 0.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 1

        risultato = self.giocatore.sposta_focus_riga_su()
        
        # Verifica 1: Struttura semplice
        self.assertIn("Riga 0:", risultato)
        
        # Verifica 2: Numeri presenti (senza asterischi)
        numeri_riga0 = self.cartella1.get_numeri_riga(0)
        for numero in numeri_riga0[:3]:
            self.assertIn(str(numero), risultato)
        
        # Verifica 3: NO asterischi, NO stats (versione semplice)
        self.assertNotIn("*", risultato)
        self.assertNotIn("Segnati", risultato)
        
        # Verifica 4: Stato interno
        self.assertEqual(self.giocatore._indice_riga_focus, 0)

    def test_sposta_focus_riga_su_semplice_auto_inizializzazione(self):
        """
        Verifica auto-inizializzazione da None → riga 1→0.
        
        Scenario:
        - _indice_riga_focus=None → Freccia SU → "Riga 0: 5 12..."
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = None

        risultato = self.giocatore.sposta_focus_riga_su()
        
        self.assertIn("Riga 0:", risultato)
        self.assertEqual(self.giocatore._indice_riga_focus, 0)
        self.assertNotIn("*", risultato)
        self.assertNotIn("Segnati", risultato)

    def test_sposta_focus_riga_su_semplice_stato_interno(self):
        """
        Verifica che lo stato interno si aggiorni correttamente anche con numeri segnati.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 2

        # Segna numeri (non deve influire sulla versione semplice)
        self.cartella1.segna_numero(10)

        risultato = self.giocatore.sposta_focus_riga_su()
        
        self.assertIn("Riga 1:", risultato)
        self.assertEqual(self.giocatore._indice_riga_focus, 1)
        self.assertNotIn("*", risultato)

    def test_sposta_focus_riga_giu_semplice_cartella_mancante(self):
        """
        Verifica gestione assenza cartella per versione GIÙ semplice.
        """
        risultato1 = self.giocatore.sposta_focus_riga_giu()
        self.assertEqual(risultato1, "Non hai selezionato nessuna cartella")
        
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None
        risultato2 = self.giocatore.sposta_focus_riga_giu()
        self.assertEqual(risultato2, "Non hai selezionato nessuna cartella")

    def test_sposta_focus_riga_giu_semplice_ultima_riga(self):
        """
        Verifica blocco dall'ultima riga (indice 2) per versione GIÙ semplice.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 2

        risultato = self.giocatore.sposta_focus_riga_giu()
        
        self.assertEqual(risultato, "Sei all'ultima riga, non puoi andare oltre")
        self.assertEqual(self.giocatore._indice_riga_focus, 2)

    def test_sposta_focus_riga_giu_semplice_movimento_normale(self):
        """
        Verifica spostamento normale da riga 0→1 con stampa semplice.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 0

        risultato = self.giocatore.sposta_focus_riga_giu()
        
        self.assertIn("Riga 1:", risultato)
        numeri_riga1 = self.cartella1.get_numeri_riga(1)
        for numero in numeri_riga1[:3]:
            self.assertIn(str(numero), risultato)
        self.assertNotIn("*", risultato)
        self.assertNotIn("Segnati", risultato)
        self.assertEqual(self.giocatore._indice_riga_focus, 1)

    def test_sposta_focus_riga_giu_semplice_auto_inizializzazione(self):
        """
        Verifica auto-inizializzazione da None → riga 0→1.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = None

        risultato = self.giocatore.sposta_focus_riga_giu()
        
        self.assertIn("Riga 1:", risultato)
        self.assertEqual(self.giocatore._indice_riga_focus, 1)
        self.assertNotIn("*", risultato)

    def test_sposta_focus_riga_giu_semplice_stato_interno(self):
        """
        Verifica aggiornamento stato interno con cartella segnata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 0

        self.cartella1.segna_numero(50)  # Numero segnato

        risultato = self.giocatore.sposta_focus_riga_giu()
        
        self.assertIn("Riga 1:", risultato)
        self.assertEqual(self.giocatore._indice_riga_focus, 1)
        self.assertNotIn("*", risultato)


    # ---------------------------------------------------------------------
    # TEST METODO: sposta_focus_riga_su_avanzata
    # ---------------------------------------------------------------------

    def test_sposta_focus_riga_su_avanzata_cartella_mancante(self):
        """
        Verifica che sposta_focus_riga_su_avanzata gestisca l'assenza di cartella focus.
        """
        # Scenario 1: Giocatore senza cartelle
        risultato1 = self.giocatore.sposta_focus_riga_su_avanzata()
        self.assertEqual(
            risultato1,
            "Non hai selezionato nessuna cartella",
            "Senza cartelle deve ritornare messaggio appropriato."
        )

        # Scenario 2: Focus rimosso manualmente
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None
        risultato2 = self.giocatore.sposta_focus_riga_su_avanzata()
        self.assertEqual(
            risultato2,
            "Non hai selezionato nessuna cartella",
            "Senza focus attivo deve ritornare messaggio appropriato."
        )

    def test_sposta_focus_riga_su_avanzata_prima_riga(self):
        """
        Verifica blocco dalla prima riga per versione avanzata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 0

        risultato = self.giocatore.sposta_focus_riga_su_avanzata()
        
        self.assertEqual(
            risultato,
            "Sei alla prima riga, non puoi andare oltre",
            "Blocco dalla prima riga deve restituire messaggio corretto."
        )
        self.assertEqual(self.giocatore._indice_riga_focus, 0)

    def test_sposta_focus_riga_su_avanzata_movimento_normale(self):
        """
        Verifica spostamento 1→0 con stampa avanzata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 1

        risultato = self.giocatore.sposta_focus_riga_su_avanzata()
        
        self.assertIn("Riga 0:", risultato)
        numeri_riga0 = self.cartella1.get_numeri_riga(0)
        for numero in numeri_riga0[:2]:
            self.assertIn(str(numero), risultato)
        self.assertEqual(self.giocatore._indice_riga_focus, 0)

    def test_sposta_focus_riga_su_avanzata_auto_inizializzazione(self):
        """
        Verifica auto-inizializzazione None→0 per versione avanzata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = None

        risultato = self.giocatore.sposta_focus_riga_su_avanzata()
        
        self.assertIn("Riga 0:", risultato)
        self.assertEqual(self.giocatore._indice_riga_focus, 0)

    def test_sposta_focus_riga_su_avanzata_stato_cartella_con_segni(self):
        """
        Verifica asterischi con cartella parzialmente segnata per versione avanzata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 1

        numeri_riga0 = self.cartella1.get_numeri_riga(0)
        self.cartella1.segna_numero(numeri_riga0[0])

        risultato = self.giocatore.sposta_focus_riga_su_avanzata()
        
        num_segnato_str = f"*{numeri_riga0[0]}"
        self.assertIn(num_segnato_str, risultato)

    # ---------------------------------------------------------------------
    # TEST METODO: sposta_focus_riga_giu_avanzata
    # ---------------------------------------------------------------------

    def test_sposta_focus_riga_giu_avanzata_cartella_mancante(self):
        """
        Verifica gestione cartella mancante per GIÙ avanzata.
        """
        risultato1 = self.giocatore.sposta_focus_riga_giu_avanzata()
        self.assertEqual(risultato1, "Non hai selezionato nessuna cartella")
        
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None
        risultato2 = self.giocatore.sposta_focus_riga_giu_avanzata()
        self.assertEqual(risultato2, "Non hai selezionato nessuna cartella")

    def test_sposta_focus_riga_giu_avanzata_ultima_riga(self):
        """
        Verifica blocco ultima riga per GIÙ avanzata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 2

        risultato = self.giocatore.sposta_focus_riga_giu_avanzata()
        
        self.assertEqual(risultato, "Sei all'ultima riga, non puoi andare oltre")
        self.assertEqual(self.giocatore._indice_riga_focus, 2)

    def test_sposta_focus_riga_giu_avanzata_movimento_normale(self):
        """
        Verifica movimento 0→1 per GIÙ avanzata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 0

        risultato = self.giocatore.sposta_focus_riga_giu_avanzata()
        
        self.assertIn("Riga 1:", risultato)
        numeri_riga1 = self.cartella1.get_numeri_riga(1)
        for numero in numeri_riga1[:2]:
            self.assertIn(str(numero), risultato)
        self.assertEqual(self.giocatore._indice_riga_focus, 1)

    def test_sposta_focus_riga_giu_avanzata_auto_inizializzazione(self):
        """
        Verifica auto-inizializzazione None→1 per GIÙ avanzata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = None

        risultato = self.giocatore.sposta_focus_riga_giu_avanzata()
        
        self.assertIn("Riga 1:", risultato)
        self.assertEqual(self.giocatore._indice_riga_focus, 1)

    def test_sposta_focus_riga_giu_avanzata_stato_cartella_con_segni(self):
        """
        Verifica asterischi per GIÙ avanzata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_riga_focus = 1

        numeri_riga2 = self.cartella1.get_numeri_riga(2)
        self.cartella1.segna_numero(numeri_riga2[0])

        risultato = self.giocatore.sposta_focus_riga_giu_avanzata()
        
        num_segnato_str = f"*{numeri_riga2[0]}"
        self.assertIn(num_segnato_str, risultato)


    # ---------------------------------------------------------------------
    # TEST METODI: sposta_focus_colonna_sinistra/destra (VERSIONE SEMPLICE)
    # ---------------------------------------------------------------------

    def test_sposta_focus_colonna_sinistra_semplice_cartella_mancante(self):
        """
        Verifica che sposta_focus_colonna_sinistra() gestisca correttamente l'assenza di cartella focus
        nella versione semplice (stampa_colonna_semplice).
        
        Scenario:
        - Giocatore senza cartelle o senza focus impostato.
        
        Risultato atteso:
        - Ritorna messaggio "Non hai selezionato nessuna cartella".
        """
        # Scenario 1: Giocatore senza cartelle
        risultato1 = self.giocatore.sposta_focus_colonna_sinistra()
        self.assertEqual(
            risultato1,
            "Non hai selezionato nessuna cartella",
            "Senza cartelle deve ritornare messaggio appropriato."
        )

        # Scenario 2: Focus rimosso manualmente
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None
        risultato2 = self.giocatore.sposta_focus_colonna_sinistra()
        self.assertEqual(
            risultato2,
            "Non hai selezionato nessuna cartella",
            "Senza focus attivo deve ritornare messaggio appropriato."
        )

    def test_sposta_focus_colonna_sinistra_semplice_prima_colonna(self):
        """
        Verifica che il metodo blocchi lo spostamento dalla prima colonna (indice 0)
        nella versione semplice.
        
        Scenario:
        - Focus su colonna 0, tentativo di spostamento verso sinistra.
        
        Risultato atteso:
        - Ritorna "Sei alla prima colonna, non puoi andare oltre".
        - Indice colonna non cambia (rimane 0).
        """
        # Setup: cartella + focus colonna 0
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 0

        risultato = self.giocatore.sposta_focus_colonna_sinistra()
        
        self.assertEqual(
            risultato,
            "Sei alla prima colonna, non puoi andare oltre",
            "Blocco dalla prima colonna deve restituire messaggio corretto."
        )
        
        self.assertEqual(
            self.giocatore._indice_colonna_focus,
            0,
            "Indice colonna invariato su blocco."
        )


    def test_sposta_focus_colonna_sinistra_semplice_movimento_normale(self):
        """
        Verifica spostamento normale da colonna 5→4 con stampa semplice.
        
        Scenario:
        - Focus colonna 5 → Freccia SINISTRA → Focus colonna 4 + "Colonna 4: ..."
        
        Risultato atteso:
        - Contiene "Colonna 4:".
        - Se ha numeri, li mostra. Se è vuota, dice "vuota".
        - Indice colonna = 4.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 5

        risultato = self.giocatore.sposta_focus_colonna_sinistra()
        
        # Verifica 1: Struttura semplice (intestazione corretta)
        self.assertIn("Colonna 4:", risultato)
        
        # Verifica 2: Contenuto coerente con la realtà della cartella
        numeri_colonna4 = self.cartella1.get_numeri_colonna(4)
        
        if numeri_colonna4:
            # Se la colonna ha numeri, devono essere nella stringa
            for numero in numeri_colonna4[:3]: 
                self.assertIn(str(numero), risultato)
            # E NON deve esserci scritto "vuota" se ci sono numeri
            self.assertNotIn("vuota", risultato)
        else:
            # Se la colonna è vuota, DEVE esserci scritto "vuota"
            self.assertIn("vuota", risultato)
        
        # Verifica 3: NO asterischi, NO stats (versione semplice)
        self.assertNotIn("*", risultato)
        self.assertNotIn("Segnati:", risultato)
        
        # Verifica 4: Stato interno corretto
        self.assertEqual(self.giocatore._indice_colonna_focus, 4)


    def test_sposta_focus_colonna_sinistra_semplice_auto_inizializzazione(self):
        """
        Verifica auto-inizializzazione da None → colonna 4→3.
        
        Scenario:
        - _indice_colonna_focus=None → Freccia SINISTRA → "Colonna 3: 12 25..."
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = None

        risultato = self.giocatore.sposta_focus_colonna_sinistra()
        
        self.assertIn("Colonna 3:", risultato)
        self.assertEqual(self.giocatore._indice_colonna_focus, 3)
        self.assertNotIn("*", risultato)

    def test_sposta_focus_colonna_sinistra_semplice_colonna_vuota(self):
        """
        Verifica gestione colonna vuota nella navigazione sinistra.
        
        Scenario:
        - Movimento che porta su colonna 4 che risulta vuota.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 4

        risultato = self.giocatore.sposta_focus_colonna_sinistra()
        
        self.assertIn("Colonna 3:", risultato)
        self.assertEqual(self.giocatore._indice_colonna_focus, 3)
        # Nota: testiamo che gestisce il ritorno anche se colonna vuota

    def test_sposta_focus_colonna_destra_semplice_cartella_mancante(self):
        """
        Verifica gestione assenza cartella per versione DESTRA semplice.
        """
        risultato1 = self.giocatore.sposta_focus_colonna_destra()
        self.assertEqual(risultato1, "Non hai selezionato nessuna cartella")
        
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None
        risultato2 = self.giocatore.sposta_focus_colonna_destra()
        self.assertEqual(risultato2, "Non hai selezionato nessuna cartella")

    def test_sposta_focus_colonna_destra_semplice_ultima_colonna(self):
        """
        Verifica blocco dall'ultima colonna (indice 8) per versione DESTRA semplice.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 8

        risultato = self.giocatore.sposta_focus_colonna_destra()
        
        self.assertEqual(risultato, "Sei all'ultima colonna (9), non puoi andare oltre")
        self.assertEqual(self.giocatore._indice_colonna_focus, 8)

    def test_sposta_focus_colonna_destra_semplice_movimento_normale(self):
        """
        Verifica spostamento normale da colonna 3→4 con stampa semplice.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 3

        risultato = self.giocatore.sposta_focus_colonna_destra()
        
        self.assertIn("Colonna 4:", risultato)
        numeri_colonna4 = self.cartella1.get_numeri_colonna(4)
        for numero in numeri_colonna4[:3]:
            self.assertIn(str(numero), risultato)
        self.assertNotIn("*", risultato)
        self.assertEqual(self.giocatore._indice_colonna_focus, 4)

    def test_sposta_focus_colonna_destra_semplice_auto_inizializzazione(self):
        """
        Verifica auto-inizializzazione da None → colonna 4→5.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = None

        risultato = self.giocatore.sposta_focus_colonna_destra()
        
        self.assertIn("Colonna 5:", risultato)
        self.assertEqual(self.giocatore._indice_colonna_focus, 5)
        self.assertNotIn("*", risultato)

    def test_sposta_focus_colonna_destra_semplice_colonna_vuota(self):
        """
        Verifica gestione colonna vuota nella navigazione destra.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 4

        risultato = self.giocatore.sposta_focus_colonna_destra()
        
        self.assertIn("Colonna 5:", risultato)
        self.assertEqual(self.giocatore._indice_colonna_focus, 5)

    def test_sposta_focus_colonna_destra_semplice_stato_interno(self):
        """
        Verifica aggiornamento stato interno con cartella segnata.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 3

        self.cartella1.segna_numero(50)  # Numero segnato

        risultato = self.giocatore.sposta_focus_colonna_destra()
        
        self.assertIn("Colonna 4:", risultato)
        self.assertEqual(self.giocatore._indice_colonna_focus, 4)
        self.assertNotIn("*", risultato)  # Versione semplice NO asterischi


    # ---------------------------------------------------------------------
    # TEST METODO: sposta_focus_colonna_sinistra_avanzata
    # ---------------------------------------------------------------------

    def test_sposta_focus_colonna_sinistra_avanzata_cartella_mancante(self):
        """
        Verifica che sposta_focus_colonna_sinistra_avanzata gestisca l'assenza di cartella focus.
        
        Scenario:
        - Giocatore senza cartelle o senza focus impostato.
        
        Risultato atteso:
        - Ritorna messaggio "Non hai selezionato nessuna cartella".
        """
        # Scenario 1: Giocatore senza cartelle
        risultato1 = self.giocatore.sposta_focus_colonna_sinistra_avanzata()
        self.assertEqual(
            risultato1,
            "Non hai selezionato nessuna cartella",
            "Senza cartelle deve ritornare messaggio appropriato."
        )

        # Scenario 2: Focus rimosso manualmente
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None
        risultato2 = self.giocatore.sposta_focus_colonna_sinistra_avanzata()
        self.assertEqual(
            risultato2,
            "Non hai selezionato nessuna cartella",
            "Senza focus attivo deve ritornare messaggio appropriato."
        )

    def test_sposta_focus_colonna_sinistra_avanzata_prima_colonna(self):
        """
        Verifica blocco dalla prima colonna (indice 0) per versione avanzata.
        
        Scenario:
        - Focus su colonna 0, tentativo di spostamento a sinistra.
        
        Risultato atteso:
        - Ritorna "Sei alla prima colonna, non puoi andare oltre".
        - Indice colonna non cambia (rimane 0).
        """
        # Setup: cartella + focus colonna 0
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 0

        risultato = self.giocatore.sposta_focus_colonna_sinistra_avanzata()
        
        self.assertEqual(
            risultato,
            "Sei alla prima colonna, non puoi andare oltre",
            "Blocco dalla prima colonna deve restituire messaggio corretto."
        )
        
        self.assertEqual(
            self.giocatore._indice_colonna_focus,
            0,
            "Indice colonna invariato su blocco."
        )

    def test_sposta_focus_colonna_sinistra_avanzata_movimento_normale(self):
        """
        Verifica spostamento normale da colonna 5→4 con stampa avanzata.
        
        Scenario:
        - Focus colonna 5 → Freccia SINISTRA → Focus colonna 4 + stampa completa.
        
        Risultato atteso:
        - Contiene "Colonna 4:" e numeri reali.
        - Contiene "Segnati:" (riepilogo stats).
        - Indice colonna aggiornato a 4.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 5

        risultato = self.giocatore.sposta_focus_colonna_sinistra_avanzata()
        
        # Verifica 1: Struttura base
        self.assertIn("Colonna 4:", risultato)
        
        # Verifica 2: Presenza numeri reali (se colonna non vuota)
        numeri_colonna4 = self.cartella1.get_numeri_colonna(4)
        if numeri_colonna4:
            for numero in numeri_colonna4:
                self.assertIn(str(numero), risultato)
        else:
            self.assertIn("vuota", risultato)

        # Verifica 3: Presenza stats avanzate (solo se non vuota)
        if numeri_colonna4:
             self.assertIn("Segnati:", risultato)
        
        # Verifica 4: Stato interno
        self.assertEqual(self.giocatore._indice_colonna_focus, 4)

    def test_sposta_focus_colonna_sinistra_avanzata_auto_inizializzazione(self):
        """
        Verifica auto-inizializzazione da None → colonna 4→3.
        
        Scenario:
        - _indice_colonna_focus=None → Freccia SINISTRA → "Colonna 3:..."
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = None

        risultato = self.giocatore.sposta_focus_colonna_sinistra_avanzata()
        
        self.assertIn("Colonna 3:", risultato)
        self.assertEqual(self.giocatore._indice_colonna_focus, 3)

    def test_sposta_focus_colonna_sinistra_avanzata_stato_cartella_con_segni(self):
        """
        Verifica presenza indicatori di stato (asterischi) e riepiloghi.
        
        Scenario:
        - Colonna 3 con un numero segnato.
        - Spostamento da colonna 4 a 3.
        
        Risultato atteso:
        - Stringa contiene "*NUMERO".
        - Stringa contiene "Segnati: 1 su X".
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 4

        # Prepara colonna 3: segna un numero se presente
        numeri_colonna3 = self.cartella1.get_numeri_colonna(3)
        if numeri_colonna3:
            numero_da_segnare = numeri_colonna3[0]
            self.cartella1.segna_numero(numero_da_segnare)
            
            risultato = self.giocatore.sposta_focus_colonna_sinistra_avanzata()
            
            # Verifica presenza asterisco sul numero segnato
            num_segnato_str = f"*{numero_da_segnare}"
            self.assertIn(
                num_segnato_str, 
                risultato,
                f"Deve essere presente l'asterisco per il numero segnato {numero_da_segnare}"
            )
            
            # Verifica presenza riepilogo
            self.assertIn("Segnati:", risultato)
        else:
            # Caso speciale colonna vuota (se generata vuota nel test)
            risultato = self.giocatore.sposta_focus_colonna_sinistra_avanzata()
            self.assertIn("vuota", risultato)


    # ---------------------------------------------------------------------
    # TEST METODO: sposta_focus_colonna_destra_avanzata
    # ---------------------------------------------------------------------

    def test_sposta_focus_colonna_destra_avanzata_cartella_mancante(self):
        """
        Verifica gestione cartella mancante per DESTRA avanzata.
        """
        risultato1 = self.giocatore.sposta_focus_colonna_destra_avanzata()
        self.assertEqual(risultato1, "Non hai selezionato nessuna cartella")
        
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None
        risultato2 = self.giocatore.sposta_focus_colonna_destra_avanzata()
        self.assertEqual(risultato2, "Non hai selezionato nessuna cartella")

    def test_sposta_focus_colonna_destra_avanzata_ultima_colonna(self):
        """
        Verifica blocco ultima colonna (indice 8) per DESTRA avanzata.
        
        Scenario:
        - Focus su colonna 8, tentativo di spostamento a destra.
        
        Risultato atteso:
        - Messaggio "Sei all'ultima colonna (9), non puoi andare oltre".
        - Indice rimane 8.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 8

        risultato = self.giocatore.sposta_focus_colonna_destra_avanzata()
        
        self.assertEqual(
            risultato, 
            "Sei all'ultima colonna (9), non puoi andare oltre"
        )
        self.assertEqual(self.giocatore._indice_colonna_focus, 8)

    def test_sposta_focus_colonna_destra_avanzata_movimento_normale(self):
        """
        Verifica movimento normale da 3→4 con stampa avanzata.
        
        Scenario:
        - Focus colonna 3 → Freccia DESTRA → Colonna 4.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 3

        risultato = self.giocatore.sposta_focus_colonna_destra_avanzata()
        
        self.assertIn("Colonna 4:", risultato)
        
        # Verifica numeri reali
        numeri_colonna4 = self.cartella1.get_numeri_colonna(4)
        if numeri_colonna4:
            for numero in numeri_colonna4:
                self.assertIn(str(numero), risultato)
            self.assertIn("Segnati:", risultato)
        else:
             self.assertIn("vuota", risultato)
            
        self.assertEqual(self.giocatore._indice_colonna_focus, 4)

    def test_sposta_focus_colonna_destra_avanzata_auto_inizializzazione(self):
        """
        Verifica auto-inizializzazione da None → colonna 4→5.
        
        Scenario:
        - _indice_colonna_focus=None → Freccia DESTRA → "Colonna 5:..."
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = None

        risultato = self.giocatore.sposta_focus_colonna_destra_avanzata()
        
        self.assertIn("Colonna 5:", risultato)
        self.assertEqual(self.giocatore._indice_colonna_focus, 5)


    def test_sposta_focus_colonna_destra_avanzata_stato_cartella_con_segni(self):
        """
        Verifica asterischi per DESTRA avanzata su colonna segnata.
        
        Scenario:
        - Colonna 4 con numero segnato.
        - Spostamento da colonna 3 a 4.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        self.giocatore._indice_colonna_focus = 3

        # Segna numero su colonna 4 (se esiste)
        numeri_colonna4 = self.cartella1.get_numeri_colonna(4)
        
        if numeri_colonna4:
            # CASO A: Colonna con numeri
            self.cartella1.segna_numero(numeri_colonna4[0])
            
            risultato = self.giocatore.sposta_focus_colonna_destra_avanzata()
            
            num_segnato_str = f"*{numeri_colonna4[0]}"
            self.assertIn(num_segnato_str, risultato)
            self.assertIn("Segnati:", risultato)
        else:
            # CASO B: Colonna vuota (Fallback generato random)
            risultato = self.giocatore.sposta_focus_colonna_destra_avanzata()
            
            # In modalità avanzata, Cartella stampa "Segnati: 0 su 0" invece di "vuota"
            # Quindi verifichiamo che ci siano le statistiche vuote
            self.assertIn("Segnati: 0 su 0", risultato)


    # ---------------------------------------------------------------------
    # TEST METODO: segna_numero_manuale
    # ---------------------------------------------------------------------

    def test_segna_numero_manuale_input_invalido(self):
        """
        Verifica che il metodo gestisca correttamente input non validi.
        
        Scenario:
        - Utente inserisce numero fuori range (95) o tipo errato.
        - Tabellone mockato (non dovrebbe nemmeno essere consultato).
        
        Risultato atteso:
        - Messaggio di errore per numero non valido.
        """
        # Creiamo un mock semplice del tabellone (non verrà usato, ma serve come parametro)
        mock_tabellone = Mock()
        
        # Test numero fuori range alto
        risultato = self.giocatore.segna_numero_manuale(95, mock_tabellone)
        self.assertIn("Errore", risultato)
        self.assertIn("tra 1 e 90", risultato)
        
        # Test numero fuori range basso
        risultato_basso = self.giocatore.segna_numero_manuale(0, mock_tabellone)
        self.assertIn("Errore", risultato_basso)

    def test_segna_numero_manuale_nessun_focus(self):
        """
        Verifica blocco azione se non c'è una cartella selezionata.
        
        Scenario:
        - Giocatore con cartelle ma focus rimosso (None).
        - Numero valido (45).
        
        Risultato atteso:
        - Messaggio "Seleziona prima una cartella".
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore._indice_cartella_focus = None # Rimuovi focus
        mock_tabellone = Mock()

        risultato = self.giocatore.segna_numero_manuale(45, mock_tabellone)
        
        self.assertEqual(
            risultato,
            "Errore: Seleziona prima una cartella su cui segnare il numero."
        )

    def test_segna_numero_manuale_non_estratto(self):
        """
        Verifica controllo anti-baro: impossibile segnare numeri non usciti.
        
        Scenario:
        - Utente prova a segnare 45.
        - Tabellone riporta che sono usciti solo [10, 20].
        - Focus cartella attivo.
        
        Risultato atteso:
        - Errore specifico "non è ancora stato estratto".
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        
        # Mock Tabellone: ritorna lista senza il 45
        mock_tabellone = Mock()
        mock_tabellone.get_numeri_estratti.return_value = [10, 20]

        risultato = self.giocatore.segna_numero_manuale(45, mock_tabellone)
        
        self.assertIn("non è ancora stato estratto", risultato)
        # Verifica che il metodo del tabellone sia stato chiamato
        mock_tabellone.get_numeri_estratti.assert_called_once()

    def test_segna_numero_manuale_non_presente_in_cartella(self):
        """
        Verifica caso: numero uscito MA non presente sulla cartella selezionata.
        
        Scenario:
        - Tabellone ha estratto il 45.
        - Cartella selezionata NON contiene il 45.
        
        Risultato atteso:
        - Messaggio "Il numero 45 non è presente nella Cartella X".
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        
        # Recupera un numero che SICURAMENTE non è nella cartella
        numeri_cartella = self.cartella1.get_numeri_cartella()
        numero_assente = 1
        while numero_assente in numeri_cartella:
            numero_assente += 1
            
        # Mock Tabellone: il numero assente risulta estratto
        mock_tabellone = Mock()
        mock_tabellone.get_numeri_estratti.return_value = [numero_assente, 10, 20]

        risultato = self.giocatore.segna_numero_manuale(numero_assente, mock_tabellone)
        
        self.assertIn(f"non è presente nella Cartella 1", risultato)

    def test_segna_numero_manuale_gia_segnato(self):
        """
        Verifica feedback per numero già segnato in precedenza.
        
        Scenario:
        - Numero 45 presente in cartella ed estratto.
        - Numero 45 GIÀ segnato manualmente prima.
        - Utente riprova a segnarlo.
        
        Risultato atteso:
        - Messaggio "già stato segnato".
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        
        # Prendi un numero reale dalla cartella
        numero_reale = self.cartella1.get_numeri_cartella()[0]
        
        # Segnalo preventivamente
        self.cartella1.segna_numero(numero_reale)
        
        # Mock Tabellone: numero estratto
        mock_tabellone = Mock()
        mock_tabellone.get_numeri_estratti.return_value = [numero_reale]

        risultato = self.giocatore.segna_numero_manuale(numero_reale, mock_tabellone)
        
        self.assertIn("è già stato segnato", risultato)

    def test_segna_numero_manuale_successo(self):
        """
        Verifica il flusso felice: segnatura avvenuta con successo.
        
        Scenario:
        - Numero presente in cartella, non segnato.
        - Numero estratto dal tabellone.
        
        Risultato atteso:
        - Messaggio "Fatto! Segnato...".
        - Stato cartella verificato: numero risulta segnato.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        self.giocatore.imposta_focus_cartella(1)
        
        # Prendi numero reale non ancora segnato
        numero_reale = self.cartella1.get_numeri_cartella()[0]
        
        # Mock Tabellone
        mock_tabellone = Mock()
        mock_tabellone.get_numeri_estratti.return_value = [numero_reale, 90]

        risultato = self.giocatore.segna_numero_manuale(numero_reale, mock_tabellone)
        
        # Verifica 1: Messaggio successo
        self.assertIn("Fatto! Segnato", risultato)
        self.assertIn(f"numero {numero_reale}", risultato)
        
        # Verifica 2: Stato effettivo cartella modificato
        self.assertTrue(
            self.cartella1.is_numero_segnato(numero_reale),
            "Il numero dovrebbe risultare segnato nella cartella dopo l'operazione."
        )

    def test_segna_numero_manuale_cartella_errata(self):
        """
        Verifica gameplay: il numero c'è ma su un'altra cartella (non quella focus).
        
        Scenario:
        - Giocatore ha 2 cartelle.
        - Numero 45 presente SOLO su Cartella 2.
        - Focus su Cartella 1.
        - Utente prova a segnare 45.
        
        Risultato atteso:
        - Messaggio "Non presente nella Cartella 1" (anche se c'è nella 2!).
        """
        # Creiamo due cartelle diverse
        c1 = Cartella()
        c2 = Cartella()
        
        # Assicuriamoci che c1 e c2 abbiano numeri diversi (rigeneriamo se serve, ma è probabile)
        # Per sicurezza, forziamo uno scenario nel test o cerchiamo un numero esclusivo
        numeri_c1 = set(c1.get_numeri_cartella())
        numeri_c2 = set(c2.get_numeri_cartella())
        
        # Trova numero presente in c2 ma NON in c1
        diff = list(numeri_c2 - numeri_c1)
        if not diff:
            self.skipTest("Impossibile trovare numeri diversi tra le due cartelle random")
            
        numero_target = diff[0]
        
        self.giocatore.aggiungi_cartella(c1)
        self.giocatore.aggiungi_cartella(c2)
        
        # Focus sulla Cartella 1 (dove il numero NON c'è)
        self.giocatore.imposta_focus_cartella(1)
        
        # Mock Tabellone
        mock_tabellone = Mock()
        mock_tabellone.get_numeri_estratti.return_value = [numero_target]

        risultato = self.giocatore.segna_numero_manuale(numero_target, mock_tabellone)
        
        # Deve dire che non c'è nella Cartella 1
        self.assertIn("non è presente nella Cartella 1", risultato)
        
        # Verifica che NON sia stato segnato per sbaglio sulla cartella 2
        self.assertFalse(c2.is_numero_segnato(numero_target))



    # ---------------------------------------------------------------------
    # TEST METODO: cerca_numero_nelle_cartelle
    # ---------------------------------------------------------------------

    def test_cerca_numero_input_invalido(self):
        """
        Verifica che il metodo gestisca correttamente input non validi.
        
        Scenario:
        - Numero fuori range (es. 95) o negativo.
        
        Risultato atteso:
        - Messaggio di errore "numero valido tra 1 e 90".
        """
        risultato = self.giocatore.cerca_numero_nelle_cartelle(95)
        self.assertIn("Errore", risultato)
        self.assertIn("tra 1 e 90", risultato)
        
        risultato_neg = self.giocatore.cerca_numero_nelle_cartelle(-5)
        self.assertIn("Errore", risultato_neg)

    def test_cerca_numero_senza_cartelle(self):
        """
        Verifica comportamento se il giocatore non ha cartelle assegnate.
        
        Scenario:
        - Giocatore appena creato, lista cartelle vuota.
        
        Risultato atteso:
        - Messaggio di errore specifico "Non hai ancora assegnato nessuna cartella".
        """
        # Assicuriamoci che non ci siano cartelle
        self.giocatore.cartelle = []
        
        risultato = self.giocatore.cerca_numero_nelle_cartelle(10)
        
        self.assertEqual(
            risultato,
            "Errore: Non hai ancora assegnato nessuna cartella."
        )

    def test_cerca_numero_non_trovato(self):
        """
        Verifica ricerca di un numero che non è presente in nessuna cartella.
        
        Scenario:
        - Giocatore con 1 cartella.
        - Si cerca un numero assente.
        
        Risultato atteso:
        - Messaggio "Il numero X non è presente nelle tue cartelle".
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        
        # Troviamo un numero sicuramente assente
        numeri_presenti = self.cartella1.get_numeri_cartella()
        numero_assente = 1
        while numero_assente in numeri_presenti:
            numero_assente += 1
            
        risultato = self.giocatore.cerca_numero_nelle_cartelle(numero_assente)
        
        self.assertIn(f"Il numero {numero_assente} non è presente", risultato)

    def test_cerca_numero_trovato_da_segnare(self):
        """
        Verifica ricerca di un numero presente e NON ancora segnato.
        
        Scenario:
        - Numero presente nella Cartella 1.
        - Stato: non segnato.
        
        Risultato atteso:
        - "Trovato X in:"
        - "Cartella 1"
        - "DA SEGNARE"
        - Indicazione corretta della riga.
        """
        self.giocatore.aggiungi_cartella(self.cartella1)
        
        # Prendi un numero reale
        numero_presente = self.cartella1.get_numeri_cartella()[0]
        
        # Trova in che riga è (per verificare l'output)
        riga_reale = -1
        for r in range(3):
            if numero_presente in self.cartella1.get_numeri_riga(r):
                riga_reale = r
                break
                
        risultato = self.giocatore.cerca_numero_nelle_cartelle(numero_presente)
        
        # Verifiche
        self.assertIn(f"Trovato {numero_presente}", risultato)
        self.assertIn("Cartella 1", risultato)
        self.assertIn(f"Riga {riga_reale + 1}", risultato) # Verifica riga umana (base-1)
        self.assertIn("DA SEGNARE", risultato) # Non lo abbiamo segnato

    def test_cerca_numero_trovato_multiplo_misto(self):
        """
        Verifica ricerca numero presente in PIÙ cartelle con stati DIVERSI.
        
        Scenario:
        - Giocatore ha 2 cartelle identiche (clonate per il test).
        - Numero X presente in entrambe.
        - Su Cartella 1 è segnato ("Già segnato").
        - Su Cartella 2 è intonso ("DA SEGNARE").
        
        Risultato atteso:
        - Report multilinea.
        - Riga per Cartella 1 con "Già segnato".
        - Riga per Cartella 2 con "DA SEGNARE".
        """
        # Creiamo una cartella e cloniamola (o usiamo deepcopy, o generiamo finché non troviamo match)
        # Metodo rapido: usiamo la stessa istanza cartella due volte (lecito per il test logico)
        # Attenzione: se segno su c1 e c1 è c2, segno su entrambe.
        # Dobbiamo trovare due cartelle diverse che hanno un numero in comune.
        
        c1 = Cartella()
        c2 = Cartella()
        
        # Cerchiamo intersezione
        numeri_c1 = set(c1.get_numeri_cartella())
        numeri_c2 = set(c2.get_numeri_cartella())
        intersezione = list(numeri_c1 & numeri_c2)
        
        if not intersezione:
            # Caso raro: cartelle disgiunte. Forziamo il test creando c2 manualmente simile a c1?
            # Oppure riproviamo loop. Per robustezza, forziamo un numero in c2.
            # Ma Cartella non ha set_numero().
            # Allora usiamo Mock per c2 per garantire la presenza.
            self.skipTest("Skipped: Impossibile trovare numero comune tra cartelle random (raro ma possibile)")
            
        numero_comune = intersezione[0]
        
        self.giocatore.aggiungi_cartella(c1)
        self.giocatore.aggiungi_cartella(c2)
        
        # Segna SOLO sulla cartella 1
        c1.segna_numero(numero_comune)
        
        risultato = self.giocatore.cerca_numero_nelle_cartelle(numero_comune)
        
        # Verifica Output Cartella 1 (Già segnato)
        self.assertIn("Cartella 1", risultato)
        # Controllo che la sottostringa Cartella 1 sia associata a Già segnato
        # Splittiamo le righe per essere precisi
        righe = risultato.split('\n')
        
        riga_c1 = next((r for r in righe if "Cartella 1" in r), "")
        self.assertIn("Già segnato", riga_c1)
        
        # Verifica Output Cartella 2 (DA SEGNARE)
        riga_c2 = next((r for r in righe if "Cartella 2" in r), "")
        self.assertIn("DA SEGNARE", riga_c2)
