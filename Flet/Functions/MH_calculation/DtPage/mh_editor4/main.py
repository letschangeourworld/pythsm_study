import flet as ft
import os
import csv
import pandas as pd
import name_data as nd
import code_ref as cr

# font
font_style: dict = {
    "main": {
        "HDText" : ""
    }
}

# Data Table styling dictionary
data_table_style: dict = {
    "main": {
        "expand": True,
        # "bgcolor": "#fdfdfe",
    },
    "data_table": {
        "heading_row_color": "#e3e4ea",
        "expand": True,
        "heading_row_height": 30,
        "data_row_max_height": 40,
    }
}

# To form class styling dictionary
form_style: dict = {
    "main": {
        "expand": True,
        # "bgcolor": "#fdfdfe",
        # "padding": ft.padding.only(left = 35, right = 35),
    },
    "field_cond": {
        "height": 38,
        "border_color": "#aeaeb3",
        "focused_border_color": "black",
        "border_radius": 5,
        "cursor_height": 16,
        "cursor_color": "black",
        "content_padding": 10,
        "border_width": 1.5,
        "text_size": 13,
    },
    "dropdown_cond": {
        "height": 38,
        "border_color": "#aeaeb3",
        "focused_border_color": "black",
        "border_radius": 5,
        "content_padding": 10,
        "border_width": 1.5,
        "text_size": 13,
    },
    "dropdown_options": {
        "hood_ext" : 0,
        "roof" : 1,
        "trunk" : 2,
        "fender" : 3,
        "frt_dr_ext" : 4,
        "frt_dr_frame" : 5,
        "rr_dr_ext" : 6,
        "rr_dr_frame" : 7,
        "s_otr" : 8,
        "trunk_ext" : 9,
        "f_lid_otr" : 10,
        "hood_inr" : 11,
        "hood_hinge" : 12,
        "cowl" : 13,
        "engine_rm" : 14,
        "frt_dr_inr" : 15,
        "frt_dr_inr_frame" : 16,
        "rr_dr_inr" : 17,
        "rr_dr_inr_frame" : 18,
        "s_otr_opn" : 19,
        "rr_extn" : 20,
        "trunk_int" : 21,
        "trunk_hinge" : 22,
        "f_lid_inr" : 23,
    },
    "calc_unit_code" : {
        "hood_ext" : 0,
        "roof" : 1,
        "trunk" : 2,
        "fender" : 3,
        "frt_dr_ext" : 4,
        "frt_dr_frame" : 5,
        "rr_dr_ext" : 6,
        "rr_dr_frame" : 7,
        "s_otr" : 8,
        "trunk_ext" : 9,
        "f_lid_otr" : 10,
        "hood_inr" : 11,
        "hood_hinge" : 12,
        "cowl" : 13,
        "engine_rm" : 14,
        "frt_dr_inr" : 15,
        "frt_dr_inr_frame" : 16,
        "rr_dr_inr" : 17,
        "rr_dr_inr_frame" : 18,
        "s_otr_opn" : 19,
        "rr_extn" : 20,
        "trunk_int" : 21,
        "trunk_hinge" : 22,
        "f_lid_inr" : 23,
        
        "rr_extn(20) + trunk_int(21)" : 24,
        "hood_ext(0) + roof(1) + trunk(2)" : 25,
        "fender(3) + frt_dr_ext(4) + rr_dr_ext(6) + s_otr(8)" : 26,
        "s_otr_opn(19) + frt_dr_inr(15) + rr_dr_inr(17) " : 27,
        "hood_inr(11) + (24)" : 28,
        "{ (25) + (26) + (27) } * 0.5" : 29,
        "{ (25) + (26) + (27) + (28) } * 0.5" : 30,
        "{ (26) + (27) + (24) } * 0.5" : 31,
        "(25) * 0.5" : 32,
        "(25) + (26) + (27) + (28)" : 33,
        "면적과 관련 없음" : 100
    }
}

# [1] Data Table Class
class DataTable(ft.UserControl):
    def __init__(self, df: pd.DataFrame):
        super().__init__(**data_table_style["main"])
        
        self.font_text01 = list(font_style["main"].keys())[0]
        self.df = df
        self.table = ft.DataTable(**data_table_style["data_table"])
        self.headers: list = self.df.columns
        
        self.table.columns = [
            ft.DataColumn(
                ft.Text(
                    title.upper(),
                    weight = "w600",
                    size = 13
                )
            ) for title in self.headers
        ]
        self.table.rows = []
        for row in self.df.itertuples():
            self.table.rows.append(
                ft.DataRow(
                    [
                        ft.DataCell(
                            ft.Text(
                                row[col_no],
                                color = ft.colors.BLACK87,
                                text_align = ft.TextAlign.RIGHT,
                                weight = "bold",
                                font_family = self.font_text01,
                            )
                        ) for col_no in range(1,len(self.df.columns)+1)
                    ]
                )
            )
    
    def build(self):
        return self.table

