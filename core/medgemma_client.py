"""
Orion Core - Cliente Med-Gemma
Integración con el modelo médico especializado de Google
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import google.generativeai as genai


@dataclass
class MedGemmaResult:
    """Resultado de clasificación de Med-Gemma"""
    codigo_triage: str
    confianza: float
    razonamiento: str
    diagnosticos_diferenciales: List[str]
    recomendaciones_adicionales: List[str]


class MedGemmaClient:
    """
    Cliente para interactuar con Med-Gemma (modelo médico de Google)
    
    Soporta:
    - Google AI API (cloud)
    - Vertex AI (enterprise)
    - Ollama (local)
    """
    
    # Mapeo de códigos de triage
    CODIGOS_TRIAGE = {
        "D1": "EMERGENCIA - Riesgo vital inmediato",
        "D2": "URGENCIA - Atención prioritaria",
        "D7": "URGENCIA BAJA COMPLEJIDAD - Requiere atención",
        "D3": "CONSULTA PRIORITARIA - Evaluación médica necesaria"
    }
    
    def __init__(self, mode: str = "google_ai", api_key: Optional[str] = None):
        """
        Inicializa el cliente Med-Gemma
        
        Args:
            mode: "google_ai", "vertex_ai", o "ollama"
            api_key: API key de Google (solo para google_ai)
        """
        self.mode = mode
        
        if mode == "google_ai":
            api_key = api_key or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY no configurada")
            
            genai.configure(api_key=api_key)
            # Usar Gemini 2.0 Flash con capacidades médicas
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
        elif mode == "vertex_ai":
            # TODO: Implementar Vertex AI
            raise NotImplementedError("Vertex AI no implementado aún")
            
        elif mode == "ollama":
            # TODO: Implementar Ollama local
            raise NotImplementedError("Ollama no implementado aún")
        
        else:
            raise ValueError(f"Modo no soportado: {mode}")
    
    def classify(self, sintoma: str, respuestas: Dict[str, Any]) -> MedGemmaResult:
        """
        Clasifica un caso de triage usando Med-Gemma
        
        Args:
            sintoma: Síntoma principal
            respuestas: Diccionario con respuestas a preguntas
            
        Returns:
            MedGemmaResult con clasificación y razonamiento
        """
        # Construir prompt médico
        prompt = self._build_medical_prompt(sintoma, respuestas)
        
        # Obtener respuesta del modelo
        response = self._query_model(prompt)
        
        # Parsear respuesta
        result = self._parse_response(response)
        
        return result
    
    def _build_medical_prompt(self, sintoma: str, respuestas: Dict[str, Any]) -> str:
        """Construye el prompt médico para Med-Gemma"""
        
        # Formatear respuestas
        respuestas_texto = "\n".join([
            f"- {pregunta}: {respuesta}"
            for pregunta, respuesta in respuestas.items()
        ])
        
        prompt = f"""Eres un médico de urgencias experto con amplia experiencia en clasificación de triage.

CASO CLÍNICO:
Síntoma principal: {sintoma.upper()}

Hallazgos clínicos:
{respuestas_texto}

TAREA:
Clasifica este caso según los siguientes códigos de triage:

- **D1 (EMERGENCIA)**: Riesgo vital inmediato, requiere atención en < 5 minutos
  Ejemplos: IAM, ACV, shock, paro respiratorio inminente
  
- **D2 (URGENCIA)**: Condición grave que requiere atención prioritaria en < 30 minutos
  Ejemplos: Angina inestable, sepsis, trauma moderado-severo
  
- **D7 (URGENCIA BAJA COMPLEJIDAD)**: Requiere atención médica pero sin riesgo inmediato
  Ejemplos: Fracturas simples, infecciones no complicadas
  
- **D3 (CONSULTA PRIORITARIA)**: Evaluación médica necesaria pero puede esperar
  Ejemplos: Síntomas inespecíficos, seguimiento de condiciones crónicas

INSTRUCCIONES:
1. Analiza el caso considerando:
   - Gravedad de los síntomas
   - Riesgo de deterioro rápido
   - Diagnósticos diferenciales más probables
   - Necesidad de intervención inmediata

