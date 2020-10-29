from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ''' 用户数据表 '''
    class Meta:
        db_table = 'df_user'  # db.sqlite3 中数据表名称
        verbose_name = '用户' # admin 后台显示数据表名称
        verbose_name_plural = verbose_name


class Address(models.Model):
    ''' 地址数据表 '''
    user = models.ForeignKey('User', verbose_name='所属用户', on_delete=models.CASCADE) # verbose_name: admin 后台显示数据表字段名称
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.receiver + ' ' + self.addr # admin 后台显示数据表项名称
