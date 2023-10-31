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
    page.title = " "
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
    
    plant_names_dict = nd.plant_name
    plant_keys = list(plant_names_dict.keys())
    plant_name = plant_keys[2]
    
    process_names_dict = nd.process_name
    process_values = list(process_names_dict.values())
    process_name = process_values[0]
    
    car_model_dict = nd.car_model_name
    car_model_values = list(car_model_dict.values())
    car_model_name = car_model_values[0]
    
    df_names_dict = nd.files
    df_names_list = list(df_names_dict.values())
    std_df_name = df_names_list[0]
    area_df_name = df_names_list[1]
    
    page.add(
        tm.tab_menu(page = page,
                    std_df_name = std_df_name,
                    area_df_name = area_df_name,
                    plant_name = plant_name,
                    process_name = process_name,
                    car_model_name = car_model_name
                    )
    )

if __name__ == "__main__":
    ft.app(target = main)
