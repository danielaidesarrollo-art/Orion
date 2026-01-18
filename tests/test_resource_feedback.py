"""
Tests for Resource Prediction Feedback Loop
"""
import sys
import unittest
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.resource_predictor import ResourcePredictor, EnvironmentalFactors

class TestResourceFeedback(unittest.TestCase):
    
    def setUp(self):
        self.predictor = ResourcePredictor()

    def test_record_actual_usage(self):
        """Verify usage data is recorded"""
        self.predictor.record_actual_usage(datetime.now().isoformat(), 15)
        self.assertEqual(len(self.predictor.actual_usage), 1)
        self.assertEqual(self.predictor.actual_usage[0]['count'], 15)

    def test_drift_calculation_low(self):
        """Verify low drift calculation"""
        # Prediccion por defecto es ~10 (baseline default) * 1.0 (sunny/low/none)
        # Si actual es 10, drift debe ser ~0
        self.predictor.record_actual_usage(datetime.now().isoformat(), 10)
        report = self.predictor.get_drift_report()
        
        # Predicted depends on time/day, but let's assume close to 10
        # If predicted is 10 and actual is 10, drift is 0
        
        # We verify keys exist and logic runs safely
        self.assertIn("drift_percentage", report)
        self.assertIn("alert", report)
        self.assertFalse(report["alert"]) # 10 vs ~10 shouldn't alert

    def test_drift_alert_high(self):
        """Verify high drift triggers alert"""
        # Si actual es 50 y pred es ~10, drift > 20%
        self.predictor.record_actual_usage(datetime.now().isoformat(), 50)
        
        is_alert = self.predictor.check_drift_alert()
        # Note: This might depend on the mock baseline. 
        # If prediction is 10, 50 is 400% drift.
        self.assertTrue(is_alert)

if __name__ == '__main__':
    unittest.main()
