from django.db import models
import reddit_analysis as ra

class User(models.Model):
    username = models.CharField(max_length=50)
    count = models.IntegerField()
