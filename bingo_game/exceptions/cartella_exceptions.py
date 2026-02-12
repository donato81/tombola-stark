"""
Modulo per la gestione delle eccezioni personalizzate della classe Cartella.

Questo modulo contiene tutte le eccezioni specifiche che la classe Cartella può lanciare
durante l'esecuzione dei suoi metodi. Le eccezioni sono organizzate gerarchicamente:
una classe base (CartellaException) e sei eccezioni specifiche che ereditano da essa.

Struttura delle eccezioni:
- CartellaException (classe base, genitore di tutte le altre)
  ├── CartellaNumeroTypeException (il parametro numero non è un intero)
  ├── CartellaNumeroValueException (il valore di numero non è nel range 1-90)
  ├── CartellaRigaTypeException (il parametro numero_riga non è un intero)
  ├── CartellaRigaValueException (il valore di numero_riga non è 0, 1 o 2)
  ├── CartellaColonnaTypeException (il parametro numero_colonna non è un intero)
  └── CartellaColonnaValueException (il valore di numero_colonna non è 0-8)

Vantaggi di questa struttura:
- Gerarchia chiara: tutte le eccezioni della Cartella ereditano da CartellaException
- Cattura granulare: puoi catturare eccezioni specifiche oppure tutte insieme
- Messaggi chiari: ogni eccezione ha messaggi descrittivi per facilitare il debug
- Manutenibile: aggiungere nuove eccezioni è semplice grazie alla struttura base

Path: bingo_game/exceptions/cartella_exceptions.py
"""


# ============================================================================
# CLASSE BASE - Tutte le eccezioni della Cartella ereditano da questa
# ============================================================================

class CartellaException(Exception):
    """
    Eccezione base per tutti gli errori della classe Cartella.
    
    Questa è la classe genitore di tutte le eccezioni specifiche della Cartella.
    Usarla per catturare TUTTE le eccezioni della Cartella in una sola volta.
    
    Esempio:
        try:
            cartella.get_numeri_riga(5)
        except CartellaException:
            print("Errore generico nella Cartella")
    """
    pass


# ============================================================================
# ECCEZIONI PER IL PARAMETRO "numero" (1-90)
# ============================================================================

class CartellaNumeroTypeException(CartellaException):
    """
    Eccezione lanciata quando il parametro 'numero' non è un intero.
    
    Questa eccezione viene lanciata quando un metodo riceve un numero che non è
    di tipo int (es. string, float, None, list, ecc.).
    
    Attributi:
        numero_ricevuto: il valore effettivamente ricevuto
        tipo_ricevuto: il tipo effettivo del parametro
    
    Esempio:
        cartella.segna_numero("45")  # TypeError: numero deve essere int, ricevuto str
        cartella.is_numero_segnato(45.5)  # TypeError: numero deve essere int, ricevuto float
    """
    
    def __init__(self, numero_ricevuto):
        """
        Inizializza l'eccezione con il valore ricevuto.
        
        Args:
            numero_ricevuto: il valore che è stato passato ma non è un intero
        """
        self.numero_ricevuto = numero_ricevuto
        self.tipo_ricevuto = type(numero_ricevuto).__name__
        
        # Messaggio descrittivo che spiega il problema
        messaggio = (
            f"Il parametro 'numero' deve essere un intero (int), "
            f"ma hai fornito {self.tipo_ricevuto}. "
            f"Valore ricevuto: {numero_ricevuto}"
        )
        
        super().__init__(messaggio)


class CartellaNumeroValueException(CartellaException):
    """
    Eccezione lanciata quando il valore di 'numero' non è nel range 1-90.
    
    Questa eccezione viene lanciata quando un metodo riceve un numero che è sì
    un intero, ma non è compreso tra 1 e 90 (il range valido della tombola).
    
    Attributi:
        numero_ricevuto: il valore intero ricevuto ma fuori range
    
    Esempio:
        cartella.segna_numero(0)   # ValueError: numero 0 è fuori range 1-90
        cartella.segna_numero(91)  # ValueError: numero 91 è fuori range 1-90
        cartella.segna_numero(-5)  # ValueError: numero -5 è fuori range 1-90
    """
    
    def __init__(self, numero_ricevuto):
        """
        Inizializza l'eccezione con il numero fuori range ricevuto.
        
        Args:
            numero_ricevuto: il valore intero che è fuori dal range 1-90
        """
        self.numero_ricevuto = numero_ricevuto
        
        # Messaggio descrittivo che spiega il problema
        messaggio = (
            f"Il parametro 'numero' deve essere compreso tra 1 e 90, "
            f"ma hai fornito {numero_ricevuto}. "
            f"Range valido: 1-90"
        )
        
        super().__init__(messaggio)


