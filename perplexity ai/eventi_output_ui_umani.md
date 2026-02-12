from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Literal

__all__ = [
    "EventoRiepilogoCartellaCorrente",
    "EventoLimiteNavigazioneCartelle",
    "EventoVisualizzaCartellaSemplice",
    "EventoVisualizzaCartellaAvanzata",
    "EventoVisualizzaTutteCartelleSemplice",
    "EventoVisualizzaTutteCartelleAvanzata",
    "EventoNavigazioneRiga",
    "EventoNavigazioneRigaAvanzata",
]
Direzione_Navigazione_Cartelle = Literal[
    "precedente",
    "successiva"
]

Tipo_Limite_Navigazione_Cartelle = Literal[
    "minimo",
    "massimo"
]


Direzione_Navigazione_Righe = Literal[
    "precedente",
    "successiva",
]

Tipo_Limite_Navigazione_Righe = Literal[
    "minimo",
    "massimo",
]

Esito_Navigazione_Riga = Literal[
    "mostra",
    "limite",
]


@dataclass(frozen=True)
class EventoRiepilogoCartellaCorrente:
    """
    Evento "di output" per UI/renderer: contiene i dati necessari a rendere
    un riepilogo sintetico della cartella attualmente in focus.

    Obiettivo di stabilità:
    - Nessun testo pronto: la UI decide lingua, formato, quantità di dettagli.
    - Dati completi e neutrali: il renderer può produrre sia versioni brevi
      sia versioni verbose senza cambiare la logica del giocatore.

    Convenzioni:
    - indice_cartella è 0-based (indice interno).
    - numero_cartella è 1-based (numero "umano"), utile per annunci.
    - numeri_non_segnati è una sequenza ordinata crescente (se fornita).

    Nota:
    - percentuale è un valore numerico (tipicamente float) già calcolato dalla Cartella.
      Il renderer deciderà come formattarlo (es. 33.3%).
    """

    # Identità del giocatore (utile per log e UI multi-giocatore)
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Identità della cartella (sia indice interno che numero "umano")
    indice_cartella: int
    numero_cartella: int

    # Statistiche sintetiche
    numeri_segnati: int
    totale_numeri: int
    mancanti: int
    percentuale: float

    # Dettaglio opzionale: lista numeri ancora da segnare (ordinata)
    # Sequence[int] è intenzionale: è un tipo "read-only" lato consumer.
    numeri_non_segnati: Sequence[int]

    @classmethod
    def crea_da_cartella(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        indice_cartella: int,
        numeri_segnati: int,
        totale_numeri: int,
        percentuale: float,
        numeri_non_segnati: Sequence[int],
    ) -> "EventoRiepilogoCartellaCorrente":
        """
        Factory method (costruttore alternativo) per creare l'evento di riepilogo cartella
        in modo uniforme e sicuro.

        Perché è utile:
        - Centralizza la convenzione 0-based -> 1-based (numero_cartella).
        - Garantisce che la lista dei numeri non segnati sia ordinata.
        - Calcola in modo coerente il numero di mancanti (len della lista).

        Nota:
        - Questo metodo NON genera testo e non valida il focus: riceve già dati "puliti".
        - Se fornisci numeri_non_segnati non ordinati, verranno ordinati qui per stabilità.
        """

        # Converte indice interno (0-based) in numero "umano" (1-based).
        numero_cartella = indice_cartella + 1

        # Stabilità: normalizza l'ordine dei numeri non segnati.
        # Usiamo sorted(...) per non dipendere dal chiamante.
        numeri_non_segnati_ordinati = tuple(sorted(numeri_non_segnati))

        # Mancanti = quantità di numeri non segnati.
        mancanti = len(numeri_non_segnati_ordinati)

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            indice_cartella=indice_cartella,
            numero_cartella=numero_cartella,
            numeri_segnati=numeri_segnati,
            totale_numeri=totale_numeri,
            mancanti=mancanti,
            percentuale=percentuale,
            numeri_non_segnati=numeri_non_segnati_ordinati,
        )



