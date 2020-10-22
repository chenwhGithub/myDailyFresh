import random
from datetime import datetime
from django.shortcuts import render
from django.views import View
from django.db import transaction
from django.http import JsonResponse
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from goods.models import GoodsSKU
from user.models import Address
from .models import OrderInfo, OrderGoods

# Create your views here.
class PlaceView(LoginRequiredMixin, View):
    def post(self, request):
        ''' 显示订单页面 '''
        user = request.user
        sku_ids = request.POST.getlist('sku_ids') # 只传 sku_id，其它信息从数据库中读取
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
        return render(request, 'order_place.html', context)


class CreateView(View):
    @transaction.atomic
    def post(self, request):
        ''' 订单创建 '''
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status':1, 'errmsg':'用户未登录'})

        addr_id = request.POST.get("addr_id")
        pay_method = request.POST.get("pay_method")
        sku_ids = request.POST.get("sku_ids")

        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'status':2, 'errmsg':'参数不完整'})

        addr = Address.objects.get(id=addr_id)
        order_sequence = str(random.random())[2:7]
        order_id = datetime.now().strftime("%Y%m%d%H%M%S") + order_sequence
        transit_price = 10
        total_count = 0
        total_price = 0
        save_id = transaction.savepoint()

        try:
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             transit_price=transit_price)
            sku_ids = sku_ids.split(',')
            conn = get_redis_connection('default')
            cart_key = 'cart_%d'%user.id
            for sku_id in sku_ids:
                count = int(conn.hget(cart_key, sku_id)) # 从 redis 中获取商品数目

                for i in range(3): # 乐观锁，尝试三次
                    sku = GoodsSKU.objects.get(id=sku_id)
                    orgin_stock = sku.stock # 每次重新获取商品当前最新库存
                    if count > orgin_stock:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'status':3, 'errmsg': '库存不足'})

                    new_stock = orgin_stock - count
                    new_sales = sku.sales + count
                    affected_rows = GoodsSKU.objects.filter(id=sku.id, stock=orgin_stock).update(stock=new_stock, sales=new_sales)
                    if affected_rows == 0:
                        if i == 2:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'status':4, 'errmsg': '下单失败'})
                        continue

                    # 向订单商品表中添加信息
                    orderGoods = OrderGoods.objects.create(order=order,
                                              sku=sku,
                                              count=count,
                                              price=sku.price)
                    orderGoods.save()

                    total_count += count
                    total_price += sku.price * count
                    break

            # 更新订单信息表中的商品总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'status':5, 'errmsg': '下单失败'})

        transaction.savepoint_commit(save_id)
        conn.hdel(cart_key, *sku_ids) # 清除用户购物车中商品的记录
        return JsonResponse({'status':0})
