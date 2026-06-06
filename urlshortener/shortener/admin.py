from django.contrib import admin
from .models import ShortURL, ClickAnalytics

@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ['short_code', 'user', 'original_url', 'click_count', 'created_at', 'is_active']
    list_filter = ['is_active', 'custom_code', 'created_at']
    search_fields = ['short_code', 'original_url', 'user__username']

@admin.register(ClickAnalytics)
class ClickAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['short_url', 'clicked_at', 'ip_address']
    list_filter = ['clicked_at']
