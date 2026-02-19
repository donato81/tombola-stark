"""
Test per la classe GiocatoreBase del modulo bingo_game.players.giocatore_base.

Questa suite verifica:

- La corretta creazione di un GiocatoreBase con parametri validi e il
sollevamento delle eccezioni personalizzate in caso di valori non validi
(nome, id_giocatore).
- I metodi di identità get_nome() e get_id_giocatore(), che devono
restituire rispettivamente il nome e l'id del giocatore inizializzati.
- La gestione delle cartelle tramite aggiungi_cartella(), get_cartelle()
e get_numero_cartelle(), inclusa la validazione del tipo di cartella,
l'assegnazione automatica di nome e indice e l'aggiornamento del conteggio.
- L'aggiornamento delle cartelle rispetto ai numeri estratti con
aggiorna_con_numero(), che deve validare tipo e range del numero
(1-90) e propagare il numero valido a tutte le cartelle del giocatore.
- I metodi di stato complessivo get_stato_cartelle() e has_tombola(),
che devono rispettivamente aggregare gli stati delle singole cartelle
e indicare se almeno una cartella ha completato la tombola.
"""

# Importa il modulo unittest per la creazione dei test
import unittest
# Importa la classe GiocatoreBase e le eccezioni personalizzate
from bingo_game.players.giocatore_base import GiocatoreBase
# Importa la classe Cartella per creare cartelle di test
from bingo_game.cartella import Cartella
# Importa le eccezioni personalizzate per la validazione dei parametri
from bingo_game.exceptions import (
    GiocatoreNomeTypeException,
    GiocatoreNomeValueException,
    GiocatoreIdTypeException,
    GiocatoreCartellaTypeException,
    GiocatoreNumeroTypeException,
    GiocatoreNumeroValueException,
)

