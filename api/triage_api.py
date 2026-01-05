"""
Orion Emergency Module - API REST
🔶 Orion Omega - Módulo de Triage
API para clasificación inteligente de triage de urgencias
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from core.inference_engine import InferenceEngine, TriageResult


# Modelos de datos
class TriageRequest(BaseModel):
    """Solicitud de clasificación de triage"""
    sintoma: Optional[str] = Field(None, description="Síntoma principal (opcional si se proporciona texto_paciente)")
    texto_paciente: Optional[str] = Field(None, description="Descripción del paciente para detección automática")
    respuestas: Dict[str, Any] = Field(default_factory=dict, description="Respuestas a preguntas obligatorias")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sintoma": "dolor toracico",
                "respuestas": {
                    "inicio_brusco": "si",
                    "intensidad": "alta",
                    "irradiacion": "brazo izquierdo"
                }
            }
        }


class PreguntasResponse(BaseModel):
    """Respuesta con preguntas obligatorias"""
    sintoma: str
    preguntas: List[Dict[str, Any]]


class TriageResponse(BaseModel):
    """Respuesta de clasificación de triage"""
    codigo_triage: str
    categoria: str
    instruccion_atencion: str
    posibles_causas: List[str]
    preguntas_realizadas: List[Dict[str, Any]]
    confianza: float
    recomendaciones: List[str]


class SintomasResponse(BaseModel):
    """Lista de síntomas disponibles"""
    sintomas: List[str]
    total: int


# Inicializar FastAPI
app = FastAPI(
    title="🔶 Orion Omega API",
    description="Módulo de Triage - Sistema de Clasificación Inteligente de Urgencias",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta a la base de conocimiento
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent / "data" / "triage_knowledge_base.json"

# Instancia global del motor de inferencia
inference_engine: Optional[InferenceEngine] = None


def get_inference_engine() -> InferenceEngine:
    """Dependency para obtener el motor de inferencia"""
    global inference_engine
    
    if inference_engine is None:
        if not KNOWLEDGE_BASE_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Base de conocimiento no encontrada. Ejecute el ETL primero."
            )
        inference_engine = InferenceEngine(str(KNOWLEDGE_BASE_PATH))
    
    return inference_engine


@app.get("/api/info")
async def api_info():
    """Información de la API"""
    return {
        "nombre": "🔶 Orion Omega API",
        "modulo": "Triage",
        "version": "1.0.0",
        "descripcion": "Módulo de Triage - Clasificación Inteligente de Urgencias",
        "arquitectura": {
            "orion_alfa": "Módulo Administrativo (Gestión de Protocolos)",
            "orion_omega": "Módulo de Triage (Clasificación en Tiempo Real)"
        },
        "endpoints": {
            "sintomas": "/api/sintomas",
            "preguntas": "/api/preguntas/{sintoma}",
            "clasificar": "/api/triage"
        }
    }


# Montar archivos estáticos para el frontend
# Esto debe ir AL FINAL para no bloquear las rutas de la API
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/api/sintomas", response_model=SintomasResponse)
async def listar_sintomas(engine: InferenceEngine = Depends(get_inference_engine)):
    """
    Lista todos los síntomas disponibles en la base de conocimiento.
    """
    sintomas = list(engine.sintomas_index.keys())
    return SintomasResponse(
        sintomas=sintomas,
        total=len(sintomas)
    )


@app.get("/api/preguntas/{sintoma}", response_model=PreguntasResponse)
async def obtener_preguntas(
    sintoma: str,
    engine: InferenceEngine = Depends(get_inference_engine)
):
    """
    Obtiene las preguntas obligatorias para un síntoma específico.
    """
    preguntas = engine.get_preguntas_obligatorias(sintoma)
    
    if not preguntas:
        raise HTTPException(
            status_code=404,
            detail=f"Síntoma no encontrado: {sintoma}"
        )
    
    return PreguntasResponse(
        sintoma=sintoma,
        preguntas=preguntas
    )


@app.post("/api/triage", response_model=TriageResponse)
async def clasificar_triage(
    request: TriageRequest,
    engine: InferenceEngine = Depends(get_inference_engine)
):
    """
    Clasifica el triage basado en el síntoma y las respuestas.
    
    - **sintoma**: Síntoma principal (opcional si se proporciona texto_paciente)
    - **texto_paciente**: Descripción del paciente para detección automática
    - **respuestas**: Diccionario con respuestas a preguntas obligatorias
    """
    # Detectar síntoma si no se proporciona
    sintoma = request.sintoma
    
    if not sintoma and request.texto_paciente:
        sintoma = engine.detect_sintoma(request.texto_paciente)
        if not sintoma:
            raise HTTPException(
                status_code=400,
                detail="No se pudo detectar el síntoma. Proporcione el síntoma explícitamente."
            )
    
    if not sintoma:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar 'sintoma' o 'texto_paciente'"
        )
    
    # Clasificar triage
    try:
        resultado = engine.clasificar_triage(sintoma, request.respuestas)
        recomendaciones = engine.get_recomendaciones(sintoma)
        
        return TriageResponse(
            codigo_triage=resultado.codigo_triage,
            categoria=resultado.categoria,
            instruccion_atencion=resultado.instruccion_atencion,
            posibles_causas=resultado.posibles_causas,
            preguntas_realizadas=resultado.preguntas_realizadas,
            confianza=resultado.confianza,
            recomendaciones=recomendaciones
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en clasificación: {str(e)}")


@app.get("/api/metrics")
async def get_metrics():
    """Obtener métricas del sistema para el dashboard administrativo"""
    import random
    import time
    
    # Simulación de métricas en tiempo real
    return {
        "triage_count": random.randint(120, 150),
        "accuracy": round(random.uniform(98.0, 99.9), 1),
        "latency_ms": random.randint(8, 25),
        "epoch": 204 + int(time.time() / 3600),  # Simular avance de entrenamiento
        "active_nodes": 3,
        "system_status": "OPTIMAL"
    }


@app.get("/health")
async def health_check():
    """Endpoint de salud"""
    return {
        "status": "healthy",
        "knowledge_base_loaded": inference_engine is not None,
        "knowledge_base_path": str(KNOWLEDGE_BASE_PATH)
    }


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("🔶 Orion Omega - Módulo de Triage")
    print("🚀 Iniciando API de Clasificación Inteligente...")
    print(f"📊 Base de conocimiento: {KNOWLEDGE_BASE_PATH}")
    print("="*60)
    
    uvicorn.run(
        "triage_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
