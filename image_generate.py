import cv2
from fastapi import Body
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import math

def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)

def draw_rounded_rect(image, top_left, bottom_right, corner_radius, color, thickness, fill_color=None, side_color=None):
    """
    绘制圆角矩形
    :param image: 背景图像 (4 通道，RGBA)
    :param top_left: 矩形左上角坐标 (x1, y1)
    :param bottom_right: 矩形右下角坐标 (x2, y2)
    :param corner_radius: 圆角半径
    :param color: 边框颜色 (BGR 格式)
    :param thickness: 边框粗细
    :param fill_color: 内部填充颜色 (BGR 格式)，如果为 None 则不填充
    :param side_color: 非填充区域的颜色 (BGR 格式)，如果为 None 则不设置
    """
    x1, y1 = top_left
    x2, y2 = bottom_right

    # 如果指定了填充颜色，则填充矩形内部
    if fill_color is not None:
        # 创建一个掩码图像
        mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
        # 绘制填充的圆角矩形
        cv2.rectangle(mask, (x1 + corner_radius, y1), (x2 - corner_radius, y2), 255, -1)
        cv2.rectangle(mask, (x1, y1 + corner_radius), (x2, y2 - corner_radius), 255, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, 255, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, 255, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, 255, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, 255, -1)
        # 将填充颜色扩展到 4 通道（RGBA），并设置透明度为 255
        fill_color_rgba = (*fill_color, 255)
        # 将填充颜色应用到图像上
        image[mask == 255] = fill_color_rgba

    # 绘制四个圆角
    cv2.ellipse(image, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, color, thickness)
    cv2.ellipse(image, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, color, thickness)
    cv2.ellipse(image, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, color, thickness)
    cv2.ellipse(image, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, color, thickness)

    # 绘制矩形边
    cv2.line(image, (x1 + corner_radius, y1), (x2 - corner_radius, y1), color, thickness)  # 上边
    cv2.line(image, (x1 + corner_radius, y2), (x2 - corner_radius, y2), color, thickness)  # 下边
    cv2.line(image, (x1, y1 + corner_radius), (x1, y2 - corner_radius), color, thickness)  # 左边
    cv2.line(image, (x2, y1 + corner_radius), (x2, y2 - corner_radius), color, thickness)  # 右边

    # 如果指定了 side_color，则设置非填充区域的颜色
    if side_color is not None:
        # 创建一个掩码图像
        mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
        # 绘制圆角矩形区域
        cv2.rectangle(mask, (x1 + corner_radius, y1), (x2 - corner_radius, y2), 255, -1)
        cv2.rectangle(mask, (x1, y1 + corner_radius), (x2, y2 - corner_radius), 255, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, 255, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, 255, -1)
        cv2.ellipse(mask, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, 255, -1)
        cv2.ellipse(mask, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, 255, -1)
        # 将非填充区域设置为 side_color
        b, g, r = side_color
        image[mask == 0] = [b, g, r, 0]  # 将 RGB 和 Alpha 通道都设置为 0

def create_rounded_rectangle(width, height, corner_radius, color, thickness, fill_color=None, side_color=None):
    """
    创建一个带有圆角矩形的图像
    :param width: 图像宽度
    :param height: 图像高度
    :param corner_radius: 圆角半径
    :param color: 边框颜色 (BGR 格式)
    :param thickness: 边框粗细
    :param fill_color: 内部填充颜色 (BGR 格式)，如果为 None 则不填充
    :param side_color: 非填充区域的颜色 (BGR 格式)，如果为 None 则不设置
    :return: 生成的图像数组 (4 通道，RGBA)
    """
    # 创建一个空白图像 (4 通道，RGBA)
    image = np.zeros((height, width, 4), dtype=np.uint8)

    # 绘制圆角矩形
    top_left = (0, 0)  # 左上角坐标
    bottom_right = (width - 1, height - 1)  # 右下角坐标
    draw_rounded_rect(image, top_left, bottom_right, corner_radius, color, thickness, fill_color, side_color)

    return image