@dataclass(frozen=True)
class EventoLimiteNavigazioneCartelle:
    """
    Evento di output UI umani: indica che un comando di navigazione cartelle
    non può procedere perché è stato raggiunto un limite.

    Perché esiste:
    - Evitare di ristampare riepiloghi già letti pochi secondi prima.
    - Dare un feedback breve e chiaro (1 riga) quando si tenta di andare oltre
      la prima o l'ultima cartella.

    Dati contenuti:
    - direzione: da quale comando arriva il limite ("precedente" o "successiva").
    - limite: quale limite è stato raggiunto ("minimo" = prima cartella, "massimo" = ultima cartella).
    - totale_cartelle: N totale cartelle possedute.
    - numero_cartella_corrente: indice umano (1..N) della cartella su cui si è fermi.

    Nota:
    - Questo evento non è un errore di dominio: l'azione è valida, ma non produce
      spostamento (autolimite). Per questo viene ritornato con EsitoAzione(ok=True).
    """

    id_giocatore: Optional[int]
    nome_giocatore: str

    direzione: Direzione_Navigazione_Cartelle
    limite: Tipo_Limite_Navigazione_Cartelle

    totale_cartelle: int
    numero_cartella_corrente: int

    @classmethod
    def limite_minimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Cartelle,
        totale_cartelle: int,
    ) -> "EventoLimiteNavigazioneCartelle":
        """
        Costruttore comodo per il caso: limite minimo (prima cartella).

        Imposta automaticamente:
        - limite="minimo"
        - numero_cartella_corrente=1
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            limite="minimo",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=1,
        )

    @classmethod
    def limite_massimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Cartelle,
        totale_cartelle: int,
    ) -> "EventoLimiteNavigazioneCartelle":
        """
        Costruttore comodo per il caso: limite massimo (ultima cartella).

        Imposta automaticamente:
        - limite="massimo"
        - numero_cartella_corrente=totale_cartelle
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            limite="massimo",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=totale_cartelle,
        )


@dataclass(frozen=True)
class EventoVisualizzaCartellaSemplice:
    """
    Evento di output per la UI del giocatore umano: rappresenta la cartella
    corrente in forma "semplice", senza testo pronto, usando solo dati grezzi.

    Scopo:
    - Permettere al renderer di mostrare la cartella (o di farla leggere a uno
      screen reader) senza che il dominio costruisca stringhe.
    - Fornire una fotografia stabile della cartella corrente: posizione nel
      set di cartelle e contenuto della griglia.

    Convenzioni:
    - indice_cartella è 0-based (indice interno).
    - numero_cartella è 1-based (numero "umano", da 1 a totale_cartelle).
    - griglia_semplice è una griglia 3x9 (righe x colonne) immutabile:
        * "-" nelle celle vuote,
        * int nelle celle che contengono un numero.
    """

    # Identità della cartella nel contesto del giocatore umano
    indice_cartella: int
    numero_cartella: int
    totale_cartelle: int

    # Contenuto "semplice" della cartella (solo numeri o "-")
    # Ogni tupla interna rappresenta una riga; le celle sono in ordine di colonna.
    griglia_semplice: tuple[tuple[int | str, ...], ...]

    @classmethod
    def crea_da_cartella(
        cls,
        *,
        indice_cartella: int,
        totale_cartelle: int,
        griglia_semplice: tuple[tuple[int | str, ...], ...],
    ) -> "EventoVisualizzaCartellaSemplice":
        """
        Factory method per costruire l'evento a partire dai dati già elaborati
        dalla Cartella (get_griglia_semplice) e dal contesto del giocatore.

        Perché è utile:
        - Centralizza la convenzione 0-based -> 1-based (numero_cartella).
        - Mantiene la griglia immutabile così come fornita dalla Cartella.
        - Evita duplicazioni di logica nei metodi di GiocatoreUmano.

        Parametri:
        - indice_cartella: int
          Indice interno (0-based) della cartella attualmente in focus.
        - totale_cartelle: int
          Numero totale di cartelle possedute dal giocatore umano.
        - griglia_semplice: tuple[tuple[int | str, ...], ...]
          Griglia 3x9 ottenuta da Cartella.get_griglia_semplice().

        Ritorna:
        - EventoVisualizzaCartellaSemplice pronto per essere inserito in EsitoAzione.
        """

        # Converte l'indice interno (0-based) nel numero "umano" (1-based).
        numero_cartella = indice_cartella + 1

        # Non modifichiamo griglia_semplice: assumiamo che Cartella abbia già
        # prodotto una struttura coerente (3x9, immutabile).
        return cls(
            indice_cartella=indice_cartella,
            numero_cartella=numero_cartella,
            totale_cartelle=totale_cartelle,
            griglia_semplice=griglia_semplice,
        )


