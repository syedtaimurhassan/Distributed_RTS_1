"""Import shim so `python -m drts_mp1...` works without installing the package.

The canonical source lives under `src/drts_mp1`.
"""

from __future__ import annotations

import pkgutil
from pathlib import Path

__path__ = pkgutil.extend_path(__path__, __name__)  # type: ignore[name-defined]
_src_pkg = Path(__file__).resolve().parent.parent / "src" / "drts_mp1"
if _src_pkg.exists():
    __path__.append(str(_src_pkg))
