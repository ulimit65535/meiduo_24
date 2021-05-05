from rest_framework import serializers
from . models import Area


class AreaSerializer(serializers.ModelSerializer):
    """列表视图的序列化器"""

    class Meta:
        model = Area
        fields = ['id', 'name']


class SubsSerializer(serializers.ModelSerializer):
    """详情视图使用的序列化器"""
    # subs = serializers.PrimaryKeyRelatedField()  # 只会序列化出id
    # subs = serializers.StringRelatedField()  # 只会序列化出name
    # 这里因为模型中修改了area_set,序列化器中的变量要与模型中的字段对应
    subs = AreaSerializer(many=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']