@dataclass(frozen=True)
class EventoVisualizzaCartellaAvanzata:
    """
    Evento di output per la UI del giocatore umano: rappresenta la cartella
    corrente in forma "AVANZATA", con stato segnati e riepilogo numerico.

    Scopo:
    - Fornire al renderer tutti i dati per visualizzazione completa (griglia + segnati + statistiche).
    - Mantenere separati dati grezzi (qui) da presentazione (renderer + dizionario lingua).

    Convenzioni:
    - indice_cartella: 0-based (indice interno del giocatore).
    - numero_cartella: 1-based (numero "umano" per annunci).
    - griglia_semplice: 3x9 con int (numeri) o "-" (vuoti).
    - numeri_segnati_ordinati: tuple ordinata per controllo rapido "numero X è segnato?".
    - stato_cartella: dict normalizzato con tuple (immutabile) per footer riepilogo.

    Nota:
    - Il renderer combina griglia + numeri_segnati per asterischi e "Segnati: ...".
    - Numeri letti dallo screen reader nella lingua utente; parole dal dizionario.
    """

    # Identità della cartella nel contesto del giocatore umano
    indice_cartella: int
    numero_cartella: int
    totale_cartelle: int

    # Dati grezzi dalla Cartella (pacchetto completo)
    griglia_semplice: tuple[tuple[int | str, ...], ...]
    stato_cartella: dict[str, int | float | tuple[int, ...]]
    numeri_segnati_ordinati: tuple[int, ...]

    @classmethod
    def crea_da_dati_avanzati(
        cls,
        *,
        indice_cartella: int,
        totale_cartelle: int,
        dati_avanzati: tuple[
            tuple[tuple[int | str, ...], ...],      # griglia_semplice
            dict[str, int | float | tuple[int, ...]],  # stato_cartella
            tuple[int, ...]                          # numeri_segnati_ordinati
        ],
    ) -> "EventoVisualizzaCartellaAvanzata":
        """
        Factory method per creare l'evento da dati già elaborati dalla Cartella.

        Perché è utile:
        - Riceve direttamente il pacchetto da Cartella.get_dati_visualizzazione_avanzata().
        - Centralizza la logica 0-based -> 1-based (numero_cartella).
        - Garantisce che tutti i dati siano già normalizzati (tuple, immutabili).

        Parametri:
        - indice_cartella: int (0-based) della cartella in focus.
        - totale_cartelle: int, numero totale cartelle del giocatore.
        - dati_avanzati: tuple esatta da Cartella.get_dati_visualizzazione_avanzata().

        Ritorna:
        - Evento pronto per EsitoAzione(ok=True, evento=...) e renderer.
        """
        # 1) Scompone il pacchetto stabile dalla Cartella.
        griglia_semplice, stato_cartella, numeri_segnati_ordinati = dati_avanzati

        # 2) Converte indice interno (0-based) in numero "umano" (1-based).
        numero_cartella = indice_cartella + 1

        # 3) Costruisce l'evento: dati già validati/immutabili dalla Cartella.
        return cls(
            indice_cartella=indice_cartella,
            numero_cartella=numero_cartella,
            totale_cartelle=totale_cartelle,
            griglia_semplice=griglia_semplice,
            stato_cartella=stato_cartella,
            numeri_segnati_ordinati=numeri_segnati_ordinati,
        )


