from django.db import models
from django.contrib.auth.models import User

# User der profile er data save korar jonno
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, null=True, blank=True)
    last_risk_score = models.IntegerField(null=True, blank=True)
    last_recommended_policy = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Insurance Agent ba Company der details save korar jonno
class InsuranceAgent(models.Model):
    policy_name = models.CharField(max_length=100) # Jemon: Premium Health Insurance
    company_name = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    office_address = models.TextField()

    def __str__(self):
        return f"{self.agent_name} ({self.company_name}) - {self.policy_name}"
class InsuranceHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    income = models.IntegerField()
    risk_score = models.IntegerField()
    recommended_policy = models.CharField(max_length=100)
    date_saved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.recommended_policy}"