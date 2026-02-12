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
    "EventoNavigazioneColonna",
    "EventoNavigazioneColonnaAvanzata",
    "EventoSegnazioneNumero",
    "RisultatoRicercaNumeroInCartella",
    "EventoRicercaNumeroInCartelle",
    "EventoVerificaNumeroEstratto",
    "EventoUltimoNumeroEstratto",
    "EventoUltimiNumeriEstratti",
    "EventoRiepilogoTabellone",
    "EventoListaNumeriEstratti",
    "EventoStatoFocusCorrente",
    "EventoVaiARigaAvanzata",
    "EventoVaiAColonnaAvanzata",
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

Direzione_Navigazione_Colonne = Literal[
    "sinistra",
    "destra",
]

Tipo_Limite_Navigazione_Colonne = Literal[
    "minimo",
    "massimo",
]

Esito_Navigazione_Colonna = Literal[
    "mostra",
    "limite",
]

Esito_Segnazione_Numero = Literal[
    "segnato",
    "gia_segnato",
    "non_presente",
    "non_estratto",
]

# Esito della ricerca: azione valida, ma con due possibili risultati logici.
Esito_Ricerca_Numero = Literal[
    "trovato",
    "non_trovato"
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


@dataclass(frozen=True)
class EventoNavigazioneColonna:
    """
    Evento di output per UI/renderer: rappresenta l'esito di un comando di navigazione
    sulle colonne della cartella in focus, in modalità "SEMPLICE".

    Obiettivo:
    - Sostituire i metodi che ritornano stringhe (sposta colonna sinistra/destra)
      con un evento stabile.
    - Permettere al renderer di produrre:
      * la lettura della colonna selezionata (caso "mostra")
      * un feedback breve di limite (caso "limite")

    Scelte di coerenza con il progetto:
    - Un solo evento per sinistra e destra: cambia la direzione, non cambia la struttura dati. [file:118]
    - Nessun testo pronto: le frasi verranno prese dal dizionario lingua nel renderer. [file:118]
    - Evento immutabile: i dati non devono essere modificati dopo la creazione. [web:28]

    Convenzioni:
    - numero_cartella_corrente: 1-based (quello che l'utente vede).
    - numero_colonna_corrente: 1-based (1..totale_colonne).
    - colonna_semplice: presente solo quando esito="mostra".
      È una tupla di 3 celle (una per riga, dall'alto verso il basso) con:
        * int se c'è un numero
        * "-" se la cella è vuota
    - limite: presente solo quando esito="limite" (minimo o massimo).
    """

    # Contesto giocatore (utile per UI future o log)
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Da quale comando arriva l'evento
    direzione: Direzione_Navigazione_Colonne

    # Che tipo di esito si è verificato
    esito: Esito_Navigazione_Colonna

    # Contesto cartella in focus
    totale_cartelle: int
    numero_cartella_corrente: int

    # Contesto colonne
    totale_colonne: int
    numero_colonna_corrente: int

    # Dati colonna (solo per esito="mostra")
    colonna_semplice: Optional[tuple[int | str, ...]]

    # Dati limite (solo per esito="limite")
    limite: Optional[Tipo_Limite_Navigazione_Colonne]

    @classmethod
    def mostra_colonna(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Colonne,
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_colonne: int,
        indice_colonna_corrente: int,
        colonna_semplice: tuple[int | str, ...],
    ) -> "EventoNavigazioneColonna":
        """
        Costruttore comodo per il caso "mostra".

        Quando si usa:
        - Primo utilizzo (focus colonna era None): si inizializza alla colonna 0 e si mostra.
        - Spostamento riuscito: si aggiorna l'indice colonna e si mostra la nuova colonna.

        Cosa garantisce:
        - Converte l'indice 0-based interno in numero 1-based per la UI.
        - Non fa chiamate alla Cartella: riceve solo dati già pronti.
        """
        # Conversione coerente: 0-based interno -> 1-based per la UI.
        numero_colonna_corrente = indice_colonna_corrente + 1

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            esito="mostra",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_colonne=totale_colonne,
            numero_colonna_corrente=numero_colonna_corrente,
            colonna_semplice=colonna_semplice,
            limite=None,
        )

    @classmethod
    def limite_minimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Colonne,
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_colonne: int,
    ) -> "EventoNavigazioneColonna":
        """
        Costruttore comodo per il caso: limite minimo (prima colonna).

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
            totale_colonne=totale_colonne,
            numero_colonna_corrente=1,
            colonna_semplice=None,
            limite="minimo",
        )

    @classmethod
    def limite_massimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: Direzione_Navigazione_Colonne,
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_colonne: int,
    ) -> "EventoNavigazioneColonna":
        """
        Costruttore comodo per il caso: limite massimo (ultima colonna).

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
            totale_colonne=totale_colonne,
            numero_colonna_corrente=totale_colonne,
            colonna_semplice=None,
            limite="massimo",
        )


