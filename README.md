<div align="center">

![Orion Emergency Module](assets/logo.jpg)

# Orion Emergency Module

**Sistema Híbrido de Triage de Urgencias**

Sistema inteligente que combina reglas clínicas + IA médica (Med-Gemma) para clasificación de triage robusta y confiable.

---

### 🔷 Orion Alfa | Módulo Administrativo
Gestión, configuración y supervisión del sistema

### 🔶 Orion Omega | Módulo de Triage
Clasificación inteligente y atención de emergencias

</div>

## 🎯 Características Principales

- ✅ **Doble Clasificación**: Reglas clínicas + Med-Gemma AI
- ✅ **Validación Cruzada**: Detección de discordancias
- ✅ **Explicabilidad Total**: Razonamiento dual transparente
- ✅ **Alta Confiabilidad**: Sistema de alertas y escalamiento
- ✅ **ETL Flexible**: Procesa Excel y CSV
- ✅ **API REST**: FastAPI con documentación Swagger
- ✅ **Cumplimiento**: Preparado para integración SafeCore (HIPAA)

## 🚀 Inicio Rápido

### 1. Clonar Repositorio

```bash
git clone https://github.com/danielaidesarrollo-art/Orion.git
cd Orion
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
pip install -r requirements-medgemma.txt  # Para integración Med-Gemma
```

### 3. Configurar (Opcional: Med-Gemma)

```bash
# Obtener API key en: https://makersuite.google.com/app/apikey
$env:GOOGLE_API_KEY = "tu-api-key"
```

### 4. Iniciar API

```bash
python api\triage_api.py
```

Accede a: **http://localhost:8000/docs**

## 📊 Arquitectura

```
┌─────────────────┐
│  Google Sheets  │
│   (Protocolos)  │
└────────┬────────┘
         │ ETL
         ▼
┌─────────────────┐
│  Base de        │
│  Conocimiento   │
│  (JSON)         │
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
   │   Motor      │
   │   Híbrido    │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  API REST    │
   │  (FastAPI)   │
   └──────────────┘
```

## 📁 Estructura del Proyecto

```
Orion/
├── api/
│   └── triage_api.py          # API REST FastAPI
├── core/
│   ├── inference_engine.py    # Motor de reglas
│   ├── medgemma_client.py     # Cliente Med-Gemma
│   └── hybrid_engine.py       # Motor híbrido
├── data/
│   ├── ejemplo_triage.json    # Datos de ejemplo
│   └── triage_knowledge_base.json
├── etl/
│   └── excel_transformer.py   # Transformador ETL
├── scripts/
│   ├── descargar_google_sheets.py
│   └── demo_api.py
├── tests/
│   └── test_inference.py
├── README.md
├── MEDGEMMA_INTEGRATION.md    # Guía de integración AI
└── requirements.txt
```

## 🔄 Flujo de Trabajo

### 1. Importar Datos de Triage

```bash
# Opción A: Desde Google Sheets
python scripts\descargar_google_sheets.py

# Opción B: Desde Excel local
python etl\excel_transformer.py --input data\triage_urgencias.xlsx
```

### 2. Clasificar Casos

**Solo Reglas**:
```python
from core.inference_engine import InferenceEngine

engine = InferenceEngine("data/triage_knowledge_base.json")
resultado = engine.clasificar_triage("dolor toracico", respuestas)
```

**Híbrido (Reglas + AI)**:
```python
from core.hybrid_engine import HybridTriageEngine

hybrid = HybridTriageEngine(rules_engine, ai_client)
resultado = hybrid.classify("dolor toracico", respuestas)
```

### 3. Usar API

```bash
POST http://localhost:8000/api/triage
{
  "sintoma": "dolor toracico",
  "respuestas": {
    "¿El dolor comenzó de forma brusca?": "si"
  }
}
```

## 📋 Códigos de Triage

| Código | Categoría | Tiempo | Descripción |
|--------|-----------|--------|-------------|
| **D1** | EMERGENCIA | < 5 min | Riesgo vital inmediato |
| **D2** | URGENCIA | < 30 min | Atención prioritaria |
| **D7** | URGENCIA BAJA | < 2 hrs | Requiere atención |
| **D3** | CONSULTA | < 4 hrs | Evaluación médica |

## 🧪 Ejemplos de Uso

### Caso 1: Emergencia (IAM)

```python
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

## 🔒 Seguridad y Cumplimiento

### Actual
- ✅ API REST segura
- ✅ Validación de datos
- ✅ Logging de decisiones

### Futuro (SafeCore)
- 🔮 Zero-Knowledge Proof
- 🔮 Auditoría inmutable (HIPAA)
- 🔮 Encriptación end-to-end
- 🔮 Trazabilidad completa

## 📚 Documentación

- [README.md](README.md) - Este archivo
- [🔷 ORION_ALFA.md](ORION_ALFA.md) - Módulo Administrativo
- [🔶 ORION_OMEGA.md](ORION_OMEGA.md) - Módulo de Triage
- [MEDGEMMA_INTEGRATION.md](MEDGEMMA_INTEGRATION.md) - Guía de integración AI
- [IMPORTAR_DATOS.md](IMPORTAR_DATOS.md) - Cómo importar datos
- [INICIO_RAPIDO.md](INICIO_RAPIDO.md) - Guía de inicio rápido

## 🤝 Contribuir

Este proyecto es parte del ecosistema Daniel_AI para sistemas de salud inteligentes.

## 📄 Licencia

Proyecto propietario - Daniel AI Development

## 🔗 Enlaces

- **GitHub**: https://github.com/danielaidesarrollo-art/Orion
- **SafeCore**: https://github.com/danielaidesarrollo-art/SafeCore
- **BioCore**: https://github.com/danielaidesarrollo-art/BioCore
- **Med-Gemma**: https://ai.google.dev/

---

**Orion** - Triage Inteligente, Robusto y Confiable 🚀
