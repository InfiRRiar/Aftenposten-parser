# Newspaper Parser

Automated parser for archived newspaper issues. The script searches the
Aftenposten e-newspaper website for every date in a configured range, downloads
the matching PDF issue, and uploads it to Yandex Disk.

The current parser target is hard-coded in [`src/main.py`](src/main.py):

```text
https://e-avis.aftenposten.no/search?title=611
```

Downloaded files are uploaded to Yandex Disk as:

```text
newspapers/YYYY-MM-DD.pdf
```

## How It Works

1. Reads the date range and tokens from `.env`.
2. Loads authenticated browser cookies from `cookies.json`.
3. Opens the newspaper archive with Playwright.
4. Finds the issue for each date in the configured range.
5. Requests a PDF download token from Textalk.
6. Streams the PDF directly to Yandex Disk.

## Requirements

- Docker
- Make
- A valid account for the newspaper website
- A Yandex Disk OAuth token
- The Textalk/newspaper authentication tokens listed below

For local helper scripts, install dependencies with `uv`:

```bash
uv sync
uv run playwright install chromium
```

## Configuration

Create a local environment file:

```bash
cp .env-example .env
```

Fill in the values.

Configuration fields:

- `start_date`: first issue date to process, in `YYYY-MM-DD` format.
- `end_date`: last issue date to process, in `YYYY-MM-DD` format. The range is inclusive.
- `yd_token`: Yandex Disk OAuth token.
- `auth_token`: newspaper/PDF download token.
- `auth_bearer`: value for the `authorization` request header.
- `textalk`: value for the `x-textalk-content-client-authorize` request header.

Token extraction steps are still project-specific and intentionally left as a
TODO. Add the exact browser/devtools flow here once it is documented.

## Save Authenticated Cookies

The parser needs a Playwright storage state file named `cookies.json` in the
repository root. This file should be created while you are logged in to the
newspaper website.

Run:

```bash
uv run python utils.py/get_cookies.py
```

The script opens a browser window. Log in to the newspaper website, then return
to the terminal and press Enter. This saves `cookies.json`.

Never commit `.env` or `cookies.json`; both contain private credentials.

## Run With Docker

Build the image:

```bash
make build
```

Run the parser:

```bash
make run
```

Or build and run in one command:

```bash
make up
```

As an alternative version, just type Docker commands manually: 

```bash
docker build -t news .
docker run --network host -d news
```

The container runs in the background. To inspect it:

```bash
docker ps
docker logs -f <container_id>
```

## Project Structure

```text
.
├── src/
│   ├── main.py          # parser orchestration and PDF download flow
│   └── disk_loader.py   # Yandex Disk upload client
├── utils.py/
│   └── get_cookies.py   # helper for saving authenticated browser state
├── settings.py          # environment configuration
├── Dockerfile           # container image definition
├── Makefile             # build/run shortcuts
└── .env-example         # configuration template
```

## Notes

- The parser currently uses 3 concurrent workers.
- The date range is inclusive.
- If no issue exists for a date, that date is skipped.
- The newspaper URL and title id are currently hard-coded in `src/main.py`.
