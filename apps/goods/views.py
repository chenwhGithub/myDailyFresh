from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection
from .models import GoodsType, GoodsSKU, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

# Create your views here.
class IndexView(View):
    def get(self, request):
        ''' 点击首页按钮，跳转到 index.html 页面 '''
        types = GoodsType.objects.all() # 获取商品种类信息
        for goodstype in types: # 获取分类商品展示信息
            # 获取该类型下面的商品的标题信息并排序
            title_banner = IndexTypeGoodsBanner.objects.filter(type=goodstype, display_type=0).order_by('index')
            # 获取该类型下面的商品的图片信息并排序
            image_banner = IndexTypeGoodsBanner.objects.filter(type=goodstype, display_type=1).order_by('index')
            # 动态给 type 增加属性，分别保存首页分类商品的文字信息和图片信息
            goodstype.title_banner = title_banner
            goodstype.image_banner = image_banner

        goods_banners = IndexGoodsBanner.objects.all().order_by('index') # 获取首页轮播信息
        promotion_banners = IndexPromotionBanner.objects.all().order_by('index') # 获取首页促销活动信息
        context = {
            'types': types,
            'goods_banners': goods_banners,
            'promotion_banners': promotion_banners,
        }
        return render(request, 'index.html', context)


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
