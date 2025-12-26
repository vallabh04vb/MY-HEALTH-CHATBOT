"""
Integration tests for complete API flow:
User Request → Validation → ChromaDB → LLM → Response
"""
import pytest

class TestAPIIntegration:
    """Full end-to-end API integration tests"""

    def test_health_endpoint(self, client):
        """Test /api/health endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data
        assert "chroma_collections" in data

    def test_providers_endpoint(self, client):
        """Test /api/providers endpoint returns available providers"""
        response = client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], list)
        assert data["count"] >= 3

    def test_ask_endpoint_valid_question(self, client, sample_questions):
        """Test /api/ask with valid medical question"""
        payload = {
            "question": sample_questions["valid_medical"],
            "provider": "UHC"
        }
        response = client.post("/api/ask", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert len(data["answer"]) > 0
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert "confidence" in data
        assert 0.0 <= data["confidence"] <= 1.0
        assert data["provider"] == "UHC"

    def test_ask_endpoint_empty_question(self, client, sample_questions):
        """Test /api/ask rejects empty question"""
        payload = {
            "question": sample_questions["edge_empty"],
            "provider": "UHC"
        }
        response = client.post("/api/ask", json=payload)
        assert response.status_code == 422  # Validation error

    def test_ask_endpoint_too_long(self, client, sample_questions):
        """Test /api/ask rejects too long question"""
        payload = {
            "question": sample_questions["edge_too_long"],
            "provider": "UHC"
        }
        response = client.post("/api/ask", json=payload)
        assert response.status_code == 422  # Validation error

    def test_ask_endpoint_whitespace_only(self, client, sample_questions):
        """Test /api/ask rejects whitespace-only question"""
        payload = {
            "question": sample_questions["edge_whitespace"],
            "provider": "UHC"
        }
        response = client.post("/api/ask", json=payload)
        assert response.status_code == 422  # Validation error

    def test_feedback_endpoint(self, client, sample_questions):
        """Test /api/feedback endpoint"""
        payload = {
            "question": sample_questions["valid_medical"],
            "answer": "Test answer",
            "rating": 5,
            "comment": "Great response!"
        }
        response = client.post("/api/feedback", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "message" in data
