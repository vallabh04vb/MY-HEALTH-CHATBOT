"""
Pytest fixtures for integration tests
"""
import pytest
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables"""
    os.environ["APP_ENV"] = "testing"
    os.environ["DEBUG"] = "True"
    os.environ["CHROMA_PERSIST_DIRECTORY"] = str(Path(__file__).parent.parent / "chroma_data")
    os.environ["ENABLE_CACHE"] = "False"  # Disable cache for tests
    yield
    # Cleanup after all tests

@pytest.fixture(scope="module")
def client(test_env):
    """Create FastAPI test client"""
    from app.main import app
    client = TestClient(app)
    yield client
    client.close()

@pytest.fixture(scope="module")
def sample_questions():
    """Sample questions for testing"""
    return {
        "valid_medical": "What are the coverage criteria for bariatric surgery?",
        "valid_short": "Is MRI covered?",
        "valid_long": "What is the prior authorization process for knee replacement surgery in patients with osteoarthritis?",
        "edge_empty": "",
        "edge_whitespace": "   ",
        "edge_too_long": "x" * 501,
        "edge_non_medical": "What is the capital of France?",
        "edge_gibberish": "asdfghjkl qwerty",
    }

@pytest.fixture(scope="module")
def expected_providers():
    """Expected insurance providers"""
    return ["UHC", "AETNA", "CIGNA"]
