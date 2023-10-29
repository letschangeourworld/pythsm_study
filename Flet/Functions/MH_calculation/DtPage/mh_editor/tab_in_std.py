import flet as ft
from std_sht import StdSht
from paint_area import PaintArea
import mh_calc as mc
import pandas as pd
from dataframe import *

def std_tab_menu(
    page,
    df_name,
    plant_name,
    process_name,
    car_model_name):
    
    
    df_name_list = list(df_name.values())
    df_sht_name_list = pd.ExcelFile(df_name_list[0]).sheet_names
    
    std_table_list = []
    for i, tn in enumerate(df_sht_name_list):
        df_std_sht = pd.read_excel(df_name_list[0],
                                   sheet_name = df_sht_name_list[tn],
                                   header = 1)
        df_std_sht = df_std_sht.iloc[:26,2:]
        df_std_sht = df_std_sht.fillna("")
        df_std_sht = df_std_sht[df_std_sht.iloc[:,6] != ""]
        std_datatable = ft.DataTable(columns = col_name(df_std_sht),
                                     rows = rows(df_std_sht))
        std_table = StdSht(
            datatable = std_datatable,
            plant_name= plant_name,
            process_name = process_name,
            car_model_name = car_model_name)
            
        std_table_list.append(std_table)
        
    tab_menu_in_stdsht = ft.Tabs(
        selected_index = 0,
        scrollable = True,
        expand = True,
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
            )
        ]
    )
    return ft.Column(
        expand = True,
        alignment = ft.MainAxisAlignment.CENTER,
        controls = [tab_menu_in_stdsht]
    )
