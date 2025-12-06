from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import SensorReading, AnomalyEvent
from .ml_module import anomaly_inference
from .agent import generate_recommendation
from .models import AgentRecommendation

@receiver(post_save, sender=SensorReading)
def detect_anomaly(sender, instance, **kwargs):
    from .ml_module import comprehensive_anomaly_detection
    
    value = instance.value
    timestamp = instance.timestamp if hasattr(instance, 'timestamp') else timezone.now()
    
    # Use comprehensive anomaly detection (matches specification)
    is_anomaly, anomaly_type, severity, confidence = comprehensive_anomaly_detection(
        plot_id=instance.plot.id,
        sensor_type=instance.sensor_type,
        value=value,
        timestamp=timestamp
    )

    if is_anomaly and anomaly_type:
        ev = AnomalyEvent.objects.create(
            plot=instance.plot,
            anomaly_type=anomaly_type,
            severity=severity,
            model_confidence=confidence,
        )
        print(f"🚨 ANOMALY DETECTED: {anomaly_type} (Severity: {severity}, Confidence: {confidence:.2f})")

        # AUTO-GENERATE RECOMMENDATION
        rec_action, explain = generate_recommendation(anomaly_type, instance.sensor_type, value)
        AgentRecommendation.objects.create(
            anomaly_event=ev,
            recommended_action=rec_action,
            explanation_text=explain,
            confidence=severity  # Map severity to confidence
        )
