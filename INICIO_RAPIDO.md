# 🚀 Orion Core - Inicio Rápido

## Sistema Listo para Usar

El sistema **Orion Core** está completamente funcional con datos de ejemplo.

## 📋 Comandos Esenciales

### 1. Iniciar el Servidor API

```bash
cd C:\Users\johan\.gemini\antigravity\scratch\orion-core
python api\triage_api.py
```

Servidor disponible en: **http://localhost:8000**

### 2. Ver Documentación Interactiva

Abre en tu navegador: **http://localhost:8000/docs**

### 3. Probar la API

```bash
# Listar síntomas
curl http://localhost:8000/api/sintomas

# Clasificar un caso
curl -X POST http://localhost:8000/api/triage \
  -H "Content-Type: application/json" \
  -d '{"sintoma": "dolor toracico", "respuestas": {"¿El dolor comenzó de forma brusca?": "si"}}'
```

## 📥 Integrar tus Datos Reales

### Paso 1: Exportar desde Google Sheets

1. Abre tu Google Sheet de triage
2. **Archivo → Descargar → Microsoft Excel (.xlsx)**
3. Guarda en: `data\triage_urgencias.xlsx`

### Paso 2: Procesar con ETL

```bash
python etl\excel_transformer.py --input data\triage_urgencias.xlsx
```

### Paso 3: Reiniciar API

El sistema cargará automáticamente la nueva base de conocimiento.

## 📚 Documentación Completa

- [README.md](README.md) - Documentación principal
- [IMPORTAR_DATOS.md](IMPORTAR_DATOS.md) - Guía de importación
- [walkthrough.md](file:///C:/Users/johan/.gemini/antigravity/brain/044c3723-0fcf-4f61-9048-731265a4218e/walkthrough.md) - Walkthrough completo

## 🎯 Estado Actual

✅ ETL Transformer (Excel/CSV)
✅ Motor de Inferencia (D1-D3)
✅ API REST (5 endpoints)
✅ Documentación Swagger
✅ Tests con datos de ejemplo
⏳ **Esperando datos reales de triage**

---

**Proyecto ubicado en**: `C:\Users\johan\.gemini\antigravity\scratch\orion-core`
