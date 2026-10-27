from django.contrib import admin
from .models import PropertyValuation

@admin.register(PropertyValuation)
class PropertyValuationAdmin(admin.ModelAdmin):
    list_display = ('location', 'land_aana', 'floors', 'road_feet', 'price_formatted', 'created_at')
    list_filter = ('location', 'road_type')
    ordering = ('-created_at',)