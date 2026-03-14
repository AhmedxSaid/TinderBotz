"""Combined script to open Chrome, navigate to Bumpy, and run click sequence loop."""

import subprocess
import time
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from click_sequence import run_click_sequence_loop


def open_chrome():
    """Open Chrome and navigate to Bumpy."""
    print("Opening Chrome...")
    subprocess.Popen(
        ["C:/Program Files/Google/Chrome/Application/chrome.exe", "https://bumpy.app/app"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("Chrome opened at bumpy.app")


def main():
    """Main function: Open Chrome and run click sequence loop."""
    print("=" * 60)
    print("Starting - Opening Chrome and Bumpy")
    print("=" * 60)

    # Open Chrome
    open_chrome()

    # Wait for Chrome to load
    print("Waiting for Chrome to load...")
    time.sleep(5)

    print("\n" + "=" * 60)
    print("Starting Click Sequence Loop")
    print("=" * 60)
    print("Configuration:")
    print("  - Iterations: random (60-100) each run")
    print("  - Delay between clicks: 2-10 seconds (random)")
    print("  - Primary clicks: disabled")
    print("  - Final click: random 60-80% left (880, 1020), 20-40% right (1070, 1020)")
    print("=" * 60 + "\n")

    # Keep the Badoo click profile for Bumpy unless adjusted later.
    run_click_sequence_loop(
        num_iterations=None,  # Random between 60-100
        left_weight=None,  # Random between 60-80% left
        delay_between_clicks=2.0,
        delay_variance=8.0,  # Total delay: 2-10 seconds
        primary_x=0,  # Disabled for this flow
        primary_y=0,  # Disabled for this flow
        imprecision=0,
        left_coords=(880, 1020),
        right_coords=(1070, 1020)
    )

    print("\n" + "=" * 60)
    print("ALL COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
