from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listings(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    closed = models.BooleanField(default=False)
    description = models.CharField(max_length=150)
    category = models.CharField(max_length=30)
    img_url = models.CharField(max_length=100000, blank=True)
    current_bid = models.FloatField(default=0.0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    num_bid = models.IntegerField(default=0)
    user_bid = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="user_bid",
    )
    bidders = models.ManyToManyField(User, related_name="bidders_listing", blank=True)
    
    def __str__(self):
        return str(f"{self.name} User: {self.user.username}")


class Comments(models.Model):
    listing = models.ForeignKey(
        Listings, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.CharField(max_length=500, default="")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="user",
    )
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing")