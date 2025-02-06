# Eve Event Planner Application

Eve is a simple event planning application that allows users to create and manage events with comments.

## Architecture & Design

### Overview
- Backend: Python 3.11, FastAPI with SQLAlchemy, SQLite, and use case pattern
- DATABASE MUST BE: SQLite in /workspace/eve/data/eve.db (folder and file require 666 permissions, path must be relative in code as "data/eve.db")
- Database initialization: init_database.py script creates and initializes the database
- Frontend: Angular with Angular Material (deeppurple-amber theme)
- Authentication: Email-based with session UUID, no password
- PORTS MUST BE: Frontend - 2020, Backend - 2021 (both must be available and not used by other services)
- CORS to allow frontend to access backend
- All dates and times are stored and transmitted in UTC
  - Backend uses UTC exclusively
  - Frontend handles conversion between local time and UTC
  - Store all times in UTC without timezone info (naive datetime) in the database
- All scripts must run within context of "/workspace/eve", so that all SQLite database paths are "data/eve.db", all scripts must be stored in the project root "/workspace/eve". 
- Do not hardcode "/workspace/eve", just always store and start scripts at "/workspace/eve".
- Simpler is better
- Multiple events per author: Users can create any number of events
- Multiple comments per user: Users can post multiple comments on the same event

### Database Schema

#### Events Table
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    place TEXT,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    food TEXT,
    drinks TEXT,
    program TEXT,
    parking_info TEXT,
    music TEXT,
    theme TEXT,
    age_restrictions TEXT,
    author_email TEXT NOT NULL
);
```

#### Event Comments Table
```sql
CREATE TABLE event_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,  -- This is the user's email
    message TEXT NOT NULL,
    rating INTEGER DEFAULT 0,
    author_email TEXT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);
```

#### Sessions Table
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,  -- UUID
    user_email TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL
);
```

### Authentication
- Users authenticate by providing their email only
- A session UUID is generated and stored in the database with 8-hour expiration
- Session ID is stored in localStorage on the client side
- All API endpoints require valid session except login
- Session is passed via Authorization header

### Project Structure

