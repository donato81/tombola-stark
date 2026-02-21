from __future__ import annotations

from typing import Optional

#import metodi di progetto 
from bingo_game.players.helper_focus import GestioneFocusMixin
from bingo_game.players.helper_reclami_focus import ReclamiFocusMixin
from bingo_game.players.giocatore_base import GiocatoreBase

#inport delle validazioni necessarie al modulo 
from bingo_game.validations.validazione_oggetti import (
    esito_tabellone_disponibile,
    esito_coordinate_numero_coerenti
)
from bingo_game.validations.validazioni_input import (
    esito_numero_intero,
    esito_numero_in_range_1_90,
    esito_numero_riga_in_range_1_3,
    esito_numero_colonna_in_range_1_9,
    esito_reclamo_turno_libero,
    esito_tipo_vittoria_supportato,
)

#inport degli eventi necessari 
from bingo_game.events.eventi import EsitoAzione
from bingo_game.events.eventi_ui import (
    EventoFocusAutoImpostato,
    EventoFocusCartellaImpostato,
)
from bingo_game.events.eventi_output_ui_umani import (
    EventoRiepilogoCartellaCorrente,
    EventoLimiteNavigazioneCartelle,
    EventoVisualizzaCartellaSemplice,
    EventoVisualizzaCartellaAvanzata,
    EventoVisualizzaTutteCartelleSemplice,
    EventoVisualizzaTutteCartelleAvanzata,
    EventoNavigazioneRiga,
    EventoNavigazioneRigaAvanzata,
    EventoNavigazioneColonna,
    EventoNavigazioneColonnaAvanzata,
    EventoSegnazioneNumero,
    RisultatoRicercaNumeroInCartella,
    EventoRicercaNumeroInCartelle,
    EventoVerificaNumeroEstratto,
    EventoUltimoNumeroEstratto,
    EventoUltimiNumeriEstratti,
    EventoRiepilogoTabellone,
    EventoListaNumeriEstratti,
    EventoStatoFocusCorrente,
    EventoVaiARigaAvanzata,
    EventoVaiAColonnaAvanzata,
)
from bingo_game.events.eventi_partita import (
    Tipo_Vittoria,
    ReclamoVittoria,
    EventoReclamoVittoria,
    EventoFineTurno,
)

