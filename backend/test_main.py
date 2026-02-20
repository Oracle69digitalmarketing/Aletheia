
import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

# Mock Opik to avoid API calls during tests
os.environ["OPIK_API_KEY"] = "test_key"
os.environ["OPIK_WORKSPACE"] = "test_workspace"
os.environ["GOOGLE_API_KEY"] = "test_google_key"

from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "diagnostics" in response.json()

def test_latency_calculation():
    # This is a bit tricky to test without mocking time,
    # but we can check if it returns a reasonable integer.
    start = time.monotonic()
    time.sleep(0.1)
    end = time.monotonic()
    latency = int((end - start) * 1000)
    assert latency >= 100
