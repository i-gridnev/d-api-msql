from django.conf import settings
from django.db import models


class Wallet(models.Model):
    id = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    money = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    rent = models.ForeignKey(
        'rent.Rent', on_delete=models.CASCADE, blank=True, null=True)
    credit_amount = models.DecimalField(max_digits=5, decimal_places=2)
    debit_amount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
