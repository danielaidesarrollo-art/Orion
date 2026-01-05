# 🚀 Orion Core + Med-Gemma - Guía de Integración

Sistema Híbrido de Triage: Reglas Clínicas + IA Médica

## 📋 Requisitos Previos

1. **API Key de Google AI**
   - Obtén tu API key en: https://makersuite.google.com/app/apikey
   - O usa Google Cloud Vertex AI para enterprise

2. **Instalar Dependencias**
   ```bash
   pip install -r requirements-medgemma.txt
   ```

3. **Configurar API Key**
   ```powershell
   # Windows PowerShell
   $env:GOOGLE_API_KEY = "tu-api-key-aqui"
   
   # O crear archivo .env
   echo "GOOGLE_API_KEY=tu-api-key-aqui" > .env
   ```

---

## 🧪 Prueba Rápida de Med-Gemma

```bash
python core\medgemma_client.py
```

Esto ejecutará un caso de prueba con dolor torácico y mostrará:
- Clasificación de Med-Gemma
- Nivel de confianza
- Razonamiento clínico
- Diagnósticos diferenciales

---

## 🔄 Usar el Sistema Híbrido

### Opción 1: Desde Python

```python
from core.inference_engine import InferenceEngine
from core.medgemma_client import MedGemmaClient
from core.hybrid_engine import HybridTriageEngine

# Inicializar componentes
rules_engine = InferenceEngine("data/triage_knowledge_base.json")
ai_client = MedGemmaClient(mode="google_ai")
hybrid_engine = HybridTriageEngine(rules_engine, ai_client)

# Clasificar un caso
resultado = hybrid_engine.classify(
    sintoma="dolor toracico",
    respuestas={
        "¿El dolor comenzó de forma brusca?": "si",
        "¿Presenta dificultad para respirar?": "si"
    }
)

print(f"Código: {resultado.codigo_triage}")
print(f"Confianza: {resultado.confianza * 100}%")
print(f"Concordancia: {'✅' if resultado.concordancia else '⚠️'}")
print(f"\n{resultado.razonamiento_combinado}")
```

### Opción 2: Desde la API (Próximamente)

```bash
POST http://localhost:8000/api/triage/hybrid
Content-Type: application/json

{
  "sintoma": "dolor toracico",
  "respuestas": {
    "¿El dolor comenzó de forma brusca?": "si"
  }
}
```

---

## 📊 Interpretación de Resultados

### Concordancia Perfecta ✅

```json
{
  "codigo_triage": "D1",
  "confianza": 0.97,
  "concordancia": true,
  "nivel_alerta": "ninguno",
  "requiere_revision": false
}
```

**Interpretación**: Ambos sistemas concuerdan → Alta confianza → Proceder

---

### Discordancia Leve ⚠️

```json
{
  "codigo_triage": "D1",
  "confianza": 0.78,
  "concordancia": false,
  "nivel_alerta": "bajo",
  "requiere_revision": false,
  "resultado_reglas": {"codigo": "D2"},
  "resultado_ai": {"codigo": "D1"}
}
```

**Interpretación**: Diferencia de 1 nivel → Escalar al más grave → Proceder con precaución

---

### Discordancia Alta 🔴

```json
{
  "codigo_triage": "D1",
  "confianza": 0.65,
  "concordancia": false,
  "nivel_alerta": "alto",
  "requiere_revision": true,
  "resultado_reglas": {"codigo": "D3"},
  "resultado_ai": {"codigo": "D1"}
}
```

**Interpretación**: Diferencia de 3 niveles → **REQUIERE REVISIÓN MÉDICA** → No proceder sin evaluación

---

## 🎯 Casos de Uso

### Caso 1: Emergencia Clara (Concordancia)

**Entrada**: Dolor torácico + síntomas de IAM

**Reglas**: D1 (0.90)
**Med-Gemma**: D1 (0.95)

**Resultado**: D1 (0.97) ✅
**Acción**: Proceder con protocolo de emergencia

---

### Caso 2: Presentación Atípica (AI Detecta Riesgo)

**Entrada**: Confusión en adulto mayor

