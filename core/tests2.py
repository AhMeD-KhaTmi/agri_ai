from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from .models import FarmProfile, FieldPlot, SensorReading, AnomalyEvent, AgentRecommendation
import json
from .agent import generate_recommendation

class SensorReadingTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='farmer1', password='testpw123')
        self.profile = self.user.userprofile
        self.profile.role = 'farmer'
        self.profile.save()
        self.farm = FarmProfile.objects.create(owner=self.user, location='Testville', crop_type='wheat')
        self.plot = FieldPlot.objects.create(farm=self.farm, name="PlotA", crop_variety="some-wheat")
        self.client = Client()
        # Generate JWT token
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    def test_normal_sensor_reading(self):
        data = {
            "plot": self.plot.id,
            "sensor_type": "moisture",
            "value": 60.0  # normal value
        }
        resp = self.client.post("/api/sensor-readings/", data=json.dumps(data),
                                content_type="application/json", **self.headers)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(SensorReading.objects.filter(sensor_type="moisture", value=60.0).exists())
        # Should NOT create an anomaly event:
        self.assertFalse(AnomalyEvent.objects.exists())

    def test_anomalous_reading_triggers_event(self):
        data = {
            "plot": self.plot.id,
            "sensor_type": "moisture",
            "value": 8.5  # clear anomaly (low moisture)
        }
        resp = self.client.post("/api/sensor-readings/", data=json.dumps(data),
                                content_type="application/json", **self.headers)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(SensorReading.objects.filter(sensor_type="moisture", value=8.5).exists())
        # Should create at least one anomaly event
        self.assertTrue(AnomalyEvent.objects.exists())
        a = AnomalyEvent.objects.first()
        self.assertIn("moisture", a.anomaly_type.lower())

    def test_permission_required(self):
        # No token provided
        data = {"plot": self.plot.id, "sensor_type": "moisture", "value": 40}
        resp = self.client.post("/api/sensor-readings/", data=json.dumps(data),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 401)

class RecommendationIntegrationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='farmer2', password='testpw123')
        self.profile = self.user.userprofile
        self.profile.role = 'farmer'
        self.profile.save()
        self.farm = FarmProfile.objects.create(owner=self.user, location='Field X', crop_type='corn')
        self.plot = FieldPlot.objects.create(farm=self.farm, name="PlotX", crop_variety="sweet-corn")

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client = Client()
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    def post_sensor_anomaly(self, sensor_type, value):
        data = {
            "plot": self.plot.id,
            "sensor_type": sensor_type,
            "value": value  # set as anomaly
        }
        resp = self.client.post("/api/sensor-readings/", data=json.dumps(data),
                                content_type="application/json", **self.headers)
        return resp

    def test_recommendation_created_for_low_moisture(self):
        resp = self.post_sensor_anomaly("moisture", 5.0)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(AnomalyEvent.objects.filter(anomaly_type__icontains="moisture").exists())
        anomaly = AnomalyEvent.objects.get(anomaly_type__icontains="moisture")
        rec = AgentRecommendation.objects.get(anomaly_event=anomaly)
        action, explanation = generate_recommendation(anomaly.anomaly_type, "moisture", 5.0)
        self.assertIn("irrigate", rec.recommended_action.lower())
        self.assertEqual(rec.explanation_text, explanation)

    def test_recommendation_for_high_temp(self):
        resp = self.post_sensor_anomaly("temperature", 60.0)
        self.assertEqual(resp.status_code, 201)
        # Our anomaly type format is "Heat stress (>32°C sustained)", so search flexibly
        anomaly = AnomalyEvent.objects.filter(
            plot=self.plot
        ).filter(
            anomaly_type__icontains="heat"
        ).first()
        self.assertIsNotNone(anomaly, "Anomaly should be created for high temperature")
        rec = AgentRecommendation.objects.get(anomaly_event=anomaly)
        action, explanation = generate_recommendation(anomaly.anomaly_type, "temperature", 60.0)
        self.assertEqual(rec.explanation_text, explanation)
        self.assertTrue(
            "shade" in rec.recommended_action.lower() or "cooling" in rec.recommended_action.lower(),
            f"Recommendation should mention shade or cooling, got: {rec.recommended_action}"
        )

    def test_recommendation_for_low_humidity(self):
        resp = self.post_sensor_anomaly("humidity", 10.0)
        self.assertEqual(resp.status_code, 201)
        # Our anomaly type format is "Dry conditions (<30%)", so search flexibly
        anomaly = AnomalyEvent.objects.filter(
            plot=self.plot
        ).filter(
            anomaly_type__icontains="dry"
        ).first()
        if not anomaly:
            anomaly = AnomalyEvent.objects.filter(plot=self.plot).first()
        self.assertIsNotNone(anomaly, "Anomaly should be created for low humidity")
        rec = AgentRecommendation.objects.get(anomaly_event=anomaly)
        action, explanation = generate_recommendation(anomaly.anomaly_type, "humidity", 10.0)
        self.assertTrue(
            "misting" in rec.recommended_action.lower() or "humidity" in rec.recommended_action.lower(),
            f"Recommendation should mention misting or humidity, got: {rec.recommended_action}"
        )
        self.assertEqual(rec.explanation_text, explanation)

    def test_no_recommendation_for_normal_value(self):
        resp = self.post_sensor_anomaly("moisture", 60.0)
        self.assertEqual(resp.status_code, 201)
        # No anomaly, so no recommendation
        self.assertFalse(AnomalyEvent.objects.exists())
        self.assertFalse(AgentRecommendation.objects.exists())
