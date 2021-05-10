import xadmin
from xadmin import views
from .models import User, Address
# Register your models here.

class AddressAdmin(object):
    list_display = ['user', 'receiver', 'addr', 'zip_code', 'phone', 'is_default'] # 后台显示的列
    search_fields = ['user', 'receiver', 'addr', 'zip_code', 'phone'] # 可搜索的字段
    list_filter = ['user', 'receiver', 'addr', 'zip_code', 'phone', 'is_default'] # 可过滤的字段
    ordering = ['-user'] # 设置排序排序
    readonly_fields = ['receiver', 'zip_code'] # 设置只读字段
    list_editable = ['addr', 'zip_code', 'phone'] # 设置可编辑字段
    refresh_times = [3, 5] # 设置页面自动刷新，单位 秒
    model_icon = 'fa fa-address-card' # 设置数据表图标，http://www.fontawesome.com.cn/faicons/


class BaseSettings(object):
    enable_themes = True # 后台开启主题功能，右上角出现主题菜单
    use_bootswatch = True


class GlobalSettings(object):
    site_title = 'myDailyFresh 后台管理界面'  # 设置后台左上角 title
    site_footer = 'wenhui.chen 公司' # 设置后台底部 footer
    menu_style = 'accordion' # 设置后台左侧菜单可折叠


xadmin.site.register(Address, AddressAdmin)
xadmin.site.register(views.BaseAdminView, BaseSettings)
xadmin.site.register(views.CommAdminView, GlobalSettings)