class VoidDataTable(ft.UserControl):
    def __init__(self):
        super().__init__(**data_table_style["main"])
        
        self.table = ft.DataTable(**data_table_style["data_table"])
        headers: list = [
            "Car Model Name",
            "Part Name",
            "Part Code",
            "Area LH",
            "Area RH",
            "Area SUM"
        ]
        
        self.table.columns = [
            ft.DataColumn(
                ft.Text(
                    title.upper(),
                    weight = "w600",
                    size = 13                    
                )
            ) for title in headers
        ]
    
    def build(self):
        return self.table

class StdSht(ft.UserControl):
    def __init__(self,
                 df,
                 table_title: str = "Instruction Table",
                 process_name: str = "",
                 plant_name: str = "",
                 car_model_name: str = ""):
        super().__init__(font_style["main"])
        
        self.font_text01 = list(font_style["main"].keys())[0]
        self.df = df
        self.pdt = DataTable(df = self.df)
        self.title = table_title
        self.process_name = process_name
        self.plant_name = plant_name
        self.car_name = car_model_name
        
    def build(self):
        return self.pdt
        
class PaintArea(ft.UserControl):
    def __init__(self,
                 df,
                 table_title: str = "Unit Part Area DataTable",
                 plant_name: str = "",
                 car_model_name: str = ""
                 ):
        super().__init__(font_style["main"])
        
        self.font_text01 = list(font_style["main"].keys())[0]
        self.df = df
        self.pdt = DataTable(df = self.df)
        self.title = table_title
        self.plant_name = plant_name
        self.car_name = car_model_name
    
    def build(self):
        return self.pdt
        
