from pathlib import Path

from playwright.sync_api import sync_playwright

AUTH_URL = "https://www.aftenposten.no/"
STORAGE_STATE_PATH = Path("cookies.json")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(AUTH_URL)
        print("Log in in the opened browser window, then press Enter here.")
        input()

        context.storage_state(path=STORAGE_STATE_PATH)
        browser.close()

    print(f"Saved authenticated browser state to {STORAGE_STATE_PATH}")


if __name__ == "__main__":
    main()
