from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from .models import *
from .serializers import *

class RolePermission(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Superusers always have admin permissions
        if request.user.is_superuser and 'admin' in self.allowed_roles:
            return True
        profile = getattr(request.user, 'userprofile', None)
        if not profile:
            return False
        return profile.role in self.allowed_roles


class FarmerPermission(RolePermission):
    allowed_roles = ["farmer", "admin"]


class AdminPermission(RolePermission):
    allowed_roles = ["admin"]


class SensorReadingCreateView(generics.CreateAPIView):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated, FarmerPermission]


class SensorReadingListView(generics.ListAPIView):
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated, FarmerPermission]

    def get_queryset(self):
        plot_id = self.request.query_params.get('plot')
        return SensorReading.objects.filter(plot_id=plot_id)


class AnomalyListView(generics.ListAPIView):
    serializer_class = AnomalyEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Farmers see anomalies for their own plots, admins see all
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
            return AnomalyEvent.objects.all()
        # Farmers see anomalies for plots in their farms
        return AnomalyEvent.objects.filter(plot__farm__owner=user)


class RecommendationListView(generics.ListAPIView):
    serializer_class = AgentRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Farmers see recommendations for their own plots, admins see all
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
            return AgentRecommendation.objects.all()
        # Farmers see recommendations for anomalies in their plots
        return AgentRecommendation.objects.filter(anomaly_event__plot__farm__owner=user)


class FieldPlotListView(generics.ListAPIView):
    serializer_class = FieldPlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return plots from farms owned by the current user, or all plots if admin
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
            return FieldPlot.objects.all()
        # Filter by farms owned by the user
        return FieldPlot.objects.filter(farm__owner=user)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User created successfully',
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
