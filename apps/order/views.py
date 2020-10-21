from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from goods.models import GoodsSKU
from user.models import Address

# Create your views here.
class PlaceView(LoginRequiredMixin, View):
    def post(self, request):
        ''' 显示订单页面 '''
        user = request.user
        sku_ids = request.POST.getlist("sku_ids") # 只传 sku_id，其它信息从数据库中读取
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        skus = []
        total_count = 0
        total_price = 0
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            count = conn.hget(cart_key, sku_id)
            count = int(count)
            amount = sku.price * count
            sku.amount = amount
            sku.count = count
            skus.append(sku)

            total_count += count
            total_price += amount
        transit_price = 10
        total_pay = total_price + transit_price

        sku_ids = ','.join(sku_ids)
        addrs = Address.objects.filter(user=user)

        context = {
            'skus': skus,
            'total_count': total_count,
            'total_price': total_price,
            'addrs': addrs,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'sku_ids': sku_ids,
        }
        return render(request, "order_place.html", context)
