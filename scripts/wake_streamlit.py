import sys
import time

from playwright.sync_api import sync_playwright


APP_URL = "https://arthamitra.streamlit.app/"
HEALTH_URL = "https://arthamitra.streamlit.app/_stcore/health"
WAKE_BUTTON_TEXT = "Yes, get this app back up!"

MAX_WAIT_SECONDS = 300
CHECK_INTERVAL_SECONDS = 10


def backend_is_healthy(page) -> bool:
    try:
        response = page.request.get(
            HEALTH_URL,
            timeout=20_000,
            fail_on_status_code=False,
        )

        print(
            f"Health check: status={response.status}, "
            f"body={response.text()[:100]!r}"
        )

        return response.status == 200

    except Exception as error:
        print(f"Health check request failed: {error}")
        return False


def wake_streamlit_app() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={"width": 1440, "height": 900}
        )

        try:
            print(f"Opening {APP_URL}")

            page.goto(
                APP_URL,
                wait_until="domcontentloaded",
                timeout=120_000,
            )

            page.wait_for_timeout(5_000)

            # Case 1: Backend is already running.
            if backend_is_healthy(page):
                print("ArthaMitra is already awake and healthy.")
                return

            # Case 2: App is sleeping, so click the wake button.
            wake_button = page.get_by_role(
                "button",
                name=WAKE_BUTTON_TEXT,
                exact=True,
            )

            if wake_button.count() > 0 and wake_button.first.is_visible():
                print("Sleeping app detected. Clicking wake-up button.")

                wake_button.first.click(timeout=30_000)

            else:
                print(
                    "Wake button not visible. "
                    "The app may already be booting."
                )

            # Wait until the Streamlit backend becomes healthy.
            deadline = time.time() + MAX_WAIT_SECONDS

            while time.time() < deadline:
                if backend_is_healthy(page):
                    print("ArthaMitra is awake and healthy.")
                    return

                print(
                    f"Backend not ready. Retrying in "
                    f"{CHECK_INTERVAL_SECONDS} seconds..."
                )

                page.wait_for_timeout(
                    CHECK_INTERVAL_SECONDS * 1000
                )

            raise RuntimeError(
                f"ArthaMitra did not become healthy within "
                f"{MAX_WAIT_SECONDS} seconds."
            )

        finally:
            browser.close()


if __name__ == "__main__":
    try:
        wake_streamlit_app()

    except Exception as error:
        print(f"Wake-up failed: {error}", file=sys.stderr)
        sys.exit(1)
