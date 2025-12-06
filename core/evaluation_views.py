"""
API endpoints for evaluation metrics
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .evaluation import (
    evaluate_model_performance,
    evaluate_agent_performance,
    get_system_evaluation,
    generate_synthetic_test_data,
    AnomalyDetectionEvaluator
)
from .models import FieldPlot


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def evaluation_metrics(request):
    """
    GET /api/evaluation/
    Returns all evaluation metrics
    """
    plot_id = request.query_params.get('plot', None)
    
    if plot_id:
        try:
            plot = FieldPlot.objects.get(id=plot_id)
            plot_id = plot.id
        except FieldPlot.DoesNotExist:
            return Response({'error': 'Plot not found'}, status=404)
    else:
        # Use first available plot or default to 1
        first_plot = FieldPlot.objects.first()
        plot_id = first_plot.id if first_plot else 1
    
    # Model evaluation
    model_metrics = evaluate_model_performance(plot_id)
    
    # Agent evaluation
    agent_metrics = evaluate_agent_performance()
    
    # System evaluation
    system_metrics = get_system_evaluation()
    
    return Response({
        'ml_model_metrics': model_metrics,
        'agent_metrics': agent_metrics,
        'system_metrics': system_metrics,
        'plot_id': plot_id,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_evaluation_test(request):
    """
    POST /api/evaluation/test/
    Run evaluation test with synthetic data
    Body: {"plot_id": 1, "num_readings": 100, "anomaly_rate": 0.15}
    """
    plot_id = request.data.get('plot_id', 1)
    num_readings = request.data.get('num_readings', 100)
    anomaly_rate = request.data.get('anomaly_rate', 0.15)
    
    try:
        plot = FieldPlot.objects.get(id=plot_id)
    except FieldPlot.DoesNotExist:
        return Response({'error': 'Plot not found'}, status=404)
    
    # Generate test data
    test_data = generate_synthetic_test_data(plot_id, num_readings, anomaly_rate)
    
    # Run evaluation
    metrics = evaluate_model_performance(plot_id, test_data)
    
    return Response({
        'message': f'Evaluation test completed with {num_readings} readings',
        'metrics': metrics,
        'test_data_size': len(test_data),
        'expected_anomalies': sum(1 for _, is_anomaly, _ in test_data if is_anomaly),
    })

