"""blogs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from blog import views,valid
from blogs import settings
from django.views.static import serve
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',views.login),
    path('get_valid/',valid.get_valid),
    path('index/',views.index),
    re_path('^$',views.index),
    path('reg/',views.reg),
    path('digg/',views.digg),
    path('comment/',views.comment),
    path('content_tree/',views.content_tree),
    path('manage/',views.manage),
    path('manage/add/',views.add_article),
    path('upload/',views.upload),
    path('logout/',views.logout),

    # 管理页面编辑删除配置
    re_path(r'manage/(\d+)/change/$',views.change),
    re_path(r'manage/(\d+)/delete/$',views.remove),

    # media配置
    re_path(r'media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),

    # 文章详情页配置
    re_path(r'(?P<username>\w+)/articles/(?P<article_id>\d+)/$',views.article_detail),

    # 个人站点跳转
    # re_path(r'(?P<username>\w+)/(?P<condition>tag|archive|category)/(?P<param>.*)/$',views.home_site),
    re_path('^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$',views.home_site),

    # 个人站点配置
    re_path(r'(?P<username>\w+)/$',views.home_site),








]
