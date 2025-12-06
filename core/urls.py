from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # ✅ correct import
from .views import (
    SensorReadingCreateView,
    SensorReadingListView,
    AnomalyListView,
    RecommendationListView,
    FieldPlotListView,
    register_user
)
from .evaluation_views import evaluation_metrics, run_evaluation_test

urlpatterns = [
    path('sensor-readings/', SensorReadingCreateView.as_view()),
    path('sensor-readings/list/', SensorReadingListView.as_view()),
    path('anomalies/', AnomalyListView.as_view()),
    path('recommendations/', RecommendationListView.as_view()),
    path('plots/', FieldPlotListView.as_view()),

    # JWT ENDPOINTS
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register_user, name='register'),
    
    # EVALUATION ENDPOINTS
    path('evaluation/', evaluation_metrics, name='evaluation_metrics'),
    path('evaluation/test/', run_evaluation_test, name='run_evaluation_test'),
]
