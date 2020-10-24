import random
import time
from datetime import datetime
from django.shortcuts import render
from django.views import View
from django.db import transaction
from django.http import JsonResponse
from django.conf import settings
from django_redis import get_redis_connection
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
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


def alipay_init():
    ''' 初始化支付宝客户端 '''
    alipay_client_config = AlipayClientConfig(sandbox_debug=True) # 沙盒测试环境
    alipay_client_config.app_id = settings.ALIPAY_APP_ID
    alipay_client_config.app_private_key = settings.APP_PRIVATE_KEY
    alipay_client_config.alipay_public_key = settings.ALIPAY_PUBLIC_KEY
    client = DefaultAlipayClient(alipay_client_config)
    return client


def alipay_pay(order):
    ''' 发送支付宝支付请求 '''
    client = alipay_init()
    model = AlipayTradePagePayModel()
    model.out_trade_no = order.order_id # 商户系统的订单编号，需保证在商户系统不重复
    model.total_amount = str(order.total_price + order.transit_price)
    model.subject = '天天生鲜订单支付'
    model.product_code = 'FAST_INSTANT_TRADE_PAY'
    model.timeout_express = settings.ALIPAY_EXPRESS # 订单过期关闭时长
    # 创建请求对象
    request = AlipayTradePagePayRequest(biz_model=model)
    # 设置回调通知地址（GET）
    request.return_url = None
    # 设置回调通知地址（POST）
    request.notify_url = None
    # 执行API调用,获取支付链接
    pay_url = client.page_execute(request, http_method='GET')
    return pay_url


def alipay_query(order):
    ''' 查询支付宝支付结果 '''
    client = alipay_init()
    model = AlipayTradeQueryModel()
    model.out_trade_no = order.order_id
    request = AlipayTradeQueryRequest(biz_model=model)

    context = {}
    while True:
        response = client.execute(request)
        response = eval(response) # str转换为字典
        code = response.get('code')
        sub_code = response.get('sub_code')
        sub_msg = response.get('sub_msg')
        trade_status = response.get('trade_status')
        if sub_code == 'ACQ.TRADE_NOT_EXIST' or (code == '10000' and trade_status == 'WAIT_BUYER_PAY'):
            # 交易不存在，或状态为等待买家付款则继续等待用户付款
            time.sleep(5)
        elif code == '10000' and trade_status == 'TRADE_SUCCESS': # 支付成功
            context['status'] = 0
            context['trade_no'] = response.get('trade_no') # 支付宝交易号
            break
        else:
            context['errmsg'] = '支付失败:%s-%s'%(sub_code, sub_msg)
            break
    return context


class PayView(View):
    ''' 支付宝订单支付 '''
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status':1, 'errmsg': '用户未登录'})

        order_id = int(request.POST.get('order_id'))
        order = OrderInfo.objects.get(order_id=order_id,
                                      user=user,
                                      pay_method=3,
                                      order_status=1)
        pay_url = alipay_pay(order)
        return JsonResponse({'status':0, 'pay_url':pay_url})


class QueryView(View):
    ''' 支付宝支付结果查询 '''
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status':1, 'errmsg': '用户未登录'})

        order_id = int(request.POST.get('order_id'))
        order = OrderInfo.objects.get(order_id=order_id)
        context = alipay_query(order)
        if context['status'] == 0:
            order.trade_no = context['trade_no']
            order.order_status = 4 # 待评价
            order.save()
        print('context: %s'%(str(context)))
        return JsonResponse(context)
