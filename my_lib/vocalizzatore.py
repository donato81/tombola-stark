"""
    Modulo per la vocalizzazione di messaggi utilizzando Accessible Output 2 (AO2).
    path: my_lib/vocalizzatore.py
"""

#import della libreria Accessible Output 2
from accessible_output2.outputs.auto import Auto



class Vocalizzatore:
    def __init__(self):
        # Crea un'istanza dell'output automatico di AO2
        self.speaker = Auto()

    def vocalizza_testo(self, testo: str):
        """Vocalizza un testo generico."""
        self.speaker.speak(testo)

    def vocalizza_numero(self, numero: int):
        """Vocalizza un numero, ad esempio il numero estratto."""
        # Formatta il numero come stringa prima di vocalizzarlo
        testo = f"Numero estratto: {numero}"
        self.speaker.speak(testo)

    def vocalizza_errore(self, messaggio: str):
        """Vocalizza messaggi di errore o avviso."""
        testo = f"Attenzione, errore: {messaggio}"
        self.speaker.speak(testo)



    """metodi di vocalizzazione riguardanti la classe tabellone del gioco del bingo."""

    #metodo per vocalizzare il messaggio di inizializzazione del tabellone
    def messaggio_inizializzazione(self):
        #richiama il metodo per vocalizzare il testo passando il messaggio di inizializzazione
        self.vocalizza_testo("Inizializzazione del tabellone.")


    #metodo per vocalizzare il messaggio di errore numeri terminati
    def messaggio_errore_numeri_terminati(self):
        #richiama il metodo per vocalizzare il testo passando il messaggio di errore numeri terminati
        self.vocalizza_errore("Tutti i numeri sono stati estratti.")


    #metodo per vocalizzare il numero estratto
    def messaggio_numero_estratto(self, numero: int):
        #richiama il metodo per vocalizzare il numero estratto passando il numero
        self.vocalizza_numero(numero)


    #metodo per vocalizzare il messaggio di reset del tabellone
    def messaggio_reset_tabellone(self):
        #richiama il metodo per vocalizzare il testo passando il messaggio di reset del tabellone
        self.vocalizza_testo("Reset del tabellone.")


    #metodo di formattazione per la vocalizzazione che riceve il paramentro numeri sotto forma di numeri interi e li ritorna come stringa separati da .
    def _formatta_numeri_per_vocalizzazione(self, numeri: list[int]) -> str:
        #Crea una stringa con i numeri separati da pause vocali, usando la parola 'numero' prima di ogni cifra, e una pausa più lunga rappresentata da un punto e virgola.
        # Trasforma ogni numero in "numero X"
        numeri_formattati = [f"numero {n}" for n in numeri]
        # Unisce con un punto e virgola e spazio, che genera pausa più lunga
        return '; '.join(numeri_formattati)



    #metodo per vocalizzare la lista dei numeri estratti
    def vocalizza_numeri_estratti(self, numeri: list[int]):
        #verifica se la lista dei numeri è vuota
        if not numeri:
            # Se la lista è vuota, vocalizza un messaggio appropriato
            self.vocalizza_testo("Nessun numero è stato estratto.")
            #termina la funzione
            return
        #altrimenti formatta la lista dei numeri per la vocalizzazione
        testo = "Numeri estratti: " + self._formatta_numeri_per_vocalizzazione(numeri)
        #richiama il metodo per vocalizzare il testo passando la lista dei numeri estratti formattata
        self.vocalizza_testo(testo)


    #metodo per vocalizzare la lista dei numeri disponibili
    def vocalizza_numeri_disponibili(self, numeri: list[int]):
        #verifica se la lista dei numeri è vuota
        if not numeri:
            # Se la lista è vuota, vocalizza un messaggio appropriato
            self.vocalizza_testo("Non ci sono numeri disponibili.")
            #termina la funzione
            return
        #altrimenti formatta la lista dei numeri per la vocalizzazione
        testo = "Numeri disponibili: " + self._formatta_numeri_per_vocalizzazione(numeri)
        #richiama il metodo per vocalizzare il testo passando la lista dei numeri disponibili formattata
        self.vocalizza_testo(testo)

