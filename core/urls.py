from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # ✅ correct import
from .views import (
    SensorReadingCreateView,
    SensorReadingListView,
    AnomalyListView,
    RecommendationListView
)

urlpatterns = [
    path('sensor-readings/', SensorReadingCreateView.as_view()),
    path('sensor-readings/list/', SensorReadingListView.as_view()),
    path('anomalies/', AnomalyListView.as_view()),
    path('recommendations/', RecommendationListView.as_view()),

    # JWT ENDPOINTS
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
