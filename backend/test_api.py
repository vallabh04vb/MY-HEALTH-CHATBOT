import requests
import json

# Test query endpoint
response = requests.post(
    "http://localhost:8000/api/ask",
    json={
        "question": "What are the BMI requirements for bariatric surgery?",
        "provider": "UHC"
    }
)

print(json.dumps(response.json(), indent=2))
