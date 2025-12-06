import numpy as np
from django.utils import timezone
from datetime import timedelta

# Specification-based thresholds from Table 1
SPEC_THRESHOLDS = {
    'moisture': {
        'normal': (45, 75),
        'anomaly_low': 35,  # <35% is anomaly
        'sudden_drop_threshold': 10,  # >10% drop in 1-3 hours
    },
    'temperature': {
        'normal': (18, 28),
        'anomaly_low': 10,  # <10°C is cold stress
        'anomaly_high': 32,  # >32°C sustained is heat stress
    },
    'humidity': {
        'normal': (45, 75),
        'anomaly_low': 30,  # <30% is dry conditions
        'anomaly_high': 85,  # >85% is excessive moisture
    },
}

class SimpleAnomalyDetector:
    def __init__(self, sensor="moisture", method="threshold", window=10):
        self.sensor = sensor
        self.method = method
        self.window = window
        self.history = []
        if method == "threshold":
            # Use specification-based thresholds
            spec = SPEC_THRESHOLDS.get(sensor, {})
            if sensor == 'moisture':
                self.limits = (spec.get('anomaly_low', 35), spec.get('normal', (45, 75))[1])
            elif sensor == 'temperature':
                self.limits = (spec.get('anomaly_low', 10), spec.get('anomaly_high', 32))
            elif sensor == 'humidity':
                self.limits = (spec.get('anomaly_low', 30), spec.get('anomaly_high', 85))
            else:
                self.limits = (0, 100)

    def step(self, value):
        # returns True if anomaly, otherwise False
        if self.method == "threshold":
            lower, upper = self.limits
            return value < lower or value > upper
        elif self.method == "rolling":
            self.history.append(value)
            if len(self.history) > self.window:
                self.history.pop(0)
            if len(self.history) < self.window:
                return False
            mean = np.mean(self.history)
            std = np.std(self.history)
            return abs(value - mean) > 2.5 * std
        return False

def detect_sudden_drop(plot_id, sensor_type, current_value, current_time):
    """
    Detect sudden drops >10% in 1-3 hours (specification requirement)
    Returns: (is_anomaly, anomaly_type, severity)
    """
    from .models import SensorReading
    
    # Check readings from 1-3 hours ago
    three_hours_ago = current_time - timedelta(hours=3)
    one_hour_ago = current_time - timedelta(hours=1)
    
    recent_readings = SensorReading.objects.filter(
        plot_id=plot_id,
        sensor_type=sensor_type,
        timestamp__gte=three_hours_ago,
        timestamp__lte=one_hour_ago
    ).order_by('-timestamp')[:5]  # Get last 5 readings in that window
    
    if recent_readings.exists():
        # Calculate average of recent readings
        avg_recent = np.mean([r.value for r in recent_readings])
        
        # Check for sudden drop
        if sensor_type == 'moisture':
            drop_threshold = SPEC_THRESHOLDS['moisture']['sudden_drop_threshold']
            drop_percent = avg_recent - current_value
            if drop_percent > drop_threshold:
                return True, f"Sudden {sensor_type} drop ({drop_percent:.1f}% in 1-3h)", "high"
    
    return False, None, None

def detect_drift(plot_id, sensor_type, current_value, current_time):
    """
    Detect gradual drift >20% over 24-48 hours (specification requirement)
    Returns: (is_anomaly, anomaly_type, severity)
    """
    from .models import SensorReading
    
    # Get baseline from 24-48 hours ago
    forty_eight_hours_ago = current_time - timedelta(hours=48)
    twenty_four_hours_ago = current_time - timedelta(hours=24)
    
    baseline_readings = SensorReading.objects.filter(
        plot_id=plot_id,
        sensor_type=sensor_type,
        timestamp__gte=forty_eight_hours_ago,
        timestamp__lte=twenty_four_hours_ago
    )
    
    if baseline_readings.exists():
        avg_baseline = np.mean([r.value for r in baseline_readings])
        drift_percent = abs((current_value - avg_baseline) / avg_baseline * 100) if avg_baseline > 0 else 0
        
        if drift_percent > 20:
            direction = "increase" if current_value > avg_baseline else "decrease"
            return True, f"{sensor_type.capitalize()} drift ({drift_percent:.1f}% {direction} over 24-48h)", "medium"
    
    return False, None, None

