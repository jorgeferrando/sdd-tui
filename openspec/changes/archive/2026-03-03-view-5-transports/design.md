# Design: View 5 — Transport adapters

## Metadata
- **Change:** view-5-transports
- **Fecha:** 2026-03-03
- **Estado:** approved

## Resumen Técnico

Un único módulo `core/transports.py` define el `Transport` Protocol y sus dos
implementaciones iniciales. La función `detect_transport()` actúa como factory.

## Arquitectura

```
core/transports.py
  ├── Transport (Protocol)
  ├── TmuxTransport
  ├── ZellijTransport
  └── detect_transport() → Transport | None
```

## Detalle de Implementación

### `Transport` Protocol

```python
class Transport(Protocol):
    @property
    def name(self) -> str: ...
    def is_available(self) -> bool: ...
    def find_pane(self, process_name: str) -> str | None: ...
    def send_command(self, pane_id: str, command: str) -> None: ...
```

### `TmuxTransport`

- `is_available()`: `bool(os.environ.get("TMUX"))`
- `find_pane()`: `tmux list-panes -a -F "#{pane_id} #{pane_current_command}"` → busca por nombre de proceso (case-insensitive)
- `send_command()`: `tmux send-keys -t {pane_id} {command} Enter`
- Errores: captura `CalledProcessError` y `FileNotFoundError` en `find_pane()`, retorna `None`

### `ZellijTransport`

- `is_available()`: `bool(os.environ.get("ZELLIJ"))`
- `find_pane()`: retorna `None` — Zellij CLI no expone targeting por proceso
- `send_command()`: `zellij action write-chars {command}` + `zellij action write 10`

### Limitación de Zellij

Zellij no tiene equivalente a `tmux send-keys -t pane_id`. Su CLI solo puede
escribir en el pane enfocado. Como sdd-tui siempre tendrá el foco cuando el
usuario interactúa con él, `send_command` escribiría en el TUI mismo, no en
el panel del agente.

Consecuencia: `find_pane()` retorna `None` para señalizar que el targeting
no es posible. El TUI (view-5 completo) usará esto para mostrar un aviso
al usuario en lugar de enviar ciegamente.

### `detect_transport()`

```python
def detect_transport() -> Transport | None:
    for transport in [TmuxTransport(), ZellijTransport()]:
        if transport.is_available():
            return transport
    return None
```

Tmux tiene prioridad sobre Zellij.

## Decisiones de Diseño

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| Un solo archivo `transports.py` | Subpaquete `transports/` | Sin over-engineering para 2 clases |
| `Protocol` en vez de ABC | `ABC` con métodos abstractos | Más Pythonic, duck typing, sin herencia forzada |
| `find_pane()` retorna `None` en Zellij | Sentinel "focused" | `None` es el contrato correcto para "no encontrado / no soportado" |
| `detect_transport()` como función libre | Clase factory | Más simple, sin estado |
