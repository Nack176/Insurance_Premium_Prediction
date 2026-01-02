from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('blue', 'Blue'),
        ('green', 'Green'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')

    def __str__(self):
        return f"{self.user.username}'s profile"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)  # 'male' or 'female'
    bmi = models.FloatField()
    children = models.IntegerField()
    smoker = models.CharField(max_length=3)  # 'yes' or 'no'
    region = models.CharField(max_length=20)
    predicted_premium = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for {self.user.username} - ${self.predicted_premium}"

    class Meta:
        ordering = ['-created_at']
