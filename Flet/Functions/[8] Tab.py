import flet as ft

def main(page: ft.Page):
    page.fonts = {
        "HDSansText":"<font file path>"
    }
    page.title = "Paint Manufacturing Engineering Team 1"
    page.window_width = 1160
    page.window_height = 700
    page.padding = 5
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "always"
    # page.vertical_alignment = ft.MainAxisAlignment.END
    # page.horizontal_alignment = ft.MainAxisAlignment.END
  
    # Appbar 기능
    page.appbar = ft.AppBar(
        leading = ft.Icon(
            ft.icons.EDIT_SQUARE,
            color = ft.colors.BLUE,
            size = 30 ),
        leading_width = 50,
        title = ft.Text(
            "MH Editor",
            size = 22,
            weight = ft.FontWeight.BOLD,
            color = ft.colors.BLACK,
            font_family = "HDSansText"
        ),
        center_title = False,
        bgcolor = ft.colors.SURFACE_VARIANT
    )
    
    t = ft.Tabs(
        selected_index = 0,
        animation_duration = 400,
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
                    content = ft.Text("Standard Sheet Data Table", 
                    font_family = "HDSansText",
                    size = 15,
                    weight = "bold"),
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
                                size = 15
                                )
                    ]
                ),
                content = ft.Text("MH Calculator")
            )
        ],
        # expand = 1,
        divider_color = ft.colors.BLUE_GREY_100
    )
    page.add(t)

ft.app(target = main)