@dataclass(frozen=True)
class EventoVisualizzaTutteCartelleSemplice:
    """
    Evento di output per la UI del giocatore umano: rappresenta TUTTE le cartelle
    del giocatore in modalità "semplice", senza testo pronto.

    Scopo:
    - Permettere al renderer di mostrare una panoramica completa delle cartelle
      senza dover spostare il focus una per una.
    - Mantenere la separazione: qui solo dati grezzi, le stringhe sono nel dizionario lingua.

    Convenzioni:
    - totale_cartelle: numero totale di cartelle possedute.
    - cartelle: sequenza immutabile (tuple) di elementi, uno per cartella, in ordine.
      Ogni elemento è una tupla (numero_cartella, griglia_semplice) dove:
        * numero_cartella è 1-based (1..totale_cartelle),
        * griglia_semplice è 3x9 immutabile con int (numeri) o "-" (celle vuote).

    Nota:
    - L'intestazione "Cartella {numero_cartella} di {totale_cartelle}." può essere
      riutilizzata dal renderer usando i campi di questo evento.
    """

    totale_cartelle: int

    # Ogni elemento: (numero_cartella, griglia_semplice)
    cartelle: tuple[
        tuple[int, tuple[tuple[int | str, ...], ...]],
        ...
    ]

    @classmethod
    def crea_da_cartelle(
        cls,
        *,
        cartelle: Sequence[object],
    ) -> "EventoVisualizzaTutteCartelleSemplice":
        """
        Factory method per costruire l'evento da una sequenza di oggetti Cartella.

        Perché è utile:
        - Centralizza la numerazione 1-based delle cartelle (numero_cartella).
        - Estrae in modo uniforme la griglia semplice da ogni cartella.
        - Converte tutto in tuple immutabili per stabilità.

        Parametri:
        - cartelle: Sequence[Cartella]
          Sequenza di cartelle del giocatore (ordine naturale).

        Ritorna:
        - EventoVisualizzaTutteCartelleSemplice pronto per EsitoAzione.
        """
        totale_cartelle = len(cartelle)

        # Costruisce la sequenza immutabile (numero_cartella, griglia_semplice)
        # in modo coerente e prevedibile.
        cartelle_out = []
        for indice, cartella in enumerate(cartelle):
            numero_cartella = indice + 1

            # La Cartella espone già la griglia semplice come tuple immutabile.
            griglia_semplice = cartella.get_griglia_semplice()

            cartelle_out.append((numero_cartella, griglia_semplice))

        return cls(
            totale_cartelle=totale_cartelle,
            cartelle=tuple(cartelle_out),
        )


