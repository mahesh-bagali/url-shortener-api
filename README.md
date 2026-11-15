# URL Shortener API

A REST API foundation for a URL shortener, built with Python and FastAPI. The current implementation validates submitted HTTP/HTTPS URLs and assigns each accepted URL a unique, random, URL-friendly short code. Codes are kept in process memory only and are lost when the application restarts.

## Requirements

- Python 3.10 or newer
- pip

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run the commands using `.venv\Scripts\python.exe` directly instead.

## Run locally

```powershell
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive API documentation is available at `/docs`.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Welcome message |
| GET | `/health` | Basic process health response |
| POST | `/urls` | Validate a URL and assign a unique short code |

Example request:

```json
{
  "original_url": "https://www.example.com/products"
}
```

The response includes `message`, `original_url`, and a randomly generated seven-character `short_code`. Codes use letters and digits and are unique for the lifetime of the running process.

## Tests

Run the short-code unit tests with:

```powershell
py -m unittest tests.test_short_codes -v
```

## Configuration

Local environment variables can be placed in a root `.env` file. It is excluded from Git; do not commit credentials or other secrets. The settings foundation is in `app/config.py`.

## Project layout

```text
app/
  database/       Database package foundation
  models/         Data model package foundation
  routers/        API route handlers
  schemas/        Pydantic request and response schemas
  services/       Application services, including short-code generation
  config.py       Environment-backed settings
  main.py         FastAPI application and general endpoints
main.py           Uvicorn import entry point
requirements.txt  Python dependencies
tests/            Unit tests
```

Database integration, redirects, authentication, and analytics are not implemented yet.
