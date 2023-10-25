import flet as ft
from std_sht import StdSht
from paint_area import PaintArea
from mh_calc2 import MhCalc

class TabMenu(ft.UserControl):
    def __init__(self,
                 std_datatable: ft.DataTable,
                 area_datatable: ft.DataTable,
                 plant_name: str = "",
                 process_name: str = "",
                 car_model_name: str = "",
                 data: dict = {} ):
        
        super().__init__()
        self.std_datatable = std_datatable
        self.area_datatable = area_datatable
        self.plant_name = plant_name
        self.process_name = process_name
        self.car_model_name = car_model_name
        self.data = data
    
        self.std_table = StdSht(
            datatable = self.std_datatable,
            plant_name = self.plant_name,
            process_name = self.process_name,
            car_model_name = self.car_model_name)
        
        self.paint_table = PaintArea(
            datatable = self.area_datatable,
            car_model_name = self.car_model_name)
        
        self.mh_calc = MhCalc(data = self.data)
        
    def build(self):
        return ft.Column(
            expand = True,
            alignment = ft.MainAxisAlignment.CENTER,
            controls = [
                ft.Tabs(
                    selected_index = 0,
                    animation_duration = 300,
                    scrollable = True,
                    expand = True,
                    # on_change = tabs_changed,
                    tabs = [
                        ft.Tab(
                            tab_content = ft.Row(
                                [
                                    ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_SHARP),
                                    ft.Text("Standard Sheet",
                                            font_family = "HDText",
                                            size = 15,
                                            weight = "bold")
                                ]
                            ),
                            content = self.std_table
                        ),
                        ft.Tab(
                            tab_content = ft.Row(
                                [
                                    ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_SHARP),
                                    ft.Text("Paint Area Sheet",
                                            font_family = "HDText",
                                            size = 15,
                                            weight = "bold")
                                ]
                            ),
                            content = self.paint_table
                        ),
                        ft.Tab(
                            tab_content = ft.Row(
                                [
                                    ft.Icon(ft.icons.CALCULATE),
                                    ft.Text("MH Calculation",
                                            font_family = "HDText",
                                            size = 15,
                                            weight = "bold")
                                ]
                            ),
                            content = self.mh_calc
                            )
                    ]
                )
            ]
        )