from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class EventoVisualizzaTutteCartelleAvanzata:
    """
    Evento di output per la UI del giocatore umano: rappresenta TUTTE le cartelle
    del giocatore in modalità "AVANZATA", senza produrre stringhe pronte.

    Scopo:
    - Permettere al renderer di costruire l'output avanzato (intestazione, righe con stato,
      riepilogo finale) per tutte le cartelle, in sequenza.
    - Mantenere separati i dati grezzi (qui) dalla presentazione (renderer + dizionario lingua).

    Convenzioni:
    - totale_cartelle: numero totale di cartelle possedute.
    - cartelle: sequenza immutabile (tuple) di elementi, uno per cartella, in ordine.
      Ogni elemento è una tupla a 4 componenti:
        1) numero_cartella: int (1-based, 1..totale_cartelle)
        2) griglia_semplice: 3x9 con int (numeri) o "-" (celle vuote)
        3) stato_cartella: dict normalizzato (solo valori primitivi o tuple)
        4) numeri_segnati_ordinati: tuple[int, ...] ordinata

    Nota:
    - I dati 2), 3), 4) arrivano ESATTAMENTE da Cartella.get_dati_visualizzazione_avanzata().
    - L'evento non dipende da altri eventi: è completamente autonomo e piatto.
    """

    totale_cartelle: int

    # Ogni elemento:
    # (numero_cartella, griglia_semplice, stato_cartella, numeri_segnati_ordinati)
    cartelle: tuple[
        tuple[
            int,
            tuple[tuple[int | str, ...], ...],
            dict[str, int | float | tuple[int, ...]],
            tuple[int, ...],
        ],
        ...
    ]

    @classmethod
    def crea_da_cartelle(
        cls,
        *,
        cartelle: Sequence[object],
    ) -> "EventoVisualizzaTutteCartelleAvanzata":
        """
        Factory method per costruire l'evento da una sequenza di oggetti Cartella.

        Perché è utile:
        - Centralizza la numerazione 1-based delle cartelle (numero_cartella).
        - Estrae in modo uniforme i dati avanzati da ogni cartella, senza produrre testo.
        - Converte la collezione finale in tuple immutabile per stabilità.

        Parametri:
        - cartelle: Sequence[Cartella]
          Sequenza di cartelle del giocatore (ordine naturale).

        Ritorna:
        - EventoVisualizzaTutteCartelleAvanzata pronto per EsitoAzione e renderer.
        """
        # 1) Metadato globale: serve al renderer per intestazioni coerenti.
        totale_cartelle = len(cartelle)

        # 2) Costruisce la sequenza "piatta" delle cartelle avanzate.
        cartelle_out: list[
            tuple[
                int,
                tuple[tuple[int | str, ...], ...],
                dict[str, int | float | tuple[int, ...]],
                tuple[int, ...],
            ]
        ] = []

        for indice, cartella in enumerate(cartelle):
            # 2a) Numero "umano" 1-based.
            numero_cartella = indice + 1

            # 2b) Dati avanzati completi (griglia, stato normalizzato, segnati ordinati).
            griglia_semplice, stato_cartella, numeri_segnati_ordinati = (
                cartella.get_dati_visualizzazione_avanzata()
            )

            # 2c) Salva il pacchetto come tupla piatta, coerente con gli altri eventi "bulk".
            cartelle_out.append(
                (
                    numero_cartella,
                    griglia_semplice,
                    stato_cartella,
                    numeri_segnati_ordinati,
                )
            )

        # 3) Crea l'evento finale con strutture immutabili (tuple).
        return cls(
            totale_cartelle=totale_cartelle,
            cartelle=tuple(cartelle_out),
        )


