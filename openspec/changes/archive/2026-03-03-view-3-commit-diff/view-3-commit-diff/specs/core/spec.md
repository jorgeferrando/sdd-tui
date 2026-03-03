# Spec: Core — Git Reader (get_diff)

## Metadata
- **Dominio:** core
- **Change:** view-3-commit-diff
- **Fecha:** 2026-03-03
- **Versión:** 0.1
- **Estado:** draft

## Contexto

`GitReader` ya tiene `is_clean()` y `find_commit()`. View 3 necesita obtener
el diff de un commit concreto para mostrarlo en la TUI.

---

## Comportamiento Esperado

### `get_diff` — Obtener diff de un commit

**Dado** un hash de commit de 7 caracteres y un path de repo
**Cuando** se llama a `get_diff(commit_hash, repo_path)`
**Entonces** se ejecuta `git show {commit_hash}` y se retorna el output como `str`

```python
def get_diff(commit_hash: str, repo_path: Path) -> str | None
```

### Casos alternativos

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Hash válido | `git show` retorna output | `str` con el diff completo |
| Hash inválido | `git show` falla (exit ≠ 0) | `None` |
| No es repo git | Comando falla | `None` |
| git no instalado | `FileNotFoundError` | `None` |

### Reglas de negocio

- **RB-12:** Si `commit_hash` es `None` o vacío, retorna `None` sin ejecutar git.
- **RB-13:** Errores de subprocess se capturan silenciosamente — retorna `None`.
- **RB-14:** El output incluye el header del commit (`commit`, `Author`, `Date`, mensaje) seguido del diff.

---

### `get_working_diff` — Diff del working tree actual

**Dado** un path de repo git
**Cuando** se llama a `get_working_diff(repo_path)`
**Entonces** se ejecuta `git diff HEAD --no-color` y se retorna el output como `str`

```python
def get_working_diff(self, cwd: Path) -> str | None
```

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| Hay cambios pendientes | `git diff HEAD` retorna output | `str` con el diff |
| Working tree limpio | `git diff HEAD` retorna vacío | `None` |
| Error de git | returncode != 0 o git no instalado | `None` |

- **RB-15:** `git diff HEAD` incluye cambios staged y unstaged respecto al último commit.
- **RB-16:** Si el output es vacío string, se retorna `None` (repo limpio).

---

## Decisiones Tomadas

| Decisión | Alternativa | Motivo |
|---------|------------|--------|
| `git show {hash}` | `git diff {hash}^..{hash}` | `git show` incluye metadata del commit |
| `str \| None` | Lanzar excepción | Coherente con `find_commit()` — TUI decide cómo mostrar el error |
| Sin stripear ANSI | Forzar `--no-color` en el comando | `git show` sin flags no produce ANSI; si el usuario tiene `color.ui=always`, se stripea en TUI |

## Abierto / Pendiente

Ninguno.
