from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection
from goods.models import GoodsSKU

# Create your views here.
class InfoView(LoginRequiredMixin, View):
    def get(self, request):
        ''' 主页点击我的购物车，跳转到 cart.html 页面 '''
        user = request.user
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        cart_dict = conn.hgetall(cart_key)
        cart_count = conn.hlen(cart_key)

        skus = []
        total_count = 0
        total_price = 0
        for sku_id, count in cart_dict.items():
            sku = GoodsSKU.objects.get(id=sku_id)
            cnt = int(count)
            amount = sku.price * cnt
            sku.amount = amount
            sku.count = cnt
            skus.append(sku)

            total_count += cnt
            total_price += amount

        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus,
            'cart_count': cart_count,
        }
        return render(request, 'cart.html', context)


class UpdateView(View):
    def post(self, request):
        ''' 更新购物车信息 '''
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status':1, 'errmsg':'请先登录'})

        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        sku = GoodsSKU.objects.get(id=sku_id)
        count = int(count)
        if count > sku.stock:
            return JsonResponse({'status':2, 'errmsg':'库存不够'})

        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        conn.hset(cart_key, sku_id, count)

        return JsonResponse({'status':0, 'count':count})


class DeleteView(View):
    def post(self, request):
        ''' 删除购物车信息 '''
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status':1, 'errmsg':'请先登录'})

        sku_id = request.POST.get('sku_id')

        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        conn.hdel(cart_key, sku_id)

        return JsonResponse({'status':0})


class AddView(View):
    def post(self, request):
        ''' 添加购物车信息 '''
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status':1, 'errmsg':'请先登录'})

        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        sku = GoodsSKU.objects.get(id=sku_id)
        count = int(count)

        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        old_count = conn.hget(cart_key, sku_id)
        if old_count: # 之前有添加过该 sku_id
            count += int(old_count)
        if count > sku.stock:
            return JsonResponse({'status':2, 'errmsg':'库存不够'})

        conn.hset(cart_key, sku_id, count)
        cart_count = conn.hlen(cart_key)
        return JsonResponse({'status':0, 'cart_count':cart_count})
