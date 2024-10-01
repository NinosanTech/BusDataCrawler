from django.urls import path
from . import views

urlpatterns = [
    path('geoview/', views.geoview, name='geoview'),
    path('get_bus_data/', views.get_bus_data, name='data'),
]