#definizione della classe giocatore umano che eredita dal giocatore base
class GiocatoreUmano(GestioneFocusMixin, ReclamiFocusMixin, GiocatoreBase):
    """
    Classe concreta che rappresenta un giocatore umano.

    Eredita tutta la logica di base da GiocatoreBase (gestione di nome,
    id_giocatore, cartelle, aggiornamento con i numeri estratti e metodi
    di stato complessivo). In futuro potrà essere estesa con metodi
    specifici per l'interazione con l'utente.
    """

    #metodo 0: costruttore della classe giocatore umano
    def __init__(self, nome: str = "Giocatore umano", id_giocatore: Optional[int] = None) -> None:
        """
        Inizializza un giocatore umano.

        Parametri:
        - nome: str
        Nome descrittivo del giocatore umano. Ha un valore di default
        per facilitare la creazione di giocatori senza dover sempre
        specificare il nome esplicitamente.
        - id_giocatore: Optional[int]
        Identificativo numerico opzionale del giocatore (es. indice
        interno alla partita).

        La validazione dei parametri (tipo e valore) è gestita dal
        costruttore di GiocatoreBase.
        """
        super().__init__(nome=nome, id_giocatore=id_giocatore)
        # Indice della cartella attualmente 'sotto osservazione' (focus).
        # Inizia da None, deve essere l'utente a selezionarla.
        self._indice_cartella_focus: Optional[int] = None
        #indice focus per la riga
        self._indice_riga_focus: Optional[int] = None
        #indice interno per colonna
        self._indice_colonna_focus: Optional[int] = None
        # contenitore per il reclamo da passare a fine turno con le vittorie se sono state chiamate.
        self.reclamo_turno: Optional[ReclamoVittoria] = None


    #metodi pubblici della classe giocatore umano

    #sezione 1: metodi di impostazione del focus 

    #metodo 1: imposta il focus della cartella
    def imposta_focus_cartella(self, numero_cartella: int) -> EsitoAzione:
        """
        Imposta il focus su una specifica cartella del giocatore (scelta esplicita dell'utente).

        Obiettivo di stabilità:
        - Validare input e prerequisiti con codici errore standardizzati (no stringhe libere).
        - Riutilizzare gli helper centralizzati (evita doppioni e divergenze future).
        - Restituire sempre EsitoAzione tramite factory methods (successo/fallimento).

        Convenzioni:
        - numero_cartella è 1-based (input "umano": 1..N).
        - _indice_cartella_focus è 0-based (indice interno: 0..N-1).
        - Se cambia cartella, vengono resettati i focus di riga e colonna per non trascinare selezioni
        della cartella precedente.

        Ritorna:
        - EsitoAzione.fallimento(...) con errore:
        - "NUMERO_CARTELLA_TIPO_NON_VALIDO" se numero_cartella non è int.
        - "CARTELLE_NESSUNA_ASSEGNATA" se il giocatore non ha cartelle.
        - "NUMERO_CARTELLA_FUORI_RANGE" se numero_cartella non è tra 1 e N.
        - EsitoAzione.successo(...) con evento=EventoFocusCartellaImpostato(...) se il focus viene impostato.
        """

        # 0) Validazione del tipo: evita confronti < e > con tipi non numerici (stabilità runtime).
        if type(numero_cartella) is not int:
            return EsitoAzione.fallimento(errore="NUMERO_CARTELLA_TIPO_NON_VALIDO")

        # 1) Prerequisito: devono esistere cartelle assegnate.
        #    Riutilizziamo l'helper centralizzato, così il codice errore resta uniforme nel progetto.
        esito_cartelle = self._esito_ha_cartelle()
        if not esito_cartelle.ok:
            return esito_cartelle

        num_cartelle_totali = len(self.cartelle)

        # 2) Validazione intervallo: input umano 1..N.
        if numero_cartella < 1 or numero_cartella > num_cartelle_totali:
            return EsitoAzione.fallimento(errore="NUMERO_CARTELLA_FUORI_RANGE")

        # 3) Conversione da numero "umano" (1..N) a indice interno (0..N-1).
        nuovo_indice = numero_cartella - 1

        # 4) Se cambia cartella, resetto riga/colonna (evita stati incoerenti tra cartelle).
        reset_riga_colonna = (self._indice_cartella_focus != nuovo_indice)
        if reset_riga_colonna:
            self._reset_focus_riga_e_colonna()

        # 5) Aggiornamento stato: focus cartella interno.
        self._indice_cartella_focus = nuovo_indice

        # 6) Successo: evento per UI/screen reader, senza testo incorporato.
        return EsitoAzione.successo(
            evento=EventoFocusCartellaImpostato(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                numero_cartella=numero_cartella,
                indice_cartella=nuovo_indice,
                reset_riga_colonna=reset_riga_colonna,
            )
        )


    #metodo 2 ...
    def riepilogo_cartella_corrente(self) -> EsitoAzione:
        """
        Produce un riepilogo della cartella attualmente in focus, in forma di evento (dati),
        senza costruire stringhe pronte per la UI.

        Obiettivo:
        - Separare logica (calcoli e controlli) da presentazione (testo per screen reader).
        - Restituire un EsitoAzione standardizzato, che la UI potrà convertire in stringhe
        tramite il renderer e il contenitore lingua (es. it.py).

        Comportamento:
        - Se il giocatore non ha cartelle o il focus cartella non è utilizzabile, ritorna
        EsitoAzione(ok=False, errore=...) propagando i codici errore del mixin.
        - il focus cartella è None di default, il metodo non abilita autoimpostazione che deve essere effettuato da utente.
        - Non modifica i focus di riga e colonna (comando di sola lettura).

        Ritorna:
        - EsitoAzione:
            - ok=False con errore valorizzato (evento=None) se non è possibile procedere.
            - ok=True con evento=EventoRiepilogoCartellaCorrente(...) se il riepilogo è disponibile.

        Nota:
        - L'eventuale evento di auto-focus generato dagli helper (EventoFocusAutoImpostato)
        non viene propagato qui, perché EsitoAzione attualmente trasporta un singolo evento;
        l'evento principale di questo comando è il riepilogo della cartella.
        """
        # 1) Verifica prerequisiti e focus cartella in modo centralizzato e standardizzato.
        #    autoimposta=True permette di selezionare automaticamente la prima cartella
        #    se il focus non è ancora stato impostato.
        esito_focus = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_focus.ok:
            return esito_focus

        # 2) Recupera la cartella attualmente in focus (ora è sicuro farlo).
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]

        # 3) Calcola i dati "neutri" necessari al renderer (niente testo qui).
        numeri_segnati = cartella_in_focus.conta_numeri_segnati()
        numeri_non_segnati = cartella_in_focus.get_numeri_non_segnati()
        totale_numeri = cartella_in_focus.quantita_numeri
        percentuale = cartella_in_focus.get_percentuale_completamento()

        # 4) Crea l'evento di output usando il factory method, così:
        #    - numero_cartella (1-based) viene calcolato in modo uniforme,
        #    - numeri_non_segnati viene ordinato in modo garantito,
        #    - mancanti viene derivato dalla lista senza duplicare logica.
        evento = EventoRiepilogoCartellaCorrente.crea_da_cartella(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            indice_cartella=self._indice_cartella_focus,
            numeri_segnati=numeri_segnati,
            totale_numeri=totale_numeri,
            percentuale=percentuale,
            numeri_non_segnati=numeri_non_segnati,
        )

        # 5) Successo: ritorniamo l'esito con l'evento (nessuna stringa prodotta qui).
        return EsitoAzione(ok=True, errore=None, evento=evento)


    #metodo 3 ...
    def riepilogo_cartella_precedente(self) -> EsitoAzione:
        """
        Sposta il focus alla cartella precedente e ritorna un esito standardizzato.

        Obiettivo:
        - Rendere la navigazione coerente con l'architettura "no stringhe nel dominio":
        il metodo non costruisce testo, ma produce EsitoAzione + evento.
        - Ridurre la verbosità: se si è già sulla prima cartella, non ristampa il riepilogo,
        ma genera un evento di limite (1 riga nel renderer).

        Comportamento:
        - Se non ci sono cartelle o il focus non è determinabile, ritorna EsitoAzione(ok=False, errore=...).
        - Se il focus cartella è None e autoimposta=True:
            - il focus viene impostato su 0 (prima cartella) dagli helper;
            - il metodo ritorna direttamente riepilogo_cartella_corrente() (nessun messaggio di limite).
        - Se il focus è già sulla prima cartella (indice 0):
            - non sposta il focus;
            - ritorna EsitoAzione(ok=True) con EventoLimiteNavigazioneCartelle (limite minimo).
        - Altrimenti:
            - decrementa il focus di 1;
            - resetta focus riga/colonna;
            - ritorna riepilogo_cartella_corrente().

        Ritorna:
        - EsitoAzione: con evento di riepilogo o evento di limite, oppure con errore standardizzato.
        """
        focus_era_none = (self._indice_cartella_focus is None)

        # 1) Verifica cartelle + focus cartella valido (auto-imposta su 0 se None).
        esito_focus = self._esito_focus_cartella_valido(auto_imposta=True)
        if not esito_focus.ok:
            return esito_focus

        # 2) Se il focus era None, gli helper potrebbero averlo appena auto-impostato.
        #    In questo caso non applichiamo alcun messaggio di limite: restituiamo direttamente il riepilogo.
        if focus_era_none:
            return self.riepilogo_cartella_corrente()

        # 3) Da qui in poi: focus esiste ed è coerente.
        totale_cartelle = len(self.cartelle)

        # 4) Limite minimo: se siamo già sulla prima cartella, non possiamo andare indietro.
        if self._indice_cartella_focus == 0:
            evento = EventoLimiteNavigazioneCartelle.limite_minimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                direzione="precedente",
                totale_cartelle=totale_cartelle,
            )
            return EsitoAzione(ok=True, errore=None, evento=evento)

        # 5) Sposta focus alla cartella precedente.
        self._indice_cartella_focus -= 1

        # 6) Reset focus riga/colonna per evitare stati trascinati tra cartelle.
        self._reset_focus_riga_e_colonna()

        # 7) Ritorna il riepilogo della cartella ora in focus.
        return self.riepilogo_cartella_corrente()


    #metodo 4 ...
    def riepilogo_cartella_successiva(self) -> EsitoAzione:
        """
        Sposta il focus alla cartella successiva e ritorna un esito standardizzato con evento (dati), senza costruire stringhe pronte per la UI.

        Obiettivo:
            - Consentire la navigazione “in avanti” tra le cartelle in modo fluido (utile con screen reader).
            - Mantenere separata la logica di gioco dalla presentazione: qui si producono eventi, il renderer li trasforma in testo.

        Comportamento:
            - Verifica in modo centralizzato che:
                - esistano cartelle,
                - il focus cartella sia valido (indice nel range),
                - se il focus è None e auto-imposta è abilitato, venga impostato automaticamente alla prima cartella (indice 0).
                - Se il focus era None ed è stato auto-impostato:
                    - ritorna direttamente riepilogo_cartella_corrente() (nessun evento di limite).
                - Se il focus è già sull’ultima cartella:
                    - non sposta il focus;
                    - ritorna EsitoAzione(ok=True, evento=EventoLimiteNavigazioneCartelle.limite_massimo(...)).
                - Altrimenti:
                    - incrementa il focus di 1;
                    - resetta i focus interni di riga e colonna;
                    - ritorna riepilogo_cartella_corrente().

        - Ritorna:
            - EsitoAzione:
                - ok=False con errore valorizzato (evento=None) se non è possibile determinare un focus valido;
                - ok=True con evento di limite (massimo) oppure con evento di riepilogo (prodotto da riepilogo_cartella_corrente()).
        """

        focus_era_none = (self._indice_cartella_focus is None)

        # 1: Verifica cartelle + focus + range (auto-imposta il focus a 0 se è None).
        esito = self._esito_focus_cartella_valido(auto_imposta=True)
        if not esito.ok:
            return esito

        # 2: Se il focus era None ed è stato auto-impostato a 0, niente autolimite: solo riepilogo.
        if focus_era_none:
            return self.riepilogo_cartella_corrente()

        # 3) Da qui in poi il focus è certamente impostato: calcoliamo N per il messaggio "N di N".
        totale_cartelle = len(self.cartelle)
        ultimo_indice = totale_cartelle - 1

        # 4) Autolimite: se siamo già sull'ultima cartella, non possiamo andare oltre.
        if self._indice_cartella_focus == ultimo_indice:
            evento = EventoLimiteNavigazioneCartelle.limite_massimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                direzione="successiva",
                totale_cartelle=totale_cartelle,
            )
            return EsitoAzione(ok=True, errore=None, evento=evento)

        # 5) Sposta il focus alla cartella successiva.
        self._indice_cartella_focus += 1

        # 6) Reset dei focus interni per evitare di trascinare riga/colonna tra cartelle.
        self._reset_focus_riga_e_colonna()

        # 7) Ritorna il riepilogo della cartella ora in focus (2 righe).
        return self.riepilogo_cartella_corrente()


    #Sezione 2: metodi per la visualizzazione delle cartelle e lo scorrimento 

    #metodo 5 ...
    def visualizza_cartella_corrente_semplice(self) -> EsitoAzione:
        """
        Comando di visualizzazione "semplice" della cartella attualmente in focus.

        Obiettivo:
        - Rendere la cartella corrente leggibile senza produrre testo pronto per l'utente.
        - Mantenere separata la logica di gioco (dati) dalla presentazione (renderer).
        - Uniformare il contratto di uscita con gli altri comandi di consultazione.

        Comportamento:
        - Verifica centralizzata del focus cartella (auto_imposta=False, come da design).
        - Se il focus non è valido: ritorna EsitoAzione(ok=False) con codice errore standard.
        - Se il focus è valido:
            1) Recupera la cartella in focus.
            2) Estrae i dati grezzi della griglia (numeri o "-").
            3) Crea l'evento dedicato tramite factory method.
            4) Ritorna EsitoAzione(ok=True) con l'evento pronto per il renderer.

        Ritorna:
        - EsitoAzione:
            * ok=False, errore=CODICE_FOCUS_INVALIDO (evento=None) se non si può procedere.
            * ok=True, errore=None, evento=EventoVisualizzaCartellaSemplice se visualizzazione disponibile.

        Nota:
        - Questo comando è di sola lettura: non modifica focus riga/colonna né stato della cartella.
        - La griglia semplice contiene solo numeri (int) e "-" (vuoto), senza indicatori di segnazione.
        """
        # 1) Guard-rail centralizzato: verifica che esista una cartella valida in focus.
        #    auto_imposta=False: non imposta focus automaticamente (comando di consultazione pura).
        esito_focus = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_focus.ok:
            # Propagazione errore standard: coerente con gli altri comandi di navigazione.
            return esito_focus

        # 2) Accesso sicuro alla cartella: l'helper ha garantito che _indice_cartella_focus è valido.
        cartella_corrente = self.cartelle[self._indice_cartella_focus]

        # 3) Estrae i dati grezzi della griglia dalla cartella (3x9: int o "-").
        #    Nessuna stringa qui: solo dati neutri per l'evento.
        griglia_semplice = cartella_corrente.get_griglia_semplice()

        # 4) Costruisce l'evento tramite factory method: centralizza la logica di metadati.
        #    - indice_cartella: interno (0-based)
        #    - totale_cartelle: contesto del giocatore
        #    - griglia_semplice: dati dalla cartella (già immutabile)
        evento = EventoVisualizzaCartellaSemplice.crea_da_cartella(
            indice_cartella=self._indice_cartella_focus,
            totale_cartelle=len(self.cartelle),
            griglia_semplice=griglia_semplice,
        )

        # 5) Successo: ritorna l'esito standard con evento pronto per il renderer.
        #    Il renderer userà MESSAGGI_OUTPUT_UI_UMANI per trasformare i dati in testo.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #metodo 6 ...
    def visualizza_cartella_corrente_avanzata(self) -> EsitoAzione:
        """
        Comando di visualizzazione AVANZATA della cartella attualmente in focus.

        Obiettivo:
        - Mostrare griglia completa con stato segnati (asterischi) + riepiloghi per riga + totale.
        - Mantenere separata logica (dati grezzi) da presentazione (renderer + dizionario).
        - Uniformare con visualizza_cartella_corrente_semplice() (stesso contratto).

        Comportamento:
        - Verifica focus cartella (auto_imposta=False, consultazione pura).
        - Se focus non valido: EsitoAzione(ok=False) con errore standard.
        - Se focus valido:
            1) Recupera cartella in focus.
            2) Estrae pacchetto dati avanzati (griglia + stato + segnati).
            3) Crea evento tramite factory method.
            4) Ritorna EsitoAzione(ok=True) con evento per renderer.

        Ritorna:
        - EsitoAzione:
            * ok=False, errore=CODICE_FOCUS_INVALIDO se focus non valido.
            * ok=True, evento=EventoVisualizzaCartellaAvanzata se disponibile.

        Nota:
        - Comando di sola lettura: non modifica focus riga/colonna né stato cartella.
        - Renderer userà dati per: asterischi (*), "Segnati: ..." per riga, footer totale.
        """
        # 1) Guard-rail standard: verifica cartella in focus valida.
        #    auto_imposta=False: consultazione pura, non modifica stato.
        esito_focus = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_focus.ok:
            # Propaga errore standard: coerente con tutti i comandi di consultazione.
            return esito_focus

        # 2) Accesso sicuro: helper ha garantito che _indice_cartella_focus è valido.
        cartella_corrente = self.cartelle[self._indice_cartella_focus]

        # 3) Estrae il pacchetto completo dati avanzati dalla cartella.
        #    Contiene: griglia 3x9 + stato numerico + segnati ordinati.
        dati_avanzati = cartella_corrente.get_dati_visualizzazione_avanzata()

        # 4) Costruisce l'evento tramite factory: centralizza metadati giocatore.
        evento = EventoVisualizzaCartellaAvanzata.crea_da_dati_avanzati(
            indice_cartella=self._indice_cartella_focus,
            totale_cartelle=len(self.cartelle),
            dati_avanzati=dati_avanzati,  # Pacchetto completo e immutabile
        )

        # 5) Successo: esito standard con evento pronto per il renderer.
        #    Renderer produrrà: griglia con asterischi + "Segnati: ..." + footer totale.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #metodo 7 ...
    def visualizza_tutte_cartelle_semplice(self) -> EsitoAzione:
        """
        Comando di visualizzazione "semplice" di TUTTE le cartelle possedute dal giocatore.

        Obiettivo:
        - Fornire al renderer una panoramica completa di tutte le cartelle del giocatore
        in modalità "semplice", senza produrre testo pronto in questa fase.
        - Mantenere separata la logica di gioco (dati/eventi) dalla presentazione (renderer).
        - Uniformare l'uscita con gli altri comandi di consultazione: ritorna sempre EsitoAzione.

        Comportamento:
        - Esegue il controllo centralizzato "ha cartelle?" tramite l'helper dedicato.
        Se il controllo fallisce:
            * Propaga l'EsitoAzione di errore (ok=False) così com'è.
            * Non costruisce alcun evento.
        - Se il giocatore ha cartelle:
            1) Usa la factory dell'evento per trasformare tutte le cartelle in griglie semplici.
            2) Ritorna EsitoAzione(ok=True) con evento=EventoVisualizzaTutteCartelleSemplice.

        Ritorna:
        - EsitoAzione:
            * ok=False con errore già impostato dall'helper (evento=None) se non si può procedere.
            * ok=True, errore=None, evento=EventoVisualizzaTutteCartelleSemplice se disponibile.

        Nota:
        - Comando di sola lettura: non modifica focus né stato delle cartelle.
        - Il renderer userà MESSAGGI_OUTPUT_UI_UMANI per trasformare i dati dell'evento in testo.
        """
        # 1) Guard-rail centralizzato: se il giocatore non ha cartelle, l'helper
        #    ritorna un EsitoAzione di errore già completo (codice/ok coerenti col progetto).
        esito_cartelle = self._esito_ha_cartelle()
        if not esito_cartelle.ok:
            return esito_cartelle

        # 2) Costruzione evento "ricco di dati": nessuna stringa, solo dati grezzi e immutabili.
        evento = EventoVisualizzaTutteCartelleSemplice.crea_da_cartelle(
            cartelle=self.cartelle,
        )

        # 3) Successo: l'evento è pronto per essere trasformato in righe dal renderer.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #metodo 8 ...
    def visualizza_tutte_cartelle_avanzata(self) -> EsitoAzione:
        """
        Comando di visualizzazione "AVANZATA" di TUTTE le cartelle possedute dal giocatore.

        Obiettivo:
        - Fornire al renderer tutti i dati necessari per stampare l'output avanzato
        di tutte le cartelle (intestazioni, righe con stato, riepiloghi), senza
        costruire testo qui dentro.
        - Mantenere separata la logica di gioco (eventi/dati) dalla presentazione
        (renderer + dizionario lingua).
        - Uniformare il contratto con gli altri comandi di consultazione: ritorna
        sempre EsitoAzione.

        Comportamento:
        - Esegue il controllo centralizzato "ha cartelle?".
        Se il controllo fallisce:
            * Propaga l'EsitoAzione di errore così com'è.
            * Non costruisce alcun evento.
        - Se il giocatore ha cartelle:
            1) Estrae per ogni cartella i dati avanzati tramite API della Cartella
            (griglia semplice, stato normalizzato, segnati ordinati).
            2) Crea l'evento bulk EventoVisualizzaTutteCartelleAvanzata via factory method.
            3) Ritorna EsitoAzione(ok=True) con l'evento pronto per il renderer.

        Ritorna:
        - EsitoAzione:
            * ok=False con errore già impostato dall'helper (evento=None) se non si può procedere.
            * ok=True, errore=None, evento=EventoVisualizzaTutteCartelleAvanzata se disponibile.

        Nota:
        - Questo comando è di sola lettura: non modifica focus né stato del giocatore.
        - Il renderer userà MESSAGGI_OUTPUT_UI_UMANI per trasformare l'evento in righe testuali.
        """
        # 1) Guard-rail centralizzato: se non ho cartelle, l'helper decide il codice errore.
        #    Qui ci limitiamo a propagare l'esito, senza aggiungere logica.
        esito_cartelle = self._esito_ha_cartelle()
        if not esito_cartelle.ok:
            return esito_cartelle

        # 2) Costruzione dell'evento "ricco di dati": nessuna stringa, solo payload strutturato.
        #    La factory centralizza:
        #    - numerazione 1-based delle cartelle
        #    - estrazione uniforme dei dati avanzati da ogni cartella
        evento = EventoVisualizzaTutteCartelleAvanzata.crea_da_cartelle(
            cartelle=self.cartelle,
        )

        # 3) Successo: ritorna l'esito standard con evento pronto per il renderer.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #Sezione 3: Metodi dedicati allo spostamento del focus di riga

    # metodo 9 ...
    def sposta_focus_riga_su_semplice(self) -> EsitoAzione:
        """
        Comando di navigazione: sposta il focus riga verso l'alto (riga precedente)
        sulla cartella attualmente in focus.

        Obiettivo:
        - Non produrre stringhe pronte: ritorna un evento (EventoNavigazioneRiga) dentro EsitoAzione.
        - Il renderer userà l'evento + dizionario lingua per mostrare:
          * la riga in formato semplice (esito="mostra")
          * un feedback breve di limite (esito="limite", limite="minimo")

        Comportamento:
        - Verifica pre-condizione di navigazione con _esito_pronto_per_navigazione().
          Se fallisce: propaga l'errore (ok=False) e non crea eventi.
        - Se il focus riga è None:
          * inizializza la riga (tipicamente a 0) tramite helper
          * mostra la riga 0 senza attivare l'autolimite
        - Se il focus riga è già 0:
          * non sposta il focus
          * ritorna evento di limite minimo
        - Altrimenti:
          * decrementa l'indice riga e mostra la nuova riga selezionata

        Ritorna:
        - EsitoAzione:
          * ok=False con errore standard se non si può navigare (evento=None)
          * ok=True con evento=EventoNavigazioneRiga (mostra o limite)

        Nota:
        - Indici interni riga: 0..2. La conversione 1-based è nel factory dell'evento/renderer.
        """
        # 1) Guard-rail centralizzato: senza cartella valida in focus (o altri vincoli)
        #    non si procede e non si creano eventi.
        esito_nav = self._esito_pronto_per_navigazione()
        if not esito_nav.ok:
            return esito_nav

        # 2) Capisco se è il "primo utilizzo" del focus riga.
        #    In quel caso mostreremo subito la riga 0.
        riga_era_none = (self._indice_riga_focus is None)

        # 3) Assicura che il focus riga sia impostato (senza costruire testo).
        #    Se l'helper fallisce, propago l'errore.
        esito_init_riga = self._esito_inizializza_focus_riga_se_manca()
        if not esito_init_riga.ok:
            return esito_init_riga

        # Contesto comune (utile per l'evento e per UI future).
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]
        totale_cartelle = len(self.cartelle)
        numero_cartella_corrente = self._indice_cartella_focus + 1
        totale_righe = cartella_in_focus.righe

        # Direzione del comando (coerente col nome del metodo: "su" = precedente).
        direzione = "precedente"

        # 4) Caso "primo utilizzo": focus appena inizializzato, mostro riga 0 (o quella impostata).
        if riga_era_none:
            indice_riga_corrente = self._indice_riga_focus  # atteso 0 dopo init
            riga_semplice = cartella_in_focus.get_riga_semplice(indice_riga_corrente)

            evento = EventoNavigazioneRiga.mostra_riga(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_righe=totale_righe,
                indice_riga_corrente=indice_riga_corrente,
                riga_semplice=riga_semplice,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 5) Autolimite: già sulla prima riga, non posso salire.
        if self._indice_riga_focus == 0:
            evento = EventoNavigazioneRiga.limite_minimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_righe=totale_righe,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 6) Spostamento effettivo verso l'alto: aggiorno stato interno.
        nuova_riga = self._indice_riga_focus - 1
        self._indice_riga_focus = nuova_riga

        # 7) Dati riga in formato semplice (9 celle int o "-"), senza testo pronto.
        riga_semplice = cartella_in_focus.get_riga_semplice(nuova_riga)

        # 8) Evento "mostra": il renderer produrrà la stampa finale.
        evento = EventoNavigazioneRiga.mostra_riga(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome_giocatore,
            direzione=direzione,
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            indice_riga_corrente=nuova_riga,
            riga_semplice=riga_semplice,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #metodo 10 ...
    def sposta_focus_riga_giu_semplice(self) -> EsitoAzione:
        """
        Comando di navigazione: sposta il focus riga verso il basso (riga successiva)
        sulla cartella attualmente in focus.

        Obiettivo:
        - Non produrre stringhe pronte: ritorna un evento (EventoNavigazioneRiga) dentro EsitoAzione.
        - Il renderer userà l'evento + dizionario lingua per mostrare:
          * la riga in formato semplice (esito="mostra")
          * un feedback breve di limite (esito="limite", limite="massimo")

        Comportamento:
        - Verifica pre-condizione di navigazione con _esito_pronto_per_navigazione().
          Se fallisce: propaga l'errore (ok=False) e non crea eventi.
        - Se il focus riga è None:
          * inizializza la riga (tipicamente a 0) tramite helper
          * mostra la riga 0 senza saltare direttamente alla riga 1
        - Se il focus riga è già l'ultima riga:
          * non sposta il focus
          * ritorna evento di limite massimo
        - Altrimenti:
          * incrementa l'indice riga e mostra la nuova riga selezionata

        Ritorna:
        - EsitoAzione:
          * ok=False con errore standard se non si può navigare (evento=None)
          * ok=True con evento=EventoNavigazioneRiga (mostra o limite)

        Nota:
        - Indici interni riga: 0..2. La conversione 1-based è nel factory dell'evento/renderer.
        """
        # 1) Guard-rail centralizzato: senza cartella valida in focus (o altri vincoli)
        #    non si procede e non si creano eventi.
        esito_nav = self._esito_pronto_per_navigazione()
        if not esito_nav.ok:
            return esito_nav

        # 2) Capisco se è il "primo utilizzo" del focus riga.
        #    In quel caso mostreremo subito la riga 0.
        riga_era_none = (self._indice_riga_focus is None)

        # 3) Assicura che il focus riga sia impostato (senza costruire testo).
        #    Se l'helper fallisce, propago l'errore.
        esito_init_riga = self._esito_inizializza_focus_riga_se_manca()
        if not esito_init_riga.ok:
            return esito_init_riga

        # Contesto comune (utile per l'evento e per UI future).
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]
        totale_cartelle = len(self.cartelle)
        numero_cartella_corrente = self._indice_cartella_focus + 1
        totale_righe = cartella_in_focus.righe

        # Direzione del comando (coerente col nome del metodo: "giù" = successiva).
        direzione = "successiva"

        # 4) Caso "primo utilizzo": focus appena inizializzato, mostro riga 0 (o quella impostata).
        if riga_era_none:
            indice_riga_corrente = self._indice_riga_focus  # atteso 0 dopo init
            riga_semplice = cartella_in_focus.get_riga_semplice(indice_riga_corrente)

            evento = EventoNavigazioneRiga.mostra_riga(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_righe=totale_righe,
                indice_riga_corrente=indice_riga_corrente,
                riga_semplice=riga_semplice,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 5) Autolimite: se sono già sull'ultima riga, non posso scendere.
        ultima_riga = totale_righe - 1
        if self._indice_riga_focus == ultima_riga:
            evento = EventoNavigazioneRiga.limite_massimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_righe=totale_righe,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 6) Spostamento effettivo verso il basso: aggiorno stato interno.
        nuova_riga = self._indice_riga_focus + 1
        self._indice_riga_focus = nuova_riga

        # 7) Dati riga in formato semplice (9 celle int o "-"), senza testo pronto.
        riga_semplice = cartella_in_focus.get_riga_semplice(nuova_riga)

        # 8) Evento "mostra": il renderer produrrà la stampa finale.
        evento = EventoNavigazioneRiga.mostra_riga(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome_giocatore,
            direzione=direzione,
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            indice_riga_corrente=nuova_riga,
            riga_semplice=riga_semplice,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #metodo 11 ...
    def sposta_focus_riga_su_avanzata(self) -> EsitoAzione:
        """
        Comando di navigazione (AVANZATA): sposta il focus riga verso l'alto
        (riga precedente) sulla cartella attualmente in focus.

        Obiettivo:
        - Non produrre stringhe pronte: ritorna un evento EventoNavigazioneRigaAvanzata in EsitoAzione.
        - Il renderer userà l'evento + dizionario lingua per produrre:
          * la riga con stato (esito="mostra")
          * un feedback breve di limite (esito="limite", limite="minimo")

        Comportamento:
        - Se la pre-condizione di navigazione fallisce: propaga l'errore e non crea eventi.
        - Se il focus riga è None: inizializza (tipicamente a 0) e mostra la riga 0.
        - Se il focus riga è già 0: non sposta e ritorna evento di limite minimo.
        - Altrimenti: decrementa l'indice, aggiorna il focus e mostra la nuova riga.

        Ritorna:
        - EsitoAzione ok=False con errore standard, oppure ok=True con evento EventoNavigazioneRigaAvanzata.
        """
        # 1) Guard-rail centralizzato: se non posso navigare, non creo eventi.
        esito_nav = self._esito_pronto_per_navigazione()
        if not esito_nav.ok:
            return esito_nav

        # 2) Caso "primo utilizzo": se il focus riga è None, vogliamo mostrare subito la riga 0.
        riga_era_none = (self._indice_riga_focus is None)

        # 3) Assicura che il focus riga esista; se l'helper fallisce, propago l'esito.
        esito_init_riga = self._esito_inizializza_focus_riga_se_manca()
        if not esito_init_riga.ok:
            return esito_init_riga

        # Contesto comune per l'evento.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]
        totale_cartelle = len(self.cartelle)
        numero_cartella_corrente = self._indice_cartella_focus + 1
        totale_righe = cartella_in_focus.righe

        direzione = "precedente"

        # 4) Primo utilizzo: mostra riga corrente (atteso 0).
        if riga_era_none:
            indice_riga_corrente = self._indice_riga_focus
            dati_riga_avanzati = cartella_in_focus.get_dati_visualizzazione_riga_avanzata(
                indice_riga_corrente
            )

            evento = EventoNavigazioneRigaAvanzata.mostra_riga(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_righe=totale_righe,
                indice_riga_corrente=indice_riga_corrente,
                dati_riga_avanzati=dati_riga_avanzati,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 5) Autolimite minimo: già sulla prima riga.
        if self._indice_riga_focus == 0:
            evento = EventoNavigazioneRigaAvanzata.limite_minimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_righe=totale_righe,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 6) Spostamento effettivo verso l'alto: aggiorno stato interno.
        nuova_riga = self._indice_riga_focus - 1
        self._indice_riga_focus = nuova_riga

        # 7) Dati avanzati della riga (riga 9-celle + stato + segnati ordinati), senza testo pronto.
        dati_riga_avanzati = cartella_in_focus.get_dati_visualizzazione_riga_avanzata(nuova_riga)

        # 8) Evento "mostra": il renderer produrrà la stampa avanzata finale.
        evento = EventoNavigazioneRigaAvanzata.mostra_riga(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome_giocatore,
            direzione=direzione,
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            indice_riga_corrente=nuova_riga,
            dati_riga_avanzati=dati_riga_avanzati,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #metodo 12 ...
    def sposta_focus_riga_giu_avanzata(self) -> EsitoAzione:
        """
        Comando di navigazione (AVANZATA): sposta il focus riga verso il basso
        (riga successiva) sulla cartella attualmente in focus.

        Obiettivo:
        - Non produrre stringhe pronte: ritorna un evento EventoNavigazioneRigaAvanzata in EsitoAzione.
        - Il renderer userà l'evento + dizionario lingua per produrre:
          * la riga con stato (esito="mostra")
          * un feedback breve di limite (esito="limite", limite="massimo")

        Comportamento:
        - Se la pre-condizione di navigazione fallisce: propaga l'errore e non crea eventi.
        - Se il focus riga è None: inizializza (tipicamente a 0) e mostra la riga 0 (senza saltare alla 1).
        - Se il focus riga è già l'ultima: non sposta e ritorna evento di limite massimo.
        - Altrimenti: incrementa l'indice, aggiorna il focus e mostra la nuova riga.

        Ritorna:
        - EsitoAzione ok=False con errore standard, oppure ok=True con evento EventoNavigazioneRigaAvanzata.
        """
        # 1) Guard-rail centralizzato: se non posso navigare, non creo eventi.
        esito_nav = self._esito_pronto_per_navigazione()
        if not esito_nav.ok:
            return esito_nav

        # 2) Caso "primo utilizzo": se il focus riga è None, vogliamo mostrare subito la riga 0.
        riga_era_none = (self._indice_riga_focus is None)

        # 3) Assicura che il focus riga esista; se l'helper fallisce, propago l'esito.
        esito_init_riga = self._inizializza_focus_riga_se_manca()
        if not esito_init_riga.ok:
            return esito_init_riga

        # Contesto comune per l'evento.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]
        totale_cartelle = len(self.cartelle)
        numero_cartella_corrente = self._indice_cartella_focus + 1
        totale_righe = cartella_in_focus.righe

        direzione = "successiva"

        # 4) Primo utilizzo: mostra riga corrente (atteso 0).
        if riga_era_none:
            indice_riga_corrente = self._indice_riga_focus
            dati_riga_avanzati = cartella_in_focus.get_dati_visualizzazione_riga_avanzata(
                indice_riga_corrente
            )

            evento = EventoNavigazioneRigaAvanzata.mostra_riga(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_righe=totale_righe,
                indice_riga_corrente=indice_riga_corrente,
                dati_riga_avanzati=dati_riga_avanzati,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 5) Autolimite massimo: già sull'ultima riga.
        ultima_riga = totale_righe - 1
        if self._indice_riga_focus == ultima_riga:
            evento = EventoNavigazioneRigaAvanzata.limite_massimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_righe=totale_righe,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 6) Spostamento effettivo verso il basso: aggiorno stato interno.
        nuova_riga = self._indice_riga_focus + 1
        self._indice_riga_focus = nuova_riga

        # 7) Dati avanzati della riga (riga 9-celle + stato + segnati ordinati), senza testo pronto.
        dati_riga_avanzati = cartella_in_focus.get_dati_visualizzazione_riga_avanzata(nuova_riga)

        # 8) Evento "mostra": il renderer produrrà la stampa avanzata finale.
        evento = EventoNavigazioneRigaAvanzata.mostra_riga(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome_giocatore,
            direzione=direzione,
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            indice_riga_corrente=nuova_riga,
            dati_riga_avanzati=dati_riga_avanzati,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #Sezione 4: METODI DEDICATI ALLO SPOSTAMENTO DEL FOCUS DI COLONNA

    #metodo 13 ...
    def sposta_focus_colonna_sinistra(self) -> EsitoAzione:
        """
        Comando di navigazione: sposta il focus colonna verso sinistra (colonna precedente)
        sulla cartella attualmente in focus.

        Obiettivo:
        - Non produrre stringhe pronte: ritorna un evento EventoNavigazioneColonna in EsitoAzione.
        - Il renderer userà l'evento + dizionario lingua per mostrare:
          * la colonna in formato semplice (esito="mostra")
          * un feedback breve di limite (esito="limite", limite="minimo")

        Comportamento:
        - Se la pre-condizione di navigazione fallisce: propaga l'errore e non crea eventi.
        - Se il focus colonna è None: inizializza (tipicamente a 0) e mostra la colonna 0.
        - Se il focus colonna è già 0: non sposta e ritorna evento di limite minimo.
        - Altrimenti: decrementa l'indice, aggiorna il focus e mostra la nuova colonna.

        Ritorna:
        - EsitoAzione ok=False con errore standard, oppure ok=True con evento EventoNavigazioneColonna.
        """
        # 1) Guard-rail centralizzato: se non posso navigare, non creo eventi.
        esito_nav = self._esito_pronto_per_navigazione()
        if not esito_nav.ok:
            return esito_nav

        # 2) Caso "primo utilizzo": se il focus colonna è None, vogliamo mostrare subito la colonna 0.
        colonna_era_none = (self._indice_colonna_focus is None)

        # 3) Assicura che il focus colonna esista; se l'helper fallisce, propago l'esito.
        esito_init_colonna = self._esito_inizializza_focus_colonna_se_manca()
        if not esito_init_colonna.ok:
            return esito_init_colonna

        # Contesto comune per l'evento.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]
        totale_cartelle = len(self.cartelle)
        numero_cartella_corrente = self._indice_cartella_focus + 1
        totale_colonne = cartella_in_focus.colonne

        direzione = "precedente"

        # 4) Primo utilizzo: mostra colonna corrente (attesa 0).
        if colonna_era_none:
            indice_colonna_corrente = self._indice_colonna_focus  # atteso 0 dopo init
            colonna_semplice = cartella_in_focus.get_colonna_semplice(indice_colonna_corrente)

            evento = EventoNavigazioneColonna.mostra_colonna(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_colonne=totale_colonne,
                indice_colonna_corrente=indice_colonna_corrente,
                colonna_semplice=colonna_semplice,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 5) Autolimite minimo: già sulla prima colonna.
        if self._indice_colonna_focus == 0:
            evento = EventoNavigazioneColonna.limite_minimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_colonne=totale_colonne,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 6) Spostamento effettivo verso sinistra: aggiorno stato interno.
        nuova_colonna = self._indice_colonna_focus - 1
        self._indice_colonna_focus = nuova_colonna

        # 7) Dati colonna in formato semplice (3 celle int o "-"), senza testo pronto.
        colonna_semplice = cartella_in_focus.get_colonna_semplice(nuova_colonna)

        # 8) Evento "mostra": il renderer produrrà la stampa finale.
        evento = EventoNavigazioneColonna.mostra_colonna(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome_giocatore,
            direzione=direzione,
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_colonne=totale_colonne,
            indice_colonna_corrente=nuova_colonna,
            colonna_semplice=colonna_semplice,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #metodo 14 ...
    def sposta_focus_colonna_destra(self) -> EsitoAzione:
        """
        Comando di navigazione: sposta il focus colonna verso destra (colonna successiva)
        sulla cartella attualmente in focus.

        Obiettivo:
        - Non produrre stringhe pronte: ritorna un evento EventoNavigazioneColonna in EsitoAzione.
        - Il renderer userà l'evento + dizionario lingua per mostrare:
          * la colonna in formato semplice (esito="mostra")
          * un feedback breve di limite (esito="limite", limite="massimo")

        Comportamento:
        - Se la pre-condizione di navigazione fallisce: propaga l'errore e non crea eventi.
        - Se il focus colonna è None: inizializza (tipicamente a 0) e mostra la colonna 0.
        - Se il focus colonna è già l'ultima: non sposta e ritorna evento di limite massimo.
        - Altrimenti: incrementa l'indice, aggiorna il focus e mostra la nuova colonna.

        Ritorna:
        - EsitoAzione ok=False con errore standard, oppure ok=True con evento EventoNavigazioneColonna.
        """
        # 1) Guard-rail centralizzato: se non posso navigare, non creo eventi.
        esito_nav = self._esito_pronto_per_navigazione()
        if not esito_nav.ok:
            return esito_nav

        # 2) Caso "primo utilizzo": se il focus colonna è None, vogliamo mostrare subito la colonna 0.
        colonna_era_none = (self._indice_colonna_focus is None)

        # 3) Assicura che il focus colonna esista; se l'helper fallisce, propago l'esito.
        esito_init_colonna = self._esito_inizializza_focus_colonna_se_manca()
        if not esito_init_colonna.ok:
            return esito_init_colonna

        # Contesto comune per l'evento.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]
        totale_cartelle = len(self.cartelle)
        numero_cartella_corrente = self._indice_cartella_focus + 1
        totale_colonne = cartella_in_focus.colonne

        direzione = "successiva"

        # 4) Primo utilizzo: mostra colonna corrente (attesa 0).
        if colonna_era_none:
            indice_colonna_corrente = self._indice_colonna_focus  # atteso 0 dopo init
            colonna_semplice = cartella_in_focus.get_colonna_semplice(indice_colonna_corrente)

            evento = EventoNavigazioneColonna.mostra_colonna(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_colonne=totale_colonne,
                indice_colonna_corrente=indice_colonna_corrente,
                colonna_semplice=colonna_semplice,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 5) Autolimite massimo: già sull'ultima colonna.
        ultima_colonna = totale_colonne - 1
        if self._indice_colonna_focus == ultima_colonna:
            evento = EventoNavigazioneColonna.limite_massimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_colonne=totale_colonne,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 6) Spostamento effettivo verso destra: aggiorno stato interno.
        nuova_colonna = self._indice_colonna_focus + 1
        self._indice_colonna_focus = nuova_colonna

        # 7) Dati colonna in formato semplice (3 celle int o "-"), senza testo pronto.
        colonna_semplice = cartella_in_focus.get_colonna_semplice(nuova_colonna)

        # 8) Evento "mostra": il renderer produrrà la stampa finale.
        evento = EventoNavigazioneColonna.mostra_colonna(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome_giocatore,
            direzione=direzione,
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_colonne=totale_colonne,
            indice_colonna_corrente=nuova_colonna,
            colonna_semplice=colonna_semplice,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #metodo 15 ...
    def sposta_focus_colonna_sinistra_avanzata(self) -> EsitoAzione:
        """
        Comando di navigazione (AVANZATA): sposta il focus colonna verso sinistra
        (colonna precedente) sulla cartella attualmente in focus.

        Obiettivo:
        - Eliminare la produzione di stringhe pronte: ritorna un evento EventoNavigazioneColonnaAvanzata.
        - Il renderer userà l'evento + dizionario lingua per produrre:
          * la colonna con stato (esito="mostra")
          * un feedback breve di limite (esito="limite", limite="minimo")

        Comportamento:
        - Se la pre-condizione di navigazione fallisce: propaga l'errore e non crea eventi.
        - Se il focus colonna è None: inizializza (tipicamente a 0) e mostra la colonna 0.
        - Se il focus colonna è già 0: non sposta e ritorna evento di limite minimo.
        - Altrimenti: decrementa l'indice, aggiorna il focus e mostra la nuova colonna.

        Ritorna:
        - EsitoAzione ok=False con errore standard, oppure ok=True con evento EventoNavigazioneColonnaAvanzata.
        """
        # 1) Guard-rail centralizzato: se non posso navigare, non creo eventi.
        esito_nav = self._esito_pronto_per_navigazione()
        if not esito_nav.ok:
            return esito_nav

        # 2) Caso "primo utilizzo": se il focus colonna è None, vogliamo mostrare subito la colonna 0.
        colonna_era_none = (self._indice_colonna_focus is None)

        # 3) Assicura che il focus colonna esista; se l'helper fallisce, propago l'esito.
        esito_init_colonna = self._esito_inizializza_focus_colonna_se_manca()
        if not esito_init_colonna.ok:
            return esito_init_colonna

        # Contesto comune per l'evento.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]
        totale_cartelle = len(self.cartelle)
        numero_cartella_corrente = self._indice_cartella_focus + 1
        totale_colonne = cartella_in_focus.colonne

        # Direzione del comando: sinistra = precedente.
        direzione = "sinistra"

        # 4) Primo utilizzo: mostra colonna corrente (attesa 0).
        if colonna_era_none:
            indice_colonna_corrente = self._indice_colonna_focus  # atteso 0 dopo init
            dati_colonna_avanzati = cartella_in_focus.get_dati_visualizzazione_colonna_avanzata(
                indice_colonna_corrente
            )

            evento = EventoNavigazioneColonnaAvanzata.mostra_colonna(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_colonne=totale_colonne,
                indice_colonna_corrente=indice_colonna_corrente,
                dati_colonna_avanzati=dati_colonna_avanzati,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 5) Autolimite minimo: già sulla prima colonna.
        if self._indice_colonna_focus == 0:
            evento = EventoNavigazioneColonnaAvanzata.limite_minimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_colonne=totale_colonne,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 6) Spostamento effettivo verso sinistra: aggiorno stato interno.
        nuova_colonna = self._indice_colonna_focus - 1
        self._indice_colonna_focus = nuova_colonna

        # 7) Dati avanzati colonna (colonna 3-celle + stato + segnati ordinati), senza testo pronto.
        dati_colonna_avanzati = cartella_in_focus.get_dati_visualizzazione_colonna_avanzata(nuova_colonna)

        # 8) Evento "mostra": il renderer produrrà la stampa avanzata finale.
        evento = EventoNavigazioneColonnaAvanzata.mostra_colonna(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome_giocatore,
            direzione=direzione,
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_colonne=totale_colonne,
            indice_colonna_corrente=nuova_colonna,
            dati_colonna_avanzati=dati_colonna_avanzati,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #metodo 16 ...
    def sposta_focus_colonna_destra_avanzata(self) -> EsitoAzione:
        """
        Comando di navigazione (AVANZATA): sposta il focus colonna verso destra
        (colonna successiva) sulla cartella attualmente in focus.

        Obiettivo:
        - Eliminare la produzione di stringhe pronte: ritorna un evento EventoNavigazioneColonnaAvanzata.
        - Il renderer userà l'evento + dizionario lingua per produrre:
          * la colonna con stato (esito="mostra")
          * un feedback breve di limite (esito="limite", limite="massimo")

        Comportamento:
        - Se la pre-condizione di navigazione fallisce: propaga l'errore e non crea eventi.
        - Se il focus colonna è None: inizializza (tipicamente a 0) e mostra la colonna 0.
        - Se il focus colonna è già l'ultima colonna: non sposta e ritorna evento di limite massimo.
        - Altrimenti: incrementa l'indice, aggiorna il focus e mostra la nuova colonna.

        Ritorna:
        - EsitoAzione ok=False con errore standard, oppure ok=True con evento EventoNavigazioneColonnaAvanzata.
        """
        # 1) Guard-rail centralizzato: se non posso navigare, non creo eventi.
        esito_nav = self._esito_pronto_per_navigazione()
        if not esito_nav.ok:
            return esito_nav

        # 2) Caso "primo utilizzo": se il focus colonna è None, vogliamo mostrare subito la colonna 0.
        colonna_era_none = (self._indice_colonna_focus is None)

        # 3) Assicura che il focus colonna esista; se l'helper fallisce, propago l'esito.
        esito_init_colonna = self._esito_inizializza_focus_colonna_se_manca()
        if not esito_init_colonna.ok:
            return esito_init_colonna

        # Contesto comune per l'evento.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]
        totale_cartelle = len(self.cartelle)
        numero_cartella_corrente = self._indice_cartella_focus + 1
        totale_colonne = cartella_in_focus.colonne

        # Direzione del comando: destra = successiva.
        direzione = "destra"

        # 4) Primo utilizzo: mostra colonna corrente (attesa 0).
        if colonna_era_none:
            indice_colonna_corrente = self._indice_colonna_focus  # atteso 0 dopo init
            dati_colonna_avanzati = cartella_in_focus.get_dati_visualizzazione_colonna_avanzata(
                indice_colonna_corrente
            )

            evento = EventoNavigazioneColonnaAvanzata.mostra_colonna(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_colonne=totale_colonne,
                indice_colonna_corrente=indice_colonna_corrente,
                dati_colonna_avanzati=dati_colonna_avanzati,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 5) Autolimite massimo: già sull'ultima colonna.
        ultima_colonna = totale_colonne - 1
        if self._indice_colonna_focus == ultima_colonna:
            evento = EventoNavigazioneColonnaAvanzata.limite_massimo(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome_giocatore,
                direzione=direzione,
                totale_cartelle=totale_cartelle,
                numero_cartella_corrente=numero_cartella_corrente,
                totale_colonne=totale_colonne,
            )

            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento,
            )

        # 6) Spostamento effettivo verso destra: aggiorno stato interno.
        nuova_colonna = self._indice_colonna_focus + 1
        self._indice_colonna_focus = nuova_colonna

        # 7) Dati avanzati colonna (colonna 3-celle + stato + segnati ordinati), senza testo pronto.
        dati_colonna_avanzati = cartella_in_focus.get_dati_visualizzazione_colonna_avanzata(nuova_colonna)

        # 8) Evento "mostra": il renderer produrrà la stampa avanzata finale.
        evento = EventoNavigazioneColonnaAvanzata.mostra_colonna(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome_giocatore,
            direzione=direzione,
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_colonne=totale_colonne,
            indice_colonna_corrente=nuova_colonna,
            dati_colonna_avanzati=dati_colonna_avanzati,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #sezione 5: metodi di segnazione e di ricerca numero 

    #metodo 17 ...
    def segna_numero_manuale(self, numero_utente: int, tabellone) -> EsitoAzione:
        """
        Permette al giocatore di segnare manualmente un numero sulla cartella attualmente in focus.

        Obiettivo (coerente col progetto):
        - Nessuna stringa prodotta qui: ritorna sempre un EsitoAzione.
        - In caso di problemi tecnici/prerequisiti mancanti (input, tabellone, focus) ritorna ok=False con codice errore.
        - In caso di tentativo valido (anche se fallisce "per regole di gioco") ritorna ok=True con EventoSegnazioneNumero,
          usando i factory method: non_estratto / non_presente / gia_segnato / segnato.

        Regole:
        - Il focus cartella NON viene auto-impostato: se manca, è errore (azione che modifica stato).
        - Le coordinate (riga/colonna) vengono incluse solo quando hanno senso (segnato / gia_segnato).
        - Il progresso della cartella (segnati/totale/percentuale) viene sempre riportato nell'evento.

        Parametri:
        - numero_utente: int (1..90)
        - tabellone: oggetto Tabellone della partita corrente (validato con validazione_oggetti)

        Ritorna:
        - EsitoAzione(ok=False, errore=...) se non si può procedere.
        - EsitoAzione(ok=True, evento=EventoSegnazioneNumero...) se il tentativo è stato gestito.
        """

        # 1) Validazione input: tipo e range (prerequisito tecnico)
        #    Se fallisce, non creiamo eventi: ritorniamo un errore standard.
        esito_numero_non_valido = esito_numero_in_range_1_90(numero_utente)
        if not esito_numero_non_valido.ok:
            return esito_numero_non_valido

        # 2) Validazione tabellone: deve essere disponibile e coerente (prerequisito tecnico)
        esito_tab = esito_tabellone_disponibile(tabellone)
        if not esito_tab.ok:
            return esito_tab

        # 3) Validazione cartelle + focus cartella (prerequisito tecnico, niente auto-imposta)
        esito_focus_cartella = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_focus_cartella.ok:
            return esito_focus_cartella 

        # 4) Contesto comune per l'evento (dati cartella e progresso)
        indice_cartella = self._indice_cartella_focus  # 0-based
        totale_cartelle = len(self.cartelle)
        cartella = self.cartelle[indice_cartella]

        # Progresso della cartella: lo includiamo sempre, in tutti i casi evento.
        numeri_segnati = cartella.conta_numeri_segnati()
        totale_numeri = cartella.quantita_numeri
        percentuale = cartella.get_percentuale_completamento()

        # 5) Regola anti-baro: il numero deve essere estratto dal tabellone
        #    Se non è estratto, ritorniamo un evento "non_estratto" (non è un errore tecnico).
        if not tabellone.is_numero_estratto(numero_utente):
            evento = EventoSegnazioneNumero.non_estratto(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                numero=numero_utente,
                indice_cartella=indice_cartella,
                totale_cartelle=totale_cartelle,
                numeri_segnati=numeri_segnati,
                totale_numeri=totale_numeri,
                percentuale=percentuale,
            )
            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento
            )

        # 6) Il numero è estratto: ora verifichiamo se è presente in cartella
        #    Se non è presente, ritorniamo evento "non_presente".
        if numero_utente not in cartella.get_numeri_cartella():
            evento = EventoSegnazioneNumero.non_presente(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                numero=numero_utente,
                indice_cartella=indice_cartella,
                totale_cartelle=totale_cartelle,
                numeri_segnati=numeri_segnati,
                totale_numeri=totale_numeri,
                percentuale=percentuale,
            )
            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento
            )

        # 7) Il numero è presente: recuperiamo le coordinate una sola volta (dato grezzo)
        #    In teoria non dovrebbe mai essere None qui, ma restiamo difensivi.
        coordinate = cartella.get_coordinate_numero(numero_utente)
        if coordinate is None:
            return EsitoAzione(
                ok=False,
                errore="ERRORE_INTERNO",
                evento=None
            )

        indice_riga, indice_colonna = coordinate

        # 8) Se è già segnato, ritorniamo evento "gia_segnato" (progresso invariato).
        if cartella.is_numero_segnato(numero_utente):
            evento = EventoSegnazioneNumero.gia_segnato(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                numero=numero_utente,
                indice_cartella=indice_cartella,
                totale_cartelle=totale_cartelle,
                indice_riga=indice_riga,
                indice_colonna=indice_colonna,
                numeri_segnati=numeri_segnati,
                totale_numeri=totale_numeri,
                percentuale=percentuale,
            )
            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento
            )

        # 9) Azione: segna davvero il numero e poi ricalcola il progresso (deve essere "dopo la segnatura")
        cartella.segna_numero(numero_utente)

        numeri_segnati_after = cartella.conta_numeri_segnati()
        percentuale_after = cartella.get_percentuale_completamento()

        evento = EventoSegnazioneNumero.segnato(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            numero=numero_utente,
            indice_cartella=indice_cartella,
            totale_cartelle=totale_cartelle,
            indice_riga=indice_riga,
            indice_colonna=indice_colonna,
            numeri_segnati=numeri_segnati_after,
            totale_numeri=totale_numeri,
            percentuale=percentuale_after,
        )
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento
        )


    def cerca_numero_nelle_cartelle(self, numero_cercato: int) -> EsitoAzione:
        """
        Cerca un numero in TUTTE le cartelle del giocatore e ritorna un EsitoAzione con un evento UI.

        Obiettivo (coerenza architetturale):
        - Nessuna stringa prodotta qui: il testo è responsabilità del renderer.
        - Nessuna modifica allo stato di gioco (non cambia focus e non segna numeri).
        - Output stabile e testabile tramite EventoRicercaNumeroInCartelle.

        Comportamento:
        - Se l'input non è valido, ritorna EsitoAzione(okFalse) con codice errore standardizzato.
        - Se il giocatore non ha cartelle, ritorna EsitoAzione(okFalse) propagando l'errore dell'helper.
        - Se il numero non è presente in nessuna cartella, ritorna EsitoAzione(okTrue) con evento nontrovato.
        - Se il numero è presente in una o più cartelle, ritorna EsitoAzione(okTrue) con evento trovato e risultati.

        Parametri:
        - numerocercato: int tra 1 e 90.

        Ritorna:
        - EsitoAzione con evento EventoRicercaNumeroInCartelle (trovato/nontrovato) oppure con errore.
        """

        # 1) Validazione input: tipo e range (stesso stile del resto del progetto).
        esito_numero_in_range = esito_numero_in_range_1_90(numero_cercato)
        if not esito_numero_in_range.ok:
            return esito_numero_in_range

        # 2) Prerequisito minimo: il giocatore deve avere almeno una cartella.
        esito_cartelle = self._esito_ha_cartelle()
        if not esito_cartelle.ok:
            return esito_cartelle

        totale_cartelle = len(self.cartelle)

        # 3) Raccolta risultati (dati grezzi, senza testo).
        risultati = []

        for indice_cartella, cartella in enumerate(self.cartelle):
            # Check veloce di presenza: se non c'è, non chiediamo coordinate (riduce lavoro).
            # Nota: get_numeri_cartella ritorna una lista ordinata, ma qui ci serve solo per membership.
            numeri_cartella = cartella.get_numeri_cartella()
            if numero_cercato not in numeri_cartella:
                continue

            # validiamo le coordinate 
            coordinate_presenti = esito_coordinate_numero_coerenti(cartella, numero_cercato)
            if not coordinate_presenti.ok:
                return coordinate_presenti

            # Se il numero è dichiarato presente, le coordinate devono esistere: controllo difensivo.
            coordinate = cartella.get_coordinate_numero(numero_cercato)
            indice_riga, indice_colonna = coordinate

            # Stato segnato/non segnato (dato grezzo utile al renderer).
            segnato = cartella.is_numero_segnato(numero_cercato)

            risultato = RisultatoRicercaNumeroInCartella.crea(
                indice_cartella=indice_cartella,
                indice_riga=indice_riga,
                indice_colonna=indice_colonna,
                segnato=segnato,
            )
            risultati.append(risultato)

        # 4) Creazione evento finale (trovato/nontrovato) con factory method per stabilità.
        if not risultati:
            evento = EventoRicercaNumeroInCartelle.nontrovato(
                id_giocatore=self.idgiocatore,
                nome_giocatore=self.nome,
                numero=numero_cercato,
                totale_cartelle=totale_cartelle,
            )
            return EsitoAzione(
                ok=True,
                errore=None,
                evento=evento
            )

        evento = EventoRicercaNumeroInCartelle.trovato(
            id_giocatore=self.idgiocatore,
            nome_giocatore=self.nome,
            numero=numero_cercato,
            totale_cartelle=totale_cartelle,
            risultati=risultati,
        )
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento
        )


    #sezione 6 metodi di consultazione del tabellone 

    def verifica_numero_estratto(self, numero: object, tabellone: object) -> EsitoAzione:
        """
        Verifica se un numero richiesto dall'utente è già stato estratto nel tabellone.

        Obiettivo (coerenza con i comandi UI già presenti):
        - Nessuna stringa pronta nel dominio: si produce un evento dati e basta.
        - Comando di sola lettura: non modifica lo stato del giocatore e non modifica il tabellone.
        - Guardie robuste e standardizzate: se input o tabellone non sono validi, si ritorna
          un EsitoAzione(ok=False, errore=..., evento=None) senza creare eventi.

        Parametri:
        - numero (object): valore inserito dall'utente (verrà validato come int in range 1..90).
        - tabellone (object): oggetto tabellone fornito dal layer superiore (Partita/GameController).

        Ritorna:
        - EsitoAzione(ok=False, errore=..., evento=None) se:
          - il numero non è valido (tipo o range),
          - il tabellone non è disponibile/coerente.
        - EsitoAzione(ok=True, errore=None, evento=EventoVerificaNumeroEstratto(...)) se la verifica è eseguibile,
          con estratto=True/False in base allo stato del tabellone.
        """

        # 1) Guardia: il numero deve essere un intero in range 1..90.
        esito_numero = esito_numero_in_range_1_90(numero)
        if not esito_numero.ok:
            return esito_numero

        # 2) Guardia: il tabellone deve essere presente e del tipo atteso.
        esito_tabellone = esito_tabellone_disponibile(tabellone)
        if not esito_tabellone.ok:
            return esito_tabellone

        # 3) Normalizzazione: dopo la validazione, è sicuro convertire in int.
        numero_int = int(numero)

        # 4) Query al tabellone: controllo “read-only” (nessun side effect).
        #    Nota: Tabellone.is_numero_estratto si aspetta un numero già validato.
        estratto = tabellone.is_numero_estratto(numero_int)

        # 5) Creazione evento UI neutrale (nessun testo qui).
        if estratto:
            evento = EventoVerificaNumeroEstratto.estratto_si(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                numero=numero_int,
            )
        else:
            evento = EventoVerificaNumeroEstratto.estratto_no(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                numero=numero_int,
            )

        # 6) Esito finale: comando valido in entrambi i casi (estratto sì / estratto no).
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento
        )



    def comunica_ultimo_numero_estratto(self, tabellone: object) -> EsitoAzione:
        """
        Comando UI: restituisce l'ultimo numero estratto dal tabellone.

        Obiettivo (coerente con gli altri metodi del GiocatoreUmano):
        - Nessuna stringa pronta nel dominio: si ritorna un evento minimale per il renderer.
        - Metodo di sola lettura: non modifica lo stato del giocatore e non modifica il tabellone.
        - Precondizioni gestite con guardie standard: se il tabellone non è disponibile, si ritorna
          EsitoAzione(ok=False, errore=..., evento=None) senza creare eventi.

        Parametri:
        - tabellone (object): oggetto Tabellone della partita, fornito dal controller/Partita.

        Ritorna:
        - EsitoAzione(ok=False, errore="TABELLONE_NON_DISPONIBILE", evento=None) se il tabellone è assente o errato.
        - EsitoAzione(ok=True, errore=None, evento=EventoUltimoNumeroEstratto(...)) se la richiesta è gestibile:
          - ultimo_numero è un int -> evento "numero_presente"
          - ultimo_numero è None  -> evento "nessuna_estrazione"
        """

        # 1) Guardia: il tabellone deve essere presente e del tipo corretto.
        #    Coerenza: in caso di fallimento, NON creiamo eventi UI.
        esito_tabellone = esito_tabellone_disponibile(tabellone)
        if not esito_tabellone.ok:
            return esito_tabellone

        # 2) Lettura dell'informazione dal tabellone (nessun side-effect).
        #    Richiede che Tabellone esponga un metodo di consultazione dedicato.
        ultimo_numero = tabellone.get_ultimo_numero_estratto()

        # 3) Creazione evento minimale (nessun testo qui).
        if ultimo_numero is None:
            evento = EventoUltimoNumeroEstratto.nessuna_estrazione(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
            )
        else:
            evento = EventoUltimoNumeroEstratto.numero_presente(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                ultimo_numero=ultimo_numero,
            )

        # 4) Esito finale: comando valido in entrambi i casi (presente / nessuna estrazione).
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento
        )


    def visualizzaultiminumeriestratti(self, tabellone: object) -> EsitoAzione:
        """
        Comando UI: richiede al tabellone gli ultimi 5 numeri estratti e ritorna un evento
        pronto per il renderer (senza costruire stringhe nel dominio).

        Obiettivo (coerente con il resto di GiocatoreUmano):
        - Validare prerequisiti tecnici (tabellone disponibile) e, se falliscono, ritornare
          EsitoAzione(ok=False, errore=..., evento=None).
        - Se la richiesta è lecita, ritornare EsitoAzione(ok=True) con un evento:
          - EventoUltimiNumeriEstratti.nessuna_estrazione(...) se non esiste ancora cronologia.
          - EventoUltimiNumeriEstratti.crea_con_numeri(...) se esistono numeri da mostrare.

        Nota di stabilità:
        - Anche se il tabellone ha un default, qui passiamo sempre 5 esplicitamente per chiarezza.
        """

        # 1) Guardia tecnica: se il tabellone non è disponibile/non valido, non creiamo eventi UI.
        esitotab = esito_tabellone_disponibile(tabellone)
        if not esitotab.ok:
            return esitotab

        # 2) Consultazione pura: chiediamo esplicitamente gli ultimi 5 numeri.
        #    Il tabellone ritorna una tupla (immutabile) vuota se non c'è ancora alcuna estrazione.
        richiesti = 5
        ultimi = tabellone.get_ultimi_numeri_estratti(richiesti)

        # 3) Costruzione evento: nessun testo qui, solo dati grezzi per il renderer.
        if not ultimi:
            evento = EventoUltimiNumeriEstratti.nessuna_estrazione(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                richiesti=richiesti,
            )
        else:
            evento = EventoUltimiNumeriEstratti.crea_con_numeri(
                id_giocatore=self.id_giocatore,
                nome_giocatore=self.nome,
                richiesti=richiesti,
                numeri=ultimi,
            )

        # 4) Esito finale: comando gestito correttamente in entrambi i casi (0 numeri o N numeri).
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento
        )


    def riepilogo_tabellone(self, tabellone: object) -> EsitoAzione:
        """
        Comando UI: produce un riepilogo globale del tabellone (contatori, percentuale,
        ultimi estratti e ultimo estratto) sotto forma di evento dati.

        Obiettivo (coerente con gli altri metodi di GiocatoreUmano):
        - Nessun testo pronto: qui si costruiscono solo dati per il renderer.
        - Guardia tecnica: se il tabellone non è disponibile/non valido, ritorna subito
          EsitoAzione(ok=False, errore=..., evento=None) senza creare eventi.
        - Se il tabellone è valido, ritorna sempre EsitoAzione(ok=True, evento=EventoRiepilogoTabellone),
          anche quando non è stata fatta ancora nessuna estrazione (caso lecito, non un errore).
        """

        # 1) Guardia: il tabellone deve essere disponibile e coerente (prerequisito tecnico).
        esitotab = esito_tabellone_disponibile(tabellone)
        if not esitotab.ok:
            return esitotab

        # 2) Recupero "fotografia" completa dal tabellone.
        #    Qui evitiamo di ricostruire i contatori con chiamate multiple: la logica resta nel tabellone.
        stato = tabellone.get_stato_tabellone()

        # 3) Mappo i campi del dizionario del tabellone nei campi dell'evento.
        #    Nota: nel tabellone "numeri_disponibili" corrisponde ai "mancanti" del riepilogo.
        totale_numeri = stato["totale_numeri"]
        totale_estratti = stato["numeri_estratti"]
        totale_mancanti = stato["numeri_disponibili"]
        percentuale = stato["percentuale_avanzamento"]
        ultimi_estratti = stato["ultimi_numeri_estratti"]
        ultimo_estratto = stato["ultimo_numero_estratto"]

        # 4) Costruzione evento tramite factory method (stabilità: tuple immutabili + campi derivati).
        evento = EventoRiepilogoTabellone.crea(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            totale_numeri=totale_numeri,
            totale_estratti=totale_estratti,
            totale_mancanti=totale_mancanti,
            percentuale_estrazione=percentuale,
            ultimi_estratti=ultimi_estratti,
            ultimo_estratto=ultimo_estratto,
        )

        # 5) Esito finale: consultazione gestita correttamente (anche se non ci sono estrazioni).
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento
        )


    def lista_numeri_estratti(self, tabellone: object) -> EsitoAzione:
        """
        Comando UI: restituisce l'elenco completo dei numeri estratti dal tabellone,
        sotto forma di evento dati (EventoListaNumeriEstratti).

        Obiettivo (coerente con gli altri metodi di consultazione):
        - Nessun testo pronto: qui si producono solo dati grezzi per il renderer.
        - Stabilità: l'evento espone una tupla immutabile e ordinata.
        - Guardia tecnica: se il tabellone non è disponibile/non valido, ritorna subito
          l'EsitoAzione di errore senza creare eventi.
        - Caso "nessuna estrazione": è un caso lecito, non un errore (lista vuota).
        """

        # 1) Guardia: il tabellone deve essere disponibile e coerente (prerequisito tecnico).
        esitotab = esito_tabellone_disponibile(tabellone)
        if not esitotab.ok:
            return esitotab

        # 2) Lettura dal dominio: il tabellone espone già la lista ordinata dei numeri estratti.
        #    Non ricostruiamo la lista manualmente: la logica resta nel Tabellone.
        numeri_estratti = tabellone.get_numeri_estratti()

        # 3) Costruzione evento tramite factory method:
        #    normalizza (ordina + tupla immutabile) e calcola totale_estratti.
        evento = EventoListaNumeriEstratti.crea(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            numeri_estratti=numeri_estratti,
        )

        # 4) Esito finale standard: consultazione riuscita (anche se la lista è vuota).
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    #SEZIONE 7: consultazione dei focus di cartella riga e colonna e spostamenti rapidi 

    def stato_focus_corrente(self) -> EsitoAzione:
        """
        Comando UI: restituisce lo stato dei focus correnti (cartella, riga, colonna)
        come evento EventoStatoFocusCorrente.

        Obiettivo (coerente con gli altri metodi di consultazione):
        - È una semplice "fotografia" dello stato interno del giocatore umano.
        - Non modifica nulla: non auto-imposta focus e non resetta indici.
        - Non produce testo: ritorna un evento dati per il renderer.
        - È sempre disponibile: anche senza cartelle o con focus None, ritorna ok=True.
        """

        # 1) Contesto globale utile al renderer (es. "Cartella X di N").
        #    Se il giocatore non ha cartelle, totale_cartelle sarà 0: caso lecito.
        totale_cartelle = len(self.cartelle)

        # 2) Creazione evento tramite factory:
        #    convertiamo gli indici interni 0-based in numeri umani 1-based
        #    (e manteniamo None se il focus non è stato impostato).
        evento = EventoStatoFocusCorrente.crea_da_indici(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            totale_cartelle=totale_cartelle,
            indice_cartella=self._indice_cartella_focus,
            indice_riga=self._indice_riga_focus,
            indice_colonna=self._indice_colonna_focus,
        )

        # 3) Esito standard: consultazione riuscita (mai un errore tecnico in questo comando).
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )


    def vai_a_riga_avanzata(self, numero_riga: object) -> EsitoAzione:
        """
        Imposta direttamente il focus sulla riga indicata (input umano 1..3) e ritorna
        un evento di output UI in formato AVANZATO con i dati della riga.

        Obiettivi:
        - Validare input (tipo e range) con codici errore standardizzati.
        - Non auto-impostare il focus cartella: se manca, fallisce (azione esplicita).
        - Non produrre stringhe: ritorna EsitoAzione + evento dati.

        Parametri:
        - numeroriga (object): numero riga in formato umano (atteso int 1..3).

        Ritorna:
        - EsitoAzione(ok=False, errore="NUMERO_TIPO_NON_VALIDO") se numeroriga non è int.
        - EsitoAzione(ok=False, errore="NUMERO_RIGA_FUORI_RANGE") se numeroriga non è 1..3.
        - EsitoAzione(ok=False, errore=...) se il focus cartella non è valido (no auto-focus).
        - EsitoAzione(ok=True, evento=EventoVaiARigaAvanzata...) se l’operazione riesce.
        """

        # 1) Validazione tipo intero e range: riga umana 1..3.
        numero_riga_int_in_range = esito_numero_riga_in_range_1_3(numero_riga)
        if not numero_riga_int_in_range.ok:
            return numero_riga_int_in_range

        # Da qui numeroriga è int per contratto.
        numero_riga_int: int = numero_riga

        # 2) Precondizione: focus cartella valido SENZA auto-impostazione.
        esito_focus_cartella = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_focus_cartella.ok:
            return esito_focus_cartella

        # 3) Conversione in indice interno 0-based e aggiornamento focus riga.
        indice_riga_target = numero_riga_int - 1
        self._indice_riga_focus = indice_riga_target

        # 4) Recupero dati avanzati della riga e costruzione evento.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]

        dati_riga_avanzati = cartella_in_focus.get_dati_visualizzazione_riga_avanzata(indice_riga_target)

        evento = EventoVaiARigaAvanzata.crea_da_dati_riga_avanzati(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            numero_riga=numero_riga_int,
            dati_riga_avanzati=dati_riga_avanzati,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento
        )


    def vai_a_colonna_avanzata(self, numero_colonna: object) -> EsitoAzione:
        """
        Imposta direttamente il focus sulla colonna indicata (input umano 1..9) e ritorna
        un evento di output UI in formato AVANZATO con i dati della colonna.

        Obiettivi:
        - Validare input (tipo e range) con codici errore standardizzati.
        - Non auto-impostare il focus cartella: se manca, fallisce (azione esplicita).
        - Non produrre stringhe: ritorna EsitoAzione + evento dati.

        Parametri:
        - numero_colonna (object): numero colonna in formato umano (atteso int 1..9).

        Ritorna:
        - EsitoAzione(ok=False, errore="NUMERO_TIPO_NON_VALIDO") se numero_colonna non è int.
        - EsitoAzione(ok=False, errore="NUMERO_COLONNA_FUORI_RANGE") se numero_colonna non è 1..9.
        - EsitoAzione(ok=False, errore=...) se il focus cartella non è valido (no auto-focus).
        - EsitoAzione(ok=True, evento=EventoVaiAColonnaAvanzata...) se l’operazione riesce.
        """

        # 1) Validazione tipo intero e range: riga umana 1..9.
        numero_colonna_int_in_range = esito_numero_colonna_in_range_1_9(numero_colonna)
        if not numero_colonna_int_in_range.ok:
            return numero_colonna_int_in_range

        # Da qui numeroriga è int per contratto.
        numero_colonna_int: int = numero_colonna

        # 2) Precondizione: focus cartella valido SENZA auto-impostazione.
        esito_focus_cartella = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_focus_cartella.ok:
            return esito_focus_cartella

        # 3) Conversione in indice interno 0-based e aggiornamento focus riga.
        indice_colonna_target = numero_colonna_int - 1
        self._indice_colonna_focus = indice_colonna_target

        # 4) Recupero dati avanzati della colonna e costruzione evento.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]

        dati_colonna_avanzati = cartella_in_focus.get_dati_visualizzazione_colonna_avanzata(indice_colonna_target)

        evento = EventoVaiAColonnaAvanzata.crea_da_dati_colonna_avanzati(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            numero_colonna=numero_colonna_int,
            dati_colonna_avanzati=dati_colonna_avanzati,
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento
        )


    #SEZIONE 8: METODO DI ANNUNCIO VINCITE

    def annuncia_vittoria(self, tipo_vittoria: "Tipo_Vittoria", numero_turno: int) -> EsitoAzione:
        """
        Registra un reclamo di vittoria per il turno corrente, unificando i vecchi metodi
        (ambo/terno/quaterna/cinquina/tombola).

        Principio chiave (coerenza col progetto):
        - Questo metodo NON verifica se la vittoria esiste davvero (quello è compito della Partita).
        - Qui si fanno solo prerequisiti e coerenza focus (cartella/riga) e si costruisce un evento dati.
        - Nessuna stringa prodotta: si ritorna sempre EsitoAzione con codice errore o evento.

        Regole prerequisiti:
        - Sempre: è richiesta una cartella in focus (autoimposta=False).
        - Solo per vittorie di riga (ambo/terno/quaterna/cinquina): è richiesta anche una riga in focus
          selezionata esplicitamente (no auto-focus).

        Parametri:
        - tipo_vittoria: "tombola" oppure una vittoria di riga (es. "ambo", "terno", "quaterna", "cinquina").
        - numero_turno: numero del turno corrente (>= 1), usato nell'EventoReclamoVittoria (fase ANTE_TURNO).

        Ritorna:
        - EsitoAzione(ok=False, errore="RECLAMO_GIA_PRESENTE") se un reclamo turno è già stato registrato.
        - EsitoAzione(ok=False, errore=...) se mancano prerequisiti (focus cartella/riga, ecc.).
        - EsitoAzione(ok=True, evento=EventoReclamoVittoria.ante_turno(...)) se il reclamo viene registrato.
        """

        # 0) Un solo reclamo per turno: se già presente, non sovrascriviamo.
        verifica_reclamo_turno = self.reclamo_turno
        turno_libero = esito_reclamo_turno_libero(verifica_reclamo_turno )
        if not turno_libero .ok:
            return turno_libero

        # 1) Validazione base: il tipo deve essere uno di quelli supportati.
        #    Se arriva un valore non previsto, meglio fallire subito in modo difensivo.
        verifica_tipo_vittoria = esito_tipo_vittoria_supportato(tipo_vittoria)
        if not verifica_tipo_vittoria.ok:
            return verifica_tipo_vittoria

        # 2) Prerequisito comune: deve esserci una cartella in focus (senza auto-impostazione).
        esito_focus_cartella = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_focus_cartella.ok:
            return esito_focus_cartella

        # 3) Costruzione reclamo in base al tipo.
        if tipo_vittoria == "tombola":
            # Tombola: basta la cartella, la riga deve essere None.
            reclamo = ReclamoVittoria.tombola(
                indice_cartella=self._indice_cartella_focus
            )
        else:
            # Vittorie di riga: oltre alla cartella serve anche la riga selezionata esplicitamente.
            esito_focus_riga = self._esito_focus_riga_valido(auto_imposta=False)
            if not esito_focus_riga.ok:
                return esito_focus_riga

            reclamo = ReclamoVittoria.vittoria_di_riga(
                tipo=tipo_vittoria,
                indice_cartella=self._indice_cartella_focus,
                indice_riga=self._indice_riga_focus
            )

        # 4) Salviamo lo stato del turno (serve per bloccare doppi reclami nello stesso turno).
        self.reclamo_turno = reclamo

        # 5) Creiamo l'evento "soft" ANTE_TURNO per conferma UI (la validazione reale è in Partita).
        evento = EventoReclamoVittoria.ante_turno(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            numero_turno=numero_turno,
            reclamo=reclamo
        )

        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento
        )


    def passa_turno(self, numero_turno: int) -> "EventoFineTurno":
        """
        Conclude le azioni del giocatore umano per il turno corrente.

        Coerenza col progetto:
        - Il numero di turno è deciso dalla Partita (o dal controller), quindi viene passato qui
          come parametro (il giocatore non lo mantiene come stato interno).
        - Non genera testo: ritorna un EventoFineTurno (dati puri) che verrà interpretato da UI/Partita.

        Parametri:
        - numero_turno: turno corrente (convenzione: intero >= 1), fornito dal livello Partita/controller.

        Ritorna:
        - EventoFineTurno contenente l'eventuale reclamo registrato durante il turno.
        """
        return self._passa_turno_core(numero_turno=numero_turno)
