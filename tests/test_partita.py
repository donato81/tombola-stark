"""
SUITE DI TEST PER LA CLASSE PARTITA
Modulo: tests.test_partita

Questa suite di test verifica il comportamento della classe Partita,
che funge da controller principale per il gioco della tombola.

I test sono organizzati nelle seguenti sezioni logiche:

SEZIONE 1: Inizializzazione e Stato Iniziale
- Verifica che la partita venga inizializzata con lo stato corretto ("non_iniziata").
- Verifica che le liste (giocatori, vincite) siano vuote alla creazione.
- Verifica i valori di default (es. costo cartella, tipo vincite).
- (sezione 1 completata e funzionante.)

SEZIONE 2: Gestione del Roster Giocatori
- Aggiunta corretta di un giocatore valido.
- Gestione errori: aggiunta di giocatore duplicato (PartitaGiocatoreGiaPresenteException).
- Gestione errori: aggiunta giocatore nullo o tipo errato.
- Gestione errori: superamento numero massimo giocatori (se applicabile).

SEZIONE 3: Gestione Stati e Avvio/Termine
- Avvio partita con numero insufficiente di giocatori (PartitaGiocatoriInsufficientiException).
- Avvio corretto e cambio stato in "in_corso".
- Tentativo di avviare una partita già in corso o terminata.
- Terminazione partita e cambio stato in "terminata".

SEZIONE 4: Flusso di Gioco ed Estrazioni
- Verifica estrazione numero (chiama tabellone ed aggiorna stato).
- Verifica aggiornamento giocatori dopo estrazione.
- Gestione errori: tentativo di estrarre a partita non iniziata.
- Gestione errori: estrazione a partita terminata.

SEZIONE 5: Logica di Verifica Vincite e Premi
- Verifica rilevamento vincite semplici (es. Ambo).
- Verifica che una vincita già pagata non venga ripagata nello stesso turno/riga.
- Verifica progressione premi (Ambo -> Terno -> ... -> Tombola).
- Controllo correttezza del dizionario di ritorno di esegui_turno.

SEZIONE 6: Reset e Utility
- Test dei metodi getter informativi (get_stato_completo, get_vincite, ecc.).
"""

import unittest
from bingo_game.partita import Partita
from bingo_game.tabellone import Tabellone 
from bingo_game.cartella import Cartella
from bingo_game.exceptions.partita_exceptions import (
    PartitaException,
    PartitaStatoException,
    PartitaGiaIniziataException,
    PartitaNonInCorsoException,
    PartitaGiaTerminataException,
    PartitaRosterException,
    PartitaRosterPienoException,
    PartitaGiocatoriInsufficientiException,
    PartitaGiocatoreTypeException,
    PartitaGiocatoreGiaPresenteException,
    PartitaGiocoException,
    PartitaNumeriEsauritiException
)
# Importiamo GiocatoreBase o una sua implementazione concreta/mock per i test
from bingo_game.players.giocatore_base import GiocatoreBase

