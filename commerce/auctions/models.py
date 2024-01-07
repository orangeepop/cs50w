from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

CATEGORIES = (
    ('1', 'Fashion'),
    ('2', 'Toys'),
    ('3', 'Electronics'),
    ('4', 'Home'),
    ('5', 'Other'),
)

class User(AbstractUser):
    pass

class Listings(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=64)
    price = models.IntegerField()
    description = models.CharField(max_length=64)
    image = models.URLField(blank = True)
    category = models.CharField(max_length=1, choices=CATEGORIES)
    closed = models.BooleanField(default=False)
    winner = models.CharField(max_length=64, blank=True)
    
class Watchlist(models.Model):
    user = models.CharField(max_length=64)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE)
    class Meta:
        unique_together = ("user", "listing")

class Bids(models.Model):
    user = models.CharField(max_length=64)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE)
    bid = models.IntegerField()
    highest_bid = models.BooleanField()

class Comments(models.Model):
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