@dataclass(frozen=True)
class EventoNavigazioneColonnaAvanzata:
    """
    Evento di output per UI/renderer: rappresenta l'esito di un comando di navigazione
    sulle colonne della cartella in focus, in modalità "AVANZATA".

    Obiettivo:
    - Sostituire i metodi che ritornano stringhe (sposta colonna sinistra/destra avanzata)
      con un evento stabile.
    - Permettere al renderer di produrre:
      * la lettura della colonna selezionata con stato (caso "mostra")
      * un feedback breve di limite (caso "limite")

    Principio importante (coerenza del progetto):
    - L'evento non contiene oggetti Cartella e non chiama metodi della Cartella.
      Riceve solo dati già pronti (tipicamente dal metodo Cartella.get_dati_visualizzazione_colonna_avanzata()).
    - Nessun testo pronto: le frasi arrivano dal dizionario lingua nel renderer.
    - Evento immutabile: i dati non devono essere modificati dopo la creazione. [web:28]

    Convenzioni:
    - numero_cartella_corrente: 1-based (quello che l'utente vede).
    - numero_colonna_corrente: 1-based (1..totale_colonne).
    - colonna_semplice: presente solo quando esito="mostra".
      È una tupla di 3 celle con int (numeri) oppure "-" (vuoti), dall'alto verso il basso.
    - stato_colonna: presente solo quando esito="mostra".
      È un dict normalizzato (liste convertite in tuple) con totali/segnati/percentuale.
    - numeri_segnati_colonna_ordinati: presente solo quando esito="mostra".
      È una tupla ordinata dei numeri segnati presenti nella colonna.
    - limite: presente solo quando esito="limite" (minimo o massimo).
    """

    # Contesto giocatore (utile per UI future o log multi-giocatore)
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Da quale comando arriva l'evento
    direzione: "Direzione_Navigazione_Colonne"

    # Che tipo di esito si è verificato
    esito: "Esito_Navigazione_Colonna"

    # Contesto cartella in focus
    totale_cartelle: int
    numero_cartella_corrente: int

    # Contesto colonne
    totale_colonne: int
    numero_colonna_corrente: int

    # Dati colonna (solo per esito="mostra")
    colonna_semplice: Optional[tuple[int | str, ...]]
    stato_colonna: Optional[dict[str, int | float | tuple[int, ...]]]
    numeri_segnati_colonna_ordinati: Optional[tuple[int, ...]]

    # Dati limite (solo per esito="limite")
    limite: Optional["Tipo_Limite_Navigazione_Colonne"]

    @classmethod
    def mostra_colonna(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: "Direzione_Navigazione_Colonne",
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_colonne: int,
        indice_colonna_corrente: int,
        dati_colonna_avanzati: tuple[
            tuple[int | str, ...],
            dict[str, int | float | tuple[int, ...]],
            tuple[int, ...],
        ],
    ) -> "EventoNavigazioneColonnaAvanzata":
        """
        Costruttore comodo per il caso "mostra".

        Quando si usa:
        - Primo utilizzo (focus colonna era None): si inizializza alla colonna 0 e si mostra.
        - Spostamento riuscito: si aggiorna l'indice colonna e si mostra la nuova colonna.

        Perché è stabile:
        - Riceve un pacchetto dati già pronto dalla Cartella (nessun accesso alla Cartella qui).
        - Centralizza la conversione 0-based -> 1-based (numero_colonna_corrente).
        """
        # 1) Scompone il pacchetto dati (tutto già pronto per il renderer).
        colonna_semplice, stato_colonna, numeri_segnati_colonna_ordinati = dati_colonna_avanzati

        # 2) Conversione coerente: 0-based interno -> 1-based per la UI.
        numero_colonna_corrente = indice_colonna_corrente + 1

        # 3) Evento "mostra": contiene i dati necessari per rendere la colonna in modo avanzato.
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            direzione=direzione,
            esito="mostra",
            totale_cartelle=totale_cartelle,
            numero_cartella_corrente=numero_cartella_corrente,
            totale_colonne=totale_colonne,
            numero_colonna_corrente=numero_colonna_corrente,
            colonna_semplice=colonna_semplice,
            stato_colonna=stato_colonna,
            numeri_segnati_colonna_ordinati=numeri_segnati_colonna_ordinati,
            limite=None,
        )

    @classmethod
    def limite_minimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: "Direzione_Navigazione_Colonne",
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_colonne: int,
    ) -> "EventoNavigazioneColonnaAvanzata":
        """
        Costruttore comodo per il caso: limite minimo (prima colonna).

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
            totale_colonne=totale_colonne,
            numero_colonna_corrente=1,
            colonna_semplice=None,
            stato_colonna=None,
            numeri_segnati_colonna_ordinati=None,
            limite="minimo",
        )

    @classmethod
    def limite_massimo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        direzione: "Direzione_Navigazione_Colonne",
        totale_cartelle: int,
        numero_cartella_corrente: int,
        totale_colonne: int,
    ) -> "EventoNavigazioneColonnaAvanzata":
        """
        Costruttore comodo per il caso: limite massimo (ultima colonna).

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
            totale_colonne=totale_colonne,
            numero_colonna_corrente=totale_colonne,
            colonna_semplice=None,
            stato_colonna=None,
            numeri_segnati_colonna_ordinati=None,
            limite="massimo",
        )


