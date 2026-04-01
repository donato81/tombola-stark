"""
Modulo per la vocalizzazione di messaggi tramite Accessible Output 2 (AO2).

Espone:
- IVocalizzatore: contratto Protocol minimale per la vocalizzazione.
- NullVocalizzatore: implementazione muta headless-safe.
- Vocalizzatore: adattatore AO2 con backend iniettabile e best-effort.

path: my_lib/vocalizzatore.py
"""
from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable

try:
    from accessible_output2.outputs.auto import Auto as _Auto
    _AO2_DISPONIBILE = True
except ImportError:
    _Auto = None  # type: ignore[assignment]
    _AO2_DISPONIBILE = False

_error_logger = logging.getLogger("error")


class _SpeakBackend(Protocol):
    """Interfaccia minimale del backend TTS: unico metodo speak richiesto."""

    def speak(self, testo: str, interrupt: bool = False) -> None:
        ...


@runtime_checkable
class IVocalizzatore(Protocol):
    """Contratto Protocol per la vocalizzazione di testo."""

    def vocalizza_testo(self, testo: str, interrompi: bool = False) -> None:
        """Vocalizza il testo; se interrompi=True interrompe la lettura in corso."""
        ...


class NullVocalizzatore:
    """Implementazione muta di IVocalizzatore: no-op silenziosa per test e ambienti headless."""

    def vocalizza_testo(self, testo: str, interrompi: bool = False) -> None:
        """No-op silenziosa: non produce alcun output vocale."""


class Vocalizzatore:
    """
    Adattatore AO2 per la vocalizzazione di testo.

    Accetta un backend iniettabile (utile nei test); se omesso usa Auto() di AO2.
    Gli errori del backend non si propagano: best-effort senza bloccare il gioco.
    """

    def __init__(self, backend: _SpeakBackend | None = None) -> None:
        """
        Inizializza il vocalizzatore.

        Args:
            backend: backend TTS iniettabile. Se None, viene usato Auto() di AO2.

        Raises:
            ImportError: se backend è None e accessible_output2 non è installato.
        """
        if backend is not None:
            self._backend: _SpeakBackend = backend
        elif _AO2_DISPONIBILE and _Auto is not None:
            self._backend = _Auto()
        else:
            raise ImportError(
                "accessible_output2 non è disponibile. "
                "Installa la dipendenza o inietta un backend esplicito."
            )

    def vocalizza_testo(self, testo: str, interrompi: bool = False) -> None:
        """
        Vocalizza il testo tramite il backend TTS.

        Args:
            testo: il testo da vocalizzare.
            interrompi: se True, interrompe la lettura in corso prima di parlare.

        Note:
            Non propaga eccezioni: un errore del backend viene silenziosamente ignorato.
        """
        try:
            self._backend.speak(testo, interrupt=interrompi)
        except Exception:
            _error_logger.exception("Errore backend TTS in vocalizza_testo")

