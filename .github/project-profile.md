initialized: true
project_name: "tombola-stark"
version: "0.10.0"
primary_language: "Python"
secondary_languages: []
ui_framework: "wxPython"
test_runner: "pytest"
build_system: "cx_freeze"
architecture: "clean-architecture-simplified"
accessibility: true
platform: "Windows 10/11"
screen_reader: "NVDA, JAWS, Orca"
---

# Profilo Progetto

> Questo file è la source of truth del progetto.
> Compilato da Agent-Welcome durante il setup iniziale.
> Non modificare manualmente i valori del frontmatter YAML.

## Identità

- **Nome**: tombola-stark
- **Versione corrente**: 0.10.0
- **Descrizione**: Tombola accessibile agli screen reader per non vedenti.

## Stack Tecnico

- **Linguaggio primario**: Python
- **Linguaggi secondari**: nessuno
- **Framework UI**: wxPython
- **Test runner**: pytest
- **Build system**: cx_freeze
- **Piattaforma target**: Windows 10/11

## Architettura

- **Pattern**: Clean Architecture semplificata
- **Layer**: Dominio -> Controller/Application -> Interfaccia
- **Riferimento**: README.md, documentations/ARCHITECTURE.md

## Accessibilità

- **Richiesta**: obbligatoria
- **Screen reader**: NVDA, JAWS, Orca
- **Standard**: output lineare, tastiera-first, messaggi brevi e semanticamente vocalizzabili
- **Riferimento**: README.md, CHANGELOG.md, bingo_game/ui/

## Componenti Framework Attivi

Instructions language-specific attive per questo progetto:
- .github/instructions/python.instructions.md
- .github/instructions/tests.instructions.md
- .github/instructions/ui.instructions.md
- .github/instructions/domain.instructions.md

## Note Progetto

- Repository applicativo per Windows con focus su accessibilita screen reader.
- Il framework e stato reinizializzato dopo aggiornamento a Framework Copilot v1.6.0.
- Topic sospeso in memoria sessione: refactor confini Partita/GameController.
