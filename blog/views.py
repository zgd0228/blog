from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from django.contrib import auth
from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.db.models import Count,F
from django.db import transaction
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
import random
import json
import os
import threading
from blogs import settings
from blog.models import UserInfo
from blog import models


# Create your views here.


def login(request):
    '''
    用户登录页面
    :param request:
    :return:
    '''
    response = {'user':None,'msg':None}
    if request.is_ajax():
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        valid_code = request.POST.get('valid_code')
        if valid_code.upper() == request.session.get('valid_code').upper():
            user = auth.authenticate(username = user,password = pwd)
            if user:
                response['user'] = user.username
                auth.login(request,user)
            else:
                response['msg'] = '用户名或密码错误'
        else:
            response['msg'] = '验证码错误'
        return JsonResponse(response)
    return render(request,'login.html')

class Forms(forms.Form):
    '''

    '''
    user = forms.CharField(min_length=4,label='用户名',error_messages={'required':'输入不能为空','invalid':'格式错误'},widget=widgets.TextInput(
            attrs={'class':'form-control'}))
    email = forms.CharField(label='邮箱',error_messages={'required':'输入不能为空','invalid':'格式错误'},widget=widgets.EmailInput(
        attrs={'class':'form-control'}
    ))
    pwd = forms.CharField(min_length=8,label='密码',error_messages={'required':'输入不能为空','invalid':'格式错误'},widget=widgets.PasswordInput(
        attrs={'class':'form-control'}
    ))
    pwd2 = forms.CharField(min_length=8,label='确认密码',error_messages={'required':'输入不能为空','invalid':'格式错误'},widget=widgets.PasswordInput(
        attrs={'class':'form-control'}
    ))

    def clean_user(self):
        user1 = self.cleaned_data.get('user')

        user = UserInfo.objects.filter(username=user1).first()
        if not user:
            return user1
        else:
            raise ValidationError('用户名已存在')

    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        pwd2 = self.cleaned_data.get('pwd2')
        if pwd and pwd2:
            if pwd == pwd2:
                return self.cleaned_data
            else:
                raise ValidationError('两次输入的密码不一致，请重新输入')
        else:
            return self.cleaned_data

def reg(request):
    '''
    用户注册页面
    :param request:
    :return:
    '''
    form_reg = Forms()
    response = {'user':None,'msg':None}
    form = Forms(request.POST)
    if request.is_ajax():
        if form.is_valid():
            response['user'] = form.cleaned_data.get('user')
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            avatar = request.FILES.get('avatar')
            extra = {}
            if avatar:
                extra['avatar'] = avatar
            UserInfo.objects.create_user(username=user,password=pwd,email=email,**extra)
        else:
            response['msg'] = form.errors
        return JsonResponse(response)
    return render(request,'reg.html',{'form':form_reg})

def index(request):
    '''
    博客首页
    :param request:
    :return:
    '''

    article_all = models.Article.objects.all()
    return render(request,'index.html',{'article_all':article_all})

@login_required()
def logout(request):
    '''
    用户退出登录页面
    :return:
    '''
    auth.logout(request)

    return redirect('/login/')