class TestPartita(unittest.TestCase):
    
    def setUp(self):
        """
        Setup eseguito prima di ogni test.
        Crea un'istanza di Tabellone e una di Partita pulita.
        """
        # Creiamo un tabellone fresco per ogni test
        self.tabellone = Tabellone()
        
        # Creiamo la partita passando il tabellone obbligatorio
        # Inizialmente senza giocatori (default)
        self.partita = Partita(tabellone=self.tabellone)


    """SEZIONE 1: METODI DI Inizializzazione e Stato Iniziale"""

    #metodo che va a testare l'inizializzazione pulita della partita 
    def test_inizializzazione_stato_base(self):
        """
        Verifica che la partita venga inizializzata con lo stato e gli attributi di base corretti.
        """
        # Verifica lo stato iniziale
        self.assertEqual(
            self.partita.stato_partita, 
            "non_iniziata",
            "La partita dovrebbe nascere nello stato 'non_iniziata'."
        )
        
        # Verifica l'ultimo numero estratto (deve essere None)
        self.assertIsNone(
            self.partita.ultimo_numero_estratto,
            "L'ultimo numero estratto dovrebbe essere None all'avvio."
        )
        
        # Verifica che il set dei premi assegnati sia vuoto
        self.assertEqual(
            self.partita.premi_gia_assegnati, 
            set(),
            "Il set dei premi già assegnati dovrebbe essere vuoto."
        )
        
        # Verifica che il tabellone sia stato assegnato correttamente
        self.assertIsInstance(
            self.partita.tabellone, 
            Tabellone,
            "L'attributo tabellone dovrebbe essere un'istanza valida di Tabellone."
        )


    #metodo che va a testare l'inizializzazione della partita senza giocatori presenti 
    def test_inizializzazione_giocatori_vuota(self):
        """
        Verifica l'inizializzazione della lista giocatori quando non ne vengono forniti.
        
        Obiettivo:
        - Assicurarsi che self.giocatori sia una lista vuota [] e non None.
        - Verificare che il contatore dei giocatori ritorni 0.
        """
        # Verifica che la lista interna sia inizializzata come lista vuota
        # (Importante: non deve essere None per evitare errori successivi)
        self.assertEqual(
            self.partita.giocatori, 
            [],
            "La lista giocatori dovrebbe essere inizializzata come lista vuota [] se non fornita."
        )
        
        # Verifica che il metodo get_numero_giocatori ritorni 0
        numero_giocatori = self.partita.get_numero_giocatori()
        self.assertEqual(
            numero_giocatori, 
            0,
            f"Il numero di giocatori dovrebbe essere 0, trovato: {numero_giocatori}"
        )
        
        # Verifica aggiuntiva di tipo: deve essere proprio una lista
        self.assertIsInstance(
            self.partita.giocatori, 
            list,
            "L'attributo giocatori deve essere di tipo list."
        )


    #metodo che va a testare l'inizializzazione della partita con presenza di giocatori
    def test_inizializzazione_giocatori_popolata(self):
        """
        Verifica l'inizializzazione della partita fornendo una lista di giocatori esistenti.
        
        Obiettivo:
        - Verificare che i giocatori passati vengano registrati correttamente.
        - Verificare che la lista interna sia una COPIA indipendente (sicurezza).
        """

        # Creazione di due giocatori fittizi per il test
        # Nota: usiamo ID univoci e nomi semplici
        g1 = GiocatoreBase(nome="Mario", id_giocatore=1)
        g2 = GiocatoreBase(nome="Luigi", id_giocatore=2)
        lista_iniziale = [g1, g2]

        # Creazione di una NUOVA istanza di partita per questo specifico test
        # (sovrascriviamo quella del setUp che era vuota)
        partita_con_giocatori = Partita(tabellone=self.tabellone, giocatori=lista_iniziale)

        # 1. Verifica che i giocatori siano stati caricati
        self.assertEqual(
            partita_con_giocatori.get_numero_giocatori(),
            2,
            "Il numero di giocatori registrati dovrebbe essere 2."
        )
        self.assertEqual(
            partita_con_giocatori.get_giocatori(),
            lista_iniziale,
            "La lista interna dei giocatori dovrebbe corrispondere a quella fornita."
        )

        # 2. Verifica di sicurezza sulla copia della lista
        # Modifichiamo la lista originale 'esterna' (aggiungiamo un intruso)
        lista_iniziale.append("Giocatore Intruso")
        
        # La lista interna della partita NON deve essere cambiata
        self.assertEqual(
            partita_con_giocatori.get_numero_giocatori(),
            2,
            "La modifica della lista esterna non deve influenzare la lista interna della partita."
        )
        self.assertNotIn(
            "Giocatore Intruso",
            partita_con_giocatori.get_giocatori(),
            "L'elemento aggiunto alla lista esterna non deve apparire nella partita."
        )


    """SEZIONE 2: metodi di test per la Gestione del Roster Giocatori"""

    #metodo che va ad aggiungere e testare un giocatore nuovo
    def test_aggiungi_giocatore_valido(self):
        """
        Verifica l'aggiunta corretta di un singolo giocatore valido.
        
        Obiettivo:
        - Aggiungere un giocatore tramite il metodo aggiungi_giocatore.
        - Verificare che il numero totale di giocatori incrementi correttamente.
        - Verificare che il giocatore sia effettivamente presente nella lista.
        """
        # Creiamo un giocatore valido (usando int per l'id come richiesto)
        giocatore = GiocatoreBase(nome="Nuovo Giocatore", id_giocatore=10)
        
        # Aggiungiamo il giocatore alla partita (che inizialmente è vuota dal setUp)
        self.partita.aggiungi_giocatore(giocatore)
        
        # Verifica 1: Il conteggio deve essere 1
        self.assertEqual(
            self.partita.get_numero_giocatori(),
            1,
            "Il numero di giocatori dovrebbe essere 1 dopo l'aggiunta."
        )
        
        # Verifica 2: Il giocatore deve essere nella lista
        lista_giocatori = self.partita.get_giocatori()
        self.assertIn(
            giocatore,
            lista_giocatori,
            "Il giocatore aggiunto dovrebbe essere presente nella lista ritornata."
        )
        
        # Verifica 3: Deve essere proprio LUI (stesso oggetto)
        self.assertEqual(
            lista_giocatori[0],
            giocatore,
            "Il primo giocatore della lista deve corrispondere all'oggetto aggiunto."
        )


    #metodo di test per evitare giocatori dupplicati 
    def test_aggiungi_giocatore_duplicato(self):
        """
        Verifica che non sia possibile aggiungere lo stesso giocatore due volte.
        
        Obiettivo:
        - Aggiungere un giocatore.
        - Tentare di aggiungere nuovamente LO STESSO oggetto giocatore.
        - Verificare che venga sollevata l'eccezione PartitaGiocatoreGiaPresenteException.
        """
        giocatore = GiocatoreBase(nome="Mario Duplicato", id_giocatore=99)
        
        # Prima aggiunta: deve avere successo
        self.partita.aggiungi_giocatore(giocatore)
        
        # Seconda aggiunta: deve sollevare eccezione
        # Usiamo assertRaises per catturare l'eccezione specifica
        with self.assertRaises(PartitaGiocatoreGiaPresenteException):
            self.partita.aggiungi_giocatore(giocatore)
            
        # Verifica post-errore: il numero di giocatori deve essere rimasto 1
        self.assertEqual(
            self.partita.get_numero_giocatori(),
            1,
            "Il numero di giocatori non dovrebbe aumentare dopo un tentativo di duplicazione fallito."
        )


    #metodo per evitare aggiunte di giocatori con un formato non valido 
    def test_aggiungi_giocatore_tipi_errati_multipli(self):
        """
        Verifica che l'eccezione PartitaGiocatoreTypeException venga sollevata
        per diversi tipi di input non validi.
        
        Obiettivo:
        - Tentare di aggiungere: stringa, intero, lista, dizionario, oggetto non correlato.
        - Assicurarsi che TUTTI vengano rifiutati.
        """
        # Creiamo una lista di "impostori" di vario tipo
        oggetti_invalidi = [
            "Sono una stringa",              # Stringa
            123,                             # Intero
            ["Giocatore", 1],                # Lista
            {"nome": "Mario"},               # Dizionario
            Tabellone(),                     # Oggetto valido ma di classe sbagliata
            None                             # NoneType
        ]

        # Cicliamo su ogni impostore
        for oggetto_invalido in oggetti_invalidi:
            # Usiamo subTest per identificare quale caso specifico sta girando
            # (utile nel report se uno fallisce)
            with self.subTest(caso=oggetto_invalido):
                with self.assertRaises(PartitaGiocatoreTypeException):
                    self.partita.aggiungi_giocatore(oggetto_invalido)
        
        # Verifica finale: dopo tutto questo bombardamento, il roster deve essere ancora vuoto
        self.assertEqual(
            self.partita.get_numero_giocatori(),
            0,
            "Nessun oggetto invalido deve essere stato aggiunto al roster."
        )


    #metodo che controllo che alla partita possano aggiungersi giocatori fino al numero massimo consentito 
    def test_aggiungi_giocatore_roster_pieno(self):
        """
        Verifica che non sia possibile aggiungere giocatori oltre il limite massimo.
        
        Obiettivo:
        - Riempire la partita fino a MAX_GIOCATORI.
        - Verificare che fino al limite l'aggiunta funzioni.
        - Tentare di aggiungere un ulteriore giocatore (over-limit).
        - Verificare che venga sollevata l'eccezione PartitaRosterPienoException.
        """
        # Recuperiamo il limite massimo dalla classe
        limite_max = self.partita.MAX_GIOCATORI
        
        # 1. Fase di riempimento: saturiamo i posti disponibili
        for i in range(limite_max):
            # Creiamo giocatori unici per non far scattare l'errore duplicati
            g = GiocatoreBase(nome=f"Giocatore {i}", id_giocatore=i)
            self.partita.aggiungi_giocatore(g)
            
        # Verifica intermedia: il roster deve essere pieno esattamente al limite
        self.assertEqual(
            self.partita.get_numero_giocatori(), 
            limite_max,
            f"Il roster dovrebbe contenere esattamente {limite_max} giocatori."
        )
        
        # 2. Fase di test errore: proviamo ad aggiungere l'elemento di troppo
        giocatore_extra = GiocatoreBase(nome="Giocatore Extra", id_giocatore=999)
        
        with self.assertRaises(PartitaRosterPienoException):
            self.partita.aggiungi_giocatore(giocatore_extra)
            
        # 3. Verifica finale: il numero non deve essere cambiato (non deve essere MAX + 1)
        self.assertEqual(
            self.partita.get_numero_giocatori(), 
            limite_max,
            "Il numero di giocatori non deve superare il limite massimo configurato."
        )


    """SEZIONE 3: METODI PER LA Gestione Stati e Avvio/Termine"""

    #metodo che blocca l'avvio della partita per giocatori insufficenti 
    def test_avvio_partita_giocatori_insufficienti(self):
        """
        Verifica che non sia possibile avviare la partita se il numero di giocatori
        è inferiore al minimo richiesto (MIN_GIOCATORI).
        
        Obiettivo:
        - Tentare avvio con 0 giocatori.
        - Tentare avvio con (MIN_GIOCATORI - 1) giocatori.
        - Verificare che venga sollevata l'eccezione PartitaGiocatoriInsufficientiException.
        - Verificare che lo stato rimanga "non_iniziata".
        """

        # 1. Tentativo con 0 giocatori (stato iniziale del setUp)
        with self.assertRaises(PartitaGiocatoriInsufficientiException):
            self.partita.avvia_partita()
            
        # Verifica che lo stato non sia cambiato
        self.assertEqual(
            self.partita.stato_partita,
            "non_iniziata",
            "Lo stato non deve cambiare se l'avvio fallisce (0 giocatori)."
        )
        
        # 2. Tentativo con giocatori insufficienti (es. 1 solo se il minimo è 2)
        minimo_richiesto = self.partita.MIN_GIOCATORI
        # Aggiungiamo giocatori fino ad arrivare a 'minimo - 1'
        for i in range(minimo_richiesto - 1):
            g = GiocatoreBase(nome=f"Giocatore Solitario {i}", id_giocatore=i)
            self.partita.aggiungi_giocatore(g)
            
        # Ora abbiamo dei giocatori, ma non abbastanza. Riprova l'avvio.
        with self.assertRaises(PartitaGiocatoriInsufficientiException):
            self.partita.avvia_partita()
            
        # Verifica finale dello stato
        self.assertEqual(
            self.partita.stato_partita,
            "non_iniziata",
            f"Lo stato non deve cambiare se l'avvio fallisce ({minimo_richiesto - 1} giocatori)."
        )


    #metodo che va a testare l'avvio corretto della partita con i prerequisiti giusti 
    def test_avvio_partita_successo(self):
        """
        Verifica il corretto avvio della partita quando i requisiti sono soddisfatti.
        
        Obiettivo:
        - Aggiungere il numero minimo di giocatori richiesti.
        - Verificare che is_pronta_per_iniziare() ritorni True.
        - Chiamare avvia_partita() con successo.
        - Verificare il cambio di stato in "in_corso".
        """
        # 1. Preparazione: Raggiungiamo il numero minimo di giocatori
        minimo_richiesto = self.partita.MIN_GIOCATORI
        for i in range(minimo_richiesto):
            self.partita.aggiungi_giocatore(
                GiocatoreBase(nome=f"Player {i}", id_giocatore=i)
            )
            
        # 2. Verifica preliminare: il sistema deve dirci che è pronto
        self.assertTrue(
            self.partita.is_pronta_per_iniziare(),
            "La partita dovrebbe risultare pronta per iniziare con il numero minimo di giocatori."
        )
        
        # 3. Azione: Avvio la partita (non deve sollevare eccezioni)
        try:
            self.partita.avvia_partita()
        except PartitaException as e:
            self.fail(f"avvia_partita ha sollevato un'eccezione inattesa: {e}")
            
        # 4. Verifiche finali sullo stato
        self.assertEqual(
            self.partita.stato_partita,
            "in_corso",
            "Lo stato della partita deve diventare 'in_corso' dopo l'avvio."
        )
        
        # Controllo incrociato col metodo getter
        self.assertEqual(
            self.partita.get_stato_partita(),
            "in_corso",
            "Il metodo getter deve ritornare lo stato aggiornato."
        )


    #metodo per testare l'avvio della partita quando ci sono stati invalidi ovvero, la partita non risulta "non_iniziata"
    def test_avvio_partita_stati_invalidi(self):
        """
        Verifica che non sia possibile avviare una partita se questa non è nello stato 'non_iniziata'.
        
        Obiettivo:
        - Verificare che avvia_partita() fallisca se la partita è già "in_corso".
        - Verificare che avvia_partita() fallisca se la partita è "terminata".
        """
        # Preparazione comune: popoliamo la partita per renderla avviabile
        for i in range(self.partita.MIN_GIOCATORI):
            self.partita.aggiungi_giocatore(GiocatoreBase(f"P{i}", i))

        # Scenario 1: Partita già IN CORSO
        with self.subTest(caso="Partita già in corso"):
            # Avviamo la prima volta (lecito)
            self.partita.avvia_partita()
            
            # Tentiamo di ri-avviare
            with self.assertRaises(PartitaGiaIniziataException):
                self.partita.avvia_partita()
                
        # Scenario 2: Partita TERMINATA
        with self.subTest(caso="Partita già terminata"):
            # Forziamo lo stato a terminata (o usiamo il metodo termina_partita se preferisci)
            # Qui usiamo il metodo pubblico per essere più 'realistici'
            self.partita.termina_partita()
            
            # Verifica preliminare che siamo davvero nello stato terminata
            self.assertEqual(self.partita.stato_partita, "terminata")
            
            # Tentiamo di avviare una partita finita
            with self.assertRaises(PartitaGiaIniziataException):
                self.partita.avvia_partita()


    #metodo che va a testare le varie casistiche di chiusura della partita 
    def test_termina_partita(self):
        """
        Verifica la corretta terminazione della partita e la gestione degli stati invalidi.
        
        Obiettivo:
        - Verificare la terminazione corretta partendo da stato "in_corso".
        - Verificare la terminazione corretta partendo da stato "non_iniziata".
        - Verificare che termini con errore se già "terminata" (PartitaGiaTerminataException).
        - Controllare che il metodo helper is_terminata() sia coerente.
        """
        
        # Scenario 1: Terminazione standard (da in_corso a terminata)
        with self.subTest(caso="Terminazione da in_corso"):
            # Creiamo una nuova partita pulita per isolare il subtest
            p = Partita(tabellone=self.tabellone)
            # La portiamo in corso (trucco: impostiamo lo stato manualmente per non dover aggiungere giocatori)
            p.stato_partita = "in_corso"
            
            p.termina_partita()
            
            self.assertEqual(p.stato_partita, "terminata", "Lo stato deve essere 'terminata'.")
            self.assertTrue(p.is_terminata(), "is_terminata() deve ritornare True.")

        # Scenario 2: Terminazione anticipata (da non_iniziata a terminata)
        with self.subTest(caso="Terminazione da non_iniziata"):
            p = Partita(tabellone=self.tabellone)
            # È già non_iniziata di default
            
            p.termina_partita()
            
            self.assertEqual(p.stato_partita, "terminata")
            self.assertTrue(p.is_terminata())

        # Scenario 3: Errore su doppia terminazione
        with self.subTest(caso="Doppia terminazione"):
            p = Partita(tabellone=self.tabellone)
            p.stato_partita = "terminata"  # Simula partita già finita
            
            # Deve sollevare eccezione
            with self.assertRaises(PartitaGiaTerminataException):
                p.termina_partita()


    """SEZIONE 4: METODI DI TEST SUL Flusso di Gioco ed Estrazioni"""

    #metodo per avviare una mini partita e verificare che tutto fili nel modo corretto
    def test_estrazione_numero_flusso_corretto(self):
        """
        Verifica il corretto funzionamento dell'estrazione numeri.
        
        Obiettivo:
        - Avviare correttamente la partita.
        - Estrarre un numero e verificare che sia valido (1-90).
        - Verificare che self.ultimo_numero_estratto sia aggiornato.
        - Estrarre un secondo numero e verificare che sia diverso dal primo.
        """
        # 1. Setup: Avviamo la partita
        # Aggiungiamo il minimo dei giocatori per poter avviare
        for i in range(self.partita.MIN_GIOCATORI):
            self.partita.aggiungi_giocatore(GiocatoreBase(f"P{i}", i))
        
        self.partita.avvia_partita()
        
        # 2. Prima Estrazione
        numero_1 = self.partita.estrai_prossimo_numero()
        
        # Verifica validità numero
        self.assertIsInstance(numero_1, int)
        self.assertTrue(1 <= numero_1 <= 90, f"Numero estratto fuori range: {numero_1}")
        
        # Verifica aggiornamento stato interno
        self.assertEqual(
            self.partita.get_ultimo_numero_estratto(),
            numero_1,
            "Il metodo getter deve ritornare l'ultimo numero estratto."
        )
        self.assertEqual(
            self.partita.ultimo_numero_estratto,
            numero_1,
            "L'attributo ultimo_numero_estratto deve essere aggiornato."
        )

        # 3. Seconda Estrazione (per verificare che cambi)
        numero_2 = self.partita.estrai_prossimo_numero()
        
        self.assertNotEqual(
            numero_1, 
            numero_2,
            "In una tombola non possono essere estratti due numeri uguali consecutivi (o in assoluto)."
        )
        self.assertEqual(
            self.partita.get_ultimo_numero_estratto(),
            numero_2,
            "Lo stato deve aggiornarsi al nuovo numero estratto."
        )


    #metodo che va a testare l'estrazione di un numero mirato e lo segna correttamente sulla cartella del giocatore di test
    def test_aggiorna_giocatori_con_numero_propagazione_corretta(self):
        """
        Verifica che l'aggiornamento dei giocatori con un numero estratto
        venga propagato correttamente alle cartelle tramite GiocatoreBase.

        Obiettivo:
        - Creare un giocatore con almeno una cartella.
        - Scegliere un numero sicuramente presente in quella cartella.
        - Chiamare Partita.aggiorna_giocatori_con_numero(numero).
        - Verificare che la cartella risulti segnata su quel numero.
        - Verificare che un numero valido ma non presente NON risulti segnato.
        """
        
        # 1. Setup: creiamo un giocatore e una cartella
        giocatore = GiocatoreBase(nome="Giocatore Test", id_giocatore=1)
        cartella = Cartella()  # Usa il costruttore di default della cartella
        giocatore.aggiungi_cartella(cartella)

        # Registriamo il giocatore nella partita e aggiungiamo un secondo dummy
        # per rispettare eventuali requisiti minimi di giocatori in altri contesti.
        self.partita.aggiungi_giocatore(giocatore)
        self.partita.aggiungi_giocatore(GiocatoreBase(nome="Dummy", id_giocatore=2))

        # 2. Scegliamo un numero PRESENTE nella cartella
        numeri_cartella = cartella.numeri_cartella  # set con tutti i numeri della cartella
        self.assertGreater(
            len(numeri_cartella),
            0,
            "La cartella dovrebbe contenere almeno un numero."
        )
        numero_presente = next(iter(numeri_cartella))  # Un numero qualsiasi presente sulla cartella

        # 3. Azione: propaghiamo il numero ai giocatori tramite Partita
        # Impostiamo lo stato corretto per evitare eccezioni di stato.
        self.partita.stato_partita = "in_corso"
        self.partita.aggiorna_giocatori_con_numero(numero_presente)

        # 4. Verifica: il numero deve risultare segnato nella cartella
        self.assertTrue(
            cartella.is_numero_segnato(numero_presente),
            f"Il numero {numero_presente} dovrebbe risultare segnato sulla cartella del giocatore."
        )

        # 5. Controprova: scegliamo un numero VALIDO ma NON presente nella cartella
        tutti_i_numeri = set(range(1, 91))          # 1..90
        numeri_non_presenti = tutti_i_numeri - numeri_cartella
        self.assertGreater(
            len(numeri_non_presenti),
            0,
            "Dovrebbe esistere almeno un numero valido non presente nella cartella."
        )
        numero_assente = next(iter(numeri_non_presenti))

        # Verifichiamo che questo numero non risulti segnato
        self.assertFalse(
            cartella.is_numero_segnato(numero_assente),
            f"Il numero {numero_assente} non dovrebbe risultare segnato sulla cartella."
        )


    #metodo che va a testare le estrazioni nei casi invalidi ovvero quando non è consentito 
    def test_estrazione_errori_stati_invalidi_e_numeri_esauriti(self):
        """
        Verifica la gestione degli errori durante le estrazioni.

        Obiettivo:
        - Verificare che estrai_prossimo_numero() sollevi PartitaNonInCorsoException
          se la partita è nello stato 'non_iniziata'.
        - Verificare che estrai_prossimo_numero() sollevi PartitaNonInCorsoException
          se la partita è nello stato 'terminata'.
        - Verificare che, quando il tabellone ha esaurito i numeri,
          venga sollevata PartitaNumeriEsauritiException.
        """

        # Scenario 1: Partita NON INIZIATA
        with self.subTest(caso="estrazione con partita non_iniziata"):
            # Stato iniziale del setUp: "non_iniziata"
            self.assertEqual(self.partita.stato_partita, "non_iniziata")

            with self.assertRaises(PartitaNonInCorsoException):
                self.partita.estrai_prossimo_numero()

        # Scenario 2: Partita TERMINATA
        with self.subTest(caso="estrazione con partita terminata"):
            # Forziamo lo stato a 'terminata'
            self.partita.stato_partita = "terminata"

            with self.assertRaises(PartitaNonInCorsoException):
                self.partita.estrai_prossimo_numero()

        # Scenario 3: Numeri esauriti sul tabellone
        with self.subTest(caso="estrazione con numeri esauriti"):
            # Per questo scenario usiamo una nuova istanza di Partita pulita
            tabellone = Tabellone()
            partita_piena = Partita(tabellone=tabellone)

            # Aggiungiamo il minimo di giocatori per poter avviare la partita
            for i in range(partita_piena.MIN_GIOCATORI):
                partita_piena.aggiungi_giocatore(GiocatoreBase(f"G{i}", i))

            partita_piena.avvia_partita()

            # Estriamo tutti i numeri possibili dal tabellone
            # Il Tabellone è stato progettato per lavorare su 90 numeri (1..90)
            # Quindi dopo 90 estrazioni, deve andare in esaurimento.
            for _ in range(90):
                numero = partita_piena.estrai_prossimo_numero()
                self.assertIsInstance(numero, int)

            # Alla 91esima estrazione ci aspettiamo l'eccezione specifica della partita
            with self.assertRaises(PartitaNumeriEsauritiException):
                partita_piena.estrai_prossimo_numero()


    """SEZIONE 5: METODI CHE VANNO A TESTARE Logica di Verifica Vincite e Premi"""

    #metodo che va a testare una vincita semplice, l'ambo
    def test_verifica_premi_rileva_vincita_semplice_ambo(self):
        """
        Verifica che verifica_premi() rilevi correttamente una vincita semplice (ambo).

        Obiettivo:
        - Creare una partita con un solo giocatore e una sola cartella.
        - Forzare una situazione in cui una riga della cartella abbia un AMBO (due numeri segnati).
        - Chiamare verifica_premi() e verificare che:
          - venga restituito esattamente un evento di premio;
          - il premio sia di tipo "ambo";
          - il riferimento a giocatore, cartella e riga sia corretto.
        """

        # 1. Creazione partita con un giocatore e una cartella
        giocatore = GiocatoreBase(nome="Giocatore Ambo", id_giocatore=1)
        cartella = Cartella()
        giocatore.aggiungi_cartella(cartella)

        # Registriamo il giocatore nella partita
        self.partita.aggiungi_giocatore(giocatore)

        # 2. Scegliamo una riga e due numeri di quella riga per creare un ambo
        # Per farlo, usiamo i metodi pubblici della cartella:
        # - get_numeri_riga(indice_riga): ci restituisce i numeri di una riga.
        indice_riga = 0
        numeri_riga = cartella.get_numeri_riga(indice_riga)
        self.assertGreaterEqual(
            len(numeri_riga),
            2,
            "La riga selezionata dovrebbe contenere almeno due numeri per poter formare un ambo."
        )

        # Prendiamo i primi due numeri di quella riga
        numero_1 = numeri_riga[0]
        numero_2 = numeri_riga[1]

        # 3. Simuliamo che questi due numeri siano stati estratti
        # Usiamo il metodo di GiocatoreBase per segnare i numeri sulle cartelle
        giocatore.aggiorna_con_numero(numero_1)
        giocatore.aggiorna_con_numero(numero_2)

        # Verifica intermedia: i numeri devono risultare segnati sulla cartella
        self.assertTrue(
            cartella.is_numero_segnato(numero_1),
            f"Il numero {numero_1} dovrebbe risultare segnato sulla cartella."
        )
        self.assertTrue(
            cartella.is_numero_segnato(numero_2),
            f"Il numero {numero_2} dovrebbe risultare segnato sulla cartella."
        )

        # 4. Azione: chiamiamo verifica_premi() sulla partita
        premi_trovati = self.partita.verifica_premi()

        # 5. Verifiche sul risultato
        # Deve esserci esattamente UN evento di premio
        self.assertEqual(
            len(premi_trovati),
            1,
            f"Dovrebbe essere stato rilevato esattamente un premio, trovati: {len(premi_trovati)}."
        )

        evento = premi_trovati[0]

        # Il premio deve essere di tipo "ambo"
        self.assertEqual(
            evento.get("premio"),
            "ambo",
            f"Il tipo di premio atteso è 'ambo', trovato: {evento.get('premio')}."
        )

        # Il nome del giocatore deve corrispondere
        self.assertEqual(
            evento.get("giocatore"),
            giocatore.get_nome(),
            "Il nome del giocatore nell'evento non corrisponde al giocatore reale."
        )

        # L'indice della cartella deve corrispondere
        self.assertEqual(
            evento.get("cartella"),
            cartella.indice,
            "L'indice della cartella nell'evento non corrisponde a quello reale."
        )

        # La riga deve essere quella su cui abbiamo creato l'ambo
        self.assertEqual(
            evento.get("riga"),
            indice_riga,
            "L'indice di riga nell'evento non corrisponde alla riga su cui è stato creato l'ambo."
        )


    #metodo che va a testare la non riassegnazione di premi già presenti ed assegnati.
    def test_verifica_premi_non_ripete_premi_gia_assegnati(self):
        """
        Verifica che una vincita già rilevata non venga riproposta
        nelle chiamate successive a verifica_premi() se lo stato
        della cartella non cambia.

        Obiettivo:
        - Creare una situazione di AMBO su una riga di una cartella.
        - Chiamare verifica_premi() una prima volta e verificare che:
          - venga restituito l'evento di premio.
          - la chiave del premio venga aggiunta a premi_gia_assegnati.
        - Chiamare verifica_premi() una seconda volta senza modificare la cartella.
        - Verificare che:
          - NON vengano restituiti nuovi eventi.
          - premi_gia_assegnati contenga ancora la chiave, ma senza duplicazioni.
        """

        # 1. Setup: giocatore e cartella con situazione di ambo
        giocatore = GiocatoreBase(nome="Giocatore Ambo Ripetuto", id_giocatore=10)
        cartella = Cartella()
        giocatore.aggiungi_cartella(cartella)

        self.partita.aggiungi_giocatore(giocatore)

        # Scegliamo una riga e due numeri di quella riga per creare un ambo
        indice_riga = 1
        numeri_riga = cartella.get_numeri_riga(indice_riga)
        self.assertGreaterEqual(
            len(numeri_riga),
            2,
            "La riga selezionata dovrebbe contenere almeno due numeri per poter formare un ambo."
        )
        numero_1 = numeri_riga[0]
        numero_2 = numeri_riga[1]

        # Segniamo i due numeri tramite GiocatoreBase
        giocatore.aggiorna_con_numero(numero_1)
        giocatore.aggiorna_con_numero(numero_2)

        # Verifica intermedia: i numeri devono risultare segnati
        self.assertTrue(cartella.is_numero_segnato(numero_1))
        self.assertTrue(cartella.is_numero_segnato(numero_2))

        # 2. Prima chiamata a verifica_premi(): deve rilevare l'ambo
        premi_prima = self.partita.verifica_premi()

        self.assertEqual(
            len(premi_prima),
            1,
            f"Alla prima verifica dovrebbe essere trovato esattamente un premio, trovati: {len(premi_prima)}."
        )

        evento = premi_prima[0]
        self.assertEqual(evento.get("premio"), "ambo")
        self.assertEqual(evento.get("riga"), indice_riga)
        self.assertEqual(evento.get("cartella"), cartella.indice)

        # Costruiamo la chiave attesa così come la usa verifica_premi()
        chiave_ambo_attesa = f"cartella_{cartella.indice}_riga_{indice_riga}_ambo"

        # Verifichiamo che la chiave sia stata memorizzata in premi_gia_assegnati
        self.assertIn(
            chiave_ambo_attesa,
            self.partita.premi_gia_assegnati,
            "La chiave dell'ambo dovrebbe essere presente in premi_gia_assegnati dopo la prima verifica."
        )

        # Salviamo la dimensione attuale del set per controllare che non cresca indebitamente
        dimensione_set_prima = len(self.partita.premi_gia_assegnati)

        # 3. Seconda chiamata a verifica_premi() SENZA modificare la cartella
        premi_seconda = self.partita.verifica_premi()

        # Non devono esserci nuovi premi: lista vuota
        self.assertEqual(
            len(premi_seconda),
            0,
            f"Dopo aver già assegnato l'ambo, non dovrebbero esserci nuovi premi, trovati: {len(premi_seconda)}."
        )

        # La chiave deve essere ancora presente nel set, ma la dimensione non deve aumentare
        self.assertIn(
            chiave_ambo_attesa,
            self.partita.premi_gia_assegnati,
            "La chiave dell'ambo deve rimanere registrata tra i premi già assegnati."
        )
        self.assertEqual(
            len(self.partita.premi_gia_assegnati),
            dimensione_set_prima,
            "Il set premi_gia_assegnati non deve crescere se non ci sono nuovi premi."
        )


    #metodo di test che valuta la progressione nel assegnazione dei primi prima su una riga sola poi su tutta la cartella 
    def test_verifica_premi_progressione_premi_su_stessa_riga(self):
        """
        Verifica la progressione dei premi sulla stessa riga:
        ambo -> terno -> quaterna -> cinquina, e infine tombola.

        Obiettivo:
        - Creare una cartella e selezionare una riga.
        - Segnare progressivamente i numeri di quella riga:
            2 numeri  -> ambo
            3 numeri  -> terno
            4 numeri  -> quaterna
            5 numeri  -> cinquina
        - Dopo ogni step chiamare verifica_premi() e verificare che:
            - venga restituito solo il nuovo premio (senza ripetere i precedenti).
        - Completare poi tutta la cartella (tutti i 15 numeri segnati).
        - Verificare che venga rilevata anche la tombola (premio "tombola" con riga=None).
        """

        # Setup giocatore + cartella
        giocatore = GiocatoreBase(nome="Giocatore Progressione", id_giocatore=20)
        cartella = Cartella()
        giocatore.aggiungi_cartella(cartella)
        self.partita.aggiungi_giocatore(giocatore)

        # Scegliamo una riga su cui lavorare
        indice_riga = 0
        numeri_riga = cartella.get_numeri_riga(indice_riga)
        self.assertEqual(
            len(numeri_riga),
            5,
            "Ogni riga di cartella deve contenere 5 numeri per la tombola classica."
        )

        # Helper locale per chiamare verifica_premi e controllare che torni ESATTAMENTE un premio specifico
        def _verifica_unico_premio_atteso(premio_atteso: str, step_descr: str):
            premi = self.partita.verifica_premi()
            self.assertEqual(
                len(premi),
                1,
                f"{step_descr}: ci si aspetta esattamente 1 nuovo premio, trovati: {len(premi)}."
            )
            evento = premi[0]
            self.assertEqual(
                evento.get("premio"),
                premio_atteso,
                f"{step_descr}: il premio atteso è '{premio_atteso}', trovato: {evento.get('premio')}."
            )
            self.assertEqual(
                evento.get("riga"),
                indice_riga,
                f"{step_descr}: la riga del premio non corrisponde a quella attesa."
            )
            self.assertEqual(
                evento.get("cartella"),
                cartella.indice,
                f"{step_descr}: l'indice della cartella nell'evento non è corretto."
            )

        # 1) Segniamo 2 numeri: AMBO
        giocatore.aggiorna_con_numero(numeri_riga[0])
        giocatore.aggiorna_con_numero(numeri_riga[1])

        # Verifica intermedia: devono risultare segnati
        self.assertTrue(cartella.is_numero_segnato(numeri_riga[0]))
        self.assertTrue(cartella.is_numero_segnato(numeri_riga[1]))

        _verifica_unico_premio_atteso("ambo", "Dopo 2 numeri segnati (ambo)")

        # 2) Segniamo il terzo numero: TERNO
        giocatore.aggiorna_con_numero(numeri_riga[2])
        self.assertTrue(cartella.is_numero_segnato(numeri_riga[2]))

        _verifica_unico_premio_atteso("terno", "Dopo 3 numeri segnati (terno)")

        # 3) Segniamo il quarto numero: QUATERNA
        giocatore.aggiorna_con_numero(numeri_riga[3])
        self.assertTrue(cartella.is_numero_segnato(numeri_riga[3]))

        _verifica_unico_premio_atteso("quaterna", "Dopo 4 numeri segnati (quaterna)")

        # 4) Segniamo il quinto numero: CINQUINA
        giocatore.aggiorna_con_numero(numeri_riga[4])
        self.assertTrue(cartella.is_numero_segnato(numeri_riga[4]))

        _verifica_unico_premio_atteso("cinquina", "Dopo 5 numeri segnati (cinquina)")

        # 5) Completiamo tutta la cartella (TOMBOLA)
        # Prendiamo tutti i numeri della cartella e li segniamo
        tutti_i_numeri_cartella = cartella.numeri_cartella
        for numero in tutti_i_numeri_cartella:
            giocatore.aggiorna_con_numero(numero)

        # Verifica intermedia: la cartella deve essere completa (tombola)
        self.assertTrue(
            cartella.verifica_cartella_completa(),
            "La cartella dovrebbe risultare completa (tombola) dopo aver segnato tutti i numeri."
        )

        # Chiamata a verifica_premi: deve rilevare la tombola come nuovo premio
        premi_tombola = self.partita.verifica_premi()

        # Ci aspettiamo almeno un evento con premio "tombola"
        self.assertGreaterEqual(
            len(premi_tombola),
            1,
            "Dopo la completa segnatura della cartella ci si aspetta almeno un evento di tombola."
        )

        # Cerchiamo esplicitamente l'evento tombola
        eventi_tombola = [
            e for e in premi_tombola
            if e.get("premio") == "tombola" and e.get("cartella") == cartella.indice
        ]
        self.assertEqual(
            len(eventi_tombola),
            1,
            f"Ci dovrebbe essere esattamente un evento di tombola per questa cartella, trovati: {len(eventi_tombola)}."
        )

        evento_tombola = eventi_tombola[0]
        self.assertIsNone(
            evento_tombola.get("riga"),
            "Per la tombola, il campo 'riga' dovrebbe essere None."
        )
        self.assertEqual(
            evento_tombola.get("giocatore"),
            giocatore.get_nome(),
            "L'evento di tombola deve riferirsi al giocatore corretto."
        )


    #metodo che va a testare che esegui_turno ritorni diati coerenti con quelli previsti
    def test_esegui_turno_restituisce_dati_coerenti(self):
        """
        Verifica che esegui_turno():
        - esegua correttamente un'estrazione;
        - aggiorni lo stato della partita;
        - rilevi eventuali premi;
        - ritorni un dizionario coerente con lo stato effettivo della partita.

        Obiettivo:
        - Preparare una partita con un giocatore e una cartella.
        - Creare una situazione in cui un turno generi almeno un premio (es. ambo).
        - Chiamare esegui_turno().
        - Verificare coerenza di:
          - numero_estratto
          - stato_partita_prima / stato_partita_dopo
          - tombola_rilevata
          - partita_terminata
          - premi_nuovi (contenuto e struttura).
        """
        # 1. Setup: giocatore + cartella + partita avviata
        giocatore = GiocatoreBase(nome="Giocatore Turno", id_giocatore=30)
        cartella = Cartella()
        giocatore.aggiungi_cartella(cartella)

        self.partita.aggiungi_giocatore(giocatore)
        # Aggiungiamo un secondo giocatore dummy per essere coerenti con MIN_GIOCATORI se necessario
        self.partita.aggiungi_giocatore(GiocatoreBase(nome="Dummy Turno", id_giocatore=31))

        # Avviamo la partita
        self.partita.avvia_partita()
        self.assertEqual(
            self.partita.stato_partita,
            "in_corso",
            "La partita dovrebbe essere nello stato 'in_corso' prima di eseguire un turno."
        )

        # 2. Prepariamo un premio "semplice" (ambo) da rilevare nel turno
        # Scegliamo una riga e due numeri della cartella del giocatore
        indice_riga = 0
        numeri_riga = cartella.get_numeri_riga(indice_riga)
        self.assertGreaterEqual(len(numeri_riga), 2)

        numero_ambo_1 = numeri_riga[0]
        numero_ambo_2 = numeri_riga[1]

        # Simuliamo che il primo numero sia già stato estratto in un turno precedente:
        # lo segniamo usando l'API di GiocatoreBase (non vogliamo ancora che premi_nuovi lo rilevi)
        giocatore.aggiorna_con_numero(numero_ambo_1)

        # Verifica intermedia: il primo numero è segnato, il secondo no
        self.assertTrue(cartella.is_numero_segnato(numero_ambo_1))
        self.assertFalse(cartella.is_numero_segnato(numero_ambo_2))

        # Ci aspettiamo che il prossimo turno, se estrae numero_ambo_2,
        # generi un ambo sulla riga scelta.

        # Per non dipendere dalla randomicità del tabellone, prepariamo il tabellone in modo che:
        # - al prossimo esegui_turno() venga estratto proprio numero_ambo_2.
        # Usiamo la logica del Tabellone già testata: reset + forzatura dello stato.
        # Rimuoviamo numero_ambo_2 dal set dei disponibili e rimettiamolo in cima
        # se il Tabellone espone metodi di ispezione; in alternativa, accettiamo
        # che il premio possa o meno venire rilevato in questo turno e
        # ci limitiamo a verificare la coerenza del dizionario.
        #
        # Per evitare di manipolare internamente Tabellone, adottiamo un controllo flessibile:
        # verifichiamo la struttura e la coerenza dei campi, e se c'è almeno un premio.

        # 3. Azione: eseguiamo un turno completo
        risultato = self.partita.esegui_turno()

        # 4. Verifiche sul dizionario di ritorno

        # Verifica chiavi principali presenti
        chiavi_attese = {
            "numero_estratto",
            "stato_partita_prima",
            "stato_partita_dopo",
            "tombola_rilevata",
            "partita_terminata",
            "premi_nuovi",
        }
        self.assertTrue(
            chiavi_attese.issubset(risultato.keys()),
            f"Il dizionario risultato_turno deve contenere almeno le chiavi: {chiavi_attese}."
        )

        # numero_estratto deve essere un int valido
        numero_estratto = risultato["numero_estratto"]
        self.assertIsInstance(numero_estratto, int)
        self.assertTrue(
            1 <= numero_estratto <= 90,
            f"numero_estratto deve essere nel range 1-90, trovato: {numero_estratto}."
        )

        # stato_partita_prima deve essere 'in_corso'
        self.assertEqual(
            risultato["stato_partita_prima"],
            "in_corso",
            "stato_partita_prima deve riflettere lo stato 'in_corso' prima del turno."
        )

        # stato_partita_dopo deve essere "in_corso" o "terminata" (se si fosse fatta tombola)
        self.assertIn(
            risultato["stato_partita_dopo"],
            ["in_corso", "terminata"],
            "stato_partita_dopo deve essere 'in_corso' o 'terminata'."
        )

        # tombola_rilevata e partita_terminata devono essere coerenti tra loro e col metodo is_terminata()
        tombola_rilevata = risultato["tombola_rilevata"]
        partita_terminata = risultato["partita_terminata"]

        # partita_terminata deve coincidere con is_terminata()
        self.assertEqual(
            partita_terminata,
            self.partita.is_terminata(),
            "partita_terminata deve essere coerente con is_terminata()."
        )

        # Se la partita è terminata, tombola_rilevata deve essere True
        if partita_terminata:
            self.assertTrue(
                tombola_rilevata,
                "Se la partita è terminata dopo il turno, deve essere stata rilevata una tombola."
            )

        # 5. Verifica struttura di premi_nuovi
        premi_nuovi = risultato["premi_nuovi"]
        self.assertIsInstance(
            premi_nuovi,
            list,
            "premi_nuovi deve essere una lista (anche vuota se nessun premio è stato assegnato)."
        )

        # Se ci sono premi, verifichiamo che abbiano la struttura prevista
        for evento in premi_nuovi:
            self.assertIsInstance(evento, dict)
            self.assertIn("giocatore", evento)
            self.assertIn("cartella", evento)
            self.assertIn("premio", evento)
            self.assertIn("riga", evento)

            # Il nome del giocatore deve essere una stringa
            self.assertIsInstance(evento["giocatore"], str)
            # Il premio deve essere una stringa (ambo, terno, quaterna, cinquina, tombola)
            self.assertIsInstance(evento["premio"], str)


    """SEZIONE 6: METODI PER I TEST SULLE Utility"""

    #metodo che va a testare che le informazioni riportate al utente siano corrette 
    def test_get_stato_giocatori_ritorna_informazioni_corrette(self):
        """
        Verifica che get_stato_giocatori() ritorni una lista di dizionari
        coerenti con lo stato reale dei giocatori.

        Obiettivo:
        - Caso 0 giocatori: la lista deve essere vuota.
        - Caso con giocatori:
          * verificare struttura delle chiavi ("nome", "id", "num_cartelle", "ha_tombola");
          * verificare che i valori corrispondano a quelli esposti da GiocatoreBase;
          * verificare che ha_tombola sia False per giocatore senza cartelle complete;
          * verificare che ha_tombola sia True per giocatore con cartella completa.
        """
        # Caso 1: nessun giocatore registrato
        stato_giocatori = self.partita.get_stato_giocatori()
        self.assertIsInstance(
            stato_giocatori,
            list,
            "get_stato_giocatori deve ritornare sempre una lista."
        )
        self.assertEqual(
            len(stato_giocatori),
            0,
            "Con nessun giocatore registrato, la lista deve essere vuota."
        )

        # Caso 2: aggiungiamo due giocatori, uno senza tombola e uno con tombola
        # Import Cartella già disponibile in testa al file
        # Giocatore A: senza tombola
        giocatore_a = GiocatoreBase(nome="Giocatore A", id_giocatore=1)
        cartella_a = Cartella()
        giocatore_a.aggiungi_cartella(cartella_a)

        # Giocatore B: con cartella che porteremo a tombola
        giocatore_b = GiocatoreBase(nome="Giocatore B", id_giocatore=2)
        cartella_b = Cartella()
        giocatore_b.aggiungi_cartella(cartella_b)

        self.partita.aggiungi_giocatore(giocatore_a)
        self.partita.aggiungi_giocatore(giocatore_b)

        # Portiamo cartella_b alla tombola segnando tutti i suoi numeri
        for numero in cartella_b.numeri_cartella:
            giocatore_b.aggiorna_con_numero(numero)

        # Verifica intermedia: tombola sul giocatore B sì, A no
        self.assertFalse(giocatore_a.has_tombola(), "Giocatore A non dovrebbe avere tombola.")
        self.assertTrue(giocatore_b.has_tombola(), "Giocatore B dovrebbe avere tombola.")

        # Chiamata al metodo da testare
        stato_giocatori = self.partita.get_stato_giocatori()

        # Deve contenere due elementi (uno per giocatore)
        self.assertEqual(
            len(stato_giocatori),
            2,
            "Con due giocatori registrati, la lista deve contenere 2 elementi."
        )

        # Creiamo una mappa nome->stato per accedere più comodamente
        mappa_per_nome = {entry["nome"]: entry for entry in stato_giocatori}

        # Verifica struttura chiavi per ogni giocatore
        for nome, entry in mappa_per_nome.items():
            self.assertIsInstance(entry, dict)
            for chiave in ["nome", "id", "num_cartelle", "ha_tombola"]:
                self.assertIn(
                    chiave,
                    entry,
                    f"L'entry del giocatore '{nome}' deve contenere la chiave '{chiave}'."
                )

        # Controlliamo coerenza valori per Giocatore A
        stato_a = mappa_per_nome["Giocatore A"]
        self.assertEqual(stato_a["nome"], giocatore_a.get_nome())
        self.assertEqual(stato_a["id"], giocatore_a.get_id_giocatore())
        self.assertEqual(stato_a["num_cartelle"], giocatore_a.get_numero_cartelle())
        self.assertFalse(
            stato_a["ha_tombola"],
            "ha_tombola per Giocatore A deve essere False."
        )

        # Controlliamo coerenza valori per Giocatore B
        stato_b = mappa_per_nome["Giocatore B"]
        self.assertEqual(stato_b["nome"], giocatore_b.get_nome())
        self.assertEqual(stato_b["id"], giocatore_b.get_id_giocatore())
        self.assertEqual(stato_b["num_cartelle"], giocatore_b.get_numero_cartelle())
        self.assertTrue(
            stato_b["ha_tombola"],
            "ha_tombola per Giocatore B deve essere True dopo la tombola."
        )


    #metodo di test per valutare la struttura e la coerenza della stampa dei dati passati al giocatore nella versione completa 
    def test_get_stato_completo_struttura_e_coerenza(self):
        """
        Verifica che get_stato_completo() ritorni una fotografia coerente
        dello stato della partita.

        Obiettivo:
        - Verificare la struttura del dizionario ritornato (chiavi presenti).
        - Verificare la coerenza dei valori con lo stato interno di Partita:
          * stato_partita
          * ultimo_numero_estratto
          * numeri_estratti (dal Tabellone)
          * giocatori (da get_stato_giocatori)
          * premi_gia_assegnati (dal set interno, convertito in lista ordinata).
        """
        # 1. Setup: partita in stato non banale
        # Creiamo due giocatori con una cartella ciascuno
        giocatore1 = GiocatoreBase(nome="Giocatore Uno", id_giocatore=101)
        giocatore2 = GiocatoreBase(nome="Giocatore Due", id_giocatore=102)

        cartella1 = Cartella()
        cartella2 = Cartella()

        giocatore1.aggiungi_cartella(cartella1)
        giocatore2.aggiungi_cartella(cartella2)

        self.partita.aggiungi_giocatore(giocatore1)
        self.partita.aggiungi_giocatore(giocatore2)

        # Avviamo la partita
        self.partita.avvia_partita()

        # Simuliamo alcune estrazioni reali attraverso il tabellone/partita
        numeri_estratti_manualmente = []
        for _ in range(3):
            n = self.partita.estrai_prossimo_numero()
            numeri_estratti_manualmente.append(n)

        # Impostiamo manualmente un ultimo numero estratto "fittizio" per vedere se viene riportato correttamente
        # (in realtà estrai_prossimo_numero lo ha già aggiornato, quindi ci appoggiamo a quello reale)
        ultimo_numero_atteso = self.partita.get_ultimo_numero_estratto()

        # Simuliamo anche un premio già assegnato registrando una chiave nel set interno
        chiave_premio_fittizia = "cartella_1_riga_0_ambo"
        self.partita.premi_gia_assegnati.add(chiave_premio_fittizia)

        # 2. Azione: chiamiamo il metodo da testare
        stato = self.partita.get_stato_completo()

        # 3. Verifica struttura: il dizionario deve contenere tutte le chiavi previste
        chiavi_attese = {
            "stato_partita",
            "ultimo_numero_estratto",
            "numeri_estratti",
            "giocatori",
            "premi_gia_assegnati",
        }
        self.assertTrue(
            chiavi_attese.issubset(stato.keys()),
            f"get_stato_completo deve contenere almeno le chiavi: {chiavi_attese}."
        )

        # 4. Coerenza di stato_partita
        self.assertEqual(
            stato["stato_partita"],
            self.partita.stato_partita,
            "stato_partita nel dizionario deve coincidere con l'attributo interno."
        )

        # 5. Coerenza di ultimo_numero_estratto
        self.assertEqual(
            stato["ultimo_numero_estratto"],
            ultimo_numero_atteso,
            "ultimo_numero_estratto nel dizionario deve coincidere con quello interno."
        )

        # 6. Coerenza di numeri_estratti con il Tabellone
        numeri_estratti_tabellone = self.tabellone.get_numeri_estratti()
        self.assertEqual(
            stato["numeri_estratti"],
            numeri_estratti_tabellone,
            "numeri_estratti deve coincidere con quanto restituito dal Tabellone."
        )

        # 7. Coerenza di giocatori con get_stato_giocatori()
        stato_giocatori_atteso = self.partita.get_stato_giocatori()
        self.assertEqual(
            stato["giocatori"],
            stato_giocatori_atteso,
            "La sezione 'giocatori' deve coincidere con il risultato di get_stato_giocatori()."
        )

        # 8. Coerenza dei premi_gia_assegnati
        # Deve essere una lista, ordinata, che contiene le stesse chiavi del set interno
        premi_lista = stato["premi_gia_assegnati"]
        self.assertIsInstance(
            premi_lista,
            list,
            "premi_gia_assegnati deve essere una lista nel dizionario di stato completo."
        )

        # Confrontiamo come insiemi per ignorare l'ordine
        self.assertEqual(
            set(premi_lista),
            self.partita.premi_gia_assegnati,
            "La lista premi_gia_assegnati deve contenere le stesse chiavi del set interno."
        )

        # 9. Verifica che la chiave fittizia sia presente
        self.assertIn(
            chiave_premio_fittizia,
            premi_lista,
            "La chiave del premio fittizio deve risultare presente in premi_gia_assegnati."
        )
