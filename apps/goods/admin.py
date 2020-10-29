from django.contrib import admin
from django.core.cache import cache
from .models import GoodsType, GoodsSKU, Goods, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner

# Register your models here.
class BaseModelAdmin(admin.ModelAdmin):
    ''' 模型管理站点 '''
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('index_data') # 清除缓存，点击首页重新获取数据

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        cache.delete('index_data')

admin.site.register(GoodsType, BaseModelAdmin)
admin.site.register(GoodsSKU, BaseModelAdmin)
admin.site.register(Goods, BaseModelAdmin)
admin.site.register(IndexGoodsBanner, BaseModelAdmin)
admin.site.register(IndexTypeGoodsBanner, BaseModelAdmin)
admin.site.register(IndexPromotionBanner, BaseModelAdmin)
