from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string, random


def generate_short_code():
    """Base62 encoding for unique short code generation."""
    chars = string.ascii_letters + string.digits  # a-z A-Z 0-9 = 62 chars
    return ''.join(random.choices(chars, k=6))


class ShortURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='short_urls')
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=20, unique=True)
    custom_code = models.BooleanField(default=False)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    click_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.short_code} -> {self.original_url[:50]}"

    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    def get_short_url(self, request):
        return request.build_absolute_uri(f'/{self.short_code}/')


class ClickAnalytics(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    referrer = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        return f"Click on {self.short_url.short_code} at {self.clicked_at}"
