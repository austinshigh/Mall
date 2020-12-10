from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=30, default="empty")

    def __str__(self):
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    url = models.URLField(max_length=500, default="")
    url2 = models.URLField(max_length=500, null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    date = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def serialize(self):
        return {
            "title": self.title,
            "price": self.price,
            "category": self.category
        }


class Review(models.Model):
    text = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=False)
    username = models.ForeignKey(User, on_delete=models.CASCADE)

    def serialize(self):
        return {
            "Username": self.username,
            "Listing": self.listing.id,
            "Date": self.date.strftime("%b %-d %Y, %-I:%M %p")
        }


class Cart(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    quantity = models.DecimalField(max_digits=3, decimal_places=0, default=1)

    def __str__(self):
        return f"User: {self.user}"


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    body = models.CharField(max_length=2000)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} | {self.time.strftime('%b %-d %Y, %-I:%M %p')}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        null=False, related_name="like")

    def __str__(self):
        return f"Customer: {self.user.username} Body: {self.review.text[:30]}"
