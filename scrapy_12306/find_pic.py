# 学习---识别12306验证码
from PIL import Image        # python 标准图形库
from PIL import ImageFilter
import urllib
import requests
import re
import urllib3
import urllib.request

pic_url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.2797480586792238"

# 将12306中验证码图片读取出来
def get_image():
    resp = urllib.request.urlopen(pic_url)   # python3 不再支持urllib2
    raw = resp.read()
    with open("./temp.jpg", 'wb') as fp:
        fp.write(raw)
    '''
    im = Image.open("./temp.jpg")
    im.show()
    print(im.crop((5,41,72,118)).show())
    '''
    return Image.open("./temp.jpg")


# 把验证码图片中子图片提取出来
def get_sub_image(im,x,y):
    assert 0 <= x <= 3
    assert 0 <= y <= 2
    WITH = HEIGHT = 68
    left = 5 + (67 + 5) * x      # 具体可以调整
    top = 41 + (67 + 5) * y
    right = left + 67
    bottom = top + 67
    box = (left, top, right, bottom)
    return im.crop(box)          # 图片裁剪，调用image

# 将图片上传到百度图片中进行识别
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36"

def baidu_image_upload(im):
    url = "http://image.baidu.com/pictureup/uploadshitu?fr=flash&fm=index&pos=upload"

    im.save("./query_image.png")
    raw = open("./query_image.png", 'rb').read()
    files = {
        'fileheight'   : "0",
        'newfilesize'  : str(len(raw)),
        'compresstime' : "0",
        'Filename'     : "image.png",
        'filewidth'    : "0",
        'filesize'     : str(len(raw)),
        'filetype'     : 'image/png',
        'Upload'       : "Submit Query",
        'filedata'     : ("image.png", raw)
    }

    resp = requests.post(url, files=files, headers={'User-Agent': UA})
    # print(resp.url)
    #  resp.url
    redirect_url = "http://image.baidu.com" + resp.text

    return redirect_url

def baidu_stu_lookup(im):
    redirect_url = baidu_image_upload(im)

    #print redirect_url
    resp = requests.get(redirect_url)

    html = resp.text

    return baidu_stu_html_extract(html)


def baidu_stu_html_extract(html):
    pattern = re.compile(r"'multitags':\s*'(.*?)'")
    matches = pattern.findall(html)
    if not matches:
        return '[ERROR?]'

    tags_str = matches[0]

    result = list(filter(None, tags_str.replace('\t', ' ').split()))

    return '|'.join(result) if result else '[UNKOWN]'

"""
   对图像进行锐化处理
"""

def ocr_question_extract(im):
    # git@github.com:madmaze/pytesseract.git
    global pytesseract
    try:
        import pytesseract
    except:
        print("[ERROR] pytesseract not installed")
        return
    im = im.crop((127, 3, 260, 22))
    im = pre_ocr_processing(im)
    # im.show()
    return pytesseract.image_to_string(im, lang='chi_sim').strip()


def pre_ocr_processing(im):
    im = im.convert("RGB")
    width, height = im.size

    white = im.filter(ImageFilter.BLUR).filter(ImageFilter.MaxFilter(23))
    grey = im.convert('L')
    impix = im.load()
    whitepix = white.load()
    greypix = grey.load()

    for y in range(height):
        for x in range(width):
            greypix[x,y] = min(255, max(255 + impix[x,y][0] - whitepix[x,y][0],
                                        255 + impix[x,y][1] - whitepix[x,y][1],
                                        255 + impix[x,y][2] - whitepix[x,y][2]))

    new_im = grey.copy()
    binarize(new_im, 150)
    return new_im

def binarize(im, thresh=120):
    assert 0 < thresh < 255
    assert im.mode == 'L'
    w, h = im.size
    for y in range(0, h):
        for x in range(0, w):
            if im.getpixel((x,y)) < thresh:
                im.putpixel((x,y), 0)
            else:
                im.putpixel((x,y), 255)

if __name__ == '__main__':
     im = get_image()

     try:
         print
         'OCR Question:', ocr_question_extract(im)
     except Exception as e:
         print
         '<OCR failed>', e

     for y in range(2):       # range(N)代表0~N-1
         for x in range(4):
             im2 = get_sub_image(im,x,y)

             result = baidu_stu_lookup(im2)
             print(y, x, result)
