import flet as ft
import name_data as nd

class MhCalc(ft.UserControl):
    def __init__(self, data):
        super().__init__()
        self.data = data
        
    def add_btn_clicked(self, e):
        self.option_text.value = f"{self.r4c1_dd.value}"
        self.update()
        
    def textbox_changed(self, e):
        self.t = ft.Text()
        self.t.value = e.control.value
        self.update()
    
    def build(self):
        self.r1_btn1 = ft.ElevatedButton(
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
        
        self.r1_btn2 = ft.ElevatedButton(
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

        self.r1_btn3 = ft.ElevatedButton(
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
            on_click = self.add_btn_clicked )

        self.r1_final = ft.Container(
            ft.Row(
                [
                    self.r1_btn1,
                    self.r1_btn2,
                    self.r1_btn3
                ],
                alignment = ft.MainAxisAlignment.START,
                spacing = 15
            ),
            padding = 0
        )
        
        # c1 묶음
        self.r2c1_input_txt = ft.TextField(
            hint_text = "작업지시문장입력",
            on_change = self.textbox_changed,
            width = 490,
            height = 50,
            border_color = ft.colors.BLACK38,
            border_width = 1.2,
            text_size = 13
        )
        
        self.r3c1_input_txt1 = ft.TextField(
            hint_text = "LENGTH",
            on_change = self.textbox_changed,
            width = 115,
            height = 50,
            border_color=ft.colors.BLACK45,
            border_width= 1.2,
            text_size = 14,
            filled = True)
        
        self.r3c1_input_txt2 = ft.TextField(
            hint_text = "WIDTH",
            on_change = self.textbox_changed,
            width = 115,
            height = 50,
            border_color=ft.colors.BLACK45,
            border_width= 1.2,
            text_size = 14,
            filled = True)
        
        self.r3c1_input_txt3 = ft.TextField(
            hint_text = "AREA",
            on_change = self.textbox_changed,
            width = 115,
            height = 50,
            border_color = ft.colors.BLACK45,
            border_width = 1.2,
            text_size = 14,
            filled = True)
        
        self.r3c1_input_txt4 = ft.TextField(
            hint_text = "Q'TY",
            on_change = self.textbox_changed,
            width = 115,
            height = 50,
            border_color = ft.colors.BLACK45,
            border_width = 1.2,
            text_size = 14,
            filled = True)
        
        self.r4c1_dd = ft.Dropdown(
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
        
        self.r3c1_row = ft.Row(
            [
                self.r3c1_input_txt1,
                self.r3c1_input_txt2,
                self.r3c1_input_txt3,
                self.r3c1_input_txt4
            ],
            alignment = ft.MainAxisAlignment.START
        )
        
        self.c1 = ft.Container(
            content = ft.Column(
                [
                    self.r2c1_input_txt,
                    self.r3c1_row,
                    self.r4c1_dd
                ],
                alignment = ft.MainAxisAlignment.START,
                spacing = 7
            )
        )
        
        # c2 묶음
        self.r2c2_symbol = ft.Text(
            color = ft.colors.BLACK87,
            weight = ft.FontWeight.BOLD,
            size = 15,
            width = 280,
            text_align = ft.TextAlign.RIGHT
        )
        self.r2c2_symbol_nm = ft.Text(
            color = ft.colors.WHITE,
            weight = ft.FontWeight.BOLD,
            size = 15,
            width = 80,
            text_align = ft.TextAlign.CENTER
        )
        
        self.keys = list(self.data.keys())
        self.values = list(self.data.values())
        
        self.r2c2_symbol.value = self.values[6]
        self.r2c2_symbol_nm.value = self.keys[6]
        
        self.r2c2_symbol_container = ft.Container(
            content = self.r2c2_symbol_nm,
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
        self.r2c2_symbol_txt_container = ft.Container(
            content = ft.Row(
                [
                    self.r2c2_symbol
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
        
        self.r3c2_mod = ft.Text(
            color = ft.colors.BLACK87,
            weight = ft.FontWeight.BOLD,
            size = 15,
            width = 280,
            text_align = ft.TextAlign.RIGHT
        )
        self.r3c2_mod_nm = ft.Text(
            color = ft.colors.WHITE,
            weight = ft.FontWeight.BOLD,
            size = 15,
            width = 80,
            text_align = ft.TextAlign.CENTER
        )
        self.r3c2_mod.value = self.values[7]
        self.r3c2_mod_nm.value = self.keys[7]
        
        self.r3c2_mod_container = ft.Container(
            content = self.r3c2_mod_nm,
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
        self.r3c2_mod_txt_container = ft.Container(
            content = ft.Row(
                [
                    self.r3c2_mod
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
        
        self.r4c2_mh = ft.Text(
            color = ft.colors.BLACK87,
            weight = ft.FontWeight.BOLD,
            size = 15,
            width = 280,
            text_align = ft.TextAlign.RIGHT
        )
        self.r4c2_mh_nm = ft.Text(
            color = ft.colors.WHITE,
            weight = ft.FontWeight.BOLD,
            size = 15,
            width = 80,
            text_align = ft.TextAlign.CENTER
        )
        self.r4c2_mh.value = self.values[8]
        self.r4c2_mh_nm.value = self.keys[8]
        
        self.r4c2_mh_container = ft.Container(
            content = self.r4c2_mh_nm,
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
        self.r4c2_mh_txt_container = ft.Container(
            content = ft.Row(
                [
                    self.r4c2_mh
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
        
        self.r5_btn1 = ft.ElevatedButton(
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
        
        self.r5_btn2 = ft.ElevatedButton(
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

        self.r5_btn3 = ft.ElevatedButton(
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
        
        self.r5_final = ft.Container(
            ft.Row(
                [
                    self.r5_btn1,
                    self.r5_btn2,
                    self.r5_btn3
                ],
                alignment = ft.MainAxisAlignment.END,
                spacing = 15
            ),
            padding = 0
        )
        
        self.r2c2_row = ft.Row(
            [
                self.r2c2_symbol_container,
                self.r2c2_symbol_txt_container
            ]
        )
        
        self.r3c2_row = ft.Row(
            [
                self.r3c2_mod_container,
                self.r3c2_mod_txt_container
            ]
        )
        
        self.r4c2_row = ft.Row(
            [
                self.r4c2_mh_container,
                self.r4c2_mh_txt_container
            ]
        )

        self.c2 = ft.Container(
            content = ft.Column(
                [
                    self.r2c2_row,
                    self.r3c2_row,
                    self.r4c2_row
                ],
                alignment = ft.MainAxisAlignment.START,
                spacing = 20
            ),
            padding = 30
        )
        
        self.c1c2 = ft.Container(
            content = ft.Row(
                [
                    self.c1,
                    self.c2
                ],
                alignment = ft.MainAxisAlignment.START
            )
        )
        
        self.c1c2_final = ft.Column(
            [
                self.c1c2
            ],
            alignment = ft.MainAxisAlignment.START
        )
        
        self.option_text = ft.Text(
                    color = ft.colors.BLACK,
                    weight = "bold",
                    text_align = ft.TextAlign.CENTER,
                    width = 145,
                    font_family = "HDText")
        
        self.dt = ft.DataTable(
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
                ft.DataColumn(ft.Text(self.keys[0],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    width = 40,
                                    text_align=ft.TextAlign.CENTER,
                                    font_family = "HDText"
                                    )),
                # 1 Instruction
                ft.DataColumn(ft.Text(self.keys[1],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    width = 300,
                                    text_align=ft.TextAlign.CENTER,
                                    font_family = "HDText"
                                    )),
                # 2 Length
                ft.DataColumn(ft.Text(self.keys[2],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    width = 60,
                                    text_align=ft.TextAlign.CENTER,
                                    font_family = "HDText"
                                    )),
                # 3 Width
                ft.DataColumn(ft.Text(self.keys[3],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    width = 60,
                                    text_align=ft.TextAlign.CENTER,
                                    font_family = "HDText"
                                    )),
                # 4 Area
                ft.DataColumn(ft.Text(self.keys[4],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    width = 60,
                                    text_align=ft.TextAlign.CENTER,
                                    font_family = "HDText"
                                    )),
                # 5 Q'TY
                ft.DataColumn(ft.Text(self.keys[5],
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
                ft.DataColumn(ft.Text(self.keys[6],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    width = 150,
                                    text_align=ft.TextAlign.CENTER,
                                    font_family = "HDText"
                                    )),
                # 8 Mod
                ft.DataColumn(ft.Text(self.keys[7],
                                    color = ft.colors.BLACK,
                                    weight = "bold",
                                    width = 60,
                                    text_align = ft.TextAlign.CENTER,
                                    font_family = "HDText"
                                    )),
                # 9 MH
                ft.DataColumn(ft.Text(self.keys[8],
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
                        ft.DataCell(ft.Text(self.values[0],
                                            color = ft.colors.BLACK,
                                            weight = "bold",
                                            text_align = ft.TextAlign.CENTER,
                                            width = 40,
                                            font_family = "HDText"
                                            )),
                        # 1 Instrunction
                        ft.DataCell(ft.Text(self.values[1],
                                            color = ft.colors.BLACK,
                                            weight = "bold",
                                            text_align = ft.TextAlign.LEFT,
                                            width = 290,
                                            font_family = "HDText"
                                            )),
                        # 2 Length
                        ft.DataCell(ft.Text(self.values[2],
                                            color = ft.colors.BLACK,
                                            weight = "bold",
                                            text_align = ft.TextAlign.RIGHT,
                                            width = 50,
                                            font_family = "HDText"
                                            )),
                        # 3 Width
                        ft.DataCell(ft.Text(self.values[3],
                                            color = ft.colors.BLACK,
                                            weight = "bold",
                                            text_align = ft.TextAlign.RIGHT,
                                            width = 50,
                                            font_family = "HDText"
                                            )),
                        # 4 Area
                        ft.DataCell(ft.Text(self.values[4],
                                            color = ft.colors.BLACK,
                                            weight = "bold",
                                            text_align = ft.TextAlign.RIGHT,
                                            width = 50,
                                            font_family = "HDText"
                                            )),
                        # 5 Q'TY
                        ft.DataCell(ft.Text(self.values[5],
                                            color = ft.colors.BLACK,
                                            weight = "bold",
                                            text_align = ft.TextAlign.RIGHT,
                                            width = 50,
                                            font_family = "HDText"
                                            )),
                        # 6 SPEC
                        ft.DataCell(self.option_text),
                        # 7 Symbol
                        ft.DataCell(ft.Text(self.values[6],
                                            color = ft.colors.BLACK,
                                            weight = "bold",
                                            text_align = ft.TextAlign.CENTER,
                                            width = 150,
                                            font_family = "HDText"
                                            )),
                        # 8 Mod
                        ft.DataCell(ft.Text(self.values[7],
                                            color = ft.colors.BLACK,
                                            weight = "bold",
                                            text_align = ft.TextAlign.RIGHT,
                                            width = 47,
                                            font_family = "HDText"
                                            )),
                        # 9 MH
                        ft.DataCell(ft.Text(self.values[8],
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
                self.r1_final,
                self.c1c2_final,
                self.r5_final,
                ft.Divider(height = 1, color = ft.colors.BLACK45),
                self.dt
            ]
        )