# ============================================================================
# ECCEZIONI PER IL PARAMETRO "numero_riga" (0-2)
# ============================================================================

class CartellaRigaTypeException(CartellaException):
    """
    Eccezione lanciata quando il parametro 'numero_riga' non è un intero.
    
    Questa eccezione viene lanciata quando un metodo riceve un indice di riga
    che non è di tipo int (es. string, float, None, list, ecc.).
    
    Attributi:
        numero_riga_ricevuto: il valore effettivamente ricevuto
        tipo_ricevuto: il tipo effettivo del parametro
    
    Esempio:
        cartella.get_numeri_riga("0")  # TypeError: numero_riga deve essere int, ricevuto str
        cartella.get_stato_riga(0.5)   # TypeError: numero_riga deve essere int, ricevuto float
    """
    
    def __init__(self, numero_riga_ricevuto):
        """
        Inizializza l'eccezione con il valore ricevuto.
        
        Args:
            numero_riga_ricevuto: il valore che è stato passato ma non è un intero
        """
        self.numero_riga_ricevuto = numero_riga_ricevuto
        self.tipo_ricevuto = type(numero_riga_ricevuto).__name__
        
        # Messaggio descrittivo che spiega il problema
        messaggio = (
            f"Il parametro 'numero_riga' deve essere un intero (int), "
            f"ma hai fornito {self.tipo_ricevuto}. "
            f"Valore ricevuto: {numero_riga_ricevuto}"
        )
        
        super().__init__(messaggio)


class CartellaRigaValueException(CartellaException):
    """
    Eccezione lanciata quando il valore di 'numero_riga' non è 0, 1 o 2.
    
    Questa eccezione viene lanciata quando un metodo riceve un indice di riga
    che è sì un intero, ma non è uno dei valori validi (0, 1, 2).
    La cartella ha esattamente 3 righe, con indici 0, 1 e 2.
    
    Attributi:
        numero_riga_ricevuto: il valore intero ricevuto ma non valido
    
    Esempio:
        cartella.get_numeri_riga(-1)  # ValueError: numero_riga -1 non valido, deve essere 0, 1 o 2
        cartella.get_numeri_riga(3)   # ValueError: numero_riga 3 non valido, deve essere 0, 1 o 2
        cartella.stampa_riga(5)       # ValueError: numero_riga 5 non valido, deve essere 0, 1 o 2
    """
    
    def __init__(self, numero_riga_ricevuto):
        """
        Inizializza l'eccezione con il numero di riga fuori range ricevuto.
        
        Args:
            numero_riga_ricevuto: il valore intero che non è 0, 1 o 2
        """
        self.numero_riga_ricevuto = numero_riga_ricevuto
        
        # Messaggio descrittivo che spiega il problema
        messaggio = (
            f"Il parametro 'numero_riga' deve essere 0, 1 o 2, "
            f"ma hai fornito {numero_riga_ricevuto}. "
            f"La cartella ha 3 righe con indici: 0, 1, 2"
        )
        
        super().__init__(messaggio)


# ============================================================================
# ECCEZIONI PER IL PARAMETRO "numero_colonna" (0-8)
# ============================================================================

class CartellaColonnaTypeException(CartellaException):
    """
    Eccezione lanciata quando il parametro 'numero_colonna' non è un intero.
    
    Questa eccezione viene lanciata quando un metodo riceve un indice di colonna
    che non è di tipo int (es. string, float, None, list, ecc.).
    
    Attributi:
        numero_colonna_ricevuto: il valore effettivamente ricevuto
        tipo_ricevuto: il tipo effettivo del parametro
    
    Esempio:
        cartella.get_numeri_colonna("3")  # TypeError: numero_colonna deve essere int, ricevuto str
        cartella.stampa_colonna(5.0)      # TypeError: numero_colonna deve essere int, ricevuto float
    """
    
    def __init__(self, numero_colonna_ricevuto):
        """
        Inizializza l'eccezione con il valore ricevuto.
        
        Args:
            numero_colonna_ricevuto: il valore che è stato passato ma non è un intero
        """
        self.numero_colonna_ricevuto = numero_colonna_ricevuto
        self.tipo_ricevuto = type(numero_colonna_ricevuto).__name__
        
        # Messaggio descrittivo che spiega il problema
        messaggio = (
            f"Il parametro 'numero_colonna' deve essere un intero (int), "
            f"ma hai fornito {self.tipo_ricevuto}. "
            f"Valore ricevuto: {numero_colonna_ricevuto}"
        )
        
        super().__init__(messaggio)


