# Spec: Core — Transport adapters

## Metadata
- **Dominio:** core
- **Change:** view-5-transports
- **Fecha:** 2026-03-03
- **Versión:** 0.1
- **Estado:** approved

## Contexto

Para que el TUI pueda enviar instrucciones a un agente IA en otro panel,
se necesita una capa de transporte que abstraiga el multiplexer de terminal.

## Comportamiento Esperado

### Auto-detección

**Dado** un entorno con `$TMUX` activo
**Cuando** se llama `detect_transport()`
**Entonces** retorna `TmuxTransport`

**Dado** un entorno con `$ZELLIJ` activo y sin `$TMUX`
**Cuando** se llama `detect_transport()`
**Entonces** retorna `ZellijTransport`

**Dado** un entorno sin multiplexer (solo Ghostty nativo, etc.)
**Cuando** se llama `detect_transport()`
**Entonces** retorna `None`

### TmuxTransport

- `is_available()` → `True` si `$TMUX` está definido
- `find_pane(process_name)` → busca entre todos los panes el que corre ese proceso; retorna `pane_id` o `None`
- `send_command(pane_id, command)` → ejecuta `tmux send-keys -t {pane_id} {command} Enter`
- Puede targetear cualquier pane independientemente del foco

### ZellijTransport

- `is_available()` → `True` si `$ZELLIJ` está definido
- `find_pane(process_name)` → retorna `None` siempre — Zellij no expone API de targeting por proceso
- `send_command(pane_id, command)` → envía al pane **enfocado** via `zellij action write-chars` + `write 10`
- **Limitación:** no puede targetear un pane específico; siempre actúa sobre el pane con foco

### Limitación conocida de Zellij

Cuando sdd-tui está corriendo y tiene el foco, `send_command` se enviaría
al propio TUI, no al panel del agente IA. Esta limitación es inherente al
CLI de Zellij (no existe `zellij send-keys -t pane_id`).

El TUI deberá informar al usuario de esta limitación cuando detecte Zellij,
o requerir que el usuario enfoque manualmente el panel del agente antes de enviar.

## Reglas

- **RB-TR-01:** `detect_transport()` prueba tmux antes que zellij.
- **RB-TR-02:** `find_pane()` retorna `None` si no encuentra el proceso o si hay error.
- **RB-TR-03:** ZellijTransport ignora el parámetro `pane_id` en `send_command`.
- **RB-TR-04:** Los transportes no lanzan excepciones — propagan errores de subprocess solo en `send_command`.