def overlay_image(background, overlay, center, fill_color=None):
    """
    将覆盖图像覆盖到原图像上，覆盖图像的中心位于指定坐标。如果覆盖图像的某些区域没有填充（即完全透明），则使用自定义颜色或背景图像的颜色。

    参数:
        background (numpy.ndarray): 原图像（4 通道，RGBA）。
        overlay (numpy.ndarray): 覆盖图像（4 通道，RGBA）。
        center (tuple): 覆盖图像的中心坐标 (x, y)。
        fill_color (tuple): 自定义填充颜色 (R, G, B, A)，默认为 None（使用背景图像的颜色）。

    返回:
        numpy.ndarray: 覆盖后的图像（4 通道，RGBA）。
    """
    # 获取覆盖图像的尺寸
    overlay_height, overlay_width = overlay.shape[:2]

    # 计算覆盖图像的左上角坐标
    x = int(center[0] - overlay_width / 2)
    y = int(center[1] - overlay_height / 2)

    # 创建一个背景图像的副本，避免修改原图像
    result = background.copy()

    # 确保覆盖图像的坐标在背景图像范围内
    if x >= 0 and y >= 0 and x + overlay_width <= background.shape[1] and y + overlay_height <= background.shape[0]:
        # 提取覆盖图像的透明通道
        alpha = overlay[:, :, 3] / 255.0  # 透明度 (0 到 1)
        alpha = alpha[:, :, np.newaxis]  # 扩展维度以匹配 RGB 通道

        # 创建一个掩码，标识哪些像素是完全透明的
        transparent_mask = (overlay[:, :, 3] == 0)

        # 将覆盖图像叠加到背景图像上
        result[y:y+overlay_height, x:x+overlay_width, :3] = (
            overlay[:, :, :3] * alpha +
            background[y:y+overlay_height, x:x+overlay_width, :3] * (1 - alpha)
        )

        # 对于完全透明的像素，使用自定义颜色或背景图像的颜色
        if fill_color is not None:
            # 如果提供了自定义颜色，则使用该颜色填充
            result[y:y+overlay_height, x:x+overlay_width, :3][transparent_mask] = fill_color[:3]
            result[y:y+overlay_height, x:x+overlay_width, 3][transparent_mask] = fill_color[3] if len(fill_color) > 3 else 255
        else:
            # 如果未提供自定义颜色，则使用背景图像的颜色
            result[y:y+overlay_height, x:x+overlay_width, :3][transparent_mask] = (
                background[y:y+overlay_height, x:x+overlay_width, :3][transparent_mask]
            )

        # 更新叠加后的透明通道
        result[y:y+overlay_height, x:x+overlay_width, 3] = np.maximum(
            background[y:y+overlay_height, x:x+overlay_width, 3],
            overlay[:, :, 3]
        )
    else:
        raise ValueError("覆盖图像超出背景图像范围")

    return result

def generate_background(color):
    """生成背景"""
    # 创建纯色背景
    background = np.zeros((1885, 578, 4), dtype=np.uint8)
    background[:, :, :3] = color  # 设置背景颜色
    background[:, :, 3] = 255  # 设置背景为不透明

    # 创建圆角矩形图像（4 通道，RGBA）
    coner = create_rounded_rectangle(552, 1852, 25, (255, 255, 255,255), 10, (255, 255, 255),color)
    coner[:, :, 3] = 233  # 设置透明度为 233

    # 调整覆盖图像的中心坐标，确保不超出背景图像范围
    center_x = 578 // 2  # 背景图像宽度的中心
    center_y = 1885 // 2  # 背景图像高度的中心

    # 将圆角矩形叠加到背景图像上
    background = overlay_image(background, coner, (center_x, center_y),color)
    return background

def generate_template_background(width,height,color):
    """生成背景"""
    # 创建纯色背景
    b,r,g = color
    image =  create_rounded_rectangle(width,height,15,(b,r,g,255),5)

    return image