@dataclass(frozen=True)
class EventoSegnazioneNumero:
    """
    Evento di output (dati grezzi) che rappresenta l'esito del tentativo di segnare
    un numero sulla cartella attualmente in focus.

    Scopo:
    - Fornire al renderer tutte le informazioni necessarie per un feedback breve e stabile
      (numero, esito, coordinate, progresso), senza produrre stringhe.
    - Mantenere la coerenza con gli altri eventi: dati immutabili, convenzioni chiare,
      conversioni centralizzate tramite factory method.

    Cosa NON gestisce volutamente:
    - Errori tecnici (es. tabellone mancante/non valido).
    - Precondizioni (es. focus cartella non impostato).
    Questi aspetti vanno gestiti a livello più alto (EsitoAzione/errori), prima di creare l'evento.

    Convenzioni:
    - indice_cartella, indice_riga, indice_colonna sono 0-based (interni).
    - numero_cartella è 1-based (umano), calcolato dai factory method.
    - Le coordinate (riga/colonna) sono presenti solo quando l'esito le rende significative.
    """

    # Contesto giocatore (utile per log / statistiche / multi-giocatore)
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Esito e numero coinvolto
    esito: Esito_Segnazione_Numero
    numero: int

    # Contesto cartella
    indice_cartella: int           # 0-based
    numero_cartella: int           # 1-based
    totale_cartelle: int

    # Coordinate del numero (solo quando applicabile)
    indice_riga: Optional[int]     # 0-based
    indice_colonna: Optional[int]  # 0-based

    # Progresso della cartella (dopo il tentativo di segnatura)
    numeri_segnati: int
    totale_numeri: int
    mancanti: int
    percentuale: float

    @classmethod
    def segnato(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero: int,
        indice_cartella: int,
        totale_cartelle: int,
        indice_riga: int,
        indice_colonna: int,
        numeri_segnati: int,
        totale_numeri: int,
        percentuale: float,
    ) -> "EventoSegnazioneNumero":
        """
        Costruttore comodo per il caso in cui il numero viene segnato con successo.
        Include coordinate e progresso aggiornato.
        """
        numero_cartella = indice_cartella + 1
        mancanti = totale_numeri - numeri_segnati

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            esito="segnato",
            numero=numero,
            indice_cartella=indice_cartella,
            numero_cartella=numero_cartella,
            totale_cartelle=totale_cartelle,
            indice_riga=indice_riga,
            indice_colonna=indice_colonna,
            numeri_segnati=numeri_segnati,
            totale_numeri=totale_numeri,
            mancanti=mancanti,
            percentuale=percentuale,
        )

    @classmethod
    def gia_segnato(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero: int,
        indice_cartella: int,
        totale_cartelle: int,
        indice_riga: int,
        indice_colonna: int,
        numeri_segnati: int,
        totale_numeri: int,
        percentuale: float,
    ) -> "EventoSegnazioneNumero":
        """
        Costruttore comodo per il caso in cui il numero era già segnato.
        Include coordinate (utile per feedback) e progresso invariato.
        """
        numero_cartella = indice_cartella + 1
        mancanti = totale_numeri - numeri_segnati

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            esito="gia_segnato",
            numero=numero,
            indice_cartella=indice_cartella,
            numero_cartella=numero_cartella,
            totale_cartelle=totale_cartelle,
            indice_riga=indice_riga,
            indice_colonna=indice_colonna,
            numeri_segnati=numeri_segnati,
            totale_numeri=totale_numeri,
            mancanti=mancanti,
            percentuale=percentuale,
        )

    @classmethod
    def non_presente(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero: int,
        indice_cartella: int,
        totale_cartelle: int,
        numeri_segnati: int,
        totale_numeri: int,
        percentuale: float,
    ) -> "EventoSegnazioneNumero":
        """
        Costruttore comodo per il caso in cui il numero non è presente nella cartella.
        Le coordinate non sono disponibili perché il numero non ha posizione nella matrice.
        """
        numero_cartella = indice_cartella + 1
        mancanti = totale_numeri - numeri_segnati

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            esito="non_presente",
            numero=numero,
            indice_cartella=indice_cartella,
            numero_cartella=numero_cartella,
            totale_cartelle=totale_cartelle,
            indice_riga=None,
            indice_colonna=None,
            numeri_segnati=numeri_segnati,
            totale_numeri=totale_numeri,
            mancanti=mancanti,
            percentuale=percentuale,
        )

    @classmethod
    def non_estratto(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero: int,
        indice_cartella: int,
        totale_cartelle: int,
        numeri_segnati: int,
        totale_numeri: int,
        percentuale: float,
    ) -> "EventoSegnazioneNumero":
        """
        Costruttore comodo per il caso in cui il numero non è ancora stato estratto.
        Le coordinate vengono lasciate a None perché non è stata effettuata (o non serve) la ricerca nella matrice.
        """
        numero_cartella = indice_cartella + 1
        mancanti = totale_numeri - numeri_segnati

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            esito="non_estratto",
            numero=numero,
            indice_cartella=indice_cartella,
            numero_cartella=numero_cartella,
            totale_cartelle=totale_cartelle,
            indice_riga=None,
            indice_colonna=None,
            numeri_segnati=numeri_segnati,
            totale_numeri=totale_numeri,
            mancanti=mancanti,
            percentuale=percentuale,
        )


