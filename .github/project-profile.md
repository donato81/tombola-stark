---
initialized: true
project_name: "Tombola Stark"
version: "0.9.3"
primary_language: "Python"
secondary_languages: []
ui_framework: "wxPython"
test_runner: "unitest"
build_system: "cx_Freeze"
architecture: "clean-architecture-4-layer"
accessibility: true
framework_edit_mode: false
verbosity: "collaborator"
personality: "mentor"
platform: "Windows 10/11"
screen_reader: "NVDA/JAWS"
---

# Profilo Progetto

> Questo file è la source of truth del progetto.
> Compilato da Agent-Welcome durante il setup iniziale.
> Non modificare manualmente i valori del frontmatter YAML.

## Identità

- **Nome**: Tombola Stark
- **Versione corrente**: 0.9.3
- **Descrizione**: Tombola digitale accessibile ai nonvedenti con screen reader.

## Stack Tecnico

- **Linguaggio primario**: Python
- **Linguaggi secondari**: nessuno
- **Framework UI**: wxPython
- **Test runner**: pytest
- **Build system**: cx_Freeze
- **Piattaforma target**: Windows 10/11

## Architettura

- **Pattern**: Clean Architecture 4-layer
- **Layer**: Presentation → Application → Domain → Infrastructure
- **Riferimento**: docs/ARCHITECTURE.md

## Accessibilità

- **Richiesta**: sì
- **Screen reader**: NVDA / JAWS
- **Standard**: output lineare, navigazione da tastiera, zero dipendenza dal mouse
- **Riferimento**: .github/instructions/ui.instructions.md

## Componenti Framework Attivi

Instructions language-specific attive per questo progetto:
- python.instructions.md (già presente)

## Note Progetto

- **Framework Edit Mode**: Variabile di controllo sicurezza. Se `false`,
  i componenti del framework sono protetti da modifiche accidentali.
  Modificabile solo tramite il prompt `#framework-unlock`.
- **Verbosity**: Livello di verbosita comunicativa globale degli
    agenti. Valori: `tutor` | `collaborator` | `nerd`. Default:
    `collaborator`. Modificabile tramite `#verbosity`.
    Override temporaneo di sessione: dichiaralo verbalmente in chat
    senza modificare questo file.
- **Personality**: Postura operativa e stile relazionale degli
    agenti. Valori: `mentor` | `pragmatico` | `reviewer` |
    `architect`. Default: `pragmatico`. Modificabile tramite
    `#personality`. Override temporaneo di sessione: dichiaralo
    verbalmente in chat senza modificare questo file.

framework_edit_mode: true

(spazio per note contestuali — aggiornabile tramite
`#project-update` in qualsiasi momento)