def add_text_to_image_with_font(image, text, position, font_path, font_size, color):
    """
    使用外部字体文件将文字添加到图片上，并返回 RGBA 图像。
    支持换行符 `\n`。

    :param image: 背景图像 (可以是 NumPy 数组或 PIL 图像)
    :param text: 要添加的文字
    :param position: 文字的位置 (x, y)
    :param font_path: 字体文件路径 (例如 ".ttf" 或 ".otf")
    :param font_size: 字体大小
    :param color: 文字颜色 (RGBA 格式)
    :return: 添加文字后的图像 (NumPy 数组，4 通道 RGBA)
    """
    # 如果输入是 NumPy 数组，转换为 PIL 图像
    if isinstance(image, np.ndarray):
        if image.shape[2] == 3:  # 如果是 3 通道图像，转换为 4 通道
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        image = Image.fromarray(image, 'RGBA')  # 转换为 PIL 图像 (RGBA 模式)
    elif image.mode != 'RGBA':  # 如果 PIL 图像不是 RGBA 模式，转换为 RGBA
        image = image.convert('RGBA')

    # 加载字体文件
    font = ImageFont.truetype(font_path, font_size)

    # 创建绘图对象
    draw = ImageDraw.Draw(image)

    # 获取字体高度
    bbox = font.getbbox("A")  # 获取字符的边界框
    font_height = bbox[3] - bbox[1]  # 计算高度

    # 逐行绘制文本
    x, y = position
    for line in text.split('\n'):
        draw.text((x, y), line, font=font, fill=color)
        y += font_height  # 移动到下一行

    # 将 PIL 图像转换回 NumPy 数组 (RGBA 格式)
    image_with_text = np.array(image)
    return image_with_text


def truncate_string(string, max_length=12):
    """
    将字符串截断为指定长度，并在末尾添加省略号。
    :param string: 输入的字符串
    :param max_length: 最大长度（包括省略号）
    :return: 截断后的字符串
    """
    

    if len(string) > max_length:
        return string[:max_length - 3] + "..."  # 保留前 max_length - 3 个字符，并添加 "..."
    
    punctuation_map = {
        "，": ",",  # 中文逗号 -> 英文逗号
        "。": ".",  # 中文句号 -> 英文句号
        "！": "!",  # 中文感叹号 -> 英文感叹号
        "？": "?",  # 中文问号 -> 英文问号
        "；": ";",  # 中文分号 -> 英文分号
        "：": ":",  # 中文冒号 -> 英文冒号
        "“": '"',  # 中文左双引号 -> 英文双引号
        "”": '"',  # 中文右双引号 -> 英文双引号
        "‘": "'",  # 中文左单引号 -> 英文单引号
        "’": "'",  # 中文右单引号 -> 英文单引号
        "（": "(",  # 中文左括号 -> 英文左括号
        "）": ")",  # 中文右括号 -> 英文右括号
        "《": "<",  # 中文左书名号 -> 英文小于号
        "》": ">",  # 中文右书名号 -> 英文大于号
        "【": "[",  # 中文左方括号 -> 英文左方括号
        "】": "]",  # 中文右方括号 -> 英文右方括号
        "、": ",",  # 中文顿号 -> 英文逗号
        "—": "-",  # 中文破折号 -> 英文连字符
        "…": "...",  # 中文省略号 -> 英文省略号
    }
    for chinese_punc, english_punc in punctuation_map.items():
        string = string.replace(chinese_punc, english_punc)
    return string