@dataclass(frozen=True)
class EventoNavigazioneRiga:
    """
    Evento di output per UI/renderer: rappresenta l'esito di un comando di
    navigazione sulle righe della cartella in focus.

    Obiettivo:
    - Sostituire i metodi che ritornano stringhe (sposta riga su/giù) con un evento.
    - Permettere al renderer di produrre:
      * la lettura della riga selezionata (caso "mostra")
      * un feedback breve di limite (caso "limite")

    Scelte di coerenza con il progetto:
    - Un solo evento per "precedente" e "successiva": cambia la direzione, non cambia
      la struttura dei dati.
    - Nessun testo pronto: le frasi verranno prese dal dizionario lingua nel renderer.
    - Evento immutabile: i dati non devono essere modificati dopo la creazione.

    Convenzioni:
    - numero_cartella_corrente: 1-based (quello che l'utente vede).
    - numero_riga_corrente: 1-based (1..totale_righe).
    - riga_semplice: presente solo quando esito="mostra".
      È una tupla di 9 celle con int (numeri) oppure "-" (vuoti).
    - limite: presente solo quando esito="limite" (minimo o massimo).

    Nota:
    - Questo evento NON gestisce la pre-condizione di navigazione (cartella mancante, ecc.).
      Se il giocatore non è pronto per navigare, il metodo chiamante ritorna l'errore e
      non crea eventi (stile già usato nel resto del progetto).
    """

    # Contesto giocatore (utile per UI future o log multi-giocatore)
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Da quale comando arriva l'evento
    direzione: Direzione_Navigazione_Righe 

    # Che tipo di esito si è verificato
    esito: Esito_Navigazione_Riga

    # Contesto cartella in focus
    totale_cartelle: int
    numero_cartella_corrente: int

    # Contesto righe
    totale_righe: int
    numero_riga_corrente: int

    # Dati riga (solo per esito="mostra")
    riga_semplice: Optional[tuple[int | str, ...]]

    # Dati limite (solo per esito="limite")
    limite: Optional[Tipo_Limite_Navigazione_Righe]

    @classmethod
    def mostra_riga(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Righe,
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_righe: int,
        indice_riga_corrente: int,
        riga_semplice: tuple[int | str, ...],
    ) -> "EventoNavigazioneRiga":
        """
        Costruttore comodo per il caso "mostra".

        Quando si usa:
        - Primo utilizzo (focus riga era None): si inizializza alla riga 0 e si mostra.
        - Spostamento riuscito: si aggiorna l'indice riga e si mostra la nuova riga.

        Cosa garantisce:
        - Converte la riga 0-based (interna) in numero 1-based (umano).
        - Imposta limite=None perché non è un caso di autolimite.
        """
        # 1) Conversione coerente: 0-based interno -> 1-based per la UI.
        numero_riga_corrente = indice_riga_corrente + 1

        # 2) Evento "mostra": contiene anche i dati della riga.
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            esito="mostra",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            numero_riga_corrente=numero_riga_corrente,
            riga_semplice=riga_semplice,
            limite=None,
        )

    @classmethod
    def limite_minimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Righe,
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_righe: int,
    ) -> "EventoNavigazioneRiga":
        """
        Costruttore comodo per il caso: limite minimo (prima riga).

        Quando si usa:
        - Se l'utente chiede "precedente" ma la riga in focus è già la prima.

        Nota UI:
        - Il messaggio deve essere breve (scelta coerente per screen reader).
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            esito="limite",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            numero_riga_corrente=1,
            riga_semplice=None,
            limite="minimo",
        )

    @classmethod
    def limite_massimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Righe,
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_righe: int,
    ) -> "EventoNavigazioneRiga":
        """
        Costruttore comodo per il caso: limite massimo (ultima riga).

        Quando si usa:
        - Se l'utente chiede "successiva" ma la riga in focus è già l'ultima.

        Nota UI:
        - Il messaggio deve essere breve (scelta coerente per screen reader).
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            esito="limite",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            numero_riga_corrente=totale_righe,
            riga_semplice=None,
            limite="massimo",
        )


