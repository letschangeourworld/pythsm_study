import flet as ft
from std_sht import StdSht
from paint_area import PaintArea
import mh_calc as mc
import pandas as pd
import name_data as nd

df_name = nd.files
# df_name_keys = list(df_name.keys())
df_name_values = list(df_name.values())

def std_tab_menu(page,
                 std_datatable,
                 plant_name,
                 process_name,
                 car_model_name,
                 df):
    # def tabs_changed(e):
    #     print(f"Tabs changed to {e.control.selected_index}")
    
    tabs = pd.ExcelFile(df_name_values).sheet_names
    
    std_table = StdSht(
        datatable = std_datatable,
        plant_name= plant_name,
        process_name = process_name,
        car_model_name = car_model_name)
        
    menu = ft.Tabs(
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
                content = std_table
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
                content = paint_table
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
                content = mc.mh_calc(page))
        ]
    )
    return ft.Column(
        expand = True,
        alignment = ft.MainAxisAlignment.CENTER,
        controls = [menu]
    )
