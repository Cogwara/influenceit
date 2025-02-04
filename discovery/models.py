from django.db import models
from django.conf import settings
from django.utils.text import slugify
from users.models import InfluencerProfile

# Discovery App - Handle influencer search and matching


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    # For FontAwesome or similar icons
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Niche(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='niches')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SavedItem(models.Model):
    ITEM_TYPES = (
        ('influencer', 'Influencer'),
        ('brand', 'Brand'),
        ('campaign', 'Campaign'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    item_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'item_type', 'item_id']

    def __str__(self):
        return f"{self.item_type} saved by {self.user.username}"


class InfluencerList(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    influencers = models.ManyToManyField(
        InfluencerProfile, related_name='lists')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class SearchFilter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    query = models.CharField(max_length=255, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    niches = models.ManyToManyField(Niche, blank=True)
    min_followers = models.IntegerField(null=True, blank=True)
    max_followers = models.IntegerField(null=True, blank=True)
    min_engagement = models.FloatField(null=True, blank=True)
    max_engagement = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class RecentSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'query']

    def __str__(self):
        return f"{self.user.username} - {self.query}"
