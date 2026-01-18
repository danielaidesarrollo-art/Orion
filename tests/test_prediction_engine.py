
import sys
from pathlib import Path
import json
import io

# Add root to path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from api.triage_api import app
from core.resource_predictor import ResourcePredictor, EnvironmentalFactors

client = TestClient(app)

def test_prediction_logic():
    print("\n[TEST] Testing ResourcePredictor Core Logic...")
    predictor = ResourcePredictor()
    
    # Mock data directly
    predictor.baseline_model = {
        "0-10": 20.0  # Monday 10am: 20 patients
    }
    
    # Test 1: Baseline only (Monday 10am)
    from datetime import datetime
    target = datetime(2023, 10, 2, 10, 0) # Oct 2, 2023 is a Monday
    factors = EnvironmentalFactors(
        weather="sunny",
        traffic="low",
        event="none"
    )
    
    result = predictor.predict(target, factors)
    print(f"  > Baseline Prediction: {result.predicted_patients_per_hour} patients")
    assert result.predicted_patients_per_hour == 20.0
    
    # Test 2: Factors Impact (Storm + Protest)
    factors_bad = EnvironmentalFactors(
        weather="storm",   # 1.25
        traffic="low",     # 1.0
        event="protest"    # 1.35
    )
    # Expected: 20 * 1.25 * 1.35 = 33.75
    
    result_bad = predictor.predict(target, factors_bad)
    print(f"  > Storm+Protest Prediction: {result_bad.predicted_patients_per_hour} patients")
    print(f"  > Required Doctors: {result_bad.required_doctors}")
    print(f"  > Required Nurses: {result_bad.required_nurses}")
    
    assert 33.0 <= result_bad.predicted_patients_per_hour <= 34.0
    print("  > Core Logic OK")

def test_api_integration():
    print("\n[TEST] Testing API Endpoints...")
    
    # 1. Upload Training Data
    csv_content = """date,hour,patients_seen
2023-10-02,08,10
2023-10-02,09,20
2023-10-02,10,30
"""
    files = {'file': ('train.csv', csv_content, 'text/csv')}
    response = client.post("/api/predict/train", files=files)
    print(f"  > Upload Status: {response.status_code}")
    print(f"  > Response: {response.json()}")
    assert response.status_code == 200
    
    # 2. Get Prediction via API
    # Monday (Oct 2) at 09:00 -> Average 20 from CSV training above? 
    # Actually training does "day of week" + "hour".
    # 2023-10-02 is Monday. Hour 09 has 20 patients.
    
    payload = {
        "datetime_str": "2023-10-09 09:00", # Next Monday
        "weather": "rainy",
        "traffic": "medium",
        "event": "none"
    }
    
    resp_predict = client.post("/api/predict/resources", json=payload)
    print(f"  > Prediction Status: {resp_predict.status_code}")
    data = resp_predict.json()
    print(f"  > Prediction Data: {json.dumps(data, indent=2)}")
    
    assert resp_predict.status_code == 200
    assert data["predicted_patients_per_hour"] > 20.0 # Should be > 20 due to rain/traffic
    print("  > API Integration OK")

if __name__ == "__main__":
    test_prediction_logic()
    test_api_integration()
    print("\nAll tests passed successfully! 🚀")