**Reglas**: D3 (0.60) - "Consulta prioritaria"
**Med-Gemma**: D1 (0.85) - "Posible ACV o sepsis"

**Resultado**: D1 (0.75) ⚠️
**Acción**: Escalar a emergencia + Evaluación neurológica

---

### Caso 3: Falso Positivo (Reglas Conservadoras)

**Entrada**: Dolor abdominal leve

**Reglas**: D2 (0.70) - "Protocolo estándar"
**Med-Gemma**: D7 (0.80) - "Gastritis probable"

**Resultado**: D2 (0.73) ⚠️
**Acción**: Seguir protocolo D2, considerar ajuste de reglas

---

## ⚙️ Configuración Avanzada

### Ajustar Pesos de Clasificación

```python
# Más peso a reglas (conservador)
hybrid_engine = HybridTriageEngine(
    rules_engine, 
    ai_client,
    peso_reglas=0.6,  # 60% reglas
    peso_ai=0.4       # 40% AI
)

# Más peso a AI (casos complejos)
hybrid_engine = HybridTriageEngine(
    rules_engine, 
    ai_client,
    peso_reglas=0.3,  # 30% reglas
    peso_ai=0.7       # 70% AI
)
```

### Modo Fallback (Sin AI)

```python
# Si Med-Gemma no está disponible, usa solo reglas
hybrid_engine = HybridTriageEngine(
    rules_engine,
    ai_client=None  # Modo solo reglas
)
```

---

## 📈 Métricas y Monitoreo

### Métricas Clave

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| Concordancia | > 85% | TBD |
| Sensibilidad D1 | > 98% | TBD |
| Especificidad D3 | > 80% | TBD |
| Tiempo respuesta | < 2s | ~1s |

### Logging de Decisiones

Todas las clasificaciones híbridas se registran con:
- Timestamp
- Resultados de ambos sistemas
- Concordancia
- Nivel de alerta
- Decisión final

---

## 🔒 Consideraciones de Seguridad

### Privacidad de Datos

⚠️ **IMPORTANTE**: Al usar Google AI API, los datos se envían a servidores de Google.

**Recomendaciones**:
1. **Anonimizar datos**: No enviar nombres, IDs de pacientes
2. **Usar modelo local**: Considerar Ollama + Med-Gemma local
3. **Integrar SafeCore**: Encriptación end-to-end

### Cumplimiento HIPAA

Para cumplimiento HIPAA:
- ✅ Usar Vertex AI (Google Cloud) con BAA
- ✅ Implementar SafeCore para auditoría
- ✅ Encriptar datos en tránsito y reposo
- ✅ Logs de auditoría inmutables

---

## 🚨 Manejo de Errores

### Si Med-Gemma Falla

El sistema automáticamente hace fallback a clasificación por reglas:

```python
try:
    resultado = hybrid_engine.classify(sintoma, respuestas)
except Exception as e:
    print(f"⚠️ Med-Gemma falló: {e}")
    # Sistema continúa con reglas solamente
```

### Si Reglas Fallan

```python
# Siempre validar que el síntoma existe
sintomas_disponibles = rules_engine.sintomas_index.keys()
if sintoma not in sintomas_disponibles:
    print(f"❌ Síntoma '{sintoma}' no encontrado")
```

---

## 📚 Próximos Pasos

1. **Validar con datos reales**
   - Procesar Excel de triage completo
   - Comparar clasificaciones reglas vs AI

2. **Ajustar pesos**
   - Analizar casos de discordancia
   - Optimizar balance reglas/AI

3. **Integrar con API**
   - Endpoint `/api/triage/hybrid`
   - Documentación Swagger

4. **Validación clínica**
   - Revisión por médicos
   - Ajuste de umbrales de alerta

---

## 💡 Tips y Mejores Prácticas

1. **Usa híbrido para casos complejos**: Casos simples pueden usar solo reglas
2. **Monitorea discordancias**: Son oportunidades de aprendizaje
3. **Documenta casos atípicos**: Mejora continua del sistema
4. **Valida regularmente**: Compara con diagnósticos finales

---

**Orion Core + Med-Gemma** = Triage Robusto y Confiable 🚀
