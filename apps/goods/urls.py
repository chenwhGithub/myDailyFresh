from django.urls import path
from django.conf.urls import url
from . import views
from .views import IndexView, DetailView, ListView, GoodsSeachView

app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    url(r'^goods/(?P<goods_id>\d+)/$', DetailView.as_view(), name='detail'),
    url(r'^list/(?P<type_id>\d+)/(?P<page_num>\d+)/$', ListView.as_view(), name='list'),
    url(r'^search/', GoodsSeachView(), name='search'),
]