@dataclass(frozen=True)
class RisultatoRicercaNumeroInCartella:
    """
    Dato grezzo che descrive DOVE si trova un numero in UNA specifica cartella.

    Scopo:
    - Incapsulare le info utili al renderer senza produrre testo pronto.
    - Tenere separate: (1) la ricerca e (2) la formattazione del report.

    Convenzioni:
    - Tutti gli indici (indice_cartella, indice_riga, indice_colonna) sono 0-based.
    - numero_cartella è 1-based (quello che l'utente si aspetta di sentire/leggere).
    """

    # Identità cartella: indice interno e numero umano.
    indice_cartella: int
    numero_cartella: int

    # Coordinate del numero, 0-based, ottenute dalla Cartella (dato grezzo).
    indice_riga: int
    indice_colonna: int

    # Stato: True se già segnato, False se non segnato.
    segnato: bool

    @classmethod
    def crea(
        cls,
        *,
        indice_cartella: int,
        indice_riga: int,
        indice_colonna: int,
        segnato: bool,
    ) -> RisultatoRicercaNumeroInCartella:
        """
        Factory method per creare un risultato in modo uniforme.

        Perché esiste:
        - Centralizza la conversione indice (0-based) -> numero (1-based) per la cartella.
        - Evita che il chiamante debba calcolare numero_cartella a mano.
        """
        numero_cartella = indice_cartella + 1  # Convenzione coerente con gli altri eventi.
        return cls(
            indice_cartella=indice_cartella,
            numero_cartella=numero_cartella,
            indice_riga=indice_riga,
            indice_colonna=indice_colonna,
            segnato=segnato,
        )


