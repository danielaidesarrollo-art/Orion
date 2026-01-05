# 📋 Guía de Importación Manual del Archivo Excel

## Opción 1: Copia Manual (Más Rápida)

1. Abre el Explorador de Archivos
2. Navega a tu carpeta de triage en el Desktop
3. Copia el archivo Excel de triage
4. Pégalo en esta ubicación:
   ```
   C:\Users\johan\.gemini\antigravity\scratch\orion-core\data\triage_urgencias.xlsx
   ```

## Opción 2: Usando PowerShell

Ejecuta este comando en PowerShell (ajusta la ruta de origen si es necesaria):

```powershell
Copy-Item -Path "$env:USERPROFILE\Desktop\triage de urgencias\*.xlsx" -Destination "C:\Users\johan\.gemini\antigravity\scratch\orion-core\data\triage_urgencias.xlsx"
```

## Opción 3: Arrastrar y Soltar

1. Abre VS Code en la carpeta del proyecto
2. En el explorador de archivos, navega a la carpeta `data`
3. Arrastra el archivo Excel desde tu Desktop a la carpeta `data`
4. Renómbralo a `triage_urgencias.xlsx`

## Después de Copiar el Archivo

Una vez que el archivo esté en su lugar, ejecuta:

```bash
python etl\excel_transformer.py --input data\triage_urgencias.xlsx --output data\triage_knowledge_base.json
```

## Verificar que el Archivo Está en su Lugar

```bash
dir data\*.xlsx
```

---

**Nota**: Si la carpeta en tu Desktop tiene un nombre diferente a "triage de urgencias", ajusta las rutas según corresponda.