class InputAreaForm(ft.UserControl):
    def __init__(self, table: ft.DataTable) -> None:
        super().__init__(**form_style["main"])
        
        self.table = table
        
        # to pass and convert the dropdown value (part_name) to textfield value (part_code)
        def dropdown_changed(e) -> None:
            self.part_code.value = form_style["dropdown_options"][self.part_name.value]
            self.part_code.update()
        
        def lh_value_added(e) -> None:
            if self.area_lh.value != "":
                if self.area_rh.value != "":
                    lh = float(self.area_lh.value)
                    rh = float(self.area_rh.value)
                    self.area_sum.value = str(round((lh+rh),3))
                    self.area_sum.update()
                else:
                    lh = float(self.area_lh.value)
                    rh = 0
                    self.area_sum.value = str(round((lh+rh),3))
                    self.area_sum.update()
        
        def rh_value_added(e) -> None:
            if self.area_rh.value != "":
                if self.area_lh.value != "":
                    lh = float(self.area_lh.value)
                    rh = float(self.area_rh.value)
                    self.area_sum.value = str(round((lh+rh),3))
                    self.area_sum.update()
                else:
                    lh = 0
                    rh = float(self.area_lh.value)
                    self.area_sum.value = str(round((lh+rh),3))
                    self.area_sum.update()
                    
        def vehicle_code_upper(e) -> None:
            if self.vehicle_code != "":
                self.vehicle_code.value = self.vehicle_code.value.upper()
                self.vehicle_code.update()
        
        # create input fields and dropdown
        self.vehicle_code = ft.TextField(**form_style["field_cond"],
                                         on_change = vehicle_code_upper)
        option_text_list = list(form_style["dropdown_options"].keys())
        self.options = [ft.dropdown.Option(option_text) for option_text in option_text_list]
        self.part_name = ft.Dropdown(**form_style["dropdown_cond"],
                                     on_change = dropdown_changed,
                                     options = self.options)
        self.part_code = ft.TextField(**form_style["field_cond"])
        self.area_lh = ft.TextField(**form_style["field_cond"], on_change = lh_value_added)
        self.area_rh = ft.TextField(**form_style["field_cond"], on_change = rh_value_added)
        self.area_sum = ft.TextField(**form_style["field_cond"])
        
        # lists for logic and or loops
        self.data: list = [
            "Car Model Name",
            "Part Name",
            "Part Code",
            "Area LH",
            "Area RH",
            "Area SUM"
        ]
        self.fields: list = [
            self.vehicle_code,
            self.part_name,
            self.part_code,
            self.area_lh,
            self.area_rh,
            self.area_sum
        ]
        
        # list comprehension to create the input fields + titles
        self.items: list = [
            ft.Column(
                expand = True,
                spacing = 10,
                controls = [
                    ft.Text(title,
                            size = 13,
                            weight = "w500" ),
                    self.fields[idx]
                ]
            ) for idx, title in enumerate(self.data)
        ]
        
        # a save button to push the data to the UI + CSV file later
        self.upload = ft.ElevatedButton(
            text = "ADD",
            color = "white",
            bgcolor = "blue600",
            height = 35,
            style = ft.ButtonStyle(
                shape = {"": ft.RoundedRectangleBorder(radius = 7)}
            ),
            elevation = 5,
            on_click = self.upload_data,
        )
        
        # to save to csv file
        self.to_csv = ft.ElevatedButton(
            text = "SAVE as CSV file",
            color = "white",
            bgcolor = "blue600",
            height = 35,
            style = ft.ButtonStyle(
                shape = {"": ft.RoundedRectangleBorder(radius = 7)}
            ),
            elevation = 5,
            on_click = self.save_to_csv
        )
        
        # to delete the specific data in a row
        self.remove = ft.ElevatedButton(
            text = "REMOVE",
            color = "white",
            bgcolor = "blue600",
            height = 35,
            style = ft.ButtonStyle(
                shape = {"": ft.RoundedRectangleBorder(radius = 7)}
            ),
            elevation = 5,
            on_click = self.remove_data,
        )
        
    # self.content is ft.Container.content property, since this inherits from ft.Container
    def build(self):
        return ft.Column(
            expand = True,
            controls = [
                ft.Column(
                    alignment= ft.MainAxisAlignment.START,
                    expand = True,
                    controls = [
                        ft.Divider(
                            height = 20,
                            color = "transparent"),
                        ft.Text(
                            "Area Data Upload Sheet",
                            size = 25,
                            weight = "w800"),
                        ft.Divider(
                            height = 20,
                            thickness = 5),
                        ft.Row(
                            width = 1050,
                            spacing = 20,
                            expand = True,
                            controls = self.items
                        ),
                        # ft.Divider(
                        #     height = 10,
                        #     color = "transparent"),
                        ft.Row(
                            width = 1050,
                            alignment = "end",
                            expand = True,
                            controls = [
                                self.upload,
                                self.remove,
                                self.to_csv
                            ]
                        )
                    ]
                ),
                ft.Row(
                    width = 1050,
                    expand =  True,
                    controls = [self.table]
                )
            ]
        )
    
    def create_data_row(self, values: list):
        data = ft.DataRow(
            cells = [
                ft.DataCell(ft.Text(values[0], size = 13, weight = "600")),
                ft.DataCell(ft.Text(values[1], size = 13, weight = "600" )),
                ft.DataCell(ft.Text(values[2], size = 13, weight = "600" )),
                ft.DataCell(ft.Text(values[3], size = 13, weight = "600" )),
                ft.DataCell(ft.Text(values[4], size = 13, weight = "600" )),
                ft.DataCell(ft.Text(values[5], size = 13, weight = "600" )),
            ]
        )
        return data
    
    def update_data_table(self, data: ft.DataRow):
        # To access to the dt table
        self.table.rows.append(data)
        self.table.update()
    
    def upload_data(self, e) -> None:
        values: list = [
            self.vehicle_code.value,
            self.part_name.value,
            self.part_code.value,
            self.area_lh.value,
            self.area_rh.value,
            self.area_sum.value
        ]
        # check all fields first
        if all(values):
            # first, creat the data row and return it
            data = self.create_data_row(values)
            # to update the data table (to pass the instance of it)
            self.update_data_table(data)
    
    def update_removed_table(self, table: ft.DataTable) -> None:
        if self.table.rows:
            self.table.rows.pop()
            self.table.update()
    
    def remove_data(self, e) -> None:
        self.update_removed_table(self.table)
        
    def save_to_csv(self, e) -> None:
        self.check_if_csv_exists()
    
    def write_data_to_csv(self) -> None:
        # We need a nested loop to gather the data from the data table,
        # then write it to the file
        csv_rows: list = []
        
        # to iterate over the rows within the table
        for row in self.table.rows[:]:
            # create a temporary list because we need a nested list
            temp_list: list = []
            
            # iterate over the list of row (row = list)
            for control in row.cells[:]:
                temp_list.append(control.content.value)
                
            csv_rows.append(temp_list)
            
        # write the rows to the csv file
        with open("area_data.csv", "w") as file:
            csvwriter = csv.writer(file)
            
            # Note : the difference between row and rows in csvwriter
            csvwriter.writerow(
                ["Car Model Name",
                 "Part Code",
                 "Part Name",
                 "Area LH",
                 "Area RH",
                 "Area SUM"
                ]
            )
            csvwriter.writerows(csv_rows)
    
    def check_if_csv_exists(self) -> None:
        # to check and/or create csv file
        # to check to see if the file name is in the root/current directory
        if "area_data.csv" not in os.listdir("."):
            # if it's not, create the file
            with open("area_data.csv", "a"):
                pass
        
        # if the file is already there, push the data to it
        else:
            self.write_data_to_csv()

