from __future__ import annotations

from bingo_game.events.eventi import EsitoAzione
from bingo_game.events.eventi_ui import EventoFocusAutoImpostato, EventoFocusCartellaImpostato


class GestioneFocusMixin:
    """
    Mixin di supporto per la gestione del focus (cartella/riga/colonna).

    Questa classe NON rappresenta un giocatore: aggiunge metodi di utilità
    a classi che sono già giocatori (es. GiocatoreUmano/GiocatoreAutomatico)
    e che quindi possiedono attributi come:
    - self.cartelle
    - self._indice_cartella_focus, self._indice_riga_focus, self._indice_colonna_focus
    """


    #metodi di helper per giocatore umano utili alla gestione dei focus di cartella/riga/colonna

    #sezione 1: metodi riferiti ai focus della cartella

    #metodo 1.
    def _esito_ha_cartelle(self) -> EsitoAzione:
        """
        Controlla se il giocatore ha almeno una cartella assegnata.

        Questo helper serve come controllo base (guardia) per molte azioni:
        navigazione, segnatura numeri, annunci vincite. [file:5]

        Differenza rispetto alla versione precedente:
        - Non ritorna più testo pronto per l'utente.
        - Ritorna un EsitoAzione con un codice errore, così la UI (o un layer esterno)
        potrà scegliere la frase corretta in base alla lingua. [file:2]

        Ritorna:
        - EsitoAzione(ok=True) se il giocatore ha almeno una cartella. [file:2]
        - EsitoAzione(ok=False, errore="CARTELLE_NESSUNA_ASSEGNATA") se non ha cartelle. [file:2]
        """

        # Se la lista è vuota, il giocatore non può eseguire azioni di gioco.
        if not self.cartelle:
            return EsitoAzione(
                ok=False,
                errore="CARTELLE_NESSUNA_ASSEGNATA",
                evento=None,
            )

        # Se esistono cartelle, il controllo è superato.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 2.
    def _esito_focus_cartella_impostato(self, auto_imposta: bool = True) -> EsitoAzione:
        """
        Controlla che esista una cartella selezionata (focus cartella impostato).

        A cosa serve (in parole semplici):
        - Molti comandi hanno bisogno di sapere "su quale cartella sto lavorando".
        - Se il giocatore ha cartelle ma non ne ha ancora selezionata una, questo helper
        può (se consentito) selezionare automaticamente la prima, per rendere la
        navigazione più fluida.

        Parametri:
        - auto_imposta (default True):
        - True: se il focus è assente, seleziona automaticamente la prima cartella (indice 0)
            e allega un EventoFocusAutoImpostato.
        - False: se il focus è assente, non seleziona nulla e ritorna un errore.

        Ritorna:
        - EsitoAzione(ok=False, errore="CARTELLE_NESSUNA_ASSEGNATA") se non ci sono cartelle.
        - EsitoAzione(ok=False, errore="FOCUS_CARTELLA_NON_IMPOSTATO") se il focus è None e auto_imposta=False.
        - EsitoAzione(ok=True, evento=EventoFocusAutoImpostato(...)) se auto-imposta il focus.
        - EsitoAzione(ok=True) se il focus era già impostato.

        Nota:
        - Questo helper NON controlla che l'indice sia dentro range (quello è compito
        dell'helper “focus cartella valido/in range” che faremo dopo).
        """

        # 1) Prima verifica che il giocatore abbia cartelle.
        esito_cartelle = self._esito_ha_cartelle()
        if not esito_cartelle.ok:
            # Propaghiamo lo stesso errore, senza modificarlo.
            return esito_cartelle

        # 2) Poi verifica che la cartella in focus sia stata selezionata.
        if self._indice_cartella_focus is None:
            if auto_imposta:
                # Scelta automatica: prima cartella disponibile.
                self._indice_cartella_focus = 0

                # Evento opzionale: la UI può decidere se annunciare questa auto-scelta.
                return EsitoAzione(
                    ok=True,
                    errore=None,
                    evento=EventoFocusAutoImpostato(
                        tipo_focus="cartella",
                        indice=0,
                    ),
                )

            # Caso "rigoroso": l'utente deve selezionare esplicitamente una cartella.
            return EsitoAzione(
                ok=False,
                errore="FOCUS_CARTELLA_NON_IMPOSTATO",
                evento=None,
            )

        # 3) Tutto ok: focus già presente, non facciamo nulla e non generiamo eventi.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 3.
    def _esito_focus_cartella_in_range(self) -> EsitoAzione:
        """
        Verifica che il focus cartella sia impostato e che l'indice sia dentro range.

        Scopo:
        - Evitare accessi non sicuri del tipo: self.cartelle[self._indice_cartella_focus]
          quando il focus è assente (None) oppure quando punta fuori dai limiti della lista.

        Comportamento:
        - Se il giocatore non ha cartelle, propaga l'esito di `_esito_ha_cartelle()`.
        - Se il focus cartella non è impostato (None), ritorna un errore di prerequisiti mancanti.
        - Se il focus cartella è impostato ma fuori range, ritorna un errore di verifica fallita.
        - Se tutto è valido, ritorna ok=True.

        Ritorna:
        - EsitoAzione(ok=True) se il focus è utilizzabile.
        - EsitoAzione(ok=False, errore=...) se non è utilizzabile.

        Note:
        - Questo metodo NON auto-imposta il focus: qui si controlla soltanto la coerenza
          dello stato corrente (helper “rigoroso” e predicibile). [file:5]
        - I codici errore usati vengono da `CodiceErrore` in `eventi.py`. [file:2]
        """

        # 1) Controllo base: se non ci sono cartelle, non esiste nessun "range" sensato.
        #    Propaghiamo l'errore già standardizzato dall'helper dedicato.
        esito_cartelle = self._esito_ha_cartelle()
        if not esito_cartelle.ok:
            return esito_cartelle

        # 2) Focus non impostato: l'utente (o la UI) non ha ancora selezionato una cartella.
        if self._indice_cartella_focus is None:
            return EsitoAzione(
                ok=False,
                errore="FOCUS_CARTELLA_NON_IMPOSTATO",
                evento=None,
            )

        # 3) Focus impostato ma non coerente con la lista attuale delle cartelle.
        #    Questo evita IndexError e segnala uno stato non valido.
        if self._indice_cartella_focus < 0 or self._indice_cartella_focus >= len(self.cartelle):
            return EsitoAzione(
                ok=False,
                errore="FOCUS_CARTELLA_FUORI_RANGE",
                evento=None,
            )

        # 4) Tutto ok: il focus è presente e punta a una cartella esistente.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 4.
    def _esito_focus_cartella_valido(self, auto_imposta: bool = True) -> EsitoAzione:
        """
        Verifica che la cartella in focus sia valida rispetto alla lista attuale delle cartelle.

        Obiettivo:
        - Centralizzare la programmazione difensiva sul focus cartella.
        - Garantire che, se un metodo successivo farà:
            self.cartelle[self._indice_cartella_focus]
          l'operazione sia sicura (focus presente e indice dentro range).

        Parametri:
        - auto_imposta: bool (default True)
          Se True, permette al controllo "focus impostato" di impostare automaticamente
          la prima cartella (indice 0) quando il focus è None.

        Ritorna:
        - EsitoAzione(ok=False, errore=...) se:
          - Mancano prerequisiti (es. focus non impostato in modalità rigorosa), oppure
          - La verifica fallisce (indice fuori range).
        - EsitoAzione(ok=True, evento=...) se il focus è valido.
          L'evento è opzionale e viene propagato se prodotto dal controllo precedente.

        Note:
        - I codici errore sono `CodiceErrore` definiti in `eventi.py`. [file:2]
        """

        # 1) Controllo base: cartelle presenti + focus cartella impostato (anche auto-impostato se richiesto).
        esito_impostato = self._esito_focus_cartella_impostato(auto_imposta=auto_imposta)
        if not esito_impostato.ok:
            # Se non posso nemmeno determinare una cartella attiva, non ha senso fare altri controlli.
            return esito_impostato

        # 2) Controllo difensivo: l'indice deve essere dentro i limiti della lista self.cartelle.
        esito_in_range = self._esito_focus_cartella_in_range()
        if not esito_in_range.ok:
            # Se l'indice è fuori range, fermo tutto e ritorno l'errore standardizzato.
            return esito_in_range

        # 3) Tutto ok: focus valido.
        #    Se nel passaggio (1) è stato generato un evento (es. auto-impostazione),
        #    lo propaghiamo, così la UI può decidere se annunciarlo o ignorarlo.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=esito_impostato.evento,
        )


    #sezione 2: metodi riguardanti il focus di riga e le sue impostazioni

    #metodo 5.
    def _esito_focus_riga_impostato(self) -> EsitoAzione:
        """
        Verifica che la riga in focus sia stata impostata dall'utente (controllo rigoroso).

        Scopo:
        - Questo helper viene usato come pre-condizione per azioni che richiedono una scelta
          esplicita della riga (es. annunci ambo/terno/quaterna/cinquina).
        - A differenza degli helper “comodi” per la navigazione, qui NON si auto-imposta
          nessuna riga: se manca, l'azione deve fermarsi.

        Cosa controlla davvero:
        1) Esista una cartella valida in focus (controllo rigoroso: auto_imposta=False).
        2) L'indice della riga in focus sia impostato (cioè non sia None).

        Cosa NON controlla:
        - Non verifica che l'indice della riga sia dentro range rispetto alla cartella corrente.
          Se serve una garanzia di “riga utilizzabile”, usare un controllo dedicato (es. helper
          “focus riga valido/in range”) oppure i prerequisiti specifici del comando.

        Ritorna:
        - EsitoAzione(ok=False, errore=...) se non si può procedere (cartella non valida o riga non impostata).
        - EsitoAzione(ok=True) se cartella valida e riga impostata.
        """

        # 1) Controllo base: devo avere una cartella valida in focus,
        #    ma qui NON voglio auto-selezionare una cartella (controllo rigoroso).
        esito_cartella = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_cartella.ok:
            # Propago l'errore così com'è (prerequisiti mancanti o verifica fallita).
            return esito_cartella

        # 2) Controllo rigoroso: la riga deve essere selezionata esplicitamente dall'utente.
        if self._indice_riga_focus is None:
            return EsitoAzione(
                ok=False,
                errore="FOCUS_RIGA_NON_IMPOSTATA",
                evento=None,
            )

        # 3) Tutto ok: cartella valida e riga impostata.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 6.
    def _esito_focus_riga_in_range(self) -> EsitoAzione:
        """
        Verifica che il focus riga sia coerente (in range) rispetto alla cartella attualmente in focus.

        Obiettivo:
        - Evitare accessi non sicuri o stati incoerenti quando un comando vuole usare la riga
          selezionata (es. leggere/segnare/validare una riga).
        - Questo helper NON auto-imposta nulla: controlla solo la coerenza dello stato corrente.

        Pre-condizione (garantita internamente):
        - Esista una cartella valida in focus (controllo rigoroso: auto_imposta=False),
          perché il range della riga dipende dalla cartella corrente.

        Cosa controlla:
        1) Cartella valida in focus (necessaria per conoscere quante righe esistono).
        2) Riga impostata (non None).
        3) Riga dentro range [0, cartella.righe).

        Ritorna:
        - EsitoAzione(ok=True) se la riga è dentro range.
        - EsitoAzione(ok=False, errore="FOCUS_RIGA_NON_IMPOSTATA") se manca il focus riga.
        - EsitoAzione(ok=False, errore="FOCUS_RIGA_FUORI_RANGE") se l'indice è incoerente.
        - Propaga eventuali errori di cartella (es. nessuna cartella, focus cartella non impostato, fuori range).
        """

        # 1) Prima di parlare di "range riga", devo avere una cartella valida in focus.
        esito_cartella = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_cartella.ok:
            return esito_cartella

        # 2) Se la riga non è impostata, non esiste un range verificabile.
        if self._indice_riga_focus is None:
            return EsitoAzione(
                ok=False,
                errore="FOCUS_RIGA_NON_IMPOSTATA",
                evento=None,
            )

        # 3) Controllo range vero e proprio, usando la cartella in focus.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]
        if self._indice_riga_focus < 0 or self._indice_riga_focus >= cartella_in_focus.righe:
            return EsitoAzione(
                ok=False,
                errore="FOCUS_RIGA_FUORI_RANGE",
                evento=None,
            )

        # 4) Tutto ok: riga coerente con la cartella in focus.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 7.
    def _esito_focus_riga_valido(self) -> EsitoAzione:
        """
        Verifica completa del focus riga: riga impostata + riga in range rispetto alla cartella in focus.

        Obiettivo:
        - Centralizzare un controllo "pronto all'uso" quando un comando vuole usare davvero la riga,
          cioè fare accessi sicuri basati su `_indice_riga_focus`.

        Caratteristiche:
        - Controllo rigoroso e predicibile: NON auto-imposta la riga.
        - Propaga gli errori con codici focus (coerenti con gli altri helper).

        Strategia:
        1) Verifica che la riga sia impostata (delegando a `_esito_focus_riga_impostato()`).
        2) Verifica che la riga sia in range (delegando a `_esito_focus_riga_in_range()`).

        Ritorna:
        - EsitoAzione(ok=True) se il focus riga è utilizzabile.
        - EsitoAzione(ok=False, errore=...) se non è utilizzabile.
        """

        # 1) Prima: riga deve essere selezionata dall'utente (nessuna auto-impostazione).
        esito_impostata = self._esito_focus_riga_impostata()
        if not esito_impostata.ok:
            return esito_impostata

        # 2) Poi: la riga deve essere coerente con la cartella attualmente in focus.
        esito_in_range = self._esito_focus_riga_in_range()
        if not esito_in_range.ok:
            return esito_in_range

        # 3) Tutto ok: focus riga valido.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #sezione 3: metodi riguardanti il focus della colonna e le sue impostazioni

    #metodo 8.
    def _esito_focus_colonna_impostata(self) -> EsitoAzione:
        """
        Verifica che la colonna in focus sia stata impostata dall'utente (controllo rigoroso).

        Scopo:
        - Helper usato come pre-condizione per comandi che richiedono una scelta esplicita
          della colonna (selezione/click logico, letture puntuali, azioni “importanti” legate
          alla colonna).
        - A differenza degli helper “comodi” per la navigazione, qui NON si auto-imposta
          nessuna colonna: se manca, l'azione deve fermarsi.

        Cosa controlla:
        1) Esista una cartella valida in focus (controllo rigoroso: auto_imposta=False).
        2) L'indice della colonna in focus sia impostato (cioè non sia None).

        Cosa NON controlla:
        - Non verifica che l'indice colonna sia dentro range rispetto alla cartella corrente.
          Se serve una garanzia di “colonna utilizzabile”, usare `_esito_focus_colonna_valido()`.

        Ritorna:
        - EsitoAzione(ok=False, errore=...) se non si può procedere (cartella non valida o colonna non impostata).
        - EsitoAzione(ok=True) se cartella valida e colonna impostata.
        """

        # 1) Prima di parlare di colonna, devo avere una cartella valida in focus.
        #    Qui non vogliamo auto-selezionare una cartella (controllo rigoroso).
        esito_cartella = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_cartella.ok:
            return esito_cartella

        # 2) La colonna deve essere stata selezionata esplicitamente dall'utente.
        if self._indice_colonna_focus is None:
            return EsitoAzione(
                ok=False,
                errore="FOCUS_COLONNA_NON_IMPOSTATA",
                evento=None,
            )

        # 3) Tutto ok: cartella valida e colonna impostata.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 9.
    def _esito_focus_colonna_in_range(self) -> EsitoAzione:
        """
        Verifica che il focus colonna sia coerente (in range) rispetto alla cartella in focus.

        Obiettivo:
        - Evitare accessi non sicuri o stati incoerenti quando un comando vuole usare la colonna
          selezionata (es. leggere un numero in una posizione, spostamenti controllati, ecc.).
        - Questo helper NON auto-imposta nulla: controlla solo la coerenza dello stato corrente.

        Pre-condizione (garantita internamente):
        - Esista una cartella valida in focus (auto_imposta=False), perché il range delle colonne
          dipende dalla cartella corrente.

        Cosa controlla:
        1) Cartella valida in focus (necessaria per conoscere quante colonne esistono).
        2) Colonna impostata (non None).
        3) Colonna dentro range [0, cartella.colonne).

        Ritorna:
        - EsitoAzione(ok=True) se la colonna è dentro range.
        - EsitoAzione(ok=False, errore="FOCUS_COLONNA_NON_IMPOSTATA") se manca il focus colonna.
        - EsitoAzione(ok=False, errore="FOCUS_COLONNA_FUORI_RANGE") se l'indice è incoerente.
        - Propaga eventuali errori di cartella (nessuna cartella, focus cartella non impostato, fuori range).
        """

        # 1) Prima di parlare di "range colonna", devo avere una cartella valida in focus.
        esito_cartella = self._esito_focus_cartella_valido(auto_imposta=False)
        if not esito_cartella.ok:
            return esito_cartella

        # 2) Se la colonna non è impostata, non esiste un range verificabile.
        if self._indice_colonna_focus is None:
            return EsitoAzione(
                ok=False,
                errore="FOCUS_COLONNA_NON_IMPOSTATA",
                evento=None,
            )

        # 3) Controllo range vero e proprio, usando la cartella in focus.
        cartella_in_focus = self.cartelle[self._indice_cartella_focus]

        # Nota: cartella_in_focus.colonne è il numero di colonne (di default 9).
        if self._indice_colonna_focus < 0 or self._indice_colonna_focus >= cartella_in_focus.colonne:
            return EsitoAzione(
                ok=False,
                errore="FOCUS_COLONNA_FUORI_RANGE",
                evento=None,
            )

        # 4) Tutto ok: colonna coerente con la cartella in focus.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 10.
    def _esito_focus_colonna_valido(self) -> EsitoAzione:
        """
        Verifica completa del focus colonna: colonna impostata + colonna in range rispetto alla cartella in focus.

        Obiettivo:
        - Centralizzare un controllo "pronto all'uso" quando un comando vuole usare davvero la colonna,
          cioè fare accessi sicuri basati su `_indice_colonna_focus`.

        Caratteristiche:
        - Controllo rigoroso e predicibile: NON auto-imposta la colonna.
        - Propaga gli errori con codici focus (coerenti con gli altri helper).

        Strategia:
        1) Verifica che la colonna sia impostata (delegando a `_esito_focus_colonna_impostata()`).
        2) Verifica che la colonna sia in range (delegando a `_esito_focus_colonna_in_range()`).

        Ritorna:
        - EsitoAzione(ok=True) se il focus colonna è utilizzabile.
        - EsitoAzione(ok=False, errore=...) se non è utilizzabile.
        """

        # 1) Prima: colonna deve essere selezionata dall'utente (nessuna auto-impostazione).
        esito_impostata = self._esito_focus_colonna_impostata()
        if not esito_impostata.ok:
            return esito_impostata

        # 2) Poi: la colonna deve essere coerente con la cartella attualmente in focus.
        esito_in_range = self._esito_focus_colonna_in_range()
        if not esito_in_range.ok:
            return esito_in_range

        # 3) Tutto ok: focus colonna valido.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #sezione 4: metodi di verifica sui focus impostati

    #metodo 11.
    def _esito_pronto_per_navigazione(self) -> EsitoAzione:
        """
        Verifica che il giocatore sia in condizione di usare i comandi di navigazione (frecce).

        Questo helper è pensato per essere chiamato all'inizio di tutti i metodi freccia
        (su/giù/sinistra/destra, semplici e avanzati), così da centralizzare una pre-condizione
        comune: esistere una cartella valida su cui navigare. [file:1]

        Comportamento:
        - Delega al controllo del focus cartella valido, con auto-impostazione abilitata:
          se il giocatore ha cartelle ma non ha ancora un focus, il focus può essere impostato
          automaticamente sulla prima cartella, rendendo la navigazione immediatamente possibile. [file:1]
        - Se il focus cartella non è determinabile o non è valido, ritorna un EsitoAzione con ok=False
          e un CodiceErrore coerente (propagato dall'helper chiamato). [file:2]

        Ritorna:
            EsitoAzione:
                - ok=True se la navigazione può proseguire.
                - ok=False se mancano prerequisiti o la verifica fallisce (errore valorizzato). [file:2]
        """

        # Delego ai controlli già centralizzati sul focus cartella (presenza + range),
        # chiedendo esplicitamente l'auto-impostazione del focus quando possibile.
        esito_cartella = self._esito_focus_cartella_valido(auto_imposta=True)
        if not esito_cartella.ok:
            # Se non posso individuare una cartella attiva valida, non ha senso proseguire.
            # Propago l'esito così com'è, mantenendo codice errore e (se presente) evento.
            return esito_cartella

        # Se sono qui, la cartella in focus esiste ed è valida: via libera alla navigazione.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=esito_cartella.evento
        )


    #metodo 12.
    def _esito_inizializza_focus_riga_se_manca(self) -> EsitoAzione:
        """
        Inizializza il focus della riga se non è ancora stato impostato (helper non rigoroso).

        Scopo:
        - Questo helper è pensato per i metodi freccia (navigazione): se la riga in focus è None
          (es. inizio partita, cambio cartella, focus resettato), imposta un valore di partenza
          e permette alla navigazione di procedere senza messaggi o blocchi.

        Scelta del default:
        - Riga 0 = riga più in alto (internamente 0-based).

        Ritorna:
        - EsitoAzione(ok=False, errore=...) se non è possibile navigare (cartella non valida o
          prerequisiti mancanti), propagando l'esito del controllo di navigazione.
        - EsitoAzione(ok=True) se tutto ok.
          - Se la riga era già impostata: evento=None.
          - Se la riga viene inizializzata qui (auto-impostazione): evento=EventoFocusAutoImpostato(tipo_focus="riga", indice=0).

        Note:
        - Questo helper modifica lo stato interno solo se necessario (assegnando la riga 0).
        - Non produce messaggi utente: eventuali testi verranno gestiti da uno strato UI.
        """

        # 1) Prima verifica che si possa navigare (cartella esiste + focus cartella valido).
        esito_navigazione = self._esito_pronto_per_navigazione()
        if not esito_navigazione.ok:
            # Se non posso navigare, non ha senso impostare un focus riga.
            # Propago l'errore così com'è (codice errore e/o evento già valorizzati).
            return esito_navigazione

        # 2) Se la riga non è ancora selezionata, la inizializzo a un valore di partenza.
        if self._indice_riga_focus is None:
            self._indice_riga_focus = 0

            # Evento opzionale: la UI può decidere se annunciare questa auto-scelta.
            return EsitoAzione(
                ok=True,
                errore=None,
                evento=EventoFocusAutoImpostato(
                    tipo_focus="riga",
                    indice=0,
                ),
            )

        # 3) Tutto ok: via libera (riga già impostata, nessun evento).
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #metodo 13.
    def _esito_inizializza_focus_colonna_se_manca(self) -> EsitoAzione:
        """
        Inizializza il focus della colonna se non è ancora stato impostato (helper non rigoroso).

        Scopo:
        - Helper pensato per i metodi freccia (navigazione): se la colonna in focus è None
          (es. inizio partita, cambio cartella, focus resettato), imposta un valore di partenza
          e permette alla navigazione di procedere senza messaggi o blocchi.

        Scelta del default:
        - Colonna 0 = prima colonna (internamente 0-based), coerente con la riga 0 come
          "prima riga".

        Ritorna:
        - EsitoAzione(ok=False, errore=...) se non è possibile navigare (prerequisiti mancanti
          o verifica fallita), propagando l'esito del controllo di navigazione.
        - EsitoAzione(ok=True) se tutto ok.
          - Se la colonna era già impostata: evento=None.
          - Se la colonna viene inizializzata qui (auto-impostazione): evento=EventoFocusAutoImpostato(tipo_focus="colonna", indice=0).

        Note:
        - Questo helper modifica lo stato interno solo se necessario (assegnando la colonna 0).
        - Non produce testo utente: l’eventuale rendering è demandato al layer UI.
        """

        # 1) Verifica che la navigazione sia possibile (cartella esiste + focus cartella valido).
        esito_navigazione = self._esito_pronto_per_navigazione()
        if not esito_navigazione.ok:
            # Se non posso navigare, non ha senso impostare un focus colonna.
            # Propago l'errore così com'è (codice errore e/o evento già valorizzati).
            return esito_navigazione

        # 2) Se la colonna non è ancora selezionata, la inizializzo a un valore di partenza.
        if self._indice_colonna_focus is None:
            self._indice_colonna_focus = 0

            # Evento opzionale: la UI può decidere se annunciare questa auto-scelta.
            return EsitoAzione(
                ok=True,
                errore=None,
                evento=EventoFocusAutoImpostato(
                    tipo_focus="colonna",
                    indice=0,
                ),
            )

        # 3) Tutto ok: colonna già impostata, nessun evento.
        return EsitoAzione(
            ok=True,
            errore=None,
            evento=None,
        )


    #sezione 5: metodi di reset dei focus.

    #metodo 14.
    def _reset_focus_riga_e_colonna(self) -> None:
        """
        Reimposta (svuota) i focus di riga e colonna, mantenendo invariato il focus cartella.

        Questo helper va usato quando la cartella in focus è già stata scelta (o sta per esserlo)
        e si vuole evitare di “trascinare” la riga o la colonna selezionate dalla cartella precedente
        (es. dopo un cambio cartella in `imposta_focus_cartella`).

        Nota:
        - Questo metodo NON modifica `_indice_cartella_focus`.
        - Per un reset completo (cartella + riga + colonna), usare l’helper dedicato.

        Effetto:
        - `_indice_riga_focus` viene impostato a None.
        - `_indice_colonna_focus` viene impostato a None.

        Ritorna:
        - None
        """

        # Focus riga: non selezionata finché l'utente non naviga (o finché non viene inizializzata).
        self._indice_riga_focus = None

        # Focus colonna: non selezionata finché l'utente non naviga (o finché non viene inizializzata).
        self._indice_colonna_focus = None


    #metodo 15.
    def _reset_focus_cartella_riga_e_colonna(self) -> None:
        """
        Reimposta (svuota) i focus di cartella, riga e colonna.

        Questo helper va usato quando vuoi azzerare completamente lo stato di selezione,
        tipicamente perché la lista delle cartelle può cambiare (es. rimozione/sostituzione/nuova assegnazione)
        oppure quando si avvia una nuova partita o si fa un reset “globale”.

        Nota:
        - Questo metodo imposta `_indice_cartella_focus` a None, quindi dopo il reset i comandi che richiedono
        una cartella selezionata dovranno far scegliere la cartella all’utente (oppure usare l’auto-impostazione
        prevista dagli altri controlli, se abilitata).
        - Non è pensato per il semplice cambio cartella durante la navigazione: in quel caso usare il reset
        di sola riga/colonna.

        Effetto:
        - `_indice_cartella_focus` viene impostato a None.
        - `_indice_riga_focus` viene impostato a None.
        - `_indice_colonna_focus` viene impostato a None.

        Ritorna:
        - None
        """

        #indice_cartella_focus resettato a none ad ogni reset, per evitare conflitti con cartelle eliminate
        self._indice_cartella_focus = None

        # Focus riga: non selezionata finché l'utente non naviga (o finché non viene inizializzata).
        self._indice_riga_focus = None

        # Focus colonna: non selezionata finché l'utente non naviga (o finché non viene inizializzata).
        self._indice_colonna_focus = None

