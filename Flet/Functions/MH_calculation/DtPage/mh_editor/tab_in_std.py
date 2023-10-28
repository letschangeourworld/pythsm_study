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
    
    tabs = pd.ExcelFile(df_name_values).sheet_names
    
    std_table = StdSht(
        datatable = std_datatable,
        plant_name= plant_name,
        process_name = process_name,
        car_model_name = car_model_name)
        
    tab_menu_in_stdsht = ft.Tabs(
        selected_index = 0,
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
           
        ]
    )
    return ft.Column(
        expand = True,
        alignment = ft.MainAxisAlignment.CENTER,
        controls = [tab_menu_in_stdsht]
    )
