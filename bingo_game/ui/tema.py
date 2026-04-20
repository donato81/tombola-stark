"""
tema.py — Vocabolario visivo condiviso per Tombola Stark.

Questo modulo definisce tutte le costanti di colore, font e dimensioni
usate dai componenti grafici dell'interfaccia. Non importa nulla.
Tutti i valori stringa esadecimali sono compatibili con wx.Colour(hex).
"""

# ---------------------------------------------------------------------------
# COLORI — Sfondi principali
# ---------------------------------------------------------------------------

COLORE_HEADER_BG = "#2C3E50"          # Sfondo della barra header di gioco
COLORE_MENU_BG = "#1A237E"            # Sfondo primario della finestra menu
COLORE_LOG_BG = "#263238"             # Sfondo del pannello log partita
COLORE_CONFIGURAZIONE_BG = "#FAFAFA"  # Sfondo finestra configurazione

# ---------------------------------------------------------------------------
# COLORI — Testi
# ---------------------------------------------------------------------------

COLORE_TESTO_CHIARO = "#ECEFF1"    # Testo chiaro su sfondi scuri (header, log)
COLORE_TESTO_SCURO = "#212121"     # Testo scuro su sfondi chiari
COLORE_TESTO_MUTED = "#B0BEC5"     # Testo attenuato / secondario
COLORE_TESTO_LABEL = "#333333"     # Testo etichette nel pannello configurazione
COLORE_TESTO_ERRORE = "#C62828"    # Testo messaggi di errore

# ---------------------------------------------------------------------------
# COLORI — Accenti
# ---------------------------------------------------------------------------

COLORE_ACCENT_ROSSO = "#E53935"       # Accento rosso vivo (azioni critiche)
COLORE_ACCENT_BLU = "#1565C0"         # Accento blu istituzionale
COLORE_TITOLO_MENU = "#FFD54F"        # Colore titolo sulla schermata menu
COLORE_HEADER_ACCENT = "#FFB300"      # Numero estratto nell'header

# ---------------------------------------------------------------------------
# COLORI — Pulsanti
# ---------------------------------------------------------------------------

COLORE_BTN_PAUSA = "#424242"         # Sfondo pulsante pausa
COLORE_BTN_NEUTRO = "#E0E0E0"        # Sfondo pulsante neutro / inattivo
COLORE_BTN_DISABILITATO = "#BDBDBD"  # Sfondo pulsante disabilitato
COLORE_BTN_GRIGIO = "#757575"        # Sfondo pulsanti secondari grigi
COLORE_BTN_INIZIA = "#2E7D32"         # "Inizia partita" (verde scuro)
COLORE_BTN_PASSA_TURNO = "#1565C0"    # "Passa turno" (blu istituzionale)
COLORE_BTN_HO_FINITO = "#E65100"      # "Ho finito — avvia verifica" (arancione)
COLORE_BTN_LAMPEGGIO_A = "#FFD54F"    # Lampeggio alt pulsante "Ho finito" (giallo-oro)
COLORE_BTN_RIPRENDI = "#388E3C"       # "Riprendi" (verde medio)

# ---------------------------------------------------------------------------
# COLORI — Celle tabellone (griglia 10×9, numeri 1-90)
# ---------------------------------------------------------------------------

COLORE_CELLA_VUOTA = "#F5F5F5"              # Cella del tabellone non ancora estratta
COLORE_CELLA_TESTO_INATTIVO = "#9E9E9E"    # Testo numero non estratto
COLORE_CELLA_ESTRATTO = "#E53935"          # Cella con numero estratto
COLORE_CELLA_ESTRATTO_IN_CARTELLA = "#FFB300"  # Numero estratto presente in cartella

# ---------------------------------------------------------------------------
# COLORI — Celle cartella (griglia 3×9, 15 numeri per cartella)
# ---------------------------------------------------------------------------

COLORE_CELLA_CARTELLA_VUOTA = "#E0E0E0"     # Cella vuota della cartella
COLORE_CELLA_CARTELLA_NUMERO = "#FFFFFF"    # Sfondo cella con numero
COLORE_CELLA_SEGNATA = "#43A047"            # Cella il cui numero è stato estratto
COLORE_CELLA_EVIDENZIATA = "#FFF176"        # Cella con focus tastiera
COLORE_CELLA_ESTRATTA_NON_SEGNATA = "#FFF9C4"  # Numero estratto ma non ancora segnato
COLORE_BORDO_FOCUS = "#1565C0"             # Bordo cella attiva con focus

# ---------------------------------------------------------------------------
# COLORI — Pulsanti premi
# ---------------------------------------------------------------------------

COLORE_BTN_TOMBOLA = "#FFB300"       # Sfondo pulsante Tombola (premio massimo)
COLORE_BTN_TOMBOLA_TESTO = "#212121" # Testo sul pulsante Tombola

# ---------------------------------------------------------------------------
# FONT — Dimensioni in punti tipografici
# ---------------------------------------------------------------------------

FONT_HEADER_PT = 12           # Dimensione testo nell'header di gioco
FONT_TITOLO_MENU_PT = 20      # Dimensione titolo nella schermata menu
FONT_LABEL_PT = 11            # Dimensione etichette generali
FONT_BTN_PT = 12              # Dimensione testo pulsanti principali
FONT_BTN_PICCOLO_PT = 11      # Dimensione testo pulsanti secondari / frecce
FONT_CARTELLA_NUMERO_PT = 14  # Dimensione numeri nelle celle cartella
FONT_TITOLO_CARTELLA_PT = 13  # Dimensione titolo sopra la cartella
FONT_OVERLAY_LABEL_PT = 16    # Dimensione etichetta secondaria overlay numero estratto
FONT_OVERLAY_PT = 72          # Dimensione numero nell'overlay visivo estrazione
FONT_LOG_PT = 10              # Dimensione testo nel pannello log

FONT_LOG_FAMIGLIA = "Courier New"  # Famiglia monospaziata per il pannello log

# ---------------------------------------------------------------------------
# DIMENSIONI — Pannelli e componenti (in pixel)
# ---------------------------------------------------------------------------

LARGHEZZA_PANNELLO_TABELLONE = 240     # Larghezza del pannello tabellone laterale
ALTEZZA_LOG = 120                      # Altezza area log in basso
ALTEZZA_HEADER = 36                    # Altezza della barra header di stato

DIMENSIONE_BTN_FRECCIA = (40, 40)               # Dimensione pulsanti [<] [>] navigazione cartelle
DIMENSIONE_BTN_SELEZIONE_CARTELLA = (36, 36)    # Dimensione pulsanti [1]..[6] selezione diretta
SPAZIATURA_BTN = 10                             # Spaziatura standard tra pulsanti
SPAZIATURA_BTN_PICCOLA = 8                      # Spaziatura ridotta tra pulsanti piccoli

DIMENSIONE_CELLA_TABELLONE = (24, 26)   # Dimensione minima cella griglia tabellone (w, h) in pixel
DIMENSIONE_CELLA_CARTELLA = (60, 34)    # Dimensione minima cella griglia cartella (w, h) in pixel
DIMENSIONE_OVERLAY = (260, 180)         # Dimensione dell'overlay visivo numero estratto

DIMENSIONE_FINESTRA_GIOCO = (1000, 700)          # Dimensione finestra principale di gioco
DIMENSIONE_FINESTRA_PRINCIPALE = (400, 380)      # Dimensione finestra menu principale
DIMENSIONE_FINESTRA_CONFIGURAZIONE = (500, 460)  # Dimensione finestra configurazione partita
