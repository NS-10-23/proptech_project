from django.conf import settings
from django.db import models


class PropertyValuation(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="valuations",
    )

    location = models.CharField(
        max_length=150
    )

    land_aana = models.FloatField(
        verbose_name="Land (Aana)"
    )

    floors = models.FloatField(
        verbose_name="Floors"
    )

    road_feet = models.IntegerField(
        verbose_name="Road Width (Feet)"
    )

    road_type = models.CharField(
        max_length=50,
        verbose_name="Road Type"
    )

    rooms = models.IntegerField(
        verbose_name="Rooms"
    )

    bathrooms = models.IntegerField(
        verbose_name="Bathrooms"
    )

    predicted_price_npr = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    price_formatted = models.CharField(
        max_length=100
    )

    monthly_rent_npr = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    cap_rate = models.CharField(
        max_length=10
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Soft-delete fields
    is_deleted = models.BooleanField(
        default=False
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.location} "
            f"({self.land_aana} Aana) - "
            f"{self.price_formatted}"
        )