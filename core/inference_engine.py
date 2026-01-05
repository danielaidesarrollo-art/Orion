"""
Orion Core - Motor de Inferencia
Sistema de clasificación de triage basado en reglas clínicas
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class TriageResult:
    """Resultado de la clasificación de triage"""
    codigo_triage: str
    categoria: str
    instruccion_atencion: str
    posibles_causas: List[str]
    preguntas_realizadas: List[Dict[str, Any]]
    confianza: float


class InferenceEngine:
    """
    Motor de inferencia para clasificación de triage.
    
    Flujo:
    1. Detectar síntoma principal (Entity Detection)
    2. Cargar contexto del síntoma
    3. Iterar preguntas obligatorias
    4. Evaluar reglas de clasificación
    5. Asignar código de urgencia
    """
    
    # Mapeo de códigos a categorías
    CODIGO_CATEGORIAS = {
        "D1": "EMERGENCIA",
        "D2": "URGENCIA",
        "D7": "URGENCIA BAJA COMPLEJIDAD",
        "D3": "CONSULTA PRIORITARIA"
    }
    
    # Prioridad de códigos (mayor número = mayor urgencia)
    CODIGO_PRIORIDAD = {
        "D1": 4,
        "D2": 3,
        "D7": 2,
        "D3": 1
    }
    
    def __init__(self, knowledge_base_path: str):
        """
        Inicializa el motor de inferencia.
        
        Args:
            knowledge_base_path: Ruta al archivo JSON con la base de conocimiento
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self.knowledge_base = self._load_knowledge_base()
        self.sintomas_index = self._build_sintomas_index()
    
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Carga la base de conocimiento desde JSON"""
        if not self.knowledge_base_path.exists():
            raise FileNotFoundError(f"Base de conocimiento no encontrada: {self.knowledge_base_path}")
        
        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_sintomas_index(self) -> Dict[str, Dict[str, Any]]:
        """Construye un índice de síntomas para búsqueda rápida"""
        index = {}
        for sintoma_data in self.knowledge_base:
            sintoma_key = sintoma_data["sintoma_raiz"].lower().strip()
            index[sintoma_key] = sintoma_data
        return index
    
    def detect_sintoma(self, texto_paciente: str) -> Optional[str]:
        """
        Detecta el síntoma principal del texto del paciente.
        
        Args:
            texto_paciente: Descripción del síntoma por el paciente
            
        Returns:
            Nombre del síntoma detectado o None
        """
        texto_lower = texto_paciente.lower()
        
        # Búsqueda exacta primero
        for sintoma_key in self.sintomas_index.keys():
            if sintoma_key in texto_lower:
                return sintoma_key
        
        # Búsqueda por palabras clave
        for sintoma_key in self.sintomas_index.keys():
            palabras_sintoma = sintoma_key.split()
            if any(palabra in texto_lower for palabra in palabras_sintoma if len(palabra) > 3):
                return sintoma_key
        
        return None
    
    def get_preguntas_obligatorias(self, sintoma: str) -> List[Dict[str, Any]]:
        """
        Obtiene las preguntas obligatorias para un síntoma.
        
        Args:
            sintoma: Nombre del síntoma
            
        Returns:
            Lista de preguntas obligatorias
        """
        sintoma_data = self.sintomas_index.get(sintoma.lower())
        if not sintoma_data:
            return []
        
        return sintoma_data.get("preguntas_obligatorias", [])
    
    def clasificar_triage(self, sintoma: str, respuestas: Dict[str, Any]) -> TriageResult:
        """
        Clasifica el triage basado en el síntoma y las respuestas.
        
        Args:
            sintoma: Nombre del síntoma principal
            respuestas: Diccionario con respuestas a las preguntas
            
        Returns:
            TriageResult con la clasificación y recomendaciones
        """
        sintoma_data = self.sintomas_index.get(sintoma.lower())
        if not sintoma_data:
            raise ValueError(f"Síntoma no encontrado en la base de conocimiento: {sintoma}")
        
        # Evaluar reglas de clasificación
        reglas = sintoma_data.get("reglas_clasificacion", [])
        codigo_asignado = None
        instruccion = ""
        causas = []
        confianza = 0.0
        
        # Evaluar cada regla
        for regla in reglas:
            if self._evaluar_condicion(regla["condiciones"], respuestas):
                codigo_actual = regla["codigo_triage"]
                
                # Si no hay código asignado o el actual tiene mayor prioridad
                if (codigo_asignado is None or 
                    self.CODIGO_PRIORIDAD[codigo_actual] > self.CODIGO_PRIORIDAD[codigo_asignado]):
                    codigo_asignado = codigo_actual
                    instruccion = regla["instruccion_atencion"]
                    causas = regla["posibles_causas"]
                    confianza = 0.9  # Alta confianza en regla exacta
        
        # Si no se encontró regla específica, asignar código por defecto
        if codigo_asignado is None:
            codigo_asignado = "D3"  # Consulta prioritaria por defecto
            instruccion = "Evaluación médica necesaria"
            causas = ["Requiere valoración clínica"]
            confianza = 0.5
        
        # Construir lista de preguntas realizadas
        preguntas_realizadas = []
        for pregunta in sintoma_data.get("preguntas_obligatorias", []):
            pregunta_id = pregunta["id"]
            pregunta_texto = pregunta["pregunta"]
            respuesta = respuestas.get(pregunta_id) or respuestas.get(pregunta_texto)
            
            preguntas_realizadas.append({
                "pregunta": pregunta_texto,
                "respuesta": respuesta
            })
        
        return TriageResult(
            codigo_triage=codigo_asignado,
            categoria=self.CODIGO_CATEGORIAS[codigo_asignado],
            instruccion_atencion=instruccion,
            posibles_causas=causas,
            preguntas_realizadas=preguntas_realizadas,
            confianza=confianza
        )
    
    def _evaluar_condicion(self, condicion: Dict[str, Any], respuestas: Dict[str, Any]) -> bool:
        """
        Evalúa si una condición se cumple con las respuestas dadas.
        
        Args:
            condicion: Diccionario con la condición a evaluar
            respuestas: Respuestas del paciente
            
        Returns:
            True si la condición se cumple
        """
        pregunta = condicion.get("pregunta", "").lower()
        respuesta_esperada = condicion.get("respuesta_esperada", "").lower()
        
        if not pregunta or not respuesta_esperada:
            return False
        
        # Buscar la respuesta correspondiente
        for key, value in respuestas.items():
            if pregunta in key.lower():
                respuesta_actual = str(value).lower()
                
                # Evaluar respuesta
                if respuesta_esperada in ["si", "sí", "yes"]:
                    return respuesta_actual in ["si", "sí", "yes", "true", "1"]
                elif respuesta_esperada in ["no"]:
                    return respuesta_actual in ["no", "false", "0"]
                else:
                    return respuesta_esperada in respuesta_actual
        
        return False
    
    def get_recomendaciones(self, sintoma: str) -> List[str]:
        """
        Obtiene las recomendaciones generales para un síntoma.
        
        Args:
            sintoma: Nombre del síntoma
            
        Returns:
            Lista de recomendaciones
        """
        sintoma_data = self.sintomas_index.get(sintoma.lower())
        if not sintoma_data:
            return []
        
        return sintoma_data.get("recomendaciones", [])
