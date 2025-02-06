import os
import sys
import pytest
import signal
import subprocess
import time
from typing import Generator, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError

# Constants
FRONTEND_URL = "http://localhost:2020"  # Frontend port
BACKEND_URL = "http://localhost:2021"   # Backend port
DATABASE_PATH = "data/eve.db"  # Already using relative path
TIMEOUT = 10000  # 10 seconds timeout for all operations

def start_backend() -> subprocess.Popen:
    """Start the backend server."""
    process = subprocess.Popen(
        ["bash", "-c", "PYTHONPATH=backend python backend/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    return process

def start_frontend() -> subprocess.Popen:
    """Start the frontend server."""
    process = subprocess.Popen(
        ["ng", "serve", "--port", "2020"],  # Frontend port
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    return process

def stop_process(process: subprocess.Popen) -> None:
    """Stop a running process with timeout."""
    if process:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait(timeout=TIMEOUT/1000)  # Convert to seconds
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)

def wait_for_server(url: str, timeout: int = TIMEOUT) -> bool:
    """Wait for a server to become available."""
    import requests
    from requests.exceptions import RequestException
    
    end_time = time.time() + timeout/1000
    while time.time() < end_time:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except RequestException:
            pass
        time.sleep(0.5)
    return False

@pytest.fixture(scope="session")
def clean_database() -> None:
    """Clean and initialize the database."""
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from sqlalchemy import create_engine
    from models import Base
    
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session")
def browser_context(clean_database) -> Generator[BrowserContext, None, None]:
    """Create a browser context for testing."""
    backend_process = None
    frontend_process = None
    browser = None
    context = None
    
    try:
        # Start servers
        backend_process = start_backend()
        if not wait_for_server(f"{BACKEND_URL}/docs"):
            pytest.fail("Backend server failed to start")

        frontend_process = start_frontend()
        if not wait_for_server(FRONTEND_URL):
            pytest.fail("Frontend server failed to start")

        # Create browser context
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            base_url=FRONTEND_URL
        )
        
        yield context

    finally:
        # Cleanup
        if context:
            context.close()
        if browser:
            browser.close()
        if frontend_process:
            stop_process(frontend_process)
        if backend_process:
            stop_process(backend_process)

@pytest.fixture
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    page = browser_context.new_page()
    page.set_default_timeout(TIMEOUT)  # Set timeout for all operations
    yield page
    page.close()

@pytest.fixture
def screenshot_on_failure(request, page: Page):
    """Take a screenshot when a test fails."""
    yield
    if request.node.rep_call.failed:
        screenshot_dir = "e2e_tests/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(
            screenshot_dir,
            f"{request.node.nodeid.replace('/', '_').replace(':', '_')}.png"
        )
        page.screenshot(path=screenshot_path)
        print(f"\nScreenshot saved: {screenshot_path}")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add screenshot capability to the test report."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)