class PaintAreaTab(ft.UserControl):
    def __init__(self, df_name):
        super().__init__(font_style["main"])
        
        self.font_text01 = list(font_style["main"].keys())[0]
        self.df_name = df_name
        
        self.df_sht_names_list = pd.ExcelFile(self.df_name).sheet_names
        self.paint_area_df = pd.read_excel(self.df_name,
                                           sheet_name = self.df_sht_names_list[0],
                                           header = 0)
        self.paint_area_df = self.paint_area_df.fillna("")
        
        self.paint_area_table = PaintArea(df = self.paint_area_df)
        self.paint_area_tables_list = []
        self.paint_area_tables_list.append(self.paint_area_table)
        
        dataTable = VoidDataTable()
        areaInputForm = InputAreaForm(table = dataTable.table)
        self.paint_area_tables_list.append(areaInputForm)
        
        self.df_sht_names_list.append("Area_Input")
        
        self.p_tabs = ft.Tabs(
            selected_index = 0,
            animation_duration = 200,
            scrollable = True,
            expand = True,
            tabs = [
                ft.Tab(
                    tab_content = ft.Row(
                        [
                            ft.Text(sht_name.upper(),
                                    font_family = self.font_text01,
                                    size = 12.5,
                                    weight = "bold")
                        ]
                    ),
                    content = p_area_table
                ) for sht_name, p_area_table in zip(self.df_sht_names_list,
                                                    self.paint_area_tables_list)
            ]
        )
        
    def build(self):
        return ft.Column(
            expand = True,
            alignment = ft.MainAxisAlignment.CENTER,
            controls = [self.p_tabs]
        )

class StdTabMenu(ft.UserControl):
    def __init__(self, df_name) -> None:
        super().__init__(font_style["main"])
        
        self.font_text01 = list(font_style["main"].keys())[0]
        self.df_name = df_name
        self.df_sht_names_list = pd.ExcelFile(self.df_name).sheet_names    
        self.std_tables_list = []
        for sht_name in self.df_sht_names_list:
            self.std_df = pd.read_excel(self.df_name,
                                        sheet_name = sht_name,
                                        header = 1)
            self.std_df = self.std_df.iloc[:27,2:]
            self.std_df = self.std_df.fillna("")
            self.std_df = self.std_df[self.std_df.iloc[:,6] != ""]
            self.std_df.iloc[:,3] = self.std_df.iloc[:,3].apply(lambda x: round(x,3))
            self.std_df.iloc[:,5] = self.std_df.iloc[:,5].apply(lambda x: round(x))
            self.std_df.iloc[:,6] = self.std_df.iloc[:,6].apply(lambda x: round(x,1))
            
            self.std_table = StdSht(df = self.std_df)
            self.std_tables_list.append(self.std_table)
            
        self.s_tabs = ft.Tabs(
            selected_index = 0,
            animation_duration = 200,
            scrollable = True,
            expand = True,
            tabs = [
                ft.Tab(
                    tab_content = ft.Row(
                        [
                            ft.Text(sht_name.upper(),
                                    font_family = self.font_text01,
                                    size = 12.5,
                                    weight = "bold")
                        ]
                    ),
                    content = std_sht
                ) for std_sht, sht_name in zip(self.std_tables_list, self.df_sht_names_list)
            ]
        )
        
        self.area_modal_btn = ft.IconButton(
            selected = 0,
            style = ft.ButtonStyle(shape = ft.StadiumBorder()),
            content = ft.Row(
                [
                ft.Icon(ft.icons.SAVE),
                ft.Text("면적수정입력",
                        size = 15,
                        weight = "bold",
                        font_family = self.font_text01,
                        text_align = ft.TextAlign.RIGHT
                        )
                ],
                alignment = ft.MainAxisAlignment.END
            ),
            on_click = self.area_modal_open_btn
        )
        
        self.dlg_modal = ft.AlertDialog(
            modal = True,
            title = ft.Text(
                "확인알림창",
                font_family = self.font_text01,
                weight = "bold",
                size = 20
            ),
            content = ft.Text(
                "전체시트의 면적데이터가 자동수정됩니다. 진행할까요?",
                font_family = self.font_text01,
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
                                            font_family = self.font_text01,
                                            weight = "bold",
                                            text_align = ft.TextAlign.CENTER)
                                ]
                            ),
                            style = ft.ButtonStyle(shape = ft.StadiumBorder()),
                            on_click = self.close_dlg_and_ready
                        ),
                        ft.FilledButton(
                            content = ft.Row(
                                [
                                    ft.Text("아니오",
                                            font_family = self.font_text01,
                                            weight = "bold",
                                            text_align = ft.TextAlign.CENTER)
                                ]
                            ),
                            style = ft.ButtonStyle(shape = ft.StadiumBorder()),
                            on_click = self.close_dlg
                        )
                    ],
                    alignment = ft.MainAxisAlignment.CENTER
                )
            ]
        )
        
    def close_dlg(self, e):
        self.dlg_modal.open = False
        self.page.update()
        
    def close_dlg_and_ready(self, e):
        self.dlg_modal.open = False
        print("Standard Sheets 수정준비!!")
        self.page.update()
        
    def area_modal_open_btn(self, e):
        self.selected = e.control.selected
        print(f"Area Modal Button Clicked! {self.selected} 번")
        self.page.dialog = self.dlg_modal
        self.dlg_modal.open = True
        self.page.update()
    
    def build(self):
        return ft.Column(
            expand = True,
            alignment = ft.MainAxisAlignment.CENTER,
            controls = [
                ft.Row(
                    [
                        self.area_modal_btn
                    ],
                    alignment = ft.MainAxisAlignment.END,
                    width = 1010
                ),
                self.s_tabs
            ]
        )

