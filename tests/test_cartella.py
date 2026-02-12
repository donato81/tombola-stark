#import delle librerie necessarie
#import     della libreria unittest per la creazione dei test
import unittest
#importazione della classe Cartella dal modulo bingo_game.cartella
from bingo_game.cartella import Cartella
#importazione del file cartella_exceptions dal percorso bingo_game/exceptions
from bingo_game.exceptions.cartella_exceptions import (
    CartellaException,
    CartellaNumeroTypeException,
    CartellaNumeroValueException,
    CartellaRigaTypeException,
    CartellaRigaValueException,
    CartellaColonnaTypeException,
    CartellaColonnaValueException
)



#definizione della classe di test per la classe Cartella
class TestCartella(unittest.TestCase):

    #metodo di setup per inizializzare la cartella prima di ogni test
    def setUp(self):
        # Crea un'istanza della cartella per i test
        self.cartella_default = Cartella()


    """test sulle OPERAZIONI FONDAMENTALI Riguardanti la CARTELLA"""

    #test del metodo segna_numero()
    def test_segna_numero(self):
        """
        Test del metodo segna_numero() della classe Cartella.
        
        Questo test verifica il comportamento corretto del metodo segna_numero()
        in tre scenari principali: segnazione valida, tentativo di ri-segnazione
        e tentativo di segnare un numero non presente nella cartella.
        
        Scenario 1: Segnazione corretta di un numero presente nella cartella
        - Otteniamo il primo numero dalla cartella
        - Lo segniamo per la prima volta
        - Verifichiamo che il metodo ritorni True (operazione riuscita)
        - Verifichiamo che il numero sia effettivamente segnato
        - Verifichiamo che il conteggio dei segnati sia aumentato a 1
        
        Scenario 2: Tentativo di ri-segnare lo stesso numero
        - Proviamo a segnare di nuovo lo stesso numero
        - Verifichiamo che il metodo ritorni False (numero già segnato)
        - Verifichiamo che il conteggio rimanga 1 (no duplicati)
        - Questo test l'idempotenza del metodo
        
        Scenario 3: Tentativo di segnare un numero non presente nella cartella
        - Troviamo un numero che sicuramente non è nella cartella
        - Proviamo a segnarlo (numero valido ma non in questa cartella)
        - Verifichiamo che il metodo ritorni False (numero non presente)
        - Verifichiamo che il conteggio rimanga 1 (nessuna modifica dello stato)
        """
        
        # SCENARIO 1: SEGNAZIONE CORRETTA DI UN NUMERO PRESENTE
        # Otteniamo la lista di tutti i numeri presenti nella cartella
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        
        # Prendiamo il primo numero della lista (sappiamo che è presente)
        primo_numero_da_segnare = numeri_cartella[0]
        
        # Segniamo il numero per la prima volta
        risultato_primo_tentativo = self.cartella_default.segna_numero(primo_numero_da_segnare)
        
        # Asserzione 1: Il metodo deve ritornare True (segnazione riuscita)
        self.assertTrue(
            risultato_primo_tentativo,
            f"Il metodo segna_numero() dovrebbe ritornare True quando segna un numero "
            f"presente nella cartella per la prima volta. Numero segnato: {primo_numero_da_segnare}"
        )
        
        # Asserzione 2: Il numero deve essere nel set dei numeri segnati
        numero_e_segnato = self.cartella_default.is_numero_segnato(primo_numero_da_segnare)
        self.assertTrue(
            numero_e_segnato,
            f"Dopo aver segnato il numero {primo_numero_da_segnare} con segna_numero(), "
            f"is_numero_segnato() dovrebbe ritornare True"
        )
        
        # Asserzione 3: Il conteggio dei numeri segnati deve essere 1
        conteggio_dopo_primo_segno = self.cartella_default.conta_numeri_segnati()
        self.assertEqual(
            conteggio_dopo_primo_segno, 1,
            f"Dopo aver segnato 1 numero, conta_numeri_segnati() dovrebbe ritornare 1, "
            f"ma ritorna {conteggio_dopo_primo_segno}"
        )
        
        # SCENARIO 2: TENTATIVO DI RI-SEGNAZIONE DELLO STESSO NUMERO
        
        # Proviamo a segnare di nuovo lo stesso numero
        risultato_secondo_tentativo = self.cartella_default.segna_numero(primo_numero_da_segnare)
        
        # Asserzione 4: Il metodo deve ritornare False (numero già segnato)
        self.assertFalse(
            risultato_secondo_tentativo,
            f"Il metodo segna_numero() dovrebbe ritornare False quando tentiamo di segnare "
            f"un numero che è già stato segnato. Numero: {primo_numero_da_segnare}"
        )
        
        # Asserzione 5: Il conteggio deve rimanere 1 (non aumentare a 2)
        conteggio_dopo_secondo_tentativo = self.cartella_default.conta_numeri_segnati()
        self.assertEqual(
            conteggio_dopo_secondo_tentativo, 1,
            f"Dopo aver tentato di ri-segnare un numero già segnato, il conteggio dovrebbe "
            f"rimanere 1, ma è {conteggio_dopo_secondo_tentativo}"
        )
        
        # SCENARIO 3: TENTATIVO DI SEGNARE UN NUMERO NON PRESENTE NELLA CARTELLA
        
        # Troviamo un numero che NON è nella cartella
        # Iteriamo tra 1 e 90 finché non troviamo un numero assente
        numero_non_presente = None
        for numero_test in range(1, 91):
            if numero_test not in numeri_cartella:
                numero_non_presente = numero_test
                break
        
        # Verifichiamo che abbiamo effettivamente trovato un numero non presente
        # (dovrebbe sempre succedere perché la cartella ha solo 15 numeri su 90)
        self.assertIsNotNone(
            numero_non_presente,
            "Non è stato possibile trovare un numero tra 1 e 90 che non sia nella cartella. "
            "Questo è un errore nel test stesso."
        )
        
        # Proviamo a segnare il numero che non è nella cartella
        risultato_numero_non_presente = self.cartella_default.segna_numero(numero_non_presente)
        
        # Asserzione 6: Il metodo deve ritornare False (numero non presente)
        self.assertFalse(
            risultato_numero_non_presente,
            f"Il metodo segna_numero() dovrebbe ritornare False quando tentiamo di segnare "
            f"un numero che non è presente in questa cartella. Numero: {numero_non_presente}"
        )
        
        # Asserzione 7: Il conteggio deve rimanere 1 (nessuna modifica)
        conteggio_dopo_numero_non_presente = self.cartella_default.conta_numeri_segnati()
        self.assertEqual(
            conteggio_dopo_numero_non_presente, 1,
            f"Dopo aver tentato di segnare un numero non presente nella cartella, il conteggio "
            f"dovrebbe rimanere 1, ma è {conteggio_dopo_numero_non_presente}"
        )


    """tests sulle eccezioni sollevate dal metodo segna_numero()"""

    #test del metodo segna_numero() - eccezione tipo numero
    def test_segna_numero_errore_tipo(self):
        """
        Verifica che segna_numero() sollevi CartellaNumeroTypeException
        quando il parametro 'numero' non è un intero.

        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """

        # Caso 1: numero è una stringa
        with self.assertRaises(CartellaNumeroTypeException):
            self.cartella_default.segna_numero("45")

        # Caso 2: numero è un float
        with self.assertRaises(CartellaNumeroTypeException):
            self.cartella_default.segna_numero(45.5)

        # Caso 3: numero è None
        with self.assertRaises(CartellaNumeroTypeException):
            self.cartella_default.segna_numero(None)

        # Caso 4: numero è una lista
        with self.assertRaises(CartellaNumeroTypeException):
            self.cartella_default.segna_numero([45])


    #test del metodo segna_numero() - eccezione valore numero fuori range
    def test_segna_numero_errore_valore_fuori_range(self):
        """
        Verifica che segna_numero() sollevi CartellaNumeroValueException
        quando il parametro 'numero' è un intero ma fuori dal range valido 1–90.

        In questo test usiamo alcuni esempi di numeri troppo bassi e troppo alti
        (0, -5, 91, 100) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """

        # Caso 1: numero troppo basso (0)
        with self.assertRaises(CartellaNumeroValueException):
            self.cartella_default.segna_numero(0)

        # Caso 2: numero negativo
        with self.assertRaises(CartellaNumeroValueException):
            self.cartella_default.segna_numero(-5)

        # Caso 3: numero troppo alto (91)
        with self.assertRaises(CartellaNumeroValueException):
            self.cartella_default.segna_numero(91)

        # Caso 4: numero molto oltre il limite (100)
        with self.assertRaises(CartellaNumeroValueException):
            self.cartella_default.segna_numero(100)




    #test del metodo is_numero_segnato()
    def test_is_numero_segnato(self):
        """
        Verifica che il metodo is_numero_segnato() controlli correttamente
        se un numero è stato segnato sulla cartella.
        
        Copre tre scenari:
        1. Numero non segnato in una cartella appena creata
        2. Numero che è stato segnato
        3. Discriminazione tra numeri segnati e non segnati
        """
        
        # SCENARIO 1: Cartella appena creata, nessun numero segnato
        # Prendi il primo numero della cartella
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        numero_primo = numeri_cartella[0]
        
        # Verifica che non sia ancora segnato
        risultato_1 = self.cartella_default.is_numero_segnato(numero_primo)
        self.assertFalse(
            risultato_1,
            f"Il numero {numero_primo} non dovrebbe essere segnato in una cartella appena creata"
        )
        
        # SCENARIO 2: Segno il primo numero e poi verifico che sia segnato
        self.cartella_default.segna_numero(numero_primo)
        
        # Ora chiedo: "è segnato il primo numero?"
        risultato_2 = self.cartella_default.is_numero_segnato(numero_primo)
        self.assertTrue(
            risultato_2,
            f"Il numero {numero_primo} dovrebbe essere segnato dopo la segnazione"
        )
        
        # SCENARIO 3: Discriminazione tra numeri diversi
        # Ho segnato il primo numero, ma non il secondo
        numero_secondo = numeri_cartella[1]
        risultato_3 = self.cartella_default.is_numero_segnato(numero_secondo)
        self.assertFalse(
            risultato_3,
            f"Il numero {numero_secondo} non dovrebbe essere segnato, "
            f"solo il numero {numero_primo} è stato segnato"
        )


    """tests sulle eccezioni sollevate dal metodo is_numero_segnato()"""

    #test del metodo is_numero_segnato() - eccezione tipo numero
    def test_is_numero_segnato_errore_tipo(self):
        """
        Verifica che is_numero_segnato() sollevi CartellaNumeroTypeException
        quando il parametro 'numero' non è un intero.

        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """

        # Caso 1: numero è una stringa
        with self.assertRaises(CartellaNumeroTypeException):
            self.cartella_default.is_numero_segnato("45")

        # Caso 2: numero è un float
        with self.assertRaises(CartellaNumeroTypeException):
            self.cartella_default.is_numero_segnato(45.5)

        # Caso 3: numero è None
        with self.assertRaises(CartellaNumeroTypeException):
            self.cartella_default.is_numero_segnato(None)

        # Caso 4: numero è una lista
        with self.assertRaises(CartellaNumeroTypeException):
            self.cartella_default.is_numero_segnato([45])

    #test del metodo is_numero_segnato() - eccezione valore numero fuori range
    def test_is_numero_segnato_errore_valore_fuori_range(self):
        """
        Verifica che is_numero_segnato() sollevi CartellaNumeroValueException
        quando il parametro 'numero' è un intero ma fuori dal range valido 1–90.

        In questo test usiamo alcuni esempi di numeri troppo bassi e troppo alti
        (0, -5, 91, 100) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """

        # Caso 1: numero troppo basso (0)
        with self.assertRaises(CartellaNumeroValueException):
            self.cartella_default.is_numero_segnato(0)

        # Caso 2: numero negativo
        with self.assertRaises(CartellaNumeroValueException):
            self.cartella_default.is_numero_segnato(-5)

        # Caso 3: numero troppo alto (91)
        with self.assertRaises(CartellaNumeroValueException):
            self.cartella_default.is_numero_segnato(91)

        # Caso 4: numero molto oltre il limite (100)
        with self.assertRaises(CartellaNumeroValueException):
            self.cartella_default.is_numero_segnato(100)




    """TEST  DI INTERROGAZIONE DEL CONTENUTO DELLA CARTELLA"""

    #test del metodo get_numeri_cartella()
    def test_get_numeri_cartella(self):
        """
        Verifica che get_numeri_cartella() ritorni correttamente
        la lista ordinata dei 15 numeri della cartella.

        Il test controlla tre aspetti:
        1) La lunghezza della lista deve essere esattamente 15.
        2) Il contenuto deve corrispondere ai numeri interni della cartella.
        3) La lista deve essere già ordinata in modo crescente.
        """

        # Chiede alla cartella la lista dei numeri
        numeri = self.cartella_default.get_numeri_cartella()

        # 1) Deve restituire esattamente 15 numeri
        self.assertEqual(
            len(numeri),
            15,
            "get_numeri_cartella() deve restituire esattamente 15 numeri."
        )

        # 2) Il contenuto deve corrispondere al set interno numeri_cartella
        #    (stessi numeri, indipendentemente dall'ordine)
        self.assertEqual(
            set(numeri),
            self.cartella_default.numeri_cartella,
            "I numeri restituiti non corrispondono a quelli interni della cartella."
        )

        # 3) La lista deve essere già ordinata in modo crescente
        self.assertEqual(
            numeri,
            sorted(numeri),
            "La lista restituita da get_numeri_cartella() deve essere ordinata in modo crescente."
        )

    #test del metodo get_numeri_riga()
    def test_get_numeri_riga(self):
        """
        Verifica che get_numeri_riga() ritorni correttamente
        i numeri presenti in ciascuna riga della cartella.

        Per ogni riga valida (0, 1, 2) controlla che:
        1) La lista contenga esattamente i valori non-None presenti nella matrice.
        2) I numeri siano ordinati in modo crescente.
        3) Tutti gli elementi siano numeri interi (nessun None, nessun altro tipo).
        """

        # La cartella ha sempre 3 righe: indici 0, 1 e 2
        for numero_riga in range(3):
            # Chiede alla cartella i numeri della riga corrente
            numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)
            # Legge direttamente dalla matrice interna la riga corrispondente
            riga_matrice = self.cartella_default.cartella[numero_riga]
            # Costruisce la lista dei numeri attesi:
            # prende solo i valori non-None presenti in quella riga
            numeri_attesi = [
                valore
                for valore in riga_matrice
                if valore is not None
            ]
            # 1) I numeri restituiti devono corrispondere esattamente
            #    ai numeri non-None presenti nella riga della matrice (in forma ordinata)
            self.assertEqual(
                numeri_riga,
                sorted(numeri_attesi),
                f"I numeri della riga {numero_riga} non corrispondono ai valori presenti nella matrice."
            )
            # 2) La lista deve essere già ordinata in modo crescente
            self.assertEqual(
                numeri_riga,
                sorted(numeri_riga),
                f"La lista restituita da get_numeri_riga({numero_riga}) deve essere ordinata in modo crescente."
            )
            # 3) Ogni elemento della lista deve essere un intero (int)
            for numero in numeri_riga:
                self.assertIsInstance(
                    numero,
                    int,
                    f"Nella riga {numero_riga} è stato trovato un elemento non intero: {numero!r}."
                )


    """tests sulle eccezioni sollevate dal metodo get_numeri_riga()"""

    #test del metodo get_numeri_riga() - eccezione tipo numero_riga
    def test_get_numeri_riga_errore_tipo(self):
        """
        Verifica che get_numeri_riga() sollevi CartellaRigaTypeException
        quando il parametro 'numero_riga' non è un intero.
        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """
        # Caso 1: numero_riga è una stringa
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_numeri_riga("0")
        # Caso 2: numero_riga è un float
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_numeri_riga(1.5)
        # Caso 3: numero_riga è None
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_numeri_riga(None)
        # Caso 4: numero_riga è una lista
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_numeri_riga([1])

    #test del metodo get_numeri_riga() - eccezione valore numero_riga fuori range
    def test_get_numeri_riga_errore_valore_fuori_range(self):
        """
        Verifica che get_numeri_riga() sollevi CartellaRigaValueException
        quando il parametro 'numero_riga' è un intero ma fuori dal range valido 0, 1, 2.
        In questo test usiamo alcuni esempi di indici non validi
        (-1, 3, 10) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """
        # Caso 1: numero_riga negativo
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.get_numeri_riga(-1)
        # Caso 2: numero_riga troppo alto (uguale al numero di righe)
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.get_numeri_riga(3)
        # Caso 3: numero_riga molto oltre il limite
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.get_numeri_riga(10)

    #test del metodo get_numeri_colonna()
    def test_get_numeri_colonna(self):
        """
        Verifica che get_numeri_colonna() ritorni correttamente
        i numeri presenti in ciascuna colonna della cartella.
        Per ogni colonna valida (0-8) controlla che:
        1) La lista contenga esattamente i valori non-None presenti nella matrice.
        2) I numeri siano ordinati in modo crescente.
        3) Tutti gli elementi siano numeri interi (nessun None, nessun altro tipo).
        """
        # La cartella ha sempre 9 colonne: indici da 0 a 8
        for numero_colonna in range(9):
            # Chiede alla cartella i numeri della colonna corrente
            numeri_colonna = self.cartella_default.get_numeri_colonna(numero_colonna)
            # Legge direttamente dalla matrice interna tutti i valori
            # presenti in quella colonna, riga per riga
            numeri_attesi = []
            for indice_riga in range(self.cartella_default.righe):
                elemento = self.cartella_default.cartella[indice_riga][numero_colonna]
                if elemento is not None:
                    numeri_attesi.append(elemento)
            # 1) I numeri restituiti devono corrispondere esattamente
            #    ai numeri non-None presenti nella colonna della matrice (in forma ordinata)
            self.assertEqual(
                numeri_colonna,
                sorted(numeri_attesi),
                f"I numeri della colonna {numero_colonna} non corrispondono ai valori presenti nella matrice."
            )
            # 2) La lista deve essere già ordinata in modo crescente
            self.assertEqual(
                numeri_colonna,
                sorted(numeri_colonna),
                f"La lista restituita da get_numeri_colonna({numero_colonna}) deve essere ordinata in modo crescente."
            )
            # 3) Ogni elemento della lista deve essere un intero (int)
            for numero in numeri_colonna:
                self.assertIsInstance(
                    numero,
                    int,
                    f"Nella colonna {numero_colonna} è stato trovato un elemento non intero: {numero!r}."
                )


    """tests sulle eccezioni sollevate dal metodo get_numeri_colonna()"""

    #test del metodo get_numeri_colonna() - eccezione tipo numero_colonna
    def test_get_numeri_colonna_errore_tipo(self):
        """
        Verifica che get_numeri_colonna() sollevi CartellaColonnaTypeException
        quando il parametro 'numero_colonna' non è un intero.
        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """
        # Caso 1: numero_colonna è una stringa
        with self.assertRaises(CartellaColonnaTypeException):
            self.cartella_default.get_numeri_colonna("0")
        # Caso 2: numero_colonna è un float
        with self.assertRaises(CartellaColonnaTypeException):
            self.cartella_default.get_numeri_colonna(1.5)
        # Caso 3: numero_colonna è None
        with self.assertRaises(CartellaColonnaTypeException):
            self.cartella_default.get_numeri_colonna(None)
        # Caso 4: numero_colonna è una lista
        with self.assertRaises(CartellaColonnaTypeException):
            self.cartella_default.get_numeri_colonna([1])


    #test del metodo get_numeri_colonna() - eccezione valore numero_colonna fuori range
    def test_get_numeri_colonna_errore_valore_fuori_range(self):
        """
        Verifica che get_numeri_colonna() sollevi CartellaColonnaValueException
        quando il parametro 'numero_colonna' è un intero ma fuori dal range valido 0-8.
        In questo test usiamo alcuni esempi di indici non validi
        (-1, 9, 10) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """
        # Caso 1: numero_colonna negativo
        with self.assertRaises(CartellaColonnaValueException):
            self.cartella_default.get_numeri_colonna(-1)
        # Caso 2: numero_colonna troppo alto (uguale al numero di colonne)
        with self.assertRaises(CartellaColonnaValueException):
            self.cartella_default.get_numeri_colonna(9)
        # Caso 3: numero_colonna molto oltre il limite
        with self.assertRaises(CartellaColonnaValueException):
            self.cartella_default.get_numeri_colonna(10)

    #test del metodo get_numeri_segnati_riga()
    def test_get_numeri_segnati_riga(self):
        """
        Verifica che get_numeri_segnati_riga() ritorni correttamente
        solo i numeri segnati presenti in ciascuna riga della cartella.
        Per ogni riga valida (0, 1, 2) il test:
        1) Ottiene tutti i numeri della riga.
        2) Segna alcuni di questi numeri (simulando il gioco).
        3) Verifica che la lista restituita contenga SOLO i numeri segnati
           di quella riga, in ordine crescente.
        """
        # Per ogni riga della cartella: 0, 1 e 2
        for numero_riga in range(3):
            # Prima di tutto, resettiamo lo stato dei numeri segnati
            # per partire da una situazione pulita per ogni riga
            self.cartella_default.reset_cartella()
            # Otteniamo tutti i numeri presenti in questa riga
            numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)
            # Se per qualche motivo la riga fosse vuota (cosa che non deve accadere
            # in una cartella valida), saltiamo il resto del ciclo per sicurezza
            if not numeri_riga:
                continue
            # Scegliamo alcuni numeri da segnare in questa riga.
            # Per semplicità, segniamo il primo e, se esiste, il secondo numero.
            numeri_da_segnare = [numeri_riga[0]]
            if len(numeri_riga) > 1:
                numeri_da_segnare.append(numeri_riga[1])
            # Segniamo questi numeri usando il metodo segna_numero()
            for numero in numeri_da_segnare:
                self.cartella_default.segna_numero(numero)
            # Ora chiediamo i numeri segnati per questa riga
            numeri_segnati_riga = self.cartella_default.get_numeri_segnati_riga(numero_riga)
            # La lista attesa è la lista dei numeri che abbiamo segnato in questa riga,
            # ordinata in modo crescente
            numeri_attesi = sorted(numeri_da_segnare)
            # Verifica che i numeri segnati di quella riga siano esattamente quelli attesi
            self.assertEqual(
                numeri_segnati_riga,
                numeri_attesi,
                f"Nella riga {numero_riga} i numeri segnati non corrispondono a quelli attesi."
            )
            # Verifica che la lista sia ordinata (anche se già lo è, per coerenza)
            self.assertEqual(
                numeri_segnati_riga,
                sorted(numeri_segnati_riga),
                f"La lista restituita da get_numeri_segnati_riga({numero_riga}) deve essere ordinata in modo crescente."
            )



    """tests sulle eccezioni sollevate dal metodo get_numeri_segnati_riga()"""

    #test del metodo get_numeri_segnati_riga() - eccezione tipo numero_riga
    def test_get_numeri_segnati_riga_errore_tipo(self):
        """
        Verifica che get_numeri_segnati_riga() sollevi CartellaRigaTypeException
        quando il parametro 'numero_riga' non è un intero.
        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """
        # Caso 1: numero_riga è una stringa
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_numeri_segnati_riga("0")
        # Caso 2: numero_riga è un float
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_numeri_segnati_riga(1.5)
        # Caso 3: numero_riga è None
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_numeri_segnati_riga(None)
        # Caso 4: numero_riga è una lista
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_numeri_segnati_riga([1])


    #test del metodo get_numeri_segnati_riga() - eccezione valore numero_riga fuori range
    def test_get_numeri_segnati_riga_errore_valore_fuori_range(self):
        """
        Verifica che get_numeri_segnati_riga() sollevi CartellaRigaValueException
        quando il parametro 'numero_riga' è un intero ma fuori dal range valido 0, 1, 2.
        In questo test usiamo alcuni esempi di indici non validi
        (-1, 3, 10) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """
        # Caso 1: numero_riga negativo
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.get_numeri_segnati_riga(-1)
        # Caso 2: numero_riga troppo alto (uguale al numero di righe)
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.get_numeri_segnati_riga(3)
        # Caso 3: numero_riga molto oltre il limite
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.get_numeri_segnati_riga(10)


    #test del metodo get_numeri_segnati_colonna()
    def test_get_numeri_segnati_colonna(self):
        """
        Verifica che get_numeri_segnati_colonna() ritorni correttamente
        solo i numeri segnati presenti in ciascuna colonna della cartella.
        Per ogni colonna valida (0-8) il test:
        1) Ottiene tutti i numeri della colonna.
        2) Segna alcuni di questi numeri (simulando il gioco).
        3) Verifica che la lista restituita contenga SOLO i numeri segnati
            di quella colonna, in ordine crescente.
        """
        # La cartella ha sempre 9 colonne: indici da 0 a 8
        for numero_colonna in range(9):
            # Prima di tutto, resettiamo lo stato dei numeri segnati
            # così ogni colonna viene testata partendo da zero
            self.cartella_default.reset_cartella()
            # Otteniamo tutti i numeri presenti in questa colonna
            numeri_colonna = self.cartella_default.get_numeri_colonna(numero_colonna)
            # Se la colonna è vuota (può accadere per alcune colonne),
            # passiamo alla colonna successiva
            if not numeri_colonna:
                continue
            # Scegliamo alcuni numeri da segnare in questa colonna.
            # Per semplicità, segniamo il primo e, se esiste, il secondo numero.
            numeri_da_segnare = [numeri_colonna[0]]
            if len(numeri_colonna) > 1:
                numeri_da_segnare.append(numeri_colonna[1])
            # Segniamo questi numeri usando il metodo segna_numero()
            for numero in numeri_da_segnare:
                self.cartella_default.segna_numero(numero)
            # Ora chiediamo i numeri segnati per questa colonna
            numeri_segnati_colonna = self.cartella_default.get_numeri_segnati_colonna(numero_colonna)
            # La lista attesa è la lista dei numeri che abbiamo segnato
            # in questa colonna, ordinata in modo crescente
            numeri_attesi = sorted(numeri_da_segnare)
            # Verifica che i numeri segnati di quella colonna siano esattamente quelli attesi
            self.assertEqual(
                numeri_segnati_colonna,
                numeri_attesi,
                f"Nella colonna {numero_colonna} i numeri segnati non corrispondono a quelli attesi."
            )
            # Verifica che la lista sia ordinata (anche se già lo è, per coerenza)
            self.assertEqual(
                numeri_segnati_colonna,
                sorted(numeri_segnati_colonna),
                f"La lista restituita da get_numeri_segnati_colonna({numero_colonna}) deve essere ordinata in modo crescente."
            )



    """tests sulle eccezioni sollevate dal metodo get_numeri_segnati_colonna()"""

    #test del metodo get_numeri_segnati_colonna() - eccezione tipo numero_colonna
    def test_get_numeri_segnati_colonna_errore_tipo(self):
        """
        Verifica che get_numeri_segnati_colonna() sollevi CartellaColonnaTypeException
        quando il parametro 'numero_colonna' non è un intero.
        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """
        # Caso 1: numero_colonna è una stringa
        with self.assertRaises(CartellaColonnaTypeException):
            self.cartella_default.get_numeri_segnati_colonna("0")
        # Caso 2: numero_colonna è un float
        with self.assertRaises(CartellaColonnaTypeException):
            self.cartella_default.get_numeri_segnati_colonna(1.5)
        # Caso 3: numero_colonna è None
        with self.assertRaises(CartellaColonnaTypeException):
            self.cartella_default.get_numeri_segnati_colonna(None)
        # Caso 4: numero_colonna è una lista
        with self.assertRaises(CartellaColonnaTypeException):
            self.cartella_default.get_numeri_segnati_colonna([1])


    #test del metodo get_numeri_segnati_colonna() - eccezione valore numero_colonna fuori range
    def test_get_numeri_segnati_colonna_errore_valore_fuori_range(self):
        """
        Verifica che get_numeri_segnati_colonna() sollevi CartellaColonnaValueException
        quando il parametro 'numero_colonna' è un intero ma fuori dal range valido 0-8.
        In questo test usiamo alcuni esempi di indici non validi
        (-1, 9, 10) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """
        # Caso 1: numero_colonna negativo
        with self.assertRaises(CartellaColonnaValueException):
            self.cartella_default.get_numeri_segnati_colonna(-1)
        # Caso 2: numero_colonna troppo alto (uguale al numero di colonne)
        with self.assertRaises(CartellaColonnaValueException):
            self.cartella_default.get_numeri_segnati_colonna(9)
        # Caso 3: numero_colonna molto oltre il limite
        with self.assertRaises(CartellaColonnaValueException):
            self.cartella_default.get_numeri_segnati_colonna(10)


    #test del metodo conta_numeri_segnati()
    def test_conta_numeri_segnati(self):
        """
        Verifica che conta_numeri_segnati() conteggi correttamente
        quanti numeri sono stati segnati nella cartella.
        Il test controlla quattro situazioni:
        1) Cartella appena creata (nessun numero segnato) -> deve ritornare 0.
        2) Dopo aver segnato alcuni numeri distinti -> il conteggio deve corrispondere.
        3) Segnare due volte lo stesso numero -> il conteggio non deve aumentare due volte.
        4) Dopo aver segnato tutti i 15 numeri -> deve ritornare 15.
        """
        # Recupera tutti i numeri della cartella
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        # 1) Cartella appena creata: nessun numero segnato
        self.assertEqual(
            self.cartella_default.conta_numeri_segnati(),
            0,
            "All'inizio, conta_numeri_segnati() deve restituire 0."
        )
        # 2) Segna i primi tre numeri della cartella
        self.cartella_default.segna_numero(numeri_cartella[0])
        self.cartella_default.segna_numero(numeri_cartella[1])
        self.cartella_default.segna_numero(numeri_cartella[2])
        self.assertEqual(
            self.cartella_default.conta_numeri_segnati(),
            3,
            "Dopo aver segnato 3 numeri distinti, conta_numeri_segnati() deve restituire 3."
        )
        # 3) Prova a segnare di nuovo uno dei numeri già segnati
        self.cartella_default.segna_numero(numeri_cartella[1])
        self.assertEqual(
            self.cartella_default.conta_numeri_segnati(),
            3,
            "Segnare di nuovo lo stesso numero non deve incrementare il conteggio."
        )
        # 4) Segna tutti i numeri rimanenti della cartella
        for numero in numeri_cartella[3:]:
            self.cartella_default.segna_numero(numero)
        self.assertEqual(
            self.cartella_default.conta_numeri_segnati(),
            15,
            "Dopo aver segnato tutti i numeri, conta_numeri_segnati() deve restituire 15."
        )



    #test del metodo get_numeri_non_segnati()
    def test_get_numeri_non_segnati(self):
        """
        Verifica che get_numeri_non_segnati() ritorni correttamente
        il complemento dei numeri NON ancora segnati nella cartella.
        Il test controlla quattro situazioni:
        1) Cartella appena creata -> 15 numeri non segnati, uguali ai numeri della cartella.
        2) Dopo aver segnato alcuni numeri -> i non segnati diminuiscono e non contengono più i segnati.
        3) Verso la vittoria -> rimane 1 solo numero non segnato.
        4) TOMBOLA -> nessun numero non segnato, lista vuota.
        """
        # Recupera tutti i numeri della cartella (sempre 15 numeri ordinati)
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        # 1) Cartella appena creata: nessun numero segnato
        numeri_non_segnati = self.cartella_default.get_numeri_non_segnati()
        # Deve esserci ancora tutti i 15 numeri
        self.assertEqual(
            len(numeri_non_segnati),
            15,
            "All'inizio, get_numeri_non_segnati() deve restituire 15 numeri."
        )
        # Devono essere esattamente i numeri della cartella
        self.assertEqual(
            set(numeri_non_segnati),
            set(numeri_cartella),
            "All'inizio, i numeri non segnati devono coincidere con tutti i numeri della cartella."
        )
        # Devono essere ordinati
        self.assertEqual(
            numeri_non_segnati,
            sorted(numeri_non_segnati),
            "La lista dei numeri non segnati deve essere ordinata in modo crescente."
        )
        # 2) Segna 3 numeri e verifica che i non segnati si riducano
        numeri_da_segnare = numeri_cartella[:3]
        for numero in numeri_da_segnare:
            self.cartella_default.segna_numero(numero)
        numeri_non_segnati = self.cartella_default.get_numeri_non_segnati()
        # Dopo aver segnato 3 numeri, devono rimanere 12 numeri non segnati
        self.assertEqual(
            len(numeri_non_segnati),
            12,
            "Dopo aver segnato 3 numeri, devono rimanere 12 numeri non segnati."
        )
        # Nessuno dei numeri segnati deve comparire nella lista dei non segnati
        for numero in numeri_da_segnare:
            self.assertNotIn(
                numero,
                numeri_non_segnati,
                "Un numero segnato non deve comparire nella lista dei non segnati."
            )
        # 3) Segna tutti tranne l'ultimo: deve rimanere 1 solo numero non segnato
        # Segniamo tutti i numeri tranne l'ultimo della lista
        for numero in numeri_cartella[3:-1]:
            self.cartella_default.segna_numero(numero)
        numeri_non_segnati = self.cartella_default.get_numeri_non_segnati()
        self.assertEqual(
            len(numeri_non_segnati),
            1,
            "Se tutti i numeri tranne uno sono stati segnati, deve rimanere un solo numero non segnato."
        )
        # 4) TOMBOLA: segna anche l'ultimo numero rimasto
        ultimo_numero = numeri_non_segnati[0]
        self.cartella_default.segna_numero(ultimo_numero)
        numeri_non_segnati = self.cartella_default.get_numeri_non_segnati()
        # Ora non deve rimanere alcun numero non segnato
        self.assertEqual(
            len(numeri_non_segnati),
            0,
            "Dopo aver segnato tutti i numeri, get_numeri_non_segnati() deve restituire una lista vuota."
        )
        self.assertEqual(
            numeri_non_segnati,
            [],
            "La lista dei numeri non segnati deve essere vuota dopo la TOMBOLA."
        )



    #test del metodo get_percentuale_completamento()
    def test_get_percentuale_completamento(self):
        """
        Verifica che get_percentuale_completamento() calcoli correttamente
        la percentuale di completamento della cartella.
        Il test controlla tre situazioni principali:
        1) Nessun numero segnato -> 0.0%.
        2) Alcuni numeri segnati -> percentuale proporzionale, arrotondata a 1 decimale.
        3) Tutti i numeri segnati -> 100.0%.
        """
        # Recupera tutti i numeri della cartella (sempre 15)
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        # 1) Cartella appena creata: nessun numero segnato
        self.assertEqual(
            self.cartella_default.get_percentuale_completamento(),
            0.0,
            "All'inizio, la percentuale di completamento deve essere 0.0%."
        )
        # 2) Segna 5 numeri (su 15) e verifica la percentuale
        #    5 / 15 * 100 = 33.333..., che arrotondato a 1 decimale diventa 33.3
        for numero in numeri_cartella[:5]:
            self.cartella_default.segna_numero(numero)
        self.assertEqual(
            self.cartella_default.get_percentuale_completamento(),
            33.3,
            "Dopo aver segnato 5 numeri su 15, la percentuale deve essere 33.3%."
        )
        # 3) Segna tutti i numeri rimanenti e verifica la percentuale finale
        for numero in numeri_cartella[5:]:
            self.cartella_default.segna_numero(numero)
        self.assertEqual(
            self.cartella_default.get_percentuale_completamento(),
            100.0,
            "Dopo aver segnato tutti i 15 numeri, la percentuale deve essere 100.0%."
        )



    """test della sezione 3 riguardante la nostra doc string iniziale."""

    def test_get_stato_riga(self):
        """
        Verifica che get_stato_riga() ritorni correttamente un dizionario
        con tutte le informazioni sullo stato di una riga specifica.
        Per ogni riga valida (0, 1, 2) il test controlla:
        1) La struttura del dizionario: tutte le chiavi presenti.
        2) Riga senza numeri segnati: percentuale 0.0, conteggio 0.
        3) Riga con alcuni numeri segnati: dati coerenti e percentuale corretta.
        4) Riga completamente segnata: percentuale 100.0, conteggio uguale a totale.
        """

        # Recupera tutti i numeri della cartella
        numeri_cartella = self.cartella_default.get_numeri_cartella()

        # Per ogni riga della cartella: 0, 1, 2
        for numero_riga in range(3):
            # Reset dello stato per iniziare puliti per ogni riga
            self.cartella_default.reset_cartella()

            # Ottiene lo stato della riga senza aver segnato nulla
            stato_riga = self.cartella_default.get_stato_riga(numero_riga)

            # 1) Verifica la struttura del dizionario: tutte le chiavi devono essere presenti
            chiavi_attese = {
                'numero_riga',
                'numeri_totali',
                'numeri_riga',
                'numeri_segnati',
                'numeri_segnati_riga',
                'percentuale_completamento'
            }

            self.assertEqual(
                set(stato_riga.keys()),
                chiavi_attese,
                f"Il dizionario dello stato della riga {numero_riga} non contiene tutte le chiavi attese."
            )

            # 2) Riga senza numeri segnati
            self.assertEqual(
                stato_riga['numero_riga'],
                numero_riga,
                f"Il numero della riga nel dizionario non corrisponde all'indice richiesto."
            )

            self.assertEqual(
                stato_riga['numeri_totali'],
                5,
                f"Nella riga {numero_riga}, il totale dei numeri deve essere sempre 5."
            )

            self.assertEqual(
                stato_riga['numeri_segnati'],
                0,
                f"Nella riga {numero_riga}, all'inizio non deve esserci alcun numero segnato."
            )

            self.assertEqual(
                stato_riga['percentuale_completamento'],
                0.0,
                f"Nella riga {numero_riga}, la percentuale all'inizio deve essere 0.0%."
            )

            self.assertEqual(
                len(stato_riga['numeri_riga']),
                5,
                f"Nella riga {numero_riga}, la lista dei numeri deve contenere esattamente 5 elementi."
            )

            self.assertEqual(
                stato_riga['numeri_segnati_riga'],
                [],
                f"Nella riga {numero_riga}, all'inizio la lista dei numeri segnati deve essere vuota."
            )

            # 3) Segna alcuni numeri della riga e verifica la coerenza dei dati
            numeri_riga_lista = stato_riga['numeri_riga']

            # Segna i primi 2 numeri della riga
            self.cartella_default.segna_numero(numeri_riga_lista[0])
            self.cartella_default.segna_numero(numeri_riga_lista[1])

            stato_riga = self.cartella_default.get_stato_riga(numero_riga)

            # Dopo aver segnato 2 numeri su 5
            self.assertEqual(
                stato_riga['numeri_segnati'],
                2,
                f"Nella riga {numero_riga}, il conteggio dei numeri segnati deve essere 2."
            )

            self.assertEqual(
                len(stato_riga['numeri_segnati_riga']),
                2,
                f"Nella riga {numero_riga}, la lista dei numeri segnati deve contenere 2 elementi."
            )

            # La percentuale di 2 su 5 è 40.0%
            self.assertEqual(
                stato_riga['percentuale_completamento'],
                40.0,
                f"Nella riga {numero_riga}, con 2 numeri segnati su 5, la percentuale deve essere 40.0%."
            )

            # Verifica che i numeri segnati siano effettivamente i primi due
            self.assertEqual(
                stato_riga['numeri_segnati_riga'],
                [numeri_riga_lista[0], numeri_riga_lista[1]],
                f"Nella riga {numero_riga}, i numeri segnati devono corrispondere a quelli effettivamente segnati."
            )

            # 4) Segna tutti i numeri rimanenti della riga e verifica la completezza
            for numero in numeri_riga_lista[2:]:
                self.cartella_default.segna_numero(numero)

            stato_riga = self.cartella_default.get_stato_riga(numero_riga)

            # Dopo aver segnato tutti i 5 numeri
            self.assertEqual(
                stato_riga['numeri_segnati'],
                5,
                f"Nella riga {numero_riga}, il conteggio deve essere 5 dopo aver segnato tutti i numeri."
            )

            self.assertEqual(
                stato_riga['percentuale_completamento'],
                100.0,
                f"Nella riga {numero_riga}, la percentuale deve essere 100.0% quando tutti i numeri sono segnati."
            )

            self.assertEqual(
                set(stato_riga['numeri_segnati_riga']),
                set(stato_riga['numeri_riga']),
                f"Nella riga {numero_riga}, quando tutto è segnato, i numeri segnati devono essere uguali a tutti i numeri della riga."
            )


    """tests sulle eccezioni sollevate dal metodo get_stato_riga()"""

    #test del metodo get_stato_riga() - eccezione tipo numero_riga
    def test_get_stato_riga_errore_tipo(self):
        """
        Verifica che get_stato_riga() sollevi CartellaRigaTypeException
        quando il parametro 'numero_riga' non è un intero.
        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """
        # Caso 1: numero_riga è una stringa
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_stato_riga("0")
        # Caso 2: numero_riga è un float
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_stato_riga(1.5)
        # Caso 3: numero_riga è None
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_stato_riga(None)
        # Caso 4: numero_riga è una lista
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.get_stato_riga([1])


    #test del metodo get_stato_riga() - eccezione valore numero_riga fuori range
    def test_get_stato_riga_errore_valore_fuori_range(self):
        """
        Verifica che get_stato_riga() sollevi CartellaRigaValueException
        quando il parametro 'numero_riga' è un intero ma fuori dal range valido 0, 1, 2.
        In questo test usiamo alcuni esempi di indici non validi
        (-1, 3, 10) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """
        # Caso 1: numero_riga negativo
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.get_stato_riga(-1)
        # Caso 2: numero_riga troppo alto (uguale al numero di righe)
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.get_stato_riga(3)
        # Caso 3: numero_riga molto oltre il limite
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.get_stato_riga(10)



    #test del metodo get_stato_cartella()
    def test_get_stato_cartella(self):
        """
        Verifica che get_stato_cartella() ritorni correttamente
        un dizionario con le informazioni globali sulla cartella.
        Il test controlla tre situazioni:
        1) Cartella appena creata: nessun numero segnato.
        2) Cartella con alcuni numeri segnati.
        3) Cartella completamente segnata (TOMBOLA).
        In ogni situazione verifica coerenza tra conteggi, liste e percentuale.
        """

        # Recupera tutti i numeri della cartella (sempre 15 numeri ordinati)
        numeri_cartella = self.cartella_default.get_numeri_cartella()

        # 1) Cartella appena creata: nessun numero segnato
        stato = self.cartella_default.get_stato_cartella()

        # Verifica che tutte le chiavi attese siano presenti
        chiavi_attese = {
            'numeri_totali',
            'numeri_segnati',
            'numeri_non_segnati',
            'lista_numeri_cartella',
            'lista_numeri_non_segnati',
            'percentuale_completamento',
        }
        self.assertEqual(
            set(stato.keys()),
            chiavi_attese,
            "Il dizionario dello stato della cartella non contiene tutte le chiavi attese."
        )

        # Totale numeri deve essere 15
        self.assertEqual(
            stato['numeri_totali'],
            15,
            "Il numero totale di numeri nella cartella deve essere 15."
        )

        # Nessun numero segnato all'inizio
        self.assertEqual(
            stato['numeri_segnati'],
            0,
            "All'inizio non deve esserci alcun numero segnato."
        )

        # Tutti i numeri sono non segnati all'inizio
        self.assertEqual(
            stato['numeri_non_segnati'],
            15,
            "All'inizio devono mancare 15 numeri da segnare."
        )

        # La lista dei numeri della cartella deve coincidere con i numeri_cartella
        self.assertEqual(
            stato['lista_numeri_cartella'],
            numeri_cartella,
            "La lista dei numeri della cartella non corrisponde a get_numeri_cartella()."
        )

        # All'inizio, la lista dei non segnati deve contenere tutti e 15 i numeri
        self.assertEqual(
            set(stato['lista_numeri_non_segnati']),
            set(numeri_cartella),
            "All'inizio, lista_numeri_non_segnati deve contenere tutti i numeri della cartella."
        )

        # Percentuale di completamento iniziale deve essere 0.0
        self.assertEqual(
            stato['percentuale_completamento'],
            0.0,
            "All'inizio, la percentuale di completamento deve essere 0.0%."
        )

        # 2) Segna alcuni numeri (ad esempio i primi 4) e verifica lo stato
        numeri_da_segnare = numeri_cartella[:4]
        for numero in numeri_da_segnare:
            self.cartella_default.segna_numero(numero)

        stato = self.cartella_default.get_stato_cartella()

        # Ora devono essere segnati 4 numeri
        self.assertEqual(
            stato['numeri_segnati'],
            4,
            "Dopo aver segnato 4 numeri, numeri_segnati deve essere 4."
        )

        # Devono mancare 11 numeri (15 - 4)
        self.assertEqual(
            stato['numeri_non_segnati'],
            11,
            "Dopo aver segnato 4 numeri, numeri_non_segnati deve essere 11."
        )

        # Le due quantità devono sommare sempre al totale
        self.assertEqual(
            stato['numeri_segnati'] + stato['numeri_non_segnati'],
            stato['numeri_totali'],
            "numeri_segnati + numeri_non_segnati deve essere sempre uguale a numeri_totali."
        )

        # Nessuno dei numeri segnati deve comparire nella lista dei non segnati
        for numero in numeri_da_segnare:
            self.assertNotIn(
                numero,
                stato['lista_numeri_non_segnati'],
                "Un numero segnato non deve apparire in lista_numeri_non_segnati."
            )

        # La percentuale deve essere coerente con i numeri segnati
        # 4 su 15 -> (4 / 15 * 100) arrotondato a una cifra decimale
        percentuale_attesa = round((4 / 15) * 100, 1)
        self.assertEqual(
            stato['percentuale_completamento'],
            percentuale_attesa,
            "La percentuale di completamento non è coerente con il numero di numeri segnati."
        )

        # 3) Segna tutti i numeri rimanenti e verifica lo stato finale (TOMBOLA)
        for numero in numeri_cartella[4:]:
            self.cartella_default.segna_numero(numero)

        stato = self.cartella_default.get_stato_cartella()

        # Tutti i 15 numeri devono risultare segnati
        self.assertEqual(
            stato['numeri_segnati'],
            15,
            "Quando tutti i numeri sono segnati, numeri_segnati deve essere 15."
        )

        # Nessun numero deve risultare non segnato
        self.assertEqual(
            stato['numeri_non_segnati'],
            0,
            "Quando tutti i numeri sono segnati, numeri_non_segnati deve essere 0."
        )

        # La lista dei non segnati deve essere vuota
        self.assertEqual(
            stato['lista_numeri_non_segnati'],
            [],
            "Dopo la TOMBOLA, lista_numeri_non_segnati deve essere vuota."
        )

        # Percentuale di completamento deve essere 100.0
        self.assertEqual(
            stato['percentuale_completamento'],
            100.0,
            "Quando tutti i numeri sono segnati, la percentuale deve essere 100.0%."
        )





    """test riguardanti la sezione 5 della doc string iniziale"""

    def test_reset_cartella(self):
        """
            Verifica che reset_cartella() cancelli correttamente tutti i numeri segnati
            senza modificare i numeri della cartella né la loro disposizione.
            Il test controlla che:
            1) Dopo aver segnato alcuni numeri, il conteggio dei segnati sia > 0.
            2) Dopo reset_cartella(), il conteggio dei segnati torni a 0.
            3) Dopo reset_cartella(), tutti i 15 numeri risultino di nuovo "non segnati".
            4) La lista dei numeri della cartella e la matrice 3x9 rimangano invariate.
        """

        # Salva una copia dei numeri e della matrice PRIMA di segnare qualcosa
        numeri_iniziali = self.cartella_default.get_numeri_cartella()
        matrice_iniziale = [riga.copy() for riga in self.cartella_default.cartella]

        # Segna alcuni numeri (ad esempio i primi 4)
        numeri_da_segnare = numeri_iniziali[:4]
        for numero in numeri_da_segnare:
            self.cartella_default.segna_numero(numero)

        # Verifica che ci siano effettivamente numeri segnati
        self.assertGreater(
            self.cartella_default.conta_numeri_segnati(),
            0,
            "Dopo aver segnato alcuni numeri, conta_numeri_segnati() deve essere > 0."
        )

        # Verifica che get_numeri_non_segnati() sia inferiore a 15
        numeri_non_segnati_prima = self.cartella_default.get_numeri_non_segnati()
        self.assertLess(
            len(numeri_non_segnati_prima),
            15,
            "Dopo aver segnato alcuni numeri, la lista dei non segnati deve avere meno di 15 elementi."
        )

        # Esegue il reset della cartella
        self.cartella_default.reset_cartella()

        # 1) Dopo il reset, nessun numero deve risultare segnato
        self.assertEqual(
            self.cartella_default.conta_numeri_segnati(),
            0,
            "Dopo reset_cartella(), conta_numeri_segnati() deve ritornare 0."
        )

        # 2) Tutti i 15 numeri devono risultare di nuovo non segnati
        numeri_non_segnati_dopo = self.cartella_default.get_numeri_non_segnati()
        self.assertEqual(
            len(numeri_non_segnati_dopo),
            15,
            "Dopo reset_cartella(), devono risultare di nuovo 15 numeri non segnati."
        )
        self.assertEqual(
            set(numeri_non_segnati_dopo),
            set(numeri_iniziali),
            "Dopo reset_cartella(), i numeri non segnati devono coincidere con tutti i numeri della cartella."
        )

        # 3) La lista dei numeri della cartella non deve essere cambiata
        numeri_finali = self.cartella_default.get_numeri_cartella()
        self.assertEqual(
            numeri_finali,
            numeri_iniziali,
            "reset_cartella() non deve modificare i numeri della cartella."
        )

        # 4) La matrice 3x9 deve essere identica a prima
        for riga_idx in range(self.cartella_default.righe):
            self.assertEqual(
                self.cartella_default.cartella[riga_idx],
                matrice_iniziale[riga_idx],
                f"reset_cartella() non deve modificare la matrice nella riga {riga_idx}."
            )


    # metodi di test per la funzionalità get_griglia_semplice del modulo cartella 

    def test_get_griglia_semplice_struttura_dimensioni_e_tipi(self):
        """Ritorna una griglia 3x9 come tuple di tuple con celle di tipo int o '-'."""

        # Act: otteniamo la griglia semplice
        griglia_semplice = self.cartella_default.get_griglia_semplice()

        # Assert: la griglia esterna deve essere una tupla con 3 righe
        self.assertIsInstance(griglia_semplice, tuple, "La griglia deve essere una tupla (immutabile).")
        self.assertEqual(
            len(griglia_semplice),
            self.cartella_default.righe,
            "La griglia deve avere esattamente self.righe righe (attese 3)."
        )

        # Assert: ogni riga deve essere una tupla con 9 colonne
        for indice_riga, riga in enumerate(griglia_semplice):
            self.assertIsInstance(riga, tuple, f"La riga {indice_riga} deve essere una tupla (immutabile).")
            self.assertEqual(
                len(riga),
                self.cartella_default.colonne,
                f"La riga {indice_riga} deve avere esattamente self.colonne colonne (attese 9)."
            )

            # Assert: ogni cella deve essere int oppure la stringa "-"
            for indice_colonna, cella in enumerate(riga):
                self.assertTrue(
                    isinstance(cella, int) or cella == "-",
                    f"Cella non valida in riga {indice_riga}, colonna {indice_colonna}: {cella!r}."
                )

    def test_get_griglia_semplice_mappatura_none_in_trattino_e_numero_in_int(self):
        """Converte None -> '-' e mantiene i numeri come int (coerenza cella-per-cella)."""

        # Arrange: teniamo un riferimento alla matrice interna per confrontare i valori
        matrice_interna = self.cartella_default.cartella

        # Act
        griglia_semplice = self.cartella_default.get_griglia_semplice()

        # Assert: conversione corretta per ogni cella (3x9)
        for indice_riga in range(self.cartella_default.righe):
            for indice_colonna in range(self.cartella_default.colonne):
                valore_interno = matrice_interna[indice_riga][indice_colonna]
                valore_semplice = griglia_semplice[indice_riga][indice_colonna]

                if valore_interno is None:
                    self.assertEqual(
                        valore_semplice,
                        "-",
                        f"Atteso '-' dove la matrice interna ha None (riga {indice_riga}, colonna {indice_colonna})."
                    )
                else:
                    self.assertIsInstance(
                        valore_semplice,
                        int,
                        f"Atteso int dove la matrice interna ha un numero (riga {indice_riga}, colonna {indice_colonna})."
                    )
                    self.assertEqual(
                        valore_semplice,
                        valore_interno,
                        f"Il numero deve restare invariato (riga {indice_riga}, colonna {indice_colonna})."
                    )

    def test_get_griglia_semplice_contiene_tutti_e_soli_i_numeri_della_cartella(self):
        """Contiene esattamente i 15 numeri della cartella; il resto delle celle è '-'."""

        # Arrange: numeri canonici della cartella (15 numeri)
        numeri_cartella = self.cartella_default.get_numeri_cartella()

        # Act
        griglia_semplice = self.cartella_default.get_griglia_semplice()

        # Estraiamo tutti i numeri presenti nella griglia
        numeri_in_griglia = []
        for riga in griglia_semplice:
            for cella in riga:
                if isinstance(cella, int):
                    numeri_in_griglia.append(cella)

        # Assert: quantità numeri corretta
        self.assertEqual(
            len(numeri_in_griglia),
            15,
            "La griglia semplice deve contenere esattamente 15 numeri (tutte le altre celle sono '-')."
        )

        # Assert: gli stessi numeri (nessuno mancante e nessun extra)
        self.assertEqual(
            set(numeri_in_griglia),
            set(numeri_cartella),
            "I numeri presenti nella griglia devono coincidere con i 15 numeri della cartella."
        )

    def test_get_griglia_semplice_immutabile(self):
        """La griglia ritornata deve essere immutabile (tuple di tuple, non modificabile)."""

        griglia_semplice = self.cartella_default.get_griglia_semplice()

        # Assert: non posso riassegnare una riga
        with self.assertRaises(TypeError):
            griglia_semplice[0] = griglia_semplice[0]

        # Assert: non posso riassegnare una cella
        with self.assertRaises(TypeError):
            griglia_semplice[0][0] = griglia_semplice[0][0]

    def test_get_griglia_semplice_snapshot_non_si_modifica_se_cambio_matrice_interna(self):
        """La griglia ottenuta è uno snapshot: non cambia se la matrice interna viene modificata dopo."""

        # Act: otteniamo uno snapshot
        griglia_prima = self.cartella_default.get_griglia_semplice()

        # Arrange: cambiamo volutamente la matrice interna dopo aver ottenuto lo snapshot
        # (test white-box per garantire assenza di riferimenti condivisi).
        cella_modificata = None
        for indice_riga in range(self.cartella_default.righe):
            for indice_colonna in range(self.cartella_default.colonne):
                if self.cartella_default.cartella[indice_riga][indice_colonna] is not None:
                    cella_modificata = (indice_riga, indice_colonna)
                    self.cartella_default.cartella[indice_riga][indice_colonna] = None
                    break
            if cella_modificata is not None:
                break

        self.assertIsNotNone(
            cella_modificata,
            "Il test richiede una cella numerica da poter modificare nella matrice interna."
        )

        indice_riga_mod, indice_colonna_mod = cella_modificata

        # Assert: lo snapshot ottenuto PRIMA resta uguale a com'era
        # (quindi in quella posizione deve esserci ancora un int, non '-')
        self.assertIsInstance(
            griglia_prima[indice_riga_mod][indice_colonna_mod],
            int,
            "Lo snapshot deve restare invariato: una cella che era un numero deve restare un int."
        )

        # Assert: una chiamata successiva invece riflette la modifica (nella nuova griglia deve comparire '-')
        griglia_dopo = self.cartella_default.get_griglia_semplice()
        self.assertEqual(
            griglia_dopo[indice_riga_mod][indice_colonna_mod],
            "-",
            "La nuova chiamata deve riflettere la modifica della matrice interna (cella ora vuota -> '-')."
        )

    def test_get_griglia_semplice_stabile_a_stato_invariato(self):
        """Chiamate ripetute, a stato invariato, devono produrre la stessa griglia."""

        griglia_1 = self.cartella_default.get_griglia_semplice()
        griglia_2 = self.cartella_default.get_griglia_semplice()

        # Assert: contenuto deterministico
        self.assertEqual(griglia_1, griglia_2, "A stato invariato, la griglia semplice deve essere identica.")


    #metodi di test per la funzionalità del modulo cartella get_dati_visualizzazione_avanzata

    def test_get_dati_visualizzazione_avanzata_struttura_valore_ritorno(self):
        """Ritorna una tupla (griglia, stato_normalizzato, numeri_segnati_ordinati) con tipi attesi."""

        # Act
        dati = self.cartella_default.get_dati_visualizzazione_avanzata()

        # Assert: il pacchetto deve essere una tupla di 3 elementi
        self.assertIsInstance(dati, tuple, "Il pacchetto dati deve essere una tupla.")
        self.assertEqual(len(dati), 3, "Il pacchetto dati deve contenere esattamente 3 elementi.")

        griglia_semplice, stato_normalizzato, numeri_segnati_ordinati = dati

        # Assert: griglia semplice (già testata altrove, qui controlliamo solo la forma base)
        self.assertIsInstance(griglia_semplice, tuple, "La griglia semplice deve essere una tupla (immutabile).")
        self.assertEqual(len(griglia_semplice), self.cartella_default.righe, "La griglia deve avere 3 righe.")
        for riga in griglia_semplice:
            self.assertIsInstance(riga, tuple, "Ogni riga della griglia deve essere una tupla (immutabile).")
            self.assertEqual(len(riga), self.cartella_default.colonne, "Ogni riga deve avere 9 celle.")
            for cella in riga:
                self.assertTrue(
                    isinstance(cella, int) or cella == "-",
                    f"Ogni cella deve essere int o '-'. Trovato: {cella!r}"
                )

        # Assert: stato normalizzato
        self.assertIsInstance(stato_normalizzato, dict, "Lo stato normalizzato deve essere un dict.")

        # Assert: numeri segnati ordinati
        self.assertIsInstance(numeri_segnati_ordinati, tuple, "I numeri segnati ordinati devono essere una tupla.")
        for n in numeri_segnati_ordinati:
            self.assertIsInstance(n, int, f"I numeri segnati devono essere int. Trovato: {n!r}")

    def test_get_dati_visualizzazione_avanzata_griglia_coincide_con_get_griglia_semplice(self):
        """La griglia nel pacchetto deve coincidere con quella prodotta da get_griglia_semplice()."""

        # Arrange: griglia canonica
        griglia_attesa = self.cartella_default.get_griglia_semplice()

        # Act
        griglia_pacchetto, _, _ = self.cartella_default.get_dati_visualizzazione_avanzata()

        # Assert
        self.assertEqual(
            griglia_pacchetto,
            griglia_attesa,
            "La griglia nel pacchetto avanzato deve coincidere con get_griglia_semplice()."
        )

    def test_get_dati_visualizzazione_avanzata_stato_normalizzato_chiavi_e_tipi(self):
        """Lo stato normalizzato deve avere tutte le chiavi attese e tuple al posto delle liste."""

        # Act
        _, stato_normalizzato, _ = self.cartella_default.get_dati_visualizzazione_avanzata()

        # Assert: chiavi attese
        chiavi_attese = {
            "numeri_totali",
            "numeri_segnati",
            "numeri_non_segnati",
            "lista_numeri_cartella",
            "lista_numeri_non_segnati",
            "percentuale_completamento",
        }
        self.assertEqual(
            set(stato_normalizzato.keys()),
            chiavi_attese,
            "Lo stato normalizzato non contiene tutte le chiavi attese."
        )

        # Assert: tipi base (conteggi e percentuale)
        self.assertIsInstance(stato_normalizzato["numeri_totali"], int, "numeri_totali deve essere int.")
        self.assertIsInstance(stato_normalizzato["numeri_segnati"], int, "numeri_segnati deve essere int.")
        self.assertIsInstance(stato_normalizzato["numeri_non_segnati"], int, "numeri_non_segnati deve essere int.")
        self.assertIsInstance(
            stato_normalizzato["percentuale_completamento"],
            float,
            "percentuale_completamento deve essere float."
        )

        # Assert: liste normalizzate -> tuple
        self.assertIsInstance(
            stato_normalizzato["lista_numeri_cartella"],
            tuple,
            "lista_numeri_cartella deve essere una tupla (non una lista)."
        )
        self.assertIsInstance(
            stato_normalizzato["lista_numeri_non_segnati"],
            tuple,
            "lista_numeri_non_segnati deve essere una tupla (non una lista)."
        )

        # Assert: contenuti delle tuple (solo int)
        for n in stato_normalizzato["lista_numeri_cartella"]:
            self.assertIsInstance(n, int, f"lista_numeri_cartella deve contenere solo int. Trovato: {n!r}")
        for n in stato_normalizzato["lista_numeri_non_segnati"]:
            self.assertIsInstance(n, int, f"lista_numeri_non_segnati deve contenere solo int. Trovato: {n!r}")

    def test_get_dati_visualizzazione_avanzata_cartella_nuova_coerenza_iniziale(self):
        """A inizio partita: numeri segnati vuoti, non segnati=15, percentuale=0.0."""

        # Act
        _, stato_normalizzato, numeri_segnati_ordinati = self.cartella_default.get_dati_visualizzazione_avanzata()

        # Assert: nessun numero segnato
        self.assertEqual(
            numeri_segnati_ordinati,
            tuple(),
            "A inizio partita, numeri_segnati_ordinati deve essere vuota."
        )

        # Assert: coerenza conteggi
        self.assertEqual(stato_normalizzato["numeri_totali"], 15, "numeri_totali deve essere 15.")
        self.assertEqual(stato_normalizzato["numeri_segnati"], 0, "A inizio partita, numeri_segnati deve essere 0.")
        self.assertEqual(
            stato_normalizzato["numeri_non_segnati"],
            15,
            "A inizio partita, numeri_non_segnati deve essere 15."
        )
        self.assertEqual(
            stato_normalizzato["percentuale_completamento"],
            0.0,
            "A inizio partita, percentuale_completamento deve essere 0.0."
        )

        # Assert: lista non segnati coincide con lista cartella
        self.assertEqual(
            stato_normalizzato["lista_numeri_non_segnati"],
            stato_normalizzato["lista_numeri_cartella"],
            "A inizio partita, tutti i numeri devono risultare non segnati."
        )

    def test_get_dati_visualizzazione_avanzata_dopo_segnature_coerenza_stato_e_segnati(self):
        """Dopo alcune segnature: numeri_segnati_ordinati e stato_normalizzato devono essere coerenti."""

        # Arrange: scegliamo alcuni numeri reali della cartella e li segniamo
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        numeri_da_segnare = [numeri_cartella[0], numeri_cartella[1], numeri_cartella[2]]

        for numero in numeri_da_segnare:
            esito = self.cartella_default.segna_numero(numero)
            self.assertTrue(esito, f"Setup non riuscito: impossibile segnare il numero {numero}.")

        # Act
        _, stato_normalizzato, numeri_segnati_ordinati = self.cartella_default.get_dati_visualizzazione_avanzata()

        # Assert: numeri segnati ordinati corretti
        self.assertEqual(
            numeri_segnati_ordinati,
            tuple(sorted(numeri_da_segnare)),
            "numeri_segnati_ordinati deve contenere esattamente i numeri segnati, in ordine."
        )

        # Assert: conteggi coerenti
        self.assertEqual(
            stato_normalizzato["numeri_segnati"],
            len(numeri_da_segnare),
            "numeri_segnati deve coincidere con quanti numeri abbiamo segnato."
        )
        self.assertEqual(
            stato_normalizzato["numeri_non_segnati"],
            15 - len(numeri_da_segnare),
            "numeri_non_segnati deve essere il complemento rispetto ai 15 numeri totali."
        )

        # Assert: lista non segnati non deve contenere numeri segnati
        for numero in numeri_da_segnare:
            self.assertNotIn(
                numero,
                stato_normalizzato["lista_numeri_non_segnati"],
                "Un numero segnato non deve comparire nella lista dei non segnati."
            )

        # Assert: lista non segnati deve essere ordinata (tuple ma ordinata)
        self.assertEqual(
            stato_normalizzato["lista_numeri_non_segnati"],
            tuple(sorted(stato_normalizzato["lista_numeri_non_segnati"])),
            "lista_numeri_non_segnati deve essere ordinata in modo crescente."
        )

    def test_get_dati_visualizzazione_avanzata_tombola_coerenza_finale(self):
        """A cartella completa: non segnati vuota, segnati=15, percentuale=100.0."""

        # Arrange: segniamo tutti i numeri della cartella
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        for numero in numeri_cartella:
            esito = self.cartella_default.segna_numero(numero)
            self.assertTrue(esito, f"Setup non riuscito: impossibile segnare il numero {numero}.")

        # Act
        _, stato_normalizzato, numeri_segnati_ordinati = self.cartella_default.get_dati_visualizzazione_avanzata()

        # Assert: segnati = tutti i numeri della cartella (ordinati)
        self.assertEqual(
            numeri_segnati_ordinati,
            tuple(numeri_cartella),
            "A TOMBOLA, numeri_segnati_ordinati deve coincidere con tutti i numeri della cartella."
        )

        # Assert: coerenza conteggi e liste
        self.assertEqual(stato_normalizzato["numeri_segnati"], 15, "A TOMBOLA, numeri_segnati deve essere 15.")
        self.assertEqual(stato_normalizzato["numeri_non_segnati"], 0, "A TOMBOLA, numeri_non_segnati deve essere 0.")
        self.assertEqual(
            stato_normalizzato["lista_numeri_non_segnati"],
            tuple(),
            "A TOMBOLA, lista_numeri_non_segnati deve essere vuota."
        )
        self.assertEqual(
            stato_normalizzato["percentuale_completamento"],
            100.0,
            "A TOMBOLA, percentuale_completamento deve essere 100.0."
        )

    def test_get_dati_visualizzazione_avanzata_immutabilita_contenitori_ritornati(self):
        """I contenitori principali ritornati devono essere tuple (non modificabili)."""

        griglia_semplice, stato_normalizzato, numeri_segnati_ordinati = self.cartella_default.get_dati_visualizzazione_avanzata()

        # Assert: griglia e numeri segnati sono tuple (quindi non riassegnabili)
        with self.assertRaises(TypeError):
            griglia_semplice[0] = griglia_semplice[0]

        with self.assertRaises(TypeError):
            numeri_segnati_ordinati[0] = 999  # anche se vuota, TypeError comunque in caso di item assignment

        # Assert: le liste dentro lo stato sono tuple, quindi non hanno append e non sono modificabili
        lista_cartella = stato_normalizzato["lista_numeri_cartella"]
        lista_non_segnati = stato_normalizzato["lista_numeri_non_segnati"]

        self.assertIsInstance(lista_cartella, tuple, "lista_numeri_cartella deve essere una tupla.")
        self.assertIsInstance(lista_non_segnati, tuple, "lista_numeri_non_segnati deve essere una tupla.")

        # Tentativo di modifica: la tupla non supporta append
        with self.assertRaises(AttributeError):
            lista_cartella.append(1)

        with self.assertRaises(AttributeError):
            lista_non_segnati.append(1)


    #metodi di test dedicati alla validazione del metodo get_riga_semplice()

    def test_get_riga_semplice_errore_tipo_numero_riga(self):
        """Solleva CartellaRigaTypeException se numero_riga non è un int."""

        # Arrange: una serie di input volutamente di tipo errato
        valori_non_int = ["0", 1.0, None, [], (0,), {"riga": 0}]

        # Act + Assert: ogni valore deve generare l'eccezione di tipo
        for valore in valori_non_int:
            with self.assertRaises(CartellaRigaTypeException):
                self.cartella_default.get_riga_semplice(valore)

    def test_get_riga_semplice_errore_valore_fuori_range(self):
        """Solleva CartellaRigaValueException se numero_riga è fuori dal range valido 0..2."""

        # Arrange: indici riga fuori range (negativi e oltre l'ultima riga)
        valori_fuori_range = [-1, 3, 10, 999]

        # Act + Assert
        for valore in valori_fuori_range:
            with self.assertRaises(CartellaRigaValueException):
                self.cartella_default.get_riga_semplice(valore)

    def test_get_riga_semplice_formato_e_tipi_per_ogni_riga_valida(self):
        """Per ogni riga valida (0..2) ritorna una tupla di 9 celle con int o '-'."""

        # Act + Assert su tutte le righe valide
        for numero_riga in range(self.cartella_default.righe):
            riga_semplice = self.cartella_default.get_riga_semplice(numero_riga)

            # Assert: la riga deve essere una tupla (immutabile) e lunga 9
            self.assertIsInstance(riga_semplice, tuple, "La riga semplice deve essere una tupla (immutabile).")
            self.assertEqual(
                len(riga_semplice),
                self.cartella_default.colonne,
                "La riga semplice deve avere esattamente 9 celle."
            )

            # Assert: ogni cella deve essere int oppure "-"
            for indice_colonna, cella in enumerate(riga_semplice):
                self.assertTrue(
                    isinstance(cella, int) or cella == "-",
                    f"Cella non valida in riga {numero_riga}, colonna {indice_colonna}: {cella!r}."
                )

    def test_get_riga_semplice_coincide_con_get_griglia_semplice(self):
        """La riga ritornata deve coincidere con get_griglia_semplice()[numero_riga]."""

        # Arrange: griglia canonica
        griglia_semplice = self.cartella_default.get_griglia_semplice()

        # Act + Assert: confronto per ogni riga valida
        for numero_riga in range(self.cartella_default.righe):
            riga_semplice = self.cartella_default.get_riga_semplice(numero_riga)

            self.assertEqual(
                riga_semplice,
                griglia_semplice[numero_riga],
                f"La riga {numero_riga} deve coincidere con la riga estratta dalla griglia semplice."
            )

    def test_get_riga_semplice_immutabile(self):
        """La riga ritornata deve essere immutabile (tupla non modificabile)."""

        # Act
        riga_semplice = self.cartella_default.get_riga_semplice(0)

        # Assert: non deve essere possibile assegnare elementi
        with self.assertRaises(TypeError):
            riga_semplice[0] = riga_semplice[0]

    def test_get_riga_semplice_snapshot_non_cambia_se_matrice_interna_viene_modificata(self):
        """La riga ottenuta è uno snapshot: non cambia se la matrice interna cambia dopo."""

        # Arrange: scegliamo una riga valida e prendiamo uno snapshot
        numero_riga = 0
        riga_prima = self.cartella_default.get_riga_semplice(numero_riga)

        # Modifichiamo volutamente la matrice interna DOPO aver ottenuto lo snapshot.
        # Cerchiamo una cella numerica nella riga e la rendiamo None per creare una differenza.
        indice_colonna_modificata = None
        for indice_colonna in range(self.cartella_default.colonne):
            if self.cartella_default.cartella[numero_riga][indice_colonna] is not None:
                indice_colonna_modificata = indice_colonna
                self.cartella_default.cartella[numero_riga][indice_colonna] = None
                break

        self.assertIsNotNone(
            indice_colonna_modificata,
            "Il test richiede almeno una cella numerica nella riga per poter simulare una modifica."
        )

        # Assert: la riga ottenuta PRIMA deve restare invariata (in quella cella deve restare un int)
        self.assertIsInstance(
            riga_prima[indice_colonna_modificata],
            int,
            "Lo snapshot della riga deve restare invariato: una cella che era un numero deve restare un int."
        )

        # Assert: una nuova chiamata deve riflettere la modifica (ora la cella deve diventare '-')
        riga_dopo = self.cartella_default.get_riga_semplice(numero_riga)
        self.assertEqual(
            riga_dopo[indice_colonna_modificata],
            "-",
            "La nuova chiamata deve riflettere la modifica della matrice interna (None -> '-')."
        )


    #metodi per test del metodo get_dati_visualizzazione_avanzata_riga

    def test_get_dati_visualizzazione_riga_avanzata_errore_tipo_numero_riga(self):
        """Solleva CartellaRigaTypeException se numero_riga non è un int."""

        # Arrange: input volutamente di tipo errato
        valori_non_int = ["0", 1.0, None, [], (0,), {"riga": 0}]

        # Act + Assert
        for valore in valori_non_int:
            with self.assertRaises(CartellaRigaTypeException):
                self.cartella_default.get_dati_visualizzazione_riga_avanzata(valore)

    def test_get_dati_visualizzazione_riga_avanzata_errore_valore_fuori_range(self):
        """Solleva CartellaRigaValueException se numero_riga è fuori dal range valido 0..2."""

        # Arrange: indici riga non validi
        valori_fuori_range = [-1, 3, 10, 999]

        # Act + Assert
        for valore in valori_fuori_range:
            with self.assertRaises(CartellaRigaValueException):
                self.cartella_default.get_dati_visualizzazione_riga_avanzata(valore)

    def test_get_dati_visualizzazione_riga_avanzata_struttura_e_tipi_ritorno(self):
        """Ritorna (riga_semplice, stato_riga_normalizzato, numeri_segnati_riga_ordinati) con tipi attesi."""

        # Arrange
        numero_riga = 0

        # Act
        dati = self.cartella_default.get_dati_visualizzazione_riga_avanzata(numero_riga)

        # Assert: pacchetto a 3 elementi
        self.assertIsInstance(dati, tuple, "Il pacchetto deve essere una tupla.")
        self.assertEqual(len(dati), 3, "Il pacchetto deve contenere esattamente 3 elementi.")

        riga_semplice, stato_riga_normalizzato, numeri_segnati_riga_ordinati = dati

        # Assert: riga semplice (9 celle, int o '-')
        self.assertIsInstance(riga_semplice, tuple, "riga_semplice deve essere una tupla (immutabile).")
        self.assertEqual(len(riga_semplice), self.cartella_default.colonne, "riga_semplice deve avere 9 celle.")
        for indice_colonna, cella in enumerate(riga_semplice):
            self.assertTrue(
                isinstance(cella, int) or cella == "-",
                f"Cella non valida in colonna {indice_colonna}: {cella!r}."
            )

        # Assert: stato normalizzato
        self.assertIsInstance(stato_riga_normalizzato, dict, "stato_riga_normalizzato deve essere un dict.")

        chiavi_attese = {
            "numeri_totali",
            "numeri_segnati",
            "numeri_riga",
            "numeri_segnati_riga",
            "percentuale_completamento",
        }
        self.assertEqual(
            set(stato_riga_normalizzato.keys()),
            chiavi_attese,
            "stato_riga_normalizzato non contiene tutte le chiavi attese."
        )

        # Assert: tipi dei campi normalizzati
        self.assertIsInstance(stato_riga_normalizzato["numeri_totali"], int, "numeri_totali deve essere int.")
        self.assertIsInstance(stato_riga_normalizzato["numeri_segnati"], int, "numeri_segnati deve essere int.")
        self.assertIsInstance(stato_riga_normalizzato["numeri_riga"], tuple, "numeri_riga deve essere tuple.")
        self.assertIsInstance(
            stato_riga_normalizzato["numeri_segnati_riga"],
            tuple,
            "numeri_segnati_riga deve essere tuple."
        )
        self.assertIsInstance(
            stato_riga_normalizzato["percentuale_completamento"],
            float,
            "percentuale_completamento deve essere float."
        )

        # Assert: contenuto tuple stato (solo int)
        for n in stato_riga_normalizzato["numeri_riga"]:
            self.assertIsInstance(n, int, f"numeri_riga deve contenere solo int. Trovato: {n!r}")
        for n in stato_riga_normalizzato["numeri_segnati_riga"]:
            self.assertIsInstance(n, int, f"numeri_segnati_riga deve contenere solo int. Trovato: {n!r}")

        # Assert: numeri segnati ordinati
        self.assertIsInstance(
            numeri_segnati_riga_ordinati,
            tuple,
            "numeri_segnati_riga_ordinati deve essere una tupla."
        )
        for n in numeri_segnati_riga_ordinati:
            self.assertIsInstance(n, int, f"numeri_segnati_riga_ordinati deve contenere solo int. Trovato: {n!r}")

        # Deve essere ordinata
        self.assertEqual(
            numeri_segnati_riga_ordinati,
            tuple(sorted(numeri_segnati_riga_ordinati)),
            "numeri_segnati_riga_ordinati deve essere ordinata in modo crescente."
        )

    def test_get_dati_visualizzazione_riga_avanzata_riga_coerente_con_griglia_semplice(self):
        """riga_semplice deve coincidere con get_griglia_semplice()[numero_riga]."""

        for numero_riga in range(self.cartella_default.righe):
            # Arrange: griglia canonica
            griglia_semplice = self.cartella_default.get_griglia_semplice()

            # Act
            riga_semplice, _, _ = self.cartella_default.get_dati_visualizzazione_riga_avanzata(numero_riga)

            # Assert
            self.assertEqual(
                riga_semplice,
                griglia_semplice[numero_riga],
                f"riga_semplice deve coincidere con la riga {numero_riga} estratta dalla griglia semplice."
            )

    def test_get_dati_visualizzazione_riga_avanzata_stato_coerente_con_get_stato_riga(self):
        """stato_riga_normalizzato deve essere coerente con get_stato_riga() e avere tuple al posto di liste."""

        # Arrange
        numero_riga = 0
        stato_originale = self.cartella_default.get_stato_riga(numero_riga)

        # Act
        _, stato_riga_normalizzato, numeri_segnati_riga_ordinati = self.cartella_default.get_dati_visualizzazione_riga_avanzata(numero_riga)

        # Assert: coerenza conteggi/percentuale
        self.assertEqual(
            stato_riga_normalizzato["numeri_totali"],
            int(stato_originale["numeri_totali"]),
            "numeri_totali normalizzato deve coincidere con quello dello stato originale."
        )
        self.assertEqual(
            stato_riga_normalizzato["numeri_segnati"],
            int(stato_originale["numeri_segnati"]),
            "numeri_segnati normalizzato deve coincidere con quello dello stato originale."
        )
        self.assertEqual(
            stato_riga_normalizzato["percentuale_completamento"],
            float(stato_originale["percentuale_completamento"]),
            "percentuale_completamento normalizzato deve coincidere con quella dello stato originale."
        )

        # Assert: liste convertite in tuple e contenuto coerente
        self.assertEqual(
            stato_riga_normalizzato["numeri_riga"],
            tuple(int(n) for n in stato_originale["numeri_riga"]),
            "numeri_riga normalizzato deve coincidere con i numeri_riga originali (ma come tupla)."
        )
        self.assertEqual(
            stato_riga_normalizzato["numeri_segnati_riga"],
            tuple(int(n) for n in stato_originale["numeri_segnati_riga"]),
            "numeri_segnati_riga normalizzato deve coincidere con i numeri_segnati_riga originali (ma come tupla)."
        )

        # Assert: la tupla numeri_segnati_riga_ordinati deve essere la versione ordinata dei segnati riga
        self.assertEqual(
            numeri_segnati_riga_ordinati,
            tuple(sorted(stato_riga_normalizzato["numeri_segnati_riga"])),
            "numeri_segnati_riga_ordinati deve essere l'ordinamento di numeri_segnati_riga."
        )

    def test_get_dati_visualizzazione_riga_avanzata_scenario_iniziale_nessun_segnato(self):
        """Scenario iniziale: nessun numero segnato nella riga -> segnati vuoti e percentuale 0.0."""

        # Arrange
        numero_riga = 0

        # Act
        _, stato_riga_normalizzato, numeri_segnati_riga_ordinati = self.cartella_default.get_dati_visualizzazione_riga_avanzata(numero_riga)

        # Assert: a inizio partita, la riga non ha segnati
        self.assertEqual(
            stato_riga_normalizzato["numeri_segnati"],
            0,
            "All'inizio, numeri_segnati della riga deve essere 0."
        )
        self.assertEqual(
            stato_riga_normalizzato["percentuale_completamento"],
            0.0,
            "All'inizio, percentuale_completamento della riga deve essere 0.0."
        )
        self.assertEqual(
            stato_riga_normalizzato["numeri_segnati_riga"],
            tuple(),
            "All'inizio, numeri_segnati_riga deve essere vuota."
        )
        self.assertEqual(
            numeri_segnati_riga_ordinati,
            tuple(),
            "All'inizio, numeri_segnati_riga_ordinati deve essere vuota."
        )

    def test_get_dati_visualizzazione_riga_avanzata_scenario_parziale_alcuni_segnati(self):
        """Scenario parziale: segnando 2 numeri della riga, i segnati e i conteggi devono aggiornarsi."""

        # Arrange: scegliamo una riga e prendiamo i suoi numeri reali
        numero_riga = 0
        numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)

        # Per regola di generazione, una riga ha 5 numeri; comunque rendiamo il test difensivo.
        self.assertTrue(len(numeri_riga) >= 2, "Setup test: la riga deve avere almeno 2 numeri da segnare.")

        numeri_da_segnare = [numeri_riga[0], numeri_riga[1]]

        # Segniamo i due numeri scelti
        for numero in numeri_da_segnare:
            esito = self.cartella_default.segna_numero(numero)
            self.assertTrue(esito, f"Setup non riuscito: impossibile segnare il numero {numero}.")

        # Act
        _, stato_riga_normalizzato, numeri_segnati_riga_ordinati = self.cartella_default.get_dati_visualizzazione_riga_avanzata(numero_riga)

        # Assert: conteggi coerenti
        self.assertEqual(
            stato_riga_normalizzato["numeri_segnati"],
            2,
            "Dopo aver segnato 2 numeri della riga, numeri_segnati deve essere 2."
        )

        # Assert: segnati riga coerenti (possono essere tuple non ordinate, ma devono contenere i 2 numeri)
        self.assertEqual(
            set(stato_riga_normalizzato["numeri_segnati_riga"]),
            set(numeri_da_segnare),
            "numeri_segnati_riga deve contenere esattamente i numeri segnati nella riga."
        )

        # Assert: ordinati correttamente
        self.assertEqual(
            numeri_segnati_riga_ordinati,
            tuple(sorted(numeri_da_segnare)),
            "numeri_segnati_riga_ordinati deve contenere i numeri segnati, ordinati."
        )

    def test_get_dati_visualizzazione_riga_avanzata_scenario_completo_tutti_segnati(self):
        """Scenario completo: segnando tutti i numeri della riga -> percentuale 100.0 e segnati == numeri_riga."""

        # Arrange
        numero_riga = 0
        numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)

        # Segniamo tutti i numeri della riga scelta
        for numero in numeri_riga:
            esito = self.cartella_default.segna_numero(numero)
            self.assertTrue(esito, f"Setup non riuscito: impossibile segnare il numero {numero}.")

        # Act
        _, stato_riga_normalizzato, numeri_segnati_riga_ordinati = self.cartella_default.get_dati_visualizzazione_riga_avanzata(numero_riga)

        # Assert: conteggi e percentuale
        self.assertEqual(
            stato_riga_normalizzato["numeri_totali"],
            len(numeri_riga),
            "numeri_totali deve coincidere con i numeri effettivi della riga."
        )
        self.assertEqual(
            stato_riga_normalizzato["numeri_segnati"],
            len(numeri_riga),
            "Con riga completa, numeri_segnati deve essere uguale a numeri_totali."
        )
        self.assertEqual(
            stato_riga_normalizzato["percentuale_completamento"],
            100.0,
            "Con riga completa, percentuale_completamento deve essere 100.0."
        )

        # Assert: segnati == tutti i numeri riga (come insieme)
        self.assertEqual(
            set(stato_riga_normalizzato["numeri_segnati_riga"]),
            set(numeri_riga),
            "Con riga completa, numeri_segnati_riga deve contenere tutti i numeri della riga."
        )

        # Assert: ordinati
        self.assertEqual(
            numeri_segnati_riga_ordinati,
            tuple(sorted(numeri_riga)),
            "Con riga completa, numeri_segnati_riga_ordinati deve coincidere con i numeri della riga ordinati."
        )

    def test_get_dati_visualizzazione_riga_avanzata_immutabilita_contenitori(self):
        """Le tuple esposte (riga e liste normalizzate) non devono essere modificabili."""

        # Arrange
        numero_riga = 0

        # Act
        riga_semplice, stato_riga_normalizzato, numeri_segnati_riga_ordinati = self.cartella_default.get_dati_visualizzazione_riga_avanzata(numero_riga)

        # Assert: riga semplice immutabile (tupla)
        with self.assertRaises(TypeError):
            riga_semplice[0] = riga_semplice[0]

        # Assert: numeri_segnati_riga_ordinati è tupla (non assegnabile)
        # Nota: l'assegnazione per indice deve fallire anche se la tupla è vuota (TypeError sull'item assignment).
        with self.assertRaises(TypeError):
            numeri_segnati_riga_ordinati[0] = 999

        # Assert: tuple nello stato non hanno append (quindi non modificabili come liste)
        numeri_riga_tuple = stato_riga_normalizzato["numeri_riga"]
        numeri_segnati_riga_tuple = stato_riga_normalizzato["numeri_segnati_riga"]

        self.assertIsInstance(numeri_riga_tuple, tuple, "numeri_riga deve essere una tupla.")
        self.assertIsInstance(numeri_segnati_riga_tuple, tuple, "numeri_segnati_riga deve essere una tupla.")

        with self.assertRaises(AttributeError):
            numeri_riga_tuple.append(1)

        with self.assertRaises(AttributeError):
            numeri_segnati_riga_tuple.append(1)


    #metodi di test per get_colonna_semplice

    def test_get_colonna_semplice_errore_tipo_numero_colonna(self):
        """Solleva CartellaColonnaTypeException se numero_colonna non è un int."""

        # Arrange: input volutamente di tipo errato
        valori_non_int = ["0", 1.0, None, [], (0,), {"colonna": 0}]

        # Act + Assert
        for valore in valori_non_int:
            with self.assertRaises(CartellaColonnaTypeException):
                self.cartella_default.get_colonna_semplice(valore)

    def test_get_colonna_semplice_errore_valore_fuori_range(self):
        """Solleva CartellaColonnaValueException se numero_colonna è fuori dal range valido 0..8."""

        # Arrange: indici colonna non validi
        valori_fuori_range = [-1, 9, 10, 999]

        # Act + Assert
        for valore in valori_fuori_range:
            with self.assertRaises(CartellaColonnaValueException):
                self.cartella_default.get_colonna_semplice(valore)

    def test_get_colonna_semplice_formato_e_tipi_per_ogni_colonna_valida(self):
        """Per ogni colonna valida (0..8) ritorna una tupla di 3 celle con int o '-'."""

        # Act + Assert su tutte le colonne valide
        for numero_colonna in range(self.cartella_default.colonne):
            colonna_semplice = self.cartella_default.get_colonna_semplice(numero_colonna)

            # Assert: la colonna deve essere una tupla (immutabile) e lunga 3 (una cella per riga)
            self.assertIsInstance(colonna_semplice, tuple, "La colonna semplice deve essere una tupla (immutabile).")
            self.assertEqual(
                len(colonna_semplice),
                self.cartella_default.righe,
                "La colonna semplice deve avere esattamente 3 celle (una per riga)."
            )

            # Assert: ogni cella deve essere int oppure "-"
            for indice_riga, cella in enumerate(colonna_semplice):
                self.assertTrue(
                    isinstance(cella, int) or cella == "-",
                    f"Cella non valida in riga {indice_riga}, colonna {numero_colonna}: {cella!r}."
                )

    def test_get_colonna_semplice_coincide_con_get_griglia_semplice(self):
        """La colonna ritornata deve coincidere con i valori della griglia semplice (ordine alto->basso)."""

        # Arrange: griglia canonica
        griglia_semplice = self.cartella_default.get_griglia_semplice()

        # Act + Assert: confronto per ogni colonna valida
        for numero_colonna in range(self.cartella_default.colonne):
            colonna_semplice = self.cartella_default.get_colonna_semplice(numero_colonna)

            colonna_attesa = (
                griglia_semplice[0][numero_colonna],
                griglia_semplice[1][numero_colonna],
                griglia_semplice[2][numero_colonna],
            )

            self.assertEqual(
                colonna_semplice,
                colonna_attesa,
                f"La colonna {numero_colonna} deve coincidere con la colonna estratta dalla griglia semplice."
            )

    def test_get_colonna_semplice_immutabile(self):
        """La colonna ritornata deve essere immutabile (tupla non modificabile)."""

        # Act
        colonna_semplice = self.cartella_default.get_colonna_semplice(0)

        # Assert: non deve essere possibile assegnare elementi
        with self.assertRaises(TypeError):
            colonna_semplice[0] = colonna_semplice[0]


    def test_get_colonna_semplice_snapshot_non_cambia_se_matrice_interna_viene_modificata(self):
        """La colonna ottenuta è uno snapshot: non cambia se la matrice interna cambia dopo."""

        # Arrange: scegliamo una colonna che contenga ALMENO un numero.
        # Nota: alcune colonne possono essere vuote (tutte None), quindi non possiamo fissare colonna=0.
        numero_colonna = None
        indice_riga_con_numero = None

        for c in range(self.cartella_default.colonne):
            for r in range(self.cartella_default.righe):
                if self.cartella_default.cartella[r][c] is not None:
                    numero_colonna = c
                    indice_riga_con_numero = r
                    break
            if numero_colonna is not None:
                break

        # Se non troviamo nessun numero nella matrice, la cartella è invalida per definizione.
        self.assertIsNotNone(
            numero_colonna,
            "Setup test fallito: non è stato trovato alcun numero nella matrice interna della cartella."
        )
        self.assertIsNotNone(
            indice_riga_con_numero,
            "Setup test fallito: non è stata trovata alcuna riga con un numero nella colonna selezionata."
        )

        # Act: prendiamo uno snapshot PRIMA della modifica
        colonna_prima = self.cartella_default.get_colonna_semplice(numero_colonna)

        # Salviamo il valore originale per avere un controllo extra (debug/robustezza)
        valore_originale = self.cartella_default.cartella[indice_riga_con_numero][numero_colonna]
        self.assertIsInstance(
            valore_originale,
            int,
            "Setup test fallito: la cella selezionata dovrebbe contenere un int prima della modifica."
        )

        # Modifichiamo volutamente la matrice interna DOPO aver ottenuto lo snapshot.
        # Rendiamo None la cella numerica trovata, così la colonna semplice deve mostrare '-' in una nuova chiamata.
        self.cartella_default.cartella[indice_riga_con_numero][numero_colonna] = None

        # Assert: lo snapshot ottenuto PRIMA deve restare invariato (in quella posizione deve restare un int)
        self.assertIsInstance(
            colonna_prima[indice_riga_con_numero],
            int,
            "Lo snapshot della colonna deve restare invariato: una cella che era un numero deve restare un int."
        )
        self.assertEqual(
            colonna_prima[indice_riga_con_numero],
            valore_originale,
            "Lo snapshot della colonna deve conservare il valore originale della cella (non deve cambiare)."
        )

        # Assert: una nuova chiamata deve riflettere la modifica (ora la cella deve diventare '-')
        colonna_dopo = self.cartella_default.get_colonna_semplice(numero_colonna)
        self.assertEqual(
            colonna_dopo[indice_riga_con_numero],
            "-",
            "La nuova chiamata deve riflettere la modifica della matrice interna (None -> '-')."
        )


    #test per metodo get_dati_visualizzazione_colonna_avanzata

    def test_get_dati_visualizzazione_colonna_avanzata_errore_tipo_numero_colonna(self):
        """Solleva CartellaColonnaTypeException se numero_colonna non è un int."""

        # Arrange: input volutamente di tipo errato
        valori_non_int = ["0", 1.0, None, [], (0,), {"colonna": 0}]

        # Act + Assert
        for valore in valori_non_int:
            with self.assertRaises(CartellaColonnaTypeException):
                self.cartella_default.get_dati_visualizzazione_colonna_avanzata(valore)

    def test_get_dati_visualizzazione_colonna_avanzata_errore_valore_fuori_range(self):
        """Solleva CartellaColonnaValueException se numero_colonna è fuori dal range valido 0..8."""

        # Arrange: indici colonna non validi
        valori_fuori_range = [-1, 9, 10, 999]

        # Act + Assert
        for valore in valori_fuori_range:
            with self.assertRaises(CartellaColonnaValueException):
                self.cartella_default.get_dati_visualizzazione_colonna_avanzata(valore)

    def test_get_dati_visualizzazione_colonna_avanzata_struttura_e_tipi_ritorno(self):
        """Ritorna (colonna_semplice, stato_colonna_normalizzato, numeri_segnati_colonna_ordinati) con tipi attesi."""

        # Arrange
        numero_colonna = 0

        # Act
        dati = self.cartella_default.get_dati_visualizzazione_colonna_avanzata(numero_colonna)

        # Assert: pacchetto a 3 elementi
        self.assertIsInstance(dati, tuple, "Il pacchetto deve essere una tupla.")
        self.assertEqual(len(dati), 3, "Il pacchetto deve contenere esattamente 3 elementi.")

        colonna_semplice, stato_colonna_normalizzato, numeri_segnati_colonna_ordinati = dati

        # Assert: colonna semplice (3 celle, int o '-')
        self.assertIsInstance(colonna_semplice, tuple, "colonna_semplice deve essere una tupla (immutabile).")
        self.assertEqual(
            len(colonna_semplice),
            self.cartella_default.righe,
            "colonna_semplice deve avere 3 celle (una per riga)."
        )
        for indice_riga, cella in enumerate(colonna_semplice):
            self.assertTrue(
                isinstance(cella, int) or cella == "-",
                f"Cella non valida in riga {indice_riga}: {cella!r}."
            )

        # Assert: stato normalizzato
        self.assertIsInstance(stato_colonna_normalizzato, dict, "stato_colonna_normalizzato deve essere un dict.")

        chiavi_attese = {
            "numeri_totali",
            "numeri_segnati",
            "numeri_colonna",
            "numeri_segnati_colonna",
            "percentuale_completamento",
        }
        self.assertEqual(
            set(stato_colonna_normalizzato.keys()),
            chiavi_attese,
            "stato_colonna_normalizzato non contiene tutte le chiavi attese."
        )

        # Assert: tipi dei campi normalizzati
        self.assertIsInstance(stato_colonna_normalizzato["numeri_totali"], int, "numeri_totali deve essere int.")
        self.assertIsInstance(stato_colonna_normalizzato["numeri_segnati"], int, "numeri_segnati deve essere int.")
        self.assertIsInstance(stato_colonna_normalizzato["numeri_colonna"], tuple, "numeri_colonna deve essere tuple.")
        self.assertIsInstance(
            stato_colonna_normalizzato["numeri_segnati_colonna"],
            tuple,
            "numeri_segnati_colonna deve essere tuple."
        )
        self.assertIsInstance(
            stato_colonna_normalizzato["percentuale_completamento"],
            float,
            "percentuale_completamento deve essere float."
        )

        # Assert: contenuto tuple stato (solo int)
        for n in stato_colonna_normalizzato["numeri_colonna"]:
            self.assertIsInstance(n, int, f"numeri_colonna deve contenere solo int. Trovato: {n!r}")
        for n in stato_colonna_normalizzato["numeri_segnati_colonna"]:
            self.assertIsInstance(n, int, f"numeri_segnati_colonna deve contenere solo int. Trovato: {n!r}")

        # Assert: numeri segnati ordinati
        self.assertIsInstance(
            numeri_segnati_colonna_ordinati,
            tuple,
            "numeri_segnati_colonna_ordinati deve essere una tupla."
        )
        for n in numeri_segnati_colonna_ordinati:
            self.assertIsInstance(
                n,
                int,
                f"numeri_segnati_colonna_ordinati deve contenere solo int. Trovato: {n!r}"
            )

        # Deve essere ordinata
        self.assertEqual(
            numeri_segnati_colonna_ordinati,
            tuple(sorted(numeri_segnati_colonna_ordinati)),
            "numeri_segnati_colonna_ordinati deve essere ordinata in modo crescente."
        )

    def test_get_dati_visualizzazione_colonna_avanzata_colonna_coerente_con_griglia_semplice(self):
        """colonna_semplice deve coincidere con get_griglia_semplice() (ordine alto->basso)."""

        # Arrange: griglia canonica
        griglia_semplice = self.cartella_default.get_griglia_semplice()

        # Act + Assert: confronto per ogni colonna valida
        for numero_colonna in range(self.cartella_default.colonne):
            colonna_semplice, _, _ = self.cartella_default.get_dati_visualizzazione_colonna_avanzata(numero_colonna)

            colonna_attesa = (
                griglia_semplice[0][numero_colonna],
                griglia_semplice[1][numero_colonna],
                griglia_semplice[2][numero_colonna],
            )

            self.assertEqual(
                colonna_semplice,
                colonna_attesa,
                f"colonna_semplice deve coincidere con la colonna {numero_colonna} estratta dalla griglia semplice."
            )

    def test_get_dati_visualizzazione_colonna_avanzata_stato_coerente_con_metodi_colonna(self):
        """stato_colonna_normalizzato deve essere coerente con get_numeri_colonna e get_numeri_segnati_colonna."""

        # Arrange
        numero_colonna = 0
        numeri_colonna = self.cartella_default.get_numeri_colonna(numero_colonna)
        numeri_segnati_colonna = self.cartella_default.get_numeri_segnati_colonna(numero_colonna)

        # Act
        _, stato_colonna_normalizzato, numeri_segnati_colonna_ordinati = self.cartella_default.get_dati_visualizzazione_colonna_avanzata(numero_colonna)

        # Assert: conteggi coerenti con le liste di partenza
        self.assertEqual(
            stato_colonna_normalizzato["numeri_totali"],
            len(numeri_colonna),
            "numeri_totali deve coincidere con len(get_numeri_colonna())."
        )
        self.assertEqual(
            stato_colonna_normalizzato["numeri_segnati"],
            len(numeri_segnati_colonna),
            "numeri_segnati deve coincidere con len(get_numeri_segnati_colonna())."
        )

        # Assert: liste convertite in tuple e contenuto coerente
        self.assertEqual(
            stato_colonna_normalizzato["numeri_colonna"],
            tuple(int(n) for n in numeri_colonna),
            "numeri_colonna normalizzato deve coincidere con get_numeri_colonna() (come tupla)."
        )
        self.assertEqual(
            stato_colonna_normalizzato["numeri_segnati_colonna"],
            tuple(int(n) for n in numeri_segnati_colonna),
            "numeri_segnati_colonna normalizzato deve coincidere con get_numeri_segnati_colonna() (come tupla)."
        )

        # Assert: la tupla numeri_segnati_colonna_ordinati deve essere la versione ordinata dei segnati colonna
        self.assertEqual(
            numeri_segnati_colonna_ordinati,
            tuple(sorted(stato_colonna_normalizzato["numeri_segnati_colonna"])),
            "numeri_segnati_colonna_ordinati deve essere l'ordinamento di numeri_segnati_colonna."
        )

    def test_get_dati_visualizzazione_colonna_avanzata_percentuale_colonna_con_numeri_nessun_segnato(self):
        """Colonna con numeri ma senza segnati: percentuale deve essere 0.0."""

        # Arrange: troviamo una colonna che abbia almeno un numero
        colonna_con_numeri = None
        for c in range(self.cartella_default.colonne):
            if len(self.cartella_default.get_numeri_colonna(c)) > 0:
                colonna_con_numeri = c
                break

        self.assertIsNotNone(
            colonna_con_numeri,
            "Setup test: serve almeno una colonna con numeri (in una cartella valida dovrebbe esistere)."
        )

        # Act
        _, stato_colonna_normalizzato, _ = self.cartella_default.get_dati_visualizzazione_colonna_avanzata(colonna_con_numeri)

        # Assert
        self.assertEqual(
            stato_colonna_normalizzato["numeri_segnati"],
            0,
            "All'inizio, numeri_segnati nella colonna deve essere 0."
        )
        self.assertEqual(
            stato_colonna_normalizzato["percentuale_completamento"],
            0.0,
            "Con nessun numero segnato, percentuale_completamento deve essere 0.0."
        )

    def test_get_dati_visualizzazione_colonna_avanzata_percentuale_colonna_con_numeri_parziale(self):
        """Colonna con numeri e segnati parziali: percentuale deve essere round(segnati/totali*100, 1)."""

        # Arrange: troviamo una colonna con almeno 2 numeri (così possiamo segnare 1 e restare parziali)
        colonna_con_almeno_due_numeri = None
        for c in range(self.cartella_default.colonne):
            if len(self.cartella_default.get_numeri_colonna(c)) >= 2:
                colonna_con_almeno_due_numeri = c
                break

        self.assertIsNotNone(
            colonna_con_almeno_due_numeri,
            "Setup test: serve una colonna con almeno 2 numeri per un caso parziale."
        )

        numeri_colonna = self.cartella_default.get_numeri_colonna(colonna_con_almeno_due_numeri)

        # Segniamo solo 1 numero della colonna, lasciandone almeno 1 non segnato
        numero_da_segnare = numeri_colonna[0]
        esito = self.cartella_default.segna_numero(numero_da_segnare)
        self.assertTrue(esito, f"Setup non riuscito: impossibile segnare il numero {numero_da_segnare}.")

        # Act
        _, stato_colonna_normalizzato, numeri_segnati_colonna_ordinati = self.cartella_default.get_dati_visualizzazione_colonna_avanzata(colonna_con_almeno_due_numeri)

        # Assert: conteggi e segnati
        self.assertEqual(
            stato_colonna_normalizzato["numeri_totali"],
            len(numeri_colonna),
            "numeri_totali deve coincidere con la quantità di numeri nella colonna."
        )
        self.assertEqual(
            stato_colonna_normalizzato["numeri_segnati"],
            1,
            "Dopo aver segnato un numero della colonna, numeri_segnati deve essere 1."
        )
        self.assertEqual(
            numeri_segnati_colonna_ordinati,
            (numero_da_segnare,),
            "numeri_segnati_colonna_ordinati deve contenere esattamente il numero segnato."
        )

        # Assert: percentuale calcolata come da metodo
        percentuale_attesa = round((1 / len(numeri_colonna)) * 100, 1)
        self.assertEqual(
            stato_colonna_normalizzato["percentuale_completamento"],
            percentuale_attesa,
            "percentuale_completamento non è coerente con il rapporto segnati/totali."
        )

    def test_get_dati_visualizzazione_colonna_avanzata_percentuale_colonna_con_numeri_tutti_segnati(self):
        """Colonna con numeri tutti segnati: percentuale deve essere 100.0 e segnati==totali."""

        # Arrange: troviamo una colonna che abbia almeno 1 numero
        colonna_con_numeri = None
        for c in range(self.cartella_default.colonne):
            if len(self.cartella_default.get_numeri_colonna(c)) > 0:
                colonna_con_numeri = c
                break

        self.assertIsNotNone(
            colonna_con_numeri,
            "Setup test: serve una colonna con numeri per poterla segnare completamente."
        )

        numeri_colonna = self.cartella_default.get_numeri_colonna(colonna_con_numeri)

        # Segniamo TUTTI i numeri della colonna
        for numero in numeri_colonna:
            esito = self.cartella_default.segna_numero(numero)
            self.assertTrue(esito, f"Setup non riuscito: impossibile segnare il numero {numero}.")

        # Act
        _, stato_colonna_normalizzato, numeri_segnati_colonna_ordinati = self.cartella_default.get_dati_visualizzazione_colonna_avanzata(colonna_con_numeri)

        # Assert: conteggi e percentuale finale
        self.assertEqual(
            stato_colonna_normalizzato["numeri_totali"],
            len(numeri_colonna),
            "numeri_totali deve coincidere con i numeri effettivi della colonna."
        )
        self.assertEqual(
            stato_colonna_normalizzato["numeri_segnati"],
            len(numeri_colonna),
            "Con colonna completa, numeri_segnati deve essere uguale a numeri_totali."
        )
        self.assertEqual(
            stato_colonna_normalizzato["percentuale_completamento"],
            100.0,
            "Con colonna completa, percentuale_completamento deve essere 100.0."
        )

        # Assert: segnati == tutti i numeri colonna
        self.assertEqual(
            numeri_segnati_colonna_ordinati,
            tuple(sorted(numeri_colonna)),
            "Con colonna completa, numeri_segnati_colonna_ordinati deve coincidere con i numeri della colonna ordinati."
        )

    def test_get_dati_visualizzazione_colonna_avanzata_caso_limite_colonna_senza_numeri(self):
        """Se una colonna è vuota (0 numeri), numeri_totali=0 e percentuale=0.0."""

        # Arrange: cerchiamo una colonna vuota (possibile in una cartella 15 numeri su 9 colonne)
        colonna_vuota = None
        for c in range(self.cartella_default.colonne):
            if len(self.cartella_default.get_numeri_colonna(c)) == 0:
                colonna_vuota = c
                break

        # Se non troviamo una colonna vuota, saltiamo: dipende dalla generazione casuale della cartella.
        if colonna_vuota is None:
            self.skipTest("Nessuna colonna vuota trovata in questa cartella: caso limite non riproducibile qui.")

        # Act
        _, stato_colonna_normalizzato, numeri_segnati_colonna_ordinati = self.cartella_default.get_dati_visualizzazione_colonna_avanzata(colonna_vuota)

        # Assert: conteggi e percentuale nel caso limite
        self.assertEqual(
            stato_colonna_normalizzato["numeri_totali"],
            0,
            "In una colonna vuota, numeri_totali deve essere 0."
        )
        self.assertEqual(
            stato_colonna_normalizzato["numeri_segnati"],
            0,
            "In una colonna vuota, numeri_segnati deve essere 0."
        )
        self.assertEqual(
            stato_colonna_normalizzato["percentuale_completamento"],
            0.0,
            "In una colonna vuota, percentuale_completamento deve essere 0.0."
        )
        self.assertEqual(
            stato_colonna_normalizzato["numeri_colonna"],
            tuple(),
            "In una colonna vuota, numeri_colonna deve essere una tupla vuota."
        )
        self.assertEqual(
            stato_colonna_normalizzato["numeri_segnati_colonna"],
            tuple(),
            "In una colonna vuota, numeri_segnati_colonna deve essere una tupla vuota."
        )
        self.assertEqual(
            numeri_segnati_colonna_ordinati,
            tuple(),
            "In una colonna vuota, numeri_segnati_colonna_ordinati deve essere una tupla vuota."
        )

    def test_get_dati_visualizzazione_colonna_avanzata_immutabilita_contenitori(self):
        """Le tuple esposte (colonna e liste normalizzate) non devono essere modificabili."""

        # Arrange
        numero_colonna = 0

        # Act
        colonna_semplice, stato_colonna_normalizzato, numeri_segnati_colonna_ordinati = self.cartella_default.get_dati_visualizzazione_colonna_avanzata(numero_colonna)

        # Assert: colonna semplice immutabile (tupla)
        with self.assertRaises(TypeError):
            colonna_semplice[0] = colonna_semplice[0]

        # Assert: numeri_segnati_colonna_ordinati è tupla (non assegnabile)
        with self.assertRaises(TypeError):
            numeri_segnati_colonna_ordinati[0] = 999

        # Assert: tuple nello stato non hanno append (quindi non modificabili come liste)
        numeri_colonna_tuple = stato_colonna_normalizzato["numeri_colonna"]
        numeri_segnati_colonna_tuple = stato_colonna_normalizzato["numeri_segnati_colonna"]

        self.assertIsInstance(numeri_colonna_tuple, tuple, "numeri_colonna deve essere una tupla.")
        self.assertIsInstance(numeri_segnati_colonna_tuple, tuple, "numeri_segnati_colonna deve essere una tupla.")

        with self.assertRaises(AttributeError):
            numeri_colonna_tuple.append(1)

        with self.assertRaises(AttributeError):
            numeri_segnati_colonna_tuple.append(1)


    #test per il metodo 


    def test_get_coordinate_numero_errore_tipo_numero(self):
        """Solleva CartellaNumeroTypeException se numero non è un int."""

        # Arrange: input volutamente di tipo errato
        valori_non_int = ["5", 1.0, None, [], (5,), {"numero": 5}]

        # Act + Assert
        for valore in valori_non_int:
            with self.assertRaises(CartellaNumeroTypeException):
                self.cartella_default.get_coordinate_numero(valore)

    def test_get_coordinate_numero_errore_valore_fuori_range(self):
        """Solleva CartellaNumeroValueException se numero è fuori dal range valido 1..90."""

        # Arrange: valori fuori range (assumiamo max_numero=90)
        valori_fuori_range = [0, -1, self.cartella_default.max_numero + 1, 999]

        # Act + Assert
        for valore in valori_fuori_range:
            with self.assertRaises(CartellaNumeroValueException):
                self.cartella_default.get_coordinate_numero(valore)

    def test_get_coordinate_numero_numero_non_presente_ritorna_none(self):
        """Se il numero non appartiene alla cartella, ritorna None (senza scansionare inutilmente)."""

        # Arrange: scegliamo un numero valido 1..90 che NON sia nella cartella
        numero_assente = None
        for n in range(1, self.cartella_default.max_numero + 1):
            if n not in self.cartella_default.numeri_cartella:
                numero_assente = n
                break

        self.assertIsNotNone(
            numero_assente,
            "Setup test fallito: non è stato trovato alcun numero assente (caso improbabile, cartella invalida)."
        )

        # Act
        coordinate = self.cartella_default.get_coordinate_numero(numero_assente)

        # Assert
        self.assertIsNone(
            coordinate,
            "Per un numero non presente nella cartella, get_coordinate_numero deve ritornare None."
        )

    def test_get_coordinate_numero_numero_presente_ritorna_coordinate_corrette(self):
        """Se il numero è presente, ritorna (riga, colonna) 0-based coerenti con la matrice interna."""

        # Arrange: prendiamo un numero sicuramente presente
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        self.assertTrue(
            len(numeri_cartella) > 0,
            "Setup test fallito: get_numeri_cartella dovrebbe restituire almeno un numero."
        )

        numero_presente = numeri_cartella[0]

        # Act
        coordinate = self.cartella_default.get_coordinate_numero(numero_presente)

        # Assert: deve essere una tupla (riga, colonna)
        self.assertIsNotNone(
            coordinate,
            "Per un numero presente nella cartella, get_coordinate_numero non deve ritornare None."
        )
        self.assertIsInstance(coordinate, tuple, "Le coordinate devono essere una tupla.")
        self.assertEqual(len(coordinate), 2, "Le coordinate devono contenere esattamente 2 elementi (riga, colonna).")

        indice_riga, indice_colonna = coordinate

        # Assert: indici validi
        self.assertIsInstance(indice_riga, int, "indice_riga deve essere un int.")
        self.assertIsInstance(indice_colonna, int, "indice_colonna deve essere un int.")
        self.assertGreaterEqual(indice_riga, 0, "indice_riga deve essere >= 0.")
        self.assertLess(indice_riga, self.cartella_default.righe, "indice_riga deve essere < self.righe.")
        self.assertGreaterEqual(indice_colonna, 0, "indice_colonna deve essere >= 0.")
        self.assertLess(indice_colonna, self.cartella_default.colonne, "indice_colonna deve essere < self.colonne.")

        # Assert: la matrice in quelle coordinate deve contenere proprio quel numero
        self.assertEqual(
            self.cartella_default.cartella[indice_riga][indice_colonna],
            numero_presente,
            "Le coordinate ritornate devono puntare al numero richiesto nella matrice interna."
        )

    def test_get_coordinate_numero_non_modifica_lo_stato_cartella(self):
        """get_coordinate_numero non deve modificare matrice, numeri_cartella o numeri segnati."""

        # Arrange: snapshot dello stato prima
        matrice_prima = [riga.copy() for riga in self.cartella_default.cartella]
        numeri_cartella_prima = set(self.cartella_default.numeri_cartella)
        numeri_segnati_prima = set(self.cartella_default.numeri_segnati)

        # Scegliamo un numero presente e un numero assente (se possibile) per coprire entrambi i rami
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        self.assertTrue(
            len(numeri_cartella) > 0,
            "Setup test fallito: get_numeri_cartella dovrebbe restituire almeno un numero."
        )
        numero_presente = numeri_cartella[0]

        numero_assente = None
        for n in range(1, self.cartella_default.max_numero + 1):
            if n not in self.cartella_default.numeri_cartella:
                numero_assente = n
                break

        # Act: chiamate che non devono cambiare lo stato
        _ = self.cartella_default.get_coordinate_numero(numero_presente)
        if numero_assente is not None:
            _ = self.cartella_default.get_coordinate_numero(numero_assente)

        # Assert: stato invariato
        self.assertEqual(
            self.cartella_default.cartella,
            matrice_prima,
            "La matrice interna non deve cambiare dopo get_coordinate_numero."
        )
        self.assertEqual(
            set(self.cartella_default.numeri_cartella),
            numeri_cartella_prima,
            "numeri_cartella non deve cambiare dopo get_coordinate_numero."
        )
        self.assertEqual(
            set(self.cartella_default.numeri_segnati),
            numeri_segnati_prima,
            "numeri_segnati non deve cambiare dopo get_coordinate_numero."
        )

    def test_get_coordinate_numero_incoerenza_set_matrice_ritorna_none(self):
        """Se un numero è nel set numeri_cartella ma non è in matrice, il metodo deve ritornare None (caso sicurezza)."""

        # Arrange: prendiamo un numero sicuramente presente
        numeri_cartella = self.cartella_default.get_numeri_cartella()
        self.assertTrue(
            len(numeri_cartella) > 0,
            "Setup test fallito: get_numeri_cartella dovrebbe restituire almeno un numero."
        )

        numero_presente = numeri_cartella[0]

        # Troviamo le coordinate reali in stato coerente
        coordinate = self.cartella_default.get_coordinate_numero(numero_presente)
        self.assertIsNotNone(
            coordinate,
            "Setup test fallito: un numero presente deve avere coordinate prima di introdurre incoerenza."
        )

        indice_riga, indice_colonna = coordinate

        # Verifica di sicurezza: la cella deve contenere il numero
        self.assertEqual(
            self.cartella_default.cartella[indice_riga][indice_colonna],
            numero_presente,
            "Setup test fallito: la cella selezionata deve contenere il numero prima della modifica."
        )

        # Introduciamo incoerenza: togliamo il numero dalla matrice ma lo lasciamo nel set numeri_cartella
        self.cartella_default.cartella[indice_riga][indice_colonna] = None

        # Act
        coordinate_dopo = self.cartella_default.get_coordinate_numero(numero_presente)

        # Assert: deve ritornare None (non deve crashare)
        self.assertIsNone(
            coordinate_dopo,
            "In caso di incoerenza (numero nel set ma non in matrice), get_coordinate_numero deve ritornare None."
        )


    #test per il metodo get_numeri_riga

    def test_get_numeri_riga_errore_tipo_numero_riga(self):
        """Solleva CartellaRigaTypeException se numero_riga non è un int."""

        # Arrange: input volutamente di tipo errato
        valori_non_int = ["0", 1.0, None, [], (0,), {"riga": 0}]

        # Act + Assert
        for valore in valori_non_int:
            with self.assertRaises(CartellaRigaTypeException):
                self.cartella_default.get_numeri_riga(valore)

    def test_get_numeri_riga_errore_valore_fuori_range(self):
        """Solleva CartellaRigaValueException se numero_riga è fuori dal range valido 0..2."""

        # Arrange: indici riga non validi
        valori_fuori_range = [-1, 3, 10, 999]

        # Act + Assert
        for valore in valori_fuori_range:
            with self.assertRaises(CartellaRigaValueException):
                self.cartella_default.get_numeri_riga(valore)

    def test_get_numeri_riga_ritorna_lista_ordinata_con_soli_int_per_ogni_riga_valida(self):
        """Per ogni riga valida (0..2) ritorna una lista ordinata di soli int (nessun None)."""

        # Act + Assert: testiamo tutte le righe valide
        for numero_riga in range(self.cartella_default.righe):
            numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)

            # Assert: deve essere una lista
            self.assertIsInstance(numeri_riga, list, "get_numeri_riga deve ritornare una lista.")

            # Assert: in una cartella valida, ogni riga deve contenere 5 numeri
            self.assertEqual(
                len(numeri_riga),
                5,
                f"Nella riga {numero_riga}, la lista deve contenere esattamente 5 numeri."
            )

            # Assert: deve essere ordinata in modo crescente
            self.assertEqual(
                numeri_riga,
                sorted(numeri_riga),
                f"La lista restituita da get_numeri_riga({numero_riga}) deve essere ordinata."
            )

            # Assert: tutti gli elementi devono essere int
            for numero in numeri_riga:
                self.assertIsInstance(
                    numero,
                    int,
                    f"Nella riga {numero_riga} è stato trovato un elemento non intero: {numero!r}."
                )

    def test_get_numeri_riga_coerente_con_matrice_interna(self):
        """La lista deve coincidere con i valori non-None presenti nella riga della matrice (in forma ordinata)."""

        # Act + Assert: per ogni riga valida
        for numero_riga in range(self.cartella_default.righe):
            numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)

            # Calcoliamo l'atteso leggendo direttamente la riga nella matrice interna
            riga_matrice = self.cartella_default.cartella[numero_riga]
            numeri_attesi = [valore for valore in riga_matrice if valore is not None]

            self.assertEqual(
                numeri_riga,
                sorted(numeri_attesi),
                f"I numeri della riga {numero_riga} non corrispondono ai valori non-None presenti nella matrice."
            )

    def test_get_numeri_riga_non_modifica_lo_stato_cartella(self):
        """get_numeri_riga non deve modificare la matrice interna della cartella."""

        # Arrange: snapshot della matrice prima
        matrice_prima = [riga.copy() for riga in self.cartella_default.cartella]

        # Act: chiamiamo il metodo su tutte le righe
        for numero_riga in range(self.cartella_default.righe):
            _ = self.cartella_default.get_numeri_riga(numero_riga)

        # Assert: la matrice deve essere identica
        self.assertEqual(
            self.cartella_default.cartella,
            matrice_prima,
            "La matrice interna non deve cambiare dopo get_numeri_riga."
        )

    def test_get_numeri_riga_filtra_none_se_riga_incoerente(self):
        """Se una riga contiene None (caso limite), get_numeri_riga deve filtrarlo e mantenere l'ordinamento."""

        # Arrange: scegliamo una riga valida e forziamo un None (caso limite, white-box)
        numero_riga = 0

        # Cerchiamo una colonna dove c'è un numero, per poterlo sostituire con None
        indice_colonna_modificata = None
        valore_originale = None
        for indice_colonna in range(self.cartella_default.colonne):
            valore = self.cartella_default.cartella[numero_riga][indice_colonna]
            if valore is not None:
                indice_colonna_modificata = indice_colonna
                valore_originale = valore
                break

        self.assertIsNotNone(
            indice_colonna_modificata,
            "Setup test fallito: non è stata trovata alcuna cella numerica da convertire in None."
        )

        # Forziamo l'incoerenza: un None dentro la riga
        self.cartella_default.cartella[numero_riga][indice_colonna_modificata] = None

        # Act
        numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)

        # Assert: il valore rimosso non deve più comparire
        self.assertNotIn(
            valore_originale,
            numeri_riga,
            "Dopo aver impostato una cella a None, il numero originale non deve comparire nell'output."
        )

        # Assert: la lista deve rimanere ordinata
        self.assertEqual(
            numeri_riga,
            sorted(numeri_riga),
            "Anche nel caso limite con None, la lista deve rimanere ordinata."
        )

        # Assert: nessun None deve essere presente
        self.assertNotIn(
            None,
            numeri_riga,
            "L'output di get_numeri_riga non deve mai contenere None."
        )


    #test per metodo get_numeri_colonna

    def test_get_numeri_colonna_errore_tipo_numero_colonna(self):
        """Solleva CartellaColonnaTypeException se numero_colonna non è un int."""

        # Arrange: input volutamente di tipo errato
        valori_non_int = ["0", 1.0, None, [], (0,), {"colonna": 0}]

        # Act + Assert
        for valore in valori_non_int:
            with self.assertRaises(CartellaColonnaTypeException):
                self.cartella_default.get_numeri_colonna(valore)

    def test_get_numeri_colonna_errore_valore_fuori_range(self):
        """Solleva CartellaColonnaValueException se numero_colonna è fuori dal range valido 0..8."""

        # Arrange: indici colonna non validi
        valori_fuori_range = [-1, 9, 10, 999]

        # Act + Assert
        for valore in valori_fuori_range:
            with self.assertRaises(CartellaColonnaValueException):
                self.cartella_default.get_numeri_colonna(valore)

    def test_get_numeri_colonna_ritorna_lista_ordinata_con_soli_int_per_ogni_colonna_valida(self):
        """Per ogni colonna valida (0..8) ritorna una lista ordinata di soli int (nessun None)."""

        # Act + Assert: testiamo tutte le colonne valide
        for numero_colonna in range(self.cartella_default.colonne):
            numeri_colonna = self.cartella_default.get_numeri_colonna(numero_colonna)

            # Assert: deve essere una lista
            self.assertIsInstance(numeri_colonna, list, "get_numeri_colonna deve ritornare una lista.")

            # Assert: in una cartella valida, una colonna può avere da 0 a 3 numeri
            self.assertGreaterEqual(
                len(numeri_colonna),
                0,
                f"Nella colonna {numero_colonna}, la lista deve avere lunghezza >= 0."
            )
            self.assertLessEqual(
                len(numeri_colonna),
                3,
                f"Nella colonna {numero_colonna}, la lista non può avere più di 3 numeri."
            )

            # Assert: deve essere ordinata in modo crescente
            self.assertEqual(
                numeri_colonna,
                sorted(numeri_colonna),
                f"La lista restituita da get_numeri_colonna({numero_colonna}) deve essere ordinata."
            )

            # Assert: tutti gli elementi devono essere int
            for numero in numeri_colonna:
                self.assertIsInstance(
                    numero,
                    int,
                    f"Nella colonna {numero_colonna} è stato trovato un elemento non intero: {numero!r}."
                )

    def test_get_numeri_colonna_coerente_con_matrice_interna(self):
        """La lista deve coincidere con i valori non-None presenti nella colonna della matrice (in forma ordinata)."""

        # Act + Assert: per ogni colonna valida
        for numero_colonna in range(self.cartella_default.colonne):
            numeri_colonna = self.cartella_default.get_numeri_colonna(numero_colonna)

            # Calcoliamo l'atteso leggendo direttamente la colonna nella matrice interna
            numeri_attesi = []
            for indice_riga in range(self.cartella_default.righe):
                valore = self.cartella_default.cartella[indice_riga][numero_colonna]
                if valore is not None:
                    numeri_attesi.append(valore)

            self.assertEqual(
                numeri_colonna,
                sorted(numeri_attesi),
                f"I numeri della colonna {numero_colonna} non corrispondono ai valori non-None presenti nella matrice."
            )

    def test_get_numeri_colonna_non_modifica_lo_stato_cartella(self):
        """get_numeri_colonna non deve modificare la matrice interna della cartella."""

        # Arrange: snapshot della matrice prima
        matrice_prima = [riga.copy() for riga in self.cartella_default.cartella]

        # Act: chiamiamo il metodo su tutte le colonne
        for numero_colonna in range(self.cartella_default.colonne):
            _ = self.cartella_default.get_numeri_colonna(numero_colonna)

        # Assert: la matrice deve essere identica
        self.assertEqual(
            self.cartella_default.cartella,
            matrice_prima,
            "La matrice interna non deve cambiare dopo get_numeri_colonna."
        )

    def test_get_numeri_colonna_filtra_none_se_colonna_incoerente(self):
        """Se una colonna contiene None (caso normale), il metodo deve ignorarlo e non includerlo nell'output."""

        # Arrange: scegliamo una colonna che abbia almeno un numero e almeno un None
        # (in una cartella classica è un caso molto comune: una colonna può avere 1 o 2 numeri su 3 righe)
        numero_colonna = None
        for c in range(self.cartella_default.colonne):
            valori_colonna = [self.cartella_default.cartella[r][c] for r in range(self.cartella_default.righe)]
            if any(v is not None for v in valori_colonna) and any(v is None for v in valori_colonna):
                numero_colonna = c
                break

        if numero_colonna is None:
            self.skipTest(
                "Nessuna colonna trovata con mix None/numero (caso raro con questa generazione): test non applicabile."
            )

        # Act
        numeri_colonna = self.cartella_default.get_numeri_colonna(numero_colonna)

        # Assert: nessun None deve essere presente
        self.assertNotIn(
            None,
            numeri_colonna,
            "L'output di get_numeri_colonna non deve mai contenere None."
        )

        # Assert: deve essere ordinata in modo crescente
        self.assertEqual(
            numeri_colonna,
            sorted(numeri_colonna),
            "La lista deve essere ordinata anche quando la colonna contiene None nella matrice."
        )

    def test_get_numeri_colonna_caso_limite_colonna_svuotata_white_box(self):
        """Caso limite: se svuotiamo una colonna (tutte None), get_numeri_colonna deve ritornare lista vuota."""

        # Arrange: scegliamo una colonna che abbia almeno un numero, poi la svuotiamo
        numero_colonna = None
        for c in range(self.cartella_default.colonne):
            if len(self.cartella_default.get_numeri_colonna(c)) > 0:
                numero_colonna = c
                break

        self.assertIsNotNone(
            numero_colonna,
            "Setup test fallito: non è stata trovata alcuna colonna con numeri (cartella invalida)."
        )

        # Svuotiamo la colonna rendendo None tutte le celle (white-box)
        for indice_riga in range(self.cartella_default.righe):
            self.cartella_default.cartella[indice_riga][numero_colonna] = None

        # Act
        numeri_colonna = self.cartella_default.get_numeri_colonna(numero_colonna)

        # Assert
        self.assertEqual(
            numeri_colonna,
            [],
            "Dopo aver svuotato una colonna, get_numeri_colonna deve ritornare una lista vuota."
        )


    """test sui metodi della sezione 6 della doc string iniziale."""

    #test del metodo verifica_ambo_riga()
    def test_verifica_ambo_riga(self):
        """
        Verifica che verifica_ambo_riga() rilevi correttamente
        la presenza di almeno 2 numeri segnati (ambo) in una riga.

        Per ogni riga valida (0, 1, 2) il test controlla tre scenari:
        1) Nessun numero segnato sulla riga -> deve ritornare False.
        2) Un solo numero segnato sulla riga -> deve ritornare False.
        3) Almeno due numeri segnati sulla riga -> deve ritornare True.
        """

        # Per ogni riga della cartella: 0, 1 e 2
        for numero_riga in range(3):
            # Reset completo prima di testare la riga
            self.cartella_default.reset_cartella()

            # Prende tutti i numeri di quella riga
            numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)

            # Se per qualche motivo la riga non avesse numeri (caso teorico), salta
            if len(numeri_riga) == 0:
                continue

            # SCENARIO 1: Nessun numero segnato -> False
            risultato = self.cartella_default.verifica_ambo_riga(numero_riga)
            self.assertFalse(
                risultato,
                f"Nella riga {numero_riga}, senza numeri segnati, verifica_ambo_riga() deve ritornare False."
            )

            # SCENARIO 2: Segna un solo numero della riga -> ancora False
            self.cartella_default.segna_numero(numeri_riga[0])

            risultato = self.cartella_default.verifica_ambo_riga(numero_riga)
            self.assertFalse(
                risultato,
                f"Nella riga {numero_riga}, con un solo numero segnato, verifica_ambo_riga() deve ritornare False."
            )

            # SCENARIO 3: Segna almeno due numeri della riga -> True
            if len(numeri_riga) > 1:
                self.cartella_default.segna_numero(numeri_riga[1])

            risultato = self.cartella_default.verifica_ambo_riga(numero_riga)
            self.assertTrue(
                risultato,
                f"Nella riga {numero_riga}, con almeno due numeri segnati, verifica_ambo_riga() deve ritornare True."
            )



    """test sulle eccezioni sollevate dal metodo verifica_ambo_riga()"""

    #test del metodo verifica_ambo_riga() - eccezione tipo numero_riga
    def test_verifica_ambo_riga_errore_tipo(self):
        """
        Verifica che verifica_ambo_riga() sollevi CartellaRigaTypeException
        quando il parametro 'numero_riga' non è un intero.
        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """
        # Caso 1: numero_riga è una stringa
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_ambo_riga("0")
        # Caso 2: numero_riga è un float
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_ambo_riga(1.5)
        # Caso 3: numero_riga è None
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_ambo_riga(None)
        # Caso 4: numero_riga è una lista
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_ambo_riga([2])


    #test del metodo verifica_ambo_riga() - eccezione valore numero_riga fuori range
    def test_verifica_ambo_riga_errore_valore_fuori_range(self):
        """
        Verifica che verifica_ambo_riga() sollevi CartellaRigaValueException
        quando il parametro 'numero_riga' è un intero ma fuori dal range valido 0, 1, 2.
        In questo test usiamo alcuni esempi di indici non validi
        (-1, 3, 5) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """
        # Caso 1: numero_riga negativo
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_ambo_riga(-1)
        # Caso 2: numero_riga troppo alto (uguale al numero di righe)
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_ambo_riga(3)
        # Caso 3: numero_riga molto oltre il limite
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_ambo_riga(5)



    #test del metodo verifica_terno_riga()
    def test_verifica_terno_riga(self):
        """
        Verifica che verifica_terno_riga() rilevi correttamente
        la presenza di almeno 3 numeri segnati (terno) in una riga.

        Per ogni riga valida (0, 1, 2) il test controlla tre scenari:
        1) Nessun numero segnato sulla riga -> deve ritornare False.
        2) Due numeri segnati sulla riga -> deve ritornare False.
        3) Almeno tre numeri segnati sulla riga -> deve ritornare True.
        """

        # Per ogni riga della cartella: 0, 1 e 2
        for numero_riga in range(3):
            # Reset completo prima di testare la riga
            self.cartella_default.reset_cartella()

            # Prende tutti i numeri di quella riga
            numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)

            # Se per qualche motivo la riga non avesse numeri, salta
            if len(numeri_riga) == 0:
                continue

            # SCENARIO 1: Nessun numero segnato -> False
            risultato = self.cartella_default.verifica_terno_riga(numero_riga)
            self.assertFalse(
                risultato,
                f"Nella riga {numero_riga}, senza numeri segnati, verifica_terno_riga() deve ritornare False."
            )

            # SCENARIO 2: Segna due numeri della riga -> ancora False
            self.cartella_default.segna_numero(numeri_riga[0])
            if len(numeri_riga) > 1:
                self.cartella_default.segna_numero(numeri_riga[1])

            risultato = self.cartella_default.verifica_terno_riga(numero_riga)
            self.assertFalse(
                risultato,
                f"Nella riga {numero_riga}, con due numeri segnati, verifica_terno_riga() deve ritornare False."
            )

            # SCENARIO 3: Segna almeno tre numeri della riga -> True
            if len(numeri_riga) > 2:
                self.cartella_default.segna_numero(numeri_riga[2])

            risultato = self.cartella_default.verifica_terno_riga(numero_riga)
            self.assertTrue(
                risultato,
                f"Nella riga {numero_riga}, con almeno tre numeri segnati, verifica_terno_riga() deve ritornare True."
            )


    """tests sulle eccezioni sollevate dal metodo verifica_terno_riga()"""

    #test del metodo verifica_terno_riga() - eccezione tipo numero_riga
    def test_verifica_terno_riga_errore_tipo(self):
        """
        Verifica che verifica_terno_riga() sollevi CartellaRigaTypeException
        quando il parametro 'numero_riga' non è un intero.
        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """
        # Caso 1: numero_riga è una stringa
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_terno_riga("2")
        # Caso 2: numero_riga è un float
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_terno_riga(0.5)
        # Caso 3: numero_riga è None
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_terno_riga(None)
        # Caso 4: numero_riga è una lista
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_terno_riga([1])


    #test del metodo verifica_terno_riga() - eccezione valore numero_riga fuori range
    def test_verifica_terno_riga_errore_valore_fuori_range(self):
        """
        Verifica che verifica_terno_riga() sollevi CartellaRigaValueException
        quando il parametro 'numero_riga' è un intero ma fuori dal range valido 0, 1, 2.
        In questo test usiamo alcuni esempi di indici non validi
        (-1, 3, 6) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """
        # Caso 1: numero_riga negativo
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_terno_riga(-1)
        # Caso 2: numero_riga troppo alto (uguale al numero di righe)
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_terno_riga(3)
        # Caso 3: numero_riga molto oltre il limite
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_terno_riga(6)




    #test del metodo verifica_quaterna_riga()
    def test_verifica_quaterna_riga(self):
        """
        Verifica che verifica_quaterna_riga() rilevi correttamente
        la presenza di almeno 4 numeri segnati (quaterna) in una riga.

        Per ogni riga valida (0, 1, 2) il test controlla tre scenari:
        1) Meno di 4 numeri segnati sulla riga -> deve ritornare False.
        2) Esattamente 4 numeri segnati sulla riga -> deve ritornare True.
        3) Tutti i numeri della riga segnati (5 su 5) -> deve comunque ritornare True.
        """

        # Per ogni riga della cartella: 0, 1 e 2
        for numero_riga in range(3):
            # Reset completo prima di testare la riga
            self.cartella_default.reset_cartella()

            # Prende tutti i numeri di quella riga
            numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)

            # Se per qualche motivo la riga non avesse numeri, salta
            if len(numeri_riga) == 0:
                continue

            # SCENARIO 1: Segna 0, 1, 2 o 3 numeri -> sempre False
            # Segniamo al massimo 3 numeri, se la riga li ha
            max_da_segnare = min(3, len(numeri_riga))
            for i in range(max_da_segnare):
                self.cartella_default.segna_numero(numeri_riga[i])

            risultato = self.cartella_default.verifica_quaterna_riga(numero_riga)
            self.assertFalse(
                risultato,
                f"Nella riga {numero_riga}, con meno di 4 numeri segnati, verifica_quaterna_riga() deve ritornare False."
            )

            # SCENARIO 2: Segna il quarto numero (se esiste) -> True
            if len(numeri_riga) > 3:
                self.cartella_default.segna_numero(numeri_riga[3])

                risultato = self.cartella_default.verifica_quaterna_riga(numero_riga)
                self.assertTrue(
                    risultato,
                    f"Nella riga {numero_riga}, con almeno 4 numeri segnati, verifica_quaterna_riga() deve ritornare True."
                )

            # SCENARIO 3: Segna tutti i numeri della riga -> ancora True
            for numero in numeri_riga:
                self.cartella_default.segna_numero(numero)

            risultato = self.cartella_default.verifica_quaterna_riga(numero_riga)
            self.assertTrue(
                risultato,
                f"Nella riga {numero_riga}, con tutti i 5 numeri segnati, verifica_quaterna_riga() deve continuare a ritornare True."
            )


    """tests sulle eccezioni sollevate dal metodo verifica_quaterna_riga()"""

    #test del metodo verifica_quaterna_riga() - eccezione tipo numero_riga
    def test_verifica_quaterna_riga_errore_tipo(self):
        """
        Verifica che verifica_quaterna_riga() sollevi CartellaRigaTypeException
        quando il parametro 'numero_riga' non è un intero.
        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """
        # Caso 1: numero_riga è una stringa
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_quaterna_riga("1")
        # Caso 2: numero_riga è un float
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_quaterna_riga(2.0)
        # Caso 3: numero_riga è None
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_quaterna_riga(None)
        # Caso 4: numero_riga è una lista
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_quaterna_riga([0])


    #test del metodo verifica_quaterna_riga() - eccezione valore numero_riga fuori range
    def test_verifica_quaterna_riga_errore_valore_fuori_range(self):
        """
        Verifica che verifica_quaterna_riga() sollevi CartellaRigaValueException
        quando il parametro 'numero_riga' è un intero ma fuori dal range valido 0, 1, 2.
        In questo test usiamo alcuni esempi di indici non validi
        (-1, 3, 4) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """
        # Caso 1: numero_riga negativo
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_quaterna_riga(-1)
        # Caso 2: numero_riga troppo alto (uguale al numero di righe)
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_quaterna_riga(3)
        # Caso 3: numero_riga molto oltre il limite
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_quaterna_riga(4)



    #test del metodo verifica_cinquina_riga() da elaborare come i precedenti metodi di test sulle vittorie
    def test_verifica_cinquina_riga(self):
        """
        Verifica che verifica_cinquina_riga() rilevi correttamente
        la presenza di tutti i 5 numeri segnati (cinquina) in una riga.

        Per ogni riga valida (0, 1, 2) il test controlla due scenari:
        1) Meno di 5 numeri segnati sulla riga -> deve ritornare False.
        2) Tutti i 5 numeri segnati sulla riga -> deve ritornare True.
        """

        # Per ogni riga della cartella: 0, 1 e 2
        for numero_riga in range(3):
            # Reset completo prima di testare la riga
            self.cartella_default.reset_cartella()

            # Prende tutti i numeri di quella riga
            numeri_riga = self.cartella_default.get_numeri_riga(numero_riga)

            # Se per qualche motivo la riga non avesse numeri, salta
            if len(numeri_riga) == 0:
                continue

            # SCENARIO 1: Segna meno di tutti i numeri -> False
            # Segniamo al massimo 4 numeri, se la riga li ha
            max_da_segnare = min(4, len(numeri_riga))
            for i in range(max_da_segnare):
                self.cartella_default.segna_numero(numeri_riga[i])

            risultato = self.cartella_default.verifica_cinquina_riga(numero_riga)
            self.assertFalse(
                risultato,
                f"Nella riga {numero_riga}, con meno di 5 numeri segnati, verifica_cinquina_riga() deve ritornare False."
            )

            # SCENARIO 2: Segna tutti i numeri della riga -> True
            for numero in numeri_riga:
                self.cartella_default.segna_numero(numero)

            risultato = self.cartella_default.verifica_cinquina_riga(numero_riga)
            self.assertTrue(
                risultato,
                f"Nella riga {numero_riga}, con tutti i 5 numeri segnati, verifica_cinquina_riga() deve ritornare True."
            )


    """tests sulle eccezioni sollevate dal metodo verifica_cinquina_riga()"""

    #test del metodo verifica_cinquina_riga() - eccezione tipo numero_riga
    def test_verifica_cinquina_riga_errore_tipo(self):
        """
        Verifica che verifica_cinquina_riga() sollevi CartellaRigaTypeException
        quando il parametro 'numero_riga' non è un intero.
        In questo test proviamo a chiamare il metodo con valori di tipo errato
        (stringa, float, None, lista) e ci aspettiamo che in tutti i casi
        venga sollevata la stessa eccezione di tipo.
        """
        # Caso 1: numero_riga è una stringa
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_cinquina_riga("2")
        # Caso 2: numero_riga è un float
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_cinquina_riga(0.0)
        # Caso 3: numero_riga è None
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_cinquina_riga(None)
        # Caso 4: numero_riga è una lista
        with self.assertRaises(CartellaRigaTypeException):
            self.cartella_default.verifica_cinquina_riga([1])


    #test del metodo verifica_cinquina_riga() - eccezione valore numero_riga fuori range
    def test_verifica_cinquina_riga_errore_valore_fuori_range(self):
        """
        Verifica che verifica_cinquina_riga() sollevi CartellaRigaValueException
        quando il parametro 'numero_riga' è un intero ma fuori dal range valido 0, 1, 2.
        In questo test usiamo alcuni esempi di indici non validi
        (-1, 3, 7) e ci aspettiamo che in tutti i casi venga sollevata
        l'eccezione di valore.
        """
        # Caso 1: numero_riga negativo
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_cinquina_riga(-1)
        # Caso 2: numero_riga troppo alto (uguale al numero di righe)
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_cinquina_riga(3)
        # Caso 3: numero_riga molto oltre il limite
        with self.assertRaises(CartellaRigaValueException):
            self.cartella_default.verifica_cinquina_riga(7)



    #test del metodo verifica_cartella_completa()
    def test_verifica_cartella_completa(self):
        """
        Verifica che verifica_cartella_completa() rilevi correttamente
        la TOMBOLA, cioè quando tutti i 15 numeri della cartella sono segnati.

        Il test controlla tre scenari:
        1) Nessun numero segnato -> deve ritornare False.
        2) Alcuni numeri segnati ma non tutti -> deve ritornare False.
        3) Tutti i 15 numeri segnati -> deve ritornare True.
        """

        # Recupera tutti i numeri della cartella (sempre 15)
        numeri_cartella = self.cartella_default.get_numeri_cartella()

        # SCENARIO 1: Cartella appena creata, nessun numero segnato
        self.assertFalse(
            self.cartella_default.verifica_cartella_completa(),
            "Con nessun numero segnato, verifica_cartella_completa() deve ritornare False."
        )

        # SCENARIO 2: Segna alcuni numeri (ma non tutti), ad esempio i primi 5
        for numero in numeri_cartella[:5]:
            self.cartella_default.segna_numero(numero)

        self.assertFalse(
            self.cartella_default.verifica_cartella_completa(),
            "Con solo alcuni numeri segnati, verifica_cartella_completa() deve ritornare False."
        )

        # SCENARIO 3: Segna TUTTI i numeri della cartella (TOMBOLA!)
        for numero in numeri_cartella:
            self.cartella_default.segna_numero(numero)

        self.assertTrue(
            self.cartella_default.verifica_cartella_completa(),
            "Quando tutti i 15 numeri sono segnati, verifica_cartella_completa() deve ritornare True."
        )


