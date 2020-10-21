from django.urls import path
from .views import PlaceView

app_name = 'order'
urlpatterns = [
    path('place/', PlaceView.as_view(), name='place'),
]
