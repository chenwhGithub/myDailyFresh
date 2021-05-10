import xadmin
from .models import OrderInfo, OrderGoods
# Register your models here.

class OrderInfoAdmin(object):
    list_display = ['order_id', 'user', 'addr', 'pay_method', 'total_count', 'total_price', 'transit_price', 'status', 'trade_no', 'create_time', 'is_deleted']
    ordering = ['-create_time']
    model_icon = 'fa fa-cart-arrow-down'


class OrderGoodsAdmin(object):
    list_display = ['order', 'sku', 'count', 'price', 'comment', 'comment_time']
    ordering = ['-order']
    model_icon = 'fa fa-gift'


xadmin.site.register(OrderInfo, OrderInfoAdmin)
xadmin.site.register(OrderGoods, OrderGoodsAdmin)
