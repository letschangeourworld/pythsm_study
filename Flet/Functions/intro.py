import flet as ft

def main(page: ft.Page):
    page.title = 'intro app'
    page.bgcolor = ft.colors.BLACK12
    page.horizontal_alignment = 'left'
    page.vertical_alignment = 'center'
    page.scroll = 'hidden'
    print(page.session_id)
    print(page.platform)
    for i in range(100):
        t = ft.Text(value = "Hello World")
        page.add(t)

ft.app(target = main, view = ft.FLET_APP)
