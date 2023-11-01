import flet as ft
from paint_area import PaintArea
import mh_calc as mc
import tab_in_std as tis

def tab_menu(page,
             std_df_name,
             area_df_name,
             plant_name,
             process_name,
             car_model_name ):
    
    std_tabs = tis.std_tab_menu(
        page = page,
        df_name = std_df_name,
        plant_name = plant_name,
        process_name = process_name,
        car_model_name = car_model_name)
    
    paint_table = PaintArea(
        df_name = area_df_name,
        car_model_name = car_model_name)
        
    mh_calc = mc.mh_calc(page)
    
    top_menu = ft.Tabs(
        selected_index = 0,
        animation_duration = 300,
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
                content = std_tabs
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
                content = mh_calc
            )
        ]
    )
    
    return ft.Column(
        expand = True,
        alignment = ft.MainAxisAlignment.CENTER,
        controls = [top_menu]
    )
