# DANIEL_AI Orion - Prompt Maestro

## Sistema de Decisión Clínica Integrado

**Orion** implementa el Prompt Maestro de DANIEL_AI con integración completa del ecosistema:

- ✅ **DataCore**: NLP Entity Detection + Honeypot Redirection
- ✅ **SafeCore**: Zero-Knowledge Proof + Auditoría
- ✅ **BioCore**: Bio-Hash Irreversible + Biometría
- ✅ **Med-Gemma**: IA Médica (opcional)
- ✅ **Chain-of-Thought**: Razonamiento clínico paso a paso

---

## 🧠 Arquitectura del Prompt Maestro

### Flujo de Procesamiento

```
1. INPUT (Voz/Texto/Imagen)
   ↓
2. [DataCore] NLP Entity Detection
   ↓
3. [SafeCore] Threat Detection → Honeypot?
   ↓
4. [SafeCore] Zero-Knowledge Proof Validation
   ↓
5. [BioCore] Bio-Hash Generation
   ↓
6. [Orion] Preguntas Clave Dinámicas
   ↓
7. [Orion] Clasificación Multimodal
   ├─ Sistema de Reglas
   └─ Med-Gemma AI (opcional)
   ↓
8. [Orion] Validación Cruzada
   ↓
9. INSTRUCCIONES INMEDIATAS ⚡
   ↓
10. [Orion] Logging Estructurado JSON
    ↓
11. [Orion] Cálculo de Gas (COP)
```

---

## 📋 Uso del Motor Maestro

### Ejemplo Básico

```python
from core.inference_engine import InferenceEngine
from core.orion_master import OrionMasterEngine, BiometricData

# Inicializar
rules_engine = InferenceEngine("data/triage_knowledge_base.json")
orion = OrionMasterEngine(
    rules_engine=rules_engine,
    enable_zkp=True,
    enable_honeypot=True
)

# Input del paciente
input_text = "Dolor torácico intenso que comenzó hace 20 minutos"

# Respuestas a preguntas clave
respuestas = {
    "¿El dolor comenzó de forma brusca?": "si",
    "¿Presenta dificultad para respirar?": "si"
}

# Datos biométricos (opcional)
biometria = BiometricData(
    heart_rate=110,
    blood_pressure_systolic=160,
    oxygen_saturation=94.0
)

# Procesar triage
resultado = orion.process_triage(
    input_text=input_text,
    respuestas=respuestas,
    biometric_data=biometria,
    patient_id="PAC_12345"
)

# Resultado
print(f"Clasificación: {resultado.clasificacion_final}")
print(f"Instrucciones: {resultado.instrucciones_inmediatas}")
print(f"Bio-Hash: {resultado.patient_bio_hash}")
print(f"Gas: {resultado.gas_consumido} COP")
```

---

## 🔐 Características de Seguridad

### 1. Zero-Knowledge Proof (SafeCore)

Valida elegibilidad del paciente **sin exponer identidad real**:

```python
# ZKP permite validar:
# - Paciente es elegible para atención
# - Gravedad del caso justifica recursos
# SIN revelar:
# - Nombre real
# - Número de identificación
# - Datos personales
```

### 2. Bio-Hash Irreversible (BioCore)

Genera hash único e irreversible del paciente:

```python
bio_hash = SHA256(
    patient_id + 
    timestamp + 
    heart_rate + 
    blood_pressure
)

# Resultado: "a3f5b2c8d1e4..."
# Imposible revertir a datos originales
```

### 3. Honeypot Redirection (SafeCore)

Detecta y contiene amenazas automáticamente:

```python
# Patrones detectados:
# - SQL Injection
# - XSS (Cross-Site Scripting)
# - Code Injection
# - Comandos maliciosos

# Acción: Redirigir a entorno sintético
# Resultado: Sistema real protegido
```

---

## 📊 Logging Estructurado

Cada decisión genera un log JSON completo:

```json
{
  "timestamp": "2026-01-05T14:45:00",
  "patient_bio_hash": "a3f5b2c8d1e4f7a9...",
  "sintoma_detectado": "dolor toracico",
  "clasificacion_final": "D1",
  "categoria": "EMERGENCIA",
  "confianza": 0.95,
  "concordancia": true,
  "instrucciones_inmediatas": [
    "EMERGENCIA - Traslado inmediato a sala de reanimación..."
  ],
  "causas_posibles": [
    "Infarto agudo de miocardio",
    "Angina inestable"
  ],
  "conducta_asignada": "URG",
  "codigo_conducta": "D1",
  "derivacion_vpp": false,
  "gas_consumido": 0.0061,
  "zkp_validation": true,
  "threat_detected": false,
  "honeypot_activated": false
}
```

---

## 💰 Sistema de Costos (Gas)

Cálculo automático de costos operacionales:

| Componente | Costo (COP) |
|------------|-------------|
| Base | 0.001 |
| Por pregunta | 0.0001 |
| Med-Gemma AI | 0.005 |
| ZKP Validation | 0.002 |

**Ejemplo**:
- 4 preguntas + ZKP = 0.0034 COP
- 4 preguntas + AI + ZKP = 0.0084 COP

---

## 🎯 Códigos de Conducta

| Código | Conducta | Descripción | VPP |
|--------|----------|-------------|-----|
| **D1** | URG | Emergencia inmediata | No |
| **D2** | URG | Urgencia prioritaria | No |
| **D7** | LM | Baja complejidad | ✅ Sí |
| **D3** | CONS | Consulta prioritaria | ✅ Sí |

**VPP** (Vías de Procesamiento Vertical): Derivación para liberar recursos críticos.

---

## 🚀 Ejecutar Demo

```bash
python scripts\demo_orion_master.py
```

**Salida esperada**:
```
🚀 DANIEL_AI ORION - MOTOR MAESTRO
   Integración: DataCore + SafeCore + BioCore + Med-Gemma

📋 CASO CLÍNICO 1: EMERGENCIA - DOLOR TORÁCICO

🔍 [DataCore] Ejecutando NLP Entity Detection...
   ✅ Síntoma detectado: dolor toracico

🛡️  [SafeCore] Analizando amenazas...
   ✅ Sin amenazas detectadas

🔐 [SafeCore] Validando elegibilidad con ZKP...
   ✅ ZKP validado

🧬 [BioCore] Generando Bio-Hash irreversible...
   ✅ Bio-Hash: a3f5b2c8d1e4f7a9...

📋 [Orion] Ejecutando preguntas clave...
   • ¿El dolor comenzó de forma brusca?: si
   • ¿Presenta dificultad para respirar?: si

🧠 [Orion] Ejecutando clasificación híbrida...
   ✅ Clasificación: D1 (EMERGENCIA)
   ✅ Confianza: 90.0%

🚨 [INSTRUCCIONES INMEDIATAS]:
   ⚡ EMERGENCIA - Traslado inmediato...

📊 [Orion] Decisión registrada - Gas: 0.0034 COP
```

---

## 📈 Reporte Mensual

```python
reporte = orion.get_monthly_report()

# Resultado:
{
  "total_decisiones": 150,
  "gas_total_cop": 0.5100,
  "decisiones_por_codigo": {
    "D1": 25,
    "D2": 45,
    "D7": 50,
    "D3": 30
  },
  "amenazas_detectadas": 3,
  "zkp_validaciones": 150
}
```

---

## 🔄 Integración con Ecosistema

### DataCore
- NLP Entity Detection
- Honeypot Redirection
- Threat Analysis

### SafeCore
- Zero-Knowledge Proof
- Auditoría Inmutable
- Encriptación

### BioCore
- Bio-Hash Irreversible
- Biometría
- Identidad Protegida

### Med-Gemma (Opcional)
- IA Médica
- Razonamiento Clínico
- Diagnósticos Diferenciales

---

## 📝 Cumplimiento HIPAA

✅ **Identidad Protegida**: Bio-Hash irreversible
✅ **Zero-Knowledge Proof**: Validación sin exposición
✅ **Auditoría Completa**: Logs inmutables
✅ **Encriptación**: Datos en tránsito y reposo
✅ **Trazabilidad**: Registro de cada decisión

---

## 🎓 Chain-of-Thought Reasoning

El motor ejecuta razonamiento paso a paso:

1. **Identificación**: Detectar síntoma principal
2. **Validación**: Preguntas clave dinámicas
3. **Análisis**: Evaluar respuestas vs reglas
4. **Clasificación**: Asignar código de urgencia
5. **Acción**: Instrucciones inmediatas
6. **Optimización**: Derivación VPP si aplica
7. **Registro**: Log estructurado completo

---

**DANIEL_AI Orion** - Triage Inteligente, Seguro y Cumplidor 🚀
