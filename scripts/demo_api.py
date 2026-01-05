"""
Script de demostración de Orion Core API
Muestra ejemplos de uso de todos los endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Imprime un separador de sección"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def demo_info():
    """Muestra información de la API"""
    print_section("1. INFORMACIÓN DE LA API")
    
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    
    print(f"Nombre: {data['nombre']}")
    print(f"Versión: {data['version']}")
    print(f"Descripción: {data['descripcion']}")
    print("\nEndpoints disponibles:")
    for name, path in data['endpoints'].items():
        print(f"  - {name}: {path}")

def demo_sintomas():
    """Lista todos los síntomas disponibles"""
    print_section("2. SÍNTOMAS DISPONIBLES")
    
    response = requests.get(f"{BASE_URL}/api/sintomas")
    data = response.json()
    
    print(f"Total de síntomas: {data['total']}\n")
    for i, sintoma in enumerate(data['sintomas'], 1):
        print(f"  {i}. {sintoma.title()}")

def demo_preguntas(sintoma):
    """Muestra las preguntas obligatorias para un síntoma"""
    print_section(f"3. PREGUNTAS PARA: {sintoma.upper()}")
    
    response = requests.get(f"{BASE_URL}/api/preguntas/{sintoma}")
    data = response.json()
    
    print(f"Síntoma: {data['sintoma'].title()}")
    print(f"Total de preguntas: {len(data['preguntas'])}\n")
    
    for i, pregunta in enumerate(data['preguntas'], 1):
        print(f"{i}. {pregunta['pregunta']}")
        print(f"   Tipo: {pregunta['tipo_respuesta']}")
        print()

def demo_clasificacion_emergencia():
    """Demuestra clasificación de emergencia (D1)"""
    print_section("4. CASO DE EMERGENCIA (D1)")
    
    payload = {
        "sintoma": "dolor toracico",
        "respuestas": {
            "¿El dolor comenzó de forma brusca?": "si",
            "¿El dolor se irradia al brazo izquierdo, mandíbula o espalda?": "si",
            "¿Presenta dificultad para respirar?": "si",
            "¿Presenta sudoración fría?": "si"
        }
    }
    
    print("📋 Caso clínico:")
    print("   Paciente con dolor torácico de inicio brusco")
    print("   Irradiación a brazo izquierdo")
    print("   Dificultad respiratoria")
    print("   Sudoración fría\n")
    
    response = requests.post(f"{BASE_URL}/api/triage", json=payload)
    data = response.json()
    
    print(f"🚨 RESULTADO:")
    print(f"   Código: {data['codigo_triage']}")
    print(f"   Categoría: {data['categoria']}")
    print(f"   Confianza: {data['confianza'] * 100}%")
    print(f"\n💉 Instrucción:")
    print(f"   {data['instruccion_atencion']}")
    print(f"\n🔍 Posibles causas:")
    for causa in data['posibles_causas']:
        print(f"   - {causa}")

def demo_clasificacion_urgencia():
    """Demuestra clasificación de urgencia (D2)"""
    print_section("5. CASO DE URGENCIA (D2)")
    
    payload = {
        "sintoma": "confusion",
        "respuestas": {
            "¿La confusión comenzó de forma súbita?": "no",
            "¿El paciente responde a estímulos verbales?": "si",
            "¿Presenta fiebre?": "si",
            "¿Tiene antecedentes de diabetes?": "no"
        }
    }
    
    print("📋 Caso clínico:")
    print("   Paciente confuso con fiebre")
    print("   Responde a estímulos verbales")
    print("   Sin antecedentes de diabetes\n")
    
    response = requests.post(f"{BASE_URL}/api/triage", json=payload)
    data = response.json()
    
    print(f"⚠️  RESULTADO:")
    print(f"   Código: {data['codigo_triage']}")
    print(f"   Categoría: {data['categoria']}")
    print(f"   Confianza: {data['confianza'] * 100}%")
    print(f"\n💉 Instrucción:")
    print(f"   {data['instruccion_atencion']}")
    print(f"\n🔍 Posibles causas:")
    for causa in data['posibles_causas']:
        print(f"   - {causa}")

def demo_deteccion_automatica():
    """Demuestra detección automática de síntoma"""
    print_section("6. DETECCIÓN AUTOMÁTICA DE SÍNTOMA")
    
    payload = {
        "texto_paciente": "No puedo mover el brazo derecho y se me torció la boca",
        "respuestas": {
            "¿Se le torció la boca o presenta asimetría facial?": "si",
            "¿No puede levantar uno o ambos brazos?": "si",
            "¿Presenta dificultad para hablar o no se le entiende?": "no",
            "¿Los síntomas comenzaron hace menos de 4.5 horas?": "si"
        }
    }
    
    print("📋 Texto del paciente:")
    print(f'   "{payload["texto_paciente"]}"\n')
    
    response = requests.post(f"{BASE_URL}/api/triage", json=payload)
    data = response.json()
    
    print(f"🧠 Síntoma detectado: FUERZA MUSCULAR")
    print(f"\n🚨 RESULTADO:")
    print(f"   Código: {data['codigo_triage']}")
    print(f"   Categoría: {data['categoria']}")
    print(f"\n💉 Instrucción:")
    print(f"   {data['instruccion_atencion']}")

def main():
    print("\n" + "🌟" * 30)
    print("   ORION CORE - DEMOSTRACIÓN DEL SISTEMA")
    print("🌟" * 30)
    
    try:
        demo_info()
        demo_sintomas()
        demo_preguntas("dolor toracico")
        demo_clasificacion_emergencia()
        demo_clasificacion_urgencia()
        demo_deteccion_automatica()
        
        print("\n" + "=" * 60)
        print("  ✅ DEMOSTRACIÓN COMPLETADA")
        print("=" * 60)
        print("\n💡 Accede a la documentación interactiva en:")
        print("   http://localhost:8000/docs")
        print("\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar a la API")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   python api/triage_api.py\n")

if __name__ == "__main__":
    main()
