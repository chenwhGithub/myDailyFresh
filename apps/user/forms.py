from django import forms


# 登录表单验证
class LoginForm(forms.Form):
    # 定义输入字段的校验规则，每条规则有对应的默认报错信息
    # 属性名与 HTML input 的 name 一致，映射到 POST 消息中
    username = forms.CharField(required=True)
    pwd = forms.CharField(required=True, min_length=6)
