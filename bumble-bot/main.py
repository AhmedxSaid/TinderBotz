# =============================================================================
# THIS BOT IS FOR EDUCATIONAL PURPOSES ONLY.
# Automating Bumble violates their Terms of Service and may result in account ban.
# Use at your own risk. The author assumes no liability.
# =============================================================================

"""Entry point for the Bumble automation bot.

Usage
-----
Normal mode (auto-swipe)::

    python main.py --config config.json

Training mode (collect labelled data)::

    python main.py --config config.json --train

Train model after collecting enough data::

    python main.py --config config.json --train-model

Flags
-----
--config   Path to the JSON configuration file (default: config.json).
--train    Manually label profiles and save photos for ML training.
--train-model   Train the CNN on previously collected data.
"""

from __future__ import annotations

import argparse
import glob
import logging
import os
import random
import signal
import sys
import time
from typing import Optional

from bot.browser import BumbleBrowser
from bot.classifier import PreferenceLearner
from bot.config import Config
from bot.decision import DecisionEngine
from bot.utils import ensure_dirs, random_delay, setup_logging
from bot.vision import ProfileAnalyzer
from click_sequence import run_click_sequence

logger = logging.getLogger("bumble_bot")


class BumbleBot:
    """Orchestrates login, swiping, breaks, and optional training mode.

    Args:
        config_path: Path to the JSON configuration file.
    """

    def __init__(self, config_path: str = "config.json") -> None:
        self._config = Config(config_path)

        # Set up logging first
        log_cfg = self._config.get_section("logging")
        setup_logging(
            log_file=log_cfg.get("log_file", "data/logs/bumble_bot.log"),
            log_level=log_cfg.get("log_level", "INFO"),
        )

        # Ensure data directories exist
        ensure_dirs(
            "data/logs",
            "data/training/like",
            "data/training/dislike",
            "data/models",
        )

        self._browser: Optional[BumbleBrowser] = None
        self._analyzer: Optional[ProfileAnalyzer] = None
        self._learner: Optional[PreferenceLearner] = None
        self._engine: Optional[DecisionEngine] = None

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _init_components(self) -> None:
        """Create all child components."""
        logger.info("Initializing components...")

        self._browser = BumbleBrowser(self._config)
        self._analyzer = ProfileAnalyzer()
        self._learner = PreferenceLearner()
        self._engine = DecisionEngine(self._config, self._learner)

    # ------------------------------------------------------------------
    # Login flow
    # ------------------------------------------------------------------

    def login(self) -> bool:
        """Create a browser instance and attempt to log in.

        Returns:
            True if login succeeded (or session already active), else False.
        """
        self._browser = BumbleBrowser(self._config)

        # Check if we should use existing session (already logged in)
        use_existing = self._config.get("bumble", "use_existing_session", True)

        
        if use_existing:
            logger.info("Using existing browser session (skipping login)")
            # Navigate to Bumble to verify session is valid
            if self._browser:
                self._browser.driver.get("https://bumble.com/app")  # type: ignore[union-attr]
                time.sleep(3)
                # Verify we're actually logged in by checking for profile cards
                return self._browser._is_logged_in()  # type: ignore[union-attr]
            return True
        
        method = self._config.get("bumble", "login_method", "facebook")
        logger.info("Login method: %s", method)

        if method == "facebook":
            email = self._config.get("bumble", "facebook_email", "")
            password = self._config.get("bumble", "facebook_password", "")
            if not email or not password:
                logger.error("Facebook credentials not configured.")
                return False
            return self._browser.login_facebook(email, password)  # type: ignore[union-attr]

        elif method == "phone":
            phone = self._config.get("bumble", "phone_number", "")
            if not phone:
                logger.error("Phone number not configured.")
                return False
            return self._browser.login_phone(phone)  # type: ignore[union-attr]

        else:
            logger.error("Unknown login method: %s", method)
            return False

    # ------------------------------------------------------------------
    # Main swiping loop
    # ------------------------------------------------------------------

    def run_click_sequence_action(self) -> None:
        """Run the automated click sequence with imprecision and weighted clicks.
        
        This performs:
        1. Primary clicks at (1100, 900) with ±50 pixel imprecision (2-4 times)
        2. Weighted final click at left (1050, 1040) or right (1250, 1040)
        """
        logger.info("Running click sequence action...")
        try:
            result = run_click_sequence(
                primary_x=1100,
                primary_y=900,
                imprecision=50,
                left_coords=(1050, 1040),
                right_coords=(1250, 1040),
                left_weight=0.65,  # 65% chance for left, 35% for right
                delay_after_primary=1.0
            )
            logger.info(f"Click sequence completed: {result}")
        except Exception as e:
            logger.error(f"Click sequence failed: {e}")

    def run(self) -> None:
        """Main bot loop: login then process profiles until limits are hit.

        Respects ``max_swipes_per_session``, break schedules, and
        'no more profiles' detection.
        """
        self._init_components()

        if not self.login():
            logger.error("Login failed; exiting.")
            return

        # Run click sequence action after login
        self.run_click_sequence_action()

        swipe_cfg = self._config.get_section("swipe_settings")
        stealth_cfg = self._config.get_section("stealth")

        # Number of consecutive non-likes (i.e. people we weren't attracted to)
        # before we take a break. Reset after each break.
        consecutive_passes = 0
        passes_before_break = swipe_cfg.get("passes_before_break", 20)

        # Current swipe count in this session
        swipes_this_session = 0
        max_swipes = swipe_cfg.get("max_swipes_per_session", 100)

        # Time when the next break is allowed to start
        next_break_time = time.time() + swipe_cfg.get("min_swipes_before_break", 20)

        # How long to wait before we're allowed to swipe again after a break
        break_duration = swipe_cfg.get("break_duration", 30)

        # Whether the user wants us to auto-fill the "They added you" prompt
        auto_fill_yes = self._config.get("bumble", "auto_fill_yes", True)

        while True:
            # ------------------------------------------------------------------
            # Check session limits
            # ------------------------------------------------------------------
            if swipes_this_session >= max_swipes:
                logger.info(
                    "Reached max swipes per session (%d). Ending session.",
                    max_swipes,
                )
                break

            # ------------------------------------------------------------------
            # Check if we need a break (but only after minimum swipe count)
            # ------------------------------------------------------------------
            if (
                consecutive_passes >= passes_before_break
                and time.time() >= next_break_time
            ):
                logger.info(
                    "Taking a break after %d consecutive passes (%d swipes this session).",
                    consecutive_passes,
                    swipes_this_session,
                )
                # Close the browser to appear offline
                self._browser.quit()  # type: ignore[union-attr]
                self._browser = None

                # Sleep for break_duration seconds
                time.sleep(break_duration)

                # Reset counters
                consecutive_passes = 0
                next_break_time = time.time() + swipe_cfg.get(
                    "min_swipes_before_break", 20
                )

                # Restart the browser
                logger.info("Resuming after break.")
                self._browser = BumbleBrowser(self._config)
                self._browser.driver.get("https://bumble.com/app")  # type: ignore[union-attr]
                time.sleep(3)
                if not self._browser._is_logged_in():  # type: ignore[union-attr]
                    logger.error("Login failed after break; exiting.")
                    break
                self._handle_match_popup()

            # ------------------------------------------------------------------
            # Main action: try to swipe the current card
            # ------------------------------------------------------------------

            # Wait for page to settle
            time.sleep(1)

            # Handle the "You both liked each other" popup (premium feature)
            self._handle_match_popup()

            # Handle the "They Added You" popup if it appears
            if auto_fill_yes:
                self._handle_they_added_you_popup()

            # Detect "no more profiles" early
            if self._browser.no_more_profiles():  # type: ignore[union-attr]
                logger.info("No more profiles to swipe. Ending session.")
                break

            # Capture screenshot for analysis
            img = self._browser.get_current_profile_screenshot()  # type: ignore[union-attr]
            if not img:
                logger.warning("Failed to capture profile screenshot.")
                continue

            # Decide whether to swipe right (like) or left (pass)
            decision = self._engine.decide(img, self._analyzer)  # type: ignore[arg-type]

            if decision == "like":
                logger.info("Decision: LIKE")
                self._browser.like()  # type: ignore[union-attr]
                swipes_this_session += 1

            elif decision == "dislike":
                logger.info("Decision: DISLIKE")
                self._browser.dislike()  # type: ignore[union-attr]
                swipes_this_session += 1
                consecutive_passes += 1

            else:
                # Save the screenshot for later labeling
                timestamp = int(time.time() * 1000)
                path = f"data/training/unknown/{timestamp}.jpg"
                self._browser.save_current_profile(path)  # type: ignore[union-attr]
                logger.warning("Decision: UNKNOWN - Saved to %s", path)
                # Treat as dislike to keep swiping
                self._browser.dislike()  # type: ignore[union-attr]
                swipes_this_session += 1
                consecutive_passes += 1

            # Small random delay to appear more human
            random_delay()

    def _handle_match_popup(self) -> None:
        """Check for a match popup and dismiss it if present."""
        try:
            self._browser.handle_match_popup()  # type: ignore[union-attr]
        except Exception as e:
            logger.debug("No match popup found (expected): %s", e)

    def _handle_they_added_you_popup(self) -> None:
        """Check for a 'They Added You' popup and click 'Yes' if found."""
        try:
            self._browser.handle_they_added_you_popup()  # type: ignore[union-attr]
        except Exception as e:
            logger.debug("No 'They Added You' popup found (expected): %s", e)


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Bumble Bot")
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to the JSON configuration file.",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Manually label profiles and save photos for ML training.",
    )
    parser.add_argument(
        "--train-model",
        action="store_true",
        help="Train the CNN on previously collected data.",
    )

    args = parser.parse_args()

    # Register the Ctrl+C signal handler for graceful shutdown
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    if args.train_model:
        logger.info("Training model on collected data...")
        learner = PreferenceLearner()
        learner.train()
        logger.info("Training complete!")
        return

    bot = BumbleBot(args.config)

    if args.train:
        logger.info("Starting bot in TRAINING mode...")
    else:
        logger.info("Starting bot in AUTO mode...")

    bot.run()
    logger.info("Bot shutdown complete.")


if __name__ == "__main__":
    main()
