from django.db import models

# Create your models here.
class OrderInfo(models.Model):
    ''' 订单模型类 '''
    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )

    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成')
    )

    ORDER_STATUS_DIC = {
        1: '待支付',
        2: '待发货',
        3: '待收货',
        4: '待评价',
        5: '已完成',
    }

    PAY_METHOD_DIC = {
        1: '货到付款',
        2: '微信支付',
        3: '支付宝',
        4: '银联支付',
    }

    order_id = models.CharField(max_length=128, primary_key=True, verbose_name='订单号')
    user = models.ForeignKey('user.User', verbose_name='用户', on_delete=models.CASCADE)
    addr = models.ForeignKey('user.Address', verbose_name='收货地址', on_delete=models.CASCADE)
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=3, verbose_name='支付方式')
    total_count = models.IntegerField(default=1, verbose_name='商品数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')
    transit_price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name='运费')
    status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')
    trade_no = models.CharField(max_length=128, default="", verbose_name='支付编号')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_deleted = models.BooleanField(default=False, verbose_name="是否被删除")

    def __str__(self):
        return self.user.username + ' ' + str(self.create_time)

    class Meta:
        db_table = 'df_order_info'
        verbose_name = '订单'
        verbose_name_plural = verbose_name


class OrderGoods(models.Model):
    ''' 订单商品模型类 '''
    order = models.ForeignKey('OrderInfo', verbose_name='订单', on_delete=models.CASCADE)
    sku = models.ForeignKey('goods.GoodsSKU', verbose_name='商品SKU', on_delete=models.CASCADE)
    count = models.IntegerField(default=1, verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    comment = models.CharField(max_length=256, default="", verbose_name='评论')
    comment_time = models.DateTimeField(auto_now=True, verbose_name='评论时间')

    def __str__(self):
        return str(self.order) + ' ' + self.sku.name

    class Meta:
        db_table = 'df_order_goods'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name
