from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.timezone import now


class User(AbstractUser):
    pass

class Posts(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    post = models.CharField(max_length=300)
    timestamp = models.DateTimeField(default=now)
    likes = models.IntegerField(default=0)
