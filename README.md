# URL Shortener API

A backend URL shortening service built with **FastAPI, PostgreSQL, Redis, and Docker**. It allows authenticated users to create and manage short URLs, redirect visitors to original destinations, and track URL engagement through click analytics.

## Features

- **URL Shortening** – Generate unique short codes for long URLs.
- **User Authentication** – Secure registration and login using JWT authentication.
- **URL Management** – Create, retrieve, update, and delete shortened URLs.
- **Ownership Protection** – Users can manage only their own URLs.
- **Redis Caching** – Cache URL mappings to improve redirect performance.
- **Click Tracking** – Track URL visits and increment click counts.
- **Analytics** – Retrieve URL engagement statistics.
- **Rate Limiting** – Protect API endpoints against excessive requests.
- **Input Validation** – Validate request data using Pydantic.
- **Automated Testing** – Unit tests and integration tests using pytest.
- **Docker Support** – Containerized application with Docker Compose and Redis.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| FastAPI | REST API framework |
| Pydantic | Data validation and settings |
| PostgreSQL | Relational database |
| SQLModel | Database ORM |
| Redis | Caching and rate limiting |
| JWT | Authentication |
| Pytest | Unit and integration testing |
| Docker | Application containerization |
| Docker Compose | Multi-container orchestration |

## Architecture

```text
                 Client
                   |
                   v
             FastAPI API
                   |
          +--------+--------+
          |        |        |
          v        v        v
      PostgreSQL  Redis   Security
          |        |        |
          v        v        v
       URL Data   Cache   JWT / Rate
       User Data          Limiting
          |
          v
      Analytics
```

## Project Structure

```text
url-shortener-api/
│
├── app/
│   ├── database/
│   │   ├── redis.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── urls.py
│   │   └── users.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── urls.py
│   │   └── analytics.py
│   │
│   ├── schemas/
│   │   ├── urls.py
│   │   └── users.py
│   │
│   ├── services/
│   │   ├── cache.py
│   │   ├── rate_limiter.py
│   │   ├── security.py
│   │   └── short_codes.py
│   │
│   ├── config.py
│   └── main.py
│
├── tests/
├── .dockerignore
├── .gitignore
├── Dockerfile
├── compose.yaml
├── main.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

Install the following:

- Python 3.14+
- PostgreSQL
- Redis
- Git
- Docker Desktop (for containerized execution)

### 1. Clone the repository

```bash
git clone https://github.com/mahesh-bagali/url-shortener-api.git
cd url-shortener-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure your local PostgreSQL, Redis, and JWT settings.

Never commit your actual `.env` file or credentials to GitHub.

### 5. Start the application

```bash
uvicorn main:app --reload --port 8001
```

The API will be available at:

```text
http://127.0.0.1:8001
```

## API Documentation

FastAPI automatically generates interactive API documentation.

| Documentation | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8001/docs |
| ReDoc | http://127.0.0.1:8001/redoc |
| Health Check | http://127.0.0.1:8001/health |

Use Swagger UI to explore and test the available endpoints.

## Running with Docker Compose

Make sure Docker Desktop is running.

Build and start the API and Redis services:

```bash
docker compose up -d --build
```

Check running containers:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f api
```

Stop the services:

```bash
docker compose down
```

The API is exposed on port `8001`, while Redis is available internally to the API service.

**Note:** PostgreSQL is configured as an external service in the current Docker Compose setup.

## Running Tests

Run the complete test suite:

```bash
python -m pytest -v
```

The project has successfully passed **48 tests**, covering unit and integration scenarios.

Test coverage includes:

- Short-code generation
- URL validation
- Authentication
- URL ownership
- Redis caching
- Click tracking
- Analytics
- Security and rate limiting

## Future Improvements

- Custom short URLs
- Expiration dates for shortened URLs
- QR code generation
- Advanced analytics
- CI/CD automation

## Author

**Mahesh Bagali**

GitHub: [@mahesh-bagali](https://github.com/mahesh-bagali)

## License

This project is currently shared without a specified open-source license.
