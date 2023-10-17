import flet as ft

def hello(e):
    print(e)
    print('Click_Function Executed inside the Container')

def main(page: ft.Page):
    page.title = 'Container'
    page.padding = 20
    page.bgcolor = ft.colors.WHITE
    c = ft.Container(
        content = ft.Text(
            value = 'Hello! Hi!',
            color = 'Black',
            weight = "bold",
            size = 40
        ),
        width  = 300,
        height = 300,
        padding = ft.padding.all(25),
        border_radius = ft.border_radius.all(30),
        # border_radius = ft.border_radius.only(top_left = 20, bottom_right = 20),
        on_click = lambda e: hello(e),
        # on_hover = lambda e: hello(e),
        # on_long_press = lambda e: hello(e),
        gradient = ft.LinearGradient(
            # tile_mode = "mirror",
            begin = ft.alignment.top_right,
            end = ft.alignment.bottom_right,
            colors = [
                "blue26",
                # "red12",
                # "purple12",
                "pink12",
                # "blue26"
            ],
        ),
        border = ft.border.all(width = 5, color = ft.colors.BLACK26),
        margin = ft.margin.all(20),
        # margin = ft.margin.only(top = 20, left = 20),
        tooltip = "Container for showing Hello"
    )

    page.add(c)

ft.app(target = main, view = ft.FLET_APP)
