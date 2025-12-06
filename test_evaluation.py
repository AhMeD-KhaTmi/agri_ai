#!/usr/bin/env python
"""
Evaluation Test Harness
Tests ML model and agent performance using synthetic data with ground truth labels
As per specification requirements
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_ai.settings')
django.setup()

from core.evaluation import (
    AnomalyDetectionEvaluator,
    generate_synthetic_test_data,
    evaluate_model_performance,
    evaluate_agent_performance,
    get_system_evaluation
)
from core.models import FieldPlot, FarmProfile
from django.contrib.auth import get_user_model
from django.utils import timezone


def print_metrics(title: str, metrics: dict):
    """Pretty print metrics"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    for key, value in metrics.items():
        if isinstance(value, float):
            if 'rate' in key.lower() or 'score' in key.lower() or 'precision' in key.lower() or 'recall' in key.lower():
                print(f"  {key:.<40} {value*100:.2f}%")
            else:
                print(f"  {key:.<40} {value:.4f}")
        else:
            print(f"  {key:.<40} {value}")
    print()


def run_evaluation_test_harness():
    """Main test harness"""
    print("="*60)
    print("🧪 EVALUATION TEST HARNESS")
    print("Testing ML Model and Agent Performance")
    print("="*60)
    
    # Get or create a test plot
    User = get_user_model()
    user, _ = User.objects.get_or_create(username='test_user', defaults={'password': 'test123'})
    if not hasattr(user, 'userprofile'):
        from core.models import UserProfile
        UserProfile.objects.create(user=user, role='admin')
    
    farm, _ = FarmProfile.objects.get_or_create(
        owner=user,
        defaults={'location': 'Test Farm', 'crop_type': 'Test Crop'}
    )
    plot, _ = FieldPlot.objects.get_or_create(
        farm=farm,
        defaults={'name': 'Test Plot', 'crop_variety': 'Test Variety'}
    )
    
    print(f"\n📊 Using Plot ID: {plot.id}")
    
    # Test 1: Generate synthetic test data
    print("\n🔬 Test 1: Generating synthetic test data with ground truth labels...")
    test_data = generate_synthetic_test_data(plot.id, num_readings=200, anomaly_rate=0.15)
    
    actual_anomalies = sum(1 for _, is_anomaly, _ in test_data if is_anomaly)
    normal_readings = len(test_data) - actual_anomalies
    
    print(f"   Generated {len(test_data)} test readings")
    print(f"   - Actual anomalies: {actual_anomalies} ({actual_anomalies/len(test_data)*100:.1f}%)")
    print(f"   - Normal readings: {normal_readings} ({normal_readings/len(test_data)*100:.1f}%)")
    
    # Test 2: Evaluate ML model performance
    print("\n🤖 Test 2: Evaluating ML Model Performance...")
    model_metrics = evaluate_model_performance(plot.id, test_data)
    print_metrics("ML Model Evaluation Metrics", model_metrics)
    
    # Test 3: Evaluate Agent Performance
    print("\n🤖 Test 3: Evaluating AI Agent Performance...")
    agent_metrics = evaluate_agent_performance()
    print_metrics("AI Agent Evaluation Metrics", agent_metrics)
    
    # Test 4: System-level evaluation
    print("\n📈 Test 4: System-Level Evaluation...")
    system_metrics = get_system_evaluation()
    print_metrics("System Evaluation Metrics", system_metrics)
    
    # Summary
    print("\n" + "="*60)
    print("📊 EVALUATION SUMMARY")
    print("="*60)
    
    print(f"\n✅ ML Model Performance:")
    print(f"   Precision: {model_metrics['precision']*100:.2f}%")
    print(f"   Recall: {model_metrics['recall']*100:.2f}%")
    print(f"   F1-Score: {model_metrics['f1_score']*100:.2f}%")
    print(f"   False Positive Rate: {model_metrics['false_positive_rate']*100:.2f}%")
    
    if agent_metrics.get('average_decision_latency_seconds'):
        print(f"\n✅ AI Agent Performance:")
        print(f"   Average Relevance: {agent_metrics['average_recommendation_relevance']*100:.2f}%")
        print(f"   Average Latency: {agent_metrics['average_decision_latency_seconds']*1000:.2f}ms")
        print(f"   Latency < 1 second: {'✅ Yes' if agent_metrics.get('latency_under_1_second') else '⚠️  No'}")
    
    print(f"\n✅ System Status:")
    print(f"   Total Readings: {system_metrics['total_sensor_readings']}")
    print(f"   Anomalies Detected: {system_metrics['total_anomalies_detected']}")
    print(f"   Recommendations: {system_metrics['total_recommendations_generated']}")
    
    print("\n" + "="*60)
    print("✅ Evaluation Test Harness Complete!")
    print("="*60)
    
    return {
        'model_metrics': model_metrics,
        'agent_metrics': agent_metrics,
        'system_metrics': system_metrics,
    }


if __name__ == "__main__":
    try:
        results = run_evaluation_test_harness()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error running evaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

