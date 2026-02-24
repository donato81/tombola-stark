"""
Costanti tasti rapidi per la TUI Tombola Stark — v0.10.0

Tutti i tasti sono catturati con msvcrt.getwch() senza attendere Invio.
I tasti speciali (frecce, PagSu, PagGiù) producono due byte su Windows:
  - primo byte: prefisso \xe0 (tasto esteso)
  - secondo byte: codice specifico del tasto

I tasti lettera producono un solo byte (carattere minuscolo).

Riferimento mappatura: documentations/mappatura_tasti_terminale.md
"""

# ---------------------------------------------------------------------------
# Gruppo 1 — Navigazione riga semplice
# Metodi: sposta_focus_riga_su_semplice, sposta_focus_riga_giu_semplice
# ---------------------------------------------------------------------------

FRECCIA_SU: str = "\xe0H"
"""Freccia Su: sale alla riga precedente (lettura grezza)."""

FRECCIA_GIU: str = "\xe0P"
"""Freccia Giù: scende alla riga successiva (lettura grezza)."""

# ---------------------------------------------------------------------------
# Gruppo 2 — Navigazione riga avanzata
# Metodi: sposta_focus_riga_su_avanzata, sposta_focus_riga_giu_avanzata
# ---------------------------------------------------------------------------

TASTO_A: str = "a"
"""Tasto A: sale alla riga precedente con analisi completa (segnati + mancanti)."""

TASTO_Z: str = "z"
"""Tasto Z: scende alla riga successiva con analisi completa (segnati + mancanti)."""

# ---------------------------------------------------------------------------
# Gruppo 3 — Navigazione colonna semplice
# Metodi: sposta_focus_colonna_sinistra, sposta_focus_colonna_destra
# ---------------------------------------------------------------------------

FRECCIA_SINISTRA: str = "\xe0K"
"""Freccia Sinistra: sposta il cursore alla colonna precedente (lettura cella)."""

FRECCIA_DESTRA: str = "\xe0M"
"""Freccia Destra: sposta il cursore alla colonna successiva (lettura cella)."""

# ---------------------------------------------------------------------------
# Gruppo 4 — Navigazione colonna avanzata
# Metodi: sposta_focus_colonna_sinistra_avanzata, sposta_focus_colonna_destra_avanzata
# ---------------------------------------------------------------------------

TASTO_Q: str = "q"
"""Tasto Q: colonna precedente con analisi verticale completa."""

TASTO_W: str = "w"
"""Tasto W: colonna successiva con analisi verticale completa."""

# ---------------------------------------------------------------------------
# Gruppo 5 — Salto diretto a riga o colonna specifica (richiede prompt)
# Metodi: vai_a_riga_avanzata, vai_a_colonna_avanzata
# ---------------------------------------------------------------------------

TASTO_R: str = "r"
"""Tasto R: salta direttamente alla riga indicata (prompt 1-3)."""

TASTO_C: str = "c"
"""Tasto C: salta direttamente alla colonna indicata (prompt 1-9)."""

# ---------------------------------------------------------------------------
# Gruppo 6 — Gestione e navigazione cartelle
# Metodi: riepilogo_cartella_successiva, riepilogo_cartella_precedente,
#         imposta_focus_cartella + riepilogo_cartella_corrente
# ---------------------------------------------------------------------------

PAG_GIU: str = "\xe0Q"
"""PagGiù: avanza alla cartella successiva con riepilogo premi."""

PAG_SU: str = "\xe0I"
"""PagSu: torna alla cartella precedente con riepilogo premi."""

TASTO_1: str = "1"
"""Tasto 1: seleziona direttamente la cartella 1."""

TASTO_2: str = "2"
"""Tasto 2: seleziona direttamente la cartella 2."""

TASTO_3: str = "3"
"""Tasto 3: seleziona direttamente la cartella 3."""

TASTO_4: str = "4"
"""Tasto 4: seleziona direttamente la cartella 4."""

