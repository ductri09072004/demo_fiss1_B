import requests
import json

# Update demo-v90 path in MongoDB
url = "https://auto-tool-production.up.railway.app/api/db/services/demo-v90"
headers = {"Content-Type": "application/json"}
data = {
    "argocd_application": {
        "path": "."
    }
}

try:
    response = requests.put(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
