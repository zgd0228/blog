from io import BytesIO
from PIL import ImageDraw,Image,ImageFont
import random
from django.shortcuts import render,HttpResponse,redirect

def get_color():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))

def get_valid(request):
    valid_str = ''
    img = Image.new('RGB',(165,34),color=get_color())

    # 磁盘存储验证码
    '''
        info = open('validcode.png','wb')
        img.save(info,'png')
        info2 = open('validcode.png','rb')
        data=info2.read()
    '''
    # 内存存储读取验证码
    draw = ImageDraw.Draw(img)
    zq_font = ImageFont.truetype('static/font/zq.ttf',size=30)
    for i in range(5):
        random_num = str(random.randint(0,9))
        random_low = chr(random.randint(95,122))
        random_upper = chr(random.randint(65,90))
        random_char = random.choice([random_low,random_num,random_upper])
        draw.text((i*30+20,2),random_char,get_color(),font=zq_font)
        valid_str += random_char
    print(valid_str)
    # 划线
    '''
     for i in range(5):
        x1 = random.randint(0,160)
        x2 = random.randint(0,160)
        y1 = random.randint(0,34)
        y2 = random.randint(0,34)
        draw.line((x1,y1,x2,y2),get_color())
    '''
   # 画点
    '''
    for i in range(10):
        draw.point([random.randint(0,160),random.randint(0,34)],get_color())
    '''
    request.session['valid_code'] = valid_str
    info = BytesIO()
    img.save(info,'png')
    data = info.getvalue()

    return HttpResponse(data)