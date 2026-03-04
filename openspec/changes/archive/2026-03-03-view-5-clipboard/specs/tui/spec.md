# Spec: TUI — View 5 (Clipboard command launcher)

## Metadata
- **Dominio:** tui
- **Change:** view-5-clipboard
- **Jira:** N/A
- **Fecha:** 2026-03-03
- **Versión:** 0.1
- **Estado:** draft

## Contexto

View 2 muestra el estado del pipeline de un change pero no ofrece una forma
de actuar sobre él. El usuario tiene que recordar y escribir manualmente los
comandos SDD (`/sdd-apply T01`, `/sdd-verify`, etc.) en el terminal de Claude.

View 5 cierra ese gap: una tecla en View 2 construye el comando correcto para
la siguiente fase pendiente y lo copia al portapapeles.

---

## Comportamiento Actual

View 2 no tiene acceso al flujo de ejecución SDD.
Los keybindings disponibles son: `Esc`, `r`, `p`, `d`, `s`, `t`.

---

## Comportamiento Esperado (Post-Cambio)

### Caso Principal — Copiar siguiente comando

**Dado** View 2 de un change con fases pendientes
**Cuando** el usuario pulsa `Space`
**Entonces** el TUI determina la siguiente fase pendiente, construye el
comando SDD correspondiente, lo copia al portapapeles y muestra una
notificación `Copied: {comando}`

### Lógica de construcción del comando

El comando se construye según el **primer estado NOT DONE** del pipeline,
en este orden:

| Fase pendiente | Comando copiado |
|---------------|-----------------|
| `propose` | `/sdd-propose "{change-name}"` |
| `spec` | `/sdd-spec {change-name}` |
| `design` | `/sdd-design {change-name}` |
| `tasks` | `/sdd-tasks {change-name}` |
| `apply` (ninguna tarea hecha) | `/sdd-apply {change-name}` |
| `apply` (algunas tareas hechas) | `/sdd-apply {next-task-id}` |
| `verify` | `/sdd-verify {change-name}` |
| todas DONE | `/sdd-archive {change-name}` |

### Notificación

Formato: `Copied: {comando}`

La notificación usa `self.notify()` de Textual — aparece en la esquina
inferior derecha y desaparece sola.

### Casos de edge

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Apply en curso | Algunas tareas `[x]`, alguna `[ ]` | Comando apunta a la primera `[ ]` |
| Todas las fases DONE | Pipeline completo | Copia `/sdd-archive {change-name}` |
| Change sin `tasks.md` | Apply pendiente sin tareas definidas | Copia `/sdd-apply {change-name}` |

---

## Reglas de Negocio

- **RB-V5-01:** Space siempre copia algo — nunca es un no-op silencioso.
- **RB-V5-02:** El comando refleja el estado real del pipeline en el momento de pulsar Space, no un estado cacheado.
- **RB-V5-03:** La notificación muestra el comando completo tal como debe pegarse en el terminal de Claude.
- **RB-V5-04:** No hay preview previo a la copia — la notificación post-copia es suficiente feedback.
- **RB-V5-05:** `next-task-id` se determina como la primera tarea con `done=False` en `change.tasks`.

---

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Tecla única inteligente (`Space`) | Tecla por fase | Menos cognitive load — el TUI sabe qué toca |
| Solo notificación post-copia | Preview en footer | Más simple; el usuario ya conoce el flujo |
| Siempre copia (nunca no-op) | Desactivar Space si no hay pendientes | Consistencia — archive también es una acción válida |
| Comandos con formato `/sdd-*` | `/sdd:*` (con dos puntos) | Los skills usan guion como separador |

## Abierto / Pendiente

Ninguno.
