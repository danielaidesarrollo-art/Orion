"""
Script para importar el archivo Excel de triage desde el Desktop
"""

import shutil
from pathlib import Path
import os

def importar_excel_triage():
    """Importa el archivo Excel desde el Desktop"""
    
    # Rutas
    desktop = Path.home() / "Desktop" / "triage de urgencias"
    destino = Path(__file__).parent.parent / "data"
    
    print(f"🔍 Buscando archivos en: {desktop}")
    
    if not desktop.exists():
        print(f"❌ No se encontró la carpeta: {desktop}")
        print("\n💡 Por favor, verifica la ruta o copia manualmente el archivo Excel a:")
        print(f"   {destino}")
        return False
    
    # Buscar archivos Excel
    archivos_excel = list(desktop.glob("*.xlsx")) + list(desktop.glob("*.xls"))
    
    if not archivos_excel:
        print(f"❌ No se encontraron archivos Excel en: {desktop}")
        return False
    
    print(f"\n✅ Archivos encontrados:")
    for i, archivo in enumerate(archivos_excel, 1):
        print(f"   {i}. {archivo.name} ({archivo.stat().st_size / 1024:.2f} KB)")
    
    # Copiar el primer archivo
    archivo_origen = archivos_excel[0]
    archivo_destino = destino / "triage_urgencias.xlsx"
    
    # Crear directorio si no existe
    destino.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📋 Copiando: {archivo_origen.name}")
    shutil.copy2(archivo_origen, archivo_destino)
    
    print(f"✅ Archivo copiado exitosamente a:")
    print(f"   {archivo_destino}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("📂 ORION CORE - IMPORTADOR DE EXCEL")
    print("=" * 60 + "\n")
    
    if importar_excel_triage():
        print("\n✨ Importación completada")
        print("\n📝 Siguiente paso: Ejecutar el transformador ETL")
        print("   python etl/excel_transformer.py --input data/triage_urgencias.xlsx")
    else:
        print("\n⚠️  Importación fallida")
        print("\n📝 Alternativa: Copia manualmente el archivo Excel a:")
        print("   C:\\Users\\johan\\.gemini\\antigravity\\scratch\\orion-core\\data\\triage_urgencias.xlsx")
