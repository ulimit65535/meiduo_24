from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views


urlpatterns = [
    # 查询所有省
    # url(r'^areas/$', views.AreaListView.as_view()),
    # url(r'^areas/(?P<pk>\d+)/$', views.AreaDetailView.as_view()),
]

router = DefaultRouter()
# 这里必须给base_name，因为视图中没有定义queryset,若已定义，自动为queryset中模型名的小写
router.register(r'areas', views.AreaViewSet, base_name='area')
urlpatterns += router.urls
