# 🔷 Orion Alfa - Módulo Administrativo

<div align="center">

![Orion Emergency Module](assets/logo.jpg)

**Gestión, Configuración y Supervisión del Sistema**

</div>

## 📋 Descripción

**Orion Alfa** es el módulo administrativo del sistema Orion Emergency Module. Proporciona las herramientas necesarias para gestionar protocolos clínicos, configurar reglas de triage, y supervisar el rendimiento del sistema.

## 🎯 Funcionalidades Principales

### 1. Gestión de Protocolos
- ✅ Importación desde Google Sheets
- ✅ Procesamiento ETL de Excel/CSV
- ✅ Validación de reglas clínicas
- ✅ Actualización de base de conocimiento

### 2. Configuración del Sistema
- ✅ Parámetros de clasificación (D1-D7)
- ✅ Umbrales de confianza
- ✅ Integración Med-Gemma AI
- ✅ Configuración de alertas

### 3. Supervisión y Auditoría
- ✅ Logs de decisiones
- ✅ Métricas de rendimiento
- ✅ Detección de discordancias
- ✅ Reportes de calidad

## 🚀 Inicio Rápido

### Importar Protocolos desde Google Sheets

```bash
python scripts\descargar_google_sheets.py
```

### Procesar Archivo Excel Local

```bash
python etl\excel_transformer.py --input data\triage_urgencias.xlsx
```

### Verificar Base de Conocimiento

```bash
python tests\test_inference.py
```

## 📁 Archivos Principales

```
orion-core/
├── etl/
│   └── excel_transformer.py      # Transformador ETL
├── scripts/
│   └── descargar_google_sheets.py # Importador Google Sheets
├── data/
│   └── triage_knowledge_base.json # Base de conocimiento
└── tests/
    └── test_inference.py          # Tests de validación
```

## 🔗 Integración con Orion Omega

Orion Alfa genera y mantiene la base de conocimiento que utiliza **Orion Omega** para la clasificación de casos en tiempo real.

```
Orion Alfa (Admin) → Base de Conocimiento → Orion Omega (Triage)
```

## 📚 Documentación Relacionada

- [README Principal](README.md)
- [Orion Omega - Módulo de Triage](ORION_OMEGA.md)
- [Guía de Importación de Datos](IMPORTAR_DATOS.md)
- [Integración Med-Gemma](MEDGEMMA_INTEGRATION.md)

---

**Orion Alfa** - Gestión Inteligente de Protocolos Clínicos 🔷
