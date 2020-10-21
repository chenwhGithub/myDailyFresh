from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
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


class UpdateView(View):
    ''' 更新购物车信息 '''
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status': 1, "errmsg": '请先登录'})

        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        sku = GoodsSKU.objects.get(id=sku_id)
        count = int(count)
        if count > sku.stock:
            return JsonResponse({'status':2, 'errmsg':"库存不够"})

        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        conn.hset(cart_key, sku_id, count)

        return JsonResponse({'status':0, 'count':count})


class DeleteView(View):
    def post(self, request):
        ''' 删除购物车信息 '''
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status': 1, "errmsg": '请先登录'})

        sku_id = request.POST.get('sku_id')

        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        conn.hdel(cart_key, sku_id)

        return JsonResponse({'status':0})
