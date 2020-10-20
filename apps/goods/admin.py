from django.contrib import admin
from django.core.cache import cache
from utils.utils import get_index_data
from celery_tasks.tasks import generate_static_index_html
from .models import GoodsType, GoodsSKU, Goods, GoodsImage, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner

# Register your models here.
class BaseModelAdmin(admin.ModelAdmin):
    '''模型管理站点'''
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        context = get_index_data() # 获取首页数据信息
        generate_static_index_html.delay(context) # 调用 celery 重新生成静态首页文件
        cache.delete('index_data') # 清除缓存，用以当 render index.html 时重新生成 index.html 文件

    def delete_model(self, request, obj):
        super().delete_model(request, obj)

        context = get_index_data()
        generate_static_index_html.delay(context)
        cache.delete('index_data')


admin.site.register(GoodsType, BaseModelAdmin)
admin.site.register(GoodsSKU, BaseModelAdmin)
admin.site.register(Goods, BaseModelAdmin)
admin.site.register(GoodsImage, BaseModelAdmin)
admin.site.register(IndexGoodsBanner, BaseModelAdmin)
admin.site.register(IndexTypeGoodsBanner, BaseModelAdmin)
admin.site.register(IndexPromotionBanner, BaseModelAdmin)
