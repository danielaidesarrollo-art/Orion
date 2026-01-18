"""
Test for AI-Driven Resource Prediction
"""
import sys
import unittest
from unittest.mock import MagicMock
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from core.resource_predictor import ResourcePredictor, EnvironmentalFactors

class TestAIPrediction(unittest.TestCase):
    
    def setUp(self):
        self.predictor = ResourcePredictor()
        # Mocking AI Client to avoid needing real API key for testing logic
        self.predictor.ai_client = MagicMock()
        
    def test_rich_data_ingestion_and_training(self):
        """Test that CSV with clinical data triggers AI analysis"""
        
        # CSV with 'symptom' (Rich format)
        csv_content = b"""timestamp,symptom,triage_code,wait_time_min,consultation_time_min
2023-10-02 08:30:00,chest pain severe,D1,5,45
2023-10-02 08:45:00,cardiac arrest,D1,0,60
2023-10-02 09:00:00,mild headache,D3,15,10
"""
        # Mock AI response: High severity for this batch (cardiac cases)
        self.predictor.ai_client.analyze_batch_patterns.return_value = 2.5 
        
        result = self.predictor.train_from_csv(csv_content)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "rich_ai")
        self.assertTrue(self.predictor.ai_client.analyze_batch_patterns.called)
        
        # Verify model entry
        # Monday (Day 0) Hour 8 (08:00) should have high severity
        key = "0-8" 
        entry = self.predictor.baseline_model.get(key)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["severity"], 2.5)
        self.assertEqual(entry["count"], 2.0) # 2 cases in 8am hour
        
    def test_prediction_with_severity(self):
        """Test that high severity increases required doctors"""
        
        # Setup model with high severity
        self.predictor.baseline_model = {
            "0-10": {"count": 10.0, "severity": 2.0} # 10 patients, but high severity (x2)
        }
        
        target_time = datetime(2023, 10, 2, 10, 0, 0) # A Monday at 10am
        factors = EnvironmentalFactors("sunny", "low", "none")
        
        result = self.predictor.predict(target_time, factors)
        
        # Base demand 10. Severity 2.0 -> Weighted Demand 20.
        # Capacity Doctor = 4 patients/hr
        # Required Doctors = 20 / 4 = 5
        self.assertEqual(result.required_doctors, 5)
        
        # Compare with low severity
        self.predictor.baseline_model["0-10"]["severity"] = 1.0
        result_low = self.predictor.predict(target_time, factors)
        # Weighted Demand 10. Required Doctors = 10 / 4 = 3
        self.assertEqual(result_low.required_doctors, 3)

if __name__ == '__main__':
    unittest.main()
