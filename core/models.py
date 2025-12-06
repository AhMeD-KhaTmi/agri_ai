from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class FarmProfile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    crop_type = models.CharField(max_length=50)

    def __str__(self):
        return self.location


class FieldPlot(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    crop_variety = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class SensorReading(models.Model):
    SENSOR_CHOICES = [
        ('moisture', 'Soil Moisture'),
        ('temperature', 'Temperature'),
        ('humidity', 'Humidity'),
    ]

    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE)
    sensor_type = models.CharField(max_length=20, choices=SENSOR_CHOICES)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, default='simulator')

    def __str__(self):
        return f"{self.sensor_type} - {self.value}"


class AnomalyEvent(models.Model):
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE)
    anomaly_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20)
    model_confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class AgentRecommendation(models.Model):
    anomaly_event = models.ForeignKey(AnomalyEvent, on_delete=models.CASCADE)
    recommended_action = models.TextField()
    explanation_text = models.TextField()
    confidence = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    USER_ROLES = [
        ("admin", "Admin"),
        ("farmer", "Farmer"),
        ("agent", "Agent"),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default="farmer")

    def __str__(self):
        return f"{self.user.username} ({self.role})"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
