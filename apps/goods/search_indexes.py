from haystack import indexes
from .models import GoodsSKU

# 类名必须为 Model+Index，指定对某个类的某些字段建立索引
class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    # 必须有且只能有一个字段为 document=True
    # use_template=True 允许使用数据模板文件去建立索引，数据模板路径：templates/search/indexes/app/model_text.txt
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return GoodsSKU

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
