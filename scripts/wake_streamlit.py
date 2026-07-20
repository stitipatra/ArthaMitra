import sys
import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


APP_URL = "https://arthamitra.streamlit.app/"
APP_TEXT = "ArthaMitra"


def wake_app() -> None:
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
            page.goto(APP_URL, wait_until="domcontentloaded", timeout=120_000)
            page.wait_for_timeout(5_000)

            wake_button = page.get_by_text(
                "Yes, get this app back up!",
                exact=False,
            )

            if wake_button.count() > 0 and wake_button.first.is_visible():
                print("Sleeping app detected. Clicking wake-up button.")
                wake_button.first.click()
            else:
                print("Wake-up button not found. App may already be running.")

            # Wait for Streamlit to boot.
            deadline = time.time() + 180

            while time.time() < deadline:
                page.wait_for_timeout(5_000)

                body_text = page.locator("body").inner_text()

                if APP_TEXT.lower() in body_text.lower():
                    print("ArthaMitra is awake and loaded.")
                    return

                print("App is still starting...")

            raise RuntimeError(
                "App did not finish loading within three minutes.")

        except PlaywrightTimeoutError as error:
            raise RuntimeError(
                "Timed out while opening or waking the app.") from error

        finally:
            browser.close()


if __name__ == "__main__":
    try:
        wake_app()
    except Exception as error:
        print(f"Wake-up failed: {error}", file=sys.stderr)
        sys.exit(1)
