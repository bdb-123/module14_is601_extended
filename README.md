# FastAPI Calculator & CarCompare Application

A full-stack web application built with FastAPI, PostgreSQL, and Docker featuring:
- **Calculator API** - Perform arithmetic operations with user authentication
- **CarCompare** - Compare car listings across multiple marketplaces (Final Project)

---

## 📋 Table of Contents

- [Features](#features)
- [Final Project: CarCompare](#final-project-carcompare)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running Locally](#running-locally)
  - [Running with Docker](#running-with-docker)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)

---

## ✨ Features

### Calculator API
- User authentication with JWT tokens
- Perform addition, subtraction, multiplication, division
- Calculation history tracking
- RESTful API endpoints

### CarCompare (Final Project)
- **Car Management** - Add, view, update, delete cars in your garage
- **Listing Tracking** - Track car listings from multiple sources (Autotrader, Craigslist, etc.)
- **Price Comparison** - Automatically compute statistics (min/max/avg prices, best deal)
- **VIN Decoder** - Decode VIN numbers using NHTSA API to auto-populate car details
- **Ownership Enforcement** - Multi-layer security ensuring users only access their own data
- **Cascade Deletes** - Automatic cleanup of related data

---

## 🚗 Final Project: CarCompare

**CarCompare** is a car marketplace comparison tool that helps users track and compare listings for their cars across multiple platforms.

### Problem Solved
When selling a car, it's tedious to track listings across Autotrader, Craigslist, Facebook Marketplace, eBay Motors, etc. CarCompare centralizes all your listings and provides instant price comparisons to help you:
- Find the best deal (lowest price per mile)
- Track average market prices
- Monitor listing performance across platforms
- Make data-driven pricing decisions

### Key Features
1. **Car Garage** - Manage multiple cars with year, make, model, trim, and VIN
2. **Multi-Source Listings** - Track listings from any marketplace
3. **Smart Statistics** - Automatic calculation of:
   - Min/Max/Average prices
   - Average price per mile
   - Best deal identification
4. **VIN Decoder Integration** - Auto-populate car details from VIN using NHTSA API
5. **Data Ownership** - Each user's data is completely isolated with ownership verification

### Technical Highlights
- **SQLAlchemy Models** with proper relationships and cascade deletes
- **Pydantic Validation** with custom validators for VIN, price, mileage, URLs
- **RESTful API Design** following BREAD pattern (Browse, Read, Edit, Add, Delete)
- **External API Integration** with NHTSA VIN decoder
- **Comprehensive Testing** - 39 integration tests with 75%+ model coverage
- **Type Safety** - Full type hints throughout the codebase

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Authentication**: JWT (OAuth2PasswordBearer)
- **Caching**: Redis
- **Testing**: pytest, pytest-cov
- **Containerization**: Docker & Docker Compose
- **Frontend**: Jinja2 Templates, Vanilla JavaScript

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+
- Redis (for session management)
- Docker & Docker Compose (for containerized deployment)

### Running Locally

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd module14_is601_extended
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/calculator_db
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Start PostgreSQL and Redis**
   ```bash
   # Using Homebrew (Mac)
   brew services start postgresql
   brew services start redis
   
   # Or using Docker
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:14
   docker run -d -p 6379:6379 redis:7
   ```

6. **Initialize the database**
   ```bash
   python -c "from app.database_init import init_db; init_db()"
   ```

7. **Run database migrations (Alembic)**
   
   Apply migrations to create Car and Listing tables:
   ```bash
   alembic upgrade head
   ```
   
   To create new migrations after model changes:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
   
   To rollback migrations:
   ```bash
   alembic downgrade -1  # Rollback one migration
   alembic downgrade base  # Rollback all migrations
   ```

8. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

9. **Access the application**
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

### Running with Docker

1. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/docs

3. **Stop all services**
   ```bash
   docker-compose down
   ```

4. **Production deployment**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT token |
| POST | `/auth/logout` | Logout and invalidate token |

### Calculator Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calculations` | List all calculations for current user |
| POST | `/calculations` | Create a new calculation |
| GET | `/calculations/{id}` | Get specific calculation |
| PATCH | `/calculations/{id}` | Update a calculation |
| DELETE | `/calculations/{id}` | Delete a calculation |

### CarCompare - Cars
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cars` | List all cars for current user |
| POST | `/cars` | Create a new car |
| GET | `/cars/{car_id}` | Get specific car details |
| PATCH | `/cars/{car_id}` | Update car information |
| DELETE | `/cars/{car_id}` | Delete car and all its listings |

### CarCompare - Listings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cars/{car_id}/listings` | List all listings for a car |
| POST | `/cars/{car_id}/listings` | Create a new listing |
| GET | `/cars/{car_id}/listings/{listing_id}` | Get specific listing |
| PATCH | `/cars/{car_id}/listings/{listing_id}` | Update listing |
| DELETE | `/cars/{car_id}/listings/{listing_id}` | Delete listing |

### CarCompare - Advanced
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cars/{car_id}/compare` | Get price comparison statistics |
| GET | `/vin/{vin}` | Decode VIN using NHTSA API (no auth) |

### Web Routes (UI)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/login` | Login page |
| GET | `/register` | Registration page |
| GET | `/dashboard` | User dashboard |
| GET | `/cars-ui` | Car management UI |
| GET | `/cars-ui/{car_id}` | Car detail with listings |

---

## 🧪 Testing

The project includes comprehensive test coverage at three levels:

### Test Structure
- **Unit Tests** (`tests/unit/`): Test individual functions and logic
- **Integration Tests** (`tests/integration/`): Test API endpoints and database interactions
- **E2E Tests** (`tests/e2e/`): Test complete workflows from user registration to feature usage

### Integration Tests (39 tests for CarCompare)
- Car CRUD operations with ownership enforcement
- Listing CRUD operations with dual ownership (user + car)
- Price comparison statistics accuracy
- Cascade delete operations
- VIN uniqueness constraints
- Relationship integrity

### E2E Tests (8 tests for CarCompare)
- Complete car management workflow (register → login → CRUD)
- Listing management workflow with multiple listings
- Price comparison statistics end-to-end
- VIN decoder integration workflow
- Unauthorized access scenarios (security testing)
- Validation error scenarios (negative testing)
- Multi-user data isolation
- Cascade delete operations

### Run all tests
```bash
pytest
```

### Run specific test suites
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests (requires server to start automatically)
pytest tests/e2e/ -v

# Car tests only
pytest tests/integration/test_car.py -v

# Listing tests only
pytest tests/integration/test_listing.py -v

# Comparison tests only
pytest tests/integration/test_car_compare.py -v

# CarCompare E2E tests
pytest tests/e2e/test_carcompare_e2e.py -v
```

### Check code coverage
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Test Results
- **39 integration tests** - All passing ✅
- **Car model coverage**: 75%
- **Listing model coverage**: 74%
- **Overall coverage**: 17% (focused on new CarCompare feature)

---

## 📸 Screenshots

### Required Screenshots for Submission

1. **Browse Cars** - List view showing all user's cars
2. **Add Car** - Form to add a new car (with VIN decoder option)
3. **Edit Car** - Update car details
4. **Delete Car** - Confirmation dialog for car deletion
5. **Browse Listings** - Table showing all listings for a specific car
6. **Add Listing** - Form to add a new listing for a car
7. **Edit Listing** - Update listing information (price, mileage, source)
8. **Delete Listing** - Confirmation for listing deletion
9. **Compare View** - Statistics dashboard showing:
   - Total listing count
   - Min/Max/Average prices
   - Average price per mile
   - Best deal identification

### Screenshot Locations
Place screenshots in `/docs/screenshots/` with naming:
- `browse-cars.png`
- `add-car.png`
- `edit-car.png`
- `delete-car.png`
- `browse-listings.png`
- `add-listing.png`
- `edit-listing.png`
- `delete-listing.png`
- `compare-view.png`

---

## � Project Structure

```
module14_is601_extended/
├── app/
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py         # User authentication model
│   │   ├── calculation.py  # Calculator operations
│   │   ├── car.py          # Car model (CarCompare)
│   │   └── listing.py      # Listing model (CarCompare)
│   ├── schemas/             # Pydantic validation schemas
│   │   ├── car.py          # Car schemas + VINDecodeResponse
│   │   └── listing.py      # Listing schemas
│   ├── services/            # External service integrations
│   │   └── vin_decoder.py  # NHTSA VIN decoder client
│   ├── auth/                # Authentication logic
│   ├── core/                # Configuration
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection
│   └── database_init.py     # Database initialization
├── tests/
│   ├── integration/
│   │   ├── test_car.py           # Car CRUD tests (13 tests)
│   │   ├── test_listing.py       # Listing CRUD tests (16 tests)
│   │   └── test_car_compare.py   # Comparison tests (10 tests)
│   └── conftest.py          # pytest fixtures
├── templates/               # Jinja2 HTML templates
├── static/                  # CSS, JavaScript
├── docs/                    # Documentation
│   └── screenshots/         # Application screenshots
├── docker-compose.yml       # Docker development setup
├── docker-compose.prod.yml  # Docker production setup
├── Dockerfile               # Application container
├── requirements.txt         # Python dependencies
├── pytest.ini               # pytest configuration
└── README.md                # This file
```

---

## 📚 Development Resources

- **FastAPI Documentation**: <https://fastapi.tiangolo.com/>
- **SQLAlchemy 2.0 Documentation**: <https://docs.sqlalchemy.org/>
- **Pydantic v2 Documentation**: <https://docs.pydantic.dev/>
- **PostgreSQL Documentation**: <https://www.postgresql.org/docs/>
- **NHTSA VIN Decoder API**: <https://vpic.nhtsa.dot.gov/api/>
- **Alembic Documentation**: <https://alembic.sqlalchemy.org/>

---

## 🐳 Docker Deployment

### Docker Hub Repository

The application is automatically built and pushed to Docker Hub via GitHub Actions:

**Docker Hub**: <https://hub.docker.com/r/bdb67/module14_is601>

Pull the latest image:
```bash
docker pull bdb67/module14_is601:latest
```

Run the container:
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=your_database_url \
  -e REDIS_URL=your_redis_url \
  -e SECRET_KEY=your_secret \
  bdb67/module14_is601:latest
```

### Build Locally

```bash
docker build -t module14_is601 .
```

### Docker Compose (Development)

```bash
docker-compose up --build
```

### Docker Compose (Production)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🤝 Contributing

This is a student project for IS601. Contributions are not currently accepted.

---

## 📄 License

This project is for educational purposes as part of the IS601 course.

---

## 👤 Author

Billy B - IS601 Student

---

# 📦 Appendix: Development Environment Setup

For first-time setup of development tools, see the sections below.

---

# 🧩 1. Install Homebrew (Mac Only)

> Skip this step if you're on Windows.

Homebrew is a package manager for macOS.  
You’ll use it to easily install Git, Python, Docker, etc.

**Install Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Verify Homebrew:**

```bash
brew --version
```

If you see a version number, you're good to go.

---

# 🧩 2. Install and Configure Git

## Install Git

- **MacOS (using Homebrew)**

```bash
brew install git
```

- **Windows**

Download and install [Git for Windows](https://git-scm.com/download/win).  
Accept the default options during installation.

**Verify Git:**

```bash
git --version
```

---

## Configure Git Globals

Set your name and email so Git tracks your commits properly:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Confirm the settings:

```bash
git config --list
```

---

## Generate SSH Keys and Connect to GitHub

> Only do this once per machine.

1. Generate a new SSH key:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

(Press Enter at all prompts.)

2. Start the SSH agent:

```bash
eval "$(ssh-agent -s)"
```

3. Add the SSH private key to the agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy your SSH public key:

- **Mac/Linux:**

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

- **Windows (Git Bash):**

```bash
cat ~/.ssh/id_ed25519.pub | clip
```

5. Add the key to your GitHub account:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click **New SSH Key**, paste the key, save.

6. Test the connection:

```bash
ssh -T git@github.com
```

You should see a success message.

---

# 🧩 3. Clone the Repository

Now you can safely clone the course project:

```bash
git clone <repository-url>
cd <repository-directory>
```

---

# 🛠️ 4. Install Python 3.10+

## Install Python

- **MacOS (Homebrew)**

```bash
brew install python
```

- **Windows**

Download and install [Python for Windows](https://www.python.org/downloads/).  
✅ Make sure you **check the box** `Add Python to PATH` during setup.

**Verify Python:**

```bash
python3 --version
```
or
```bash
python --version
```

---

## Create and Activate a Virtual Environment

(Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

---

# 🐳 5. (Optional) Docker Setup

> Skip if Docker isn't used in this module.

## Install Docker

- [Install Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

## Build Docker Image

```bash
docker build -t <image-name> .
```

## Run Docker Container

```bash
docker run -it --rm <image-name>
```

---

# 🚀 6. Running the Project

- **Without Docker**:

```bash
python main.py
```

(or update this if the main script is different.)

- **With Docker**:

```bash
docker run -it --rm <image-name>
```

---

# 📝 7. Submission Instructions

After finishing your work:

```bash
git add .
git commit -m "Complete Module X"
git push origin main
```

Then submit the GitHub repository link as instructed.

---

# 🔥 Useful Commands Cheat Sheet

| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Install Homebrew (Mac)          | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Install Git                     | `brew install git` or Git for Windows installer |
| Configure Git Global Username  | `git config --global user.name "Your Name"`      |
| Configure Git Global Email     | `git config --global user.email "you@example.com"` |
| Clone Repository                | `git clone <repo-url>`                          |
| Create Virtual Environment     | `python3 -m venv venv`                           |
| Activate Virtual Environment   | `source venv/bin/activate` / `venv\Scripts\activate.bat` |
| Install Python Packages        | `pip install -r requirements.txt`               |
| Build Docker Image              | `docker build -t <image-name> .`                |
| Run Docker Container            | `docker run -it --rm <image-name>`               |
| Push Code to GitHub             | `git add . && git commit -m "message" && git push` |

---

# 📋 Notes

- Install **Homebrew** first on Mac.
- Install and configure **Git** and **SSH** before cloning.
- Use **Python 3.10+** and **virtual environments** for Python projects.
- **Docker** is optional depending on the project.

---

# 📎 Quick Links

- [Homebrew](https://brew.sh/)
- [Git Downloads](https://git-scm.com/downloads)
- [Python Downloads](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [GitHub SSH Setup Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
# trigger build
