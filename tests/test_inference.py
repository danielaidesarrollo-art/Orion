"""
Tests para el motor de inferencia de Orion Core
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from core.inference_engine import InferenceEngine


def test_dolor_toracico_emergencia():
    """Test: Dolor torácico con síntomas de emergencia"""
    print("\n🧪 Test 1: Dolor torácico - EMERGENCIA")
    print("=" * 60)
    
    engine = InferenceEngine("data/ejemplo_triage.json")
    
    # Caso: Dolor torácico de inicio brusco
    respuestas = {
        "¿El dolor comenzó de forma brusca?": "si",
        "¿El dolor se irradia al brazo izquierdo, mandíbula o espalda?": "si",
        "¿Presenta dificultad para respirar?": "si",
        "¿Presenta sudoración fría?": "si"
    }
    
    resultado = engine.clasificar_triage("dolor toracico", respuestas)
    
    print(f"✅ Código: {resultado.codigo_triage}")
    print(f"✅ Categoría: {resultado.categoria}")
    print(f"✅ Instrucción: {resultado.instruccion_atencion}")
    print(f"✅ Confianza: {resultado.confianza * 100}%")
    print(f"✅ Causas posibles: {', '.join(resultado.posibles_causas)}")
    
    assert resultado.codigo_triage == "D1", "Debe ser código D1 (EMERGENCIA)"
    print("\n✅ Test PASADO\n")


def test_confusion_con_fiebre():
    """Test: Confusión con fiebre - URGENCIA"""
    print("\n🧪 Test 2: Confusión con fiebre - URGENCIA")
    print("=" * 60)
    
    engine = InferenceEngine("data/ejemplo_triage.json")
    
    respuestas = {
        "¿La confusión comenzó de forma súbita?": "no",
        "¿El paciente responde a estímulos verbales?": "si",
        "¿Presenta fiebre?": "si",
        "¿Tiene antecedentes de diabetes?": "no"
    }
    
    resultado = engine.clasificar_triage("confusion", respuestas)
    
    print(f"✅ Código: {resultado.codigo_triage}")
    print(f"✅ Categoría: {resultado.categoria}")
    print(f"✅ Instrucción: {resultado.instruccion_atencion}")
    print(f"✅ Causas posibles: {', '.join(resultado.posibles_causas)}")
    
    assert resultado.codigo_triage == "D2", "Debe ser código D2 (URGENCIA)"
    print("\n✅ Test PASADO\n")


def test_codigo_acv():
    """Test: Síntomas de ACV - CÓDIGO ACV"""
    print("\n🧪 Test 3: Síntomas de ACV - EMERGENCIA")
    print("=" * 60)
    
    engine = InferenceEngine("data/ejemplo_triage.json")
    
    respuestas = {
        "¿Se le torció la boca o presenta asimetría facial?": "si",
        "¿No puede levantar uno o ambos brazos?": "si",
        "¿Presenta dificultad para hablar o no se le entiende?": "si",
        "¿Los síntomas comenzaron hace menos de 4.5 horas?": "si"
    }
    
    resultado = engine.clasificar_triage("fuerza muscular", respuestas)
    
    print(f"✅ Código: {resultado.codigo_triage}")
    print(f"✅ Categoría: {resultado.categoria}")
    print(f"✅ Instrucción: {resultado.instruccion_atencion}")
    print(f"✅ Causas posibles: {', '.join(resultado.posibles_causas)}")
    
    assert resultado.codigo_triage == "D1", "Debe ser código D1 (EMERGENCIA)"
    assert "ACV" in resultado.instruccion_atencion or "stroke" in resultado.instruccion_atencion.lower()
    print("\n✅ Test PASADO\n")


def test_deteccion_sintoma():
    """Test: Detección automática de síntoma"""
    print("\n🧪 Test 4: Detección automática de síntoma")
    print("=" * 60)
    
    engine = InferenceEngine("data/ejemplo_triage.json")
    
    # Texto del paciente
    textos = [
        "Tengo un dolor muy fuerte en el pecho",
        "Estoy confundido y no sé dónde estoy",
        "No puedo mover el brazo derecho"
    ]
    
    sintomas_esperados = ["dolor toracico", "confusion", "fuerza muscular"]
    
    for texto, esperado in zip(textos, sintomas_esperados):
        detectado = engine.detect_sintoma(texto)
        print(f"📝 Texto: '{texto}'")
        print(f"✅ Síntoma detectado: {detectado}")
        assert detectado == esperado, f"Debe detectar '{esperado}'"
    
    print("\n✅ Test PASADO\n")


def test_obtener_preguntas():
    """Test: Obtener preguntas obligatorias"""
    print("\n🧪 Test 5: Obtener preguntas obligatorias")
    print("=" * 60)
    
    engine = InferenceEngine("data/ejemplo_triage.json")
    
    preguntas = engine.get_preguntas_obligatorias("dolor toracico")
    
    print(f"✅ Total de preguntas: {len(preguntas)}")
    for i, pregunta in enumerate(preguntas, 1):
        print(f"  {i}. {pregunta['pregunta']} ({pregunta['tipo_respuesta']})")
    
    assert len(preguntas) > 0, "Debe haber preguntas obligatorias"
    print("\n✅ Test PASADO\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 ORION CORE - SUITE DE TESTS")
    print("=" * 60)
    
    try:
        test_dolor_toracico_emergencia()
        test_confusion_con_fiebre()
        test_codigo_acv()
        test_deteccion_sintoma()
        test_obtener_preguntas()
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