# Classe di test per GiocatoreBase
class TestGiocatoreBase(unittest.TestCase):
    """
    TestCase per verificare il comportamento della classe GiocatoreBase.

    Utilizza un'istanza di GiocatoreBase creata in setUp() come base per
    la maggior parte dei test, evitando ripetizioni di codice e
    mantenendo leggibile la suite di test.
    """

    """metodi della classe di test"""


        #metodo di setUp che viene eseguito prima di ogni metodo di test
    def setUp(self) -> None:
        """
        Prepara un'istanza standard di GiocatoreBase per i test.

        Crea un giocatore con nome valido e senza id esplicito, che
        verrà riutilizzato nei vari metodi di test.
        """
        self.giocatore = GiocatoreBase(nome="Giocatore di test")


    #metodo di test per la creazione del giocatore base e parametri invalidi
    def test_creazione_giocatore_base_e_parametri_invalidi(self) -> None:
        """
        Verifica la creazione corretta di GiocatoreBase con parametri validi
        e il sollevamento delle eccezioni personalizzate in caso di valori
        non validi per nome e id_giocatore.
        """
        # Caso valido: nome stringa non vuota, id_giocatore non specificato
        giocatore = GiocatoreBase(nome="Mario")
        self.assertIsInstance(giocatore, GiocatoreBase)
        self.assertEqual(giocatore.get_nome(), "Mario")
        self.assertIsNone(giocatore.get_id_giocatore())
        self.assertEqual(giocatore.get_numero_cartelle(), 0)

        # Nome: tipo non valido
        with self.assertRaises(GiocatoreNomeTypeException):
            GiocatoreBase(nome=123)  # type: ignore[arg-type]

        # Nome: stringa vuota o solo spazi
        with self.assertRaises(GiocatoreNomeValueException):
            GiocatoreBase(nome="")
        with self.assertRaises(GiocatoreNomeValueException):
            GiocatoreBase(nome="   ")

        # id_giocatore: tipo non valido
        with self.assertRaises(GiocatoreIdTypeException):
            GiocatoreBase(nome="Mario", id_giocatore="1")  # type: ignore[arg-type]
        with self.assertRaises(GiocatoreIdTypeException):
            GiocatoreBase(nome="Mario", id_giocatore=1.5)  # type: ignore[arg-type]

        # id_giocatore: valori validi (None e int)
        giocatore_con_id = GiocatoreBase(nome="Luigi", id_giocatore=1)
        self.assertEqual(giocatore_con_id.get_id_giocatore(), 1)


    #metodo di test per il flusso base di aggiunta cartelle
    def test_aggiungi_cartella_flusso_base(self) -> None:
        """
        Verifica il flusso base di gestione delle cartelle del giocatore.
        Controlla che:
        - all'inizio il giocatore non abbia cartelle;
        - dopo l'aggiunta di una cartella, il numero di cartelle e la lista
        interna siano aggiornati correttamente;
        - nome e indice vengano assegnati automaticamente come
        "Cartella 1", "Cartella 2", ecc. quando non sono presenti.
        """
        # All'inizio il giocatore non deve avere cartelle
        self.assertEqual(self.giocatore.get_numero_cartelle(), 0)
        self.assertEqual(self.giocatore.get_cartelle(), [])

        # Prima cartella senza nome e indice: verranno assegnati dal giocatore
        cartella1 = Cartella()
        self.giocatore.aggiungi_cartella(cartella1)

        self.assertEqual(self.giocatore.get_numero_cartelle(), 1)
        cartelle = self.giocatore.get_cartelle()
        self.assertEqual(len(cartelle), 1)
        self.assertIs(cartelle[0], cartella1)
        self.assertEqual(cartella1.nome, "Cartella 1")
        self.assertEqual(cartella1.indice, 1)

        # Seconda cartella, stessa logica
        cartella2 = Cartella()
        self.giocatore.aggiungi_cartella(cartella2)

        self.assertEqual(self.giocatore.get_numero_cartelle(), 2)
        cartelle = self.giocatore.get_cartelle()
        self.assertEqual(len(cartelle), 2)
        self.assertIs(cartelle[0], cartella1)
        self.assertIs(cartelle[1], cartella2)
        self.assertEqual(cartella2.nome, "Cartella 2")
        self.assertEqual(cartella2.indice, 2)



    #metodo per testare l'aggiunta di cartelle non valide 
    def test_aggiungi_cartella_tipo_non_valido(self) -> None:
        """
        Verifica che aggiungi_cartella() accetti solo oggetti Cartella.

        In caso di oggetto di tipo errato deve essere sollevata
        GiocatoreCartellaTypeException e lo stato interno del giocatore
        non deve essere modificato.
        """
        # All'inizio il giocatore non deve avere cartelle
        self.assertEqual(self.giocatore.get_numero_cartelle(), 0)

        # Oggetto di tipo int
        with self.assertRaises(GiocatoreCartellaTypeException):
            self.giocatore.aggiungi_cartella(42)  # type: ignore[arg-type]

        # Oggetto di tipo stringa
        with self.assertRaises(GiocatoreCartellaTypeException):
            self.giocatore.aggiungi_cartella("non sono una cartella")  # type: ignore[arg-type]

        # Oggetto di tipo None
        with self.assertRaises(GiocatoreCartellaTypeException):
            self.giocatore.aggiungi_cartella(None)  # type: ignore[arg-type]

        # Oggetto di tipo lista
        with self.assertRaises(GiocatoreCartellaTypeException):
            self.giocatore.aggiungi_cartella([])  # type: ignore[arg-type]

        # Dopo tutti i tentativi falliti, il giocatore non deve avere cartelle
        self.assertEqual(self.giocatore.get_numero_cartelle(), 0)
        self.assertEqual(self.giocatore.get_cartelle(), [])


    #metodo per testare la validazione del parametro in aggiorna_con_numero()
    def test_aggiorna_con_numero_validazione_parametro(self) -> None:
        """
        Verifica la validazione del parametro 'numero' in aggiorna_con_numero().
        Controlla che:
        - numeri non interi causino GiocatoreNumeroTypeException;
        - interi fuori dall'intervallo 1-90 causino GiocatoreNumeroValueException;
        - numeri interi validi (1-90) non sollevino eccezioni.
        """
        # Tipo non valido: float
        with self.assertRaises(GiocatoreNumeroTypeException):
            self.giocatore.aggiorna_con_numero(1.5)  # type: ignore[arg-type]

        # Tipo non valido: stringa
        with self.assertRaises(GiocatoreNumeroTypeException):
            self.giocatore.aggiorna_con_numero("10")  # type: ignore[arg-type]

        # Tipo non valido: None
        with self.assertRaises(GiocatoreNumeroTypeException):
            self.giocatore.aggiorna_con_numero(None)  # type: ignore[arg-type]

        # Valore fuori range: troppo basso (0)
        with self.assertRaises(GiocatoreNumeroValueException):
            self.giocatore.aggiorna_con_numero(0)

        # Valore fuori range: troppo alto (91)
        with self.assertRaises(GiocatoreNumeroValueException):
            self.giocatore.aggiorna_con_numero(91)

        # Valori al limite del range: 1 e 90 devono essere accettati
        try:
            self.giocatore.aggiorna_con_numero(1)
            self.giocatore.aggiorna_con_numero(90)
        except Exception as exc:  # pragma: no cover
            self.fail(f"aggiorna_con_numero() ha sollevato un'eccezione inattesa: {exc!r}")


    #metodo per testare il flusso base di aggiorna_con_numero()
    def test_aggiorna_con_numero_flusso_base(self) -> None:
        """
        Verifica il flusso base di aggiorna_con_numero() con numeri validi.

        Controlla che:
        - per ogni cartella del giocatore, si scelga un numero effettivamente
          presente in quella cartella;
        - il numero venga propagato tramite segna_numero() a tutte le cartelle;
        - dopo l'aggiornamento, il numero risulti segnato in ogni cartella che
          lo contiene, verificato con is_numero_segnato().
        """
        # Crea due cartelle e le assegna al giocatore
        cartella1 = Cartella()
        cartella2 = Cartella()
        self.giocatore.aggiungi_cartella(cartella1)
        self.giocatore.aggiungi_cartella(cartella2)

        # Verifica pre-condizione: il giocatore ha esattamente 2 cartelle
        self.assertEqual(self.giocatore.get_numero_cartelle(), 2)

        # Estrai i numeri presenti in ciascuna cartella
        numeri_cartella1 = cartella1.get_numeri_cartella()
        numeri_cartella2 = cartella2.get_numeri_cartella()

        # Scegli il primo numero da ciascuna cartella (numero che sappiamo
        # essere effettivamente presente)
        numero_da_segnare_1 = numeri_cartella1[0]
        numero_da_segnare_2 = numeri_cartella2[0]

        # Applica l'aggiornamento con il primo numero della prima cartella
        self.giocatore.aggiorna_con_numero(numero_da_segnare_1)

        # Verifica che il numero sia segnato nella prima cartella
        self.assertTrue(cartella1.is_numero_segnato(numero_da_segnare_1))

        # Se il numero è presente anche nella seconda cartella, deve essere segnato
        if numero_da_segnare_1 in numeri_cartella2:
            self.assertTrue(cartella2.is_numero_segnato(numero_da_segnare_1))

        # Applica l'aggiornamento con il primo numero della seconda cartella
        self.giocatore.aggiorna_con_numero(numero_da_segnare_2)

        # Verifica che il numero sia segnato nella seconda cartella
        self.assertTrue(cartella2.is_numero_segnato(numero_da_segnare_2))

        # Se il numero è presente anche nella prima cartella, deve essere segnato
        if numero_da_segnare_2 in numeri_cartella1:
            self.assertTrue(cartella1.is_numero_segnato(numero_da_segnare_2))



    #metodo per testare l'aggregazione corretta degli stati delle cartelle
    def test_get_stato_cartelle_aggregazione_corretta(self) -> None:
        """
        Verifica che get_stato_cartelle() aggreghi correttamente gli stati
        delle singole cartelle.

        Controlla che:
        - con zero cartelle, ritorni una lista vuota;
        - con una cartella, ritorni una lista con un dizionario di stato;
        - con più cartelle, ritorni una lista con tutti gli stati nell'ordine
          corretto e sincronizzati con lo stato interno di ogni cartella.
        """
        # Stato iniziale: nessuna cartella, get_stato_cartelle deve
        # ritornare una lista vuota
        stato_iniziale = self.giocatore.get_stato_cartelle()
        self.assertEqual(stato_iniziale, [])

        # Aggiungi la prima cartella
        cartella1 = Cartella()
        self.giocatore.aggiungi_cartella(cartella1)

        # Verifica che get_stato_cartelle ritorni esattamente uno stato
        stato_con_una = self.giocatore.get_stato_cartelle()
        self.assertEqual(len(stato_con_una), 1)

        # Verifica che lo stato corrisponda a quello della cartella1
        stato_cartella1_diretto = cartella1.get_stato_cartella()
        self.assertEqual(stato_con_una[0], stato_cartella1_diretto)

        # Aggiungi la seconda cartella
        cartella2 = Cartella()
        self.giocatore.aggiungi_cartella(cartella2)

        # Verifica che get_stato_cartelle ritorni esattamente due stati
        stato_con_due = self.giocatore.get_stato_cartelle()
        self.assertEqual(len(stato_con_due), 2)

        # Verifica l'ordine: primo stato di cartella1, secondo di cartella2
        stato_cartella1_verificato = cartella1.get_stato_cartella()
        stato_cartella2_verificato = cartella2.get_stato_cartella()
        self.assertEqual(stato_con_due[0], stato_cartella1_verificato)
        self.assertEqual(stato_con_due[1], stato_cartella2_verificato)

        # Modifica lo stato interno: segnare un numero in cartella1
        numeri_cartella1 = cartella1.get_numeri_cartella()
        numero_da_segnare = numeri_cartella1[0]
        cartella1.segna_numero(numero_da_segnare)

        # Richiedi gli stati aggregati di nuovo
        stato_dopo_modifica = self.giocatore.get_stato_cartelle()

        # Verifica che lo stato di cartella1 sia aggiornato e rifletta
        # la segnazione del numero
        stato_cartella1_aggiornato = cartella1.get_stato_cartella()
        self.assertEqual(stato_dopo_modifica[0], stato_cartella1_aggiornato)

        # Verifica che lo stato di cartella2 rimanga invariato
        # (non è stata modificata)
        stato_cartella2_immutato = cartella2.get_stato_cartella()
        self.assertEqual(stato_dopo_modifica[1], stato_cartella2_immutato)


    #metodo per testare il corretto funzionamento di has_tombola()
    def test_has_tombola_ritorna_boolean_corretto(self) -> None:
        """
        Verifica che has_tombola() ritorni False quando nessuna cartella ha
        completato la tombola, e True quando almeno una cartella l'ha completata.

        Controlla che:
        - con cartelle senza tombola, ritorni False;
        - quando una cartella completa la tombola, ritorni True;
        - rimanga True anche se vengono aggiunte altre cartelle senza tombola.
        """
        # Crea e aggiungi la prima cartella (senza tombola completata)
        cartella1 = Cartella()
        self.giocatore.aggiungi_cartella(cartella1)

        # Verifica pre-condizione: nessuna cartella ha completato la tombola
        self.assertFalse(self.giocatore.has_tombola())

        # Crea e aggiungi una seconda cartella (ancora senza tombola)
        cartella2 = Cartella()
        self.giocatore.aggiungi_cartella(cartella2)

        # Verifica che has_tombola continui a ritornare False
        self.assertFalse(self.giocatore.has_tombola())

        # Completa la tombola sulla seconda cartella segnando tutti i numeri
        # Estrai tutti i numeri presenti in cartella2
        numeri_cartella2 = cartella2.get_numeri_cartella()

        # Segnale uno per uno tutti i numeri della cartella
        for numero in numeri_cartella2:
            cartella2.segna_numero(numero)

        # Verifica che la cartella abbia effettivamente completato la tombola
        self.assertTrue(cartella2.verifica_cartella_completa())

        # Verifica che has_tombola ora ritorni True (almeno una cartella
        # ha completato la tombola)
        self.assertTrue(self.giocatore.has_tombola())

        # Crea e aggiungi una terza cartella senza tombola completata
        cartella3 = Cartella()
        self.giocatore.aggiungi_cartella(cartella3)

        # Verifica che has_tombola continui a ritornare True, perché la
        # cartella2 ha già completato, anche se cartella3 non l'ha fatto
        self.assertTrue(self.giocatore.has_tombola())


    # Fix 1/3 - Test per reclamo_turno inizializzato a None
    def test_reclamo_turno_inizializzato_a_none(self) -> None:
        """
        Verifica che reclamo_turno sia inizializzato a None alla creazione
        del giocatore.
        """
        from bingo_game.events.eventi_partita import ReclamoVittoria
        
        giocatore = GiocatoreBase("Test")
        self.assertIsNone(giocatore.reclamo_turno)


    # Fix 1/3 - Test per reset_reclamo_turno
    def test_reset_reclamo_turno(self) -> None:
        """
        Verifica che reset_reclamo_turno() azzeri correttamente il reclamo
        del turno corrente.
        """
        from bingo_game.events.eventi_partita import ReclamoVittoria
        
        giocatore = GiocatoreBase("Test")
        # Imposta un reclamo
        giocatore.reclamo_turno = ReclamoVittoria(
            tipo="ambo", 
            indice_cartella=0, 
            indice_riga=0
        )
        # Verifica che il reclamo sia stato impostato
        self.assertIsNotNone(giocatore.reclamo_turno)
        
        # Esegui il reset
        giocatore.reset_reclamo_turno()
        
        # Verifica che il reclamo sia None
        self.assertIsNone(giocatore.reclamo_turno)


    # Fix 1/3 - Test per is_automatico su GiocatoreBase
    def test_is_automatico_base_false(self) -> None:
        """
        Verifica che is_automatico() ritorni False per GiocatoreBase
        (comportamento di default per giocatore umano).
        """
        giocatore = GiocatoreBase("Test")
        self.assertFalse(giocatore.is_automatico())
