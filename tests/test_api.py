import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ELIS API" in response.json()["message"]

def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_extract_metadata():
    """Test metadata extraction endpoint."""
    response = client.post("/extract/metadata", json={
        "text": "Case ID: 7A/123. Order Date: 12-05-2023."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "7A/123"
    assert data["date"] == "2023-05-12"

def test_classify():
    """Test classification endpoint."""
    response = client.post("/classify", json={
        "text": "Under Section 7A of EPF Act, determination of dues. Employer failed to comply."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["case_type"] == "7A"
    assert "outcome" in data

def test_extract_timeline():
    """Test timeline extraction endpoint."""
    response = client.post("/extract/timeline", json={
        "text": "On 02.07.2018, case was called. Adjourned to 15.08.2018."
    })
    assert response.status_code == 200
    data = response.json()
    assert "timeline" in data
    assert data["count"] >= 1

def test_qa():
    """Test QA endpoint."""
    response = client.post("/qa", json={
        "question": "What was the total dues?",
        "context": "The total dues amount to Rs. 50,000."
    })
    assert response.status_code == 200
    data = response.json()
    assert "50,000" in data["answer"] or "50000" in data["answer"]

def test_extract_all():
    """Test full extraction endpoint."""
    response = client.post("/extract/all", json={
        "text": "Section 7A order. Case ID: TN/123. Date: 01-01-2024. Employer failed to remit."
    })
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "classification" in data
    assert "timeline" in data
