'''
Text Extraction from Images
'''

import flet as ft
from flet import *
import pytesseract      # Need to install pytesseract
from PIL import Image
import os

# Make a virtual environment based on python and install pytesseract through pip
# Download pytesseract installation file in this site below :
# https://github.com/UB-Mannheim/tesseract/wiki
# Select your own language in Additional language/script data during installation
# Add the path of pytesseract directory installed into the environment variable of your pc
# Force to designate the directory of pytesseract execution as follows

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def main(page: ft.Page):
    page.title = "Text Extraction in Images"
    # 내 PC에 있는 폰트 path 연결하여 이용하기
    page.fonts = {
       "D2Coding" : "C:\\Windows\\Fonts\\D2Coding-Ver1.3-20171129.ttc"
    } 
    # 페이지 상단 appbar 만들기
    page.appbar = ft.AppBar(
        leading = ft.Icon(
            ft.icons.BEACH_ACCESS_ROUNDED,
            color = ft.colors.BLUE,
            size = 40 ),
        leading_width = 40,
        title = ft.Text(
            "Text Extraction in Images",
            size = 20, weight = "bold",
            color = ft.colors.BLACK ),
        center_title = False,
        bgcolor = ft.colors.SURFACE_VARIANT
    )
    page.padding = 30
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "auto"
    page.window_width = 600
    page.window_height = 700

    # 현재의 directory에 저장시킨 이미지 파일명 입력
    pic_loc = ft.TextField(
        hint_text = "Image Path",
        border = ft.InputBorder.UNDERLINE,
        filled = True,
        height = 50)

    # 이미지 파일명 입력 전을 감안한 ft.Image 빈 객체 생성
    pic_preview = ft.Image(src = False, width = 500, height = 500)
    
    # 이미지에서 텍스트 추출되기 전을 감안한 ft.Text 빈 객체 생성
    # 추출된 텍스트를 여기에 삽입할 것임
    text = ft.Text("",
                   weight = "bold",
                   color = ft.colors.BLACK,
                   size = 15,
                   font_family = "D2Coding")
    
    # 이미지명을 입력한 후, 버튼을 클릭했을 때, 실행되어야 할 기능
    def button_click(e):
        pic_pro = Image.open(pic_loc.value)        # 이미지 불러오기
        txt = pytesseract.image_to_string(pic_pro) # 이미지에서 텍스트 추출하기
        text.value = str(txt)                      # 추출한 텍스트를 ft.Text 객체에 넣기
        
        # 이미지 파일 path를 입력하여 ft.Image 객체에 이미지를 넣기
        pic_preview.src = f"{os.getcwd()}/{pic_loc.value}"
        page.update()
        
    # 기능들을 연결해 넣고 페이지 생성
    page.add(
        ft.Column(
            [
                pic_loc,
                ft.ElevatedButton(
                    width = 240,
                    height = 50,
                    content = ft.Row(
                        [
                            ft.Icon(
                                name = ft.icons.PARK_ROUNDED,
                                color = ft.colors.GREEN),
                            ft.Text(
                                "Start Image Process",
                                size = 15,
                                weight = "bold",
                                font_family = "D2Coding")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_AROUND,
                        spacing = 5 ),
                    on_click = button_click ),
                
                ft.Divider(height = 10, color = "Gray"),
                ft.Text("Image Preview",
                        color = ft.colors.BLACK,
                        weight = "bold",
                        size = 18,
                        font_family = "D2Coding"),
                ft.Divider(height = 10, color = "Gray"),
                pic_preview,
                ft.Text("Recognized Result",
                        color = ft.colors.BLACK,
                        weight = "bold",
                        size = 18,
                        font_family = "D2Coding"),
                ft.Divider(height = 10, color = "Gray"),
                text
            ],
            spacing = 10
        )
    )

ft.app(target = main, view = ft.AppView)
