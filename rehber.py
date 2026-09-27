#!/usr/bin/env python3
"""Onion Rehberi başlatıcı. Kullanım: python3 rehber.py  (menü)  ya da  python3 rehber.py --help"""

import sys

if sys.version_info < (3, 8):
    sys.exit("Onion Rehberi Python 3.8 veya üstünü gerektirir.")

from onion_rehberi.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
