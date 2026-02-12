from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from collections.abc import Sequence

# import moduli di progetto eventi
from bingo_game.events.codici_errori import Codici_Errori
from bingo_game.events.codici_eventi import EVENTO_FOCUS_AUTO_IMPOSTATO
from bingo_game.events.eventi_output_ui_umani import (
EventoRiepilogoCartellaCorrente,
EventoLimiteNavigazioneCartelle,
EventoVisualizzaCartellaSemplice,
EventoVisualizzaCartellaAvanzata,
EventoVisualizzaTutteCartelleSemplice,
EventoVisualizzaTutteCartelleAvanzata,
EventoNavigazioneRiga,
EventoNavigazioneRigaAvanzata,
)
from bingo_game.ui.locales import MESSAGGI_ERRORI, MESSAGGI_EVENTI, MESSAGGI_OUTPUT_UI_UMANI, MESSAGGI_SISTEMA
from bingo_game.events.codici_messaggi_sistema import (
    SISTEMA_ERRORE_CODICE_MANCANTE,
    SISTEMA_ERRORE_MESSAGGIO_NON_DISPONIBILE,
    SISTEMA_ERRORE_CODICE_NON_MAPPATO_DEBUG,
    SISTEMA_SELEZIONE_AUTOMATICA_EFFETTUATA,
    SISTEMA_TIPO_FOCUS_NON_PREVISTO_DEBUG,
    SISTEMA_TEMPLATE_EVENTO_MANCANTE_DEBUG,
    SISTEMA_PLACEHOLDER_TEMPLATE_MANCANTE_DEBUG,
    SISTEMA_FOCUS_CARTELLA_IMPOSTATO,
    SISTEMA_FOCUS_RESET_RIGA_COLONNA,
    SISTEMA_TURNO_PASSATO,
    SISTEMA_RECLAMO_ASSOCIATO_TOMBOLA,
    SISTEMA_RECLAMO_ASSOCIATO_RIGA,
    SISTEMA_RECLAMO_ASSOCIATO_RIGA_NON_DISPONIBILE,
    SISTEMA_RECLAMO_INVIATO,
    SISTEMA_RIFERIMENTO_TOMBOLA,
    SISTEMA_RIFERIMENTO_RIGA,
    SISTEMA_RIFERIMENTO_RIGA_NON_DISPONIBILE,
    SISTEMA_ESITO_RECLAMO,
    SISTEMA_ESITO_RECLAMO_MOTIVO,
    SISTEMA_ESITO_RECLAMO_TURNO,
    SISTEMA_ESITO_RECLAMO_NUMERO_ESTRATTO,
    SISTEMA_EVENTO_NON_SUPPORTATO,
    SISTEMA_EVENTO_NON_SUPPORTATO_DEBUG,
)

from bingo_game.events.eventi import EsitoAzione
from bingo_game.events.eventi_partita import (
    EventoEsitoReclamoVittoria,
    EventoFineTurno,
    EventoReclamoVittoria,
)
from bingo_game.events.eventi_ui import (
    EventoFocusAutoImpostato,
    EventoFocusCartellaImpostato,
)

from bingo_game.ui.locales.it import MESSAGGI_ERRORI, MESSAGGI_EVENTI


@dataclass(frozen=True)
class RenderOptions:
    """
    Opzioni di rendering (estendibili).

    Nota:
    - Tenere le opzioni in una dataclass rende più semplice evolvere il renderer nel tempo
      senza cambiare la firma dei metodi (es. modalità verbose, prefissi, ecc.).
    """
    # Se True, quando un codice errore non è presente nel catalogo, ritorna anche un dettaglio tecnico.
    debug_unknown_codes: bool = False


