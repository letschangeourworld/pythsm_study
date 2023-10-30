import flet as ft
from std_sht import StdSht
from paint_area import PaintArea
import mh_calc as mc
import tab_in_std as tis

def tab_menu(page: page,
             df : df_dict,
             paint_area : area_datatable,
             plant : plant_name,
             process : process_name,
             car_model : car_model_name ):
    
    std_tabs = tis.std_tab_menu(page = page,
                                df = df_dict,
                                plant = plant_name,
                                process = process_name,
                                car_model = car_model_name)
    
    paint_table = PaintArea(
        datatable = area_datatable,
        car_model_name = car_model_name)
    
    menu = ft.Tabs(
        selected_index = 0,
        animation_duration = 300,
        scrollable = True,
        expand = True,
        # on_change = tabs_changed,
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
                content = mc.mh_calc(page))
        ]
    )
    return ft.Column(
        expand = True,
        alignment = ft.MainAxisAlignment.CENTER,
        controls = [menu]
    )