@dataclass(frozen=True)
class EventoRicercaNumeroInCartelle:
    """
    Evento di output per UI/renderer: esito della ricerca di un numero
    in TUTTE le cartelle del giocatore umano.

    Obiettivo:
    - Nessun testo pronto: il renderer userà dizionario lingua e regole UI.
    - Contratto stabile: dati sufficienti sia per output breve sia per output dettagliato.

    Cosa NON gestisce volutamente:
    - Errori tecnici / precondizioni (numero non valido, nessuna cartella assegnata).
      Questi casi devono essere gestiti prima e ritornati come EsitoAzione ok=False
      con codice errore (come fai nel resto del progetto).
    """

    # Identità giocatore (utile per UI future o log; coerente con altri eventi).
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Numero cercato (input valido già verificato a monte).
    numero: int

    # Contesto globale: quante cartelle possiede il giocatore.
    totale_cartelle: int

    # Esito logico della ricerca.
    esito: Esito_Ricerca_Numero

    # Risultati (uno per cartella trovata). Vuoto se non_trovato.
    risultati: tuple[RisultatoRicercaNumeroInCartella, ...]

    @classmethod
    def non_trovato(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero: int,
        totale_cartelle: int,
    ) -> EventoRicercaNumeroInCartelle:
        """
        Costruttore comodo: ricerca valida, ma il numero non è presente in nessuna cartella.

        Nota:
        - risultati è una tupla vuota (immutabile e facile da testare).
        - esito è 'non_trovato' (il renderer non deve dedurre l'esito).
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            numero=numero,
            totale_cartelle=totale_cartelle,
            esito="non_trovato",
            risultati=(),
        )

    @classmethod
    def trovato(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero: int,
        totale_cartelle: int,
        risultati: Sequence[RisultatoRicercaNumeroInCartella],
    ) -> EventoRicercaNumeroInCartelle:
        """
        Costruttore comodo: numero trovato in una o più cartelle.

        Stabilità / coerenza:
        - Converte la sequenza in tupla immutabile (evento frozen).
        - Ordina per indice_cartella per avere output deterministico (utile per test e screen reader).

        Nota:
        - Qui non facciamo validazioni "di dominio" complesse: le precondizioni sono già state fatte.
        - Se per qualche motivo risultati arrivasse vuoto, l'esito resterebbe 'trovato':
          per questo è consigliato costruire questo evento solo quando c'è almeno 1 risultato.
        """
        risultati_ordinati = tuple(sorted(risultati, key=lambda r: r.indice_cartella))
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            numero=numero,
            totale_cartelle=totale_cartelle,
            esito="trovato",
            risultati=risultati_ordinati,
        )


@dataclass(frozen=True)
class EventoVerificaNumeroEstratto:
    """
    Evento di output per UI/renderer: risponde alla domanda
    "il numero X è già stato estratto?".

    Obiettivo di stabilità (coerente con gli altri eventi UI umani):
    - Nessun testo pronto dentro il dominio.
    - L'evento contiene solo i dati minimi e neutrali.
    - La UI sceglie lingua, tono e verbosità tramite dizionario e renderer.

    Nota:
    - Questo evento NON valida il range del numero e NON valida l'esistenza del tabellone.
      Tali controlli vengono gestiti nel metodo del GiocatoreUmano prima di creare l'evento.
    """

    # Contesto giocatore: utile per log/UI multi-giocatore e coerenza con gli altri eventi.
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Dato richiesto dall'utente.
    numero: int

    # Esito della verifica sul tabellone: True se estratto, False se non ancora estratto.
    estratto: bool

    @classmethod
    def estratto_si(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero: int,
    ) -> "EventoVerificaNumeroEstratto":
        """
        Factory method per il caso "numero estratto".

        Perché esiste:
        - Centralizza la costruzione dell'evento.
        - Rende più leggibile l'intento nel chiamante (GiocatoreUmano).
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            numero=numero,
            estratto=True,
        )

    @classmethod
    def estratto_no(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero: int,
    ) -> "EventoVerificaNumeroEstratto":
        """
        Factory method per il caso "numero non estratto".

        Perché esiste:
        - Simmetrico a estratto_si.
        - Evita booleani “sparsi” e riduce gli errori di chiamata.
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            numero=numero,
            estratto=False,
        )


@dataclass(frozen=True)
class EventoUltimoNumeroEstratto:
    """
    Evento di output per UI/renderer: comunica l'ultimo numero estratto dal tabellone.

    Obiettivo (coerente con gli altri eventi UI umani):
    - Nessun testo pronto dentro il dominio: il renderer userà un dizionario lingua.
    - Evento piccolo e stabile: contiene solo i dati necessari a vocalizzare la risposta.
    - Immutabile: i consumer non devono poter modificare i dati dopo la creazione.

    Nota importante:
    - Questo evento NON valida la presenza del tabellone e NON gestisce stati "partita non avviata".
      Le precondizioni vengono gestite nel metodo chiamante (GiocatoreUmano / controller comandi).
    """

    # Contesto giocatore: coerente con gli altri eventi di output.
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Ultimo numero estratto:
    # - int  -> esiste almeno una estrazione.
    # - None -> nessuna estrazione ancora.
    ultimo_numero: Optional[int]

    @classmethod
    def numero_presente(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        ultimo_numero: int,
    ) -> "EventoUltimoNumeroEstratto":
        """
        Factory method per il caso positivo: esiste un ultimo numero estratto.

        Perché è utile:
        - Rende esplicita l'intenzione nel chiamante.
        - Riduce il rischio di costruire eventi incoerenti (es. dimenticare il valore).
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            ultimo_numero=ultimo_numero,
        )

    @classmethod
    def nessuna_estrazione(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
    ) -> "EventoUltimoNumeroEstratto":
        """
        Factory method per il caso negativo: nessuna estrazione effettuata finora.

        Scelta di design:
        - Usiamo ultimonumero=None per rappresentare "non disponibile" senza aggiungere altri campi.
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            ultimo_numero=None,
        )


@dataclass(frozen=True)
class EventoUltimiNumeriEstratti:
    """
    Evento di output per UI/renderer: comunica gli ultimi numeri estratti dal tabellone.

    Scopo:
    - Permettere al renderer (e allo screen reader) di vocalizzare rapidamente
      gli ultimi numeri usciti, utile quando l'utente si distrae o rientra in partita.

    Principi di coerenza/stabilità (come gli altri eventi UI umani):
    - Nessun testo pronto nel dominio: il renderer userà un dizionario lingua.
    - Evento compatto: solo dati necessari.
    - Dati immutabili: tuple per evitare modifiche accidentali lato consumer.

    Nota di dominio:
    - In questa fase NON esiste un input utente "quanti numeri vuoi vedere":
      la logica del tabellone ritorna fino a un massimo fisso (es. 5).
    """

    # Contesto giocatore (coerente con gli altri eventi).
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Massimo richiesto dalla logica (in questa fase è fisso, tipicamente 5).
    # Tenerlo nell'evento aiuta la UI a costruire frasi coerenti (es. "ultimi 5").
    richiesti: int

    # Numeri effettivamente disponibili, nell'ordine in cui vuoi vocalizzarli.
    # Convenzione: questa tupla viene fornita già nell'ordine di estrazione
    # deciso dal tabellone (e quindi non viene riordinata qui).
    numeri: tuple[int, ...]

    # Quanti numeri stai per visualizzare/vocalizzare (0..richiesti).
    # È ridondante rispetto a len(numeri), ma lo includiamo per delegare meno al renderer.
    visualizzati: int

    @classmethod
    def crea_con_numeri(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        richiesti: int,
        numeri: Sequence[int],
    ) -> "EventoUltimiNumeriEstratti":
        """
        Factory method per il caso in cui esista almeno un numero da mostrare.

        Perché usare una factory:
        - Converte sempre in tuple immutabile.
        - Calcola visualizzati in modo coerente.
        - Centralizza eventuali controlli di coerenza (es. non superare richiesti).
        """
        numeri_out = tuple(numeri)

        # Stabilità: ci si aspetta che il tabellone rispetti già la regola "fino a richiesti".
        # Tuttavia, il controllo difensivo evita eventi incoerenti in caso di bug a monte.
        if len(numeri_out) > richiesti:
            numeri_out = numeri_out[-richiesti:]

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            richiesti=richiesti,
            numeri=numeri_out,
            visualizzati=len(numeri_out),
        )

    @classmethod
    def nessuna_estrazione(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        richiesti: int,
    ) -> "EventoUltimiNumeriEstratti":
        """
        Factory method per il caso in cui non sia stato estratto ancora nulla.

        Scelta di design:
        - numeri=() comunica "nessun dato" senza Optional.
        - visualizzati=0 è esplicito (e non lascia lavoro al renderer).
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            richiesti=richiesti,
            numeri=(),
            visualizzati=0,
        )


