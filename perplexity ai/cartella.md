from __future__ import annotations 
#import delle librerie python necessarie al codice
#importazione della libreria random per la generazione dei numeri casuali
import random
#import delle eccezioni personalizzate
from bingo_game.exceptions.cartella_exceptions import (
    CartellaNumeroTypeException,
    CartellaNumeroValueException,
    CartellaRigaTypeException,
    CartellaRigaValueException,
    CartellaColonnaTypeException,
    CartellaColonnaValueException,
)



#definizione della classe Cartella
class Cartella:
    #costruttore della classe Cartella
    def __init__(self, max_numero=90, quantita_numeri=15, nome: str | None = None, indice: int | None = None):
        #definizione dei parametri della cartella
        #totale numeri estraibili
        self.max_numero = max_numero
        #quantita massima di numeri per la cartella
        self.quantita_numeri = quantita_numeri
        #nome della cartella
        self.nome = nome
        #indice della cartella
        self.indice = indice
        #definisce quante righe ha la cartella
        self.righe = 3
        #definisce quante colonne ha la cartella
        self.colonne = 9
        #definisce quanti numeri possono essere contenuti in una riga
        self.numeri_per_riga = 5
        # Set per segnare i numeri estratti presenti nella cartella
        self.numeri_segnati = set()
        #crea una matrice di liste utilizzando il numero di righe e di colonne
        self.cartella = [[None for _ in range(self.colonne)] for _ in range(self.righe)]
        #inizializza il set dei numeri presenti nella cartella
        self.numeri_cartella = set()
        # Genera la cartella come set di numeri unici casuali
        self._genera_cartella()


    """metodi di classe"""

    """metodi privati dedicati alla generazione della cartella di gioco della tombola italiana"""

    #metodo per definire gli intervalli di numeri per ogni colonna
    def _definisci_range_colonne(self): 
        #lista che contiene gli intervalli di numeri per ogni colonna
        range_colonne  = [
            range(1, 10),    # Colonna 0: numeri da 1 a 9
            range(10, 20),   # Colonna 1: numeri da 10 a 19
            range(20, 30),   # Colonna 2: numeri da 20 a 29
            range(30, 40),   # Colonna 3: numeri da 30 a 39
            range(40, 50),   # Colonna 4: numeri da 40 a 49
            range(50, 60),   # Colonna 5: numeri da 50 a 59
            range(60, 70),   # Colonna 6: numeri da 60 a 69
            range(70, 80),   # Colonna 7: numeri da 70 a 79
            range(80, 91)    # Colonna 8: numeri da 80 a 90
        ] 
        return range_colonne

    #metodo per calcolare la distribuzione dei numeri tra le colonne
    def _get_colonne_occupazione_corrente(self):
        """
        Conta quanti numeri sono già stati messi in ogni colonna.
        Questo metodo esamina la matrice della cartella e per ogni colonna (da 0 a 8)
        conta quanti numeri NON sono None (cioè quanti numeri sono già stati posizionati).
        Ritorna una lista di 9 numeri, uno per ogni colonna.
        Ogni numero rappresenta "quanti numeri sono già in questa colonna".
        Esempio:
        Se la cartella ha numeri solo nella prima riga:
        - Colonna 0: ha 1 numero
        - Colonna 1: ha 0 numeri
        - Colonna 2: ha 1 numero
        - ... e così via
        Ritorna: [1, 0, 1, 1, 0, 1, 0, 0, 1]
        Returns:
            list: Lista di 9 interi (uno per ogni colonna) che dice quanti numeri sono
                già presenti in quella colonna. Ogni numero è tra 0 e 3.
        """
        
        # Crea una lista con 9 zeri (uno per ogni colonna)
        occupazione = [0] * self.colonne
        
        # Per ogni riga della matrice
        for riga in range(self.righe):
            # Per ogni colonna della matrice
            for colonna in range(self.colonne):
                # Prendi il valore nella posizione attuale
                valore = self.cartella[riga][colonna]
                
                # Se il valore NON è None (cioè è un numero)
                if valore is not None:
                    # Incrementa il contatore di questa colonna
                    occupazione[colonna] += 1
        
        # Ritorna la lista con i conteggi finali
        return occupazione

    #metodo per scegliere le colonne disponibili per una riga
    def _scegli_colonne_disponibili_per_riga(self, numero_riga):
        """
        Sceglie quali colonne possono ancora ricevere numeri in questa riga.
        Una colonna è disponibile se ha MENO di 3 numeri.
        Una colonna NON è disponibile se ha già 3 numeri (il massimo consentito).
        Questo metodo chiama _get_colonne_occupazione_corrente() per sapere
        quanti numeri ci sono in ogni colonna al momento.
        Poi ritorna una lista con SOLO le colonne che possono ancora ricevere numeri.
        Parametri:
            numero_riga: il numero della riga che vogliamo riempire (0, 1 o 2)
                        Nota: questo parametro serve per eventuali future estensioni
        Returns:
            list: Lista con i numeri delle colonne disponibili
        Esempio:
            Se l'occupazione è [2, 3, 1, 3, 0, 1, 2, 3, 1]
            Ritorna [0, 2, 4, 5, 6, 8]
            (Esclude le colonne 1, 3, 7 che hanno già 3 numeri)
        """
        
        # Chiama il metodo che conta i numeri per ogni colonna
        occupazione = self._get_colonne_occupazione_corrente()
        
        # Crea una lista vuota per le colonne disponibili
        colonne_disponibili = []
        
        # Per ogni colonna (da 0 a 8)
        for indice_colonna in range(self.colonne):
            # Prendi il numero di numeri già presenti in questa colonna
            numeri_nella_colonna = occupazione[indice_colonna]
            
            # Se la colonna ha MENO di 3 numeri
            if numeri_nella_colonna < 3:
                # Aggiungila alla lista delle colonne disponibili
                colonne_disponibili.append(indice_colonna)
        
        # Ritorna la lista con le colonne che possono ancora ricevere numeri
        return colonne_disponibili

    #metodo per riempire una riga con numeri unici
    def _riempi_riga(self, numero_riga):
        """
        Riempie una riga con ESATTAMENTE 5 numeri unici.
        Questo metodo è il cuore della generazione della cartella.
        Riempie UNA SOLA riga con esattamente cinque numeri, rispettando:
        - Massimo 3 numeri per colonna
        - Range numeri corretto per ogni colonna
        - Numeri unici (nessun duplicato)
        - 5 colonne diverse per questa riga
        Parametri:
            numero_riga: il numero della riga da riempire (0, 1 o 2)
        Returns:
            Nulla. Modifica direttamente self.cartella
        """
        
        # Chiama il metodo che dice quali colonne possono ricevere numeri
        colonne_disponibili = self._scegli_colonne_disponibili_per_riga(numero_riga)
        
        # Controlla che ci siano almeno 5 colonne disponibili
        if len(colonne_disponibili) < 5:
            raise RuntimeError(f"Errore: solo {len(colonne_disponibili)} colonne disponibili per riga {numero_riga}, servono 5")
        
        # Scegli ESATTAMENTE 5 colonne diverse a caso tra quelle disponibili
        colonne_scelte = random.sample(colonne_disponibili, 5)
        
        # Per ogni colonna scelta, genera un numero e posizionalo
        for indice_colonna in colonne_scelte:
            # Riprova finché non trovi un numero che non è già nella cartella
            numero_valido = False
            tentativi = 0
            max_tentativi = 100
            
            while not numero_valido and tentativi < max_tentativi:
                tentativi += 1
                
                # Ottieni il range di numeri possibili per questa colonna
                range_colonna = self._definisci_range_colonne()[indice_colonna]
                
                # Genera un numero casuale dal range di questa colonna
                numero_casuale = random.choice(list(range_colonna))
                
                # Controlla se il numero è già nella cartella
                if numero_casuale not in self.numeri_cartella:
                    # Il numero è nuovo, è valido
                    numero_valido = True
                    # Posiziona il numero nella matrice
                    self.cartella[numero_riga][indice_colonna] = numero_casuale
                    # Aggiungilo al set dei numeri della cartella
                    self.numeri_cartella.add(numero_casuale)
            
            # Se dopo 100 tentativi non trova un numero valido, errore
            if not numero_valido:
                raise RuntimeError(f"Impossibile trovare un numero valido per riga {numero_riga}, colonna {indice_colonna}")




    #metodo per estrarre tutti i numeri dalla matrice e creare un set
    def _estrai_numeri_set(self):
        """ Estrae tutti i numeri dalla matrice self.cartella e li inserisce in un set.
            Questo metodo scorre la matrice 3x9, raccoglie tutti i valori che non sono None, e crea un set con questi numeri.
            Parametri:
            - Nessuno (usa self.cartella e self.righe e self.colonne)
            Ritorna:
            - Un set contenente tutti i 15 numeri presenti nella cartella
            Il set viene usato da segna_numero() per verifiche veloci di appartenenza (ricerca O(1))
        """

        # Crea un set vuoto che conterrà tutti i numeri estratti
        numeri_cartella = set()

        # Itera su ogni riga della matrice
        for indice_riga in range(self.righe):
            # Per ogni riga, itera su ogni colonna

            for indice_colonna in range(self.colonne):
                # Prende il numero nella posizione corrente
                valore = self.cartella[indice_riga][indice_colonna]
                # Se il numero non è None (cioè è un numero valido) 

                if valore is not None:
                    # Aggiunge il numero al set
                    numeri_cartella.add(valore)

        # Ritorna il set con tutti i numeri
        return numeri_cartella



    #metodo per ordinare i numeri dentro ogni colonna
    def _ordina_numeri_nelle_colonne(self):
        """
        Ordina i numeri dentro ogni colonna dal più piccolo al più grande.
        """
        
        # Per ogni colonna (da 0 a 8)
        for indice_colonna in range(self.colonne):
            # Estrai tutti i numeri presenti in questa colonna
            numeri_colonna = []
            posizioni_numeri = []
            
            for indice_riga in range(self.righe):
                numero = self.cartella[indice_riga][indice_colonna]
                if numero is not None:
                    numeri_colonna.append(numero)
                    posizioni_numeri.append(indice_riga)
            
            # Ordina i numeri dal più piccolo al più grande
            numeri_colonna.sort()
            
            # Metti di nuovo i numeri ordinati nelle STESSE posizioni di prima
            for indice_posizione in range(len(posizioni_numeri)):
                riga_corretta = posizioni_numeri[indice_posizione]
                self.cartella[riga_corretta][indice_colonna] = numeri_colonna[indice_posizione]






    #metodo per validare che la cartella sia stata generata correttamente
    def _valida_cartella_generata(self):
        """
        Valida che la cartella generata rispetti TUTTE le 7 regole fondamentali.
        Regole che controlla:
        1. Totale numeri: esattamente 15
        2. Numeri unici: nessun duplicato
        3. Massimo 3 numeri per colonna
        4. Esattamente 5 numeri per riga
        5. Ogni numero nel range corretto della colonna
        6. 5 colonne diverse per ogni riga
        7. Nessun None nella matrice (tutte le posizioni riempite correttamente)
        Raises:
            RuntimeError: se una qualsiasi regola viene violata
        """
        
        # REGOLA 1: Conta i numeri totali - devono essere ESATTAMENTE 15
        totale_numeri = len(self.numeri_cartella)
        if totale_numeri != 15:
            raise RuntimeError(f"Errore Regola 1: totale numeri {totale_numeri}, deve essere 15")
        
        # REGOLA 2: Tutti i numeri devono essere unici (nessun duplicato)
        numeri_non_unici = []
        for numero in self.numeri_cartella:
            conteggio = 0
            for riga in self.cartella:
                for valore in riga:
                    if valore == numero:
                        conteggio += 1
            if conteggio > 1:
                numeri_non_unici.append(numero)
        
        if numeri_non_unici:
            raise RuntimeError(f"Errore Regola 2: numeri duplicati trovati {numeri_non_unici}")
        
        # REGOLA 3: Massimo 3 numeri per colonna
        occupazione = self._get_colonne_occupazione_corrente()
        for indice_colonna in range(len(occupazione)):
            if occupazione[indice_colonna] > 3:
                raise RuntimeError(f"Errore Regola 3: colonna {indice_colonna} ha {occupazione[indice_colonna]} numeri, massimo 3")
        
        # REGOLA 4: Esattamente 5 numeri per riga
        for indice_riga in range(self.righe):
            numeri_nella_riga = 0
            for valore in self.cartella[indice_riga]:
                if valore is not None:
                    numeri_nella_riga += 1
            if numeri_nella_riga != 5:
                raise RuntimeError(f"Errore Regola 4: riga {indice_riga} ha {numeri_nella_riga} numeri, deve averne 5")
        
        # REGOLA 5: Ogni numero nel range corretto della colonna
        range_colonne = self._definisci_range_colonne()
        for indice_riga in range(self.righe):
            for indice_colonna in range(self.colonne):
                numero = self.cartella[indice_riga][indice_colonna]
                if numero is not None:
                    range_colonna = range_colonne[indice_colonna]
                    if numero not in range_colonna:
                        raise RuntimeError(f"Errore Regola 5: numero {numero} in riga {indice_riga} colonna {indice_colonna} non è nel range {range_colonna}")
        
        # REGOLA 6: 5 colonne diverse per ogni riga
        for indice_riga in range(self.righe):
            colonne_utilizzate = []
            for indice_colonna in range(self.colonne):
                numero = self.cartella[indice_riga][indice_colonna]
                if numero is not None:
                    colonne_utilizzate.append(indice_colonna)
            
            if len(colonne_utilizzate) != 5:
                raise RuntimeError(f"Errore Regola 6: riga {indice_riga} non ha 5 colonne diverse, ha {len(colonne_utilizzate)}")
            
            if len(set(colonne_utilizzate)) != 5:
                raise RuntimeError(f"Errore Regola 6: riga {indice_riga} ha colonne duplicate")
        
        # REGOLA 7: Nessun None nella matrice (tutte le celle riempite)
        nessun_none = True
        for indice_riga in range(self.righe):
            numeri_nella_riga = sum(1 for valore in self.cartella[indice_riga] if valore is not None)
            if numeri_nella_riga != 5:
                nessun_none = False
                break
        
        if not nessun_none:
            raise RuntimeError("Errore Regola 7: la cartella non è stata riempita correttamente")
        
        # Se arriviamo qui, tutto è corretto
        print("Validazione completata: Cartella VALIDA! Tutte le 7 regole rispettate.")


    #metodo per generare la cartella di gioco
    def _genera_cartella(self):
        """
        Genera una cartella completa con 15 numeri distribuiti su 3 righe.
        Questo è il metodo ORCHESTRATORE principale.
        Coordina il riempimento di tutte le righe della cartella.
        Il processo:
        1. Inizializza la matrice vuota (3 righe x 9 colonne)
        2. Riempie la riga 0 con 5 numeri
        3. Riempie la riga 1 con 5 numeri
        4. Riempie la riga 2 con 5 numeri
        5. Estrae tutti i numeri generati nel set numeri_cartella
        6. Ordina i numeri nelle colonne dal più piccolo al più grande
        7. Valida che tutto sia corretto secondo le regole
        Returns:
            Nulla. Modifica direttamente self.cartella e self.numeri_cartella
        """
        
        # Inizializza la matrice: 3 righe x 9 colonne, tutto vuoto (None)
        self.cartella = [[None for _ in range(self.colonne)] for _ in range(self.righe)]
        
        # Inizializza il set dei numeri della cartella (vuoto)
        self.numeri_cartella = set()
        
        # Riempi la riga 0 con 5 numeri unici
        self._riempi_riga(0)
        
        # Riempi la riga 1 con 5 numeri unici
        self._riempi_riga(1)
        
        # Riempi la riga 2 con 5 numeri unici
        self._riempi_riga(2)
        
        # Estrai tutti i numeri dalla matrice e mettili nel set numeri_cartella
        self.numeri_cartella = self._estrai_numeri_set()
        
        # Ordina i numeri nelle colonne dal più piccolo al più grande
        self._ordina_numeri_nelle_colonne()

        # Valida che la cartella generata rispetti tutte le regole
        self._valida_cartella_generata()







    """metodi pubblici della classe Cartella"""


    #metodo per ottenere i numeri della cartella
    def get_numeri_cartella(self):
        # Ritorna la lista ordinata dei numeri nella cartella
        return sorted(self.numeri_cartella)


    def get_griglia_semplice(self) -> tuple[tuple[int | str, ...], ...]:
        """
        Ritorna una rappresentazione "semplice" della cartella come struttura dati immutabile.

        Scopo:
        - Esporre i dati della cartella senza generare stringhe di output pronte per l'utente.
        - Fornire una base stabile per gli eventi (e quindi per il renderer), mantenendo la logica
        di trasformazione vicino al dominio Cartella.
        - Evitare che codice esterno modifichi accidentalmente la matrice interna: il metodo
        restituisce una copia immutabile (tupla di tuple).

        Formato di ritorno:
        - Una griglia 3x9 (righe x colonne) sotto forma di tupla di tuple.
        - Ogni cella contiene:
            - "-" se nella matrice interna è presente None (spazio vuoto),
            - un int se nella matrice interna è presente un numero.

        Note:
        - Questo metodo NON dipende da lingua/renderer e NON produce testo multi-riga.
        - La scelta di usare "-" (stringa) come segnaposto è volutamente minimale: il renderer
        potrà decidere come presentarlo (trattino, "vuoto", pausa, ecc.).

        Ritorna:
        - tuple[tuple[int | str, ...], ...]: griglia immutabile 3x9 con numeri e "-".
        """

        # 1) Prepariamo una lista temporanea che verrà poi convertita in struttura immutabile.
        righe_out: list[tuple[int | str, ...]] = []


        # 2) Scansione riga/colonna della matrice interna.
        for indice_riga in range(self.righe):
            celle_riga: list[int | str] = []

            for indice_colonna in range(self.colonne):
                valore = self.cartella[indice_riga][indice_colonna]

                # 3) Normalizzazione "semplice":
                #    - None diventa "-", mantenendo l'idea della stampa semplice.
                #    - I numeri restano int (dato grezzo).
                if valore is None:
                    celle_riga.append("-")
                else:
                    celle_riga.append(valore)

            # 4) Convertiamo la riga in tupla per renderla immutabile.
            righe_out.append(tuple(celle_riga))

        # 5) Convertiamo l'intera griglia in tupla di tuple (immutabile).
        return tuple(righe_out)


    def get_dati_visualizzazione_avanzata(self) -> tuple[tuple[tuple[int | str, ...], ...], dict[str, int | float | tuple[int, ...]], tuple[int, ...]]:
        """
        Ritorna TUTTI i dati necessari per una visualizzazione "avanzata" della cartella,
        senza produrre stringhe. Fornisce griglia, stato segnati e riepilogo numerico.

        Scopo:
        - Sostituire stampa_cartella_con_stato() con dati grezzi per eventi/renderer.
        - Centralizzare tutta la logica di "visualizzazione avanzata" in Cartella.
        - Garantire immutabilità: tutto ritornato come tuple (nessuna lista modificabile).

        Componenti ritornati:
        1) griglia_semplice: tuple[3 righe x 9 celle] con int (numeri) o "-" (vuoti).
        2) stato_cartella: dict normalizzato con tuple invece di liste (conteggi, percentuali).
        3) numeri_segnati_ordinati: tuple[int] ordinata dei numeri attualmente segnati.

        Ritorno:
        - tuple[griglia, stato, segnati]: pacchetto completo e immutabile per l'evento.
        """
        # 1) Griglia base 3x9: riutilizza il metodo già stabile e testato.
        #    Contiene solo numeri (int) oppure "-" (vuoti).
        griglia_semplice = self.get_griglia_semplice()

        # 2) Stato globale: conteggi, percentuali, liste ordinate.
        #    Riutilizza get_stato_cartella() per evitare duplicazioni di logica.
        stato_cartella = self.get_stato_cartella()

        # 3) Numeri segnati ordinati: per sapere QUALI numeri della griglia sono usciti.
        #    Dal set interno → tuple ordinata (immutabile e prevedibile).
        numeri_segnati_ordinati = tuple(sorted(self.numeri_segnati))

        # 4) Normalizza lo stato per immutabilità: tutte le liste diventano tuple.
        #    Garantisce che il consumatore (evento/renderer) non modifichi accidentalmente.
        stato_normalizzato = {
            'numeri_totali': stato_cartella['numeri_totali'],
            'numeri_segnati': stato_cartella['numeri_segnati'],
            'numeri_non_segnati': stato_cartella['numeri_non_segnati'],
            'lista_numeri_cartella': tuple(stato_cartella['lista_numeri_cartella']),
            'lista_numeri_non_segnati': tuple(stato_cartella['lista_numeri_non_segnati']),
            'percentuale_completamento': stato_cartella['percentuale_completamento'],
        }

        # 5) Pacchetto completo: tutto immutabile, tutto riutilizzabile.
        #    L'evento scompone questa tupla e la passa al renderer.
        return (
            griglia_semplice,           # 3x9 per il layout
            stato_normalizzato,         # numeri per footer/percentuali
            numeri_segnati_ordinati,    # per asterischi + "Segnati: ..."
        )


    def get_riga_semplice(self, numero_riga: int) -> tuple[int | str, ...]:
        """
        Ritorna la riga della cartella in formato "semplice" come struttura dati immutabile.

        Scopo:
        - Fornire una rappresentazione dati (non testuale) della riga richiesta, utile per eventi/renderer.
        - Evitare che il chiamante debba:
            * chiamare get_griglia_semplice()
            * spacchettare la griglia
            * estrarre manualmente la riga
        Rendendo il codice più leggibile e coerente (es. nel giocatore umano quando si muove il focus riga).

        Formato di ritorno:
        - Una tupla di 9 celle (colonne 0..8) dove ogni cella è:
            * int se c'è un numero,
            * "-" se la cella è vuota.

        Parametri:
        - numero_riga: int (0, 1 o 2)

        Eccezioni:
        - CartellaRigaTypeException: se numero_riga non è un int.
        - CartellaRigaValueException: se numero_riga non è nel range valido (0..self.righe-1).

        Nota:
        - Questo metodo NON produce stringhe pronte per l'utente.
        - La conversione 0->1 (e simili) resta responsabilità del renderer/UI.
        """
        # 1) Validazione tipo: vogliamo un indice riga numerico.
        if not isinstance(numero_riga, int):
            raise CartellaRigaTypeException(numero_riga)

        # 2) Validazione range: la cartella ha self.righe righe (tipicamente 3: 0,1,2).
        if numero_riga < 0 or numero_riga >= self.righe:
            raise CartellaRigaValueException(numero_riga)

        # 3) Riusa la rappresentazione canonica "semplice" 3x9 (int o "-").
        griglia_semplice = self.get_griglia_semplice()

        # 4) Estrae e ritorna solo la riga richiesta (tupla immutabile di 9 celle).
        return griglia_semplice[numero_riga]


    def get_dati_visualizzazione_riga_avanzata(self, numero_riga: int) -> tuple[tuple[int | str, ...], dict[str, int | float | tuple[int, ...]], tuple[int, ...]]:
        """
        Ritorna TUTTI i dati necessari per una visualizzazione "avanzata" di UNA riga
        della cartella, senza produrre stringhe.

        Scopo:
        - Sostituire stampa_riga(...) con dati grezzi per eventi/renderer.
        - Riutilizzare la logica già esistente (griglia semplice + stato riga).
        - Garantire stabilità: ritorno prevedibile e con strutture il più possibile immutabili.

        Componenti ritornati:
        1) riga_semplice: tupla di 9 celle con int (numeri) o "-" (vuoti).
        2) stato_riga: dict normalizzato (liste convertite in tuple) con conteggi e percentuale.
        3) numeri_segnati_riga_ordinati: tupla ordinata dei numeri segnati presenti nella riga.

        Nota:
        - Il renderer userà riga_semplice + numeri_segnati_riga_ordinati per aggiungere "*"
          ai numeri segnati, senza che Cartella produca testo.
        """

        # 1) Validazioni difensive: stesso stile dei metodi pubblici già presenti.
        if not isinstance(numero_riga, int):
            raise CartellaRigaTypeException(numero_riga)

        if numero_riga < 0 or numero_riga >= self.righe:
            raise CartellaRigaValueException(numero_riga)

        # 2) Estrae la riga "layout 9 celle" riusando la griglia semplice già stabile.
        griglia_semplice = self.get_griglia_semplice()
        riga_semplice = griglia_semplice[numero_riga]

        # 3) Recupera lo stato completo della riga (conteggi e percentuale) riusando logica esistente.
        stato_riga = self.get_stato_riga(numero_riga)

        # 4) Normalizza lo stato per ridurre il rischio di modifiche accidentali (liste -> tuple).
        stato_riga_normalizzato: dict[str, int | float | tuple[int, ...]] = {
            "numeri_totali": int(stato_riga["numeri_totali"]),
            "numeri_segnati": int(stato_riga["numeri_segnati"]),
            "numeri_riga": tuple(int(n) for n in stato_riga["numeri_riga"]),
            "numeri_segnati_riga": tuple(int(n) for n in stato_riga["numeri_segnati_riga"]),
            "percentuale_completamento": float(stato_riga["percentuale_completamento"]),
        }

        # 5) Numeri segnati ordinati della riga: comodo per lookup e per output prevedibile.
        numeri_segnati_riga_ordinati = tuple(sorted(stato_riga_normalizzato["numeri_segnati_riga"]))

        # 6) Pacchetto finale: pronto per evento e renderer (nessuna stringa prodotta qui).
        return (
            riga_semplice,
            stato_riga_normalizzato,
            numeri_segnati_riga_ordinati,
        )


    def get_colonna_semplice(self, numero_colonna: int) -> tuple[int | str, ...]:
        """
        Ritorna la rappresentazione "semplice" di UNA colonna come struttura dati immutabile,
        senza produrre stringhe.

        Scopo:
        - Supportare la navigazione colonne (sinistra/destra) tramite eventi + renderer.
        - Riutilizzare la griglia semplice già stabile e testata (get_griglia_semplice),
          evitando duplicazioni di logica sui "-" (celle vuote).
        - Esporre un formato minimale e neutrale: 3 celle in ordine dall'alto verso il basso.

        Formato di ritorno:
        - tuple di lunghezza 3 (una cella per ciascuna riga).
        - Ogni cella contiene:
            - "-" se nella matrice interna era None (spazio vuoto),
            - un int se nella matrice interna era presente un numero.

        Parametri:
            - numero_colonna: int (0-8), indice di colonna da estrarre.

        Ritorna:
            - tuple[int | str, ...]: colonna immutabile con 3 celle (int o "-").
        """

        # 1) Validazioni difensive: coerenti con gli altri metodi pubblici della Cartella.
        if not isinstance(numero_colonna, int):
            raise CartellaColonnaTypeException(numero_colonna)

        if numero_colonna < 0 or numero_colonna >= self.colonne:
            raise CartellaColonnaValueException(numero_colonna)

        # 2) Ottengo la griglia semplice già normalizzata (int o "-").
        #    Questo mantiene la logica dei "vuoti" in un unico punto del codice.
        griglia_semplice = self.get_griglia_semplice()

        # 3) Estraggo la colonna richiesta, mantenendo l'ordine dall'alto verso il basso:
        #    riga 0, riga 1, riga 2.
        celle_colonna = []
        for indice_riga in range(self.righe):
            celle_colonna.append(griglia_semplice[indice_riga][numero_colonna])

        # 4) Ritorno una tupla immutabile per stabilità lato evento/renderer.
        return tuple(celle_colonna)


    def get_dati_visualizzazione_colonna_avanzata(self, numero_colonna: int) -> tuple[tuple[int | str, ...], dict[str, int | float | tuple[int, ...]], tuple[int, ...]]:
        """
        Ritorna TUTTI i dati necessari per una visualizzazione "avanzata" di UNA colonna
        della cartella, senza produrre stringhe.

        Scopo:
        - Sostituire stampa_colonna(...) con dati grezzi per eventi/renderer.
        - Riutilizzare la logica già esistente (griglia semplice + numeri colonna + segnati colonna).
        - Garantire stabilità: ritorno prevedibile e con strutture il più possibile immutabili.

        Componenti ritornati:
        1) colonna_semplice: tupla di 3 celle (una per riga) con int (numeri) o "-" (vuoti),
           in ordine dall'alto verso il basso.
        2) stato_colonna: dict normalizzato (liste convertite in tuple) con conteggi e percentuale.
        3) numeri_segnati_colonna_ordinati: tupla ordinata dei numeri segnati presenti nella colonna.

        Nota:
        - Il renderer userà colonna_semplice + numeri_segnati_colonna_ordinati per aggiungere "*"
          ai numeri segnati, senza che Cartella produca testo.
        """

        # 1) Validazioni difensive: stesso stile dei metodi pubblici già presenti.
        if not isinstance(numero_colonna, int):
            raise CartellaColonnaTypeException(numero_colonna)

        if numero_colonna < 0 or numero_colonna >= self.colonne:
            raise CartellaColonnaValueException(numero_colonna)

        # 2) Estrae la colonna "layout 3 celle" riusando la griglia semplice già stabile.
        #    Manteniamo l'ordine: riga 0, riga 1, riga 2.
        griglia_semplice = self.get_griglia_semplice()
        colonna_semplice = tuple(griglia_semplice[indice_riga][numero_colonna] for indice_riga in range(self.righe))

        # 3) Recupera i numeri presenti in colonna e i numeri segnati in colonna riusando logica esistente.
        numeri_colonna = self.get_numeri_colonna(numero_colonna)
        numeri_segnati_colonna = self.get_numeri_segnati_colonna(numero_colonna)

        # 4) Calcola conteggi e percentuale completamento.
        numeri_totali = int(len(numeri_colonna))
        numeri_segnati = int(len(numeri_segnati_colonna))

        if numeri_totali > 0:
            percentuale = round((numeri_segnati / numeri_totali) * 100, 1)
        else:
            percentuale = 0.0

        # 5) Normalizza lo stato per ridurre il rischio di modifiche accidentali (liste -> tuple).
        stato_colonna_normalizzato: dict[str, int | float | tuple[int, ...]] = {
            "numeri_totali": numeri_totali,
            "numeri_segnati": numeri_segnati,
            "numeri_colonna": tuple(int(n) for n in numeri_colonna),
            "numeri_segnati_colonna": tuple(int(n) for n in numeri_segnati_colonna),
            "percentuale_completamento": float(percentuale),
        }

        # 6) Numeri segnati ordinati della colonna: comodo per lookup e per output prevedibile.
        numeri_segnati_colonna_ordinati = tuple(sorted(stato_colonna_normalizzato["numeri_segnati_colonna"]))

        # 7) Pacchetto finale: pronto per evento e renderer (nessuna stringa prodotta qui).
        return (
            colonna_semplice,
            stato_colonna_normalizzato,
            numeri_segnati_colonna_ordinati,
        )


    #metodo per segnare un numero nella cartella
    def segna_numero(self, numero: int):
        """
        Segna un numero della cartella se presente e non ancora segnato.
        Questo metodo implementa la logica di segnazione di un numero durante il gioco.
        Utilizza un doppio controllo difensivo per garantire robustezza: verifica che il numero
        sia di tipo valido (int), nel range corretto (1-90), presente nella cartella e non sia
        già stato segnato. Il metodo è idempotente: chiamarlo due volte con lo stesso numero
        non ha effetti collaterali, la seconda chiamata semplicemente ritorna False.

        Parametri:
            - numero: int, il numero che si desidera segnare (deve essere tra 1 e 90)

        Ritorna:
            - bool: True se il numero è stato segnato con successo (era presente nella cartella
              e non era stato segnato in precedenza)
            - False se il numero non è stato segnato perché:
              * non è presente nella cartella (numero non valido per questa cartella)
              * è già stato segnato in precedenza (tentativo di re-segnazione)

        Eccezioni:
            - CartellaNumeroTypeException: se numero non è un intero (int)
            - CartellaNumeroValueException: se numero non è compreso tra 1 e 90

        Comportamento:
            - Se il numero non è int, solleva CartellaNumeroTypeException
            - Se il numero non è nel range 1-90, solleva CartellaNumeroValueException
            - Se il numero non esiste nella cartella, ritorna False senza modificare lo stato
            - Se il numero esiste ma è già segnato, ritorna False senza modificare lo stato
            - Se il numero esiste e non è segnato, lo aggiunge a numeri_segnati e ritorna True
            - Il set numeri_segnati è sempre coerente: non contiene mai duplicati
            - L'operazione è O(1) grazie ai set Python

        Complessità temporale: O(1) - lookup e insert su set sono operazioni costanti

        Esempio 1 - Segnazione valida:
            cartella = Cartella()
            numeri = cartella.get_numeri_cartella()
            risultato = cartella.segna_numero(numeri[0])
            print(risultato)  # Output: True (numero segnato con successo)

        Esempio 2 - Tentativo di re-segnazione:
            cartella = Cartella()
            numeri = cartella.get_numeri_cartella()
            primo_tentativo = cartella.segna_numero(numeri[0])
            secondo_tentativo = cartella.segna_numero(numeri[0])
            print(primo_tentativo)   # Output: True (primo tentativo riuscito)
            print(secondo_tentativo) # Output: False (il numero è già stato segnato)

        Esempio 3 - Numero non presente nella cartella:
            cartella = Cartella()
            risultato = cartella.segna_numero(50)  # 50 potrebbe non essere nella cartella
            print(risultato)  # Output: False (numero non nella cartella)

        Esempio 4 - Numero con tipo sbagliato:
            cartella = Cartella()
            cartella.segna_numero("45")  # Solleva CartellaNumeroTypeException

        Esempio 5 - Numero fuori range:
            cartella = Cartella()
            cartella.segna_numero(91)  # Solleva CartellaNumeroValueException
        """

        # Prima validazione: il tipo deve essere int
        if not isinstance(numero, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaNumeroTypeException(numero)

        # Seconda validazione: il valore deve essere nel range valido (1-90)
        if numero < 1 or numero > 90:
            # Se il numero è fuori range, solleva un'eccezione specifica di valore
            raise CartellaNumeroValueException(numero)

        # TERZO CONTROLLO: Verifica che il numero sia presente nella cartella
        # Se il numero non è in numeri_cartella, significa che non appartiene a questa cartella
        if numero not in self.numeri_cartella:
            # Il numero non è valido per questa cartella, ritorna False
            # L'operazione non viene effettuata
            return False

        # QUARTO CONTROLLO: Verifica che il numero non sia già stato segnato
        # Questo previene la re-segnazione e garantisce che ogni numero sia segnato una sola volta
        if numero in self.numeri_segnati:
            # Il numero è già stato segnato, ritorna False
            # L'operazione non viene effettuata (idempotenza)
            # Nota: non è un errore, è solo una situazione già gestita
            return False

        # SEGNAZIONE VALIDA: Il numero passa tutti i controlli
        # Aggiungi il numero al set dei numeri segnati
        self.numeri_segnati.add(numero)

        # Ritorna True per indicare che l'operazione è stata completata con successo
        return True

    #metodo per verificare se un numero è già stato segnato nella cartella
    def is_numero_segnato(self, numero: int) -> bool:
        """
        Verifica se un numero è già stato segnato nella cartella.
        Questo metodo interroga lo stato della cartella per controllare se un numero specifico
        è presente nella lista dei numeri segnati. Ritorna un valore booleano semplice.

        Parametri:
            - numero: int, il numero da verificare (deve essere tra 1 e 90)

        Ritorna:
            - bool: True se il numero è stato segnato, False altrimenti

        Eccezioni:
            - CartellaNumeroTypeException: se numero non è un intero (int)
            - CartellaNumeroValueException: se numero non è compreso tra 1 e 90

        Comportamento:
            - Se il numero non è int, solleva CartellaNumeroTypeException
            - Se il numero non è nel range 1-90, solleva CartellaNumeroValueException
            - Se il numero è nel set numeri_segnati, ritorna True
            - Se il numero non è nel set numeri_segnati, ritorna False
            - L'operazione è O(1) grazie ai set Python

        Complessità temporale: O(1) - lookup su set è un'operazione costante

        Esempio 1 - Numero non segnato:
            cartella = Cartella()
            numeri = cartella.get_numeri_cartella()
            risultato = cartella.is_numero_segnato(numeri[0])
            print(risultato)  # Output: False (numero non ancora segnato)

        Esempio 2 - Numero segnato:
            cartella = Cartella()
            numeri = cartella.get_numeri_cartella()
            cartella.segna_numero(numeri[0])
            risultato = cartella.is_numero_segnato(numeri[0])
            print(risultato)  # Output: True (numero è stato segnato)

        Esempio 3 - Numero con tipo sbagliato:
            cartella = Cartella()
            cartella.is_numero_segnato("45")  # Solleva CartellaNumeroTypeException

        Esempio 4 - Numero fuori range:
            cartella = Cartella()
            cartella.is_numero_segnato(91)  # Solleva CartellaNumeroValueException
        """
        
        # Prima validazione: il tipo deve essere int
        if not isinstance(numero, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaNumeroTypeException(numero)

        # Seconda validazione: il valore deve essere nel range valido (1-90)
        if numero < 1 or numero > 90:
            # Se il numero è fuori range, solleva un'eccezione specifica di valore
            raise CartellaNumeroValueException(numero)

        # Verifica se il numero è nel set dei numeri segnati
        # L'operazione è O(1) grazie ai set Python
        return numero in self.numeri_segnati


    #metodo per resettare lo stato della cartella
    def reset_cartella(self):
        """Resetta lo stato della cartella cancellando i numeri segnati.
        Questo metodo ripristina la cartella al suo stato iniziale dopo la generazione,
        permettendo di ricominciare a giocare sulla stessa cartella senza rigenerarla.
        La matrice della cartella e i numeri rimangono invariati, viene cancellato solo
        il set dei numeri segnati.
        Parametri:
        - Nessuno
        Ritorna:
        - Nulla (modifica self.numeri_segnati impostando un set vuoto)
        Effetti collaterali:
        - Svuota completamente il set self.numeri_segnati
        - Lo stato della cartella ritorna come se fosse appena stata generata
        """

        # Svuota il set dei numeri segnati creando un nuovo set vuoto
        self.numeri_segnati = set()


    """metodi pubblici di interrogazione semplice sulla cartella"""

    #metodo per contare i numeri segnati nella cartella
    def conta_numeri_segnati(self):
        """
            Ritorna il numero totale di numeri segnati nella cartella.
            Questo metodo fornisce un'interrogazione semplice dello stato attuale della cartella,
            indicando quanti dei 15 numeri disponibili sono già stati segnati durante il gioco.
            È utile per tracciare il progresso dell'utente e per determinare quanto manca
            alla vittoria (tombola).
            Ritorna:
            - int: Il numero di numeri segnati (da 0 a 15)
            Comportamento:
            - Ritorna 0 quando la cartella è appena creata o dopo un reset
            - Incrementa di 1 ogni volta che segni un numero con segna_numero()
            - Ritorna 15 quando la cartella è completamente segnata (TOMBOLA!)
            - Non modifica lo stato della cartella
        Complessità temporale: O(1) - accesso diretto alla lunghezza del set
            Esempio:
            cartella = Cartella()
            print(cartella.conta_numeri_segnati())  # Output: 0
            numeri = cartella.get_numeri_cartella()
            cartella.segna_numero(numeri[0])
            cartella.segna_numero(numeri[1])
            cartella.segna_numero(numeri[2])
            print(cartella.conta_numeri_segnati())  # Output: 3
            # Per sapere quanti numeri mancano alla vittoria
            numeri_mancanti = 15 - cartella.conta_numeri_segnati()
            print(f"Numeri ancora da segnare: {numeri_mancanti}")
        """
    
        # Ritorna il numero di elementi nel set dei numeri segnati
        # len() è O(1) perché Python tiene internamente il conto della lunghezza
        return len(self.numeri_segnati)



    #metodo per ottenere i numeri non ancora segnati nella cartella
    def get_numeri_non_segnati(self):
        """
        Ritorna una lista ordinata di tutti i numeri della cartella che non sono stati ancora segnati.
        Questo metodo fornisce il complemento rispetto a get_numeri_cartella(): mentre quello ritorna TUTTI i 15 numeri della cartella, questo ritorna solo quelli che NON sono stati segnati finora.
        È utile per sapere quali numeri rimangono da estrarre e segnare durante il gioco.
        Il metodo utilizza l'operazione di differenza insiemistica tra i set Python per calcolare
        in modo efficiente quali numeri mancano, poi li ritorna come lista ordinata per coerenza
        con altri metodi di interrogazione.
        Ritorna:
        - list: Lista ordinata (crescente) dei numeri non segnati (da 0 a 15 numeri)
        Comportamento:
        - Ritorna una lista di 15 numeri quando la cartella è appena creata (nessuno segnato)
        - Man mano che segni i numeri, la lista si riduce
        - Ritorna una lista vuota quando tutti i 15 numeri sono segnati (TOMBOLA!)
        - La lista è sempre ordinata in modo crescente per coerenza
        - Non modifica lo stato della cartella
        Relazione con altri metodi:
        - conta_numeri_segnati() ritorna quanti numeri sono segnati (0-15)
        - len(get_numeri_non_segnati()) ritorna quanti numeri MANCANO (0-15)
        - conta_numeri_segnati() + len(get_numeri_non_segnati()) = sempre 15
        - Se get_numeri_non_segnati() è vuoto, verifica_cartella_completa() ritorna True
        Complessità temporale: O(n) dove n è la dimensione del set più piccolo (max 15)
        Esempio 1 - Inizio del gioco:
        cartella = Cartella()
        numeri_mancanti = cartella.get_numeri_non_segnati()
        print(len(numeri_mancanti))  # Output: 15 (nessuno è stato segnato)
        print(numeri_mancanti)       # Output: [1, 5, 8, 12, 15, 18, ...]
        Esempio 2 - A metà del gioco:
        cartella = Cartella()
        numeri = cartella.get_numeri_cartella()
        cartella.segna_numero(numeri[0])
        cartella.segna_numero(numeri[1])
        cartella.segna_numero(numeri[2])
        numeri_mancanti = cartella.get_numeri_non_segnati()
        print(len(numeri_mancanti))  # Output: 12 (3 numeri segnati, 12 rimangono)
        Esempio 3 - Verso la vittoria:
        cartella = Cartella()
        numeri = cartella.get_numeri_cartella()
        for numero in numeri[:-1]:  # Segna tutti tranne l'ultimo
            cartella.segna_numero(numero)
        numeri_mancanti = cartella.get_numeri_non_segnati()
        print(len(numeri_mancanti))  # Output: 1 (solo 1 numero rimane alla TOMBOLA!)
        print(numeri_mancanti)       # Output: [numero_finale]
    Esempio 4 - TOMBOLA completata:
        cartella = Cartella()
        numeri = cartella.get_numeri_cartella()
        for numero in numeri:  # Segna TUTTI i numeri
            cartella.segna_numero(numero)
        numeri_mancanti = cartella.get_numeri_non_segnati()
        print(len(numeri_mancanti))  # Output: 0 (lista vuota)
        print(numeri_mancanti)       # Output: []
        if not numeri_mancanti and cartella.verifica_cartella_completa():
            print("TOMBOLA!")
        """

        # Calcola i numeri non segnati usando l'operazione di differenza insiemistica
        # self.numeri_cartella - self.numeri_segnati ritorna un nuovo set con i numeri
        # che sono in numeri_cartella ma NON sono in numeri_segnati
        numeri_non_segnati_set = self.numeri_cartella - self.numeri_segnati
        # Converte il set in una lista e la ordina in modo crescente
        # Questo garantisce coerenza con get_numeri_cartella() che ritorna ordinato
        numeri_non_segnati_lista = sorted(numeri_non_segnati_set)
        # Ritorna la lista ordinata dei numeri non segnati
        return numeri_non_segnati_lista



    #metodo per ottenere la percentuale di completamento della cartella
    def get_percentuale_completamento(self):
        """
        Ritorna la percentuale di cartella completata da 0.0 a 100.0.
        Utile per mostrare il progresso del giocatore verso la TOMBOLA.
        Calcola (numeri segnati / 15) * 100 e ritorna un float.
        Ritorna:
            - float: Percentuale di completamento (0.0 = nessuno segnato, 100.0 = tutti segnati)
        Esempio:
            cartella = Cartella()
            print(cartella.get_percentuale_completamento())  # Output: 0.0
            numeri = cartella.get_numeri_cartella()
            for numero in numeri[:5]:
                cartella.segna_numero(numero)
            print(cartella.get_percentuale_completamento())  # Output: 33.33333...
            for numero in numeri[5:]:
                cartella.segna_numero(numero)
            print(cartella.get_percentuale_completamento())  # Output: 100.0
        """

        # Calcola la percentuale: numeri segnati / totale * 100
        percentuale = (self.conta_numeri_segnati() / self.quantita_numeri) * 100
        # Ritorna il valore float arrotondato a una cifra decimale
        return round(percentuale, 1)



    #metodo per ottenere i numeri presenti in una riga specifica
    def get_numeri_riga(self, numero_riga: int):
        """
        Ritorna una lista ordinata di tutti i numeri presenti in una riga specifica.
        La riga viene estratta dalla matrice cartella, vengono raccolti solo i valori
        non-None e ritornati come lista ordinata crescente.

        Parametri:
            - numero_riga: int (0, 1 o 2) che specifica quale riga interrogare

        Ritorna:
            - list: Lista ordinata dei numeri nella riga (da 1 a 5 numeri)

        Eccezioni:
            - CartellaRigaTypeException: se numero_riga non è un intero (int)
            - CartellaRigaValueException: se numero_riga non è 0, 1 o 2

        Esempio:
            cartella = Cartella()
            numeri_riga_0 = cartella.get_numeri_riga(0)
            print(numeri_riga_0)  # Output: [5, 12, 24, 48, 85]
        """
        
        # Prima validazione: il tipo deve essere int
        if not isinstance(numero_riga, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaRigaTypeException(numero_riga)

        # Seconda validazione: il valore deve essere un indice di riga valido (0, 1, 2)
        # self.righe contiene il numero totale di righe (di solito 3)
        if numero_riga < 0 or numero_riga >= self.righe:
            # Se l'indice è fuori range, solleva un'eccezione specifica di valore
            raise CartellaRigaValueException(numero_riga)

        # Raccoglie i numeri dalla riga specifica
        numeri_riga = []

        # Itera su tutte le colonne della riga
        for indice_colonna in range(self.colonne):
            elemento = self.cartella[numero_riga][indice_colonna]

            # Aggiunge il numero se non è None
            if elemento is not None:
                numeri_riga.append(elemento)
        # Ritorna la lista ordinata
        return sorted(numeri_riga)



    #metodo per ottenere i numeri presenti in una colonna specifica
    def get_numeri_colonna(self, numero_colonna: int):
        """
        Ritorna una lista ordinata di tutti i numeri presenti in una colonna specifica.
        La colonna viene estratta dalla matrice cartella, vengono raccolti solo i valori
        non-None e ritornati come lista ordinata crescente.

        Parametri:
            - numero_colonna: int (0-8) che specifica quale colonna interrogare

        Ritorna:
            - list: Lista ordinata dei numeri nella colonna (da 1 a 3 numeri)

        Eccezioni:
            - CartellaColonnaTypeException: se numero_colonna non è un intero (int)
            - CartellaColonnaValueException: se numero_colonna non è compreso tra 0 e 8

        Esempio:
            cartella = Cartella()
            numeri_colonna_0 = cartella.get_numeri_colonna(0)
            print(numeri_colonna_0)  # Output: [5, 18, 42]
        """

        # Prima validazione: il tipo deve essere int
        if not isinstance(numero_colonna, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaColonnaTypeException(numero_colonna)

        # Seconda validazione: il valore deve essere un indice di colonna valido (0-8)
        if numero_colonna < 0 or numero_colonna >= self.colonne:
            # Se l'indice è fuori range, solleva un'eccezione specifica di valore
            raise CartellaColonnaValueException(numero_colonna)

        # Raccoglie i numeri dalla colonna specifica
        numeri_colonna = []

        # Itera su tutte le righe della colonna
        for indice_riga in range(self.righe):
            elemento = self.cartella[indice_riga][numero_colonna]

            # Aggiunge il numero se non è None
            if elemento is not None:
                numeri_colonna.append(elemento)

        # Ritorna la lista ordinata
        return sorted(numeri_colonna)


    #metodo per ottenere i numeri segnati in una riga specifica
    def get_numeri_segnati_riga(self, numero_riga: int):
        """
        Ritorna una lista ordinata di tutti i numeri segnati presenti in una riga specifica.
        Il metodo estrae i numeri della riga specificata e verifica quale di essi sono stati
        segnati durante il gioco, ritornando solo quelli che hanno lo stato "segnato".

        Parametri:
            - numero_riga: int (0, 1 o 2) che specifica quale riga interrogare

        Ritorna:
            - list: Lista ordinata dei numeri segnati nella riga (da 0 a 5 numeri)

        Eccezioni:
            - CartellaRigaTypeException: se numero_riga non è un intero (int)
            - CartellaRigaValueException: se numero_riga non è 0, 1 o 2

        Esempio:
            cartella = Cartella()
            numeri = cartella.get_numeri_cartella()
            cartella.segna_numero(numeri[0])
            cartella.segna_numero(numeri[1])
            numeri_segnati_riga_0 = cartella.get_numeri_segnati_riga(0)
            print(numeri_segnati_riga_0)  # Output: [5, 24] (i numeri della riga 0 che sono segnati)
        """

        # Prima validazione: il tipo deve essere int
        if not isinstance(numero_riga, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaRigaTypeException(numero_riga)

        # Seconda validazione: il valore deve essere un indice di riga valido (0, 1, 2)
        if numero_riga < 0 or numero_riga >= self.righe:
            # Se l'indice è fuori range, solleva un'eccezione specifica di valore
            raise CartellaRigaValueException(numero_riga)

        # Ottiene tutti i numeri presenti nella riga specificata
        numeri_riga = self.get_numeri_riga(numero_riga)

        # Raccoglie i numeri segnati di questa riga
        numeri_segnati_riga = []

        # Itera su ogni numero trovato nella riga
        for numero in numeri_riga:
            # Verifica se il numero è nel set dei numeri segnati
            if numero in self.numeri_segnati:
                # Aggiunge il numero alla lista dei numeri segnati
                numeri_segnati_riga.append(numero)

        # Ritorna la lista ordinata (già in ordine, ma manteniamo la coerenza)
        return sorted(numeri_segnati_riga)




    #metodo per ottenere i numeri segnati in una colonna specifica
    def get_numeri_segnati_colonna(self, numero_colonna: int):
        """
        Ritorna una lista ordinata di tutti i numeri segnati presenti in una colonna specifica.
        Il metodo estrae i numeri della colonna specificata e verifica quali di essi sono stati
        segnati durante il gioco, ritornando solo quelli che hanno lo stato "segnato".

        Parametri:
            - numero_colonna: int (0, 1, 2, 3, 4, 5, 6, 7, 8) che specifica quale colonna interrogare

        Ritorna:
            - list: Lista ordinata dei numeri segnati nella colonna (da 0 a 3 numeri)

        Eccezioni:
            - CartellaColonnaTypeException: se numero_colonna non è un intero (int)
            - CartellaColonnaValueException: se numero_colonna non è compreso tra 0 e 8

        Esempio:
            cartella = Cartella()
            numeri = cartella.get_numeri_cartella()
            cartella.segna_numero(numeri[0])
            cartella.segna_numero(numeri[1])
            numeri_segnati_colonna_0 = cartella.get_numeri_segnati_colonna(0)
            print(numeri_segnati_colonna_0)  # Output: [5, 7] (i numeri della colonna 0 che sono segnati)
        """

        # Prima validazione: il tipo deve essere int
        if not isinstance(numero_colonna, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaColonnaTypeException(numero_colonna)

        # Seconda validazione: il valore deve essere un indice di colonna valido (0-8)
        if numero_colonna < 0 or numero_colonna >= self.colonne:
            # Se l'indice è fuori range, solleva un'eccezione specifica di valore
            raise CartellaColonnaValueException(numero_colonna)

        # Ottiene tutti i numeri presenti nella colonna specificata
        numeri_colonna = self.get_numeri_colonna(numero_colonna)

        # Raccoglie i numeri segnati di questa colonna
        numeri_segnati_colonna = []

        # Itera su ogni numero trovato nella colonna
        for numero in numeri_colonna:
            # Verifica se il numero è nel set dei numeri segnati
            if numero in self.numeri_segnati:
                # Aggiunge il numero alla lista dei numeri segnati
                numeri_segnati_colonna.append(numero)

        # Ritorna la lista ordinata (già ordinata, ma manteniamo la coerenza)
        return sorted(numeri_segnati_colonna)



    #metodo per ottenere lo stato completo di una riga specifica
    def get_stato_riga(self, numero_riga: int):
        """
        Ritorna un dizionario con informazioni complete sullo stato di una riga specifica.
        Il metodo fornisce una panoramica dettagliata della situazione di una riga durante il gioco,
        includendo i numeri presenti, quanti sono stati segnati, e la percentuale di completamento.

        Parametri:
            - numero_riga: int (0, 1 o 2) che specifica quale riga interrogare

        Ritorna:
            - dict: Dizionario con le seguenti chiavi:
                * numero_riga: int, il numero della riga (0, 1 o 2)
                * numeri_totali: int, il numero totale di numeri in questa riga (sempre 5)
                * numeri_riga: list, lista ordinata di tutti i numeri della riga
                * numeri_segnati: int, il numero di numeri segnati in questa riga
                * numeri_segnati_riga: list, lista ordinata dei numeri segnati in questa riga
                * percentuale_completamento: float, percentuale di riga completata (0.0 a 100.0)

        Eccezioni:
            - CartellaRigaTypeException: se numero_riga non è un intero (int)
            - CartellaRigaValueException: se numero_riga non è 0, 1 o 2

        Esempio:
            cartella = Cartella()
            numeri = cartella.get_numeri_cartella()
            cartella.segna_numero(numeri[0])
            cartella.segna_numero(numeri[1])
            stato = cartella.get_stato_riga(0)
            print(stato)
            # Output: {
            #    'numero_riga': 0,
            #    'numeri_totali': 5,
            #    'numeri_riga': [5, 12, 24, 48, 85],
            #    'numeri_segnati': 2,
            #    'numeri_segnati_riga': [5, 12],
            #    'percentuale_completamento': 40.0
            # }
        """

        # Prima validazione: il tipo deve essere int
        if not isinstance(numero_riga, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaRigaTypeException(numero_riga)

        # Seconda validazione: il valore deve essere un indice di riga valido (0, 1, 2)
        if numero_riga < 0 or numero_riga >= self.righe:
            # Se l'indice è fuori range, solleva un'eccezione specifica di valore
            raise CartellaRigaValueException(numero_riga)

        # Ottiene tutti i numeri della riga
        numeri_riga_lista = self.get_numeri_riga(numero_riga)

        # Ottiene i numeri segnati della riga
        numeri_segnati_riga_lista = self.get_numeri_segnati_riga(numero_riga)

        # Calcola il numero totale di numeri nella riga
        numeri_totali = len(numeri_riga_lista)

        # Calcola il numero di numeri segnati nella riga
        numeri_segnati_conteggio = len(numeri_segnati_riga_lista)

        # Calcola la percentuale di completamento della riga
        if numeri_totali > 0:
            percentuale = (numeri_segnati_conteggio / numeri_totali) * 100
            percentuale = round(percentuale, 1)
        else:
            percentuale = 0.0

        # Crea il dizionario con tutte le informazioni dello stato della riga
        stato_riga = {
            'numero_riga': numero_riga,
            'numeri_totali': numeri_totali,
            'numeri_riga': numeri_riga_lista,
            'numeri_segnati': numeri_segnati_conteggio,
            'numeri_segnati_riga': numeri_segnati_riga_lista,
            'percentuale_completamento': percentuale
        }

        # Ritorna il dizionario con le informazioni complete
        return stato_riga



    #metodo per ottenere lo stato completo della cartella
    def get_stato_cartella(self):
        """
        Ritorna un dizionario con informazioni complete sullo stato globale della cartella.
        Il metodo fornisce una panoramica riepilogativa della situazione attuale della cartella durante il gioco,
        includendo i numeri totali, i segnati, i rimasti, e la percentuale di completamento.
        Parametri:
            - Nessuno (lavora sull'intera cartella)
        Ritorna:
            - dict: Dizionario con le seguenti chiavi:
                * numeri_totali: int, il numero totale di numeri nella cartella (sempre 15)
                * numeri_segnati: int, il numero di numeri segnati finora (da 0 a 15)
                * numeri_non_segnati: int, il numero di numeri rimasti da segnare (da 0 a 15)
                * lista_numeri_cartella: list, lista ordinata di tutti i 15 numeri della cartella
                * lista_numeri_non_segnati: list, lista ordinata dei numeri ancora da segnare
                * percentuale_completamento: float, percentuale globale di completamento (0.0 a 100.0)
        Esempio:
            cartella = Cartella()
            numeri = cartella.get_numeri_cartella()
            cartella.segna_numero(numeri[0])
            cartella.segna_numero(numeri[1])
            cartella.segna_numero(numeri[2])
            stato = cartella.get_stato_cartella()
            print(stato)
            # Output: {
            #    'numeri_totali': 15,
            #    'numeri_segnati': 3,
            #    'numeri_non_segnati': 12,
            #    'lista_numeri_cartella': [5, 12, 24, 48, 85, ...],
            #    'lista_numeri_non_segnati': [8, 15, 18, 22, ...],
            #    'percentuale_completamento': 20.0
            # }
        """
        
        # Ottiene la lista di tutti i numeri della cartella
        numeri_cartella = self.get_numeri_cartella()
        
        # Ottiene il conteggio dei numeri segnati
        numeri_segnati_conteggio = self.conta_numeri_segnati()
        
        # Ottiene la lista dei numeri non segnati
        numeri_non_segnati_lista = self.get_numeri_non_segnati()
        
        # Calcola il numero di numeri rimasti da segnare
        numeri_non_segnati_conteggio = len(numeri_non_segnati_lista)
        
        # Ottiene la percentuale di completamento della cartella
        percentuale = self.get_percentuale_completamento()
        
        # Crea il dizionario con tutte le informazioni globali della cartella
        stato_cartella = {
            'numeri_totali': self.quantita_numeri,
            'numeri_segnati': numeri_segnati_conteggio,
            'numeri_non_segnati': numeri_non_segnati_conteggio,
            'lista_numeri_cartella': numeri_cartella,
            'lista_numeri_non_segnati': numeri_non_segnati_lista,
            'percentuale_completamento': percentuale
        }
        
        # Ritorna il dizionario con tutte le informazioni globali della cartella
        return stato_cartella


    """metodi innerenti alle verifiche di vittoria, ambo, terno, quaterna, cinquina, tombola."""

    #metodo per verificare se una riga ha l'ambo (2 numeri segnati)
    def verifica_ambo_riga(self, numero_riga: int):
        """
        Verifica se una riga contiene almeno 2 numeri segnati (ambo).
        Questo metodo controlla una riga specifica della cartella e conta quanti numeri presenti in quella riga
        sono stati segnati. Se almeno 2 numeri sono segnati, significa che la riga ha un ambo.

        Parametri:
            - numero_riga: int (0, 1 o 2) che specifica quale riga controllare

        Ritorna:
            - bool: True se in quella riga sono segnati almeno 2 numeri, False altrimenti

        Eccezioni:
            - CartellaRigaTypeException: se numero_riga non è un intero (int)
            - CartellaRigaValueException: se numero_riga non è 0, 1 o 2

        Esempio:
            cartella = Cartella()
            cartella.segna_numero(5)
            cartella.segna_numero(24)
            if cartella.verifica_ambo_riga(0):
                print("Ambo sulla riga 0!")
        """

        # Prima validazione: il tipo deve essere int
        if not isinstance(numero_riga, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaRigaTypeException(numero_riga)

        # Seconda validazione: il valore deve essere un indice di riga valido (0, 1, 2)
        if numero_riga < 0 or numero_riga >= self.righe:
            # Se l'indice è fuori range, solleva un'eccezione specifica di valore
            raise CartellaRigaValueException(numero_riga)

        # Crea una lista per contenere i numeri della riga specificata
        numeri_riga = []

        # Itera su tutte le colonne della riga specificata
        for indice_colonna in range(self.colonne):
            # Ottiene l'elemento nella posizione (numero_riga, indice_colonna)
            elemento = self.cartella[numero_riga][indice_colonna]

            # Se l'elemento non è None (cioè è un numero), lo aggiunge alla lista
            if elemento is not None:
                numeri_riga.append(elemento)

        # Conta quanti numeri della riga sono stati segnati
        numeri_segnati_in_riga = 0

        # Itera su ogni numero trovato nella riga
        for numero in numeri_riga:
            # Verifica se il numero è nel set dei numeri segnati
            if numero in self.numeri_segnati:
                # Incrementa il contatore dei numeri segnati
                numeri_segnati_in_riga += 1

        # Ritorna True se sono segnati almeno 2 numeri, False altrimenti
        return numeri_segnati_in_riga >= 2



    #metodo per verificare se una riga ha il terno (3 numeri segnati)
    def verifica_terno_riga(self, numero_riga: int):
        """
        Verifica se una riga contiene almeno 3 numeri segnati (terno).
        Questo metodo controlla una riga specifica della cartella e conta quanti numeri presenti in quella riga
        sono stati segnati. Se almeno 3 numeri sono segnati, significa che la riga ha un terno.

        Parametri:
            - numero_riga: int (0, 1 o 2) che specifica quale riga controllare

        Ritorna:
            - bool: True se in quella riga sono segnati almeno 3 numeri, False altrimenti

        Eccezioni:
            - CartellaRigaTypeException: se numero_riga non è un intero (int)
            - CartellaRigaValueException: se numero_riga non è 0, 1 o 2

        Esempio:
            cartella = Cartella()
            cartella.segna_numero(5)
            cartella.segna_numero(24)
            cartella.segna_numero(53)
            if cartella.verifica_terno_riga(0):
                print("Terno sulla riga 0!")
        """

        # Prima validazione: il tipo deve essere int
        if not isinstance(numero_riga, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaRigaTypeException(numero_riga)

        # Seconda validazione: il valore deve essere un indice di riga valido (0, 1, 2)
        if numero_riga < 0 or numero_riga >= self.righe:
            # Se l'indice è fuori range, solleva un'eccezione specifica di valore
            raise CartellaRigaValueException(numero_riga)

        # Crea una lista per contenere i numeri della riga specificata
        numeri_riga = []

        # Itera su tutte le colonne della riga specificata
        for indice_colonna in range(self.colonne):
            # Ottiene l'elemento nella posizione (numero_riga, indice_colonna)
            elemento = self.cartella[numero_riga][indice_colonna]

            # Se l'elemento non è None (cioè è un numero), lo aggiunge alla lista
            if elemento is not None:
                numeri_riga.append(elemento)

        # Conta quanti numeri della riga sono stati segnati
        numeri_segnati_in_riga = 0

        # Itera su ogni numero trovato nella riga
        for numero in numeri_riga:
            # Verifica se il numero è nel set dei numeri segnati
            if numero in self.numeri_segnati:
                # Incrementa il contatore dei numeri segnati
                numeri_segnati_in_riga += 1

        # Ritorna True se sono segnati almeno 3 numeri, False altrimenti
        return numeri_segnati_in_riga >= 3


    #metodo per verificare se una riga ha la quaterna (4 numeri segnati)
    def verifica_quaterna_riga(self, numero_riga: int):
        """
        Verifica se una riga contiene almeno 4 numeri segnati (quaterna).
        Questo metodo controlla una riga specifica della cartella e conta quanti numeri presenti in quella riga
        sono stati segnati. Se almeno 4 numeri sono segnati, significa che la riga ha una quaterna.

        Parametri:
            - numero_riga: int (0, 1 o 2) che specifica quale riga controllare

        Ritorna:
            - bool: True se in quella riga sono segnati almeno 4 numeri, False altrimenti

        Eccezioni:
            - CartellaRigaTypeException: se numero_riga non è un intero (int)
            - CartellaRigaValueException: se numero_riga non è 0, 1 o 2

        Esempio:
            cartella = Cartella()
            cartella.segna_numero(5)
            cartella.segna_numero(24)
            cartella.segna_numero(53)
            cartella.segna_numero(78)
            if cartella.verifica_quaterna_riga(0):
                print("Quaterna sulla riga 0!")
        """

        # Prima validazione: il tipo deve essere int
        if not isinstance(numero_riga, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaRigaTypeException(numero_riga)

        # Seconda validazione: il valore deve essere un indice di riga valido (0, 1, 2)
        if numero_riga < 0 or numero_riga >= self.righe:
            # Se l'indice è fuori range, solleva un'eccezione specifica di valore
            raise CartellaRigaValueException(numero_riga)

        # Crea una lista per contenere i numeri della riga specificata
        numeri_riga = []

        # Itera su tutte le colonne della riga specificata
        for indice_colonna in range(self.colonne):
            # Ottiene l'elemento nella posizione (numero_riga, indice_colonna)
            elemento = self.cartella[numero_riga][indice_colonna]

            # Se l'elemento non è None (cioè è un numero), lo aggiunge alla lista
            if elemento is not None:
                numeri_riga.append(elemento)

        # Conta quanti numeri della riga sono stati segnati
        numeri_segnati_in_riga = 0

        # Itera su ogni numero trovato nella riga
        for numero in numeri_riga:
            # Verifica se il numero è nel set dei numeri segnati
            if numero in self.numeri_segnati:
                # Incrementa il contatore dei numeri segnati
                numeri_segnati_in_riga += 1

        # Ritorna True se sono segnati almeno 4 numeri, False altrimenti
        return numeri_segnati_in_riga >= 4


    #metodo per verificare se una riga ha la cinquina (5 numeri segnati)
    def verifica_cinquina_riga(self, numero_riga: int):
        """
        Verifica se una riga contiene 5 numeri segnati (cinquina).
        Questo metodo controlla una riga specifica della cartella e conta quanti numeri presenti in quella riga
        sono stati segnati. Se sono stati segnati tutti e 5 i numeri della riga, significa che la riga ha una cinquina.

        Parametri:
            - numero_riga: int (0, 1 o 2) che specifica quale riga controllare

        Ritorna:
            - bool: True se in quella riga sono segnati 5 numeri, False altrimenti

        Eccezioni:
            - CartellaRigaTypeException: se numero_riga non è un intero (int)
            - CartellaRigaValueException: se numero_riga non è 0, 1 o 2

        Esempio:
            cartella = Cartella()
            cartella.segna_numero(5)
            cartella.segna_numero(24)
            cartella.segna_numero(53)
            cartella.segna_numero(78)
            cartella.segna_numero(85)
            if cartella.verifica_cinquina_riga(0):
                print("Cinquina sulla riga 0!")
        """

        # Prima validazione: il tipo deve essere int
        if not isinstance(numero_riga, int):
            # Se il tipo non è intero, solleva un'eccezione specifica di tipo
            raise CartellaRigaTypeException(numero_riga)

        # Seconda validazione: il valore deve essere un indice di riga valido (0, 1, 2)
        if numero_riga < 0 or numero_riga >= self.righe:
            # Se l'indice è fuori range, solleva un'eccezione specifica di valore
            raise CartellaRigaValueException(numero_riga)

        # Crea una lista per contenere i numeri della riga specificata
        numeri_riga = []

        # Itera su tutte le colonne della riga specificata
        for indice_colonna in range(self.colonne):
            # Ottiene l'elemento nella posizione (numero_riga, indice_colonna)
            elemento = self.cartella[numero_riga][indice_colonna]

            # Se l'elemento non è None (cioè è un numero), lo aggiunge alla lista
            if elemento is not None:
                numeri_riga.append(elemento)

        # Conta quanti numeri della riga sono stati segnati
        numeri_segnati_in_riga = 0

        # Itera su ogni numero trovato nella riga
        for numero in numeri_riga:
            # Verifica se il numero è nel set dei numeri segnati
            if numero in self.numeri_segnati:
                # Incrementa il contatore dei numeri segnati
                numeri_segnati_in_riga += 1

        # Ritorna True se sono segnati 5 numeri, False altrimenti
        return numeri_segnati_in_riga >= 5


    #metodo per verificare se la cartella è completamente segnata (tombola)
    def verifica_cartella_completa(self):
        """
            Verifica se TUTTI i 15 numeri della cartella sono stati segnati (TOMBOOLA!).
            Questo metodo controlla se il numero di numeri segnati è uguale al totale dei numeri presenti nella cartella (15). È la vittoria massima della tombola!
            Ritorna:
            - True se tutti i 15 numeri sono segnati (TOMBOOLA!)
            - False altrimenti
            Esempio:
            cartella = Cartella()
            # ... segna tutti i 15 numeri uno alla volta ...
            if cartella.verifica_cartella_completa():
                print("🎉🎉🎉 TOMBOLA! 🎉🎉🎉")
        """
        # Verifica se il numero di numeri segnati è uguale al totale dei numeri della cartella
        return len(self.numeri_segnati) == self.quantita_numeri



