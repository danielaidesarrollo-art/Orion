"""
Script para descargar y procesar el archivo de Google Sheets
"""

import requests
import json
from pathlib import Path

def descargar_google_sheets(sheet_url: str, output_path: str):
    """
    Descarga un Google Sheet como archivo Excel
    
    Args:
        sheet_url: URL del Google Sheet
        output_path: Ruta donde guardar el archivo
    """
    # Extraer el ID del documento
    if "/d/" in sheet_url:
        doc_id = sheet_url.split("/d/")[1].split("/")[0]
    else:
        raise ValueError("URL de Google Sheets inválida")
    
    # URL de exportación a Excel
    export_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=xlsx"
    
    print(f"📥 Descargando desde Google Sheets...")
    print(f"   ID del documento: {doc_id}")
    
    # Descargar el archivo
    response = requests.get(export_url)
    
    if response.status_code == 200:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Archivo descargado exitosamente")
        print(f"   Tamaño: {len(response.content) / 1024:.2f} KB")
        print(f"   Ubicación: {output_file}")
        return True
    else:
        print(f"❌ Error al descargar: {response.status_code}")
        print(f"   Asegúrate de que el documento sea público o accesible")
        return False

if __name__ == "__main__":
    # URL del Google Sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1HsQyeqlhKtLs-o6UQoraVey4e9akvT4HPnkLnH8ZV5Y/edit?gid=797773963#gid=797773963"
    
    # Ruta de salida
    output_path = "data/triage_urgencias.xlsx"
    
    print("=" * 60)
    print("📊 ORION CORE - DESCARGA DE GOOGLE SHEETS")
    print("=" * 60 + "\n")
    
    if descargar_google_sheets(sheet_url, output_path):
        print("\n✨ Descarga completada")
        print("\n📝 Siguiente paso: Ejecutar el transformador ETL")
        print("   python etl/excel_transformer.py --input data/triage_urgencias.xlsx")
    else:
        print("\n⚠️  Descarga fallida")
