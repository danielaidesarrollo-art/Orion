"""
Orion Core Connectors
Adapters for SafeCore, DataCore, and BioCore integration
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# -----------------------------------------------------------------------------
# SAFE CORE CONNECTOR
# -----------------------------------------------------------------------------

class SafeCoreConnector:
    """
    Connector for SafeCore Security System
    Handles threat detection, ZKP validation, and honeypot activation
    """
    
    def __init__(self, enable_zkp: bool = True, enable_honeypot: bool = True):
        self.enable_zkp = enable_zkp
        self.enable_honeypot = enable_honeypot
        self.threat_patterns = [
            "sql", "injection", "script", "alert(", "drop table",
            "union select", "exec(", "eval(", "<script", "javascript:"
        ]

    def detect_threat(self, input_text: str, answers: Dict[str, Any]) -> bool:
        """Detects security threats in input and answers"""
        input_lower = input_text.lower()
        
        # Check input text
        for pattern in self.threat_patterns:
            if pattern in input_lower:
                return True
        
        # Check answers
        for value in answers.values():
            if isinstance(value, str) and any(p in value.lower() for p in self.threat_patterns):
                return True
                
        return False

    def validate_zkp(self, patient_id: Optional[str], bio_hash: Optional[str]) -> bool:
        """
        Validates eligibility using Zero-Knowledge Proof simulation
        In a real scenario, this would compute cryptographic proofs
        """
        if not self.enable_zkp:
            return True
            
        # Simulation: If patient_id provided, assume valid proof can be generated
        # Anonymous access is also valid in this context
        return True

    def activate_honeypot(self, input_text: str, timestamp: str) -> Dict[str, Any]:
        """Returns honeypot redirect metadata"""
        return {
            "redirect": True,
            "target": "SYNTHETIC_ENV_01",
            "reason": "THREAT_DETECTED",
            "timestamp": timestamp
        }

# -----------------------------------------------------------------------------
# DATA CORE CONNECTOR
# -----------------------------------------------------------------------------

class DataCoreConnector:
    """
    Connector for DataCore
    Handles NLP Entity Detection and Knowledge Base access
    """
    
    def __init__(self, rules_engine: Any):
        # In a full microservices architecture, this would be an API client
        # Currently adapts the existing rules_engine
        self.rules_engine = rules_engine

    def detect_entity(self, input_text: str) -> Optional[str]:
        """Uses DataCore NLP to detect the main symptom/entity"""
        return self.rules_engine.detect_sintoma(input_text)
    
    def get_protocol(self, symptom: str) -> Dict[str, Any]:
        """Retrieves clinical protocol for a symptom"""
        return self.rules_engine.get_preguntas_obligatorias(symptom)

# -----------------------------------------------------------------------------
# BIO CORE CONNECTOR
# -----------------------------------------------------------------------------

class BioCoreConnector:
    """
    Connector for BioCore
    Handles biometric data processing and irreversible Identity Hashing
    """

    def generate_bio_hash(self, patient_id: Optional[str], biometric_data: Any) -> str:
        """
        Generates irreversible Bio-Hash
        Combines ID + biological markers (if available) + salt
        """
        if not patient_id:
            patient_id = "ANONYMOUS"
            
        hash_input = f"{patient_id}_{datetime.now().isoformat()}"
        
        if biometric_data:
            # Safely access attributes if biometric_data is an object or dict
             hr = getattr(biometric_data, 'heart_rate', None) or '0'
             bp = getattr(biometric_data, 'blood_pressure_systolic', None) or '0'
             hash_input += f"_{hr}_{bp}"
        
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def validate_vitals(self, biometric_data: Any) -> Dict[str, str]:
        """Checks vital signs against critical thresholds"""
        alerts = {}
        if not biometric_data:
            return alerts
            
        # Example validation logic
        hr = getattr(biometric_data, 'heart_rate', None)
        if hr and (hr > 120 or hr < 40):
            alerts['heart_rate'] = 'CRITICAL'
            
        return alerts
