

class PaintAreaTab(ft.UserControl):
    def __init__(self, df_name):
        super().__init__(font_style["main"])
        
        self.font_text01 = list(font_style["main"].keys())[0]
        self.df_name = df_name
        
        self.paint_area_df = pd.read_csv(self.df_name, encoding = "utf-8")
        self.paint_area_df = self.paint_area_df.fillna("")
        self.paint_area_table = PaintArea(df = self.paint_area_df)
        
        voidTable = VoidDataTable()
        self.areaInputForm = InputAreaForm(voidTable)
        
        self.p_tabs = ft.Tabs(
            selected_index = 0,
            animation_duration = 200,
            scrollable = True,
            expand = True,
            tabs = [
                ft.Tab(
                    tab_content = ft.Row(
                        expand = True,
                        controls = [
                            ft.Text("면적입력결과",
                                    font_family = self.font_text01,
                                    size = 15,
                                    weight = "bold"
                            )
                        ]
                    ),
                    content = self.paint_area_table
                ),
                ft.Tab(
                    tab_content = ft.Row(
                        controls = [
                            ft.Text("면적수동입력",
                                    font_family = self.font_text01,
                                    size = 15,
                                    weight = "bold"
                            )
                        ]
                    ),
                    content = self.areaInputForm
                )
            ]
        )
    
    def build(self):
        return ft.Column(
            # expand = True,
            controls = [self.p_tabs]
        )

class StdTabMenu(ft.UserControl):
    def __init__(self, df_folder_name) -> None:
        super().__init__(font_style["main"])
        
        self.font_text01 = list(font_style["main"].keys())[0]
        
        path = f"{df_folder_name}"
        self.df_full_name_list = os.listdir(path)
        
        self.df_only_name_list = []
        for name in self.df_full_name_list:
            self.df_only_name_list.append(name.split(".csv")[0])
        
        self.std_tables_list = []
        for dataframe in self.df_full_name_list:
            self.std_df = pd.read_csv(f"{df_folder_name}/{dataframe}", encoding = "utf-8")
            self.std_df = self.std_df.fillna("")
            self.std_df[self.std_df.columns[3]] = self.std_df[self.std_df.columns[3]].apply(lambda x: round(x,3))
            self.std_df[self.std_df.columns[5]] = self.std_df[self.std_df.columns[5]].apply(lambda x: round(x))
            self.std_df[self.std_df.columns[6]] = self.std_df[self.std_df.columns[6]].apply(lambda x: round(x,1))
            
            self.std_table = StdSht(df = self.std_df)
            self.std_tables_list.append(self.std_table)
        
        self.s_tabs = ft.Tabs(
            selected_index = 0,
            animation_duration = 200,
            scrollable = True,
            expand = True,
            tabs = [
                ft.Tab(
                    tab_content = ft.Row(
                        [
                            ft.Text(name.upper(),
                                    font_family = self.font_text01,
                                    size = 12,
                                    weight = "bold")
                        ]
                    ),
                    content = std_sht
                ) for std_sht, name in zip(self.std_tables_list, self.df_only_name_list)
            ]
        )
        
        self.area_modal_btn = ft.IconButton(
            selected = 0,
            style = ft.ButtonStyle(shape = ft.StadiumBorder()),
            content = ft.Row(
                [
                ft.Icon(ft.icons.SAVE),
                ft.Text("면적수정입력",
                        size = 15,
                        weight = "bold",
                        font_family = self.font_text01,
                        text_align = ft.TextAlign.RIGHT
                        )
                ],
                alignment = ft.MainAxisAlignment.END
            ),
            on_click = self.area_modal_open_btn
        )
        
        self.dlg_modal = ft.AlertDialog(
            modal = True,
            title = ft.Text(
                "확인알림창",
                font_family = self.font_text01,
                weight = "bold",
                size = 20
            ),
            content = ft.Text(
                "전체시트의 면적데이터가 자동수정됩니다. 진행할까요?",
                font_family = self.font_text01,
                weight = "bold",
                size = 16
            ),
            actions = [
                ft.Row(
                    [
                        ft.FilledButton(
                            content = ft.Row(
                                [
                                    ft.Text("예",
                                            font_family = self.font_text01,
                                            weight = "bold",
                                            text_align = ft.TextAlign.CENTER)
                                ]
                            ),
                            style = ft.ButtonStyle(shape = ft.StadiumBorder()),
                            on_click = self.close_dlg_and_ready
                        ),
                        ft.FilledButton(
                            content = ft.Row(
                                [
                                    ft.Text("아니오",
                                            font_family = self.font_text01,
                                            weight = "bold",
                                            text_align = ft.TextAlign.CENTER)
                                ]
                            ),
                            style = ft.ButtonStyle(shape = ft.StadiumBorder()),
                            on_click = self.close_dlg
                        )
                    ],
                    alignment = ft.MainAxisAlignment.CENTER
                )
            ]
        )
        
    def close_dlg(self, e):
        self.dlg_modal.open = False
        self.page.update()
        
    def close_dlg_and_ready(self, e):
        self.dlg_modal.open = False
        print("Standard Sheets 수정준비!!")
        self.page.update()
        
    def area_modal_open_btn(self, e):
        self.selected = e.control.selected
        print(f"Area Modal Button Clicked! {self.selected} 번")
        self.page.dialog = self.dlg_modal
        self.dlg_modal.open = True
        self.page.update()
    
    def build(self):
        return ft.Column(
            expand = True,
            alignment = ft.MainAxisAlignment.CENTER,
            controls = [
                ft.Row(
                    [
                        self.area_modal_btn
                    ],
                    alignment = ft.MainAxisAlignment.END,
                    width = 1010
                ),
                self.s_tabs
            ]
        )

