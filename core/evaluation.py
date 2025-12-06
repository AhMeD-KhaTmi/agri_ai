"""
Evaluation Metrics Module
Implements precision, recall, F1-score, and other metrics as per specification
"""
from django.utils import timezone
from datetime import timedelta
from .models import SensorReading, AnomalyEvent
import numpy as np
from typing import List, Tuple, Dict


class AnomalyDetectionEvaluator:
    """
    Evaluates ML model performance using ground truth labels
    """
    
    def __init__(self):
        self.true_positives = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.true_negatives = 0
    
    def add_prediction(self, predicted_anomaly: bool, actual_anomaly: bool):
        """Add a prediction result"""
        if predicted_anomaly and actual_anomaly:
            self.true_positives += 1
        elif predicted_anomaly and not actual_anomaly:
            self.false_positives += 1
        elif not predicted_anomaly and actual_anomaly:
            self.false_negatives += 1
        else:
            self.true_negatives += 1
    
    def precision(self) -> float:
        """Precision: Of all detected anomalies, what percentage are true anomalies?"""
        if self.true_positives + self.false_positives == 0:
            return 0.0
        return self.true_positives / (self.true_positives + self.false_positives)
    
    def recall(self) -> float:
        """Recall: Of all true anomalies, what percentage are detected?"""
        if self.true_positives + self.false_negatives == 0:
            return 0.0
        return self.true_positives / (self.true_positives + self.false_negatives)
    
    def f1_score(self) -> float:
        """F1-score: Harmonic mean of precision and recall"""
        prec = self.precision()
        rec = self.recall()
        if prec + rec == 0:
            return 0.0
        return 2 * (prec * rec) / (prec + rec)
    
    def false_positive_rate(self) -> float:
        """False Positive Rate: Percentage of normal readings incorrectly flagged"""
        if self.false_positives + self.true_negatives == 0:
            return 0.0
        return self.false_positives / (self.false_positives + self.true_negatives)
    
    def accuracy(self) -> float:
        """Overall accuracy"""
        total = self.true_positives + self.false_positives + self.false_negatives + self.true_negatives
        if total == 0:
            return 0.0
        return (self.true_positives + self.true_negatives) / total
    
    def get_metrics(self) -> Dict[str, float]:
        """Get all metrics as dictionary"""
        return {
            'precision': self.precision(),
            'recall': self.recall(),
            'f1_score': self.f1_score(),
            'false_positive_rate': self.false_positive_rate(),
            'accuracy': self.accuracy(),
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives,
            'true_negatives': self.true_negatives,
        }


class AgentEvaluator:
    """
    Evaluates AI Agent performance
    """
    
    def evaluate_recommendation_relevance(self, anomaly_type: str, recommendation: str) -> float:
        """
        Qualitative assessment of recommendation relevance (0.0 to 1.0)
        Simple keyword matching for automated evaluation
        """
        anomaly_lower = anomaly_type.lower()
        rec_lower = recommendation.lower()
        
        # Check if recommendation contains relevant keywords for the anomaly type
        relevance_score = 0.5  # Base score
        
        if "moisture" in anomaly_lower:
            if any(word in rec_lower for word in ["irrigat", "moisture", "water", "drainage"]):
                relevance_score = 0.9
        elif "temperature" in anomaly_lower or "heat" in anomaly_lower or "cold" in anomaly_lower:
            if any(word in rec_lower for word in ["temperature", "heat", "cold", "shade", "cooling", "climate"]):
                relevance_score = 0.9
        elif "humidity" in anomaly_lower:
            if any(word in rec_lower for word in ["humidity", "moisture", "ventilation", "misting"]):
                relevance_score = 0.9
        
        return relevance_score
    
    def measure_decision_latency(self, start_time, end_time) -> float:
        """Measure time from anomaly detection to recommendation (should be <1 second)"""
        return (end_time - start_time).total_seconds()


