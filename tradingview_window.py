from playwright.sync_api import sync_playwright
import os

# --- Configuration ---
# Path where Playwright will store your cookies and session data.
USER_DATA_DIR = os.path.join(os.getcwd(), 'playwright_user_data')
TARGET_URL = 'https://www.tradingview.com/chart/'
SCREENSHOT_PATH = 'tradingview_logged_in_screenshot.png'
# ---------------------

def run_persistent_script():
    """
    Launches a persistent browser context to maintain a logged-in user session.
    The first run requires manual login; subsequent runs will reuse the session.
    """
    print("Starting Playwright Persistent Session script...")
    
    # Check if the user data directory exists
    if not os.path.isdir(USER_DATA_DIR):
        print(f"\n--- IMPORTANT: First Run Detected ---")
        print(f"Directory '{USER_DATA_DIR}' created. Please log in manually.")
        print("--------------------------------------\n")
    else:
        print(f"\n--- Reusing existing session from '{USER_DATA_DIR}' ---")
        print("You should be logged in automatically.")
        print("------------------------------------------------------\n")
    
    with sync_playwright() as p:
        # Launch persistent context instead of a standard browser
        # This is the key to reusing the session data (cookies, local storage)
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            slow_mo=100  # Slower speed for easier observation during login
        )
        
        # We only need the first page in the context
        page = context.pages[0] if context.pages else context.new_page()

        # 1. Navigate to the TradingView chart page
        print(f'Navigating to {TARGET_URL}...')
        page.goto(TARGET_URL)
        
        # 2. Wait for a common element on the page to ensure it's loaded
        # Use a generic, robust selector for TradingView charts (e.g., the main chart container)
        # This is a safe selector for the main chart content frame.
        page.wait_for_selector('.chart-widget-popup', state='hidden', timeout=30000)
        print(f"Page title: {page.title()}")
        
        # Optional: Add a short, explicit wait after the page is fully loaded
        page.wait_for_timeout(2000)

        # 3. Take a screenshot of the logged-in view
        page.screenshot(path=SCREENSHOT_PATH, full_page=True)
        print(f'Screenshot saved as {SCREENSHOT_PATH}')

        # Close the context, which also closes the browser window
        context.close()

if __name__ == "__main__":
    try:
        run_persistent_script()
        print('Script finished successfully.')
    except Exception as e:
        print(f'An error occurred: {e}')