def generate_60s_image(data:dict = Body(...) ,  color=None,path='./assests/image/60s.png'):
    """生成60s的图片"""
    background = generate_template_background(480,540,color)
    
    temp = np.zeros((40,150,4), dtype=np.uint8)

    coner = add_text_to_image_with_font(temp,"60S看世界",(30,8),'./font/NotoSansSC-Bold.otf',15,color)

    image = Image.open(path).convert("RGBA")  # 确保是 RGBA 格式

    # 创建一个与图片大小相同的纯色图像
    image = np.array(image)
    alpha_channel = image[:, :, 3]

    # 创建纯色图层
    color_layer = np.zeros_like(image)
    color_layer[:, :, :3] = color  # 设置颜色通道
    color_layer[:, :, 3] = alpha_channel  # 保留原始透明度通道
    # 将颜色覆盖到透明形状上


    image = color_layer

    coner = overlay_image(coner,image,(20,20))
    background = overlay_image(background,coner,(250,40),(255,255,255,255))
    # 解析文字
    reponse = data['data']['news']
    
    # 拼接文字
    for i in range(0,len(reponse)):
        background = add_text_to_image_with_font(background,'·  ' + truncate_string(reponse[i],38),(20,70+i*30),'./font/NotoSansSC-Bold.otf',12,(0,0,0))
    
    return background

def convert_b64(b64, target_size=None):
    """
    将 Base64 编码的图片转换为 NumPy 数组，并缩放到指定大小。

    参数:
        b64 (str): Base64 编码的图片字符串。
        target_size (tuple): 目标大小，格式为 (width, height)。如果为 None，则不缩放。

    返回:
        np.ndarray: 缩放后的 NumPy 数组（RGBA 格式）。
    """
    # 1. 解码 Base64 字符串为二进制数据
    binary_data = base64.b64decode(b64)

    # 2. 将二进制数据加载到内存中的文件流
    image_stream = io.BytesIO(binary_data)

    # 3. 从文件流中加载图片并转换为 RGBA
    image = Image.open(image_stream)

    # 4. 缩放图片到指定大小
    if target_size is not None:
        image = image.resize(target_size, Image.Resampling.LANCZOS)  # 使用高质量的抗锯齿算法

    # 5. 将图片转换为 NumPy 数组
    image_array = np.array(image)
    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGRA)

    return image_array

def generate_bili_image(data:dict = Body(...) ,  color=None,path='./assests/image/bili.png'):
    """生成 bili 的图片"""
    background = generate_template_background(250,400,color)

    temp = np.zeros((40,125,4), dtype=np.uint8)

    coner = add_text_to_image_with_font(temp,"bili 热搜",(40,10),'./font/NotoSansSC-Bold.otf',15,color)

    image = Image.open(path).convert("RGBA")  # 确保是 RGBA 格式

    # 创建一个与图片大小相同的纯色图像
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)

    coner = overlay_image(coner,image,(20,20))

    bililist = data['list']

    l = []
    for i in range(0,len(bililist)):
        l.append(bililist[i]['keyword'])
    

    background = overlay_image(background,coner,(150,40),(255,255,255,255))
    
    # 拼接文字
    for i in range(0,len(l)):
        background = add_text_to_image_with_font(background,'·  ' +truncate_string(l[i],38),(20,70+i*30),'./font/NotoSansSC-Bold.otf',12,(0,0,0))
    
    return background

def generate_fish_image(data:dict = Body(...) ,  color=None,path='./assests/image/fish.png'):
    """生成摸鱼日历的图片"""
    background = generate_template_background(200,400,color)

    temp = np.zeros((40,150,4), dtype=np.uint8)

    coner = add_text_to_image_with_font(temp,"摸鱼日历",(40,10),'./font/NotoSansSC-Bold.otf',15,color)

    image = Image.open(path).convert("RGBA")

    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)

    coner = overlay_image(coner,image,(20,20))
    
    i =0
    for festival,day in data.items():
        background = add_text_to_image_with_font(background,'距离                  还剩             天',(20,70+i*40),'./font/NotoSansSC-Bold.otf',15,(0,0,0,255))
        background = add_text_to_image_with_font(background,festival,(57,70+i*40),'./font/SSFangTangTi.ttf',25,color)
        if str(day).__len__()==1:
            day = "  "+str(day)
        if str(day).__len__()==2:
            day = " "+str(day)
        if str(day).__len__()==3:
            day = str(day)
        background = add_text_to_image_with_font(background,day,(140,70+i*40),'./font/NotoSansSC-Bold.otf',17,color)
        i+=1

    background = overlay_image(background,coner,(125,40))
    return background