class CartellaColonnaValueException(CartellaException):
    """
    Eccezione lanciata quando il valore di 'numero_colonna' non è tra 0 e 8.
    
    Questa eccezione viene lanciata quando un metodo riceve un indice di colonna
    che è sì un intero, ma non è compreso tra 0 e 8. La cartella ha esattamente
    9 colonne, con indici da 0 a 8.
    
    Attributi:
        numero_colonna_ricevuto: il valore intero ricevuto ma non valido
    
    Esempio:
        cartella.get_numeri_colonna(-1)  # ValueError: numero_colonna -1 non valido, deve essere 0-8
        cartella.get_numeri_colonna(9)   # ValueError: numero_colonna 9 non valido, deve essere 0-8
        cartella.stampa_colonna(10)      # ValueError: numero_colonna 10 non valido, deve essere 0-8
    """
    
    def __init__(self, numero_colonna_ricevuto):
        """
        Inizializza l'eccezione con il numero di colonna fuori range ricevuto.
        
        Args:
            numero_colonna_ricevuto: il valore intero che non è tra 0 e 8
        """
        self.numero_colonna_ricevuto = numero_colonna_ricevuto
        
        # Messaggio descrittivo che spiega il problema
        messaggio = (
            f"Il parametro 'numero_colonna' deve essere compreso tra 0 e 8, "
            f"ma hai fornito {numero_colonna_ricevuto}. "
            f"La cartella ha 9 colonne con indici: 0, 1, 2, 3, 4, 5, 6, 7, 8"
        )
        
        super().__init__(messaggio)


# ============================================================================
# RIEPILOGO DELLE ECCEZIONI
# ============================================================================

"""
COME USARE QUESTE ECCEZIONI:

1. CATTURA SPECIFICA (consigliato durante lo sviluppo):
   try:
       cartella.get_numeri_riga(5)
   except CartellaRigaValueException as e:
       print(f"Riga non valida: {e}")

2. CATTURA GENERICA PER TIPO (quando non importa il tipo specifico):
   try:
       cartella.get_numeri_riga("zero")
   except CartellaRigaTypeException:
       print("Il tipo deve essere intero")

3. CATTURA GENERICA PER CATEGORIA (quando importa solo se è tipo o valore):
   try:
       numero = int(input("Numero: "))
       cartella.segna_numero(numero)
   except CartellaNumeroTypeException:
       print("Errore di tipo")
   except CartellaNumeroValueException:
       print("Errore di valore")

4. CATTURA GLOBALE (quando vogliamo gestire QUALSIASI errore della Cartella):
   try:
       cartella.get_numeri_riga(5)
   except CartellaException as e:
       print(f"Errore generico della Cartella: {e}")

METODI CHE LANCIANO QUESTE ECCEZIONI:

numero_ricevuto non è int:
- segna_numero(numero)
- is_numero_segnato(numero)

numero_ricevuto non è in 1-90:
- segna_numero(numero) 
- is_numero_segnato(numero)

numero_riga_ricevuto non è int:
- get_numeri_riga(numero_riga)
- get_numeri_segnati_riga(numero_riga)
- get_stato_riga(numero_riga)
- stampa_riga(numero_riga)
- verifica_ambo_riga(numero_riga)
- verifica_terno_riga(numero_riga)
- verifica_quaterna_riga(numero_riga)
- verifica_cinquina_riga(numero_riga)

numero_riga_ricevuto non è 0, 1 o 2:
- get_numeri_riga(numero_riga)
- get_numeri_segnati_riga(numero_riga)
- get_stato_riga(numero_riga)
- stampa_riga(numero_riga)
- verifica_ambo_riga(numero_riga)
- verifica_terno_riga(numero_riga)
- verifica_quaterna_riga(numero_riga)
- verifica_cinquina_riga(numero_riga)

numero_colonna_ricevuto non è int:
- get_numeri_colonna(numero_colonna)
- get_numeri_segnati_colonna(numero_colonna)
- stampa_colonna(numero_colonna)

numero_colonna_ricevuto non è 0-8:
- get_numeri_colonna(numero_colonna)
- get_numeri_segnati_colonna(numero_colonna)
- stampa_colonna(numero_colonna)
"""
