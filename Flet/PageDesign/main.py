import flet as ft
from appmenu import appmenu
from Foryourmovie import section2
from Gridcard import gridscreen

def main(page: ft.Page):
    # page 폭과 높이를 확인하여 별도의 변수에 입력
    heightscr = page.window_height
    widthscr = page.window_width
    page.spacing = 0
    page.padding = 0
    page.update()
    
    # Row 안에 Container를 생성
    # Container 폭,높이를 page 폭,높이와 동일하게 설정
    # Container 안에 Column 3가지(appmenu, section, gridscreen)로 구성
    page.add(
        ft.ResponsiveRow(
            [ft.Container(
                width = widthscr,
                height = heightscr,
                gradient = ft.LinearGradient(begin = ft.alignment.top_left,
                                             end = ft.Alignment(0.5, 0.9),
                                             colors = ['#2C0B50','#7C1C60'] ),
                content = ft.Column( [appmenu, section2, gridscreen] )
                )
            ]
            )
        )
    page.update()

ft.app(port = 8550, target = main)

