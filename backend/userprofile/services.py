from django.db.models import F
from .models import Wallet


def charge_wallet(wallet: Wallet, price) -> bool:
    success = Wallet.objects.filter(
        id=wallet.id, is_active=True, money__gte=price).update(money=F('money') - price)
    return success > 0


def debit_wallet(wallet: Wallet, amount) -> bool:
    success = Wallet.objects.filter(
        id=wallet.id).update(money=F('money') + amount)
    return success > 0