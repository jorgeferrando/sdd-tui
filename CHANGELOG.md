# Changelog

Generated from `openspec/changes/archive/`.

## [Unreleased]

- `provider-abstraction`: Introduce una capa de abstracción de providers (Protocol-based) para desacoplar
- `todos-panel`: Añadir una pantalla `TodosScreen` a la TUI que muestre los archivos de `openspec/todos/`
- `complexity-badge`: Añadir una columna `SIZE` en `EpicsView` que muestre una métrica de complejidad por change,
- `decision-status-badges`: Añadir un campo `status` a las decisiones de diseño (`locked` / `open` / `deferred`) y mostrarlo como badge visual en `DecisionsTimeline`
- `milestone-grouping`: Añadir soporte para agrupar changes en EpicsView por hitos (milestones) definidos en `openspec/milestones.yaml`. Cuando el archivo existe, los changes activos se organizan bajo cabeceras de milestone en lugar de mostrarse en una lista plana
- `pipeline-next-action`: Añadir una línea `NEXT` al `PipelinePanel` de View 2 que muestra visualmente
- `progress-dashboard`: Añadir una pantalla global de progreso (`ProgressDashboard`) que agrega el estado
- `skill-palette`: Pantalla de skills disponibles con escaneo dinámico de `~/.claude/skills/` y copia al portapapeles del comando de invocación. Accesible desde View 1 (EpicsView) y View 2 (ChangeDetailScreen), con paleta de comandos global
- `spec-health-hints`: Añadir una columna `HINT` en `SpecHealthScreen` que muestre el comando SDD más
- `gh-actions`: Integración con GitHub Actions y releases en la TUI. Tres features complementarias
- `git-local-info`: La TUI tiene integración básica con git (diff por tarea, estado del working tree, PR status),
- `observatory-v1`: `sdd-tui` inspecciona un proyecto a la vez: siempre `Path.cwd()`.
- `pr-status`: El Pipeline sidebar de View 2 muestra el estado del flujo SDD (propose → verify),
- `sdd-init-onboarding`: Ampliar `/sdd-init` con un flujo de onboarding guiado que, mediante preguntas interactivas,
- `sdd-setup-experience`: La experiencia de instalación actual de sdd-tui requiere múltiples pasos manuales:
- `sdd-tooling-steer-audit`: Cuando un agente llega a un proyecto existente no conoce sus convenciones.
- `startup-deps-check`: `sdd-tui` asume que `git` existe (ya lo hace, falla silenciosamente).
- `velocity-metrics`: No hay forma de medir la velocidad del proceso SDD: cuánto tardamos en completar
- `cleanup-spec-debt`: El proyecto tiene dos piezas de deuda que minan la confianza en las specs
- `docs-skills-install`: Las skills SDD (`/sdd-init`, `/sdd-apply`, etc.) son necesarias para usar sdd-tui
- `openspec-enrichment`: El formato `openspec/` es funcional pero le falta contexto global del proyecto
- `perf-async-diffs`: La carga de diffs en View 2 bloquea el event loop de Textual.
- `tooling-python-lint`: El proyecto no tiene ningún linter ni formateador configurado. Esto significa:
- `tui-tests`: El core de sdd-tui (pipeline, reader, metrics, spec_parser) tiene cobertura
- `ux-feedback`: La app ejecuta acciones sin dar ningún feedback al usuario sobre el resultado.
- `ux-navigation`: Tres fricciones de navegación independientes que degradan la fluidez de uso:
- `view-8-spec-health`: sdd-tui navega y muestra el estado de los changes pero no evalúa su calidad.
- `view-9-delta-specs`: Las specs canónicas en `openspec/specs/{dominio}/spec.md` acumulan cambios
- `view-help-screen`: sdd-tui tiene ~20 keybindings distribuidos en 5 pantallas. El footer de
- `view-search-filter`: View 1 muestra todos los changes en un DataTable. Con pocos cambios esto
- `cleanup-remove-transports`: Eliminar `core/transports.py` y `tests/test_transports.py` introducidos en
- `docs-readme-install`: El README describe el estado inicial del proyecto (diseño conceptual, vistas no
- `view-3-commit-diff`: View 2 muestra qué tareas están commiteadas y con qué hash, pero no permite
- `view-4-doc-viewer`: View 2 muestra el estado de las tareas y el pipeline de un change, pero para
- `view-5-clipboard`: Desde View 2 (detalle de un change), el usuario puede lanzar cualquier
- `view-5-transports`: Añadir una capa de transporte desacoplada que permita al TUI enviar instrucciones
- `view-6-refresh-in-place`: Al pulsar `r` en View 2 (ChangeDetailScreen), la app recarga los datos pero regresa
- `view-7-show-archived`: View 1 (EpicsView) solo muestra changes activos. No hay forma de consultar los
- `bootstrap`: El proyecto existe como repositorio vacío. Necesitamos el esqueleto mínimo
- `view-2-change-detail`: View 1 muestra el estado del pipeline por change (a nivel de fase SDD).