@dataclass(frozen=True)
class EventoRiepilogoTabellone:
    """
    Evento di output per la UI del giocatore umano: riepilogo globale del tabellone.

    Obiettivi (coerenti con gli altri eventi UI):
    - Nessun testo pronto: il renderer decide lingua e formato.
    - Dati neutrali e stabili: solo primitivi e tuple immutabili.
    - Non includere liste complete (troppo verbose); solo contatori e ultimi estratti.

    Convenzioni:
    - percentuale_estrazione è un numero (0.0-100.0); il renderer decide la formattazione.
    - ultimi_estratti è in ordine temporale (dal più vecchio al più recente).
    """

    # Contesto giocatore (utile per UI future / log multi-giocatore)
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Statistiche globali
    totale_numeri: int
    totale_estratti: int
    totale_mancanti: int
    percentuale_estrazione: float

    # Cronologia recente (non verbosa)
    ultimi_estratti: tuple[int, ...]
    ultimi_visualizzati: int

    # Ultimo numero estratto (None se non è stato estratto ancora nulla)
    ultimo_estratto: Optional[int]

    @classmethod
    def crea(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        totale_numeri: int,
        totale_estratti: int,
        totale_mancanti: int,
        percentuale_estrazione: float,
        ultimi_estratti: Sequence[int],
        ultimo_estratto: Optional[int],
    ) -> "EventoRiepilogoTabellone":
        """
        Factory method per creare l'evento in modo uniforme e sicuro.

        Perché utile (come negli altri eventi):
        - Converte strutture mutabili in tuple immutabili (stabilità lato consumer/UI).
        - Calcola campi derivati (ultimi_visualizzati).
        - Normalizza il caso "nessuna estrazione" impostando ultimo_estratto a None.
        """
        # Normalizzazione: il consumer deve ricevere sempre una tupla immutabile.
        ultimi_estratti_out = tuple(ultimi_estratti)

        # Campo derivato: evita logica ripetuta nel renderer.
        ultimi_visualizzati_out = len(ultimi_estratti_out)

        # Normalizzazione difensiva: se non ci sono estrazioni, l'ultimo estratto non esiste.
        ultimo_estratto_out = (
            None if ultimi_visualizzati_out == 0 else ultimo_estratto
        )

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            totale_numeri=totale_numeri,
            totale_estratti=totale_estratti,
            totale_mancanti=totale_mancanti,
            percentuale_estrazione=percentuale_estrazione,
            ultimi_estratti=ultimi_estratti_out,
            ultimi_visualizzati=ultimi_visualizzati_out,
            ultimo_estratto=ultimo_estratto_out,
        )


@dataclass(frozen=True)
class EventoListaNumeriEstratti:
    """
    Evento di output per la UI del giocatore umano: elenco completo dei numeri estratti.

    Scopo:
    - Fornire al renderer un dato "grezzo" ma completo (potenzialmente lungo),
      utile per consultazione e verifica.
    - Nessun testo pronto: il renderer decide come impaginare e vocalizzare.

    Scelte di stabilità (coerenti con gli altri eventi UI):
    - numeri_estratti è una tupla immutabile.
    - numeri_estratti è ordinata in senso crescente (dal più piccolo al più grande),
      per facilitare lettura e ricerca.
    """

    # Contesto giocatore (utile per UI future / log multi-giocatore)
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Dato principale (potenzialmente verboso, ma richiesto da questo comando)
    numeri_estratti: tuple[int, ...]

    # Metadato di servizio: evita len() nel renderer e supporta intestazioni coerenti.
    totale_estratti: int

    @classmethod
    def crea(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numeri_estratti: Sequence[int],
    ) -> "EventoListaNumeriEstratti":
        """
        Factory method per creare l'evento in modo uniforme e sicuro.

        Perché utile:
        - Normalizza l'input: ordina e converte in tupla immutabile.
        - Calcola totale_estratti in modo centralizzato (stabilità e coerenza UI).
        """
        # Normalizzazione: garantisce ordine crescente e struttura immutabile.
        numeri_estratti_out = tuple(sorted(numeri_estratti))

        # Campo derivato: comodo per il renderer (intestazioni e controlli).
        totale_estratti_out = len(numeri_estratti_out)

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            numeri_estratti=numeri_estratti_out,
            totale_estratti=totale_estratti_out,
        )


