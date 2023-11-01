import flet as ft
import pandas as pd

def col_name(df: pd.DataFrame) -> list:
    return [
        ft.DataColumn(
            ft.Text(col.upper(),
                    color = ft.colors.BLACK,
                    weight = "bold",
                    text_align = ft.TextAlign.CENTER,
                    font_family = "HDText"
            )
        ) for col in df.columns
    ]

def rows(df: pd.DataFrame) -> list:
    rows = []
    for row in df.itertuples():
        rows.append(
            ft.DataRow(
                cells = [
                    ft.DataCell(
                        ft.Text(row[col_no],
                                color = ft.colors.BLACK87,
                                weight = "bold",
                                text_align = ft.TextAlign.RIGHT,
                                font_family = "HDText"
                        )
                    ) for col_no in range(1,len(df.columns)+1)
                ]
            )
        )
    return rows