def resize_image(input_path,max_size):
    with Image.open(input_path) as img:
        # 获取原始大小
        width, height = img.size
        max_width, max_height = max_size

        # 计算缩放比例
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_size = (int(width * ratio), int(height * ratio))
        else:
            new_size = (width, height)  # 如果图片小于目标大小，不缩放

        # 缩放图片
        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

    resized_img = resized_img.convert('RGBA')

    return np.array(resized_img)

def generate_anime_image(data: dict, color=None,path='./assests/image/anime.png'):
    """生成动漫日历的图片"""
    background = generate_template_background(480,540,color)

    temp = np.zeros((40,150,4), dtype=np.uint8)

    coner = add_text_to_image_with_font(temp,"今日新番",(40,10),'./font/NotoSansSC-Bold.otf',15,color)

    image = Image.open(path).convert("RGBA")

    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)

    coner = overlay_image(coner,image,(20,20))
    background = overlay_image(background,coner,(250,40))
    i = 0
    for name,path in data.items():
            
        name = insert_newline(name,7)

        if i <4:
            image = resize_image(path,(150,125))
            image =cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
            background = overlay_image(background,image,(80+i*110,150))
            background = add_text_to_image_with_font(background,name,(40+i*115,220),'./font/NotoSansSC-Bold.otf',10,(0,0,0,255))
        else :
            if i<8:
                image = resize_image(path,(150,125))
                image= cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)
                background = overlay_image(background,image,(80+(i-4)*110,350))
                background = add_text_to_image_with_font(background,name,(40+(i-4)*115,420),'./font/NotoSansSC-Bold.otf',10,(0,0,0,255))
        i+=1
    return background

def insert_newline(text, max_length):
    """
    在字符串超过指定长度时插入换行符。

    参数:
        text (str): 输入字符串。
        max_length (int): 最大长度，超过此长度则插入换行符。

    返回:
        str: 处理后的字符串。
    """
    fortimes =  math.ceil(text.__len__()/max_length)
    
    newstr = ''
    for i in range(fortimes):
        newstr += text[i*max_length:(i+1)*max_length] + '\n\n'

    return newstr

def generate_one_image(data:dict,color,path='./assests/image/one.png'):
    background = generate_template_background(480,120,color)

    temp = np.zeros((40,150,4), dtype=np.uint8)

    coner = add_text_to_image_with_font(temp,"每日一言",(40,10),'./font/NotoSansSC-Bold.otf',15,color)

    if path=='./assests/image/one.png':

        image = Image.open(path).convert("RGBA")

        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)

    coner = overlay_image(coner,image,(20,20))
    background = overlay_image(background,coner,(240,30))
   
    string = insert_newline(data['hitokoto'],25)

    background = add_text_to_image_with_font(background,string,(20,50),'./font/SSFangTangTi.ttf',30,color)
    background = add_text_to_image_with_font(background,f"--{data['from']}",(350,80),'./font/NotoSansSC-Regular.otf',20,color)
    return background

def generate_card(data:dict,color):
    card = np.zeros((120,140,4), dtype=np.uint8)

    convert = {
        0:"星期一",
        1:"星期二",
        2:"星期三",
        3:"星期四",
        4:"星期五",
        5:"星期六",
        6:"星期日"
    }
    
    week = convert[data['week']]
    card = add_text_to_image_with_font(card,week,(10,5),'./font/SSFangTangTi.ttf',50,color)
    card = add_text_to_image_with_font(card,data['date'],(10,70),'./font/SSFangTangTi.ttf',20,color)
    return card

def numpy_to_base64(image_array):
    """
    将 NumPy 数组转换为 Base64 编码的字符串。

    参数:
        image_array (np.ndarray): 图片的 NumPy 数组。

    返回:
        str: Base64 编码的字符串。
    """
    # 将 NumPy 数组转换为 PIL 图像
    image = Image.fromarray(image_array)

    # 将图像保存为字节流
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")

    # 将字节流转换为 Base64
    encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return encoded_string