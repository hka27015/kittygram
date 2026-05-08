from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from cats.models import Cat


class DailyCat(models.Model):
    date = models.DateField(unique=True)
    cat = models.ForeignKey(Cat, on_delete=models.SET_NULL, null=True, blank=True, related_name='daily_wins')
    score = models.PositiveIntegerField(default=0)
    is_finalized = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date}"


class CatVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='votes')
    vote_date = models.DateField(default=now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'vote_date'], name='unique_vote_per_day')
        ]


class Prediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='predictions')
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    is_success = models.BooleanField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_prediction_per_day')
        ]