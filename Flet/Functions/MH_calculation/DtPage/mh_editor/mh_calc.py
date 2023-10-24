import flet as ft
import name_data as nd

data = nd.data01
keys = list(data.keys())
values = list(data.values())

def mh_calc(page):
    def add_btn_clicked(e):
        option_text.value = f"{r4c1_dd.value}"
        page.update()

    t = ft.Text()
    def textbox_changed(e):
        t.value = e.control.value
        page.update()

    r1_btn1 = ft.ElevatedButton(
        width = 130,
        bgcolor = ft.colors.ON_SURFACE_VARIANT,
        color = ft.colors.WHITE,
        content = ft.Row(
            [
                ft.Text("다시 시작",
                        size = 15.5,
                        weight = "bold",
                        text_align = ft.TextAlign.LEFT,
                        font_family = "HDText"),
                ft.Icon(ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT_ROUNDED),
            ]
        )             
    )
    
    r1_btn2 = ft.ElevatedButton(
        width = 130,
        bgcolor = ft.colors.ON_SURFACE_VARIANT,
        color = ft.colors.WHITE,
        content = ft.Row(
            [
                ft.Text("검색 시작",
                        size = 15.5,
                        weight = "bold",
                        text_align = ft.TextAlign.LEFT,
                        font_family = "HDText" ),
                ft.Icon(ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT_ROUNDED)
            ]
        )
    )

    r1_btn3 = ft.ElevatedButton(
        width = 220,
        bgcolor = ft.colors.ON_SURFACE_VARIANT,
        color = ft.colors.WHITE,
        content = ft.Row(
            [
                ft.Text("검색결과 테이블내 입력",
                        size = 15.5,
                        weight = "bold",
                        text_align = ft.TextAlign.LEFT,
                        font_family = "HDText" ),
                ft.Icon(ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT_ROUNDED)
            ]
        ),
        on_click = add_btn_clicked )

    r1_final = ft.Container(
        ft.Row(
            [
                r1_btn1,
                r1_btn2,
                r1_btn3
            ],
            alignment = ft.MainAxisAlignment.START,
            spacing = 15
        ),
        padding = 0
    )
    
    # c1 묶음
    r2c1_input_txt = ft.TextField(
        hint_text = "작업지시문장입력",
        on_change = textbox_changed,
        width = 490,
        height = 50,
        border_color =ft.colors.BLACK38,
        border_width = 1.2,
        text_size = 13
    )
    
    r3c1_input_txt1 = ft.TextField(
        hint_text = "LENGTH",
        on_change = textbox_changed,
        width = 115,
        height = 50,
        border_color=ft.colors.BLACK45,
        border_width= 1.2,
        text_size = 14,
        filled = True)
    
    r3c1_input_txt2 = ft.TextField(
        hint_text = "WIDTH",
        on_change = textbox_changed,
        width = 115,
        height = 50,
        border_color=ft.colors.BLACK45,
        border_width= 1.2,
        text_size = 14,
        filled = True)
    
    r3c1_input_txt3 = ft.TextField(
        hint_text = "AREA",
        on_change = textbox_changed,
        width = 115,
        height = 50,
        border_color = ft.colors.BLACK45,
        border_width = 1.2,
        text_size = 14,
        filled = True)
    
    r3c1_input_txt4 = ft.TextField(
        hint_text = "Q'TY",
        on_change = textbox_changed,
        width = 115,
        height = 50,
        border_color = ft.colors.BLACK45,
        border_width = 1.2,
        text_size = 14,
        filled = True)
    
    r4c1_dd = ft.Dropdown(
        label = "SPEC",
        width = 490,
        height = 50,
        color = ft.colors.BLACK,
        autofocus= True,
        options = [
            ft.dropdown.Option("option01"),
            ft.dropdown.Option("option02"),
            ft.dropdown.Option("option03")
        ]
    )
    
    r3c1_row = ft.Row(
        [
            r3c1_input_txt1,
            r3c1_input_txt2,
            r3c1_input_txt3,
            r3c1_input_txt4
        ],
        alignment = ft.MainAxisAlignment.START
    )
    
    c1 = ft.Container(
        content = ft.Column(
            [
                
                r2c1_input_txt,
                r3c1_row,
                r4c1_dd
            ],
            alignment = ft.MainAxisAlignment.START,
            spacing = 7
        )
    )
    
    # c2 묶음
    r2c2_symbol = ft.Text(
        color = ft.colors.BLACK87,
        weight = ft.FontWeight.BOLD,
        size = 15,
        width = 280,
        text_align = ft.TextAlign.RIGHT
    )
    r2c2_symbol_nm = ft.Text(
        color = ft.colors.WHITE,
        weight = ft.FontWeight.BOLD,
        size = 15,
        width = 80,
        text_align = ft.TextAlign.CENTER
    )
    r2c2_symbol.value = values[6]
    r2c2_symbol_nm.value = keys[6]
    
    r2c2_symbol_container = ft.Container(
        content = r2c2_symbol_nm,
        bgcolor = ft.colors.BLACK87,
        padding = 7,
        shadow = ft.BoxShadow(
            spread_radius = 0.5,
            blur_radius = 10,
            color = ft.colors.BLUE_GREY_300,
            offset = ft.Offset(0, 0),
            blur_style = ft.ShadowBlurStyle.OUTER
        )
    )
    r2c2_symbol_txt_container = ft.Container(
        content = ft.Row(
            [
                r2c2_symbol
            ]
        ),
        bgcolor = ft.colors.LIGHT_BLUE_50,
        padding = 7,
        width = 300,
        shadow = ft.BoxShadow(
            spread_radius = 0.5,
            blur_radius = 1,
            color = ft.colors.BLUE_GREY_300,
            offset = ft.Offset(0, 0),
            blur_style = ft.ShadowBlurStyle.OUTER,
        )
    )
    
    r3c2_mod = ft.Text(
        color = ft.colors.BLACK87,
        weight = ft.FontWeight.BOLD,
        size = 15,
        width = 280,
        text_align = ft.TextAlign.RIGHT
    )
    r3c2_mod_nm = ft.Text(
        color = ft.colors.WHITE,
        weight = ft.FontWeight.BOLD,
        size = 15,
        width = 80,
        text_align = ft.TextAlign.CENTER
    )
    r3c2_mod.value = values[7]
    r3c2_mod_nm.value = keys[7]
    
    r3c2_mod_container = ft.Container(
        content = r3c2_mod_nm,
        bgcolor = ft.colors.BLACK87,
        padding = 7,
        shadow = ft.BoxShadow(
            spread_radius = 0.5,
            blur_radius = 10,
            color = ft.colors.BLUE_GREY_300,
            offset = ft.Offset(0, 0),
            blur_style = ft.ShadowBlurStyle.OUTER
        )
    )
    r3c2_mod_txt_container = ft.Container(
        content = ft.Row(
            [
                r3c2_mod
            ]
        ),
        bgcolor = ft.colors.LIGHT_BLUE_50,
        padding = 7,
        width = 300,
        shadow = ft.BoxShadow(
            spread_radius = 0.5,
            blur_radius = 1,
            color = ft.colors.BLUE_GREY_300,
            offset = ft.Offset(0, 0),
            blur_style = ft.ShadowBlurStyle.OUTER,
        )
    )
    
    r4c2_mh = ft.Text(
        color = ft.colors.BLACK87,
        weight = ft.FontWeight.BOLD,
        size = 15,
        width = 280,
        text_align = ft.TextAlign.RIGHT
    )
    r4c2_mh_nm = ft.Text(
        color = ft.colors.WHITE,
        weight = ft.FontWeight.BOLD,
        size = 15,
        width = 80,
        text_align = ft.TextAlign.CENTER
    )
    r4c2_mh.value = values[8]
    r4c2_mh_nm.value = keys[8]
    
    r4c2_mh_container = ft.Container(
        content = r4c2_mh_nm,
        bgcolor = ft.colors.BLACK87,
        padding = 7,
        shadow = ft.BoxShadow(
            spread_radius = 0.5,
            blur_radius = 10,
            color = ft.colors.BLUE_GREY_300,
            offset = ft.Offset(0, 0),
            blur_style = ft.ShadowBlurStyle.OUTER
        )
    )
    r4c2_mh_txt_container = ft.Container(
        content = ft.Row(
            [
                r4c2_mh
            ],
            spacing = 30
        ),
        width = 300,
        bgcolor = ft.colors.LIGHT_BLUE_50,
        padding = 7,
        shadow = ft.BoxShadow(
            spread_radius = 0.5,
            blur_radius = 1,
            color = ft.colors.BLUE_GREY_300,
            offset = ft.Offset(0, 0),
            blur_style = ft.ShadowBlurStyle.OUTER,
        )
    )
    
    r5_btn1 = ft.ElevatedButton(
        width = 150,
        bgcolor = ft.colors.ON_SURFACE_VARIANT,
        color = ft.colors.WHITE,
        content = ft.Row(
            [
                ft.Text("Remove Table",
                        size = 15.5,
                        weight = "bold",
                        text_align = ft.TextAlign.CENTER,
                        font_family = "HDText")
            ]
        )             
    )
    
    r5_btn2 = ft.ElevatedButton(
        width = 150,
        bgcolor = ft.colors.ON_SURFACE_VARIANT,
        color = ft.colors.WHITE,
        content = ft.Row(
            [
                ft.Text("Add Table",
                        size = 15.5,
                        weight = "bold",
                        text_align = ft.TextAlign.CENTER,
                        font_family = "HDText" )
            ]
        )
    )

    r5_btn3 = ft.ElevatedButton(
        width = 150,
        bgcolor = ft.colors.ON_SURFACE_VARIANT,
        color = ft.colors.WHITE,
        content = ft.Row(
            [
                ft.Text("Save to Excel",
                        size = 15.5,
                        weight = "bold",
                        text_align = ft.TextAlign.CENTER,
                        font_family = "HDText" )
            ]
        )
    )
    
    r5_final = ft.Container(
        ft.Row(
            [
                r5_btn1,
                r5_btn2,
                r5_btn3
            ],
            alignment = ft.MainAxisAlignment.END,
            spacing = 15
        ),
        padding = 0
    )
    
    r2c2_row = ft.Row(
        [
            r2c2_symbol_container,
            r2c2_symbol_txt_container
        ]
    )
    
    r3c2_row = ft.Row(
        [
            r3c2_mod_container,
            r3c2_mod_txt_container
        ]
    )
    
    r4c2_row = ft.Row(
        [
            r4c2_mh_container,
            r4c2_mh_txt_container
        ]
    )

    c2 = ft.Container(
        content = ft.Column(
            [
                r2c2_row,
                r3c2_row,
                r4c2_row
            ],
            alignment = ft.MainAxisAlignment.START,
            spacing = 20
        ),
        padding = 30
    )
    
    c1c2 = ft.Container(
        content = ft.Row(
            [
                c1,
                c2
            ],
            alignment = ft.MainAxisAlignment.START
        )
    )
    
    c1c2_final = ft.Column(
        [
            c1c2
        ],
        alignment = ft.MainAxisAlignment.START
    )
    
    option_text = ft.Text(
                color = ft.colors.BLACK,
                weight = "bold",
                text_align = ft.TextAlign.CENTER,
                width = 145,
                font_family = "HDText")
    
    dt = ft.DataTable(
        width = 1100,
        height = 300,
        bgcolor = ft.colors.WHITE,
        border = ft.border.all(0,color=ft.colors.BLACK45),
        border_radius = 6,
        heading_row_color = ft.colors.BLACK26,
        heading_row_height = 20,
        divider_thickness = 0,
        column_spacing = 1,
        columns = [
            # 0 Number
            ft.DataColumn(ft.Text(keys[0],
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 40,
                                text_align=ft.TextAlign.CENTER,
                                font_family = "HDText"
                                )),
            # 1 Instruction
            ft.DataColumn(ft.Text(keys[1],
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 300,
                                text_align=ft.TextAlign.CENTER,
                                font_family = "HDText"
                                )),
            # 2 Length
            ft.DataColumn(ft.Text(keys[2],
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 60,
                                text_align=ft.TextAlign.CENTER,
                                font_family = "HDText"
                                )),
            # 3 Width
            ft.DataColumn(ft.Text(keys[3],
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 60,
                                text_align=ft.TextAlign.CENTER,
                                font_family = "HDText"
                                )),
            # 4 Area
            ft.DataColumn(ft.Text(keys[4],
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 60,
                                text_align=ft.TextAlign.CENTER,
                                font_family = "HDText"
                                )),
            # 5 Q'TY
            ft.DataColumn(ft.Text(keys[5],
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 60,
                                text_align=ft.TextAlign.CENTER,
                                font_family = "HDText"
                                )),
            # 6 SPEC
            ft.DataColumn(ft.Text("SPEC",
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 150,
                                text_align=ft.TextAlign.CENTER,
                                font_family = "HDText"
                                )),
            # 7 Symbol
            ft.DataColumn(ft.Text(keys[6],
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 150,
                                text_align=ft.TextAlign.CENTER,
                                font_family = "HDText"
                                )),
            # 8 Mod
            ft.DataColumn(ft.Text(keys[7],
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 60,
                                text_align = ft.TextAlign.CENTER,
                                font_family = "HDText"
                                )),
            # 9 MH
            ft.DataColumn(ft.Text(keys[8],
                                color = ft.colors.BLACK,
                                weight = "bold",
                                width = 60,
                                text_align = ft.TextAlign.CENTER,
                                font_family = "HDText"
                                ))
        ],
        rows = [
            ft.DataRow(
                [
                    # 0 Number
                    ft.DataCell(ft.Text(values[0],
                                        color = ft.colors.BLACK,
                                        weight = "bold",
                                        text_align = ft.TextAlign.CENTER,
                                        width = 40,
                                        font_family = "HDText"
                                        )),
                    # 1 Instrunction
                    ft.DataCell(ft.Text(values[1],
                                        color = ft.colors.BLACK,
                                        weight = "bold",
                                        text_align = ft.TextAlign.LEFT,
                                        width = 290,
                                        font_family = "HDText"
                                        )),
                    # 2 Length
                    ft.DataCell(ft.Text(values[2],
                                        color = ft.colors.BLACK,
                                        weight = "bold",
                                        text_align = ft.TextAlign.RIGHT,
                                        width = 50,
                                        font_family = "HDText"
                                        )),
                    # 3 Width
                    ft.DataCell(ft.Text(values[3],
                                        color = ft.colors.BLACK,
                                        weight = "bold",
                                        text_align = ft.TextAlign.RIGHT,
                                        width = 50,
                                        font_family = "HDText"
                                        )),
                    # 4 Area
                    ft.DataCell(ft.Text(values[4],
                                        color = ft.colors.BLACK,
                                        weight = "bold",
                                        text_align = ft.TextAlign.RIGHT,
                                        width = 50,
                                        font_family = "HDText"
                                        )),
                    # 5 Q'TY
                    ft.DataCell(ft.Text(values[5],
                                        color = ft.colors.BLACK,
                                        weight = "bold",
                                        text_align = ft.TextAlign.RIGHT,
                                        width = 50,
                                        font_family = "HDText"
                                        )),
                    # 6 SPEC
                    ft.DataCell(option_text),
                    # 7 Symbol
                    ft.DataCell(ft.Text(values[6],
                                        color = ft.colors.BLACK,
                                        weight = "bold",
                                        text_align = ft.TextAlign.CENTER,
                                        width = 150,
                                        font_family = "HDText"
                                        )),
                    # 8 Mod
                    ft.DataCell(ft.Text(values[7],
                                        color = ft.colors.BLACK,
                                        weight = "bold",
                                        text_align = ft.TextAlign.RIGHT,
                                        width = 47,
                                        font_family = "HDText"
                                        )),
                    # 9 MH
                    ft.DataCell(ft.Text(values[8],
                                        color = ft.colors.BLACK,
                                        weight = "bold",
                                        text_align = ft.TextAlign.RIGHT,
                                        width = 42,
                                        font_family = "HDText"
                                        ))
                ],
            )
        ]
    )
    
    return ft.Column(
        expand = True,
        # alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.Text(""),
            ft.Text(" ※ 문장입력 → 실행 → 모드자동검색 → 결과를 테이블내 입력",
                    color = ft.colors.BLACK54,
                    weight = "bold",
                    font_family = "HDText" ),
            r1_final,
            c1c2_final,
            r5_final,
            ft.Divider(height = 1,
                       color = ft.colors.BLACK45),
            dt
        ]
    )