def generate_synthetic_test_data(plot_id: int, num_readings: int = 100, anomaly_rate: float = 0.15) -> List[Tuple[float, bool, str]]:
    """
    Generate synthetic test data with known ground truth labels
    Returns: List of (value, is_anomaly, sensor_type) tuples
    """
    test_data = []
    np.random.seed(42)  # For reproducibility
    
    sensors = ['moisture', 'temperature', 'humidity']
    
    for sensor in sensors:
        readings_per_sensor = num_readings // len(sensors)
        
        for i in range(readings_per_sensor):
            is_anomaly = np.random.random() < anomaly_rate
            
            if sensor == 'moisture':
                if is_anomaly:
                    value = np.random.choice([np.random.uniform(10, 34), np.random.uniform(76, 95)])
                else:
                    value = np.random.uniform(45, 75)  # Normal range
            elif sensor == 'temperature':
                if is_anomaly:
                    value = np.random.choice([np.random.uniform(5, 9), np.random.uniform(33, 40)])
                else:
                    value = np.random.uniform(18, 28)  # Normal range
            elif sensor == 'humidity':
                if is_anomaly:
                    value = np.random.choice([np.random.uniform(15, 29), np.random.uniform(86, 95)])
                else:
                    value = np.random.uniform(45, 75)  # Normal range
            
            test_data.append((value, is_anomaly, sensor))
    
    return test_data


def evaluate_model_performance(plot_id: int, test_data: List[Tuple[float, bool, str]] = None) -> Dict:
    """
    Evaluate ML model performance using test data with ground truth
    """
    from .ml_module import comprehensive_anomaly_detection
    
    if test_data is None:
        test_data = generate_synthetic_test_data(plot_id, num_readings=100)
    
    evaluator = AnomalyDetectionEvaluator()
    current_time = timezone.now()
    
    for value, is_actual_anomaly, sensor_type in test_data:
        # Get model prediction
        is_predicted_anomaly, _, _, _ = comprehensive_anomaly_detection(
            plot_id=plot_id,
            sensor_type=sensor_type,
            value=value,
            timestamp=current_time
        )
        
        # Compare with ground truth
        evaluator.add_prediction(is_predicted_anomaly, is_actual_anomaly)
        current_time += timedelta(minutes=5)  # Simulate time progression
    
    return evaluator.get_metrics()


def evaluate_agent_performance() -> Dict:
    """
    Evaluate AI Agent performance
    """
    from .models import AnomalyEvent, AgentRecommendation
    from datetime import timedelta
    
    agent_evaluator = AgentEvaluator()
    
    # Get recent anomalies with recommendations
    recent_anomalies = AnomalyEvent.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=7)
    ).prefetch_related('agentrecommendation_set')
    
    relevance_scores = []
    latency_times = []
    
    for anomaly in recent_anomalies:
        try:
            rec = anomaly.agentrecommendation_set.first()
            if rec:
                # Evaluate relevance
                relevance = agent_evaluator.evaluate_recommendation_relevance(
                    anomaly.anomaly_type,
                    rec.recommended_action
                )
                relevance_scores.append(relevance)
                
                # Measure latency (time from anomaly to recommendation creation)
                latency = agent_evaluator.measure_decision_latency(
                    anomaly.timestamp,
                    rec.timestamp
                )
                latency_times.append(latency)
        except Exception:
            continue
    
    avg_relevance = np.mean(relevance_scores) if relevance_scores else 0.0
    avg_latency = np.mean(latency_times) if latency_times else 0.0
    max_latency = np.max(latency_times) if latency_times else 0.0
    
    return {
        'average_recommendation_relevance': avg_relevance,
        'average_decision_latency_seconds': avg_latency,
        'max_decision_latency_seconds': max_latency,
        'latency_under_1_second': max_latency < 1.0 if latency_times else None,
        'evaluated_recommendations': len(relevance_scores),
    }


def get_system_evaluation() -> Dict:
    """
    System-level evaluation metrics
    """
    from .models import SensorReading, AnomalyEvent
    
    # Data consistency checks
    total_readings = SensorReading.objects.count()
    readings_with_plots = SensorReading.objects.filter(plot__isnull=False).count()
    data_consistency = readings_with_plots / total_readings if total_readings > 0 else 1.0
    
    # Anomaly detection rate
    total_anomalies = AnomalyEvent.objects.count()
    anomaly_rate = total_anomalies / total_readings if total_readings > 0 else 0.0
    
    # Recommendation generation rate
    from .models import AgentRecommendation
    total_recommendations = AgentRecommendation.objects.count()
    recommendation_rate = total_recommendations / total_anomalies if total_anomalies > 0 else 0.0
    
    return {
        'total_sensor_readings': total_readings,
        'total_anomalies_detected': total_anomalies,
        'total_recommendations_generated': total_recommendations,
        'data_consistency': data_consistency,
        'anomaly_detection_rate': anomaly_rate,
        'recommendation_generation_rate': recommendation_rate,
    }