@dataclass(frozen=True)
class EventoStatoFocusCorrente:
    """
    Evento di output per la UI del giocatore umano: stato dei focus correnti.

    Scopo:
    - Fornire una fotografia breve e stabile dei focus attualmente impostati:
      cartella, riga, colonna.
    - Non modifica lo stato di gioco (evento di consultazione/sistema).
    - Nessun testo pronto: il renderer decide la lingua e le frasi.

    Scelte di stabilità (coerenti con gli altri eventi UI):
    - Espone solo numeri "umani" (1-based) perché sono quelli utili al renderer.
    - I campi sono Optional: None significa "focus non impostato".
    """

    # Contesto giocatore (utile per UI future / log multi-giocatore).
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Contesto globale (per frasi tipo "Cartella 2 di 6").
    totale_cartelle: int

    # Focus correnti (valori umani 1-based; None se non impostato).
    numero_cartella: Optional[int]
    numero_riga: Optional[int]
    numero_colonna: Optional[int]

    @classmethod
    def crea_da_indici(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        totale_cartelle: int,
        indice_cartella: Optional[int],
        indice_riga: Optional[int],
        indice_colonna: Optional[int],
    ) -> "EventoStatoFocusCorrente":
        """
        Factory method per creare l'evento partendo dagli indici interni (0-based).

        Perché utile:
        - Centralizza la conversione 0-based -> 1-based.
        - Normalizza i None: se un focus non è impostato resta None anche nel numero umano.
        - Mantiene il renderer semplice: non deve conoscere indici interni.

        Nota di coerenza:
        - Non valida range (es. 0..N-1): l'evento fotografa lo stato così com'è;
          eventuali incoerenze sono gestite a monte (errori/focus fuori range).
        """
        # Conversione coerente 0-based interno -> 1-based per la UI.
        numero_cartella = None if indice_cartella is None else indice_cartella + 1
        numero_riga = None if indice_riga is None else indice_riga + 1
        numero_colonna = None if indice_colonna is None else indice_colonna + 1

        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            totale_cartelle=totale_cartelle,
            numero_cartella=numero_cartella,
            numero_riga=numero_riga,
            numero_colonna=numero_colonna,
        )


@dataclass(frozen=True)
class EventoVaiARigaAvanzata:
    """
    Evento di output per la UI del giocatore umano: “vai direttamente alla riga N”
    (della cartella attualmente in focus) e mostrala in modalità **avanzata**.

    Scopo:
    - Supportare comandi “diretti” (es. scorciatoie tipo Ctrl+1/Ctrl+2/Ctrl+3)
      che non “scorrono” tra le righe ma selezionano una riga specifica.
    - Fornire al renderer i dati necessari per leggere la riga in modo compatto:
      griglia della riga + riepilogo dei segnati (lista) + stato/riepilogo avanzato.

    Note di coerenza col progetto:
    - Nessun testo pronto: il renderer userà i codici già presenti nel dizionario
      (es. intestazione riga avanzata, etichette “Segnati: ...”, ecc.). [file:134]
    - Nessun campo di “limite/esito/direzione”: questo evento rappresenta solo
      il caso riuscito (la validazione avviene prima; gli errori restano errori). [file:131]
    - Non include contesto cartella (numero cartella, totale cartelle) perché,
      per questo comando, è implicito che si operi sulla cartella già in focus.

    Convenzioni:
    - numero_riga: 1-based (1..3) per coerenza UI.
    - rigasemplice: tupla di 9 celle (int oppure "-" per vuoto), immutabile.
    - statoriga: dizionario normalizzato (solo primitivi o tuple) pronto per renderer.
    - numerisegnati_riga_ordinati: tupla ordinata dei segnati presenti nella riga.
    """

    # Contesto giocatore (utile per UI future / log multi-giocatore).
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Riga selezionata (umana 1..3).
    numero_riga: int

    # Dati per visualizzazione avanzata.
    riga_semplice: tuple[int | str, ...]
    stato_riga: dict[str, int | float | tuple[int, ...]]
    numeri_segnati_riga_ordinati: tuple[int, ...]

    @classmethod
    def crea_da_dati_riga_avanzati(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero_riga: int,
        dati_riga_avanzati: tuple[
            tuple[int | str, ...],                 # riga_semplice (9 celle)
            dict[str, int | float | tuple[int, ...]],  # statoriga normalizzato
            tuple[int, ...],                       # numeri_segnati_riga_ordinati
        ],
    ) -> "EventoVaiARigaAvanzata":
        """
        Factory method per creare l'evento a partire dal “pacchetto stabile”
        prodotto dalla Cartella (in analogia a EventoNavigazioneRigaAvanzata). [file:131]

        Perché utile:
        - Centralizza la scomposizione del pacchetto dati (evita duplicazioni).
        - Garantisce che le strutture in uscita siano immutabili (tuple).
        - Mantiene la conversione della riga in formato umano (1-based) coerente
          e controllabile in un punto solo.

        Parametri:
        - numero_riga: riga in formato umano 1..3 (già validata a monte).
        - dati_riga_avanzati: tupla ottenuta da un metodo tipo
          Cartella.get_dati_visualizzazione_riga_avanzata(...), già normalizzata.

        Nota:
        - Questo metodo non valida range o coerenza del focus: se mancano prerequisiti
          (cartella non in focus, riga fuori range, ecc.) si ritorna un errore,
          non si crea l'evento.
        """
        riga_semplice, stato_riga, numeri_segnati_riga_ordinati = dati_riga_avanzati

        # Forziamo a tuple per stabilità/immutabilità lato renderer.
        riga_semplice_out = tuple(riga_semplice)
        numeri_segnati_out = tuple(numeri_segnati_riga_ordinati)

        # statoriga è già “normalizzato” a monte (primitivi/tuple); qui lo passiamo
        # così com'è per non introdurre logiche duplicate.
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            numero_riga=numero_riga,
            riga_semplice=riga_semplice_out,
            stato_riga=stato_riga,
            numeri_segnati_riga_ordinati=numeri_segnati_out,
        )


