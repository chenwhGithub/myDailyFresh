import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.shortcuts import render, redirect
from django.views.generic import View
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from celery_tasks.tasks import send_register_active_email
from .models import User, Address

# Create your views here.
class RegisterView(View):
    def get(self, request):
        ''' 首页点击注册按钮，跳转到 register.html 页面 '''
        return render(request, 'register.html')

    def post(self, request):
        ''' register.html 页面点击注册按钮，处理表单数据 '''
        uname = request.POST.get('user_name')
        pwd = request.POST.get('pwd')
        pwd2 = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        if not all([uname, pwd, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式错误'})

        if pwd != pwd2:
            return render(request, 'register.html', {'errmsg': '两次密码不一致'})

        user = None
        try:
            user = User.objects.get(username=uname)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        user = User.objects.create_user(uname, email, pwd) # 内存中创建一条数据表项
        user.is_active = 0 # 用户尚未激活，通过邮件链接激活
        user.save() # 增加数据表项到数据库

        serializer = Serializer(settings.SECRET_KEY, 3600) # 对 user.id 加密后生成激活链接，有效期 3600s
        info = {'userid': user.id}
        token = serializer.dumps(info)
        send_register_active_email.delay(email, uname, token.decode())

        return redirect(reverse('goods:index'))


class ActiveView(View):
    def get(self, request, token):
        ''' 点击邮件里的激活链接 '''
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['userid']
            user = User.objects.get(id=user_id)
            user.is_active = 1 # 用户已激活
            user.save() # 更新数据库表项信息
            return redirect(reverse('user:login')) # 跳转到登录页面
        except SignatureExpired:
            return HttpResponse('激活链接已过期')


class LoginView(View):
    def get(self, request):
        ''' 首页点击登录按钮/邮件点击激活链接，跳转到 login.html 页面 '''
        username = ''
        checked = ''
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        ''' login.html 页面点击登录按钮，处理表单数据 '''
        uname = request.POST.get('username')
        pwd = request.POST.get('pwd')
        rmb = request.POST.get('remember')

        if not all([uname, pwd]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 若用户名和密码正确，但未激活，authenticate() 默认返回 None
        # 通过 settings.py 设置可以取消 authenticate() 激活验证
        # AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']
        user = authenticate(username=uname, password=pwd)
        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next', reverse('goods:index'))
                response = redirect(next_url)
                if rmb == 'on':
                    response.set_cookie('username', uname, max_age=7*24*3600) # 记住用户名
                else:
                    response.delete_cookie('username')
                return response # 跳转到主页，自动传递 request.user 变量到网页模板文件
            else:
                return render(request, 'login.html', {'errmsg': '账户尚未激活'})
        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


class LogoutView(View):
    def get(self, request):
        ''' 点击退出登录按钮，然后跳转到主页 '''
        logout(request)
        return redirect(reverse('goods:index'))


class InfoView(LoginRequiredMixin, View):
    def get(self, request):
        ''' 点击用户中心按钮，跳转到 user_center_info.html 页面 '''
        user = request.user
        addr_default = None
        try:
            addr_default = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            addr_default = None

        con = get_redis_connection('default') # 连接远端 redis 数据库
        history_key = 'history_%d'% user.id
        sku_ids = con.lrange(history_key, 0, 4) # 获取最近的5个浏览商品信息
        skus = []
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            skus.append(sku)

        context = {
            'page_type': 'info',
            'addr_default': addr_default,
            'skus': skus,
        }
        return render(request, 'user_center_info.html', context)


class OrderView(LoginRequiredMixin, View):
    def get(self, request, page_num):
        ''' 点击用户中心-全部订单按钮，跳转到 user_center_order.html 页面 '''
        user = request.user
        orders = OrderInfo.objects.filter(user=user, is_deleted=0).order_by('-create_time') # - 表示降序排列
        for order in orders:
            goods_list = OrderGoods.objects.filter(order=order)
            order.goods_list = goods_list
            order.status_name = OrderInfo.ORDER_STATUS_DIC[order.status]
            order.pay_method_name = OrderInfo.PAY_METHOD_DIC[order.pay_method]
            order.total_pay = order.total_price + order.transit_price
            for goods in goods_list:
                amount = goods.count * goods.price
                goods.amount = amount

        paginator = Paginator(orders, 2)
        total_page = paginator.num_pages
        page_num = int(page_num)
        if page_num > total_page:
            page_num = 1
        page = paginator.page(page_num)

        # 获取显示的页码范围，这里设置只显示三个页码
        page_list = []
        if total_page <= 3: # 若总页数小于3，则将页码全部显示
            page_list = range(1, total_page+1)
        elif page_num == 1: # 若当前页码为第一页，则显示页码 1,2,3
            page_list = range(1, 4)
        elif page_num == total_page: # 若当前页码为最后一页，则显示最后三个页码
            page_list = range(total_page-2, total_page+1)
        else: # 其他情况则显示前一页，当前页，后一页页码
            page_list = range(page_num-1, page_num+2)

        context = {
            'page': page,
            'page_list': page_list,
            'page_type': 'order',
        }
        return render(request, 'user_center_order.html', context)


class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        ''' 点击用户中心-收货地址按钮，跳转到 user_center_address.html 页面 '''
        user = request.user
        addr_default = None
        try:
            addr_default = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            addr_default = None

        context = {
            'page_type': 'address',
            'addr_default': addr_default,
        }

        return render(request, 'user_center_address.html', context)

    def post(self, request):
        ''' 用户中心-收货地址页面点击提交按钮，处理表单数据 '''
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        if not all([receiver, addr, phone]):
            return render(request, 'user_center_address.html', {'errmsg': '数据不完整'})

        user = request.user
        addr_default = None
        try:
            addr_default = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            addr_default = None

        is_default = True
        if addr_default:
            is_default = False

        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default = is_default
                               )

        return redirect(reverse('user:address'))
