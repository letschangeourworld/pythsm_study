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
    page.scroll = "auto"
    pic_loc = ft.TextField(label = "Fill in the image file name (ex: example.png)")
    pic_preview = ft.Image(src = False, width = 500, height = 500)
    
    def process_pic(e):
        pic_pro = Image.open(pic_loc.value)
        txt = pytesseract.image_to_string(pic_pro)
        pic_preview.src = f"{os.getcwd()}/{pic_loc.value}"
        page.snack_bar = ft.SnackBar(
            ft.Text(txt, size = 20),
            ft.Text("Successfully got your image!!", size = 20),
            bgcolor = "green" )
        page.snack_bar.open = True
        page.update()

    page.add(
        ft.Column(
            [
                pic_loc,
                ft.ElevatedButton(
                    "Processed picture",
                    bgcolor = "blue",
                    color = "white",
                    on_click = process_pic ),
                ft.Text("Result Picture", weight = "bold"),
                pic_preview
            ]
        )
    )

ft.app(target = main, view = ft.AppView)