class TabMenu(ft.UserControl):
    def __init__(self, std_df_folder_name, area_df_name):
        super().__init__(**form_style["main"])
        
        self.font_text01 = list(font_style["main"].keys())[0]
        self.std_df_folder_name = std_df_folder_name
        
        self.std_tabs = StdTabMenu(df_folder_name = self.std_df_folder_name)
        self.paint_area_tabs = PaintAreaTab(df_name = area_df_name)
        self.keys = list(form_style["calc_unit_code"].keys())
        self.values = list(form_style["calc_unit_code"].values())
        self.code_ref = cr.code_ref_txt(self.keys, self.values)
        
        self.m_tabs = ft.Tabs(
            selected_index = 0,
            animation_duration = 300,
            scrollable = True,
            expand = True,
            tabs = [
                ft.Tab(
                    tab_content = ft.Row(
                        [
                            ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_SHARP),
                            ft.Text("Standard Sheet",
                                    font_family = self.font_text01,
                                    size = 15,
                                    weight = "bold")
                        ]
                    ),
                    content = self.std_tabs
                ),
                ft.Tab(
                    tab_content = ft.Row(
                        [
                            ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_SHARP),
                            ft.Text("Paint Area Sheet",
                                    font_family = self.font_text01,
                                    size = 15,
                                    weight = "bold")
                        ]
                    ),
                    content = self.paint_area_tabs
                ),
                ft.Tab(
                    tab_content = ft.Row(
                        [
                            ft.Icon(ft.icons.CALCULATE),
                            ft.Text("Code Ref",
                                    font_family = self.font_text01,
                                    size = 15,
                                    weight = "bold")
                        ]
                    ),
                    content = self.code_ref
                )
            ]
        )
    
    def build(self):
        return self.m_tabs

def main(page: ft.Page):
    page.title = "Paint Manufacturing Engineering"
    font = nd.font_path
    font_values = list(font.values())
    page.fonts = { "HDText" : f"{font_values[0]}" }
    page.window_width = 1100
    page.window_height = 800
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.appbar = ft.AppBar(
        leading = ft.Icon(ft.icons.EDIT_SQUARE,
                          color = ft.colors.WHITE,
                          size = 30),
        leading_width = 50,
        title = ft.Text("MH Editor",
                        size = 30,
                        weight = ft.FontWeight.BOLD,
                        color = ft.colors.WHITE,
                        font_family = "HDText" ),
        bgcolor = ft.colors.ON_SURFACE_VARIANT
    )
    
    df_dict = nd.files
    df_list = list(df_dict.values())
    std_df_folder_name = df_list[0]
    area_df_name = df_list[1]
    tab_menu = TabMenu(std_df_folder_name, area_df_name)
    
    page.add(
        ft.Column(
            expand = True,
            alignment = ft.MainAxisAlignment.CENTER,
            controls = [tab_menu]
        )
    )

if __name__ == "__main__":
    ft.app(target = main)

