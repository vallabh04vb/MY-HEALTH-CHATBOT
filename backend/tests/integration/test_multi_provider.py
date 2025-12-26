"""
Integration tests for multi-provider functionality
"""
import pytest

class TestMultiProvider:
    """Test multi-provider support (UHC, Aetna, Cigna)"""

    def test_uhc_provider(self, client, sample_questions):
        """Test UHC provider queries"""
        payload = {
            "question": sample_questions["valid_medical"],
            "provider": "UHC"
        }
        response = client.post("/api/ask", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "UHC"

        # Check sources are present
        assert "sources" in data
        assert isinstance(data["sources"], list)

    def test_aetna_provider(self, client, sample_questions):
        """Test Aetna provider queries"""
        payload = {
            "question": sample_questions["valid_medical"],
            "provider": "Aetna"
        }
        response = client.post("/api/ask", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "AETNA"  # Normalized to uppercase

    def test_cigna_provider(self, client, sample_questions):
        """Test Cigna provider queries"""
        payload = {
            "question": sample_questions["valid_medical"],
            "provider": "Cigna"
        }
        response = client.post("/api/ask", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "CIGNA"  # Normalized to uppercase

    def test_provider_case_insensitive(self, client, sample_questions):
        """Test provider names are case-insensitive"""
        payload1 = {
            "question": sample_questions["valid_medical"],
            "provider": "uhc"
        }
        payload2 = {
            "question": sample_questions["valid_medical"],
            "provider": "UHC"
        }

        response1 = client.post("/api/ask", json=payload1)
        response2 = client.post("/api/ask", json=payload2)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["provider"] == response2.json()["provider"]

    def test_all_providers_return_answers(self, client, sample_questions):
        """Test that all three providers can return answers"""
        providers = ["UHC", "AETNA", "CIGNA"]

        for provider in providers:
            payload = {
                "question": sample_questions["valid_medical"],
                "provider": provider
            }
            response = client.post("/api/ask", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert len(data["answer"]) > 0
            assert 0.0 <= data["confidence"] <= 1.0
