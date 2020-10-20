from django.urls import path
from .views import InfoView

app_name = 'cart'
urlpatterns = [
    path('', InfoView.as_view(), name='info'),
]
