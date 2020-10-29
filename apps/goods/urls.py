from django.urls import path
from django.conf.urls import url
from . import views
from .views import IndexView, DetailView, ListView, GoodsSeachView

app_name = 'goods'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('detail/<int:goods_id>', DetailView.as_view(), name='detail'),
    path('list/<int:type_id>/<int:page_num>', ListView.as_view(), name='list'),
    path('search/', GoodsSeachView(), name='search'), # / 必需，完整 url = /search/?q=xx
]