class TabMenu(ft.UserControl):
    def __init__(self, std_df_name, area_df_name):
        super().__init__(**form_style["main"])
        
        self.font_text01 = list(font_style["main"].keys())[0]
        self.std_df_name = std_df_name
        
        self.std_tabs = StdTabMenu(df_name = std_df_name)
        self.paint_area_tabs = PaintAreaTab(df_name = area_df_name)
        self.keys = list(form_style["calc_unit_code"].keys())
        self.values = list(form_style["calc_unit_code"].values())
        self.code_ref = cr.code_ref_txt(self.keys, self.values)
        
        self.m_tabs = ft.Tabs(
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
                                    font_family = self.font_text01,
                                    size = 15,
                                    weight = "bold")
                        ]
                    ),
                    content = self.std_tabs
                ),
                ft.Tab(
                    tab_content = ft.Row(
                        [
                            ft.Icon(ft.icons.DRIVE_FILE_RENAME_OUTLINE_SHARP),
                            ft.Text("Paint Area Sheet",
                                    font_family = self.font_text01,
                                    size = 15,
                                    weight = "bold")
                        ]
                    ),
                    content = self.paint_area_tabs
                ),
                ft.Tab(
                    tab_content = ft.Row(
                        [
                            ft.Icon(ft.icons.CALCULATE),
                            ft.Text("Code Ref",
                                    font_family = self.font_text01,
                                    size = 15,
                                    weight = "bold")
                        ]
                    ),
                    content = self.code_ref
                )
            ]
        )
    
    def build(self):
        return ft.Column(
            expand = True,
            alignment = ft.MainAxisAlignment.CENTER,
            controls = [
                self.m_tabs
            ]
        )

def main(page: ft.Page):
    page.title = ""
    font = nd.font_path
    font_values = list(font.values())
    page.fonts = { "HDText" : f"{font_values[0]}" }
    page.window_width = 1100
    page.window_height = 1000
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.appbar = ft.AppBar(
        leading = ft.Icon(ft.icons.EDIT_SQUARE,
                          color = ft.colors.WHITE,
                          size = 30),
        leading_width = 50,
        title = ft.Text("MH Editor",
                        size = 30,
                        weight = ft.FontWeight.BOLD,
                        color = ft.colors.WHITE,
                        font_family = "HDText" ),
        bgcolor = ft.colors.ON_SURFACE_VARIANT
    )
    
    df_name_dict = nd.files
    df_names_list = list(df_name_dict.values())
    std_df_name = df_names_list[0]
    area_df_name = df_names_list[1]
    tab_menu = TabMenu(std_df_name = std_df_name, area_df_name = area_df_name)
    
    page.add(tab_menu)
    
    
if __name__ == "__main__":
    ft.app(target = main)

