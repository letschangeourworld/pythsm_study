import flet as ft
from paint_area import PaintArea
import mh_calc as mc
import tab_in_std as tis
import name_data as nd
from code_ref import code_ref_txt

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
        
    data = nd.code_ref_txt
    code_ref_keys = list(data.keys())
    code_ref_values = list(data.values())
    code_ref = code_ref_txt(code_ref_keys, code_ref_vales)
    
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
                        ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_SHARP),
                        ft.Text("Code Ref",
                                font_family = "HDText",
                                size = 15,
                                weight = "bold")
                    ]
                ),
                content = code_ref
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