class TerminalRenderer:
    """
    Renderer per output testuale su terminale.

    Convenzione:
    - Il metodo pubblico principale è render_esito(), che funge da orchestratore.
    - Restituisce sempre una lista di righe (anche una sola riga).
    """

    def __init__(self, options: Optional[RenderOptions] = None) -> None:
        self._options = options or RenderOptions()

    #sezione: metodi di classe

    def render_esito(self, esito: EsitoAzione) -> Sequence[str]:
        """
        Orchestratore: converte un EsitoAzione in righe stampabili per terminale/screen reader.

        Contratto di output:
        - Ritorna sempre una lista di righe (list[str]).
        - La UI/CLI può stampare con "\\n".join(righe) oppure vocalizzare unendo le righe.

        Gestione casi (completa):
        1) esito.ok == False
           - Renderizza l'errore tramite catalogo locale (MESSAGGI_ERRORI) delegando a _render_errore().
           - Include fallback robusti se il catalogo è incompleto o il codice manca.

        2) esito.ok == True
           2.1) esito.evento is None
                - Successo "silenzioso": ritorna [] (nessuna riga da stampare).
           2.2) esito.evento è una dataclass evento nota
                - Deleghe a handler dedicati, uno per tipo evento (focus, reclami, fine turno).
           2.3) esito.evento è presente ma di tipo sconosciuto
                - Ritorna un messaggio di fallback (con dettagli tecnici se debug_unknown_codes=True).

        Nota architetturale:
        - Gli errori vengono tradotti tramite catalogo (ui/locales/it.py).
        - Gli eventi vengono renderizzati tramite funzioni dedicate: in futuro si potranno
          spostare anche i testi evento in un catalogo dedicato, senza cambiare questa orchestrazione.
        """

        # 1) Caso errore: il dominio segnala che l'azione non può procedere.
        if not esito.ok:
            return self._render_errore(esito)

        # 2) Caso successo: può essere "silenzioso" oppure avere un evento da comunicare.
        evento = esito.evento
        if evento is None:
            # Successo senza payload: nessuna riga da mostrare.
            return []

        if isinstance(evento, EventoFocusAutoImpostato):
            return self._render_evento_focus_auto_impostato(evento)

        if isinstance(evento, EventoFocusCartellaImpostato):
            return self._render_evento_focus_cartella_impostato(evento)

        if isinstance(evento, EventoFineTurno):
            return self._render_evento_fine_turno(evento)

        if isinstance(evento, EventoReclamoVittoria):
            return self._render_evento_reclamo_vittoria(evento)

        if isinstance(evento, EventoEsitoReclamoVittoria):
            return self._render_evento_esito_reclamo_vittoria(evento)

        #5) evento di riepilogo della cartella 
        if isinstance(evento, EventoRiepilogoCartellaCorrente):
            return self._render_evento_riepilogo_cartella_corrente(evento)

        #5) evento evento limite navigazione cartelle
        if isinstance(evento, EventoLimiteNavigazioneCartelle):
            return self._render_evento_limite_navigazione_cartelle(evento)

        #6) crea evento per lettura cartella semplice 
        if isinstance(evento, EventoVisualizzaCartellaSemplice):
            return self._render_cartella_semplice(evento)

        # 7) evento per visualizzazione di TUTTE le cartelle in modalità semplice
        if isinstance(evento, EventoVisualizzaTutteCartelleSemplice):
            return self._render_tutte_cartelle_semplice(evento)

        #8) istanza del evento per visualizzazione cartella avanzata
        if isinstance(evento, EventoVisualizzaCartellaAvanzata):
            return self._render_cartella_avanzata(evento)

        # 9) evento per visualizzazione di TUTTE le cartelle in modalità avanzata
        if isinstance(evento, EventoVisualizzaTutteCartelleAvanzata):
            return self._render_tutte_cartelle_avanzata(evento)

        # 10) evento per la stampa semplice delle righe di una cartella una per volta in base al movimento delle freccie 
        if isinstance(evento, EventoNavigazioneRiga):
            return self._render_evento_navigazione_riga(evento)

        #10) Evento sconosciuto: fallback robusto.
        return self._render_evento_sconosciuto(evento)


    def _render_errore(self, esito: EsitoAzione) -> Sequence[str]:
        """
        Renderizza un EsitoAzione di errore (ok=False) usando esclusivamente i cataloghi
        di localizzazione (it.py), senza stringhe hardcoded nel renderer.

        Responsabilità:
        - Convertire esito.errore (Codici_Errori) in righe testuali tramite MESSAGGI_ERRORI.
        - Gestire casi anomali in modo robusto e predicibile:
        - ok=False ma errore=None  -> fallback di sistema (catalogo)
        - codice non presente nel catalogo errori -> fallback di sistema (catalogo)
        - in debug, aggiunge dettaglio tecnico (sempre da catalogo)

        Contratto di stabilità:
        - Ritorna sempre una tuple[str, ...] (immutabile) pur dichiarando Sequence[str].
        - Il renderer non emette testo libero: tutto passa dai cataloghi.

        Parametri:
        - esito: EsitoAzione atteso con ok=False.

        Ritorna:
        - Sequence[str]: tuple di righe pronte per output terminale/screen reader.
        """
        # 1) Caso anomalo: ok=False ma senza codice errore.
        #    Non dovrebbe accadere se il dominio è coerente, ma qui difendiamo il renderer.
        codice: Codici_Errori | None = esito.errore
        if codice is None:
            righe = MESSAGGI_SISTEMA.get(SISTEMA_ERRORE_CODICE_MANCANTE)
            # Ulteriore difesa: se manca pure il template di sistema, ritorniamo un fallback minimale.
            # (Questo è l'unico punto in cui non possiamo "inventare" un altro codice.)
            return righe if righe is not None else tuple()

        # 2) Caso normale: codice presente -> recupero righe dal catalogo errori.
        righe = MESSAGGI_ERRORI.get(codice)
        if righe is not None:
            return righe

        # 3) Caso fallback: codice non presente nel catalogo (catalogo incompleto).
        #    In modalità "non debug" restituiamo un messaggio generico di sistema.
        base = MESSAGGI_SISTEMA.get(SISTEMA_ERRORE_MESSAGGIO_NON_DISPONIBILE)
        if base is None:
            # Difensivo: se manca anche questo, ritorniamo vuoto (nessun testo).
            base = tuple()

        if not self._options.debug_unknown_codes:
            return base

        # 4) Debug attivo: aggiungiamo dettaglio tecnico (sempre da catalogo).
        #    Usiamo un template con placeholder {codice}.
        debug_tpl = MESSAGGI_SISTEMA.get(SISTEMA_ERRORE_CODICE_NON_MAPPATO_DEBUG)

        if debug_tpl is None:
            # Se il template debug manca, restituiamo almeno il messaggio base.
            return base

        try:
            debug_righe = tuple(r.format(codice=codice) for r in debug_tpl)
        except KeyError as exc:
            # Se manca un placeholder nel template (errore di catalogo), fallback coerente:
            # usiamo la stringa di sistema dedicata ai placeholder mancanti.
            fallback_tpl = MESSAGGI_SISTEMA.get(SISTEMA_PLACEHOLDER_TEMPLATE_MANCANTE_DEBUG)
            if fallback_tpl is None:
                return base
            return tuple(r.format(exc=exc) for r in fallback_tpl)

        # Base + debug, mantenendo sempre immutabilità (tuple).
        return tuple(base) + debug_righe




    def _render_evento_focus_auto_impostato(self, evento: "EventoFocusAutoImpostato") -> Sequence[str]:
        """
        Renderizza EventoFocusAutoImpostato in righe testuali, usando il catalogo locale eventi.

        Scopo:
        - Fornire un feedback (opzionale) quando il sistema imposta automaticamente un focus mancante.
        - Utile per screen reader e per capire cosa è stato selezionato "di default".
        - Evitare stringhe hardcoded nel renderer: il testo principale viene preso da MESSAGGI_EVENTI,
          usando una chiave evento stabile (costante) per ridurre refusi.

        Regole:
        - Converte l'indice interno 0-based in numero "umano" 1-based.
        - Usa un template con placeholder dal catalogo:
          - {tipo}: "Cartella" / "Riga" / "Colonna"
          - {numero}: numero umano (1-based)

        Fallback:
        - Se la chiave evento non è presente nel catalogo o il tipo_focus è inatteso,
          ritorna un messaggio generico (con dettaglio tecnico in debug).

        Ritorna:
        - Sequence[str]: righe pronte per terminale/screen reader (ritornate come tuple per coerenza/immutabilità).
        """

        # 1) Conversione indice interno -> numero umano.
        numero_umano = evento.indice + 1

        # 2) Normalizzazione tipo_focus in una parola "utente-friendly".
        #    (Il template in italiano usa il femminile: "selezionata", quindi Cartella/Riga/Colonna vanno bene.)
        if evento.tipo_focus == "cartella":
            tipo = "Cartella"
        elif evento.tipo_focus == "riga":
            tipo = "Riga"
        elif evento.tipo_focus == "colonna":
            tipo = "Colonna"
        else:
            # Difensivo: TipoFocus è un Literal, ma gestiamo comunque eventuali valori inattesi.
            if self._options.debug_unknown_codes:
                return (
                    "Selezione automatica effettuata.",
                    f"Dettaglio tecnico: tipo_focus non previsto -> {evento.tipo_focus}.",
                )
            return ("Selezione automatica effettuata.",)

        # 3) Recupero template dal catalogo eventi (chiave stabile, via costante).
        templates = MESSAGGI_EVENTI.get(EVENTO_FOCUS_AUTO_IMPOSTATO)
        if not templates:
            # Catalogo incompleto: fallback.
            if self._options.debug_unknown_codes:
                return (
                    f"{tipo} selezionata automaticamente: {numero_umano}.",
                    f"Dettaglio tecnico: template {EVENTO_FOCUS_AUTO_IMPOSTATO} non presente nel catalogo.",
                )
            return (f"{tipo} selezionata automaticamente: {numero_umano}.",)

        # 4) Render multi-riga: ogni riga del template viene formattata con i placeholder.
        righe: list[str] = []
        for template in templates:
            try:
                righe.append(template.format(tipo=tipo, numero=numero_umano))
            except KeyError as exc:
                # Template malformato (placeholder non fornito): fallback robusto.
                if self._options.debug_unknown_codes:
                    return (
                        "Selezione automatica effettuata.",
                        f"Dettaglio tecnico: placeholder mancante nel template -> {exc}.",
                    )
                return ("Selezione automatica effettuata.",)

        return tuple(righe)


    def _render_evento_focus_cartella_impostato(self, evento: "EventoFocusCartellaImpostato") -> Sequence[str]:
        """
        Renderizza EventoFocusCartellaImpostato in righe testuali.

        Scopo:
        - Confermare che l'utente ha impostato esplicitamente la cartella in focus.
        - Se durante il cambio cartella sono stati resettati riga/colonna, lo comunica in modo chiaro.

        Strategia:
        - Riga 1: conferma cartella selezionata.
        - Riga 2 (opzionale): indica che riga/colonna sono state azzerate a seguito del cambio cartella.

        Parametri:
        - evento: EventoFocusCartellaImpostato.

        Ritorna:
        - list[str]: righe pronte per terminale/screen reader.
        """

        righe: List[str] = [f"Focus impostato sulla cartella {evento.numero_cartella}."]

        # Se la cartella è cambiata, il giocatore_umano ha resettato i focus secondari:
        # è un'informazione utile per evitare confusione nella navigazione successiva.
        if evento.reset_riga_colonna:
            righe.append("Riga e colonna in focus sono state reimpostate.")

        return righe


    def _render_evento_fine_turno(self, evento: "EventoFineTurno") -> Sequence[str]:
        """
        Renderizza EventoFineTurno in righe testuali.

        Scopo:
        - Comunicare che il giocatore ha passato il turno.
        - Se presente un reclamo associato al passaggio turno, mostra i dettagli essenziali
          (tipo vittoria + riferimenti cartella/riga) in modo leggibile.

        Nota:
        - Questo rendering è pensato per terminale/screen reader: frasi brevi e dati chiave.

        Parametri:
        - evento: EventoFineTurno.

        Ritorna:
        - list[str]: righe pronte per terminale/screen reader.
        """

        righe: List[str] = ["Turno passato."]

        reclamo = evento.reclamo_turno
        if reclamo is None:
            return righe

        # Conversione a numeri "umani" per cartella/riga.
        cartella_umano = reclamo.indice_cartella + 1

        if reclamo.tipo == "tombola":
            righe.append(f"Reclamo associato: {reclamo.tipo} (cartella {cartella_umano}).")
            return righe

        # Per ambo/terno/quaterna/cinquina: ci aspettiamo una riga valorizzata.
        if reclamo.indice_riga is None:
            # Difensivo: non dovrebbe accadere secondo contratto ReclamoVittoria.
            righe.append(f"Reclamo associato: {reclamo.tipo} (cartella {cartella_umano}, riga non disponibile).")
            return righe

        riga_umano = reclamo.indice_riga + 1
        righe.append(f"Reclamo associato: {reclamo.tipo} (cartella {cartella_umano}, riga {riga_umano}).")
        return righe


    def _render_evento_reclamo_vittoria(self, evento: "EventoReclamoVittoria") -> Sequence[str]:
        """
        Renderizza EventoReclamoVittoria (fase tipica: ANTE_TURNO) in righe testuali.

        Scopo:
        - Fornire un feedback immediato quando il giocatore genera un reclamo "soft"
          (warning, revocabile) basato sui focus interni.

        Strategia:
        - Riga 1: tipo reclamo e fase.
        - Riga 2: riferimento cartella/riga (se applicabile), usando numeri "umani".

        Parametri:
        - evento: EventoReclamoVittoria.

        Ritorna:
        - list[str]: righe pronte per terminale/screen reader.
        """

        reclamo = evento.reclamo
        cartella_umano = reclamo.indice_cartella + 1

        righe: List[str] = [f"Reclamo inviato: {reclamo.tipo} (fase {evento.fase})."]

        if reclamo.tipo == "tombola":
            righe.append(f"Riferimento: cartella {cartella_umano}.")
            return righe

        # Per reclami di riga, ci aspettiamo indice_riga valorizzato.
        if reclamo.indice_riga is None:
            righe.append(f"Riferimento: cartella {cartella_umano}, riga non disponibile.")
            return righe

        riga_umano = reclamo.indice_riga + 1
        righe.append(f"Riferimento: cartella {cartella_umano}, riga {riga_umano}.")
        return righe


    def _render_evento_esito_reclamo_vittoria(self, evento: "EventoEsitoReclamoVittoria") -> Sequence[str]:
        """
        Renderizza EventoEsitoReclamoVittoria in righe testuali.

        Scopo:
        - Comunicare l'esito della validazione di un reclamo (tipicamente dalla Partita).
        - In caso di fallimento, mostra il codice errore (macchina) come fallback minimo.
          (In futuro potrà essere mappato con un catalogo dedicato anche per esiti reclamo.)

        Strategia:
        - Riga 1: esito (ACCETTATO / RIFIUTATO) + tipo reclamo + fase.
        - Riga 2: riferimento cartella/riga.
        - Riga 3 (opzionale): dettaglio errore se ok=False e errore presente.
        - Riga 4/5 (opzionali): contesto turno/numero estratto se disponibili.

        Parametri:
        - evento: EventoEsitoReclamoVittoria.

        Ritorna:
        - list[str]: righe pronte per terminale/screen reader.
        """

        reclamo = evento.reclamo
        cartella_umano = reclamo.indice_cartella + 1

        esito_testo = "ACCETTATO" if evento.ok else "RIFIUTATO"
        righe: List[str] = [f"Esito reclamo {esito_testo}: {reclamo.tipo} (fase {evento.fase})."]

        # Riga di riferimento cartella/riga.
        if reclamo.tipo == "tombola":
            righe.append(f"Riferimento: cartella {cartella_umano}.")
        else:
            if reclamo.indice_riga is None:
                righe.append(f"Riferimento: cartella {cartella_umano}, riga non disponibile.")
            else:
                riga_umano = reclamo.indice_riga + 1
                righe.append(f"Riferimento: cartella {cartella_umano}, riga {riga_umano}.")

        # Dettaglio errore (fallback tecnico).
        if not evento.ok and evento.errore is not None:
            righe.append(f"Motivo: {evento.errore}.")

        # Contesto opzionale: utile soprattutto in log/terminal.
        if evento.indice_turno is not None:
            righe.append(f"Turno: {evento.indice_turno}.")
        if evento.numero_estratto is not None:
            righe.append(f"Numero estratto: {evento.numero_estratto}.")

        return righe


    def _render_evento_riepilogo_cartella_corrente(self, evento: EventoRiepilogoCartellaCorrente) -> Sequence[str]:
        """
        Renderizza EventoRiepilogoCartellaCorrente in righe testuali per UI/screen reader.

        Output atteso:
        - 2 righe totali:
        1) sintesi cartella (segnati/totale, mancanti, percentuale)
        2) numeri da segnare (nessuno oppure lista)

        Nota di stabilità:
        - I template stanno nel catalogo MESSAGGI_OUTPUT_UI_UMANI (non nei messaggi di sistema).
        - Qui si fa solo formattazione (es. join della lista), non logica di gioco.
        """
        # 1) Riga 1: sintesi (sempre presente).
        template_riga_1 = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_1"][0]
        riga_1 = template_riga_1.format(
            numero_cartella=evento.numero_cartella,
            numeri_segnati=evento.numeri_segnati,
            totale_numeri=evento.totale_numeri,
            mancanti=evento.mancanti,
            percentuale=evento.percentuale,
        )

        # 2) Riga 2: dipende dai mancanti.
        if evento.mancanti == 0:
            template_riga_2 = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_NESSUNO"][0]
            riga_2 = template_riga_2
        else:
            # Stabilità: la dataclass garantisce già l'ordinamento, qui formattiamo soltanto.
            lista = ", ".join(str(n) for n in evento.numeri_non_segnati)
            template_riga_2 = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_LISTA"][0]
            riga_2 = template_riga_2.format(lista=lista)

        # Ritorno immutabile: tuple invece di list.
        return (riga_1, riga_2)


    def _render_evento_limite_navigazione_cartelle(self, evento: EventoLimiteNavigazioneCartelle) -> Sequence[str]:
        """
        Renderizza EventoLimiteNavigazioneCartelle.

        Output:
        - 1 sola riga (tuple con un elemento), per ridurre la verbosità durante la navigazione.

        Nota:
        - I template sono nel catalogo MESSAGGI_OUTPUT_UI_UMANI.
        - Qui si fa solo formattazione (sostituzione placeholder).
        """
        if evento.limite == "minimo":
            template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MINIMO"][0]
        else:
            template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MASSIMO"][0]

        riga = template.format(totale_cartelle=evento.totale_cartelle)
        return (riga,)


    def _render_cartella_semplice(self, evento: EventoVisualizzaCartellaSemplice) -> tuple[str, ...]:
        """
        Rende l'EventoVisualizzaCartellaSemplice in righe testuali.

        Strategia (coerente con il progetto):
        - Le parole "umane" (cartella/riga/vuoto) arrivano dal dizionario lingua.
        - I numeri rimangono numeri fino all'ultimo momento e vengono convertiti in str,
          così lo screen reader li leggerà secondo la lingua dell'utente.
        - Le celle vengono separate con ", " per una lettura più scandita.

        Output:
        - 1 riga intestazione (Cartella N di M)
        - 3 righe, una per ogni riga della griglia (Riga 1/2/3: ...)
        """
        # 1) Template e parole dalla lingua (it.py).
        template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_INTESTAZIONE"][0]
        template_prefisso_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA"][0]
        parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]

        # 2) Intestazione: "Cartella {numero_cartella} di {totale_cartelle}."
        intestazione = template_intestazione.format(
            numero_cartella=evento.numero_cartella,
            totale_cartelle=evento.totale_cartelle,
        )

        righe_out: list[str] = [intestazione]

        # 3) Tre righe (3x9). Ogni cella: numero oppure parola "vuoto".
        for indice_riga, riga in enumerate(evento.griglia_semplice):
            numero_riga = indice_riga + 1  # 1-based per l'utente

            prefisso = template_prefisso_riga.format(numero_riga=numero_riga)

            # Trasforma ogni cella in token parlabile:
            # - "-" -> parola "vuoto"
            # - int -> "42"
            tokens: list[str] = []
            for cella in riga:
                if cella == "-":
                    tokens.append(parola_vuoto)
                else:
                    # Qui ci aspettiamo un int (dato grezzo).
                    tokens.append(str(cella))

            contenuto_riga = ", ".join(tokens)
            righe_out.append(prefisso + contenuto_riga)

        return tuple(righe_out)


    def _render_tutte_cartelle_semplice(self, evento: EventoVisualizzaTutteCartelleSemplice) -> tuple[str, ...]:
        """
        Rende l'EventoVisualizzaTutteCartelleSemplice in righe testuali.

        Obiettivo:
        - Mostrare tutte le cartelle del giocatore in modalità "semplice",
          una dopo l'altra, senza cambiare focus e senza testi "pronti" nel payload.

        Strategia (coerente con _render_cartella_semplice):
        - Le parole "umane" (intestazione, prefisso riga, cella vuota) arrivano
          dal dizionario lingua MESSAGGI_OUTPUT_UI_UMANI.
        - I numeri restano numeri fino all'ultimo e vengono convertiti in stringa
          solo in fase di rendering.
        - Le celle sono separate con ", " per una lettura più scandita.

        Separazione tra cartelle:
        - Aggiunge una riga vuota come separatore tra cartelle.
        - NON aggiunge la riga vuota dopo l'ultima cartella.

        Output:
        - Per ogni cartella:
          1) 1 riga intestazione: "Cartella X di Y."
          2) 3 righe di griglia: "Riga 1/2/3: ..."
        - Più una riga vuota tra cartelle (non dopo l'ultima).
        """
        # Se non c'è nulla da stampare, ritorna output vuoto (nessun testo).
        if not evento.cartelle:
            return tuple()

        # Template e parole dalla lingua (it.py).
        template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_INTESTAZIONE"][0]
        template_prefisso_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA"][0]
        parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]

        righe_out: list[str] = []
        totale = evento.totale_cartelle
        ultima_idx = len(evento.cartelle) - 1

        # Cicla su tutte le cartelle già trasformate in griglia semplice.
        for idx, (numero_cartella, griglia) in enumerate(evento.cartelle):
            # Intestazione: "Cartella {numero_cartella} di {totale_cartelle}."
            righe_out.append(
                template_intestazione.format(
                    numero_cartella=numero_cartella,
                    totale_cartelle=totale,
                )
            )

            # Tre righe (3x9). Ogni cella: numero oppure parola "vuoto".
            for indice_riga, riga in enumerate(griglia):
                numero_riga = indice_riga + 1  # 1-based per l'utente
                prefisso = template_prefisso_riga.format(numero_riga=numero_riga)

                tokens: list[str] = []
                for cella in riga:
                    if cella == "-":
                        tokens.append(parola_vuoto)
                    else:
                        tokens.append(str(cella))

                righe_out.append(prefisso + ", ".join(tokens))

            # Separatore tra cartelle: riga vuota solo se non è l'ultima.
            if idx != ultima_idx:
                righe_out.append("")

        return tuple(righe_out)


    def _render_cartella_avanzata(self, evento: EventoVisualizzaCartellaAvanzata) -> tuple[str, ...]:
        """
        Rende un EventoVisualizzaCartellaAvanzata in righe testuali per l'utente umano.

        Output previsto (schema):
        - 1 riga: intestazione (cartella N di M, modalità avanzata)
        - 3 righe: una per ogni riga della griglia 3x9
            * numeri separati da ", "
            * celle vuote -> parola dal dizionario (es. "vuoto")
            * numeri segnati -> numero seguito da "*" (es. "68*")
            * a fine riga: "Segnati: ..." oppure "Segnati: nessuno."
        - 1 riga: footer riepilogo globale (totale segnati / totali / percentuale)

        Note di coerenza:
        - Le parole/frasi arrivano dal dizionario lingua (MESSAGGI_OUTPUT_UI_UMANI).
        - I numeri restano numeri fino al rendering finale (str(numero)).
        - Il simbolo "*" viene gestito dal renderer (non è una stringa da tradurre).
        """
        # 1) Preleva i template dalla lingua (una sola volta).
        template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVVANZATA_INTESTAZIONE"][0]
        template_prefisso_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA"][0]
        parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]
        template_segnati_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVVANZATA_ETICHETTA_SEGNATI_RIGA"][0]
        testo_segnati_riga_nessuno = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVVANZATA_SEGNATI_RIGA_NESSUNO"][0]
        template_footer = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVVANZATA_FOOTER_RIEPILOGO"][0]

        # 2) Intestazione.
        righe_out: list[str] = [
            template_intestazione.format(
                numero_cartella=evento.numero_cartella,
                totale_cartelle=evento.totale_cartelle,
            )
        ]

        # 3) Per controlli rapidi: converte la tupla dei segnati in set (lookup O(1)).
        #    (Massimo 15 numeri: è comunque leggero, ma questo rende il codice più pulito.)
        segnati_set = set(evento.numeri_segnati_ordinati)

        # 4) Rendering delle 3 righe della griglia.
        for indice_riga, riga in enumerate(evento.griglia_semplice):
            numero_riga = indice_riga + 1  # 1-based per l'utente

            # 4a) Prefisso "Riga 1: "
            prefisso = template_prefisso_riga.format(numero_riga=numero_riga)

            # 4b) Celle della riga (9 valori) + lista segnati di riga.
            tokens: list[str] = []
            segnati_nella_riga: list[int] = []

            for cella in riga:
                # Cella vuota: "-" -> parola "vuoto"
                if cella == "-":
                    tokens.append(parola_vuoto)
                    continue

                # Cella numerica: int
                numero = int(cella)

                # Se segnato: aggiunge "*" dopo il numero e lo inserisce nel riepilogo di riga.
                if numero in segnati_set:
                    tokens.append(f"{numero}*")
                    segnati_nella_riga.append(numero)
                else:
                    tokens.append(str(numero))

            # 4c) Unisce le celle con separatore ", " per lettura più scandita.
            contenuto_riga = ", ".join(tokens)  # join è la via più semplice e robusta per comporre stringhe [web:182][web:183]

            # 4d) Riepilogo segnati a fine riga.
            if not segnati_nella_riga:
                riepilogo_riga = testo_segnati_riga_nessuno
            else:
                lista_segnati = ", ".join(str(n) for n in sorted(segnati_nella_riga))
                riepilogo_riga = template_segnati_riga.format(lista_segnati=lista_segnati)

            # 4e) Riga finale.
            righe_out.append(f"{prefisso}{contenuto_riga}. {riepilogo_riga}")

        # 5) Footer globale (totali e percentuale).
        numeri_segnati = int(evento.stato_cartella["numeri_segnati"])
        numeri_totali = int(evento.stato_cartella["numeri_totali"])
        percentuale = float(evento.stato_cartella["percentuale_completamento"])

        righe_out.append(
            template_footer.format(
                numeri_segnati=numeri_segnati,
                numeri_totali=numeri_totali,
                percentuale=percentuale,
            )
        )

        return tuple(righe_out)


    def _render_tutte_cartelle_avanzata(self, evento: EventoVisualizzaTutteCartelleAvanzata) -> tuple[str, ...]:
        """
        Rende l'EventoVisualizzaTutteCartelleAvanzata in righe testuali per l'utente umano.

        Obiettivo:
        - Stampare TUTTE le cartelle del giocatore in sequenza, in modalità "avanzata",
          riusando lo stesso stile del renderer singolo (_render_cartella_avanzata).

        Strategia:
        - Usa esclusivamente i template/parole dal dizionario lingua MESSAGGI_OUTPUT_UI_UMANI.
        - I numeri restano numeri fino al rendering finale (str(numero)).
        - Le celle sono separate con ", " per una lettura più scandita.
        - I numeri segnati vengono resi come "{numero}*" (asterisco gestito dal renderer).
        - A fine riga viene aggiunto il riepilogo segnati di riga.
        - A fine cartella viene aggiunto il footer globale (totali e percentuale).

        Separazione tra cartelle:
        - Inserisce una riga vuota come separatore tra i blocchi cartella.
        - NON inserisce la riga vuota dopo l'ultima cartella.

        Output:
        - Per ogni cartella:
          1) intestazione avanzata
          2) 3 righe di griglia con riepilogo segnati di riga
          3) footer riepilogo globale cartella
        """
        # Se non ci sono cartelle, non produciamo alcun output:
        # sarà il dominio (GiocatoreUmano) a decidere se generare un errore.
        if not evento.cartelle:
            return tuple()

        # 1) Preleva i template dalla lingua (una sola volta).
        template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVVANZATA_INTESTAZIONE"][0]
        template_prefisso_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA"][0]
        parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]
        template_segnati_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVVANZATA_ETICHETTA_SEGNATI_RIGA"][0]
        testo_segnati_riga_nessuno = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVVANZATA_SEGNATI_RIGA_NESSUNO"][0]
        template_footer = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVVANZATA_FOOTER_RIEPILOGO"][0]

        righe_out: list[str] = []
        totale = evento.totale_cartelle
        ultima_idx = len(evento.cartelle) - 1

        # 2) Cicla su tutte le cartelle avanzate (pacchetti già pronti).
        for idx, (numero_cartella, griglia, stato_cartella, numeri_segnati_ordinati) in enumerate(evento.cartelle):
            # 2a) Intestazione cartella (modalità avanzata).
            righe_out.append(
                template_intestazione.format(
                    numero_cartella=numero_cartella,
                    totale_cartelle=totale,
                )
            )

            # 2b) Lookup veloce: trasforma i segnati in set (max 15 numeri, comunque leggero).
            segnati_set = set(numeri_segnati_ordinati)

            # 2c) Rendering delle 3 righe della griglia.
            for indice_riga, riga in enumerate(griglia):
                numero_riga = indice_riga + 1  # 1-based per l'utente
                prefisso = template_prefisso_riga.format(numero_riga=numero_riga)

                tokens: list[str] = []
                segnati_nella_riga: list[int] = []

                for cella in riga:
                    # Cella vuota: "-" -> parola "vuoto"
                    if cella == "-":
                        tokens.append(parola_vuoto)
                        continue

                    # Cella numerica: int
                    numero = int(cella)

                    # Se segnato: aggiunge "*" e lo traccia per il riepilogo di riga.
                    if numero in segnati_set:
                        tokens.append(f"{numero}*")
                        segnati_nella_riga.append(numero)
                    else:
                        tokens.append(str(numero))

                # Unisce le celle con separatore ", " per lettura più scandita.
                contenuto_riga = ", ".join(tokens)

                # Riepilogo segnati a fine riga.
                if not segnati_nella_riga:
                    riepilogo_riga = testo_segnati_riga_nessuno
                else:
                    lista_segnati = ", ".join(str(n) for n in sorted(segnati_nella_riga))
                    riepilogo_riga = template_segnati_riga.format(lista_segnati=lista_segnati)

                # Riga completa: contenuto + riepilogo segnati di riga.
                righe_out.append(f"{prefisso}{contenuto_riga}. {riepilogo_riga}")

            # 2d) Footer globale (totali e percentuale) per la cartella corrente.
            numeri_segnati = int(stato_cartella["numeri_segnati"])
            numeri_totali = int(stato_cartella["numeri_totali"])
            percentuale = float(stato_cartella["percentuale_completamento"])

            righe_out.append(
                template_footer.format(
                    numeri_segnati=numeri_segnati,
                    numeri_totali=numeri_totali,
                    percentuale=percentuale,
                )
            )

            # 2e) Separatore tra cartelle: riga vuota solo se non è l'ultima.
            if idx != ultima_idx:
                righe_out.append("")

        return tuple(righe_out)


    def _render_evento_navigazione_riga(self, evento: EventoNavigazioneRiga) -> tuple[str, ...]:
        """
        Rende l'EventoNavigazioneRiga in righe testuali, in modo poco verboso.

        Scelte di output (come richiesto):
        - Caso esito="mostra":
          * Produce UNA sola riga: "Riga X: ..." + contenuto della riga in formato semplice.
          * Non stampa alcun riferimento alla cartella (es. "Cartella 1 di X") per evitare verbosità.
          * Celle unite con ", ":
              - "-" -> parola dal dizionario (UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA)
              - int -> str(numero)

        - Caso esito="limite":
          * Produce UNA sola riga breve:
              - minimo -> UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO
              - massimo -> UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO

        Robustezza:
        - Se arrivano dati incoerenti (es. esito="mostra" ma riga_semplice=None),
          ritorna una stringa vuota per coerenza con lo stile del progetto (anche se non dovrebbe accadere).
        """
        # 1) Caso "limite": messaggio breve, nessun altro contesto.
        if evento.esito == "limite":
            if evento.limite == "minimo":
                return (MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO"][0],)
            if evento.limite == "massimo":
                return (MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO"][0],)

            # Limite non riconosciuto (non dovrebbe accadere): output neutro.
            return ("",)

        # 2) Caso "mostra": una sola riga "Riga X: ..." + lista celle.
        if evento.esito == "mostra":
            # Se per qualche motivo manca la riga, non andiamo in errore.
            if evento.riga_semplice is None:
                return ("",)

            template_prefisso_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA"][0]
            parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]

            # Prefisso: "Riga {numero_riga}: "
            prefisso = template_prefisso_riga.format(numero_riga=evento.numero_riga_corrente)

            # Trasforma le 9 celle in token "parlabili".
            tokens: list[str] = []
            for cella in evento.riga_semplice:
                if cella == "-":
                    tokens.append(parola_vuoto)
                else:
                    tokens.append(str(cella))

            return (prefisso + ", ".join(tokens),)

        # 3) Esito sconosciuto (non dovrebbe accadere): output neutro.
        return ("",)


    def _render_evento_sconosciuto(self, evento: object) -> Sequence[str]:
        """
        Fallback per eventi non riconosciuti dal renderer.

        Scopo:
        - Evitare crash del terminale quando arriva un evento nuovo non ancora supportato.
        - Fornire un messaggio generico; se debug_unknown_codes=True, aggiungere dettagli tecnici.

        Parametri:
        - evento: oggetto evento non gestito.

        Ritorna:
        - list[str]: righe pronte per terminale/screen reader.
        """

        if self._options.debug_unknown_codes:
            return [
                "Evento non supportato dal renderer.",
                f"Dettaglio tecnico: tipo evento -> {type(evento).__name__}.",
            ]

        return ["Evento non supportato dal renderer."]
