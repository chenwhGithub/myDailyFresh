from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

def get_index_data():
    ''' 获取首页数据信息 '''
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