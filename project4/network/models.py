from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.views.generic import ListView

class User(AbstractUser):
    pass
class Follows(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    class Meta:
        unique_together = ['user', 'follower']

class Posts(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    post = models.CharField(max_length=300)
    timestamp = models.DateTimeField(default=now)
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author,
            "post": self.post,
            "timestamp": self.timestamp,
            "likes": self.likes
        }

class Paginate(ListView):
    paginate_by = 10
    model = Posts
