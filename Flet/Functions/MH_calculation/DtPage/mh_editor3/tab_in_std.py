import flet as ft
from std_sht import StdSht
import pandas as pd
from dataframe import *
from time import sleep

def std_tab_menu(
    page,
    df_name,
    plant_name,
    process_name,
    car_model_name):
    
    df_sht_names_list = pd.ExcelFile(df_name).sheet_names    
    std_tables_list = []
    for sht_name in df_sht_names_list:
        std_df = pd.read_excel(df_name,
                               sheet_name = sht_name,
                               header = 1)
        std_df = std_df.iloc[:27,2:]
        std_df = std_df.fillna("")
        std_df = std_df[std_df.iloc[:,6] != ""]
        std_df.iloc[:,3] = std_df.iloc[:,3].apply(lambda x: round(x,3))
        std_df.iloc[:,5] = std_df.iloc[:,5].apply(lambda x: round(x))
        std_df.iloc[:,6] = std_df.iloc[:,6].apply(lambda x: round(x,1))
        std_datatable = ft.DataTable(columns = col_name(std_df),
                                     rows = rows(std_df))
        
        std_table = StdSht(
            datatable = std_datatable,
            plant_name = plant_name,
            process_name = process_name,
            car_model_name = car_model_name)
            
        std_tables_list.append(std_table)
        
    tab_menu_in_stdtable = ft.Tabs(
        selected_index = 0,
        animation_duration = 200,
        scrollable = True,
        expand = True,
        tabs = [
            ft.Tab(
                tab_content = ft.Row(
                    [
                        ft.Text(sht_name.upper(),
                                font_family = "HDText",
                                size = 12.5,
                                weight = "bold")
                    ]
                ),
                content = std_table
            ) for std_table, sht_name in zip(std_tables_list, df_sht_names_list)
        ]
    )
    
    def close_dlg(e):
        dlg_modal.open = False
        page.update()
        
    def close_dlg_and_ready(e):
        dlg_modal.open = False
        print("Standard Sheets 수정준비!!")
        page.update()
    
    dlg_modal = ft.AlertDialog(
        modal = True,
        title = ft.Text(
            "확인알림창",
            font_family = "HDText",
            weight = "bold",
            size = 20
        ),
        content = ft.Text(
            "전체시트의 면적데이터가 자동수정됩니다. 진행할까요?",
            font_family = "HDText",
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
                                        font_family = "HDText",
                                        weight = "bold",
                                        text_align = ft.TextAlign.CENTER)
                            ]
                        ),
                        style = ft.ButtonStyle(shape = ft.StadiumBorder()),
                        on_click = lambda e: close_dlg_and_ready(e)
                    ),
                    ft.FilledButton(
                        content = ft.Row(
                            [
                                ft.Text("아니오",
                                        font_family = "HDText",
                                        weight = "bold",
                                        text_align = ft.TextAlign.CENTER)
                            ]
                        ),
                        style = ft.ButtonStyle(shape = ft.StadiumBorder()),
                        on_click = lambda e: close_dlg(e)
                    )
                ],
                alignment = ft.MainAxisAlignment.CENTER
            )
        ]
    )
    
    def area_modal_open_btn(e):
        selected = e.control.selected
        print(f"Area Modal Button Clicked! {selected} 번")
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()
        
    area_modal_btn = ft.IconButton(
        selected = 0,
        style = ft.ButtonStyle(shape = ft.StadiumBorder()),
        content = ft.Row(
            [
               ft.Icon(ft.icons.SAVE),
               ft.Text("면적수정입력",
                       size = 15,
                       weight = "bold",
                       font_family = "HDText"
                       )
            ]
        ),
        on_click = lambda e: area_modal_open_btn(e)
    )
    
    return ft.Column(
        expand = True,
        alignment = ft.MainAxisAlignment.CENTER,
        controls = [
            ft.Row(
                [
                    area_modal_btn
                ],
                alignment = ft.MainAxisAlignment.END,
                width = 1008
            ),
            tab_menu_in_stdtable
        ]
    )
