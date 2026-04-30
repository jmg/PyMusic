# -*- coding: utf-8 -*-
"""Placeholder for an eyeD3-based tag reader.

The original module performed import-time side effects against a hard-coded
file on the developer's machine. It has been left in place as a stub so the
package keeps importing cleanly under Python 3.
"""

if __name__ == "__main__":  # pragma: no cover - manual smoke test only
    try:
        import eyed3  # noqa: F401
    except ImportError:
        print("eyed3 is not installed")
    else:
        print("eyed3 import succeeded")
