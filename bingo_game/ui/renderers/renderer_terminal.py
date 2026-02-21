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

        # 3) istanzia l'evento di focus autoimpostato
        if isinstance(evento, EventoFocusAutoImpostato):
            return self._render_evento_focus_auto_impostato(evento)

        # 4) istanzia l'evento di focus impostato sulla cartella.
        if isinstance(evento, EventoFocusCartellaImpostato):
            return self._render_evento_focus_cartella_impostato(evento)

        # 6) istanzia l'evento per la chiamata di reclamo vittoria
        if isinstance(evento, EventoReclamoVittoria):
            return self._render_evento_reclamo_vittoria(evento)

        # 7) istanzia l'evento ritornato dalla partita sul esito del reclamo di vittoria
        if isinstance(evento, EventoEsitoReclamoVittoria):
            return self._render_evento_esito_reclamo_vittoria(evento)

        # 8) evento di riepilogo della cartella 
        if isinstance(evento, EventoRiepilogoCartellaCorrente):
            return self._render_evento_riepilogo_cartella_corrente(evento)

        # 9) evento evento limite navigazione cartelle
        if isinstance(evento, EventoLimiteNavigazioneCartelle):
            return self._render_evento_limite_navigazione_cartelle(evento)

        # 10) crea evento per lettura cartella semplice 
        if isinstance(evento, EventoVisualizzaCartellaSemplice):
            return self._render_cartella_semplice(evento)

        # 11) evento per visualizzazione di TUTTE le cartelle in modalità semplice
        if isinstance(evento, EventoVisualizzaTutteCartelleSemplice):
            return self._render_tutte_cartelle_semplice(evento)

        # 12) istanza del evento per visualizzazione cartella avanzata
        if isinstance(evento, EventoVisualizzaCartellaAvanzata):
            return self._render_cartella_avanzata(evento)

        # 13) evento per visualizzazione di TUTTE le cartelle in modalità avanzata
        if isinstance(evento, EventoVisualizzaTutteCartelleAvanzata):
            return self._render_tutte_cartelle_avanzata(evento)

        # 14) evento per la stampa semplice delle righe di una cartella una per volta in base al movimento delle freccie 
        if isinstance(evento, EventoNavigazioneRiga):
            return self._render_evento_navigazione_riga(evento)

        # 15) istanza del metodo di renderer per la visualizzazione avanzata della riga 
        if isinstance(evento, EventoNavigazioneRigaAvanzata):
            return self._render_evento_navigazione_riga_avanzata(evento)

        # 16) evento per la stampa semplice delle colonne di una cartella una per volta in base al movimento delle frecce
        if isinstance(evento, EventoNavigazioneColonna):
            return self._render_evento_navigazione_colonna(evento)

        # 17) evento per la stampa avanzata delle colonne di una cartella una per volta in base al movimento delle frecce
        if isinstance(evento, EventoNavigazioneColonnaAvanzata):
            return self._render_evento_navigazione_colonna_avanzata(evento)

        # 18) evento per il feedback di segnazione numero: successo e casi non validi (già segnato / non presente / non estratto)
        if isinstance(evento, EventoSegnazioneNumero):
            return self._render_evento_segnazione_numero(evento)

        # 19) evento per la ricerca di un numero in tutte le cartelle: genera un report multi-riga (intestazione, riepilogo, dettagli)
        if isinstance(evento, EventoRicercaNumeroInCartelle):
            return self._render_evento_ricerca_numero_in_cartelle(evento)

        # 20) evento per la verifica sul tabellone: comunica se un numero è già stato estratto oppure no
        if isinstance(evento, EventoVerificaNumeroEstratto):
            return self._render_evento_verifica_numero_estratto(evento)

        # 21) evento per comunicare l'ultimo numero estratto dal tabellone (presente oppure nessuna estrazione)
        if isinstance(evento, EventoUltimoNumeroEstratto):
            return self._render_evento_ultimo_numero_estratto(evento)

        # 22) evento per comunicare gli ultimi N numeri estratti dal tabellone (lista breve oppure nessuna estrazione)
        if isinstance(evento, EventoUltimiNumeriEstratti):
            return self._render_evento_ultimi_numeri_estratti(evento)

        # 23) evento riepilogo tabellone: stampa 3 righe (sintesi globale + ultimi estratti + ultimo estratto)
        if isinstance(evento, EventoRiepilogoTabellone):
            return self._render_evento_riepilogo_tabellone(evento)

        # 24) evento lista completa numeri estratti: stampa intestazione + righe per decine non vuote (1–9, 10–19, ..., 80–90)
        if isinstance(evento, EventoListaNumeriEstratti):
            return self._render_evento_lista_numeri_estratti(evento)

        # 25) evento stato focus corrente: report fisso su 3 righe (cartella, riga, colonna)
        if isinstance(evento, EventoStatoFocusCorrente):
            return self._render_evento_stato_focus_corrente(evento)

        # 26) evento "vai a riga" (avanzato): selezione diretta riga e lettura su 2 righe (intestazione + contenuto con segnati)
        if isinstance(evento, EventoVaiARigaAvanzata):
            return self._render_evento_vai_a_riga_avanzata(evento)

        # 27) evento "vai a colonna" (avanzato): selezione diretta colonna e lettura su 2 righe (intestazione + contenuto con segnati)
        if isinstance(evento, EventoVaiAColonnaAvanzata):
            return self._render_evento_vai_a_colonna_avanzata(evento)

        # 28) evento reclamo vittoria (ANTE_TURNO): conferma registrazione + nota sulla validazione a fine turno
        if isinstance(evento, EventoReclamoVittoria):
            return self._render_evento_reclamo_vittoria_registrato(evento)

        # 28) evento fine turno: conferma "turno passato" + (opzionale) conferma reclamo inviato con il turno
        if isinstance(evento, EventoFineTurno):
            return self._render_evento_fine_turno(evento)

        # 0) Evento sconosciuto: fallback robusto.
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
        template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_INTESTAZIONE"][0]
        template_prefisso_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA"][0]
        parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]
        template_segnati_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_ETICHETTA_SEGNATI_RIGA"][0]
        testo_segnati_riga_nessuno = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_SEGNATI_RIGA_NESSUNO"][0]
        template_footer = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_FOOTER_RIEPILOGO"][0]

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
        template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_INTESTAZIONE"][0]
        template_prefisso_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA"][0]
        parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]
        template_segnati_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_ETICHETTA_SEGNATI_RIGA"][0]
        testo_segnati_riga_nessuno = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_SEGNATI_RIGA_NESSUNO"][0]
        template_footer = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_FOOTER_RIEPILOGO"][0]

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


    def _render_evento_navigazione_riga_avanzata(self, evento: EventoNavigazioneRigaAvanzata) -> tuple[str, ...]:
        """
        Rende l'EventoNavigazioneRigaAvanzata in righe testuali (3 righe nel caso "mostra").

        Scelte di output (coerenti con la navigazione riga semplice):
        - Caso esito="limite":
          * Produce UNA sola riga breve:
              - minimo -> UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO
              - massimo -> UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO

        - Caso esito="mostra":
          * Produce TRE righe:
            1) Intestazione riga avanzata: UMANI_RIGA_AVANZATA_INTESTAZIONE
            2) Contenuto riga: celle unite con ", " + riepilogo "Segnati: ..."
               - "-" -> parola dal dizionario (UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA)
               - numero non segnato -> "N"
               - numero segnato -> "N*" (asterisco aggiunto dal renderer)
            3) Footer riepilogo: UMANI_CARTELLA_AVANZATA_FOOTER_RIEPILOGO
               con i valori presi da evento.stato_riga

        Robustezza (come riga semplice):
        - Se arrivano dati incoerenti (es. esito="mostra" ma riga_semplice=None),
          ritorna una stringa vuota per coerenza con lo stile del progetto.
        """
        # 1) Caso "limite": messaggio breve, nessun altro contesto.
        if evento.esito == "limite":
            if evento.limite == "minimo":
                return (MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO"][0],)
            if evento.limite == "massimo":
                return (MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO"][0],)

            # Limite non riconosciuto (non dovrebbe accadere): output neutro.
            return ("",)

        # 2) Caso "mostra": intestazione + riga + footer.
        if evento.esito == "mostra":
            # Come nel renderer della riga semplice: controllo difensivo minimo.
            if evento.riga_semplice is None:
                return ("",)

            template_intestazione_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RIGA_AVANZATA_INTESTAZIONE"][0]
            parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]
            template_segnati_riga = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_ETICHETTA_SEGNATI_RIGA"][0]
            testo_segnati_riga_nessuno = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_SEGNATI_RIGA_NESSUNO"][0]
            template_footer = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_FOOTER_RIEPILOGO"][0]

            # Riga 1: intestazione avanzata.
            intestazione = template_intestazione_riga.format(numero_riga=evento.numero_riga_corrente)

            # Riga 2: contenuto celle + riepilogo segnati.
            segnati_set = set(evento.numeri_segnati_riga_ordinati)

            tokens: list[str] = []
            segnati_nella_riga: list[int] = []

            for cella in evento.riga_semplice:
                if cella == "-":
                    tokens.append(parola_vuoto)
                    continue

                numero = int(cella)
                if numero in segnati_set:
                    tokens.append(f"{numero}*")
                    segnati_nella_riga.append(numero)
                else:
                    tokens.append(str(numero))

            contenuto_riga = ", ".join(tokens)

            if not segnati_nella_riga:
                riepilogo_riga = testo_segnati_riga_nessuno
            else:
                lista_segnati = ", ".join(str(n) for n in sorted(segnati_nella_riga))
                riepilogo_riga = template_segnati_riga.format(lista_segnati=lista_segnati)

            riga_contenuto = f"{contenuto_riga}. {riepilogo_riga}"

            # Riga 3: footer riepilogo (totali e percentuale) preso dallo stato riga.
            numeri_segnati = int(evento.stato_riga["numeri_segnati"])
            numeri_totali = int(evento.stato_riga["numeri_totali"])
            percentuale = float(evento.stato_riga["percentuale_completamento"])
            footer = template_footer.format(
                numeri_segnati=numeri_segnati,
                numeri_totali=numeri_totali,
                percentuale=percentuale,
            )

            return (intestazione, riga_contenuto, footer)

        # 3) Esito sconosciuto (non dovrebbe accadere): output neutro.
        return ("",)


    def _render_evento_navigazione_colonna(self, evento: EventoNavigazioneColonna) -> tuple[str, ...]:
        """
        Rende l'EventoNavigazioneColonna in righe testuali, in modo poco verboso.

        Scelte di output (coerenti con la navigazione riga - modalità semplice):
        - Caso esito="mostra":
          * Produce UNA sola riga: "Colonna X: ..." + contenuto della colonna in formato semplice.
          * Celle unite con ", " in ordine dall'alto verso il basso:
              - "-" -> parola dal dizionario (UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA)
              - int -> str(numero)

        - Caso esito="limite":
          * Produce UNA sola riga breve:
              - minimo -> UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO
              - massimo -> UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO

        Robustezza:
        - Se arrivano dati incoerenti (es. esito="mostra" ma colonna_semplice=None),
          ritorna una stringa vuota per coerenza con lo stile del progetto.
        """

        # 1) Caso "limite": messaggio breve, nessun altro contesto.
        if evento.esito == "limite":
            if evento.limite == "minimo":
                return (MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO"][0],)
            if evento.limite == "massimo":
                return (MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO"][0],)

            # Limite non riconosciuto (non dovrebbe accadere): output neutro.
            return ("",)

        # 2) Caso "mostra": una sola riga "Colonna X: ..." + 3 celle.
        if evento.esito == "mostra":
            # Se per qualche motivo manca la colonna, non andiamo in errore.
            if evento.colonna_semplice is None:
                return ("",)

            template_prefisso_colonna = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_PREFISSO_COLONNA"][0]
            parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]

            # Prefisso: "Colonna {numero_colonna}: "
            prefisso = template_prefisso_colonna.format(numero_colonna=evento.numero_colonna_corrente)

            # Trasforma le 3 celle in token "parlabili" (dall'alto verso il basso).
            tokens: list[str] = []
            for cella in evento.colonna_semplice:
                if cella == "-":
                    tokens.append(parola_vuoto)
                else:
                    tokens.append(str(cella))

            return (prefisso + ", ".join(tokens),)

        # 3) Esito sconosciuto (non dovrebbe accadere): output neutro.
        return ("",)


    def _render_evento_navigazione_colonna_avanzata(self, evento: EventoNavigazioneColonnaAvanzata) -> tuple[str, ...]:
        """
        Rende l'EventoNavigazioneColonnaAvanzata in righe testuali (3 righe nel caso "mostra").

        Scelte di output (coerenti con la navigazione riga avanzata):
        - Caso esito="limite":
          * Produce UNA sola riga breve:
              - minimo -> UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO
              - massimo -> UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO

        - Caso esito="mostra":
          * Produce TRE righe:
            1) Intestazione colonna avanzata: UMANI_COLONNA_AVANZATA_INTESTAZIONE
            2) Contenuto colonna: celle unite con ", " + riepilogo "Segnati: ..."
               - "-" -> parola dal dizionario (UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA)
               - numero non segnato -> "N"
               - numero segnato -> "N*" (asterisco aggiunto dal renderer)
            3) Footer riepilogo colonna: UMANI_COLONNA_AVANZATA_FOOTER_RIEPILOGO
               con i valori presi da evento.stato_colonna

        Robustezza (coerente con gli altri renderer):
        - Se arrivano dati incoerenti o incompleti nel caso "mostra", ritorna ("",)
          invece di sollevare eccezioni.
        """

        # 1) Caso "limite": messaggio breve, nessun altro contesto.
        if evento.esito == "limite":
            if evento.limite == "minimo":
                return (MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO"][0],)
            if evento.limite == "massimo":
                return (MESSAGGI_OUTPUT_UI_UMANI["UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO"][0],)

            # Limite non riconosciuto (non dovrebbe accadere): output neutro.
            return ("",)

        # 2) Caso "mostra": intestazione + colonna + footer.
        if evento.esito == "mostra":
            # Controllo difensivo: se mancano dati, non andiamo in errore.
            if evento.colonna_semplice is None:
                return ("",)
            if evento.stato_colonna is None:
                return ("",)
            if evento.numeri_segnati_colonna_ordinati is None:
                return ("",)

            template_intestazione_colonna = MESSAGGI_OUTPUT_UI_UMANI["UMANI_COLONNA_AVANZATA_INTESTAZIONE"][0]
            parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]
            template_segnati_colonna = MESSAGGI_OUTPUT_UI_UMANI["UMANI_COLONNA_AVANZATA_ETICHETTA_SEGNATI"][0]
            testo_segnati_colonna_nessuno = MESSAGGI_OUTPUT_UI_UMANI["UMANI_COLONNA_AVANZATA_SEGNATI_NESSUNO"][0]
            template_footer = MESSAGGI_OUTPUT_UI_UMANI["UMANI_COLONNA_AVANZATA_FOOTER_RIEPILOGO"][0]

            # Riga 1: intestazione avanzata.
            intestazione = template_intestazione_colonna.format(numero_colonna=evento.numero_colonna_corrente)

            # Riga 2: contenuto celle + riepilogo segnati.
            segnati_set = set(evento.numeri_segnati_colonna_ordinati)

            tokens: list[str] = []
            segnati_nella_colonna: list[int] = []

            for cella in evento.colonna_semplice:
                if cella == "-":
                    tokens.append(parola_vuoto)
                    continue

                numero = int(cella)
                if numero in segnati_set:
                    tokens.append(f"{numero}*")
                    segnati_nella_colonna.append(numero)
                else:
                    tokens.append(str(numero))

            contenuto_colonna = ", ".join(tokens)

            if not segnati_nella_colonna:
                riepilogo_colonna = testo_segnati_colonna_nessuno
            else:
                lista_segnati = ", ".join(str(n) for n in sorted(segnati_nella_colonna))
                riepilogo_colonna = template_segnati_colonna.format(lista_segnati=lista_segnati)

            colonna_contenuto = f"{contenuto_colonna}. {riepilogo_colonna}"

            # Riga 3: footer riepilogo (totali e percentuale) preso dallo stato colonna.
            try:
                numeri_segnati = int(evento.stato_colonna["numeri_segnati"])
                numeri_totali = int(evento.stato_colonna["numeri_totali"])
                percentuale = float(evento.stato_colonna["percentuale_completamento"])
            except (KeyError, TypeError, ValueError):
                return ("",)

            footer = template_footer.format(
                numeri_segnati=numeri_segnati,
                numeri_totali=numeri_totali,
                percentuale=percentuale,
            )

            return (intestazione, colonna_contenuto, footer)

        # 3) Esito sconosciuto (non dovrebbe accadere): output neutro.
        return ("",)


    def _render_evento_segnazione_numero(self, evento: EventoSegnazioneNumero) -> tuple[str, ...]:
        """
        Rende l'EventoSegnazioneNumero in righe testuali, in modo poco verboso e stabile.

        Scelte di output:
        - Produce sempre UNA sola riga in tutti i casi previsti dal dizionario:
          * esito="segnato"      -> UMANI_SEGNAZIONE_NUMERO_SEGNATO
          * esito="gia_segnato"  -> UMANI_SEGNAZIONE_NUMERO_GIA_SEGNATO
          * esito="non_presente" -> UMANI_SEGNAZIONE_NUMERO_NON_PRESENTE
          * esito="non_estratto" -> UMANI_SEGNAZIONE_NUMERO_NON_ESTRATTO

        Conversioni/coerenza:
        - Le coordinate nell'evento sono 0-based (indice_riga/indice_colonna).
          Nel testo vanno rese "umane" (1-based) aggiungendo +1, ma solo quando presenti.

        Robustezza (coerente con gli altri renderer):
        - Se mancano dati necessari per il template scelto (es. coordinate None nel caso "segnato"),
          oppure l'esito è sconosciuto, ritorna ("",) per non rompere il sistema.
        - Se il dizionario non contiene una chiave attesa, ritorna ("",) come fallback neutro.
        """

        # 1) Caso: numero segnato con successo.
        if evento.esito == "segnato":
            # Per questo template servono anche coordinate; se non ci sono, fallback neutro.
            if evento.indice_riga is None or evento.indice_colonna is None:
                return ("",)

            try:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_SEGNAZIONE_NUMERO_SEGNATO"][0]
            except KeyError:
                return ("",)

            # Conversione 0-based -> 1-based per il testo "umano".
            numero_riga = evento.indice_riga + 1
            numero_colonna = evento.indice_colonna + 1

            return (template.format(
                numero=evento.numero,
                numero_riga=numero_riga,
                numero_colonna=numero_colonna,
            ),)

        # 2) Caso: numero già segnato.
        if evento.esito == "gia_segnato":
            try:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_SEGNAZIONE_NUMERO_GIA_SEGNATO"][0]
            except KeyError:
                return ("",)

            return (template.format(
                numero=evento.numero,
                numero_cartella=evento.numero_cartella,
            ),)

        # 3) Caso: numero non presente nella cartella.
        if evento.esito == "non_presente":
            try:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_SEGNAZIONE_NUMERO_NON_PRESENTE"][0]
            except KeyError:
                return ("",)

            return (template.format(
                numero=evento.numero,
                numero_cartella=evento.numero_cartella,
            ),)

        # 4) Caso: numero non ancora estratto.
        if evento.esito == "non_estratto":
            try:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_SEGNAZIONE_NUMERO_NON_ESTRATTO"][0]
            except KeyError:
                return ("",)

            return (template.format(numero=evento.numero),)

        # 5) Esito sconosciuto (non dovrebbe accadere): output neutro.
        return ("",)


    def _render_evento_ricerca_numero_in_cartelle(self, evento: EventoRicercaNumeroInCartelle) -> tuple[str, ...]:
        """
        Rende EventoRicercaNumeroInCartelle in un report testuale stabile e deterministico.

        Contratto di output:
        - Ritorna sempre una tuple di righe (tuple[str, ...]).
        - Prima riga sempre presente: intestazione ricerca.
        - Se esito="non_trovato": 2 righe (intestazione + non trovato).
        - Se esito="trovato": almeno 3 righe (intestazione + riepilogo + N righe dettagli).

        Regole di formattazione:
        - Dettagli: una riga per ogni cartella trovata, in ordine deterministico (già garantito dall'evento).
        - Conversioni per UI:
          * numero_cartella arriva già 1-based (dal RisultatoRicercaNumeroInCartella).
          * indice_riga e indice_colonna sono 0-based: il renderer converte in 1-based con +1.

        Robustezza:
        - Se l'esito è incoerente con i risultati (es. trovato ma risultati vuoti), ritorna ("",).
        - Se manca una chiave nel dizionario o un placeholder non è formattabile, ritorna ("",).
        - Se un risultato contiene dati non validi (indici non convertibili), ritorna ("",).
        """

        # ---- Lettura template dal dizionario (tutto difensivo, niente eccezioni verso l'esterno) ----
        try:
            template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RICERCA_NUMERO_INTESTAZIONE"][0]
            template_non_trovato = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RICERCA_NUMERO_NON_TROVATO"][0]
            template_riep_singolare = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_SINGOLARE"][0]
            template_riep_plurale = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_PLURALE"][0]
            template_riga_risultato = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RICERCA_NUMERO_RISULTATO_RIGA"][0]
            testo_stato_segnato = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RICERCA_NUMERO_STATO_SEGNATO"][0]
            testo_stato_da_segnare = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RICERCA_NUMERO_STATO_DA_SEGNARE"][0]
        except KeyError:
            return ("",)

        # ---- Riga 1: intestazione (sempre) ----
        try:
            intestazione = template_intestazione.format(
                numero=evento.numero,
                totale_cartelle=evento.totale_cartelle,
            )
        except Exception:
            return ("",)

        # ---- Caso: non trovato ----
        if evento.esito == "non_trovato":
            # Coerenza: per "non_trovato" ci si aspetta risultati vuoti.
            if evento.risultati:
                return ("",)

            try:
                riga_esito = template_non_trovato.format(numero=evento.numero)
            except Exception:
                return ("",)

            return (intestazione, riga_esito)

        # ---- Caso: trovato ----
        if evento.esito == "trovato":
            # Coerenza: per "trovato" ci si aspetta almeno 1 risultato.
            if not evento.risultati:
                return ("",)

            conteggio_cartelle = len(evento.risultati)

            # Riga 2: riepilogo trovato (singolare/plurale).
            try:
                if conteggio_cartelle == 1:
                    riepilogo = template_riep_singolare.format(numero=evento.numero)
                else:
                    riepilogo = template_riep_plurale.format(
                        numero=evento.numero,
                        conteggio_cartelle=conteggio_cartelle,
                    )
            except Exception:
                return ("",)

            # Righe successive: dettaglio per ogni risultato.
            righe_dettaglio: list[str] = []
            for r in evento.risultati:
                # Stato: parola breve dal dizionario.
                stato = testo_stato_segnato if bool(r.segnato) else testo_stato_da_segnare

                # Conversioni 0-based -> 1-based per la UI.
                try:
                    numero_riga = int(r.indice_riga) + 1
                    numero_colonna = int(r.indice_colonna) + 1
                    numero_cartella = int(r.numero_cartella)
                except (TypeError, ValueError):
                    return ("",)

                try:
                    riga_dettaglio = template_riga_risultato.format(
                        numero_cartella=numero_cartella,
                        numero_riga=numero_riga,
                        numero_colonna=numero_colonna,
                        stato=stato,
                    )
                except Exception:
                    return ("",)

                righe_dettaglio.append(riga_dettaglio)

            return (intestazione, riepilogo, *righe_dettaglio)

        # ---- Esito sconosciuto (non dovrebbe accadere) ----
        return ("",)


    def _render_evento_verifica_numero_estratto(self, evento: EventoVerificaNumeroEstratto) -> tuple[str, ...]:
        """
        Rende l'EventoVerificaNumeroEstratto in una sola riga testuale, stabile e poco verbosa.

        Scelte di output:
        - Se evento.estratto è True:
          * Usa UMANI_VERIFICA_NUMERO_ESTRATTO_SI e sostituisce {numero}.
        - Se evento.estratto è False:
          * Usa UMANI_VERIFICA_NUMERO_ESTRATTO_NO e sostituisce {numero}.

        Robustezza (coerente con gli altri renderer del progetto):
        - Se manca la chiave nel dizionario o la formattazione fallisce, ritorna ("",).
        - Non solleva eccezioni verso l'esterno: fallback neutro per non rompere la UI.
        """

        # 1) Selezione della chiave dizionario in base al booleano (nessuna logica di dominio).
        codice = "UMANI_VERIFICA_NUMERO_ESTRATTO_SI" if bool(evento.estratto) else "UMANI_VERIFICA_NUMERO_ESTRATTO_NO"

        # 2) Recupero template in modo difensivo.
        try:
            template = MESSAGGI_OUTPUT_UI_UMANI[codice][0]
        except KeyError:
            return ("",)

        # 3) Formattazione finale (sempre una sola riga).
        try:
            riga = template.format(numero=evento.numero)
        except Exception:
            return ("",)

        return (riga,)


    def _render_evento_ultimo_numero_estratto(self, evento: EventoUltimoNumeroEstratto) -> tuple[str, ...]:
        """
        Rende EventoUltimoNumeroEstratto in una sola riga, in modo stabile e poco verboso.

        Scelte di output:
        - Se evento.ultimo_numero è None:
          * Usa UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO.
        - Se evento.ultimo_numero è un int:
          * Usa UMANI_ULTIMO_NUMERO_ESTRATTO_PRESENTE e sostituisce {ultimonumero}.

        Robustezza (coerente con gli altri renderer del progetto):
        - Se manca la chiave nel dizionario o la formattazione fallisce, ritorna ("",).
        - Se ultimo_numero è di tipo inatteso, ritorna ("",) per non generare eccezioni.
        """

        # 1) Selezione chiave dizionario in base alla disponibilità del dato.
        if evento.ultimo_numero is None:
            codice = "UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO"
        else:
            # Difesa minima: il renderer accetta solo int "puliti" come ultimo numero.
            if not isinstance(evento.ultimo_numero, int):
                return ("",)
            codice = "UMANI_ULTIMO_NUMERO_ESTRATTO_PRESENTE"

        # 2) Recupero template in modo difensivo.
        try:
            template = MESSAGGI_OUTPUT_UI_UMANI[codice][0]
        except KeyError:
            return ("",)

        # 3) Formattazione finale (sempre una sola riga).
        try:
            if codice == "UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO":
                riga = template
            else:
                riga = template.format(ultimonumero=evento.ultimo_numero)
        except Exception:
            return ("",)

        return (riga,)


    def _render_evento_ultimi_numeri_estratti(self, evento: EventoUltimiNumeriEstratti) -> tuple[str, ...]:
        """
        Rende EventoUltimiNumeriEstratti in una sola riga testuale, stabile e poco verbosa.

        Scelte di output:
        - Se non ci sono numeri disponibili (evento.visualizzati == 0 oppure evento.numeri vuota):
          * Usa UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO.
        - Se ci sono numeri disponibili:
          * Usa UMANI_ULTIMI_NUMERI_ESTRATTI_PRESENTI e sostituisce:
            - {visualizzati} con il conteggio effettivo mostrato
            - {lista} con i numeri uniti da ", " nell'ordine fornito dal tabellone

        Coerenza:
        - Il renderer non riordina i numeri: rispetta l'ordine già deciso dal tabellone.
        - Output sempre su una sola riga (adatto a screen reader e UI testuale).

        Robustezza:
        - Se mancano chiavi nel dizionario o la formattazione fallisce, ritorna ("",).
        - Se i dati sono incoerenti (es. visualizzati != len(numeri)), il renderer usa i dati concreti (len(numeri))
          per costruire una frase coerente, senza sollevare eccezioni.
        """

        # 1) Normalizza in modo difensivo il conteggio effettivo basandosi sulla tupla numeri.
        try:
            numeri = tuple(evento.numeri)
        except Exception:
            return ("",)

        visualizzati_effettivi = len(numeri)

        # 2) Caso "nessuna estrazione": messaggio breve e coerente con gli altri eventi.
        if visualizzati_effettivi == 0 or int(getattr(evento, "visualizzati", 0)) == 0:
            try:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO"][0]
            except KeyError:
                return ("",)

            return (template,)

        # 3) Caso "numeri presenti": una sola riga con elenco.
        try:
            template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_ULTIMI_NUMERI_ESTRATTI_PRESENTI"][0]
        except KeyError:
            return ("",)

        # 4) Costruisce la lista "parlabile": numeri separati da virgola e spazio.
        #    join() richiede stringhe, quindi convertiamo ogni elemento in str. [web:168]
        try:
            lista = ", ".join(str(int(n)) for n in numeri)
        except Exception:
            return ("",)

        # 5) Formattazione finale.
        try:
            riga = template.format(
                visualizzati=visualizzati_effettivi,
                lista=lista,
            )
        except Exception:
            return ("",)

        return (riga,)


    def _render_evento_riepilogo_tabellone(self, evento: EventoRiepilogoTabellone) -> tuple[str, ...]:
        """
        Rende EventoRiepilogoTabellone in 3 righe testuali, coerenti e stabili.

        Output (sempre 3 righe, in ordine fisso):
        1) Sintesi globale tabellone: UMANI_RIEPILOGO_TABELLONE_RIGA_1
        2) Ultimi numeri estratti (lista breve):
           - se nessuna estrazione -> UMANI_ULTIMI_NUMERI_ESTRATTI_NESSUNO
           - altrimenti           -> UMANI_ULTIMI_NUMERI_ESTRATTI_PRESENTI
        3) Ultimo numero estratto (singolo):
           - se nessuna estrazione -> UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO
           - altrimenti           -> UMANI_ULTIMO_NUMERO_ESTRATTO_PRESENTE

        Note di coerenza:
        - Il renderer non riordina: rispetta l'ordine della tupla ultimi_estratti (dal più vecchio al più recente).
        - La lista dei numeri usa sempre separatore ', ' (virgola + spazio) come richiesto.

        Robustezza (come gli altri renderer del progetto):
        - Non solleva eccezioni: se qualcosa va storto, ogni riga diventa "".
        - Mantiene comunque il contratto: restituisce sempre una tupla di 3 righe.
        """

        # --- Riga 1: sintesi globale ---
        riga_1 = ""
        try:
            template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RIEPILOGO_TABELLONE_RIGA_1"][0]
            riga_1 = template.format(
                totale_estratti=evento.totale_estratti,
                totale_numeri=evento.totale_numeri,
                totale_mancanti=evento.totale_mancanti,
                percentuale_estrazione=evento.percentuale_estrazione,
            )
        except Exception:
            riga_1 = ""

        # --- Riga 2: ultimi numeri estratti (lista breve) ---
        riga_2 = ""
        try:
            ultimi = tuple(evento.ultimi_estratti)
            visualizzati = len(ultimi)

            if visualizzati == 0 or int(getattr(evento, "ultimi_visualizzati", 0)) == 0:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_ULTIMI_NUMERI_ESTRATTI_NESSUNO"][0]
                riga_2 = template
            else:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_ULTIMI_NUMERI_ESTRATTI_PRESENTI"][0]

                # Lista con virgola e spazio come richiesto.
                lista = ", ".join(str(int(n)) for n in ultimi)

                riga_2 = template.format(
                    visualizzati=visualizzati,
                    lista=lista,
                )
        except Exception:
            riga_2 = ""

        # --- Riga 3: ultimo estratto (singolo) ---
        riga_3 = ""
        try:
            if evento.ultimo_estratto is None:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO"][0]
                riga_3 = template
            else:
                # Difesa minima: il renderer accetta solo int "puliti".
                if not isinstance(evento.ultimo_estratto, int):
                    raise TypeError("ultimo_estratto non è int")

                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_ULTIMO_NUMERO_ESTRATTO_PRESENTE"][0]

                # Nota: nel tuo dizionario il placeholder è {ultimo_numero}.
                riga_3 = template.format(ultimo_numero=evento.ultimo_estratto)
        except Exception:
            riga_3 = ""

        return (riga_1, riga_2, riga_3)


    def _render_evento_lista_numeri_estratti(self, evento: EventoListaNumeriEstratti) -> tuple[str, ...]:
        """
        Rende EventoListaNumeriEstratti in un report testuale "a decine", stabile e consultabile.

        Struttura output:
        - Riga 1: intestazione con UMANI_LISTA_NUMERI_ESTRATTI_INTESTAZIONE.
        - Righe successive: una riga per ogni decina NON vuota:
            1–9, 10–19, 20–29, ..., 80–90
          usando UMANI_LISTA_NUMERI_ESTRATTI_DECINA_LISTA.

        Regole di impaginazione (come richiesto):
        - I numeri sono già in ordine crescente (garantito dall'evento).
        - Le decine vuote NON vengono stampate.
        - La lista all'interno della decina è separata da ", " (virgola + spazio).

        Robustezza:
        - Se mancano chiavi nel dizionario o la formattazione fallisce, ritorna ("",).
        - Se i dati risultano incoerenti (es. totale_estratti non compatibile), il renderer non solleva eccezioni.
        """

        # 1) Recupero templates in modo difensivo.
        try:
            template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_LISTA_NUMERI_ESTRATTI_INTESTAZIONE"][0]
            template_decina = MESSAGGI_OUTPUT_UI_UMANI["UMANI_LISTA_NUMERI_ESTRATTI_DECINA_LISTA"][0]
        except KeyError:
            return ("",)

        # 2) Normalizza la lista numeri in modo difensivo.
        try:
            numeri = tuple(int(n) for n in evento.numeri_estratti)
        except Exception:
            return ("",)

        # 3) Intestazione (sempre presente).
        try:
            intestazione = template_intestazione.format(totale_estratti=evento.totale_estratti)
        except Exception:
            return ("",)

        righe: list[str] = [intestazione]

        # 4) Prepara i bucket per decine:
        #    - 1..9 trattata come "decina" speciale (da=1, a=9)
        #    - 10..19, 20..29, ..., 80..90
        # Nota: 90 sta da solo come "80–90" per restare coerenti col tuo esempio e col tabellone 1..90.
        buckets: dict[tuple[int, int], list[int]] = {
            (1, 9): [],
            (10, 19): [],
            (20, 29): [],
            (30, 39): [],
            (40, 49): [],
            (50, 59): [],
            (60, 69): [],
            (70, 79): [],
            (80, 90): [],
        }

        # 5) Inserisce ogni numero estratto nel bucket corretto.
        #    Eventuali numeri fuori range (non dovrebbero arrivare) vengono ignorati per stabilità.
        for n in numeri:
            if 1 <= n <= 9:
                buckets[(1, 9)].append(n)
                continue

            if 10 <= n <= 79:
                start = (n // 10) * 10
                end = start + 9
                key = (start, end)
                if key in buckets:
                    buckets[key].append(n)
                continue

            if 80 <= n <= 90:
                buckets[(80, 90)].append(n)
                continue

            # Fuori range: non rompiamo il renderer.
            continue

        # 6) Emissione righe per le decine NON vuote, in ordine deterministico.
        ordine_decine = (
            (1, 9),
            (10, 19),
            (20, 29),
            (30, 39),
            (40, 49),
            (50, 59),
            (60, 69),
            (70, 79),
            (80, 90),
        )

        for da, a in ordine_decine:
            lista_numeri = buckets[(da, a)]
            if not lista_numeri:
                # Decina vuota: la saltiamo.
                continue

            # Lista "parlabile" con virgola e spazio. [web:177]
            lista = ", ".join(str(x) for x in lista_numeri)

            try:
                riga = template_decina.format(da=da, a=a, lista=lista)
            except Exception:
                return ("",)

            righe.append(riga)

        return tuple(righe)


    def _render_evento_stato_focus_corrente(self, evento: EventoStatoFocusCorrente) -> tuple[str, ...]:
        """
        Rende EventoStatoFocusCorrente in 3 righe stabili e prevedibili:
        1) Cartella in focus (presente/nessuna)
        2) Riga in focus (presente/nessuna)
        3) Colonna in focus (presente/nessuna)

        Coerenza:
        - I numeri nell'evento sono già "umani" (1-based): il renderer non fa conversioni.
        - Output sempre in ordine fisso per facilitare ascolto e test.

        Robustezza (a prova di crash):
        - Nessuna eccezione verso l'esterno.
        - Se una chiave manca o la formattazione fallisce, la singola riga diventa "".
        - Ritorna sempre una tupla di 3 righe.
        """

        # --- Riga 1: cartella ---
        riga_cartella = ""
        try:
            if evento.numero_cartella is None:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_STATO_FOCUS_CORRENTE_CARTELLA_NESSUNA"][0]
                riga_cartella = template
            else:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_STATO_FOCUS_CORRENTE_CARTELLA_PRESENTE"][0]
                riga_cartella = template.format(
                    numero_cartella=evento.numero_cartella,
                    totale_cartelle=evento.totale_cartelle,
                )
        except Exception:
            riga_cartella = ""

        # --- Riga 2: riga ---
        riga_riga = ""
        try:
            if evento.numero_riga is None:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_STATO_FOCUS_CORRENTE_RIGA_NESSUNA"][0]
                riga_riga = template
            else:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_STATO_FOCUS_CORRENTE_RIGA_PRESENTE"][0]
                riga_riga = template.format(numero_riga=evento.numero_riga)
        except Exception:
            riga_riga = ""

        # --- Riga 3: colonna ---
        riga_colonna = ""
        try:
            if evento.numero_colonna is None:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_STATO_FOCUS_CORRENTE_COLONNA_NESSUNA"][0]
                riga_colonna = template
            else:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_STATO_FOCUS_CORRENTE_COLONNA_PRESENTE"][0]
                riga_colonna = template.format(numero_colonna=evento.numero_colonna)
        except Exception:
            riga_colonna = ""

        return (riga_cartella, riga_riga, riga_colonna)


    def _render_evento_vai_a_riga_avanzata(self, evento: EventoVaiARigaAvanzata) -> tuple[str, ...]:
        """
        Rende EventoVaiARigaAvanzata in 2 righe testuali, in modo stabile e coerente.

        Output richiesto (sempre 2 righe, ordine fisso):
        1) Intestazione: UMANI_RIGA_AVANZATA_INTESTAZIONE
        2) Contenuto riga: numeri/vuoti + riepilogo segnati (stile riga avanzata già esistente)
           - "-" -> parola dal dizionario UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA
           - numero segnato -> "N*" (asterisco aggiunto dal renderer)
           - numero non segnato -> "N"
           + ". " + ("Segnati: ..." oppure "Segnati: nessuno.")

        Robustezza (a prova di crash):
        - Se mancano chiavi nel dizionario o dati incoerenti, ritorna ("", "").
        - Nessuna eccezione verso l'esterno.
        """

        # --- Riga 1: intestazione ---
        intestazione = ""
        try:
            template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RIGA_AVANZATA_INTESTAZIONE"][0]
            intestazione = template_intestazione.format(numero_riga=evento.numero_riga)
        except Exception:
            intestazione = ""

        # --- Riga 2: contenuto + riepilogo segnati ---
        riga_contenuto = ""
        try:
            parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]
            template_segnati = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_ETICHETTA_SEGNATI_RIGA"][0]
            testo_segnati_nessuno = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_AVANZATA_SEGNATI_RIGA_NESSUNO"][0]
        except KeyError:
            return ("", "")

        try:
            segnati_set = set(evento.numeri_segnati_riga_ordinati)

            tokens: list[str] = []
            segnati_nella_riga: list[int] = []

            for cella in evento.riga_semplice:
                if cella == "-":
                    tokens.append(parola_vuoto)
                    continue

                numero = int(cella)
                if numero in segnati_set:
                    tokens.append(f"{numero}*")
                    segnati_nella_riga.append(numero)
                else:
                    tokens.append(str(numero))

            contenuto = ", ".join(tokens)

            if not segnati_nella_riga:
                riepilogo = testo_segnati_nessuno
            else:
                lista_segnati = ", ".join(str(n) for n in sorted(segnati_nella_riga))
                riepilogo = template_segnati.format(lista_segnati=lista_segnati)

            riga_contenuto = f"{contenuto}. {riepilogo}"
        except Exception:
            riga_contenuto = ""

        return (intestazione, riga_contenuto)


    def _render_evento_vai_a_colonna_avanzata(self, evento: EventoVaiAColonnaAvanzata) -> tuple[str, ...]:
        """
        Rende EventoVaiAColonnaAvanzata in 2 righe testuali, in modo stabile e coerente.

        Output richiesto (sempre 2 righe, ordine fisso):
        1) Intestazione: UMANI_COLONNA_AVANZATA_INTESTAZIONE
        2) Contenuto colonna: numeri/vuoti + riepilogo segnati
           - "-" -> parola dal dizionario UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA
           - numero segnato -> "N*" (asterisco aggiunto dal renderer)
           - numero non segnato -> "N"
           + ". " + ("Segnati: ..." oppure "Segnati: nessuno.")

        Robustezza (a prova di crash):
        - Se mancano chiavi nel dizionario o dati incoerenti, ritorna ("", "").
        - Nessuna eccezione verso l'esterno.
        """

        # --- Riga 1: intestazione ---
        intestazione = ""
        try:
            template_intestazione = MESSAGGI_OUTPUT_UI_UMANI["UMANI_COLONNA_AVANZATA_INTESTAZIONE"][0]
            intestazione = template_intestazione.format(numero_colonna=evento.numero_colonna)
        except Exception:
            intestazione = ""

        # --- Riga 2: contenuto + riepilogo segnati ---
        colonna_contenuto = ""
        try:
            parola_vuoto = MESSAGGI_OUTPUT_UI_UMANI["UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA"][0]
            template_segnati = MESSAGGI_OUTPUT_UI_UMANI["UMANI_COLONNA_AVANZATA_ETICHETTA_SEGNATI"][0]
            testo_segnati_nessuno = MESSAGGI_OUTPUT_UI_UMANI["UMANI_COLONNA_AVANZATA_SEGNATI_NESSUNO"][0]
        except KeyError:
            return ("", "")

        try:
            segnati_set = set(evento.numeri_segnati_colonna_ordinati)

            tokens: list[str] = []
            segnati_nella_colonna: list[int] = []

            # Celle dall'alto verso il basso.
            for cella in evento.colonna_semplice:
                if cella == "-":
                    tokens.append(parola_vuoto)
                    continue

                numero = int(cella)
                if numero in segnati_set:
                    tokens.append(f"{numero}*")
                    segnati_nella_colonna.append(numero)
                else:
                    tokens.append(str(numero))

            contenuto = ", ".join(tokens)  # join richiede stringhe: abbiamo già tokens in str.

            if not segnati_nella_colonna:
                riepilogo = testo_segnati_nessuno
            else:
                lista_segnati = ", ".join(str(n) for n in sorted(segnati_nella_colonna))
                riepilogo = template_segnati.format(lista_segnati=lista_segnati)

            colonna_contenuto = f"{contenuto}. {riepilogo}"
        except Exception:
            colonna_contenuto = ""

        return (intestazione, colonna_contenuto)


    def _render_evento_reclamo_vittoria_registrato(self, evento: EventoReclamoVittoria) -> tuple[str, ...]:
        """
        Rende EventoReclamoVittoria (fase ANTE_TURNO) in 2 righe per UI/screen reader.

        Output (sempre 2 righe, ordine fisso):
        1) Conferma registrazione reclamo:
           - tombola  -> UMANI_RECLAMO_VITTORIA_TOMBOLA_REGISTRATO
           - vittoria di riga -> UMANI_RECLAMO_VITTORIA_RIGA_REGISTRATO (con {tipo})
        2) Nota standard: UMANI_RECLAMO_VITTORIA_NOTA_VALIDAZIONE

        Stabilità (come richiesto):
        - In ogni caso di errore (chiave mancante, format fallito, dati incoerenti),
          ritorna ("", "") senza fallback alternativi e senza sollevare eccezioni.
        """

        # In questo renderer consideriamo solo la conferma "soft" ANTE_TURNO.
        # Se arriva una fase diversa, per coerenza e stabilità non stampiamo nulla.
        try:
            if getattr(evento, "fase", None) != "ANTE_TURNO":
                return ("", "")
        except Exception:
            return ("", "")

        # --- Riga 1: conferma registrazione ---
        riga_1 = ""
        try:
            tipo = getattr(evento.reclamo, "tipo", None)

            if tipo == "tombola":
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RECLAMO_VITTORIA_TOMBOLA_REGISTRATO"][0]
                riga_1 = template
            else:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RECLAMO_VITTORIA_RIGA_REGISTRATO"][0]
                riga_1 = template.format(tipo=str(tipo))
        except Exception:
            riga_1 = ""

        # --- Riga 2: nota validazione ---
        riga_2 = ""
        try:
            template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RECLAMO_VITTORIA_NOTA_VALIDAZIONE"][0]
            riga_2 = template
        except Exception:
            riga_2 = ""

        return (riga_1, riga_2)


    def _render_evento_fine_turno(self, evento: EventoFineTurno) -> tuple[str, ...]:
        """
        Rende EventoFineTurno in una sola riga, coerente con gli altri messaggi di conferma.

        Casi:
        - Se evento.reclamo_turno è None:
          * UMANI_FINE_TURNO_PASSATO
        - Se evento.reclamo_turno è presente:
          * UMANI_FINE_TURNO_PASSATO_CON_RECLAMO con {tipo}

        Stabilità (a prova di crash):
        - In caso di qualunque problema (chiavi mancanti, format fallito, dati non presenti),
          ritorna ("",) e non solleva eccezioni.
        """

        # 1) Scelta del template in base alla presenza del reclamo nel turno.
        try:
            reclamo = getattr(evento, "reclamo_turno", None)
        except Exception:
            return ("",)

        # 2) Caso senza reclamo: messaggio semplice.
        if reclamo is None:
            try:
                template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_FINE_TURNO_PASSATO"][0]
                return (template,)
            except Exception:
                return ("",)

        # 3) Caso con reclamo: include il tipo (ambo/terno/quaterna/cinquina/tombola).
        try:
            template = MESSAGGI_OUTPUT_UI_UMANI["UMANI_FINE_TURNO_PASSATO_CON_RECLAMO"][0]
        except Exception:
            return ("",)

        try:
            tipo = getattr(reclamo, "tipo", None)
            if tipo is None:
                return ("",)

            riga = template.format(tipo=str(tipo))
        except Exception:
            return ("",)

        return (riga,)


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
