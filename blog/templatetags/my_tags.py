from django import template
from blog import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = template.Library()

@register.simple_tag
def tags(x,y):

    return x*y

@register.inclusion_tag("classification.html")
def get_classification(username):

    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    # 查询每一个分类名称以及对应的文章数
    # ret = models.Category.objects.values('pk').annotate(c=Count('article__title')).values('title','c')
    # 查询当前站点的每一个分类名称以及对应的文章数
    cate_list = models.Category.objects.filter(blog=blog).values('pk').annotate(c =
                                        Count('article__title')).values('title','c')
     # 查询当前站点的每一个标签名称以及对应的文章数
    tag_list = models.Tag.objects.filter(blog=blog).values('pk').annotate(c =
                                        Count('article')).values('title','c')
     # 查询当前站点的每一个年月名称以及对应的文章数
    # time_p = models.Article.objects.filter(user=user).extra(select={"y-m":"date_format(create_time,'%%Y-%%m')"
    #                                               }).values('title','y-m')

    # date_list = models.Article.objects.filter(user=user).extra(select={"y-m":"date_format(create_time,'%%Y-%%m')"
    #                                               }).values('y-m').annotate(c=Count('nid')).values('y-m','c')
    date_list = models.Article.objects.filter(user=user).annotate(month=TruncMonth('create_time')).values('month'
                                                ).annotate(c=Count('nid')).values('month','c')

    return {'blog':blog,'cate_list':cate_list,'date_list':date_list,'tag_list':tag_list,'user':user}