@dataclass(frozen=True)
class EventoVaiAColonnaAvanzata:
    """
    Evento di output per la UI del giocatore umano: “vai direttamente alla colonna N”
    (della cartella attualmente in focus) e mostrala in modalità **avanzata**.

    Scopo:
    - Supportare comandi “diretti” (es. scorciatoie tipo Alt+1..Alt+9) che non
      “scorrono” tra le colonne ma selezionano una colonna specifica.
    - Fornire al renderer i dati necessari per una lettura compatta/accessibile:
      celle della colonna + riepilogo dei segnati + stato/riepilogo avanzato.

    Note di coerenza col progetto:
    - Nessun testo pronto: il renderer userà i codici già presenti nel dizionario
      (es. intestazione colonna avanzata, etichette “Segnati: ...”, ecc.). [file:134]
    - Nessun campo di “limite/esito/direzione”: questo evento rappresenta solo
      il caso riuscito (validazione prerequisiti e range fatta prima). [file:131]
    - Non include contesto cartella (numero cartella, totale cartelle) perché
      per questo comando la cartella è implicita dal focus corrente.

    Convenzioni:
    - numero_colonna: 1-based (1..9) per coerenza UI.
    - colonnasemplice: tupla di 3 celle (una per riga, dall'alto verso il basso),
      ciascuna cella è int oppure "-" per vuoto.
    - statocolonna: dizionario normalizzato (solo primitivi o tuple) pronto per renderer.
    - numerisegnati_colonna_ordinati: tupla ordinata dei segnati presenti nella colonna.
    """

    # Contesto giocatore (utile per UI future / log multi-giocatore).
    id_giocatore: Optional[int]
    nome_giocatore: str

    # Colonna selezionata (umana 1..9).
    numero_colonna: int

    # Dati per visualizzazione avanzata.
    colonna_semplice: tuple[int | str, ...]
    stato_colonna: dict[str, int | float | tuple[int, ...]]
    numeri_segnati_colonna_ordinati: tuple[int, ...]

    @classmethod
    def crea_da_dati_colonna_avanzati(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero_colonna: int,
        dati_colonna_avanzati: tuple[
            tuple[int | str, ...],                 # colonna_semplice (3 celle)
            dict[str, int | float | tuple[int, ...]],  # stato_colonna normalizzato
            tuple[int, ...],                       # numeri_segnati_colonna_ordinati
        ],
    ) -> "EventoVaiAColonnaAvanzata":
        """
        Factory method per creare l'evento a partire dal “pacchetto stabile”
        prodotto dalla Cartella (in analogia a EventoNavigazioneColonnaAvanzata). [file:131]

        Perché utile:
        - Centralizza la scomposizione del pacchetto dati (evita duplicazioni).
        - Garantisce strutture immutabili (tuple) lato renderer.
        - Mantiene il numero colonna in formato umano (1-based) coerente
          e controllabile in un punto solo.

        Parametri:
        - numero_colonna: colonna in formato umano 1..9 (già validata a monte).
        - dati_colonna_avanzati: tupla ottenuta da un metodo tipo
          Cartella.get_dati_visualizzazione_colonna_avanzata(...), già normalizzata.

        Nota:
        - Questo metodo non valida prerequisiti o range: se mancano prerequisiti
          (cartella non in focus, colonna fuori range, ecc.) si ritorna un errore,
          non si crea l'evento.
        """
        colonna_semplice, stato_colonna, numeri_segnati_colonna_ordinati = dati_colonna_avanzati

        # Forziamo a tuple per stabilità/immutabilità lato renderer.
        colonna_semplice_out = tuple(colonna_semplice)
        numeri_segnati_out = tuple(numeri_segnati_colonna_ordinati)

        # statocolonna è già “normalizzato” a monte (primitivi/tuple); qui lo passiamo
        # così com'è per non introdurre logiche duplicate.
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            numero_colonna=numero_colonna,
            colonna_semplice=colonna_semplice_out,
            stato_colonna=stato_colonna,
            numeri_segnati_colonna_ordinati=numeri_segnati_out,
        )
