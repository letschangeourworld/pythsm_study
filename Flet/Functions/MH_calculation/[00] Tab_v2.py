import flet as ft

def main(page: ft.Page):
    page.fonts = {
        "HDSansText":"<font file path>"
    }
    page.title = ""
    page.window_width = 1160
    page.window_height = 700
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "always"
  
    # Appbar 기능
    # page.appbar = ft.AppBar(
    #     leading = ft.Icon(
    #         ft.icons.EDIT_SQUARE,
    #         color = ft.colors.BLUE,
    #         size = 30 ),
    #     leading_width = 50,
    #     title = ft.Text(
    #         "MH Editor",
    #         size = 22,
    #         weight = ft.FontWeight.BOLD,
    #         color = ft.colors.BLACK,
    #         font_family = "HDSansText"
    #     ),
    #     center_title = False,
    #     bgcolor = ft.colors.SURFACE_VARIANT
    # )
    def tab_change(e):
        index = e.control.selected_index
        namescreen = e.control.tabs[index].text
        for x in range(len(e.control.tabs)):
            if index == x:
                page.controls[0].controls[0].content.controls[0].value = namescreen
        page.update()

    tab = ft.Tabs(
        selected_index = 0,
        animation_duration = 300,
        label_color = "black",
        indicator_color = "black",
        indicator_border_radius = 20,
        # divider_color = "#7c59f0",
        scrollable = True,
        on_change = tab_change,
        tabs = [
            ft.Tab(
                tab_content = ft.Row(
                    [
                        ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_SHARP),
                        ft.Text("Standard Sheet",
                                font_family = "HDSansText",
                                size = 15,
                                weight = "bold"
                                )
                    ]
                ),
                content = ft.Container(
                    content = ft.Text("Standard Sheet Data Table"),
                    alignment = ft.alignment.center
                ),
            ),
            ft.Tab(
                tab_content = ft.Row(
                    [
                        ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED),
                        ft.Text("Paint Area",
                                font_family = "HDSansText",
                                size = 15,
                                weight = "bold"
                                )
                    ]
                ),
                content = ft.Text("Paint Area Data Table", weight = "bold")
            ),
            ft.Tab(
                tab_content = ft.Row(
                    [
                        ft.Icon(ft.icons.CALCULATE),
                        ft.Text("MH Calculator",
                                font_family = "HDSansText",
                                size = 15,
                                weight = "bold"
                                )
                    ]
                ),
                content = ft.Text("MH Calculator", weight = "bold")
            )
        ]
    )

    tab_bar = ft.Container(
        width = page.window_width,
        height = 110,
        padding = 5,
        border_radius = ft.border_radius.vertical(bottom = 30),
        shadow = ft.BoxShadow(
            spread_radius = 1,
            blur_radius = 5,
            # color = ft.colors.BLUE_GREY_300,
            color = "#fc4795",
            # offset = ft.Offset(0,0),
            # blur_style = ft.ShadowBlurStyle.OUTER
        ),
        gradient = ft.LinearGradient(
            begin = ft.alignment.top_left,
            end = ft.alignment.bottom_right,
            colors = ["#ffffff","#7c59f0"]
        ),
        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon = "menu",
                            icon_size = 30,
                            icon_color = "blue" ),
                        ft.Text(
                            "MH Editor",
                            size = 27,
                            color = ft.colors.BLACK,
                            weight = "bold",
                            font_family = "HDSansText" )
                    ]                    
                ),
                tab
            ]
        )
    )
    page.overlay.append(tab_bar)
    # page.add(tab_bar)
    page.add(
        ft.Column(
            [
                ft.Container(
                    margin= ft.margin.only(
                        top = page.window_height / 2 ),
                    # alignment= ft.alignment.center,
                    content = ft.Column(
                        [
                            ft.Text("Sample", size = 30)
                        ]
                    )
                )
            ]
        )
    )

ft.app(target = main)
