# Proposal: View 5 — Clipboard command launcher

## Metadata
- **Change:** view-5-clipboard
- **Jira:** N/A
- **Fecha:** 2026-03-03
- **Estado:** draft

## Descripción

Desde View 2 (detalle de un change), el usuario puede lanzar cualquier
comando del flujo SDD con una tecla. El TUI construye el comando correcto
y lo copia al portapapeles. El usuario lo pega en el terminal donde tiene
Claude activo.

## Motivación

El flujo SDD actual requiere que el usuario recuerde y escriba manualmente
cada comando en Claude (`/sdd:apply T01`, `/sdd:verify`, etc.). El TUI ya
tiene toda la información para construir esos comandos — change activo, tarea
siguiente, fase actual. Solo falta exponerlos de forma accionable.

La solución vía clipboard es la más simple y robusta: funciona con cualquier
terminal, cualquier multiplexer, cualquier agente IA, sin permisos especiales
ni dependencias adicionales.

## Comportamiento esperado

El usuario está en View 2 de un change. Ve el estado del pipeline y las tareas.
Pulsa una tecla (por ejemplo `a` para apply) → el TUI copia al portapapeles
el comando `/sdd:apply T03` (la siguiente tarea pendiente) y muestra una
notificación `Copied: /sdd:apply T03`. El usuario va al terminal de Claude,
pega y ejecuta.

## Indicador de estado del agente (opcional)

Una barra de estado podría mostrar si hay un pane con Claude activo
(detectado via `$TMUX` o `$ZELLIJ`), pero la copia al portapapeles
funciona independientemente de ese indicador.

## Approach

- Textual tiene `self.app.copy_to_clipboard(text)` built-in — sin deps nuevas
- Los comandos se construyen en función del estado del pipeline del change
- Keybindings nuevos en `ChangeDetailScreen`
- Notificación visual con `self.notify()`

## Impacto estimado

- Archivos modificados: `tui/change_detail.py`
- Sin cambios en core ni en otros módulos
- Sin dependencias nuevas
