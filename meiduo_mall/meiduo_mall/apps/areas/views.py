from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Area
from .serializers import AreaSerializer, SubsSerializer
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework  .viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin


# # Create your views here.
# class AreaListView(APIView):
#     """查询所有省"""
#
#     def get(self, request):
#         # 1.获取指定查询集
#         qs = Area.objects.filter(parent=None)
#         # 2. 创建序列化器进行序列化
#         serializer = AreaSerializer(qs, many=True)
#         # 3.响应
#         return Response(serializer.data)
#
#
# class AreaDetailView(APIView):
#     """查询单一省或市"""
#
#     def get(self,request, pk):
#         # 1. 根据pk查询指定的省或市
#         try:
#             area = Area.objects.get(id=pk)
#         except Area.DoesNotExist:
#             return Response({'message': '无效pk'}, status=status.HTTP_400_BAD_REQUEST)
#         # 2. 创建序列化器进行序列化
#         serializer = SubsSerializer(area)
#         # 3. 响应
#         return Response(serializer.data)


# class AreaListView(ListAPIView):
#     serializer_class = AreaSerializer
#     queryset = Area.objects.filter(parent=None)
#
#
# class AreaDetailView(RetrieveAPIView):
#     serializer_class = SubsSerializer
#     queryset = Area.objects.all()


class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """
    注意继承顺序，CacheResponseMixin做了一层封装，实际使用了装饰器cache_response，
    然后调用父类ReadOnlyModelViewSet的list和retrieve方法
    """
    # 指定查询集
    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    # 指定序列化器
    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubsSerializer
