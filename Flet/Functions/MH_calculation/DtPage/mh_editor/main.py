import flet as ft
import tab_menu as tm
import pandas as pd
import name_data as nd

def main(page: ft.Page):
    font = nd.font_path
    font_values = list(font.values())
    page.fonts = {
        "HDText" : f"{font_values[0]}"
    }
    page.title = "Paint Manufacturing Engineering"
    page.window_width = 1100
    page.window_height = 1100
    page.padding = 20
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
    
    plant_name = nd.plant_name
    plant_keys = list(plant_name.keys())
    process_name = nd.process_name
    process_values = list(process_name.values())
    car_model_name = nd.car_model_name
    car_values = list(car_model_name.values())
    
    df_dict = nd.files
    df_names_list = list(df_dict.values())
    std_df_name = df_name_list[0]
    
    df_paint_area = pd.read_excel(df_name_list[1])
    df_paint_area = df_paint_area.fillna("")
    area_datatable = ft.DataTable(columns = col_name(df_paint_area),
                                  rows = rows(df_paint_area)
                                 )
    page.add(
        tm.tab_menu(page = page,
                    df_name = std_df_name,
                    area_datatable = area_datatable,
                    plant_name = plant_keys[2],
                    process_name = process_values[0],
                    car_model_name = car_values[0]
                    )
    )

if __name__ == "__main__":
    ft.app(target = main)