```plaintext
/workspace/eve/
├── backend/                              # Backend Python FastAPI application
│   ├── controllers/                      # API route handlers
│   │   ├── __init__.py
│   │   ├── auth_controller.py           # Authentication endpoints
│   │   ├── comment_controller.py        # Comment-related endpoints
│   │   └── event_controller.py          # Event-related endpoints
│   ├── use_cases/                       # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_use_cases.py           # Authentication logic
│   │   ├── comment_use_cases.py        # Comment operations
│   │   └── event_use_cases.py          # Event operations
│   ├── tests/                           # Backend unit tests
│   │   ├── __init__.py
│   │   ├── conftest.py                 # Test fixtures and configuration
│   │   ├── test_auth.py                # Authentication tests
│   │   ├── test_comment_system.py      # Comment system integration tests
│   │   ├── test_comments.py            # Comment operations tests
│   │   ├── test_database_integrity.py  # Database integrity tests
│   │   ├── test_datetime_validation.py # DateTime validation tests
│   │   ├── test_event_filters.py       # Event filtering tests
│   │   ├── test_events.py              # Event operations tests
│   │   └── test_input_validation.py    # Input validation tests
│   ├── __init__.py
│   ├── database.py                      # Database configuration and session
│   ├── main.py                          # FastAPI application setup
│   ├── models.py                        # SQLAlchemy models
│   └── requirements.txt                 # Python dependencies
│
├── frontend/                            # Angular frontend application
│   ├── src/
│   │   ├── app/
│   │   │   ├── events/                 # Event-related components
│   │   │   │   ├── event-details/      # Event details view
│   │   │   │   │   ├── event-details.component.css
│   │   │   │   │   ├── event-details.component.html
│   │   │   │   │   └── event-details.component.ts
│   │   │   │   ├── event-form/        # Event creation/editing form
│   │   │   │   │   ├── event-form.component.css
│   │   │   │   │   ├── event-form.component.html
│   │   │   │   │   └── event-form.component.ts
│   │   │   │   ├── events.component.css
│   │   │   │   ├── events.component.html
│   │   │   │   ├── events.component.scss
│   │   │   │   └── events.component.ts
│   │   │   ├── guards/                # Route guards
│   │   │   │   ├── auth.guard.spec.ts
│   │   │   │   └── auth.guard.ts
│   │   │   ├── interceptors/          # HTTP interceptors
│   │   │   │   ├── auth.interceptor.spec.ts
│   │   │   │   └── auth.interceptor.ts
│   │   │   ├── login/                 # Login component
│   │   │   │   ├── login.component.html
│   │   │   │   ├── login.component.scss
│   │   │   │   └── login.component.ts
│   │   │   ├── models/                # TypeScript interfaces
│   │   │   │   ├── comment.model.ts
│   │   │   │   └── event.model.ts
│   │   │   ├── services/              # Angular services
│   │   │   │   ├── auth.service.spec.ts
│   │   │   │   ├── auth.service.ts
│   │   │   │   ├── comment.service.spec.ts
│   │   │   │   ├── comment.service.ts
│   │   │   │   ├── event.service.spec.ts
│   │   │   │   └── event.service.ts
│   │   │   ├── shared/                # Shared components
│   │   │   │   └── confirm-dialog/
│   │   │   │       └── confirm-dialog.component.ts
│   │   │   ├── testing/               # Test utilities
│   │   │   │   └── test-helpers.ts
│   │   │   ├── app.component.html
│   │   │   ├── app.component.scss
│   │   │   ├── app.component.ts
│   │   │   ├── app.config.ts
│   │   │   ├── app.module.ts
│   │   │   └── app.routes.ts
│   │   ├── environments/              # Environment configurations
│   │   │   ├── environment.prod.ts
│   │   │   └── environment.ts
│   │   ├── index.html
│   │   ├── main.ts
│   │   └── styles.scss
│   ├── angular.json                    # Angular configuration
│   ├── karma.conf.js                   # Karma test configuration
│   ├── package.json                    # Node.js dependencies
│   ├── tsconfig.app.json              # TypeScript config for app
│   ├── tsconfig.json                  # TypeScript base config
│   └── tsconfig.spec.json             # TypeScript config for tests
│
├── e2e_tests/                          # End-to-end tests
│   ├── conftest.py                    # E2E test configuration
│   ├── test_auth_e2e.py              # Authentication flow tests
│   ├── test_comments_e2e.py          # Comment operations tests
│   ├── test_events_e2e.py            # Event operations tests
│   ├── test_helpers.py               # Test utilities
│   └── test_new_user_e2e.py          # New user flow tests
│
├── data/                              # Database files
│   ├── eve.db                        # Main SQLite database
│   └── test.db                       # Test database
│
├── test_artifacts/                    # Test failure artifacts
│   └── [timestamp]/                  # Organized by run time
│       ├── backend.log
│       ├── frontend.log
│       └── server.log
│
├── init_database.py                   # Database initialization script
├── requirements.txt                   # Python root dependencies
├── run_all.sh                        # Run all tests script
├── run_e2e_tests.sh                  # Run e2e tests script, and auto outputs both frontend and backend logs
├── run_frontend_tests.sh             # Run frontend tests script
├── setup.sh                          # Project setup script
└── test_api_integration.py           # API integration tests
```


### Backend Architecture

