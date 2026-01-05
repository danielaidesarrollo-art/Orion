# 📊 Acceso al Archivo de Google Sheets

El archivo de Google Sheets requiere autenticación para acceder.

## Opciones para Proceder:

### Opción 1: Hacer el Archivo Público (Recomendado)

1. Abre el Google Sheet: https://docs.google.com/spreadsheets/d/1HsQyeqlhKtLs-o6UQoraVey4e9akvT4HPnkLnH8ZV5Y/edit
2. Haz clic en **"Compartir"** (botón en la esquina superior derecha)
3. En "Acceso general", cambia a **"Cualquier persona con el enlace"**
4. Asegúrate de que el permiso sea **"Lector"**
5. Haz clic en **"Copiar enlace"** y **"Listo"**

Luego ejecuta:
```bash
python scripts\descargar_google_sheets.py
```

### Opción 2: Descargar Manualmente

1. Abre el Google Sheet
2. Ve a **Archivo → Descargar → Microsoft Excel (.xlsx)**
3. Guarda el archivo en: `C:\Users\johan\.gemini\antigravity\scratch\orion-core\data\triage_urgencias.xlsx`

### Opción 3: Dar Acceso a la Cuenta de Servicio

Comparte el archivo con esta cuenta:
```
jetski-w-bravo@jetski-w-bravo.iam.gserviceaccount.com
```

---

## Una vez que tengas el archivo disponible:

```bash
# Procesar el Excel
python etl\excel_transformer.py --input data\triage_urgencias.xlsx --output data\triage_knowledge_base.json

# Probar el sistema
python tests\test_inference.py

# Iniciar la API
python api\triage_api.py
```

## Estado Actual

✅ Proyecto Orion Core creado
✅ ETL transformer implementado
✅ Motor de inferencia listo
✅ API REST configurada
✅ Tests creados
⏳ **Esperando acceso al archivo de Google Sheets**
