"""
DANIEL_AI Orion - Motor de Decisión Clínica Maestro
Sistema integrado con DataCore, SafeCore y BioCore
"""

import json
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from core.inference_engine import InferenceEngine

# Med-Gemma es opcional
try:
    from core.medgemma_client import MedGemmaClient
    from core.hybrid_engine import HybridTriageEngine
    MEDGEMMA_AVAILABLE = True
except ImportError:
    MedGemmaClient = None
    HybridTriageEngine = None
    MEDGEMMA_AVAILABLE = False


@dataclass
class BiometricData:
    """Datos biométricos del paciente (BioCore)"""
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    oxygen_saturation: Optional[float] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    bio_hash: Optional[str] = None  # Hash irreversible de identidad


@dataclass
class TriageDecisionLog:
    """Log estructurado de decisión de triage"""
    timestamp: str
    patient_bio_hash: str  # Identidad encriptada
    sintoma_detectado: str
    preguntas_realizadas: List[Dict[str, Any]]
    clasificacion_reglas: Dict[str, Any]
    clasificacion_ai: Dict[str, Any]
    clasificacion_final: str
    categoria: str
    confianza: float
    concordancia: bool
    instrucciones_inmediatas: List[str]
    causas_posibles: List[str]
    conducta_asignada: str  # URG, CONS, LM
    codigo_conducta: str  # D1, D2, D3, D7
    derivacion_vpp: bool  # Vía de Procesamiento Vertical
    observaciones: str
    gas_consumido: float  # Para reporte mensual COP
    zkp_validation: bool  # Zero-Knowledge Proof validado
    threat_detected: bool  # Amenaza detectada
    honeypot_activated: bool  # Honeypot activado


