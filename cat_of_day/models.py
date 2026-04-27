from django.conf import settings
from django.db import models
from django.utils import timezone
from cats.models import Cat


class DailyCat(models.Model):
    date = models.DateField(unique=True)
    cat = models.ForeignKey(
        Cat,
        on_delete=models.CASCADE,
        related_name='daily_wins',
        null=True,
        blank=True
    )
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.cat}"


class CatVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    vote_date = models.DateField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'vote_date'],
                name='unique_vote_per_day'
            )
        ]
