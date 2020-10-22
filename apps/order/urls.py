from django.urls import path
from .views import PlaceView, CreateView

app_name = 'order'
urlpatterns = [
    path('place/', PlaceView.as_view(), name='place'),
    path('create/', CreateView.as_view(), name='create'),
]
