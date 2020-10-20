from django.shortcuts import render
from django.views.generic import View
from django.core.cache import cache
from django_redis import get_redis_connection
from utils.utils import get_index_data
from celery_tasks.tasks import generate_static_index_html
from .models import GoodsType, GoodsSKU, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

# Create your views here.
class IndexView(View):
    def get(self, request):
        ''' 点击首页按钮，跳转到 index.html 页面 '''
        context = cache.get('index_data') # 从 cache 获取数据
        if not context:
            context = get_index_data()
            generate_static_index_html.delay(context) # 调用 celery 重新生成静态首页文件
            cache.set('index_data', context, 3600) # 单位秒

        return render(request, 'index.html')


class DetailView(View):
    '''点击商品图片，跳转到 detal.html 详情页面'''
    def get(self, request, goods_id):
        types = GoodsType.objects.all()
        sku = GoodsSKU.objects.get(id=goods_id)

        user = request.user
        if user.is_authenticated:
            conn = get_redis_connection('default')
            history_key = "history_%d"% user.id
            conn.lrem(history_key, 0, goods_id) # 先列表中删除该id，防止最近浏览记录中存在两个相同的商品
            conn.lpush(history_key, goods_id) # 插入最新浏览的商品id
            conn.ltrim(history_key, 0, 4) # 移除老的浏览的商品id，用于用户中心显示最近浏览信息

        context = {
            'types': types,
            'sku': sku,
        }
        return render(request, 'detail.html', context)
