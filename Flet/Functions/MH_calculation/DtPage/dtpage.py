import flet as ft

'''
To show and extract DataFrame of excel files on flet
'''

class DtPage(ft.UserControl):
    default_row_per_page = 10
    default_sheet_number = 1
    def __init__(
        self,
        datatable: ft.DataTable,
        table_title: str = "Paint Area Table",
        rows_per_page: int = default_row_per_page,
        sheet_number: int = default_sheet_number
    ):
        super().__init__()  # 부모클래스의 초기화 속성 상속
        self.dt = datatable
        self.title = table_title
        self.rows_per_page = rows_per_page
        
        self.num_rows = len(datatable.rows)
        self.current_page = 1
        
        # num_rows : 전체 행수
        # rows_per_page : 페이지당 설정한 행수
        # p_int : 전체 행을 설정한 행의 수로 나눈 몫 -> 페이지수
        # p_add : 전체 행을 설정한 행의 수로 나눈 나머지 -> 마지막 페이지 행수
        # 마지막 페이지에 남은 행이 있으면 페이지 1개를 더하고 아니면 0을 더하기
        p_int, p_add = divmod(self.num_rows, self.rows_per_page)
        self.num_pages = p_int + (1 if p_add else 0)
        
        self.v_current_page = ft.Text(
            str(self.current_page),
            tooltip = "현재 페이지 설정을 위해 클릭하시오.",
            weight = ft.FontWeight.BOLD
        )
        
        self.current_page_changer_field = ft.TextField(
            value = str(self.current_page),
            dense = True,
            filled = False,
            width = 50,
            on_submit = lambda e: self.set_page(page = e.control.value),
            visible = False,
            keyboard_type = ft.KeyboardType.NUMBER,
            content_padding = 2,
            text_align = ft.TextAlign.CENTER
        )
        
        # 콘텐츠에 더블탭을 감지하기 위한 Gesture Detector
        # 페이지 변경 입력을 위한 TextField에 현재 페이지값을 보여줌
        self.gesture_detect = ft.GestureDetector(
            content = ft.Row(
                controls = [
                    self.v_current_page,
                    self.current_page_changer_field
                ]
            ),
            on_double_tap = self.on_double_tap_page_changer
        )
        
        self.v_num_of_row_changer_field = ft.TextField(
            value = str(self.rows_per_page),
            dense = True,
            filled = False,
            width = 50,
            on_submit = lambda e: self.set_rows_per_page(e.control.value),
            keyboard_type = ft.KeyboardType.NUMBER,
            content_padding = 2,
            text_align = ft.TextAlign.CENTER
        )
        
        self.v_count = ft.Text(weight = ft.FontWeight.BOLD)
        self.pdt = ft.DataTable(
            columns = self.dt.columns,
            rows = self.build_rows()
        )
    
    # getter and setter 사용생략을 위해 @property 사용
    # datatable 함수는 ft.DataTable 값을 출력
    @property
    def datatable(self) -> ft.DataTable:
        return self.pdt
    
    # datacolumns 함수는 ft.DataColumn 값을 list화한 값을 출력
    # pdt.columns는 ft.DataTable의 columns속성값을 가져오는데,
    # 이것은 dt(datatable)의 각 column들을 모아놓은 list값임
    # pdt.columns (flet에서) -> dt.columns (dataframe에서) -> 컬럼 리스트
    @property
    def datacolumns(self) -> list[ft.DataColumn]:
        return self.pdt.columns
    
    @property
    def datarows(self) -> list[ft.DataRow]:
        return self.dt.rows
    
    # 페이지당 행수를 설정하는 함수생성
    def set_rows_per_page(self, new_row_per_page: str):
        try:
            if 1 <= int(new_row_per_page) <= self.num_rows:
                self.rows_per_page = int(new_row_per_page)
            else:
                self.default_row_per_page
        except ValueError:
            self.rows_per_page = self.default_row_per_page
        
        # TextField에 페이지에 설정된 행수를 입력해 줌
        self.v_num_of_row_changer_field.value = str(self.rows_per_page)
        
        p_int, p_add = divmod(self.num_rows, self.rows_per_page)
        self.num_pages = p_int + (1 if p_add else 0)
        self.set_page(page = 1)
        
    # 현재 페이지를 찾아서 설정하는 함수생성
    # input 변수 : page, delta
    # page변수는 기본값 None이고, delta변수는 기본값 0 임.
    def set_page(self, page: [str, int, None] = None, delta: int = 0):
        if page is not None:
            try:
                if 1 <= int(page) <= self.num_pages:
                    self.current_page = int(page)
                else:
                    self.current_page = 1
            except ValueError:
                self.current_page = 1
        # delta값이 1 (True)일 경우, 현재 페이지수에 1을 더함 (다음페이지가기)
        elif delta:
            self.current_page += delta
        else:
            return self.refresh_data()
    
    # 다음 페이지로 가는 함수생성
    # 현재 페이지가 총 페이지수 보다 작은 경우에만 delta값 1 입력
    def next_page(self, e: ft.ControlEvent):
        if self.current_page < self.num_pages:
            self.set_page(delta = 1)
    
    # 이전 페이지로 가는 함수생성
    # 현재 페이지가 1보다 클 경우에만 현재의 delta 누적값에서 1을 빼기
    def prev_page(self, e: ft.ControlEvent):
        if self.current_page > 1:
            self.set_page(delta =- 1)
    
    # 처음 페이지로 돌아가기        
    def goto_first_page(self, e: ft.ControlEvent):
        self.set_page(page = 1)
        
    # 마지막 페이지로 가기
    def goto_last_page(self, e: ft.ControlEvent):
        self.set_page(page = self.num_pages)
    
    # ft.DataTable 값의 rows 속성값 생성
    def build_rows(self) -> list:
        return self.dt.rows[slice(*self.dt_on_page())]
    
    
    # first_idx : 현재 보여지는 페이지의 첫번째 행
    # last_idx : 현재 보여지는 페이지의 마지막 행
    # first_idx_multi : 첫번째 행값
    # 현재 페이지가 1 페이지 일 경우, first_idx_multi에 0 입력
    # 그렇지 않을 경우 : 현재 페이지에 1을 뺀 값을 first_idx_multi에 입력 (이전 페이지값)
    def dt_on_page(self) -> tuple[int, int]:
        # 현재 페이지가 1 일 경우
        if self.current_page == 1:
            first_idx_multi = 0
        else:
            first_idx_multi = self.current_page - 1
        
        # 설정한 페이지의 행수에 이전 페이지 값을 곱함
        first_idx = first_idx_multi * self.rows_per_page
        
        # 설정한 페이지의 행수에 현재 페이지 값을 곱함
        last_idx = self.current_page * self.rows_per_page
        
        return first_idx, last_idx
    
    def build(self):
        return ft.Card(
            ft.Container(
                ft.Column(
                    [
                        ft.Text(self.title,
                                size = 20,
                                weight = "bold",
                                style = ft.TextThemeStyle.HEADLINE_MEDIUM,
                                font_family = "HDText"),
                        self.pdt,
                        ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.IconButton(
                                        ft.icons.KEYBOARD_DOUBLE_ARROW_LEFT,
                                        on_click = self.goto_first_page,
                                        tooltip = "첫페이지"
                                        ),
                                        ft.IconButton(
                                            ft.icons.KEYBOARD_ARROW_LEFT,
                                            on_click = self.prev_page,
                                            tooltip = "이전페이지"
                                        ),
                                        self.gesture_detect,
                                        ft.IconButton(
                                            ft.icons.KEYBOARD_ARROW_RIGHT,
                                            on_click = self.next_page,
                                            tooltip = "다음페이지"
                                        ),
                                        ft.IconButton(
                                            ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
                                            on_click=self.goto_last_page,
                                            tooltip = "마지막페이지"
                                        )   
                                    ]
                                ),
                                ft.Row(
                                    [
                                        self.v_num_of_row_changer_field,
                                        ft.Text(
                                            "페이지당 행수 설정",
                                            size = 15,
                                            weight = "bold",
                                            style = ft.TextThemeStyle.HEADLINE_MEDIUM,
                                            font_family = "HDText"
                                        ),  
                                    ],
                                ),
                                self.v_count,
                            ],
                            alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO
                ),
                padding = 5,
            ),
            elevation = 5,
        )
    
    def on_double_tap_page_changer(self, e):
        self.current_page_changer_field.value = str(self.current_page)
        self.v_current_page.visible = not self.v_current_page.visible
        self.current_page_changer_field.visible = not self.current_page_changer_field.visible
        self.update()
        
    def refresh_data(self):
        self.pdt.rows = self.build_rows()
        self.v_count.value = f"총 행수: {self.num_rows}"
        self.v_current_page.value = f"{self.current_page}/{self.num_pages}"
        self.current_page_changer_field.visible = False
        self.v_current_page.visible = True
        self.update()
        
    def did_mount(self):
        self.refresh_data()
