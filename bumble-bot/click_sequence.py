"""Mouse click automation with human-like imprecision and weighted actions.

This module provides functions to perform clicks at specified coordinates
with randomization, and weighted random selection between left/right clicks.
"""

import random
import time
from typing import Tuple

import pyautogui


# Configure pyautogui for safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


def add_imprecision(base_x: int, base_y: int, imprecision: int = 50) -> Tuple[int, int]:
    """Add random imprecision to coordinates.
    
    Args:
        base_x: Base X coordinate.
        base_y: Base Y coordinate.
        imprecision: Maximum pixel offset in any direction (default 50).
    
    Returns:
        Tuple of (x, y) with random offset applied.
    """
    offset_x = random.randint(-imprecision, imprecision)
    offset_y = random.randint(-imprecision, imprecision)
    return base_x + offset_x, base_y + offset_y


def click_at(
    x: int,
    y: int,
    button: str = "left",
    imprecision: int = 0,
    duration: float = 0.2
) -> None:
    """Click at the specified coordinates with optional imprecision.
    
    Args:
        x: X coordinate for the click.
        y: Y coordinate for the click.
        button: Mouse button to use ('left' or 'right').
        imprecision: Pixel imprecision to add to coordinates.
        duration: Time in seconds to move mouse to position.
    """
    # Add imprecision if specified
    if imprecision > 0:
        x, y = add_imprecision(x, y, imprecision)
    
    # Move to position and click
    pyautogui.moveTo(x, y, duration=duration)
    pyautogui.click(button=button)


def weighted_choice(options: list, weights: list) -> any:
    """Make a weighted random choice from options.
    
    Args:
        options: List of options to choose from.
        weights: List of weights corresponding to each option.
    
    Returns:
        Selected option based on weighted probability.
    """
    return random.choices(options, weights=weights, k=1)[0]


def perform_clicks_with_imprecision(
    base_x: int,
    base_y: int,
    imprecision: int,
    min_clicks: int = 0,
    max_clicks: int = 4,
    bias_towards_middle: bool = True,
    delay_min: float = 0.3,
    delay_max: float = 0.8
) -> int:
    """Perform multiple clicks at coordinates with imprecision.
    
    Args:
        base_x: Base X coordinate.
        base_y: Base Y coordinate.
        imprecision: Pixel imprecision to add to coordinates.
        min_clicks: Minimum number of clicks to perform (default 0).
        max_clicks: Maximum number of clicks to perform (default 4).
        bias_towards_middle: If True, 2-4 clicks are more likely than 0-1.
        delay_min: Minimum delay between clicks in seconds.
        delay_max: Maximum delay between clicks in seconds.
    
    Returns:
        Number of clicks performed.
    """
    # Generate weighted random number of clicks
    if bias_towards_middle:
        # Weighted towards 2-4, with 0-1 being less likely
        weights = [0.1, 0.15, 0.25, 0.25, 0.25]  # clicks 0,1,2,3,4
        num_clicks = weighted_choice(range(min_clicks, max_clicks + 1), weights)
    else:
        num_clicks = random.randint(min_clicks, max_clicks)
    
    for i in range(num_clicks):
        # Get coordinates with imprecision
        click_x, click_y = add_imprecision(base_x, base_y, imprecision)
        
        # Move and click
        pyautogui.moveTo(click_x, click_y, duration=0.2)
        pyautogui.click(button="left")
        
        print(f"Click {i + 1}/{num_clicks} at ({click_x}, {click_y})")
        
        # Add random delay between clicks (not after last click)
        if i < num_clicks - 1:
            delay = random.uniform(delay_min, delay_max)
            time.sleep(delay)
    
    return num_clicks


def perform_weighted_click(
    left_coords: Tuple[int, int],
    right_coords: Tuple[int, int],
    left_weight: float = 0.6,
    right_weight: float = 0.4,
    imprecision: int = 0
) -> str:
    """Perform a click at either left or right coordinates based on weighted probability.
    
    Args:
        left_coords: Tuple of (x, y) for left click.
        right_coords: Tuple of (x, y) for right click.
        left_weight: Weight/probability for left click (default 0.6 = 60%).
        right_weight: Weight/probability for right click (default 0.4 = 40%).
        imprecision: Pixel imprecision to add to coordinates.
    
    Returns:
        String indicating which side was clicked ('left' or 'right').
    """
    options = ["left", "right"]
    weights = [left_weight, right_weight]
    
    choice = weighted_choice(options, weights)
    
    if choice == "left":
        target_x, target_y = left_coords
        print(f"Performing LEFT click at {left_coords}")
    else:
        target_x, target_y = right_coords
        print(f"Performing RIGHT click at {right_coords}")
    
    # Apply imprecision and click
    if imprecision > 0:
        target_x, target_y = add_imprecision(target_x, target_y, imprecision)
    
    pyautogui.moveTo(target_x, target_y, duration=0.2)
    pyautogui.click(button="left")
    
    print(f"Clicked at ({target_x}, {target_y})")
    
    return choice


