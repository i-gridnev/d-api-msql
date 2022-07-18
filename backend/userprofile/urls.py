from django.urls import path

from . import views

app_name = 'profile'
urlpatterns = [
    path('', views.UserListView.as_view(), name='index'),
]