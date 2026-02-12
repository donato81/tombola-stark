#import delle librerie necessarie
#importazione della libreria random per l'estrazione casuale dei numeri 
import random



#definizione della classe Tabellone
class Tabellone:

    #costruttore della classe Tabellone
    def __init__(self):
        # Inizializza il tabellone
        self._inizializza_tabellone()





    """metodi della classe tabellone"""

    """sezione: metodi di creazione del tabellone"""

    #metodo per inizializzare il tabellone
    def _inizializza_tabellone(self):
        # Inizializza il set dei numeri disponibili da 1 a 90
        self.numeri_disponibili = set(range(1, 91))
        # Inizializza il set dei numeri estratti
        self.numeri_estratti = set()
        # Contenitore: ultimo numero estratto (None se nessuna estrazione)
        self.ultimo_numero_estratto = None
        # Storico delle estrazioni in ordine temporale (serve per "ultimi N estratti")
        self.storico_estrazioni = []


    #metodo per estrarre un numero casuale
    def estrai_numero(self):
        # Verifica se ci sono numeri disponibili da estrarre
        if self.numeri_terminati():
            self.gestione_errore_numeri_terminati()
        # Crea una lista dei numeri disponibili per l'estrazione
        lista_disponibili = list(self.numeri_disponibili)
        # Estrae un numero casuale dalla lista dei numeri disponibili
        numero_estratto = random.choice(lista_disponibili)
        # Rimuove il numero estratto dai numeri disponibili e lo aggiunge ai numeri estratti
        self.numeri_disponibili.remove(numero_estratto)
        #aggiunge il numero estratto al set dei numeri estratti
        self.numeri_estratti.add(numero_estratto)
        # Aggiorna il contenitore dell'ultimo numero estratto
        self.ultimo_numero_estratto = numero_estratto
        # Salva la cronologia (ordine reale di estrazione)
        self.storico_estrazioni.append(numero_estratto)
        # Ritorna il numero estratto
        return numero_estratto


    def is_numero_estratto(self, numero: int) -> bool:
        """
        Verifica se un numero è già stato estratto dal tabellone.

        Scopo:
        - Fornire un controllo semplice e riutilizzabile per sapere se un numero
          è già presente tra i numeri estratti.
        - Non produce stringhe e non modifica lo stato del tabellone.

        Nota:
        - La validazione del numero (tipo e range 1..90) deve essere effettuata
          prima di chiamare questo metodo, così qui si resta volutamente "puliti"
          e predicibili.

        Parametri:
        - numero (int): numero da verificare.

        Ritorna:
        - bool: True se il numero risulta tra i numeri estratti, False altrimenti.
        """

        # Controllo semplice: membership nel set dei numeri estratti.
        return numero in self.numeri_estratti


    #metodo per resettare il tabellone
    def reset_tabellone(self):
        # Reinizializza il tabellone
        self._inizializza_tabellone()



    """sezione: metodi di stato/controllo"""
    #metodo per verificare se i numeri del tabellone sono terminati
    def numeri_terminati(self):
        # Ritorna True se non ci sono più numeri disponibili da estrarre, altrimenti False
        return len(self.numeri_disponibili) == 0



    #metodo per la gestione del errore sui numeri terminati
    def gestione_errore_numeri_terminati(self):
        # Solleva un'eccezione se non ci sono più numeri disponibili
        raise ValueError("Tutti i numeri sono stati estratti. Impossibile estrarre un altro numero.")



    #metodo per ottenere il numero totale di numeri estratti
    def get_conteggio_estratti(self):
        """
        Ritorna il numero totale di numeri estratti dal tabellone fino a questo momento.

        Questo metodo permette di sapere quante estrazioni sono già state effettuate
        durante la partita, senza dover accedere direttamente alla struttura interna
        che contiene i numeri estratti.

        Ritorna:
        - int: il numero di elementi presenti nel set self.numeri_estratti

        Esempi:
        - Subito dopo l'inizializzazione o il reset del tabellone:
          get_conteggio_estratti() ritorna 0, perché non è stato ancora estratto
          nessun numero.

        - Dopo 10 chiamate a estrai_numero():
          get_conteggio_estratti() ritorna 10.

        Note:
        - Il risultato è sempre compreso tra 0 e 90.
        - L'operazione è molto veloce, perché len() su un set è in tempo costante.
        """
        # Usa len() sul set dei numeri estratti per ottenere il conteggio attuale
        return len(self.numeri_estratti)


    #metodo per ottenere il numero totale di numeri ancora disponibili
    def get_conteggio_disponibili(self):
        """
        Ritorna il numero totale di numeri ancora disponibili da estrarre.

        Questo metodo permette di sapere quanti numeri non sono ancora stati
        estratti dal tabellone, senza accedere direttamente alla struttura
        interna che contiene i numeri disponibili.

        Ritorna:
        - int: il numero di elementi presenti nel set self.numeri_disponibili

        Esempi:
        - Subito dopo l'inizializzazione o il reset del tabellone:
          get_conteggio_disponibili() ritorna 90, perché tutti i numeri da 1 a 90
          sono ancora disponibili.

        - Dopo 10 chiamate a estrai_numero():
          get_conteggio_disponibili() ritorna 80.

        Note:
        - Il risultato è sempre compreso tra 0 e 90.
        - L'operazione è molto veloce, perché len() su un set è in tempo costante.
        """
        # Usa len() sul set dei numeri disponibili per ottenere il conteggio attuale
        return len(self.numeri_disponibili)



    #metodo per ritornare i numeri estratti
    def get_numeri_estratti(self):
        #ritorna una lista ordinata dei numeri estratti
        return sorted(self.numeri_estratti)




    #metodo per ritornare i numeri disponibili
    def get_numeri_disponibili(self):
        #ritorna una lista ordinata dei numeri disponibili
        return sorted(self.numeri_disponibili)



    #metodo per ottenere la percentuale di avanzamento del tabellone
    def get_percentuale_avanzamento(self):
        """
        Calcola e ritorna la percentuale di avanzamento del tabellone.

        La percentuale viene calcolata in base al numero di numeri estratti
        rispetto al totale dei numeri possibili (da 1 a 90).

        Formula:
        percentuale = (numeri_estratti / 90) * 100

        Ritorna:
        - float: percentuale di avanzamento del tabellone, compresa tra 0.0 e 100.0

        Esempi:
        - Subito dopo l'inizializzazione o il reset del tabellone:
          get_percentuale_avanzamento() ritorna 0.0.

        - Dopo 45 estrazioni:
          get_percentuale_avanzamento() ritorna 50.0.

        - Dopo 90 estrazioni (tutti i numeri estratti):
          get_percentuale_avanzamento() ritorna 100.0.
        """
        # Numero totale dei numeri possibili nel tabellone
        totale_numeri = 90

        # Conteggio dei numeri già estratti
        numeri_estratti = self.get_conteggio_estratti()

        # Calcola la percentuale di avanzamento
        percentuale = (numeri_estratti / totale_numeri) * 100

        # Ritorna il valore float arrotondato a una cifra decimale
        return round(percentuale, 1)


    def get_ultimo_numero_estratto(self):
        """
        Ritorna l'ultimo numero estratto dal tabellone.

        Scopo:
        - Fornire un accesso stabile al concetto di "ultimo estratto" (ordine temporale),
          che non è ricavabile dai set perché non mantengono l'ordine di inserimento.
        - Metodo di sola lettura: non modifica lo stato del tabellone e non produce testo.

        Ritorna:
        - int: l'ultimo numero estratto, se è stata effettuata almeno una estrazione.
        - None: se non è stata effettuata ancora nessuna estrazione (tabellone appena creato o resettato).
        """
        return self.ultimo_numero_estratto


    def get_ultimi_numeri_estratti(self, n: int = 5) -> tuple[int, ...]:
        """
        Ritorna una tupla con gli ultimi N numeri estratti, in ordine temporale.

        Scopo:
        - Fornire una cronologia recente delle estrazioni (es. ultimi 5 numeri),
          utile quando l’utente si distrae o rientra in partita.
        - Non modifica lo stato del tabellone.

        Parametri:
        - n (int): quanti numeri recenti ritornare. Deve essere un intero > 0.

        Ritorna:
        - tuple[int, ...]: una tupla (immutabile) contenente gli ultimi N numeri estratti.
          Se le estrazioni sono meno di N, ritorna tutti quelli disponibili.
          Se non è stato estratto ancora nulla, ritorna una tupla vuota.

        Eccezioni:
        - ValueError: se n non è un intero oppure se n <= 0.
        """
        # Validazione difensiva: n deve essere un intero positivo
        if not isinstance(n, int):
            raise ValueError("Il parametro 'n' deve essere un intero.")

        if n <= 0:
            raise ValueError("Il parametro 'n' deve essere maggiore di 0.")

        # Nessuna estrazione effettuata: ritorno vuoto, ma coerente (tupla immutabile)
        if not self.storico_estrazioni:
            return tuple()

        # Slicing: se n è più grande della cronologia, Python ritorna comunque tutto.
        ultimi = self.storico_estrazioni[-n:]

        # Ritorno tupla per sicurezza (immutabile lato chiamante/UI)
        return tuple(ultimi)


    #metodo per ottenere lo stato completo del tabellone
    def get_stato_tabellone(self):
        """
        Ritorna un dizionario con le informazioni globali sullo stato del tabellone.

        Il dizionario contiene:
        - totale_numeri: int, il numero totale dei numeri gestiti dal tabellone (sempre 90)
        - numeri_estratti: int, quanti numeri sono già stati estratti
        - numeri_disponibili: int, quanti numeri sono ancora disponibili da estrarre
        - ultimi_numeri_estratti(tuple(int)) ultimi 5 o n numeri estratti.
        - ultimo_numero_estratto(int) l'ultimo numero estratto.

        - percentuale_avanzamento: float, percentuale di avanzamento del tabellone (0.0–100.0),
          arrotondata a un solo decimale

        Questo metodo fornisce una “fotografia” completa del tabellone, utile
        per la logica di gioco, per la visualizzazione e per eventuali
        vocalizzazioni strutturate.
        """
        # Numero totale di numeri gestiti dal tabellone
        totale_numeri = 90

        # Conteggio dei numeri estratti e disponibili
        conteggio_estratti = self.get_conteggio_estratti()
        conteggio_disponibili = self.get_conteggio_disponibili()

        # ultimi 5 numeri estratti 
        ultimi = 5
        ultimi_numeri_estratti = self.get_ultimi_numeri_estratti(ultimi)

        #ultimo numero estratto 
        ultimo_numero_estratto = self.get_ultimo_numero_estratto()

        # Percentuale di avanzamento (già arrotondata a un decimale nel metodo dedicato)
        percentuale_avanzamento = self.get_percentuale_avanzamento()

        # Costruisce il dizionario con tutte le informazioni
        stato_tabellone = {
            "totale_numeri": totale_numeri,
            "numeri_estratti": conteggio_estratti,
            "numeri_disponibili": conteggio_disponibili,
            "ultimi_numeri_estratti": ultimi_numeri_estratti,
            "ultimo_numero_estratto": ultimo_numero_estratto,
            "percentuale_avanzamento": percentuale_avanzamento,
        }

        # Ritorna il dizionario completo
        return stato_tabellone



