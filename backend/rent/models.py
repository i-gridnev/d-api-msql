from django.conf import settings
from django.db import models


class Bike(models.Model):
    name = models.CharField(max_length=200)
    code = models.IntegerField(unique=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    mileage = models.IntegerField(default=0)
    is_rented = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __repr__(self) -> str:
        return f'{self.name} - {self.code} - {"activ" if self.is_active else "deactivated"}'


class Rent(models.Model):
    bike = models.ForeignKey(
        'Bike', related_name='rents', on_delete=models.CASCADE)
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='rents', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    distance = models.IntegerField(default=0)
