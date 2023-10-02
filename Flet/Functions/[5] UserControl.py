import flet as ft

class Counter(ft.UserControl):
    def build(self):
        self.counter = 0
        text = ft.Text(str(self.counter))

        # build함수의 하위함수로 배치하면 build함수의 지역변수를 가져올 수 있음
        # self를 사용하지 않아도 됨
        def add_click(e):
            self.counter += 1
            text.value = str(self.counter)  
            self.update()
        
        return ft.Row(
            [
                text,
                ft.ElevatedButton(
                    "Add",
                    on_click = add_click )
            ]
        )

def main(page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.window_width = 580
    page.window_height = 740
    page.add(Counter(), Counter())

ft.app(target=main)

############################################################



