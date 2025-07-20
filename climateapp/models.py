# climateapp/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now 

class ImpactRecord(models.Model):
    id:int
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    diet_co2 = models.FloatField(default=0)
    commute_co2 = models.FloatField(default=0)
    energy_co2 = models.FloatField(default=0)
    water_co2 = models.FloatField(default=0)
    total_co2 = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.total_co2} kg on {self.created_at.date()}"

class Task(models.Model):
    id:int
    DAILY = 'daily'
    WEEKLY = 'weekly'
    TASK_TYPE_CHOICES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES, default=DAILY)
    day_of_week = models.CharField(max_length=10, blank=True, null=True)  # For daily tasks like "Monday"
    goal = models.CharField(max_length=50, blank=True, null=True)
    is_weekly = models.BooleanField(default=False)  # New: to distinguish weekly tasks

    def __str__(self):
        return self.title

class UserTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateField(default=now)  

    def __str__(self):
        return f"{self.user.username} - {self.task.title}"