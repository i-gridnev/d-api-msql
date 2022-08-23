
from django.urls import path, include
from . import views

app_name = 'rent'
urlpatterns = [
    path('', views.RentDetailView.as_view(), name='rent_bike'),
    path('bikes/', views.BikeListView.as_view(), name='crud_bike_list'),
    path('bike/<int:bike_id>/', views.BikeDetailView.as_view(), name='crud_bike_detail'),
]