TASTO_5: str = "5"
"""Tasto 5: seleziona direttamente la cartella 5."""

TASTO_6: str = "6"
"""Tasto 6: seleziona direttamente la cartella 6."""

#: Insieme dei tasti numerici 1-6 per selezione rapida delle cartelle.
TASTI_CARTELLE: frozenset = frozenset({
    TASTO_1, TASTO_2, TASTO_3, TASTO_4, TASTO_5, TASTO_6
})

# ---------------------------------------------------------------------------
# Gruppo 7 — Visualizzazione cartella corrente e tutte le cartelle
# Metodi: visualizza_cartella_corrente_semplice, visualizza_cartella_corrente_avanzata,
#         visualizza_tutte_cartelle_semplice, visualizza_tutte_cartelle_avanzata
# ---------------------------------------------------------------------------

TASTO_D: str = "d"
"""Tasto D (Display): mostra numeri cartella in focus in forma grezza."""

TASTO_F: str = "f"
"""Tasto F (Full display): mostra cartella in focus con numeri segnati e riepiloghi."""

TASTO_G: str = "g"
"""Tasto G (Globale): mostra tutte le cartelle in forma semplice."""

TASTO_H: str = "h"
"""Tasto H: mostra tutte le cartelle con analisi avanzata."""

# ---------------------------------------------------------------------------
# Gruppo 8 — Consultazione del tabellone
# Metodi: comunica_ultimo_numero_estratto, visualizza_ultimi_numeri_estratti,
#         riepilogo_tabellone, lista_numeri_estratti,
#         verifica_numero_estratto (prompt), cerca_numero_nelle_cartelle (prompt)
# ---------------------------------------------------------------------------

TASTO_U: str = "u"
"""Tasto U (Ultimo): legge l'ultimo numero estratto."""

TASTO_I: str = "i"
"""Tasto I (Indietro): legge gli ultimi 5 numeri estratti."""

TASTO_O: str = "o"
"""Tasto O (Overview): panoramica completa del tabellone."""

TASTO_L: str = "l"
"""Tasto L (Lista): lista completa di tutti i numeri estratti."""

TASTO_E: str = "e"
"""Tasto E (Estratto): verifica se un numero è stato estratto (richiede prompt)."""

TASTO_N: str = "n"
"""Tasto N (Numero): cerca un numero nelle cartelle del giocatore (richiede prompt)."""

# ---------------------------------------------------------------------------
# Gruppo 9 — Orientamento e stato corrente
# Metodo: stato_focus_corrente
# ---------------------------------------------------------------------------

TASTO_PUNTO_INTERROGATIVO: str = "?"
"""Tasto ?: indica cartella, riga e colonna del cursore corrente."""

# ---------------------------------------------------------------------------
# Gruppo 10 — Azioni di gioco
# Metodi: segna_numero_manuale (prompt), annuncia_vittoria (prompt),
#         passa_turno, [procedura uscita]
# ---------------------------------------------------------------------------

TASTO_S: str = "s"
"""Tasto S (Segna): segna un numero sulla cartella in focus (richiede prompt)."""

TASTO_V: str = "v"
"""Tasto V (Vittoria): dichiara una vincita (richiede prompt tipo vincita)."""

TASTO_P: str = "p"
"""Tasto P (Prosegui): passa al turno successivo e innesca nuova estrazione."""

TASTO_X: str = "x"
"""Tasto X (eXit): avvia procedura di uscita con conferma esplicita."""

# ---------------------------------------------------------------------------
# Prefisso byte tasti estesi (msvcrt)
# ---------------------------------------------------------------------------

PREFISSO_TASTO_ESTESO: str = "\xe0"
"""
Primo byte prodotto da msvcrt per i tasti estesi (frecce, PagSu/PagGiù).
Se getwch() restituisce questo valore, occorre leggere un secondo byte.
"""
