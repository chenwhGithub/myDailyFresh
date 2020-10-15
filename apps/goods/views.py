from django.shortcuts import render
from django.views.generic import View
from .models import GoodsType

# Create your views here.
class IndexView(View):
    def get(self, request):
        ''' 点击首页按钮，跳转到 index.html 页面 '''
        types = GoodsType.objects.all() # 获取商品种类信息
        context = {
            'types': types,
        }
        return render(request, 'index.html', context)