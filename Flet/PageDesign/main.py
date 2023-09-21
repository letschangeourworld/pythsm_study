import flet as ft
from appmenu import appmenu
from Foryourmovie import section2
from Gridcard import gridscreen

def main(page: ft.Page):
    # This detects the height and width on your screen
    heightscr = page.window_height
    widthscr = page.window_width
    page.spacing = 0
    page.padding = 0
    page.update()
    
    page.add(
        ft.ResponsiveRow([
            ft.Container(
                width = widthscr,
                height = heightscr,
                gradient = ft.LinearGradient(
                    begin = ft.alignment.top_left,
                    end = ft.Alignment(0.5, 0.9),
                    colors = ['#2C0B50','#7C1C60']
                    ),
                content = ft.Column(
                    # This components from own libraries
                    [appmenu,
                     section2,
                     gridscreen]
                    )
                )
            ])
        )
    
    page.update()

ft.app(port = 8550, target = main)
