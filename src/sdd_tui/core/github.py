# core/github.py — compatibility shim (to be removed in a future epic)
# All implementations have moved to core/providers/
from sdd_tui.core.providers.github import (  # noqa: F401
    get_ci_status,
    get_pr_status,
    get_releases,
)
from sdd_tui.core.providers.protocol import (  # noqa: F401
    CiStatus,
    PrStatus,
    ReleaseInfo,
)
