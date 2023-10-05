
import flet as ft
import sampledata

'''
> sampledata.py 
alldata = {
        "NO": "1",
        "INSTRUCTION" : '루프패드를 부착하기 위해 도구를 잡는다.',
        "LENGTH" : '1',
        "WIDTH" : '1',
        "AREA" : '1',
        "Q'TY" : '2',
        "SYMBOL" : 'M04G04',
        "MOD" : '7.0',
        "MH": '2.0'
    }
'''

data = sampledata.alldata
keys = list(data.keys())
values = list(data.values())

dt = ft.DataTable(
    width = 950,
    height = 300,
    bgcolor = ft.colors.WHITE,
    border = ft.border.all(0,color=ft.colors.BLACK45),
    border_radius = 6,
    # vertical_lines= ft.border.BorderSide(0),
    # horizontal_lines= ft.border.BorderSide(0),
    # sort_column_index = 0,
    heading_row_color = ft.colors.BLACK26,
    heading_row_height = 20,
    divider_thickness = 0,
    column_spacing = 1,
    columns = [
        ft.DataColumn(ft.Text(keys[0],
                              color = ft.colors.BLACK,
                              weight = "bold",
                              width = 40,
                              text_align=ft.TextAlign.CENTER,
                              font_family = "HDSansText"
                              )),
        ft.DataColumn(ft.Text(keys[1],
                              color = ft.colors.BLACK,
                              weight = "bold",
                              width = 300,
                              text_align=ft.TextAlign.CENTER,
                              font_family = "HDSansText"
                              )),
        ft.DataColumn(ft.Text(keys[2],
                              color = ft.colors.BLACK,
                              weight = "bold",
                              width = 60,
                              text_align=ft.TextAlign.CENTER,
                              font_family = "HDSansText"
                              )),
        ft.DataColumn(ft.Text(keys[3],
                              color = ft.colors.BLACK,
                              weight = "bold",
                              width = 60,
                              text_align=ft.TextAlign.CENTER,
                              font_family = "HDSansText"
                              )),
        ft.DataColumn(ft.Text(keys[4],
                              color = ft.colors.BLACK,
                              weight = "bold",
                              width = 60,
                              text_align=ft.TextAlign.CENTER,
                              font_family = "HDSansText"
                              )),
        ft.DataColumn(ft.Text(keys[5],
                              color = ft.colors.BLACK,
                              weight = "bold",
                              width = 60,
                              text_align=ft.TextAlign.CENTER,
                              font_family = "HDSansText"
                              )),
        ft.DataColumn(ft.Text(keys[6],
                              color = ft.colors.BLACK,
                              weight = "bold",
                              width = 150,
                              text_align=ft.TextAlign.CENTER,
                              font_family = "HDSansText"
                              )),
        ft.DataColumn(ft.Text(keys[7],
                              color = ft.colors.BLACK,
                              weight = "bold",
                              width = 60,
                              text_align = ft.TextAlign.CENTER,
                              font_family = "HDSansText"
                              )),
        ft.DataColumn(ft.Text(keys[8],
                              color = ft.colors.BLACK,
                              weight = "bold",
                              width = 60,
                              text_align = ft.TextAlign.CENTER,
                              font_family = "HDSansText"
                              ))
    ],
    rows = [
        ft.DataRow(
            [
                ft.DataCell(ft.Text(values[0],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    text_align = ft.TextAlign.CENTER,
                                    width = 40,
                                    font_family = "HDSansText"
                                    )),
                ft.DataCell(ft.Text(values[1],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    text_align = ft.TextAlign.LEFT,
                                    width = 290,
                                    font_family = "HDSansText"
                                    )),
                ft.DataCell(ft.Text(values[2],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    text_align = ft.TextAlign.RIGHT,
                                    width = 50,
                                    font_family = "HDSansText"
                                    )),
                ft.DataCell(ft.Text(values[3],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    text_align = ft.TextAlign.RIGHT,
                                    width = 50,
                                    font_family = "HDSansText"
                                    )),
                ft.DataCell(ft.Text(values[4],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    text_align = ft.TextAlign.RIGHT,
                                    width = 50,
                                    font_family = "HDSansText"
                                    )),
                ft.DataCell(ft.Text(values[5],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    text_align = ft.TextAlign.RIGHT,
                                    width = 50,
                                    font_family = "HDSansText"
                                    )),
                ft.DataCell(ft.Text(values[6],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    text_align = ft.TextAlign.CENTER,
                                    width = 150,
                                    font_family = "HDSansText"
                                    )),
                ft.DataCell(ft.Text(values[7],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    text_align = ft.TextAlign.RIGHT,
                                    width = 47,
                                    font_family = "HDSansText"
                                    )),
                ft.DataCell(ft.Text(values[8],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    text_align = ft.TextAlign.RIGHT,
                                    width = 42,
                                    font_family = "HDSansText"
                                    ))
            ],
        )
    ]
)