@dataclass(frozen=True)
class EventoNavigazioneRigaAvanzata:
    """
    Evento di output per UI/renderer: rappresenta l'esito di un comando di navigazione
    sulle righe della cartella in focus, in modalità "AVANZATA".

    Obiettivo:
    - Sostituire i metodi che ritornano stringhe (sposta riga su/giù avanzata) con un evento.
    - Permettere al renderer di produrre:
      * la lettura della riga selezionata con stato (caso "mostra")
      * un feedback breve di limite (caso "limite")

    Principio importante (coerenza del progetto):
    - L'evento non contiene oggetti Cartella e non chiama metodi della Cartella.
      Riceve solo dati già pronti (tipicamente dal metodo Cartella.get_dati_visualizzazione_riga_avanzata()).
    - Nessun testo pronto: le frasi arrivano dal dizionario lingua nel renderer.
    - Evento immutabile: i dati non devono essere modificati dopo la creazione. [web:28]

    Convenzioni:
    - numero_cartella_corrente: 1-based (quello che l'utente vede).
    - numero_riga_corrente: 1-based (1..totale_righe).
    - riga_semplice: presente solo quando esito="mostra".
      È una tupla di 9 celle con int (numeri) oppure "-" (vuoti).
    - stato_riga: presente solo quando esito="mostra".
      È un dict normalizzato (liste convertite in tuple) con totali/segnati/percentuale.
    - numeri_segnati_riga_ordinati: presente solo quando esito="mostra".
      È una tupla ordinata dei numeri segnati presenti nella riga.
    - limite: presente solo quando esito="limite" (minimo o massimo).
    """

    # Contesto giocatore (utile per UI future o log multi-giocatore)
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Da quale comando arriva l'evento
    direzione: Direzione_Navigazione_Righe

    # Che tipo di esito si è verificato
    esito: Esito_Navigazione_Riga

    # Contesto cartella in focus
    totale_cartelle: int
    numero_cartella_corrente: int

    # Contesto righe
    totale_righe: int
    numero_riga_corrente: int

    # Dati riga (solo per esito="mostra")
    riga_semplice: Optional[tuple[int | str, ...]]
    stato_riga: Optional[dict[str, int | float | tuple[int, ...]]]
    numeri_segnati_riga_ordinati: Optional[tuple[int, ...]]

    # Dati limite (solo per esito="limite")
    limite: Optional[Tipo_Limite_Navigazione_Righe]

    @classmethod
    def mostra_riga(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Righe,
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_righe: int,
        indice_riga_corrente: int,
        dati_riga_avanzati: tuple[
            tuple[int | str, ...],
            dict[str, int | float | tuple[int, ...]],
            tuple[int, ...],
        ],
    ) -> "EventoNavigazioneRigaAvanzata":
        """
        Costruttore comodo per il caso "mostra".

        Quando si usa:
        - Primo utilizzo (focus riga era None): si inizializza alla riga 0 e si mostra.
        - Spostamento riuscito: si aggiorna l'indice riga e si mostra la nuova riga.

        Perché è stabile:
        - Riceve un pacchetto dati già pronto dalla Cartella (nessun accesso alla Cartella qui).
        - Centralizza la conversione 0-based -> 1-based (numero_riga_corrente).
        """
        # 1) Scompone il pacchetto dati (tutto già pronto per il renderer).
        riga_semplice, stato_riga, numeri_segnati_riga_ordinati = dati_riga_avanzati

        # 2) Conversione coerente: 0-based interno -> 1-based per la UI.
        numero_riga_corrente = indice_riga_corrente + 1

        # 3) Evento "mostra": contiene i dati necessari per rendere la riga in modo avanzato.
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            esito="mostra",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            numero_riga_corrente=numero_riga_corrente,
            riga_semplice=riga_semplice,
            stato_riga=stato_riga,
            numeri_segnati_riga_ordinati=numeri_segnati_riga_ordinati,
            limite=None,
        )

    @classmethod
    def limite_minimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Righe,
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_righe: int,
    ) -> "EventoNavigazioneRigaAvanzata":
        """
        Costruttore comodo per il caso: limite minimo (prima riga).

        Output UI:
        - Deve essere breve (scelta coerente per screen reader).
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            esito="limite",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            numero_riga_corrente=1,
            riga_semplice=None,
            stato_riga=None,
            numeri_segnati_riga_ordinati=None,
            limite="minimo",
        )

    @classmethod
    def limite_massimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Righe,
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_righe: int,
    ) -> "EventoNavigazioneRigaAvanzata":
        """
        Costruttore comodo per il caso: limite massimo (ultima riga).

        Output UI:
        - Deve essere breve (scelta coerente per screen reader).
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            esito="limite",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_righe=totale_righe,
            numero_riga_corrente=totale_righe,
            riga_semplice=None,
            stato_riga=None,
            numeri_segnati_riga_ordinati=None,
            limite="massimo",
        )
