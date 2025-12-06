from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = '__all__'

class AnomalyEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnomalyEvent
        fields = '__all__'

class AgentRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRecommendation
        fields = '__all__'

class FieldPlotSerializer(serializers.ModelSerializer):
    farm_location = serializers.CharField(source='farm.location', read_only=True)
    farm_crop_type = serializers.CharField(source='farm.crop_type', read_only=True)
    
    class Meta:
        model = FieldPlot
        fields = ['id', 'name', 'crop_variety', 'farm', 'farm_location', 'farm_crop_type']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=['farmer', 'agent', 'admin'], write_only=True, default='farmer')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        role = validated_data.pop('role', 'farmer')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=password
        )
        
        # Update the user profile that was created by the signal
        # The signal automatically creates a UserProfile with default role
        profile = user.userprofile
        profile.role = role
        profile.save()
        
        return user
