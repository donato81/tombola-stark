"""
setup.py — Configurazione build eseguibile Windows per Tombola Stark.

Utilizza cx_Freeze per impacchettare main.py e tutte le dipendenze
in una cartella autonoma eseguibile senza installazione Python.

Uso:
    python setup.py build_exe
"""

import sys
from pathlib import Path
from cx_Freeze import setup, Executable

# ------------------------------------------------------------
# Cartella di output
# ------------------------------------------------------------
OUTPUT_DIR = "build/tombola-stark-0.14.0"

# ------------------------------------------------------------
# Pacchetti da includere esplicitamente nel build
# (cx_Freeze rileva le dipendenze in automatico, ma alcuni
# pacchetti nativi devono essere listati per sicurezza)
# ------------------------------------------------------------
packages = [
    "bingo_game",
    "my_lib",
    "accessible_output2",
    "wx",
    "pygame",
    "gtts",
    "playsound",
    "win32api",
    "win32con",
    "win32gui",
    "win32com",
    "pyttsx3",
    "requests",
    "certifi",
    "charset_normalizer",
]

# ------------------------------------------------------------
# Moduli da escludere per ridurre le dimensioni del build
# ------------------------------------------------------------
excludes = [
    "tkinter",
    "_tkinter",
    "test",
    "unittest",
    "distutils",
    "doctest",
    "pdb",
    "profile",
    "pstats",
    "difflib",
    "ftplib",
    "imaplib",
    "mailbox",
    "nntplib",
    "optparse",
    "poplib",
    "smtplib",
    "telnetlib",
    "xmlrpc",
    "curses",
]

# ------------------------------------------------------------
# File aggiuntivi da copiare accanto all'eseguibile
# (cartella logs vuota, così il gioco può scrivere i log)
# ------------------------------------------------------------
include_files = []

# Crea la cartella logs se non esiste, per includerla nel build
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
(logs_dir / ".gitkeep").touch(exist_ok=True)
include_files.append(("logs", "logs"))

# Copia accessible_output2 con le DLL per NVDA/JAWS/SAPI
ao2_path = Path(sys.prefix) / "Lib" / "site-packages" / "accessible_output2"
if not ao2_path.exists():
    # Prova nel virtualenv
    import sysconfig
    ao2_path = Path(sysconfig.get_path("purelib")) / "accessible_output2"

if ao2_path.exists():
    include_files.append((str(ao2_path), "lib/accessible_output2"))

# Copia libloader (dipendenza runtime di accessible_output2)
libloader_path = ao2_path.parent / "libloader"
if libloader_path.exists():
    include_files.append((str(libloader_path), "lib/libloader"))

# ------------------------------------------------------------
# Opzioni build
# ------------------------------------------------------------
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "build_exe": OUTPUT_DIR,
    "silent": False,
    "zip_exclude_packages": [
        "accessible_output2",
        "libloader",
        "platform_utils",
    ],
}

# ------------------------------------------------------------
# Eseguibile
# Win32GUI nasconde la finestra console di Windows (corretto
# per un'app grafica wxPython).
# Per debug, sostituisci "Win32GUI" con "console".
# ------------------------------------------------------------
base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable(
        script="main.py",
        base=base,
        target_name="tombola-stark.exe",
        copyright="2026 Tombola Stark — Gioco accessibile per NVDA",
    )
]

# ------------------------------------------------------------
# Setup
# ------------------------------------------------------------
setup(
    name="Tombola Stark",
    version="0.14.0",
    description="Tombola digitale accessibile per screen reader NVDA",
    author="donato81",
    options={"build_exe": build_exe_options},
    executables=executables,
)
