from django.db import models


# Create your models here.
class Area(models.Model):
    """省区划，这里不继承BaseModel,因为数据不需要更改"""
    name = models.CharField(max_length=20, verbose_name='名称')
    # 自关联表，外键指向本身。related_name将查询被关联查询集的管理器的名称由area_set修改为subs
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name
