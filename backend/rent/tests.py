from .models import Bike
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django import setup
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
setup()


class BikesCrudTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.bike1 = Bike.objects.create(name='First', code=1111, price=15.1)
        cls.bike2 = Bike.objects.create(name='Second', code=2222, price=10.1)
        cls.bike3 = Bike.objects.create(name='Third', code=3333, price=100.1)

    @classmethod
    def tearDownClass(cls):
        cls.bike1.delete()
        cls.bike2.delete()
        cls.bike3.delete()

    def test_get_all_bikes(self):
        url = reverse('rent:crud_bike_list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_create_bike(self):
        url = reverse('rent:crud_bike_list')
        new_bike = {
            "name": "new_bike",
            "code": 2205061,
            "price": 10.2
        }
        response = self.client.post(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], new_bike['name'])

    def test_create_invalid_bike(self):
        url = reverse('rent:crud_bike_list')
        new_bike = {
            "name": "new_bike",
            "price": 10.2
        }
        response = self.client.post(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_bike_with_existing_code(self):
        url = reverse('rent:crud_bike_list')
        new_bike = {
            "name": "some_new_bike",
            "code": 3333,
            "price": 10.2
        }
        response = self.client.post(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BikeCrudTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.bike1 = Bike.objects.create(name='First', code=1111, price=15.1)
        cls.bike2 = Bike.objects.create(name='Second', code=2222, price=10.1)
        cls.bike3 = Bike.objects.create(name='Third', code=3333, price=100.1)

    @classmethod
    def tearDownClass(cls):
        cls.bike1.delete()
        cls.bike2.delete()
        cls.bike3.delete()

    def test_get_one_bike(self):
        url = reverse('rent:crud_bike_detail', args=(self.bike1.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.bike1.name)

    def test_get_not_existing_bike(self):
        url = reverse('rent:crud_bike_detail', args=(1012,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_create_new_bike(self):
        url = reverse('rent:crud_bike_detail', args=(1224,))
        new_bike = {
            "name": "some_new_bike",
            "code": 10124,
            "price": 18.2
        }
        response = self.client.put(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], new_bike['name'])

    def test_put_update_bike_with_existing_code(self):
        url = reverse('rent:crud_bike_detail', args=(self.bike2.id,))
        new_bike = {
            "name": "some_new_bike",
            "code": self.bike1.code,
            "price": 18.2
        }
        response = self.client.put(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_put_update_bike_partial(self):
        url = reverse('rent:crud_bike_detail', args=(self.bike2.id,))
        new_bike = {
            "name": "some_new_bike",
        }
        response = self.client.put(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_update_bike_success(self):
        url = reverse('rent:crud_bike_detail', args=(self.bike2.id,))
        new_bike = {
            "name": "some_new_bike",
            "code": 136987,
            "price": 18.2
        }
        response = self.client.put(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], new_bike['name'])

    def test_patch_update_bike_success(self):
        url = reverse('rent:crud_bike_detail', args=(self.bike1.id,))
        new_bike = {
            "price": 800.2
        }
        response = self.client.patch(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['price']), new_bike['price'])

    def test_patch_update_bike_code_exists(self):
        url = reverse('rent:crud_bike_detail', args=(self.bike1.id,))
        new_bike = {
            "code": self.bike2.code
        }
        response = self.client.patch(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_patch_update_not_existing_bike(self):
        url = reverse('rent:crud_bike_detail', args=(1345,))
        new_bike = {
            "some": 4568
        }
        response = self.client.patch(url, data=new_bike, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_bike_success(self):
        url = reverse('rent:crud_bike_detail', args=(self.bike1.id,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_bike(self):
        url = reverse('rent:crud_bike_detail', args=(1245,))
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)