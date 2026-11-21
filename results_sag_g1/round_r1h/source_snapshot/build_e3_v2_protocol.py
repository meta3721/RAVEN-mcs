"""Build frozen E3-v2 protocol artifacts. Does not run SAG."""

from __future__ import annotations

import argparse
from pathlib import Path

from raven_mcs.experiments.run_sag_g1_r1g import run_r1g_main


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    result = run_r1g_main(root=args.root)
    print(result.get("verdict"), result.get("e3v2_routing"))


if __name__ == "__main__":
    main()
