from django.urls import path
from .views import InfoView, UpdateView, DeleteView

app_name = 'cart'
urlpatterns = [
    path('', InfoView.as_view(), name='info'),
    path('update', UpdateView.as_view(), name='update'),
    path('delete', DeleteView.as_view(), name='delete'),
]