def home_site(request,username,**kwargs):
    """

    :param request:
    :param username:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()

    if not user:
        return render(request,'not_found.html')
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'tag':
            article_list = models.Article.objects.filter(user=user).filter(tags__title=param)
        elif condition == 'category':
            article_list = models.Article.objects.filter(user=user).filter(category__title=param)
        else:
            year,month = param.split('-')
            article_list = models.Article.objects.filter(user=user).filter(create_time__year=year,create_time__month=month)

    else:
        # articles = user.article_set.all()
        article_list = models.Article.objects.filter(user=user)
    return render(request,'home_site.html',locals())

@login_required()
def get_classification_data(username):
    '''

    :param username:
    :return:
    '''
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog

    cate_list = models.Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list(
        "title", "c")

    tag_list = models.Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")

    date_list = models.Article.objects.filter(user=user).extra(
        select={"y_m_date": "date_format(create_time,'%%Y/%%m')"}).values("y_m_date").annotate(
        c=Count("nid")).values_list("y_m_date", "c")

    return {"blog": blog, "cate_list": cate_list, "date_list": date_list, "tag_list": tag_list}


def article_detail(request,username,article_id):
    '''
    文章详情页显示
    :param request:
    :param username:
    :param article_id:
    :return:
    '''
    user = UserInfo.objects.filter(username=username).first()
    article_obj = models.Article.objects.filter(pk=article_id).first()
    comment_obj = models.Comment.objects.filter(article_id=article_id)

    return render(request,'article_detail.html',locals())

@login_required()
def digg(request):
    '''
    文章点赞功能的实现
    :param request:
    :return:
    '''

    if request.method == "POST":

        articles_id = request.POST.get('article_id')
        is_up = json.loads(request.POST.get('is_up'))
        user_id = request.user.pk
        response = {'state':True}
        obj = models.ArticleUpDown.objects.filter(article_id=articles_id,user_id=user_id).first()
        if not obj:
            models.ArticleUpDown.objects.create(user_id = user_id,article_id = articles_id,is_up =is_up)
            ret = models.Article.objects.filter(pk = articles_id)
            if is_up:
                ret.update(up_count = F('up_count')+1)
            else:
                ret.update(down_count = F('down_count')+1)
        else:
            response['state'] = False
            response['handle'] = obj.is_up


        return JsonResponse(response)

@login_required()
def comment(request):
    '''
    对文章进行评论
    :param request:
    :return:
    '''
    article_id = request.POST.get('article_id')
    comments = request.POST.get('comment')
    parent_id = request.POST.get('parent_comment')
    response = {}

    article_obj = models.Article.objects.filter(pk=article_id).first()

    with transaction.atomic():
        # 事务操作：同进同退，只要有一个报错，另外一个的操作也将不会执行
        content = models.Comment.objects.create(content=comments,user_id=request.user.pk,parent_comment_id=parent_id,article_id=article_id)
        models.Article.objects.filter(pk=article_id).update(comment_count = F('comment_count')+1)
    response['user']=request.user.username
    response['create_time'] = content.create_time.strftime('%Y-%m-%d %X')
    response['content'] = comments
    if parent_id:
        response['parent_comment'] = content.parent_comment.content
        response['parent_name'] = content.parent_comment.user.username

    # 发送邮件
    t = threading.Thread(target=send_mail,args=('您的%s文章新增加一条评论'%article_obj.title,
        comments,
        settings.EMAIL_HOST_USER,
        ["3271302686@qq.com"]))
    t.start()

    return JsonResponse(response)

@login_required()
def content_tree(request):
    '''
    评论树的实现
    :param request:
    :return:
    '''
    article_id = request.GET.get('article_id')

    ret = list(models.Comment.objects.filter(article_id=article_id).values('pk','content','parent_comment_id'))

    return JsonResponse(ret,safe=False)

@login_required()
def manage(request):
    '''
    跳转管理页面
    :param request:
    :return:
    '''
    article_obj = models.Article.objects.all()

    return render(request,'manage.html',locals())

@login_required()
def add_article(request):
    '''
    添加文章
    :param request:
    :return:
    '''
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = 1

        soup = BeautifulSoup(content,'html.parser')
        # 过滤：防止xs攻击
        for tag in soup.find_all():
            if tag.name == 'script':
                tag.decompose()

        # 摘要截断
        desc = soup.text[0:150]

        user_id = request.user.pk
        models.Article.objects.create(title=title,content=str(soup),desc = desc,category_id = category_id,user_id=user_id)
        return redirect('/manage/')

    return render(request,'backend/add_article.html')

def upload(request):
    '''
    上传文件的处理，将上传的文件显示到编辑器上
    :param request:
    :return:
    '''
    img = request.FILES.get('upload_img')
    path = os.path.join(settings.MEDIA_ROOT,'article_img',img.name)
    with open(path,'wb') as f:
        for line in img:
            f.write(line)

    response = {
        'error':0,
        'url':'media/article_img/%s'%img.name
    }

    return HttpResponse(json.dumps(response))

@login_required()
def remove(request,id):
    '''
    删除文章
    :param request:
    :param id:
    :return:
    '''
    article_obj = models.Article.objects.filter(pk=id)
    article_obj.delete()

    return redirect('/manage/')

@login_required()
def change(request,id):
    '''
    编辑文章或者修改文章
    :param request:
    :param id:
    :return:
    '''
    article_obj = models.Article.objects.filter(pk=id).first()
    print(article_obj.user)

    return render(request,'backend/change.html',{'article_obj':article_obj})



