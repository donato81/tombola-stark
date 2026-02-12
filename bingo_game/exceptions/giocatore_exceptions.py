"""
Modulo per la gestione delle eccezioni personalizzate della classe GiocatoreBase.

Questo modulo contiene tutte le eccezioni specifiche che le classi
Giocatore (GiocatoreBase, GiocatoreUmano, GiocatoreAutomatico) possono
lanciare durante l'esecuzione dei loro metodi.

Le eccezioni sono organizzate gerarchicamente:
- una classe base (GiocatoreException)
- varie eccezioni specifiche che ereditano da essa.

Struttura delle eccezioni:

- GiocatoreException (classe base, genitore di tutte le altre)

  ├── GiocatoreNomeTypeException
  │   (il parametro nome non è una stringa)
  ├── GiocatoreNomeValueException
  │   (il parametro nome è vuoto o solo spazi)
  ├── GiocatoreIdTypeException
  │   (il parametro id_giocatore non è un intero o None)
  ├── GiocatoreCartellaTypeException
  │   (l'oggetto passato ad aggiungi_cartella non è una Cartella)
  ├── GiocatoreNumeroTypeException
  │   (il parametro numero non è un intero)
  └── GiocatoreNumeroValueException
  (il valore di numero non è nel range 1-90)

Vantaggi di questa struttura:

- Gerarchia chiara: tutte le eccezioni del giocatore ereditano da GiocatoreException.
- Cattura granulare: puoi catturare eccezioni specifiche oppure tutte insieme.
- Messaggi chiari: ogni eccezione ha messaggi descrittivi per facilitare il debug.
- Manutenibile: aggiungere nuove eccezioni è semplice grazie alla struttura base.

Path: bingo_game/exceptions/giocatore_exceptions.py
"""

# CLASSE BASE - Tutte le eccezioni del Giocatore ereditano da questa
class GiocatoreException(Exception):
    """
    Eccezione base per tutti gli errori delle classi Giocatore.
    Questa è la classe genitore di tutte le eccezioni specifiche legate
    ai giocatori (GiocatoreBase, GiocatoreUmano, GiocatoreAutomatico).
    Usarla per catturare TUTTE le eccezioni dei giocatori in una sola volta.
    Esempio:
        try:
            giocatore.aggiungi_cartella(oggetto_non_valido)
        except GiocatoreException:
            print("Errore generico nel giocatore")
    """
    pass



# ECCEZIONI PER IL PARAMETRO "nome" DEL GIOCATORE
class GiocatoreNomeTypeException(GiocatoreException):
    """
    Eccezione lanciata quando il parametro 'nome' non è una stringa.
    Viene usata quando il costruttore di GiocatoreBase (o derivati) riceve
    un valore non str per il nome (es. int, float, None, list, ecc.).
    Attributi:
        nome_ricevuto: il valore effettivamente ricevuto
        tipo_ricevuto: il tipo effettivo del parametro
    Esempio:
        GiocatoreBase(123)         # TypeError: nome deve essere str, ricevuto int
        GiocatoreBase(None)       # TypeError: nome deve essere str, ricevuto NoneType
    """

    def __init__(self, nome_ricevuto):
        """
        Inizializza l'eccezione con il valore ricevuto.
        Args:
            nome_ricevuto: il valore che è stato passato ma non è una stringa
        """
        self.nome_ricevuto = nome_ricevuto
        self.tipo_ricevuto = type(nome_ricevuto).__name__
        messaggio = (
            "Il parametro 'nome' deve essere una stringa (str), "
            f"ma hai fornito {self.tipo_ricevuto}. "
            f"Valore ricevuto: {nome_ricevuto}"
        )
        super().__init__(messaggio)


class GiocatoreNomeValueException(GiocatoreException):
    """
    Eccezione lanciata quando il valore di 'nome' è vuoto o solo spazi.
    Viene usata quando il costruttore riceve una stringa, ma priva di
    contenuto utile per identificare il giocatore.
    Attributi:
        nome_ricevuto: la stringa ricevuta ma ritenuta non valida
    Esempio:
        GiocatoreBase("")          # ValueError: nome non può essere vuoto
        GiocatoreBase("   ")       # ValueError: nome non può essere solo spazi
    """

    def __init__(self, nome_ricevuto: str):
        """
        Inizializza l'eccezione con il nome non valido ricevuto.
        Args:
            nome_ricevuto: la stringa considerata non valida
        """
        self.nome_ricevuto = nome_ricevuto
        messaggio = (
            "Il parametro 'nome' non può essere vuoto o composto solo da spazi. "
            f"Valore ricevuto: {repr(nome_ricevuto)}"
        )
        super().__init__(messaggio)



