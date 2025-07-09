from django.db import models


class Task(models.Model):
    text = models.CharField(null=False, blank=False, max_length=128, unique=True)
    is_done = models.BooleanField(default=False)
