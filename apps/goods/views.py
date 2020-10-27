from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection
from django.core.paginator import Paginator
from django.core.cache import cache
from haystack.views import SearchView
from .models import GoodsType, GoodsSKU, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from order.models import OrderGoods


def get_index_data():
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
    return context

# Create your views here.
class IndexView(View):
    def get(self, request):
        ''' 点击首页按钮，跳转到 index.html 页面 '''
        context = cache.get('index_data')
        if not context:
            context = get_index_data()
            cache.set('index_data', context, 2*3600) # 设置缓冲生存周期单位秒

        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)
        context['cart_count'] = cart_count

        return render(request, 'index.html', context)


class DetailView(View):
    '''点击商品图片，跳转到 detal.html 详情页面'''
    def get(self, request, goods_id):
        types = GoodsType.objects.all()
        sku = GoodsSKU.objects.get(id=goods_id)
        order_goods_list = OrderGoods.objects.filter(sku=sku).exclude(comment="")

        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            history_key = 'history_%d'% user.id
            conn.lrem(history_key, 0, goods_id) # 先列表中删除该id，防止最近浏览记录中存在两个相同的商品
            conn.lpush(history_key, goods_id) # 插入最新浏览的商品id
            conn.ltrim(history_key, 0, 4) # 移除老的浏览的商品id，用于用户中心显示最近浏览信息

            cart_key = 'cart_%d'%user.id
            cart_count = conn.hlen(cart_key)

        context = {
            'types': types,
            'sku': sku,
            'cart_count': cart_count,
            'order_goods_list': order_goods_list,
        }
        return render(request, 'detail.html', context)


# /list/type_id/page_num?sort='default'
class ListView(View):
    ''' 商品列表页 '''
    def get(self, request, type_id, page_num):
        sort_dic = {
            'price': 'price',
            'hot': '-sales', # - 表示降序排列
            'default': '-id',
        }
        types = GoodsType.objects.all()
        type_cur = GoodsType.objects.get(id=type_id)
        sort = request.GET.get('sort')
        sku_list = GoodsSKU.objects.filter(type=type_cur).order_by(sort_dic[sort])

        paginator = Paginator(sku_list, 2) # 每页显示两条记录
        total_page = paginator.num_pages # 总的页数
        page_num = int(page_num)
        if page_num > total_page:
            page_num = 1
        skus_page = paginator.page(page_num) # 当前页的 page 对象

        # 获取显示的页码范围，这里设置只显示三个页码
        page_list = []
        if total_page <= 3: # 若总页数小于3，则将页码全部显示
            page_list = range(1, total_page+1)
        elif page_num == 1: # 若当前页码为第一页，则显示页码 1,2,3
            page_list = range(1, 4)
        elif page_num == total_page: # 若当前页码为最后一页，则显示最后三个页码
            page_list = range(total_page-2, total_page+1)
        else: # 其他情况则显示前一页，当前页，后一页页码
            page_list = range(page_num-1, page_num+2)

        user = request.user
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = "cart_%d"%user.id
            cart_count = conn.hlen(cart_key)

        context = {
            'types': types,
            'type': type_cur,
            'skus_page': skus_page,
            'page_list': page_list,
            'sort': sort,
            'cart_count': cart_count,
        }
        return render(request, 'list.html', context)


class GoodsSeachView(SearchView):
    ''' 商品搜索视图 '''
    def extra_context(self):
        ''' 重载 extra_context 来添加额外的 context 字段 '''
        """ 默认的 context 字段
        context = {
            'query': self.query, # 搜索关键字
            'form': self.form,
            'page': page, # 当前页的page对象，遍历page对象，获取到的是SearchResult类的实例对象，对象的属性object才是模型类的对象
            'paginator': paginator, # 分页paginator对象
            'suggestion': None,
        }
        """
        context = super(GoodsSeachView, self).extra_context()

        user = self.request.user
        types = GoodsType.objects.all()
        cart_count = 0
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = "cart_%d"%user.id
            cart_count = conn.hlen(cart_key)

        # 添加上下文字段
        context['types'] = types
        context['cart_count'] = cart_count
        return context
