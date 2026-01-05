# 🔶 Orion Omega - Módulo de Triage

<div align="center">

![Orion Emergency Module](assets/logo.jpg)

**Clasificación Inteligente de Emergencias en Tiempo Real**

</div>

## 📋 Descripción

**Orion Omega** es el módulo de triage del sistema Orion Emergency Module. Utiliza un motor híbrido que combina reglas clínicas con inteligencia artificial (Med-Gemma) para clasificar casos de emergencia con alta precisión y confiabilidad.

## 🎯 Funcionalidades Principales

### 1. Clasificación Dual
- ✅ **Motor de Reglas**: Clasificación basada en protocolos clínicos
- ✅ **Med-Gemma AI**: Validación con inteligencia artificial médica
- ✅ **Validación Cruzada**: Detección automática de discordancias
- ✅ **Escalamiento Inteligente**: Priorización en casos de duda

### 2. API REST
- ✅ **FastAPI**: Alto rendimiento y documentación automática
- ✅ **Swagger UI**: Interfaz interactiva en `/docs`
- ✅ **Endpoints**: Clasificación, síntomas, estadísticas
- ✅ **Validación**: Esquemas Pydantic

### 3. Códigos de Triage

| Código | Categoría | Tiempo | Descripción |
|--------|-----------|--------|-------------|
| **D1** | EMERGENCIA | < 5 min | Riesgo vital inmediato |
| **D2** | URGENCIA | < 30 min | Atención prioritaria |
| **D7** | URGENCIA BAJA | < 2 hrs | Requiere atención |
| **D3** | CONSULTA | < 4 hrs | Evaluación médica |

## 🚀 Inicio Rápido

### 1. Iniciar el Servidor

```bash
python api\triage_api.py
```

Servidor disponible en: **http://localhost:8000**

### 2. Acceder a Swagger UI

Abre en tu navegador: **http://localhost:8000/docs**

### 3. Clasificar un Caso

**Endpoint**: `POST /api/triage`

```json
{
  "sintoma": "dolor toracico",
  "respuestas": {
    "¿El dolor comenzó de forma brusca?": "si",
    "¿Presenta dificultad para respirar?": "si",
    "¿Irradiación a brazo izquierdo?": "si"
  }
}
```

**Respuesta**:

```json
{
  "codigo": "D1",
  "categoria": "EMERGENCIA",
  "confianza": 0.97,
  "concordancia": true,
  "razonamiento_reglas": "Dolor torácico con criterios de IAM",
  "razonamiento_ai": "Alta probabilidad de síndrome coronario agudo",
  "requiere_revision": false
}
```

## 🧪 Ejemplos de Uso

### Caso 1: Emergencia (IAM)

```python
from core.hybrid_engine import HybridTriageEngine

resultado = hybrid.classify(
    sintoma="dolor toracico",
    respuestas={
        "¿El dolor comenzó de forma brusca?": "si",
        "¿Presenta dificultad para respirar?": "si",
        "¿Irradiación a brazo izquierdo?": "si"
    }
)

# Resultado:
# Código: D1 (EMERGENCIA)
# Confianza: 0.97
# Concordancia: ✅ (Reglas + AI concuerdan)
```

### Caso 2: Discordancia (Alerta)

```python
resultado = hybrid.classify(
    sintoma="confusion",
    respuestas={
        "¿Presenta fiebre?": "no",
        "¿Responde a estímulos?": "si"
    }
)

# Resultado:
# Código: D1 (escalado por AI)
# Confianza: 0.75
# Concordancia: ⚠️ (Reglas: D3, AI: D1)
# Requiere revisión: ✅
```

## 📁 Archivos Principales

```
orion-core/
├── api/
│   └── triage_api.py             # API REST FastAPI
├── core/
│   ├── inference_engine.py       # Motor de reglas
│   ├── medgemma_client.py        # Cliente Med-Gemma
│   └── hybrid_engine.py          # Motor híbrido
└── data/
    └── triage_knowledge_base.json # Base de conocimiento
```

## 🔄 Flujo de Clasificación

```
┌─────────────────┐
│   Caso Nuevo    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ Reglas │ │Med-Gemma │
│Clínicas│ │    AI    │
└───┬────┘ └────┬─────┘
    │           │
    └─────┬─────┘
          ▼
   ┌──────────────┐
   │  Validación  │
   │   Cruzada    │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Clasificación│
   │    Final     │
   └──────────────┘
```

## 🔗 Integración con Orion Alfa

Orion Omega consume la base de conocimiento generada por **Orion Alfa** para realizar la clasificación de casos.

```
Orion Alfa (Admin) → Base de Conocimiento → Orion Omega (Triage)
```

## 📚 Documentación Relacionada

- [README Principal](README.md)
- [Orion Alfa - Módulo Administrativo](ORION_ALFA.md)
- [Integración Med-Gemma](MEDGEMMA_INTEGRATION.md)
- [Inicio Rápido](INICIO_RAPIDO.md)

---

**Orion Omega** - Triage Inteligente, Robusto y Confiable 🔶
