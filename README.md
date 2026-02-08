# Flight Reservation Service

A RESTful backend API built with **Django REST Framework** for managing flight reservations. The service allows users to search for available flights by route and date, and create reservations with passenger information. It features token-based authentication, input validation, and full CRUD operations for flights, passengers, and reservations.

## Tech Stack

- **Python 3.10+**
- **Django 3.2** - Web framework
- **Django REST Framework** - RESTful API toolkit
- **PostgreSQL** - Database (SQLite supported for testing)
- **Token Authentication** - DRF token-based auth

## Project Structure

```
flight-services/
├── flightApp/                  # Main application
│   ├── models.py               # Flight, Passanger, Reservation models
│   ├── views.py                # API viewsets and custom endpoints
│   ├── serializers.py          # DRF serializers with validation
│   ├── tests.py                # Unit tests
│   └── migrations/             # Database migrations
├── flightServices/             # Django project configuration
│   ├── settings.py             # Settings (DB, auth, middleware)
│   ├── urls.py                 # URL routing
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point
├── manage.py                   # Django CLI utility
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Multi-container setup (app + PostgreSQL)
└── .github/workflows/ci.yml   # GitHub Actions CI pipeline
```

## Data Models

| Model | Fields | Description |
|-------|--------|-------------|
| **Flight** | `flightNumber`, `operatingAirLines`, `departureCity`, `arrivalCity`, `dateOfDeparture`, `estimatedTimeOfDeparture` | Stores flight information |
| **Passanger** | `firstName`, `lastName`, `middleName`, `email`, `phone` | Stores passenger details |
| **Reservation** | `flight` (FK), `passanger` (OneToOne) | Links a passenger to a flight |

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api-token-auth/` | Obtain auth token (username + password) |

### Flights (Token Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/flightServices/flights/` | List all flights |
| POST | `/flightServices/flights/` | Create a flight |
| GET | `/flightServices/flights/{id}/` | Get flight details |
| PUT | `/flightServices/flights/{id}/` | Update a flight |
| DELETE | `/flightServices/flights/{id}/` | Delete a flight |

### Passengers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/flightServices/passanger/` | List all passengers |
| POST | `/flightServices/passanger/` | Create a passenger |
| GET | `/flightServices/passanger/{id}/` | Get passenger details |
| PUT | `/flightServices/passanger/{id}/` | Update a passenger |
| DELETE | `/flightServices/passanger/{id}/` | Delete a passenger |

### Reservations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/flightServices/reservation/` | List all reservations |
| POST | `/flightServices/reservation/` | Create a reservation |
| GET | `/flightServices/reservation/{id}/` | Get reservation details |
| PUT | `/flightServices/reservation/{id}/` | Update a reservation |
| DELETE | `/flightServices/reservation/{id}/` | Delete a reservation |

### Custom Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/flightServices/findFlights/` | Search flights by `departureCity`, `arrivalCity`, `dateOfDeparture` |
| POST | `/flightServices/saveReservation/` | Create reservation with passenger info and `flightId` |

#### Example: Search Flights
```bash
curl -X POST http://localhost:8000/flightServices/findFlights/ \
  -H "Content-Type: application/json" \
  -d '{"departureCity": "NYC", "arrivalCity": "LAX", "dateOfDeparture": "2024-03-15"}'
```

#### Example: Create Reservation
```bash
curl -X POST http://localhost:8000/flightServices/saveReservation/ \
  -H "Content-Type: application/json" \
  -d '{
    "flightId": 1,
    "firstName": "John",
    "lastName": "Doe",
    "middleName": "Q",
    "email": "john@example.com",
    "phone": "555-1234"
  }'
```

## Local Development Setup

### Prerequisites
- Python 3.10+
- PostgreSQL Server
- pip

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/govicsit/flight-services.git
   cd flight-services
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE flightdb;
   ```
   Update database credentials in `flightServices/settings.py` if needed (default: `postgres`/`postgres`).

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (for admin access and token generation)
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://localhost:8000/flightServices/`.

## Running with Docker

### Using Docker Compose (recommended)
```bash
docker-compose up --build
```
This starts both the Django app and a PostgreSQL database. The API will be available at `http://localhost:8000/`.

### Using Docker only
```bash
docker build -t flight-services .
docker run -p 8000:8000 flight-services
```
> Note: When running without Docker Compose, you need to provide your own PostgreSQL instance and configure the connection via environment variables (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).

## Running Tests

### Run all tests
```bash
python manage.py test
```

### Run with verbose output
```bash
python manage.py test -v 2
```

### Run a specific test class
```bash
python manage.py test flightApp.tests.FlightModelTest
```

Tests use an in-memory **SQLite** database by default (configured automatically for the test environment), so PostgreSQL is not required to run the test suite.

## CI/CD

This project includes a GitHub Actions pipeline (`.github/workflows/ci.yml`) that runs on every push and pull request to `main`:

- Installs Python dependencies
- Runs the full test suite
- Runs linting checks
