import flet as ft
from flet import *
from dtpage import DtPage
import pandas as pd

def main(page: ft.Page):
    font_path = "<font path>"
    page.fonts = {
        "HDText" : f"{font_path}"
    }
    page.scroll = "always"
    page.title = "Paint Manufacturing Engineering"
    page.window_width = 1240
    page.window_height = 900
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
    
    def col_name(df: pd.DataFrame) -> list:
        return [
            ft.DataColumn(
                ft.Text(col,
                        color = ft.colors.BLACK,
                        weight = "bold",
                        text_align = ft.TextAlign.RIGHT,
                        font_family = "HDText"
                )
            ) for col in df.columns
        ]
    
    def rows(df: pd.DataFrame) -> list:
        rows = []
        for idx, row in df.iterrows():
            rows.append(
                ft.DataRow(
                    cells = [
                        ft.DataCell(
                            ft.Text(row[col],
                                    color = ft.colors.BLACK87,
                                    # weight = "bold",
                                    text_align = ft.TextAlign.RIGHT,
                                    font_family = "HDText"
                            )
                        ) for col in df.columns
                    ]
                )
            )
        return rows
    
    df = pd.read_excel("mh_part_area_sheet.xlsx")
    datatable = ft.DataTable(columns = col_name(df), rows = rows(df))
    
    pdt = DtPage(
        datatable = datatable,
        # table_title = "도장면적리스트",
    )
    pdt.datatable.border = ft.border.all(1,"gray")
    
    for i in pdt.datacolumns:
        i.label = ft.Row(
            [
                i.label,
                ft.Icon(name = "aaa")
            ]
        )
    page.add(pdt)
    
ft.app(target = main)