def run_click_sequence(
    primary_x: int = 1100,
    primary_y: int = 900,
    imprecision: int = 50,
    left_coords: Tuple[int, int] = (1050, 1040),
    right_coords: Tuple[int, int] = (1250, 1040),
    left_weight: float = 0.65,
    delay_after_primary: float = 1.0
) -> dict:
    """Run the complete click sequence as specified.
    
    Sequence:
    1. Click at primary coordinates (1100, 900) with +50 imprecision, 2-4 times
    2. Wait briefly
    3. Click at left or right coordinates with weighted probability (more left clicks)
    
    Args:
        primary_x: X coordinate for primary click area.
        primary_y: Y coordinate for primary click area.
        imprecision: Pixel imprecision for primary clicks.
        left_coords: Coordinates for left click option.
        right_coords: Coordinates for right click option.
        left_weight: Probability weight for left click (higher = more left clicks).
        delay_after_primary: Delay in seconds after primary clicks.
    
    Returns:
        Dictionary with results of the click sequence.
    """
    print("=" * 50)
    print("Starting click sequence...")
    print("=" * 50)
    
    results = {
        "primary_clicks": 0,
        "final_click_side": None
    }
    
    # Step 1: Perform primary clicks (0-4 times, biased towards 2-4) with imprecision
    # Skip if primary_x or primary_y is 0 (disabled for Badoo)
    if primary_x == 0 or primary_y == 0:
        print(f"\n[Step 1] Primary clicks DISABLED")
        results["primary_clicks"] = 0
    else:
        print(f"\n[Step 1] Primary clicks at ({primary_x}, {primary_y}) with ±{imprecision} imprecision")
        results["primary_clicks"] = perform_clicks_with_imprecision(
            base_x=primary_x,
            base_y=primary_y,
            imprecision=imprecision,
            min_clicks=0,
            max_clicks=4,
            bias_towards_middle=True,
            delay_min=0.3,
            delay_max=0.8
        )
        print(f"Completed {results['primary_clicks']} primary clicks")
    
    # Delay after primary clicks (skip if 0)
    if delay_after_primary > 0:
        time.sleep(delay_after_primary)
    
    # Step 2: Perform weighted left/right click
    print(f"\n[Step 2] Weighted click (left: {left_weight*100:.0f}%, right: {(1-left_weight)*100:.0f}%)")
    results["final_click_side"] = perform_weighted_click(
        left_coords=left_coords,
        right_coords=right_coords,
        left_weight=left_weight,
        right_weight=1 - left_weight,
        imprecision=0  # No imprecision for final click unless specified
    )
    
    print("\n" + "=" * 50)
    print("Click sequence completed!")
    print("=" * 50)
    
    return results


def run_click_sequence_loop(
    num_iterations: int = None,
    delay_between_clicks: float = 2.0,
    delay_variance: float = 8.0,
    primary_x: int = 1100,
    primary_y: int = 900,
    imprecision: int = 50,
    left_coords: Tuple[int, int] = (1050, 1040),
    right_coords: Tuple[int, int] = (1250, 1040),
    left_weight: float = None
) -> list:
    """Run the click sequence multiple times in a loop.
    
    Args:
        num_iterations: Number of times to repeat the click sequence.
                        If None, random between 60-100.
        delay_between_clicks: Minimum delay between click sequences (default 2 seconds).
        delay_variance: Additional random delay up to this value (default 8 seconds, total 2-10s).
        primary_x: X coordinate for primary click area.
        primary_y: Y coordinate for primary click area.
        imprecision: Pixel imprecision for primary clicks.
        left_coords: Coordinates for left click option.
        right_coords: Coordinates for right click option.
        left_weight: Probability weight for left click. If None, random between 0.60-0.80.
    
    Returns:
        List of results from each iteration.
    """
    # Random number of iterations between 60-100 if not specified
    if num_iterations is None:
        num_iterations = random.randint(60, 100)
    
    # Random left_weight between 60-80% if not specified
    if left_weight is None:
        left_weight = random.uniform(0.60, 0.80)
    
    print("=" * 60)
    print(f"STARTING CLICK SEQUENCE LOOP - {num_iterations} iterations")
    print("Press Ctrl+C or ESC to abort at any time")
    print("=" * 60)
    
    results_list = []
    
    try:
        for i in range(num_iterations):
            print(f"\n{'='*20} Iteration {i+1}/{num_iterations} {'='*20}")
            
            result = run_click_sequence(
                primary_x=primary_x,
                primary_y=primary_y,
                imprecision=imprecision,
                left_coords=left_coords,
                right_coords=right_coords,
                left_weight=left_weight,
                delay_after_primary=1.0
            )
            results_list.append(result)
            
            # Calculate delay for next iteration (2-10 seconds)
            if i < num_iterations - 1:
                delay = delay_between_clicks + random.uniform(0, delay_variance)
                print(f"Waiting {delay:.1f} seconds before next iteration...")
                time.sleep(delay)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("ABORTED BY USER - Stopping click sequence")
        print("=" * 60)
        # Return partial results
        left_count = sum(1 for r in results_list if r.get("final_click_side") == "left")
        right_count = sum(1 for r in results_list if r.get("final_click_side") == "right")
        print(f"\nPartial Summary: Left clicks: {left_count}, Right clicks: {right_count}")
        print(f"Completed {len(results_list)} out of {num_iterations} iterations")
        return results_list
    
    print("\n" + "=" * 60)
    print(f"LOOP COMPLETED - {num_iterations} iterations done!")
    print("=" * 60)
    
    # Summary
    left_count = sum(1 for r in results_list if r.get("final_click_side") == "left")
    right_count = sum(1 for r in results_list if r.get("final_click_side") == "right")
    print(f"\nSummary: Left clicks: {left_count}, Right clicks: {right_count}")
    
    return results_list


if __name__ == "__main__":
    # Run the click sequence loop with random iterations (60-100)
    # Random left/right weight (60-80% left)
    # Delay between clicks: 2-10 seconds
    results = run_click_sequence_loop(
        num_iterations=None,  # Will be random between 60-100
        left_weight=None,  # Will be random between 60-80%
        delay_between_clicks=2.0,
        delay_variance=8.0,  # Total delay: 2-10 seconds
        primary_x=1100,
        primary_y=900,
        imprecision=50,
        left_coords=(1050, 1040),
        right_coords=(1250, 1040)
    )
    
    print(f"\nFinal Results: {results}")
