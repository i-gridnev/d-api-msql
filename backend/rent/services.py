from datetime import datetime, timedelta
from decimal import ROUND_DOWN, Decimal
from rest_framework.exceptions import NotFound, ParseError
from django.utils import timezone
from django.db.models import F

from .models import Bike, Rent


def reserve_bike(bike_id: int) -> Bike:
    bike = get_bike(bike_id)
    success = Bike.objects.filter(
        id=bike_id, is_rented=False).update(is_rented=True)
    if success > 0:
        bike.is_rented = True  # for consistency without query
        return bike
    raise ParseError('Bike is already rented')


def release_bike_reserve(bike_id: int, distance: int = 0) -> None:
    success = Bike.objects.filter(id=bike_id)
    if distance:
        success = success.update(
            is_rented=False, mileage=F('mileage') + distance)
    else:
        success = success.update(is_rented=False)
    if not success > 0:
        raise ParseError('Integrity problem - unable to update Bike')


def get_bike(bike_id: int) -> Bike:
    try:
        return Bike.objects.get(id=bike_id, is_active=True)
    except Bike.DoesNotExist:
        raise NotFound('Bike not found or is deactivated')


def create_rent(bike: Bike, user) -> Rent:
    rent = Rent.objects.create(bike=bike, tenant=user)
    rent.transaction_set.create(
        wallet=user.wallet, credit_amount=bike.price)
    return rent


def stop_rent(rent_id: int, user_id: int, distance: int) -> Rent:
    validate_rent(rent_id, user_id)
    success = Rent.objects.filter(
        id=rent_id, ended_at__isnull=True).update(ended_at=timezone.now(), distance=distance)
    if success > 0:
        # refresh rent from db with bike
        return Rent.objects.select_related('bike').get(id=rent_id)
    raise ParseError('Rent invalid, already finished')


def validate_rent(rent_id: int, user_id: int) -> None:
    if not Rent.objects.filter(id=rent_id, tenant__id=user_id).exists():
        raise NotFound('Your rent with that id is not found')


def calc_minutes_to_refund(created_at: datetime, ended_at: datetime) -> int:
    return round(((ended_at - created_at) / timedelta(minutes=1)) % 60)


def calc_refund_amount(minutes: int, price: Decimal) -> Decimal:
    return Decimal(price*minutes/60).quantize(Decimal('.01'), rounding=ROUND_DOWN)
