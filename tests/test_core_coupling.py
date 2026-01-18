"""
Tests for Core Coupling (OrionMasterEngine + Connectors)
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.connectors import SafeCoreConnector, DataCoreConnector, BioCoreConnector
from core.orion_master import OrionMasterEngine, BiometricData

class TestCoreCoupling(unittest.TestCase):
    
    def setUp(self):
        self.mock_rules_engine = MagicMock()
        self.mock_rules_engine.detect_sintoma.return_value = "dolor toracico"
        self.mock_rules_engine.get_preguntas_obligatorias.return_value = []
        self.mock_rules_engine.clasificar_triage.return_value = MagicMock(
            codigo_triage="D1", confianza=0.9, instruccion_atencion="Test", posibles_causas=[]
        )
        
        self.engine = OrionMasterEngine(self.mock_rules_engine, enable_zkp=True, enable_honeypot=True)

    def test_safe_core_threat_detection(self):
        """Verify SafeCore successfully blocks threats"""
        # Direct connector test
        connector = SafeCoreConnector()
        self.assertTrue(connector.detect_threat("drop table users", {}))
        self.assertFalse(connector.detect_threat("dolor de cabeza", {}))
        
        # Integration via Engine
        result = self.engine.process_triage(
            input_text="DROP TABLE users", # Threat matching 'drop table'
            respuestas={},
            biometric_data=None
        )
        self.assertTrue(result.threat_detected)
        self.assertEqual(result.codigo_conducta, "BLOCKED")

    def test_bio_core_hashing(self):
        """Verify BioCore generates irreversible hashes"""
        import time
        connector = BioCoreConnector()
        hash1 = connector.generate_bio_hash("patient123", None)
        time.sleep(0.01) # Ensure timestamp difference
        hash2 = connector.generate_bio_hash("patient123", None)
        
        self.assertNotEqual(hash1, hash2) # Should be different due to timestamp
        self.assertEqual(len(hash1), 64) # SHA-256 length

    def test_data_core_delegation(self):
        """Verify DataCore is used for NLP"""
        self.engine.process_triage("me duele el pecho", {}, None)
        # Should call connector, which calls rules engine
        self.mock_rules_engine.detect_sintoma.assert_called_with("me duele el pecho")

if __name__ == '__main__':
    unittest.main()
