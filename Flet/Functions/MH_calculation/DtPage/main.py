import flet as ft
from flet import *
from dtpage import DtPage
from simpledt import DataFrame
import simpledt
import pandas as pd

def main(page: ft.Page):
    font_path = "<font path>"
    page.fonts = {
        "HDText" : f"{font_path}"
    }
    page.scroll = "auto"
    page.title = ""
    page.window_width = 1100
    page.window_height = 860
    page.theme_mode = ft.ThemeMode.LIGHT
    page.appbar = ft.AppBar(
        leading = ft.Icon(
            ft.icons.EDIT_SQUARE,
            color = ft.colors.WHITE,
            size = 30),
        leading_width = 50,
        title = ft.Text(
            "MH Editor",
            size = 30,
            weight = ft.FontWeight.BOLD,
            color = ft.colors.WHITE,
            font_family = "HDText"
        ),
        center_title = False,
        bgcolor = ft.colors.ON_SURFACE_VARIANT
    )
    
    # df = pd.read_excel("mh_part_area_sheet.xlsx")
    # simpledt_df = DataFrame(df)
    # simpledt_dt = simpledt_df.datatable
    csv = simpledt.CSVDataTable("./day.csv")
    pdt = DtPage(
        datatable = csv.datatable,
        table_title = "",        
    )
    pdt.datatable.border = ft.border.all(1,"gray")
    
    for i in pdt.datarows:
        rownum = i.cells[0].content.value
        if int(rownum) % 2 == 0:
            i.color = "white"
            
    for i in pdt.datacolumns:
        i.label = ft.Row(
            [
                i.label,
                ft.Icon(name = "aaa")
            ]
        )
    page.add(pdt)
    
ft.app(target = main)
