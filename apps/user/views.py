import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.shortcuts import render, redirect
from django.views.generic import View
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponse
from .models import User

# Create your views here.
class RegisterView(View):

    def get(self, request):
        ''' 首页点击注册按钮，跳转到 register.html 页面 '''
        return render(request, 'register.html')

    def post(self,request):
        ''' register.html 页面点击注册按钮，处理表单数据 '''
        uname = request.POST.get('user_name')
        pwd = request.POST.get("pwd")
        pwd2 = request.POST.get("cpwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        if allow != 'on':
            return render(request, "register.html", {'errmsg': "请同意协议"})

        if not all([uname, pwd, email]):
            return render(request, "register.html", {'errmsg': "数据不完整"})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, "register.html", {'errmsg': "邮箱格式错误"})

        if pwd != pwd2:
            return render(request, 'register.html', {'errmsg': '两次密码不一致'})

        user = None
        try:
            user = User.objects.get(username=uname)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, "register.html", {'errmsg': "用户名已存在"})

        user = User.objects.create_user(uname, email, pwd)
        user.is_active = 0 # 用户尚未激活，通过邮件链接激活
        user.save() # 数据库中增加表项

        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {"confirm": user.id}
        token = serializer.dumps(info)
        token = token.decode()
        subject = '天天生鲜欢迎你'
        message = ''
        sender = settings.EMAIL_FROM
        receiver = [email]
        html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><br>　<a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(uname, token, token)
        send_mail(subject, message=message, from_email=sender, recipient_list=receiver, html_message=html_message)

        return redirect(reverse('goods:index'))


class ActiveView(View):

    def get(self, request, token):
        ''' 点击邮件里的激活链接 '''
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1 # 用户已激活
            user.save() # 更新数据库表项信息
            return redirect(reverse('user:login')) # 跳转到登录页面
        except SignatureExpired:
            return HttpResponse("激活链接已过期") # 激活链接过期


class LoginView(View):

    def get(self, request):
        ''' 首页点击登录按钮/邮件点击激活链接，跳转到 login.html 页面 '''
        return render(request, 'login.html')