# ECCEZIONE PER IL PARAMETRO "id_giocatore"
class GiocatoreIdTypeException(GiocatoreException):
    """
    Eccezione lanciata quando 'id_giocatore' non è un intero o None.
    Viene usata quando il costruttore riceve un id con tipo non valido.
    Attributi:
        id_ricevuto: il valore effettivamente ricevuto
        tipo_ricevuto: il tipo effettivo del parametro
    Esempio:
        GiocatoreBase("Mario", id_giocatore="1")  # TypeError: id_giocatore deve essere int o None
    """

    def __init__(self, id_ricevuto):
        """
        Inizializza l'eccezione con il valore ricevuto.
        Args:
            id_ricevuto: il valore che è stato passato ma non è int o None
        """
        self.id_ricevuto = id_ricevuto
        self.tipo_ricevuto = type(id_ricevuto).__name__
        messaggio = (
            "Il parametro 'id_giocatore' deve essere un intero (int) o None, "
            f"ma hai fornito {self.tipo_ricevuto}. "
            f"Valore ricevuto: {id_ricevuto}"
        )
        super().__init__(messaggio)



# ECCEZIONE PER IL PARAMETRO "cartella" IN aggiungi_cartella()
class GiocatoreCartellaTypeException(GiocatoreException):
    """
    Eccezione lanciata quando l'oggetto passato ad aggiungi_cartella()
    non è un'istanza di Cartella.
    Viene usata per impedire di aggiungere al giocatore oggetti di tipo
    errato (es. None, int, stringhe, ecc.).
    Attributi:
        cartella_ricevuta: il valore effettivamente ricevuto
        tipo_ricevuto: il tipo effettivo del parametro
    Esempio:
        giocatore.aggiungi_cartella(None)
        giocatore.aggiungi_cartella("non è una cartella")
    """

    def __init__(self, cartella_ricevuta):
        """
        Inizializza l'eccezione con il valore ricevuto.
        Args:
            cartella_ricevuta: il valore che è stato passato ma non è una Cartella
        """
        self.cartella_ricevuta = cartella_ricevuta
        self.tipo_ricevuto = type(cartella_ricevuta).__name__
        messaggio = (
            "Il parametro 'cartella' deve essere un'istanza di Cartella, "
            f"ma hai fornito {self.tipo_ricevuto}. "
            f"Valore ricevuto: {cartella_ricevuta}"
        )
        super().__init__(messaggio)



# ECCEZIONI PER IL PARAMETRO "numero" IN aggiorna_con_numero()
class GiocatoreNumeroTypeException(GiocatoreException):
    """
    Eccezione lanciata quando il parametro 'numero' non è un intero.
    Viene usata da aggiorna_con_numero() quando riceve un valore non int.
    Attributi:
        numero_ricevuto: il valore effettivamente ricevuto
        tipo_ricevuto: il tipo effettivo del parametro
    Esempio:
        giocatore.aggiorna_con_numero("45")
        giocatore.aggiorna_con_numero(10.5)
    """

    def __init__(self, numero_ricevuto):
        """
        Inizializza l'eccezione con il valore ricevuto.
        Args:
            numero_ricevuto: il valore che è stato passato ma non è un intero
        """
        self.numero_ricevuto = numero_ricevuto
        self.tipo_ricevuto = type(numero_ricevuto).__name__
        messaggio = (
            "Il parametro 'numero' deve essere un intero (int), "
            f"ma hai fornito {self.tipo_ricevuto}. "
            f"Valore ricevuto: {numero_ricevuto}"
        )
        super().__init__(messaggio)


class GiocatoreNumeroValueException(GiocatoreException):
    """
    Eccezione lanciata quando il valore di 'numero' non è nel range 1-90.
    Viene usata da aggiorna_con_numero() quando il numero è int ma fuori
    dal range valido della tombola.
    Attributi:
        numero_ricevuto: il valore intero ricevuto ma fuori range
    Esempio:
        giocatore.aggiorna_con_numero(0)
        giocatore.aggiorna_con_numero(100)
    """

    def __init__(self, numero_ricevuto: int):
        """
        Inizializza l'eccezione con il numero fuori range ricevuto.
        Args:
            numero_ricevuto: il valore intero che è fuori dal range 1-90
        """
        self.numero_ricevuto = numero_ricevuto
        messaggio = (
            "Il parametro 'numero' deve essere compreso tra 1 e 90, "
            f"ma hai fornito {numero_ricevuto}. "
            "Range valido: 1-90"
        )
        super().__init__(messaggio)
