from django.contrib import admin
from .models import *

@admin.register(FarmProfile)
class FarmProfileAdmin(admin.ModelAdmin):
    list_display = ['location', 'crop_type', 'owner']
    list_filter = ['crop_type']
    search_fields = ['location', 'owner__username']

@admin.register(FieldPlot)
class FieldPlotAdmin(admin.ModelAdmin):
    list_display = ['name', 'crop_variety', 'farm', 'farm_owner']
    list_filter = ['crop_variety']
    search_fields = ['name', 'farm__location']
    
    def farm_owner(self, obj):
        return obj.farm.owner.username
    farm_owner.short_description = 'Owner'

@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['sensor_type', 'value', 'plot', 'timestamp']
    list_filter = ['sensor_type', 'timestamp']
    readonly_fields = ['timestamp']

@admin.register(AnomalyEvent)
class AnomalyEventAdmin(admin.ModelAdmin):
    list_display = ['anomaly_type', 'severity', 'plot', 'timestamp']
    list_filter = ['severity', 'anomaly_type', 'timestamp']

@admin.register(AgentRecommendation)
class AgentRecommendationAdmin(admin.ModelAdmin):
    list_display = ['recommended_action', 'confidence', 'timestamp']
    list_filter = ['confidence', 'timestamp']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
    
    def save_model(self, request, obj, form, change):
        # If user is a superuser, ensure they have admin role
        if obj.user.is_superuser:
            obj.role = 'admin'
        super().save_model(request, obj, form, change)
