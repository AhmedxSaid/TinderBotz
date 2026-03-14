"""Test script for click_sequence.py - simulates the click actions without actual mouse clicks."""

import random
import time
from typing import Tuple


def add_imprecision(base_x: int, base_y: int, imprecision: int = 50) -> Tuple[int, int]:
    """Add random imprecision to coordinates."""
    offset_x = random.randint(-imprecision, imprecision)
    offset_y = random.randint(-imprecision, imprecision)
    return base_x + offset_x, base_y + offset_y


def weighted_choice(options: list, weights: list) -> any:
    """Make a weighted random choice from options."""
    return random.choices(options, weights=weights, k=1)[0]


def perform_clicks_with_imprecision(
    base_x: int,
    base_y: int,
    imprecision: int,
    min_clicks: int = 2,
    max_clicks: int = 4,
    delay_min: float = 0.3,
    delay_max: float = 0.8,
    simulate: bool = True
) -> int:
    """Perform multiple clicks at coordinates with imprecision."""
    num_clicks = random.randint(min_clicks, max_clicks)
    
    for i in range(num_clicks):
        click_x, click_y = add_imprecision(base_x, base_y, imprecision)
        
        if simulate:
            print(f"[SIMULATED] Click {i + 1}/{num_clicks} at ({click_x}, {click_y})")
        else:
            import pyautogui
            pyautogui.moveTo(click_x, click_y, duration=0.2)
            pyautogui.click(button="left")
        
        if i < num_clicks - 1:
            delay = random.uniform(delay_min, delay_max)
            time.sleep(delay)
    
    return num_clicks


def perform_weighted_click(
    left_coords: Tuple[int, int],
    right_coords: Tuple[int, int],
    left_weight: float = 0.6,
    right_weight: float = 0.4,
    imprecision: int = 0,
    simulate: bool = True
) -> str:
    """Perform a click at either left or right coordinates based on weighted probability."""
    options = ["left", "right"]
    weights = [left_weight, right_weight]
    
    choice = weighted_choice(options, weights)
    
    if choice == "left":
        target_x, target_y = left_coords
        print(f"[SIMULATED] Performing LEFT click at {left_coords}")
    else:
        target_x, target_y = right_coords
        print(f"[SIMULATED] Performing RIGHT click at {right_coords}")
    
    if imprecision > 0:
        target_x, target_y = add_imprecision(target_x, target_y, imprecision)
    
    if not simulate:
        import pyautogui
        pyautogui.moveTo(target_x, target_y, duration=0.2)
        pyautogui.click(button="left")
    
    print(f"[SIMULATED] Clicked at ({target_x}, {target_y})")
    
    return choice


def run_click_sequence(
    primary_x: int = 1100,
    primary_y: int = 900,
    imprecision: int = 50,
    left_coords: Tuple[int, int] = (1050, 1040),
    right_coords: Tuple[int, int] = (1250, 1040),
    left_weight: float = 0.65,
    delay_after_primary: float = 1.0,
    simulate: bool = True
) -> dict:
    """Run the complete click sequence as specified."""
    print("=" * 50)
    print("Starting click sequence...")
    print("=" * 50)
    
    results = {
        "primary_clicks": 0,
        "final_click_side": None
    }
    
    # Step 1: Perform primary clicks (2-4 times) with imprecision
    print(f"\n[Step 1] Primary clicks at ({primary_x}, {primary_y}) with ±{imprecision} imprecision")
    results["primary_clicks"] = perform_clicks_with_imprecision(
        base_x=primary_x,
        base_y=primary_y,
        imprecision=imprecision,
        min_clicks=2,
        max_clicks=4,
        delay_min=0.3,
        delay_max=0.8,
        simulate=simulate
    )
    print(f"Completed {results['primary_clicks']} primary clicks")
    
    time.sleep(delay_after_primary)
    
    # Step 2: Perform weighted left/right click
    print(f"\n[Step 2] Weighted click (left: {left_weight*100:.0f}%, right: {(1-left_weight)*100:.0f}%)")
    results["final_click_side"] = perform_weighted_click(
        left_coords=left_coords,
        right_coords=right_coords,
        left_weight=left_weight,
        right_weight=1 - left_weight,
        imprecision=0,
        simulate=simulate
    )
    
    print("\n" + "=" * 50)
    print("Click sequence completed!")
    print("=" * 50)
    
    return results


if __name__ == "__main__":
    print("Testing click sequence (SIMULATED mode)...")
    print()
    
    # Run 5 test sequences to show the randomization
    for i in range(5):
        print(f"\n{'='*20} Test {i+1} {'='*20}")
        result = run_click_sequence(
            primary_x=1100,
            primary_y=900,
            imprecision=50,
            left_coords=(1050, 1040),
            right_coords=(1250, 1040),
            left_weight=0.65,
            delay_after_primary=0.5,
            simulate=True
        )
        print(f"Results: {result}")
        time.sleep(0.5)
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)
    print("\nTo run with actual mouse clicks, set simulate=False")
    print("or import click_sequence.py and call run_click_sequence(simulate=False)")
