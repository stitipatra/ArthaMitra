import sys
import time

from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)


APP_URL = "https://arthamitra.streamlit.app/"
WAKE_BUTTON_TEXT = "Yes, get this app back up!"
APP_READY_TEXT = "ArthaMitra"

MAX_WAIT_SECONDS = 240
CHECK_INTERVAL_SECONDS = 5


def app_is_ready(page) -> bool:
    try:
        body_text = page.locator("body").inner_text(timeout=10_000)
        return APP_READY_TEXT.lower() in body_text.lower()
    except PlaywrightTimeoutError:
        return False


def wake_streamlit_app() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/130 Safari/537.36"
            ),
        )

        try:
            print(f"Opening {APP_URL}")

            page.goto(
                APP_URL,
                wait_until="domcontentloaded",
                timeout=120_000,
            )

            page.wait_for_timeout(5_000)

            # Case 1: App is already awake.
            if app_is_ready(page):
                print("ArthaMitra is already awake.")
                return

            # Case 2: App is sleeping.
            wake_button = page.get_by_role(
                "button",
                name=WAKE_BUTTON_TEXT,
                exact=False,
            )

            if wake_button.count() > 0 and wake_button.first.is_visible():
                print("Sleeping app detected. Clicking wake-up button.")
                wake_button.first.click(timeout=30_000)
            else:
                print(
                    "Wake-up button not found. "
                    "The app may still be loading, so waiting..."
                )

            deadline = time.time() + MAX_WAIT_SECONDS

            while time.time() < deadline:
                page.wait_for_timeout(CHECK_INTERVAL_SECONDS * 1000)

                if app_is_ready(page):
                    print("ArthaMitra is awake and fully loaded.")
                    return

                print("Waiting for ArthaMitra to load...")

            raise RuntimeError(
                f"ArthaMitra did not load within {MAX_WAIT_SECONDS} seconds."
            )

        except PlaywrightTimeoutError as error:
            raise RuntimeError(
                "Timed out while opening or checking ArthaMitra."
            ) from error

        finally:
            browser.close()


if __name__ == "__main__":
    try:
        wake_streamlit_app()
    except Exception as error:
        print(f"Wake-up check failed: {error}", file=sys.stderr)
        sys.exit(1)
