"""
Demo del Motor Maestro DANIEL_AI Orion
Muestra integración completa con DataCore, SafeCore y BioCore
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from core.inference_engine import InferenceEngine
from core.orion_master import OrionMasterEngine, BiometricData


def demo_caso_emergencia():
    """Demo: Caso de emergencia con todas las integraciones"""
    
    print("\n" + "="*80)
    print("🚀 DANIEL_AI ORION - MOTOR MAESTRO")
    print("   Integración: DataCore + SafeCore + BioCore + Med-Gemma")
    print("="*80 + "\n")
    
    # Inicializar motor
    print("⚙️  Inicializando componentes...")
    rules_engine = InferenceEngine("data/triage_knowledge_base.json")
    
    # Motor maestro con todas las integraciones
    orion = OrionMasterEngine(
        rules_engine=rules_engine,
        ai_client=None,  # Med-Gemma opcional
        enable_zkp=True,
        enable_honeypot=True
    )
    
    print("✅ Motor Maestro inicializado\n")
    
    # CASO 1: Emergencia - Dolor Torácico
    print("="*80)
    print("📋 CASO CLÍNICO 1: EMERGENCIA - DOLOR TORÁCICO")
    print("="*80 + "\n")
    
    # Input del paciente (puede ser voz, texto o imagen transcrita)
    input_paciente = """
    Paciente masculino de 55 años presenta dolor torácico intenso
    que comenzó hace 20 minutos de forma súbita. Refiere dolor
    opresivo que se irradia al brazo izquierdo y mandíbula.
    """
    
    # Respuestas a preguntas clave
    respuestas = {
        "¿El dolor comenzó de forma brusca?": "si",
        "¿El dolor se irradia al brazo izquierdo, mandíbula o espalda?": "si",
        "¿Presenta dificultad para respirar?": "si",
        "¿Presenta sudoración fría?": "si"
    }
    
    # Datos biométricos (BioCore)
    biometria = BiometricData(
        heart_rate=110,
        blood_pressure_systolic=160,
        blood_pressure_diastolic=95,
        oxygen_saturation=94.0,
        temperature=37.2,
        respiratory_rate=22
    )
    
    # Procesar triage
    resultado = orion.process_triage(
        input_text=input_paciente,
        respuestas=respuestas,
        biometric_data=biometria,
        patient_id="PAC_12345"
    )
    
    # Mostrar resultado
    print("\n" + "="*80)
    print("📊 RESULTADO FINAL")
    print("="*80)
    print(f"\n🏥 CLASIFICACIÓN: {resultado.clasificacion_final} - {resultado.categoria}")
    print(f"📈 Confianza: {resultado.confianza * 100:.1f}%")
    print(f"🔄 Concordancia: {'✅ Sí' if resultado.concordancia else '⚠️ No'}")
    print(f"📍 Conducta: {resultado.conducta_asignada}")
    print(f"🔐 Bio-Hash: {resultado.patient_bio_hash[:32]}...")
    print(f"✅ ZKP Validado: {'Sí' if resultado.zkp_validation else 'No'}")
    print(f"💰 Gas consumido: {resultado.gas_consumido:.4f} COP")
    
    print(f"\n🚨 INSTRUCCIONES INMEDIATAS:")
    for instruccion in resultado.instrucciones_inmediatas:
        print(f"   ⚡ {instruccion}")
    
    print(f"\n🔍 CAUSAS POSIBLES:")
    for causa in resultado.causas_posibles:
        print(f"   • {causa}")
    
    print(f"\n📝 OBSERVACIONES:")
    print(f"   {resultado.observaciones}")
    
    if resultado.derivacion_vpp:
        print(f"\n💡 OPTIMIZACIÓN: Derivación a VPP recomendada")
    
    # Exportar log
    orion.export_decision_log(resultado, "logs/decision_emergencia.json")
    
    print("\n" + "="*80)
    
    # CASO 2: Amenaza de Seguridad (Honeypot)
    print("\n\n" + "="*80)
    print("🛡️  CASO 2: DETECCIÓN DE AMENAZA - HONEYPOT")
    print("="*80 + "\n")
    
    input_malicioso = "dolor <script>alert('XSS')</script> toracico"
    
    try:
        resultado_amenaza = orion.process_triage(
            input_text=input_malicioso,
            respuestas={},
            patient_id="ATTACKER"
        )
        
        if resultado_amenaza.honeypot_activated:
            print("✅ HONEYPOT ACTIVADO - Amenaza contenida")
            print(f"   Clasificación: {resultado_amenaza.clasificacion_final}")
            print(f"   Observaciones: {resultado_amenaza.observaciones}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Reporte mensual
    print("\n\n" + "="*80)
    print("📊 REPORTE MENSUAL")
    print("="*80 + "\n")
    
    reporte = orion.get_monthly_report()
    
    print(f"Total de decisiones: {reporte['total_decisiones']}")
    print(f"Gas total consumido: {reporte['gas_total_cop']:.4f} COP")
    print(f"Amenazas detectadas: {reporte['amenazas_detectadas']}")
    print(f"Validaciones ZKP: {reporte['zkp_validaciones']}")
    
    print(f"\nDecisiones por código:")
    for codigo, count in reporte['decisiones_por_codigo'].items():
        print(f"   {codigo}: {count}")
    
    print("\n" + "="*80)
    print("✨ DEMOSTRACIÓN COMPLETADA")
    print("="*80 + "\n")


if __name__ == "__main__":
    demo_caso_emergencia()
