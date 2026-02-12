from __future__ import annotations

from bingo_game.events.eventi import EsitoAzione
from bingo_game.events.eventi_partita import (
    TipoVittoria,
    ReclamoVittoria,
    EventoReclamoVittoria,
)


class ReclamiFocusMixin:
    """
    Mixin di supporto per la gestione dei reclami vittoria.

    Questa classe NON rappresenta un giocatore: aggiunge metodi che creano
    eventi di reclamo partendo dai focus interni (cartella/riga) e dai dati
    del giocatore (id e nome).
    """

    #metodi helper di classe

    #metodo 1.
    def _esito_prerequisiti_reclamo_cartella(self) -> EsitoAzione:
        """
        Verifica i prerequisiti minimi per poter creare/registrare un reclamo legato alla cartella
        (es. tombola), usando esclusivamente il focus interno.

        Obiettivo:
        - Garantire che esista una cartella valida in focus su cui “agganciare” il reclamo.
        - Questo controllo è *rigoroso*: NON auto-imposta il focus cartella.

        Cosa fa:
        - Delega al controllo di focus cartella valido con auto_imposta=False.
        - Propaga l'errore così com'è (codice errore coerente con CodiceErrore).

        Cosa NON fa:
        - Non verifica se la vittoria esiste davvero sulla cartella (quello è compito della Partita).
        - Non genera eventi: in caso di successo ritorna sempre evento=None (helper silenzioso).

        Ritorna:
        - EsitoAzione(ok=True) se il focus cartella è impostato ed è dentro range.
        - EsitoAzione(ok=False, errore=...) se mancano prerequisiti o il focus è incoerente.
        """

        # Per i reclami vogliamo essere rigorosi: niente auto-impostazione del focus cartella.
        esito_focus = self._esito_focus_cartella_valido(auto_imposta=False)

        # Se non ho una cartella valida in focus, non posso creare un reclamo “formale”.
        if not esito_focus.ok:
            return esito_focus

        # Prerequisiti soddisfatti: nessun evento da propagare in questa fase.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 2.
    def _esito_prerequisiti_reclamo_riga(self) -> EsitoAzione:
        """
        Verifica i prerequisiti minimi per poter creare/registrare un reclamo legato a una riga
        (ambo/terno/quaterna/cinquina), usando esclusivamente i focus interni.

        Obiettivo:
        - Garantire che esista una cartella valida in focus e che esista anche una riga valida in focus.
        - Questo controllo è *rigoroso*: NON auto-imposta né la cartella né la riga.

        Strategia:
        1) Riusa `_esito_prerequisiti_reclamo_cartella()` per garantire che la cartella in focus sia valida.
        2) Verifica che `_indice_riga_focus` sia impostato.
        3) Verifica che `_indice_riga_focus` sia dentro range rispetto alla cartella in focus.

        Cosa NON fa:
        - Non verifica se la vittoria esiste davvero sulla riga (la validazione reale è compito della Partita).
        - Non genera eventi: in caso di successo ritorna sempre evento=None (helper silenzioso).

        Ritorna:
        - EsitoAzione(ok=True) se cartella e riga in focus sono impostate e coerenti.
        - EsitoAzione(ok=False, errore=...) se mancano prerequisiti o lo stato dei focus è incoerente.
        """

        # 1) Prerequisito cartella (rigoroso): devo avere una cartella valida in focus.
        esito_cartella = self._esito_prerequisiti_reclamo_cartella()
        if not esito_cartella.ok:
            return esito_cartella

        # 2) Prerequisito riga (rigoroso): la riga deve essere stata selezionata esplicitamente.
        if self._indice_riga_focus is None:
            return EsitoAzione(
                ok=False,
                errore="FOCUS_RIGA_NON_IMPOSTATA",
                evento=None,
            )

        # 3) Controllo difensivo: la riga deve essere compatibile con la cartella attualmente in focus.
        #    A questo punto `_indice_cartella_focus` è garantito non-None e in range.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]

        if self._indice_riga_focus < 0 or self._indice_riga_focus >= cartella_in_focus.righe:
            return EsitoAzione(
                ok=False,
                errore="FOCUS_RIGA_FUORI_RANGE",
                evento=None,
            )

        # 4) Prerequisiti soddisfatti: nessun evento da propagare in questa fase.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 3.
    def _esito_crea_evento_reclamo_da_focus(self, tipo: TipoVittoria) -> EsitoAzione:
        """
        Crea un EventoReclamoVittoria (fase ANTE_TURNO) usando esclusivamente i focus interni.

        Scopo:
        - Unificare in un solo punto:
          1) verifica prerequisiti (rigorosi, senza auto-impostazione),
          2) creazione del DTO ReclamoVittoria,
          3) incapsulamento in EventoReclamoVittoria pronto per essere inviato alla Partita.

        Regola importante:
        - Questo metodo NON deve mai sollevare eccezioni per prerequisiti mancanti:
          in caso di problemi ritorna EsitoAzione(ok=False, errore=CodiceErrore).
          (Coerente con il pattern degli altri helper.)

        Strategia prerequisiti:
        - Se tipo == "tombola": serve solo una cartella valida in focus.
        - Altrimenti (ambo/terno/quaterna/cinquina): serve cartella valida + riga valida in focus.

        Ritorna:
        - EsitoAzione(ok=False, errore=..., evento=None) se i prerequisiti non sono soddisfatti.
        - EsitoAzione(ok=True, errore=None, evento=EventoReclamoVittoria(...)) se tutto ok.
        """

        # 1) Seleziono il controllo prerequisiti corretto in base al tipo di vittoria.
        #    Tutti i prerequisiti sono "rigorosi": niente auto-impostazione.
        if tipo == "tombola":
            esito_prereq = self._esito_prerequisiti_reclamo_cartella()
        else:
            esito_prereq = self._esito_prerequisiti_reclamo_riga()

        # 2) Se mancano prerequisiti o lo stato focus è incoerente, propago l'errore così com'è.
        if not esito_prereq.ok:
            return esito_prereq

        # 3) A questo punto i prerequisiti garantiscono:
        #    - _indice_cartella_focus non è None ed è in range
        #    - per reclami di riga: _indice_riga_focus non è None ed è in range
        indice_cartella = self._indice_cartella_focus

        # 4) Costruisco il ReclamoVittoria coerente col tipo.
        if tipo == "tombola":
            reclamo = ReclamoVittoria(
                tipo=tipo,
                indice_cartella=indice_cartella,
                indice_riga=None,
            )
        else:
            indice_riga = self._indice_riga_focus

            # Difensivo: non dovrebbe accadere dopo i prerequisiti.
            if indice_riga is None:
                return EsitoAzione(
                    ok=False,
                    errore="FOCUS_RIGA_NON_IMPOSTATA",
                    evento=None,
                )

            reclamo = ReclamoVittoria(
                tipo=tipo,
                indice_cartella=indice_cartella,
                indice_riga=indice_riga,
            )

        # 5) Incapsulo il reclamo in un evento "soft" ANTE_TURNO (warning, revocabile).
        evento = EventoReclamoVittoria(
            id_giocatore=self.id_giocatore,
            nome_giocatore=self.nome,
            reclamo=reclamo,
            fase="ANTE_TURNO",
        )

        # 6) Successo: ritorno esito ok con payload evento pronto per la Partita.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=evento,
        )
