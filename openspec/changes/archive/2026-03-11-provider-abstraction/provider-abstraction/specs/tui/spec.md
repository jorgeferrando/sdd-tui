# Spec: TUI — provider-abstraction (GitWorkflowSetupScreen)

## Metadata
- **Dominio:** tui
- **Change:** provider-abstraction
- **Jira:** N/A
- **Fecha:** 2026-03-11
- **Versión:** 2.7
- **Estado:** draft

## Contexto

Delta sobre la spec TUI v2.6. Añade `GitWorkflowSetupScreen` (wizard de configuración
del flujo git) y el binding `S` en `EpicsView`.

## Comportamiento Actual

`EpicsView` no expone configuración git del proyecto. La sección `git_workflow:` no
existe en `openspec/config.yaml`.

## Requisitos (EARS)

### Binding S en EpicsView

- **REQ-SW01** `[Event]` When the user presses `S` in `EpicsView`, the system SHALL
  open `GitWorkflowSetupScreen`.

- **REQ-SW02** `[Ubiquitous]` The `S` binding SHALL appear in the `Footer` with
  label "Setup".

### GitWorkflowSetupScreen — estructura

- **REQ-WZ01** `[Event]` When `GitWorkflowSetupScreen` mounts, the system SHALL
  display the first question of the wizard. If `git_workflow:` already exists in
  `openspec/config.yaml`, it SHALL display a summary of the current config with
  an option to reconfigure.

- **REQ-WZ02** `[Ubiquitous]` The wizard SHALL present 5 questions in sequence,
  one at a time:
  1. **Issue tracker** — github | jira* | trello* | none
  2. **Git host** — github | bitbucket* | gitlab* | none
  3. **Branching model** — github-flow | git-flow
  4. **Change prefix** — `issue` | `#` | sin prefijo | personalizado
  5. **Changelog format** — labels | commit-prefix | both

- **REQ-WZ03** `[Ubiquitous]` Options marked with `*` (jira, trello, bitbucket,
  gitlab) SHALL be displayed as disabled with the label "(próximamente)". Attempting
  to select them SHALL show an inline message "Not yet available" without advancing.

- **REQ-WZ04** `[Event]` When the user selects option `[4] personalizado` for
  change prefix, the system SHALL present a text input field for free-form entry.
  The input SHALL accept any non-empty string.

### GitWorkflowSetupScreen — guardado

- **REQ-WZ05** `[Event]` When the user completes all 5 questions, the system SHALL
  write the `git_workflow:` section to `openspec/config.yaml` and notify
  "Git workflow configured ✓".

- **REQ-WZ06** `[Ubiquitous]` The write operation SHALL be atomic: only the
  `git_workflow:` block is added or replaced. The rest of `openspec/config.yaml`
  (project, jira_prefix, paths, etc.) SHALL remain unchanged.

- **REQ-WZ07** `[Unwanted]` If `openspec/config.yaml` does not exist, the system
  SHALL create it with only the `git_workflow:` section plus the comment
  `# Añadir jira_prefix: si usas SDD`.

### GitWorkflowSetupScreen — cancelación

- **REQ-WZ08** `[Event]` When the user presses `Escape` at any point during the
  wizard, the system SHALL discard all answers and return to `EpicsView` without
  modifying `openspec/config.yaml`.

- **REQ-WZ09** `[Ubiquitous]` The wizard is all-or-nothing: partial answers are
  never persisted.

### Escenarios de verificación

**REQ-WZ05 + REQ-WZ06** — config existente no sobreescrita
**Dado** `openspec/config.yaml` con `project: sdd-tui` y `jira_prefix: DI`
**Cuando** el usuario completa el wizard y guarda
**Entonces** el archivo contiene `project: sdd-tui`, `jira_prefix: DI` y la nueva
sección `git_workflow:` — los campos previos no fueron alterados

**REQ-WZ08** — cancelación a mitad
**Dado** el usuario ha respondido 3 de 5 preguntas
**Cuando** pulsa Escape
**Entonces** `openspec/config.yaml` no fue modificado

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|----------|------------|--------|
| Wizard secuencial (una pregunta por pantalla) | Formulario único | Reduce carga cognitiva; cada opción tiene espacio para su descripción |
| Esc = descartar todo | Guardar parcial | El wizard es una transacción; config parcial puede dejar el sistema en estado inconsistente |
| "Próximamente" visible pero no seleccionable | Ocultar opciones futuras | El usuario puede planificar la migración al proveedor correcto |
| `S` en EpicsView | Binding en menú de ayuda | Acceso directo — la configuración se necesita antes de usar cualquier feature git-native |
