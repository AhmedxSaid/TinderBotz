"""Combined script to open Chrome, navigate to Bumble, and run click sequence loop."""

import subprocess
import time
import random
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from click_sequence import run_click_sequence_loop


def open_chrome():
    """Open Chrome and navigate to Bumble."""
    print("Opening Chrome...")
    subprocess.Popen(
        ["C:/Program Files/Google/Chrome/Application/chrome.exe", "https://bumble.com/app"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("Chrome opened at bumble.com")


def main():
    """Main function: Open Chrome and run click sequence loop."""
    print("=" * 60)
    print("Starting - Opening Chrome and Bumble")
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
    print("  - Primary clicks: 0-4 times at (1100, 900) with ±50 imprecision (2-4 most likely)")
    print("  - Final click: random 60-80% left (1050, 1040), 20-40% right (1250, 1040)")
    print("=" * 60 + "\n")
    
    # Run the click sequence loop (will be random 60-100 iterations, 60-80% left)
    results = run_click_sequence_loop(
        num_iterations=None,  # Random between 60-100
        left_weight=None,  # Random between 60-80% left
        delay_between_clicks=2.0,
        delay_variance=8.0,  # Total delay: 2-10 seconds
        primary_x=1100,
        primary_y=900,
        imprecision=50,
        left_coords=(1050, 1040),
        right_coords=(1250, 1040)
    )
    
    print("\n" + "=" * 60)
    print("ALL COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
