# 📥 Cómo Importar tus Datos de Triage

Ya que el Google Sheet requiere autenticación, aquí tienes las opciones más prácticas:

## ✅ Opción 1: Exportar como Excel (RECOMENDADO)

1. Abre tu Google Sheet
2. Ve a **Archivo → Descargar → Microsoft Excel (.xlsx)**
3. Guarda el archivo descargado en:
   ```
   C:\Users\johan\.gemini\antigravity\scratch\orion-core\data\triage_urgencias.xlsx
   ```
4. Ejecuta el transformador:
   ```bash
   python etl\excel_transformer.py --input data\triage_urgencias.xlsx
   ```

## ✅ Opción 2: Exportar como CSV

1. Abre tu Google Sheet
2. Ve a **Archivo → Descargar → Valores separados por comas (.csv)**
3. Guarda como `triage_urgencias.csv` en la carpeta `data`
4. Ejecuta:
   ```bash
   python etl\excel_transformer.py --input data\triage_urgencias.csv
   ```

**Nota**: Si tienes múltiples hojas, deberás exportar cada una y procesarlas individualmente.

## ✅ Opción 3: Hacer el Sheet Público (Temporal)

1. Abre el Google Sheet
2. Haz clic en **"Compartir"**
3. Cambia a **"Cualquier persona con el enlace"** → **"Lector"**
4. Ejecuta:
   ```bash
   python scripts\descargar_google_sheets.py
   ```
5. Después de descargar, puedes volver a hacer el sheet privado

## 🧪 Mientras tanto: Probar con Datos de Ejemplo

El sistema ya incluye datos de ejemplo con 3 síntomas. Puedes probarlo ahora:

```bash
# Usar la base de conocimiento de ejemplo
copy data\ejemplo_triage.json data\triage_knowledge_base.json

# Ejecutar tests
python tests\test_inference.py

# Iniciar API
python api\triage_api.py
```

Luego visita: http://localhost:8000/docs para ver la documentación interactiva de la API.

---

**¿Listo para proceder?** Elige una opción y avísame cuando hayas exportado el archivo.
