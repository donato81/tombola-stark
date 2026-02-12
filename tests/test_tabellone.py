#import delle librerie necessarie
#importazione della libreria unittest per la creazione dei test
import unittest
#importazione del modulo tabellone dalla cartella bingo_game
from bingo_game.tabellone import Tabellone


#definizione della classe di test per la classe Tabellone
class TestTabellone(unittest.TestCase):

    #metodo di setup per istanziare la classe tabellone prima di ogni test
    def setUp(self):
        self.tabellone = Tabellone()


    #metodo di test per l'inizializzazione del tabellone
    def test_inizializza_tabellone(self):
        #verifica con assert che il tabellone sia stato inizializzato correttamente e che il numeri disponibili contenga 90 numeri 
        self.assertEqual(len(self.tabellone.numeri_disponibili), 90)
        #verifica con assert che i numeri estratti siano 0
        self.assertEqual(len(self.tabellone.numeri_estratti), 0)


    #metodo di test per l'estrazione di un numero
    def test_estrai_numero(self):
        #estrazione di un numero
        numero_estratto = self.tabellone.estrai_numero()
        #verifica con assert che il numero estratto sia compreso tra 1 e 90
        self.assertTrue(1 <= numero_estratto <= 90)
        #verifica con assert che il numero estratto non sia più nei numeri disponibili
        self.assertNotIn(numero_estratto, self.tabellone.numeri_disponibili)
        #verifica con assert che il numero estratto sia stato aggiunto ai numeri estratti
        self.assertIn(numero_estratto, self.tabellone.numeri_estratti)


    #metodo di test per verificare l'eccezzione quando si estraggono tutti i numeri
    def test_estrai_numeri_esaurito(self):
        #estrazione di tutti i numeri
        for _ in range(90):
            self.tabellone.estrai_numero()
        #verifica con assert che venga sollevata un'eccezione quando si tenta di estrarre un altro numero
        with self.assertRaises(ValueError):
            self.tabellone.estrai_numero()
        #verifica con assert che non ci siano più numeri disponibili
        self.assertEqual(len(self.tabellone.numeri_disponibili), 0)


    def test_is_numero_estratto(self):
        """
        Verifica is_numero_estratto: True/False coerente prima e dopo estrazioni,
        e assenza di effetti collaterali sullo stato del tabellone.
        """

        # --- SCENARIO 1: all'inizio nessun numero è estratto ---
        # Scegliamo un numero valido e verifichiamo che non risulti estratto.
        numero_test = 1
        self.assertFalse(
            self.tabellone.is_numero_estratto(numero_test),
            "All'inizio un numero valido deve risultare non estratto."
        )

        # Verifica che la chiamata non modifichi lo stato (metodo di sola lettura)
        conteggio_estratti_prima = self.tabellone.get_conteggio_estratti()
        conteggio_disponibili_prima = self.tabellone.get_conteggio_disponibili()
        set_estratti_prima = set(self.tabellone.numeri_estratti)
        set_disponibili_prima = set(self.tabellone.numeri_disponibili)

        _ = self.tabellone.is_numero_estratto(numero_test)

        self.assertEqual(
            self.tabellone.get_conteggio_estratti(),
            conteggio_estratti_prima,
            "is_numero_estratto non deve modificare il conteggio degli estratti."
        )
        self.assertEqual(
            self.tabellone.get_conteggio_disponibili(),
            conteggio_disponibili_prima,
            "is_numero_estratto non deve modificare il conteggio dei disponibili."
        )
        self.assertSetEqual(
            set(self.tabellone.numeri_estratti),
            set_estratti_prima,
            "is_numero_estratto non deve modificare il set dei numeri estratti."
        )
        self.assertSetEqual(
            set(self.tabellone.numeri_disponibili),
            set_disponibili_prima,
            "is_numero_estratto non deve modificare il set dei numeri disponibili."
        )

        # --- SCENARIO 2: dopo una estrazione ---
        numero_estratto = self.tabellone.estrai_numero()

        self.assertTrue(
            self.tabellone.is_numero_estratto(numero_estratto),
            "Dopo l'estrazione, il numero estratto deve risultare presente tra gli estratti."
        )

        # Scegliamo un numero che sicuramente non può essere estratto: uno dai disponibili.
        # (Così evitiamo di testare un numero casualmente già estratto.)
        numero_non_estratto = next(iter(self.tabellone.numeri_disponibili))
        self.assertFalse(
            self.tabellone.is_numero_estratto(numero_non_estratto),
            "Un numero ancora disponibile non deve risultare estratto."
        )

        # --- SCENARIO 3: dopo più estrazioni, tutti i numeri estratti devono risultare True ---
        estrazioni_aggiuntive = 10
        cronologia = [numero_estratto]
        for _ in range(estrazioni_aggiuntive):
            cronologia.append(self.tabellone.estrai_numero())

        for n in cronologia:
            self.assertTrue(
                self.tabellone.is_numero_estratto(n),
                "Ogni numero già estratto deve risultare estratto (True)."
            )

        # --- SCENARIO 4: valori fuori range (nessuna eccezione prevista) ---
        # Il metodo è volutamente "pulito": non valida range/tipo, quindi qui ci aspettiamo
        # solo un comportamento stabile (tipicamente False) e nessun effetto collaterale.
        self.assertFalse(
            self.tabellone.is_numero_estratto(0),
            "Per un numero fuori range (0) ci si aspetta un comportamento predicibile (False)."
        )
        self.assertFalse(
            self.tabellone.is_numero_estratto(91),
            "Per un numero fuori range (91) ci si aspetta un comportamento predicibile (False)."
        )


    #metodo di test per verificare il reset del tabellone
    def test_reset_tabellone(self):
        #estrazione di alcuni numeri
        for _ in range(10):
            self.tabellone.estrai_numero()
        #reset del tabellone
        self.tabellone.reset_tabellone()
        #verifica con assert che i numeri disponibili dopo il reset siano 90
        self.assertEqual(len(self.tabellone.numeri_disponibili), 90)
        #verifica con assert che i numeri estratti dopo il reset siano 0
        self.assertEqual(len(self.tabellone.numeri_estratti), 0)
        #crea un set di numeri da 1 a 90
        self.assertSetEqual(self.tabellone.numeri_disponibili, set(range(1, 91)))




    #metodo per eseguire i test sulle liste dei numeri estratti e disponibili
    def test_numeri_estratti_e_disponibili(self):
        #dichiara il numero di estrazioni da compiere
        estrazioni_fatte = 15
        #utilizzo di set per tenere traccia dei numeri estratti
        numeri_estratti = set()
        for _ in range(estrazioni_fatte):
            numero = self.tabellone.estrai_numero()
            numeri_estratti.add(numero)
        #ottieni i numeri estratti tramite il metodo get_numeri_estratti
        lista_estratti = self.tabellone.get_numeri_estratti()
        #ottieni i numeri disponibili tramite il metodo get_numeri_disponibili
        lista_disponibili = self.tabellone.get_numeri_disponibili()
        #verifica con assert che i numeri estratti siano corretti
        self.assertEqual(len(lista_estratti), estrazioni_fatte)
        #verifica con assert che i numeri disponibili siano corretti
        self.assertEqual(len(lista_disponibili), 90 - estrazioni_fatte)
        #verifica con assert che i numeri estratti siano ordinati correttamente
        self.assertEqual(lista_estratti, sorted(lista_estratti))
        #verifica con assert che i numeri disponibili siano ordinati correttamente
        self.assertEqual(lista_disponibili, sorted(lista_disponibili))
        # Controlla che tutti i numeri estratti siano nella lista degli estratti
        for numero in numeri_estratti:
            self.assertIn(numero, lista_estratti)
            self.assertNotIn(numero, lista_disponibili)
        # Verifica che numeri estratti e disponibili completino insieme il set da 1 a 90
        insieme_totale = set(lista_estratti) | set(lista_disponibili)
        self.assertEqual(insieme_totale, set(range(1, 91)))



    #metodo di test per il conteggio dei numeri estratti
    def test_get_conteggio_estratti(self):
        """
        Verifica che get_conteggio_estratti() ritorni correttamente
        il numero di numeri estratti dal tabellone.

        Il test controlla tre scenari principali:
        1) Tabellone appena inizializzato (nessun numero estratto) -> 0.
        2) Dopo alcune estrazioni (ad esempio 5 numeri) -> il conteggio deve
           coincidere con il numero di estrazioni effettuate.
        3) Dopo molte estrazioni (ad esempio 20 numeri) -> il conteggio deve
           aggiornarsi correttamente e rimanere coerente con il set interno
           dei numeri estratti.
        """

        # SCENARIO 1: Tabellone appena creato, nessun numero estratto
        conteggio_iniziale = self.tabellone.get_conteggio_estratti()
        self.assertEqual(
            conteggio_iniziale,
            0,
            "Subito dopo l'inizializzazione, get_conteggio_estratti() deve ritornare 0."
        )

        # SCENARIO 2: Dopo alcune estrazioni (5 numeri)
        estrazioni_prima_fase = 5
        for _ in range(estrazioni_prima_fase):
            self.tabellone.estrai_numero()

        conteggio_dopo_5 = self.tabellone.get_conteggio_estratti()
        self.assertEqual(
            conteggio_dopo_5,
            estrazioni_prima_fase,
            f"Dopo {estrazioni_prima_fase} estrazioni, get_conteggio_estratti() "
            f"deve ritornare {estrazioni_prima_fase}, ma ha ritornato {conteggio_dopo_5}."
        )

        # SCENARIO 3: Dopo ulteriori estrazioni (totale 20 numeri)
        estrazioni_seconda_fase = 15
        for _ in range(estrazioni_seconda_fase):
            self.tabellone.estrai_numero()

        conteggio_totale = self.tabellone.get_conteggio_estratti()

        # Il totale atteso è la somma delle estrazioni effettuate
        estrazioni_totali_attese = estrazioni_prima_fase + estrazioni_seconda_fase
        self.assertEqual(
            conteggio_totale,
            estrazioni_totali_attese,
            f"Dopo {estrazioni_totali_attese} estrazioni, get_conteggio_estratti() "
            f"deve ritornare {estrazioni_totali_attese}, ma ha ritornato {conteggio_totale}."
        )

        # Verifica di coerenza con il set interno numeri_estratti
        self.assertEqual(
            conteggio_totale,
            len(self.tabellone.numeri_estratti),
            "Il valore ritornato da get_conteggio_estratti() deve essere uguale "
            "alla lunghezza del set numeri_estratti."
        )



    #metodo di test per il conteggio dei numeri disponibili
    def test_get_conteggio_disponibili(self):
        """
        Verifica che get_conteggio_disponibili() ritorni correttamente
        il numero di numeri ancora disponibili da estrarre.

        Il test controlla tre scenari principali:
        1) Tabellone appena inizializzato (nessuna estrazione) -> 90 numeri disponibili.
        2) Dopo alcune estrazioni (ad esempio 5 numeri) -> il conteggio deve
           essere 90 - numero_estrazioni.
        3) Dopo molte estrazioni (ad esempio 20 numeri) -> il conteggio deve
           aggiornarsi correttamente e rimanere coerente con il set interno
           dei numeri disponibili.
        """

        # SCENARIO 1: Tabellone appena creato, nessun numero estratto
        conteggio_iniziale = self.tabellone.get_conteggio_disponibili()
        self.assertEqual(
            conteggio_iniziale,
            90,
            "Subito dopo l'inizializzazione, get_conteggio_disponibili() "
            "deve ritornare 90."
        )

        # SCENARIO 2: Dopo alcune estrazioni (5 numeri)
        estrazioni_prima_fase = 5
        for _ in range(estrazioni_prima_fase):
            self.tabellone.estrai_numero()

        conteggio_dopo_5 = self.tabellone.get_conteggio_disponibili()
        disponibili_attesi_dopo_5 = 90 - estrazioni_prima_fase
        self.assertEqual(
            conteggio_dopo_5,
            disponibili_attesi_dopo_5,
            f"Dopo {estrazioni_prima_fase} estrazioni, get_conteggio_disponibili() "
            f"deve ritornare {disponibili_attesi_dopo_5}, ma ha ritornato "
            f"{conteggio_dopo_5}."
        )

        # SCENARIO 3: Dopo ulteriori estrazioni (totale 20 numeri)
        estrazioni_seconda_fase = 15
        for _ in range(estrazioni_seconda_fase):
            self.tabellone.estrai_numero()

        conteggio_totale_disponibili = self.tabellone.get_conteggio_disponibili()

        # Il totale delle estrazioni effettuate
        estrazioni_totali = estrazioni_prima_fase + estrazioni_seconda_fase
        disponibili_attesi_finali = 90 - estrazioni_totali

        self.assertEqual(
            conteggio_totale_disponibili,
            disponibili_attesi_finali,
            f"Dopo {estrazioni_totali} estrazioni, get_conteggio_disponibili() "
            f"deve ritornare {disponibili_attesi_finali}, ma ha ritornato "
            f"{conteggio_totale_disponibili}."
        )

        # Verifica di coerenza con il set interno numeri_disponibili
        self.assertEqual(
            conteggio_totale_disponibili,
            len(self.tabellone.numeri_disponibili),
            "Il valore ritornato da get_conteggio_disponibili() deve essere uguale "
            "alla lunghezza del set numeri_disponibili."
        )



    #metodo di test per la percentuale di avanzamento del tabellone
    def test_get_percentuale_avanzamento(self):
        """
        Verifica che get_percentuale_avanzamento() calcoli correttamente
        la percentuale di avanzamento del tabellone.

        Il test controlla tre scenari principali:
        1) Nessun numero estratto -> 0.0%.
        2) Alcuni numeri estratti (ad esempio 9 e 45 numeri) -> percentuale
           coerente con il rapporto estratti/90, arrotondata a una cifra decimale.
        3) Tutti i numeri estratti (90 numeri) -> 100.0%.
        """

        # SCENARIO 1: Tabellone appena inizializzato, nessun numero estratto
        percentuale_iniziale = self.tabellone.get_percentuale_avanzamento()
        self.assertEqual(
            percentuale_iniziale,
            0.0,
            "Subito dopo l'inizializzazione, get_percentuale_avanzamento() "
            "deve ritornare 0.0."
        )

        # SCENARIO 2a: Dopo 9 estrazioni (10% del tabellone)
        estrazioni_prima_fase = 9
        for _ in range(estrazioni_prima_fase):
            self.tabellone.estrai_numero()

        percentuale_dopo_9 = self.tabellone.get_percentuale_avanzamento()
        percentuale_attesa_9 = round((estrazioni_prima_fase / 90) * 100, 1)

        self.assertEqual(
            percentuale_dopo_9,
            percentuale_attesa_9,
            f"Dopo {estrazioni_prima_fase} estrazioni, get_percentuale_avanzamento() "
            f"deve ritornare {percentuale_attesa_9}, ma ha ritornato "
            f"{percentuale_dopo_9}."
        )

        # SCENARIO 2b: Dopo 45 estrazioni (50% del tabellone)
        estrazioni_seconda_fase = 36  # 9 + 36 = 45 estrazioni totali
        for _ in range(estrazioni_seconda_fase):
            self.tabellone.estrai_numero()

        estrazioni_totali_meta = estrazioni_prima_fase + estrazioni_seconda_fase
        percentuale_dopo_45 = self.tabellone.get_percentuale_avanzamento()
        percentuale_attesa_45 = round((estrazioni_totali_meta / 90) * 100, 1)

        self.assertEqual(
            percentuale_dopo_45,
            percentuale_attesa_45,
            f"Dopo {estrazioni_totali_meta} estrazioni, get_percentuale_avanzamento() "
            f"deve ritornare {percentuale_attesa_45}, ma ha ritornato "
            f"{percentuale_dopo_45}."
        )

        # SCENARIO 3: Dopo 90 estrazioni (tabellone completo)
        estrazioni_rimanenti = 90 - estrazioni_totali_meta
        for _ in range(estrazioni_rimanenti):
            self.tabellone.estrai_numero()

        percentuale_finale = self.tabellone.get_percentuale_avanzamento()
        self.assertEqual(
            percentuale_finale,
            100.0,
            "Dopo aver estratto tutti i 90 numeri, get_percentuale_avanzamento() "
            "deve ritornare 100.0."
        )


    def test_get_ultimo_numero_estratto(self):
        """
        Verifica get_ultimo_numero_estratto: None all'inizio e dopo reset,
        valore corretto dopo estrazioni, e assenza di effetti collaterali.
        """

        # --- SCENARIO 1: tabellone appena creato -> nessuna estrazione ---
        self.assertIsNone(
            self.tabellone.get_ultimo_numero_estratto(),
            "All'inizio get_ultimo_numero_estratto deve ritornare None."
        )

        # Verifica che la chiamata non modifichi lo stato del tabellone
        conteggio_estratti_prima = self.tabellone.get_conteggio_estratti()
        conteggio_disponibili_prima = self.tabellone.get_conteggio_disponibili()
        numeri_estratti_prima = set(self.tabellone.numeri_estratti)
        numeri_disponibili_prima = set(self.tabellone.numeri_disponibili)

        _ = self.tabellone.get_ultimo_numero_estratto()

        self.assertEqual(
            self.tabellone.get_conteggio_estratti(),
            conteggio_estratti_prima,
            "get_ultimo_numero_estratto non deve modificare il conteggio degli estratti."
        )
        self.assertEqual(
            self.tabellone.get_conteggio_disponibili(),
            conteggio_disponibili_prima,
            "get_ultimo_numero_estratto non deve modificare il conteggio dei disponibili."
        )
        self.assertSetEqual(
            set(self.tabellone.numeri_estratti),
            numeri_estratti_prima,
            "get_ultimo_numero_estratto non deve modificare l'insieme dei numeri estratti."
        )
        self.assertSetEqual(
            set(self.tabellone.numeri_disponibili),
            numeri_disponibili_prima,
            "get_ultimo_numero_estratto non deve modificare l'insieme dei numeri disponibili."
        )

        # --- SCENARIO 2: dopo una estrazione -> ultimo numero deve coincidere ---
        primo_numero = self.tabellone.estrai_numero()
        self.assertEqual(
            self.tabellone.get_ultimo_numero_estratto(),
            primo_numero,
            "Dopo una estrazione, get_ultimo_numero_estratto deve ritornare il numero estratto."
        )

        # --- SCENARIO 3: dopo più estrazioni -> deve aggiornarsi sempre ---
        secondo_numero = self.tabellone.estrai_numero()
        self.assertEqual(
            self.tabellone.get_ultimo_numero_estratto(),
            secondo_numero,
            "Dopo due estrazioni, deve ritornare il secondo (cioè l'ultimo in ordine temporale)."
        )

        terzo_numero = self.tabellone.estrai_numero()
        self.assertEqual(
            self.tabellone.get_ultimo_numero_estratto(),
            terzo_numero,
            "Dopo tre estrazioni, deve ritornare il terzo (cioè l'ultimo in ordine temporale)."
        )

        # --- SCENARIO 4: reset -> deve tornare None ---
        self.tabellone.reset_tabellone()
        self.assertIsNone(
            self.tabellone.get_ultimo_numero_estratto(),
            "Dopo reset_tabellone, get_ultimo_numero_estratto deve ritornare None."
        )


    def test_get_ultimi_numeri_estratti(self):
        """
        Verifica get_ultimi_numeri_estratti: casi di errore su n, caso vuoto,
        slicing corretto (meno/più di n), ordine temporale e assenza di effetti collaterali.
        """

        # --- CASI DI ERRORE: n non è int ---
        with self.assertRaises(ValueError, msg="Se n non è int deve essere sollevato ValueError."):
            self.tabellone.get_ultimi_numeri_estratti("5")  # type: ignore

        with self.assertRaises(ValueError, msg="Se n non è int deve essere sollevato ValueError."):
            self.tabellone.get_ultimi_numeri_estratti(5.0)  # type: ignore

        with self.assertRaises(ValueError, msg="Se n non è int deve essere sollevato ValueError."):
            self.tabellone.get_ultimi_numeri_estratti(None)  # type: ignore

        # --- CASI DI ERRORE: n <= 0 ---
        with self.assertRaises(ValueError, msg="Se n è 0 deve essere sollevato ValueError."):
            self.tabellone.get_ultimi_numeri_estratti(0)

        with self.assertRaises(ValueError, msg="Se n è negativo deve essere sollevato ValueError."):
            self.tabellone.get_ultimi_numeri_estratti(-3)

        # --- CASO BASE: nessuna estrazione -> tupla vuota ---
        ultimi = self.tabellone.get_ultimi_numeri_estratti()
        self.assertIsInstance(
            ultimi,
            tuple,
            "Il metodo deve restituire sempre una tupla."
        )
        self.assertEqual(
            ultimi,
            tuple(),
            "Senza estrazioni, get_ultimi_numeri_estratti deve ritornare una tupla vuota."
        )

        # Verifica che il metodo non modifichi lo stato (conteggi invariati)
        conteggio_estratti_prima = self.tabellone.get_conteggio_estratti()
        conteggio_disponibili_prima = self.tabellone.get_conteggio_disponibili()
        _ = self.tabellone.get_ultimi_numeri_estratti(3)
        self.assertEqual(
            self.tabellone.get_conteggio_estratti(),
            conteggio_estratti_prima,
            "get_ultimi_numeri_estratti non deve modificare il numero di estratti."
        )
        self.assertEqual(
            self.tabellone.get_conteggio_disponibili(),
            conteggio_disponibili_prima,
            "get_ultimi_numeri_estratti non deve modificare il numero di disponibili."
        )

        # --- CASO: estrazioni meno di n -> ritorna tutto ---
        estrazioni_fatte = 3
        cronologia = []
        for _ in range(estrazioni_fatte):
            numero = self.tabellone.estrai_numero()
            cronologia.append(numero)

        ultimi_5 = self.tabellone.get_ultimi_numeri_estratti(5)
        self.assertEqual(
            ultimi_5,
            tuple(cronologia),
            "Se le estrazioni sono meno di n, deve ritornare tutti i numeri in ordine temporale."
        )

        # --- CASO: estrazioni maggiori di n -> ritorna solo gli ultimi n ---
        # Portiamo le estrazioni totali a 8 e chiediamo gli ultimi 5.
        for _ in range(5):
            numero = self.tabellone.estrai_numero()
            cronologia.append(numero)

        ultimi_5 = self.tabellone.get_ultimi_numeri_estratti(5)
        self.assertEqual(
            ultimi_5,
            tuple(cronologia[-5:]),
            "Deve ritornare esattamente gli ultimi n numeri estratti in ordine temporale."
        )

        # --- CASO: n=1 -> ritorna l'ultimo numero estratto ---
        ultimo_atteso = cronologia[-1]
        ultimi_1 = self.tabellone.get_ultimi_numeri_estratti(1)
        self.assertEqual(
            ultimi_1,
            (ultimo_atteso,),
            "Con n=1 deve ritornare una tupla contenente solo l'ultimo numero estratto."
        )

        # Controllo finale: il metodo deve continuare a non modificare lo stato
        self.assertEqual(
            self.tabellone.get_conteggio_estratti(),
            len(cronologia),
            "Dopo varie chiamate a get_ultimi_numeri_estratti, il conteggio estratti deve restare invariato."
        )
        self.assertEqual(
            self.tabellone.get_conteggio_disponibili(),
            90 - len(cronologia),
            "Dopo varie chiamate a get_ultimi_numeri_estratti, il conteggio disponibili deve restare coerente."
        )


    def test_get_stato_tabellone(self):
        """
        Verifica che get_stato_tabellone ritorni un dizionario completo e coerente
        sia all'inizio (nessuna estrazione) sia dopo alcune estrazioni.
        """

        # --- SCENARIO 1: tabellone appena creato (stato iniziale) ---
        stato_iniziale = self.tabellone.get_stato_tabellone()

        # Controllo tipo
        self.assertIsInstance(stato_iniziale, dict, "get_stato_tabellone deve ritornare un dizionario.")

        # Controllo chiavi attese (struttura)
        chiavi_attese = {
            "totale_numeri",
            "numeri_estratti",
            "numeri_disponibili",
            "ultimi_numeri_estratti",
            "ultimo_numero_estratto",
            "percentuale_avanzamento",
        }
        self.assertEqual(set(stato_iniziale.keys()), chiavi_attese, "Il dizionario di stato deve contenere esattamente le chiavi attese.")

        # Controllo valori iniziali
        self.assertEqual(stato_iniziale["totale_numeri"], 90, "totale_numeri deve essere sempre 90.")
        self.assertEqual(stato_iniziale["numeri_estratti"], 0, "All'inizio numeri_estratti deve essere 0.")
        self.assertEqual(stato_iniziale["numeri_disponibili"], 90, "All'inizio numeri_disponibili deve essere 90.")
        self.assertEqual(stato_iniziale["ultimi_numeri_estratti"], tuple(), "All'inizio ultimi_numeri_estratti deve essere una tupla vuota.")
        self.assertIsNone(stato_iniziale["ultimo_numero_estratto"], "All'inizio ultimo_numero_estratto deve essere None.")
        self.assertEqual(stato_iniziale["percentuale_avanzamento"], 0.0, "All'inizio percentuale_avanzamento deve essere 0.0.")

        # Controllo invariante di coerenza
        self.assertEqual(
            stato_iniziale["numeri_estratti"] + stato_iniziale["numeri_disponibili"],
            stato_iniziale["totale_numeri"],
            "La somma di numeri_estratti e numeri_disponibili deve essere totale_numeri."
        )
        self.assertTrue(
            0.0 <= stato_iniziale["percentuale_avanzamento"] <= 100.0,
            "percentuale_avanzamento deve essere sempre compresa tra 0.0 e 100.0."
        )

        # --- SCENARIO 2: dopo alcune estrazioni ---
        estrazioni_fatte = 10
        cronologia_estrazioni = []
        for _ in range(estrazioni_fatte):
            numero = self.tabellone.estrai_numero()
            cronologia_estrazioni.append(numero)

        stato_dopo = self.tabellone.get_stato_tabellone()

        # Controllo che la struttura rimanga la stessa
        self.assertEqual(
            set(stato_dopo.keys()),
            chiavi_attese,
            "Dopo le estrazioni, il dizionario deve mantenere le stesse chiavi attese."
        )

        # Coerenza conteggi
        self.assertEqual(
            stato_dopo["totale_numeri"],
            90,
            "totale_numeri deve rimanere sempre 90."
        )
        self.assertEqual(
            stato_dopo["numeri_estratti"],
            estrazioni_fatte,
            "numeri_estratti deve corrispondere al numero di estrazioni effettuate."
        )
        self.assertEqual(
            stato_dopo["numeri_disponibili"],
            90 - estrazioni_fatte,
            "numeri_disponibili deve essere 90 - numero_estrazioni."
        )

        # Coerenza ultimo estratto
        ultimo_estratto_atteso = cronologia_estrazioni[-1]
        self.assertEqual(
            stato_dopo["ultimo_numero_estratto"],
            ultimo_estratto_atteso,
            "ultimo_numero_estratto deve coincidere con l'ultima estrazione effettuata."
        )

        # Coerenza ultimi 5 estratti (ordine temporale)
        ultimi_5_attesi = tuple(cronologia_estrazioni[-5:])
        self.assertEqual(
            stato_dopo["ultimi_numeri_estratti"],
            ultimi_5_attesi,
            "ultimi_numeri_estratti deve contenere gli ultimi 5 numeri estratti in ordine temporale."
        )

        # Coerenza percentuale (arrotondata a 1 decimale)
        percentuale_attesa = round((estrazioni_fatte / 90) * 100, 1)
        self.assertEqual(
            stato_dopo["percentuale_avanzamento"],
            percentuale_attesa,
            "percentuale_avanzamento deve essere coerente con numeri_estratti e arrotondata a 1 decimale."
        )

        # Controlli di sanità/invarianti anche dopo le estrazioni
        self.assertEqual(
            stato_dopo["numeri_estratti"] + stato_dopo["numeri_disponibili"],
            stato_dopo["totale_numeri"],
            "Anche dopo le estrazioni, estratti + disponibili deve fare 90."
        )
        self.assertTrue(
            0.0 <= stato_dopo["percentuale_avanzamento"] <= 100.0,
            "Anche dopo le estrazioni, percentuale_avanzamento deve restare nel range 0.0 - 100.0."
        )

        # Coerenza anche con i metodi di conteggio (se presenti)
        self.assertEqual(
            stato_dopo["numeri_estratti"],
            self.tabellone.get_conteggio_estratti(),
            "numeri_estratti nello stato deve coincidere con get_conteggio_estratti."
        )
        self.assertEqual(
            stato_dopo["numeri_disponibili"],
            self.tabellone.get_conteggio_disponibili(),
            "numeri_disponibili nello stato deve coincidere con get_conteggio_disponibili."
        )


    def test_numeri_terminati(self):
        """
        Verifica numeri_terminati: False all'inizio, False finché resta almeno un numero,
        True quando non ci sono più numeri disponibili, senza effetti collaterali.
        """

        # --- SCENARIO 1: tabellone appena creato -> non può essere terminato ---
        self.assertFalse(
            self.tabellone.numeri_terminati(),
            "All'inizio numeri_terminati deve essere False (ci sono 90 numeri disponibili)."
        )

        # Verifica che la chiamata non modifichi lo stato (metodo di sola lettura)
        conteggio_estratti_prima = self.tabellone.get_conteggio_estratti()
        conteggio_disponibili_prima = self.tabellone.get_conteggio_disponibili()
        set_disponibili_prima = set(self.tabellone.numeri_disponibili)

        _ = self.tabellone.numeri_terminati()

        self.assertEqual(
            self.tabellone.get_conteggio_estratti(),
            conteggio_estratti_prima,
            "numeri_terminati non deve modificare il conteggio degli estratti."
        )
        self.assertEqual(
            self.tabellone.get_conteggio_disponibili(),
            conteggio_disponibili_prima,
            "numeri_terminati non deve modificare il conteggio dei disponibili."
        )
        self.assertSetEqual(
            set(self.tabellone.numeri_disponibili),
            set_disponibili_prima,
            "numeri_terminati non deve modificare il set dei numeri disponibili."
        )

        # --- SCENARIO 2: dopo alcune estrazioni -> deve restare False ---
        estrazioni_parziali = 10
        for _ in range(estrazioni_parziali):
            self.tabellone.estrai_numero()

        self.assertFalse(
            self.tabellone.numeri_terminati(),
            "Finché resta almeno un numero disponibile, numeri_terminati deve essere False."
        )

        # --- SCENARIO 3: esaurimento totale -> deve diventare True ---
        # Completiamo le estrazioni fino ad arrivare a 90 (tabellone completamente vuoto).
        estrazioni_rimanenti = 90 - estrazioni_parziali
        for _ in range(estrazioni_rimanenti):
            self.tabellone.estrai_numero()

        self.assertEqual(
            len(self.tabellone.numeri_disponibili),
            0,
            "Dopo 90 estrazioni, il set dei numeri disponibili deve essere vuoto."
        )
        self.assertTrue(
            self.tabellone.numeri_terminati(),
            "Quando non ci sono più numeri disponibili, numeri_terminati deve essere True."
        )

        # --- SCENARIO 4: reset -> torna False ---
        self.tabellone.reset_tabellone()
        self.assertFalse(
            self.tabellone.numeri_terminati(),
            "Dopo reset_tabellone, numeri_terminati deve tornare False."
        )

    def test_gestione_errore_numeri_terminati(self):
        """
        Verifica gestione_errore_numeri_terminati: solleva sempre ValueError con messaggio atteso,
        e non modifica lo stato del tabellone.
        """

        # Salviamo lo stato prima della chiamata (per verificare che non venga modificato)
        conteggio_estratti_prima = self.tabellone.get_conteggio_estratti()
        conteggio_disponibili_prima = self.tabellone.get_conteggio_disponibili()
        set_estratti_prima = set(self.tabellone.numeri_estratti)
        set_disponibili_prima = set(self.tabellone.numeri_disponibili)

        # --- SCENARIO 1: chiamata diretta -> deve sollevare ValueError con messaggio corretto ---
        with self.assertRaises(ValueError) as ctx:
            self.tabellone.gestione_errore_numeri_terminati()

        self.assertEqual(
            str(ctx.exception),
            "Tutti i numeri sono stati estratti. Impossibile estrarre un altro numero.",
            "Il messaggio dell'eccezione deve essere esattamente quello previsto."
        )

        # Verifica assenza di effetti collaterali: la chiamata deve essere 'pura' (solo raise)
        self.assertEqual(
            self.tabellone.get_conteggio_estratti(),
            conteggio_estratti_prima,
            "gestione_errore_numeri_terminati non deve modificare il conteggio degli estratti."
        )
        self.assertEqual(
            self.tabellone.get_conteggio_disponibili(),
            conteggio_disponibili_prima,
            "gestione_errore_numeri_terminati non deve modificare il conteggio dei disponibili."
        )
        self.assertSetEqual(
            set(self.tabellone.numeri_estratti),
            set_estratti_prima,
            "gestione_errore_numeri_terminati non deve modificare il set dei numeri estratti."
        )
        self.assertSetEqual(
            set(self.tabellone.numeri_disponibili),
            set_disponibili_prima,
            "gestione_errore_numeri_terminati non deve modificare il set dei numeri disponibili."
        )

        # --- SCENARIO 2: tabellone esaurito -> estrai_numero deve sollevare ValueError ---
        # (Questo scenario verifica che la gestione dell'errore sia effettivamente agganciata al flusso reale.)
        for _ in range(90):
            self.tabellone.estrai_numero()

        self.assertTrue(
            self.tabellone.numeri_terminati(),
            "Dopo 90 estrazioni, numeri_terminati deve essere True."
        )

        with self.assertRaises(ValueError, msg="A tabellone esaurito, estrai_numero deve sollevare ValueError."):
            self.tabellone.estrai_numero()


#script per eseguire il test
if __name__ == '__main__':
    unittest.main()
