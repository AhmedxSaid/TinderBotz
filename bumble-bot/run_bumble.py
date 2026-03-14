"""Standalone script to open Chrome, navigate to Bumble, and run click sequence."""

import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from click_sequence import run_click_sequence


def setup_chrome():
    """Setup Chrome with stealth options."""
    options = Options()
    
    # Stealth options to avoid detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    
    # User agent to appear more human
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Disable webdriver flag
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Install and setup Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Execute scripts to hide webdriver
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    return driver


def main():
    """Main function to open Bumble and run click sequence."""
    print("Opening Chrome...")
    driver = setup_chrome()
    
    print("Navigating to Bumble...")
    driver.get("https://bumble.com/app")
    
    # Wait for page to load
    print("Waiting for page to load...")
    time.sleep(5)
    
    print("\n" + "="*50)
    print("Chrome is now open at bumble.com")
    print("="*50)
    print("\nNOTE: Please log in to Bumble manually if not already logged in.")
    print("The click sequence will start in 10 seconds...")
    print("="*50 + "\n")
    
    # Give user time to log in
    time.sleep(10)
    
    # Run the click sequence
    print("Starting click sequence...")
    result = run_click_sequence(
        primary_x=1100,
        primary_y=900,
        imprecision=50,
        left_coords=(1050, 1040),
        right_coords=(1250, 1040),
        left_weight=0.65,
        delay_after_primary=1.0
    )
    
    print(f"\nClick sequence result: {result}")
    print("\nKeeping browser open for 60 seconds...")
    time.sleep(60)
    
    print("Closing browser...")
    driver.quit()
    print("Done!")


if __name__ == "__main__":
    main()