def main(page: ft.Page):
    page.fonts = {
        "HDSansText":"C:\\Users\\2801123\\AppData\\Local\\Microsoft\\Windows\\Fonts\\HYUNDAISANSTEXTKROTFREGULAR.OTF"
    }
    page.title = "MH TABLE"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "always"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.horizontal_alignment = ft.MainAxisAlignment.END

    page.appbar = ft.AppBar(
        leading = ft.Icon(
            ft.icons.CALCULATE_ROUNDED,
            color = ft.colors.BLUE,
            size = 40 ),
        leading_width = 30,
        title = ft.Text(
            "MH Calculator",
            size = 20,
            weight = ft.FontWeight.BOLD,
            color = ft.colors.BLACK,
            font_family = "HDSansText"
        ),
        center_title = False,
        bgcolor = ft.colors.SURFACE_VARIANT
    )

    def textbox_changed(e):
        t.value = e.control.value
        page.update()

    t = ft.Text()

    line_1 = ft.Row(
        [
            ft.ElevatedButton(
                width = 130,
                bgcolor = ft.colors.LIGHT_BLUE_700,
                color = ft.colors.WHITE,
                content = ft.Row(
                    [
                        ft.Text("Initialize", size= 16.5),
                        ft.Icon(ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT_ROUNDED),
                    ]
                )             
            ),
            ft.Text("                                                    "),
            ft.ElevatedButton(
                width = 130,
                bgcolor = ft.colors.LIGHT_BLUE_700,
                color = ft.colors.WHITE,
                content = ft.Row(
                    [
                        ft.Text("Execute", size= 16.5),
                        ft.Icon(ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT_ROUNDED)
                    ]
                )
            )
        ]
    )

    line_2 = ft.Row(
        [
            ft.TextField(
                hint_text= "Instruction Sentence",
                on_change = textbox_changed,
                width = 490,
                height = 40,
                border_color=ft.colors.BLACK38,
                border_width= 1.2,
                text_size= 15 ),
            ft.Text("   "),
            ft.Container(
                content = ft.Text(
                    "SYMBOL",
                    color = ft.colors.WHITE,
                    weight = ft.FontWeight.BOLD,
                    size = 15,
                    width = 80,
                    text_align = ft.TextAlign.CENTER
                ),
                bgcolor = ft.colors.BLACK87,
                padding = 7,
                shadow = ft.BoxShadow(
                    spread_radius = 0.5,
                    blur_radius = 10,
                    color = ft.colors.BLUE_GREY_300,
                    offset = ft.Offset(0, 0),
                    blur_style = ft.ShadowBlurStyle.OUTER,
                )
            ),
            ft.Text(" "),
            ft.Container(
                content = ft.Row(
                    [
                        ft.Text(
                            "M04G04",
                            size = 15,
                            width = 285,
                            color = ft.colors.BLACK,
                            weight = ft.FontWeight.BOLD,
                            text_align = ft.TextAlign.RIGHT,
                            font_family = "HDSansText" ),
                    ]
                ),
                bgcolor = ft.colors.LIGHT_BLUE_50,
                padding = 7,
                shadow = ft.BoxShadow(
                    spread_radius = 0,
                    blur_radius = 1,
                    color = ft.colors.BLUE_GREY_300,
                    offset = ft.Offset(0, 0),
                    blur_style = ft.ShadowBlurStyle.OUTER,
                )                    
            )
        ]
    )

    line_3 = ft.Row(
        [
            ft.TextField(
                hint_text = "LENGTH",
                on_change = textbox_changed,
                width = 115,
                height = 35,
                border_color=ft.colors.BLACK45,
                border_width= 1.2,
                text_size = 14,
                filled = True),
            ft.TextField(
                hint_text = "WIDTH",
                on_change = textbox_changed,
                width = 115,
                height = 35,
                border_color=ft.colors.BLACK45,
                border_width= 1.2,
                text_size = 14,
                filled = True),
            ft.TextField(
                hint_text = "AREA",
                on_change = textbox_changed,
                width = 115,
                height = 35,
                border_color = ft.colors.BLACK45,
                border_width = 1.2,
                text_size = 14,
                filled = True),
            ft.TextField(
                hint_text = "Q'TY",
                on_change = textbox_changed,
                width = 115,
                height = 35,
                border_color = ft.colors.BLACK45,
                border_width = 1.2,
                text_size = 14,
                filled = True),

            ft.Text("   "),
            ft.Container(
                content = ft.Text(
                    "MOD",
                    color = ft.colors.WHITE,
                    weight = ft.FontWeight.BOLD,
                    size = 15,
                    width = 80,
                    text_align = ft.TextAlign.CENTER
                ),
                bgcolor = ft.colors.BLACK87,
                padding = 7,
                shadow = ft.BoxShadow(
                    spread_radius = 0.5,
                    blur_radius = 10,
                    color = ft.colors.BLUE_GREY_300,
                    offset = ft.Offset(0, 0),
                    blur_style = ft.ShadowBlurStyle.OUTER,
                )
            ),
            ft.Text(" "),
            ft.Container(
                content = ft.Row(
                    [
                        ft.Text(
                            "7.0",
                            size = 15,
                            width = 285,
                            color = ft.colors.BLACK,
                            weight = ft.FontWeight.BOLD,
                            text_align = ft.TextAlign.RIGHT,
                            font_family = "HDSansText" ),
                    ]
                ),
                bgcolor = ft.colors.LIGHT_BLUE_50,
                padding = 7,
                shadow = ft.BoxShadow(
                    spread_radius = 0,
                    blur_radius = 1,
                    color = ft.colors.BLUE_GREY_300,
                    offset = ft.Offset(0, 0),
                    blur_style = ft.ShadowBlurStyle.OUTER,
                )                    
            )
        ]
    )

    line_4 = ft.Row(
        [
            ft.Dropdown(
                label = "SPEC",
                width = 490,
                height = 40,
                color = ft.colors.WHITE,
                options = [
                    ft.dropdown.Option("option01"),
                    ft.dropdown.Option("option02")
                ],
                autofocus= True
            ),
            ft.Text("   "),
            ft.Container(
                content = ft.Text(
                    "MH",
                    color = ft.colors.WHITE,
                    weight = ft.FontWeight.BOLD,
                    size = 15,
                    width = 80,
                    text_align = ft.TextAlign.CENTER
                ),
                bgcolor = ft.colors.BLACK87,
                padding = 7,
                shadow = ft.BoxShadow(
                    spread_radius = 0.5,
                    blur_radius = 10,
                    color = ft.colors.BLUE_GREY_300,
                    offset = ft.Offset(0, 0),
                    blur_style = ft.ShadowBlurStyle.OUTER,
                )
            ),
            ft.Text(" "),
            ft.Container(
                content = ft.Row(
                    [
                        ft.Text(
                            "2.0",
                            size = 15,
                            width = 285,
                            color = ft.colors.BLACK,
                            weight = ft.FontWeight.BOLD,
                            text_align = ft.TextAlign.RIGHT,
                            font_family = "HDSansText" ),
                    ]
                ),
                bgcolor = ft.colors.LIGHT_BLUE_50,
                padding = 7,
                shadow = ft.BoxShadow(
                    spread_radius = 0,
                    blur_radius = 1,
                    color = ft.colors.BLUE_GREY_300,
                    offset = ft.Offset(0, 0),
                    blur_style = ft.ShadowBlurStyle.OUTER,
                )                    
            )
        ]
    )

    line_1234 = ft.Container(
        content = ft.Column(
            [
                line_1,
                line_2,
                line_3,
                line_4,
                ft.Text(" "),
                ft.Divider(height = 1, color=ft.colors.BLACK45)
            ]
        )
    )

    page.add(line_1234, dt)

ft.app(target = main)

