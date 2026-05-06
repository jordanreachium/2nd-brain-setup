"""Allow `python -m code` invocation by delegating to run.main()."""
from __future__ import annotations

import sys

from code.run import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