#### CORS Configuration
- Frontend origin (http://localhost:2020) is allowed
- Credentials are allowed
- Allowed methods: GET, POST, PUT, DELETE, OPTIONS
- All headers are allowed and exposed
- Preflight requests are cached for 1 hour
- OPTIONS endpoints handle preflight requests

#### API Endpoints

HTTP Status Codes:
- 200: Successful operations
- 400: Bad request (validation errors)
- 401: Invalid/missing session
- 403: Not authorized (trying to modify other's content)
- 404: Resource not found

Error Response Format:
```json
{
  "detail": "error message"
}
```

Authentication:
- POST /api/auth/login (email) -> session_id
- POST /api/auth/logout

Events:
- GET /api/events - List all events
- GET /api/events/my - List user's events
- GET /api/events/upcoming - List upcoming events
- GET /api/events/{id} - Get event details
- POST /api/events - Create new event
- PUT /api/events/{id} - Update event (author only, returns 403 if not authorized)
- DELETE /api/events/{id} - Delete event (author only, returns 403 if not authorized)

Comments:
- GET /api/events/{id}/comments - List event comments
- POST /api/events/{id}/comments - Add comment
- PUT /api/events/{id}/comments/{comment_id} - Update comment (author only, returns 403 if not authorized)
- DELETE /api/events/{id}/comments/{comment_id} - Delete comment (author only, returns 403 if not authorized)

### Frontend Architecture

#### Features
- Home page displays:
  - List of upcoming events
  - List of user's own events
- Full CRUD operations for events and comments
- Material Design UI components
- Responsive layout
- Event filtering and sorting
- Real-time form validation


## Prerequisites

### Automated Installation
Run the setup script to install all dependencies and initialize the database:
```bash
./setup.sh
```

### Manual Installation (if needed)
1. System packages (Debian/Ubuntu):
```bash
sudo apt-get update -qq && sudo apt-get install -y -qq chromium nodejs npm
```

2. Global npm packages:
```bash
sudo npm install -g --no-progress --no-audit @angular/cli
```

3. Python packages:
```bash
pip install -r requirements.txt --quiet
playwright install --with-deps chromium firefox webkit
```

4. Database setup:
```bash
mkdir -p data && chmod 777 data && touch data/eve.db && chmod 777 data/eve.db
python init_database.py
```

### System Requirements
- Python 3.11+
- Node.js 16+
- SQLite3 (included in Python)
- Database path: data/eve.db (relative to project root)

## Installation & Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Initialize database (creates /workspace/eve/data/eve.db if not exists)
python init_database.py
```

Note: Make sure /workspace/eve/data directory and eve.db file both have 666 permissions:
```bash
chmod 666 /workspace/eve/data
chmod 666 /workspace/eve/data/eve.db
```

### Frontend Setup
```bash
cd frontend
npm install
```

## Development

### Running Backend
```bash
cd /workspace/eve
PYTHONPATH=backend python backend/main.py
```
Server will run on http://0.0.0.0:2021

Note: PYTHONPATH=backend is required for all Python commands that import from the backend package:
- Running the server: `PYTHONPATH=backend python backend/main.py`
- Running tests: `PYTHONPATH=backend python -m pytest backend/tests/`
- Running API integration tests: `PYTHONPATH=backend python test_api_integration.py`
- Database initialization: `PYTHONPATH=backend python init_database.py`

The provided scripts (run_all.sh, run_e2e_tests.sh) already include the correct PYTHONPATH setting.

### Running Frontend
```bash
cd frontend
ng serve  # Uses globally installed Angular CLI
```
Note: Make sure you have installed Angular CLI globally as specified in Prerequisites.
Application will be available at http://localhost:2020

## Testing

The project includes four types of tests:
1. Backend Unit Tests (pytest)
2. API Integration Tests (Python)
3. Frontend Unit Tests (Karma/Jasmine)
4. End-to-End Tests (Playwright)

### Test Prerequisites
Before running tests, ensure:
```bash
# 1. Database permissions
chmod 666 data/eve.db
chmod 666 data

# 2. Install test dependencies
pip install pytest pytest-playwright
playwright install  # Installs browser for e2e tests

# 3. Set environment variables for frontend tests
export CHROME_BIN=/usr/bin/chromium
```

### Backend Unit Tests
Located in `backend/tests/`, covering:
- Authentication (test_auth.py)
- Events (test_events.py)
- Comments (test_comments.py)

Run backend tests:
```bash
cd /workspace/eve
PYTHONPATH=backend python -m pytest backend/tests/
```

Expected output: 12 tests passing, covering session management, CRUD operations, and permissions.

### Frontend Unit Tests
Located in `frontend/src/app/`, testing:
- Services (auth, event, comment)
- Guards (auth)
- Components

Run frontend tests:
```bash
cd frontend
npm run test -- --watch=false --browsers=ChromeHeadlessNoSandbox
```

Expected output: 25 tests passing, covering HTTP interactions, state management, and routing.

Note: Frontend tests require Chromium browser and proper karma.conf.js configuration for container environments.

### API Integration Tests
Single test script (`test_api_integration.py`) that:
- Tests all endpoints sequentially
- Verifies auth flows
- Validates CRUD operations
- Checks permissions
- Cleans up test data

Run API tests:
```bash
cd /workspace/eve
PYTHONPATH=backend python test_api_integration.py
```

Features:
- Automatic database cleanup
- Detailed progress output
- Screenshots of failures
- Preserves database schema

### End-to-End Tests
Located in `e2e_tests/`, using Playwright to test:
- User flows
- Frontend-backend integration
- Data persistence
- UI interactions
- Ignore date, time fields and components
- Keep timeouts as it is, increasing will not solve any problem
- Check both backend and frontend logs for debugging

Run e2e tests:
```bash
# Run all tests (not recommended)
./run_e2e_tests.sh

# Run a specific test file
./run_e2e_tests.sh test_auth.py

# Run a specific test function
pytest e2e_tests/test_events.py::test_create_event -v
```

The script:
1. Initializes clean database
2. Starts frontend (port 2020)
3. Starts backend (port 2021)
4. Runs Playwright tests
5. Captures failure screenshots in e2e_tests/screenshots/
6. Cleans up processes

Note: It's recommended to run one test at a time to better isolate and debug issues.

### Convenience Scripts

1. Run all backend tests:
```bash
./run_all.sh
```

2. Run frontend tests:
```bash
./run_frontend_tests.sh
```

3. Run e2e tests:
```bash
# Run all tests (not recommended)
./run_e2e_tests.sh

# Run a specific test file
./run_e2e_tests.sh test_auth.py

# Run a specific test function
pytest e2e_tests/test_events.py::test_create_event -v
```

### Test Coverage

1. Backend Tests Cover:
- Session management
- CRUD operations
- Authorization
- Data validation
- Error handling

2. Frontend Tests Cover:
- HTTP interactions
- State management
- Route protection
- Form validation
- Error handling

3. E2E Tests Cover:
- User flows
- Data persistence
- UI/UX validation
- Cross-component integration
- Browser compatibility

Important E2E Test Requirements:
- Date/time fields are not validated in tests
- HTML dumps are limited to the relevant container (mat-sidenav-content)
- Tests must match the actual frontend implementation
- Run one test at a time to isolate issues
- Each test should be independent and self-contained

### Troubleshooting

1. Frontend Test Issues:
- Ensure Chromium is installed
- Set CHROME_BIN environment variable
- Check karma.conf.js for sandbox settings
- Verify Angular version compatibility

2. Backend Test Issues:
- Check database permissions (666 for both data directory and eve.db)
- Verify Python package versions
- Ensure working directory is correct (/workspace/eve)
- Verify database path is relative (data/eve.db)

3. E2E Test Issues:
- Check Playwright browser installation
- Verify ports 2020/2021 are available
- Ensure both servers are running
- Run tests one at a time for better isolation
- Check screenshots in e2e_tests/screenshots/ for failures
- Verify selectors match actual frontend implementation
- Avoid testing date/time fields
- Check HTML dumps are limited to relevant container

## Business Logic

### Events
- Events have a title, description, location, and time range
- Additional details include food, drinks, program, parking info, music, theme, and age restrictions
- Only the event author can edit or delete their events
- All users can view events

### Comments
- Users can comment on events
- Comments include a message and optional rating (0 by default)
- Only the comment author can edit or delete their comments
- All users can view comments

### Authentication
- Users provide their email to login
- Session expires after 8 hours
- New login creates new session
- Logout invalidates the session