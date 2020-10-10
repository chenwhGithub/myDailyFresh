from django.shortcuts import render
from django.views.generic import View

# Create your views here.
class RegisterView(View):

    def get(self, request):
        ''' 首页点击注册按钮，跳转到 register.html 页面 '''
        return render(request, 'register.html')


class LoginView(View):

    def get(self, request):
        ''' 首页点击登录按钮，跳转到 login.html 页面 '''
        return render(request, 'login.html')
