"""
Orion Core - Resource Predictor
Motor de predicción de recursos basado en datos históricos y factores ambientales.
"""

import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from core.medgemma_client import MedGemmaClient  # Importar cliente

@dataclass
class EnvironmentalFactors:
    """Factores ambientales que afectan la demanda"""
    weather: str  # sunny, rainy, storm
    traffic: str  # low, medium, high
    event: str    # none, concert, protest, holiday

@dataclass
class PredictionResult:
    """Resultado de la predicción de recursos"""
    predicted_patients_per_hour: float
    required_doctors: int
    required_nurses: int
    required_box_units: int
    confidence_score: float
    factors_applied: Dict[str, float]

class ResourcePredictor:
    """
    Motor de predicción de recursos v2.
    
    Características:
    - Ingesta de CSV histórico para entrenamiento
    - Cálculo de línea base por Día de Semana + Hora
    - Multiplicadores por factores ambientales
    """
    
    # Rutas por defecto
    MODEL_PATH = Path(__file__).parent.parent / "data" / "prediction_model.json"
    
    # Multiplicadores de impacto (Heurísticas v1)
    MULTIPLIERS = {
        "weather": {
            "sunny": 1.0,
            "rainy": 1.10,    # +10% accidentes/respiratorio
            "storm": 1.25     # +25% trauma/respiratorio grave
        },
        "traffic": {
            "low": 1.0,
            "medium": 1.05,
            "high": 1.15      # +15% retrasos en ambulancias/ingresos acumulados
        },
        "event": {
            "none": 1.0,
            "concert": 1.20,  # +20% intoxicaciones/trauma menor
            "protest": 1.35,  # +35% trauma/respiratorio
            "holiday": 1.15   # +15% accidentes/violencia
        }
    }
    
    # Ratios de recursos (Heurísticas v1)
    # Pacientes por hora que puede atender 1 unidad
    CAPACITY = {
        "doctor": 4.0,   # 4 pacientes/hora
        "nurse": 6.0,    # 6 pacientes/hora
        "box": 2.5       # Rotación de cama cada ~2.5 horas (inverso) -> se calcula diferente
    }

    def __init__(self):
        self.baseline_model = {}
        self.actual_usage = [] 
        self.ai_client = MedGemmaClient() if "GOOGLE_API_KEY" in os.environ else None
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo de línea base si existe"""
        if self.MODEL_PATH.exists():
            try:
                with open(self.MODEL_PATH, 'r') as f:
                    self.baseline_model = json.load(f)
            except Exception as e:
                print(f"Error cargando modelo: {e}")
                self.baseline_model = {}

    def train_from_csv(self, csv_content: bytes) -> Dict[str, Any]:
        """
        Entrena modelos usando CSV histórico.
        Soporta CSV simple (conteo) o CSV rico (síntomas/tiempos).
        """
        from io import BytesIO
        
        try:
            df = pd.read_csv(BytesIO(csv_content))
            
            # Detectar formato
            is_rich = 'symptom' in df.columns and 'timestamp' in df.columns
            
            new_model = {}
            
            if is_rich:
                # Procesamiento Rico con AI
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['hour'] = df['timestamp'].dt.hour
                
                # Agrupar por slot
                grouped = df.groupby(['day_of_week', 'hour'])
                
                for (d, h), group in grouped:
                    key = f"{int(d)}-{int(h)}"
                    count = len(group)
                    
                    # Generar resumen para AI
                    symptoms_summary = "; ".join(group['symptom'].fillna("").astype(str).tolist()[:20]) # Limit 20 samples
                    
                    # Consultar AI para peso de severidad
                    severity = 1.0
                    if self.ai_client and not group.empty:
                        print(f"Analizando severidad para Day {d} Hour {h}...")
                        severity = self.ai_client.analyze_batch_patterns(symptoms_summary)
                    
                    new_model[key] = {
                        "count": float(count),
                        "severity": severity,
                        "avg_wait": float(group['wait_time_min'].mean()) if 'wait_time_min' in group else 0
                    }
                    
            else:
                # Procesamiento Legacy (Solo conteo)
                # Validar columnas
                required_cols = ['date', 'hour', 'patients_seen']
                if not all(col in df.columns for col in required_cols):
                    # fallback permissive check or error
                    pass 

                if 'date' in df.columns:
                   df['date'] = pd.to_datetime(df['date'])
                   df['day_of_week'] = df['date'].dt.dayofweek
                
                baseline = df.groupby(['day_of_week', 'hour'])['patients_seen'].mean().reset_index()
                for _, row in baseline.iterrows():
                    key = f"{int(row['day_of_week'])}-{int(row['hour'])}"
                    new_model[key] = {"count": float(row['patients_seen']), "severity": 1.0}

            self.baseline_model = new_model
            
            # Guardar
            self.MODEL_PATH.parent.mkdir(exist_ok=True)
            with open(self.MODEL_PATH, 'w') as f:
                json.dump(self.baseline_model, f)
                
            return {
                "status": "success",
                "mode": "rich_ai" if is_rich else "simple",
                "baseline_entries": len(new_model)
            }

        except Exception as e:
            return {"error": f"Error procesando CSV: {str(e)}"}

    def predict(self, target_time: datetime, factors: EnvironmentalFactors) -> PredictionResult:
        """
        Genera una predicción de recursos para una fecha/hora dada y factores externos.
        """
        # 1. Obtener Línea Base
        day_of_week = target_time.weekday()
        hour = target_time.hour
        key = f"{day_of_week}-{hour}"
        
        # Estructura del modelo ahora puede guardar: {"count": 10.0, "severity": 1.5}
        # o mantener compatibilidad con float simple
        model_entry = self.baseline_model.get(key, 10.0)
        
        if isinstance(model_entry, dict):
            base_demand = model_entry.get("count", 10.0)
            clinical_severity = model_entry.get("severity", 1.0)
        else:
            base_demand = float(model_entry)
            clinical_severity = 1.0
        
        # 2. Calcular Multiplicadores
        factor_score = 1.0
        applied_factors = {}
        
        # Clima
        w_mult = self.MULTIPLIERS["weather"].get(factors.weather, 1.0)
        factor_score *= w_mult
        applied_factors["weather"] = w_mult
        
        # Tráfico
        t_mult = self.MULTIPLIERS["traffic"].get(factors.traffic, 1.0)
        factor_score *= t_mult
        applied_factors["traffic"] = t_mult
        
        # Eventos
        e_mult = self.MULTIPLIERS["event"].get(factors.event, 1.0)
        factor_score *= e_mult
        applied_factors["event"] = e_mult
        
        # 3. Demanda Final Predicha
        predicted_demand = base_demand * factor_score
        
        # 4. Cálculo de Recursos (Heurística)
        import math
        
        # Doctores: (Demanda * Severidad) / Capacidad Dr
        # Severidad alta (cardiacos) aumenta requerimiento aunque sean pocos pacientes
        weighted_demand = predicted_demand * clinical_severity
        required_drs = math.ceil(weighted_demand / self.CAPACITY["doctor"])
        
        # Enfermeras: Ratio 1.5 a 1 con Docs o mín 2
        required_nurses = max(2, math.ceil(required_drs * 1.5))
        
        # Camas/Box: Demanda * Tiempo Estancia Promedio (3 horas) * Factor Ocupación (1.2 buffer)
        # Ley de Little: L = λ * W
        avg_stay_hours = 3.0
        active_patients = predicted_demand * avg_stay_hours
        required_boxes = math.ceil(active_patients * 1.1) # +10% buffer
        
        return PredictionResult(
            predicted_patients_per_hour=round(predicted_demand, 1),
            required_doctors=required_drs,
            required_nurses=required_nurses,
            required_box_units=required_boxes,
            confidence_score=0.85 if key in self.baseline_model else 0.4,
            factors_applied={**applied_factors, "clinical_severity": clinical_severity}
        )

    def record_actual_usage(self, timestamp: str, count: int):
        """Registra el uso real de recursos para feedback loop"""
        self.actual_usage.append({
            "timestamp": timestamp,
            "count": count
        })
        # Mantener solo ultimas 24h (simulado, guardar ultimos 100)
        if len(self.actual_usage) > 100:
            self.actual_usage.pop(0)

    def get_drift_report(self) -> Dict[str, Any]:
        """Calcula desviación entre predicción y realidad"""
        if not self.actual_usage:
            return {"status": "no_data", "drift_percentage": 0.0}
        
        # Comparar ultimo dato real con prediccion promedio (simulado)
        latest = self.actual_usage[-1]
        
        # En prod: buscar prediccion historica para ese timestamp
        # Aquí: comparamos con heurística simple de la hora actual
        dt = datetime.fromisoformat(latest["timestamp"])
        prediction = self.predict(dt, EnvironmentalFactors("sunny", "low", "none"))
        
        predicted_val = prediction.predicted_patients_per_hour
        actual_val = float(latest["count"])
        
        if predicted_val == 0:
            drift = 0.0
        else:
            drift = ((actual_val - predicted_val) / predicted_val) * 100.0
            
        return {
            "status": "active",
            "latest_timestamp": latest["timestamp"],
            "actual": actual_val,
            "predicted": predicted_val,
            "drift_percentage": round(drift, 2),
            "alert": abs(drift) > 20.0
        }

    def check_drift_alert(self) -> bool:
        """Verifica si la desviación supera el umbral crítico (>20%)"""
        report = self.get_drift_report()
        return report.get("alert", False)
