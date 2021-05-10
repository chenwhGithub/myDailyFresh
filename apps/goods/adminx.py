import xadmin
from django.core.cache import cache
from .models import GoodsType, GoodsSKU, Goods, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner
# Register your models here.

class GoodsTypeAdmin(object):
    list_display = ['name', 'logo', 'image']
    search_fields = ['name', 'logo']
    list_filter = ['name', 'logo']
    ordering = ['-name']
    model_icon = 'fa fa-desktop'

    def save_model(self):
        cache.delete('index_data')

    def delete_model(self):
        cache.delete('index_data')


class GoodsSKUAdmin(object):
    list_display = ['type', 'goods', 'name', 'desc', 'price', 'image', 'stock', 'sales', 'status']
    ordering = ['-type']
    model_icon = 'fa fa-hourglass'

    def save_model(self):
        cache.delete('index_data')

    def delete_model(self):
        cache.delete('index_data')


class GoodsAdmin(object):
    list_display = ['name', 'detail']
    ordering = ['-name']
    model_icon = 'fa fa-heartbeat'

    def save_model(self):
        cache.delete('index_data')

    def delete_model(self):
        cache.delete('index_data')


class IndexGoodsBannerAdmin(object):
    list_display = ['sku', 'image', 'index']
    ordering = ['index']
    model_icon = 'fa fa-university'

    def save_model(self):
        cache.delete('index_data')

    def delete_model(self):
        cache.delete('index_data')


class IndexTypeGoodsBannerAdmin(object):
    list_display = ['type', 'sku', 'display_type', 'index']
    ordering = ['index']
    model_icon = 'fa fa-life-ring'

    def save_model(self):
        cache.delete('index_data')

    def delete_model(self):
        cache.delete('index_data')


class IndexPromotionBannerAdmin(object):
    list_display = ['name', 'url', 'image', 'index']
    ordering = ['index']
    model_icon = 'fa fa-microchip'

    def save_model(self):
        cache.delete('index_data')

    def delete_model(self):
        cache.delete('index_data')


xadmin.site.register(GoodsType, GoodsTypeAdmin)
xadmin.site.register(GoodsSKU, GoodsSKUAdmin)
xadmin.site.register(Goods, GoodsAdmin)
xadmin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
xadmin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
xadmin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
