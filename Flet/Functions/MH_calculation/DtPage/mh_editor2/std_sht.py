import flet as ft
# import tab_in_std as tis

class StdSht(ft.UserControl):
    def __init__(self,
                 datatable: ft.DataTable,
                 table_title: str = "Instruction Table",
                 process_name: str = "",
                 plant_name: str = "",
                 car_model_name: str = ""):
        super().__init__()
        self.dt = datatable
        self.title = table_title
        self.process_name = process_name
        self.plant_name = plant_name
        self.car_name = car_model_name
        self.pdt = ft.DataTable(
            width= 1005,
            border = ft.border.all(0, color = ft.colors.BLACK45),
            border_radius = 6,
            heading_row_color = ft.colors.BLACK26,
            heading_row_height = 40,
            column_spacing = 1,
            columns = self.dt.columns,
            rows = self.dt.rows
        )
    
    def build(self):
        return ft.Column(
            [
                ft.Text(""),
                ft.Card(
                    ft.Container(
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Row(
                                            [
                                                ft.Text(self.title,
                                                color = ft.colors.BLACK,
                                                weight = "bold",
                                                size = 20,
                                                text_align = ft.TextAlign.CENTER,
                                                style = ft.TextThemeStyle.HEADLINE_MEDIUM,
                                                font_family = "HDText"),
                                            ],
                                            alignment = ft.MainAxisAlignment.START
                                        ),
                                        ft.Row(
                                            [
                                                ft.Text(f"| Plant : {self.plant_name} ",
                                                color = ft.colors.BLACK,
                                                weight = "bold",
                                                size = 15,
                                                text_align = ft.TextAlign.RIGHT,
                                                font_family = "HDText"
                                                ),
                                        ft.Text(f"| Process : {self.process_name} ",
                                                color = ft.colors.BLACK,
                                                weight = "bold",
                                                size = 15,
                                                text_align = ft.TextAlign.RIGHT,
                                                font_family = "HDText"
                                                ),
                                        ft.Text(f"| Car Model : {self.car_name}  ",
                                                color = ft.colors.BLACK,
                                                weight = "bold",
                                                size = 15,
                                                text_align = ft.TextAlign.RIGHT,
                                                font_family = "HDText"
                                                ),
                                            ],
                                            alignment = ft.MainAxisAlignment.END
                                        )
                                    ],
                                    alignment = ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                self.pdt,
                            ],
                        ),
                        padding = 25,
                        
                    ),
                    elevation = 5,
                )
            ],
            scroll= ft.ScrollMode.AUTO
        )
