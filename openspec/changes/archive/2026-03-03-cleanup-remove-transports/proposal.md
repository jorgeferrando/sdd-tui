# Proposal: Cleanup — Remove transport adapters

## Metadata
- **Change:** cleanup-remove-transports
- **Jira:** N/A
- **Fecha:** 2026-03-03
- **Estado:** approved

## Descripción

Eliminar `core/transports.py` y `tests/test_transports.py` introducidos en
view-5-transports. El approach de comunicación inter-panel via tmux/zellij
ha sido descartado en favor de copiar instrucciones al portapapeles.

## Motivación

El código de transporte es dead code — ninguna parte del TUI lo usa todavía
y el approach que lo haría útil (tmux send-keys / zellij write-chars) ha sido
reemplazado por clipboard. Mantenerlo añade ruido sin valor.

## Impacto

- Archivos eliminados: `src/sdd_tui/core/transports.py`, `tests/test_transports.py`
- Sin cambios en el resto del código