# Simple global per-sensor rolling stats for demonstration (thread-safe solution may be needed for production!)
rolling_detectors = {
    'moisture': SimpleAnomalyDetector("moisture", method="rolling"),
    'temperature': SimpleAnomalyDetector("temperature", method="rolling"),
    'humidity': SimpleAnomalyDetector("humidity", method="rolling"),
}

threshold_detectors = {
    'moisture': SimpleAnomalyDetector("moisture", method="threshold"),
    'temperature': SimpleAnomalyDetector("temperature", method="threshold"),
    'humidity': SimpleAnomalyDetector("humidity", method="threshold"),
}

def anomaly_inference(sensor_type, value, method="rolling"):
    """
    Basic inference without context (used for simple threshold checks)
    """
    if method == "threshold":
        return threshold_detectors[sensor_type].step(value)
    elif method == "rolling":
        return rolling_detectors[sensor_type].step(value)
    return False

def comprehensive_anomaly_detection(plot_id, sensor_type, value, timestamp):
    """
    Comprehensive anomaly detection matching specification:
    - Threshold violations (normal ranges)
    - Sudden drops (>10% in 1-3 hours)
    - Data drift (>20% over 24-48h)
    
    Returns: (is_anomaly, anomaly_type, severity, confidence)
    """
    # 1. Check threshold violations (specification-based)
    spec = SPEC_THRESHOLDS.get(sensor_type, {})
    anomaly_type = None
    severity = "medium"
    confidence = 0.85
    
    if sensor_type == 'moisture':
        if value < spec.get('anomaly_low', 35):
            anomaly_type = f"Low {sensor_type} (<{spec.get('anomaly_low', 35)}%)"
            severity = "high"
        elif value > spec.get('normal', (45, 75))[1]:
            anomaly_type = f"High {sensor_type} (>{spec.get('normal', (45, 75))[1]}%)"
            severity = "medium"
    elif sensor_type == 'temperature':
        if value < spec.get('anomaly_low', 10):
            anomaly_type = f"Cold stress (<{spec.get('anomaly_low', 10)}°C)"
            severity = "high"
        elif value > spec.get('anomaly_high', 32):
            anomaly_type = f"Heat stress (>{spec.get('anomaly_high', 32)}°C sustained)"
            severity = "high"
        elif value < spec.get('normal', (18, 28))[0] or value > spec.get('normal', (18, 28))[1]:
            anomaly_type = f"Temperature out of normal range"
            severity = "medium"
    elif sensor_type == 'humidity':
        if value < spec.get('anomaly_low', 30):
            anomaly_type = f"Dry conditions (<{spec.get('anomaly_low', 30)}%)"
            severity = "medium"
        elif value > spec.get('anomaly_high', 85):
            anomaly_type = f"Excessive moisture (>{spec.get('anomaly_high', 85)}%)"
            severity = "medium"
        elif value < spec.get('normal', (45, 75))[0] or value > spec.get('normal', (45, 75))[1]:
            anomaly_type = f"Humidity out of normal range"
            severity = "low"
    
    # 2. Check for sudden drops (especially important for moisture)
    if sensor_type == 'moisture':
        sudden_drop, drop_type, drop_severity = detect_sudden_drop(plot_id, sensor_type, value, timestamp)
        if sudden_drop:
            anomaly_type = drop_type
            severity = drop_severity
            confidence = 0.95  # High confidence for sudden drops
            return True, anomaly_type, severity, confidence
    
    # 3. Check for data drift
    drift, drift_type, drift_severity = detect_drift(plot_id, sensor_type, value, timestamp)
    if drift and not anomaly_type:  # Only if no threshold violation already detected
        anomaly_type = drift_type
        severity = drift_severity
        confidence = 0.80
    
    # Return result
    if anomaly_type:
        return True, anomaly_type, severity, confidence
    
    return False, None, None, 0.0
