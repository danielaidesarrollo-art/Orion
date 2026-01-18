"""
Orion Core - Motor Híbrido
Combina clasificación por reglas + Med-Gemma AI
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from core.inference_engine import InferenceEngine, TriageResult
from core.medgemma_client import MedGemmaClient, MedGemmaResult


@dataclass
class HybridTriageResult:
    """Resultado de clasificación híbrida (Reglas + AI)"""
    
    # Clasificación final
    codigo_triage: str
    categoria: str
    confianza: float
    
    # Resultados individuales
    resultado_reglas: TriageResult
    resultado_ai: MedGemmaResult
    
    # Validación cruzada
    concordancia: bool
    requiere_revision: bool
    nivel_alerta: str  # "ninguno", "bajo", "medio", "alto"
    
    # Explicabilidad
    explicacion_final: str
    razonamiento_combinado: str


class HybridTriageEngine:
    """
    Motor de triage híbrido que combina:
    1. Sistema de reglas clínicas (Orion Core)
    2. Inteligencia artificial médica (Med-Gemma)
    
    Ventajas:
    - Doble validación para mayor confiabilidad
    - Detección de casos atípicos
    - Explicabilidad completa
    - Fallback si AI falla
    """
    
    # Prioridad de códigos (mayor = más urgente)
    PRIORIDAD_CODIGOS = {
        "D1": 4,  # Emergencia
        "D2": 3,  # Urgencia
        "D7": 2,  # Urgencia baja complejidad
        "D3": 1   # Consulta prioritaria
    }
    
    CATEGORIAS = {
        "D1": "EMERGENCIA",
        "D2": "URGENCIA",
        "D7": "URGENCIA BAJA COMPLEJIDAD",
        "D3": "CONSULTA PRIORITARIA"
    }
    
    def __init__(self, 
                 rules_engine: InferenceEngine,
                 ai_client: Optional[MedGemmaClient] = None,
                 peso_reglas: float = 0.4,
                 peso_ai: float = 0.6):
        """
        Inicializa el motor híbrido
        
        Args:
            rules_engine: Motor de inferencia basado en reglas
            ai_client: Cliente de Med-Gemma (opcional)
            peso_reglas: Peso de la clasificación por reglas (0-1)
            peso_ai: Peso de la clasificación por AI (0-1)
        """
        self.rules_engine = rules_engine
        self.ai_client = ai_client
        self.peso_reglas = peso_reglas
        self.peso_ai = peso_ai
        
        # Modo de operación
        self.modo = "hybrid" if ai_client else "rules_only"
    
    def classify(self, sintoma: str, respuestas: Dict[str, Any], images: Optional[List[Any]] = None) -> HybridTriageResult:
        """
        Clasifica un caso usando el sistema híbrido (Soporte Multimodal)
        
        Args:
            sintoma: Síntoma principal
            respuestas: Respuestas a preguntas obligatorias
            images: Imágenes clínicas (opcional)
            
        Returns:
            HybridTriageResult con clasificación combinada
        """
        # 1. Clasificación por reglas (siempre)
        resultado_reglas = self.rules_engine.clasificar_triage(sintoma, respuestas)
        
        # 2. Clasificación por AI (si está disponible)
        if self.modo == "hybrid" and self.ai_client:
            try:
                # Pasar imágenes a Med-Gemma
                resultado_ai = self.ai_client.classify(sintoma, respuestas, images)
            except Exception as e:
                print(f"⚠️ Med-Gemma falló, usando solo reglas: {e}")
                # Fallback a solo reglas
                return self._create_rules_only_result(resultado_reglas)
        else:
            # Modo solo reglas
            return self._create_rules_only_result(resultado_reglas)
        
        # 3. Validación cruzada
        resultado_final = self._cross_validate(resultado_reglas, resultado_ai)
        
        return resultado_final
    
    def _cross_validate(self, 
                       reglas: TriageResult, 
                       ai: MedGemmaResult) -> HybridTriageResult:
        """
        Valida cruzadamente los resultados de reglas y AI
        
        Estrategia:
        - Concordancia perfecta → Confianza máxima
        - Discordancia leve (1 nivel) → Escalar al más grave
        - Discordancia alta (2+ niveles) → Alerta + revisión médica
        """
        
        # Verificar concordancia
        concordancia = (reglas.codigo_triage == ai.codigo_triage)
        
        # Calcular diferencia de prioridad
        prioridad_reglas = self.PRIORIDAD_CODIGOS[reglas.codigo_triage]
        prioridad_ai = self.PRIORIDAD_CODIGOS[ai.codigo_triage]
        diferencia = abs(prioridad_reglas - prioridad_ai)
        
        # Determinar código final y nivel de alerta
        if concordancia:
            # Concordancia perfecta
            codigo_final = reglas.codigo_triage
            confianza_base = max(reglas.confianza, ai.confianza)
            bonus_concordancia = 0.1
            confianza_final = min(1.0, confianza_base + bonus_concordancia)
            nivel_alerta = "ninguno"
            requiere_revision = False
            
            explicacion = (
                f"✅ CONCORDANCIA PERFECTA: Ambos sistemas clasifican como {codigo_final}. "
                f"Alta confianza en la decisión."
            )
        
        elif diferencia == 1:
            # Discordancia leve (1 nivel)
            codigo_final = self._escalar_codigo(reglas.codigo_triage, ai.codigo_triage)
            confianza_final = (
                self.peso_reglas * reglas.confianza + 
                self.peso_ai * ai.confianza
            )
            nivel_alerta = "bajo"
            requiere_revision = False
            
            explicacion = (
                f"⚠️ DISCORDANCIA LEVE: Reglas={reglas.codigo_triage}, AI={ai.codigo_triage}. "
                f"Escalando a {codigo_final} por precaución."
            )
        
        else:
            # Discordancia alta (2+ niveles)
            codigo_final = self._escalar_codigo(reglas.codigo_triage, ai.codigo_triage)
            confianza_final = min(reglas.confianza, ai.confianza) * 0.7
            nivel_alerta = "alto" if diferencia >= 3 else "medio"
            requiere_revision = True
            
            explicacion = (
                f"🔴 DISCORDANCIA ALTA: Reglas={reglas.codigo_triage}, AI={ai.codigo_triage}. "
                f"Clasificando como {codigo_final}. REQUIERE REVISIÓN MÉDICA."
            )
        
        # Construir razonamiento combinado
        razonamiento = self._build_combined_reasoning(reglas, ai, concordancia)
        
        return HybridTriageResult(
            codigo_triage=codigo_final,
            categoria=self.CATEGORIAS[codigo_final],
            confianza=confianza_final,
            resultado_reglas=reglas,
            resultado_ai=ai,
            concordancia=concordancia,
            requiere_revision=requiere_revision,
            nivel_alerta=nivel_alerta,
            explicacion_final=explicacion,
            razonamiento_combinado=razonamiento
        )
    
    def _escalar_codigo(self, codigo1: str, codigo2: str) -> str:
        """Escala al código más grave (conservador)"""
        prioridad1 = self.PRIORIDAD_CODIGOS[codigo1]
        prioridad2 = self.PRIORIDAD_CODIGOS[codigo2]
        
        return codigo1 if prioridad1 > prioridad2 else codigo2
    
    def _build_combined_reasoning(self, 
                                  reglas: TriageResult, 
                                  ai: MedGemmaResult,
                                  concordancia: bool) -> str:
        """Construye razonamiento combinado"""
        
        razonamiento = "## ANÁLISIS DUAL\n\n"
        
        # Razonamiento de reglas
        razonamiento += "### 📋 Sistema de Reglas Clínicas\n"
        razonamiento += f"**Código**: {reglas.codigo_triage}\n"
        razonamiento += f"**Confianza**: {reglas.confianza * 100:.0f}%\n"
        razonamiento += f"**Instrucción**: {reglas.instruccion_atencion}\n"
        razonamiento += f"**Causas posibles**: {', '.join(reglas.posibles_causas)}\n\n"
        
        # Razonamiento de AI
        razonamiento += "### 🤖 Inteligencia Artificial Médica (Med-Gemma)\n"
        razonamiento += f"**Código**: {ai.codigo_triage}\n"
        razonamiento += f"**Confianza**: {ai.confianza * 100:.0f}%\n"
        razonamiento += f"**Razonamiento**: {ai.razonamiento}\n"
        razonamiento += f"**Diagnósticos diferenciales**: {', '.join(ai.diagnosticos_diferenciales)}\n"
        
        if ai.recomendaciones_adicionales:
            razonamiento += f"**Recomendaciones**: {', '.join(ai.recomendaciones_adicionales)}\n"
        
        razonamiento += "\n"
        
        # Conclusión
        if concordancia:
            razonamiento += "### ✅ Conclusión\n"
            razonamiento += "Ambos sistemas concuerdan. Alta confianza en la clasificación.\n"
        else:
            razonamiento += "### ⚠️ Conclusión\n"
            razonamiento += (
                "Discordancia detectada entre sistemas. "
                "Se recomienda evaluación médica adicional para confirmar clasificación.\n"
            )
        
        return razonamiento
    
    def _create_rules_only_result(self, reglas: TriageResult) -> HybridTriageResult:
        """Crea resultado cuando solo hay clasificación por reglas"""
        
        # Crear resultado AI vacío
        ai_dummy = MedGemmaResult(
            codigo_triage=reglas.codigo_triage,
            confianza=0.0,
            razonamiento="Med-Gemma no disponible",
            diagnosticos_diferenciales=[],
            recomendaciones_adicionales=[]
        )
        
        return HybridTriageResult(
            codigo_triage=reglas.codigo_triage,
            categoria=self.CATEGORIAS[reglas.codigo_triage],
            confianza=reglas.confianza,
            resultado_reglas=reglas,
            resultado_ai=ai_dummy,
            concordancia=True,
            requiere_revision=False,
            nivel_alerta="ninguno",
            explicacion_final="Clasificación basada únicamente en reglas clínicas (Med-Gemma no disponible)",
            razonamiento_combinado=f"**Sistema de Reglas**: {reglas.instruccion_atencion}"
        )
