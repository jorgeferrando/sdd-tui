# Proposal: View 5 — Transport adapters

## Metadata
- **Change:** view-5-transports
- **Jira:** N/A
- **Fecha:** 2026-03-03
- **Estado:** approved

## Descripción

Añadir una capa de transporte desacoplada que permita al TUI enviar instrucciones
a un agente IA (Claude, Codex, Gemini, Opencode, etc.) corriendo en otro panel
del terminal, sin que el TUI dependa de qué multiplexer o qué agente se usa.

## Motivación

La visión de view-5 es que el TUI pueda orquestar el flujo SDD completo
(propose → spec → design → tasks → apply → verify) enviando instrucciones al
agente IA activo. Para ello hace falta primero una capa de transporte que
abstraiga el mecanismo de comunicación inter-panel.

## Approach

Definir un `Transport` Protocol en `core/` con dos implementaciones iniciales:
- `TmuxTransport` — detección via `$TMUX`, targeting por pane ID
- `ZellijTransport` — detección via `$ZELLIJ`, con limitación de targeting

Función `detect_transport()` auto-detecta el multiplexer activo.

## Impacto

- Archivos nuevos: `core/transports.py`, `tests/test_transports.py`
- Sin cambios en TUI ni en core existente
- Sin dependencias nuevas
