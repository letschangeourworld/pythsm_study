import flet as ft
from std_sht import StdSht
from paint_area import PaintArea
import mh_calc as mc
import pandas as pd
from dataframe import *

def std_tab_menu(
    page,
    df_dict,
    plant_name,
    process_name,
    car_model_name):
    
    # df_name : The name or path of excel files made in a dictionary
    df_names_list = list(df_dict.values())
    df_sht_names_list = pd.ExcelFile(df_names_list[0]).sheet_names
    
    std_tables_list = []
    for sn in df_sht_names_list:
        std_df = pd.read_excel(df_names_list[0],
                               sheet_name = df_sht_names_list[sn],
                               header = 1)
        std_df = std_df.iloc[:26,2:]
        std_df = std_df.fillna("")
        std_df = std_df[std_df.iloc[:,6] != ""]
        std_datatable = ft.DataTable(columns = col_name(std_df),
                                     rows = rows(std_df))
        std_table = StdSht(
            datatable = std_datatable,
            plant_name= plant_name,
            process_name = process_name,
            car_model_name = car_model_name)
            
        std_tables_list.append(std_table)
        
    tab_menu_in_stdtable = ft.Tabs(
        selected_index = 0,
        scrollable = True,
        expand = True,
        tabs = [
            ft.Tab(
                tab_content = ft.Row(
                    [
                        ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_SHARP),
                        ft.Text(sht_name,
                                font_family = "HDText",
                                size = 15,
                                weight = "bold")
                    ]
                ),
                content = std_table
            ) for std_table, sht_name in zip(std_tables_list, df_sht_names_list)
        ]
    )
    return ft.Column(
        expand = True,
        alignment = ft.MainAxisAlignment.CENTER,
        controls = [tab_menu_in_stdtable]
    )
