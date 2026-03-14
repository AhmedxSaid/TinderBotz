"""Run the Bumble, Badoo, and Bumpy automation scripts sequentially."""

import os
import subprocess
import sys


SCRIPT_NAMES = [
    "open_bumble_and_click.py",
    "open_badoo_and_click.py",
    "open_bumpy_and_click.py",
]


def main():
    """Run each site automation script once in sequence."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("Starting combined run for Bumble, Badoo, and Bumpy")
    print("=" * 60)

    for index, script_name in enumerate(SCRIPT_NAMES, start=1):
        script_path = os.path.join(base_dir, script_name)

        print(f"\n[{index}/{len(SCRIPT_NAMES)}] Running {script_name}")
        print("-" * 60)

        subprocess.run([sys.executable, script_path], check=True)

    print("\n" + "=" * 60)
    print("ALL SCRIPTS COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
