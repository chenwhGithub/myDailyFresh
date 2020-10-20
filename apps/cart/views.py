from django.shortcuts import render
from django.views.generic import View
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from goods.models import GoodsSKU

# Create your views here.
class InfoView(LoginRequiredMixin , View):
    ''' 购物车页面显示 '''
    def get(self, request):
        user = request.user
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        cart_dict = conn.hgetall(cart_key)

        skus = []
        total_count = 0
        total_price = 0
        for sku_id, count in cart_dict.items():
            sku = GoodsSKU.objects.get(id=sku_id)
            cnt = int(count)
            amount = sku.price * cnt
            sku.amount = amount # 动态增加属性
            sku.count = cnt
            skus.append(sku)

            total_count += cnt
            total_price += amount

        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus,
        }
        return render(request, 'cart.html', context)
