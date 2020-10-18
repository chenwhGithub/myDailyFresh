from django.urls import path
from django.conf.urls import url
from . import views
from .views import IndexView, DetailView

app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    url(r'^goods/(?P<goods_id>\d+)/$', DetailView.as_view(), name='detail'),
]