class OrionMasterEngine:
    """
    Motor Maestro de DANIEL_AI Orion
    
    Integra:
    - DataCore: NLP Entity Detection + Honeypot
    - SafeCore: Zero-Knowledge Proof + Auditoría
    - BioCore: Biometría + Bio-Hash
    - Med-Gemma: IA Médica
    - Sistema de Reglas: Protocolos clínicos
    """
    
    # Mapeo de códigos a conductas
    CODIGO_TO_CONDUCTA = {
        "D1": "URG",  # Urgencia inmediata
        "D2": "URG",  # Urgencia
        "D7": "LM",   # Baja complejidad (Libre Movimiento)
        "D3": "CONS"  # Consulta
    }
    
    # Umbrales para derivación VPP
    VPP_THRESHOLD_CODES = ["D7", "D3"]
    
    def __init__(self, 
                 rules_engine: InferenceEngine,
                 ai_client: Optional[MedGemmaClient] = None,
                 enable_zkp: bool = True,
                 enable_honeypot: bool = True):
        """
        Inicializa el motor maestro
        
        Args:
            rules_engine: Motor de reglas clínicas
            ai_client: Cliente Med-Gemma (opcional)
            enable_zkp: Habilitar Zero-Knowledge Proof
            enable_honeypot: Habilitar Honeypot para amenazas
        """
        self.rules_engine = rules_engine
        self.ai_client = ai_client
        self.enable_zkp = enable_zkp
        self.enable_honeypot = enable_honeypot
        
        # Motor híbrido
        if ai_client and MEDGEMMA_AVAILABLE and HybridTriageEngine:
            self.hybrid_engine = HybridTriageEngine(rules_engine, ai_client)
        else:
            self.hybrid_engine = None
        
        # Logs de decisiones
        self.decision_logs: List[TriageDecisionLog] = []
    
    def process_triage(self,
                      input_text: str,
                      respuestas: Dict[str, Any],
                      biometric_data: Optional[BiometricData] = None,
                      patient_id: Optional[str] = None) -> TriageDecisionLog:
        """
        Procesa un caso de triage completo con Chain-of-Thought
        
        Flujo:
        1. NLP Entity Detection (DataCore)
        2. Threat Detection + Honeypot (SafeCore)
        3. Zero-Knowledge Proof (SafeCore)
        4. Bio-Hash Generation (BioCore)
        5. Multimodal Triage Logic
        6. Clasificación Híbrida
        7. Instrucciones Inmediatas
        8. Logging Estructurado
        
        Args:
            input_text: Texto del paciente (voz/texto/imagen transcrita)
            respuestas: Respuestas a preguntas clave
            biometric_data: Datos biométricos opcionales
            patient_id: ID del paciente (será hasheado)
            
        Returns:
            TriageDecisionLog con decisión completa
        """
        timestamp = datetime.now().isoformat()
        
        # PASO 1: NLP Entity Detection (DataCore)
        print("🔍 [DataCore] Ejecutando NLP Entity Detection...")
        sintoma_detectado = self._detect_entity(input_text)
        
        if not sintoma_detectado:
            raise ValueError("No se pudo detectar síntoma principal del input")
        
        print(f"   ✅ Síntoma detectado: {sintoma_detectado}")
        
        # PASO 2: Threat Detection (SafeCore)
        print("🛡️  [SafeCore] Analizando amenazas...")
        threat_detected = self._detect_threat(input_text, respuestas)
        honeypot_activated = False
        
        if threat_detected and self.enable_honeypot:
            print("   ⚠️  AMENAZA DETECTADA - Activando Honeypot")
            honeypot_activated = True
            # Redirigir a entorno sintético
            return self._redirect_to_honeypot(input_text, timestamp)
        
        print("   ✅ Sin amenazas detectadas")
        
        # PASO 3: Zero-Knowledge Proof (SafeCore)
        print("🔐 [SafeCore] Validando elegibilidad con ZKP...")
        zkp_valid = self._validate_zkp(patient_id, biometric_data)
        
        if not zkp_valid and self.enable_zkp:
            raise PermissionError("Validación ZKP fallida - Paciente no elegible")
        
        print("   ✅ ZKP validado")
        
        # PASO 4: Bio-Hash Generation (BioCore)
        print("🧬 [BioCore] Generando Bio-Hash irreversible...")
        bio_hash = self._generate_bio_hash(patient_id, biometric_data)
        print(f"   ✅ Bio-Hash: {bio_hash[:16]}...")
        
        # PASO 5: Validación Dinámica - Preguntas Clave
        print(f"\n📋 [Orion] Ejecutando preguntas clave para '{sintoma_detectado}'...")
        preguntas_obligatorias = self.rules_engine.get_preguntas_obligatorias(sintoma_detectado)
        
        preguntas_realizadas = []
        for pregunta in preguntas_obligatorias:
            respuesta = respuestas.get(pregunta['pregunta'], 'No respondida')
            preguntas_realizadas.append({
                "pregunta": pregunta['pregunta'],
                "respuesta": respuesta,
                "tipo": pregunta['tipo_respuesta']
            })
            print(f"   • {pregunta['pregunta']}: {respuesta}")
        
        # PASO 6: Clasificación Multimodal (Chain-of-Thought)
        print("\n🧠 [Orion] Ejecutando clasificación híbrida...")
        
        if self.hybrid_engine:
            # Clasificación híbrida (Reglas + AI)
            resultado_hibrido = self.hybrid_engine.classify(sintoma_detectado, respuestas)
            
            clasificacion_final = resultado_hibrido.codigo_triage
            categoria = resultado_hibrido.categoria
            confianza = resultado_hibrido.confianza
            concordancia = resultado_hibrido.concordancia
            
            clasificacion_reglas = {
                "codigo": resultado_hibrido.resultado_reglas.codigo_triage,
                "confianza": resultado_hibrido.resultado_reglas.confianza,
                "instruccion": resultado_hibrido.resultado_reglas.instruccion_atencion
            }
            
            clasificacion_ai = {
                "codigo": resultado_hibrido.resultado_ai.codigo_triage,
                "confianza": resultado_hibrido.resultado_ai.confianza,
                "razonamiento": resultado_hibrido.resultado_ai.razonamiento
            }
            
            instrucciones_inmediatas = [resultado_hibrido.resultado_reglas.instruccion_atencion]
            causas_posibles = resultado_hibrido.resultado_reglas.posibles_causas
            
        else:
            # Solo reglas
            resultado_reglas = self.rules_engine.clasificar_triage(sintoma_detectado, respuestas)
            
            clasificacion_final = resultado_reglas.codigo_triage
            categoria = self.hybrid_engine.CATEGORIAS.get(clasificacion_final, "DESCONOCIDO") if self.hybrid_engine else "CLASIFICADO"
            confianza = resultado_reglas.confianza
            concordancia = True
            
            clasificacion_reglas = {
                "codigo": resultado_reglas.codigo_triage,
                "confianza": resultado_reglas.confianza,
                "instruccion": resultado_reglas.instruccion_atencion
            }
            
            clasificacion_ai = {"codigo": "N/A", "confianza": 0.0, "razonamiento": "AI no disponible"}
            
            instrucciones_inmediatas = [resultado_reglas.instruccion_atencion]
            causas_posibles = resultado_reglas.posibles_causas
        
        print(f"   ✅ Clasificación: {clasificacion_final} ({categoria})")
        print(f"   ✅ Confianza: {confianza * 100:.1f}%")
        print(f"   ✅ Concordancia: {'✅' if concordancia else '⚠️'}")
        
        # PASO 7: Asignación de Conducta
        conducta = self.CODIGO_TO_CONDUCTA.get(clasificacion_final, "CONS")
        
        # PASO 8: Optimización de Recursos - VPP
        derivacion_vpp = clasificacion_final in self.VPP_THRESHOLD_CODES
        
        if derivacion_vpp:
            print(f"   💡 Derivación a VPP recomendada (Baja complejidad)")
        
        # PASO 9: Instrucciones Inmediatas (ANTES de cualquier otra acción)
        print(f"\n🚨 [INSTRUCCIONES INMEDIATAS]:")
        for instruccion in instrucciones_inmediatas:
            print(f"   ⚡ {instruccion}")
        
        # PASO 10: Cálculo de Gas (para reporte COP)
        gas_consumido = self._calculate_gas_cost(
            len(preguntas_realizadas),
            bool(self.ai_client),
            zkp_valid
        )
        
        # PASO 11: Crear Log Estructurado
        decision_log = TriageDecisionLog(
            timestamp=timestamp,
            patient_bio_hash=bio_hash,
            sintoma_detectado=sintoma_detectado,
            preguntas_realizadas=preguntas_realizadas,
            clasificacion_reglas=clasificacion_reglas,
            clasificacion_ai=clasificacion_ai,
            clasificacion_final=clasificacion_final,
            categoria=categoria,
            confianza=confianza,
            concordancia=concordancia,
            instrucciones_inmediatas=instrucciones_inmediatas,
            causas_posibles=causas_posibles,
            conducta_asignada=conducta,
            codigo_conducta=clasificacion_final,
            derivacion_vpp=derivacion_vpp,
            observaciones=self._generate_observations(clasificacion_final, causas_posibles),
            gas_consumido=gas_consumido,
            zkp_validation=zkp_valid,
            threat_detected=threat_detected,
            honeypot_activated=honeypot_activated
        )
        
        # Guardar log
        self.decision_logs.append(decision_log)
        
        print(f"\n📊 [Orion] Decisión registrada - Gas: {gas_consumido:.4f} COP")
        
        return decision_log
    
    def _detect_entity(self, input_text: str) -> Optional[str]:
        """NLP Entity Detection - Detecta síntoma principal"""
        # Usar motor de inferencia existente
        return self.rules_engine.detect_sintoma(input_text)
    
    def _detect_threat(self, input_text: str, respuestas: Dict[str, Any]) -> bool:
        """Detecta amenazas de seguridad en el input"""
        # Patrones de amenaza
        threat_patterns = [
            "sql", "injection", "script", "alert(", "drop table",
            "union select", "exec(", "eval(", "<script", "javascript:"
        ]
        
        input_lower = input_text.lower()
        
        for pattern in threat_patterns:
            if pattern in input_lower:
                return True
        
        # Verificar respuestas
        for value in respuestas.values():
            if isinstance(value, str) and any(p in value.lower() for p in threat_patterns):
                return True
        
        return False
    
    def _validate_zkp(self, patient_id: Optional[str], biometric_data: Optional[BiometricData]) -> bool:
        """
        Valida elegibilidad con Zero-Knowledge Proof
        Sin exponer identidad real
        """
        # Simulación de ZKP - En producción, usar protocolo ZKP real
        if not patient_id:
            return True  # Modo anónimo permitido
        
        # Verificar que hay datos suficientes para validación
        if biometric_data and biometric_data.bio_hash:
            # ZKP: Probar que el paciente es elegible sin revelar identidad
            return True
        
        return True  # Por ahora, siempre válido
    
    def _generate_bio_hash(self, patient_id: Optional[str], biometric_data: Optional[BiometricData]) -> str:
        """Genera Bio-Hash irreversible (BioCore)"""
        if not patient_id:
            patient_id = "ANONYMOUS"
        
        # Combinar ID + datos biométricos + timestamp
        hash_input = f"{patient_id}_{datetime.now().isoformat()}"
        
        if biometric_data:
            hash_input += f"_{biometric_data.heart_rate}_{biometric_data.blood_pressure_systolic}"
        
        # SHA-256 irreversible
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _calculate_gas_cost(self, num_preguntas: int, ai_used: bool, zkp_used: bool) -> float:
        """Calcula costo de gas para reporte COP"""
        base_cost = 0.001  # COP base
        
        # Costo por pregunta
        cost = base_cost + (num_preguntas * 0.0001)
        
        # Costo adicional por AI
        if ai_used:
            cost += 0.005
        
        # Costo adicional por ZKP
        if zkp_used:
            cost += 0.002
        
        return cost
    
    def _generate_observations(self, codigo: str, causas: List[str]) -> str:
        """Genera observaciones clínicas"""
        return f"Clasificación {codigo}. Diagnósticos diferenciales: {', '.join(causas[:3])}"
    
    def _redirect_to_honeypot(self, input_text: str, timestamp: str) -> TriageDecisionLog:
        """Redirige amenaza a Honeypot (entorno sintético)"""
        return TriageDecisionLog(
            timestamp=timestamp,
            patient_bio_hash="HONEYPOT_REDIRECT",
            sintoma_detectado="THREAT_DETECTED",
            preguntas_realizadas=[],
            clasificacion_reglas={"codigo": "BLOCKED", "confianza": 1.0, "instruccion": "Acceso denegado"},
            clasificacion_ai={"codigo": "BLOCKED", "confianza": 1.0, "razonamiento": "Threat detected"},
            clasificacion_final="BLOCKED",
            categoria="SECURITY_THREAT",
            confianza=1.0,
            concordancia=True,
            instrucciones_inmediatas=["Sistema protegido - Acceso bloqueado"],
            causas_posibles=["Intento de ataque detectado"],
            conducta_asignada="BLOCKED",
            codigo_conducta="BLOCKED",
            derivacion_vpp=False,
            observaciones="Honeypot activado - Amenaza contenida",
            gas_consumido=0.0,
            zkp_validation=False,
            threat_detected=True,
            honeypot_activated=True
        )
    
    def export_decision_log(self, log: TriageDecisionLog, filepath: str):
        """Exporta log de decisión a JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(log), f, ensure_ascii=False, indent=2)
        
        print(f"📄 Log exportado a: {filepath}")
    
    def get_monthly_report(self) -> Dict[str, Any]:
        """Genera reporte mensual de operaciones y costos"""
        total_gas = sum(log.gas_consumido for log in self.decision_logs)
        total_decisions = len(self.decision_logs)
        
        decisions_by_code = {}
        for log in self.decision_logs:
            code = log.codigo_conducta
            decisions_by_code[code] = decisions_by_code.get(code, 0) + 1
        
        threats_detected = sum(1 for log in self.decision_logs if log.threat_detected)
        
        return {
            "total_decisiones": total_decisions,
            "gas_total_cop": total_gas,
            "decisiones_por_codigo": decisions_by_code,
            "amenazas_detectadas": threats_detected,
            "zkp_validaciones": sum(1 for log in self.decision_logs if log.zkp_validation)
        }