2. Responde ÚNICAMENTE en formato JSON válido (sin markdown, sin ```json):

{{
  "codigo_triage": "D1",
  "confianza": 0.95,
  "razonamiento": "Explicación clínica detallada de por qué este código",
  "diagnosticos_diferenciales": ["Diagnóstico 1", "Diagnóstico 2", "Diagnóstico 3"],
  "recomendaciones_adicionales": ["Recomendación 1", "Recomendación 2"]
}}

IMPORTANTE:
- Sé conservador: en caso de duda, escala al código más grave
- Proporciona razonamiento clínico claro y específico
- Lista los diagnósticos diferenciales más probables
- Incluye recomendaciones de manejo inmediato

Responde ahora:"""
        
        return prompt
    
    def _query_model(self, prompt: str) -> str:
        """Consulta al modelo Med-Gemma"""
        
        if self.mode == "google_ai":
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Baja temperatura para respuestas consistentes
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=1024,
                    )
                )
                return response.text
            
            except Exception as e:
                raise RuntimeError(f"Error al consultar Med-Gemma: {e}")
        
        else:
            raise NotImplementedError(f"Modo {self.mode} no implementado")
    
    def _parse_response(self, response: str) -> MedGemmaResult:
        """Parsea la respuesta JSON de Med-Gemma"""
        
        try:
            # Limpiar respuesta (remover markdown si existe)
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            response_clean = response_clean.strip()
            
            # Parsear JSON
            data = json.loads(response_clean)
            
            # Validar código de triage
            codigo = data.get("codigo_triage", "").upper()
            if codigo not in self.CODIGOS_TRIAGE:
                raise ValueError(f"Código de triage inválido: {codigo}")
            
            # Validar confianza
            confianza = float(data.get("confianza", 0.5))
            if not 0.0 <= confianza <= 1.0:
                confianza = max(0.0, min(1.0, confianza))
            
            return MedGemmaResult(
                codigo_triage=codigo,
                confianza=confianza,
                razonamiento=data.get("razonamiento", ""),
                diagnosticos_diferenciales=data.get("diagnosticos_diferenciales", []),
                recomendaciones_adicionales=data.get("recomendaciones_adicionales", [])
            )
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Respuesta de Med-Gemma no es JSON válido: {e}\nRespuesta: {response}")
        
        except Exception as e:
            raise ValueError(f"Error al parsear respuesta de Med-Gemma: {e}")
    
    def classify_with_context(self, sintoma: str, respuestas: Dict[str, Any], 
                             contexto_adicional: str = "") -> MedGemmaResult:
        """
        Clasifica con contexto adicional del paciente
        
        Args:
            sintoma: Síntoma principal
            respuestas: Respuestas a preguntas
            contexto_adicional: Información adicional (ej: antecedentes, medicamentos)
        """
        prompt = self._build_medical_prompt(sintoma, respuestas)
        
        if contexto_adicional:
            prompt += f"\n\nCONTEXTO ADICIONAL DEL PACIENTE:\n{contexto_adicional}\n"
        
        response = self._query_model(prompt)
        return self._parse_response(response)


# Función de utilidad para pruebas rápidas
def test_medgemma_client():
    """Prueba rápida del cliente Med-Gemma"""
    
    print("🧪 Probando cliente Med-Gemma...\n")
    
    # Verificar API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY no configurada")
        print("   Configura la variable de entorno:")
        print("   $env:GOOGLE_API_KEY = 'tu-api-key'")
        return
    
    try:
        # Inicializar cliente
        client = MedGemmaClient(mode="google_ai")
        print("✅ Cliente Med-Gemma inicializado\n")
        
        # Caso de prueba: Dolor torácico
        print("📋 Caso de prueba: Dolor torácico con síntomas de IAM")
        
        resultado = client.classify(
            sintoma="dolor toracico",
            respuestas={
                "¿El dolor comenzó de forma brusca?": "si",
                "¿El dolor se irradia al brazo izquierdo?": "si",
                "¿Presenta dificultad para respirar?": "si",
                "¿Presenta sudoración fría?": "si"
            }
        )
        
        print(f"\n🎯 RESULTADO:")
        print(f"   Código: {resultado.codigo_triage}")
        print(f"   Confianza: {resultado.confianza * 100}%")
        print(f"\n💭 Razonamiento:")
        print(f"   {resultado.razonamiento}")
        print(f"\n🔍 Diagnósticos diferenciales:")
        for dx in resultado.diagnosticos_diferenciales:
            print(f"   - {dx}")
        
        print("\n✅ Prueba completada exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    test_medgemma_client()
