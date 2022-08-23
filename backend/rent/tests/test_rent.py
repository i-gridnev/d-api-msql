from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django import setup
import os

from rent.models import Bike
from userprofile.models import Wallet
from rent.services import *

from userprofile.services import charge_wallet, debit_wallet

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
setup()


class RentTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.bike_ok = Bike.objects.create(name='First', code=1111, price=15.01)
        cls.rented_bike = Bike.objects.create(
            name='Second', code=2222, price=10.1, is_rented=True)
        cls.deactivated_bike = Bike.objects.create(
            name='Third', code=3333, price=18.4, is_active=False)
        cls.user_ok = get_user_model().objects.create(
            username='Tester 1', password='tester')
        cls.user_wallet_deactivated = get_user_model().objects.create(
            username='Tester 2', password='tester2')
        cls.user_poor = get_user_model().objects.create(
            username='Tester 3', password='tester3')
        Wallet.objects.create(id=cls.user_ok, money=850.12)
        Wallet.objects.create(id=cls.user_wallet_deactivated,
                              money=20.11, is_active=False)
        Wallet.objects.create(id=cls.user_poor, money=0.02)

    @classmethod
    def tearDownClass(cls):
        cls.bike_ok.delete()
        cls.rented_bike.delete()
        cls.deactivated_bike.delete()
        cls.user_ok.delete()
        cls.user_wallet_deactivated.delete()
        cls.user_poor.delete()

    def test_reserve_bike_success(self):
        bike = reserve_bike(self.bike_ok.id)
        self.assertEqual(bike.code, self.bike_ok.code)
        self.assertEqual(bike.is_rented, True)
        bike.refresh_from_db()
        self.assertEqual(bike.is_rented, True)
        self.bike_ok.is_rented = False
        self.bike_ok.save()

    def test_reserve_bike_fail(self):
        with self.assertRaises(ParseError):
            reserve_bike(self.rented_bike.id)

    def test_charge_wallet_success(self):
        before = self.user_ok.wallet.money
        charge = charge_wallet(self.user_ok.wallet, self.bike_ok.price)
        self.user_ok.wallet.refresh_from_db()
        after = before-self.bike_ok.price
        self.assertEqual(charge, True)
        self.assertEqual(float(self.user_ok.wallet.money), after)

    def test_charge_wallet_error(self):
        charge1 = charge_wallet(self.user_poor.wallet, self.bike_ok.price)
        charge2 = charge_wallet(
            self.user_wallet_deactivated.wallet, self.bike_ok.price)
        self.assertEqual(charge1, False)
        self.assertEqual(charge2, False)

    def test_get_bike_success(self):
        test_bike = get_bike(self.bike_ok.id)
        self.assertEqual(test_bike.name, self.bike_ok.name)
        self.assertEqual(test_bike.code, self.bike_ok.code)

    def test_get_bike_not_exists(self):
        with self.assertRaises(NotFound):
            get_bike(3213131)

    def test_create_rent_success(self):
        rent = create_rent(self.bike_ok, self.user_ok)
        self.assertEqual(rent.bike.code, self.bike_ok.code)
        self.assertEqual(rent.tenant.username, self.user_ok.username)
        transaction = rent.transaction_set.first()
        self.assertEqual(float(transaction.credit_amount), self.bike_ok.price)
        self.assertEqual(transaction.wallet, self.user_ok.wallet)

    # def test_request_rent_success(self):
    #     url = reverse('rent:rent_bike')
    #     new_rent = {
    #         "bike_id": self.bike_ok.id,
    #         "user_id": self.user_ok.id
    #     }
    #     response = self.client.post(url, data=new_rent, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(
    #         float(response.data['transaction']['amount']), self.bike1.price)

    # def test_request_rent_no_money(self):
    #     url = reverse('rent:rent_bike')
    #     new_rent = {
    #         "bike_id": self.bike3.id,
    #         "user_id": self.user1.id
    #     }
    #     response = self.client.post(url, data=new_rent, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data['error'], 'Not enough money')


class RentStopTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bike_ok = Bike.objects.create(name='First', code=1111, price=15.01)
        cls.rented_bike = Bike.objects.create(
            name='Second', code=2222, price=10.1, is_rented=True)

        cls.user_ok = get_user_model().objects.create(
            username='Tester 1', password='tester')
        Wallet.objects.create(id=cls.user_ok, money=50.12)
        cls.date_start = timezone.datetime(
            2022, 10, 10, 10, 33, tzinfo=timezone.get_current_timezone())
        cls.date_end1 = timezone.datetime(
            2022, 10, 10, 12, 51, tzinfo=timezone.get_current_timezone())
        cls.distance1 = 15
        cls.rent_ok1 = Rent.objects.create(
            bike=cls.bike_ok, tenant=cls.user_ok, created_at=cls.date_start)

    @classmethod
    def tearDownClass(cls):
        cls.bike_ok.delete()
        cls.rented_bike.delete()
        cls.user_ok.delete()
        cls.rent_ok1.delete()

    def test_validate_rent_success(self):
        validate_rent(self.rent_ok1.id, self.user_ok.id)

    def test_validate_rent_not_owened_by_user(self):
        with self.assertRaises(NotFound):
            validate_rent(self.rent_ok1.id, 101)

    def test_stop_rent(self):
        rent = stop_rent(self.rent_ok1.id, self.user_ok.id, self.distance1)
        self.assertIsNotNone(rent.ended_at)
        self.assertEqual(rent.distance, self.distance1)
        with self.assertRaises(ParseError):
            stop_rent(self.rent_ok1.id, self.user_ok.id, self.distance1)
        rent.ended_at = None
        rent.save()

    def test_release_bike_reserve_success(self):
        release_bike_reserve(self.rented_bike.id)
        self.rented_bike.refresh_from_db()
        self.assertEqual(self.rented_bike.is_rented, False)
        self.rented_bike.is_rented = True
        self.rented_bike.save()

    def test_release_bike_reserve_success_with_distance(self):
        mileage_before = self.rented_bike.mileage
        release_bike_reserve(self.rented_bike.id, self.distance1)
        self.rented_bike.refresh_from_db()
        self.assertEqual(self.rented_bike.is_rented, False)
        mileage_after = self.rented_bike.mileage
        self.assertEqual(mileage_after-mileage_before, self.distance1)
        self.rented_bike.is_rented = True
        self.rented_bike.save()

    def test_release_bike_reserve_error(self):
        with self.assertRaises(ParseError):
            release_bike_reserve(424242)

    def test_calc_minutes_to_refund(self):
        d_start = timezone.datetime(
            2022, 10, 10, 10, 33, tzinfo=timezone.get_current_timezone())
        diff = 12  # 18 min above full hours
        t_delta = timedelta(hours=3, minutes=diff)
        d_end = d_start + t_delta
        res = calc_minutes_to_refund(d_start, d_end)
        self.assertEqual(res, diff)

    def test_calc_refund_amount(self):
        minutes = 30
        price = Decimal(5)
        refund = Decimal(2.5)
        res = calc_refund_amount(minutes, price)
        self.assertEqual(res, refund)
