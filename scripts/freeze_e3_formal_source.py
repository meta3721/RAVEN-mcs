#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from raven_mcs.e3.formal.constants import art_path
from raven_mcs.e3.formal.source_freeze import write
if __name__ == "__main__": print(write(ROOT, art_path(ROOT)))
